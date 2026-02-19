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
    "luxury_apartments",
    BuildingConfig(
        display_name="Class A / Luxury Apartments",
        base_cost_per_sf=185,
        cost_range=(165, 205),
        scope_items_profile="multifamily_luxury_apartments_structural_v1",
        dealshield_tile_profile="multifamily_luxury_apartments_v1",
        equipment_cost_per_sf=25,  # Appliances, fixtures
        typical_floors=4,
        trades=TradeBreakdown(
            structural=0.28,
            mechanical=0.22,
            electrical=0.12,
            plumbing=0.18,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,
            permits=0.02,
            legal=0.015,
            financing=0.03,
            contingency=0.08,
            testing=0.005,
            construction_management=0.03,
            startup=0.01,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.055,
                equity_ratio=0.25,
                target_dscr=1.25,
                target_roi=0.06,  # Market standard 6% for luxury apartments
            )
        },
        nlp=NLPConfig(
            keywords=[
                "luxury apartment",
                "class a",
                "high-end apartment",
                "luxury multifamily",
                "upscale apartment",
                "premium apartment",
            ],
            priority=5,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.45,
            "San Francisco": 1.50,
            "Miami": 1.20,
        },
        special_features={
            "rooftop_amenity": 35,
            "pool": 25,
            "fitness_center": 20,
            "parking_garage": 45,
            "concierge": 15,
        },
        base_revenue_per_sf_annual=36.0,
        base_revenue_per_unit_monthly=3500,  # Nashville luxury market rate
        units_per_sf=0.000909,  # ≈ 1 unit / 1,100 SF
        occupancy_rate_base=0.93,
        occupancy_rate_premium=0.90,
        operating_margin_base=0.65,
        operating_margin_premium=0.7,
        market_cap_rate=0.055,  # 5.5% for Nashville luxury apartments
        management_fee_ratio=0.04,
        maintenance_cost_ratio=0.08,
        utility_cost_ratio=0.03,
        insurance_cost_ratio=0.02,
        property_tax_ratio=0.10,
        marketing_ratio=0.02,
        reserves_ratio=0.03,
        security_ratio=0.02,
        supply_cost_ratio=0.01,
    ),
)
