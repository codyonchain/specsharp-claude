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
            "shell/civil basis and site constraints",
            "leasing assumptions and tenant improvement carry",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "shell/civil basis and site constraints",
                    "leasing assumptions and tenant improvement carry",
                ],
                "GO_THIN": [
                    "shell/civil basis drift under bids",
                    "lease-up timing and concessions under market softness",
                ],
                "NOGO_DEBT_PASSES": [
                    "basis and carry pressure versus market rent support",
                    "lease-up absorption realism and TI exposure",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and rent support before debt sizing",
                    "lease-up timing and capital stack resilience",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "shell/civil basis discipline",
                    "lease-up realism",
                ],
                "GO_THIN": [
                    "basis drift risk",
                    "lease-up/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis",
                    "absorption and TI exposure",
                ],
                "NOGO_DEBT_FAILS": [
                    "value support and debt sizing",
                    "carry and lease-up timing",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: shell/civil basis discipline and lease-up realism. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate shell/civil bids and lease-up timing/carry sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a basis/value-support break more than a lender-coverage break. Focus repairs on basis/carry drivers and absorption/TI exposure.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "Base case breaks the policy threshold and debt coverage is below target.",
                    "detail": "Primary repair drivers: sitework/civil and shell basis and lease-up absorption shape. Rework basis/NOI and debt terms before rerun.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on shell/civil basis and lease-up realism.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate bids (shell/civil) and lease-up/carry sensitivity before commit.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. This points to weak value support versus basis; repair basis/carry and absorption/TI exposure.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Repair basis/value support first, then adjust debt sizing/terms and timing assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("industrial", "distribution_center"): {
        "drivers_primary": [
            "yard/dock throughput assumptions and turnover sequencing",
            "power density and sortation/ESFR scope discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "yard/dock throughput assumptions and turnover sequencing",
                    "power density and sortation/ESFR scope discipline",
                ],
                "GO_THIN": [
                    "yard/dock cycle-time sensitivity under peak ops",
                    "sortation/power scope drift and commissioning timing",
                ],
                "NOGO_DEBT_PASSES": [
                    "power/sortation scope versus rent support",
                    "yard and dock sequencing under operational constraints",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on power/sortation scope",
                    "lease-up timing and debt sizing resilience",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "yard/dock throughput realism",
                    "power/sortation scope discipline",
                ],
                "GO_THIN": [
                    "cycle-time sensitivity",
                    "scope drift + commissioning timing",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs scope",
                    "operational sequencing realism",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "timing/carry resilience",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: yard/dock throughput realism and power/sortation scope control. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate yard/dock cycle-time assumptions and sortation/power scope + commissioning timing.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/value-support break driven by power/sortation scope and operational sequencing assumptions. Repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair value support first (basis reset on power/sortation scope), then rework debt sizing/terms and timing assumptions.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on yard/dock throughput realism and power/sortation scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate cycle-time assumptions and power/sortation scope + commissioning timing.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus scope; power/sortation scope and sequencing assumptions are forcing drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/value support first, then adjust debt sizing/terms and timing/carry assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("industrial", "manufacturing"): {
        "drivers_primary": [
            "process MEP scope and utility load assumptions",
            "commissioning/qualification ramp realism",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "process MEP scope and utility load assumptions",
                    "commissioning/qualification ramp realism",
                ],
                "GO_THIN": [
                    "utility/service capacity constraints and tie-ins",
                    "qualification timing versus carry and throughput ramp",
                ],
                "NOGO_DEBT_PASSES": [
                    "process MEP basis versus stabilized NOI support",
                    "qualification/ramp assumptions driving early NOI gap",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on process MEP + utility infrastructure",
                    "debt sizing versus ramp timing and stabilization risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "process MEP + utilities realism",
                    "qualification ramp discipline",
                ],
                "GO_THIN": [
                    "utility/tie-in constraints",
                    "qualification timing vs carry",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs process MEP basis",
                    "ramp assumptions driving NOI gap",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/stabilization risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: process MEP/utility assumptions and qualification-to-stabilization ramp realism.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate utility capacity/tie-ins and qualification timing versus carry and throughput ramp.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/NOI-support break driven by process MEP and ramp assumptions, not a pure lender-coverage failure.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair value support first (process MEP + utility infrastructure basis), then rework debt sizing/terms around ramp and stabilization risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on process MEP/utility assumptions and qualification ramp realism.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate utility/tie-in constraints and qualification timing versus carry and ramp.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus process MEP basis and ramp assumptions driving NOI support.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset process MEP/utility basis first, then adjust debt sizing/terms around ramp/stabilization risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("industrial", "cold_storage"): {
        "drivers_primary": [
            "refrigeration plant and envelope scope discipline",
            "utility load/rate assumptions and redundancy readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "refrigeration plant and envelope scope discipline",
                    "utility load/rate assumptions and redundancy readiness",
                ],
                "GO_THIN": [
                    "commissioning-to-stabilization ramp assumptions",
                    "utility constraints and refrigeration package inclusions",
                ],
                "NOGO_DEBT_PASSES": [
                    "refrigeration/envelope basis versus rate support",
                    "ramp timing and utility cost assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on refrigeration + envelope package",
                    "debt sizing versus ramp timing and utility cost risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "refrigeration/envelope scope discipline",
                    "utility load/rate + redundancy readiness",
                ],
                "GO_THIN": [
                    "commissioning-to-stabilization ramp",
                    "utility constraints + package inclusions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs refrigeration basis",
                    "ramp + utility cost driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/utility cost risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: refrigeration/envelope scope discipline and utility load/rate assumptions. Cold storage risk is commissioning and power-driven.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate commissioning-to-stabilization ramp and refrigeration package inclusions (vendor vs GC carry) + utility constraints.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by refrigeration/envelope basis and ramp/utility cost assumptions, not dock/truck flow.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair refrigeration/envelope basis and ramp/utility assumptions first, then adjust debt sizing/terms around stabilization risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on refrigeration/envelope scope and utility load/rate assumptions.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate commissioning ramp and refrigeration package inclusions + utility constraints.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus refrigeration/envelope basis and ramp/utility cost assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset refrigeration/envelope basis first, then rework debt sizing/terms around ramp and utility cost risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("industrial", "flex_space"): {
        "drivers_primary": [
            "office/showroom mix and finish standard discipline",
            "tenant mix, demising flexibility, and TI exposure",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "office/showroom mix and finish standard discipline",
                    "tenant mix, demising flexibility, and TI exposure",
                ],
                "GO_THIN": [
                    "finish/TI drift under tenant-specific buildouts",
                    "lease-up timing and tenant-mix carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "basis versus blended rent support across tenant mix",
                    "TI/finish exposure and demising-driven volatility",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and TI exposure control",
                    "debt sizing versus lease-up timing and carry",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "office/finish discipline",
                    "tenant-mix + TI exposure",
                ],
                "GO_THIN": [
                    "tenant-specific TI drift",
                    "lease-up/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs blended rent",
                    "TI exposure + demising volatility",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "lease-up timing/carry",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: office/finish discipline and tenant-mix/TI exposure control. Flex risk is mainly tenant-driven, not pure logistics.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate tenant-specific TI/finish drift and lease-up timing under tenant-mix volatility.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/blended-rent support break driven by TI/finish exposure and demising/tenant-mix volatility.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis/value support first, then rework debt sizing/terms. Lease-up timing and TI exposure are forcing drivers.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on office/finish discipline and tenant-mix/TI exposure.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate tenant-specific TI/finish drift and lease-up/carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus basis; blended rent support and TI/finish exposure are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/value support first, then adjust debt sizing/terms and timing assumptions.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
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
