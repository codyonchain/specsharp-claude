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
    "flex_space",
    BuildingConfig(
        display_name="Flex Industrial",
        # Hybrid: warehouse/light industrial shell + meaningful office/showroom.
        # Should feel more finished than bulk warehouse, but not “Office”.
        base_cost_per_sf=115,
        cost_range=(100, 135),
        equipment_cost_per_sf=10,
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.31,
            mechanical=0.19,  # more HVAC than warehouse (office/showroom), less than manufacturing
            electrical=0.14,  # more lighting + branch power than warehouse
            plumbing=0.08,
            finishes=0.28,  # higher interior finish load vs warehouse
        ),
        soft_costs=SoftCosts(
            design_fees=0.05,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.07,
            testing=0.005,
            construction_management=0.025,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.72,
                debt_rate=0.060,
                equity_ratio=0.28,
                target_dscr=1.22,
                target_roi=0.10,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "flex industrial",
                "flex space",
                "flex",
                "warehouse office",
                "showroom",
                "light industrial",
                "r&d space",
                "tech space",
            ],
            priority=17,
            incompatible_classes=[],
        ),
        # Keep existing multipliers unchanged to avoid shifting regional behavior in this patch cycle.
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.93,
            "Memphis": 0.91,
            "New York": 1.30,
            "San Francisco": 1.35,
            "Chicago": 1.12,
            "Miami": 1.07,
        },
        # Revenue metrics — Flex typically rents higher than bulk warehouse (often still NNN-ish).
        base_revenue_per_sf_annual=14.5,
        occupancy_rate_base=0.93,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.84,
        operating_margin_premium=0.87,
        # Op-ex ratios (leaner than Office; slightly higher than bulk warehouse due to office/showroom)
        utility_cost_ratio=0.04,
        property_tax_ratio=0.09,
        insurance_cost_ratio=0.02,
        maintenance_cost_ratio=0.03,
        management_fee_ratio=0.03,
        janitorial_ratio=0.01,
        security_ratio=0.01,
        reserves_ratio=0.02,
        # Specialization should be opt-in (explicit adders)
        special_features={
            "enhanced_office_showroom_finish": 18,
            "two_story_office_mezzanine": 12,
            "heavy_power": 20,
            "clean_room": 60,
            "crane_bays": 28,
            "compressed_air": 10,
            "lab_buildout": 35,
        },
    ),
)
