"""DealShield tile profiles for restaurant types."""

DEALSHIELD_TILE_DEFAULTS = {}

DEALSHIELD_TILE_PROFILES = {
    "restaurant_quick_service_v1": {
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
                "tile_id": "revenue_minus_10",
                "label": "Revenue -10%",
                "metric_ref": "revenue_analysis.annual_revenue",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "finishes_plus_10",
                "label": "Finishes +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
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
                "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
                "plus_tiles": ["finishes_plus_10"],
            },
        ],
        "provenance": {"notes": "Restaurant quick service tile profile v1."},
    }
}
