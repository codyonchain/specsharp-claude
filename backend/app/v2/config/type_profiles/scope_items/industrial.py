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
                    {
                        "key": "mezzanine_structure",
                        "label": "Mezzanine structure (framing, deck, stairs)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.10,
                        },
                        "quantity_rule": {
                            "type": "mezz_sf",
                            "params": {
                                "default_sf": 0.0,
                                "override_keys": [
                                    "mezzanine_sf",
                                    "mezz_sf",
                                    "mezzanineSquareFeet",
                                ],
                                "percent_override_keys": [
                                    "mezzanine_percent",
                                    "mezzanine_pct",
                                    "mezzaninePercent",
                                    "mezzaninePct",
                                ],
                            },
                        },
                        "omit_if_zero_quantity": True,
                    },
                ],
                "conditional_rescales": [
                    {
                        "trigger_item_key": "mezzanine_structure",
                        "target_item_keys": [
                            "concrete_slab_on_grade",
                            "tilt_wall_shell",
                            "foundations_footings",
                            "dock_pits_loading_aprons",
                        ],
                        "remaining_share": 0.90,
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "rtu_primary_hvac",
                        "label": "Rooftop units (RTUs) & primary heating/cooling equipment",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.50,
                        },
                        "quantity_rule": {
                            "type": "rtu_count",
                            "params": {
                                "sf_per_unit": 15000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "makeup_air_exhaust",
                        "label": "Make-up air units and exhaust fans",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.20,
                        },
                        "quantity_rule": {
                            "type": "exhaust_fan_count",
                            "params": {
                                "sf_per_unit": 40000.0,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "ductwork_distribution",
                        "label": "Ductwork, distribution, and ventilation",
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
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "high_bay_lighting",
                        "label": "High-bay lighting & controls",
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
                        "key": "power_distribution_panels",
                        "label": "Power distribution, panels, and branch circuits",
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
                            "share": 0.50,
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
                        "key": "domestic_water_roof_drains",
                        "label": "Domestic water, hose bibs, and roof drains",
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
                            "share": 0.45,
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
                            "share": 0.40,
                        },
                        "quantity_rule": {
                            "type": "warehouse_sf",
                            "params": {
                                "default_percent": 0.05,
                                "default_min_sf": 1500.0,
                                "office_override_keys": [
                                    "office_sf",
                                    "officeSquareFeet",
                                    "office_space_sf",
                                ],
                                "office_percent_override_keys": [
                                    "office_percent",
                                    "office_pct",
                                    "officePercent",
                                    "officePct",
                                ],
                            },
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
}
