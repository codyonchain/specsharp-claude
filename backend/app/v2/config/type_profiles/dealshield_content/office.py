"""DealShield content profiles for office subtypes."""

DEALSHIELD_CONTENT_PROFILES = {
    "office_class_a_v1": {
        "version": "v1",
        "profile_id": "office_class_a_v1",
        "fastest_change": {
            "headline": "What would move the Class A decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Validate hard-cost basis +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Re-cut Class A rent/absorption downside -10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test TI/LC and amenity fit-out carry",
                    "tile_id": "ti_lc_and_amenity_fitout_plus_11",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "ti_lc_and_amenity_fitout_plus_11",
                "text": "Anchor-floor TI and amenity scope are assumed frozen before leasing concessions are finalized.",
                "why": "Late TI revisions stack with lease-up incentives and quickly erode Class A carry tolerance.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Underwriting assumes premium absorption velocity without a staged rent bridge by suite mix.",
                "why": "Even short lease-up slippage can materially shift DSCR in high-service office programs.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "MEP procurement and façade allowances are treated as fully bought-out earlier than bid reality.",
                "why": "Allowance drift at close-out timing compresses both contingency and stabilization runway.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which Class A envelope and MEP packages are still allowance-backed versus hard-bid?",
                    "What unresolved owner standards can still change bid scope before GMP lock?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What executed tenant paper supports rent assumptions by floor and unit mix?",
                    "What downside lease-up cadence was approved if anchor occupancy slips one quarter?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "ti_lc_and_amenity_fitout_plus_11",
                "questions": [
                    "Which TI standards are contract-locked versus still in landlord option packages?",
                    "Where do concession assumptions overlap with fit-out timing risk in the base case?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Anchor tenant TI package remains open while pricing is treated as fixed.",
                "action": "Issue a TI decision log with approval deadlines and dollarized change windows.",
            },
            {
                "id": "rf_2",
                "flag": "Premium absorption assumptions are not reconciled to executed lease milestones.",
                "action": "Publish a signed-lease bridge from underwritten rents to contracted occupancy dates.",
            },
            {
                "id": "rf_3",
                "flag": "Fit-out sequencing risk is carried in narrative but not mapped to carry costs.",
                "action": "Tie fit-out milestone delays to explicit carry and DSCR sensitivity checkpoints.",
            },
        ],
    },
    "office_class_b_v1": {
        "version": "v1",
        "profile_id": "office_class_b_v1",
        "fastest_change": {
            "headline": "What would move the Class B decision fastest?",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Validate hard-cost basis +/-10%",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Re-cut renewal and rollover revenue downside -10%",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_trade",
                    "label": "Pressure-test renewal downtime and base-building refresh",
                    "tile_id": "renewal_downtime_and_refresh_plus_9",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "renewal_downtime_and_refresh_plus_9",
                "text": "Rollover downtime assumptions understate churn from staggered renewal windows and floor refresh overlap.",
                "why": "Class B tenancy turnover can compound downtime when refresh sequencing is modeled too optimistically.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Rent-roll resiliency is assumed without a fallback plan for mid-term tenant step-downs.",
                "why": "Moderate rent resets can pull NOI below target while vacancy is still clearing.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Deferred-maintenance scope is partially embedded in soft contingencies instead of explicit hard-cost lines.",
                "why": "Hidden refresh scope can surface late and absorb covenant headroom quickly.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which deferred-maintenance packages are quantified versus left as general contingencies?",
                    "What bid coverage exists for MEP refresh in occupied floor stacks?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What portion of projected rent roll is tied to pending renewals versus signed terms?",
                    "How does the model perform if renewal conversions lag by one leasing cycle?",
                ],
            },
            {
                "id": "qb_trade_1",
                "driver_tile_id": "renewal_downtime_and_refresh_plus_9",
                "questions": [
                    "Where are turnover outages and refresh scopes linked in the construction sequence?",
                    "Which tenant-improvement refresh items can be deferred without revenue impact?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Renewal downtime assumptions are flatter than historical Class B turnover patterns.",
                "action": "Add a renewal timing ladder with downside occupancy case tied to rent roll concentration.",
            },
            {
                "id": "rf_2",
                "flag": "Base-building refresh scope is pooled in contingency with weak item-level ownership.",
                "action": "Break out deferred-maintenance packages with cost owners and release criteria.",
            },
            {
                "id": "rf_3",
                "flag": "Rent reset sensitivity is not tied to specific rollover cohorts.",
                "action": "Run a cohort-based rollover sensitivity and revalidate DSCR at each renewal tranche.",
            },
        ],
    },
}
