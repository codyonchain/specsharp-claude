from datetime import datetime

from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import AuthContext, get_auth_context, _resolve_membership, _upsert_default_membership
from app.core.config import settings
from app.db.database import Base
from app.db.models import Organization, OrganizationMember, Project, ProjectAccess
from app.v2.api.scope import _assign_unscoped_projects_for_dev, _get_scoped_project


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _project(project_id: str, name: str) -> Project:
    return Project(
        project_id=project_id,
        name=name,
        description="test",
        project_classification="ground_up",
        square_footage=10000,
        location="Nashville, TN",
        total_cost=1000000.0,
        scope_data="{}",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_auth_context_requires_bearer_token():
    with pytest.raises(HTTPException) as exc:
        await get_auth_context(credentials=None, requested_org_id=None, db=_session())
    assert exc.value.status_code == 401


def test_default_org_membership_created_for_new_user():
    db = _session()
    member = _upsert_default_membership(db, user_id="user_1", email="alpha@example.com")
    assert member.org_id
    assert member.user_id == "user_1"
    assert member.role == "owner"
    assert member.is_default is True

    # Re-running should return the same membership, not create duplicates.
    same_member = _upsert_default_membership(db, user_id="user_1", email="alpha@example.com")
    assert same_member.org_id == member.org_id


def test_requested_org_requires_membership():
    db = _session()
    member = _upsert_default_membership(db, user_id="user_2", email="beta@example.com")
    resolved = _resolve_membership(
        db,
        user_id="user_2",
        email="beta@example.com",
        requested_org_id=member.org_id,
    )
    assert resolved.org_id == member.org_id

    with pytest.raises(HTTPException) as exc:
        _resolve_membership(
            db,
            user_id="user_2",
            email="beta@example.com",
            requested_org_id="missing-org",
        )
    assert exc.value.status_code == 403


def test_resolve_membership_claims_email_preprovisioned_record_case_insensitive():
    db = _session()
    org = Organization(id="org_claim", name="Claim Org")
    db.add(org)
    db.flush()
    db.add(
        OrganizationMember(
            org_id=org.id,
            user_id="pending_user",
            email="Casey.User@Example.com",
            role="owner",
            is_default=True,
        )
    )
    db.commit()

    claimed = _resolve_membership(
        db,
        user_id="supabase_uid_1",
        email="casey.user@example.com",
        requested_org_id=None,
    )
    assert claimed.org_id == "org_claim"
    assert claimed.user_id == "supabase_uid_1"


def test_resolve_membership_blocks_unprovisioned_when_auto_provision_disabled(monkeypatch):
    db = _session()
    monkeypatch.setattr(settings, "allow_auto_org_provisioning", False)
    with pytest.raises(HTTPException) as exc:
        _resolve_membership(
            db,
            user_id="new_uid",
            email="new.user@example.com",
            requested_org_id=None,
        )
    assert exc.value.status_code == 403


def test_scope_query_enforces_org_access_and_dev_backfill(monkeypatch):
    db = _session()
    p1 = _project("proj_scope_1", "Project 1")
    p2 = _project("proj_scope_2", "Project 2")
    db.add_all([p1, p2])
    db.commit()
    db.refresh(p1)
    db.refresh(p2)

    db.add(ProjectAccess(project_id=p1.project_id, org_id="org_1", owner_user_id="user_1"))
    db.add(ProjectAccess(project_id=p2.project_id, org_id="org_2", owner_user_id="user_2"))
    db.commit()

    auth = AuthContext(
        user_id="user_1",
        email="user1@example.com",
        org_id="org_1",
        role="owner",
        access_token="token",
    )

    assert _get_scoped_project(db, p1.project_id, auth) is not None
    assert _get_scoped_project(db, p2.project_id, auth) is None
    assert _get_scoped_project(db, str(p1.id), auth) is not None

    # Backfill only applies to unscoped projects in non-production environments.
    p3 = _project("proj_scope_3", "Project 3")
    db.add(p3)
    db.commit()
    monkeypatch.setattr(settings, "environment", "development")
    _assign_unscoped_projects_for_dev(db, auth)

    mapped = db.query(ProjectAccess).filter(ProjectAccess.project_id == "proj_scope_3").first()
    assert mapped is not None
    assert mapped.org_id == "org_1"


def test_dev_backfill_is_disabled_outside_local_sqlite(monkeypatch):
    db = _session()
    p1 = _project("proj_scope_4", "Project 4")
    db.add(p1)
    db.commit()

    auth = AuthContext(
        user_id="user_4",
        email="user4@example.com",
        org_id="org_4",
        role="owner",
        access_token="token",
    )

    monkeypatch.setattr(settings, "environment", "production")
    monkeypatch.setattr(settings, "database_url", "postgresql://example")
    _assign_unscoped_projects_for_dev(db, auth)

    mapped = db.query(ProjectAccess).filter(ProjectAccess.project_id == "proj_scope_4").first()
    assert mapped is None
