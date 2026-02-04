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
    "community_college",
    BuildingConfig(
        display_name="Community College",
        base_cost_per_sf=295,
        cost_range=(270, 320),
        equipment_cost_per_sf=30,
        typical_floors=2,
        trades=TradeBreakdown(
            structural=0.27,
            mechanical=0.25,
            electrical=0.14,
            plumbing=0.14,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.06,
            permits=0.02,
            legal=0.015,
            financing=0.025,
            contingency=0.075,
            testing=0.01,
            construction_management=0.03,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.04,
                equity_ratio=0.25,
                grants_ratio=0.10,
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "community college",
                "junior college",
                "technical college",
                "vocational school",
                "trade school",
            ],
            priority=25,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.35,
            "San Francisco": 1.40,
            "Chicago": 1.15,
            "Miami": 1.08,
        },
        special_features={
            "vocational_lab": 40,
            "computer_lab": 25,
            "library": 20,
            "student_services": 15,
        },
        base_revenue_per_sf_annual=150,
        base_revenue_per_student_annual=8000,
        students_per_sf=0.005,
        occupancy_rate_base=0.85,
        occupancy_rate_premium=0.92,
        operating_margin_base=0.08,
        operating_margin_premium=0.12,
    ),
)
