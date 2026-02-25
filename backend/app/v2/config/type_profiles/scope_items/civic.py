"""Scope item profiles for civic subtypes."""

SCOPE_ITEM_DEFAULTS = {
    "default_profile_by_subtype": {
        "community_center": "civic_community_center_structural_v1",
        "courthouse": "civic_courthouse_structural_v1",
        "government_building": "civic_government_building_structural_v1",
        "library": "civic_library_structural_v1",
        "public_safety": "civic_public_safety_structural_v1",
    },
}


SCOPE_ITEM_PROFILES = {
    "civic_library_structural_v1": {
        "profile_id": "civic_library_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "library_stack_bay_reinforcement",
                        "label": "Stack-Bay Reinforcement",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.42},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "library_long_span_reading_room_structure",
                        "label": "Long-Span Reading Room Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "library_archive_core_and_roof_support",
                        "label": "Archive Core and Roof Support",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.25},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "library_makerspace_exhaust_and_makeup_air",
                        "label": "Makerspace Exhaust and Makeup Air",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.37},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "library_reading_room_thermal_zoning",
                        "label": "Reading Room Thermal Zoning",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "library_collection_preservation_humidity_control",
                        "label": "Collection Preservation Humidity Control",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.29},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "library_daylighting_and_stack_lighting_controls",
                        "label": "Daylighting and Stack Lighting Controls",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "library_public_it_and_wifi_backbone",
                        "label": "Public IT and Wi-Fi Backbone",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "library_access_control_and_afterhours_monitoring",
                        "label": "Access Control and After-Hours Monitoring",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "library_restroom_groups_and_accessibility",
                        "label": "Restroom Groups and Accessibility",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 14000.0, "minimum": 1},
                        },
                    },
                    {
                        "key": "library_makerspace_wet_utility_distribution",
                        "label": "Makerspace Wet Utility Distribution",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "library_domestic_and_storm_piping_allowance",
                        "label": "Domestic and Storm Piping Allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "library_acoustic_reading_room_finishes",
                        "label": "Acoustic Reading Room Finishes",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "library_public_lobby_and_service_desk_millwork",
                        "label": "Public Lobby and Service Desk Millwork",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "library_makerspace_durable_surface_package",
                        "label": "Makerspace Durable Surface Package",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
        ],
    },
    "civic_courthouse_structural_v1": {
        "profile_id": "civic_courthouse_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "courthouse_holding_and_sallyport_structure",
                        "label": "Holding and Sallyport Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.41},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "courthouse_courtroom_long_span_framing",
                        "label": "Courtroom Long-Span Framing",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "courthouse_secure_vertical_core_hardening",
                        "label": "Secure Vertical Core Hardening",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.25},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "courthouse_courtroom_hvac_zone_separation",
                        "label": "Courtroom HVAC Zone Separation",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_holding_area_ventilation_controls",
                        "label": "Holding Area Ventilation Controls",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_judicial_chambers_environmental_conditioning",
                        "label": "Judicial Chambers Environmental Conditioning",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.29},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "courthouse_magnetometer_and_screening_power",
                        "label": "Magnetometer and Screening Power",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_evidence_and_custody_security_systems",
                        "label": "Evidence and Custody Security Systems",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_courtroom_av_and_recording",
                        "label": "Courtroom AV and Recording",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "courthouse_public_and_juror_restroom_groups",
                        "label": "Public and Juror Restroom Groups",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.39},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 13000.0, "minimum": 2},
                        },
                    },
                    {
                        "key": "courthouse_holding_cell_plumbing_allowances",
                        "label": "Holding Cell Plumbing Allowances",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_domestic_and_storm_systems",
                        "label": "Domestic and Storm Systems",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "courthouse_ballistic_glazing_and_secure_partitions",
                        "label": "Ballistic Glazing and Secure Partitions",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "courthouse_courtroom_finish_and_millwork",
                        "label": "Courtroom Finish and Millwork",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "courthouse_judicial_chambers_finish_package",
                        "label": "Judicial Chambers Finish Package",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
        ],
    },
    "civic_government_building_structural_v1": {
        "profile_id": "civic_government_building_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "government_records_vault_structure",
                        "label": "Records Vault Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.40},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "government_public_lobby_and_counter_structure",
                        "label": "Public Lobby and Counter Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "government_council_chamber_support_framing",
                        "label": "Council Chamber Support Framing",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.25},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "government_records_archive_environmental_controls",
                        "label": "Archive Environmental Controls",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "government_public_lobby_ventilation_distribution",
                        "label": "Public Lobby Ventilation Distribution",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "government_council_chamber_hvac_controls",
                        "label": "Council Chamber HVAC Controls",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "government_service_counter_power_and_data",
                        "label": "Service Counter Power and Data",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "government_council_chamber_av_stack",
                        "label": "Council Chamber AV Stack",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "government_secure_records_access_and_monitoring",
                        "label": "Secure Records Access and Monitoring",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "government_public_restroom_fixtures",
                        "label": "Public Restroom Fixtures",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 15000.0, "minimum": 1},
                        },
                    },
                    {
                        "key": "government_staff_core_plumbing_distribution",
                        "label": "Staff Core Plumbing Distribution",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "government_domestic_and_storm_infrastructure",
                        "label": "Domestic and Storm Infrastructure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "government_public_lobby_durable_finishes",
                        "label": "Public Lobby Durable Finishes",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "government_service_counter_casework_package",
                        "label": "Service Counter Casework Package",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "government_council_chamber_finish_and_acoustics",
                        "label": "Council Chamber Finish and Acoustics",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
        ],
    },
    "civic_community_center_structural_v1": {
        "profile_id": "civic_community_center_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "community_multiuse_hall_structure",
                        "label": "Multiuse Hall Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.40},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "community_gym_and_activity_zone_support",
                        "label": "Gym and Activity Zone Support",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "community_pavilion_and_site_structure",
                        "label": "Pavilion and Site Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.25},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "community_gym_ventilation_and_dehumidification",
                        "label": "Gym Ventilation and Dehumidification",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "community_kitchen_exhaust_and_makeup_air",
                        "label": "Kitchen Exhaust and Makeup Air",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "community_shared_program_zone_controls",
                        "label": "Shared Program Zone Controls",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "community_event_lighting_and_power_distribution",
                        "label": "Event Lighting and Power Distribution",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "community_afterhours_access_and_monitoring",
                        "label": "After-Hours Access and Monitoring",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "community_it_low_voltage_for_multiuse_programs",
                        "label": "IT Low Voltage for Multiuse Programs",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "community_public_restroom_and_locker_groups",
                        "label": "Public Restroom and Locker Groups",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.39},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 12000.0, "minimum": 1},
                        },
                    },
                    {
                        "key": "community_kitchen_plumbing_core",
                        "label": "Kitchen Plumbing Core",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "community_domestic_and_site_storm_piping",
                        "label": "Domestic and Site Storm Piping",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "community_multiuse_room_finish_durability_package",
                        "label": "Multiuse Room Finish Durability Package",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "community_gym_floor_and_wall_systems",
                        "label": "Gym Floor and Wall Systems",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "community_lobby_and_program_support_casework",
                        "label": "Lobby and Program Support Casework",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
        ],
    },
    "civic_public_safety_structural_v1": {
        "profile_id": "civic_public_safety_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "public_safety_apparatus_bay_reinforced_frame",
                        "label": "Apparatus Bay Reinforced Frame",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.41},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "public_safety_emergency_operations_hardening",
                        "label": "Emergency Operations Hardening",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "public_safety_rapid_turnout_support_structure",
                        "label": "Rapid Turnout Support Structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.25},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "public_safety_apparatus_exhaust_capture_system",
                        "label": "Apparatus Exhaust Capture System",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.37},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_dispatch_zone_hvac_controls",
                        "label": "Dispatch Zone HVAC Controls",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_emergency_power_plant_mechanical",
                        "label": "Emergency Power Plant Mechanical",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "public_safety_dispatch_and_radio_backbone",
                        "label": "Dispatch and Radio Backbone",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_emergency_power_distribution_and_ats",
                        "label": "Emergency Power Distribution and ATS",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_secure_access_and_perimeter_monitoring",
                        "label": "Secure Access and Perimeter Monitoring",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "public_safety_restroom_and_decon_groups",
                        "label": "Restroom and Decon Groups",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 11000.0, "minimum": 1},
                        },
                    },
                    {
                        "key": "public_safety_apparatus_bay_trench_and_washdown",
                        "label": "Apparatus Bay Trench and Washdown",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_domestic_and_site_storm_network",
                        "label": "Domestic and Site Storm Network",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "public_safety_high_durability_interior_package",
                        "label": "High-Durability Interior Package",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "public_safety_dispatch_console_and_support_casework",
                        "label": "Dispatch Console and Support Casework",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "public_safety_apparatus_ready_room_finishes",
                        "label": "Apparatus Ready Room Finishes",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.31},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
        ],
    },
}
