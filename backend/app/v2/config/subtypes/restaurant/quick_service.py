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
    BuildingType.RESTAURANT,
    "quick_service",
    BuildingConfig(
        display_name="Quick Service Restaurant",
        base_cost_per_sf=360,
        cost_range=(250, 350),
        cost_clamp={"min_cost_per_sf": 250, "max_cost_per_sf": 700},
        scope_items_profile="restaurant_quick_service_structural_v1",
        dealshield_tile_profile="restaurant_quick_service_v1",
        equipment_cost_per_sf=40,  # Kitchen equipment mostly in base cost
        typical_floors=1,
        trades=TradeBreakdown(
            structural=0.22,
            mechanical=0.28,
            electrical=0.15,
            plumbing=0.15,
            finishes=0.20,
        ),
        soft_costs=SoftCosts(
            design_fees=0.055,
            permits=0.02,
            legal=0.007,
            financing=0.02,
            contingency=0.06,
            testing=0.005,
            construction_management=0.03,
            startup=0.015,
        ),  # Total: 18% soft costs
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.065,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.12,
            )
        },
        nlp=NLPConfig(
            keywords=[
                "fast food",
                "quick service",
                "QSR",
                "drive through",
                "fast casual",
                "takeout",
            ],
            priority=12,
            incompatible_classes=[],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.94,
            "Memphis": 0.92,
            "New York": 1.35,
            "San Francisco": 1.40,
        },
        special_features={
            "drive_thru": {
                "basis": "COUNT_BASED",
                "value": 85000,
                "count": 1,
                "count_override_keys": ["drive_thru_lane_count", "drive_thru_count", "lane_count"],
                "unit_label": "lane",
            },  # Drive-thru lane and window
            "outdoor_seating": {
                "basis": "AREA_SHARE_GSF",
                "value": 20,
                "area_share_of_gsf": 0.06,
            },  # Patio seating area
            "play_area": {
                "basis": "AREA_SHARE_GSF",
                "value": 35,
                "area_share_of_gsf": 0.08,
            },  # Children's playground
            "double_drive_thru": {
                "basis": "COUNT_BASED",
                "value": 80000,
                "count": 2,
                "count_override_keys": [
                    "double_drive_thru_lane_count",
                    "drive_thru_lane_count",
                    "drive_thru_count",
                    "lane_count",
                ],
                "unit_label": "lane",
            },  # Dual drive-thru lanes
            "digital_menu_boards": {
                "basis": "COUNT_BASED",
                "value": 15000,
                "count": 2,
                "count_override_keys": [
                    "digital_menu_board_count",
                    "menu_board_count",
                    "board_count",
                ],
                "unit_label": "board",
            },  # Digital ordering displays
        },
        special_feature_pricing_statuses={
            "drive_thru": "included_in_baseline",
            "outdoor_seating": "incremental",
            "play_area": "incremental",
            "double_drive_thru": "incremental",
            "digital_menu_boards": "incremental",
        },
        base_revenue_per_sf_annual=525,
        occupancy_rate_base=0.88,
        occupancy_rate_premium=0.95,
        operating_margin_base=0.12,
        operating_margin_premium=0.18,
        food_cost_ratio=0.28,
        labor_cost_ratio=0.30,
        beverage_cost_ratio=0.08,
        management_fee_ratio=0.04,
        utility_cost_ratio=0.04,
        maintenance_cost_ratio=0.03,
        marketing_ratio=0.04,
        franchise_fee_ratio=0.06,
        insurance_cost_ratio=0.02,
    ),
)
