"""Scope item profiles for educational subtypes."""

from typing import Dict, List, Tuple


def _item(key: str, label: str, share: float) -> Dict[str, object]:
    return {
        "key": key,
        "label": label,
        "unit": "SF",
        "quantity_rule": {"type": "sf", "params": {}},
        "allocation": {"type": "share_of_trade", "share": float(share)},
    }


def _trade_profile(trade_key: str, trade_label: str, rows: List[Tuple[str, str, float]]) -> Dict[str, object]:
    return {
        "trade_key": trade_key,
        "trade_label": trade_label,
        "items": [_item(key, label, share) for key, label, share in rows],
    }


SCOPE_ITEM_PROFILES = {
    "educational_elementary_school_structural_v1": {
        "profile_id": "educational_elementary_school_structural_v1",
        "trade_profiles": [
            _trade_profile("structural", "Structural", [
                ("elem_structural_classroom_wing", "Classroom wing framing and slab package", 0.40),
                ("elem_structural_multiuse_block", "Multi-use block and support bay framing", 0.35),
                ("elem_structural_canopy_and_entries", "Entry canopies and covered circulation", 0.25),
            ]),
            _trade_profile("mechanical", "Mechanical", [
                ("elem_mech_classroom_ventilation", "Classroom ventilation and outside-air controls", 0.40),
                ("elem_mech_gym_and_cafeteria_hvac", "Gym/cafeteria HVAC zoning", 0.35),
                ("elem_mech_support_and_storage_exhaust", "Support-area exhaust and balancing", 0.25),
            ]),
            _trade_profile("electrical", "Electrical", [
                ("elem_elec_learning_power", "Instructional power and branch devices", 0.40),
                ("elem_elec_lighting_and_controls", "Lighting controls and occupancy sensing", 0.35),
                ("elem_elec_security_and_communications", "Security, PA, and low-voltage backbone", 0.25),
            ]),
            _trade_profile("plumbing", "Plumbing", [
                ("elem_plumb_restroom_groups", "Student restroom groups and fixtures", 0.40),
                ("elem_plumb_cafeteria_and_kitchen", "Cafeteria and kitchen plumbing services", 0.35),
                ("elem_plumb_domestic_hot_cold_distribution", "Domestic hot/cold distribution loops", 0.25),
            ]),
            _trade_profile("finishes", "Finishes", [
                ("elem_finish_classroom_package", "Classroom finish package", 0.40),
                ("elem_finish_shared_spaces", "Shared spaces and corridor finishes", 0.35),
                ("elem_finish_library_and_admin", "Library and admin area finish upgrades", 0.25),
            ]),
        ],
    },
    "educational_middle_school_structural_v1": {
        "profile_id": "educational_middle_school_structural_v1",
        "trade_profiles": [
            _trade_profile("structural", "Structural", [
                ("mid_structural_learning_blocks", "Learning blocks and commons framing", 0.40),
                ("mid_structural_media_lab_wing", "Media/lab wing structural package", 0.35),
                ("mid_structural_covered_activity_links", "Covered activity links and connector zones", 0.25),
            ]),
            _trade_profile("mechanical", "Mechanical", [
                ("mid_mech_learning_hvac_zones", "Learning-zone HVAC with schedule controls", 0.40),
                ("mid_mech_lab_exhaust_and_makeup", "Lab exhaust and makeup-air package", 0.35),
                ("mid_mech_auditorium_and_gym_distribution", "Auditorium/gym distribution and balancing", 0.25),
            ]),
            _trade_profile("electrical", "Electrical", [
                ("mid_elec_stem_and_media_power", "STEM/media power and dedicated circuits", 0.40),
                ("mid_elec_instructional_lighting_controls", "Instructional lighting and control backbone", 0.35),
                ("mid_elec_safety_comms_and_access", "Safety communications and access controls", 0.25),
            ]),
            _trade_profile("plumbing", "Plumbing", [
                ("mid_plumb_restroom_and_locker_zones", "Restroom and locker-zone rough-in", 0.40),
                ("mid_plumb_science_lab_services", "Science lab sinks and service piping", 0.35),
                ("mid_plumb_domestic_recirc_and_support", "Domestic recirculation and support spaces", 0.25),
            ]),
            _trade_profile("finishes", "Finishes", [
                ("mid_finish_classroom_and_corridor", "Classroom/corridor finish package", 0.40),
                ("mid_finish_labs_and_media_centers", "Lab and media-center finishes", 0.35),
                ("mid_finish_auditorium_and_activity", "Auditorium/activity-area finish upgrades", 0.25),
            ]),
        ],
    },
    "educational_high_school_structural_v1": {
        "profile_id": "educational_high_school_structural_v1",
        "trade_profiles": [
            _trade_profile("structural", "Structural", [
                ("hs_structural_academic_core", "Academic core framing and floor systems", 0.30),
                ("hs_structural_stadium_support", "Stadium and field-house structural support", 0.27),
                ("hs_structural_performing_arts_mass", "Performing-arts volume and rigging supports", 0.23),
                ("hs_structural_shop_and_service_blocks", "Shop/service block framing and slab support", 0.20),
            ]),
            _trade_profile("mechanical", "Mechanical", [
                ("hs_mech_academic_hvac_zones", "Academic wing HVAC zoning", 0.30),
                ("hs_mech_stem_lab_ventilation", "STEM lab ventilation and pressurization", 0.27),
                ("hs_mech_athletics_conditioning", "Athletics conditioning and dehumidification", 0.23),
                ("hs_mech_assembly_and_stage_airside", "Assembly/stage airside package", 0.20),
            ]),
            _trade_profile("electrical", "Electrical", [
                ("hs_elec_instructional_power_distribution", "Instructional power distribution", 0.30),
                ("hs_elec_stage_and_av_backbone", "Stage and AV electrical backbone", 0.27),
                ("hs_elec_athletics_lighting_controls", "Athletics lighting and controls", 0.23),
                ("hs_elec_security_firealarm_and_network", "Security/fire alarm/network integration", 0.20),
            ]),
            _trade_profile("plumbing", "Plumbing", [
                ("hs_plumb_restroom_and_locker_cores", "Restroom and locker cores", 0.30),
                ("hs_plumb_lab_and_cte_service_piping", "Lab and CTE service piping", 0.27),
                ("hs_plumb_kitchen_and_cafeteria_services", "Kitchen/cafeteria plumbing services", 0.23),
                ("hs_plumb_domestic_and_storm_interfaces", "Domestic/storm interfaces and trim", 0.20),
            ]),
            _trade_profile("finishes", "Finishes", [
                ("hs_finish_academic_interiors", "Academic interior finish package", 0.30),
                ("hs_finish_performing_arts_interiors", "Performing-arts interior and acoustic finishes", 0.27),
                ("hs_finish_athletics_support_interiors", "Athletics support interior finishes", 0.23),
                ("hs_finish_media_and_admin_program", "Media/admin finishes and specialty casework", 0.20),
            ]),
        ],
    },
    "educational_university_structural_v1": {
        "profile_id": "educational_university_structural_v1",
        "trade_profiles": [
            _trade_profile("structural", "Structural", [
                ("uni_structural_research_block", "Research block framing and vibration controls", 0.30),
                ("uni_structural_lecture_hall_volume", "Lecture-hall volume framing", 0.27),
                ("uni_structural_vertical_circulation_core", "Vertical circulation core and transfer zones", 0.23),
                ("uni_structural_specialty_support_levels", "Specialty support levels and roof framing", 0.20),
            ]),
            _trade_profile("mechanical", "Mechanical", [
                ("uni_mech_research_ventilation_core", "Research ventilation core and exhaust controls", 0.24),
                ("uni_mech_lab_makeup_air_systems", "Lab makeup-air and heat-recovery package", 0.22),
                ("uni_mech_controls_and_commissioning_points", "Building controls and commissioning points", 0.20),
                ("uni_mech_lecture_and_student_space_hvac", "Lecture/student-space HVAC zoning", 0.18),
                ("uni_mech_critical_support_and_redundancy", "Critical support redundancy loops", 0.16),
            ]),
            _trade_profile("electrical", "Electrical", [
                ("uni_elec_research_power_distribution", "Research power distribution and isolation", 0.24),
                ("uni_elec_lab_critical_branching", "Lab critical branching and panel strategy", 0.22),
                ("uni_elec_controls_and_low_voltage_backbone", "Controls and low-voltage backbone", 0.20),
                ("uni_elec_lecture_hall_av_and_lighting", "Lecture-hall AV and lighting controls", 0.18),
                ("uni_elec_emergency_and_backup_interfaces", "Emergency and backup power interfaces", 0.16),
            ]),
            _trade_profile("plumbing", "Plumbing", [
                ("uni_plumb_lab_process_and_domestic", "Lab process/domestic piping package", 0.30),
                ("uni_plumb_restroom_and_core_services", "Restroom and core service plumbing", 0.27),
                ("uni_plumb_student_and_foodservice_support", "Student/foodservice support plumbing", 0.23),
                ("uni_plumb_special_waste_and_treatment", "Special waste/treatment tie-ins", 0.20),
            ]),
            _trade_profile("finishes", "Finishes", [
                ("uni_finish_research_and_technical_spaces", "Research/technical space finishes", 0.30),
                ("uni_finish_lecture_and_classroom_spaces", "Lecture/classroom finish package", 0.27),
                ("uni_finish_student_center_common_areas", "Student-center/common-area finishes", 0.23),
                ("uni_finish_library_and_admin_suites", "Library/admin suite finishes", 0.20),
            ]),
        ],
    },
    "educational_community_college_structural_v1": {
        "profile_id": "educational_community_college_structural_v1",
        "trade_profiles": [
            _trade_profile("structural", "Structural", [
                ("cc_structural_instructional_blocks", "Instructional block framing", 0.40),
                ("cc_structural_vocational_lab_bays", "Vocational lab bay structural package", 0.35),
                ("cc_structural_student_services_and_entries", "Student services and entry structural scope", 0.25),
            ]),
            _trade_profile("mechanical", "Mechanical", [
                ("cc_mech_instructional_hvac_zones", "Instructional HVAC zoning and controls", 0.40),
                ("cc_mech_vocational_lab_exhaust", "Vocational lab exhaust and makeup systems", 0.35),
                ("cc_mech_student_services_distribution", "Student-services air distribution and balancing", 0.25),
            ]),
            _trade_profile("electrical", "Electrical", [
                ("cc_elec_instructional_power_network", "Instructional power and network distribution", 0.40),
                ("cc_elec_vocational_equipment_branching", "Vocational equipment branching and controls", 0.35),
                ("cc_elec_security_access_and_firealarm", "Security/access/fire alarm integration", 0.25),
            ]),
            _trade_profile("plumbing", "Plumbing", [
                ("cc_plumb_restroom_and_core_services", "Restroom and core plumbing services", 0.40),
                ("cc_plumb_vocational_labs_and_shop_sinks", "Vocational lab/shop sink plumbing package", 0.35),
                ("cc_plumb_breakroom_and_support_services", "Breakroom/support services and recirculation", 0.25),
            ]),
            _trade_profile("finishes", "Finishes", [
                ("cc_finish_instructional_interiors", "Instructional interior finish package", 0.40),
                ("cc_finish_vocational_training_spaces", "Vocational training-space durability finishes", 0.35),
                ("cc_finish_student_services_and_admin", "Student services/admin finishes", 0.25),
            ]),
        ],
    },
}


SCOPE_ITEM_DEFAULTS = {
    "elementary_school": "educational_elementary_school_structural_v1",
    "middle_school": "educational_middle_school_structural_v1",
    "high_school": "educational_high_school_structural_v1",
    "university": "educational_university_structural_v1",
    "community_college": "educational_community_college_structural_v1",
}
