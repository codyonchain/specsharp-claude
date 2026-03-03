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
            "peak-hour throughput and service-time assumptions",
            "equipment/spec package inclusions and lead-time risk",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "peak-hour throughput and service-time assumptions",
                    "equipment/spec package inclusions and lead-time risk",
                ],
                "GO_THIN": [
                    "drive-thru constraint point (order/window/kitchen line)",
                    "opening ramp realism and labor scheduling coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "sales density to NOI conversion under prime cost burden",
                    "prototype/spec drift and equipment package carry exposure",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset (buildout + equipment) and occupancy burden",
                    "lender coverage resilience under ramp and prime cost risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "throughput/service-time realism",
                    "equipment/spec discipline",
                ],
                "GO_THIN": [
                    "constraint point + ramp risk",
                    "labor scheduling coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion vs prime cost",
                    "spec/equipment drift exposure",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + prime cost risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: throughput/service-time assumptions and equipment/spec package control. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate peak-hour cars/hour (or tickets/hour), service-time targets, and equipment OFI vs GC carry before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as unit-economics/value-support break driven by NOI conversion (prime cost + occupancy burden) and spec/equipment drift; repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair buildout/equipment basis and NOI conversion first, then rework debt sizing/terms. Ramp and service-time assumptions are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on throughput/service-time realism and equipment/spec discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate peak-hour throughput + service time, and equipment OFI vs GC carry.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI conversion (prime cost + occupancy burden) and spec/equipment drift exposure.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and prime-cost risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("restaurant", "full_service"): {
        "drivers_primary": [
            "turns/check assumptions and service-flow capacity",
            "labor + food prime-cost control and occupancy burden",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "turns/check assumptions and service-flow capacity",
                    "labor + food prime-cost control and occupancy burden",
                ],
                "GO_THIN": [
                    "opening ramp realism (turns, staffing, mix stabilization)",
                    "buildout scope discipline (BOH line, bar, finishes, equipment)",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion under prime cost and occupancy burden",
                    "basis discipline under high-variability buildout scope",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and margin protection before debt sizing",
                    "coverage resilience under ramp and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "turns/check + service-flow realism",
                    "prime cost + occupancy discipline",
                ],
                "GO_THIN": [
                    "ramp/mix stabilization",
                    "buildout scope variability",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion vs prime cost",
                    "basis discipline under scope churn",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: turns/check assumptions and prime-cost/occupancy burden control. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate service-flow capacity (tables/turns), staffing plan, and buildout/equipment scope inclusions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as unit-economics/value-support break driven by NOI conversion (prime cost + occupancy) and scope/basis drift; repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms. Ramp and staffing volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on turns/check realism and prime-cost/occupancy discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate service-flow capacity, staffing plan, and buildout/equipment scope inclusions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI conversion (prime cost + occupancy) and basis discipline under scope churn.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("restaurant", "fine_dining"): {
        "drivers_primary": [
            "reservation mix and check-to-NOI conversion assumptions",
            "labor intensity, beverage mix, and occupancy burden control",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "reservation mix and check-to-NOI conversion assumptions",
                    "labor intensity, beverage mix, and occupancy burden control",
                ],
                "GO_THIN": [
                    "ramp-to-stabilization timing (reservations, staffing, mix)",
                    "high-spec buildout/equipment inclusions and change-order risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion under labor intensity and mix volatility",
                    "basis discipline under high-spec buildout scope",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and margin protection before debt sizing",
                    "coverage resilience under ramp timing and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "check-to-NOI conversion realism",
                    "labor/mix + occupancy discipline",
                ],
                "GO_THIN": [
                    "ramp timing + mix stabilization",
                    "high-spec scope drift risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion under labor intensity",
                    "basis discipline under high-spec scope",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: check-to-NOI conversion realism and labor/mix + occupancy burden control.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate reservation/mix ramp timing and high-spec buildout/equipment inclusions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as unit-economics/value-support break driven by NOI conversion (labor intensity + mix volatility) and high-spec basis drift; repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms. Ramp timing and staffing volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on check-to-NOI conversion and labor/mix + occupancy discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate reservation/mix ramp timing and high-spec buildout/equipment inclusions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI conversion (labor intensity + mix) and high-spec basis discipline.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("restaurant", "cafe"): {
        "drivers_primary": [
            "morning peak throughput and queue/service-time assumptions",
            "labor scheduling discipline and occupancy burden control",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "morning peak throughput and queue/service-time assumptions",
                    "labor scheduling discipline and occupancy burden control",
                ],
                "GO_THIN": [
                    "espresso line/equipment readiness and commissioning risk",
                    "daypart mix stabilization and staffing coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion under labor/occupancy burden",
                    "equipment inclusions and downtime/ramp risk",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under ramp and labor volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "peak throughput + service-time realism",
                    "labor/occupancy discipline",
                ],
                "GO_THIN": [
                    "equipment readiness/commissioning",
                    "daypart mix + staffing coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion vs labor/occupancy",
                    "equipment inclusions + ramp risk",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + labor volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: morning peak throughput realism and labor/occupancy burden control. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate espresso line/equipment readiness, queue/service-time assumptions, and daypart mix stabilization.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as unit-economics/value-support break driven by NOI conversion (labor + occupancy), ticket/throughput consistency, and equipment/ramp assumptions; repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms. Ramp and labor volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on peak throughput/service time and labor/occupancy discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate equipment readiness/commissioning and morning peak queue/service-time assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI conversion (labor + occupancy) and equipment/ramp assumptions driving value support.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and labor volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("restaurant", "bar_tavern"): {
        "drivers_primary": [
            "daypart mix and beverage margin durability",
            "labor/security intensity and occupancy burden control",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "daypart mix and beverage margin durability",
                    "labor/security intensity and occupancy burden control",
                ],
                "GO_THIN": [
                    "weekend volatility and event-driven demand sensitivity",
                    "licensing/compliance constraints and staffing coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion under mix volatility and labor/security burden",
                    "occupancy burden versus sales density and ramp risk",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under volatility and compliance/staffing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "mix + beverage margin durability",
                    "labor/security + occupancy discipline",
                ],
                "GO_THIN": [
                    "volatility sensitivity",
                    "licensing + staffing coverage",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI conversion vs volatility",
                    "occupancy burden vs sales density",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "volatility + compliance risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: daypart mix/beverage margin durability and labor/security + occupancy burden control.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate weekend volatility sensitivity, licensing/compliance constraints, and staffing coverage assumptions.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as unit-economics/value-support break driven by mix volatility and labor/security + occupancy burden; repair those before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms. Volatility and compliance/staffing risks are forcing drivers.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on mix/beverage margin durability and labor/security + occupancy discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate volatility sensitivity, licensing constraints, and staffing coverage assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI conversion under volatility (mix/margin) and labor/security + occupancy burden.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around volatility and compliance risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
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
            "ADR/occupancy ramp assumptions to NOI conversion",
            "FF&E scope and rooms turnover timing discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "ADR/occupancy ramp assumptions to NOI conversion",
                    "FF&E scope and rooms turnover timing discipline",
                ],
                "GO_THIN": [
                    "RevPAR sensitivity under rate/occupancy volatility",
                    "FF&E refresh timing and pre-opening cost control",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI support versus basis under RevPAR assumptions",
                    "ramp-to-stabilization timing and cost leakage drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under ramp and RevPAR volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "ADR/occupancy->NOI realism",
                    "FF&E/turnover discipline",
                ],
                "GO_THIN": [
                    "RevPAR sensitivity",
                    "pre-open/FF&E timing risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs RevPAR NOI",
                    "ramp timing + cost leakage",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + RevPAR volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: ADR/occupancy ramp realism and FF&E + rooms turnover timing discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate RevPAR sensitivity (rate/occupancy), ramp-to-stabilization timing, and FF&E/pre-opening cost control before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by RevPAR-to-NOI conversion and ramp timing/cost leakage, not a pure lender-coverage failure. Repair those assumptions before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis/value support and NOI conversion first, then rework debt sizing/terms. Ramp timing and RevPAR volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on ADR/occupancy-to-NOI realism and FF&E/turnover discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate RevPAR sensitivity, ramp timing, and FF&E/pre-opening cost control.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-RevPAR-to-NOI conversion and ramp/cost leakage drivers are primary.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and RevPAR volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("hospitality", "full_service_hotel"): {
        "drivers_primary": [
            "ADR mix and group/banquet/F&B program to NOI conversion",
            "operator-driven fit-out scope discipline (ballroom/F&B/back-of-house)",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "ADR mix and group/banquet/F&B program to NOI conversion",
                    "operator-driven fit-out scope discipline (ballroom/F&B/back-of-house)",
                ],
                "GO_THIN": [
                    "mix volatility and ramp timing (group base, transient, banquet capture)",
                    "labor intensity and departmental margin protection",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus operator program scope and mix assumptions",
                    "ramp timing and labor/margin leakage driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on operator-driven fit-out scope",
                    "debt sizing resilience under ramp and mix/labor volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "mix->NOI realism (rooms + F&B/banquet)",
                    "operator scope discipline",
                ],
                "GO_THIN": [
                    "mix/ramp volatility",
                    "labor intensity + margin protection",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs operator scope",
                    "ramp + labor/margin leakage",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + mix/labor volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: ADR/mix-to-NOI conversion and operator-driven fit-out scope discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate mix/ramp timing (group base + banquet capture), labor intensity, and operator program scope inclusions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a policy/value-support break dominated by operator program scope, mix assumptions, and labor/margin leakage-not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair operator-driven scope/basis and NOI conversion first, then rework debt sizing/terms. Ramp timing and mix/labor volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on mix-to-NOI conversion and operator-driven program scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate mix/ramp timing, labor intensity, and operator-driven fit-out scope inclusions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-operator scope, mix assumptions, and labor/margin leakage are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset operator scope/basis first, then adjust debt sizing/terms around ramp timing and mix/labor volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("specialty", "data_center"): {
        "drivers_primary": [
            "power train and cooling scope discipline (switchgear/UPS/chillers)",
            "utility interconnect timing and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "power train and cooling scope discipline (switchgear/UPS/chillers)",
                    "utility interconnect timing and commissioning readiness",
                ],
                "GO_THIN": [
                    "redundancy scope drift and OFI vs GC carry boundaries",
                    "commissioning-to-stabilization ramp assumptions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus power/cooling basis",
                    "timeline/commissioning assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on power/cooling scope",
                    "debt sizing resilience under utility/timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "power/cooling scope discipline",
                    "utility timing + commissioning readiness",
                ],
                "GO_THIN": [
                    "redundancy/OFI scope drift",
                    "commissioning ramp risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs power/cooling basis",
                    "timing/commissioning NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "utility/timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: power/cooling scope discipline and utility interconnect + commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate redundancy scope boundaries (OFI vs GC carry), utility interconnect timing, and commissioning-to-stabilization ramp assumptions.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by power/cooling basis and commissioning/timing assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair power/cooling basis and commissioning/timing assumptions first, then rework debt sizing/terms around utility/timeline risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on power/cooling scope discipline and utility timing + commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate redundancy/OFI scope boundaries and commissioning + utility timing assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus power/cooling basis and commissioning/timing assumptions driving NOI support.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset power/cooling basis first, then adjust debt sizing/terms around utility/timeline risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("specialty", "laboratory"): {
        "drivers_primary": [
            "MEP intensity and HVAC/controls scope discipline",
            "validation/commissioning readiness and turnover sequencing",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "MEP intensity and HVAC/controls scope discipline",
                    "validation/commissioning readiness and turnover sequencing",
                ],
                "GO_THIN": [
                    "clean utilities and redundancy inclusions (scope boundaries)",
                    "qualification timeline assumptions versus carry and ramp",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus lab MEP basis",
                    "validation timeline and operating assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on lab MEP/controls scope",
                    "debt sizing resilience under qualification timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "lab MEP/HVAC scope discipline",
                    "validation + turnover readiness",
                ],
                "GO_THIN": [
                    "scope boundary risk (clean utilities)",
                    "qualification timing vs carry",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs lab MEP basis",
                    "timeline/ops assumptions NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "qualification timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: lab MEP/HVAC scope discipline and validation/commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate clean-utility inclusions, HVAC/controls scope boundaries, and qualification timeline assumptions versus carry/ramp.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by lab MEP basis and validation timeline assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair lab MEP/controls basis and qualification/timeline assumptions first, then rework debt sizing/terms around turnover risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on lab MEP/HVAC scope discipline and validation/turnover readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate scope boundaries (clean utilities/HVAC/controls) and qualification timing versus carry.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support versus lab MEP basis and validation/timeline assumptions driving NOI support.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset lab MEP basis first, then adjust debt sizing/terms around qualification and turnover risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("specialty", "self_storage"): {
        "drivers_primary": [
            "unit mix yield and achieved rate assumptions",
            "security/access control and climate-control scope discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "unit mix yield and achieved rate assumptions",
                    "security/access control and climate-control scope discipline",
                ],
                "GO_THIN": [
                    "lease-up velocity and competitive pricing sensitivity",
                    "climate-control scope and operating cost assumptions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under achieved rates",
                    "lease-up timing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and rate support before debt sizing",
                    "coverage resilience under lease-up and competition risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "unit mix + rate realism",
                    "security/climate scope discipline",
                ],
                "GO_THIN": [
                    "lease-up velocity sensitivity",
                    "opex/climate scope risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "lease-up timing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "lease-up/competition risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: unit-mix yield/achieved rates and security/climate scope discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate lease-up velocity assumptions, competitive pricing sensitivity, and climate-control scope/opex assumptions.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by achieved rates/unit-mix yield and lease-up timing assumptions. Repair rate support and timing drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair rate support and lease-up timing first, then rework debt sizing/terms. Competition sensitivity and operating assumptions are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on unit-mix/rate realism and security/climate scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate lease-up velocity, competitive pricing sensitivity, and climate-control scope/opex assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-achieved rates/unit mix and lease-up timing assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset rate support/lease-up assumptions first, then adjust debt sizing/terms around competition and opex risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("specialty", "car_dealership"): {
        "drivers_primary": [
            "OEM program compliance and showroom/brand standard scope",
            "service bay productivity assumptions and site/circulation constraints",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "OEM program compliance and showroom/brand standard scope",
                    "service bay productivity assumptions and site/circulation constraints",
                ],
                "GO_THIN": [
                    "scope drift under OEM change orders and finish standards",
                    "service/parts throughput ramp assumptions versus labor burden",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus OEM-driven scope/basis",
                    "service throughput and margin assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset under OEM scope requirements",
                    "debt sizing resilience under ramp and margin volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "OEM scope compliance",
                    "service throughput realism",
                ],
                "GO_THIN": [
                    "OEM change-order drift risk",
                    "throughput ramp vs labor burden",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs OEM basis",
                    "service NOI support assumptions",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + margin volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: OEM program scope compliance and service throughput realism. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate OEM scope inclusions/change-order exposure, service bay productivity assumptions, and site/circulation constraints.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by OEM scope/basis and service NOI assumptions, not a pure lender-coverage failure. Repair scope/basis and throughput drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair OEM-driven basis and service NOI support first, then rework debt sizing/terms. Ramp timing and margin volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on OEM scope compliance and service throughput realism.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate OEM change-order exposure, service bay productivity, and site/circulation constraints.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-OEM scope/basis and service NOI assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset OEM-driven basis first, then adjust debt sizing/terms around ramp and margin volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("specialty", "broadcast_facility"): {
        "drivers_primary": [
            "acoustics/isolation and RF/shielding scope discipline",
            "power/UPS/generator and cooling readiness for equipment loads",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "acoustics/isolation and RF/shielding scope discipline",
                    "power/UPS/generator and cooling readiness for equipment loads",
                ],
                "GO_THIN": [
                    "commissioning/testing scope and turnover sequencing",
                    "specialty MEP inclusions (isolation, grounding, redundancy)",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus specialty scope/basis (acoustics/RF/power)",
                    "commissioning/timing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty acoustics/RF/power scope",
                    "debt sizing resilience under commissioning and timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "acoustics/RF scope discipline",
                    "power/cooling readiness",
                ],
                "GO_THIN": [
                    "commissioning/testing sequencing",
                    "specialty inclusions risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs specialty basis",
                    "timing/commissioning NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "commissioning/timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: acoustics/RF scope discipline and power/cooling readiness for equipment loads. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate acoustics/RF inclusions, grounding/redundancy scope boundaries, and commissioning/testing sequencing before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by specialty acoustics/RF/power scope and commissioning/timing assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair specialty scope/basis and commissioning/timing assumptions first, then rework debt sizing/terms around turnover and load-risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on acoustics/RF scope discipline and power/cooling readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate acoustics/RF inclusions and commissioning/testing sequencing before commit.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-specialty scope/basis and commissioning/timing assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset specialty scope/basis first, then adjust debt sizing/terms around commissioning and turnover risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "surgical_center"): {
        "drivers_primary": [
            "OR/PACU program scope and sterile processing requirements",
            "med gas, infection control, and commissioning/turnover readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "OR/PACU program scope and sterile processing requirements",
                    "med gas, infection control, and commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "equipment/vendor inclusions and program-driven scope drift",
                    "commissioning-to-opening timeline assumptions versus carry",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus clinical program basis",
                    "throughput/ramp and staffing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on clinical program + MEP scope",
                    "debt sizing resilience under ramp and turnover risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program scope (OR/PACU/sterile)",
                    "commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "vendor inclusions drift risk",
                    "timeline vs carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs program basis",
                    "ramp/staffing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/turnover risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: clinical program scope (OR/PACU/sterile) and commissioning/turnover readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate vendor inclusions (equipment vs GC carry), program-driven scope drift, and commissioning-to-opening timeline assumptions.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by clinical program basis and ramp/staffing assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair program/MEP basis and ramp assumptions first, then rework debt sizing/terms around turnover risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on clinical program scope and commissioning/turnover readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate vendor inclusions, scope drift, and commissioning-to-opening timeline assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-program basis and ramp/staffing NOI assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset program/MEP basis first, then adjust debt sizing/terms around ramp and turnover risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "imaging_center"): {
        "drivers_primary": [
            "shielding/buildout scope and equipment vendor inclusions",
            "power/HVAC readiness and calibration/commissioning plan",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "shielding/buildout scope and equipment vendor inclusions",
                    "power/HVAC readiness and calibration/commissioning plan",
                ],
                "GO_THIN": [
                    "equipment lead times and OFI vs GC carry boundaries",
                    "commissioning/calibration timing versus opening ramp",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus imaging buildout/equipment basis",
                    "volume ramp assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on equipment/buildout scope",
                    "debt sizing resilience under volume and timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "vendor inclusions + shielding scope",
                    "power/HVAC + commissioning readiness",
                ],
                "GO_THIN": [
                    "lead-time/OFI drift risk",
                    "calibration timing vs ramp",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "volume ramp NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "volume/timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: vendor inclusions/shielding scope and power/HVAC + calibration readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate equipment lead times, OFI vs GC carry boundaries, and commissioning/calibration timing before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by imaging buildout/equipment basis and volume ramp assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and ramp assumptions first, then rework debt sizing/terms around timing and volume risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on vendor inclusions/shielding scope and commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate lead times/OFI boundaries and calibration timing versus opening ramp.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-basis and volume ramp assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around timing and volume risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "urgent_care"): {
        "drivers_primary": [
            "visit volume/throughput assumptions and staffing coverage",
            "standardized buildout scope and reimbursement/collections timing",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "visit volume/throughput assumptions and staffing coverage",
                    "standardized buildout scope and reimbursement/collections timing",
                ],
                "GO_THIN": [
                    "ramp-to-stabilization timing (volume + staffing)",
                    "scope drift under landlord conditions and MEP tie-ins",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under visit volume assumptions",
                    "collections timing and staffing cost burden driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under ramp and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "volume/staffing realism",
                    "buildout standardization + collections timing",
                ],
                "GO_THIN": [
                    "ramp timing risk",
                    "scope/MEP tie-in drift",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "staffing/collections NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: visit volume/throughput realism and staffing coverage, plus standardized buildout scope discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate ramp timing (volume + staffing), landlord/MEP tie-ins, and collections timing assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by NOI conversion (volume x staffing x collections timing) and basis, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms around ramp and staffing volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on volume/staffing realism and standardized buildout scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate ramp timing, staffing coverage, and MEP/landlord tie-in scope risk.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-NOI conversion (volume/staffing/collections) and basis are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "outpatient_clinic"): {
        "drivers_primary": [
            "program mix and room utilization assumptions",
            "staffing coverage and MEP scope discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program mix and room utilization assumptions",
                    "staffing coverage and MEP scope discipline",
                ],
                "GO_THIN": [
                    "ramp timing and provider productivity assumptions",
                    "buildout inclusions and landlord/MEP tie-in risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under utilization assumptions",
                    "NOI support driven by staffing and reimbursement timing",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under ramp and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/utilization realism",
                    "staffing + MEP scope discipline",
                ],
                "GO_THIN": [
                    "provider productivity ramp",
                    "tie-in/inclusions risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "staffing/reimbursement NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/utilization realism and staffing + buildout scope discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate provider productivity ramp, buildout inclusions, and landlord/MEP tie-ins before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by utilization/NOI conversion and basis, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms around ramp and staffing volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on utilization assumptions and staffing/buildout scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate ramp timing, provider productivity, and tie-in/inclusions risk.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-utilization/NOI conversion and basis are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/NOI conversion first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "medical_office_building"): {
        "drivers_primary": [
            "leasing velocity and tenant improvement exposure",
            "MEP/vertical distribution scope and common-area basis discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "leasing velocity and tenant improvement exposure",
                    "MEP/vertical distribution scope and common-area basis discipline",
                ],
                "GO_THIN": [
                    "TI allowances and specialty tenant buildout variability",
                    "lease-up timing and carry sensitivity under absorption risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under leasing assumptions",
                    "TI exposure and timing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and leasing support before debt sizing",
                    "coverage resilience under TI and absorption risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "leasing + TI exposure realism",
                    "MEP/common-area basis discipline",
                ],
                "GO_THIN": [
                    "TI variability risk",
                    "lease-up/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "TI/timing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "absorption/TI risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: leasing velocity and TI exposure realism, plus MEP/common-area basis discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate TI allowance exposure, specialty tenant variability, and lease-up/carry sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by leasing/TI assumptions and basis, not a pure lender-coverage failure. Repair leasing support and TI exposure drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and leasing support first, then rework debt sizing/terms around absorption and TI exposure risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on leasing/TI exposure realism and MEP/common-area basis discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate TI variability, allowance exposure, and lease-up/carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-leasing/TI assumptions and basis are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/leasing support first, then adjust debt sizing/terms around absorption and TI risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "dental_office"): {
        "drivers_primary": [
            "operatory count and equipment inclusions (chairs, suction, compressors)",
            "sterilization flow and MEP readiness/commissioning",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "operatory count and equipment inclusions (chairs, suction, compressors)",
                    "sterilization flow and MEP readiness/commissioning",
                ],
                "GO_THIN": [
                    "equipment lead times and OFI vs GC carry boundaries",
                    "opening ramp and staffing coverage assumptions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus dental buildout/equipment basis",
                    "volume and staffing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on buildout/equipment scope",
                    "debt sizing resilience under ramp and staffing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "equipment inclusions + operatory realism",
                    "MEP/commissioning readiness",
                ],
                "GO_THIN": [
                    "lead-time/OFI drift risk",
                    "ramp/staffing sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "volume/staffing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/staffing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: operatory/equipment inclusions and MEP/commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate equipment lead times, OFI vs GC carry boundaries, and opening ramp/staffing assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by buildout/equipment basis and volume/staffing assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and ramp assumptions first, then rework debt sizing/terms around staffing and timing risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on operatory/equipment inclusions and commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate lead times/OFI boundaries and ramp/staffing assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-basis and volume/staffing assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around ramp and staffing risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "hospital"): {
        "drivers_primary": [
            "clinical program scope (ED/ICU/OR) and MEP intensity discipline",
            "phasing/turnover sequencing and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "clinical program scope (ED/ICU/OR) and MEP intensity discipline",
                    "phasing/turnover sequencing and commissioning readiness",
                ],
                "GO_THIN": [
                    "regulatory/life-safety constraints and scope boundary risk",
                    "schedule/carry sensitivity under phased construction complexity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus program/MEP basis",
                    "phasing and commissioning timeline assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on program/MEP scope",
                    "debt sizing resilience under phasing and schedule risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/MEP scope discipline",
                    "phasing + commissioning readiness",
                ],
                "GO_THIN": [
                    "regulatory/scope boundary risk",
                    "schedule/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs program basis",
                    "timeline/phasing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "phasing/schedule risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/MEP scope discipline and phasing/commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate regulatory/life-safety scope boundaries and schedule/carry sensitivity under phased complexity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by program/MEP basis and phasing/commissioning timeline assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair program/MEP basis and timeline assumptions first, then rework debt sizing/terms around phasing and schedule risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/MEP scope discipline and phasing/commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate regulatory scope boundaries and schedule/carry sensitivity under phasing complexity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-program/MEP basis and phasing timeline assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset program basis first, then adjust debt sizing/terms around phasing and schedule risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "medical_center"): {
        "drivers_primary": [
            "program scope mix (clinic + imaging + procedure) and MEP intensity discipline",
            "turnover sequencing and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope mix (clinic + imaging + procedure) and MEP intensity discipline",
                    "turnover sequencing and commissioning readiness",
                ],
                "GO_THIN": [
                    "program-driven equipment inclusions and scope boundary risk",
                    "schedule/carry sensitivity under multi-service complexity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus mixed-program basis",
                    "ramp and staffing assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on mixed-program scope",
                    "debt sizing resilience under ramp and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/MEP scope discipline",
                    "turnover + commissioning readiness",
                ],
                "GO_THIN": [
                    "equipment inclusions drift risk",
                    "schedule/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "ramp/staffing NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: mixed-program scope discipline and commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate equipment inclusions/scope boundaries and schedule/carry sensitivity under multi-service complexity.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by mixed-program basis and ramp/staffing assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair program basis and NOI conversion first, then rework debt sizing/terms around ramp and staffing volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on mixed-program scope discipline and commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate equipment inclusions/scope boundaries and schedule/carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support-mixed-program basis and ramp/staffing assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset program basis first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "nursing_home"): {
        "drivers_primary": [
            "staffing ratios and wage inflation sensitivity",
            "reimbursement mix and occupancy stability assumptions",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "staffing ratios and wage inflation sensitivity",
                    "reimbursement mix and occupancy stability assumptions",
                ],
                "GO_THIN": [
                    "clinical/life-safety compliance scope and operating cost drift",
                    "occupancy stability and payer-mix volatility",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI support versus basis under staffing cost burden",
                    "reimbursement and occupancy assumptions driving value support",
                ],
                "NOGO_DEBT_FAILS": [
                    "NOI conversion and staffing burden before debt sizing",
                    "coverage resilience under payer mix and occupancy volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "staffing cost burden realism",
                    "reimbursement/occupancy stability",
                ],
                "GO_THIN": [
                    "compliance/opex drift risk",
                    "payer/occupancy volatility",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI support vs staffing burden",
                    "reimbursement/occupancy value support",
                ],
                "NOGO_DEBT_FAILS": [
                    "NOI conversion + debt sizing",
                    "payer/occupancy volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: staffing cost burden and reimbursement/occupancy stability. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate staffing ratios/wage inflation sensitivity, compliance scope drift, and payer/occupancy volatility assumptions.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as NOI-support/value-support break driven by staffing burden and reimbursement/occupancy assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair NOI conversion (staffing + reimbursement) first, then rework debt sizing/terms around occupancy and payer-mix volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on staffing burden realism and reimbursement/occupancy stability.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate staffing/wage sensitivity, compliance scope drift, and payer/occupancy volatility.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI support-staffing burden and reimbursement/occupancy assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset NOI conversion first, then adjust debt sizing/terms around payer mix and occupancy volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("healthcare", "rehabilitation"): {
        "drivers_primary": [
            "therapy program mix and staffing coverage assumptions",
            "length-of-stay and reimbursement timing to NOI conversion",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "therapy program mix and staffing coverage assumptions",
                    "length-of-stay and reimbursement timing to NOI conversion",
                ],
                "GO_THIN": [
                    "ramp-to-stabilization timing (census + staffing)",
                    "equipment/program scope and operating cost drift risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI support versus basis under staffing burden",
                    "census/ramp and reimbursement assumptions driving value support",
                ],
                "NOGO_DEBT_FAILS": [
                    "NOI conversion and basis reset before debt sizing",
                    "coverage resilience under ramp and staffing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program mix + staffing realism",
                    "reimbursement/LOS NOI conversion",
                ],
                "GO_THIN": [
                    "census ramp timing",
                    "program/opex drift risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "NOI support vs staffing burden",
                    "census/ramp value support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp + staffing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: therapy program mix/staffing realism and reimbursement-to-NOI conversion. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate census ramp timing, staffing coverage, and program/operating-cost drift assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as NOI-support/value-support break driven by staffing burden and census/ramp assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair NOI conversion and ramp assumptions first, then rework debt sizing/terms around staffing volatility and reimbursement timing risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program mix/staffing realism and reimbursement-to-NOI conversion.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate census ramp timing, staffing coverage, and operating-cost drift assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair NOI support-staffing burden and census/ramp assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset NOI conversion first, then adjust debt sizing/terms around ramp and staffing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("educational", "elementary_school"): {
        "drivers_primary": [
            "program scope discipline (classrooms, commons, sitework)",
            "phasing and schedule control around occupied operations",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (classrooms, commons, sitework)",
                    "phasing and schedule control around occupied operations",
                ],
                "GO_THIN": [
                    "site/civil scope drift and contingency realism",
                    "schedule windows (summer) and carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program/site assumptions",
                    "phasing/schedule constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and schedule feasibility before debt sizing",
                    "coverage resilience under phasing and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/site scope discipline",
                    "phasing/schedule control",
                ],
                "GO_THIN": [
                    "site/civil drift risk",
                    "summer window/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "schedule/phasing forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "carry/phasing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/site scope discipline and phasing/schedule control around occupied operations. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate site/civil scope boundaries, contingency realism, and summer-window schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/schedule feasibility break driven by site/civil scope and phasing constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around phasing and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/site scope discipline and phasing/schedule control.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate site/civil scope boundaries and summer-window schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; basis and schedule/phasing feasibility are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/schedule feasibility first, then adjust debt sizing/terms around carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("educational", "middle_school"): {
        "drivers_primary": [
            "program scope discipline (classrooms, gym, commons)",
            "phasing/schedule control and life-safety compliance execution",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (classrooms, gym, commons)",
                    "phasing/schedule control and life-safety compliance execution",
                ],
                "GO_THIN": [
                    "MEP scope drift (gym/commons) and contingency realism",
                    "schedule windows and carry sensitivity under occupied phasing",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program/MEP assumptions",
                    "phasing/schedule constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and schedule feasibility before debt sizing",
                    "coverage resilience under phasing/carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program scope discipline",
                    "phasing + compliance execution",
                ],
                "GO_THIN": [
                    "MEP/scope drift risk",
                    "occupied phasing/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "schedule/phasing forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "carry/phasing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program scope discipline and phasing/schedule control under compliance requirements. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate MEP scope boundaries, contingency realism, and occupied-phasing schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/schedule feasibility break driven by program/MEP scope and phasing constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around phasing and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program scope discipline and phasing/schedule control under compliance.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate MEP scope boundaries and occupied-phasing schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; basis and schedule/phasing feasibility are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/schedule feasibility first, then adjust debt sizing/terms around carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("educational", "high_school"): {
        "drivers_primary": [
            "program scope discipline (CTE, athletics, auditorium) and MEP intensity",
            "phasing/schedule control and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (CTE, athletics, auditorium) and MEP intensity",
                    "phasing/schedule control and commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty space scope drift (labs/CTE/kitchens/auditorium)",
                    "schedule windows and carry sensitivity under occupied campus phasing",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under specialty program scope",
                    "phasing/commissioning timeline assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty scope and MEP intensity",
                    "debt sizing resilience under phasing and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "specialty program/MEP discipline",
                    "phasing + commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "occupied phasing/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/commissioning forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "phasing/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: specialty program/MEP discipline and phasing/commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty space scope boundaries (CTE/labs/auditorium/athletics) and occupied-campus schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/value-support break driven by specialty program scope and timeline/commissioning assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and timeline assumptions first, then rework debt sizing/terms around phasing and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on specialty program/MEP discipline and phasing/commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope boundaries and occupied-campus phasing schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; specialty scope and timeline/commissioning assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around phasing and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("educational", "university"): {
        "drivers_primary": [
            "program scope discipline (research, housing, dining, athletics) and MEP intensity",
            "phasing/schedule control and commissioning readiness on occupied campus",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (research, housing, dining, athletics) and MEP intensity",
                    "phasing/schedule control and commissioning readiness on occupied campus",
                ],
                "GO_THIN": [
                    "specialty scope drift (labs, dining, athletics) and procurement lead times",
                    "enrollment/utilization assumptions and funding timing sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program and utilization assumptions",
                    "timeline/procurement and commissioning assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty scope and timeline risk",
                    "debt sizing resilience under utilization and carry volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/MEP discipline",
                    "occupied-campus phasing + commissioning",
                ],
                "GO_THIN": [
                    "specialty procurement + scope drift",
                    "utilization/funding sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/procurement forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "utilization/carry volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/MEP discipline and occupied-campus phasing/commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty scope/procurement lead times and utilization/funding timing sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/value-support break driven by program scope and timeline/procurement assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and timeline assumptions first, then rework debt sizing/terms around utilization and carry volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/MEP discipline and occupied-campus phasing/commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope/procurement lead times and utilization/funding timing sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program scope and timeline/procurement assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around utilization and carry volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("educational", "community_college"): {
        "drivers_primary": [
            "program scope discipline (instruction, labs, workforce training) and MEP intensity",
            "phasing/schedule control and budget/funding constraints",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (instruction, labs, workforce training) and MEP intensity",
                    "phasing/schedule control and budget/funding constraints",
                ],
                "GO_THIN": [
                    "specialty lab/workforce scope drift and procurement timing",
                    "schedule windows and carry sensitivity under occupied phasing",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program assumptions",
                    "timeline and funding constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and schedule feasibility before debt sizing",
                    "coverage resilience under phasing and funding timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/MEP discipline",
                    "phasing + funding constraint control",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "occupied phasing/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/funding forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "phasing/funding timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/MEP discipline and phasing/schedule control under funding constraints. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty lab/workforce scope boundaries and occupied-phasing schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by program scope and funding timing constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and timeline feasibility first, then rework debt sizing/terms around phasing, carry, and funding timing risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/MEP discipline and phasing/schedule control under funding constraints.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope boundaries and occupied-phasing schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program scope and timeline/funding constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/timeline feasibility first, then adjust debt sizing/terms around phasing and funding timing risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("civic", "library"): {
        "drivers_primary": [
            "program scope discipline (collections, study, community space) and sitework",
            "phasing/schedule control and stakeholder-driven change management",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (collections, study, community space) and sitework",
                    "phasing/schedule control and stakeholder-driven change management",
                ],
                "GO_THIN": [
                    "interiors/FF&E scope drift under stakeholder changes",
                    "schedule windows and carry sensitivity under occupied operations",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program/FF&E assumptions",
                    "timeline/stakeholder constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and schedule feasibility before debt sizing",
                    "coverage resilience under stakeholder and schedule risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/site scope discipline",
                    "phasing + stakeholder change control",
                ],
                "GO_THIN": [
                    "FF&E/interiors drift risk",
                    "occupied schedule/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/stakeholder forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/stakeholder risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/FF&E scope discipline and schedule control under stakeholder change risk. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate interiors/FF&E scope boundaries and occupied-operations schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by program/FF&E scope and stakeholder-driven change, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around stakeholder and phasing risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/FF&E scope discipline and occupied schedule control under stakeholder change risk.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate FF&E/interiors scope boundaries and occupied-operations schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program/FF&E scope and stakeholder-driven timeline risk are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/timeline feasibility first, then adjust debt sizing/terms around stakeholder and phasing risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("civic", "courthouse"): {
        "drivers_primary": [
            "security/access control and life-safety compliance scope",
            "courtroom/holding/evidence program requirements and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "security/access control and life-safety compliance scope",
                    "courtroom/holding/evidence program requirements and commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift (security systems, holding, evidence, IT)",
                    "schedule/carry sensitivity under complex phasing and approvals",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus security/program basis",
                    "timeline/approvals and commissioning assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on security/program scope",
                    "debt sizing resilience under approval and schedule risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "security/compliance scope discipline",
                    "program + commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "approvals/schedule sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/approvals forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "approval/schedule risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: security/compliance scope discipline and program/commissioning readiness (courtrooms/holding/evidence). No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate security systems scope boundaries, program requirements (holding/evidence/IT), and approvals/schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by security/program scope and approvals/commissioning constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and approval/schedule feasibility first, then rework debt sizing/terms around commissioning and turnover risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on security/compliance scope discipline and courthouse program/commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate security/program scope boundaries and approvals/schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; security/program basis and approvals/timeline constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/timeline feasibility first, then adjust debt sizing/terms around approval and turnover risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("civic", "government_building"): {
        "drivers_primary": [
            "program scope discipline (office + public service areas) and sitework",
            "security/access and commissioning/turnover readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (office + public service areas) and sitework",
                    "security/access and commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "stakeholder-driven scope drift and change-order exposure",
                    "schedule/carry sensitivity under occupied phasing and procurement constraints",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program/security assumptions",
                    "timeline/procurement constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and schedule feasibility before debt sizing",
                    "coverage resilience under procurement and schedule risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/site scope discipline",
                    "security + turnover readiness",
                ],
                "GO_THIN": [
                    "stakeholder scope drift",
                    "procurement/schedule sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/procurement forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/procurement risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/security scope discipline and turnover readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate stakeholder-driven scope boundaries, procurement constraints, and occupied-phasing schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by program/security scope and procurement/schedule constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around procurement and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/security scope discipline and turnover readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate stakeholder scope boundaries and procurement/schedule constraints under occupied phasing.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program/security basis and procurement/timeline constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/timeline feasibility first, then adjust debt sizing/terms around procurement and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("civic", "community_center"): {
        "drivers_primary": [
            "program scope discipline (gym, pool, multipurpose) and MEP intensity",
            "schedule/phasing control and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (gym, pool, multipurpose) and MEP intensity",
                    "schedule/phasing control and commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift (pool MEP, gym, acoustics) and contingency realism",
                    "schedule windows and carry sensitivity under occupied operations",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under specialty program scope",
                    "timeline/commissioning constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty scope and MEP intensity",
                    "debt sizing resilience under schedule and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "specialty program/MEP discipline",
                    "phasing + commissioning readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "schedule/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/commissioning forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: specialty program/MEP discipline and commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty scope boundaries (pool/gym MEP, acoustics), contingency realism, and occupied schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by specialty scope and commissioning constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around commissioning and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on specialty program/MEP discipline and commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope boundaries, contingency realism, and occupied schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; specialty scope and timeline/commissioning constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around commissioning and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("civic", "public_safety"): {
        "drivers_primary": [
            "program scope discipline (dispatch, bays, holding, evidence) and specialty MEP",
            "security/access control and commissioning/turnover readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (dispatch, bays, holding, evidence) and specialty MEP",
                    "security/access control and commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift (IT/radio, bays, decon, evidence)",
                    "schedule/approvals sensitivity under operational constraints",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus specialty program basis",
                    "timeline/commissioning constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty scope and MEP intensity",
                    "debt sizing resilience under approval and schedule risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "specialty program/MEP discipline",
                    "security + turnover readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "approvals/schedule sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/commissioning forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "approval/schedule risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: specialty program/MEP discipline (public safety) and security/turnover readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty scope boundaries (dispatch/IT/radio, bays, decon, evidence) and approvals/schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by specialty scope and commissioning constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and approvals/schedule feasibility first, then rework debt sizing/terms around commissioning and turnover risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on public safety program/MEP discipline and security/turnover readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope boundaries and approvals/schedule assumptions under operational constraints.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; specialty scope and timeline/commissioning constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around approvals, commissioning, and turnover risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("recreation", "fitness_center"): {
        "drivers_primary": [
            "membership/utilization assumptions to NOI conversion",
            "equipment package inclusions and buildout scope discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "membership/utilization assumptions to NOI conversion",
                    "equipment package inclusions and buildout scope discipline",
                ],
                "GO_THIN": [
                    "ramp-to-stabilization timing (member growth and churn)",
                    "operating cost burden (staffing/maintenance) and occupancy costs",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under utilization assumptions",
                    "NOI support driven by churn, staffing, and pricing assumptions",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under ramp and churn volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "utilization->NOI realism",
                    "equipment/buildout discipline",
                ],
                "GO_THIN": [
                    "ramp/churn sensitivity",
                    "opex + occupancy burden",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "NOI conversion drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/churn volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: utilization-to-NOI realism and equipment/buildout scope discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate ramp/churn assumptions, pricing sensitivity, and operating cost/occupancy burden before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as NOI-support/value-support break driven by utilization/churn and operating cost assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms around ramp and churn volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on utilization-to-NOI realism and equipment/buildout discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate ramp/churn assumptions and operating cost/occupancy burden.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; utilization/churn and operating cost assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset NOI conversion first, then adjust debt sizing/terms around ramp and churn volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("recreation", "sports_complex"): {
        "drivers_primary": [
            "field/court program scope and utilization assumptions",
            "site/civil and parking/circulation constraints",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "field/court program scope and utilization assumptions",
                    "site/civil and parking/circulation constraints",
                ],
                "GO_THIN": [
                    "tournament/event scheduling ramp and revenue mix",
                    "operating cost burden (staffing/maintenance) and lighting systems scope",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under utilization assumptions",
                    "schedule/ramp and operating cost assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on program/site scope",
                    "debt sizing resilience under ramp and utilization volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/utilization realism",
                    "site/civil + circulation discipline",
                ],
                "GO_THIN": [
                    "event ramp/mix sensitivity",
                    "opex + lighting scope risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "ramp/opex NOI drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "ramp/utilization volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/utilization realism and site/civil + circulation constraints. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate event/tournament ramp assumptions, operating cost burden, and lighting/field system scope boundaries before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by utilization/ramp assumptions and operating cost burden, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and utilization/ramp assumptions first, then rework debt sizing/terms around operating cost and seasonality volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on utilization realism and site/civil + circulation constraints.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate event ramp assumptions, opex burden, and lighting/field system scope boundaries.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; utilization/ramp and operating cost assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around ramp and seasonality volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("recreation", "aquatic_center"): {
        "drivers_primary": [
            "pool systems scope (filtration/heating) and humidity-control MEP discipline",
            "commissioning/turnover readiness and operating cost burden",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "pool systems scope (filtration/heating) and humidity-control MEP discipline",
                    "commissioning/turnover readiness and operating cost burden",
                ],
                "GO_THIN": [
                    "specialty MEP scope drift (dehumidification, natatorium enclosure)",
                    "schedule/commissioning sensitivity under complex startup",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus specialty MEP basis",
                    "operating cost assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on natatorium MEP/enclosure scope",
                    "debt sizing resilience under commissioning and opex risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "natatorium MEP scope discipline",
                    "commissioning + opex realism",
                ],
                "GO_THIN": [
                    "MEP/enclosure drift risk",
                    "commissioning/timing sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "opex NOI drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "commissioning/opex risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: natatorium MEP/enclosure scope discipline and commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate dehumidification/enclosure scope boundaries, commissioning/startup sequencing, and operating cost assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by specialty MEP basis and operating cost assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair specialty MEP basis and opex assumptions first, then rework debt sizing/terms around commissioning and startup risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on natatorium MEP scope discipline and commissioning + opex realism.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate enclosure/MEP scope boundaries and commissioning/startup sequencing.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; specialty MEP basis and operating cost assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset MEP basis first, then adjust debt sizing/terms around commissioning and opex risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("recreation", "recreation_center"): {
        "drivers_primary": [
            "multi-program scope discipline (gym, fitness, community rooms)",
            "MEP intensity and commissioning/turnover readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "multi-program scope discipline (gym, fitness, community rooms)",
                    "MEP intensity and commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift (acoustics, pool add-ons, equipment) and contingency realism",
                    "schedule windows and carry sensitivity under occupied operations",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program scope assumptions",
                    "timeline/commissioning and opex assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on specialty scope and MEP intensity",
                    "debt sizing resilience under schedule and opex risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/MEP discipline",
                    "commissioning/turnover readiness",
                ],
                "GO_THIN": [
                    "specialty scope drift risk",
                    "schedule/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/opex NOI drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/opex risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/MEP discipline and commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate specialty scope boundaries (equipment/acoustics/add-ons), contingency realism, and occupied schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by program scope and commissioning/opex assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and timeline assumptions first, then rework debt sizing/terms around schedule and operating cost risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/MEP discipline and commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate specialty scope boundaries, contingency realism, and occupied schedule assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program scope and timeline/opex assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around schedule and opex risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("recreation", "stadium"): {
        "drivers_primary": [
            "program scope discipline (seating/bowl/concourses) and site/circulation constraints",
            "specialty systems (lighting, sound, security) and commissioning readiness",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "program scope discipline (seating/bowl/concourses) and site/circulation constraints",
                    "specialty systems (lighting, sound, security) and commissioning readiness",
                ],
                "GO_THIN": [
                    "scope drift under stakeholder and code/security requirements",
                    "schedule/carry sensitivity under complex procurement and commissioning",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under program/systems scope assumptions",
                    "timeline/commissioning constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on program/systems scope",
                    "debt sizing resilience under schedule and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "program/site scope discipline",
                    "specialty systems + commissioning readiness",
                ],
                "GO_THIN": [
                    "stakeholder scope drift risk",
                    "procurement/commissioning timing sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timeline/commissioning forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: program/site scope discipline and specialty systems + commissioning readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate stakeholder-driven scope boundaries, specialty systems inclusions, and procurement/commissioning schedule assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break driven by program/systems scope and commissioning constraints, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and schedule feasibility first, then rework debt sizing/terms around procurement, commissioning, and carry risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on program/site scope discipline and specialty systems commissioning readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate scope boundaries, specialty systems inclusions, and procurement/commissioning timing assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; program/systems scope and timeline/commissioning constraints are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around schedule, commissioning, and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("mixed_use", "office_residential"): {
        "drivers_primary": [
            "phasing/carry discipline across office and residential delivery",
            "leasing/TI exposure (office) and absorption/pricing (residential)",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "phasing/carry discipline across office and residential delivery",
                    "leasing/TI exposure (office) and absorption/pricing (residential)",
                ],
                "GO_THIN": [
                    "office lease-up timing/credit mix and TI/LC exposure",
                    "podium/vertical MEP interfaces and schedule-window sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under phased stabilization assumptions",
                    "office TI/leasing drag and carry assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (phasing + leasing)",
                    "debt sizing resilience under carry and absorption risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "phasing/carry discipline",
                    "office leasing + resi absorption realism",
                ],
                "GO_THIN": [
                    "office TI/leasing sensitivity",
                    "podium/MEP + schedule risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "phasing/leasing forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "carry/absorption risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: phased carry discipline and the office-leasing + residential-absorption assumptions that drive stabilized value support. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate office lease-up/TI exposure and podium/vertical MEP interfaces that drive schedule/carry sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a phased-stabilization/value-support break dominated by carry assumptions and office leasing/TI exposure, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair stabilization viability (phasing + carry + leasing) first, then rework debt sizing/terms. Office TI drag and schedule interfaces are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on phasing/carry discipline and office leasing/TI exposure plus residential absorption assumptions.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate office lease-up/TI exposure and podium/MEP schedule interfaces driving carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; phasing/carry and office leasing/TI exposure are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization viability first, then adjust debt sizing/terms around carry, lease-up, and interface risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("mixed_use", "retail_residential"): {
        "drivers_primary": [
            "ground-floor activation and retail lease-up assumptions",
            "residential absorption/pricing and phasing/carry discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "ground-floor activation and retail lease-up assumptions",
                    "residential absorption/pricing and phasing/carry discipline",
                ],
                "GO_THIN": [
                    "retail tenant mix and TI exposure under activation risk",
                    "podium/parking interfaces and schedule-window sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under retail activation assumptions",
                    "carry and retail TI/leasing drag driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (activation + carry)",
                    "debt sizing resilience under mixed-use phasing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "retail activation realism",
                    "resi absorption + phasing/carry discipline",
                ],
                "GO_THIN": [
                    "retail TI/leasing sensitivity",
                    "podium/parking + schedule risk",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "activation/carry forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "phasing/activation risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: retail activation (lease-up + tenant mix) and residential absorption, with phasing/carry discipline across the podium. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate retail tenanting/TI exposure and podium/parking interfaces that drive schedule/carry sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a stabilization/value-support break dominated by retail activation assumptions and carry/TI exposure, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair activation and phasing/carry assumptions first, then rework debt sizing/terms. Retail TI drag and interface-driven schedule risk are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on retail activation realism and residential absorption with phasing/carry discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate retail tenanting/TI exposure and podium/parking schedule interfaces driving carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; retail activation (lease-up/TI) and carry assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization viability first, then adjust debt sizing/terms around activation, carry, and interface risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("mixed_use", "hotel_residential"): {
        "drivers_primary": [
            "hotel ramp assumptions (ADR/occupancy) to NOI conversion",
            "residential absorption/pricing and phasing/carry discipline",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "hotel ramp assumptions (ADR/occupancy) to NOI conversion",
                    "residential absorption/pricing and phasing/carry discipline",
                ],
                "GO_THIN": [
                    "operator-driven scope and mixed-program MEP/commissioning interfaces",
                    "ramp timing sensitivity across hotel and residential delivery",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under hotel ramp and resi absorption assumptions",
                    "carry and program interface risk driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (ramp + carry)",
                    "debt sizing resilience under multi-program timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "hotel ramp->NOI realism",
                    "resi absorption + phasing/carry discipline",
                ],
                "GO_THIN": [
                    "operator scope/interface risk",
                    "multi-program ramp timing sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "ramp/carry forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "timing/interface risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: hotel ramp (ADR/occupancy->NOI) and residential absorption, with phasing/carry discipline across the mixed program. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate operator-driven scope/MEP interfaces and ramp timing assumptions across hotel and residential delivery before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a phased-stabilization/value-support break dominated by hotel ramp assumptions and program interface risk, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair ramp and phasing/carry assumptions first, then rework debt sizing/terms. Operator scope interfaces and timing risk are forcing drivers.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on hotel ramp realism and residential absorption with phasing/carry discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate operator-driven scope/MEP interfaces and multi-program ramp timing assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; hotel ramp assumptions and carry/interface risk are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization viability first, then adjust debt sizing/terms around ramp timing and interface risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("mixed_use", "transit_oriented"): {
        "drivers_primary": [
            "phasing/carry discipline under entitlement and infrastructure interfaces",
            "ground-floor activation and residential absorption assumptions",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "phasing/carry discipline under entitlement and infrastructure interfaces",
                    "ground-floor activation and residential absorption assumptions",
                ],
                "GO_THIN": [
                    "infrastructure/utility interfaces and public-realm scope drift",
                    "schedule windows, approvals, and carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under infrastructure and timing assumptions",
                    "activation and phasing constraints driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on infrastructure/public-realm scope",
                    "debt sizing resilience under approvals and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "infrastructure/phasing discipline",
                    "activation + absorption realism",
                ],
                "GO_THIN": [
                    "interface scope drift risk",
                    "approvals/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "timing/activation forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "approvals/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: infrastructure/phasing discipline and activation/absorption realism under transit interfaces. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate infrastructure/utility interfaces, public-realm scope boundaries, and approvals/schedule carry sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a timing/interface value-support break dominated by infrastructure scope and approvals/carry assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair infrastructure basis and approvals/schedule feasibility first, then rework debt sizing/terms. Carry sensitivity and activation timing are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on infrastructure/phasing discipline and activation/absorption realism under transit interfaces.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate infrastructure/public-realm scope boundaries and approvals/schedule carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; infrastructure scope and approvals/carry assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/timeline feasibility first, then adjust debt sizing/terms around approvals and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("mixed_use", "urban_mixed"): {
        "drivers_primary": [
            "multi-component phasing/carry discipline and capital plan realism",
            "activation/tenanting assumptions across uses (retail + office + resi)",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "multi-component phasing/carry discipline and capital plan realism",
                    "activation/tenanting assumptions across uses (retail + office + resi)",
                ],
                "GO_THIN": [
                    "interface scope drift (podium/parking/vertical MEP) and contingency realism",
                    "lease-up sequencing and carry sensitivity under market volatility",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under phased stabilization assumptions",
                    "activation and carry assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (sequencing + carry)",
                    "debt sizing resilience under interface and market volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "phasing/carry discipline",
                    "activation across uses realism",
                ],
                "GO_THIN": [
                    "interface/scope drift risk",
                    "sequencing + carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "activation/carry forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "interface/market risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: multi-component phasing/carry discipline and activation assumptions across uses. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate podium/parking/MEP interface scope boundaries and sequencing/carry sensitivity under market volatility before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a phased-stabilization/value-support break dominated by carry, activation, and interface scope assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair stabilization viability (sequencing + carry + activation) first, then rework debt sizing/terms. Interface scope drift and market volatility are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on phasing/carry discipline and activation assumptions across uses.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate interface scope boundaries and sequencing/carry sensitivity under market volatility.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; carry, activation, and interface scope assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization viability first, then adjust debt sizing/terms around carry, activation, and interface risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("parking", "surface_parking"): {
        "drivers_primary": [
            "demand capture and pricing elasticity assumptions",
            "site/civil scope discipline (paving, drainage, lighting)",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "demand capture and pricing elasticity assumptions",
                    "site/civil scope discipline (paving, drainage, lighting)",
                ],
                "GO_THIN": [
                    "utilization ramp timing (daypart/event mix) and enforcement assumptions",
                    "opex burden (staffing, maintenance) and permit/compliance timing",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under utilization/pricing assumptions",
                    "civil scope and operating assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset and NOI conversion before debt sizing",
                    "coverage resilience under utilization and pricing volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "demand/pricing realism",
                    "civil/site scope discipline",
                ],
                "GO_THIN": [
                    "utilization ramp sensitivity",
                    "opex/enforcement assumptions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "NOI conversion drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "utilization/pricing volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: demand/pricing realism and site/civil scope discipline (paving/drainage/lighting). No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate utilization ramp timing, pricing elasticity, and enforcement/opex assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as NOI-support/value-support break driven by utilization/pricing assumptions and civil scope basis, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis and NOI conversion first, then rework debt sizing/terms around utilization, pricing, and opex volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on demand/pricing realism and civil/site scope discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate utilization ramp timing, pricing elasticity, and enforcement/opex assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; utilization/pricing and civil basis assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset NOI conversion first, then adjust debt sizing/terms around utilization and pricing volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("parking", "parking_garage"): {
        "drivers_primary": [
            "structure scope discipline (spans, PT, ramps) and life-safety systems",
            "demand capture and pricing elasticity assumptions to NOI conversion",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "structure scope discipline (spans, PT, ramps) and life-safety systems",
                    "demand capture and pricing elasticity assumptions to NOI conversion",
                ],
                "GO_THIN": [
                    "concrete/steel volatility and schedule sensitivity",
                    "ventilation/fire protection scope boundaries and commissioning readiness",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus structural basis under utilization assumptions",
                    "opex/enforcement and life-safety systems assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on structure/systems scope",
                    "debt sizing resilience under utilization and construction volatility",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "structure/life-safety scope discipline",
                    "demand/pricing realism",
                ],
                "GO_THIN": [
                    "materials/schedule volatility",
                    "systems commissioning readiness",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "NOI support vs opex/systems",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "utilization + construction volatility",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: structural/life-safety scope discipline and demand/pricing realism. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate materials/schedule volatility, ventilation/fire scope boundaries, and utilization/pricing sensitivity before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by structural basis and utilization/pricing assumptions, not a pure lender-coverage failure. Repair basis and NOI drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair structural basis and NOI conversion first, then rework debt sizing/terms around utilization and construction volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on structure/life-safety scope discipline and demand/pricing realism.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate materials/schedule volatility and ventilation/fire scope boundaries plus utilization sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; structural basis and utilization/pricing assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around utilization and construction volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("parking", "underground_parking"): {
        "drivers_primary": [
            "excavation/shoring and groundwater/waterproofing risk discipline",
            "schedule/carry sensitivity under complex sequencing and approvals",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "excavation/shoring and groundwater/waterproofing risk discipline",
                    "schedule/carry sensitivity under complex sequencing and approvals",
                ],
                "GO_THIN": [
                    "geotech uncertainty and dewatering/waterproofing scope drift",
                    "construction schedule volatility and contingency realism",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus underground basis under utilization assumptions",
                    "timeline and geotech/waterproofing risk driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on excavation/shoring/waterproofing scope",
                    "debt sizing resilience under schedule and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "geotech/waterproofing discipline",
                    "schedule/carry sensitivity",
                ],
                "GO_THIN": [
                    "geotech uncertainty + scope drift",
                    "schedule/contingency realism",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "geotech/timeline forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "schedule/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: excavation/shoring + waterproofing risk discipline and schedule/carry sensitivity. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate geotech uncertainty, dewatering/waterproofing scope boundaries, and schedule/contingency realism before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as basis/timeline feasibility break dominated by geotech/waterproofing risk and schedule/carry assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair underground basis and schedule feasibility first, then rework debt sizing/terms around carry and geotech volatility.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on geotech/waterproofing discipline and schedule/carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate geotech uncertainty, waterproofing scope boundaries, and schedule/contingency realism.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; underground basis and geotech/timeline risks are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around schedule/carry and geotech volatility.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("parking", "automated_parking"): {
        "drivers_primary": [
            "equipment vendor scope boundaries and uptime/maintenance assumptions",
            "commissioning/integration readiness and turnover sequencing",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "equipment vendor scope boundaries and uptime/maintenance assumptions",
                    "commissioning/integration readiness and turnover sequencing",
                ],
                "GO_THIN": [
                    "vendor lead times and OFI vs GC carry boundaries",
                    "integration/testing risk and ramp-to-stabilization assumptions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus equipment basis under utilization assumptions",
                    "uptime/maintenance and commissioning assumptions driving NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset on equipment/vendor scope",
                    "debt sizing resilience under commissioning and uptime risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "vendor scope + uptime realism",
                    "commissioning/integration readiness",
                ],
                "GO_THIN": [
                    "lead-time/OFI drift risk",
                    "testing/ramp sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "uptime/commissioning NOI support",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "commissioning/uptime risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: vendor scope boundaries/uptime assumptions and commissioning/integration readiness. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate vendor lead times, OFI vs GC carry boundaries, and integration/testing assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "Treat as value-support break driven by equipment basis and uptime/maintenance + commissioning assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair equipment basis and commissioning/integration assumptions first, then rework debt sizing/terms around uptime and ramp risk.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on vendor scope/uptime realism and commissioning/integration readiness.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate lead times/OFI boundaries and integration/testing assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. Repair value support; equipment basis and uptime/commissioning assumptions are primary drivers.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis first, then adjust debt sizing/terms around commissioning and uptime risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("office", "class_a"): {
        "drivers_primary": [
            "leasing velocity and achieved rent assumptions to stabilize NOI",
            "TI/LC exposure and downtime/carry sensitivity",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "leasing velocity and achieved rent assumptions to stabilize NOI",
                    "TI/LC exposure and downtime/carry sensitivity",
                ],
                "GO_THIN": [
                    "tenant credit mix and lease-up timing under market softness",
                    "capital plan (tenanting + refresh) versus stabilized value support",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under leasing/TI/LC assumptions",
                    "downtime and carry assumptions driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability and value support reset",
                    "debt sizing resilience under lease-up and carry risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "leasing->NOI realism",
                    "TI/LC + downtime sensitivity",
                ],
                "GO_THIN": [
                    "lease-up timing/credit mix risk",
                    "capex plan vs value support",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "carry/downtime forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "lease-up/carry risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: stabilization viability (leasing->NOI) and TI/LC + downtime/carry sensitivity. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate lease-up timing/tenant credit mix, TI/LC exposure, and capital plan assumptions before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a stabilization/value-support break dominated by leasing, TI/LC, and downtime/carry assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair stabilization viability and value support first, then rework debt sizing/terms. Lease-up timing and carry assumptions are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on stabilization viability (leasing->NOI) and TI/LC + downtime sensitivity.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate lease-up timing/credit mix, TI/LC exposure, and downtime/carry assumptions.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. This points to weak value support under leasing/TI/LC and downtime/carry assumptions; repair those first.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization/value support first, then adjust debt sizing/terms around lease-up and carry risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("office", "class_b"): {
        "drivers_primary": [
            "leasing velocity, downtime, and renewal probability assumptions",
            "TI/LC and operating expense control versus stabilized value support",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "leasing velocity, downtime, and renewal probability assumptions",
                    "TI/LC and operating expense control versus stabilized value support",
                ],
                "GO_THIN": [
                    "tenant rollover concentration and re-tenanting capex exposure",
                    "market rent sensitivity under vacancy and concessions pressure",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under vacancy/concession assumptions",
                    "re-tenanting capex and expense drift driving policy break",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (leasing + capex)",
                    "debt sizing resilience under rollover and vacancy risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "downtime/renewal realism",
                    "TI/LC + expense control",
                ],
                "GO_THIN": [
                    "rollover concentration risk",
                    "rent sensitivity under concessions",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "capex/expense drift forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "rollover/vacancy risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: downtime/renewal realism and TI/LC + expense control versus stabilized value support. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate rollover concentration, re-tenanting capex exposure, and rent sensitivity under vacancy/concession pressure before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a stabilization/value-support break dominated by vacancy/concession assumptions and re-tenanting capex/expense drift, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair stabilization viability and value support first, then rework debt sizing/terms. Rollover/vacancy and capex exposure are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on downtime/renewal realism and TI/LC + expense control versus stabilized value support.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate rollover concentration, re-tenanting capex exposure, and rent sensitivity under vacancy/concession pressure.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. This points to weak value support under vacancy/concession and re-tenanting capex/expense drift; repair those first.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization/value support first, then adjust debt sizing/terms around rollover, vacancy, and capex risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("retail", "shopping_center"): {
        "drivers_primary": [
            "tenant mix durability and anchor/credit concentration risk",
            "lease-up timing, TI/LC exposure, and downtime/carry sensitivity",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "tenant mix durability and anchor/credit concentration risk",
                    "lease-up timing, TI/LC exposure, and downtime/carry sensitivity",
                ],
                "GO_THIN": [
                    "renewal probability and re-tenanting capex exposure",
                    "rent sensitivity under vacancy/concession pressure",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under lease-up and TI/LC assumptions",
                    "anchor/credit concentration and downtime forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability reset (lease-up + TI/LC)",
                    "debt sizing resilience under vacancy and tenant-mix risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "tenant mix/anchor durability",
                    "lease-up + TI/LC sensitivity",
                ],
                "GO_THIN": [
                    "renewal + capex exposure",
                    "vacancy/concession sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "concentration + downtime drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "stabilization viability + debt sizing",
                    "vacancy/tenant-mix risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: tenant-mix/anchor durability and lease-up + TI/LC exposure under downtime/carry sensitivity. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate renewal probability, re-tenanting capex/TI exposure, and rent sensitivity under vacancy/concession pressure before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a stabilization/value-support break dominated by tenant-mix concentration, lease-up timing, and TI/LC exposure, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair stabilization viability and value support first, then rework debt sizing/terms. Vacancy/concession sensitivity and capex/TI exposure are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on tenant-mix/anchor durability and lease-up + TI/LC exposure under downtime sensitivity.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate renewals, re-tenanting capex/TI exposure, and vacancy/concession sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. This points to weak value support under tenant-mix concentration, lease-up timing, and TI/LC exposure; repair those first.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset stabilization/value support first, then adjust debt sizing/terms around vacancy and capex/TI exposure risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
    },
    ("retail", "big_box"): {
        "drivers_primary": [
            "tenant credit and lease term durability (single-tenant concentration)",
            "backfill risk and re-tenanting scope/capex exposure",
        ],
        "drivers": {
            "dealshield": {
                "GO_STRONG": [
                    "tenant credit and lease term durability (single-tenant concentration)",
                    "backfill risk and re-tenanting scope/capex exposure",
                ],
                "GO_THIN": [
                    "subdivide/reuse feasibility and scope boundary risk",
                    "lease-up timing and carry sensitivity under backfill uncertainty",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support versus basis under backfill assumptions",
                    "re-tenanting capex/scope and downtime forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset under reuse/subdivide scope",
                    "debt sizing resilience under backfill timing risk",
                ],
            },
            "executive": {
                "GO_STRONG": [
                    "tenant credit/term durability",
                    "backfill + capex exposure",
                ],
                "GO_THIN": [
                    "reuse/subdivide scope risk",
                    "backfill timing/carry sensitivity",
                ],
                "NOGO_DEBT_PASSES": [
                    "value support vs basis",
                    "downtime + capex forcing drivers",
                ],
                "NOGO_DEBT_FAILS": [
                    "basis reset + debt sizing",
                    "backfill timing risk",
                ],
            },
        },
        "templates": {
            "dealshield": {
                "GO_STRONG": {
                    "summary": "GO - policy clears with healthy cushion (value gap positive).",
                    "detail": "Primary monitoring: tenant credit/term durability and backfill/capex exposure discipline. No near-base first-break flags.",
                },
                "GO_THIN": {
                    "summary": "GO (Thin Cushion) - policy clears, but first-break proximity is tight.",
                    "detail": "First break is near-base stress; validate reuse/subdivide scope feasibility, backfill timing assumptions, and carry sensitivity under downtime risk before commit.",
                },
                "NOGO_DEBT_PASSES": {
                    "summary": "NO-GO - policy breaks on value support (value gap non-positive), even though DSCR clears.",
                    "detail": "This is a value-support break dominated by backfill timing and re-tenanting capex/scope assumptions, not a pure lender-coverage failure. Repair those drivers before reruns.",
                },
                "NOGO_DEBT_FAILS": {
                    "summary": "NO-GO - policy breaks and DSCR is below target.",
                    "detail": "Repair basis/value support first (reuse/subdivide scope + capex), then rework debt sizing/terms. Backfill timing and carry are forcing risks.",
                },
            },
            "executive": {
                "GO_STRONG": {
                    "how_to_interpret": "GO: policy clears with healthy cushion. Debt Lens clears. Focus diligence on tenant credit/term durability and backfill/capex exposure discipline.",
                    "target_yield_lens_label": "Target Yield: Met (Cushion)",
                },
                "GO_THIN": {
                    "how_to_interpret": "GO (Thin Cushion): policy clears, but first break is close. Validate reuse/subdivide scope feasibility and backfill timing/carry sensitivity.",
                    "target_yield_lens_label": "Target Yield: Thin Cushion",
                },
                "NOGO_DEBT_PASSES": {
                    "how_to_interpret": "NO-GO: policy breaks even though Debt Lens clears. This points to weak value support under backfill timing and re-tenanting capex/scope assumptions; repair those first.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
                "NOGO_DEBT_FAILS": {
                    "how_to_interpret": "NO-GO: policy breaks and Debt Lens fails. Reset basis/value support first, then adjust debt sizing/terms around backfill timing and downtime risk.",
                    "target_yield_lens_label": "Target Yield: Not Met",
                },
            },
        },
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
