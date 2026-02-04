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
    BuildingType.CIVIC,
    "courthouse",
    BuildingConfig(
        display_name="Courthouse",
        base_cost_per_sf=325,
        cost_range=(300, 350),
        equipment_cost_per_sf=30,
        typical_floors=4,
        trades=TradeBreakdown(
            structural=0.28,  # Security requirements
            mechanical=0.24,
            electrical=0.16,
            plumbing=0.13,
            finishes=0.19,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.015,
            legal=0.025,
            financing=0.025,
            contingency=0.09,
            testing=0.012,
            construction_management=0.04,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.80,
                debt_rate=0.038,
                equity_ratio=0.20,
                target_dscr=1.15,
                target_roi=0.0,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "courthouse",
                "court house",
                "justice center",
                "judicial center",
                "court building",
                "federal court",
                "district court",
            ],
            priority=40,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.42,
            "San Francisco": 1.45,
            "Chicago": 1.25,
            "Miami": 1.18,
        },
        special_features={
            "courtroom": 50,
            "jury_room": 25,
            "holding_cells": 40,
            "judges_chambers": 30,
            "security_screening": 35,
        },
        base_revenue_per_sf_annual=0,
        occupancy_rate_base=1.0,
        occupancy_rate_premium=1.0,
        operating_margin_base=0,
        operating_margin_premium=0,
    ),
)
