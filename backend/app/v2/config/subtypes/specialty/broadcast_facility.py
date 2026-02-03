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
    "broadcast_facility",
    BuildingConfig(
        display_name="Broadcast / Studio Facility",
        base_cost_per_sf=325,
        cost_range=(300, 350),
        equipment_cost_per_sf=75,  # Studio equipment
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.24,
            mechanical=0.26,  # Sound isolation HVAC
            electrical=0.20,  # High power for equipment
            plumbing=0.10,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.025,
            legal=0.018,
            financing=0.03,
            contingency=0.08,
            testing=0.015,
            construction_management=0.03,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "broadcast",
                "studio",
                "television station",
                "radio station",
                "recording studio",
                "production facility",
                "soundstage",
            ],
            priority=35,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,  # Music city
            "Manchester": 0.92,
            "Memphis": 0.94,
            "New York": 1.45,
            "San Francisco": 1.40,
            "Chicago": 1.20,
            "Miami": 1.15,
        },
        special_features={
            "sound_stage": 60,
            "control_room": 45,
            "green_screen": 30,
            "acoustic_treatment": 40,
            "broadcast_tower": 100,
        },
        base_revenue_per_sf_annual=100,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.25,
        operating_margin_premium=0.35,
    ),
)
