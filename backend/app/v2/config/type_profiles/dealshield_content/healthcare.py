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
                "text": "Mechanical scope is priced at schematic density while clinical equipment planning is still moving.",
                "why": "Mechanical pressure is a direct lever; unresolved loads can reprice the job late.",
            },
            {
                "id": "mlw_2",
                "text": "Revenue assumptions rely on absorption pace without signed tenant depth.",
                "why": "Revenue downside is explicitly modeled; tenancy quality matters as much as occupancy speed.",
            },
            {
                "id": "mlw_3",
                "text": "Hard-cost carry underweights owner-side scope migration into GC packages.",
                "why": "Cost sensitivity can hide scope transfer risk unless inclusions are locked.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What is included in hard costs versus owner-provided clinical scope, in writing?",
                    "Any utility upgrade assumptions still unverified with the serving authority?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "Which tenancy assumptions drive the revenue case and what is contract-backed today?",
                    "What lease-up sensitivity is most exposed if anchor tenancy starts late?",
                    "Which payer-mix assumptions could compress effective rate first?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "mechanical_plus_10",
                "questions": [
                    "Which HVAC capacity assumptions are still schematic and awaiting final load confirmation?",
                    "Any med-gas, filtration, or specialty ventilation scope still pending design freeze?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "MEP basis has unresolved equipment dependencies.",
                "action": "Request updated MEP narrative tied to the current equipment schedule and load calcs.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue case depends on unsigned specialty tenancy.",
                "action": "Get tenant status by suite and reconcile modeled rents to current deal terms.",
            },
            {
                "id": "rf_3",
                "flag": "Owner-furnished versus contractor-furnished boundaries remain ambiguous.",
                "action": "Force a single responsibility matrix before GMP lock to avoid scope migration claims.",
            },
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
                "text": "Final clinical flow can still shift MEP distribution and room-level fit-out density.",
                "why": "Mechanical sensitivity is explicit, so late planning changes can move total exposure quickly.",
            },
            {
                "id": "mlw_2",
                "text": "Patient-volume ramp is underwritten as steady even though launch curves are uneven.",
                "why": "Revenue downside lever will be hit early if the first operating quarters miss.",
            },
            {
                "id": "mlw_3",
                "text": "Hard-cost model assumes limited rework from infection-control comments.",
                "why": "Cost sensitivity and mechanical sensitivity can stack if compliance changes arrive late.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What hard-cost inclusions are still assumption-based rather than quote-backed?",
                    "Any site or utility items excluded from contractor scope that still hit total project cost?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What patient-volume assumptions support this revenue case, by month for year one?",
                    "What payer-mix risk is not reflected in baseline operations?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "mechanical_plus_10",
                "questions": [
                    "Any late diagnostic equipment adding HVAC or electrical load?",
                    "Which infection-control requirements remain open with authorities or operator standards?",
                    "What is the fallback scope if MEP submittal turnaround slips?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Clinical planning inputs are not fully frozen.",
                "action": "Request updated room data sheets and the MEP impact log tied to each pending decision.",
            },
            {
                "id": "rf_2",
                "flag": "Opening-quarter revenue assumptions are not stress-tested against slower ramp.",
                "action": "Run a slower-launch operating case and confirm DSCR resilience before approval.",
            },
            {
                "id": "rf_3",
                "flag": "Permit comments may force late compliance changes in critical spaces.",
                "action": "Track unresolved compliance comments weekly with explicit cost and schedule owners.",
            },
        ],
    },
}
