from typing import Optional

SCOPE_ITEM_DEFAULTS = {
    "surface_parking": "parking_surface_parking_structural_v1",
    "parking_garage": "parking_parking_garage_structural_v1",
    "underground_parking": "parking_underground_parking_structural_v1",
    "automated_parking": "parking_automated_parking_structural_v1",
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
    "parking_surface_parking_structural_v1": {
        "profile_id": "parking_surface_parking_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="surface_subgrade_prep", label="Subgrade Preparation and Compaction", unit="SF", share=0.28),
                    _item(key="surface_base_course", label="Aggregate Base Course Placement", unit="SF", share=0.26),
                    _item(key="surface_asphalt_or_concrete_paving", label="Paving Installation", unit="SF", share=0.24),
                    _item(key="surface_curb_and_island_concrete", label="Curb, Island, and Edge Restraint Concrete", unit="SF", share=0.22),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="surface_drainage_piping", label="Storm Drainage Piping", unit="SF", share=0.38),
                    _item(key="surface_oil_water_separator", label="Oil-Water Separator Equipment", unit="LS", share=0.34, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="surface_pump_controls", label="Drainage Pump Controls", unit="LS", share=0.28, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="surface_site_lighting", label="Site Lighting Poles and Fixtures", unit="SF", share=0.28),
                    _item(key="surface_lighting_controls", label="Lighting Controls and Metering", unit="LS", share=0.26, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="surface_access_gate_power", label="Gate and Access Power Distribution", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="surface_ev_stubouts_and_panels", label="EV Stub-Outs and Spare Panel Capacity", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="surface_catch_basins", label="Catch Basins and Inlets", unit="EA", share=0.40, quantity_type="restroom_groups", quantity_params={"sf_per_group": 12000.0, "minimum": 2}),
                    _item(key="surface_storm_mains", label="Storm Main Tie-ins", unit="SF", share=0.32),
                    _item(key="surface_trench_drain_runs", label="Trench Drain Runs", unit="SF", share=0.28),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="surface_striping_and_markings", label="Striping and Pavement Markings", unit="SF", share=0.37),
                    _item(key="surface_signage_package", label="Wayfinding and Regulatory Signage", unit="LS", share=0.33, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="surface_wheel_stops_and_bollards", label="Wheel Stops and Bollards", unit="SF", share=0.30),
                ],
            ),
        ],
    },
    "parking_parking_garage_structural_v1": {
        "profile_id": "parking_parking_garage_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="garage_foundation_and_core", label="Foundations and Vertical Cores", unit="SF", share=0.23),
                    _item(key="garage_post_tension_decks", label="Post-Tension Deck Slabs", unit="SF", share=0.21),
                    _item(key="garage_ramp_structure", label="Ramp Structure and Slab Thickening", unit="SF", share=0.20),
                    _item(key="garage_seismic_and_bracing", label="Lateral Bracing and Seismic Detailing", unit="SF", share=0.19),
                    _item(key="garage_expansion_joint_package", label="Expansion Joint and Movement Package", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="garage_ventilation_fans", label="Garage Ventilation Fans", unit="LS", share=0.27, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_co_monitoring", label="CO Monitoring and Control Network", unit="LS", share=0.25, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_smoke_control", label="Smoke Control Sequences", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_system_balancing", label="Air Balance and Commissioning", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="garage_distribution_and_panels", label="Power Distribution and Panels", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_lighting_levels", label="Lighting Levels and Fixture Package", unit="SF", share=0.21),
                    _item(key="garage_emergency_power", label="Emergency Egress and Backup Power", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_entry_exit_controls", label="Entry/Exit Controls and Revenue Equipment", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="garage_ev_charging_backbone", label="EV Charging Backbone and Load Management", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="garage_floor_drains", label="Floor Drains and Trap Primers", unit="SF", share=0.36),
                    _item(key="garage_storm_leaders", label="Storm Leaders and Trunk Mains", unit="SF", share=0.34),
                    _item(key="garage_fire_water_extensions", label="Fire Water Extensions", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="garage_deck_coatings", label="Traffic Deck Coatings", unit="SF", share=0.27),
                    _item(key="garage_joint_sealants", label="Joint Sealants and Crack Repairs", unit="SF", share=0.25),
                    _item(key="garage_striping_and_signage", label="Striping, Signage, and Stall Numbering", unit="SF", share=0.24),
                    _item(key="garage_protection_bollards", label="Bollards and Impact Protection", unit="SF", share=0.24),
                ],
            ),
        ],
    },
    "parking_underground_parking_structural_v1": {
        "profile_id": "parking_underground_parking_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="underground_excavation_support", label="Excavation Support and Shoring", unit="SF", share=0.20),
                    _item(key="underground_foundation_walls", label="Foundation Walls and Retaining Structure", unit="SF", share=0.19),
                    _item(key="underground_transfer_slab", label="Transfer Slab and Columns", unit="SF", share=0.17),
                    _item(key="underground_waterproofing_substrate", label="Waterproofing Substrate Prep", unit="SF", share=0.16),
                    _item(key="underground_underpinning_zones", label="Underpinning and Adjacent Structure Protection", unit="LS", share=0.15, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_heave_mitigation", label="Base-Slab Heave Mitigation Measures", unit="LS", share=0.13, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="underground_high_static_fans", label="High-Static Ventilation Fans", unit="LS", share=0.24, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_dewatering_pumps", label="Dewatering Pump Arrays", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_condensation_control", label="Condensation and Humidity Control", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_smoke_purge_controls", label="Smoke Purge Controls", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_commissioning_sequences", label="Mechanical Commissioning Sequences", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="underground_waterproof_distribution", label="Waterproof Electrical Distribution", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_emergency_lighting", label="Emergency Lighting and Egress Controls", unit="SF", share=0.21),
                    _item(key="underground_life_safety_panels", label="Life Safety Panels and Monitoring", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_equipment_power", label="Pump and Fan Power Feeders", unit="LS", share=0.19, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="underground_corrosion_grounding", label="Corrosion Protection and Grounding Upgrades", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="underground_perimeter_drain", label="Perimeter Drain Network", unit="SF", share=0.30),
                    _item(key="underground_sump_pits", label="Sump Pits and Discharge Piping", unit="LS", share=0.26, quantity_type="constant", quantity_params={"value": 2}),
                    _item(key="underground_storm_relief", label="Storm Relief and Overflow", unit="SF", share=0.24),
                    _item(key="underground_waterproof_penetrations", label="Waterproof Penetration Detailing", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="underground_high_durability_coatings", label="High-Durability Coatings", unit="SF", share=0.28),
                    _item(key="underground_wayfinding", label="Underground Wayfinding and Marking", unit="SF", share=0.26),
                    _item(key="underground_protective_barriers", label="Protective Barriers and Guardrails", unit="SF", share=0.24),
                    _item(key="underground_access_control_enclosures", label="Access Control Enclosures", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
        ],
    },
    "parking_automated_parking_structural_v1": {
        "profile_id": "parking_automated_parking_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="automated_tower_frame", label="Tower Frame and Rack Supports", unit="SF", share=0.23),
                    _item(key="automated_lift_shaft_structure", label="Lift Shaft and Pit Structure", unit="SF", share=0.21),
                    _item(key="automated_transfer_platforms", label="Transfer Platforms and Equipment Pads", unit="SF", share=0.20),
                    _item(key="automated_service_catwalks", label="Service Catwalks and Access Platforms", unit="SF", share=0.19),
                    _item(key="automated_seismic_isolation_anchors", label="Seismic Isolation and Anchor Hardening", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="automated_lift_mechanics", label="Lift and Shuttle Mechanical Systems", unit="LS", share=0.23, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_drive_motors", label="Drive Motors and Gear Assemblies", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_hydraulic_power", label="Hydraulic/Actuation Power Units", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_mechanical_redundancy", label="Mechanical Redundancy Packages", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_mechanical_commissioning", label="Mechanical Commissioning and Tuning", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="automated_power_distribution", label="Primary Power Distribution", unit="LS", share=0.20, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_controls_network", label="Controls Network and PLC Panels", unit="LS", share=0.18, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_sensors_and_safety", label="Sensors and Safety Interlock Devices", unit="LS", share=0.17, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_backup_power", label="Backup Power and Ride-Through Systems", unit="LS", share=0.16, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_operator_interface", label="Operator Interface and Payment Controls", unit="LS", share=0.15, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_remote_monitoring_and_cyberhardening", label="Remote Monitoring and Cyber Hardening", unit="LS", share=0.14, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="automated_trench_and_sump", label="Trench Drain and Sump Collection", unit="SF", share=0.38),
                    _item(key="automated_fire_protection_tieins", label="Fire Protection Tie-ins", unit="LS", share=0.34, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="automated_condensate_management", label="Condensate and Drip Management", unit="LS", share=0.28, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="automated_entry_lobby_finishes", label="Entry Lobby and Vehicle Transfer Finishes", unit="SF", share=0.28),
                    _item(key="automated_equipment_protection", label="Equipment Protection Coatings", unit="SF", share=0.26),
                    _item(key="automated_signage_and_wayfinding", label="Signage and Wayfinding Package", unit="SF", share=0.24),
                    _item(key="automated_service_corridor_finishes", label="Service Corridor and Access Finishes", unit="SF", share=0.22),
                ],
            ),
        ],
    },
}
