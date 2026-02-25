"""DealShield tile profiles for educational types."""

DEALSHIELD_TILE_PROFILES = {
    "educational_elementary_school_v1": {
        "version": "v1",
        "profile_id": "educational_elementary_school_v1",
        "tiles": [
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
                "metric_ref": "modifiers.revenue_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "early_grade_program_and_ventilation_plus_9",
                "label": "Early-Grade Program + Ventilation +9%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": True,
                "transform": {"op": "mul", "value": 1.09},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": [
                    "cost_plus_10",
                    "revenue_minus_10",
                    "early_grade_program_and_ventilation_plus_9",
                ],
            },
            {
                "row_id": "elementary_enrollment_rightsizing_drag",
                "label": "Enrollment Rightsizing Drag",
                "apply_tiles": ["early_grade_program_and_ventilation_plus_9"],
            },
        ],
        "provenance": {"vertical": "educational", "subtype": "elementary_school"},
    },
    "educational_middle_school_v1": {
        "version": "v1",
        "profile_id": "educational_middle_school_v1",
        "tiles": [
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
                "metric_ref": "modifiers.revenue_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "media_and_stem_load_plus_10",
                "label": "Media + STEM Load +10%",
                "metric_ref": "trade_breakdown.electrical",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": [
                    "cost_plus_10",
                    "revenue_minus_10",
                    "media_and_stem_load_plus_10",
                ],
            },
            {
                "row_id": "middle_curriculum_lab_fitout_drag",
                "label": "Curriculum Lab Fit-Out Drag",
                "apply_tiles": ["media_and_stem_load_plus_10"],
            },
        ],
        "provenance": {"vertical": "educational", "subtype": "middle_school"},
    },
    "educational_high_school_v1": {
        "version": "v1",
        "profile_id": "educational_high_school_v1",
        "tiles": [
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
                "metric_ref": "modifiers.revenue_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "athletics_and_performing_arts_plus_11",
                "label": "Athletics + Performing Arts +11%",
                "metric_ref": "trade_breakdown.finishes",
                "required": True,
                "transform": {"op": "mul", "value": 1.11},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": [
                    "cost_plus_10",
                    "revenue_minus_10",
                    "athletics_and_performing_arts_plus_11",
                ],
            },
            {
                "row_id": "high_school_activity_program_bloat",
                "label": "Activity Program Bloat",
                "apply_tiles": ["athletics_and_performing_arts_plus_11"],
            },
        ],
        "provenance": {"vertical": "educational", "subtype": "high_school"},
    },
    "educational_university_v1": {
        "version": "v1",
        "profile_id": "educational_university_v1",
        "tiles": [
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
                "metric_ref": "modifiers.revenue_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "research_mep_and_controls_plus_12",
                "label": "Research MEP + Controls +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": True,
                "transform": {"op": "mul", "value": 1.12},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": [
                    "cost_plus_10",
                    "revenue_minus_10",
                    "research_mep_and_controls_plus_12",
                ],
            },
            {
                "row_id": "university_research_commissioning_drag",
                "label": "Research Commissioning Drag",
                "apply_tiles": ["research_mep_and_controls_plus_12"],
            },
        ],
        "provenance": {"vertical": "educational", "subtype": "university"},
    },
    "educational_community_college_v1": {
        "version": "v1",
        "profile_id": "educational_community_college_v1",
        "tiles": [
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
                "metric_ref": "modifiers.revenue_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "vocational_fitout_and_turnover_plus_9",
                "label": "Vocational Fit-Out + Turnover +9%",
                "metric_ref": "trade_breakdown.finishes",
                "required": True,
                "transform": {"op": "mul", "value": 1.09},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": [
                    "cost_plus_10",
                    "revenue_minus_10",
                    "vocational_fitout_and_turnover_plus_9",
                ],
            },
            {
                "row_id": "community_college_workforce_program_shift",
                "label": "Workforce Program Shift",
                "apply_tiles": ["vocational_fitout_and_turnover_plus_9"],
            },
        ],
        "provenance": {"vertical": "educational", "subtype": "community_college"},
    },
}

DEALSHIELD_TILE_DEFAULTS = {
    "elementary_school": "educational_elementary_school_v1",
    "middle_school": "educational_middle_school_v1",
    "high_school": "educational_high_school_v1",
    "university": "educational_university_v1",
    "community_college": "educational_community_college_v1",
}
