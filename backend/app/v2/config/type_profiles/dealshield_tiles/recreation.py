"""DealShield tile profiles for recreation types."""


DEALSHIELD_TILE_PROFILES = {
    "recreation_fitness_center_v1": {
        "profile_id": "recreation_fitness_center_v1",
        "version": "v1",
        "decision_table_columns": [
            {"id": "total_cost", "label": "Total Project Cost", "metric_ref": "totals.total_project_cost"},
            {"id": "cost_per_sf", "label": "Cost/SF", "metric_ref": "totals.cost_per_sf"},
            {
                "id": "conditioning_risk",
                "label": "Conditioning Risk",
                "metric_ref": "row.risk_labels.conditioning_risk",
            },
            {
                "id": "wet_core_risk",
                "label": "Wet Core Risk",
                "metric_ref": "row.risk_labels.wet_core_risk",
            },
            {
                "id": "usage_risk",
                "label": "Usage Risk",
                "metric_ref": "row.risk_labels.usage_risk",
            },
        ],
        "base_row": {
            "label": "Base",
            "delta": "Program baseline",
            "risk_labels": {
                "conditioning_risk": "low",
                "wet_core_risk": "low",
                "usage_risk": "low",
            },
        },
        "tiles": [
            {
                "tile_id": "fitness_center_hvac_load_plus_11",
                "label": "High-Load Ventilation +11%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.11},
                "required": True,
            },
            {
                "tile_id": "fitness_center_locker_plumbing_plus_9",
                "label": "Locker/Shower Plumbing +9%",
                "metric_ref": "trade_breakdown.plumbing",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "fitness_center_peak_power_density_plus_8",
                "label": "Peak Power Density +8%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "fitness_center_membership_revenue_minus_7",
                "label": "Membership Revenue -7%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.93},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "fitness_center_hvac_load_plus_11",
                    "fitness_center_membership_revenue_minus_7",
                ],
                "risk_labels": {
                    "conditioning_risk": "med",
                    "wet_core_risk": "low",
                    "usage_risk": "med",
                },
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "fitness_center_hvac_load_plus_11",
                    "fitness_center_locker_plumbing_plus_9",
                    "fitness_center_peak_power_density_plus_8",
                    "fitness_center_membership_revenue_minus_7",
                ],
                "risk_labels": {
                    "conditioning_risk": "high",
                    "wet_core_risk": "high",
                    "usage_risk": "high",
                },
            },
            {
                "row_id": "fitness_center_peak_utilization_crunch",
                "label": "Peak Utilization Crunch",
                "delta": "HVAC and power undersized for peak class stacking",
                "apply_tiles": [
                    "fitness_center_hvac_load_plus_11",
                    "fitness_center_peak_power_density_plus_8",
                ],
                "risk_labels": {
                    "conditioning_risk": "high",
                    "wet_core_risk": "low",
                    "usage_risk": "high",
                },
            },
        ],
        "provenance": {
            "notes": "Fitness-center-authored stress profile anchored to ventilation, locker plumbing, and power density.",
        },
    },
    "recreation_sports_complex_v1": {
        "profile_id": "recreation_sports_complex_v1",
        "version": "v1",
        "decision_table_columns": [
            {"id": "total_cost", "label": "Total Project Cost", "metric_ref": "totals.total_project_cost"},
            {"id": "cost_per_sf", "label": "Cost/SF", "metric_ref": "totals.cost_per_sf"},
            {
                "id": "span_risk",
                "label": "Long-Span Risk",
                "metric_ref": "row.risk_labels.span_risk",
            },
            {
                "id": "event_systems_risk",
                "label": "Event Systems Risk",
                "metric_ref": "row.risk_labels.event_systems_risk",
            },
            {
                "id": "scheduling_risk",
                "label": "Scheduling Risk",
                "metric_ref": "row.risk_labels.scheduling_risk",
            },
        ],
        "base_row": {
            "label": "Base",
            "delta": "Program baseline",
            "risk_labels": {
                "span_risk": "low",
                "event_systems_risk": "low",
                "scheduling_risk": "low",
            },
        },
        "tiles": [
            {
                "tile_id": "sports_complex_long_span_structure_plus_12",
                "label": "Long-Span Structural Premium +12%",
                "metric_ref": "trade_breakdown.structural",
                "transform": {"op": "mul", "value": 1.12},
                "required": True,
            },
            {
                "tile_id": "sports_complex_event_hvac_plus_8",
                "label": "Event Hall HVAC +8%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "sports_complex_scoreboard_power_plus_9",
                "label": "Scoreboard/Lighting Power +9%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "sports_complex_event_revenue_minus_6",
                "label": "Tournament Revenue -6%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.94},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "sports_complex_long_span_structure_plus_12",
                    "sports_complex_event_revenue_minus_6",
                ],
                "risk_labels": {
                    "span_risk": "med",
                    "event_systems_risk": "low",
                    "scheduling_risk": "med",
                },
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "sports_complex_long_span_structure_plus_12",
                    "sports_complex_event_hvac_plus_8",
                    "sports_complex_scoreboard_power_plus_9",
                    "sports_complex_event_revenue_minus_6",
                ],
                "risk_labels": {
                    "span_risk": "high",
                    "event_systems_risk": "high",
                    "scheduling_risk": "high",
                },
            },
            {
                "row_id": "sports_complex_tournament_schedule_slip",
                "label": "Tournament Schedule Slip",
                "delta": "Late event calendar compression and turnover rework",
                "apply_tiles": [
                    "sports_complex_event_hvac_plus_8",
                    "sports_complex_scoreboard_power_plus_9",
                ],
                "risk_labels": {
                    "span_risk": "low",
                    "event_systems_risk": "high",
                    "scheduling_risk": "high",
                },
            },
        ],
        "provenance": {
            "notes": "Sports-complex-authored stress profile with long-span structure and event operations anchors.",
        },
    },
    "recreation_aquatic_center_v1": {
        "profile_id": "recreation_aquatic_center_v1",
        "version": "v1",
        "decision_table_columns": [
            {"id": "total_cost", "label": "Total Project Cost", "metric_ref": "totals.total_project_cost"},
            {"id": "cost_per_sf", "label": "Cost/SF", "metric_ref": "totals.cost_per_sf"},
            {
                "id": "humidity_risk",
                "label": "Humidity-Control Risk",
                "metric_ref": "row.risk_labels.humidity_risk",
            },
            {
                "id": "water_system_risk",
                "label": "Water-System Risk",
                "metric_ref": "row.risk_labels.water_system_risk",
            },
            {
                "id": "operations_risk",
                "label": "Operations Risk",
                "metric_ref": "row.risk_labels.operations_risk",
            },
        ],
        "base_row": {
            "label": "Base",
            "delta": "Program baseline",
            "risk_labels": {
                "humidity_risk": "low",
                "water_system_risk": "low",
                "operations_risk": "low",
            },
        },
        "tiles": [
            {
                "tile_id": "aquatic_center_dehumidification_plus_14",
                "label": "Natatorium Dehumidification +14%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.14},
                "required": True,
            },
            {
                "tile_id": "aquatic_center_pool_piping_plus_12",
                "label": "Pool Piping/Filtration +12%",
                "metric_ref": "trade_breakdown.plumbing",
                "transform": {"op": "mul", "value": 1.12},
                "required": True,
            },
            {
                "tile_id": "aquatic_center_corrosion_hardening_plus_9",
                "label": "Corrosion Hardening +9%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "aquatic_center_program_revenue_minus_8",
                "label": "Program Revenue -8%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.92},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "aquatic_center_dehumidification_plus_14",
                    "aquatic_center_program_revenue_minus_8",
                ],
                "risk_labels": {
                    "humidity_risk": "med",
                    "water_system_risk": "low",
                    "operations_risk": "med",
                },
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "aquatic_center_dehumidification_plus_14",
                    "aquatic_center_pool_piping_plus_12",
                    "aquatic_center_corrosion_hardening_plus_9",
                    "aquatic_center_program_revenue_minus_8",
                ],
                "risk_labels": {
                    "humidity_risk": "high",
                    "water_system_risk": "high",
                    "operations_risk": "high",
                },
            },
            {
                "row_id": "aquatic_center_water_chemistry_rework",
                "label": "Water Chemistry Rework",
                "delta": "Filtration and chemistry sequencing revisions",
                "apply_tiles": [
                    "aquatic_center_pool_piping_plus_12",
                    "aquatic_center_corrosion_hardening_plus_9",
                ],
                "risk_labels": {
                    "humidity_risk": "low",
                    "water_system_risk": "high",
                    "operations_risk": "med",
                },
            },
        ],
        "provenance": {
            "notes": "Aquatic-center-authored stress profile with humidity control, piping, and corrosion anchors.",
        },
    },
    "recreation_recreation_center_v1": {
        "profile_id": "recreation_recreation_center_v1",
        "version": "v1",
        "decision_table_columns": [
            {"id": "total_cost", "label": "Total Project Cost", "metric_ref": "totals.total_project_cost"},
            {"id": "cost_per_sf", "label": "Cost/SF", "metric_ref": "totals.cost_per_sf"},
            {
                "id": "program_risk",
                "label": "Program-Mix Risk",
                "metric_ref": "row.risk_labels.program_risk",
            },
            {
                "id": "mep_risk",
                "label": "Shared MEP Risk",
                "metric_ref": "row.risk_labels.mep_risk",
            },
            {
                "id": "operations_risk",
                "label": "Operations Risk",
                "metric_ref": "row.risk_labels.operations_risk",
            },
        ],
        "base_row": {
            "label": "Base",
            "delta": "Program baseline",
            "risk_labels": {
                "program_risk": "low",
                "mep_risk": "low",
                "operations_risk": "low",
            },
        },
        "tiles": [
            {
                "tile_id": "recreation_center_multiprogram_finishes_plus_10",
                "label": "Multiprogram Fit-Out +10%",
                "metric_ref": "trade_breakdown.finishes",
                "transform": {"op": "mul", "value": 1.10},
                "required": True,
            },
            {
                "tile_id": "recreation_center_shared_hvac_plus_9",
                "label": "Shared-Use HVAC +9%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "recreation_center_locker_plumbing_plus_8",
                "label": "Locker Plumbing +8%",
                "metric_ref": "trade_breakdown.plumbing",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "recreation_center_program_revenue_minus_5",
                "label": "Program Revenue -5%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.95},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "recreation_center_multiprogram_finishes_plus_10",
                    "recreation_center_program_revenue_minus_5",
                ],
                "risk_labels": {
                    "program_risk": "med",
                    "mep_risk": "low",
                    "operations_risk": "med",
                },
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "recreation_center_multiprogram_finishes_plus_10",
                    "recreation_center_shared_hvac_plus_9",
                    "recreation_center_locker_plumbing_plus_8",
                    "recreation_center_program_revenue_minus_5",
                ],
                "risk_labels": {
                    "program_risk": "high",
                    "mep_risk": "high",
                    "operations_risk": "high",
                },
            },
            {
                "row_id": "recreation_center_program_mix_shift",
                "label": "Program Mix Shift",
                "delta": "Late conversion between youth, fitness, and event programming",
                "apply_tiles": [
                    "recreation_center_multiprogram_finishes_plus_10",
                    "recreation_center_shared_hvac_plus_9",
                ],
                "risk_labels": {
                    "program_risk": "high",
                    "mep_risk": "med",
                    "operations_risk": "med",
                },
            },
        ],
        "provenance": {
            "notes": "Recreation-center-authored stress profile focused on shared-use fit-out and mixed operations.",
        },
    },
    "recreation_stadium_v1": {
        "profile_id": "recreation_stadium_v1",
        "version": "v1",
        "decision_table_columns": [
            {"id": "total_cost", "label": "Total Project Cost", "metric_ref": "totals.total_project_cost"},
            {"id": "cost_per_sf", "label": "Cost/SF", "metric_ref": "totals.cost_per_sf"},
            {
                "id": "seating_bowl_risk",
                "label": "Seating-Bowl Risk",
                "metric_ref": "row.risk_labels.seating_bowl_risk",
            },
            {
                "id": "event_power_risk",
                "label": "Event-Power Risk",
                "metric_ref": "row.risk_labels.event_power_risk",
            },
            {
                "id": "attendance_risk",
                "label": "Attendance Risk",
                "metric_ref": "row.risk_labels.attendance_risk",
            },
        ],
        "base_row": {
            "label": "Base",
            "delta": "Program baseline",
            "risk_labels": {
                "seating_bowl_risk": "low",
                "event_power_risk": "low",
                "attendance_risk": "low",
            },
        },
        "tiles": [
            {
                "tile_id": "stadium_seating_bowl_structure_plus_15",
                "label": "Seating Bowl Structure +15%",
                "metric_ref": "trade_breakdown.structural",
                "transform": {"op": "mul", "value": 1.15},
                "required": True,
            },
            {
                "tile_id": "stadium_crowd_ventilation_plus_10",
                "label": "Crowd Ventilation +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.10},
                "required": True,
            },
            {
                "tile_id": "stadium_event_power_plus_13",
                "label": "Event Power/Lighting +13%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.13},
                "required": True,
            },
            {
                "tile_id": "stadium_attendance_revenue_minus_9",
                "label": "Attendance Revenue -9%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.91},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "stadium_seating_bowl_structure_plus_15",
                    "stadium_attendance_revenue_minus_9",
                ],
                "risk_labels": {
                    "seating_bowl_risk": "med",
                    "event_power_risk": "low",
                    "attendance_risk": "med",
                },
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "stadium_seating_bowl_structure_plus_15",
                    "stadium_crowd_ventilation_plus_10",
                    "stadium_event_power_plus_13",
                    "stadium_attendance_revenue_minus_9",
                ],
                "risk_labels": {
                    "seating_bowl_risk": "high",
                    "event_power_risk": "high",
                    "attendance_risk": "high",
                },
            },
            {
                "row_id": "stadium_event_calendar_disruption",
                "label": "Event Calendar Disruption",
                "delta": "Calendar compression and turnover logistics miss",
                "apply_tiles": [
                    "stadium_crowd_ventilation_plus_10",
                    "stadium_event_power_plus_13",
                ],
                "risk_labels": {
                    "seating_bowl_risk": "low",
                    "event_power_risk": "high",
                    "attendance_risk": "high",
                },
            },
        ],
        "provenance": {
            "notes": "Stadium-authored stress profile for seating-bowl structure, crowd systems, and event revenue volatility.",
        },
    },
}


DEALSHIELD_TILE_DEFAULTS = {
    "fitness_center": "recreation_fitness_center_v1",
    "sports_complex": "recreation_sports_complex_v1",
    "aquatic_center": "recreation_aquatic_center_v1",
    "recreation_center": "recreation_recreation_center_v1",
    "stadium": "recreation_stadium_v1",
}
