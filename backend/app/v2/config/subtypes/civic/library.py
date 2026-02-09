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
    BuildingType.CIVIC,
    "library",
    BuildingConfig(
        display_name="Public Library",
        base_cost_per_sf=275,
        cost_range=(250, 300),
        equipment_cost_per_sf=25,
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.28,  # Higher loads from dense book stacks
            mechanical=0.25,  # Ventilation and thermal control for community/maker areas
            electrical=0.16,  # Daylighting controls, AV, and maker-space power density
            plumbing=0.13,
            finishes=0.18,  # Acoustic treatments are carried in feature adders
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
                debt_ratio=0.70,
                debt_rate=0.038,
                equity_ratio=0.20,
                grants_ratio=0.10,
                target_dscr=1.15,
                target_roi=0.0,
            ),
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.60,
                debt_rate=0.045,
                equity_ratio=0.15,
                philanthropy_ratio=0.15,
                grants_ratio=0.10,
                target_dscr=1.10,
                target_roi=0.0,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "library",
                "public library",
                "branch library",
                "main library",
                "media center",
                "learning center",
                "learning commons",
                "community library",
                "library makerspace",
            ],
            priority=38,
            incompatible_classes=[],
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
            "stacks_load_reinforcement": 35,
            "acoustic_treatment": 25,
            "daylighting_controls": 20,
            "community_rooms": 20,
            "maker_space_mep": 40,
        },
        base_revenue_per_sf_annual=0,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0,
        operating_margin_premium=0,
    ),
)
