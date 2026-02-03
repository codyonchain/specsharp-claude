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
    "cafe",
    BuildingConfig(
        display_name="Cafe/Coffee Shop",
        base_cost_per_sf=300,  # Adjusted to industry standard
        cost_range=(275, 325),
        equipment_cost_per_sf=20,  # Coffee equipment mostly in base cost
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.23,
            mechanical=0.22,
            electrical=0.16,
            plumbing=0.14,
            finishes=0.25,
        ),
        soft_costs=SoftCosts(
            design_fees=0.045,  # 4.5% - simpler cafe design
            permits=0.015,  # 1.5%
            legal=0.005,  # 0.5%
            financing=0.02,  # 2% - shorter construction period
            contingency=0.045,  # 4.5% - simple, well-understood
            testing=0.005,  # 0.5% - coffee equipment testing
            construction_management=0.02,  # 2%
            startup=0.01,  # 1% - training, initial inventory
        ),  # Total: 16% soft costs (lower for simpler cafes)
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.68,
                debt_rate=0.063,
                equity_ratio=0.32,
                target_dscr=1.22,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "cafe",
                "coffee shop",
                "coffee house",
                "espresso bar",
                "coffee bar",
                "bakery cafe",
                "tea shop",
            ],
            priority=12,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.35,
            "San Francisco": 1.40,
        },
        special_features={
            "outdoor_seating": 20,  # Sidewalk/patio seating
            "drive_thru": 35,  # Coffee drive-thru
            "bakery_display": 15,  # Display cases
            "lounge_area": 20,  # Comfortable seating area
            "meeting_room": 25,  # Small meeting space
        },
        base_revenue_per_sf_annual=350,
        occupancy_rate_base=0.80,
        occupancy_rate_premium=0.85,
        operating_margin_base=0.11,
        operating_margin_premium=0.14,
        food_cost_ratio=0.30,
        labor_cost_ratio=0.35,
        beverage_cost_ratio=0.12,
        management_fee_ratio=0.04,
        utility_cost_ratio=0.03,
        maintenance_cost_ratio=0.02,
        marketing_ratio=0.03,
        insurance_cost_ratio=0.02,
        supply_cost_ratio=0.03,
    ),
)
