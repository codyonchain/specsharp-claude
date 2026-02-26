from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Set

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import OrganizationRunQuota


@dataclass
class RunLimitSnapshot:
    is_unlimited: bool
    included_runs: int
    bonus_runs: int
    used_runs: int
    remaining_runs: int | None
    total_runs: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _parse_unlimited_access_emails(raw: str | None) -> Set[str]:
    if not raw:
        return set()
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def is_unlimited_user(email: str | None) -> bool:
    normalized = (email or "").strip().lower()
    if not normalized:
        return False
    return normalized in _parse_unlimited_access_emails(settings.unlimited_access_emails)


def _safe_non_negative(value: Any, fallback: int = 0) -> int:
    if isinstance(value, bool):
        return fallback
    if isinstance(value, (int, float)):
        return max(int(value), 0)
    return fallback


def _default_included_runs() -> int:
    return _safe_non_negative(settings.default_deal_runs, fallback=3)


def get_or_create_org_run_quota(
    db: Session,
    *,
    org_id: str,
    for_update: bool = False,
) -> OrganizationRunQuota:
    query = db.query(OrganizationRunQuota).filter(OrganizationRunQuota.org_id == org_id)
    if for_update:
        query = query.with_for_update()

    quota = query.first()
    if quota:
        return quota

    quota = OrganizationRunQuota(
        org_id=org_id,
        included_runs=_default_included_runs(),
        bonus_runs=0,
        used_runs=0,
    )
    db.add(quota)
    db.flush()
    return quota


def run_limit_snapshot_for(email: str, quota: OrganizationRunQuota | None) -> RunLimitSnapshot:
    if is_unlimited_user(email):
        return RunLimitSnapshot(
            is_unlimited=True,
            included_runs=0,
            bonus_runs=0,
            used_runs=0,
            remaining_runs=None,
            total_runs=None,
        )

    included = _safe_non_negative(getattr(quota, "included_runs", 0), fallback=_default_included_runs())
    bonus = _safe_non_negative(getattr(quota, "bonus_runs", 0))
    used = _safe_non_negative(getattr(quota, "used_runs", 0))
    total = max(included + bonus, 0)
    remaining = max(total - used, 0)

    return RunLimitSnapshot(
        is_unlimited=False,
        included_runs=included,
        bonus_runs=bonus,
        used_runs=used,
        remaining_runs=remaining,
        total_runs=total,
    )


def get_run_limit_snapshot(db: Session, *, org_id: str, email: str) -> RunLimitSnapshot:
    if is_unlimited_user(email):
        return run_limit_snapshot_for(email, None)

    quota = get_or_create_org_run_quota(db, org_id=org_id, for_update=False)
    return run_limit_snapshot_for(email, quota)


def assert_run_available(db: Session, *, org_id: str, email: str) -> RunLimitSnapshot:
    if is_unlimited_user(email):
        return run_limit_snapshot_for(email, None)

    quota = get_or_create_org_run_quota(db, org_id=org_id, for_update=True)
    snapshot = run_limit_snapshot_for(email, quota)
    if (snapshot.remaining_runs or 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Run limit reached. Contact support to add more runs.",
                "code": "run_limit_reached",
                "remaining_runs": 0,
            },
        )
    return snapshot


def consume_run(db: Session, *, org_id: str, email: str) -> RunLimitSnapshot:
    if is_unlimited_user(email):
        return run_limit_snapshot_for(email, None)

    quota = get_or_create_org_run_quota(db, org_id=org_id, for_update=True)
    snapshot_before = run_limit_snapshot_for(email, quota)
    if (snapshot_before.remaining_runs or 0) <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Run limit reached. Contact support to add more runs.",
                "code": "run_limit_reached",
                "remaining_runs": 0,
            },
        )

    quota.used_runs = _safe_non_negative(quota.used_runs) + 1
    db.flush()
    return run_limit_snapshot_for(email, quota)


def grant_bonus_runs(db: Session, *, org_id: str, add_runs: int) -> RunLimitSnapshot:
    normalized = _safe_non_negative(add_runs)
    quota = get_or_create_org_run_quota(db, org_id=org_id, for_update=True)
    quota.bonus_runs = _safe_non_negative(quota.bonus_runs) + normalized
    db.flush()
    return run_limit_snapshot_for("", quota)
