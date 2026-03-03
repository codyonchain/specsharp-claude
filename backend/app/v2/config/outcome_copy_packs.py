from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

OUTCOME_STATES = (
    "GO_STRONG",
    "GO_THIN",
    "NOGO_DEBT_PASSES",
    "NOGO_DEBT_FAILS",
)


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
    "drivers": {
        "dealshield": {},
        "executive": {},
    },
    "templates": {
        "dealshield": {},
        "executive": {},
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
            "cost basis and carry discipline under lease-up timing",
            "rent/concession elasticity versus expense growth",
        ],
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "Base case clears the policy threshold with durable cushion.",
                    "detail": "Primary monitoring drivers: cost basis and carry discipline under lease-up timing, plus rent/concession elasticity versus expense growth.",
                },
                "GO_THIN": {
                    "summary": "Base case clears the policy threshold, but cushion is thin.",
                    "detail": "Validate cost basis and carry discipline under lease-up timing, and rent/concession elasticity versus expense growth before commitment.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "Base case breaks the policy threshold (value gap non-positive), even with debt coverage clearing target.",
                    "detail": "Repair cost basis and carry discipline under lease-up timing, and rent/concession elasticity versus expense growth.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "Base case breaks the policy threshold and debt coverage is below target.",
                    "detail": "Repair cost basis and carry discipline under lease-up timing, rent/concession elasticity versus expense growth, and debt sizing assumptions.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: value support clears with cushion under current lease-up and expense assumptions. Keep diligence focused on basis and concession discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (thin cushion): policy clears, but break proximity is tight. Pressure-test lease-up carry and concession elasticity versus expense growth.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: value support breaks under current basis/carry assumptions even with debt coverage clearing target. Recut basis, concessions, and expense load assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: value support breaks and debt coverage is below target. Rework basis/carry assumptions and debt sizing together.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("multifamily", "luxury_apartments"): {
        "drivers_primary": [
            "amenity and finish-package scope discipline",
            "lease-up velocity and pricing power versus basis",
        ],
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "Base case clears the policy threshold with durable cushion.",
                    "detail": "Primary monitoring drivers: amenity and finish-package scope discipline, plus lease-up velocity and pricing power versus basis.",
                },
                "GO_THIN": {
                    "summary": "Base case clears the policy threshold, but cushion is thin.",
                    "detail": "Validate amenity and finish-package scope discipline, and lease-up velocity and pricing power versus basis before commitment.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "Base case breaks the policy threshold (value gap non-positive), even with debt coverage clearing target.",
                    "detail": "Repair amenity and finish-package scope discipline, and lease-up velocity and pricing power versus basis.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "Base case breaks the policy threshold and debt coverage is below target.",
                    "detail": "Repair amenity and finish-package scope discipline, lease-up velocity and pricing power versus basis, and debt sizing assumptions.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: value support clears with cushion under current luxury lease-up and pricing assumptions. Keep diligence focused on amenity scope and basis control.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (thin cushion): policy clears, but break proximity is tight. Pressure-test finish-package scope and pricing power versus basis.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: value support breaks under current luxury scope and basis assumptions even with debt coverage clearing target. Recut amenity scope and lease-up pricing assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: value support breaks and debt coverage is below target. Rework luxury scope/basis assumptions and debt sizing together.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("multifamily", "affordable_housing"): {
        "drivers_primary": [
            "compliance-driven scope and soft-cost drift",
            "capped-rent funding gap sensitivity under carry",
        ],
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "Base case clears the policy threshold with durable cushion.",
                    "detail": "Primary monitoring drivers: compliance-driven scope and soft-cost drift, plus capped-rent funding gap sensitivity under carry.",
                },
                "GO_THIN": {
                    "summary": "Base case clears the policy threshold, but cushion is thin.",
                    "detail": "Validate compliance-driven scope and soft-cost drift, and capped-rent funding gap sensitivity under carry before commitment.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "Base case breaks the policy threshold (value gap non-positive), even with debt coverage clearing target.",
                    "detail": "Repair compliance-driven scope and soft-cost drift, and capped-rent funding gap sensitivity under carry.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "Base case breaks the policy threshold and debt coverage is below target.",
                    "detail": "Repair compliance-driven scope and soft-cost drift, capped-rent funding gap sensitivity under carry, and debt sizing assumptions.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: value support clears with cushion under current capped-rent and compliance assumptions. Keep diligence focused on scope discipline and carry exposure.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (thin cushion): policy clears, but break proximity is tight. Pressure-test compliance scope drift and funding-gap sensitivity under carry.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: value support breaks under capped-rent funding assumptions even with debt coverage clearing target. Recut compliance scope and carry sensitivity assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: value support breaks and debt coverage is below target. Rework compliance scope/carry assumptions and debt sizing together.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
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


def _merge_pack(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge_pack(base[key], value)
        else:
            base[key] = deepcopy(value)


def _ensure_pack_shape(pack: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(pack.get("drivers_primary"), list) or not pack["drivers_primary"]:
        pack["drivers_primary"] = deepcopy(DEFAULT_PACK["drivers_primary"])
    if not isinstance(pack.get("drivers_secondary"), list):
        pack["drivers_secondary"] = deepcopy(DEFAULT_PACK["drivers_secondary"])
    if not isinstance(pack.get("label_overrides"), dict):
        pack["label_overrides"] = deepcopy(DEFAULT_PACK["label_overrides"])

    drivers = pack.get("drivers")
    if not isinstance(drivers, dict):
        drivers = {}
    for view_key in ("dealshield", "executive"):
        if not isinstance(drivers.get(view_key), dict):
            drivers[view_key] = {}
        for state_key, state_drivers in list(drivers[view_key].items()):
            if state_key not in OUTCOME_STATES or not isinstance(state_drivers, list):
                drivers[view_key].pop(state_key, None)
    pack["drivers"] = drivers

    templates = pack.get("templates")
    if not isinstance(templates, dict):
        templates = {}
    for view_key in ("dealshield", "executive"):
        if not isinstance(templates.get(view_key), dict):
            templates[view_key] = {}
        for state_key, state_template in list(templates[view_key].items()):
            if state_key not in OUTCOME_STATES or not isinstance(state_template, dict):
                templates[view_key].pop(state_key, None)
    pack["templates"] = templates

    return pack


def get_outcome_copy_pack(building_type: Any, subtype: Any) -> Dict[str, Any]:
    building_key = _normalize_key(building_type)
    subtype_key = _normalize_key(subtype)

    base_pack = deepcopy(DEFAULT_PACK)
    building_pack = BUILDING_TYPE_DEFAULT_PACKS.get(building_key)
    if isinstance(building_pack, dict):
        _merge_pack(base_pack, building_pack)
    subtype_pack = SUBTYPE_PACKS.get((building_key, subtype_key))
    if isinstance(subtype_pack, dict):
        _merge_pack(base_pack, subtype_pack)

    return _ensure_pack_shape(base_pack)
