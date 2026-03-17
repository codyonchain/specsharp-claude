#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Iterable, List, Optional, Sequence

import httpx
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal
from app.db.models import Organization, OrganizationMember

PENDING_USER_PREFIX = "pending:"


@dataclass(frozen=True)
class SupabaseLookupResult:
    user_id: Optional[str]
    status: str
    detail: str


@dataclass(frozen=True)
class ProvisioningOutcome:
    membership: OrganizationMember
    action: str
    link_state: str
    lookup_status: str
    lookup_detail: str
    default_requested: bool


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if not normalized:
        raise ValueError("Email must not be blank")
    return normalized


def _pending_user_id_for(email: str) -> str:
    return f"{PENDING_USER_PREFIX}{_normalize_email(email)}"


def _collect_emails(values: Sequence[str]) -> List[str]:
    emails: List[str] = []
    seen = set()
    for raw_value in values:
        for candidate in str(raw_value).split(","):
            normalized = _normalize_email(candidate)
            if normalized in seen:
                continue
            seen.add(normalized)
            emails.append(normalized)
    if not emails:
        raise ValueError("At least one teammate email is required")
    return emails


def _membership_link_state(user_id: str) -> str:
    return "pending-first-auth-claim" if str(user_id or "").startswith(PENDING_USER_PREFIX) else "linked-existing-user"


def _fetch_supabase_user_id_by_email(email: str) -> SupabaseLookupResult:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return SupabaseLookupResult(
            user_id=None,
            status="unavailable",
            detail="supabase-admin-config-missing",
        )

    users_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(users_url, headers=headers, params={"email": email})
    except Exception:
        return SupabaseLookupResult(
            user_id=None,
            status="unavailable",
            detail="supabase-admin-request-failed",
        )

    if response.status_code != 200:
        return SupabaseLookupResult(
            user_id=None,
            status="unavailable",
            detail=f"supabase-admin-status-{response.status_code}",
        )

    try:
        payload = response.json()
    except Exception:
        return SupabaseLookupResult(
            user_id=None,
            status="unavailable",
            detail="supabase-admin-invalid-payload",
        )
    users = payload.get("users") if isinstance(payload, dict) else None
    if not isinstance(users, list):
        return SupabaseLookupResult(
            user_id=None,
            status="unavailable",
            detail="supabase-admin-invalid-payload",
        )

    normalized = _normalize_email(email)
    for user in users:
        if not isinstance(user, dict):
            continue
        if str(user.get("email", "")).strip().lower() == normalized:
            user_id = str(user.get("id", "")).strip()
            if user_id:
                return SupabaseLookupResult(
                    user_id=user_id,
                    status="resolved",
                    detail="matched-existing-supabase-user",
                )
    return SupabaseLookupResult(
        user_id=None,
        status="not_found",
        detail="no-existing-supabase-user",
    )


def _set_default_for_email(
    db: Session,
    *,
    normalized_email: str,
    keep_membership_id: int,
) -> None:
    prior_defaults = (
        db.query(OrganizationMember)
        .filter(func.lower(OrganizationMember.email) == normalized_email)
        .filter(OrganizationMember.id != keep_membership_id)
        .filter(OrganizationMember.is_default.is_(True))
        .all()
    )
    for membership in prior_defaults:
        membership.is_default = False


def upsert_existing_org_membership(
    db: Session,
    *,
    org_id: str,
    email: str,
    role: str = "member",
    set_default: bool = False,
) -> ProvisioningOutcome:
    normalized_email = _normalize_email(email)
    normalized_role = role.strip().lower() if role and role.strip() else "member"

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise RuntimeError(f"Organization '{org_id}' does not exist")

    lookup = _fetch_supabase_user_id_by_email(normalized_email)
    resolved_user_id = lookup.user_id
    membership = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.org_id == org_id)
        .filter(func.lower(OrganizationMember.email) == normalized_email)
        .order_by(OrganizationMember.is_default.desc(), OrganizationMember.id.asc())
        .first()
    )

    action = "confirmed-existing-membership"
    if membership is None:
        membership = OrganizationMember(
            org_id=org_id,
            user_id=resolved_user_id or _pending_user_id_for(normalized_email),
            email=normalized_email,
            role=normalized_role,
            is_default=bool(set_default),
        )
        db.add(membership)
        db.flush()
        action = "created-membership"
    else:
        prior_email = membership.email
        prior_role = membership.role
        prior_user_id = membership.user_id
        prior_is_default = membership.is_default
        membership.email = normalized_email
        membership.role = normalized_role
        if resolved_user_id and (
            membership.user_id == _pending_user_id_for(normalized_email)
            or str(membership.user_id).startswith(PENDING_USER_PREFIX)
        ):
            membership.user_id = resolved_user_id
            action = "upgraded-pending-to-linked"
        if set_default:
            membership.is_default = True
        if action != "upgraded-pending-to-linked" and (
            membership.email != prior_email
            or membership.role != prior_role
            or membership.user_id != prior_user_id
            or membership.is_default != prior_is_default
        ):
            action = "updated-existing-membership"

    if set_default:
        _set_default_for_email(
            db,
            normalized_email=normalized_email,
            keep_membership_id=membership.id,
        )

    db.flush()
    return ProvisioningOutcome(
        membership=membership,
        action=action,
        link_state=_membership_link_state(membership.user_id),
        lookup_status=lookup.status,
        lookup_detail=lookup.detail,
        default_requested=bool(set_default),
    )


def provision_org_members(
    *,
    org_id: str,
    emails: Sequence[str],
    role: str = "member",
    set_default: bool = False,
) -> List[ProvisioningOutcome]:
    normalized_emails = _collect_emails(emails)
    db = SessionLocal()
    try:
        outcomes = [
            upsert_existing_org_membership(
                db,
                org_id=org_id,
                email=email,
                role=role,
                set_default=set_default,
            )
            for email in normalized_emails
        ]
        db.commit()
        for outcome in outcomes:
            db.refresh(outcome.membership)
        return outcomes
    finally:
        db.close()


def _print_memberships(outcomes: Iterable[ProvisioningOutcome]) -> None:
    materialized = list(outcomes)
    if not materialized:
        return
    org_ids = sorted({outcome.membership.org_id for outcome in materialized})
    print("Provisioned org memberships")
    if len(org_ids) == 1:
        print(f"org_id: {org_ids[0]}")
    else:
        print(f"org_ids: {', '.join(org_ids)}")
    if any(outcome.default_requested for outcome in materialized):
        print(
            "default_note: default=yes means this org is the selected default membership for that email during runtime resolution after first auth claim."
        )
    if any(outcome.lookup_status == "unavailable" for outcome in materialized):
        print(
            "lookup_note: lookup=unavailable means the membership was written pending and immediate Supabase linking could not be confirmed."
        )
    for outcome in materialized:
        membership = outcome.membership
        print(
            f"- org_id={membership.org_id} "
            f"email={membership.email} "
            f"action={outcome.action} "
            f"link={outcome.link_state} "
            f"lookup={outcome.lookup_status}:{outcome.lookup_detail} "
            f"user_id={membership.user_id} "
            f"role={membership.role} "
            f"default={'yes' if membership.is_default else 'no'}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provision teammate emails into an existing SpecSharp organization."
    )
    parser.add_argument("--org-id", required=True, help="Existing organization id")
    parser.add_argument(
        "--email",
        dest="emails",
        action="append",
        required=True,
        help="Teammate email. Repeat the flag or pass comma-separated values.",
    )
    parser.add_argument(
        "--role",
        default="member",
        help="Membership role to write for the teammate(s). Defaults to member.",
    )
    parser.add_argument(
        "--set-default",
        action="store_true",
        help="Mark this org as the default membership for the teammate email(s).",
    )
    args = parser.parse_args()

    try:
        outcomes = provision_org_members(
            org_id=args.org_id,
            emails=args.emails,
            role=args.role,
            set_default=args.set_default,
        )
        _print_memberships(outcomes)
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
