"""Scope item profiles for specialty subtypes."""

SCOPE_ITEM_PROFILES = {
    "specialty_data_center_structural_v1": {
        "profile_id": "specialty_data_center_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "raised_floor_and_cable_trench",
                        "label": "Raised Floor + Cable Trench",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.56},
                    },
                    {
                        "key": "heavy_roof_and_support_steel",
                        "label": "Heavy Roof + Support Steel",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.44},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "central_plant_chillers",
                        "label": "Central Plant Chillers",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.64},
                    },
                    {
                        "key": "aisle_containment_and_controls",
                        "label": "Aisle Containment + Controls",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "ups_switchgear_and_distribution",
                        "label": "UPS, Switchgear + Distribution",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.66},
                    },
                    {
                        "key": "generator_paralleling_and_fuel_controls",
                        "label": "Generator Paralleling + Fuel Controls",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "process_water_and_leak_detection",
                        "label": "Process Water + Leak Detection",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.68},
                    },
                    {
                        "key": "sanitary_domestic_and_trenching",
                        "label": "Sanitary / Domestic + Trenching",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.32},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "white_space_envelope",
                        "label": "White Space Envelope",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.58},
                    },
                    {
                        "key": "noc_and_support_areas",
                        "label": "NOC + Support Areas",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.42},
                    },
                ],
            },
        ],
    },
    "specialty_laboratory_structural_v1": {
        "profile_id": "specialty_laboratory_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "vibration_controlled_slabs",
                        "label": "Vibration-Controlled Slabs",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.52},
                    },
                    {
                        "key": "framing_for_fume_hood_spans",
                        "label": "Framing for Fume-Hood Spans",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.48},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "air_change_and_pressure_cascade",
                        "label": "Air Change + Pressure Cascade",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.63},
                    },
                    {
                        "key": "exhaust_scrubbers_and_recovery",
                        "label": "Exhaust Scrubbers + Energy Recovery",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.37},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "critical_panels_and_lab_power",
                        "label": "Critical Panels + Lab Power",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.57},
                    },
                    {
                        "key": "instrumentation_and_controls_backbone",
                        "label": "Instrumentation + Controls Backbone",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.43},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "process_gases_and_lab_waste",
                        "label": "Process Gases + Lab Waste",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.64},
                    },
                    {
                        "key": "domestic_and_safety_fixtures",
                        "label": "Domestic + Safety Fixtures",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "cleanable_wall_and_ceiling_systems",
                        "label": "Cleanable Wall + Ceiling Systems",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.55},
                    },
                    {
                        "key": "specialized_casework_and_benches",
                        "label": "Specialized Casework + Benches",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.45},
                    },
                ],
            },
        ],
    },
    "specialty_self_storage_structural_v1": {
        "profile_id": "specialty_self_storage_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "preengineered_frame_and_decking",
                        "label": "Pre-Engineered Frame + Decking",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.62},
                    },
                    {
                        "key": "partition_and_corridor_blocking",
                        "label": "Partition + Corridor Blocking",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "zoned_climate_control",
                        "label": "Zoned Climate Control",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.71},
                    },
                    {
                        "key": "corridor_ventilation",
                        "label": "Corridor Ventilation",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.29},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "access_control_and_camera_matrix",
                        "label": "Access Control + Camera Matrix",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.67},
                    },
                    {
                        "key": "lighting_and_metering",
                        "label": "Lighting + Metering",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.33},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "domestic_and_fire_service",
                        "label": "Domestic + Fire Service",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.72},
                    },
                    {
                        "key": "site_drainage_connections",
                        "label": "Site Drainage Connections",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "unit_doors_and_hardware",
                        "label": "Unit Doors + Hardware",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.61},
                    },
                    {
                        "key": "wayfinding_and_paint_package",
                        "label": "Wayfinding + Paint Package",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.39},
                    },
                ],
            },
        ],
    },
    "specialty_car_dealership_structural_v1": {
        "profile_id": "specialty_car_dealership_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "showroom_span_and_glazing_support",
                        "label": "Showroom Span + Glazing Support",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.53},
                    },
                    {
                        "key": "service_canopy_and_bay_structure",
                        "label": "Service Canopy + Bay Structure",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.47},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "service_bay_ventilation_and_exhaust",
                        "label": "Service Bay Ventilation + Exhaust",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.62},
                    },
                    {
                        "key": "customer_comfort_hvac",
                        "label": "Customer Comfort HVAC",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "diagnostic_power_and_shop_distribution",
                        "label": "Diagnostic Power + Shop Distribution",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.58},
                    },
                    {
                        "key": "showroom_lighting_and_display_power",
                        "label": "Showroom Lighting + Display Power",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.42},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "service_bay_drainage_and_oil_separators",
                        "label": "Service Bay Drainage + Oil Separators",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.66},
                    },
                    {
                        "key": "showroom_and_customer_facility_plumbing",
                        "label": "Showroom + Customer Facility Plumbing",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.34},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "high_impact_showroom_finishes",
                        "label": "High-Impact Showroom Finishes",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.57},
                    },
                    {
                        "key": "service_writeup_and_parts_finishes",
                        "label": "Service Write-Up + Parts Finishes",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.43},
                    },
                ],
            },
        ],
    },
    "specialty_broadcast_facility_structural_v1": {
        "profile_id": "specialty_broadcast_facility_structural_v1",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "soundstage_shell_and_roof_span",
                        "label": "Soundstage Shell + Roof Span",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.54},
                    },
                    {
                        "key": "control_room_and_riser_support",
                        "label": "Control Room + Riser Support",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.46},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "silent_hvac_and_vibration_isolation",
                        "label": "Silent HVAC + Vibration Isolation",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.65},
                    },
                    {
                        "key": "set_cooling_and_smoke_control",
                        "label": "Set Cooling + Smoke Control",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.35},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "clean_power_and_signal_grounding",
                        "label": "Clean Power + Signal Grounding",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.63},
                    },
                    {
                        "key": "lighting_grids_and_broadcast_distribution",
                        "label": "Lighting Grids + Broadcast Distribution",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.37},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "set_support_and_domestic_water",
                        "label": "Set Support + Domestic Water",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.61},
                    },
                    {
                        "key": "specialty_drainage_and_trench_lines",
                        "label": "Specialty Drainage + Trench Lines",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.39},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "acoustic_envelope_package",
                        "label": "Acoustic Envelope Package",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.59},
                    },
                    {
                        "key": "control_and_edit_suite_finishes",
                        "label": "Control + Edit Suite Finishes",
                        "unit": "SF",
                        "quantity_rule": {"type": "sf"},
                        "allocation": {"type": "share_of_trade", "share": 0.41},
                    },
                ],
            },
        ],
    },
}

SCOPE_ITEM_DEFAULTS = {
    "specialty_profile_by_subtype": {
        "data_center": "specialty_data_center_structural_v1",
        "laboratory": "specialty_laboratory_structural_v1",
        "self_storage": "specialty_self_storage_structural_v1",
        "car_dealership": "specialty_car_dealership_structural_v1",
        "broadcast_facility": "specialty_broadcast_facility_structural_v1",
    }
}
