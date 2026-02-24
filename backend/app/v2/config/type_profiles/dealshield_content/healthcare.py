"""DealShield content profiles for healthcare types."""

DEALSHIELD_CONTENT_PROFILES = {
    "healthcare_surgical_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_surgical_center_v1",
        "fastest_change": {
            "headline": "What would change this ASC decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Lock GMP carry and escalation assumptions", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress case volume and payer leakage", "tile_id": "revenue_minus_10"},
                {"id": "driver_or", "label": "Validate sterile-core and OR turnover load", "tile_id": "or_turnover_and_sterile_core_plus_12"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "or_turnover_and_sterile_core_plus_12",
                "text": "OR turnover, sterile-core sequencing, and block utilization are modeled at target state instead of surgeon-specific ramp behavior.",
                "why": "Turnover drag pushes late-day utilization down while staffing and fixed cost stay in place.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Procedure mix assumes stable high-acuity reimbursement without denials pressure during ramp.",
                "why": "A payer-authorizations miss in quarter one quickly compresses operating cushion.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Owner-contingency assumptions underweight sterile processing and commissioning callbacks.",
                "why": "The callback cycle is costly and usually appears after the base budget is treated as closed.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which buyout packages are still allowance-backed versus hard-quoted for med-gas, controls, and casework?",
                    "What portion of contingency is already encumbered by code-driven revisions?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How much of first-year case volume is contract-backed by physician groups?",
                    "What denial-rate assumption was used for top three CPT families?",
                ],
            },
            {
                "id": "qb_or",
                "driver_tile_id": "or_turnover_and_sterile_core_plus_12",
                "questions": [
                    "What is the modeled turnover time by room type and where does it differ from operator history?",
                    "Has sterile storage and decontam flow been tested against peak-day block schedules?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "OR turnover assumptions are not tied to real scheduler logs.",
                "action": "Pull six-month block data from the operator and re-run utilization and staffing sensitivity.",
            },
            {
                "id": "rf_2",
                "flag": "Sterile processing equipment lead times are not absorbed in commissioning float.",
                "action": "Issue a lead-time watchlist with explicit mitigation owners for SPD and controls gear.",
            },
            {
                "id": "rf_3",
                "flag": "Payer-mix downside case is missing from year-one underwriting.",
                "action": "Add a denial and reimbursement haircut case before final investment committee sign-off.",
            },
        ],
    },
    "healthcare_imaging_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_imaging_center_v1",
        "fastest_change": {
            "headline": "What would change this imaging-center decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Confirm shell and shielding cost certainty", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Pressure-test scan volume assumptions", "tile_id": "revenue_minus_10"},
                {"id": "driver_power", "label": "Validate electrical quality and RF shielding scope", "tile_id": "shielding_and_power_quality_plus_11"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "shielding_and_power_quality_plus_11",
                "text": "Shielding and quench risk, modality throughput, and uptime assumptions are modeled as if all OEM constraints clear on day one.",
                "why": "Unplanned power-conditioning scope often lands after procurement and carries premium pricing.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Referral capture assumes immediate shift from incumbent systems without transition lag.",
                "why": "Slow referral migration causes underutilized magnet time and weakens early cash generation.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Shielding and vibration criteria are stated at concept level, not coordinated with final equipment vendor data.",
                "why": "Late vendor criteria can force rework in slab, wall assemblies, and electrical routing.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which portions of shielding and RF door packages are still provisional?",
                    "Are slab thickening and vibration isolation quantities fully coordinated with modality count?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How many scans per modality are contractually committed by month six?",
                    "What no-show and reschedule assumptions are embedded in baseline throughput?",
                ],
            },
            {
                "id": "qb_power",
                "driver_tile_id": "shielding_and_power_quality_plus_11",
                "questions": [
                    "What utility-side upgrades are still pending confirmation from the serving provider?",
                    "Has the electrical basis captured OEM tolerance for voltage dips and transients?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Final OEM utility criteria are not reconciled to design documents.",
                "action": "Run a vendor criteria closeout and issue a signed compliance matrix by modality.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue model lacks a staged referral ramp.",
                "action": "Split year-one referrals into retained, converted, and new channels with separate timing curves.",
            },
            {
                "id": "rf_3",
                "flag": "Shielding package still carries design-assist ambiguities.",
                "action": "Freeze shielding details before GMP and remove undefined alternates from contract scope.",
            },
        ],
    },
    "healthcare_urgent_care_v1": {
        "version": "v1",
        "profile_id": "healthcare_urgent_care_v1",
        "fastest_change": {
            "headline": "What would change this urgent-care decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Resolve site and buildout allowances", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress visit volume and reimbursement", "tile_id": "revenue_minus_10"},
                {"id": "driver_flow", "label": "Validate triage flow and turnaround assumptions", "tile_id": "triage_flow_and_lab_turns_plus_10"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "triage_flow_and_lab_turns_plus_10",
                "text": "Walk-in acuity mix, peak-hour staffing, and visit velocity are treated as smooth averages instead of surge-driven variability.",
                "why": "Queue spikes inflate labor and patient leakage faster than the base case reflects.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Reimbursement assumptions do not include a delayed credentialing tail for launch providers.",
                "why": "Credentialing lag lowers collected revenue in the first quarters.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "After-hours security and infection-control scope are underrepresented in operating constraints.",
                "why": "These items can require unplanned fit-out and recurring staffing expense.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which shell, utility, and landlord obligations remain unresolved before permit submission?",
                    "What fraction of MEP and controls is still allowance-based?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How many visits/day are supported by local demand data versus aspirational capture?",
                    "What payer buckets drive the first-year cash-collection assumptions?",
                ],
            },
            {
                "id": "qb_flow",
                "driver_tile_id": "triage_flow_and_lab_turns_plus_10",
                "questions": [
                    "What is the designed room-turn standard at weekday peak and weekend peak?",
                    "Does the lab workflow preserve turnaround targets when two high-acuity cases overlap?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Launch plan does not include credentialing lag in collections forecast.",
                "action": "Apply payer-specific credentialing curves to the first two operating quarters.",
            },
            {
                "id": "rf_2",
                "flag": "Clinic flow assumptions are based on nominal staffing only.",
                "action": "Run a queue simulation for weekend surge conditions and recalibrate staffing.",
            },
            {
                "id": "rf_3",
                "flag": "Late shell clarifications continue to move scope boundaries.",
                "action": "Issue a landlord-tenant responsibility matrix before final GMP release.",
            },
        ],
    },
    "healthcare_outpatient_clinic_v1": {
        "version": "v1",
        "profile_id": "healthcare_outpatient_clinic_v1",
        "fastest_change": {
            "headline": "What would change this outpatient-clinic decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Confirm fit-out and code upgrade certainty", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress exam-room utilization ramp", "tile_id": "revenue_minus_10"},
                {"id": "driver_program", "label": "Validate exam-room program density", "tile_id": "exam_program_and_room_standard_plus_9"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "exam_program_and_room_standard_plus_9",
                "text": "Referral leakage, provider template utilization, and no-show drag are modeled at mature-network performance during ramp.",
                "why": "If provider ramp lags, room utilization and throughput fall below underwritten levels.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Visit conversion assumes a stable referral pipeline from day one.",
                "why": "Referral quality drift can lower net collections before cost base adjusts.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Renovation unknowns in existing systems are lighter than similar recent clinic conversions.",
                "why": "Hidden MEP corrections often surface in demolition and accelerate budget drawdown.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which renovation unknown allowances remain in the estimate, by trade?",
                    "Are accessibility and life-safety upgrades fully reflected in hard costs?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What percent of projected visits is tied to committed provider schedules?",
                    "How sensitive is the model to a slower referral conversion in months one through six?",
                ],
            },
            {
                "id": "qb_program",
                "driver_tile_id": "exam_program_and_room_standard_plus_9",
                "questions": [
                    "Is the room program aligned with specialty mix or still based on a generic template?",
                    "What support-room bottlenecks appear when exam demand exceeds baseline by 10%?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Provider onboarding assumptions are ahead of signed recruitment.",
                "action": "Rebuild the operating ramp using signed start dates only.",
            },
            {
                "id": "rf_2",
                "flag": "Scope narrative does not clearly isolate renovation risk allowances.",
                "action": "Break out demolition unknowns by trade and cap drawdown triggers.",
            },
            {
                "id": "rf_3",
                "flag": "Exam-room and support-room ratios are not validated with operations.",
                "action": "Run an operator program review and freeze room standards before procurement.",
            },
        ],
    },
    "healthcare_medical_office_building_v1": {
        "version": "v1",
        "profile_id": "healthcare_medical_office_building_v1",
        "fastest_change": {
            "headline": "What would change this MOB decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Lock shell and tenant-improvement boundaries", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress lease-up and effective rent", "tile_id": "revenue_minus_10"},
                {"id": "driver_mep", "label": "Validate tenant-ready MEP backbone scope", "tile_id": "tenant_fitout_mep_stack_plus_10"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "tenant_fitout_mep_stack_plus_10",
                "text": "TI/LC burn, lease-up velocity, and rollover stack exposure are underwritten as linear rather than suite-by-suite risk.",
                "why": "Overbuilding base building MEP for uncertain tenant programs compresses returns early.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Lease-up timing assumes anchor occupancy without accounting for deferred commencement risk.",
                "why": "Rent start delays have outsized effect on year-one debt coverage.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Scope split between landlord shell and tenant packages is still ambiguous in critical zones.",
                "why": "Ambiguous boundaries generate change exposure during fit-out turnover.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which tenant-improvement assumptions are embedded in base-building cost rather than TI budgets?",
                    "Are utility and civil upgrades contractually assigned with no overlap?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How many suites are under executed leases versus active LOIs?",
                    "What free-rent and concession assumptions are included in effective rent?",
                ],
            },
            {
                "id": "qb_mep",
                "driver_tile_id": "tenant_fitout_mep_stack_plus_10",
                "questions": [
                    "Which tenant specialties require heavier MEP than shell design currently allows?",
                    "What spare capacity policy is being used for panels, shafts, and rooftop equipment pads?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Shell/TI boundary log remains incomplete for high-acuity suites.",
                "action": "Publish a suite-by-suite responsibility matrix before releasing final bid packages.",
            },
            {
                "id": "rf_2",
                "flag": "Lease-up model assumes faster occupancy than current term sheet velocity.",
                "action": "Introduce a delayed-anchor scenario and re-check decision buffer.",
            },
            {
                "id": "rf_3",
                "flag": "MEP backbone spare-capacity assumptions are not governance-backed.",
                "action": "Approve a documented spare-capacity policy with ownership and operations.",
            },
        ],
    },
    "healthcare_dental_office_v1": {
        "version": "v1",
        "profile_id": "healthcare_dental_office_v1",
        "fastest_change": {
            "headline": "What would change this dental-office decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Confirm operatory buildout certainty", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress chair utilization and collections", "tile_id": "revenue_minus_10"},
                {"id": "driver_gas", "label": "Validate suction, vacuum, and med-gas scope", "tile_id": "chairside_vacuum_and_gas_plus_11"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "chairside_vacuum_and_gas_plus_11",
                "text": "Chair utilization, hygiene mix, and sterilization bottlenecks are modeled at mature-practice cadence before staffing stabilizes.",
                "why": "Late operatory expansion can trigger wall rework and utility redistribution.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Collections assumptions use mature-practice utilization while underwriting a greenfield ramp.",
                "why": "Chair utilization slippage shows up quickly in NOI for smaller footprints.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Sterilization and imaging room requirements are treated as fixed even with specialty expansion risk.",
                "why": "Additional sterilization and imaging scope has high retrofit friction after close-in.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which room-level finish standards are still provisional by operatory type?",
                    "Are imaging and sterilization support spaces fully coordinated with equipment vendors?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What chair utilization curve supports year-one revenue by month?",
                    "How is payer mix and self-pay collection performance reflected in the base case?",
                ],
            },
            {
                "id": "qb_gas",
                "driver_tile_id": "chairside_vacuum_and_gas_plus_11",
                "questions": [
                    "How many future operatories are stubbed for vacuum and med-gas today?",
                    "What rework exposure exists if sedation or oral-surgery scope expands later?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Future operatory growth assumptions are not reconciled to current rough-in plan.",
                "action": "Create a phased rough-in plan with costed future expansion pathways.",
            },
            {
                "id": "rf_2",
                "flag": "Ramp model uses mature utilization targets too early.",
                "action": "Replace year-one volume with staged chair adoption assumptions.",
            },
            {
                "id": "rf_3",
                "flag": "Sterilization and imaging adjacency is not frozen.",
                "action": "Issue final adjacency and equipment matrix before permit resubmittal.",
            },
        ],
    },
    "healthcare_hospital_v1": {
        "version": "v1",
        "profile_id": "healthcare_hospital_v1",
        "fastest_change": {
            "headline": "What would change this hospital decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Pressure-test megaproject contingency", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress census and case-mix durability", "tile_id": "revenue_minus_10"},
                {"id": "driver_redundancy", "label": "Validate redundant MEP commissioning scope", "tile_id": "acuity_mep_redundancy_plus_12"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "acuity_mep_redundancy_plus_12",
                "text": "Nurse staffing intensity, LOS pressure, and service-line mix are modeled at steady state instead of activation-phase conditions.",
                "why": "Commissioning and retest cycles can materially extend spend and schedule drag.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Census and acuity assumptions rely on immediate service-line stabilization after opening.",
                "why": "Delayed service-line activation can depress revenue while fixed staffing costs remain high.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Owner-side program contingency is spread evenly instead of weighted to critical systems and regulatory closeout.",
                "why": "Uneven risk concentration masks where overrun probability is highest.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which contingency buckets are explicitly reserved for regulatory closeout and commissioning?",
                    "Are major long-lead procurement packages fully de-risked for escalation and logistics?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What activation timeline is assumed for each major service line in year one?",
                    "How sensitive is value to slower census growth in high-margin departments?",
                ],
            },
            {
                "id": "qb_redundancy",
                "driver_tile_id": "acuity_mep_redundancy_plus_12",
                "questions": [
                    "What integrated systems testing protocol and retest allowance are included in the budget?",
                    "Where are dual-feed, backup, and failover assumptions not yet validated by design narrative?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Integrated testing effort is underestimated for critical systems turnover.",
                "action": "Add a dedicated commissioning workstream with quantified retest allowances.",
            },
            {
                "id": "rf_2",
                "flag": "Service-line ramp assumptions lack operational activation checkpoints.",
                "action": "Stage revenue assumptions to milestone-based activation rather than calendar-only targets.",
            },
            {
                "id": "rf_3",
                "flag": "Contingency allocation is not risk-weighted to critical-path packages.",
                "action": "Reallocate contingency by package risk profile and enforce draw governance.",
            },
        ],
    },
    "healthcare_medical_center_v1": {
        "version": "v1",
        "profile_id": "healthcare_medical_center_v1",
        "fastest_change": {
            "headline": "What would change this medical-center decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Lock base-building and specialty-suite carry", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress specialty program ramp", "tile_id": "revenue_minus_10"},
                {"id": "driver_power", "label": "Validate service-line power density assumptions", "tile_id": "service_line_power_density_plus_11"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "service_line_power_density_plus_11",
                "text": "Procedure mix, diagnostic throughput, and care-path coordination are assumed to scale in lockstep across service lines.",
                "why": "Underbuilt power capacity creates high-cost retrofit exposure during growth.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Service-line ramp combines independent specialty curves into a single blended forecast.",
                "why": "Blended ramps hide weak early performance in slower-onboarding specialties.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Shared infrastructure allowances are not apportioned by expected future tenant intensity.",
                "why": "Cost allocation drift can absorb value before lease economics stabilize.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "How are shared infrastructure costs allocated between immediate and future suites?",
                    "What unresolved assumptions remain in common-area MEP and life-safety packages?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What is the opening schedule by specialty suite and provider team?",
                    "Where does the model assume full-rate utilization before contracts support it?",
                ],
            },
            {
                "id": "qb_power",
                "driver_tile_id": "service_line_power_density_plus_11",
                "questions": [
                    "What reserve panel and riser strategy is documented for future high-acuity suites?",
                    "Has transformer and feeder sizing been validated against the two-year growth plan?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Power reserve strategy is not aligned with future specialty buildout pipeline.",
                "action": "Issue a growth-capacity electrical plan with defined expansion trigger points.",
            },
            {
                "id": "rf_2",
                "flag": "Revenue ramp assumptions are over-aggregated across service lines.",
                "action": "Split service-line ramps and apply independent confidence ranges.",
            },
            {
                "id": "rf_3",
                "flag": "Shared-cost allocation policy is undocumented.",
                "action": "Codify common-infrastructure allocation before lease underwriting sign-off.",
            },
        ],
    },
    "healthcare_nursing_home_v1": {
        "version": "v1",
        "profile_id": "healthcare_nursing_home_v1",
        "fastest_change": {
            "headline": "What would change this nursing-home decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Confirm resident-unit fit-out and code carry", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress occupancy and reimbursement durability", "tile_id": "revenue_minus_10"},
                {"id": "driver_lifesafety", "label": "Validate resident-room life-safety scope", "tile_id": "resident_room_life_safety_plus_9"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "resident_room_life_safety_plus_9",
                "text": "Census mix, agency labor dependency, and reimbursement pressure are treated as independent instead of compounding risks.",
                "why": "Survey-driven corrections can create concentrated rework late in turnover.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Occupancy and reimbursement assumptions are not stress-tested for higher acuity staffing pressure.",
                "why": "Higher acuity can raise labor burden and shrink margin at fixed reimbursement.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Resident support-space finishes are modeled as generic multifamily-like interiors.",
                "why": "Healthcare-grade durability and infection-control details typically cost more.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which resident-support spaces still carry non-healthcare finish assumptions?",
                    "What percentage of budget is reserved for survey correction work?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "How does the model perform with a slower occupancy ramp in skilled-nursing beds?",
                    "What wage-pressure assumption is paired with reimbursement downside?",
                ],
            },
            {
                "id": "qb_lifesafety",
                "driver_tile_id": "resident_room_life_safety_plus_9",
                "questions": [
                    "Which life-safety details are still awaiting AHJ or surveyor confirmation?",
                    "Are nurse-call and egress upgrades fully coordinated with final room layouts?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Survey correction exposure is not clearly budgeted.",
                "action": "Add a correction-cycle reserve and define release conditions.",
            },
            {
                "id": "rf_2",
                "flag": "Occupancy downside and labor-pressure cases are disconnected.",
                "action": "Run a combined occupancy-labor stress case and update approval thresholds.",
            },
            {
                "id": "rf_3",
                "flag": "Resident-room details are not fully healthcare-grade in current specs.",
                "action": "Reconcile finish schedules against healthcare durability and infection-control standards.",
            },
        ],
    },
    "healthcare_rehabilitation_v1": {
        "version": "v1",
        "profile_id": "healthcare_rehabilitation_v1",
        "fastest_change": {
            "headline": "What would change this rehabilitation-center decision fastest?",
            "drivers": [
                {"id": "driver_cost", "label": "Confirm therapy-space and equipment allowances", "tile_id": "cost_plus_10"},
                {"id": "driver_revenue", "label": "Stress therapy volume and visit mix", "tile_id": "revenue_minus_10"},
                {"id": "driver_mep", "label": "Validate therapy-gym MEP integration scope", "tile_id": "therapy_gym_mep_integration_plus_10"},
            ],
        },
        "most_likely_wrong": [
            {
                "id": "mlw_1",
                "driver_tile_id": "therapy_gym_mep_integration_plus_10",
                "text": "Therapy intensity, payer authorization friction, and LOS drift are underwritten at baseline rather than constrained ramp capacity.",
                "why": "Equipment-density drift can require additional distribution and controls rework.",
            },
            {
                "id": "mlw_2",
                "driver_tile_id": "revenue_minus_10",
                "text": "Therapy visit ramp assumes referral conversion speed that has not been demonstrated in-market.",
                "why": "Underperforming referral conversion drags utilization and NOI in year one.",
            },
            {
                "id": "mlw_3",
                "driver_tile_id": "cost_plus_10",
                "text": "Specialty flooring and mobility-safety detailing are budgeted at baseline commercial levels.",
                "why": "Rehab environments often need more robust detailing than baseline assumptions.",
            },
        ],
        "question_bank": [
            {
                "id": "qb_cost",
                "driver_tile_id": "cost_plus_10",
                "questions": [
                    "Which therapy-space finish and safety packages are still allowance-only?",
                    "Are hydrotherapy and support-area infrastructure costs fully captured?",
                ],
            },
            {
                "id": "qb_revenue",
                "driver_tile_id": "revenue_minus_10",
                "questions": [
                    "What referral channels support the month-by-month therapy volume curve?",
                    "How sensitive is revenue to slower adoption of high-margin service lines?",
                ],
            },
            {
                "id": "qb_mep",
                "driver_tile_id": "therapy_gym_mep_integration_plus_10",
                "questions": [
                    "What equipment list is frozen for therapy gyms and treatment bays?",
                    "How are ventilation and electrical loads adjusted if therapy program intensity rises?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rf_1",
                "flag": "Therapy-equipment assumptions are not fully frozen against MEP design.",
                "action": "Lock the equipment schedule and revalidate load calculations before buyout.",
            },
            {
                "id": "rf_2",
                "flag": "Referral ramp assumptions are not tied to signed feeder relationships.",
                "action": "Recast revenue ramp using committed referral sources only.",
            },
            {
                "id": "rf_3",
                "flag": "Safety and specialty-flooring scope is underdetailed.",
                "action": "Issue a rehab-specific finish and safety detail package for pricing alignment.",
            },
        ],
    },
}
