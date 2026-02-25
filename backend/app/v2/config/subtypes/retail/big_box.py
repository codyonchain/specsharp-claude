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
    "big_box",
    BuildingConfig(
        display_name="Big Box Retail",
        base_cost_per_sf=125,
        cost_range=(100, 150),
        equipment_cost_per_sf=3,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.35,
            mechanical=0.18,
            electrical=0.14,
            plumbing=0.08,
            finishes=0.25,
        ),
        soft_costs=SoftCosts(
            design_fees=0.04,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.06,
            testing=0.005,
            construction_management=0.02,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.72,
                debt_rate=0.06,
                equity_ratio=0.28,
                target_dscr=1.20,
                target_roi=0.09,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "big box",
                "anchor tenant",
                "department store",
                "superstore",
                "warehouse retail",
            ],
            priority=11,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.90,
            "Memphis": 0.88,
            "New York": 1.30,
            "San Francisco": 1.35,
        },
        special_features={
            "loading_dock": 20,
            "mezzanine": 25,
            "auto_center": 45,
            "garden_center": 30,
            "warehouse_racking": 15,
            "refrigerated_storage": 35,
            "curbside_pickup": 20,
        },
        dealshield_tile_profile="retail_big_box_v1",
        scope_items_profile="retail_big_box_structural_v1",
        base_revenue_per_sf_annual=25,
        base_sales_per_sf_annual=200,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.60,
        operating_margin_premium=0.65,
    ),
)
