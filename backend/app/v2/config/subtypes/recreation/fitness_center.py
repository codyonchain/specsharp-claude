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
    BuildingType.RECREATION,
    "fitness_center",
    BuildingConfig(
        display_name="Fitness Center / Gym",
        base_cost_per_sf=185,
        cost_range=(165, 205),
        equipment_cost_per_sf=35,  # Exercise equipment
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.26,
            mechanical=0.25,  # Heavy HVAC for workout areas
            electrical=0.14,
            plumbing=0.15,  # Showers, pools
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,
            permits=0.02,
            legal=0.015,
            financing=0.025,
            contingency=0.07,
            testing=0.008,
            construction_management=0.025,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.062,
                equity_ratio=0.30,
                target_dscr=1.25,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "gym",
                "fitness center",
                "health club",
                "workout",
                "YMCA",
                "athletic club",
                "crossfit",
                "wellness center",
            ],
            priority=41,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.35,
            "San Francisco": 1.40,
            "Chicago": 1.15,
            "Miami": 1.12,
        },
        special_features={
            "pool": 45,
            "basketball_court": 30,
            "group_fitness": 20,
            "spa_area": 35,
            "juice_bar": 15,
        },
        base_revenue_per_sf_annual=60,
        occupancy_rate_base=0.75,
        occupancy_rate_premium=0.85,
        operating_margin_base=0.20,
        operating_margin_premium=0.30,
    ),
)
