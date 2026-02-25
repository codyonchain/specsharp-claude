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
    BuildingType.PARKING,
    "surface_parking",
    BuildingConfig(
        display_name="Surface Parking Lot",
        base_cost_per_sf=18,  # Very low - just paving
        cost_range=(15, 21),
        equipment_cost_per_sf=2,  # Lighting, gates
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.60,  # Paving, grading
            mechanical=0.02,  # Minimal
            electrical=0.18,  # Lighting
            plumbing=0.05,  # Drainage
            finishes=0.15,  # Striping, signage
        ),
        soft_costs=SoftCosts(
            design_fees=0.03,
            permits=0.015,
            legal=0.01,
            financing=0.02,
            contingency=0.05,
            testing=0.005,
            construction_management=0.015,
            startup=0.005,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.30,
                target_roi=0.15,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "parking lot",
                "surface parking",
                "parking",
                "surface lot",
                "park and ride",
                "parking area",
            ],
            priority=46,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.90,
            "Memphis": 0.88,
            "New York": 1.25,
            "San Francisco": 1.30,
            "Chicago": 1.10,
            "Miami": 1.05,
        },
        special_features={
            "covered_parking": 25,
            "valet_booth": 15,
            "ev_charging": 10,
            "security_system": 8,
        },
        base_revenue_per_sf_annual=30,
        base_revenue_per_space_monthly=100,
        spaces_per_sf=0.003,
        occupancy_rate_base=0.80,
        occupancy_rate_premium=0.90,
        operating_margin_base=0.80,
        operating_margin_premium=0.85,
        dealshield_tile_profile="parking_surface_parking_v1",
        scope_profile="parking_surface_parking_structural_v1",
        scope_items_profile="parking_surface_parking_structural_v1",
    ),
)
