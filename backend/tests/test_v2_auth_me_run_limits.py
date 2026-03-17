from starlette.requests import Request
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import AuthContext
from app.core.config import settings
from app.core.run_limits import consume_run
from app.db.database import Base
from app.db.models import Organization, OrganizationRunQuota
from app.v2.api.auth import get_auth_me


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _seed_org(db, org_id: str = "org_auth_me"):
    db.add(Organization(id=org_id, name="Auth Me Org"))
    db.commit()
    return org_id


def _request() -> Request:
    return Request({"type": "http", "method": "GET", "path": "/api/v2/auth/me", "headers": []})


@pytest.mark.asyncio
async def test_auth_me_reports_real_exhaustion_for_normal_org_users(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    consume_run(db, org_id=org_id, email="member@example.com")

    response = await get_auth_me(
        request=_request(),
        auth=AuthContext(
            user_id="user_1",
            email="member@example.com",
            org_id=org_id,
            role="owner",
            access_token="token",
        ),
        db=db,
    )

    assert response["data"]["run_limits"] == {
        "is_unlimited": False,
        "included_runs": 1,
        "bonus_runs": 0,
        "used_runs": 1,
        "remaining_runs": 0,
        "total_runs": 1,
    }


@pytest.mark.asyncio
async def test_auth_me_reports_ordinary_quota_truth_when_runs_remain(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "")

    response = await get_auth_me(
        request=_request(),
        auth=AuthContext(
            user_id="user_ordinary",
            email="ordinary@example.com",
            org_id=org_id,
            role="owner",
            access_token="token",
        ),
        db=db,
    )

    assert response["data"]["run_limits"] == {
        "is_unlimited": False,
        "included_runs": 1,
        "bonus_runs": 0,
        "used_runs": 0,
        "remaining_runs": 1,
        "total_runs": 1,
    }


@pytest.mark.asyncio
async def test_auth_me_reports_unlimited_internal_access_without_false_exhaustion(monkeypatch):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.delenv("SKIP_AUTH", raising=False)
    monkeypatch.setattr(settings, "default_deal_runs", 1)
    monkeypatch.setattr(settings, "unlimited_access_emails", "vip@example.com")

    db.add(
        OrganizationRunQuota(
            org_id=org_id,
            included_runs=1,
            bonus_runs=0,
            used_runs=1,
        )
    )
    db.commit()

    response = await get_auth_me(
        request=_request(),
        auth=AuthContext(
            user_id="user_2",
            email="vip@example.com",
            org_id=org_id,
            role="owner",
            access_token="token",
        ),
        db=db,
    )

    assert response["data"]["run_limits"] == {
        "is_unlimited": True,
        "included_runs": 0,
        "bonus_runs": 0,
        "used_runs": 0,
        "remaining_runs": None,
        "total_runs": None,
    }


@pytest.mark.asyncio
async def test_auth_me_uses_non_blocking_effective_snapshot_when_skip_auth_bypasses_generation(
    monkeypatch,
):
    db = _session()
    org_id = _seed_org(db)
    monkeypatch.setenv("SKIP_AUTH", "true")
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

    response = await get_auth_me(
        request=_request(),
        auth=AuthContext(
            user_id="user_3",
            email="local-dev@specsharp.dev",
            org_id=org_id,
            role="owner",
            access_token="dev-bypass",
        ),
        db=db,
    )

    assert response["data"]["run_limits"] == {
        "is_unlimited": False,
        "included_runs": 0,
        "bonus_runs": 0,
        "used_runs": 0,
        "remaining_runs": None,
        "total_runs": None,
    }
