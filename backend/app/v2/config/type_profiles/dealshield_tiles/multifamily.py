"""DealShield tile profiles for multifamily types."""

DEALSHIELD_TILE_DEFAULTS = {
    "market_rate_apartments": "multifamily_market_rate_apartments_v1",
    "luxury_apartments": "multifamily_luxury_apartments_v1",
    "affordable_housing": "multifamily_affordable_housing_v1",
}


DEALSHIELD_TILE_PROFILES = {
    "multifamily_market_rate_apartments_v1": {
        "version": "v1",
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "cost_per_sf_plus_10",
                "label": "Cost/SF +10%",
                "metric_ref": "totals.cost_per_sf",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "finishes_plus_10",
                "label": "Finishes +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "structural_carry_proxy_plus_5",
                "label": "Structural Base Carry Proxy +5%",
                "metric_ref": "trade_breakdown.structural",
                "required": False,
                "transform": {"op": "mul", "value": 1.05},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
            },
            {
                "row_id": "ugly",
                "label": "Ugly",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
                "plus_tiles": ["finishes_plus_10"],
            },
            {
                "row_id": "structural_carry_proxy_stress",
                "label": "Structural Carry Proxy Stress",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["structural_carry_proxy_plus_5"],
            },
        ],
        "provenance": {
            "notes": "Multifamily market-rate apartments tile profile v1.",
        },
    },
    "multifamily_luxury_apartments_v1": {
        "version": "v1",
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "cost_per_sf_plus_10",
                "label": "Cost/SF +10%",
                "metric_ref": "totals.cost_per_sf",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "finishes_plus_10",
                "label": "Finishes +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "amenity_finish_plus_15",
                "label": "Amenity Finishes +15%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.15},
            },
            {
                "tile_id": "amenity_mep_plus_10",
                "label": "Amenity MEP +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
            },
            {
                "row_id": "amenity_overrun",
                "label": "Amenity Overrun",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
                "plus_tiles": ["amenity_finish_plus_15"],
            },
            {
                "row_id": "amenity_system_stress",
                "label": "Amenity Systems Stress",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["amenity_mep_plus_10"],
            },
        ],
        "provenance": {
            "notes": "Multifamily luxury apartments tile profile v1.",
        },
    },
    "multifamily_affordable_housing_v1": {
        "version": "v1",
        "tiles": [
            {
                "tile_id": "cost_plus_10",
                "label": "Cost +10%",
                "metric_ref": "totals.total_project_cost",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "cost_per_sf_plus_10",
                "label": "Cost/SF +10%",
                "metric_ref": "totals.cost_per_sf",
                "required": True,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "finishes_plus_10",
                "label": "Finishes +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "compliance_electrical_plus_8",
                "label": "Compliance Electrical +8%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.08},
            },
            {
                "tile_id": "compliance_plumbing_plus_6",
                "label": "Compliance Plumbing +6%",
                "metric_ref": "trade_breakdown.plumbing",
                "required": False,
                "transform": {"op": "mul", "value": 1.06},
            },
        ],
        "derived_rows": [
            {
                "row_id": "conservative",
                "label": "Conservative",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
            },
            {
                "row_id": "compliance_delay",
                "label": "Compliance Delay",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["compliance_electrical_plus_8"],
            },
            {
                "row_id": "funding_gap",
                "label": "Funding Gap",
                "apply_tiles": ["cost_plus_10", "cost_per_sf_plus_10"],
                "plus_tiles": ["compliance_plumbing_plus_6", "finishes_plus_10"],
            },
        ],
        "provenance": {
            "notes": "Multifamily affordable housing tile profile v1.",
        },
    },
}
