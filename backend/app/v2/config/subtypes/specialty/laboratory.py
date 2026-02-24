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
    BuildingType.SPECIALTY,
    "laboratory",
    BuildingConfig(
        display_name="Laboratory / Research Facility",
        base_cost_per_sf=450,
        cost_range=(400, 500),
        equipment_cost_per_sf=125,
        typical_floors=3,
        trades=TradeBreakdown(
            structural=0.22,
            mechanical=0.32,  # Specialized ventilation
            electrical=0.18,
            plumbing=0.16,  # Gas, water, waste systems
            finishes=0.12,
        ),
        soft_costs=SoftCosts(
            design_fees=0.09,
            permits=0.03,
            legal=0.02,
            financing=0.035,
            contingency=0.10,
            testing=0.02,
            construction_management=0.04,
            startup=0.025,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.12,
            ),
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.045,
                equity_ratio=0.10,
                grants_ratio=0.20,  # Research grants
                target_dscr=1.20,
                target_roi=0.0,
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "laboratory",
                "lab",
                "research facility",
                "R&D",
                "biotech",
                "clean room",
                "research center",
                "testing facility",
            ],
            priority=32,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.95,
            "Memphis": 0.93,
            "New York": 1.40,
            "San Francisco": 1.45,  # Biotech hub
            "Chicago": 1.20,
            "Miami": 1.12,
        },
        dealshield_tile_profile="specialty_laboratory_v1",
        scope_items_profile="specialty_laboratory_structural_v1",
        special_features={
            "cleanroom_suite": 95,
            "vivarium_support": 70,
            "process_gas_distribution": 65,
            "redundancy_exhaust_stack": 50,
        },
        base_revenue_per_sf_annual=75,
        occupancy_rate_base=0.88,
        occupancy_rate_premium=0.94,
        operating_margin_base=0.35,
        operating_margin_premium=0.42,
    ),
)
