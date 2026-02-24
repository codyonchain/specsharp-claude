SCOPE_ITEM_DEFAULTS = {
    "default_profile_by_subtype": {
        "community_center": "civic_community_center_structural_v1",
        "courthouse": "civic_courthouse_structural_v1",
        "government_building": "civic_government_building_structural_v1",
        "library": "civic_library_structural_v1",
        "public_safety": "civic_public_safety_structural_v1",
    },
}


def _civic_scope_profile() -> dict:
    return {
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "foundations_slab_and_footings",
                        "label": "Foundations, slab, and footings",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "structural_frame_and_lateral",
                        "label": "Structural frame and lateral system",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.24},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "roof_structure_and_deck",
                        "label": "Roof structure and deck",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "stairs_and_core_structure",
                        "label": "Stairs and core structural allowances",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "site_structural_allowances",
                        "label": "Site and retaining structural allowances",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.14},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "mechanical",
                "trade_label": "Mechanical",
                "items": [
                    {
                        "key": "hvac_generation_and_distribution",
                        "label": "HVAC generation and distribution",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "ventilation_and_exhaust_systems",
                        "label": "Ventilation and exhaust systems",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.24},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "controls_and_bms_allowance",
                        "label": "Controls and BMS allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "domestic_hot_water_allowance",
                        "label": "Domestic hot water and plant allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.14},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "specialty_hvac_compliance_allowance",
                        "label": "Specialty HVAC and compliance allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "electrical",
                "trade_label": "Electrical",
                "items": [
                    {
                        "key": "main_service_and_distribution",
                        "label": "Main service and distribution",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.24},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "lighting_and_receptacles",
                        "label": "Lighting and receptacles",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "fire_alarm_and_life_safety",
                        "label": "Fire alarm and life-safety systems",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "security_and_access_control",
                        "label": "Security and access control allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "it_low_voltage_backbone",
                        "label": "IT and low-voltage backbone allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.12},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
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
                        "allocation": {"type": "share_of_trade", "share": 0.32},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {"sf_per_group": 12000.0, "minimum": 1},
                        },
                    },
                    {
                        "key": "domestic_water_and_sanitary",
                        "label": "Domestic water and sanitary piping",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "storm_drainage_allowance",
                        "label": "Storm drainage and roof drain allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "specialty_plumbing_allowance",
                        "label": "Specialty plumbing and compliance allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "interior_partitions_and_ceilings",
                        "label": "Interior partitions and ceilings",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.24},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "flooring_and_wall_finishes",
                        "label": "Flooring and wall finishes",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.22},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "public_lobby_and_common_areas",
                        "label": "Public lobby and common area finishes",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "millwork_and_casework_allowance",
                        "label": "Millwork and casework allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "durability_and_security_finish_allowance",
                        "label": "Durability and security finish allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
        ],
    }


SCOPE_ITEM_PROFILES = {
    "civic_community_center_structural_v1": _civic_scope_profile(),
    "civic_courthouse_structural_v1": _civic_scope_profile(),
    "civic_government_building_structural_v1": _civic_scope_profile(),
    "civic_library_structural_v1": _civic_scope_profile(),
    "civic_public_safety_structural_v1": _civic_scope_profile(),
}
