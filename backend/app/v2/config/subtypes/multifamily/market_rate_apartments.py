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
    BuildingType.MULTIFAMILY,
    "market_rate_apartments",
    BuildingConfig(
        display_name="Class B / Market Rate Apartments",
        base_cost_per_sf=145,
        cost_range=(130, 160),
        dealshield_tile_profile="multifamily_market_rate_apartments_v1",
        equipment_cost_per_sf=15,
        typical_floors=3,
        trades=TradeBreakdown(
            structural=0.30,
            mechanical=0.20,
            electrical=0.12,
            plumbing=0.18,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.045,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.07,
            testing=0.005,
            construction_management=0.025,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.20,
                target_roi=0.10,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "apartment",
                "multifamily",
                "market rate",
                "class b",
                "rental housing",
                "apartment complex",
            ],
            priority=6,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.90,
            "Memphis": 0.88,
            "New York": 1.40,
            "San Francisco": 1.45,
        },
        base_revenue_per_sf_annual=28.5,
        base_revenue_per_unit_monthly=2000,
        units_per_sf=0.00125,  # ≈ 1 unit / 800 SF
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.6,
        operating_margin_premium=0.65,
        market_cap_rate=0.065,  # 6.5% for market rate apartments
        management_fee_ratio=0.05,
        maintenance_cost_ratio=0.07,
        utility_cost_ratio=0.04,
        insurance_cost_ratio=0.02,
        property_tax_ratio=0.12,
        marketing_ratio=0.02,
        reserves_ratio=0.02,
        supply_cost_ratio=0.01,
    ),
)
