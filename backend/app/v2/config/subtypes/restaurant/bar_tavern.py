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
    BuildingType.RESTAURANT,
    "bar_tavern",
    BuildingConfig(
        display_name="Bar/Tavern",
        base_cost_per_sf=350,  # Adjusted to industry standard
        cost_range=(325, 375),
        cost_clamp={"min_cost_per_sf": 250, "max_cost_per_sf": 700},
        equipment_cost_per_sf=25,  # Bar equipment included in base cost
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.22,
            mechanical=0.25,
            electrical=0.18,
            plumbing=0.15,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,  # 5% - simpler design than complex buildings
            permits=0.02,  # 2% - includes liquor license
            legal=0.01,  # 1% - includes liquor license legal
            financing=0.02,  # 2% - shorter construction period
            contingency=0.05,  # 5% - well-understood building type
            testing=0.005,  # 0.5% - bar equipment testing
            construction_management=0.025,  # 2.5%
            startup=0.01,  # 1% - training, initial inventory
        ),  # Total: 19% soft costs (slightly higher for liquor licensing)
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.14,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "bar",
                "tavern",
                "pub",
                "lounge",
                "nightclub",
                "cocktail bar",
                "sports bar",
                "brewpub",
            ],
            priority=13,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.38,
            "San Francisco": 1.42,
        },
        special_features={
            "outdoor_seating": 25,  # Patio/beer garden
            "live_music_stage": 30,  # Performance stage
            "game_room": 25,  # Pool tables, darts, etc.
            "rooftop_bar": 50,  # Rooftop bar area
            "private_party_room": 30,  # Private event space
            "craft_beer_system": 35,  # Specialized tap system
        },
        base_revenue_per_sf_annual=450,
        occupancy_rate_base=0.80,
        occupancy_rate_premium=0.88,
        operating_margin_base=0.14,
        operating_margin_premium=0.18,
        food_cost_ratio=0.25,
        labor_cost_ratio=0.28,
        beverage_cost_ratio=0.20,
        management_fee_ratio=0.05,
        utility_cost_ratio=0.03,
        maintenance_cost_ratio=0.03,
        marketing_ratio=0.04,
        insurance_cost_ratio=0.03,
        security_ratio=0.02,
    ),
)
