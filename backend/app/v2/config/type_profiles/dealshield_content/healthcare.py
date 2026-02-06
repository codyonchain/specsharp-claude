"""DealShield content profiles for healthcare types."""

DEALSHIELD_CONTENT_PROFILES = {
    "healthcare_medical_office_building_v1": {
        "version": "v1",
        "profile_id": "healthcare_medical_office_building_v1",
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
                    "label": "Verify MEP and fit-out risk",
                    "tile_id": "mechanical_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Mechanical scope can move after equipment planning tightens.",
                "why": "Mechanical tile captures a major sensitivity path.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What is included in hard costs vs owner-provided scope?",
                    "Any utility upgrade assumptions still unverified?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which tenancy assumptions drive the revenue case?",
                    "What lease-up sensitivity is most exposed today?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "mechanical_plus_10",
                "questions": [
                    "What HVAC capacity assumptions are still schematic?",
                    "Any med-gas or specialty ventilation scope pending?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "MEP basis has unresolved equipment dependencies.",
                "action": "Request updated MEP narrative tied to equipment list.",
            }
        ],
    },
    "healthcare_urgent_care_v1": {
        "version": "v1",
        "profile_id": "healthcare_urgent_care_v1",
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
                    "label": "Verify mechanical and clinical support scope",
                    "tile_id": "mechanical_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Final clinical flow can shift MEP and fit-out scope.",
                "why": "Mechanical sensitivity is explicit in the tile profile.",
            }
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What hard-cost inclusions are still assumption-based?",
                    "Any site or utility items excluded from contractor scope?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What patient-volume assumptions support this revenue case?",
                    "What payer-mix risk is not reflected in baseline?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "mechanical_plus_10",
                "questions": [
                    "Any late diagnostic equipment adding HVAC load?",
                    "What infection-control requirements remain open?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Clinical planning inputs are not fully frozen.",
                "action": "Request updated room data sheets and MEP impact log.",
            }
        ],
    },
}
