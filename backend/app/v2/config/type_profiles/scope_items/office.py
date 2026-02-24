from typing import Optional

SCOPE_ITEM_DEFAULTS = {
    "class_a": "office_class_a_structural_v1",
    "class_b": "office_class_b_structural_v1",
}


def _item(
    *,
    key: str,
    label: str,
    unit: str,
    share: float,
    quantity_type: str = "sf",
    quantity_params: Optional[dict] = None,
) -> dict:
    return {
        "key": key,
        "label": label,
        "unit": unit,
        "allocation": {
            "type": "share_of_trade",
            "share": share,
        },
        "quantity_rule": {
            "type": quantity_type,
            "params": quantity_params or {},
        },
    }


def _trade(trade_key: str, trade_label: str, items: list[dict]) -> dict:
    return {
        "trade_key": trade_key,
        "trade_label": trade_label,
        "items": items,
    }


SCOPE_ITEM_PROFILES = {
    "office_class_a_structural_v1": {
        "profile_id": "office_class_a_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="tower_foundation_mat", label="Tower mat foundation and core footings", unit="SF", share=0.24),
                    _item(key="steel_frame_lateral", label="Steel frame and lateral bracing package", unit="SF", share=0.22),
                    _item(key="composite_floor_system", label="Composite slab and floor framing", unit="SF", share=0.20),
                    _item(key="roof_screen_support", label="Roof structure and mechanical screen framing", unit="SF", share=0.18),
                    _item(key="vertical_core_reinforcing", label="Elevator/stair core reinforcing and embeds", unit="SF", share=0.16),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="central_plant_chillers", label="Central plant chillers and pumping", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="ahu_distribution_network", label="Air handling units and duct distribution", unit="SF", share=0.18),
                    _item(key="vav_controls_sequence", label="VAV terminals and controls sequence", unit="SF", share=0.17),
                    _item(key="outside_air_heat_recovery", label="Outside-air and heat-recovery assemblies", unit="SF", share=0.16),
                    _item(key="tenant_condenser_water_stub", label="Tenant condenser/chilled water stub-outs", unit="SF", share=0.15),
                    _item(key="commissioning_tab_bundle", label="MEP commissioning and TAB package", unit="LS", share=0.14, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="main_service_switchgear", label="Main service entrance and switchgear", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="riser_and_busway_stack", label="Vertical riser and busway stack", unit="SF", share=0.18),
                    _item(key="tenant_power_distribution", label="Tenant power panels and branch distribution", unit="SF", share=0.17),
                    _item(key="smart_lighting_controls", label="Smart lighting controls and fixture package", unit="SF", share=0.16),
                    _item(key="life_safety_fire_alarm", label="Life-safety fire alarm and egress systems", unit="LS", share=0.15, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="critical_backup_power", label="Critical backup power and transfer controls", unit="LS", share=0.15, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="domestic_water_stacks", label="Domestic water risers and circulation loops", unit="SF", share=0.23),
                    _item(key="sanitary_storm_risers", label="Sanitary and storm riser network", unit="SF", share=0.21),
                    _item(key="premium_restroom_cores", label="Premium restroom cores and fixture banks", unit="EA", share=0.20, quantity_type="restroom_groups", quantity_params={"sf_per_group": 18000.0, "minimum": 2}),
                    _item(key="pantry_breakroom_plumbing", label="Pantry and breakroom plumbing rough-in", unit="SF", share=0.19),
                    _item(key="tenant_metering_isolation", label="Tenant metering and isolation valve sets", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="lobby_stone_millwork", label="Lobby stone, millwork, and signature entry", unit="SF", share=0.21),
                    _item(key="core_corridor_finish", label="Core corridor and elevator lobby finish package", unit="SF", share=0.18),
                    _item(key="premium_restroom_finish", label="Premium restroom tile and fixture finish package", unit="SF", share=0.17),
                    _item(key="tenant_suite_white_box", label="Tenant suite white-box and demising finishes", unit="SF", share=0.16),
                    _item(key="amenity_floor_finish", label="Amenity floor finishes and branded joinery", unit="SF", share=0.15),
                    _item(key="acoustic_glass_partitions", label="Acoustic partitions and glass office fronts", unit="SF", share=0.13),
                ],
            ),
        ],
    },
    "office_class_b_structural_v1": {
        "profile_id": "office_class_b_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="slab_and_foundation_refresh", label="Slab reinforcement and foundation repairs", unit="SF", share=0.25),
                    _item(key="frame_stability_upgrades", label="Frame stability and lateral upgrades", unit="SF", share=0.22),
                    _item(key="roof_structure_patchwork", label="Roof structure patch and steel replacement", unit="SF", share=0.20),
                    _item(key="stair_core_rehab", label="Stair and core structural rehabilitation", unit="SF", share=0.18),
                    _item(key="loading_and_service_structures", label="Loading and service-area structural works", unit="SF", share=0.15),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="rtu_replacement_program", label="RTU replacement and balancing program", unit="SF", share=0.24),
                    _item(key="duct_rezone_work", label="Duct re-zoning and terminal upgrades", unit="SF", share=0.22),
                    _item(key="controls_modernization", label="Building controls modernization", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="ventilation_code_refresh", label="Ventilation code refresh and exhaust improvements", unit="SF", share=0.18),
                    _item(key="after_hours_hvac_zones", label="After-hours HVAC zoning package", unit="SF", share=0.16),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="service_distribution_refresh", label="Service distribution refresh and panel replacements", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="lighting_led_retrofit", label="LED lighting retrofit and controls", unit="SF", share=0.21),
                    _item(key="tenant_branch_refeed", label="Tenant branch circuit refeed and panel updates", unit="SF", share=0.20),
                    _item(key="fire_alarm_update", label="Fire alarm and life-safety update", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="low_voltage_rewire", label="Low-voltage and access-control rewire", unit="SF", share=0.18),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="domestic_water_repipe", label="Domestic water repipe and valve replacement", unit="SF", share=0.25),
                    _item(key="sanitary_branch_refresh", label="Sanitary branch and vent refresh", unit="SF", share=0.22),
                    _item(key="restroom_fixture_replace", label="Restroom fixture replacement program", unit="EA", share=0.20, quantity_type="restroom_groups", quantity_params={"sf_per_group": 20000.0, "minimum": 1}),
                    _item(key="breakroom_plumbing_refresh", label="Breakroom sink and pantry plumbing refresh", unit="SF", share=0.18),
                    _item(key="metering_and_backflow_updates", label="Metering and backflow device updates", unit="LS", share=0.15, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="lobby_repositioning_finish", label="Lobby repositioning and entry finishes", unit="SF", share=0.24),
                    _item(key="corridor_ceiling_flooring", label="Corridor ceiling and flooring replacement", unit="SF", share=0.22),
                    _item(key="restroom_finish_refresh", label="Restroom finish refresh package", unit="SF", share=0.20),
                    _item(key="tenant_suite_paint_carpet", label="Tenant suite paint and carpet turns", unit="SF", share=0.18),
                    _item(key="common_area_millwork_repairs", label="Common area millwork and door hardware repairs", unit="SF", share=0.16),
                ],
            ),
        ],
    },
}
