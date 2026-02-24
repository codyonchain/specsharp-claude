"""DealShield tile profiles for retail subtypes."""

DEALSHIELD_TILE_DEFAULTS = {
    "shopping_center": "retail_shopping_center_v1",
    "big_box": "retail_big_box_v1",
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
    "retail_shopping_center_v1": {
        "version": "v1",
        "profile_id": "retail_shopping_center_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "tenant_mix_and_cam_recovery_plus_11",
                "label": "Tenant Mix + CAM Recovery +11%",
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
                "plus_tiles": ["tenant_mix_and_cam_recovery_plus_11"],
            },
            {
                "row_id": "inline_suite_rollover_drag",
                "label": "Inline Suite Rollover Drag",
                "apply_tiles": ["revenue_minus_10"],
                "plus_tiles": ["tenant_mix_and_cam_recovery_plus_11"],
            },
        ],
        "provenance": {
            "notes": "Shopping-center stress profile emphasizing inline-tenant churn and CAM recovery slippage."
        },
    },
    "retail_big_box_v1": {
        "version": "v1",
        "profile_id": "retail_big_box_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "back_of_house_power_and_refrigeration_plus_12",
                "label": "Back-of-House Power + Refrigeration +12%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
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
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["back_of_house_power_and_refrigeration_plus_12"],
            },
            {
                "row_id": "anchor_box_retenanting_slip",
                "label": "Anchor Box Retenanting Slip",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["back_of_house_power_and_refrigeration_plus_12"],
            },
        ],
        "provenance": {
            "notes": "Big-box stress profile emphasizing anchor-box conversion carry and electrical capacity upgrades."
        },
    },
}
