"""DealShield tile profiles for parking types."""

DEALSHIELD_TILE_DEFAULTS = {
    "surface_parking": "parking_surface_parking_v1",
    "parking_garage": "parking_parking_garage_v1",
    "underground_parking": "parking_underground_parking_v1",
    "automated_parking": "parking_automated_parking_v1",
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
    "parking_surface_parking_v1": {
        "version": "v1",
        "profile_id": "parking_surface_parking_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "surface_lighting_and_drainage_rework_plus_8",
                "label": "Lighting and Drainage Rework +8%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.08},
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
                "plus_tiles": ["surface_lighting_and_drainage_rework_plus_8"],
            },
            {
                "row_id": "lot_turnover_and_restripe_delay",
                "label": "Lot Turnover and Restripe Delay",
                "apply_tiles": ["revenue_minus_10"],
                "plus_tiles": ["surface_lighting_and_drainage_rework_plus_8"],
            },
        ],
        "provenance": {
            "notes": "Surface parking stress profile focused on drainage corrections and turnover-related restriping carry."
        },
    },
    "parking_parking_garage_v1": {
        "version": "v1",
        "profile_id": "parking_parking_garage_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "garage_post_tension_and_coating_plus_11",
                "label": "Post-Tension and Coating Remediation +11%",
                "metric_ref": "trade_breakdown.structural",
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
                "plus_tiles": ["garage_post_tension_and_coating_plus_11"],
            },
            {
                "row_id": "garage_deck_repair_window_shift",
                "label": "Deck Repair Window Shift",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["garage_post_tension_and_coating_plus_11"],
            },
        ],
        "provenance": {
            "notes": "Garage stress profile emphasizing deck rehabilitation scope and post-tension repair volatility."
        },
    },
    "parking_underground_parking_v1": {
        "version": "v1",
        "profile_id": "parking_underground_parking_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "underground_dewatering_and_ventilation_plus_14",
                "label": "Dewatering and Ventilation Hardening +14%",
                "metric_ref": "trade_breakdown.mechanical",
                "required": False,
                "transform": {"op": "mul", "value": 1.14},
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
                "plus_tiles": ["underground_dewatering_and_ventilation_plus_14"],
            },
            {
                "row_id": "water_table_protection_resequence",
                "label": "Water Table Protection Resequence",
                "apply_tiles": ["cost_plus_10"],
                "plus_tiles": ["underground_dewatering_and_ventilation_plus_14"],
            },
        ],
        "provenance": {
            "notes": "Underground parking stress profile anchored to dewatering, ventilation, and water-table risk."
        },
    },
    "parking_automated_parking_v1": {
        "version": "v1",
        "profile_id": "parking_automated_parking_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "automated_controls_and_redundancy_plus_16",
                "label": "Controls and Redundancy Commissioning +16%",
                "metric_ref": "trade_breakdown.electrical",
                "required": False,
                "transform": {"op": "mul", "value": 1.16},
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
                "plus_tiles": ["automated_controls_and_redundancy_plus_16"],
            },
            {
                "row_id": "retrieval_system_commissioning_slip",
                "label": "Retrieval System Commissioning Slip",
                "apply_tiles": ["revenue_minus_10"],
                "plus_tiles": ["automated_controls_and_redundancy_plus_16"],
            },
        ],
        "provenance": {
            "notes": "Automated parking stress profile emphasizing control-system reliability and commissioning complexity."
        },
    },
}
