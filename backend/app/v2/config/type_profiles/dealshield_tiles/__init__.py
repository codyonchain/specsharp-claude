"""DealShield tile registry (config-owned)."""

from . import civic
from . import educational
from . import healthcare
from . import hospitality
from . import industrial
from . import mixed_use
from . import multifamily
from . import office
from . import parking
from . import recreation
from . import restaurant
from . import retail
from . import specialty

CIVIC_TILE_PROFILE_ALIASES: dict[str, dict] = {
    "civic_baseline_v1": civic.DEALSHIELD_TILE_PROFILES["civic_library_v1"],
}

# Explicit aggregation for determinism (no filesystem scanning).
DEALSHIELD_TILE_PROFILE_SOURCES: list[dict] = [
    CIVIC_TILE_PROFILE_ALIASES,
    industrial.DEALSHIELD_TILE_PROFILES,
    healthcare.DEALSHIELD_TILE_PROFILES,
    restaurant.DEALSHIELD_TILE_PROFILES,
    hospitality.DEALSHIELD_TILE_PROFILES,
    civic.DEALSHIELD_TILE_PROFILES,
    educational.DEALSHIELD_TILE_PROFILES,
    mixed_use.DEALSHIELD_TILE_PROFILES,
    multifamily.DEALSHIELD_TILE_PROFILES,
    office.DEALSHIELD_TILE_PROFILES,
    parking.DEALSHIELD_TILE_PROFILES,
    recreation.DEALSHIELD_TILE_PROFILES,
    retail.DEALSHIELD_TILE_PROFILES,
    specialty.DEALSHIELD_TILE_PROFILES,
]

DEALSHIELD_TILE_DEFAULT_SOURCES: list[dict] = [
    industrial.DEALSHIELD_TILE_DEFAULTS,
    healthcare.DEALSHIELD_TILE_DEFAULTS,
    restaurant.DEALSHIELD_TILE_DEFAULTS,
    hospitality.DEALSHIELD_TILE_DEFAULTS,
    civic.DEALSHIELD_TILE_DEFAULTS,
    educational.DEALSHIELD_TILE_DEFAULTS,
    mixed_use.DEALSHIELD_TILE_DEFAULTS,
    multifamily.DEALSHIELD_TILE_DEFAULTS,
    office.DEALSHIELD_TILE_DEFAULTS,
    parking.DEALSHIELD_TILE_DEFAULTS,
    recreation.DEALSHIELD_TILE_DEFAULTS,
    retail.DEALSHIELD_TILE_DEFAULTS,
    specialty.DEALSHIELD_TILE_DEFAULTS,
]

from typing import Any, Dict

def get_dealshield_profile(profile_id: str) -> Dict[str, Any]:
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError("profile_id required")
    pid = profile_id.strip()

    sources = globals().get("DEALSHIELD_TILE_PROFILE_SOURCES")
    if not isinstance(sources, list) or not sources:
        raise RuntimeError("DEALSHIELD_TILE_PROFILE_SOURCES missing/empty")

    for src in sources:
        if isinstance(src, dict) and pid in src:
            prof = src[pid]
            if not isinstance(prof, dict):
                raise TypeError(f"DealShield profile must be dict for {pid}")
            if "profile_id" not in prof:
                prof = {**prof, "profile_id": pid}
            return prof

    raise KeyError(f"DealShield profile not found: {pid}")
