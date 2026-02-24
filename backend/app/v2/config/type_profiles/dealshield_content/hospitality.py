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
                    "label": "Validate occupancy-led revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify guestroom turnover and FF&E risk",
                    "tile_id": "guestroom_turnover_and_ffe_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "guestroom_turnover_and_ffe_plus_10",
                "text": "Guestroom turnover sequencing is assumed stable before brand punchlist closure.",
                "why": "Late FF&E changes can force room-out-of-service periods and accelerated procurement.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Ramp assumptions treat weekday occupancy stabilization as immediate.",
                "why": "Select-service NOI is highly sensitive to early occupancy variance.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Utility and life-safety allowances are treated as fully defined pre-buyout.",
                "why": "Allowance drift late in preconstruction can compress opening float and contingency.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which MEP and utility line items are still allowance-driven instead of bid-backed?",
                    "What scope assumptions remain open across fire-life-safety approvals?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What market evidence supports opening-quarter occupancy assumptions?",
                    "What operating plan protects coverage if stabilization occurs one quarter late?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "guestroom_turnover_and_ffe_plus_10",
                "questions": [
                    "Which FF&E packages are fully released versus still in review?",
                    "Which guestroom mockup comments can still drive material substitutions?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Guestroom turnover milestones are not tied to approved FF&E release dates.",
                "action": "Issue a room-turn turnover tracker with procurement gates and escalation thresholds.",
            },
            {
                "id": "rf_2",
                "flag": "Opening occupancy assumptions exceed recent comp-set ramp trends.",
                "action": "Run downside occupancy bridge and confirm covenant headroom through stabilization.",
            },
            {
                "id": "rf_3",
                "flag": "Allowance-backed line items remain unresolved heading into buyout.",
                "action": "Require bid-tab variance log with cost and opening-date impact by trade.",
            },
        ],
    },
    "hospitality_full_service_hotel_v1": {
        "version": "v1",
        "profile_id": "hospitality_full_service_hotel_v1",
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
                    "label": "Validate banquet and ADR revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test ballroom and F&B fit-out scope",
                    "tile_id": "ballroom_and_fnb_fitout_plus_12",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "ballroom_and_fnb_fitout_plus_12",
                "text": "Ballroom, prefunction, and F&B fit-out details are assumed frozen ahead of operator sign-off.",
                "why": "Late fit-out refinements create compounding finishes, MEP, and commissioning pressure.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Banquet and group mix is treated as stable in the first operating year.",
                "why": "Full-service underwriting is exposed to event-program timing and ADR volatility.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Central plant and life-safety integration is underwritten with minimal commissioning drift.",
                "why": "System integration slippage increases both carry and pre-opening burn.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which long-lead MEP and power packages are fully bought out today?",
                    "How much contingency is explicitly allocated to system integration and turnover risk?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What signed group pipeline supports banquet and meeting revenue assumptions?",
                    "What downside ADR/occupancy case has been underwritten for year-one operations?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "ballroom_and_fnb_fitout_plus_12",
                "questions": [
                    "Which ballroom and F&B finish packages remain pending operator approval?",
                    "What alternates are pre-approved if specialty finishes slip procurement windows?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Operator-driven fit-out scope remains open late in design development.",
                "action": "Lock final ballroom/F&B scope bulletin and map each open item to cost and schedule risk.",
            },
            {
                "id": "rf_2",
                "flag": "Group business ramp assumptions are not backed by contracted demand.",
                "action": "Require contracted pipeline schedule and downside sensitivity for ADR and occupancy.",
            },
            {
                "id": "rf_3",
                "flag": "Commissioning sequence lacks explicit contingency and accountability milestones.",
                "action": "Publish integrated commissioning plan with owner sign-off gates and fallback pathways.",
            },
        ],
    },
}
