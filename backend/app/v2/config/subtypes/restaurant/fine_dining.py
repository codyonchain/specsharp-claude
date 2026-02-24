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
    "fine_dining",
    BuildingConfig(
        display_name="Fine Dining Restaurant",
        base_cost_per_sf=550,  # Premium construction and finishes
        cost_range=(500, 650),
        cost_clamp={"min_cost_per_sf": 250},
        scope_items_profile="restaurant_fine_dining_structural_v1",
        dealshield_tile_profile="restaurant_fine_dining_v1",
        equipment_cost_per_sf=50,  # High-end kitchen equipment
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.18,
            mechanical=0.28,  # Advanced HVAC for comfort
            electrical=0.18,  # Sophisticated lighting systems
            plumbing=0.14,
            finishes=0.22,  # Premium finishes and materials
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,  # 8% - high-end design and architects
            permits=0.02,  # 2%
            legal=0.01,  # 1%
            financing=0.03,  # 3% - larger investment
            contingency=0.08,  # 8% - complex finishes
            testing=0.01,  # 1% - extensive equipment testing
            construction_management=0.04,  # 4% - more oversight needed
            startup=0.02,  # 2% - extensive training
        ),  # Total: 29% soft costs
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.55,
                debt_rate=0.07,
                equity_ratio=0.45,
                target_dscr=1.35,
                target_roi=0.18,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "fine dining",
                "upscale",
                "white tablecloth",
                "gourmet",
                "haute cuisine",
                "michelin",
                "tasting menu",
            ],
            priority=14,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.04,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.45,
            "San Francisco": 1.50,
        },
        special_features={
            "wine_cellar": 60,  # Premium wine storage
            "private_dining": 45,  # Multiple private rooms
            "chef_table": 40,  # Chef's table experience
            "dry_aging_room": 50,  # Meat aging facility
            "pastry_kitchen": 35,  # Separate pastry kitchen
            "sommelier_station": 30,  # Wine service station
            "valet_parking": 25,  # Valet required
        },
        base_revenue_per_sf_annual=750,
        occupancy_rate_base=0.82,
        occupancy_rate_premium=0.85,
        operating_margin_base=0.12,
        operating_margin_premium=0.18,
        food_cost_ratio=0.28,
        labor_cost_ratio=0.35,
        beverage_cost_ratio=0.18,
        management_fee_ratio=0.06,
        utility_cost_ratio=0.03,
        maintenance_cost_ratio=0.03,
        marketing_ratio=0.02,
        insurance_cost_ratio=0.02,
        supply_cost_ratio=0.03,
    ),
)
