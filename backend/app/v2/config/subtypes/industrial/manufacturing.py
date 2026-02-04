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
    "manufacturing",
    BuildingConfig(
        display_name="Manufacturing Facility",
        base_cost_per_sf=120,
        cost_range=(100, 150),
        scope_profile="industrial_manufacturing",
        # General manufacturing allowance (fixtures, light process interfaces)
        equipment_cost_per_sf=20,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.30,
            mechanical=0.22,
            electrical=0.18,
            plumbing=0.10,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.06,
            permits=0.025,
            legal=0.015,
            financing=0.03,
            contingency=0.08,
            testing=0.01,
            construction_management=0.03,
            startup=0.015,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.70,
                debt_rate=0.062,
                equity_ratio=0.30,
                target_dscr=1.20,
                target_roi=0.08,  # Market standard 8% for manufacturing
            )
        },
        nlp=NLPConfig(
            keywords=[
                "manufacturing",
                "factory",
                "production",
                "plant",
                "assembly",
                "fabrication",
                "processing",
            ],
            priority=16,
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.35,
            "San Francisco": 1.40,
            "Chicago": 1.15,
            "Miami": 1.08,
        },
        special_features={
            # Specialized manufacturing features (opt-in only)
            "clean_room": 75,
            "heavy_power": 40,
            "crane_bays": 30,
            "compressed_air": 20,
        },
        # Revenue metrics
        # Slight premium to DC, but not enough to offset added risk by default
        base_revenue_per_sf_annual=11,
        occupancy_rate_base=0.92,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.65,
        operating_margin_premium=0.70,
        # Add these expense ratios for operational efficiency calculations
        utility_cost_ratio=0.08,  # 8% - production equipment power
        property_tax_ratio=0.06,  # 6% - industrial zones
        insurance_cost_ratio=0.03,  # 3% - higher due to equipment/liability
        maintenance_cost_ratio=0.06,  # 6% - equipment maintenance critical
        management_fee_ratio=0.02,  # 2% - facility management
        security_ratio=0.01,  # 1% - standard security
        reserves_ratio=0.03,  # 3% - equipment replacement reserves
        labor_cost_ratio=0.35,  # 35% - production staff (if included)
        raw_materials_ratio=0.25,  # 25% - materials for production
        # Total operating ratio: ~25% facility costs (excluding production labor/materials)
    ),
)
