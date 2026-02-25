"""DealShield content profiles for civic types."""


DEALSHIELD_CONTENT_PROFILES = {
    "civic_library_v1": {
        "version": "v1",
        "profile_id": "civic_library_v1",
        "fastest_change": {
            "headline": "What changes this civic feasibility decision fastest?",
            "drivers": [
                {
                    "id": "library_driver_stacks",
                    "tile_id": "library_stack_reinforcement_plus_12",
                    "label": "Confirm stack-load assumptions and structural basis.",
                },
                {
                    "id": "library_driver_makerspace",
                    "tile_id": "library_makerspace_mep_plus_10",
                    "label": "Confirm makerspace ventilation and power density assumptions.",
                },
                {
                    "id": "library_driver_access",
                    "tile_id": "library_public_access_security_plus_8",
                    "label": "Confirm after-hours access/security operations model.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "library_mlw_stack_program_drift",
                "driver_tile_id": "library_stack_reinforcement_plus_12",
                "text": "Collection growth and compact shelving assumptions likely understate live-load drift in stack zones.",
                "why": "Late stack density increases drive localized structural retrofits and sequencing rework.",
            },
            {
                "id": "library_mlw_makerspace_controls",
                "driver_tile_id": "library_makerspace_mep_plus_10",
                "text": "Makerspace process exhaust and controls are treated as standard tenant systems.",
                "why": "Specialty ventilation and controls interfaces often expand commissioning scope.",
            },
            {
                "id": "library_mlw_public_access",
                "driver_tile_id": "library_public_access_security_plus_8",
                "text": "Public access and staffing assumptions likely miss extended-hours supervision requirements.",
                "why": "Security/operations gaps force added technology and staffing allowances before turnover.",
            },
        ],
        "question_bank": [
            {
                "id": "library_qb_program",
                "driver_tile_id": "library_stack_reinforcement_plus_12",
                "questions": [
                    "Which stack areas are fixed versus expandable over the first five years?",
                    "Where are structural load allowances not backed by shelf-layout evidence?",
                ],
            },
            {
                "id": "library_qb_makerspace",
                "driver_tile_id": "library_makerspace_mep_plus_10",
                "questions": [
                    "Which makerspace functions require dedicated exhaust and filtration beyond baseline HVAC?",
                    "What controls integrations remain unresolved between base building and specialized equipment?",
                ],
            },
            {
                "id": "library_qb_access",
                "driver_tile_id": "library_public_access_security_plus_8",
                "questions": [
                    "How is after-hours public access separated from staff/service circulation?",
                    "Which access-control points are still uncoordinated with operations policy?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "library_rf_structural_basis",
                "flag": "Stack load assumptions are still scenario-level and not layout-backed.",
                "action": "Publish a stack-load matrix tied to shelf plan options and structural bay limits.",
            },
            {
                "id": "library_rf_mep_basis",
                "flag": "Makerspace MEP scope lacks signed authority and operational criteria.",
                "action": "Freeze makerspace equipment list and map each item to mechanical/electrical responsibilities.",
            },
            {
                "id": "library_rf_access_plan",
                "flag": "After-hours access model is unresolved across security and staffing teams.",
                "action": "Run an operations tabletop and lock an approved access-control sequence before GMP.",
            },
        ],
    },
    "civic_courthouse_v1": {
        "version": "v1",
        "profile_id": "civic_courthouse_v1",
        "fastest_change": {
            "headline": "What changes this civic feasibility decision fastest?",
            "drivers": [
                {
                    "id": "courthouse_driver_screening",
                    "tile_id": "courthouse_screening_and_sallyport_plus_12",
                    "label": "Validate screening-lane, sallyport, and intake assumptions.",
                },
                {
                    "id": "courthouse_driver_holding",
                    "tile_id": "courthouse_holding_and_hardening_plus_10",
                    "label": "Validate holding/custody hardening scope assumptions.",
                },
                {
                    "id": "courthouse_driver_hvac",
                    "tile_id": "courthouse_judicial_hvac_control_plus_9",
                    "label": "Validate courtroom and custody-zone HVAC/control separations.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "courthouse_mlw_custody_circulation",
                "driver_tile_id": "courthouse_holding_and_hardening_plus_10",
                "text": "Custody circulation separation is likely understated between holding, courtroom, and public routes.",
                "why": "Late routing corrections trigger structural and security-system redesign.",
            },
            {
                "id": "courthouse_mlw_screening",
                "driver_tile_id": "courthouse_screening_and_sallyport_plus_12",
                "text": "Security-screening throughput assumptions likely rely on optimistic peak-hour operations.",
                "why": "Queue growth drives additional lanes, rework, and electrical/security scope expansion.",
            },
            {
                "id": "courthouse_mlw_control_zones",
                "driver_tile_id": "courthouse_judicial_hvac_control_plus_9",
                "text": "Courtroom, chambers, and custody support zones are modeled with simplified controls segmentation.",
                "why": "Insufficient controls segregation increases commissioning failures and corrective work.",
            },
        ],
        "question_bank": [
            {
                "id": "courthouse_qb_custody",
                "driver_tile_id": "courthouse_holding_and_hardening_plus_10",
                "questions": [
                    "Which custody paths are fully separated from public circulation under all occupancy conditions?",
                    "What unresolved code comments affect holding-cell and transport interfaces?",
                ],
            },
            {
                "id": "courthouse_qb_screening",
                "driver_tile_id": "courthouse_screening_and_sallyport_plus_12",
                "questions": [
                    "What peak-hour screening throughput basis is approved by court operations and security teams?",
                    "Which queue management assumptions remain unverified in the site/entry layout?",
                ],
            },
            {
                "id": "courthouse_qb_hvac",
                "driver_tile_id": "courthouse_judicial_hvac_control_plus_9",
                "questions": [
                    "Where are courtroom acoustics and HVAC controls objectives potentially in conflict?",
                    "Which control-sequence tests are required before substantial completion?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "courthouse_rf_custody_matrix",
                "flag": "Custody/public circulation matrix is incomplete.",
                "action": "Issue an approved circulation matrix with accountable signoff per stakeholder group.",
            },
            {
                "id": "courthouse_rf_screening",
                "flag": "Screening throughput and lane assumptions are not operations-tested.",
                "action": "Run throughput simulation with peak dockets and lock lane count before DD freeze.",
            },
            {
                "id": "courthouse_rf_controls",
                "flag": "Controls segmentation for sensitive zones remains provisional.",
                "action": "Complete courtroom/custody controls sequence review and publish commissioning script set.",
            },
        ],
    },
    "civic_government_building_v1": {
        "version": "v1",
        "profile_id": "civic_government_building_v1",
        "fastest_change": {
            "headline": "What changes this civic feasibility decision fastest?",
            "drivers": [
                {
                    "id": "government_driver_records",
                    "tile_id": "government_records_vault_plus_11",
                    "label": "Validate records-vault loading and archival protection assumptions.",
                },
                {
                    "id": "government_driver_public_counter",
                    "tile_id": "government_public_service_counter_plus_8",
                    "label": "Validate constituent service-counter and lobby throughput assumptions.",
                },
                {
                    "id": "government_driver_chamber",
                    "tile_id": "government_council_av_controls_plus_9",
                    "label": "Validate council-chamber AV and controls integration assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "government_mlw_records_burden",
                "driver_tile_id": "government_records_vault_plus_11",
                "text": "Records-retention burden is likely understated for secure storage, fire rating, and retrieval operations.",
                "why": "Late archival policy enforcement drives structural and enclosure scope growth.",
            },
            {
                "id": "government_mlw_public_interface",
                "driver_tile_id": "government_public_service_counter_plus_8",
                "text": "Constituent service windows and waiting-area assumptions likely miss peak service variability.",
                "why": "Queue and accessibility corrections push finish and circulation redesign.",
            },
            {
                "id": "government_mlw_chamber_controls",
                "driver_tile_id": "government_council_av_controls_plus_9",
                "text": "Council chamber hybrid meeting controls are modeled with minimal interoperability risk.",
                "why": "Integration gaps across AV, IT, and recording systems create expensive late fixes.",
            },
        ],
        "question_bank": [
            {
                "id": "government_qb_records",
                "driver_tile_id": "government_records_vault_plus_11",
                "questions": [
                    "Which records classes require enhanced storage controls beyond baseline assumptions?",
                    "Where is vault capacity still estimated without retention policy volume studies?",
                ],
            },
            {
                "id": "government_qb_counter",
                "driver_tile_id": "government_public_service_counter_plus_8",
                "questions": [
                    "What transaction-volume evidence supports current service-counter quantity assumptions?",
                    "Which accessibility and queue assumptions remain provisional?",
                ],
            },
            {
                "id": "government_qb_chamber",
                "driver_tile_id": "government_council_av_controls_plus_9",
                "questions": [
                    "Which chamber AV requirements are still pending legal/public-records review?",
                    "What commissioning tests prove chamber systems can support hybrid sessions reliably?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "government_rf_records",
                "flag": "Archive/storage basis is not fully reconciled with retention obligations.",
                "action": "Issue an approved retention-to-capacity matrix and lock vault design criteria.",
            },
            {
                "id": "government_rf_public_lobby",
                "flag": "Public service lobby assumptions remain untested under peak-demand scenarios.",
                "action": "Complete a queue/accessibility operations model and update planning factors.",
            },
            {
                "id": "government_rf_chamber",
                "flag": "Council AV/control integration path is incomplete.",
                "action": "Define single-system integration ownership and close open interface items weekly.",
            },
        ],
    },
    "civic_community_center_v1": {
        "version": "v1",
        "profile_id": "civic_community_center_v1",
        "fastest_change": {
            "headline": "What changes this civic feasibility decision fastest?",
            "drivers": [
                {
                    "id": "community_driver_program",
                    "tile_id": "community_multi_program_fitout_plus_10",
                    "label": "Validate multipurpose-room and activity-space program assumptions.",
                },
                {
                    "id": "community_driver_kitchen_gym",
                    "tile_id": "community_kitchen_and_gym_mep_plus_9",
                    "label": "Validate kitchen/gym MEP density and turnover assumptions.",
                },
                {
                    "id": "community_driver_security",
                    "tile_id": "community_afterhours_security_plus_8",
                    "label": "Validate after-hours access/security operations assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "community_mlw_program_overlap",
                "driver_tile_id": "community_multi_program_fitout_plus_10",
                "text": "Shared program spaces likely understate overlap between youth, senior, and event functions.",
                "why": "Program overlap drives partition, storage, and finish rework across multiple phases.",
            },
            {
                "id": "community_mlw_mechanical_turnover",
                "driver_tile_id": "community_kitchen_and_gym_mep_plus_9",
                "text": "Kitchen and gym turnover assumptions likely ignore peak-use ventilation and maintenance windows.",
                "why": "Under-modeled turnover loads increase mechanical balancing and control complexity.",
            },
            {
                "id": "community_mlw_afterhours",
                "driver_tile_id": "community_afterhours_security_plus_8",
                "text": "After-hours supervision and controlled-access scope is treated as stable too early.",
                "why": "Late policy updates can force access-control redesign and staffing adjustments.",
            },
        ],
        "question_bank": [
            {
                "id": "community_qb_program",
                "driver_tile_id": "community_multi_program_fitout_plus_10",
                "questions": [
                    "Which spaces are truly flexible versus function-specific under the approved operations plan?",
                    "What scope elements remain allowance-based pending stakeholder program lock?",
                ],
            },
            {
                "id": "community_qb_mep",
                "driver_tile_id": "community_kitchen_and_gym_mep_plus_9",
                "questions": [
                    "Which high-load events define peak kitchen/gym mechanical demand assumptions?",
                    "What unresolved controls requirements remain for multi-use scheduling?",
                ],
            },
            {
                "id": "community_qb_security",
                "driver_tile_id": "community_afterhours_security_plus_8",
                "questions": [
                    "How are after-hours users segmented from restricted staff/program areas?",
                    "Which access-control responsibilities are still unresolved between operations and IT/security?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "community_rf_program",
                "flag": "Program assumptions remain fluid across user groups.",
                "action": "Freeze a signed shared-use calendar and convert allowances to fixed scope where possible.",
            },
            {
                "id": "community_rf_mep",
                "flag": "Kitchen/gym MEP loads are not tied to approved operational scenarios.",
                "action": "Publish peak-load event assumptions and validate controls strategy with commissioning lead.",
            },
            {
                "id": "community_rf_security",
                "flag": "After-hours access policy is not fully translated into building controls.",
                "action": "Complete an access policy-to-device mapping before design freeze.",
            },
        ],
    },
    "civic_public_safety_v1": {
        "version": "v1",
        "profile_id": "civic_public_safety_v1",
        "fastest_change": {
            "headline": "What changes this civic feasibility decision fastest?",
            "drivers": [
                {
                    "id": "public_safety_driver_dispatch",
                    "tile_id": "public_safety_dispatch_redundancy_plus_12",
                    "label": "Validate dispatch resilience and redundancy assumptions.",
                },
                {
                    "id": "public_safety_driver_bay",
                    "tile_id": "public_safety_apparatus_bay_hardening_plus_11",
                    "label": "Validate apparatus bay hardening and circulation assumptions.",
                },
                {
                    "id": "public_safety_driver_power",
                    "tile_id": "public_safety_emergency_power_plus_10",
                    "label": "Validate emergency-power autonomy and transfer assumptions.",
                },
            ],
        },
        "most_likely_wrong": [
            {
                "id": "public_safety_mlw_dispatch_continuity",
                "driver_tile_id": "public_safety_dispatch_redundancy_plus_12",
                "text": "Dispatch continuity assumptions likely understate failover complexity across radio, CAD, and telephony systems.",
                "why": "Integration failures across redundant pathways can delay operational readiness and increase cost.",
            },
            {
                "id": "public_safety_mlw_bay_flow",
                "driver_tile_id": "public_safety_apparatus_bay_hardening_plus_11",
                "text": "Apparatus bay circulation and turnout assumptions likely ignore concurrent vehicle movement conflicts.",
                "why": "Late flow corrections can require structural rework and door/equipment relocations.",
            },
            {
                "id": "public_safety_mlw_power_autonomy",
                "driver_tile_id": "public_safety_emergency_power_plus_10",
                "text": "Emergency-power duration assumptions are treated as fixed despite uncertain outage and fuel logistics conditions.",
                "why": "Autonomy shortfalls force late generator, storage, or controls upgrades.",
            },
        ],
        "question_bank": [
            {
                "id": "public_safety_qb_dispatch",
                "driver_tile_id": "public_safety_dispatch_redundancy_plus_12",
                "questions": [
                    "Which dispatch subsystems have validated failover tests witnessed by operations leadership?",
                    "What single points of failure remain unresolved in dispatch backbone architecture?",
                ],
            },
            {
                "id": "public_safety_qb_bay",
                "driver_tile_id": "public_safety_apparatus_bay_hardening_plus_11",
                "questions": [
                    "What turnout-time assumptions drive current bay layout and equipment staging decisions?",
                    "Which apparatus circulation constraints are still unresolved during simultaneous response events?",
                ],
            },
            {
                "id": "public_safety_qb_power",
                "driver_tile_id": "public_safety_emergency_power_plus_10",
                "questions": [
                    "What outage-duration and fuel-resupply assumptions underpin current generator sizing?",
                    "Which transfer-test protocols are required before operational acceptance?",
                ],
            },
        ],
        "red_flags_actions": [
            {
                "id": "public_safety_rf_dispatch",
                "flag": "Dispatch redundancy is not yet proven through integrated failover testing.",
                "action": "Complete end-to-end dispatch failover rehearsal with documented pass/fail outcomes.",
            },
            {
                "id": "public_safety_rf_bay",
                "flag": "Bay circulation model remains unverified for concurrent dispatch conditions.",
                "action": "Run apparatus movement simulation and resolve conflict points before IFC release.",
            },
            {
                "id": "public_safety_rf_power",
                "flag": "Emergency-power autonomy assumptions lack validated fuel and transfer evidence.",
                "action": "Lock autonomy basis and execute witnessed blackstart/transfer tests before turnover.",
            },
        ],
    },
}


DEALSHIELD_CONTENT_DEFAULTS = {
    "community_center": "civic_community_center_v1",
    "courthouse": "civic_courthouse_v1",
    "government_building": "civic_government_building_v1",
    "library": "civic_library_v1",
    "public_safety": "civic_public_safety_v1",
}
