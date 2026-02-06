"""DealShield content profiles for hospitality types."""

DEALSHIELD_CONTENT_PROFILES = {
    "hospitality_limited_service_hotel_v1": {
        "version": "v1",
        "profile_id": "hospitality_limited_service_hotel_v1",
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
                    "label": "Verify finishes and FF&E coordination risk",
                    "tile_id": "finishes_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Guestroom finish scope can shift close to procurement.",
                "why": "Finishes tile highlights this sensitivity channel.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What hard-cost inclusions are still basis assumptions?",
                    "Any site logistics or utility constraints still open?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What ADR and occupancy assumptions need third-party support?",
                    "Which market comps back the baseline revenue case?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish packages are design-complete today?",
                    "Any brand or operator standards pending confirmation?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Finish and brand standards are not fully reconciled.",
                "action": "Request signed design standards and finish delta log.",
            }
        ],
    }
}
