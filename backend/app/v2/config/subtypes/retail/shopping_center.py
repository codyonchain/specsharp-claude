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
    BuildingType.RETAIL,
    "shopping_center",
    BuildingConfig(
        display_name="Shopping Center",
        base_cost_per_sf=150,
        cost_range=(125, 175),
        equipment_cost_per_sf=5,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.30,
            mechanical=0.20,
            electrical=0.15,
            plumbing=0.10,
            finishes=0.25,
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,
            permits=0.02,
            legal=0.015,
            financing=0.025,
            contingency=0.07,
            testing=0.005,
            construction_management=0.025,
            startup=0.01,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.058,
                equity_ratio=0.30,
                target_dscr=1.25,
                target_roi=0.10,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "shopping center",
                "retail center",
                "strip mall",
                "strip center",
                "plaza",
                "shopping plaza",
            ],
            priority=10,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.35,
            "San Francisco": 1.40,
        },
        special_features={
            "covered_walkway": 20,
            "loading_dock": 25,
            "monument_signage": 15,
            "outdoor_seating": 20,
            "drive_thru": 40,
            "storage_units": 15,
        },
        dealshield_tile_profile="retail_shopping_center_v1",
        scope_items_profile="retail_shopping_center_structural_v1",
        base_revenue_per_sf_annual=35,
        base_sales_per_sf_annual=350,
        occupancy_rate_base=0.92,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.65,
        operating_margin_premium=0.70,
    ),
)
