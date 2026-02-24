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
    BuildingType.HEALTHCARE,
    "hospital",
    BuildingConfig(
        display_name="Hospital (Full Service)",
        base_cost_per_sf=850,  # Construction only
        cost_range=(900, 1200),  # Total range with equipment
        scope_items_profile="healthcare_hospital_structural_v1",
        dealshield_tile_profile="healthcare_hospital_v1",
        equipment_cost_per_sf=150,  # Medical equipment
        typical_floors=5,
        trades=TradeBreakdown(
            structural=0.15,
            mechanical=0.38,  # Medical gas, complex HVAC
            electrical=0.22,  # Redundant power, medical equipment
            plumbing=0.15,  # Medical gas, special drainage
            finishes=0.10,  # Medical-grade surfaces
        ),
        soft_costs=SoftCosts(
            design_fees=0.08,
            permits=0.025,
            legal=0.02,
            financing=0.03,
            contingency=0.10,
            testing=0.015,
            construction_management=0.04,
            startup=0.02,
        ),
        ownership_types={
            OwnershipType.FOR_PROFIT: FinancingTerms(
                debt_ratio=0.65,
                debt_rate=0.068,
                equity_ratio=0.35,
                target_dscr=1.25,
                target_roi=0.08,
            ),
            OwnershipType.NON_PROFIT: FinancingTerms(
                debt_ratio=0.75,
                debt_rate=0.04,  # Tax-exempt bonds
                equity_ratio=0.10,
                philanthropy_ratio=0.10,
                grants_ratio=0.05,
                target_dscr=1.15,
                target_roi=0.03,
            ),
            OwnershipType.GOVERNMENT: FinancingTerms(
                debt_ratio=0.40,
                debt_rate=0.035,
                equity_ratio=0.30,
                grants_ratio=0.30,
                target_dscr=1.10,
                target_roi=0.0,  # Break-even OK
            ),
        },
        nlp=NLPConfig(
            keywords=[
                "hospital",
                "emergency",
                "operating room",
                "OR",
                "ICU",
                "beds",
                "surgical",
                "medical center",
                "trauma",
                "acute care",
                "inpatient",
                "emergency department",
                "ER",
            ],
            priority=1,  # Highest priority
            incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT],
        ),
        regional_multipliers={
            "Nashville": 1.03,
            "Franklin": 1.03,
            "Franklin": 1.03,
            "Manchester": 0.96,
            "Memphis": 0.94,
            "Knoxville": 0.93,
            "New York": 1.35,
            "San Francisco": 1.40,
            "Chicago": 1.20,
            "Miami": 1.10,
        },
        special_features={
            "emergency_department": 50,  # $/SF additional
            "surgical_suite": 75,
            "imaging_suite": 40,
            "icu": 60,
            "laboratory": 25,
            "cathlab": 90,
            "pharmacy": 40,
        },
        financial_metrics={
            "primary_unit": "beds",
            "units_per_sf": 0.00075,  # This matches beds_per_sf below
            "revenue_per_unit_annual": 425000,
            "target_occupancy": 0.85,
            "breakeven_occupancy": 0.73,
            "market_rate_type": "daily_rate",
            "market_rate_default": 1500,
            "display_name": "Per Bed Requirements",
            "operational_metrics": {
                "throughput_per_unit_day": 0.95,
                "operating_days_per_year": 365,
                "utilization_target": 0.85,
                "average_length_of_stay_days": 4.2,
                "clinical_staff_fte_per_unit": 1.65,
                "support_staff_fte_per_unit": 0.95,
                "throughput_label": "Average Daily Census",
                "utilization_label": "Licensed Bed Occupancy",
                "staffing_intensity_label": "FTE per Licensed Bed",
                "efficiency_label": "LOS Throughput Efficiency",
                "efficiency_green_threshold": 84.0,
                "efficiency_yellow_threshold": 70.0,
            },
        },
        base_revenue_per_sf_annual=900,
        base_revenue_per_bed_annual=650000,
        beds_per_sf=0.00075,
        occupancy_rate_base=0.85,
        occupancy_rate_premium=0.88,
        operating_margin_base=0.20,
        operating_margin_premium=0.25,
        labor_cost_ratio=0.50,
        supply_cost_ratio=0.15,
        management_fee_ratio=0.10,
        insurance_cost_ratio=0.03,
        utility_cost_ratio=0.03,
        maintenance_cost_ratio=0.04,
    ),
)
