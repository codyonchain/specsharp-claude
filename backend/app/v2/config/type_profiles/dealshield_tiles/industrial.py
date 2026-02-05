"""DealShield tile profiles for industrial types."""

DEALSHIELD_TILE_DEFAULTS = {}

DEALSHIELD_TILE_PROFILES = {
    "industrial_warehouse_v1": {
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
                "tile_id": "structural_plus_10",
                "label": "Structural +10%",
                "metric_ref": "trade_breakdown.structural",
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
                "plus_tiles": ["structural_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial warehouse tile profile v1."},
    },
    "industrial_cold_storage_v1": {
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
                "tile_id": "equipment_plus_10",
                "label": "Equipment +10%",
                "metric_ref": "construction_costs.equipment_total",
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
                "plus_tiles": ["equipment_plus_10"],
            },
        ],
        "provenance": {"notes": "Industrial cold storage tile profile v1."},
    },
}
