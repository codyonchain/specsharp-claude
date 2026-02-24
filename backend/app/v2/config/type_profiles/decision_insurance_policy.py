from __future__ import annotations

import copy
from typing import Any, Dict, Optional

DECISION_INSURANCE_POLICY_ID = "decision_insurance_subtype_policy_v1"

DECISION_INSURANCE_POLICY_BY_PROFILE_ID: Dict[str, Dict[str, Any]] = {
    "restaurant_quick_service_v1": {
        "primary_control_variable": {
            "tile_id": "prototype_finish_rework_plus_10",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Prototype Finish Rework +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 40.0,
            "scenario_priority": ["base", "conservative", "ugly", "prototype_rework"],
        },
        "flex_calibration": {"tight_max_pct": 3.0, "moderate_max_pct": 8.0, "fallback_pct": 6.0},
    },
    "restaurant_full_service_v1": {
        "primary_control_variable": {
            "tile_id": "service_labor_and_layout_plus_12",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Service Labor + Layout +12%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "ugly", "service_flow_disruption"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.0, "fallback_pct": 2.0},
    },
    "restaurant_fine_dining_v1": {
        "primary_control_variable": {
            "tile_id": "curated_mep_and_controls_plus_12",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "Curated MEP + Controls +12%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 15.0,
            "scenario_priority": ["base", "conservative", "ugly", "chef_table_commissioning_drag"],
        },
        "flex_calibration": {"tight_max_pct": 2.5, "moderate_max_pct": 7.0, "fallback_pct": 4.0},
    },
    "restaurant_cafe_v1": {
        "primary_control_variable": {
            "tile_id": "espresso_line_equipment_plus_8",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "Espresso Line Equipment +8%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "ugly", "morning_peak_shortfall"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 6.0, "fallback_pct": 5.0},
    },
    "restaurant_bar_tavern_v1": {
        "primary_control_variable": {
            "tile_id": "entertainment_and_life_safety_plus_10",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Entertainment + Life-Safety +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 35.0,
            "scenario_priority": ["base", "conservative", "ugly", "late_night_compliance_push"],
        },
        "flex_calibration": {"tight_max_pct": 3.0, "moderate_max_pct": 8.0, "fallback_pct": 6.0},
    },
    "hospitality_limited_service_hotel_v1": {
        "primary_control_variable": {
            "tile_id": "guestroom_turnover_and_ffe_plus_10",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Guestroom Turnover + FF&E +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "ugly", "seasonal_ramp_pressure"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 6.0, "fallback_pct": 5.0},
    },
    "hospitality_full_service_hotel_v1": {
        "primary_control_variable": {
            "tile_id": "ballroom_and_fnb_fitout_plus_12",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Ballroom and F&B Fit-Out +12%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 50.0,
            "scenario_priority": ["base", "conservative", "ugly", "banquet_program_delay"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.0, "fallback_pct": 3.0},
    },
    "multifamily_market_rate_apartments_v1": {
        "primary_control_variable": {
            "tile_id": "structural_carry_proxy_plus_5",
            "metric_ref": "trade_breakdown.structural",
            "label": "Structural Base Carry Proxy +5%",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "ugly", "structural_carry_proxy_stress"],
        },
        "flex_calibration": {"tight_max_pct": 2.5, "moderate_max_pct": 7.0, "fallback_pct": 5.0},
    },
    "multifamily_luxury_apartments_v1": {
        "primary_control_variable": {
            "tile_id": "amenity_finish_plus_15",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Amenity Finishes +15%",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "amenity_overrun", "amenity_system_stress"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.5, "fallback_pct": 2.0},
    },
    "multifamily_affordable_housing_v1": {
        "primary_control_variable": {
            "tile_id": "compliance_electrical_plus_8",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Compliance Electrical +8%",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "conservative", "compliance_delay", "funding_gap"],
        },
        "flex_calibration": {"tight_max_pct": 2.5, "moderate_max_pct": 6.0, "fallback_pct": 4.0},
    },
    "industrial_warehouse_v1": {
        "primary_control_variable": {
            "tile_id": "structural_plus_10",
            "metric_ref": "trade_breakdown.structural",
            "label": "Structural +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": -8.0,
            "scenario_priority": ["base", "conservative", "ugly", "dock_queue_overrun"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.0, "fallback_pct": 3.5},
    },
    "industrial_distribution_center_v1": {
        "primary_control_variable": {
            "tile_id": "electrical_plus_10",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Electrical +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": -25.0,
            "scenario_priority": ["base", "conservative", "ugly", "sortation_power_stress"],
        },
        "flex_calibration": {"tight_max_pct": 1.0, "moderate_max_pct": 3.0, "fallback_pct": 0.8},
    },
    "industrial_manufacturing_v1": {
        "primary_control_variable": {
            "tile_id": "process_mep_plus_10",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "Process MEP +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": -35.0,
            "scenario_priority": ["base", "conservative", "ugly", "commissioning_rework_cycle"],
        },
        "flex_calibration": {"tight_max_pct": 0.8, "moderate_max_pct": 2.5, "fallback_pct": 0.5},
    },
    "industrial_flex_space_v1": {
        "primary_control_variable": {
            "tile_id": "office_finish_plus_10",
            "metric_ref": "trade_breakdown.finishes",
            "label": "Office/Finish Scope +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": -6.0,
            "scenario_priority": ["base", "conservative", "ugly", "tenant_mix_drift"],
        },
        "flex_calibration": {"tight_max_pct": 2.2, "moderate_max_pct": 5.5, "fallback_pct": 3.2},
    },
    "industrial_cold_storage_v1": {
        "primary_control_variable": {
            "tile_id": "equipment_plus_10",
            "metric_ref": "construction_costs.equipment_total",
            "label": "Equipment +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": -30.0,
            "scenario_priority": ["base", "conservative", "ugly", "refrigeration_leak_response"],
        },
        "flex_calibration": {"tight_max_pct": 1.0, "moderate_max_pct": 3.2, "fallback_pct": 0.9},
    },
}


def get_decision_insurance_policy(profile_id: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(profile_id, str) or not profile_id.strip():
        return None
    resolved = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id.strip())
    if not isinstance(resolved, dict):
        return None
    return copy.deepcopy(resolved)
