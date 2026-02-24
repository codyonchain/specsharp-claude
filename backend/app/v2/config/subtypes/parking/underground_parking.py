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
    "underground_parking",
    BuildingConfig(
        display_name="Underground Parking",
        base_cost_per_sf=125,  # Expensive excavation
        cost_range=(110, 140),
        equipment_cost_per_sf=12,
        typical_floors=2,  # Below grade levels
        trades=TradeBreakdown(
            structural=0.40,  # Major excavation and structure
            mechanical=0.15,  # Ventilation critical
            electrical=0.15,
            plumbing=0.10,  # Drainage, pumps
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.06,
            permits=0.025,
            legal=0.015,
            financing=0.03,
            contingency=0.08,
            testing=0.012,  # Waterproofing tests
            construction_management=0.03,
            startup=0.01,
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
                "underground parking",
                "subterranean parking",
                "basement parking",
                "below grade parking",
                "underground garage",
            ],
            priority=48,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.45,  # High land value
            "San Francisco": 1.50,
            "Chicago": 1.25,
            "Miami": 1.05,  # Water table issues
        },
        special_features={
            "waterproofing": 35,
            "sump_pumps": 20,
            "vehicle_lifts": 30,
            "security_booth": 15,
            "ventilation_upgrade": 25,
        },
        base_revenue_per_sf_annual=60,
        base_revenue_per_space_monthly=200,
        spaces_per_sf=0.0035,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.70,
        operating_margin_premium=0.75,
    ),
)
