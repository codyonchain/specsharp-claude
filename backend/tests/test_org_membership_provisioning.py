from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import _resolve_membership
from app.db.database import Base
from app.db.models import Organization, OrganizationMember
from scripts import provision_org_members


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return testing_session_local()


def _seed_org(db, org_id: str, name: str = "Shared Org") -> Organization:
    org = Organization(id=org_id, name=name, created_at=datetime.utcnow())
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


def _lookup_result(
    user_id: Optional[str] = None,
    *,
    status: Optional[str] = None,
    detail: Optional[str] = None,
) -> provision_org_members.SupabaseLookupResult:
    if user_id:
        return provision_org_members.SupabaseLookupResult(
            user_id=user_id,
            status=status or "resolved",
            detail=detail or "matched-existing-supabase-user",
        )
    return provision_org_members.SupabaseLookupResult(
        user_id=None,
        status=status or "not_found",
        detail=detail or "no-existing-supabase-user",
    )


def test_upsert_existing_org_membership_creates_pending_membership_without_creating_new_org(monkeypatch, capsys):
    db = _session()
    _seed_org(db, "org_shared")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )

    outcome = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_shared",
        email="Teammate@Example.com",
    )
    db.commit()
    membership = outcome.membership
    provision_org_members._print_memberships([outcome])
    captured = capsys.readouterr().out

    assert membership.org_id == "org_shared"
    assert membership.email == "teammate@example.com"
    assert membership.user_id == "pending:teammate@example.com"
    assert membership.role == "member"
    assert membership.is_default is False
    assert outcome.action == "created-membership"
    assert outcome.link_state == "pending-first-auth-claim"
    assert outcome.lookup_status == "not_found"
    assert "action=created-membership" in captured
    assert "link=pending-first-auth-claim" in captured
    assert "lookup=not_found:no-existing-supabase-user" in captured
    assert db.query(Organization).count() == 1
    assert db.query(OrganizationMember).count() == 1


def test_upsert_existing_org_membership_is_idempotent_and_upgrades_pending_user_id(monkeypatch, capsys):
    db = _session()
    _seed_org(db, "org_shared")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )
    created = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_shared",
        email="teammate@example.com",
    )
    db.commit()

    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result("supabase_uid_42"),
    )
    updated = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_shared",
        email="teammate@example.com",
        role="owner",
    )
    db.commit()
    provision_org_members._print_memberships([updated])
    captured = capsys.readouterr().out

    assert updated.membership.id == created.membership.id
    assert updated.membership.user_id == "supabase_uid_42"
    assert updated.membership.role == "owner"
    assert updated.action == "upgraded-pending-to-linked"
    assert updated.link_state == "linked-existing-user"
    assert updated.lookup_status == "resolved"
    assert "action=upgraded-pending-to-linked" in captured
    assert "link=linked-existing-user" in captured
    assert "lookup=resolved:matched-existing-supabase-user" in captured
    assert db.query(OrganizationMember).count() == 1


def test_set_default_targets_existing_org_without_cross_org_duplicates(monkeypatch, capsys):
    db = _session()
    _seed_org(db, "org_alpha", name="Alpha Org")
    _seed_org(db, "org_beta", name="Beta Org")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )
    first = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_alpha",
        email="shared@example.com",
        set_default=True,
    )
    db.commit()
    assert first.membership.is_default is True

    second = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_beta",
        email="shared@example.com",
        set_default=True,
    )
    db.commit()
    db.refresh(first.membership)
    db.refresh(second.membership)
    provision_org_members._print_memberships([first, second])
    captured = capsys.readouterr().out

    assert first.membership.org_id == "org_alpha"
    assert first.membership.is_default is False
    assert second.membership.org_id == "org_beta"
    assert second.membership.is_default is True
    assert "org_ids: org_alpha, org_beta" in captured
    assert "default_note:" in captured
    assert "default=yes" in captured
    assert db.query(OrganizationMember).count() == 2


def test_preprovisioned_membership_from_helper_claims_correct_org_on_first_auth_resolution(monkeypatch):
    db = _session()
    _seed_org(db, "org_claimable", name="Claimable Org")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )
    provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_claimable",
        email="future.user@example.com",
        set_default=True,
    )
    db.commit()

    claimed = _resolve_membership(
        db,
        user_id="supabase_uid_100",
        email="future.user@example.com",
        requested_org_id=None,
    )

    assert claimed.org_id == "org_claimable"
    assert claimed.user_id == "supabase_uid_100"
    assert claimed.is_default is True


def test_helper_preprovisioned_same_email_memberships_claim_together_and_honor_requested_org(monkeypatch):
    db = _session()
    _seed_org(db, "org_alpha", name="Alpha Org")
    _seed_org(db, "org_beta", name="Beta Org")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )

    alpha = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_alpha",
        email="shared.future@example.com",
        set_default=False,
    )
    beta = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_beta",
        email="shared.future@example.com",
        set_default=True,
    )
    db.commit()

    requested = _resolve_membership(
        db,
        user_id="supabase_uid_multi_1",
        email="shared.future@example.com",
        requested_org_id="org_alpha",
    )
    default_membership = _resolve_membership(
        db,
        user_id="supabase_uid_multi_1",
        email="shared.future@example.com",
        requested_org_id=None,
    )
    memberships = (
        db.query(OrganizationMember)
        .filter(OrganizationMember.user_id == "supabase_uid_multi_1")
        .order_by(OrganizationMember.org_id.asc())
        .all()
    )

    assert alpha.link_state == "pending-first-auth-claim"
    assert beta.link_state == "pending-first-auth-claim"
    assert requested.org_id == "org_alpha"
    assert default_membership.org_id == "org_beta"
    assert [membership.org_id for membership in memberships] == ["org_alpha", "org_beta"]
    assert next(membership for membership in memberships if membership.org_id == "org_beta").is_default is True


def test_provision_org_members_supports_multiple_emails_and_keeps_reruns_idempotent(monkeypatch, capsys):
    db = _session()
    _seed_org(db, "org_shared")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(),
    )
    original_session_local = provision_org_members.SessionLocal
    provision_org_members.SessionLocal = lambda: db
    try:
        first_pass = provision_org_members.provision_org_members(
            org_id="org_shared",
            emails=["first@example.com, second@example.com", "first@example.com"],
        )
        second_pass = provision_org_members.provision_org_members(
            org_id="org_shared",
            emails=["second@example.com", "first@example.com"],
        )
    finally:
        provision_org_members.SessionLocal = original_session_local

    provision_org_members._print_memberships(second_pass)
    captured = capsys.readouterr().out

    assert [outcome.membership.email for outcome in first_pass] == [
        "first@example.com",
        "second@example.com",
    ]
    assert [outcome.membership.email for outcome in second_pass] == [
        "second@example.com",
        "first@example.com",
    ]
    assert [outcome.action for outcome in second_pass] == [
        "confirmed-existing-membership",
        "confirmed-existing-membership",
    ]
    assert captured.count("action=confirmed-existing-membership") == 2
    assert db.query(OrganizationMember).count() == 2


def test_helper_output_flags_lookup_unavailable_without_pretending_link_success(monkeypatch, capsys):
    db = _session()
    _seed_org(db, "org_shared")
    monkeypatch.setattr(
        provision_org_members,
        "_fetch_supabase_user_id_by_email",
        lambda email: _lookup_result(
            status="unavailable",
            detail="supabase-admin-config-missing",
        ),
    )

    outcome = provision_org_members.upsert_existing_org_membership(
        db,
        org_id="org_shared",
        email="ops.user@example.com",
        set_default=True,
    )
    db.commit()
    provision_org_members._print_memberships([outcome])
    captured = capsys.readouterr().out

    assert outcome.membership.user_id == "pending:ops.user@example.com"
    assert outcome.link_state == "pending-first-auth-claim"
    assert outcome.lookup_status == "unavailable"
    assert "lookup_note:" in captured
    assert "lookup=unavailable:supabase-admin-config-missing" in captured
    assert "link=linked-existing-user" not in captured
