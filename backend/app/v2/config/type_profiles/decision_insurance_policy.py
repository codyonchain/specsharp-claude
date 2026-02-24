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
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 6.0,
            "scenario_priority": ["base", "conservative", "structural_carry_proxy_stress", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.0, "fallback_pct": 3.5},
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
            "threshold": 250000.0,
            "scenario_priority": ["base", "conservative", "amenity_overrun", "amenity_system_stress"],
        },
        "flex_calibration": {"tight_max_pct": 1.5, "moderate_max_pct": 4.5, "fallback_pct": 2.0},
    },
    "multifamily_affordable_housing_v1": {
        "primary_control_variable": {
            "tile_id": "compliance_electrical_plus_8",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Compliance Electrical +8%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 8.0,
            "scenario_priority": ["base", "conservative", "compliance_delay", "funding_gap"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 4.5, "fallback_pct": 3.0},
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
    "healthcare_surgical_center_v1": {
        "primary_control_variable": {
            "tile_id": "or_turnover_and_sterile_core_plus_12",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "IC-First OR Turnover, Sterile-Core Sequencing, and Block Utilization Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 95.0,
            "scenario_priority": ["base", "sterile_reprocessing_drag", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.4, "moderate_max_pct": 3.8, "fallback_pct": 1.6},
    },
    "healthcare_imaging_center_v1": {
        "primary_control_variable": {
            "tile_id": "shielding_and_power_quality_plus_11",
            "metric_ref": "trade_breakdown.electrical",
            "label": "IC-First Shielding/Quench Readiness, Modality Throughput, and Uptime Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 78.0,
            "scenario_priority": ["base", "magnet_commissioning_slip", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.2, "moderate_max_pct": 3.4, "fallback_pct": 1.4},
    },
    "healthcare_urgent_care_v1": {
        "primary_control_variable": {
            "tile_id": "triage_flow_and_lab_turns_plus_10",
            "metric_ref": "trade_breakdown.finishes",
            "label": "IC-First Walk-In Acuity Mix, Peak-Hour Staffing, and Visit Velocity Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 560.0,
            "scenario_priority": ["base", "weekend_surge_breakpoint", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.2, "fallback_pct": 2.3},
    },
    "healthcare_outpatient_clinic_v1": {
        "primary_control_variable": {
            "tile_id": "exam_program_and_room_standard_plus_9",
            "metric_ref": "trade_breakdown.finishes",
            "label": "IC-First Referral Leakage, Provider Template Utilization, and No-Show Drag Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 45.0,
            "scenario_priority": ["base", "care_team_growth_mismatch", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.9, "moderate_max_pct": 4.9, "fallback_pct": 2.1},
    },
    "healthcare_medical_office_building_v1": {
        "primary_control_variable": {
            "tile_id": "tenant_fitout_mep_stack_plus_10",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "IC-First TI/LC Burn, Lease-Up Velocity, and Rollover Stack Control",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": 0.0,
            "scenario_priority": ["base", "anchor_tenant_restack", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.3, "moderate_max_pct": 3.4, "fallback_pct": 1.4},
    },
    "healthcare_dental_office_v1": {
        "primary_control_variable": {
            "tile_id": "chairside_vacuum_and_gas_plus_11",
            "metric_ref": "trade_breakdown.plumbing",
            "label": "IC-First Chair Utilization, Hygiene Mix, and Sterilization Bottleneck Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 300.0,
            "scenario_priority": ["base", "sterilization_center_rework", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.8, "moderate_max_pct": 4.5, "fallback_pct": 2.0},
    },
    "healthcare_hospital_v1": {
        "primary_control_variable": {
            "tile_id": "acuity_mep_redundancy_plus_12",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "IC-First Nurse Staffing Intensity, LOS Pressure, and Service-Line Mix Control",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": -10000000.0,
            "scenario_priority": ["base", "tower_commissioning_retest", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 0.7, "moderate_max_pct": 2.2, "fallback_pct": 0.8},
    },
    "healthcare_medical_center_v1": {
        "primary_control_variable": {
            "tile_id": "service_line_power_density_plus_11",
            "metric_ref": "trade_breakdown.electrical",
            "label": "IC-First Procedure Mix, Diagnostic Throughput, and Care-Path Coordination Control",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": -75000000.0,
            "scenario_priority": ["base", "specialty_program_shift", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 0.6, "moderate_max_pct": 1.8, "fallback_pct": 0.7},
    },
    "healthcare_nursing_home_v1": {
        "primary_control_variable": {
            "tile_id": "resident_room_life_safety_plus_9",
            "metric_ref": "trade_breakdown.finishes",
            "label": "IC-First Census Mix, Agency Labor Dependency, and Reimbursement Pressure Control",
        },
        "collapse_trigger": {
            "metric": "value_gap",
            "operator": "<=",
            "threshold": -12000000.0,
            "scenario_priority": ["base", "state_survey_correction_cycle", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.1, "moderate_max_pct": 3.0, "fallback_pct": 1.2},
    },
    "healthcare_rehabilitation_v1": {
        "primary_control_variable": {
            "tile_id": "therapy_gym_mep_integration_plus_10",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "IC-First Therapy Intensity, Authorization Friction, and LOS Drift Control",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 5.0,
            "scenario_priority": ["base", "equipment_path_and_rehab_flow", "conservative", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.7, "moderate_max_pct": 4.3, "fallback_pct": 1.9},
    },
    "specialty_data_center_v1": {
        "primary_control_variable": {
            "tile_id": "power_train_redundancy_rework_plus_15",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Power Train Redundancy Rework +15%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 20.0,
            "scenario_priority": ["base", "conservative", "commissioning_failure_window", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.2, "moderate_max_pct": 3.8, "fallback_pct": 1.0},
    },
    "specialty_laboratory_v1": {
        "primary_control_variable": {
            "tile_id": "validation_air_change_rebalance_plus_12",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "Validation Air Change Rebalance +12%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 10.0,
            "scenario_priority": ["base", "conservative", "validation_retest_cycle", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.5, "moderate_max_pct": 4.2, "fallback_pct": 1.4},
    },
    "specialty_self_storage_v1": {
        "primary_control_variable": {
            "tile_id": "access_control_and_surveillance_plus_10",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Access Control + Surveillance +10%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 5.0,
            "scenario_priority": ["base", "conservative", "leaseup_drag", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.5, "fallback_pct": 2.2},
    },
    "specialty_car_dealership_v1": {
        "primary_control_variable": {
            "tile_id": "service_bay_process_mep_plus_11",
            "metric_ref": "trade_breakdown.mechanical",
            "label": "Service Bay Process MEP +11%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 8.0,
            "scenario_priority": ["base", "conservative", "service_absorption_slip", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.8, "moderate_max_pct": 4.8, "fallback_pct": 1.9},
    },
    "specialty_broadcast_facility_v1": {
        "primary_control_variable": {
            "tile_id": "signal_chain_and_power_quality_plus_12",
            "metric_ref": "trade_breakdown.electrical",
            "label": "Signal Chain + Power Quality +12%",
        },
        "collapse_trigger": {
            "metric": "value_gap_pct",
            "operator": "<=",
            "threshold": 12.0,
            "scenario_priority": ["base", "conservative", "control_room_recommissioning", "ugly"],
        },
        "flex_calibration": {"tight_max_pct": 1.6, "moderate_max_pct": 4.4, "fallback_pct": 1.7},
    },
}


def get_decision_insurance_policy(profile_id: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(profile_id, str) or not profile_id.strip():
        return None
    resolved = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id.strip())
    if not isinstance(resolved, dict):
        return None
    return copy.deepcopy(resolved)
