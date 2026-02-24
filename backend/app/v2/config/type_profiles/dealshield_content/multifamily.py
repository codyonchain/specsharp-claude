"""DealShield content profiles for multifamily types."""


DEALSHIELD_CONTENT_PROFILES = {
    "multifamily_market_rate_apartments_v1": {
        "version": "v1",
        "profile_id": "multifamily_market_rate_apartments_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm hard costs +/-10% against current bids",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_cost_per_sf",
                    "label": "Validate cost per SF +/-10% at current plan set",
                    "tile_id": "cost_per_sf_plus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify interior finish escalation risk",
                    "tile_id": "finishes_plus_10",
                },
                {
                    "id": "driver_structural_proxy",
                    "label": "Stress structural base carry proxy exposure",
                    "tile_id": "structural_carry_proxy_plus_5",
                },
            ],
        },
        "decision_insurance": {
            "severity_thresholds_pct": {
                "high": 10.0,
                "med": 4.0,
            },
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Core structure and site package assumptions can drift when detailing and utility interfaces mature.",
                "why": "Structural base scope movement is a direct proxy for early carry pressure in this profile.",
                "driver_tile_id": "structural_carry_proxy_plus_5",
            },
            {
                "id": "mlw_2",
                "text": "Parking, utility, and corridor width assumptions can shift hard costs late in DD/CD.",
                "why": "Core shell and circulation updates tend to move all-in project cost quickly.",
                "driver_tile_id": "cost_per_sf_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Finish alternates may not be pre-approved when procurement volatility appears.",
                "why": "Without pre-validated alternates, finish volatility compounds downside quickly.",
                "driver_tile_id": "finishes_plus_10",
            },
            {
                "id": "mlw_4",
                "text": "Allowances may still include unresolved site and utility tie-in risk.",
                "why": "Unresolved scope allowances are a frequent source of conservative-case misses.",
                "driver_tile_id": "cost_plus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which hard-cost assumptions are still allowances versus executable bids?",
                    "What unresolved utility and civil dependencies can still move GMP scope?",
                ],
            },
             {
                "id": "qb_cost_2",
                "driver_tile_id": "cost_per_sf_plus_10",
                "questions": [
                    "Which planning assumptions would move the current cost per SF baseline by +/-10%?",
                    "Which design options are still open that could shift gross-to-net efficiency?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "finishes_plus_10",
                "questions": [
                    "Which finish packages are released for procurement versus still schematic?",
                    "Which finish alternates are already approved for value engineering?",
                ],
            },
            {
                "id": "qb_struct_proxy_1",
                "driver_tile_id": "structural_carry_proxy_plus_5",
                "questions": [
                    "Which structural and site assumptions remain provisional versus fully coordinated?",
                    "Which scope triggers would require immediate rebasing of structural carry proxy risk?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Structural and site baseline assumptions are not fully validated against coordinated packages.",
                "action": "Reconcile structural/site assumptions with latest package coordination before IC.",
            },
            {
                "id": "rf_2",
                "flag": "Cost baseline still carries unresolved scope and allowance risk.",
                "action": "Publish inclusions/exclusions with owner and due date for each open scope decision.",
            },
            {
                "id": "rf_3",
                "flag": "Finish package risk lacks a documented fallback plan.",
                "action": "Lock finish alternates and procurement timing before final approval.",
            },
        ],
    },
    "multifamily_luxury_apartments_v1": {
        "version": "v1",
        "profile_id": "multifamily_luxury_apartments_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm core hard-cost movement",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_cost_per_sf",
                    "label": "Validate high-spec cost per SF tolerance",
                    "tile_id": "cost_per_sf_plus_10",
                },
                {
                    "id": "driver_finishes",
                    "label": "Validate premium amenity finish exposure",
                    "tile_id": "amenity_finish_plus_15",
                },
                {
                    "id": "driver_amenity_mep",
                    "label": "Stress amenity-system MEP exposure",
                    "tile_id": "amenity_mep_plus_10",
                },
            ],
        },
        "decision_insurance": {
            "severity_thresholds_pct": {
                "high": 9.0,
                "med": 3.5,
            },
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Amenity and premium finish scopes can drift after model-unit direction changes.",
                "why": "Luxury projects are highly sensitive to late interior spec decisions.",
                "driver_tile_id": "amenity_finish_plus_15",
            },
            {
                "id": "mlw_2",
                "text": "Amenity-system MEP scope can expand when controls and operating requirements are finalized.",
                "why": "Luxury projects can absorb hidden MEP scope late when amenity operations are refined.",
                "driver_tile_id": "amenity_mep_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Concierge, amenity MEP, and vertical transport scope can move total cost quickly.",
                "why": "Specialized systems in luxury towers increase hard-cost volatility.",
                "driver_tile_id": "cost_plus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which high-spec scopes are still provisional or owner-directed allowances?",
                    "What procurement packages remain exposed to long-lead repricing risk?",
                ],
            },
            {
                "id": "qb_cost_2",
                "driver_tile_id": "amenity_finish_plus_15",
                "questions": [
                    "Which amenity finishes and FF&E packages are unpriced or late-binding?",
                    "Which alternates are pre-approved if amenity package pricing exceeds target?",
                ],
            },
            {
                "id": "qb_mep_1",
                "driver_tile_id": "amenity_mep_plus_10",
                "questions": [
                    "Which amenity MEP scopes are still assumptions versus coordinated design outputs?",
                    "What contingency is allocated for late MEP upgrades during systems readiness?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Amenity and premium finish packages are not frozen before final pricing.",
                "action": "Freeze amenity scope gates and issue alternate package decisions before commitment.",
            },
            {
                "id": "rf_2",
                "flag": "Amenity MEP scope assumptions rely on outdated coordination inputs.",
                "action": "Refresh amenity MEP assumptions with current coordination set and rerun downside.",
            },
            {
                "id": "rf_3",
                "flag": "Long-lead procurement risk has no contingency-backed mitigation path.",
                "action": "Establish long-lead risk register with costed fallback options.",
            },
        ],
    },
    "multifamily_affordable_housing_v1": {
        "version": "v1",
        "profile_id": "multifamily_affordable_housing_v1",
        "fastest_change": {
            "headline": "What would change this decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Confirm base hard-cost assumptions",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_cost_per_sf",
                    "label": "Validate program cost-per-SF limits",
                    "tile_id": "cost_per_sf_plus_10",
                },
                {
                    "id": "driver_soft_cost",
                    "label": "Verify entitlement/compliance electrical scope exposure",
                    "tile_id": "compliance_electrical_plus_8",
                },
                {
                    "id": "driver_plumbing_scope",
                    "label": "Stress compliance-driven plumbing scope",
                    "tile_id": "compliance_plumbing_plus_6",
                },
            ],
        },
        "decision_insurance": {
            "severity_thresholds_pct": {
                "high": 8.0,
                "med": 3.0,
            },
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Compliance and agency revisions can increase electrical scope and control package requirements.",
                "why": "Affordable projects are sensitive to late code and compliance system adjustments.",
                "driver_tile_id": "compliance_electrical_plus_8",
            },
            {
                "id": "mlw_2",
                "text": "Compliance and accessibility refinements can increase plumbing scope late in design.",
                "why": "Late compliance revisions often surface plumbing and utility scope deltas.",
                "driver_tile_id": "compliance_plumbing_plus_6",
            },
            {
                "id": "mlw_3",
                "text": "Design-compliance revisions can force late hard-cost rebalancing.",
                "why": "Late scope changes often push conservative scenarios into funding gaps.",
                "driver_tile_id": "cost_plus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which hard-cost assumptions remain unresolved pending agency approvals?",
                    "What fallback scopes are available if program cap limits are exceeded?",
                ],
            },
            {
                "id": "qb_soft_1",
                "driver_tile_id": "compliance_electrical_plus_8",
                "questions": [
                    "Which compliance milestones could still expand electrical and life-safety scope?",
                    "What alternates are available if compliance-related electrical scope increases?",
                ],
            },
            {
                "id": "qb_rev_1",
                "driver_tile_id": "compliance_plumbing_plus_6",
                "questions": [
                    "Which compliance requirements could still drive plumbing scope adjustments?",
                    "What fallback scope options exist if compliance plumbing costs increase late?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Program compliance risk is not mapped to cost and schedule contingencies.",
                "action": "Map each compliance dependency to owner, deadline, and contingency response.",
            },
            {
                "id": "rf_2",
                "flag": "Electrical and plumbing compliance assumptions do not reflect likely late coordination changes.",
                "action": "Update compliance-system assumptions and rerun downside construction stress scenarios.",
            },
            {
                "id": "rf_3",
                "flag": "Program scope controls are not tied to pre-approved compliance fallback options.",
                "action": "Document fallback compliance scopes and validate cost impact before approval.",
            },
        ],
    },
}
