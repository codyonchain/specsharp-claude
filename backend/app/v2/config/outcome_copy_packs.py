from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple


def _normalize_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


DEFAULT_PACK: Dict[str, Any] = {
    "drivers_primary": [
        "cost basis discipline",
        "NOI durability",
    ],
    "drivers_secondary": [
        "debt sizing and rate assumptions",
        "policy break-threshold calibration",
    ],
    "label_overrides": {
        "dscr": "Debt Lens: DSCR",
    },
}


BUILDING_TYPE_DEFAULT_PACKS: Dict[str, Dict[str, Any]] = {
    "industrial": {
        "drivers_primary": [
            "basis and utility/service infrastructure",
            "stabilization ramp assumptions",
        ],
        "drivers_secondary": [
            "commissioning and turnover sequencing",
            "lease-up and absorption realism",
        ],
        "label_overrides": {"dscr": "Debt Lens: DSCR"},
    },
    "restaurant": {
        "drivers_primary": [
            "sales per SF throughput",
            "prime cost and occupancy burden",
        ],
        "drivers_secondary": [
            "prototype/buildout scope control",
            "opening-ramp realism",
        ],
        "label_overrides": {"dscr": "Debt Lens: DSCR"},
    },
    "multifamily": {
        "drivers_primary": [
            "basis and carry discipline",
            "rent-expense spread durability",
        ],
        "drivers_secondary": [
            "lease-up/concession pressure",
            "debt sizing and value support",
        ],
        "label_overrides": {"dscr": "Debt Lens: DSCR"},
    },
    "hospitality": {
        "drivers_primary": [
            "ADR/occupancy to NOI conversion",
            "program scope and value-benchmark support",
        ],
        "drivers_secondary": [
            "ramp timing and mix assumptions",
            "debt service coverage resilience",
        ],
        "label_overrides": {"dscr": "Debt Lens: DSCR"},
    },
}


SUBTYPE_PACKS: Dict[Tuple[str, str], Dict[str, Any]] = {
    ("industrial", "warehouse"): {
        "drivers_primary": [
            "sitework/civil and shell basis",
            "lease-up absorption shape",
        ],
    },
    ("industrial", "distribution_center"): {
        "drivers_primary": [
            "power density and sortation scope",
            "yard/dock sequencing and turnover",
        ],
    },
    ("industrial", "manufacturing"): {
        "drivers_primary": [
            "process MEP and utility loads",
            "commissioning/qualification ramp",
        ],
    },
    ("industrial", "cold_storage"): {
        "drivers_primary": [
            "refrigeration plant and envelope scope",
            "commissioning-to-stabilization ramp",
        ],
    },
    ("industrial", "flex_space"): {
        "drivers_primary": [
            "office/warehouse mix and finish scope",
            "tenant-mix lease-up carry",
        ],
    },
    ("restaurant", "quick_service"): {
        "drivers_primary": [
            "throughput/service-time capacity",
            "equipment/spec drift control",
        ],
    },
    ("restaurant", "full_service"): {
        "drivers_primary": [
            "turns/check under service-flow assumptions",
            "labor plus food prime-cost control",
        ],
    },
    ("restaurant", "fine_dining"): {
        "drivers_primary": [
            "check/mix conversion to NOI",
            "high-spec buildout and staffing discipline",
        ],
    },
    ("restaurant", "cafe"): {
        "drivers_primary": [
            "ticket/throughput consistency",
            "labor scheduling and occupancy burden",
        ],
    },
    ("restaurant", "bar_tavern"): {
        "drivers_primary": [
            "daypart mix and beverage margin",
            "labor/occupancy control",
        ],
    },
    ("multifamily", "market_rate_apartments"): {
        "drivers_primary": [
            "basis drift plus carry pressure",
            "lease-up/concession realism",
        ],
    },
    ("multifamily", "luxury_apartments"): {
        "drivers_primary": [
            "amenity/finish package scope",
            "lease-up velocity versus basis",
        ],
    },
    ("multifamily", "affordable_housing"): {
        "drivers_primary": [
            "compliance-driven scope/cost drift",
            "capped-rent funding-gap sensitivity",
        ],
    },
    ("hospitality", "limited_service_hotel"): {
        "drivers_primary": [
            "ADR/occupancy ramp",
            "FF&E scope and room-turn timing",
        ],
    },
    ("hospitality", "full_service_hotel"): {
        "drivers_primary": [
            "ADR mix with banquet/F&B program",
            "operator-driven fit-out scope",
        ],
    },
}


def get_outcome_copy_pack(building_type: Any, subtype: Any) -> Dict[str, Any]:
    building_key = _normalize_key(building_type)
    subtype_key = _normalize_key(subtype)

    base_pack = deepcopy(BUILDING_TYPE_DEFAULT_PACKS.get(building_key, DEFAULT_PACK))
    subtype_pack = SUBTYPE_PACKS.get((building_key, subtype_key))
    if isinstance(subtype_pack, dict):
        for key, value in subtype_pack.items():
            base_pack[key] = deepcopy(value)

    if not isinstance(base_pack.get("drivers_primary"), list) or not base_pack["drivers_primary"]:
        base_pack["drivers_primary"] = deepcopy(DEFAULT_PACK["drivers_primary"])
    if not isinstance(base_pack.get("drivers_secondary"), list):
        base_pack["drivers_secondary"] = deepcopy(DEFAULT_PACK["drivers_secondary"])
    if not isinstance(base_pack.get("label_overrides"), dict):
        base_pack["label_overrides"] = deepcopy(DEFAULT_PACK["label_overrides"])

    return base_pack
