"""DealShield tile profiles for specialty types."""

DEALSHIELD_TILE_PROFILES = {
    "specialty_data_center_v1": {
        "profile_id": "specialty_data_center_v1",
        "version": "v1",
        "base_row": {"label": "Base", "delta": "Base"},
        "tiles": [
            {
                "tile_id": "power_train_redundancy_rework_plus_15",
                "label": "Power Train Redundancy Rework +15%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.15},
                "required": True,
            },
            {
                "tile_id": "cooling_plant_rebalance_plus_12",
                "label": "Cooling Plant Rebalance +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.12},
                "required": True,
            },
            {
                "tile_id": "commissioning_labor_plus_8",
                "label": "Commissioning Labor +8%",
                "metric_ref": "totals.total_project_cost",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "lease_ramp_minus_10",
                "label": "Lease Ramp -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "transform": {"op": "mul", "value": 0.90},
                "required": True,
            },
            {
                "tile_id": "fiber_diversity_rework_plus_6",
                "label": "Fiber Diversity Rework +6%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.06},
                "required": True,
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "delta": "Moderate downside",
                "apply_tiles": [
                    "power_train_redundancy_rework_plus_15",
                    "lease_ramp_minus_10",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Med", "operations": "Med"},
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "power_train_redundancy_rework_plus_15",
                    "cooling_plant_rebalance_plus_12",
                    "commissioning_labor_plus_8",
                    "lease_ramp_minus_10",
                ],
                "risk_labels": {"cost": "High", "schedule": "High", "operations": "High"},
            },
            {
                "row_id": "commissioning_failure_window",
                "label": "Commissioning Failure Window",
                "delta": "Concurrent maintainability miss",
                "apply_tiles": [
                    "power_train_redundancy_rework_plus_15",
                    "cooling_plant_rebalance_plus_12",
                    "fiber_diversity_rework_plus_6",
                ],
                "risk_labels": {"cost": "High", "schedule": "High", "operations": "High"},
            },
        ],
    },
    "specialty_laboratory_v1": {
        "profile_id": "specialty_laboratory_v1",
        "version": "v1",
        "base_row": {"label": "Base", "delta": "Base"},
        "tiles": [
            {
                "tile_id": "validation_air_change_rebalance_plus_12",
                "label": "Validation Air Change Rebalance +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.12},
                "required": True,
            },
            {
                "tile_id": "cleanroom_recertification_plus_9",
                "label": "Cleanroom Recertification +9%",
                "metric_ref": "totals.total_project_cost",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "casework_coordination_plus_8",
                "label": "Casework Coordination +8%",
                "metric_ref": "trade_breakdown.finishes",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "grant_or_program_revenue_minus_8",
                "label": "Grant / Program Revenue -8%",
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
                    "validation_air_change_rebalance_plus_12",
                    "grant_or_program_revenue_minus_8",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Med", "operations": "Med"},
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "validation_air_change_rebalance_plus_12",
                    "cleanroom_recertification_plus_9",
                    "casework_coordination_plus_8",
                    "grant_or_program_revenue_minus_8",
                ],
                "risk_labels": {"cost": "High", "schedule": "High", "operations": "High"},
            },
            {
                "row_id": "validation_retest_cycle",
                "label": "Validation Retest Cycle",
                "delta": "Late retest and balancing",
                "apply_tiles": [
                    "validation_air_change_rebalance_plus_12",
                    "cleanroom_recertification_plus_9",
                ],
                "risk_labels": {"cost": "High", "schedule": "High", "operations": "Med"},
            },
        ],
    },
    "specialty_self_storage_v1": {
        "profile_id": "specialty_self_storage_v1",
        "version": "v1",
        "base_row": {"label": "Base", "delta": "Base"},
        "tiles": [
            {
                "tile_id": "access_control_and_surveillance_plus_10",
                "label": "Access Control + Surveillance +10%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.10},
                "required": True,
            },
            {
                "tile_id": "climate_zone_rework_plus_8",
                "label": "Climate Zone Rework +8%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.08},
                "required": True,
            },
            {
                "tile_id": "site_and_paving_plus_6",
                "label": "Site / Paving +6%",
                "metric_ref": "totals.total_project_cost",
                "transform": {"op": "mul", "value": 1.06},
                "required": True,
            },
            {
                "tile_id": "leaseup_velocity_minus_7",
                "label": "Lease-Up Velocity -7%",
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
                    "access_control_and_surveillance_plus_10",
                    "leaseup_velocity_minus_7",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Low", "operations": "Med"},
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "access_control_and_surveillance_plus_10",
                    "climate_zone_rework_plus_8",
                    "site_and_paving_plus_6",
                    "leaseup_velocity_minus_7",
                ],
                "risk_labels": {"cost": "High", "schedule": "Med", "operations": "High"},
            },
            {
                "row_id": "leaseup_drag",
                "label": "Lease-Up Drag",
                "delta": "Slow absorption and churn",
                "apply_tiles": [
                    "access_control_and_surveillance_plus_10",
                    "leaseup_velocity_minus_7",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Low", "operations": "High"},
            },
        ],
    },
    "specialty_car_dealership_v1": {
        "profile_id": "specialty_car_dealership_v1",
        "version": "v1",
        "base_row": {"label": "Base", "delta": "Base"},
        "tiles": [
            {
                "tile_id": "service_bay_process_mep_plus_11",
                "label": "Service Bay Process MEP +11%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.11},
                "required": True,
            },
            {
                "tile_id": "showroom_finish_refresh_plus_9",
                "label": "Showroom Finish Refresh +9%",
                "metric_ref": "trade_breakdown.finishes",
                "transform": {"op": "mul", "value": 1.09},
                "required": True,
            },
            {
                "tile_id": "yard_and_delivery_regrade_plus_6",
                "label": "Yard / Delivery Regrade +6%",
                "metric_ref": "totals.total_project_cost",
                "transform": {"op": "mul", "value": 1.06},
                "required": True,
            },
            {
                "tile_id": "sales_absorption_minus_9",
                "label": "Sales Absorption -9%",
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
                    "service_bay_process_mep_plus_11",
                    "sales_absorption_minus_9",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Med", "operations": "Med"},
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "service_bay_process_mep_plus_11",
                    "showroom_finish_refresh_plus_9",
                    "yard_and_delivery_regrade_plus_6",
                    "sales_absorption_minus_9",
                ],
                "risk_labels": {"cost": "High", "schedule": "Med", "operations": "High"},
            },
            {
                "row_id": "service_absorption_slip",
                "label": "Service Absorption Slip",
                "delta": "Ramp below plan",
                "apply_tiles": [
                    "service_bay_process_mep_plus_11",
                    "sales_absorption_minus_9",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Med", "operations": "High"},
            },
        ],
    },
    "specialty_broadcast_facility_v1": {
        "profile_id": "specialty_broadcast_facility_v1",
        "version": "v1",
        "base_row": {"label": "Base", "delta": "Base"},
        "tiles": [
            {
                "tile_id": "signal_chain_and_power_quality_plus_12",
                "label": "Signal Chain + Power Quality +12%",
                "metric_ref": "trade_breakdown.electrical",
                "transform": {"op": "mul", "value": 1.12},
                "required": True,
            },
            {
                "tile_id": "acoustic_isolation_rework_plus_10",
                "label": "Acoustic Isolation Rework +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "transform": {"op": "mul", "value": 1.10},
                "required": True,
            },
            {
                "tile_id": "studio_fitout_plus_7",
                "label": "Studio Fit-Out +7%",
                "metric_ref": "totals.total_project_cost",
                "transform": {"op": "mul", "value": 1.07},
                "required": True,
            },
            {
                "tile_id": "sponsor_revenue_minus_8",
                "label": "Sponsor Revenue -8%",
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
                    "signal_chain_and_power_quality_plus_12",
                    "sponsor_revenue_minus_8",
                ],
                "risk_labels": {"cost": "Med", "schedule": "Med", "operations": "Med"},
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "delta": "Severe downside",
                "apply_tiles": [
                    "signal_chain_and_power_quality_plus_12",
                    "acoustic_isolation_rework_plus_10",
                    "studio_fitout_plus_7",
                    "sponsor_revenue_minus_8",
                ],
                "risk_labels": {"cost": "High", "schedule": "High", "operations": "High"},
            },
            {
                "row_id": "control_room_recommissioning",
                "label": "Control Room Recommissioning",
                "delta": "Signal integrity retune",
                "apply_tiles": [
                    "signal_chain_and_power_quality_plus_12",
                    "acoustic_isolation_rework_plus_10",
                ],
                "risk_labels": {"cost": "High", "schedule": "Med", "operations": "High"},
            },
        ],
    },
}

DEALSHIELD_TILE_DEFAULTS = {
    "data_center": "specialty_data_center_v1",
    "laboratory": "specialty_laboratory_v1",
    "self_storage": "specialty_self_storage_v1",
    "car_dealership": "specialty_car_dealership_v1",
    "broadcast_facility": "specialty_broadcast_facility_v1",
}
