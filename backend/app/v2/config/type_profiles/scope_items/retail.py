from typing import Optional

SCOPE_ITEM_DEFAULTS = {
    "shopping_center": "retail_shopping_center_structural_v1",
    "big_box": "retail_big_box_structural_v1",
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
    "retail_shopping_center_structural_v1": {
        "profile_id": "retail_shopping_center_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="inline_shell_bay_frames", label="Inline shell bay framing and roof steel", unit="SF", share=0.28),
                    _item(key="canopy_colonnade_structure", label="Canopy and storefront colonnade steel", unit="SF", share=0.26),
                    _item(key="pad_foundation_and_slab", label="Pad foundations and plaza slab upgrades", unit="SF", share=0.24),
                    _item(key="loading_pad_reinforcement", label="Loading pad reinforcement and dock curbs", unit="SF", share=0.22),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="multi_tenant_rooftop_units", label="Multi-tenant RTU package and controls", unit="SF", share=0.30),
                    _item(key="tenant_duct_distribution", label="Tenant duct distribution and balancing", unit="SF", share=0.25),
                    _item(key="grease_exhaust_and_makeup_air", label="Restaurant bay grease exhaust and makeup air", unit="SF", share=0.23),
                    _item(key="central_bms_and_tab", label="Centerwide controls integration and TAB", unit="LS", share=0.22, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="service_switchgear_and_metering", label="Service switchgear and tenant metering", unit="LS", share=0.29, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="tenant_distribution_panels", label="Tenant distribution panels and feeders", unit="SF", share=0.26),
                    _item(key="site_lighting_and_controls", label="Parking/site lighting and photocell controls", unit="SF", share=0.24),
                    _item(key="life_safety_and_fire_alarm", label="Life-safety fire alarm and notification", unit="LS", share=0.21, quantity_type="constant", quantity_params={"value": 1}),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="domestic_water_loop", label="Domestic water loop and tenant branches", unit="SF", share=0.38),
                    _item(key="sanitary_grease_interceptor_network", label="Sanitary mains and grease interceptor network", unit="SF", share=0.34),
                    _item(key="tenant_restroom_groups", label="Tenant restroom groups and core fixture banks", unit="EA", share=0.28, quantity_type="restroom_groups", quantity_params={"sf_per_group": 14000.0, "minimum": 2}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="storefront_systems_and_glazing", label="Storefront systems and glazing package", unit="SF", share=0.27),
                    _item(key="inline_white_box_turnover", label="Inline white-box turnover and demising", unit="SF", share=0.26),
                    _item(key="common_area_paving_and_ceilings", label="Common-area paving, soffits, and ceilings", unit="SF", share=0.24),
                    _item(key="wayfinding_signage_and_entry_finishes", label="Wayfinding signage and entry finish package", unit="SF", share=0.23),
                ],
            ),
        ],
    },
    "retail_big_box_structural_v1": {
        "profile_id": "retail_big_box_structural_v1",
        "trade_profiles": [
            _trade(
                "structural",
                "Structural",
                [
                    _item(key="long_span_frame_and_columns", label="Long-span frame and high-bay columns", unit="SF", share=0.24),
                    _item(key="thickened_slab_loading_zones", label="Thickened slab and loading-zone reinforcement", unit="SF", share=0.22),
                    _item(key="mezzanine_structure_package", label="Mezzanine framing and stair cores", unit="SF", share=0.20),
                    _item(key="dock_wall_and_apron_structure", label="Dock wall and apron structural works", unit="SF", share=0.18),
                    _item(key="garden_center_canopy_structures", label="Garden center canopy and yard structures", unit="SF", share=0.16),
                ],
            ),
            _trade(
                "mechanical",
                "Mechanical",
                [
                    _item(key="high_bay_rooftop_hvac", label="High-bay rooftop HVAC equipment", unit="SF", share=0.29),
                    _item(key="sales_floor_duct_and_controls", label="Sales-floor duct distribution and controls", unit="SF", share=0.26),
                    _item(key="back_of_house_refrigeration_mechanical", label="Back-of-house refrigeration mechanical systems", unit="SF", share=0.24),
                    _item(key="auto_center_exhaust_and_makeup_air", label="Auto-center exhaust and makeup air", unit="SF", share=0.21),
                ],
            ),
            _trade(
                "electrical",
                "Electrical",
                [
                    _item(key="high_amp_service_and_switchgear", label="High-amp service and primary switchgear", unit="LS", share=0.30, quantity_type="constant", quantity_params={"value": 1}),
                    _item(key="sales_floor_branch_distribution", label="Sales-floor branch distribution and busway", unit="SF", share=0.27),
                    _item(key="refrigeration_and_case_power", label="Refrigeration and merchandiser case power", unit="SF", share=0.24),
                    _item(key="site_and_loading_lighting_controls", label="Site/loading lighting and controls", unit="SF", share=0.19),
                ],
            ),
            _trade(
                "plumbing",
                "Plumbing",
                [
                    _item(key="domestic_water_and_booster", label="Domestic water mains and booster package", unit="SF", share=0.37),
                    _item(key="sanitary_process_waste_network", label="Sanitary and process-waste network", unit="SF", share=0.34),
                    _item(key="customer_staff_restroom_cores", label="Customer and staff restroom cores", unit="EA", share=0.29, quantity_type="restroom_groups", quantity_params={"sf_per_group": 22000.0, "minimum": 2}),
                ],
            ),
            _trade(
                "finishes",
                "Finishes",
                [
                    _item(key="sales_floor_finish_package", label="Sales-floor finish package and resilient flooring", unit="SF", share=0.28),
                    _item(key="front_end_checkout_fitout", label="Front-end checkout and queue fit-out", unit="SF", share=0.26),
                    _item(key="back_of_house_partitions", label="Back-of-house partitions and service corridors", unit="SF", share=0.24),
                    _item(key="entry_façade_and_signage", label="Entry facade branding and signage finishes", unit="SF", share=0.22),
                ],
            ),
        ],
    },
}
