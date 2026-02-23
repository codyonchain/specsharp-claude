"""DealShield tile profiles for industrial types."""

DEALSHIELD_TILE_DEFAULTS = {
    "warehouse": "industrial_warehouse_v1",
    "distribution_center": "industrial_distribution_center_v1",
    "manufacturing": "industrial_manufacturing_v1",
    "flex_space": "industrial_flex_space_v1",
    "cold_storage": "industrial_cold_storage_v1",
}


def _industrial_standard_tile_profile(subtype_label: str) -> dict:
    return {
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
        "provenance": {"notes": f"Industrial {subtype_label} tile profile v1."},
    }


def _industrial_cold_storage_tile_profile() -> dict:
    return {
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
    }


DEALSHIELD_TILE_PROFILES = {
    "industrial_warehouse_v1": _industrial_standard_tile_profile("warehouse"),
    "industrial_distribution_center_v1": _industrial_standard_tile_profile("distribution center"),
    "industrial_manufacturing_v1": _industrial_standard_tile_profile("manufacturing"),
    "industrial_flex_space_v1": _industrial_standard_tile_profile("flex space"),
    "industrial_cold_storage_v1": _industrial_cold_storage_tile_profile(),
}
