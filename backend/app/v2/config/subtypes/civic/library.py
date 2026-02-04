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
    BuildingType.CIVIC,
    "library",
    BuildingConfig(
        display_name="Public Library",
        base_cost_per_sf=275,
        cost_range=(250, 300),
        equipment_cost_per_sf=25,
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.26,
            mechanical=0.24,
            electrical=0.15,
            plumbing=0.12,
            finishes=0.23,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.015,
            legal=0.015,
            financing=0.02,
            contingency=0.075,
            testing=0.01,
            construction_management=0.03,
            startup=0.012,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.038,
                equity_ratio=0.15,
                grants_ratio=0.10,  # Library grants
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "library",
                "public library",
                "branch library",
                "main library",
                "media center",
                "learning center",
            ],
            priority=38,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.38,
            "San Francisco": 1.42,
            "Chicago": 1.20,
            "Miami": 1.10,
        },
        special_features={
            "reading_room": 20,
            "computer_lab": 25,
            "childrens_area": 20,
            "meeting_rooms": 15,
            "archives": 30,
        },
        base_revenue_per_sf_annual=0,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0,
        operating_margin_premium=0,
    ),
)
