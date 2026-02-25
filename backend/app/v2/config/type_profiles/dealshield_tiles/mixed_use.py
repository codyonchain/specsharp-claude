"""DealShield tile profiles for mixed_use types."""

DEALSHIELD_TILE_DEFAULTS = {
    "office_residential": "mixed_use_office_residential_v1",
    "retail_residential": "mixed_use_retail_residential_v1",
    "hotel_retail": "mixed_use_hotel_retail_v1",
    "transit_oriented": "mixed_use_transit_oriented_v1",
    "urban_mixed": "mixed_use_urban_mixed_v1",
}


def _profile(profile_id: str, unique_tile: dict, unique_row: dict) -> dict:
    return {
        "version": "v1",
        "profile_id": profile_id,
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
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            unique_tile,
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
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": [unique_tile["tile_id"]],
            },
            unique_row,
        ],
    }


DEALSHIELD_TILE_PROFILES = {
    "mixed_use_office_residential_v1": _profile(
        profile_id="mixed_use_office_residential_v1",
        unique_tile={
            "tile_id": "amenity_and_core_fitout_plus_12",
            "label": "Amenity/Core Fit-Out +12%",
            "metric_ref": "trade_breakdown.finishes",
            "required": False,
            "transform": {"op": "mul", "value": 1.12},
        },
        unique_row={
            "row_id": "office_leaseup_drag",
            "label": "Office Lease-Up Drag",
            "apply_tiles": ["revenue_minus_10"],
            "plus_tiles": ["amenity_and_core_fitout_plus_12"],
        },
    ),
    "mixed_use_retail_residential_v1": _profile(
        profile_id="mixed_use_retail_residential_v1",
        unique_tile={
            "tile_id": "retail_frontage_and_podium_plus_11",
            "label": "Retail Frontage + Podium +11%",
            "metric_ref": "trade_breakdown.structural",
            "required": False,
            "transform": {"op": "mul", "value": 1.11},
        },
        unique_row={
            "row_id": "tenant_turnover_pressure",
            "label": "Tenant Turnover Pressure",
            "apply_tiles": ["cost_plus_10"],
            "plus_tiles": ["retail_frontage_and_podium_plus_11"],
        },
    ),
    "mixed_use_hotel_retail_v1": _profile(
        profile_id="mixed_use_hotel_retail_v1",
        unique_tile={
            "tile_id": "guestrooms_and_fnb_fitout_plus_14",
            "label": "Guestrooms + F&B Fit-Out +14%",
            "metric_ref": "trade_breakdown.finishes",
            "required": False,
            "transform": {"op": "mul", "value": 1.14},
        },
        unique_row={
            "row_id": "seasonal_demand_shock",
            "label": "Seasonal Demand Shock",
            "apply_tiles": ["revenue_minus_10"],
            "plus_tiles": ["guestrooms_and_fnb_fitout_plus_14"],
        },
    ),
    "mixed_use_transit_oriented_v1": _profile(
        profile_id="mixed_use_transit_oriented_v1",
        unique_tile={
            "tile_id": "station_interface_and_circulation_plus_13",
            "label": "Station Interface + Circulation +13%",
            "metric_ref": "trade_breakdown.structural",
            "required": False,
            "transform": {"op": "mul", "value": 1.13},
        },
        unique_row={
            "row_id": "ridership_ramp_delay",
            "label": "Ridership Ramp Delay",
            "apply_tiles": ["revenue_minus_10"],
            "plus_tiles": ["station_interface_and_circulation_plus_13"],
        },
    ),
    "mixed_use_urban_mixed_v1": _profile(
        profile_id="mixed_use_urban_mixed_v1",
        unique_tile={
            "tile_id": "vertical_mobility_and_public_realm_plus_12",
            "label": "Vertical Mobility + Public Realm +12%",
            "metric_ref": "trade_breakdown.mechanical",
            "required": False,
            "transform": {"op": "mul", "value": 1.12},
        },
        unique_row={
            "row_id": "activation_program_slip",
            "label": "Activation Program Slip",
            "apply_tiles": ["cost_plus_10"],
            "plus_tiles": ["vertical_mobility_and_public_realm_plus_12"],
        },
    ),
}
