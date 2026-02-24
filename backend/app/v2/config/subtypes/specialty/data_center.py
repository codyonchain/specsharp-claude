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
    "data_center",
    BuildingConfig(
        display_name="Data Center",
        base_cost_per_sf=1200,  # Very high due to infrastructure
        cost_range=(1000, 1400),
        equipment_cost_per_sf=400,  # Servers, cooling, UPS
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.15,
            mechanical=0.40,  # Massive cooling requirements
            electrical=0.30,  # Redundant power systems
            plumbing=0.05,
            finishes=0.10,
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.03,
            legal=0.02,
            financing=0.04,
            contingency=0.10,
            testing=0.02,  # Critical testing
            construction_management=0.04,
            startup=0.03,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.60,
                debt_rate=0.065,
                equity_ratio=0.40,
                target_dscr=1.35,
                target_roi=0.15,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "data center",
                "server farm",
                "colocation",
                "colo",
                "cloud facility",
                "computing center",
                "tier 3",
                "tier 4",
            ],
            priority=31,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.95,
            "Memphis": 0.93,
            "New York": 1.25,  # Less premium for data centers
            "San Francisco": 1.30,
            "Chicago": 1.15,
            "Miami": 1.10,
        },
        dealshield_tile_profile="specialty_data_center_v1",
        scope_items_profile="specialty_data_center_structural_v1",
        special_features={
            "tier_4_certification": 200,
            "redundant_power": 150,
            "security_system": 75,
            "fiber_connectivity": 100,
        },
        base_revenue_per_sf_annual=150,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.45,
        operating_margin_premium=0.55,
        utility_cost_ratio=0.25,
        property_tax_ratio=0.05,
        insurance_cost_ratio=0.04,
        maintenance_cost_ratio=0.10,
        management_fee_ratio=0.03,
        security_ratio=0.05,
        reserves_ratio=0.05,
        labor_cost_ratio=0.08,
        connectivity_ratio=0.05,
    ),
)
