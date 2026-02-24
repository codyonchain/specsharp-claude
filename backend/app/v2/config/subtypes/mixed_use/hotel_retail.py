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
    "hotel_retail",
    BuildingConfig(
        display_name="Hotel with Retail",
        base_cost_per_sf=295,
        cost_range=(270, 320),
        equipment_cost_per_sf=35,
        typical_floors=10,
        trades=TradeBreakdown(
            structural=0.24,
            mechanical=0.25,
            electrical=0.15,
            plumbing=0.16,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.025,
            legal=0.02,
            financing=0.032,
            contingency=0.09,
            testing=0.01,
            construction_management=0.035,
            startup=0.018,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.68,
                debt_rate=0.062,
                equity_ratio=0.32,
                target_dscr=1.28,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "hotel retail",
                "hotel with shops",
                "hospitality mixed use",
                "hotel complex",
                "resort retail",
            ],
            priority=28,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.95,
            "Memphis": 0.93,
            "New York": 1.45,
            "San Francisco": 1.50,
            "Chicago": 1.25,
            "Miami": 1.22,
        },
        special_features={
            "conference_center": 45,
            "restaurant": 50,
            "spa": 55,
            "retail_arcade": 30,
        },
        base_revenue_per_sf_annual=35,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
