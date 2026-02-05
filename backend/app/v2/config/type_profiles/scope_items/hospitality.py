SCOPE_ITEM_DEFAULTS = {}

SCOPE_ITEM_PROFILES = {
    "hospitality_limited_service_hotel_structural_v1": {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "foundations_slab_footings",
                        "label": "Foundations, slab, and footings",
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
                        "key": "structural_frame",
                        "label": "Structural frame (steel/wood)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.28,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "roof_structure_deck",
                        "label": "Roof structure and deck",
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
                        "key": "stairs_elevator_core_allowance",
                        "label": "Stairs and elevator core structural allowance",
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
                        "key": "misc_structural_allowance",
                        "label": "Misc. structural and lateral system allowances",
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
                        "key": "guestroom_hvac_allowance",
                        "label": "Guestroom HVAC (PTAC/VRF) allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.38,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "common_area_hvac_allowance",
                        "label": "Common area HVAC allowance",
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
                        "key": "ventilation_exhaust_allowance",
                        "label": "Ventilation and exhaust allowance",
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
                        "key": "controls_bms_allowance",
                        "label": "Controls and BMS allowance",
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
                        "key": "domestic_hot_water_plant_allowance",
                        "label": "Domestic hot water plant allowance",
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
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "main_service_switchgear",
                        "label": "Main service and switchgear",
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
                        "key": "lighting_receptacles",
                        "label": "Lighting and receptacles",
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
                        "key": "fire_alarm_life_safety",
                        "label": "Fire alarm and life safety allowance",
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
                        "key": "low_voltage_systems",
                        "label": "Low voltage (WiFi/security/cameras) allowance",
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
                        "key": "emergency_backup_allowance",
                        "label": "Emergency/backup power allowance",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.14,
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
                        "key": "domestic_water_sanitary_distribution",
                        "label": "Domestic water and sanitary distribution",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.36,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "restroom_groups",
                        "label": "Lobby and back-of-house restroom groups",
                        "unit": "EA",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.18,
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
                        "key": "domestic_hot_water_distribution",
                        "label": "Domestic hot water distribution allowance",
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
                        "key": "storm_roof_drains_allowance",
                        "label": "Storm and roof drains allowance",
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
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "guestroom_finishes_package",
                        "label": "Guestroom finishes package",
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
                        "key": "corridor_common_finishes_package",
                        "label": "Corridor and common area finishes package",
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
                        "key": "back_of_house_finishes",
                        "label": "Back-of-house finishes allowance",
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
                        "key": "wet_area_tile_stone_finishes",
                        "label": "Tile/stone and wet-area finishes allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.13,
                        },
                        "quantity_rule": {
                            "type": "sf",
                            "params": {},
                        },
                    },
                    {
                        "key": "casework_allowance",
                        "label": "Casework allowance",
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
                "trade_key": "site",
                "trade_label": "Site/Civil",
                "items": [
                    {
                        "key": "paving_parking_allowance",
                        "label": "Paving and parking allowance",
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
                        "key": "utilities_tie_ins_allowance",
                        "label": "Utilities tie-ins allowance",
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
                        "key": "drainage_stormwater_allowance",
                        "label": "Drainage and stormwater allowance",
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
                        "key": "site_lighting_allowance",
                        "label": "Site lighting allowance",
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
                        "key": "landscaping_minimum_sitework",
                        "label": "Landscaping and minimum sitework allowance",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": 0.17,
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
