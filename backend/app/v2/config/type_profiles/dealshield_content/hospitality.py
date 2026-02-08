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
                "text": "Guestroom finish scope is exposed to late operator and brand comments before release.",
                "why": "Finishes sensitivity is explicit, and late changes can move both cost and opening date.",
            },
            {
                "id": "mlw_2",
                "text": "Revenue case assumes ADR and occupancy stabilize faster than market absorption may support.",
                "why": "Revenue downside is a core lever and should be stress-tested against slower ramp.",
            },
            {
                "id": "mlw_3",
                "text": "Procurement plan assumes no long-lead disruption across guestroom and public-area packages.",
                "why": "Cost pressure compounds when schedule slippage forces substitutions or acceleration.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which hard-cost inclusions are still basis assumptions rather than finalized bids?",
                    "Any site logistics or utility constraints still open that can impact total project cost?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What ADR and occupancy assumptions need third-party support before IC sign-off?",
                    "Which market comps back the baseline revenue case, and what has changed since that pull?",
                    "What operating plan supports debt coverage if stabilization arrives later than underwritten?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish packages are design-complete and released for buyout today?",
                    "Any brand or operator standards still pending confirmation or waiver?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Finish and brand standards are not fully reconciled.",
                "action": "Request signed design standards, finish delta log, and cost/schedule impact per open item.",
            },
            {
                "id": "rf_2",
                "flag": "Stabilization assumptions are optimistic relative to recent submarket performance.",
                "action": "Ask for downside operating case with ADR and occupancy drag and confirm covenant headroom.",
            },
            {
                "id": "rf_3",
                "flag": "Long-lead procurement status lacks clear contingency paths.",
                "action": "Require long-lead tracker with approved alternates and owner decision dates.",
            },
        ],
    }
}
