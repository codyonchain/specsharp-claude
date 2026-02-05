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
    "quick_service",
    BuildingConfig(
        display_name="Quick Service Restaurant",
        base_cost_per_sf=360,
        cost_range=(250, 350),
        cost_clamp={"min_cost_per_sf": 250, "max_cost_per_sf": 700},
        scope_items_profile="restaurant_quick_service_structural_v1",
        equipment_cost_per_sf=40,  # Kitchen equipment mostly in base cost
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.22,
            mechanical=0.28,
            electrical=0.15,
            plumbing=0.15,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.055,
            permits=0.02,
            legal=0.007,
            financing=0.02,
            contingency=0.06,
            testing=0.005,
            construction_management=0.03,
            startup=0.015,
        ),  # Total: 18% soft costs
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "fast food",
                "quick service",
                "QSR",
                "drive through",
                "fast casual",
                "takeout",
            ],
            priority=12,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.35,
            "San Francisco": 1.40,
        },
        special_features={
            "drive_thru": 40,  # Drive-thru lane and window
            "outdoor_seating": 20,  # Patio seating area
            "play_area": 35,  # Children's playground
            "double_drive_thru": 55,  # Dual drive-thru lanes
            "digital_menu_boards": 15,  # Digital ordering displays
        },
        base_revenue_per_sf_annual=525,
        occupancy_rate_base=0.88,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.12,
        operating_margin_premium=0.18,
        food_cost_ratio=0.28,
        labor_cost_ratio=0.30,
        beverage_cost_ratio=0.08,
        management_fee_ratio=0.04,
        utility_cost_ratio=0.04,
        maintenance_cost_ratio=0.03,
        marketing_ratio=0.04,
        franchise_fee_ratio=0.06,
        insurance_cost_ratio=0.02,
    ),
)
