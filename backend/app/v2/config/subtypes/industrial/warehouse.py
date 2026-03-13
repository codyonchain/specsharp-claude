from app.v2.config.master_config import (
    BuildingType,
    BuildingConfig,
    TradeBreakdown,
    SoftCosts,
    FinancingTerms,
    OwnershipType,
    NLPConfig,
)


CONFIG = (
    BuildingType.INDUSTRIAL,
    "warehouse",
    BuildingConfig(
        display_name="Class A Distribution Warehouse",
        # Core & shell cost for bulk distribution (tilt-up / precast) in 2025.
        base_cost_per_sf=105,
        cost_range=(95, 125),
        scope_profile="industrial_shell",
        scope_items_profile="industrial_warehouse_structural_v1",
        dealshield_tile_profile="industrial_warehouse_v1",
        equipment_cost_per_sf=5,  # Dock equipment, minimal FFE
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.48,  # Large clear spans
            mechanical=0.11,  # Minimal HVAC
            electrical=0.15,
            plumbing=0.05,  # Minimal plumbing
            finishes=0.21,
        ),
        soft_costs=SoftCosts(
            design_fees=0.04,
            permits=0.02,
            legal=0.01,
            financing=0.025,
            contingency=0.06,
            testing=0.005,
            construction_management=0.02,
            startup=0.005,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.25,
                target_roi=0.07,  # Market standard 7% for warehouse
                amort_years=25,
                loan_term_years=10,
                interest_only_months=0,
            )
        },
        special_features={
            "loading_docks": {
                "basis": "COUNT_BASED",
                "value": 65000,
                "count_pricing_mode": "overage_above_default",
                "count_override_keys": [
                    "extra_loading_dock_count",
                    "extra_dock_count",
                    "loading_dock_count",
                    "dock_door_count",
                    "dock_count",
                ],
                "default_count_bands": [
                    {"label": "mid_box", "max_square_footage": 150000, "count": 4},
                    {"label": "regional", "max_square_footage": 300000, "count": 8},
                    {"label": "large_box", "max_square_footage": 600000, "count": 12},
                    {"label": "mega_box", "count": 16},
                ],
                "unit_label": "dock",
            },
            "office_buildout": {
                "basis": "AREA_SHARE_GSF",
                "value": 18,
                "area_share_of_gsf": 0.05,
            },
        },
        special_feature_pricing_statuses={
            "loading_docks": "included_in_baseline",
            "office_buildout": "included_in_baseline",
        },
        nlp=NLPConfig(
            keywords=[
                "warehouse",
                "storage",
                "distribution",
                "logistics",
                "fulfillment center",
                "bulk storage",
            ],
            priority=14,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.00,
            "Memphis": 0.96,
            "Atlanta": 1.02,
            "Chicago": 1.05,
            "Dallas": 1.00,
            "Los Angeles": 1.15,
            "New York": 1.12,
        },
        # Revenue metrics – Industrial is rent-per-SF with NNN structure.
        # Assume effective gross income ~ $12/SF/yr and 95% stabilized occ.
        base_revenue_per_sf_annual=11.5,
        occupancy_rate_base=0.95,
        occupancy_rate_premium=0.97,
        # Very lean expense load: 85–90% NOI margin.
        operating_margin_base=0.88,
        operating_margin_premium=0.90,
        # Add these expense ratios for operational efficiency calculations
        utility_cost_ratio=0.03,  # 3% - minimal HVAC, basic lighting
        property_tax_ratio=0.08,  # 8% - lower value industrial land
        insurance_cost_ratio=0.02,  # 2% - property and liability
        maintenance_cost_ratio=0.03,  # 3% - simple systems, dock maintenance
        management_fee_ratio=0.02,  # 2% - minimal management needed
        security_ratio=0.01,  # 1% - basic security systems
        reserves_ratio=0.02,  # 2% - capital reserves
        labor_cost_ratio=0.02,  # 2% - minimal staffing (security, maintenance)
        # Total operating ratio: ~15% (very efficient operations)
    ),
)
