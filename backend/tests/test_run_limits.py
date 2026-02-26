from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.run_limits import (
    assert_run_available,
    consume_run,
    get_run_limit_snapshot,
    grant_bonus_runs,
)
from app.db.database import Base
from app.db.models import Organization


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
