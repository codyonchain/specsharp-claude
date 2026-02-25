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
    "office_residential",
    BuildingConfig(
        display_name="Office with Residential",
        base_cost_per_sf=245,
        cost_range=(220, 270),
        equipment_cost_per_sf=18,
        typical_floors=8,  # 3 office + 5 residential
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.24,
            electrical=0.15,
            plumbing=0.16,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.065,
            permits=0.025,
            legal=0.018,
            financing=0.03,
            contingency=0.085,
            testing=0.01,
            construction_management=0.032,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.060,
                equity_ratio=0.30,
                target_dscr=1.25,
                target_roi=0.10,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "office residential",
                "mixed use tower",
                "office with housing",
                "work live",
                "commercial residential",
            ],
            priority=27,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.48,
            "San Francisco": 1.52,
            "Chicago": 1.28,
            "Miami": 1.20,
        },
        dealshield_tile_profile="mixed_use_office_residential_v1",
        scope_items_profile="mixed_use_office_residential_structural_v1",
        special_features={
            "amenity_deck": 35,
            "business_center": 20,
            "conference_facility": 30,
        },
        base_revenue_per_sf_annual=35,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.93,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
