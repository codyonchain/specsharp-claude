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
            "apparatus_bay": 45,
            "dispatch_center": 50,
            "training_tower": 40,
            "emergency_generator": 35,
            "sally_port": 30,
        },
        base_revenue_per_sf_annual=0,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0,
        operating_margin_premium=0,
    ),
)
