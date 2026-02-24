"""DealShield tile profiles for restaurant types."""

DEALSHIELD_TILE_DEFAULTS = {
    "quick_service": "restaurant_quick_service_v1",
    "full_service": "restaurant_full_service_v1",
    "fine_dining": "restaurant_fine_dining_v1",
    "cafe": "restaurant_cafe_v1",
    "bar_tavern": "restaurant_bar_tavern_v1",
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


def _base_rows(extra_tile_id: str, extra_row_id: str, extra_row_label: str) -> list[dict]:
    return [
        {
            "row_id": "conservative",
            "label": "Conservative",
            "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
        },
        {
            "row_id": "ugly",
            "label": "Ugly",
            "apply_tiles": ["cost_plus_10", "revenue_minus_10"],
            "plus_tiles": [extra_tile_id],
        },
        {
            "row_id": extra_row_id,
            "label": extra_row_label,
            "apply_tiles": ["cost_plus_10"],
            "plus_tiles": [extra_tile_id],
        },
    ]


DEALSHIELD_TILE_PROFILES = {
    "restaurant_quick_service_v1": {
        "version": "v1",
        "profile_id": "restaurant_quick_service_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "prototype_finish_rework_plus_10",
                "label": "Prototype Finish Rework +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "prototype_finish_rework_plus_10",
            "prototype_rework",
            "Prototype Rework",
        ),
        "provenance": {"notes": "Restaurant quick service tile profile v1."},
    },
    "restaurant_full_service_v1": {
        "version": "v1",
        "profile_id": "restaurant_full_service_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "service_labor_and_layout_plus_12",
                "label": "Service Labor + Layout +12%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.12},
            }
        ],
        "derived_rows": _base_rows(
            "service_labor_and_layout_plus_12",
            "service_flow_disruption",
            "Service Flow Disruption",
        ),
        "provenance": {"notes": "Restaurant full service tile profile v1."},
    },
    "restaurant_fine_dining_v1": {
        "version": "v1",
        "profile_id": "restaurant_fine_dining_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "curated_mep_and_controls_plus_12",
                "label": "Curated MEP + Controls +12%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.12},
            }
        ],
        "derived_rows": _base_rows(
            "curated_mep_and_controls_plus_12",
            "chef_table_commissioning_drag",
            "Chef Table Commissioning Drag",
        ),
        "provenance": {"notes": "Restaurant fine dining tile profile v1."},
    },
    "restaurant_cafe_v1": {
        "version": "v1",
        "profile_id": "restaurant_cafe_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "espresso_line_equipment_plus_8",
                "label": "Espresso Line Equipment +8%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.08},
            }
        ],
        "derived_rows": _base_rows(
            "espresso_line_equipment_plus_8",
            "morning_peak_shortfall",
            "Morning Peak Shortfall",
        ),
        "provenance": {"notes": "Restaurant cafe tile profile v1."},
    },
    "restaurant_bar_tavern_v1": {
        "version": "v1",
        "profile_id": "restaurant_bar_tavern_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "entertainment_and_life_safety_plus_10",
                "label": "Entertainment + Life-Safety +10%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "entertainment_and_life_safety_plus_10",
            "late_night_compliance_push",
            "Late-Night Compliance Push",
        ),
        "provenance": {"notes": "Restaurant bar/tavern tile profile v1."},
    },
}
