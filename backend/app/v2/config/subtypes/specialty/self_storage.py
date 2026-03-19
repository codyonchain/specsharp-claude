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
    BuildingType.SPECIALTY,
    "self_storage",
    BuildingConfig(
        display_name="Self Storage Facility",
        base_cost_per_sf=65,
        cost_range=(55, 75),
        equipment_cost_per_sf=5,
        typical_floors=3,
        trades=TradeBreakdown(
            structural=0.35,
            mechanical=0.12,  # Minimal HVAC
            electrical=0.13,
            plumbing=0.05,  # Minimal plumbing
            finishes=0.35,
        ),
        soft_costs=SoftCosts(
            design_fees=0.04,
            permits=0.02,
            legal=0.012,
            financing=0.025,
            contingency=0.06,
            testing=0.005,
            construction_management=0.02,
            startup=0.008,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.058,
                equity_ratio=0.25,
                target_dscr=1.25,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "self storage",
                "storage facility",
                "mini storage",
                "storage units",
                "public storage",
                "boat storage",
                "RV storage",
            ],
            priority=33,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.90,
            "Memphis": 0.88,
            "New York": 1.30,
            "San Francisco": 1.35,
            "Chicago": 1.10,
            "Miami": 1.05,
        },
        dealshield_tile_profile="specialty_self_storage_v1",
        scope_items_profile="specialty_self_storage_structural_v1",
        special_features={
            "climate_control_zones": {
                "basis": "AREA_SHARE_GSF",
                "value": 18,
                "area_share_of_gsf": 0.40,
            },
            "biometric_access_control": {
                "basis": "COUNT_BASED",
                "value": 60000,
                "count": 1,
                "count_override_keys": ["biometric_access_point_count", "access_control_count"],
                "unit_label": "package",
            },
            "high_density_cctv": {
                "basis": "COUNT_BASED",
                "value": 85000,
                "count": 1,
                "count_override_keys": ["cctv_package_count", "camera_system_count"],
                "unit_label": "package",
            },
            "rv_power_pedestals": {
                "basis": "COUNT_BASED",
                "value": 3500,
                "count_override_keys": ["rv_power_pedestal_count", "power_pedestal_count", "pedestal_count"],
                "default_count_bands": [
                    {"label": "small_rv_mix", "max_square_footage": 60000, "count": 8},
                    {"label": "mid_rv_mix", "max_square_footage": 120000, "count": 16},
                    {"label": "large_rv_mix", "count": 24},
                ],
                "unit_label": "pedestal",
            },
        },
        special_feature_pricing_statuses={
            "climate_control_zones": "included_in_baseline",
            "biometric_access_control": "incremental",
            "high_density_cctv": "incremental",
            "rv_power_pedestals": "incremental",
        },
        base_revenue_per_sf_annual=18,
        occupancy_rate_base=0.90,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.60,
        operating_margin_premium=0.70,
    ),
)
