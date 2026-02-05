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
    "distribution_center",
    BuildingConfig(
        display_name="Distribution Center",
        base_cost_per_sf=115,
        # Keep range consistent with base_cost_per_sf (avoid clamp/logic bugs)
        cost_range=(105, 135),
        scope_profile="industrial_shell",
        scope_items_profile="industrial_warehouse_structural_v1",
        equipment_cost_per_sf=8,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.50,
            mechanical=0.09,
            electrical=0.20,
            plumbing=0.04,
            finishes=0.17,
        ),
        soft_costs=SoftCosts(
            design_fees=0.045,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.065,
            testing=0.005,
            construction_management=0.025,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.25,
                target_roi=0.11,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "distribution center",
                "distribution",
                "DC",
                "cross-dock",
                "sorting facility",
                "hub",
            ],
            priority=15,
            incompatible_classes=[],
        ),
        # NOTE: Regional multipliers are now resolved globally via
        # resolve_location_context() in the unified regional system.
        # Keep this empty to avoid double-counting/misleading provenance.
        regional_multipliers={},
        special_features={
            "automated_sorting": 25,
            "refrigerated_area": 35,
            "loading_docks": 15,
            "extra_loading_docks": 20,
            "office_buildout": 18,
            "cold_storage": 40,
        },
        # Revenue metrics
        base_revenue_per_sf_annual=10,
        occupancy_rate_base=0.96,
        occupancy_rate_premium=0.98,
        operating_margin_base=0.68,
        operating_margin_premium=0.72,
    ),
)
