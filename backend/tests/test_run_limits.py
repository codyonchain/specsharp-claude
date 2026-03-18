from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.run_limits import (
    assert_run_available,
    consume_run,
    get_effective_run_limit_snapshot,
    get_run_limit_snapshot,
    grant_bonus_runs,
)
from app.db.database import Base
from app.db.models import Organization, OrganizationRunQuota


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _seed_org(db, org_id: str = "org_limits"):
    db.add(Organization(id=org_id, name="Limits Org"))
    db.commit()
    return org_id


def test_run_limits_default_then_block(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 2)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    initial = get_run_limit_snapshot(db, org_id=org_id, email="member@example.com")
    assert initial.total_runs == 2
    assert initial.remaining_runs == 2

    consume_run(db, org_id=org_id, email="member@example.com")
    consume_run(db, org_id=org_id, email="member@example.com")
    blocked = get_run_limit_snapshot(db, org_id=org_id, email="member@example.com")
    assert blocked.remaining_runs == 0

    with pytest.raises(HTTPException) as exc:
        assert_run_available(db, org_id=org_id, email="member@example.com")
    assert exc.value.status_code == 403
    assert isinstance(exc.value.detail, dict)
    assert exc.value.detail.get("code") == "run_limit_reached"


def test_unlimited_email_bypasses_quota(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "vip@example.com")

    snapshot = assert_run_available(db, org_id=org_id, email="vip@example.com")
    assert snapshot.is_unlimited is True
    assert snapshot.remaining_runs is None
    after = consume_run(db, org_id=org_id, email="vip@example.com")
    assert after.is_unlimited is True
    assert after.used_runs == 0


def test_grant_bonus_runs_restores_capacity(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    consume_run(db, org_id=org_id, email="member@example.com")
    with pytest.raises(HTTPException):
        assert_run_available(db, org_id=org_id, email="member@example.com")

    grant_bonus_runs(db, org_id=org_id, add_runs=3)
    snapshot = get_run_limit_snapshot(db, org_id=org_id, email="member@example.com")
    assert snapshot.total_runs == 4
    assert snapshot.used_runs == 1
    assert snapshot.remaining_runs == 3


def test_effective_snapshot_reports_real_exhaustion_for_normal_org_users(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    consume_run(db, org_id=org_id, email="member@example.com")

    snapshot = get_effective_run_limit_snapshot(db, org_id=org_id, email="member@example.com")
    assert snapshot.is_unlimited is False
    assert snapshot.remaining_runs == 0
    assert snapshot.total_runs == 1


def test_effective_snapshot_reports_unlimited_internal_access_without_false_exhaustion(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "vip@example.com")

    snapshot = get_effective_run_limit_snapshot(db, org_id=org_id, email="vip@example.com")
    assert snapshot.is_unlimited is True
    assert snapshot.remaining_runs is None


def test_local_dev_auth_bypass_returns_non_blocking_effective_snapshot_while_preserving_stored_quota_truth(
    monkeypatch,
):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("LOCAL_DEV_AUTH_BYPASS", "true")
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    db.add(
        OrganizationRunQuota(
            org_id=org_id,
            included_runs=1,
            bonus_runs=0,
            used_runs=1,
        )
    )
    db.commit()

    stored_snapshot = get_run_limit_snapshot(db, org_id=org_id, email="local-dev@specsharp.dev")
    assert stored_snapshot.is_unlimited is False
    assert stored_snapshot.remaining_runs == 0

    effective_snapshot = get_effective_run_limit_snapshot(
        db,
        org_id=org_id,
        email="local-dev@specsharp.dev",
    )
    assert effective_snapshot.is_unlimited is False
    assert effective_snapshot.remaining_runs is None
    assert effective_snapshot.total_runs is None

    allowed_snapshot = assert_run_available(db, org_id=org_id, email="local-dev@specsharp.dev")
    assert allowed_snapshot.is_unlimited is False
    assert allowed_snapshot.remaining_runs is None
    after = consume_run(db, org_id=org_id, email="local-dev@specsharp.dev")
    assert after.is_unlimited is False
    assert after.remaining_runs is None
    assert after.used_runs == 0


def test_skip_auth_no_longer_bypasses_run_limits(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.setenv("SKIP_AUTH", "true")
    monkeypatch.delenv("LOCAL_DEV_AUTH_BYPASS", raising=False)
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    consume_run(db, org_id=org_id, email="member@example.com")

    snapshot = get_effective_run_limit_snapshot(db, org_id=org_id, email="member@example.com")
    assert snapshot.is_unlimited is False
    assert snapshot.remaining_runs == 0

    with pytest.raises(HTTPException) as exc:
        assert_run_available(db, org_id=org_id, email="member@example.com")
    assert exc.value.status_code == 403
