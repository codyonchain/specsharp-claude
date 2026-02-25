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
    "university",
    BuildingConfig(
        display_name="University Building",
        base_cost_per_sf=375,
        cost_range=(325, 425),
        equipment_cost_per_sf=50,  # Lab equipment, technology
        typical_floors=4,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.28,  # Complex systems
            electrical=0.16,
            plumbing=0.14,
            finishes=0.17,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.025,
            legal=0.02,
            financing=0.03,
            contingency=0.09,
            testing=0.015,
            construction_management=0.04,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.60,
                debt_rate=0.045,  # Tax-exempt bonds
                equity_ratio=0.15,
                philanthropy_ratio=0.20,  # Donations
                grants_ratio=0.05,
                target_dscr=1.20,
                target_roi=0.0,
            ),
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.08,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "university",
                "college",
                "academic building",
                "campus",
                "lecture hall",
                "classroom building",
                "higher education",
            ],
            priority=24,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.95,
            "Memphis": 0.93,
            "New York": 1.42,
            "San Francisco": 1.48,
            "Chicago": 1.22,
            "Miami": 1.15,
        },
        dealshield_tile_profile="educational_university_v1",
        scope_items_profile="educational_university_structural_v1",
        special_features={
            "lecture_hall": 45,
            "research_lab": 75,
            "clean_room": 100,
            "library": 40,
            "student_center": 35,
        },
        base_revenue_per_sf_annual=200,
        base_revenue_per_student_annual=25000,
        students_per_sf=0.004,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.15,
        operating_margin_premium=0.20,
    ),
)
