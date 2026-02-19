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
    "affordable_housing",
    BuildingConfig(
        display_name="Affordable Housing",
        base_cost_per_sf=120,
        cost_range=(110, 130),
        dealshield_tile_profile="multifamily_affordable_housing_v1",
        equipment_cost_per_sf=10,
        typical_floors=3,
        trades=TradeBreakdown(
            structural=0.32,
            mechanical=0.18,
            electrical=0.12,
            plumbing=0.18,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.04,
            permits=0.02,
            legal=0.02,  # Higher for compliance
            financing=0.02,  # Often subsidized
            contingency=0.06,
            testing=0.005,
            construction_management=0.025,
            startup=0.005,
        ),
        ownership_types={
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.50,
                debt_rate=0.04,  # Tax-exempt bonds
                equity_ratio=0.10,
                philanthropy_ratio=0.15,
                grants_ratio=0.25,  # LIHTC, etc.
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "affordable housing",
                "workforce housing",
                "section 8",
                "LIHTC",
                "low income",
                "subsidized housing",
            ],
            priority=7,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.88,
            "Memphis": 0.86,
            "New York": 1.35,
            "San Francisco": 1.40,
        },
        base_revenue_per_sf_annual=20.0,
        base_revenue_per_unit_monthly=1200,
        units_per_sf=0.00143,  # ≈ 1 unit / 700 SF
        occupancy_rate_base=0.97,
        occupancy_rate_premium=0.96,
        operating_margin_base=0.55,
        operating_margin_premium=0.6,
        market_cap_rate=0.075,  # 7.5% for affordable housing
        management_fee_ratio=0.06,
        maintenance_cost_ratio=0.09,
        utility_cost_ratio=0.05,
        insurance_cost_ratio=0.03,
        property_tax_ratio=0.08,
        marketing_ratio=0.01,
        reserves_ratio=0.04,
        security_ratio=0.01,
        supply_cost_ratio=0.01,
    ),
)
