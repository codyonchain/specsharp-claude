"""DealShield content profiles for specialty subtypes."""

DEALSHIELD_CONTENT_PROFILES = {
    "specialty_data_center_v1": {
        "profile_id": "specialty_data_center_v1",
        "fastest_change": {
            "drivers": [
                {
                    "tile_id": "power_train_redundancy_rework_plus_15",
                    "label": "Power train redundancy scope",
                },
                {
                    "tile_id": "cooling_plant_rebalance_plus_12",
                    "label": "Cooling plant rebalance",
                },
                {
                    "tile_id": "commissioning_labor_plus_8",
                    "label": "Integrated systems commissioning",
                },
            ]
        },
        "decision_insurance": {"severity_thresholds_pct": {"high": 9.0, "med": 4.0}},
        "most_likely_wrong": [
            {
                "id": "dc_mlw_1",
                "driver_tile_id": "power_train_redundancy_rework_plus_15",
                "text": "N+1 assumptions likely understate concurrent maintainability failures at generator-paralleling handoff.",
                "why": "Single-point rework around switchgear and controls amplifies downtime risk and capex shocks.",
            },
            {
                "id": "dc_mlw_2",
                "driver_tile_id": "cooling_plant_rebalance_plus_12",
                "text": "Cooling model likely assumes steady-state load and misses shoulder-season instability during partial occupancy.",
                "why": "Control-sequence retuning often appears only under staged rack-density activation.",
            },
            {
                "id": "dc_mlw_3",
                "driver_tile_id": "commissioning_labor_plus_8",
                "text": "Commissioning duration likely optimistic for integrated BMS, EPMS, and low-voltage turnover.",
                "why": "Cross-vendor interface defects are discovered late and drive expensive retest windows.",
            },
        ],
        "question_bank": [
            {
                "id": "dc_q_1",
                "driver_tile_id": "power_train_redundancy_rework_plus_15",
                "label": "Power train reliability",
                "questions": [
                    "What was the last witnessed full-failure transfer duration under load, and who signed it?",
                    "How many maintenance operations require bypassing intended redundancy paths?",
                ],
            },
            {
                "id": "dc_q_2",
                "driver_tile_id": "cooling_plant_rebalance_plus_12",
                "label": "Cooling sequence risk",
                "questions": [
                    "Which control sequences are validated for partial IT load and shoulder-season operation?",
                    "Is condenser-water approach modeled at local design wet-bulb, not catalog conditions?",
                ],
            },
            {
                "id": "dc_q_3",
                "driver_tile_id": "commissioning_labor_plus_8",
                "label": "Commissioning quality",
                "questions": [
                    "Do integrated systems tests include utility-event simulation and black-start procedures?",
                    "How many unresolved commissioning issues are still open by severity tier?",
                ],
            },
        ],
        "red_flags": [
            "Single utility feed accepted without documented mitigation path.",
            "Generator fuel autonomy below contracted uptime commitments.",
            "BMS/EPMS handoff matrix missing accountable owners.",
        ],
        "actions": [
            "Re-run reliability model with explicit concurrent-maintainability outages.",
            "Issue staged-load commissioning plan with pass/fail criteria per interface.",
            "Bind turnover to closed critical issues and witnessed failover evidence.",
        ],
    },
    "specialty_laboratory_v1": {
        "profile_id": "specialty_laboratory_v1",
        "fastest_change": {
            "drivers": [
                {
                    "tile_id": "validation_air_change_rebalance_plus_12",
                    "label": "Air-change validation",
                },
                {
                    "tile_id": "cleanroom_recertification_plus_9",
                    "label": "Cleanroom recertification",
                },
                {
                    "tile_id": "casework_coordination_plus_8",
                    "label": "Casework and utility coordination",
                },
            ]
        },
        "decision_insurance": {"severity_thresholds_pct": {"high": 8.5, "med": 3.8}},
        "most_likely_wrong": [
            {
                "id": "lab_mlw_1",
                "driver_tile_id": "validation_air_change_rebalance_plus_12",
                "text": "Air-change targets likely assume ideal balancing conditions not reflected in final occupancy mode.",
                "why": "Minor zoning mismatches push repeat TAB and validation scope.",
            },
            {
                "id": "lab_mlw_2",
                "driver_tile_id": "cleanroom_recertification_plus_9",
                "text": "Recertification calendar is likely too aggressive for procurement and witness availability.",
                "why": "Critical certification dependencies slip when specialty vendors are not contractually aligned.",
            },
            {
                "id": "lab_mlw_3",
                "driver_tile_id": "casework_coordination_plus_8",
                "text": "Late utility conflicts around benches and hoods likely remain hidden in coordinated drawings.",
                "why": "Small clashes create sequencing rework across multiple trades.",
            },
        ],
        "question_bank": [
            {
                "id": "lab_q_1",
                "driver_tile_id": "validation_air_change_rebalance_plus_12",
                "label": "Validation readiness",
                "questions": [
                    "Which rooms have witness-ready validation scripts and approved acceptance bands?",
                    "Were pressure relationships tested with realistic door-cycle behavior?",
                ],
            },
            {
                "id": "lab_q_2",
                "driver_tile_id": "cleanroom_recertification_plus_9",
                "label": "Certification schedule",
                "questions": [
                    "Does the schedule include contingency for failed particle counts and re-clean cycles?",
                    "Are certifiers under contract with guaranteed response windows?",
                ],
            },
        ],
        "red_flags": [
            "No documented fallback when certifier availability slips.",
            "Validation scripts not mapped to latest room-function matrix.",
            "Long-lead controls hardware not tied to test readiness gates.",
        ],
        "actions": [
            "Lock a room-by-room validation dependency map with owner signoff.",
            "Add contractual response SLAs for certifiers and TAB vendors.",
            "Run pre-functional tests before turnover to compress retest cycles.",
        ],
    },
    "specialty_self_storage_v1": {
        "profile_id": "specialty_self_storage_v1",
        "fastest_change": {
            "drivers": [
                {
                    "tile_id": "access_control_and_surveillance_plus_10",
                    "label": "Access control and surveillance",
                },
                {
                    "tile_id": "climate_zone_rework_plus_8",
                    "label": "Climate-zone mechanical tuning",
                },
                {
                    "tile_id": "site_and_paving_plus_6",
                    "label": "Sitework and paving scope",
                },
            ]
        },
        "decision_insurance": {"severity_thresholds_pct": {"high": 8.0, "med": 3.5}},
        "most_likely_wrong": [
            {
                "id": "ss_mlw_1",
                "driver_tile_id": "access_control_and_surveillance_plus_10",
                "text": "Security package likely underestimates camera storage and gate-controller redundancy requirements.",
                "why": "Late owner IT/security standards typically expand low-voltage scope.",
            },
            {
                "id": "ss_mlw_2",
                "driver_tile_id": "climate_zone_rework_plus_8",
                "text": "Climate-controlled unit mix likely overstates stabilized rent premium in submarket comps.",
                "why": "Absorption can lag where premium units are over-supplied.",
            },
        ],
        "question_bank": [
            {
                "id": "ss_q_1",
                "driver_tile_id": "access_control_and_surveillance_plus_10",
                "label": "Security reliability",
                "questions": [
                    "Is uptime defined at the gate level, or at the full customer journey including kiosks and locks?",
                    "What is the fail-open/fail-closed policy and operational fallback on controller loss?",
                ],
            },
            {
                "id": "ss_q_2",
                "driver_tile_id": "climate_zone_rework_plus_8",
                "label": "Lease-up assumptions",
                "questions": [
                    "What percentage of pro forma NOI is dependent on climate-controlled premiums?",
                    "How fast can unit mix be rebalanced if premium demand underperforms?",
                ],
            },
        ],
        "red_flags": [
            "Security vendor scope excludes central storage retention policy.",
            "Lease-up schedule ignores competing facilities opening within 12 months.",
            "Paving and stormwater allowances are still conceptual.",
        ],
        "actions": [
            "Re-price security scope against final retention and monitoring standards.",
            "Stress-test lease-up with conservative demand and churn assumptions.",
            "Advance civil packages to permit-level quantities before GMP lock.",
        ],
    },
    "specialty_car_dealership_v1": {
        "profile_id": "specialty_car_dealership_v1",
        "fastest_change": {
            "drivers": [
                {
                    "tile_id": "service_bay_process_mep_plus_11",
                    "label": "Service bay process MEP",
                },
                {
                    "tile_id": "showroom_finish_refresh_plus_9",
                    "label": "Showroom finish fit-out",
                },
                {
                    "tile_id": "yard_and_delivery_regrade_plus_6",
                    "label": "Yard and delivery logistics",
                },
            ]
        },
        "decision_insurance": {"severity_thresholds_pct": {"high": 8.2, "med": 3.6}},
        "most_likely_wrong": [
            {
                "id": "cd_mlw_1",
                "driver_tile_id": "service_bay_process_mep_plus_11",
                "text": "Service-bay throughput likely assumes optimistic bay utilization with no technician ramp lag.",
                "why": "Understaffed openings suppress service-margin stabilization.",
            },
            {
                "id": "cd_mlw_2",
                "driver_tile_id": "showroom_finish_refresh_plus_9",
                "text": "OEM image-program deltas likely understated in finish carry.",
                "why": "Late branding directives force unplanned replacement cycles.",
            },
        ],
        "question_bank": [
            {
                "id": "cd_q_1",
                "driver_tile_id": "service_bay_process_mep_plus_11",
                "label": "Service absorption",
                "questions": [
                    "What is the required technician headcount by month to hit service revenue assumptions?",
                    "Are diagnostic and EV-service electrical requirements fully coordinated with equipment submittals?",
                ],
            },
            {
                "id": "cd_q_2",
                "driver_tile_id": "showroom_finish_refresh_plus_9",
                "label": "Brand compliance",
                "questions": [
                    "Which finish packages remain provisional pending OEM approval?",
                    "How is late OEM guidance funded after GMP?",
                ],
            },
        ],
        "red_flags": [
            "No contingency line for OEM branding late-change directives.",
            "Service-bay equipment utilities are coordinated only at schematic level.",
            "Delivery-yard flow conflicts unresolved for peak truck windows.",
        ],
        "actions": [
            "Freeze OEM compliance checklist with change-control cutoff dates.",
            "Add a service-ramp staffing covenant to underwriting assumptions.",
            "Simulate delivery and customer traffic to validate site logistics.",
        ],
    },
    "specialty_broadcast_facility_v1": {
        "profile_id": "specialty_broadcast_facility_v1",
        "fastest_change": {
            "drivers": [
                {
                    "tile_id": "signal_chain_and_power_quality_plus_12",
                    "label": "Signal chain and clean power",
                },
                {
                    "tile_id": "acoustic_isolation_rework_plus_10",
                    "label": "Acoustic isolation package",
                },
                {
                    "tile_id": "studio_fitout_plus_7",
                    "label": "Studio fit-out package",
                },
            ]
        },
        "decision_insurance": {"severity_thresholds_pct": {"high": 8.4, "med": 3.7}},
        "most_likely_wrong": [
            {
                "id": "bf_mlw_1",
                "driver_tile_id": "signal_chain_and_power_quality_plus_12",
                "text": "Clean-power assumptions likely ignore harmonics and grounding remediation after equipment commissioning.",
                "why": "Signal degradation remediation is expensive and schedule-sensitive.",
            },
            {
                "id": "bf_mlw_2",
                "driver_tile_id": "acoustic_isolation_rework_plus_10",
                "text": "Acoustic envelope performance likely overstates field conditions versus design intent.",
                "why": "Minor envelope discontinuities can invalidate isolation targets.",
            },
        ],
        "question_bank": [
            {
                "id": "bf_q_1",
                "driver_tile_id": "signal_chain_and_power_quality_plus_12",
                "label": "Signal integrity",
                "questions": [
                    "Were power-quality measurements captured with production-equivalent load profiles?",
                    "Do grounding and bonding details include independent verification signoff?",
                ],
            },
            {
                "id": "bf_q_2",
                "driver_tile_id": "acoustic_isolation_rework_plus_10",
                "label": "Acoustic performance",
                "questions": [
                    "Which assemblies are below target STC/NC in mockup tests?",
                    "Is there a funded mitigation plan for failed acoustic tests?",
                ],
            },
        ],
        "red_flags": [
            "No witnessed power-quality acceptance criteria in turnover package.",
            "Acoustic mockups are incomplete for final partition stackups.",
            "Signal-path redundancy not validated end-to-end.",
        ],
        "actions": [
            "Run integrated signal-chain commissioning before final punch.",
            "Expand acoustic mockup program to all critical studio boundaries.",
            "Link final acceptance to documented clean-power and redundancy tests.",
        ],
    },
}

DEALSHIELD_CONTENT_DEFAULTS = {
    "data_center": "specialty_data_center_v1",
    "laboratory": "specialty_laboratory_v1",
    "self_storage": "specialty_self_storage_v1",
    "car_dealership": "specialty_car_dealership_v1",
    "broadcast_facility": "specialty_broadcast_facility_v1",
}
