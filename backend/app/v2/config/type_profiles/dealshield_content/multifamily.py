"""DealShield content profiles for multifamily types."""


def _multifamily_content_profile(profile_id: str, subtype_label: str) -> dict:
    return {
        "version": "v1",
        "profile_id": profile_id,
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_cost_per_sf",
                    "label": "Validate cost per SF +/-10%",
                    "tile_id": "cost_per_sf_plus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify interior finish escalation risk",
                    "tile_id": "finishes_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": f"{subtype_label.title()} unit mix and efficiency assumptions may be miscalibrated.",
                "why": "Cost-per-SF sensitivity is a primary decision lever in this profile.",
            },
            {
                "id": "mlw_2",
                "text": "Final construction scope can shift late due to code, utility, and design coordination.",
                "why": "Base cost assumptions are highly sensitive to late scope movement.",
            },
            {
                "id": "mlw_3",
                "text": "Interior finish package selections are often not fully locked before procurement.",
                "why": "Finish volatility can stack on top of broad cost stress in the ugly case.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which hard-cost assumptions are still allowances versus quoted packages?",
                    "What site/civil and utility unknowns are still unresolved in the base case?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "cost_per_sf_plus_10",
                "questions": [
                    "Which unit mix and gross-to-net assumptions drive the current cost per SF baseline?",
                    "What alternate planning assumptions would move cost per SF by +/-10%?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish selections are design-complete and released for pricing?",
                    "What value-engineering alternates are approved if finish costs escalate?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Revenue assumptions are not tied to recent market evidence.",
                "action": "Update rent and occupancy comps and rerun downside coverage.",
            },
            {
                "id": "rf_2",
                "flag": "Cost baseline still carries unresolved scope and allowance risk.",
                "action": "Publish inclusions/exclusions with owner of each open scope decision.",
            },
            {
                "id": "rf_3",
                "flag": "Finish package risk lacks a documented fallback plan.",
                "action": "Lock alternates and procurement timing before investment approval.",
            },
        ],
    }


DEALSHIELD_CONTENT_PROFILES = {
    "multifamily_market_rate_apartments_v1": _multifamily_content_profile(
        "multifamily_market_rate_apartments_v1",
        "market rate apartments",
    ),
    "multifamily_luxury_apartments_v1": _multifamily_content_profile(
        "multifamily_luxury_apartments_v1",
        "luxury apartments",
    ),
    "multifamily_affordable_housing_v1": _multifamily_content_profile(
        "multifamily_affordable_housing_v1",
        "affordable housing",
    ),
}
