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
    BuildingType.MIXED_USE,
    "retail_residential",
    BuildingConfig(
        display_name="Retail with Residential Above",
        base_cost_per_sf=225,
        cost_range=(200, 250),
        equipment_cost_per_sf=20,
        typical_floors=5,  # 1 retail + 4 residential
        trades=TradeBreakdown(
            structural=0.26,
            mechanical=0.23,
            electrical=0.14,
            plumbing=0.17,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.06,
            permits=0.025,
            legal=0.018,
            financing=0.03,
            contingency=0.08,
            testing=0.008,
            construction_management=0.03,
            startup=0.012,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.72,
                debt_rate=0.058,
                equity_ratio=0.28,
                target_dscr=1.25,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "mixed use",
                "retail residential",
                "shops with apartments",
                "ground floor retail",
                "live work",
            ],
            priority=26,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.45,
            "San Francisco": 1.50,
            "Chicago": 1.25,
            "Miami": 1.18,
        },
        dealshield_tile_profile="mixed_use_retail_residential_v1",
        scope_items_profile="mixed_use_retail_residential_structural_v1",
        special_features={
            "rooftop_deck": 30,
            "parking_podium": 40,
            "retail_plaza": 25,
        },
        base_revenue_per_sf_annual=35,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
