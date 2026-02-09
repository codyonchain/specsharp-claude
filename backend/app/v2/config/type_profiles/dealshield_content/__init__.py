"""DealShield content registry (config-owned)."""

from typing import Any, Dict

from . import civic
from . import healthcare
from . import hospitality
from . import industrial
from . import restaurant

CIVIC_CONTENT_PROFILE_ALIASES: dict[str, dict] = {
    "civic_baseline_v1": {
        **civic.DEALSHIELD_CONTENT_PROFILES["civic_library_v1"],
        "profile_id": "civic_baseline_v1",
    },
}

# Explicit aggregation for determinism (no filesystem scanning).
DEALSHIELD_CONTENT_PROFILE_SOURCES: list[dict] = [
    industrial.DEALSHIELD_CONTENT_PROFILES,
    healthcare.DEALSHIELD_CONTENT_PROFILES,
    restaurant.DEALSHIELD_CONTENT_PROFILES,
    hospitality.DEALSHIELD_CONTENT_PROFILES,
    civic.DEALSHIELD_CONTENT_PROFILES,
    CIVIC_CONTENT_PROFILE_ALIASES,
]


def get_dealshield_content_profile(profile_id: str) -> Dict[str, Any]:
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError("profile_id required")
    pid = profile_id.strip()

    sources = globals().get("DEALSHIELD_CONTENT_PROFILE_SOURCES")
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("DEALSHIELD_CONTENT_PROFILE_SOURCES missing/empty")

    for src in sources:
        if isinstance(src, dict) and pid in src:
            profile = src[pid]
            if not isinstance(profile, dict):
                raise TypeError(f"DealShield content profile must be dict for {pid}")
            if "profile_id" not in profile:
                profile = {**profile, "profile_id": pid}
            return profile

    raise KeyError(f"DealShield content profile not found: {pid}")
