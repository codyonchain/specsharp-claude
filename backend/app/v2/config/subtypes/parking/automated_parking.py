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
    BuildingType.PARKING,
    "automated_parking",
    BuildingConfig(
        display_name="Automated Parking System",
        base_cost_per_sf=185,
        cost_range=(165, 205),
        equipment_cost_per_sf=65,  # Automated systems
        typical_floors=6,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.30,  # Automated systems
            electrical=0.25,  # Controls and power
            plumbing=0.05,
            finishes=0.15,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.03,
            legal=0.02,
            financing=0.035,
            contingency=0.10,
            testing=0.02,  # System testing
            construction_management=0.04,
            startup=0.025,  # System commissioning
        ),
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
                "automated parking",
                "robotic parking",
                "mechanical parking",
                "puzzle parking",
                "stack parking",
                "tower parking",
            ],
            priority=49,
            incompatible_classes=[ProjectClass.RENOVATION, ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.90,
            "New York": 1.40,  # Space premium
            "San Francisco": 1.45,
            "Chicago": 1.22,
            "Miami": 1.15,
        },
        special_features={
            "retrieval_speed": 40,
            "redundant_systems": 35,
            "valet_interface": 20,
            "ev_charging_integration": 15,
        },
        base_revenue_per_sf_annual=80,
        base_revenue_per_space_monthly=250,
        spaces_per_sf=0.005,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.65,
        operating_margin_premium=0.72,
    ),
)
