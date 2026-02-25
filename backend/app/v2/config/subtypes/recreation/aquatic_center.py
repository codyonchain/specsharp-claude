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
    "aquatic_center",
    BuildingConfig(
        dealshield_tile_profile="recreation_aquatic_center_v1",
        scope_items_profile="recreation_aquatic_center_structural_v1",
        display_name="Aquatic Center",
        base_cost_per_sf=325,
        cost_range=(300, 350),
        equipment_cost_per_sf=45,  # Pool equipment
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.30,  # Heavy HVAC and dehumidification
            electrical=0.15,
            plumbing=0.18,  # Pool systems
            finishes=0.12,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.025,
            legal=0.015,
            financing=0.03,
            contingency=0.09,
            testing=0.015,  # Water quality systems
            construction_management=0.035,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.038,
                equity_ratio=0.25,
                target_dscr=1.15,
                target_roi=0.0,
            ),
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.045,
                equity_ratio=0.15,
                grants_ratio=0.15,
                target_dscr=1.10,
                target_roi=0.0,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "aquatic center",
                "natatorium",
                "swimming pool",
                "pool",
                "water park",
                "swim center",
                "aquatics",
            ],
            priority=43,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.40,
            "San Francisco": 1.45,
            "Chicago": 1.22,
            "Miami": 1.10,  # Outdoor pools more common
        },
        special_features={
            "competition_pool": 60,
            "diving_well": 50,
            "lazy_river": 40,
            "water_slides": 45,
            "therapy_pool": 35,
        },
        base_revenue_per_sf_annual=45,
        occupancy_rate_base=0.65,
        occupancy_rate_premium=0.75,
        operating_margin_base=0.10,
        operating_margin_premium=0.18,
    ),
)
