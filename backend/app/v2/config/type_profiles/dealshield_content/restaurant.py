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
                "text": "Prototype alignment is assumed complete, but brand revisions can still re-open finish scope.",
                "why": "Finishes pressure is explicit in the ugly case and can reset procurement quickly.",
            },
            {
                "id": "mlw_2",
                "text": "Revenue ramp assumes immediate throughput before local demand patterns are proven.",
                "why": "Revenue downside is a core decision lever; opening-month softness matters.",
            },
            {
                "id": "mlw_3",
                "text": "Utility and service-capacity assumptions are carried as baseline rather than committed.",
                "why": "Cost exposure rises fast when late utility upgrades move from assumption to requirement.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which hard-cost assumptions are still carried as allowances rather than subcontractor quotes?",
                    "Any site utility or civil constraints not yet priced into the base case?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What opening-quarter sales ramp assumptions are most exposed to local demand variance?",
                    "Which demand comps support the baseline case and how recent are they?",
                    "What labor plan protects margin if throughput starts below plan?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish packages are fully specified versus still design-intent only?",
                    "Any brand-standard revisions pending approval or value-engineering decisions?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Brand finish standards are not fully locked.",
                "action": "Request final finish schedule, approved alternates, and buyout timing against schedule.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue case is not tied to site-specific opening performance data.",
                "action": "Require a site-level launch bridge from comp performance to underwritten volume.",
            },
            {
                "id": "rf_3",
                "flag": "Utility readiness dates are not contract-backed.",
                "action": "Confirm utility commitments in writing and map late dates to opening delay impact.",
            },
        ],
    }
}
