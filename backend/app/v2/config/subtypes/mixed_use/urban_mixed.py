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
    "urban_mixed",
    BuildingConfig(
        display_name="Urban Mixed Use",
        base_cost_per_sf=265,
        cost_range=(240, 290),
        equipment_cost_per_sf=25,
        typical_floors=12,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.24,
            electrical=0.15,
            plumbing=0.16,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.028,
            legal=0.02,
            financing=0.032,
            contingency=0.09,
            testing=0.012,
            construction_management=0.035,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.060,
                equity_ratio=0.30,
                target_dscr=1.25,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "urban mixed",
                "mixed use development",
                "multi-use",
                "live work play",
                "vertical mixed",
            ],
            priority=29,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.48,
            "San Francisco": 1.55,
            "Chicago": 1.30,
            "Miami": 1.22,
        },
        dealshield_tile_profile="mixed_use_urban_mixed_v1",
        scope_items_profile="mixed_use_urban_mixed_structural_v1",
        special_features={
            "public_plaza": 40,
            "green_roof": 35,
            "parking_structure": 45,
            "transit_connection": 30,
        },
        base_revenue_per_sf_annual=35,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
