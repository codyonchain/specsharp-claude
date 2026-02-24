SCOPE_ITEM_DEFAULTS = {
    "industrial_flex_structural_shares": {
        "slab": 0.45,
        "shell": 0.25,
        "foundations": 0.10,
        "dock": 0.20,
    },
}

SCOPE_ITEM_PROFILES = {
    "industrial_warehouse_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "concrete_slab_on_grade",
                        "label": "Concrete slab on grade (6\")",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.45,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "tilt_wall_shell",
                        "label": "Tilt-wall panels / structural shell",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "foundations_footings",
                        "label": "Foundations, footings, and thickened slabs",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "dock_pits_loading_aprons",
                        "label": "Dock pits and loading aprons",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 4,
                                "default_sf_per_dock": 10000.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "rtu_primary_hvac",
                        "label": "HVAC and ventilation baseline",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "unit_heaters_conditioning",
                        "label": "Unit heaters and general conditioning allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "makeup_air_exhaust",
                        "label": "Make-up air and exhaust allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "ductwork_distribution",
                        "label": "Ductwork, distribution, and ventilation",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "hvac_controls_bms",
                        "label": "HVAC controls and BMS allowance",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "office_hvac_allowance",
                        "label": "Office HVAC allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.05,
                                "default_min_sf": 1500.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "main_service_switchgear",
                        "label": "Main electrical service and switchgear",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "power_distribution_panels",
                        "label": "Power distribution, panels, and branch circuits",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "high_bay_lighting",
                        "label": "Lighting, controls, and receptacles",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "equipment_power_allowance",
                        "label": "Equipment power and specialty circuits allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "fire_alarm_low_voltage",
                        "label": "Fire alarm and low-voltage systems",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "restroom_groups",
                        "label": "Restroom groups (fixtures, waste, vent)",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.28,
                        },
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": 25000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "domestic_water_sanitary",
                        "label": "Domestic water and sanitary piping",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "roof_drains_storm_tie_in",
                        "label": "Roof drains and storm tie-in allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "trench_drains_allowance",
                        "label": "Trench drains and washdown allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "fire_protection_esfr",
                        "label": "Fire protection – ESFR sprinkler system",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "office_buildout",
                        "label": "Office build-out (walls, ceilings, flooring)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.05,
                                "default_min_sf": 1500.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "warehouse_floor_sealers",
                        "label": "Warehouse floor sealers, striping, and protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.35,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "minimal_interior_finishes",
                        "label": "Minimal interior finishes allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "doors_hardware_misc",
                        "label": "Doors, hardware, and misc interior finishes",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
    "industrial_cold_storage_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "insulated_slab_vapor_barrier",
                        "label": "Insulated slab on grade with vapor barrier",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "foundations_frost_protection",
                        "label": "Foundations, footings, and frost protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "structural_shell_roof",
                        "label": "Structural shell and roof deck (cold-rated)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "insulated_wall_panels",
                        "label": "Precast insulated wall panels / envelope",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "cold_dock_pits_aprons",
                        "label": "Cold dock pits, aprons, and canopies",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 4,
                                "default_sf_per_dock": 10000.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "industrial_refrigeration_system",
                        "label": "Industrial refrigeration system (compressors, condensers)",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.40,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "evaporators_condensers",
                        "label": "Evaporators and unit coolers",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "refrigerant_piping_distribution",
                        "label": "Refrigerant piping and distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "temperature_controls_monitoring",
                        "label": "Temperature controls and monitoring",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "defrost_dehumidification",
                        "label": "Defrost and dehumidification systems",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "high_capacity_distribution",
                        "label": "High-capacity power distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "main_service_switchgear",
                        "label": "Main electrical service and switchgear",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "motor_control_centers_vfd",
                        "label": "Motor control centers and VFDs",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "backup_power_allowance",
                        "label": "Backup power allowance and generator tie-in",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "controls_monitoring_scada",
                        "label": "Controls, monitoring, and SCADA integration",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "cold_rated_lighting",
                        "label": "Cold-rated lighting and receptacles",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.05,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "restroom_groups",
                        "label": "Restroom groups (fixtures, waste, vent)",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.25,
                        },
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": 25000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "domestic_water_freeze_protection",
                        "label": "Domestic water and freeze protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "trench_floor_drains",
                        "label": "Trench drains and sanitary waste",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "fire_protection_esfr_inrack",
                        "label": "Fire protection - ESFR / in-rack sprinkler system",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.40,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "insulated_panel_walls_ceilings",
                        "label": "Insulated panel walls and ceilings",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.45,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "sanitary_food_grade_finishes",
                        "label": "Sanitary and food-grade finishes",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "cold_dock_doors_seals",
                        "label": "Cold dock doors, seals, and high-speed door package",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.15,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 4,
                                "default_sf_per_dock": 10000.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                    {
                        "key": "control_room_office_buildout",
                        "label": "Control room and office buildout",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.05,
                                "default_min_sf": 1500.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "floor_coatings_markings",
                        "label": "Floor coatings, striping, and protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
    "industrial_manufacturing_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "heavy_duty_slab_and_foundations",
                        "label": "Heavy-duty slab, foundations, and equipment pads",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.34,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_pits_and_trenches",
                        "label": "Process pits, trenches, and housekeeping pads",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "steel_framing_and_crane_support",
                        "label": "Structural steel framing and crane support provisions",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "reinforced_roof_and_envelope",
                        "label": "Reinforced roof deck and shell envelope",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "loading_aprons_and_material_handling_bases",
                        "label": "Loading aprons and material handling base scope",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "process_hvac_and_ventilation",
                        "label": "Process HVAC and ventilation baseline",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.26,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_exhaust_and_dust_collection",
                        "label": "Process exhaust and dust collection allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "compressed_air_generation_distribution",
                        "label": "Compressed air generation and distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_cooling_water_systems",
                        "label": "Process cooling/chilled water systems",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "makeup_air_and_heat_recovery",
                        "label": "Make-up air and heat recovery systems",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_controls_bms_integration",
                        "label": "Process controls and BMS integration",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "primary_service_and_switchgear",
                        "label": "Primary service and switchgear",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.22,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "motor_control_centers_vfd",
                        "label": "Motor control centers and VFD package",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "distribution_panels_and_busway",
                        "label": "Distribution panels, feeders, and busway",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_equipment_power_drops",
                        "label": "Process equipment power drops and branch circuits",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "backup_power_critical_loads",
                        "label": "Backup power and critical load tie-ins",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "controls_and_low_voltage_network",
                        "label": "Controls, low voltage, and network integration",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.08,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "restroom_groups_and_support",
                        "label": "Restroom groups and support plumbing",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": 20000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "process_water_and_treatment",
                        "label": "Process water, treatment, and distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.26,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "condensate_and_drainage_network",
                        "label": "Condensate and drainage network",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "process_floor_trenches_and_drains",
                        "label": "Process floor trenches and drains",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "fire_protection_and_sprinkler_system",
                        "label": "Fire protection and sprinkler system",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "production_floor_coatings_and_sealers",
                        "label": "Production floor coatings and sealers",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "control_room_and_qc_lab_buildout",
                        "label": "Control room and QC lab buildout",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.08,
                                "default_min_sf": 2500.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "locker_breakroom_support_areas",
                        "label": "Locker, breakroom, and support area finishes",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.08,
                                "default_min_sf": 2500.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "equipment_guards_and_safety_curbing",
                        "label": "Equipment guards, bollards, and safety curbing",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "interior_doors_partitions_signage",
                        "label": "Interior doors, partitions, and safety signage",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
    "industrial_distribution_center_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "high_flatness_distribution_slab",
                        "label": "High-flatness concrete slab for throughput lanes",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.34,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "tilt_wall_shell_and_roof",
                        "label": "Tilt-wall shell and long-span roof structure",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.22,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "cross_dock_aprons_and_truck_courts",
                        "label": "Cross-dock aprons and truck court pavement transitions",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 6,
                                "default_sf_per_dock": 8500.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                    {
                        "key": "dock_leveler_pits_and_edge_protection",
                        "label": "Dock leveler pits, edge steel, and bumper support",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 6,
                                "default_sf_per_dock": 8500.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                    {
                        "key": "sortation_support_pedestals_and_equipment_bases",
                        "label": "Sortation pedestal embeds and equipment support bases",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "high_volume_ventilation_and_makeup_air",
                        "label": "High-volume ventilation and make-up air systems",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.24,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "dock_door_air_curtains_and_heaters",
                        "label": "Dock door air curtains and cold-weather heater package",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 6,
                                "default_sf_per_dock": 8500.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                    {
                        "key": "sortation_zone_cooling_allowance",
                        "label": "Sortation zone cooling and circulation allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "smoke_control_and_exhaust",
                        "label": "Smoke control and warehouse exhaust package",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "distribution_hvac_controls_and_monitoring",
                        "label": "Distribution HVAC controls and monitoring integration",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "office_support_hvac_allowance",
                        "label": "Office support HVAC allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.06,
                                "default_min_sf": 1800.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "distribution_primary_service_switchgear",
                        "label": "Primary service, utility metering, and switchgear",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "sortation_conveyor_power_distribution",
                        "label": "Sortation conveyor power distribution and feeders",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.24,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "material_handling_motor_control_centers",
                        "label": "Material-handling motor control centers",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "high_bay_and_dock_lighting_controls",
                        "label": "High-bay plus dock lighting and controls",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "forklift_charging_and_staging_power",
                        "label": "Forklift charging and staging power infrastructure",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "low_voltage_scanning_and_network_backbone",
                        "label": "Low-voltage scanning, network, and controls backbone",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.08,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "distribution_restroom_groups",
                        "label": "Restroom groups and support fixtures",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.24,
                        },
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": 22000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "domestic_water_and_sanitary_distribution",
                        "label": "Domestic water and sanitary distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "dock_washdown_and_trench_drains",
                        "label": "Dock washdown lines and trench drain branches",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "esfr_in_rack_fire_protection_distribution",
                        "label": "ESFR and in-rack fire protection distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "emergency_eyewash_and_tempered_water",
                        "label": "Emergency eyewash and tempered water stations",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "distribution_office_support_buildout",
                        "label": "Distribution office support buildout",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.06,
                                "default_min_sf": 1800.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "dock_door_and_bumper_packages",
                        "label": "Dock doors, seals, bumpers, and edge-of-dock package",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 6,
                                "default_sf_per_dock": 8500.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                    {
                        "key": "distribution_floor_hardener_and_striping",
                        "label": "Floor hardener, traffic striping, and wear protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.30,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "sortation_guardrails_and_bollards",
                        "label": "Sortation guardrails, bollards, and impact protection",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "interior_signage_wayfinding_and_markers",
                        "label": "Interior wayfinding, signage, and safety markers",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
        ],
    },
    "industrial_flex_space_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "flex_slab_and_foundation_package",
                        "label": "Flex slab-on-grade and foundations package",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.40,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "flex_shell_and_roof_deck",
                        "label": "Flex shell framing and roof deck",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.22,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "storefront_opening_structural_supports",
                        "label": "Storefront opening supports and header modifications",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "mezzanine_and_stair_support_allowance",
                        "label": "Office mezzanine and stair support allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "service_door_aprons_and_loading_pads",
                        "label": "Service door aprons and loading pads",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "dock_count",
                            "params": {
                                "default_min": 2,
                                "default_sf_per_dock": 20000.0,
                                "override_keys": [
                                    "dock_doors",
                                    "dock_count",
                                    "dockDoors",
                                    "dockCount",
                                ],
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "warehouse_rtu_base_system",
                        "label": "Warehouse RTU and baseline ventilation",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.22,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "office_showroom_vav_and_split_systems",
                        "label": "Office/showroom VAV and split-system conditioning",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.24,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "storefront_air_distribution_and_controls",
                        "label": "Storefront air distribution and comfort controls",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "light_industrial_exhaust_and_makeup_air",
                        "label": "Light industrial exhaust and make-up air",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "mixed_use_hvac_controls_and_zoning",
                        "label": "Mixed-use HVAC controls and zoning",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "supplemental_unit_heaters_and_destratification",
                        "label": "Supplemental unit heaters and destratification fans",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "flex_main_service_and_distribution",
                        "label": "Main electrical service and distribution backbone",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                    {
                        "key": "office_showroom_lighting_and_controls",
                        "label": "Office/showroom lighting and dimming controls",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.26,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "warehouse_high_bay_lighting_flex",
                        "label": "Warehouse high-bay lighting and controls",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "tenant_branch_power_and_receptacles",
                        "label": "Tenant branch power and receptacles",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "storefront_signage_and_exterior_lighting",
                        "label": "Storefront signage and exterior lighting package",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "low_voltage_data_security_and_fire_alarm",
                        "label": "Low-voltage data, security, and fire alarm systems",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.08,
                        },
                        "quantity_rule": {
                            "type": "constant",
                            "params": {
                                "value": 1,
                            },
                        },
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "flex_restroom_and_breakroom_groups",
                        "label": "Restroom and breakroom plumbing groups",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.28,
                        },
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": 15000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "flex_domestic_water_and_sanitary",
                        "label": "Domestic water and sanitary distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.22,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "pantry_and_janitor_service_connections",
                        "label": "Pantry sink and janitor service connections",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "light_industrial_floor_drains",
                        "label": "Light industrial floor drains and interceptors",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.12,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "fire_protection_wet_pipe_flex",
                        "label": "Wet-pipe fire protection and tenant tie-ins",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.26,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "office_partitions_and_gypsum_assemblies",
                        "label": "Office and showroom partitions (gypsum assemblies)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.26,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "storefront_glazing_and_entry_systems",
                        "label": "Storefront glazing and entry systems",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "suspended_ceilings_and_acoustical_treatments",
                        "label": "Suspended ceilings and acoustical treatments",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "showroom_flooring_and_feature_finishes",
                        "label": "Showroom flooring and feature finish package",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                    {
                        "key": "warehouse_floor_sealers_and_striping_flex",
                        "label": "Warehouse floor sealers and striping allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.16,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "interior_doors_millwork_and_painting",
                        "label": "Interior doors, millwork, and painting package",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "office_sf",
                            "params": {
                                "default_percent": 0.20,
                                "default_min_sf": 4000.0,
                                "override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
                        },
                    },
                ],
            },
        ],
    },
}
