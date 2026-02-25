"""Scope item profiles for mixed_use subtypes."""

from typing import Optional

SCOPE_ITEM_DEFAULTS = {
    "office_residential": "mixed_use_office_residential_structural_v1",
    "retail_residential": "mixed_use_retail_residential_structural_v1",
    "hotel_retail": "mixed_use_hotel_retail_structural_v1",
    "transit_oriented": "mixed_use_transit_oriented_structural_v1",
    "urban_mixed": "mixed_use_urban_mixed_structural_v1",
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
    "mixed_use_office_residential_structural_v1": {
        "profile_id": "mixed_use_office_residential_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="office_tower_core_and_transfer_frame",
                        label="Office tower core and transfer frame",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="residential_slab_balcony_structure",
                        label="Residential slab and balcony structure",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="podium_and_loading_structure",
                        label="Podium and loading zone structure",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="dual_program_hvac_distribution",
                        label="Dual-program HVAC distribution",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="residential_exhaust_and_makeup_air",
                        label="Residential exhaust and makeup-air systems",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="office_condenser_and_controls",
                        label="Office condenser loop and controls",
                        unit="LS",
                        share=0.31,
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
                        key="highrise_riser_and_metering_stack",
                        label="High-rise risers and metering stack",
                        unit="LS",
                        share=0.34,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="office_floor_power_and_lighting",
                        label="Office floor power and lighting distribution",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="residential_unit_panels_life_safety",
                        label="Residential unit panels and life-safety circuits",
                        unit="SF",
                        share=0.33,
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="mixed_use_vertical_stacks",
                        label="Mixed-use domestic and sanitary stacks",
                        unit="SF",
                        share=0.38,
                    ),
                    _item(
                        key="amenity_restroom_groups",
                        label="Amenity and lobby restroom groups",
                        unit="EA",
                        share=0.32,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 22000.0, "minimum": 1},
                    ),
                    _item(
                        key="tenant_wet_stack_and_isolation",
                        label="Tenant wet stack tie-ins and isolation valves",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="office_lobby_and_core_finishes",
                        label="Office lobby and core finishes",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="residential_corridor_and_unit_finishes",
                        label="Residential corridor and unit finishes",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="amenity_deck_and_shared_space_finishes",
                        label="Amenity deck and shared space finishes",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
        ],
    },
    "mixed_use_retail_residential_structural_v1": {
        "profile_id": "mixed_use_retail_residential_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="retail_frontage_frame_and_canopies",
                        label="Retail frontage frame and canopy support",
                        unit="SF",
                        share=0.37,
                    ),
                    _item(
                        key="podium_slab_and_transfer_girders",
                        label="Podium slab and transfer girders",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="residential_bay_and_balcony_structure",
                        label="Residential bay and balcony structure",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="retail_ventilation_exhaust_allowance",
                        label="Retail ventilation and exhaust allowance",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="residential_hvac_distribution",
                        label="Residential HVAC distribution",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="podium_mechanical_controls",
                        label="Podium-level mechanical controls",
                        unit="LS",
                        share=0.33,
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
                        key="retail_tenant_service_and_metering",
                        label="Retail tenant service and metering",
                        unit="LS",
                        share=0.34,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="residential_power_and_lighting_distribution",
                        label="Residential power and lighting distribution",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="site_lighting_and_life_safety",
                        label="Site lighting and life-safety systems",
                        unit="SF",
                        share=0.33,
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="retail_restaurant_plumbing_stubs",
                        label="Retail food-service plumbing stubs",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="residential_stacks_and_water_service",
                        label="Residential stacks and domestic water service",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="shared_restroom_and_public_plumbing",
                        label="Shared restroom and public-area plumbing",
                        unit="EA",
                        share=0.30,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 20000.0, "minimum": 1},
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="retail_storefront_and_public_finishes",
                        label="Retail storefront and public-realm finishes",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="residential_unit_and_corridor_finishes",
                        label="Residential unit and corridor finishes",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="lobby_and_rooftop_amenity_finishes",
                        label="Lobby and rooftop amenity finishes",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
        ],
    },
    "mixed_use_hotel_retail_structural_v1": {
        "profile_id": "mixed_use_hotel_retail_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="hotel_tower_core_and_long_span_transfer",
                        label="Hotel core and long-span transfer structure",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="retail_podium_frame_and_canopy_support",
                        label="Retail podium frame and canopy support",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="back_of_house_loading_structures",
                        label="Back-of-house and loading structures",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="guestroom_hvac_and_condensing_network",
                        label="Guestroom HVAC and condensing network",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="fnb_kitchen_exhaust_and_makeup_air",
                        label="F&B kitchen exhaust and makeup-air systems",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="ballroom_and_back_of_house_controls",
                        label="Ballroom and BOH controls allowance",
                        unit="LS",
                        share=0.31,
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
                        key="hotel_service_switchgear_and_distribution",
                        label="Hotel service switchgear and distribution",
                        unit="LS",
                        share=0.34,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="guestroom_power_and_lighting",
                        label="Guestroom power and lighting",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="retail_tenant_power_and_signage_allowance",
                        label="Retail tenant power and signage allowance",
                        unit="SF",
                        share=0.33,
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="guestroom_plumbing_stacks_and_boosters",
                        label="Guestroom stacks and booster systems",
                        unit="SF",
                        share=0.37,
                    ),
                    _item(
                        key="kitchen_and_fnb_grease_waste",
                        label="Kitchen and F&B grease/waste systems",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="hotel_public_restroom_groups",
                        label="Hotel public restroom groups",
                        unit="EA",
                        share=0.30,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 18000.0, "minimum": 2},
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="guestroom_and_corridor_finish_package",
                        label="Guestroom and corridor finish package",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="retail_frontage_and_public_lobby_finishes",
                        label="Retail frontage and public lobby finishes",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="fnb_and_event_space_finish_package",
                        label="F&B and event-space finish package",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
        ],
    },
    "mixed_use_transit_oriented_structural_v1": {
        "profile_id": "mixed_use_transit_oriented_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="station_interface_structure_and_bracing",
                        label="Station interface structure and bracing",
                        unit="SF",
                        share=0.37,
                    ),
                    _item(
                        key="pedestrian_bridge_and_circulation_structures",
                        label="Pedestrian bridge and circulation structures",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="mixed_use_podium_and_public_plaza_structure",
                        label="Mixed-use podium and public plaza structure",
                        unit="SF",
                        share=0.30,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="transit_adjacent_hvac_and_air_quality_controls",
                        label="Transit-adjacent HVAC and air-quality controls",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="public_concourse_smoke_control",
                        label="Public concourse smoke control",
                        unit="LS",
                        share=0.33,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="tenant_hvac_distribution_and_zoning",
                        label="Tenant HVAC distribution and zoning",
                        unit="SF",
                        share=0.32,
                    ),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(
                        key="transit_interface_power_and_resiliency",
                        label="Transit interface power and resiliency",
                        unit="LS",
                        share=0.34,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="concourse_lighting_and_wayfinding",
                        label="Concourse lighting and wayfinding systems",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="mixed_tenant_metering_and_distribution",
                        label="Mixed tenant metering and distribution",
                        unit="SF",
                        share=0.33,
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="public_realm_storm_and_drainage",
                        label="Public realm stormwater and drainage systems",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="tenant_domestic_and_sanitary_risers",
                        label="Tenant domestic and sanitary risers",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="station_and_concourse_restroom_groups",
                        label="Station and concourse restroom groups",
                        unit="EA",
                        share=0.30,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 18000.0, "minimum": 2},
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="concourse_and_public_plaza_finishes",
                        label="Concourse and public plaza finishes",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="tenant_lobby_and_corridor_finishes",
                        label="Tenant lobby and corridor finishes",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="retail_activation_and_wayfinding_finishes",
                        label="Retail activation and wayfinding finishes",
                        unit="SF",
                        share=0.32,
                    ),
                ],
            ),
        ],
    },
    "mixed_use_urban_mixed_structural_v1": {
        "profile_id": "mixed_use_urban_mixed_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(
                        key="multi_program_tower_core_and_transfer",
                        label="Multi-program tower core and transfer structure",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="public_realm_canopy_and_edge_structures",
                        label="Public-realm canopy and edge structures",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="parking_and_loading_structure",
                        label="Integrated parking and loading structure",
                        unit="SF",
                        share=0.32,
                    ),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(
                        key="vertical_mobility_machine_and_ventilation",
                        label="Vertical mobility machinery and ventilation",
                        unit="LS",
                        share=0.34,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="mixed_program_hvac_distribution",
                        label="Mixed-program HVAC distribution",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="public_realm_conditioning_and_controls",
                        label="Public-realm conditioning and controls",
                        unit="SF",
                        share=0.33,
                    ),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(
                        key="high_capacity_service_and_microgrid_ready",
                        label="High-capacity service and microgrid-ready backbone",
                        unit="LS",
                        share=0.35,
                        quantity_type="constant",
                        quantity_params={"value": 1},
                    ),
                    _item(
                        key="multi_tenant_distribution_and_metering",
                        label="Multi-tenant electrical distribution and metering",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="public_realm_lighting_and_media_power",
                        label="Public-realm lighting and media power",
                        unit="SF",
                        share=0.32,
                    ),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(
                        key="mixed_use_domestic_hot_water_network",
                        label="Mixed-use domestic hot water network",
                        unit="SF",
                        share=0.36,
                    ),
                    _item(
                        key="public_plaza_storm_reuse_and_drainage",
                        label="Public plaza stormwater reuse and drainage",
                        unit="SF",
                        share=0.34,
                    ),
                    _item(
                        key="event_space_restroom_groups",
                        label="Event-space and public restroom groups",
                        unit="EA",
                        share=0.30,
                        quantity_type="restroom_groups",
                        quantity_params={"sf_per_group": 16000.0, "minimum": 2},
                    ),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(
                        key="public_realm_activation_finish_package",
                        label="Public-realm activation finish package",
                        unit="SF",
                        share=0.35,
                    ),
                    _item(
                        key="tower_lobby_and_common_area_finishes",
                        label="Tower lobby and common-area finishes",
                        unit="SF",
                        share=0.33,
                    ),
                    _item(
                        key="multi_tenant_white_box_and_fitout_base",
                        label="Multi-tenant white-box and fit-out base",
                        unit="SF",
                        share=0.32,
                    ),
                ],
            ),
        ],
    },
}
