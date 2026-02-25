"""DealShield narrative content profiles for educational subtypes."""

DEALSHIELD_CONTENT_PROFILES = {
    "educational_elementary_school_v1": {
        "version": "v1",
        "profile_id": "educational_elementary_school_v1",
        "fastest_change": {
            "headline": "Elementary scope shifts are most sensitive to ventilation and classroom-program drift.",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Validate GMP basis against current classroom count.",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Reconfirm enrollment-backed operating plan.",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_program",
                    "label": "Lock early-grade ventilation and support-area standards.",
                    "tile_id": "early_grade_program_and_ventilation_plus_9",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Early-grade support spaces are treated as fixed while special-needs pullout demand is still moving.",
                "why": "Late classroom support reprogramming pushes mechanical and circulation rework after pricing.",
                "driver_tile_id": "early_grade_program_and_ventilation_plus_9",
            },
            {
                "id": "mlw_2",
                "text": "Base budget assumes no late alternates despite unresolved district add-alternates.",
                "why": "Alternates often backfill into base scope once bids return, widening cost carry.",
                "driver_tile_id": "cost_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Operational plan assumes stable enrollment despite active boundary review.",
                "why": "Enrollment dilution can compress annual revenue support for debt metrics.",
                "driver_tile_id": "revenue_minus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which site, safety, or accessibility allowances remain provisional?",
                    "What open alternates are likely to be absorbed into base scope?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What enrollment case underwrites the operating model?",
                    "How sensitive is debt coverage to enrollment variance?",
                ],
            },
            {
                "id": "qb_program_1",
                "driver_tile_id": "early_grade_program_and_ventilation_plus_9",
                "questions": [
                    "Which classroom-support adjacencies are still in educational-program review?",
                    "Are ventilation rates finalized for high-occupancy instructional spaces?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Program confirms are lagging GMP assumptions for early-grade support spaces.",
                "action": "Issue a district sign-off package for classroom/support counts before procurement lock.",
            },
            {
                "id": "rf_2",
                "flag": "Allowance conversion risk remains concentrated in MEP and code items.",
                "action": "Run a pre-award allowance burn-down with accountable owners and due dates.",
            },
            {
                "id": "rf_3",
                "flag": "Enrollment base case is not yet synchronized with finance assumptions.",
                "action": "Publish a shared enrollment sensitivity sheet tied directly to debt sizing assumptions.",
            },
        ],
    },
    "educational_middle_school_v1": {
        "version": "v1",
        "profile_id": "educational_middle_school_v1",
        "fastest_change": {
            "headline": "Middle-school exposure centers on curriculum labs and electrical density scope.",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Reconfirm hard-cost baseline before lab package release.",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Validate enrollment throughput assumptions for staffing plans.",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_program",
                    "label": "Freeze media/STEM infrastructure and power standards.",
                    "tile_id": "media_and_stem_load_plus_10",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Technology-ready classroom scope is assumed final while curriculum sequencing is still in flux.",
                "why": "Lab and media revisions typically increase power/data pathways after rough-in starts.",
                "driver_tile_id": "media_and_stem_load_plus_10",
            },
            {
                "id": "mlw_2",
                "text": "Procurement assumes commodity stability on electrical gear without secondary quotes.",
                "why": "Single-source assumptions magnify downside if switchgear lead times or pricing move.",
                "driver_tile_id": "cost_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Enrollment case underwrites staffing growth that has not been board-approved.",
                "why": "Delayed staffing authorization can suppress realized revenue and utilization targets.",
                "driver_tile_id": "revenue_minus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "What percent of electrical and life-safety scope is still allowance-backed?",
                    "Where are alternates likely to move into base during buyout?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What enrollment scenario is funding-supporting debt coverage?",
                    "How does staffing ramp respond to a downside enrollment case?",
                ],
            },
            {
                "id": "qb_program_1",
                "driver_tile_id": "media_and_stem_load_plus_10",
                "questions": [
                    "Have district curriculum labs and media rooms reached issue-for-procurement maturity?",
                    "Is AV/power/data density validated against final room standards?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Curriculum lab package is not frozen before electrical procurement.",
                "action": "Require instructional-program sign-off on lab/media standards before release.",
            },
            {
                "id": "rf_2",
                "flag": "Cost basis relies on unresolved alternates.",
                "action": "Convert alternates to explicit budget deltas with owner decision dates.",
            },
            {
                "id": "rf_3",
                "flag": "Enrollment and staffing assumptions are held in separate planning models.",
                "action": "Establish one synchronized staffing/enrollment basis for underwriting and operations.",
            },
        ],
    },
    "educational_high_school_v1": {
        "version": "v1",
        "profile_id": "educational_high_school_v1",
        "fastest_change": {
            "headline": "High-school downside is concentrated in athletics and performing-arts finish intensity.",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Hold baseline cost scope to issued construction documents.",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Stress enrollment and schedule assumptions used for operating support.",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_program",
                    "label": "Control athletics/performing-arts finish creep.",
                    "tile_id": "athletics_and_performing_arts_plus_11",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Athletics and performing-arts specifications are modeled as fixed before stakeholder programming closes.",
                "why": "Late finish and equipment upgrades frequently reprice major package scopes.",
                "driver_tile_id": "athletics_and_performing_arts_plus_11",
            },
            {
                "id": "mlw_2",
                "text": "Bid normalization assumes limited escalation despite deferred package buyouts.",
                "why": "Deferred procurement windows add exposure to labor and material repricing.",
                "driver_tile_id": "cost_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Enrollment projections are treated as deterministic across feeder-pattern changes.",
                "why": "Downside enrollment pressure compresses expected operating support capacity.",
                "driver_tile_id": "revenue_minus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which large packages are still pending market checks?",
                    "What contingency buckets remain exposed to unresolved owner preferences?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How is downside enrollment represented in debt support scenarios?",
                    "What triggers reforecast if enrollment materially lags target?",
                ],
            },
            {
                "id": "qb_program_1",
                "driver_tile_id": "athletics_and_performing_arts_plus_11",
                "questions": [
                    "Are stadium, field-house, and performing-arts scopes fully reconciled to budget?",
                    "What unresolved stakeholder asks can still move high-cost finish packages?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Athletics and arts scopes remain partially unresolved at procurement milestone.",
                "action": "Set a program freeze date with change-control and escalation thresholds.",
            },
            {
                "id": "rf_2",
                "flag": "Commodity and labor escalation is not refreshed for deferred packages.",
                "action": "Run a mid-procurement repricing checkpoint before final buyout approvals.",
            },
            {
                "id": "rf_3",
                "flag": "Enrollment downside is not connected to operating-support stress tests.",
                "action": "Publish enrollment-driven operating support sensitivity with governance sign-off.",
            },
        ],
    },
    "educational_university_v1": {
        "version": "v1",
        "profile_id": "educational_university_v1",
        "fastest_change": {
            "headline": "University projects are most fragile at research commissioning and MEP integration points.",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Revalidate baseline cost against current research program.",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Stress tuition/research throughput assumptions in downside cases.",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_program",
                    "label": "Lock research MEP controls and commissioning sequence.",
                    "tile_id": "research_mep_and_controls_plus_12",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Research program commissioning effort is treated as linear despite multi-lab turnover dependencies.",
                "why": "Validation and turnover loops can create compounding schedule and rework exposure.",
                "driver_tile_id": "research_mep_and_controls_plus_12",
            },
            {
                "id": "mlw_2",
                "text": "Cost baseline assumes stable long-lead procurement for specialized MEP controls.",
                "why": "Vendor and integration risk can surface late and expand installed-cost variance.",
                "driver_tile_id": "cost_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Revenue-side assumptions do not stress lower-than-planned program occupancy.",
                "why": "Program utilization shortfall reduces support for fixed operating and debt loads.",
                "driver_tile_id": "revenue_minus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which research packages still depend on preliminary vendor quotes?",
                    "How much of long-lead controls scope lacks locked pricing?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What downside enrollment/research-utilization case is used for underwriting?",
                    "How quickly can operating plans be right-sized under weak demand?",
                ],
            },
            {
                "id": "qb_program_1",
                "driver_tile_id": "research_mep_and_controls_plus_12",
                "questions": [
                    "Is commissioning sequence complete for all research-support systems?",
                    "Where are unresolved controls integrations likely to force retesting?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Research commissioning plan is incomplete at procurement lock.",
                "action": "Require a sequenced commissioning matrix with accountable subsystem owners.",
            },
            {
                "id": "rf_2",
                "flag": "Long-lead controls and lab-support packages lack final cost certainty.",
                "action": "Establish vendor lock and alternate-path contingencies before release.",
            },
            {
                "id": "rf_3",
                "flag": "Downside utilization scenarios are not represented in operating support planning.",
                "action": "Add utilization stress tests to the finance and operations governance pack.",
            },
        ],
    },
    "educational_community_college_v1": {
        "version": "v1",
        "profile_id": "educational_community_college_v1",
        "fastest_change": {
            "headline": "Community-college volatility is tied to vocational fit-out turnover and program shifts.",
            "drivers": [
                {
                    "id": "driver_cost",
                    "label": "Hold baseline against issued workforce-program fit-out scope.",
                    "tile_id": "cost_plus_10",
                },
                {
                    "id": "driver_revenue",
                    "label": "Recheck enrollment-based support assumptions each planning cycle.",
                    "tile_id": "revenue_minus_10",
                },
                {
                    "id": "driver_program",
                    "label": "Control vocational turnover scope and finishes creep.",
                    "tile_id": "vocational_fitout_and_turnover_plus_9",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "text": "Vocational lab turnover assumptions stay fixed while partner-program requirements are still negotiating.",
                "why": "Late workforce-partner changes often drive non-trivial fit-out and finishes rework.",
                "driver_tile_id": "vocational_fitout_and_turnover_plus_9",
            },
            {
                "id": "mlw_2",
                "text": "Cost plan assumes procurement stability for specialized training equipment interfaces.",
                "why": "Equipment-interface changes can drive trade rework after initial package release.",
                "driver_tile_id": "cost_plus_10",
            },
            {
                "id": "mlw_3",
                "text": "Enrollment support case does not include downside for program-mix rebalancing.",
                "why": "Program-mix shifts can lower effective throughput and annual revenue support.",
                "driver_tile_id": "revenue_minus_10",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost_1",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which trade packages remain exposed to unresolved partner equipment requirements?",
                    "Where does bid coverage remain thin for vocational support scopes?",
                ],
            },
            {
                "id": "qb_revenue_1",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What program-mix downside case is embedded in revenue support assumptions?",
                    "How often are enrollment-driven forecasts refreshed in governance reviews?",
                ],
            },
            {
                "id": "qb_program_1",
                "driver_tile_id": "vocational_fitout_and_turnover_plus_9",
                "questions": [
                    "Are vocational lab handoff standards frozen for all partner programs?",
                    "What unresolved turnover requirements could still alter finish and support scope?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Partner-program turnover criteria remain open beyond procurement milestone.",
                "action": "Issue a turnover readiness checklist with sign-off owners per program track.",
            },
            {
                "id": "rf_2",
                "flag": "Workforce lab scope contains unresolved equipment-interface assumptions.",
                "action": "Run an interface reconciliation workshop before final package release.",
            },
            {
                "id": "rf_3",
                "flag": "Enrollment and program-mix downside case is not reflected in support planning.",
                "action": "Adopt a quarterly downside refresh linking enrollment, mix, and support capacity.",
            },
        ],
    },
}
