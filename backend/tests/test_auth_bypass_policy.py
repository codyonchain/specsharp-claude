from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import build_testing_auth_context, get_auth_context
from app.core.auth_bypass import get_auth_bypass_mode, is_auth_bypass_enabled
from app.core.environment import EnvironmentChecker
from app.db.database import Base


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def _set_local_dev_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("LOCAL_DEV_AUTH_BYPASS", raising=False)
    monkeypatch.delenv("SKIP_AUTH", raising=False)


def _set_production_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://db.example.com/specsharp")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("JWT_SECRET", "jwt-secret")
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("LOCAL_DEV_AUTH_BYPASS", raising=False)
    monkeypatch.delenv("SKIP_AUTH", raising=False)


def test_startup_allows_explicit_local_dev_bypass_for_local_sqlite(monkeypatch):
    _set_local_dev_env(monkeypatch)
    monkeypatch.setenv("LOCAL_DEV_AUTH_BYPASS", "true")

    EnvironmentChecker.log_startup_config()


def test_startup_rejects_legacy_skip_auth_even_in_local_dev(monkeypatch):
    _set_local_dev_env(monkeypatch)
    monkeypatch.setenv("SKIP_AUTH", "true")

    with pytest.raises(SystemExit):
        EnvironmentChecker.log_startup_config()


def test_startup_rejects_testing_bypass_in_production_like_env(monkeypatch):
    _set_production_env(monkeypatch)
    monkeypatch.setenv("TESTING", "true")

    with pytest.raises(SystemExit):
        EnvironmentChecker.log_startup_config()


@pytest.mark.asyncio
async def test_auth_context_allows_explicit_local_dev_bypass(monkeypatch):
    _set_local_dev_env(monkeypatch)
    monkeypatch.setenv("LOCAL_DEV_AUTH_BYPASS", "true")

    auth = await get_auth_context(credentials=None, requested_org_id=None, db=_session())

    assert auth == build_testing_auth_context()
    assert get_auth_bypass_mode() == "local_dev"
    assert is_auth_bypass_enabled() is True


@pytest.mark.asyncio
async def test_auth_context_does_not_honor_legacy_skip_auth(monkeypatch):
    _set_local_dev_env(monkeypatch)
    monkeypatch.setenv("SKIP_AUTH", "true")

    with pytest.raises(HTTPException) as exc:
        await get_auth_context(credentials=None, requested_org_id=None, db=_session())

    assert exc.value.status_code == 401
    assert get_auth_bypass_mode() == "none"
    assert is_auth_bypass_enabled() is False
