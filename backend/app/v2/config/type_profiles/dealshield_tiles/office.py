"""DealShield tile profiles for office subtypes."""

DEALSHIELD_TILE_DEFAULTS = {
    "class_a": "office_class_a_v1",
    "class_b": "office_class_b_v1",
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


DEALSHIELD_TILE_PROFILES = {
    "office_class_a_v1": {
        "version": "v1",
        "profile_id": "office_class_a_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "ti_lc_and_amenity_fitout_plus_11",
                "label": "TI/LC + Amenity Fit-Out +11%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
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
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["ti_lc_and_amenity_fitout_plus_11"],
            },
            {
                "row_id": "anchor_tenant_roll_delay",
                "label": "Anchor Tenant Roll Delay",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["ti_lc_and_amenity_fitout_plus_11"],
            },
        ],
        "provenance": {
            "notes": "Office Class A stress profile emphasizing TI/LC and premium fit-out carry risk."
        },
    },
    "office_class_b_v1": {
        "version": "v1",
        "profile_id": "office_class_b_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "renewal_downtime_and_refresh_plus_9",
                "label": "Renewal Downtime + Refresh +9%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
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
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["renewal_downtime_and_refresh_plus_9"],
            },
            {
                "row_id": "rolling_renewal_gap",
                "label": "Rolling Renewal Gap",
                "apply_tiles": ["revenue_minus_10"],
                "plus_tiles": ["renewal_downtime_and_refresh_plus_9"],
            },
        ],
        "provenance": {
            "notes": "Office Class B stress profile emphasizing renewal downtime and building refresh pressure."
        },
    },
}
