"""DealShield content profiles for industrial types."""

DEALSHIELD_CONTENT_PROFILES = {
    "industrial_warehouse_v1": {
        "version": "v1",
        "profile_id": "industrial_warehouse_v1",
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
                    "label": "Verify structural and envelope risk",
                    "tile_id": "structural_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Scope gaps and site constraints can move hard costs fast.",
                "why": "Cost and structural driver tiles show first-order sensitivity.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What is in or out of hard costs for this estimate?",
                    "What sitework and utility assumptions remain open?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which lease-up assumptions are committed vs placeholder?",
                    "What demand comps support this revenue run-rate?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "structural_plus_10",
                "questions": [
                    "Any long-span framing or slab scope not fully priced?",
                    "Any geotech risk that could force foundation changes?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Geotech and civil basis is not locked.",
                "action": "Request geotech summary and sitework allowance breakout.",
            }
        ],
    },
    "industrial_cold_storage_v1": {
        "version": "v1",
        "profile_id": "industrial_cold_storage_v1",
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
                    "label": "Verify refrigeration and equipment risk",
                    "tile_id": "equipment_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Equipment scope and utility requirements often arrive late.",
                "why": "Equipment driver tile is a direct sensitivity lever.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What is in or out of hard costs for this estimate?",
                    "Any contingency carry for site and utility unknowns?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What contract terms support the revenue assumption?",
                    "What lease-up delay risk is not in base case?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "equipment_plus_10",
                "questions": [
                    "Which refrigeration package items are vendor quoted?",
                    "Any electrical service upgrades still assumed?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Equipment package basis is not contract-backed.",
                "action": "Request vendor quotes with inclusions and utility loads.",
            }
        ],
    },
}
