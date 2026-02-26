#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy import func

from app.core.config import settings
from app.core.run_limits import get_or_create_org_run_quota, run_limit_snapshot_for
from app.db.database import SessionLocal
from app.db.models import Organization, OrganizationMember


def _fetch_supabase_user_id_by_email(email: str) -> Optional[str]:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None

    users_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/admin/users"
    headers = {
        "apikey": settings.supabase_service_role_key,
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
    }

    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(users_url, headers=headers, params={"email": email})
    except Exception:
        return None

    if response.status_code != 200:
        return None

    payload = response.json()
    users = payload.get("users") if isinstance(payload, dict) else None
    if not isinstance(users, list):
        return None

    normalized = email.strip().lower()
    for user in users:
        if not isinstance(user, dict):
            continue
        if str(user.get("email", "")).strip().lower() == normalized:
            user_id = str(user.get("id", "")).strip()
            return user_id or None
    return None


def _resolve_or_create_membership(email: str) -> OrganizationMember:
    db = SessionLocal()
    try:
        normalized = email.strip().lower()
        membership = (
            db.query(OrganizationMember)
            .filter(func.lower(OrganizationMember.email) == normalized)
            .order_by(OrganizationMember.is_default.desc(), OrganizationMember.id.asc())
            .first()
        )
        if membership:
            return membership

        user_id = _fetch_supabase_user_id_by_email(normalized)
        if not user_id:
            raise RuntimeError(
                f"No existing organization membership and no Supabase user found for '{normalized}'. "
                "Create the user first in Supabase Authentication > Users."
            )

        local_part = normalized.split("@")[0] if "@" in normalized else user_id[:8]
        org = Organization(
            id=str(uuid.uuid4()),
            name=f"{local_part}'s Workspace",
            created_at=datetime.utcnow(),
        )
        db.add(org)
        db.flush()

        membership = OrganizationMember(
            org_id=org.id,
            user_id=user_id,
            email=normalized,
            role="owner",
            is_default=True,
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership
    finally:
        db.close()


def grant_runs(email: str, add_runs: int) -> None:
    if add_runs <= 0:
        raise ValueError("--add-runs must be greater than 0")

    membership = _resolve_or_create_membership(email)

    db = SessionLocal()
    try:
        membership = (
            db.query(OrganizationMember)
            .filter(OrganizationMember.id == membership.id)
            .first()
        )
        if not membership:
            raise RuntimeError("Organization membership disappeared while granting runs")

        quota = get_or_create_org_run_quota(db, org_id=membership.org_id, for_update=True)
        before = run_limit_snapshot_for(membership.email, quota)
        quota.bonus_runs = max(int(quota.bonus_runs or 0), 0) + int(add_runs)
        db.flush()
        after = run_limit_snapshot_for(membership.email, quota)
        db.commit()

        print("✅ Granted runs successfully")
        print(f"email: {membership.email}")
        print(f"org_id: {membership.org_id}")
        print(f"added_runs: {add_runs}")
        print(
            "before:",
            f"included={before.included_runs}",
            f"bonus={before.bonus_runs}",
            f"used={before.used_runs}",
            f"remaining={before.remaining_runs}",
        )
        print(
            "after: ",
            f"included={after.included_runs}",
            f"bonus={after.bonus_runs}",
            f"used={after.used_runs}",
            f"remaining={after.remaining_runs}",
        )
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Grant additional SpecSharp decision-packet runs to a user email.")
    parser.add_argument("--email", required=True, help="User email address")
    parser.add_argument("--add-runs", required=True, type=int, help="Number of runs to add")
    args = parser.parse_args()

    try:
        grant_runs(args.email, args.add_runs)
        return 0
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
