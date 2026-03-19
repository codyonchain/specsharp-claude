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
    BuildingType.CIVIC,
    "public_safety",
    BuildingConfig(
        display_name="Public Safety Facility",
        base_cost_per_sf=285,
        cost_range=(260, 310),
        dealshield_tile_profile="civic_public_safety_v1",
        scope_items_profile="civic_public_safety_structural_v1",
        equipment_cost_per_sf=35,
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.28,  # Hardened structure
            mechanical=0.24,
            electrical=0.16,  # Emergency power
            plumbing=0.14,
            finishes=0.18,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.015,
            legal=0.018,
            financing=0.02,
            contingency=0.085,
            testing=0.012,
            construction_management=0.035,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.80,
                debt_rate=0.038,
                equity_ratio=0.20,
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "fire station",
                "police station",
                "sheriff",
                "emergency services",
                "dispatch center",
                "911 center",
                "EOC",
                "public safety",
            ],
            priority=37,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.40,
            "San Francisco": 1.45,
            "Chicago": 1.22,
            "Miami": 1.15,
        },
        special_features={
            "apparatus_bay": {
                "basis": "AREA_SHARE_GSF",
                "value": 45,
                "area_share_of_gsf": 0.24,
            },
            "dispatch_center": {
                "basis": "AREA_SHARE_GSF",
                "value": 50,
                "area_share_of_gsf": 0.08,
            },
            "training_tower": {
                "basis": "COUNT_BASED",
                "value": 450000,
                "count": 1,
                "count_override_keys": ["training_tower_count", "tower_count"],
                "unit_label": "tower",
            },
            "emergency_generator": {
                "basis": "COUNT_BASED",
                "value": 300000,
                "count": 1,
                "count_override_keys": ["emergency_generator_count", "generator_count"],
                "unit_label": "generator",
            },
            "sally_port": {
                "basis": "COUNT_BASED",
                "value": 250000,
                "count": 1,
                "count_override_keys": ["sally_port_count", "sallyport_count"],
                "unit_label": "port",
            },
        },
        special_feature_pricing_statuses={
            "apparatus_bay": "included_in_baseline",
            "dispatch_center": "included_in_baseline",
            "training_tower": "incremental",
            "emergency_generator": "included_in_baseline",
            "sally_port": "incremental",
        },
        base_revenue_per_sf_annual=0,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0,
        operating_margin_premium=0,
    ),
)
