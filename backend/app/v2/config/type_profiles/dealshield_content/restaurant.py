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
                    "label": "Validate throughput revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify prototype finish lock and rollout risk",
                    "tile_id": "prototype_finish_rework_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "prototype_finish_rework_plus_10",
                "text": "Prototype standards are assumed frozen, but franchisor updates can reopen package costs.",
                "why": "Finish rework rapidly compounds across branded millwork and equipment interfaces.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Opening ramp assumes immediate lane utilization and stable ticket mix.",
                "why": "Early demand softness can create outsized NOI variance during debt stabilization.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Site utility capacity and tie-in lead times may still be under-scoped.",
                "why": "Late utility scope can move both cost and opening date in the same direction.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which civil and utility allowances are still based on concept-level takeoffs?",
                    "How much of MEP and storefront scope is covered by executable subcontractor quotes?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What empirical data supports opening-month throughput assumptions by daypart?",
                    "What labor plan protects service times if demand opens below plan?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "prototype_finish_rework_plus_10",
                "questions": [
                    "Which prototype details remain pending final franchisor sign-off?",
                    "Which finish alternates are pre-approved if supply chain substitutions are required?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Prototype finish package is still subject to brand revision.",
                "action": "Lock prototype bulletin log and align procurement release dates to approved revisions.",
            },
            {
                "id": "rf_2",
                "flag": "Drive-thru throughput assumptions are not tied to local comp data.",
                "action": "Request local launch performance bridge from comp stores to underwriting case.",
            },
            {
                "id": "rf_3",
                "flag": "Utility service activation windows are not contract-backed.",
                "action": "Obtain utility commitment letters and map timing slippage to opening-date impact.",
            },
        ],
    },
    "restaurant_full_service_v1": {
        "version": "v1",
        "profile_id": "restaurant_full_service_v1",
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
                    "label": "Validate demand/revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test service flow and fit-out complexity",
                    "tile_id": "service_labor_and_layout_plus_12",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "service_labor_and_layout_plus_12",
                "text": "Guest circulation and table-turn assumptions are treated as fixed before operations dry-runs.",
                "why": "Layout inefficiencies can require costly millwork and MEP rework post-buildout.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Revenue case assumes stable evening occupancy from opening quarter.",
                "why": "Sustained evening softness disproportionately impacts NOI in full-service models.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Kitchen line equipment integration is underwritten with limited commissioning contingency.",
                "why": "Commissioning drift can impact both opening date and construction carry.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which kitchen and bar scopes remain allowance-based versus fully bought out?",
                    "Are procurement lead times for long-lead equipment reflected in contingency planning?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How is weekday lunch and dinner capture supported by nearby demand comps?",
                    "What staffing and menu actions are pre-modeled for a soft first 90 days?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "service_labor_and_layout_plus_12",
                "questions": [
                    "Has the FOH/BOH flow been validated against actual service simulations?",
                    "Which layout dependencies could trigger late-stage electrical or plumbing rework?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Service flow assumptions are not validated by mock operations.",
                "action": "Run pre-opening flow simulation and issue a corrective layout punchlist before final finishes.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue plan lacks location-specific daypart sensitivity.",
                "action": "Recast underwriting with local lunch/dinner mix cases and staffing triggers.",
            },
            {
                "id": "rf_3",
                "flag": "Kitchen commissioning scope has thin contingency.",
                "action": "Add explicit commissioning float and contract milestone enforcement for critical systems.",
            },
        ],
    },
    "restaurant_fine_dining_v1": {
        "version": "v1",
        "profile_id": "restaurant_fine_dining_v1",
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
                    "label": "Validate premium pricing demand +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify curated systems and controls execution",
                    "tile_id": "curated_mep_and_controls_plus_12",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "curated_mep_and_controls_plus_12",
                "text": "Premium comfort and cellar controls are assumed to commission on baseline schedule.",
                "why": "Specialty controls integration creates high schedule and cost sensitivity late in delivery.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Premium check-size assumptions are treated as stable through launch months.",
                "why": "Fine-dining underwriting is highly exposed to early demand and mix shifts.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Custom millwork and imported finish allowances may not reflect current lead-time pricing.",
                "why": "Late design clarifications can trigger premium procurement premiums and float loss.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which bespoke finish packages have executable bids versus conceptual allowances?",
                    "How are long-lead imported materials buffered in contingency and schedule?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What local comp evidence supports check-size and seat-turn assumptions?",
                    "What mix-shift thresholds trigger a revised operating plan?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "curated_mep_and_controls_plus_12",
                "questions": [
                    "Which specialty HVAC/cellar interfaces still depend on unresolved vendor coordination?",
                    "Have commissioning responsibilities and acceptance criteria been contractually assigned?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Specialty controls commissioning path is not fully baselined.",
                "action": "Issue a controls integration matrix with owner-approved acceptance milestones.",
            },
            {
                "id": "rf_2",
                "flag": "Premium demand assumptions are not stress-tested to local market volatility.",
                "action": "Run downside demand scenarios tied to pricing strategy and reservation velocity.",
            },
            {
                "id": "rf_3",
                "flag": "Custom finish buyout is exposed to unresolved detailing.",
                "action": "Complete IFC-level detail package before final procurement release.",
            },
        ],
    },
    "restaurant_cafe_v1": {
        "version": "v1",
        "profile_id": "restaurant_cafe_v1",
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
                    "label": "Validate demand/revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify espresso line and equipment readiness",
                    "tile_id": "espresso_line_equipment_plus_8",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "espresso_line_equipment_plus_8",
                "text": "Core beverage equipment assumptions do not include full startup calibration and redundancy.",
                "why": "Downtime during opening weeks can rapidly erode small-format NOI assumptions.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Morning peak capture is treated as stable despite nearby competitor churn.",
                "why": "Cafes are highly sensitive to commuter and daypart behavior shifts.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Storefront and patio improvements may be under-scoped for local permitting requirements.",
                "why": "Small site upgrades can consume contingency quickly in compact footprints.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which shell and storefront allowances remain unsettled with landlord or jurisdictional review?",
                    "Are utility and grease requirements fully priced for local code interpretation?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What evidence supports expected transaction counts in first 12 weeks?",
                    "What contingency labor model exists if peak-hour conversion trails assumptions?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "espresso_line_equipment_plus_8",
                "questions": [
                    "Have espresso, grinder, and water-treatment vendors confirmed commissioning windows?",
                    "What backup plan exists for critical beverage equipment failure during launch?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Beverage equipment commissioning is not fully integrated into opening plan.",
                "action": "Publish commissioning runbook with vendor SLAs and backup equipment contingencies.",
            },
            {
                "id": "rf_2",
                "flag": "Morning demand assumptions are untested against location-specific comps.",
                "action": "Re-underwrite with conservative daypart capture bands and labor triggers.",
            },
            {
                "id": "rf_3",
                "flag": "Local patio/storefront code obligations remain partially unresolved.",
                "action": "Resolve permit comments and convert open allowances into committed scope.",
            },
        ],
    },
    "restaurant_bar_tavern_v1": {
        "version": "v1",
        "profile_id": "restaurant_bar_tavern_v1",
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
                    "label": "Validate nightlife revenue +/-10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Verify entertainment and life-safety package",
                    "tile_id": "entertainment_and_life_safety_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "entertainment_and_life_safety_plus_10",
                "text": "Entertainment and security system scope is assumed final before authority review.",
                "why": "Late AHJ or operator revisions can materially impact electrical and controls cost.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Evening/weekend demand is treated as stable despite event-driven volatility.",
                "why": "Revenue concentration in peak windows increases downside sensitivity.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Licensing-driven fit-out adjustments are not fully reflected in allowances.",
                "why": "Late compliance changes can trigger rework in bar, restroom, and egress scope.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which scope lines are contingent on final licensing or occupancy approvals?",
                    "How much contingency is reserved for late-stage egress or life-safety directives?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What event-calendar and local comp data support weekend underwriting assumptions?",
                    "What operational pivots are pre-modeled for sub-plan evening demand?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "entertainment_and_life_safety_plus_10",
                "questions": [
                    "Are A/V, security, and emergency systems integration requirements finalized with authorities?",
                    "Which entertainment package elements remain allowance-based versus procured?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Life-safety and entertainment integration assumptions remain open.",
                "action": "Run pre-final AHJ coordination and lock compliance-required alternates.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue concentration risk is not tied to volatility controls.",
                "action": "Add downside operating cases with labor/security flex thresholds.",
            },
            {
                "id": "rf_3",
                "flag": "Licensing-driven design changes may still impact fit-out scope.",
                "action": "Establish a licensing change-control log with quantified cost/schedule exposure.",
            },
        ],
    },
}
