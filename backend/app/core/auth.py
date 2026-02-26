from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional
import uuid

import httpx
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.db.models import Organization, OrganizationMember


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    user_id: str
    email: str
    org_id: str
    role: str
    access_token: str


async def _fetch_supabase_user(access_token: str) -> Dict[str, Any]:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase auth is not configured on backend",
        )

    user_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "apikey": settings.supabase_service_role_key,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(user_url, headers=headers)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to validate auth token with Supabase",
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    data = response.json()
    if not isinstance(data, dict) or not data.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Supabase user payload missing required fields",
        )
    return data


def _upsert_default_membership(db: Session, user_id: str, email: str) -> OrganizationMember:
    memberships = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == user_id)
        .order_by(OrganizationMember.is_default.desc(), OrganizationMember.id.asc())
        .all()
    )
    if memberships:
        default_member = next((m for m in memberships if m.is_default), memberships[0])
        if not default_member.is_default:
            default_member.is_default = True
            db.commit()
            db.refresh(default_member)
        return default_member

    local_part = email.split("@")[0] if "@" in email else user_id[:8]
    org = Organization(
        id=str(uuid.uuid4()),
        name=f"{local_part}'s Workspace",
        created_at=datetime.utcnow(),
    )
    db.add(org)
    db.flush()

    member = OrganizationMember(
        org_id=org.id,
        user_id=user_id,
        email=email,
        role="owner",
        is_default=True,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def _resolve_membership(
    db: Session, *, user_id: str, email: str, requested_org_id: Optional[str]
) -> OrganizationMember:
    memberships = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == user_id)
        .order_by(OrganizationMember.is_default.desc(), OrganizationMember.id.asc())
        .all()
    )

    # If provisioned by email before first login, claim that membership for this user_id.
    if not memberships and email:
        email_membership = (
            db.query(OrganizationMember)
            .filter(func.lower(OrganizationMember.email) == email.lower())
            .order_by(OrganizationMember.is_default.desc(), OrganizationMember.id.asc())
            .first()
        )
        if email_membership:
            email_membership.user_id = user_id
            db.commit()
            db.refresh(email_membership)
            memberships = [email_membership]

    if requested_org_id:
        membership = next((m for m in memberships if m.org_id == requested_org_id), None)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of requested org",
            )
        return membership

    if memberships:
        default_member = next((m for m in memberships if m.is_default), memberships[0])
        if not default_member.is_default:
            default_member.is_default = True
            db.commit()
            db.refresh(default_member)
        return default_member

    if not settings.allow_auto_org_provisioning:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not provisioned. Contact support for onboarding.",
        )

    return _upsert_default_membership(db, user_id=user_id, email=email)


async def get_auth_context(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    requested_org_id: Optional[str] = Header(None, alias="X-Org-Id"),
    db: Session = Depends(get_db),
) -> AuthContext:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_payload = await _fetch_supabase_user(credentials.credentials)
    user_id = str(user_payload.get("id", "")).strip()
    email = str(user_payload.get("email", "")).strip().lower()
    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user payload from Supabase",
        )

    membership = _resolve_membership(
        db,
        user_id=user_id,
        email=email,
        requested_org_id=requested_org_id,
    )

    return AuthContext(
        user_id=user_id,
        email=email,
        org_id=membership.org_id,
        role=membership.role or "member",
        access_token=credentials.credentials,
    )
