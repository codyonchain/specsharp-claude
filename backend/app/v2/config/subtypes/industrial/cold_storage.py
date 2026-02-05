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
    BuildingType.INDUSTRIAL,
    "cold_storage",
    BuildingConfig(
        display_name="Cold Storage Facility",
        base_cost_per_sf=175,
        cost_range=(150, 200),
        scope_profile="industrial_cold_storage",
        scope_items_profile="industrial_cold_storage_structural_v1",
        equipment_cost_per_sf=45,  # Refrigeration equipment
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.25,
            mechanical=0.35,  # Heavy refrigeration
            electrical=0.18,  # High power for refrigeration
            plumbing=0.10,
            finishes=0.12,
        ),
        soft_costs=SoftCosts(
            design_fees=0.06,
            permits=0.025,
            legal=0.015,
            financing=0.03,
            contingency=0.08,
            testing=0.015,  # More testing for systems
            construction_management=0.03,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.062,
                equity_ratio=0.30,
                target_dscr=1.35,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "cold storage",
                "freezer",
                "refrigerated",
                "frozen storage",
                "cooler",
                "cold chain",
            ],
            priority=18,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.32,
            "San Francisco": 1.38,
            "Chicago": 1.15,
            "Miami": 1.10,
        },
        special_features={
            "blast_freezer": 50,
            "multiple_temp_zones": 30,
            "automated_retrieval": 40,
            "under_slab_heating_protection": 18,
            "high_r_value_panel_upgrade": 12,
        },
        # Revenue metrics
        base_revenue_per_sf_annual=18.5,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.94,
        operating_margin_base=0.72,
        operating_margin_premium=0.75,
        # Add these expense ratios for operational efficiency calculations
        utility_cost_ratio=0.08,
        property_tax_ratio=0.07,  # 7% - specialized facility
        insurance_cost_ratio=0.03,  # 3% - higher due to product liability
        maintenance_cost_ratio=0.03,
        management_fee_ratio=0.03,  # 3% - specialized management
        security_ratio=0.01,
        reserves_ratio=0.02,
        labor_cost_ratio=0.05,  # 5% - specialized operators
        monitoring_cost_ratio=0.03,  # 3% - 24/7 temperature monitoring
        # Total operating ratio: ~30% (high due to refrigeration)
    ),
)
