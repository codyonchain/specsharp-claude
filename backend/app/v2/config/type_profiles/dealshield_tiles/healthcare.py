"""DealShield tile profiles for healthcare types."""

DEALSHIELD_TILE_DEFAULTS = {
    "surgical_center": "healthcare_surgical_center_v1",
    "imaging_center": "healthcare_imaging_center_v1",
    "urgent_care": "healthcare_urgent_care_v1",
    "outpatient_clinic": "healthcare_outpatient_clinic_v1",
    "medical_office_building": "healthcare_medical_office_building_v1",
    "dental_office": "healthcare_dental_office_v1",
    "hospital": "healthcare_hospital_v1",
    "medical_center": "healthcare_medical_center_v1",
    "nursing_home": "healthcare_nursing_home_v1",
    "rehabilitation": "healthcare_rehabilitation_v1",
}


def _base_tiles() -> list[dict]:
    return [
        {
            "tile_id": "cost_plus_10",
            "label": "Cost +10%",
            "metric_ref": "totals.total_project_cost",
            "required": True,
            "transform": {"op": "mul", "value": 1.10},
        },
        {
            "tile_id": "revenue_minus_10",
            "label": "Revenue -10%",
            "metric_ref": "revenue_analysis.annual_revenue",
            "required": True,
            "transform": {"op": "mul", "value": 0.90},
        },
    ]


def _base_rows(extra_tile_id: str, extra_row_id: str, extra_row_label: str) -> list[dict]:
    return [
        {
            "row_id": "conservative",
            "label": "Conservative",
            "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
        },
        {
            "row_id": "ugly",
            "label": "Ugly",
            "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            "plus_tiles": [extra_tile_id],
        },
        {
            "row_id": extra_row_id,
            "label": extra_row_label,
            "apply_tiles": ["cost_plus_10"],
            "plus_tiles": [extra_tile_id],
        },
    ]


DEALSHIELD_TILE_PROFILES = {
    "healthcare_surgical_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_surgical_center_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "or_turnover_and_sterile_core_plus_12",
                "label": "OR Turnover + Sterile Core +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.12},
            }
        ],
        "derived_rows": _base_rows(
            "or_turnover_and_sterile_core_plus_12",
            "sterile_reprocessing_drag",
            "Sterile Reprocessing Drag",
        ),
        "provenance": {"notes": "Healthcare surgical center tile profile v1."},
    },
    "healthcare_imaging_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_imaging_center_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "shielding_and_power_quality_plus_11",
                "label": "Shielding + Power Quality +11%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.11},
            }
        ],
        "derived_rows": _base_rows(
            "shielding_and_power_quality_plus_11",
            "magnet_commissioning_slip",
            "Magnet Commissioning Slip",
        ),
        "provenance": {"notes": "Healthcare imaging center tile profile v1."},
    },
    "healthcare_urgent_care_v1": {
        "version": "v1",
        "profile_id": "healthcare_urgent_care_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "triage_flow_and_lab_turns_plus_10",
                "label": "Triage Flow + Lab Turns +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "triage_flow_and_lab_turns_plus_10",
            "weekend_surge_breakpoint",
            "Weekend Surge Breakpoint",
        ),
        "provenance": {"notes": "Healthcare urgent care tile profile v1."},
    },
    "healthcare_outpatient_clinic_v1": {
        "version": "v1",
        "profile_id": "healthcare_outpatient_clinic_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "exam_program_and_room_standard_plus_9",
                "label": "Exam Program + Room Standard +9%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.09},
            }
        ],
        "derived_rows": _base_rows(
            "exam_program_and_room_standard_plus_9",
            "care_team_growth_mismatch",
            "Care Team Growth Mismatch",
        ),
        "provenance": {"notes": "Healthcare outpatient clinic tile profile v1."},
    },
    "healthcare_medical_office_building_v1": {
        "version": "v1",
        "profile_id": "healthcare_medical_office_building_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "tenant_fitout_mep_stack_plus_10",
                "label": "Tenant Fit-Out MEP Stack +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "tenant_fitout_mep_stack_plus_10",
            "anchor_tenant_restack",
            "Anchor Tenant Restack",
        ),
        "provenance": {"notes": "Healthcare medical office building tile profile v1."},
    },
    "healthcare_dental_office_v1": {
        "version": "v1",
        "profile_id": "healthcare_dental_office_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "chairside_vacuum_and_gas_plus_11",
                "label": "Chairside Vacuum + Gas +11%",
                "metric_ref": "trade_breakdown.plumbing",
                "required": False,
                "transform": {"op": "mul", "value": 1.11},
            }
        ],
        "derived_rows": _base_rows(
            "chairside_vacuum_and_gas_plus_11",
            "sterilization_center_rework",
            "Sterilization Center Rework",
        ),
        "provenance": {"notes": "Healthcare dental office tile profile v1."},
    },
    "healthcare_hospital_v1": {
        "version": "v1",
        "profile_id": "healthcare_hospital_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "acuity_mep_redundancy_plus_12",
                "label": "Acuity MEP + Redundancy +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.12},
            }
        ],
        "derived_rows": _base_rows(
            "acuity_mep_redundancy_plus_12",
            "tower_commissioning_retest",
            "Tower Commissioning Retest",
        ),
        "provenance": {"notes": "Healthcare hospital tile profile v1."},
    },
    "healthcare_medical_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_medical_center_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "service_line_power_density_plus_11",
                "label": "Service-Line Power Density +11%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.11},
            }
        ],
        "derived_rows": _base_rows(
            "service_line_power_density_plus_11",
            "specialty_program_shift",
            "Specialty Program Shift",
        ),
        "provenance": {"notes": "Healthcare medical center tile profile v1."},
    },
    "healthcare_nursing_home_v1": {
        "version": "v1",
        "profile_id": "healthcare_nursing_home_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "resident_room_life_safety_plus_9",
                "label": "Resident Room Life-Safety +9%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.09},
            }
        ],
        "derived_rows": _base_rows(
            "resident_room_life_safety_plus_9",
            "state_survey_correction_cycle",
            "State Survey Correction Cycle",
        ),
        "provenance": {"notes": "Healthcare nursing home tile profile v1."},
    },
    "healthcare_rehabilitation_v1": {
        "version": "v1",
        "profile_id": "healthcare_rehabilitation_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "therapy_gym_mep_integration_plus_10",
                "label": "Therapy Gym MEP Integration +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "therapy_gym_mep_integration_plus_10",
            "equipment_path_and_rehab_flow",
            "Equipment Path + Rehab Flow",
        ),
        "provenance": {"notes": "Healthcare rehabilitation tile profile v1."},
    },
}
