"""DealShield content profiles for retail subtypes."""

DEALSHIELD_CONTENT_PROFILES = {
    "retail_shopping_center_v1": {
        "version": "v1",
        "profile_id": "retail_shopping_center_v1",
        "fastest_change": {
            "headline": "What would move the shopping-center decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Re-price hard-cost stack at +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Re-cut inline shop rent and occupancy downside -10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test inline fit-out carry and rollover rework",
                    "tile_id": "tenant_mix_and_cam_recovery_plus_11",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "tenant_mix_and_cam_recovery_plus_11",
                "text": "Inline-tenant turnover is modeled as smooth despite staggered lease expirations and delayed TI recapture.",
                "why": "Rollover bunching can stack downtime, white-box rework, and fit-out carry in one leasing cycle.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Base rent assumptions hold specialty-inline tenants flat even where local traffic is still stabilizing.",
                "why": "Small occupancy misses compound quickly when anchor draw and inline mix are tightly coupled.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Storefront, canopy, and site-lighting allowances are treated as fully bought out before late package addenda.",
                "why": "Allowance drift during tenant coordination can consume contingency before leasing is fully stabilized.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which shell/site packages remain allowance-based versus hard-bid and locked?",
                    "Where do utility and frontage upgrades still carry unresolved owner standards?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What signed lease paper supports current inline occupancy by bay type?",
                    "How does NOI move if inline absorption lags one seasonal leasing cycle?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "tenant_mix_and_cam_recovery_plus_11",
                "questions": [
                    "Which tenant-improvement scopes are still carried as owner hard-cost instead of lease pass-through?",
                    "What rework allowance is modeled when inline fit-out turnover runs long?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Anchor and inline turnover windows overlap in the same quarter without rent bridge assumptions.",
                "action": "Publish a lease-expiry ladder with downtime and TI carry tied to each rollover cohort.",
            },
            {
                "id": "rf_2",
                "flag": "Inline turnover carry is modeled as linear despite tenant-specific rework depth.",
                "action": "Recast white-box and frontage rework carry by tenant class with explicit downtime scenarios.",
            },
            {
                "id": "rf_3",
                "flag": "Tenant frontage scope is pooled in contingency without package-level ownership.",
                "action": "Split frontage and canopy scopes into priced alternates with release checkpoints.",
            },
        ],
    },
    "retail_big_box_v1": {
        "version": "v1",
        "profile_id": "retail_big_box_v1",
        "fastest_change": {
            "headline": "What would move the big-box decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Re-price hard-cost stack at +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Re-cut anchor sales productivity downside -10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test back-of-house power and refrigeration upgrades",
                    "tile_id": "back_of_house_power_and_refrigeration_plus_12",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "back_of_house_power_and_refrigeration_plus_12",
                "text": "Anchor-box conversion scope assumes existing electrical rooms and refrigeration feeds are reusable.",
                "why": "Legacy service capacity shortfalls typically surface late and force expensive rework windows.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Pro forma assumes post-conversion sales ramp with minimal cannibalization from nearby formats.",
                "why": "Ramp slippage in a single anchor tenant can reset center-wide traffic and revenue recovery timing.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Dock doors, mezzanine framing, and MEP reroutes are treated as standard despite tenant-specific logistics demands.",
                "why": "Back-of-house customization can push procurement and install costs beyond baseline carry assumptions.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which conversion packages are design-assist versus fully bid and contract-backed?",
                    "Where can utility-capacity upgrades still trigger downstream reroute scope?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What committed tenant ramp assumptions support year-one anchor productivity?",
                    "How does the model perform if anchor draw stabilizes one season later than planned?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "back_of_house_power_and_refrigeration_plus_12",
                "questions": [
                    "What field verification confirms existing switchgear and refrigeration headers are reusable?",
                    "Which long-lead power/refrigeration packages are still subject to redesign risk?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Conversion program assumes legacy electrical capacity without utility verification.",
                "action": "Issue a capacity validation memo with contingency triggers tied to feeder upgrade outcomes.",
            },
            {
                "id": "rf_2",
                "flag": "Anchor retenanting timeline is not reconciled to long-lead refrigeration and power equipment.",
                "action": "Publish a long-lead procurement schedule linked to rent commencement assumptions.",
            },
            {
                "id": "rf_3",
                "flag": "Loading and back-of-house sequencing is modeled without delivery-court constraints.",
                "action": "Run a logistics phasing plan that ties dock availability to conversion milestones.",
            },
        ],
    },
}
