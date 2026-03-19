from app.v2.config.master_config import (
    BuildingType,
    BuildingConfig,
    TradeBreakdown,
    SoftCosts,
    FinancingTerms,
    OwnershipType,
    NLPConfig,
    ProjectClass,
)


CONFIG = (
    BuildingType.PARKING,
    "automated_parking",
    BuildingConfig(
        display_name="Automated Parking System",
        base_cost_per_sf=185,
        cost_range=(165, 205),
        equipment_cost_per_sf=65,  # Automated systems
        typical_floors=6,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.30,  # Automated systems
            electrical=0.25,  # Controls and power
            plumbing=0.05,
            finishes=0.15,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.03,
            legal=0.02,
            financing=0.035,
            contingency=0.10,
            testing=0.02,  # System testing
            construction_management=0.04,
            startup=0.025,  # System commissioning
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "automated parking",
                "robotic parking",
                "mechanical parking",
                "puzzle parking",
                "stack parking",
                "tower parking",
            ],
            priority=49,
            incompatible_classes=[ProjectClass.RENOVATION, ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.40,  # Space premium
            "San Francisco": 1.45,
            "Chicago": 1.22,
            "Miami": 1.15,
        },
        special_features={
            "retrieval_speed": {
                "basis": "COUNT_BASED",
                "value": 650000,
                "count": 1,
                "count_override_keys": ["retrieval_upgrade_count", "retrieval_speed_count"],
                "unit_label": "upgrade",
            },
            "redundant_systems": {
                "basis": "COUNT_BASED",
                "value": 900000,
                "count": 1,
                "count_override_keys": ["redundant_system_count", "backup_system_count"],
                "unit_label": "system",
            },
            "valet_interface": {
                "basis": "COUNT_BASED",
                "value": 180000,
                "count": 1,
                "count_override_keys": ["valet_interface_count", "interface_count"],
                "unit_label": "interface",
            },
            "ev_charging_integration": {
                "basis": "COUNT_BASED",
                "value": 10000,
                "count_override_keys": ["ev_charger_count", "ev_charging_stall_count", "charging_port_count"],
                "default_count_bands": [
                    {"label": "compact_robotic", "max_square_footage": 60000, "count": 6},
                    {"label": "tower_robotic", "max_square_footage": 120000, "count": 12},
                    {"label": "high_density_robotic", "count": 18},
                ],
                "unit_label": "charger",
            },
        },
        special_feature_pricing_statuses={
            "retrieval_speed": "incremental",
            "redundant_systems": "included_in_baseline",
            "valet_interface": "included_in_baseline",
            "ev_charging_integration": "incremental",
        },
        base_revenue_per_sf_annual=80,
        base_revenue_per_space_monthly=250,
        spaces_per_sf=0.005,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.65,
        operating_margin_premium=0.72,
        dealshield_tile_profile="parking_automated_parking_v1",
        scope_profile="parking_automated_parking_structural_v1",
        scope_items_profile="parking_automated_parking_structural_v1",
    ),
)
