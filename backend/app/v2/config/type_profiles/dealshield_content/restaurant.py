"""DealShield content profiles for restaurant types."""

DEALSHIELD_CONTENT_PROFILES = {
    "restaurant_quick_service_v1": {
        "version": "v1",
        "profile_id": "restaurant_quick_service_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify finishes and prototype compliance risk",
                    "tile_id": "finishes_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Prototype changes can push finish scope late in pricing.",
                "why": "Finishes tile is the explicit third sensitivity driver.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What hard-cost assumptions are still carried as allowances?",
                    "Any site utility or civil constraints not captured?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What sales ramp assumptions are most exposed?",
                    "Which demand comps support the baseline case?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish packages are fully specified vs placeholder?",
                    "Any brand-standard revisions pending approval?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Brand finish standards are not fully locked.",
                "action": "Request final finish schedule and approved alternates.",
            }
        ],
    }
}
