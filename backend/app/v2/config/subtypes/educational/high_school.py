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
    "high_school",
    BuildingConfig(
        display_name="High School",
        base_cost_per_sf=315,
        cost_range=(290, 340),
        equipment_cost_per_sf=35,
        typical_floors=3,
        trades=TradeBreakdown(
            structural=0.26,
            mechanical=0.26,  # Labs need ventilation
            electrical=0.15,
            plumbing=0.15,
            finishes=0.18,
        ),
        soft_costs=SoftCosts(
            design_fees=0.075,
            permits=0.022,
            legal=0.015,
            financing=0.025,
            contingency=0.085,
            testing=0.012,
            construction_management=0.04,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.04,
                equity_ratio=0.20,
                grants_ratio=0.15,
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "high school",
                "secondary school",
                "senior high",
                "grades 9-12",
                "preparatory school",
            ],
            priority=2,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.40,
            "San Francisco": 1.45,
            "Chicago": 1.20,
            "Miami": 1.12,
        },
        special_features={
            "stadium": 60,
            "field_house": 50,
            "performing_arts_center": 55,
            "science_labs": 40,
            "vocational_shops": 45,
            "media_center": 30,
        },
        base_revenue_per_sf_annual=0,
        base_revenue_per_student_annual=14000,
        students_per_sf=0.005,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.05,
        operating_margin_premium=0.08,
    ),
)
