"""DealShield tile profiles for civic types."""


def _civic_tile_profile(subtype_label: str) -> dict:
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
                "label": "Revenue -10% (not modeled)",
                "metric_ref": "revenue_analysis.market_factor",
                "required": True,
                "transform": {"op": "mul", "value": 0.90},
            },
            {
                "tile_id": "mechanical_plus_10",
                "label": "MEP Complexity +10%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            },
            {
                "tile_id": "electrical_plus_10",
                "label": "Procurement/Power +10%",
                "metric_ref": "trade_breakdown.electrical",
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
                "row_id": "permitting_and_mep",
                "label": "Permitting + MEP Risk",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["mechanical_plus_10"],
            },
            {
                "row_id": "procurement_stress",
                "label": "Procurement Stress",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["electrical_plus_10"],
            },
        ],
        "provenance": {
            "notes": f"Civic {subtype_label} baseline tile profile v1 (feasibility defaults).",
        },
    }


DEALSHIELD_TILE_DEFAULTS = {
    "community_center": "civic_community_center_v1",
    "courthouse": "civic_courthouse_v1",
    "government_building": "civic_government_building_v1",
    "library": "civic_library_v1",
    "public_safety": "civic_public_safety_v1",
}

DEALSHIELD_TILE_PROFILES = {
    "civic_community_center_v1": _civic_tile_profile("community center"),
    "civic_courthouse_v1": _civic_tile_profile("courthouse"),
    "civic_government_building_v1": _civic_tile_profile("government building"),
    "civic_library_v1": _civic_tile_profile("library"),
    "civic_public_safety_v1": _civic_tile_profile("public safety"),
}
