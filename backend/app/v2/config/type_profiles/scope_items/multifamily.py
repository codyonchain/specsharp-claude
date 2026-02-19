SCOPE_ITEM_DEFAULTS = {}


def _multifamily_scope_profile(
    subtype_label: str,
    restroom_sf_per_group: float,
    finishes_shares: dict,
) -> dict:
    return {
        "version": "v1",
        "profile_label": f"Multifamily {subtype_label} scope profile",
        "trade_profiles": [
            {
                "trade_key": "structural",
                "trade_label": "Structural",
                "items": [
                    {
                        "key": "foundations_and_slab",
                        "label": "Foundations and slab system",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.28},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "frame_and_podium",
                        "label": "Frame and podium structure",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.26},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "lateral_system",
                        "label": "Lateral and shear system allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "balconies_and_exterior_structure",
                        "label": "Balconies and exterior structural allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.14},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "stairs_and_corridors_structure",
                        "label": "Stairs and corridor structural allowance",
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
                        "key": "hvac_distribution",
                        "label": "HVAC distribution and terminals",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.30},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "ventilation_exhaust",
                        "label": "Ventilation and exhaust systems",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "domestic_hot_water",
                        "label": "Domestic hot water generation",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.18},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "controls_and_bms",
                        "label": "Mechanical controls and BMS allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.12},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "conditioning_allowance",
                        "label": "Supplemental conditioning allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.20},
                        "quantity_rule": {"type": "sf", "params": {}},
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
                        "allocation": {"type": "share_of_trade", "share": 0.22},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "lighting_and_receptacles",
                        "label": "Unit and common-area lighting/receptacles",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.36},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "fire_alarm_life_safety",
                        "label": "Fire alarm and life-safety systems",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.14},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "low_voltage_and_access",
                        "label": "Low-voltage and access control allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.12},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "backup_power_allowance",
                        "label": "Backup power allowance",
                        "unit": "LS",
                        "allocation": {"type": "share_of_trade", "share": 0.16},
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
            {
                "trade_key": "plumbing",
                "trade_label": "Plumbing",
                "items": [
                    {
                        "key": "unit_stacks_and_branch",
                        "label": "Unit plumbing stacks and branch piping",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.38},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "amenity_restroom_groups",
                        "label": "Amenity/common restroom groups",
                        "unit": "EA",
                        "allocation": {"type": "share_of_trade", "share": 0.14},
                        "quantity_rule": {
                            "type": "restroom_groups",
                            "params": {
                                "sf_per_group": restroom_sf_per_group,
                                "minimum": 1,
                            },
                        },
                    },
                    {
                        "key": "domestic_water_and_sanitary",
                        "label": "Domestic water and sanitary distribution",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.26},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "fire_protection_sprinkler",
                        "label": "Fire protection sprinkler allowance",
                        "unit": "SF",
                        "allocation": {"type": "share_of_trade", "share": 0.22},
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                ],
            },
            {
                "trade_key": "finishes",
                "trade_label": "Finishes",
                "items": [
                    {
                        "key": "unit_interiors",
                        "label": "Unit interiors (partitions, paint, flooring)",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": finishes_shares["unit_interiors"],
                        },
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "common_area_finishes",
                        "label": "Common-area finishes",
                        "unit": "SF",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": finishes_shares["common_area_finishes"],
                        },
                        "quantity_rule": {"type": "sf", "params": {}},
                    },
                    {
                        "key": "cabinetry_millwork",
                        "label": "Cabinetry and millwork allowance",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": finishes_shares["cabinetry_millwork"],
                        },
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                    {
                        "key": "appliance_and_fixture_install",
                        "label": "Appliance and fixture installation allowance",
                        "unit": "LS",
                        "allocation": {
                            "type": "share_of_trade",
                            "share": finishes_shares["appliance_and_fixture_install"],
                        },
                        "quantity_rule": {"type": "constant", "params": {"value": 1}},
                    },
                ],
            },
        ],
    }


SCOPE_ITEM_PROFILES = {
    "multifamily_market_rate_apartments_structural_v1": _multifamily_scope_profile(
        subtype_label="market rate apartments",
        restroom_sf_per_group=22000.0,
        finishes_shares={
            "unit_interiors": 0.52,
            "common_area_finishes": 0.20,
            "cabinetry_millwork": 0.15,
            "appliance_and_fixture_install": 0.13,
        },
    ),
    "multifamily_luxury_apartments_structural_v1": _multifamily_scope_profile(
        subtype_label="luxury apartments",
        restroom_sf_per_group=18000.0,
        finishes_shares={
            "unit_interiors": 0.44,
            "common_area_finishes": 0.24,
            "cabinetry_millwork": 0.18,
            "appliance_and_fixture_install": 0.14,
        },
    ),
    "multifamily_affordable_housing_structural_v1": _multifamily_scope_profile(
        subtype_label="affordable housing",
        restroom_sf_per_group=26000.0,
        finishes_shares={
            "unit_interiors": 0.58,
            "common_area_finishes": 0.18,
            "cabinetry_millwork": 0.14,
            "appliance_and_fixture_install": 0.10,
        },
    ),
}
