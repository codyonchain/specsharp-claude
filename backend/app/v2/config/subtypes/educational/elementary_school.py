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
    BuildingType.EDUCATIONAL,
    "elementary_school",
    BuildingConfig(
        display_name="Elementary School",
        base_cost_per_sf=285,
        cost_range=(260, 310),
        equipment_cost_per_sf=25,  # Classroom equipment, playground
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.28,
            mechanical=0.24,  # Good ventilation crucial
            electrical=0.13,
            plumbing=0.15,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.07,
            permits=0.02,
            legal=0.015,
            financing=0.025,
            contingency=0.08,
            testing=0.01,
            construction_management=0.035,
            startup=0.01,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.04,  # Municipal bonds
                equity_ratio=0.20,
                grants_ratio=0.15,
                target_dscr=1.15,
                target_roi=0.0,  # Public good
            )
        },
        nlp=NLPConfig(
            keywords=[
                "elementary school",
                "primary school",
                "grade school",
                "K-5",
                "K-6",
                "elementary",
            ],
            priority=2,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.38,
            "San Francisco": 1.42,
            "Chicago": 1.18,
            "Miami": 1.10,
        },
        special_features={
            "gymnasium": 35,
            "cafeteria": 30,
            "playground": 20,
            "computer_lab": 25,
            "library": 25,
        },
        base_revenue_per_sf_annual=0,
        base_revenue_per_student_annual=12000,
        students_per_sf=0.00667,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.05,
        operating_margin_premium=0.08,
    ),
)
