"""DealShield content profiles for recreation subtypes."""


DEALSHIELD_CONTENT_PROFILES = {
    "recreation_fitness_center_v1": {
        "version": "v1",
        "profile_id": "recreation_fitness_center_v1",
        "fastest_change": {
            "headline": "What changes this recreation feasibility decision fastest?",
            "drivers": [
                {
                    "id": "fitness_driver_hvac",
                    "tile_id": "fitness_center_hvac_load_plus_11",
                    "label": "Validate peak-hour ventilation and cooling density assumptions.",
                },
                {
                    "id": "fitness_driver_locker",
                    "tile_id": "fitness_center_locker_plumbing_plus_9",
                    "label": "Validate locker/shower fixture counts and service intervals.",
                },
                {
                    "id": "fitness_driver_power",
                    "tile_id": "fitness_center_peak_power_density_plus_8",
                    "label": "Validate high-demand cardio/strength power diversity assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "fitness_mlw_peak_conditioning",
                "driver_tile_id": "fitness_center_hvac_load_plus_11",
                "text": "Stacked class schedules likely understate concurrent cooling and outside-air demand during evening peaks.",
                "why": "Peak-hour conditioning misses create retrofit risk in duct routing and equipment sizing.",
            },
            {
                "id": "fitness_mlw_locker_turnover",
                "driver_tile_id": "fitness_center_locker_plumbing_plus_9",
                "text": "Locker and shower turnover assumptions likely ignore post-class demand waves.",
                "why": "Fixture and hot-water recovery gaps drive service complaints and late scope additions.",
            },
            {
                "id": "fitness_mlw_power_spikes",
                "driver_tile_id": "fitness_center_peak_power_density_plus_8",
                "text": "Electrical load diversity is modeled too optimistically for simultaneous cardio and strength circuits.",
                "why": "Circuit and panel under-sizing forces costly rework after commissioning starts.",
            },
        ],
        "question_bank": [
            {
                "id": "fitness_qb_hvac",
                "driver_tile_id": "fitness_center_hvac_load_plus_11",
                "questions": [
                    "Which spaces have verified peak occupancy schedules instead of assumptions?",
                    "Where are latent load and dehumidification allowances still conceptual?",
                ],
            },
            {
                "id": "fitness_qb_locker",
                "driver_tile_id": "fitness_center_locker_plumbing_plus_9",
                "questions": [
                    "What fixture counts are backed by operator service standards?",
                    "Which hot-water recovery assumptions remain unverified by operations?",
                ],
            },
            {
                "id": "fitness_qb_power",
                "driver_tile_id": "fitness_center_peak_power_density_plus_8",
                "questions": [
                    "Which equipment zones require dedicated circuits beyond baseline assumptions?",
                    "Where are panel capacity and demand-factor assumptions not yet validated?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "fitness_rf_hvac_basis",
                "flag": "Peak ventilation basis is not tied to approved class utilization data.",
                "action": "Publish a signed occupancy/ventilation matrix for all activity zones before DD lock.",
            },
            {
                "id": "fitness_rf_wet_core",
                "flag": "Locker and shower design counts remain allowance-driven.",
                "action": "Freeze locker-room fixture counts and recovery targets with operator signoff.",
            },
            {
                "id": "fitness_rf_power_basis",
                "flag": "Equipment power plan has unresolved branch-circuit responsibilities.",
                "action": "Issue a circuit ownership matrix by equipment package and commissioning package.",
            },
        ],
    },
    "recreation_sports_complex_v1": {
        "version": "v1",
        "profile_id": "recreation_sports_complex_v1",
        "fastest_change": {
            "headline": "What changes this recreation feasibility decision fastest?",
            "drivers": [
                {
                    "id": "sports_driver_structure",
                    "tile_id": "sports_complex_long_span_structure_plus_12",
                    "label": "Validate long-span framing and lateral assumptions.",
                },
                {
                    "id": "sports_driver_hvac",
                    "tile_id": "sports_complex_event_hvac_plus_8",
                    "label": "Validate event turnover and ventilation reset assumptions.",
                },
                {
                    "id": "sports_driver_power",
                    "tile_id": "sports_complex_scoreboard_power_plus_9",
                    "label": "Validate event-lighting and scoreboard power assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "sports_mlw_long_span_sequence",
                "driver_tile_id": "sports_complex_long_span_structure_plus_12",
                "text": "Roof and long-span sequencing likely underestimates crane access and temporary works constraints.",
                "why": "Sequencing misses can shift procurement and compress downstream interior turnover.",
            },
            {
                "id": "sports_mlw_event_hvac_turnover",
                "driver_tile_id": "sports_complex_event_hvac_plus_8",
                "text": "Turnover HVAC assumptions likely miss rapid occupancy swings between tournament blocks.",
                "why": "Air-side reset strategies may fail under repeated high-load transitions.",
            },
            {
                "id": "sports_mlw_event_power",
                "driver_tile_id": "sports_complex_scoreboard_power_plus_9",
                "text": "Event broadcast and scoreboard feeds are modeled without adequate redundancy allowances.",
                "why": "Power quality and redundancy changes are expensive once infrastructure paths are fixed.",
            },
        ],
        "question_bank": [
            {
                "id": "sports_qb_structure",
                "driver_tile_id": "sports_complex_long_span_structure_plus_12",
                "questions": [
                    "Which long-span zones still rely on preliminary framing assumptions?",
                    "Where are temporary-works and erection plans missing from current cost basis?",
                ],
            },
            {
                "id": "sports_qb_hvac",
                "driver_tile_id": "sports_complex_event_hvac_plus_8",
                "questions": [
                    "Which occupancy transition events define peak mechanical reset demand?",
                    "What unresolved controls logic remains for multiple simultaneous venues?",
                ],
            },
            {
                "id": "sports_qb_power",
                "driver_tile_id": "sports_complex_scoreboard_power_plus_9",
                "questions": [
                    "Which event systems require UPS/generator coverage not in base assumptions?",
                    "Where are lighting and AV loads still estimated without vendor data?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "sports_rf_span",
                "flag": "Long-span structural package lacks finalized erection strategy.",
                "action": "Lock erection and temporary works plan with structural engineer and CM.",
            },
            {
                "id": "sports_rf_hvac",
                "flag": "Event turnover HVAC controls remain high-level and untested.",
                "action": "Run controls simulation for back-to-back event occupancy profiles.",
            },
            {
                "id": "sports_rf_power",
                "flag": "Scoreboard/event power redundancy scope remains ambiguous.",
                "action": "Publish one-line diagrams and responsibility matrix before GMP.",
            },
        ],
    },
    "recreation_aquatic_center_v1": {
        "version": "v1",
        "profile_id": "recreation_aquatic_center_v1",
        "fastest_change": {
            "headline": "What changes this recreation feasibility decision fastest?",
            "drivers": [
                {
                    "id": "aquatic_driver_dehumidification",
                    "tile_id": "aquatic_center_dehumidification_plus_14",
                    "label": "Validate natatorium dehumidification duty and controls assumptions.",
                },
                {
                    "id": "aquatic_driver_piping",
                    "tile_id": "aquatic_center_pool_piping_plus_12",
                    "label": "Validate circulation, filtration, and chemical feed piping assumptions.",
                },
                {
                    "id": "aquatic_driver_corrosion",
                    "tile_id": "aquatic_center_corrosion_hardening_plus_9",
                    "label": "Validate corrosion-resistant electrical and controls assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "aquatic_mlw_dehumidification_basis",
                "driver_tile_id": "aquatic_center_dehumidification_plus_14",
                "text": "Natatorium latent-load assumptions likely miss simultaneous high-bather and spectator conditions.",
                "why": "Under-modeled latent control causes condensation risk and costly HVAC reconfiguration.",
            },
            {
                "id": "aquatic_mlw_filtration",
                "driver_tile_id": "aquatic_center_pool_piping_plus_12",
                "text": "Pool filtration and turnover assumptions likely understate backwash and treatment downtime.",
                "why": "Hydraulic and treatment adjustments can cascade into plumbing and controls rework.",
            },
            {
                "id": "aquatic_mlw_corrosion",
                "driver_tile_id": "aquatic_center_corrosion_hardening_plus_9",
                "text": "Electrical enclosure durability assumptions likely overestimate baseline corrosion resistance.",
                "why": "Early component failures force accelerated replacement and protective upgrades.",
            },
        ],
        "question_bank": [
            {
                "id": "aquatic_qb_dehumidification",
                "driver_tile_id": "aquatic_center_dehumidification_plus_14",
                "questions": [
                    "Which design-day humidity scenarios are approved by operator and engineer of record?",
                    "Where are spectator and competition latent loads still represented as allowances?",
                ],
            },
            {
                "id": "aquatic_qb_piping",
                "driver_tile_id": "aquatic_center_pool_piping_plus_12",
                "questions": [
                    "Which pool loops still lack finalized hydraulic calculations?",
                    "What chemical feed and backwash assumptions remain unresolved with operations?",
                ],
            },
            {
                "id": "aquatic_qb_corrosion",
                "driver_tile_id": "aquatic_center_corrosion_hardening_plus_9",
                "questions": [
                    "Which electrical components require upgraded enclosure ratings in natatorium zones?",
                    "Where are maintenance replacement intervals still based on vendor defaults?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "aquatic_rf_humidity",
                "flag": "Dehumidification control narrative is incomplete for competition and spectator events.",
                "action": "Issue a signed humidity-control sequence with event-mode setpoints.",
            },
            {
                "id": "aquatic_rf_water_system",
                "flag": "Pool system basis does not fully tie to treatment and backwash operations.",
                "action": "Publish integrated filtration and treatment process narrative with ownership tags.",
            },
            {
                "id": "aquatic_rf_corrosion",
                "flag": "Corrosion protection assumptions remain generic for high-chloride zones.",
                "action": "Freeze enclosure/coating standards by room classification prior to procurement.",
            },
        ],
    },
    "recreation_recreation_center_v1": {
        "version": "v1",
        "profile_id": "recreation_recreation_center_v1",
        "fastest_change": {
            "headline": "What changes this recreation feasibility decision fastest?",
            "drivers": [
                {
                    "id": "rec_center_driver_finishes",
                    "tile_id": "recreation_center_multiprogram_finishes_plus_10",
                    "label": "Validate multiprogram durability and reconfiguration assumptions.",
                },
                {
                    "id": "rec_center_driver_hvac",
                    "tile_id": "recreation_center_shared_hvac_plus_9",
                    "label": "Validate mixed-use scheduling and zoning assumptions.",
                },
                {
                    "id": "rec_center_driver_plumbing",
                    "tile_id": "recreation_center_locker_plumbing_plus_8",
                    "label": "Validate locker/restroom demand and maintenance assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "rec_center_mlw_program_flex",
                "driver_tile_id": "recreation_center_multiprogram_finishes_plus_10",
                "text": "Assumed room flexibility likely overlooks wear and reset requirements across conflicting user groups.",
                "why": "Durability and reset scope grows when programming frequency exceeds baseline assumptions.",
            },
            {
                "id": "rec_center_mlw_hvac_controls",
                "driver_tile_id": "recreation_center_shared_hvac_plus_9",
                "text": "Shared-zone HVAC control logic likely understates simultaneous demand from mixed-age programs.",
                "why": "Poor zone control increases comfort complaints and rebalancing costs.",
            },
            {
                "id": "rec_center_mlw_wet_core",
                "driver_tile_id": "recreation_center_locker_plumbing_plus_8",
                "text": "Restroom and locker assumptions likely undercount peak transition periods between programs.",
                "why": "Peak usage spikes can force fixture additions and domestic hot-water upgrades.",
            },
        ],
        "question_bank": [
            {
                "id": "rec_center_qb_finishes",
                "driver_tile_id": "recreation_center_multiprogram_finishes_plus_10",
                "questions": [
                    "Which spaces require rapid reset between incompatible uses?",
                    "Where are finish allowances still generic instead of program-specific?",
                ],
            },
            {
                "id": "rec_center_qb_hvac",
                "driver_tile_id": "recreation_center_shared_hvac_plus_9",
                "questions": [
                    "Which zones have unresolved occupancy profiles in controls sequences?",
                    "What evidence supports current diversity factors for simultaneous usage?",
                ],
            },
            {
                "id": "rec_center_qb_plumbing",
                "driver_tile_id": "recreation_center_locker_plumbing_plus_8",
                "questions": [
                    "Which fixture groups are still assumption-based versus operations-backed?",
                    "Where are domestic hot-water peak factors not yet validated?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "rec_center_rf_program",
                "flag": "Program reset and durability strategy is not fully defined.",
                "action": "Publish room-by-room reset standards and finish durability classes.",
            },
            {
                "id": "rec_center_rf_controls",
                "flag": "HVAC zoning logic remains provisional for shared-use hours.",
                "action": "Approve a final zoning and controls matrix tied to program calendar.",
            },
            {
                "id": "rec_center_rf_plumbing",
                "flag": "Wet-core demand model is not reconciled with peak schedule transitions.",
                "action": "Run peak fixture analysis and lock domestic water heater capacity basis.",
            },
        ],
    },
    "recreation_stadium_v1": {
        "version": "v1",
        "profile_id": "recreation_stadium_v1",
        "fastest_change": {
            "headline": "What changes this recreation feasibility decision fastest?",
            "drivers": [
                {
                    "id": "stadium_driver_structure",
                    "tile_id": "stadium_seating_bowl_structure_plus_15",
                    "label": "Validate seating-bowl and cantilever structural assumptions.",
                },
                {
                    "id": "stadium_driver_ventilation",
                    "tile_id": "stadium_crowd_ventilation_plus_10",
                    "label": "Validate crowd-mode ventilation and purge assumptions.",
                },
                {
                    "id": "stadium_driver_power",
                    "tile_id": "stadium_event_power_plus_13",
                    "label": "Validate event production and broadcast power assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "stadium_mlw_bowl_revisions",
                "driver_tile_id": "stadium_seating_bowl_structure_plus_15",
                "text": "Seating-bowl geometry and sightline coordination likely underestimate structural revision cycles.",
                "why": "Sightline-driven structural revisions can expand tonnage and fabrication lead times.",
            },
            {
                "id": "stadium_mlw_crowd_modes",
                "driver_tile_id": "stadium_crowd_ventilation_plus_10",
                "text": "Crowd-mode ventilation assumptions likely overstate reset speed between event profiles.",
                "why": "Event mode shifts can exceed modeled air-change and controls response capabilities.",
            },
            {
                "id": "stadium_mlw_event_power",
                "driver_tile_id": "stadium_event_power_plus_13",
                "text": "Broadcast and temporary production power assumptions likely miss promoter-specific load spikes.",
                "why": "Temporary power expansions are expensive once distribution pathways are constrained.",
            },
        ],
        "question_bank": [
            {
                "id": "stadium_qb_structure",
                "driver_tile_id": "stadium_seating_bowl_structure_plus_15",
                "questions": [
                    "Which seating-bowl geometry decisions are still provisional at this cost stage?",
                    "Where are long-lead structural packages exposed to late design movement?",
                ],
            },
            {
                "id": "stadium_qb_ventilation",
                "driver_tile_id": "stadium_crowd_ventilation_plus_10",
                "questions": [
                    "Which event modes drive the highest required ventilation reset rates?",
                    "Where are purge and smoke-control assumptions not validated by modeling?",
                ],
            },
            {
                "id": "stadium_qb_power",
                "driver_tile_id": "stadium_event_power_plus_13",
                "questions": [
                    "Which production loads remain estimated rather than vendor-verified?",
                    "What temporary-power contingencies are planned for non-standard events?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "stadium_rf_structure",
                "flag": "Seating-bowl structural package remains exposed to unresolved geometry decisions.",
                "action": "Freeze geometry decision gates and align them with structural procurement milestones.",
            },
            {
                "id": "stadium_rf_ventilation",
                "flag": "Ventilation mode transitions are not fully tested across event types.",
                "action": "Complete event-mode controls simulations and lock transition sequences.",
            },
            {
                "id": "stadium_rf_power",
                "flag": "Event power assumptions do not fully capture promoter-specific temporary loads.",
                "action": "Issue a promoter load matrix and reserve distribution capacity by event class.",
            },
        ],
    },
}
