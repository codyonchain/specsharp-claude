"""DealShield tile profiles for hospitality types."""

DEALSHIELD_TILE_DEFAULTS = {
    "limited_service_hotel": "hospitality_limited_service_hotel_v1",
    "full_service_hotel": "hospitality_full_service_hotel_v1",
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
    "hospitality_limited_service_hotel_v1": {
        "version": "v1",
        "profile_id": "hospitality_limited_service_hotel_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "guestroom_turnover_and_ffe_plus_10",
                "label": "Guestroom Turnover + FF&E +10%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.10},
            }
        ],
        "derived_rows": _base_rows(
            "guestroom_turnover_and_ffe_plus_10",
            "seasonal_ramp_pressure",
            "Seasonal Ramp Pressure",
        ),
        "provenance": {
            "notes": "Hospitality limited service hotel tile profile v1."
        },
    },
    "hospitality_full_service_hotel_v1": {
        "version": "v1",
        "profile_id": "hospitality_full_service_hotel_v1",
        "tiles": _base_tiles()
        + [
            {
                "tile_id": "ballroom_and_fnb_fitout_plus_12",
                "label": "Ballroom and F&B Fit-Out +12%",
                "metric_ref": "trade_breakdown.finishes",
                "required": False,
                "transform": {"op": "mul", "value": 1.12},
            }
        ],
        "derived_rows": _base_rows(
            "ballroom_and_fnb_fitout_plus_12",
            "banquet_program_delay",
            "Banquet Program Delay",
        ),
        "provenance": {
            "notes": "Hospitality full service hotel tile profile v1."
        },
    },
}
