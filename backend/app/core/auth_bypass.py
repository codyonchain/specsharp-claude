from __future__ import annotations

import os
from typing import Final

from app.core.config import settings


TESTING_ENV_VAR: Final = "TESTING"
LOCAL_DEV_AUTH_BYPASS_ENV_VAR: Final = "LOCAL_DEV_AUTH_BYPASS"
LEGACY_SKIP_AUTH_ENV_VAR: Final = "SKIP_AUTH"

_LOCAL_ENVIRONMENTS = {"development", "dev", "local"}
_TEST_ENVIRONMENTS = {"test", "testing"}
_SAFE_BYPASS_ENVIRONMENTS = _LOCAL_ENVIRONMENTS | _TEST_ENVIRONMENTS


def _env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() == "true"


def get_runtime_environment() -> str:
    env = os.getenv("ENVIRONMENT") or getattr(settings, "environment", "")
    normalized = str(env or "development").strip().lower()
    return normalized or "development"


def get_database_url() -> str:
    return str(os.getenv("DATABASE_URL") or settings.database_url or "").strip()


def is_local_development_environment() -> bool:
    return get_runtime_environment() in _LOCAL_ENVIRONMENTS


def is_local_database() -> bool:
    database_url = get_database_url().lower()
    return (
        database_url.startswith("sqlite")
        or "://localhost" in database_url
        or "://127.0.0.1" in database_url
        or "@localhost" in database_url
        or "@127.0.0.1" in database_url
    )


def is_safe_bypass_environment() -> bool:
    return get_runtime_environment() in _SAFE_BYPASS_ENVIRONMENTS and is_local_database()


def is_testing_bypass_requested() -> bool:
    return _env_true(TESTING_ENV_VAR)


def is_local_dev_auth_bypass_requested() -> bool:
    return _env_true(LOCAL_DEV_AUTH_BYPASS_ENV_VAR)


def is_legacy_skip_auth_requested() -> bool:
    return _env_true(LEGACY_SKIP_AUTH_ENV_VAR)


def is_testing_bypass_enabled() -> bool:
    return is_testing_bypass_requested() and is_safe_bypass_environment()


def is_local_dev_auth_bypass_enabled() -> bool:
    return (
        is_local_dev_auth_bypass_requested()
        and is_local_development_environment()
        and is_local_database()
    )


def get_auth_bypass_mode() -> str:
    if is_testing_bypass_enabled():
        return "testing"
    if is_local_dev_auth_bypass_enabled():
        return "local_dev"
    return "none"


def is_auth_bypass_enabled() -> bool:
    return get_auth_bypass_mode() != "none"


def get_auth_bypass_startup_error() -> str | None:
    if is_legacy_skip_auth_requested():
        return (
            "SKIP_AUTH is no longer supported. Use "
            "LOCAL_DEV_AUTH_BYPASS=true only for local development, or "
            "TESTING=true for explicit local/test runs."
        )

    if is_local_dev_auth_bypass_requested():
        if not is_local_development_environment():
            return (
                "LOCAL_DEV_AUTH_BYPASS is allowed only when ENVIRONMENT is "
                "development/dev/local."
            )
        if not is_local_database():
            return (
                "LOCAL_DEV_AUTH_BYPASS is allowed only with a local database "
                "(sqlite/localhost)."
            )

    if is_testing_bypass_requested() and not is_safe_bypass_environment():
        return (
            "TESTING auth bypass is allowed only with a local/test environment "
            "and a local database (sqlite/localhost)."
        )

    return None
