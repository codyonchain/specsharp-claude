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
    "full_service",
    BuildingConfig(
        display_name="Full Service Restaurant",
        base_cost_per_sf=385,  # Optimized for industry standards ($450-500/SF total)
        cost_range=(350, 425),
        equipment_cost_per_sf=25,  # Optimized - kitchen equipment mostly in base cost
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.20,
            mechanical=0.30,
            electrical=0.16,
            plumbing=0.14,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,  # 5% - simpler design than complex buildings
            permits=0.015,  # 1.5%
            legal=0.005,  # 0.5%
            financing=0.02,  # 2% - shorter construction period
            contingency=0.05,  # 5% - well-understood building type
            testing=0.005,  # 0.5% - kitchen equipment testing
            construction_management=0.025,  # 2.5%
            startup=0.01,  # 1% - training, initial inventory
        ),  # Total: 18% soft costs
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.60,
                debt_rate=0.068,
                equity_ratio=0.40,
                target_dscr=1.30,
                target_roi=0.15,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "restaurant",
                "dining",
                "sit-down",
                "full service",
                "casual dining",
                "family restaurant",
            ],
            priority=13,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.95,
            "Memphis": 0.93,
            "New York": 1.40,
            "San Francisco": 1.45,
        },
        special_features={
            "outdoor_seating": 25,  # Patio/sidewalk dining
            "bar": 35,  # Full bar setup
            "private_dining": 30,  # Private dining rooms
            "wine_cellar": 45,  # Temperature-controlled wine storage
            "live_kitchen": 25,  # Open/exhibition kitchen
            "rooftop_dining": 50,  # Rooftop terrace dining
            "valet_parking": 20,  # Valet setup
        },
        base_revenue_per_sf_annual=350,
        occupancy_rate_base=0.80,
        occupancy_rate_premium=0.90,
        operating_margin_base=0.10,
        operating_margin_premium=0.12,
        food_cost_ratio=0.32,
        labor_cost_ratio=0.33,
        beverage_cost_ratio=0.15,
        management_fee_ratio=0.05,
        utility_cost_ratio=0.04,
        maintenance_cost_ratio=0.03,
        marketing_ratio=0.03,
        insurance_cost_ratio=0.02,
        supply_cost_ratio=0.02,
    ),
)
