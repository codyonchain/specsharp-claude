"""DealShield tile profiles for multifamily types."""

DEALSHIELD_TILE_DEFAULTS = {
    "market_rate_apartments": "multifamily_market_rate_apartments_v1",
    "luxury_apartments": "multifamily_luxury_apartments_v1",
    "affordable_housing": "multifamily_affordable_housing_v1",
}


def _multifamily_tile_profile(subtype_label: str) -> dict:
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
        ],
        "provenance": {
            "notes": f"Multifamily {subtype_label} tile profile v1.",
        },
    }


DEALSHIELD_TILE_PROFILES = {
    "multifamily_market_rate_apartments_v1": _multifamily_tile_profile("market rate apartments"),
    "multifamily_luxury_apartments_v1": _multifamily_tile_profile("luxury apartments"),
    "multifamily_affordable_housing_v1": _multifamily_tile_profile("affordable housing"),
}
