from app.v2.config.master_config import (
    BuildingType,
    BuildingConfig,
    TradeBreakdown,
    SoftCosts,
    FinancingTerms,
    OwnershipType,
    NLPConfig,
)


CONFIG = (
    BuildingType.PARKING,
    "parking_garage",
    BuildingConfig(
        display_name="Parking Garage",
        base_cost_per_sf=65,
        cost_range=(55, 75),
        equipment_cost_per_sf=8,  # Gates, equipment
        typical_floors=5,
        trades=TradeBreakdown(
            structural=0.45,  # Heavy concrete structure
            mechanical=0.08,  # Ventilation
            electrical=0.15,  # Lighting, controls
            plumbing=0.07,  # Minimal
            finishes=0.25,  # Coatings, striping
        ),
        soft_costs=SoftCosts(
            design_fees=0.04,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.06,
            testing=0.008,
            construction_management=0.02,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.25,
                target_roi=0.12,
            ),
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.80,
                debt_rate=0.038,
                equity_ratio=0.20,
                target_dscr=1.15,
                target_roi=0.0,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "parking garage",
                "parking structure",
                "parking deck",
                "parkade",
                "parking ramp",
                "multi-level parking",
            ],
            priority=47,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.35,
            "San Francisco": 1.40,
            "Chicago": 1.20,
            "Miami": 1.10,
        },
        special_features={
            "automated_system": {
                "basis": "COUNT_BASED",
                "value": 2400000,
                "count": 1,
                "count_override_keys": ["automated_system_count", "parking_automation_count"],
                "unit_label": "system",
            },
            "ev_charging": {
                "basis": "COUNT_BASED",
                "value": 12000,
                "count_override_keys": ["ev_charger_count", "ev_charging_stall_count", "charging_port_count"],
                "default_count_bands": [
                    {"label": "compact_garage", "max_square_footage": 75000, "count": 8},
                    {"label": "urban_garage", "max_square_footage": 150000, "count": 16},
                    {"label": "destination_garage", "count": 24},
                ],
                "unit_label": "charger",
            },
            "car_wash": {
                "basis": "COUNT_BASED",
                "value": 450000,
                "count": 1,
                "count_override_keys": ["car_wash_count", "wash_tunnel_count"],
                "unit_label": "wash",
            },
            "retail_space": {
                "basis": "AREA_SHARE_GSF",
                "value": 30,
                "area_share_of_gsf": 0.04,
            },
            "green_roof": {
                "basis": "AREA_SHARE_GSF",
                "value": 20,
                "area_share_of_gsf": 0.20,
            },
        },
        special_feature_pricing_statuses={
            "automated_system": "incremental",
            "ev_charging": "incremental",
            "car_wash": "incremental",
            "retail_space": "incremental",
            "green_roof": "incremental",
        },
        base_revenue_per_sf_annual=50,
        base_revenue_per_space_monthly=150,
        spaces_per_sf=0.0033,
        occupancy_rate_base=0.85,
        occupancy_rate_premium=0.92,
        operating_margin_base=0.75,
        operating_margin_premium=0.80,
        dealshield_tile_profile="parking_parking_garage_v1",
        scope_profile="parking_parking_garage_structural_v1",
        scope_items_profile="parking_parking_garage_structural_v1",
    ),
)
