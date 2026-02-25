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
    "transit_oriented",
    BuildingConfig(
        display_name="Transit-Oriented Development",
        base_cost_per_sf=275,
        cost_range=(250, 300),
        equipment_cost_per_sf=22,
        typical_floors=8,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.23,
            electrical=0.15,
            plumbing=0.16,
            finishes=0.21,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.03,
            legal=0.022,
            financing=0.032,
            contingency=0.09,
            testing=0.012,
            construction_management=0.035,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.68,
                debt_rate=0.058,
                equity_ratio=0.32,
                target_dscr=1.25,
                target_roi=0.12,
            ),
            OwnershipType.PPP: FinancingTerms(
                debt_ratio=0.60,
                debt_rate=0.045,
                equity_ratio=0.20,
                grants_ratio=0.20,  # Transit grants
                target_dscr=1.20,
                target_roi=0.08,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "TOD",
                "transit oriented",
                "transit development",
                "station area",
                "transit village",
                "metro development",
            ],
            priority=30,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,  # No transit
            "Memphis": 0.93,
            "New York": 1.50,  # High transit value
            "San Francisco": 1.55,
            "Chicago": 1.35,
            "Miami": 1.20,
        },
        dealshield_tile_profile="mixed_use_transit_oriented_v1",
        scope_items_profile="mixed_use_transit_oriented_structural_v1",
        special_features={
            "transit_plaza": 35,
            "bike_facility": 20,
            "pedestrian_bridge": 45,
            "public_art": 15,
        },
        base_revenue_per_sf_annual=35,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
