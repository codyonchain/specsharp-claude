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
    "stadium",
    BuildingConfig(
        display_name="Stadium / Arena",
        base_cost_per_sf=425,
        cost_range=(375, 475),
        equipment_cost_per_sf=55,  # Scoreboards, sound, lighting
        typical_floors=4,  # Multiple levels of seating
        trades=TradeBreakdown(
            structural=0.32,  # Major structural for seating
            mechanical=0.22,
            electrical=0.18,  # Field lighting, displays
            plumbing=0.13,
            finishes=0.15,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.03,
            legal=0.025,
            financing=0.035,
            contingency=0.10,
            testing=0.012,
            construction_management=0.04,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.038,
                equity_ratio=0.30,
                target_dscr=1.20,
                target_roi=0.0,
            ),
            OwnershipType.PPP: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.045,
                equity_ratio=0.20,
                grants_ratio=0.15,
                target_dscr=1.25,
                target_roi=0.06,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "stadium",
                "arena",
                "coliseum",
                "ballpark",
                "football stadium",
                "baseball stadium",
                "soccer stadium",
                "sports venue",
            ],
            priority=45,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.92,
            "Memphis": 0.93,
            "New York": 1.45,
            "San Francisco": 1.50,
            "Chicago": 1.28,
            "Miami": 1.20,
        },
        special_features={
            "luxury_boxes": 75,
            "club_level": 50,
            "press_box": 40,
            "video_board": 100,
            "retractable_roof": 200,
        },
        base_revenue_per_sf_annual=250,
        base_revenue_per_seat_annual=500,
        seats_per_sf=0.05,
        occupancy_rate_base=0.40,
        occupancy_rate_premium=0.50,
        operating_margin_base=0.20,
        operating_margin_premium=0.30,
    ),
)
