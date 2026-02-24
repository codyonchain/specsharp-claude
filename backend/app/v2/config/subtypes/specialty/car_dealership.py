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
    BuildingType.SPECIALTY,
    "car_dealership",
    BuildingConfig(
        display_name="Car Dealership",
        base_cost_per_sf=185,
        cost_range=(165, 205),
        equipment_cost_per_sf=15,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.28,
            mechanical=0.20,
            electrical=0.15,
            plumbing=0.10,
            finishes=0.27,  # Showroom finishes
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,
            permits=0.02,
            legal=0.015,
            financing=0.028,
            contingency=0.07,
            testing=0.008,
            construction_management=0.025,
            startup=0.012,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.062,
                equity_ratio=0.30,
                target_dscr=1.22,
                target_roi=0.10,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "car dealership",
                "auto dealership",
                "vehicle showroom",
                "car showroom",
                "auto mall",
                "dealership",
            ],
            priority=34,
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
            "Miami": 1.10,
        },
        dealshield_tile_profile="specialty_car_dealership_v1",
        scope_items_profile="specialty_car_dealership_structural_v1",
        special_features={
            "service_center": 45,
            "detail_bay": 25,
            "parts_warehouse": 20,
            "car_wash": 30,
        },
        base_revenue_per_sf_annual=250,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0.08,
        operating_margin_premium=0.12,
    ),
)
