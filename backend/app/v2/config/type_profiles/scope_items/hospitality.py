SCOPE_ITEM_DEFAULTS = {
    "limited_service_hotel": "hospitality_limited_service_hotel_structural_v1",
    "full_service_hotel": "hospitality_full_service_hotel_structural_v1",
}


def _item(
    *,
    key: str,
    label: str,
    unit: str,
    share: float,
    quantity_type: str = "sf",
    quantity_params: dict = None,
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
    "hospitality_limited_service_hotel_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="foundations_slab_footings",
                        label="Foundations, slab, and footings",
                        unit="SF",
                        share=0.30,
                    ),
                    _item(
                        key="structural_frame",
                        label="Structural frame (steel/wood)",
                        unit="SF",
                        share=0.28,
                    ),
                    _item(
                        key="roof_structure_deck",
                        label="Roof structure and deck",
                        unit="SF",
                        share=0.18,
                    ),
                    _item(
                        key="stairs_elevator_core_allowance",
                        label="Stairs and elevator core structural allowance",
                        unit="SF",
                        share=0.14,
                    ),
                    _item(
                        key="misc_structural_allowance",
                        label="Misc. structural and lateral system allowances",
                        unit="SF",
                        share=0.10,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="guestroom_hvac_allowance",
                        label="Guestroom HVAC (PTAC/VRF) allowance",
                        unit="SF",
                        share=0.38,
                    ),
                    _item(
                        key="common_area_hvac_allowance",
                        label="Common area HVAC allowance",
                        unit="SF",
                        share=0.20,
                    ),
                    _item(
                        key="ventilation_exhaust_allowance",
                        label="Ventilation and exhaust allowance",
                        unit="SF",
                        share=0.15,
                    ),
                    _item(
                        key="controls_bms_allowance",
                        label="Controls and BMS allowance",
                        unit="LS",
                        share=0.12,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="domestic_hot_water_plant_allowance",
                        label="Domestic hot water plant allowance",
                        unit="LS",
                        share=0.15,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(
                        key="main_service_switchgear",
                        label="Main service and switchgear",
                        unit="LS",
                        share=0.22,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="lighting_receptacles",
                        label="Lighting and receptacles",
                        unit="SF",
                        share=0.40,
                    ),
                    _item(
                        key="fire_alarm_life_safety",
                        label="Fire alarm and life safety allowance",
                        unit="LS",
                        share=0.12,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="low_voltage_systems",
                        label="Low voltage (WiFi/security/cameras) allowance",
                        unit="LS",
                        share=0.12,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="emergency_backup_allowance",
                        label="Emergency/backup power allowance",
                        unit="LS",
                        share=0.14,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="domestic_water_sanitary_distribution",
                        label="Domestic water and sanitary distribution",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="restroom_groups",
                        label="Lobby and back-of-house restroom groups",
                        unit="EA",
                        share=0.18,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 15000.0, "minimum": 1},
                    ),
                    _item(
                        key="domestic_hot_water_distribution",
                        label="Domestic hot water distribution allowance",
                        unit="SF",
                        share=0.24,
                    ),
                    _item(
                        key="storm_roof_drains_allowance",
                        label="Storm and roof drains allowance",
                        unit="SF",
                        share=0.22,
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="guestroom_finishes_package",
                        label="Guestroom finishes package",
                        unit="SF",
                        share=0.45,
                    ),
                    _item(
                        key="corridor_common_finishes_package",
                        label="Corridor and common area finishes package",
                        unit="SF",
                        share=0.20,
                    ),
                    _item(
                        key="back_of_house_finishes",
                        label="Back-of-house finishes allowance",
                        unit="SF",
                        share=0.12,
                    ),
                    _item(
                        key="wet_area_tile_stone_finishes",
                        label="Tile/stone and wet-area finishes allowance",
                        unit="SF",
                        share=0.13,
                    ),
                    _item(
                        key="casework_allowance",
                        label="Casework allowance",
                        unit="LS",
                        share=0.10,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
            _trade(
                "site",
                "Site/Civil",
                [
                    _item(
                        key="paving_parking_allowance",
                        label="Paving and parking allowance",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="utilities_tie_ins_allowance",
                        label="Utilities tie-ins allowance",
                        unit="LS",
                        share=0.18,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="drainage_stormwater_allowance",
                        label="Drainage and stormwater allowance",
                        unit="SF",
                        share=0.18,
                    ),
                    _item(
                        key="site_lighting_allowance",
                        label="Site lighting allowance",
                        unit="SF",
                        share=0.12,
                    ),
                    _item(
                        key="landscaping_minimum_sitework",
                        label="Landscaping and minimum sitework allowance",
                        unit="SF",
                        share=0.17,
                    ),
                ],
            ),
        ],
    },
    "hospitality_full_service_hotel_structural_v1": {
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="ballroom_and_back_of_house_foundations",
                        label="Ballroom and back-of-house foundations",
                        unit="SF",
                        share=0.26,
                    ),
                    _item(
                        key="transfer_beams_and_long_span_framing",
                        label="Transfer beams and long-span framing",
                        unit="SF",
                        share=0.24,
                    ),
                    _item(
                        key="tower_core_outrigger_allowance",
                        label="Tower core and outrigger allowance",
                        unit="SF",
                        share=0.20,
                    ),
                    _item(
                        key="rooftop_amenity_structure_allowance",
                        label="Rooftop amenity structure allowance",
                        unit="SF",
                        share=0.15,
                    ),
                    _item(
                        key="acoustic_separation_structural_allowance",
                        label="Acoustic separation structural allowance",
                        unit="SF",
                        share=0.15,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="central_plant_chiller_boiler_allowance",
                        label="Central plant chiller/boiler allowance",
                        unit="LS",
                        share=0.28,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="ballroom_makeup_air_smoke_control",
                        label="Ballroom make-up air and smoke-control allowance",
                        unit="LS",
                        share=0.20,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="kitchen_and_laundry_exhaust_allowance",
                        label="Kitchen and laundry exhaust allowance",
                        unit="LS",
                        share=0.18,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="guestroom_fan_coil_distribution",
                        label="Guestroom fan-coil and riser distribution",
                        unit="SF",
                        share=0.22,
                    ),
                    _item(
                        key="bms_and_energy_recovery_controls",
                        label="BMS and energy-recovery controls",
                        unit="LS",
                        share=0.12,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(
                        key="medium_voltage_service_and_transformers",
                        label="Medium-voltage service and transformers",
                        unit="LS",
                        share=0.24,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="banquet_av_and_dimming_controls",
                        label="Banquet AV and dimming controls",
                        unit="LS",
                        share=0.18,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="guestroom_and_corridor_power_distribution",
                        label="Guestroom and corridor power distribution",
                        unit="SF",
                        share=0.28,
                    ),
                    _item(
                        key="life_safety_voice_evacuation",
                        label="Life-safety and voice-evacuation systems",
                        unit="LS",
                        share=0.14,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="emergency_generation_parallel_gear",
                        label="Emergency generation and paralleling gear",
                        unit="LS",
                        share=0.16,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="domestic_hot_cold_riser_systems",
                        label="Domestic hot/cold riser systems",
                        unit="SF",
                        share=0.30,
                    ),
                    _item(
                        key="commercial_kitchen_grease_waste",
                        label="Commercial kitchen grease and waste systems",
                        unit="LS",
                        share=0.20,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="laundry_hot_water_reclaim",
                        label="Laundry hot-water reclaim allowance",
                        unit="LS",
                        share=0.16,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="spa_pool_treatment_allowance",
                        label="Spa/pool treatment and filtration allowance",
                        unit="LS",
                        share=0.18,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="sanitary_storm_sewage_ejector_system",
                        label="Sanitary, storm, and sewage ejector systems",
                        unit="SF",
                        share=0.16,
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="premium_guestroom_finish_package",
                        label="Premium guestroom finish package",
                        unit="SF",
                        share=0.30,
                    ),
                    _item(
                        key="grand_lobby_public_space_finishes",
                        label="Grand lobby and public-space finishes",
                        unit="SF",
                        share=0.24,
                    ),
                    _item(
                        key="ballroom_prefunction_finishes",
                        label="Ballroom and prefunction finishes",
                        unit="SF",
                        share=0.18,
                    ),
                    _item(
                        key="food_beverage_venue_fitout",
                        label="Food-and-beverage venue fit-out",
                        unit="SF",
                        share=0.16,
                    ),
                    _item(
                        key="back_of_house_service_corridor_finishes",
                        label="Back-of-house service corridor finishes",
                        unit="SF",
                        share=0.12,
                    ),
                ],
            ),
            _trade(
                "site",
                "Site/Civil",
                [
                    _item(
                        key="porte_cochere_circulation_and_canopies",
                        label="Porte-cochere circulation and canopies",
                        unit="LS",
                        share=0.24,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="valet_and_service_drive_paving",
                        label="Valet and service-drive paving",
                        unit="SF",
                        share=0.21,
                    ),
                    _item(
                        key="landscape_hardscape_guest_arrival",
                        label="Landscape/hardscape guest-arrival package",
                        unit="SF",
                        share=0.18,
                    ),
                    _item(
                        key="site_utilities_and_fire_loop_tieins",
                        label="Site utilities and fire-loop tie-ins",
                        unit="LS",
                        share=0.19,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="exterior_lighting_wayfinding_allowance",
                        label="Exterior lighting and wayfinding allowance",
                        unit="LS",
                        share=0.18,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                ],
            ),
        ],
    },
}
