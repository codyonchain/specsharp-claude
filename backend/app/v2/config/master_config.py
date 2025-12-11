"""
Master configuration for all building types.
Single source of truth that combines construction costs, owner metrics, and NLP patterns.
This replaces: building_types_config.py, owner_metrics_config.py, and NLP detection logic.

Office revenue tuning (Nashville, Class A baseline)
---------------------------------------------------
- Base rent: $32–$36 per SF per year
- Effective rent (after concessions/vacancy): ~$34 per SF per year
- Stabilized occupancy: ~90% (base) / 94% (premium)
- Operating margin: 0.56 base / 0.62 premium
These figures keep DSCR in sync with lender expectations while leaving
restaurant assumptions untouched.
"""

import re
from collections import defaultdict
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Callable

# ============================================================================
# ENUMS
# ============================================================================

class BuildingType(str, Enum):
    """All building types in the system"""
    HEALTHCARE = "healthcare"
    MULTIFAMILY = "multifamily"
    OFFICE = "office"
    RETAIL = "retail"
    INDUSTRIAL = "industrial"
    HOSPITALITY = "hospitality"
    EDUCATIONAL = "educational"
    CIVIC = "civic"
    RECREATION = "recreation"
    MIXED_USE = "mixed_use"
    PARKING = "parking"
    RESTAURANT = "restaurant"
    SPECIALTY = "specialty"
    # Note: RELIGIOUS excluded per requirements (13 types total)

class ProjectClass(Enum):
    """Project classification types"""
    GROUND_UP = "ground_up"
    ADDITION = "addition"
    RENOVATION = "renovation"
    TENANT_IMPROVEMENT = "tenant_improvement"

class OwnershipType(Enum):
    """Ownership types for financing calculations"""
    FOR_PROFIT = "for_profit"
    NON_PROFIT = "non_profit"
    GOVERNMENT = "government"
    PPP = "public_private_partnership"

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TradeBreakdown:
    """Trade cost percentages"""
    structural: float
    mechanical: float
    electrical: float
    plumbing: float
    finishes: float

@dataclass
class SoftCosts:
    """Owner soft cost rates"""
    design_fees: float
    permits: float
    legal: float
    financing: float
    contingency: float
    testing: float
    construction_management: float
    startup: float

@dataclass
class FinancingTerms:
    """Financing parameters for ownership types"""
    debt_ratio: float
    debt_rate: float
    equity_ratio: float
    philanthropy_ratio: float = 0.0
    grants_ratio: float = 0.0
    target_dscr: float = 1.25
    target_roi: float = 0.08

@dataclass
class NLPConfig:
    """NLP detection configuration"""
    keywords: List[str]
    priority: int  # Higher = check first
    incompatible_classes: List[ProjectClass]
    confidence_threshold: float = 0.7

@dataclass
class BuildingConfig:
    """Complete configuration for a building subtype"""
    # Display
    display_name: str
    
    # Construction costs
    base_cost_per_sf: float
    cost_range: Tuple[float, float]
    equipment_cost_per_sf: float
    typical_floors: int
    
    # Trade breakdown
    trades: TradeBreakdown
    
    # Owner costs
    soft_costs: SoftCosts
    
    # Financing options
    ownership_types: Dict[OwnershipType, FinancingTerms]
    
    # NLP detection
    nlp: NLPConfig
    
    # Regional multipliers (base = Nashville = 1.0)
    regional_multipliers: Dict[str, float]
    
    # Special features that add cost
    special_features: Optional[Dict[str, float]] = None
    ti_allowance_per_sf: Optional[float] = None
    soft_costs_pct_of_hard: Optional[float] = None
    contingency_pct_of_hard: Optional[float] = None
    
    # Revenue and financial metrics - base values
    base_revenue_per_sf_annual: Optional[float] = None
    base_revenue_per_unit_monthly: Optional[float] = None
    base_revenue_per_bed_annual: Optional[float] = None
    base_revenue_per_room_annual: Optional[float] = None
    base_revenue_per_student_annual: Optional[float] = None
    base_revenue_per_visit: Optional[float] = None
    base_revenue_per_procedure: Optional[float] = None
    base_revenue_per_scan: Optional[float] = None
    base_revenue_per_seat_annual: Optional[float] = None
    base_revenue_per_space_monthly: Optional[float] = None
    base_sales_per_sf_annual: Optional[float] = None
    operating_expense_per_sf: Optional[float] = None
    cam_charges_per_sf: Optional[float] = None
    staffing_pct_property_mgmt: Optional[float] = None
    staffing_pct_maintenance: Optional[float] = None
    base_adr_by_market: Optional[Dict[str, float]] = None
    base_occupancy_by_market: Optional[Dict[str, float]] = None
    expense_percentages: Optional[Dict[str, float]] = None
    development_cost_per_sf_by_finish: Optional[Dict[str, float]] = None
    cap_rate_defaults: Optional[Dict[str, float]] = None
    yield_on_cost_hurdle: Optional[float] = None
    dscr_target: Optional[float] = None
    basis_risk_tolerance_pct: Optional[float] = None
    
    # Unit metrics
    units_per_sf: Optional[float] = None
    beds_per_sf: Optional[float] = None
    rooms_per_sf: Optional[float] = None
    students_per_sf: Optional[float] = None
    seats_per_sf: Optional[float] = None
    spaces_per_sf: Optional[float] = None
    visits_per_day: Optional[int] = None
    procedures_per_day: Optional[int] = None
    scans_per_day: Optional[int] = None
    days_per_year: Optional[int] = None
    
    # Operational metrics - base and premium
    occupancy_rate_base: Optional[float] = None
    occupancy_rate_premium: Optional[float] = None
    operating_margin_base: Optional[float] = None
    operating_margin_premium: Optional[float] = None
    
    # Valuation metrics
    market_cap_rate: Optional[float] = None  # Cap rate for property valuation
    discount_rate: Optional[float] = None    # Discount rate for DCF
    
    # Expense ratios for operational efficiency
    labor_cost_ratio: Optional[float] = None
    supply_cost_ratio: Optional[float] = None
    management_fee_ratio: Optional[float] = None
    insurance_cost_ratio: Optional[float] = None
    utility_cost_ratio: Optional[float] = None
    maintenance_cost_ratio: Optional[float] = None
    food_cost_ratio: Optional[float] = None
    equipment_lease_ratio: Optional[float] = None
    marketing_ratio: Optional[float] = None
    franchise_fee_ratio: Optional[float] = None
    security_ratio: Optional[float] = None
    beverage_cost_ratio: Optional[float] = None
    property_tax_ratio: Optional[float] = None
    reserves_ratio: Optional[float] = None
    janitorial_ratio: Optional[float] = None
    rooms_operations_ratio: Optional[float] = None
    food_beverage_ratio: Optional[float] = None
    sales_marketing_ratio: Optional[float] = None
    raw_materials_ratio: Optional[float] = None
    monitoring_cost_ratio: Optional[float] = None
    connectivity_ratio: Optional[float] = None
    
    # Financial metrics configuration
    financial_metrics: Optional[Dict[str, Any]] = None

# ============================================================================
# MASTER CONFIGURATION
# ============================================================================

# Default ground-up project timelines by building type.
# Used to drive the Executive View "Key Milestones" card (groundbreaking, structure, etc.).
# Values are month offsets from a notional start date (e.g., Q1 2025).
PROJECT_TIMELINES = {
    BuildingType.MULTIFAMILY: {
        "ground_up": {
            "total_months": 30,
            "milestones": {
                "groundbreaking": 0,
                "structure_complete": 12,
                "substantial_completion": 24,
                "grand_opening": 30,
            },
        },
    },
    BuildingType.INDUSTRIAL: {
        "ground_up": {
            "total_months": 18,
            "milestones": {
                "groundbreaking": 0,
                "structure_complete": 8,
                "substantial_completion": 14,
                "grand_opening": 18,
            },
        },
    },
    BuildingType.HOSPITALITY: {
        "ground_up": {
            "total_months": 30,
            "milestones": {
                "groundbreaking": 0,
                "structure_complete": 14,
                "substantial_completion": 24,
                "grand_opening": 30,
            },
        },
    },
    BuildingType.RESTAURANT: {
        "ground_up": {
            "total_months": 14,
            "milestones": [
                {
                    "id": "groundbreaking",
                    "label": "Groundbreaking / Site & Shell Start",
                    "offset_months": 0,
                },
                {
                    "id": "structure_complete",
                    "label": "Structure & Shell Complete",
                    "offset_months": 6,
                },
                {
                    "id": "kitchen_mep_rough_in",
                    "label": "Kitchen & MEP Rough-In Complete",
                    "offset_months": 9,
                },
                {
                    "id": "substantial_completion",
                    "label": "Health & Code Inspections + Final Punch",
                    "offset_months": 11,
                },
                {
                    "id": "grand_opening",
                    "label": "Soft / Grand Opening",
                    "offset_months": 13,
                },
            ],
        },
    },
    BuildingType.HEALTHCARE: {
        "ground_up": {
            "total_months": 18,
            "milestones": [
                {
                    "id": "design_licensing",
                    "label": "Design & Licensing",
                    "offset_months": 0,
                },
                {
                    "id": "shell_mep_rough_in",
                    "label": "Shell & MEP Rough-In",
                    "offset_months": 4,
                },
                {
                    "id": "interior_buildout",
                    "label": "Interior Buildout & Finishes",
                    "offset_months": 8,
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Equipment & Low Voltage",
                    "offset_months": 12,
                },
                {
                    "id": "soft_opening",
                    "label": "Soft Opening & Ramp-Up",
                    "offset_months": 16,
                },
            ],
        },
    },
}

MARGINS = {
    BuildingType.MULTIFAMILY: 0.35,
    BuildingType.OFFICE: 0.25,
    BuildingType.RETAIL: 0.20,
    # Industrial: NNN leases, very lean expenses. Treat margin as NOI margin.
    BuildingType.INDUSTRIAL: 0.85,
    BuildingType.HOSPITALITY: 0.18,
    BuildingType.RESTAURANT: 0.17,
    BuildingType.HEALTHCARE: 0.22,
    BuildingType.EDUCATIONAL: 0.15,
}

"""
Typical 2025 underwriting sentiment: market cap rates, target yield-on-cost,
and DSCR by primary building type.

For Multifamily specifically, these values are calibrated to:
- Market cap rate: blended across luxury, market-rate, and affordable
  (roughly mid-6%).
- Target yield-on-cost: ~150–200 bps above market cap, reflecting current
  equity expectations for new development.
"""
BUILDING_PROFILES: Dict[BuildingType, Dict[str, float]] = {
    BuildingType.MULTIFAMILY: {
        # Blended across luxury / market-rate / affordable
        'market_cap_rate': 0.0650,   # ~6.5% MF market cap
        'target_yield': 0.0800,      # ~8.0% yield-on-cost target
        'target_dscr': 1.25,
    },
    BuildingType.OFFICE: {
        'market_cap_rate': 0.0700,
        'target_yield': 0.0950,
        'target_dscr': 1.30,
    },
    BuildingType.RETAIL: {
        'market_cap_rate': 0.0630,
        'target_yield': 0.0830,
        'target_dscr': 1.30,
    },
    BuildingType.INDUSTRIAL: {
        # Modern bulk distribution in strong secondary markets (like Nashville).
        # Cap rates ~6.25–6.75%, developers underwrite to ~7% yield-on-cost.
        'market_cap_rate': 0.0650,
        'target_yield': 0.0700,
        'target_dscr': 1.25,
    },
    BuildingType.HOSPITALITY: {
        'market_cap_rate': 0.0750,
        'target_yield': 0.1000,
        'target_dscr': 1.35,
    },
    BuildingType.RESTAURANT: {
        'market_cap_rate': 0.0725,
        'target_yield': 0.0900,
        'target_dscr': 1.30,
    },
    BuildingType.HEALTHCARE: {
        'market_cap_rate': 0.0625,
        'target_yield': 0.0825,
        'target_dscr': 1.30,
    },
    BuildingType.EDUCATIONAL: {
        'market_cap_rate': 0.0675,
        'target_yield': 0.0900,
        'target_dscr': 1.30,
    },
    BuildingType.MIXED_USE: {
        'market_cap_rate': 0.0575,
        'target_yield': 0.0775,
        'target_dscr': 1.30,
    },
    BuildingType.SPECIALTY: {
        'market_cap_rate': 0.0700,
        'target_yield': 0.0900,
        'target_dscr': 1.25,
    },
    BuildingType.CIVIC: {
        'market_cap_rate': 0.0675,
        'target_yield': 0.0900,
        'target_dscr': 1.30,
    },
    BuildingType.RECREATION: {
        'market_cap_rate': 0.0675,
        'target_yield': 0.0900,
        'target_dscr': 1.30,
    },
    BuildingType.PARKING: {
        'market_cap_rate': 0.0700,
        'target_yield': 0.0900,
        'target_dscr': 1.25,
    },
}

# Class A office profile for strong urban markets (e.g., downtown Nashville).
# Assumes full-service gross rent around $38/SF, 92% stabilized occupancy,
# 6% vacancy/credit loss, 40% OpEx load, and amortized TI/LC over lease term.
OFFICE_UNDERWRITING_CONFIG: Dict[str, Dict[str, float]] = {
    "class_a": {
        # Rent & occupancy
        "base_rent_per_sf": 38.0,                # $/RSF/year, gross baseline
        "stabilized_occupancy": 0.92,            # 92% occupied once stabilized
        "vacancy_and_credit_loss_pct": 0.06,     # 6% of PGI

        # Operating expenses (non-reimbursed share of EGI)
        "opex_pct_of_egi": 0.40,

        # Leasing costs (amortized over average lease term)
        "ti_per_sf": 70.0,
        "ti_amort_years": 10,
        "lc_pct_of_lease_value": 0.06,
        "lc_amort_years": 10,

        # Capitalization / hurdle assumptions
        "exit_cap_rate": 0.0675,                 # 6.75% stabilized exit cap
        "yield_on_cost_hurdle": 0.09,            # 9.0% development hurdle
        "discount_rate": 0.0825,                 # midpoint of 8.0–8.5%
    }
}

MASTER_CONFIG: Dict[BuildingType, Dict[str, BuildingConfig]] = {
    # ------------------------------------------------------------------------
    # HEALTHCARE
    # ------------------------------------------------------------------------
    BuildingType.HEALTHCARE: {
        'hospital': BuildingConfig(
            display_name='Hospital (Full Service)',
            base_cost_per_sf=850,  # Construction only
            cost_range=(900, 1200),  # Total range with equipment
            equipment_cost_per_sf=150,  # Medical equipment
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.15,
                mechanical=0.38,  # Medical gas, complex HVAC
                electrical=0.22,  # Redundant power, medical equipment
                plumbing=0.15,   # Medical gas, special drainage
                finishes=0.10    # Medical-grade surfaces
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.025,
                legal=0.02,
                financing=0.03,
                contingency=0.10,
                testing=0.015,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.068,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.08
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.04,  # Tax-exempt bonds
                    equity_ratio=0.10,
                    philanthropy_ratio=0.10,
                    grants_ratio=0.05,
                    target_dscr=1.15,
                    target_roi=0.03
                ),
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.40,
                    debt_rate=0.035,
                    equity_ratio=0.30,
                    grants_ratio=0.30,
                    target_dscr=1.10,
                    target_roi=0.0  # Break-even OK
                )
            },
            
            nlp=NLPConfig(
                keywords=['hospital', 'emergency', 'operating room', 'OR', 'ICU', 
                         'beds', 'surgical', 'medical center', 'trauma', 'acute care',
                         'inpatient', 'emergency department', 'ER'],
                priority=1,  # Highest priority
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'Knoxville': 0.93,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'emergency_department': 50,  # $/SF additional
                'surgical_suite': 75,
                'imaging_suite': 40,
                'icu': 60,
                'laboratory': 25,
                'cathlab': 90,
                'pharmacy': 40
            },
            
            # Financial metrics configuration
            financial_metrics={
                'primary_unit': 'beds',
                'units_per_sf': 0.00075,  # This matches beds_per_sf below
                'revenue_per_unit_annual': 425000,
                'target_occupancy': 0.85,
                'breakeven_occupancy': 0.73,
                'market_rate_type': 'daily_rate',
                'market_rate_default': 1500,
                'display_name': 'Per Bed Requirements'
            },

            # Revenue metrics
            base_revenue_per_sf_annual=900,
            base_revenue_per_bed_annual=650000,
            beds_per_sf=0.00075,
            occupancy_rate_base=0.85,
            occupancy_rate_premium=0.88,
            operating_margin_base=0.20,
            operating_margin_premium=0.25,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.50,           # 50% of revenue - industry standard for hospitals
            supply_cost_ratio=0.15,          # 15% - medical supplies and pharmaceuticals
            management_fee_ratio=0.10,       # 10% - administration and management
            insurance_cost_ratio=0.03,       # 3% - malpractice and liability insurance
            utility_cost_ratio=0.03,         # 3% - utilities (high energy use)
            maintenance_cost_ratio=0.04      # 4% - facility and equipment maintenance
        ),
        
        'surgical_center': BuildingConfig(
            display_name='Ambulatory Surgical Center',
            base_cost_per_sf=480,
            cost_range=(600, 780),
            equipment_cost_per_sf=180,
            typical_floors=1,
            ti_allowance_per_sf=0,
            
            trades=TradeBreakdown(
                structural=0.12,
                mechanical=0.40,  # Heavy MEP scope for OR pressurization
                electrical=0.20,
                plumbing=0.14,
                finishes=0.14
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.015,
                construction_management=0.025,
                startup=0.01
            ),
            soft_costs_pct_of_hard=0.26,
            contingency_pct_of_hard=0.08,
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.45,
                    target_roi=0.115,
                )
            },
            
            nlp=NLPConfig(
                keywords=['surgical center', 'ambulatory surgery', 'ASC', 'surgery center',
                         'outpatient surgery', 'day surgery', 'same day surgery'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'New York': 1.32,
                'San Francisco': 1.38,
                'Chicago': 1.18,
                'Miami': 1.12
            },
            
            special_features={
                'operating_room': 100,  # Per OR
                'recovery_room': 40,
                'pre_op': 35,
                'sterile_processing': 60,
                'hc_asc_expanded_pacu': 75,
                'hc_asc_sterile_core_upgrade': 50,
                'hc_asc_pain_management_suite': 60,
                'hc_asc_hybrid_or_cath_lab': 125
            },

            financial_metrics={
                'primary_unit': 'operating rooms',
                'units_per_sf': 1.0 / 950.0,
                'revenue_per_unit_annual': 1200000,
                'display_name': 'Per OR Requirements'
            },

            base_revenue_per_sf_annual=650,
            operating_margin_base=0.24,
            yield_on_cost_hurdle=0.115,
            dscr_target=1.45,
            basis_risk_tolerance_pct=0.10,
            
            # Expense ratios tuned to ASC throughput
            labor_cost_ratio=0.38,
            supply_cost_ratio=0.20,
            management_fee_ratio=0.07,
            insurance_cost_ratio=0.04,
            utility_cost_ratio=0.025,
            maintenance_cost_ratio=0.045
        ),
        
        'medical_center': BuildingConfig(
            display_name='Medical Center',
            base_cost_per_sf=750,
            cost_range=(850, 1000),
            equipment_cost_per_sf=150,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.18,
                mechanical=0.34,
                electrical=0.20,
                plumbing=0.15,
                finishes=0.13
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.075,
                permits=0.025,
                legal=0.02,
                financing=0.03,
                contingency=0.10,
                testing=0.015,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.068,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.09,
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.042,
                    equity_ratio=0.15,
                    philanthropy_ratio=0.10,
                    target_dscr=1.18,
                    target_roi=0.04
                )
            },
            
            nlp=NLPConfig(
                keywords=['medical center', 'health center', 'healthcare center',
                         'comprehensive care', 'medical complex'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'New York': 1.33,
                'San Francisco': 1.38,
                'Chicago': 1.18,
                'Miami': 1.10
            },
            
            special_features={
                'emergency': 45,
                'surgery': 60,
                'imaging': 35,
                'laboratory': 25,
                'specialty_clinic': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=55,
            occupancy_rate_base=0.88,
            occupancy_rate_premium=0.92,
            operating_margin_base=0.25,
            operating_margin_premium=0.30,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.48,           # 48% - comprehensive staffing
            supply_cost_ratio=0.16,          # 16% - varied medical supplies
            management_fee_ratio=0.11,       # 11% - complex administration
            insurance_cost_ratio=0.03,       # 3% - liability insurance
            utility_cost_ratio=0.03,         # 3% - standard utilities
            maintenance_cost_ratio=0.04      # 4% - facility maintenance
        ),
        
        'imaging_center': BuildingConfig(
            display_name='Diagnostic Imaging Center',
            base_cost_per_sf=420,
            cost_range=(420, 560),
            equipment_cost_per_sf=120,
            typical_floors=1,
            ti_allowance_per_sf=0,
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.32,
                electrical=0.24,
                plumbing=0.08,
                finishes=0.12
            ),
            soft_costs=SoftCosts(
                design_fees=0.09,
                permits=0.02,
                legal=0.02,
                financing=0.03,
                contingency=0.07,
                testing=0.02,
                construction_management=0.04,
                startup=0.02
            ),
            soft_costs_pct_of_hard=0.25,
            contingency_pct_of_hard=0.07,
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.4,
                    target_roi=0.10,
                )
            },
            nlp=NLPConfig(
                keywords=['imaging center', 'diagnostic center', 'MRI', 'CT scan',
                         'radiology', 'x-ray', 'medical imaging', 'diagnostic imaging'],
                priority=3,
                incompatible_classes=[]
            ),
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'New York': 1.30,
                'San Francisco': 1.35,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            special_features={
                'mri_suite': 80,
                'ct_suite': 60,
                'pet_scan': 90,
                'mammography': 35,
                'ultrasound': 20,
                'hc_imaging_second_mri': 100,
                'hc_imaging_pet_ct_suite': 150,
                'hc_imaging_interventional_rad': 125
            },
            base_revenue_per_sf_annual=525,
            operating_margin_base=0.22,
            occupancy_rate_base=0.80,
            occupancy_rate_premium=0.88,
            units_per_sf=1.0 / 800.0,
            financial_metrics={
                'primary_unit': 'scan rooms',
                'units_per_sf': 1.0 / 800.0,
                'revenue_per_unit_annual': 850000,
            },
            yield_on_cost_hurdle=0.10,
            dscr_target=1.4,
            basis_risk_tolerance_pct=0.10,
            labor_cost_ratio=0.35,
            supply_cost_ratio=0.08,
            management_fee_ratio=0.10,
            insurance_cost_ratio=0.02,
            utility_cost_ratio=0.04,
            maintenance_cost_ratio=0.15,
            equipment_lease_ratio=0.10
        ),
        
        'outpatient_clinic': BuildingConfig(
            display_name='Outpatient Clinic',
            base_cost_per_sf=380,
            cost_range=(400, 480),
            equipment_cost_per_sf=50,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.26,  # Enhanced ventilation
                electrical=0.12,
                plumbing=0.15,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.10,
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.045,
                    equity_ratio=0.20,
                    grants_ratio=0.05,
                    target_dscr=1.15,
                    target_roi=0.03
                )
            },
            
            nlp=NLPConfig(
                keywords=[
                    'outpatient clinic',
                    'primary care clinic',
                    'primary care',
                    'family medicine clinic',
                    'family practice clinic',
                    'internal medicine clinic',
                    'health clinic',
                    'ambulatory care',
                    'outpatient facility',
                    'exam rooms',
                    'exam room'
                ],
                priority=3,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.28,
                'San Francisco': 1.32,
                'Chicago': 1.12,
                'Miami': 1.05
            },
            
            special_features={
                'exam_rooms': 15,
                'procedure_room': 25,
                'laboratory': 20,
                'pharmacy': 30,
                'hc_outpatient_on_site_lab': 30,
                'hc_outpatient_imaging_pod': 60,
                'hc_outpatient_behavioral_suite': 25
            },

            financial_metrics={
                'primary_unit': 'exam rooms',
                # ~650 SF per exam room (clinic + support)
                'units_per_sf': 1 / 650,
                # Annual revenue per exam room, calibrated to ~1.4–1.6M total
                # for a 12-room, 8,000 SF clinic.
                'revenue_per_unit_annual': 130000,
                'target_occupancy': 0.85,
                'breakeven_occupancy': 0.70,
                'market_rate_type': 'revenue_per_visit',
                'market_rate_default': 120,
                'display_name': 'Per Exam Room Performance'
            },

            # Revenue metrics – primary care / outpatient clinic
            base_revenue_per_sf_annual=195,
            base_revenue_per_visit=120,
            visits_per_day=50,
            days_per_year=260,
            occupancy_rate_base=0.85,
            occupancy_rate_premium=0.90,
            operating_margin_base=0.16,
            operating_margin_premium=0.20,
            
            # Expense ratios
            labor_cost_ratio=0.42,
            supply_cost_ratio=0.10,
            management_fee_ratio=0.08,
            insurance_cost_ratio=0.02,
            utility_cost_ratio=0.02,
            maintenance_cost_ratio=0.03
        ),
        
        'urgent_care': BuildingConfig(
            display_name='Urgent Care Center',
            base_cost_per_sf=350,
            cost_range=(400, 475),
            equipment_cost_per_sf=75,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.25,
                electrical=0.13,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.11,
                )
            },
            
            nlp=NLPConfig(
                keywords=['urgent care', 'walk-in clinic', 'immediate care', 
                         'express care', 'quick care', 'walk in'],
                priority=3,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.25,
                'San Francisco': 1.30,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'trauma_room': 30,
                'x_ray': 25,
                'laboratory': 20,
                'pharmacy': 25,
                'hc_urgent_on_site_lab': 38,
                'hc_urgent_imaging_suite': 75,
                'hc_urgent_observation_bays': 25
            },

            financial_metrics={
                'primary_unit': 'exam rooms',
                # Urgent care is denser than primary care; ~450 SF per room
                'units_per_sf': 1 / 450,
                # Calibrated to roughly $2M / 11 rooms ≈ $180k per room
                'revenue_per_unit_annual': 180000,
                'target_occupancy': 0.75,
                'breakeven_occupancy': 0.65,
                'market_rate_type': 'revenue_per_visit',
                'market_rate_default': 150,
                'display_name': 'Per Exam Room Performance',
            },

            # Revenue metrics
            base_revenue_per_sf_annual=430,
            base_revenue_per_visit=150,
            visits_per_day=50,
            days_per_year=365,
            occupancy_rate_base=0.70,
            occupancy_rate_premium=0.85,
            operating_margin_base=0.25,
            operating_margin_premium=0.30,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.40,           # 40% - 24/7 staffing considerations
            supply_cost_ratio=0.12,          # 12% - emergency supplies
            management_fee_ratio=0.08,       # 8% - administration
            insurance_cost_ratio=0.03,       # 3% - moderate risk
            utility_cost_ratio=0.03,         # 3% - extended hours
            maintenance_cost_ratio=0.03,     # 3% - standard maintenance
            marketing_ratio=0.03             # 3% - local marketing important
        ),
        
        'medical_office': BuildingConfig(
            display_name='Medical Office Building',
            base_cost_per_sf=270,
            cost_range=(260, 320),
            equipment_cost_per_sf=0,
            typical_floors=3,
            ti_allowance_per_sf=40,
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.28,
                electrical=0.16,
                plumbing=0.12,
                finishes=0.22
            ),
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.008,
                construction_management=0.03,
                startup=0.01
            ),
            soft_costs_pct_of_hard=0.20,
            contingency_pct_of_hard=0.05,
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.35,
                    target_roi=0.07,
                )
            },
            nlp=NLPConfig(
                keywords=[
                    'medical office building',
                    'mob',
                    'medical office suites',
                    'physician office',
                    'doctor office building',
                    'medical office landlord',
                    'medical office tower',
                    'medical office complex'
                ],
                priority=4,
                incompatible_classes=[]
            ),
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.96,
                'Memphis': 0.94,
                'New York': 1.28,
                'San Francisco': 1.34,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            special_features={
                'tenant_improvements': 40,
                'ambulatory_buildout': 60,
                'ambulatory_imaging': 35,
                'mob_imaging_ready_shell': 40,
                'mob_enhanced_mep': 20,
                'mob_procedure_suite': 30,
                'mob_pharmacy_shell': 15,
                'mob_covered_dropoff': 15
            },
            financial_metrics={
                'primary_unit': 'tenant suites',
                'units_per_sf': 1.0 / 2500.0,
                'revenue_per_unit_annual': 100000,
                'display_name': 'Per Suite Performance'
            },
            base_revenue_per_sf_annual=40,
            operating_margin_base=0.65,
            operating_margin_premium=0.70,
            yield_on_cost_hurdle=0.07,
            dscr_target=1.35,
            basis_risk_tolerance_pct=0.08
        ),
        
        'dental_office': BuildingConfig(
            display_name='Dental Office',
            base_cost_per_sf=340,
            cost_range=(360, 440),
            equipment_cost_per_sf=110,
            typical_floors=1,
            ti_allowance_per_sf=35,
            
            trades=TradeBreakdown(
                structural=0.18,
                mechanical=0.24,
                electrical=0.20,  # Heavy imaging and chair loads
                plumbing=0.18,   # Wet columns, vac, suction, med gas
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.02,
                contingency=0.07,
                testing=0.005,
                construction_management=0.02,
                startup=0.01
            ),
            soft_costs_pct_of_hard=0.22,
            contingency_pct_of_hard=0.07,
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.065,
                    equity_ratio=0.30,
                    target_dscr=1.45,
                    target_roi=0.12,
                )
            },
            
            nlp=NLPConfig(
                keywords=['dental office', 'dentist', 'dental practice', 'dental clinic',
        'orthodontist', 'oral surgery', 'dental'],
                priority=6,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.28,
                'San Francisco': 1.32,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'operatory': 15,  # Per dental chair
                'sterilization': 10,
                'x_ray': 12,
                'lab': 15,
                'hc_dental_pano_ceph': 45,
                'hc_dental_sedation_suite': 60,
                'hc_dental_sterilization_upgrade': 25,
                'hc_dental_ortho_bay_expansion': 35
            },

            financial_metrics={
                'primary_unit': 'operatories',
                'units_per_sf': 1.0 / 350.0,
                'revenue_per_unit_annual': 550000,
                'display_name': 'Per Operatory Performance'
            },

            base_revenue_per_sf_annual=430,
            occupancy_rate_base=0.96,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.62,
            operating_margin_premium=0.68,
            units_per_sf=1.0 / 350.0,
            yield_on_cost_hurdle=0.10,
            dscr_target=1.45,
            basis_risk_tolerance_pct=0.10,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.24,           # Lean dental staffing
            supply_cost_ratio=0.09,
            management_fee_ratio=0.06,
            insurance_cost_ratio=0.02,
            utility_cost_ratio=0.03,
            maintenance_cost_ratio=0.04,
            equipment_lease_ratio=0.05
        ),
        
        'rehabilitation': BuildingConfig(
            display_name='Rehabilitation Center',
            base_cost_per_sf=325,
            cost_range=(400, 475),
            equipment_cost_per_sf=100,  # Therapy equipment
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.25,
                electrical=0.13,
                plumbing=0.16,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.018
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.068,
                    equity_ratio=0.35,
                    target_dscr=1.23,
                    target_roi=0.10,
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.03
                )
            },
            
            nlp=NLPConfig(
                keywords=['rehabilitation', 'rehab center', 'physical therapy',
                         'occupational therapy', 'speech therapy', 'therapy center'],
                priority=7,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.28,
                'San Francisco': 1.33,
                'Chicago': 1.12,
                'Miami': 1.06
            },
            
            special_features={
                'therapy_gym': 40,
                'hydrotherapy': 50,
                'treatment_rooms': 20,
                'assessment_suite': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=350,
            base_revenue_per_bed_annual=280000,
            beds_per_sf=0.001,
            occupancy_rate_base=0.82,
            occupancy_rate_premium=0.88,
            operating_margin_base=0.18,
            operating_margin_premium=0.25,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.55,           # 55% - therapy staff intensive
            supply_cost_ratio=0.08,          # 8% - therapy supplies
            management_fee_ratio=0.10,       # 10% - administration
            insurance_cost_ratio=0.02,       # 2% - liability
            utility_cost_ratio=0.03,         # 3% - pool/gym facilities
            maintenance_cost_ratio=0.05      # 5% - equipment and pool maintenance
        ),
        
        'nursing_home': BuildingConfig(
            display_name='Senior Care Facility',
            base_cost_per_sf=275,
            cost_range=(275, 325),
            equipment_cost_per_sf=10,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.23,
                electrical=0.11,
                plumbing=0.15,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.008,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.066,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.09,
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.043,
                    equity_ratio=0.15,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.02
                )
            },
            
            nlp=NLPConfig(
                keywords=['nursing home', 'senior care', 'assisted living', 'elder care',
                         'senior living', 'long term care', 'skilled nursing'],
                priority=8,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.25,
                'San Francisco': 1.30,
                'Chicago': 1.10,
                'Miami': 1.08
            },
            
            special_features={
                'memory_care': 30,
                'therapy_room': 20,
                'dining_hall': 15,
                'activity_room': 12
            },

            # Revenue metrics
            base_revenue_per_sf_annual=300,
            base_revenue_per_bed_annual=95000,
            beds_per_sf=0.0015,
            occupancy_rate_base=0.88,
            occupancy_rate_premium=0.92,
            operating_margin_base=0.12,
            operating_margin_premium=0.18,
            
            # Expense ratios for operational efficiency calculations
            labor_cost_ratio=0.60,           # 60% - 24/7 care staff
            supply_cost_ratio=0.10,          # 10% - medical and living supplies
            food_cost_ratio=0.08,            # 8% - meal services
            management_fee_ratio=0.08,       # 8% - administration
            insurance_cost_ratio=0.02,       # 2% - liability
            utility_cost_ratio=0.04,         # 4% - residential-level utilities
            maintenance_cost_ratio=0.03      # 3% - facility maintenance
        )
    },
    
    # ------------------------------------------------------------------------
    # MULTIFAMILY
    # ------------------------------------------------------------------------
    BuildingType.MULTIFAMILY: {
        'luxury_apartments': BuildingConfig(
            display_name='Class A / Luxury Apartments',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=25,  # Appliances, fixtures
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.22,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.005,
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.055,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.06,  # Market standard 6% for luxury apartments
                )
            },
            
            nlp=NLPConfig(
                keywords=['luxury apartment', 'class a', 'high-end apartment', 
                         'luxury multifamily', 'upscale apartment', 'premium apartment'],
                priority=5,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Miami': 1.20
            },
            
            special_features={
                'rooftop_amenity': 35,
                'pool': 25,
                'fitness_center': 20,
                'parking_garage': 45,
                'concierge': 15
            },

            # Revenue metrics
            # NOTE: base_revenue_per_sf_annual is calibrated to be
            # mathematically consistent with units_per_sf, monthly rent,
            # occupancy_rate_base, and 12 months of income.
            #   annual_psf ≈ units_per_sf * monthly_rent * 12 * occupancy
            base_revenue_per_sf_annual=36.0,
            base_revenue_per_unit_monthly=3500,  # Nashville luxury market rate
            units_per_sf=0.000909,  # ≈ 1 unit / 1,100 SF
            occupancy_rate_base=0.93,
            occupancy_rate_premium=0.90,
            operating_margin_base=0.65,
            operating_margin_premium=0.7,
            
            # Valuation parameters
            market_cap_rate=0.055,  # 5.5% for Nashville luxury apartments
            
            # Expense ratios for operational efficiency calculations
            management_fee_ratio=0.04,       # 4% - professional property management
            maintenance_cost_ratio=0.08,     # 8% - higher for luxury finishes
            utility_cost_ratio=0.03,         # 3% - common area utilities
            insurance_cost_ratio=0.02,       # 2% - property insurance
            property_tax_ratio=0.10,         # 10% - varies by location
            marketing_ratio=0.02,            # 2% - leasing and advertising
            reserves_ratio=0.03,             # 3% - capital reserves
            security_ratio=0.02,             # 2% - concierge/security
            supply_cost_ratio=0.01           # 1% - office and maintenance supplies
        ),
        
        'market_rate_apartments': BuildingConfig(
            display_name='Class B / Market Rate Apartments',
            base_cost_per_sf=145,
            cost_range=(130, 160),
            equipment_cost_per_sf=15,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.20,
                    target_roi=0.10,
                )
            },
            
            nlp=NLPConfig(
                keywords=['apartment', 'multifamily', 'market rate', 'class b',
                         'rental housing', 'apartment complex'],
                priority=6,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.40,
                'San Francisco': 1.45
            },

            # Revenue metrics
            # Calibrated for consistency:
            #   2,000/mo * 12 * (1/800) * 0.95 ≈ $28.5/SF/yr
            base_revenue_per_sf_annual=28.5,
            base_revenue_per_unit_monthly=2000,
            units_per_sf=0.00125,  # ≈ 1 unit / 800 SF
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.6,
            operating_margin_premium=0.65,
            
            # Valuation parameters
            market_cap_rate=0.065,  # 6.5% for market rate apartments
            
            # Expense ratios for operational efficiency calculations
            management_fee_ratio=0.05,       # 5% - standard property management
            maintenance_cost_ratio=0.07,     # 7% - regular maintenance
            utility_cost_ratio=0.04,         # 4% - utilities (some tenant paid)
            insurance_cost_ratio=0.02,       # 2% - standard coverage
            property_tax_ratio=0.12,         # 12% - typical property tax
            marketing_ratio=0.02,            # 2% - advertising and leasing
            reserves_ratio=0.02,             # 2% - capital reserves
            supply_cost_ratio=0.01           # 1% - supplies
        ),
        
        'affordable_housing': BuildingConfig(
            display_name='Affordable Housing',
            base_cost_per_sf=120,
            cost_range=(110, 130),
            equipment_cost_per_sf=10,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.32,
                mechanical=0.18,
                electrical=0.12,
                plumbing=0.18,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.02,  # Higher for compliance
                financing=0.02,  # Often subsidized
                contingency=0.06,
                testing=0.005,
                construction_management=0.025,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.50,
                    debt_rate=0.04,  # Tax-exempt bonds
                    equity_ratio=0.10,
                    philanthropy_ratio=0.15,
                    grants_ratio=0.25,  # LIHTC, etc.
                    target_dscr=1.15,
                    target_roi=0.0,
                )
            },
            
            nlp=NLPConfig(
                keywords=['affordable housing', 'workforce housing', 'section 8',
                         'LIHTC', 'low income', 'subsidized housing'],
                priority=7,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.88,
                'Memphis': 0.86,
                'New York': 1.35,
                'San Francisco': 1.40
            },

            # Revenue metrics
            # Calibrated for consistency:
            #   1,200/mo * 12 * (1/700) * 0.97 ≈ $20/SF/yr
            base_revenue_per_sf_annual=20.0,
            base_revenue_per_unit_monthly=1200,
            units_per_sf=0.00143,  # ≈ 1 unit / 700 SF
            occupancy_rate_base=0.97,
            occupancy_rate_premium=0.96,
            operating_margin_base=0.55,
            operating_margin_premium=0.6,
            
            # Valuation parameters
            market_cap_rate=0.075,  # 7.5% for affordable housing
            
            # Expense ratios for operational efficiency calculations
            management_fee_ratio=0.06,       # 6% - compliance adds complexity
            maintenance_cost_ratio=0.09,     # 9% - deferred maintenance common
            utility_cost_ratio=0.05,         # 5% - owner pays more utilities
            insurance_cost_ratio=0.03,       # 3% - higher risk profile
            property_tax_ratio=0.08,         # 8% - often tax advantaged
            marketing_ratio=0.01,            # 1% - high demand, low marketing
            reserves_ratio=0.04,             # 4% - required reserves
            security_ratio=0.01,             # 1% - basic security
            supply_cost_ratio=0.01           # 1% - basic supplies
        )
    },
    
    # ------------------------------------------------------------------------
    # OFFICE
    # ------------------------------------------------------------------------
    BuildingType.OFFICE: {
        'class_a': BuildingConfig(
            display_name='Class A Office',
            base_cost_per_sf=475,
            cost_range=(440, 510),
            equipment_cost_per_sf=15,
            typical_floors=10,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.25,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25
            ),
            
            # Target ~24% owner soft costs for premium Class A delivery
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.012,
                financing=0.03,
                contingency=0.075,
                testing=0.008,
                construction_management=0.035,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.06,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.08,
                )
            },
            
            nlp=NLPConfig(
                keywords=['class a office', 'corporate headquarters', 'tower',
                         'high-rise office', 'premium office'],
                priority=8,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.92,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25
            },
            
            special_features={
                'fitness_center': 35,       # On-site gym
                'cafeteria': 30,            # Food service area
                'conference_center': 40,    # Large meeting facilities
                'structured_parking': 45,   # Parking garage
                'green_roof': 35,           # Rooftop garden
                'outdoor_terrace': 25,      # Outdoor work/break area
                'executive_floor': 45,      # C-suite buildout
                'data_center': 55,          # On-site server room
                'concierge': 20,            # Lobby concierge desk
            },

            # Revenue metrics (Nashville Class A calibration)
            base_revenue_per_sf_annual=41.0,  # realistic effective rent
            occupancy_rate_base=0.92,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.48,
            operating_margin_premium=0.52,
            operating_expense_per_sf=11.0,
            cam_charges_per_sf=7.0,
            staffing_pct_property_mgmt=0.06,
            staffing_pct_maintenance=0.12,
            market_cap_rate=0.06,
            financial_metrics=OFFICE_UNDERWRITING_CONFIG["class_a"],
            
            # Expense ratios for operational efficiency calculations
            utility_cost_ratio=0.08,         # 8% - HVAC, electric, water for premium space
            property_tax_ratio=0.12,         # 12% - higher value = higher tax
            insurance_cost_ratio=0.02,       # 2% - property and liability
            maintenance_cost_ratio=0.06,     # 6% - elevators, HVAC, common areas
            management_fee_ratio=0.03,       # 3% - professional property management
            janitorial_ratio=0.04,          # 4% - daily cleaning services
            security_ratio=0.02,            # 2% - 24/7 security and access control
            reserves_ratio=0.02             # 2% - capital improvements
        ),
        
        'class_b': BuildingConfig(
            display_name='Class B Office',
            base_cost_per_sf=175,
            cost_range=(150, 200),
            equipment_cost_per_sf=10,
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.22,
                electrical=0.14,
                plumbing=0.11,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.062,
                    equity_ratio=0.28,
                    target_dscr=1.20,
                    target_roi=0.09,
                )
            },
            
            nlp=NLPConfig(
                keywords=['office', 'office building', 'class b',
                         'commercial office', 'professional building'],
                priority=9,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.90,
                'New York': 1.40,
                'San Francisco': 1.45
            },
            
            special_features={
                'fitness_center': 30,       # Basic gym
                'cafeteria': 25,            # Break room/kitchen
                'conference_room': 20,      # Meeting rooms
                'surface_parking': 15,      # Additional parking
                'storage_space': 10,        # Extra storage
                'security_desk': 15,        # Lobby security
            },

            # Revenue metrics
            base_revenue_per_sf_annual=28,
            occupancy_rate_base=0.85,
            occupancy_rate_premium=0.88,
            operating_margin_base=0.60,
            operating_margin_premium=0.65,
            
            # Expense ratios for operational efficiency calculations
            utility_cost_ratio=0.10,         # 10% - less efficient systems
            property_tax_ratio=0.14,         # 14% - moderate value properties
            insurance_cost_ratio=0.02,       # 2% - standard coverage
            maintenance_cost_ratio=0.08,     # 8% - older systems need more maintenance
            management_fee_ratio=0.04,       # 4% - property management
            janitorial_ratio=0.03,          # 3% - standard cleaning
            security_ratio=0.01,            # 1% - basic security
            reserves_ratio=0.03             # 3% - higher reserves for older buildings
        )
    },
    
    # ------------------------------------------------------------------------
    # RETAIL
    # ------------------------------------------------------------------------
    BuildingType.RETAIL: {
        'shopping_center': BuildingConfig(
            display_name='Shopping Center',
            base_cost_per_sf=150,
            cost_range=(125, 175),
            equipment_cost_per_sf=5,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.058,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.10,
                )
            },
            
            nlp=NLPConfig(
                keywords=['shopping center', 'retail center', 'strip mall',
                         'strip center', 'plaza', 'shopping plaza'],
                priority=10,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40
            },
            
            special_features={
                'covered_walkway': 20,      # Covered storefronts
                'loading_dock': 25,         # Shared loading area
                'monument_signage': 15,     # Main sign structure
                'outdoor_seating': 20,      # Common area seating
                'drive_thru': 40,           # For end-cap tenants
                'storage_units': 15,        # Back storage areas
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            base_sales_per_sf_annual=350,
            occupancy_rate_base=0.92,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.65,
            operating_margin_premium=0.70
        ),
        
        'big_box': BuildingConfig(
            display_name='Big Box Retail',
            base_cost_per_sf=125,
            cost_range=(100, 150),
            equipment_cost_per_sf=3,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.35,
                mechanical=0.18,
                electrical=0.14,
                plumbing=0.08,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.06,
                    equity_ratio=0.28,
                    target_dscr=1.20,
                    target_roi=0.09,
                )
            },
            
            nlp=NLPConfig(
                keywords=['big box', 'anchor tenant', 'department store',
                         'superstore', 'warehouse retail'],
                priority=11,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.30,
                'San Francisco': 1.35
            },
            
            special_features={
                'loading_dock': 20,         # Multiple dock doors
                'mezzanine': 25,            # Upper level storage
                'auto_center': 45,          # Auto service bays
                'garden_center': 30,        # Outdoor sales area
                'warehouse_racking': 15,    # High-bay storage
                'refrigerated_storage': 35, # Cold storage areas
                'curbside_pickup': 20,      # Dedicated pickup area
            },

            # Revenue metrics
            base_revenue_per_sf_annual=25,
            base_sales_per_sf_annual=200,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.60,
            operating_margin_premium=0.65
        )
    },
    
    # ------------------------------------------------------------------------
    # RESTAURANT
    # ------------------------------------------------------------------------
    BuildingType.RESTAURANT: {
        'quick_service': BuildingConfig(
            display_name='Quick Service Restaurant',
            base_cost_per_sf=360,
            cost_range=(250, 350),
            equipment_cost_per_sf=40,  # Kitchen equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.28,
                electrical=0.15,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.055,
                permits=0.02,
                legal=0.007,
                financing=0.02,
                contingency=0.06,
                testing=0.005,
                construction_management=0.03,
                startup=0.015
            ),  # Total: 18% soft costs
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['fast food', 'quick service', 'QSR', 'drive through',
                         'fast casual', 'takeout'],
                priority=12,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.35,
                'San Francisco': 1.40
            },
            
            special_features={
                'drive_thru': 40,           # Drive-thru lane and window
                'outdoor_seating': 20,      # Patio seating area
                'play_area': 35,            # Children's playground
                'double_drive_thru': 55,    # Dual drive-thru lanes
                'digital_menu_boards': 15,  # Digital ordering displays
            },

            # Revenue metrics
            base_revenue_per_sf_annual=525,
            occupancy_rate_base=0.88,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.12,
            operating_margin_premium=0.18,
            
            # Expense ratios for operational efficiency calculations
            food_cost_ratio=0.28,            # 28% - industry target for QSR
            labor_cost_ratio=0.30,           # 30% - lower due to simpler operations
            beverage_cost_ratio=0.08,        # 8% - soft drinks high margin
            management_fee_ratio=0.04,       # 4% - often franchise management
            utility_cost_ratio=0.04,         # 4% - cooking equipment usage
            maintenance_cost_ratio=0.03,     # 3% - equipment maintenance
            marketing_ratio=0.04,            # 4% - local and national advertising
            franchise_fee_ratio=0.06,        # 6% - typical franchise royalty
            insurance_cost_ratio=0.02        # 2% - general liability
        ),
        
        'full_service': BuildingConfig(
            display_name='Full Service Restaurant',
            base_cost_per_sf=385,  # Optimized for industry standards ($450-500/SF total)
            cost_range=(350, 425),
            equipment_cost_per_sf=25,  # Optimized - kitchen equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.20,
                mechanical=0.30,
                electrical=0.16,
                plumbing=0.14,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,      # 5% - simpler design than complex buildings
                permits=0.015,         # 1.5%
                legal=0.005,           # 0.5%
                financing=0.02,        # 2% - shorter construction period
                contingency=0.05,      # 5% - well-understood building type
                testing=0.005,         # 0.5% - kitchen equipment testing
                construction_management=0.025,  # 2.5%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 18% soft costs
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.068,
                    equity_ratio=0.40,
                    target_dscr=1.30,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['restaurant', 'dining', 'sit-down', 'full service',
                         'casual dining', 'family restaurant'],
                priority=13,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.40,
                'San Francisco': 1.45
            },
            
            special_features={
                'outdoor_seating': 25,      # Patio/sidewalk dining
                'bar': 35,                  # Full bar setup
                'private_dining': 30,       # Private dining rooms
                'wine_cellar': 45,          # Temperature-controlled wine storage
                'live_kitchen': 25,         # Open/exhibition kitchen
                'rooftop_dining': 50,       # Rooftop terrace dining
                'valet_parking': 20,        # Valet setup
            },

            # Revenue metrics
            base_revenue_per_sf_annual=350,
            occupancy_rate_base=0.80,
            occupancy_rate_premium=0.90,
            operating_margin_base=0.10,
            operating_margin_premium=0.12,
            
            # Expense ratios for operational efficiency calculations
            food_cost_ratio=0.32,            # 32% - higher quality ingredients
            labor_cost_ratio=0.33,           # 33% - servers, hosts, bussers
            beverage_cost_ratio=0.15,        # 15% - includes alcohol program
            management_fee_ratio=0.05,       # 5% - general management
            utility_cost_ratio=0.04,         # 4% - full kitchen operations
            maintenance_cost_ratio=0.03,     # 3% - facility and equipment
            marketing_ratio=0.03,            # 3% - local marketing
            insurance_cost_ratio=0.02,       # 2% - including liquor liability
            supply_cost_ratio=0.02           # 2% - napkins, utensils, etc.
        ),
        
        'fine_dining': BuildingConfig(
            display_name='Fine Dining Restaurant',
            base_cost_per_sf=550,  # Premium construction and finishes
            cost_range=(500, 650),
            equipment_cost_per_sf=50,  # High-end kitchen equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.18,
                mechanical=0.28,  # Advanced HVAC for comfort
                electrical=0.18,  # Sophisticated lighting systems
                plumbing=0.14,
                finishes=0.22     # Premium finishes and materials
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,      # 8% - high-end design and architects
                permits=0.02,          # 2%
                legal=0.01,            # 1%
                financing=0.03,        # 3% - larger investment
                contingency=0.08,      # 8% - complex finishes
                testing=0.01,          # 1% - extensive equipment testing
                construction_management=0.04,  # 4% - more oversight needed
                startup=0.02           # 2% - extensive training
            ),  # Total: 29% soft costs
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.55,
                    debt_rate=0.07,
                    equity_ratio=0.45,
                    target_dscr=1.35,
                    target_roi=0.18
                )
            },
            
            nlp=NLPConfig(
                keywords=['fine dining', 'upscale', 'white tablecloth', 
                         'gourmet', 'haute cuisine', 'michelin', 'tasting menu'],
                priority=14,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.04,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.45,
                'San Francisco': 1.50
            },
            
            special_features={
                'wine_cellar': 60,          # Premium wine storage
                'private_dining': 45,       # Multiple private rooms
                'chef_table': 40,           # Chef's table experience
                'dry_aging_room': 50,       # Meat aging facility
                'pastry_kitchen': 35,       # Separate pastry kitchen
                'sommelier_station': 30,    # Wine service station
                'valet_parking': 25,        # Valet required
            },

            # Revenue metrics - higher per SF due to premium pricing
            base_revenue_per_sf_annual=750,
            occupancy_rate_base=0.82,      # Lower occupancy but higher prices
            occupancy_rate_premium=0.85,
            operating_margin_base=0.12,    # Better margins on premium food
            operating_margin_premium=0.18,
            
            # Expense ratios for operational efficiency calculations
            food_cost_ratio=0.28,          # 28% - premium ingredients but better margins
            labor_cost_ratio=0.35,         # 35% - highly skilled staff
            beverage_cost_ratio=0.18,      # 18% - extensive wine program
            management_fee_ratio=0.06,     # 6% - specialized management
            utility_cost_ratio=0.03,       # 3% - efficient systems
            maintenance_cost_ratio=0.03,   # 3% - preventive maintenance
            marketing_ratio=0.02,          # 2% - reputation-driven
            insurance_cost_ratio=0.02,     # 2% - comprehensive coverage
            supply_cost_ratio=0.03         # 3% - premium tableware
        ),
        
        'bar_tavern': BuildingConfig(
            display_name='Bar/Tavern',
            base_cost_per_sf=350,  # Adjusted to industry standard
            cost_range=(325, 375),
            equipment_cost_per_sf=25,  # Bar equipment included in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.25,
                electrical=0.18,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,      # 5% - simpler design than complex buildings
                permits=0.02,          # 2% - includes liquor license
                legal=0.01,            # 1% - includes liquor license legal
                financing=0.02,        # 2% - shorter construction period
                contingency=0.05,      # 5% - well-understood building type
                testing=0.005,         # 0.5% - bar equipment testing
                construction_management=0.025,  # 2.5%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 19% soft costs (slightly higher for liquor licensing)
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.14
                )
            },
            
            nlp=NLPConfig(
                keywords=['bar', 'tavern', 'pub', 'lounge', 'nightclub', 
                         'cocktail bar', 'sports bar', 'brewpub'],
                priority=13,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42
            },
            
            special_features={
                'outdoor_seating': 25,      # Patio/beer garden
                'live_music_stage': 30,     # Performance stage
                'game_room': 25,            # Pool tables, darts, etc.
                'rooftop_bar': 50,          # Rooftop bar area
                'private_party_room': 30,   # Private event space
                'craft_beer_system': 35,    # Specialized tap system
            },

            # Revenue metrics
            base_revenue_per_sf_annual=450,
            occupancy_rate_base=0.80,
            occupancy_rate_premium=0.88,
            operating_margin_base=0.14,
            operating_margin_premium=0.18,
            
            # Expense ratios for operational efficiency calculations
            food_cost_ratio=0.25,            # 25% - limited food menu
            labor_cost_ratio=0.28,           # 28% - bartenders and servers
            beverage_cost_ratio=0.20,        # 20% - alcohol is primary focus
            management_fee_ratio=0.05,       # 5% - bar management
            utility_cost_ratio=0.03,         # 3% - less cooking
            maintenance_cost_ratio=0.03,     # 3% - equipment maintenance
            marketing_ratio=0.04,            # 4% - promotions and events
            insurance_cost_ratio=0.03,       # 3% - higher liquor liability
            security_ratio=0.02              # 2% - bouncer/security needs
        ),
        
        'cafe': BuildingConfig(
            display_name='Cafe/Coffee Shop',
            base_cost_per_sf=300,  # Adjusted to industry standard
            cost_range=(275, 325),
            equipment_cost_per_sf=20,  # Coffee equipment mostly in base cost
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.23,
                mechanical=0.22,
                electrical=0.16,
                plumbing=0.14,
                finishes=0.25
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,     # 4.5% - simpler cafe design
                permits=0.015,         # 1.5%
                legal=0.005,           # 0.5%
                financing=0.02,        # 2% - shorter construction period
                contingency=0.045,     # 4.5% - simple, well-understood
                testing=0.005,         # 0.5% - coffee equipment testing
                construction_management=0.02,   # 2%
                startup=0.01           # 1% - training, initial inventory
            ),  # Total: 16% soft costs (lower for simpler cafes)
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.063,
                    equity_ratio=0.32,
                    target_dscr=1.22,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['cafe', 'coffee shop', 'coffee house', 'espresso bar',
                         'coffee bar', 'bakery cafe', 'tea shop'],
                priority=12,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.35,
                'San Francisco': 1.40
            },
            
            special_features={
                'outdoor_seating': 20,      # Sidewalk/patio seating
                'drive_thru': 35,           # Coffee drive-thru
                'bakery_display': 15,       # Display cases
                'lounge_area': 20,          # Comfortable seating area
                'meeting_room': 25,         # Small meeting space
            },

            # Revenue metrics
            base_revenue_per_sf_annual=350,
            occupancy_rate_base=0.80,
            occupancy_rate_premium=0.85,
            operating_margin_base=0.11,
            operating_margin_premium=0.14,
            
            # Expense ratios for operational efficiency calculations
            food_cost_ratio=0.30,            # 30% - pastries and light food
            labor_cost_ratio=0.35,           # 35% - baristas and bakers
            beverage_cost_ratio=0.12,        # 12% - coffee and specialty drinks
            management_fee_ratio=0.04,       # 4% - simple management
            utility_cost_ratio=0.03,         # 3% - espresso machines, ovens
            maintenance_cost_ratio=0.02,     # 2% - equipment maintenance
            marketing_ratio=0.03,            # 3% - local marketing
            insurance_cost_ratio=0.02,       # 2% - general liability
            supply_cost_ratio=0.03           # 3% - cups, lids, napkins
        )
    },
    
    # ------------------------------------------------------------------------
    # INDUSTRIAL
    # ------------------------------------------------------------------------
    BuildingType.INDUSTRIAL: {
        'warehouse': BuildingConfig(
            display_name='Class A Distribution Warehouse',
            # Core & shell cost for bulk distribution (tilt-up / precast) in 2025.
            base_cost_per_sf=105,
            cost_range=(95, 125),
            equipment_cost_per_sf=5,  # Dock equipment, minimal FFE
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.35,  # Large clear spans
                mechanical=0.15,  # Minimal HVAC
                electrical=0.12,
                plumbing=0.08,   # Minimal plumbing
                finishes=0.30
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.01,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.07,  # Market standard 7% for warehouse
                )
            },
            
            nlp=NLPConfig(
                keywords=['warehouse', 'storage', 'distribution', 'logistics', 
                         'fulfillment center', 'bulk storage'],
                priority=14,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.00,
                'Memphis': 0.96,
                'Atlanta': 1.02,
                'Chicago': 1.05,
                'Dallas': 1.00,
                'Los Angeles': 1.15,
                'New York': 1.12
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
            utility_cost_ratio=0.03,         # 3% - minimal HVAC, basic lighting
            property_tax_ratio=0.08,         # 8% - lower value industrial land
            insurance_cost_ratio=0.02,       # 2% - property and liability
            maintenance_cost_ratio=0.03,     # 3% - simple systems, dock maintenance
            management_fee_ratio=0.02,       # 2% - minimal management needed
            security_ratio=0.01,             # 1% - basic security systems
            reserves_ratio=0.02,             # 2% - capital reserves
            labor_cost_ratio=0.02            # 2% - minimal staffing (security, maintenance)
            # Total operating ratio: ~15% (very efficient operations)
        ),
        
        'distribution_center': BuildingConfig(
            display_name='Distribution Center',
            base_cost_per_sf=95,
            cost_range=(80, 110),
            equipment_cost_per_sf=8,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.33,
                mechanical=0.17,  # More HVAC than warehouse
                electrical=0.13,
                plumbing=0.09,
                finishes=0.28
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.045,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.065,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
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
                keywords=['distribution center', 'distribution', 'DC', 'cross-dock',
                         'sorting facility', 'hub'],
                priority=15,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,  # Memphis is distribution hub
                'New York': 1.28,
                'San Francisco': 1.32,
                'Chicago': 1.12,
                'Miami': 1.06
            },
            
            special_features={
                'automated_sorting': 25,
                'refrigerated_area': 35,
                'loading_docks': 15
            },

            # Revenue metrics
            base_revenue_per_sf_annual=10,
            occupancy_rate_base=0.96,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.68,
            operating_margin_premium=0.72
        ),
        
        'manufacturing': BuildingConfig(
            display_name='Manufacturing Facility',
            base_cost_per_sf=125,
            cost_range=(100, 150),
            equipment_cost_per_sf=35,  # Process equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.25,  # Heavy mechanical
                electrical=0.18,  # Heavy power
                plumbing=0.12,
                finishes=0.17
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.08,  # Market standard 8% for manufacturing
            
            # Financial metrics
            
            
            # Financial metrics
            
            
            # Financial metrics
            
            
            # Financial metrics
            
                )
            },
            
            nlp=NLPConfig(
                keywords=['manufacturing', 'factory', 'production', 'plant',
                         'assembly', 'fabrication', 'processing'],
                priority=16,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            
            special_features={
                'clean_room': 75,
                'heavy_power': 40,
                'crane_bays': 30,
                'compressed_air': 20
            },

            # Revenue metrics
            base_revenue_per_sf_annual=12,
            occupancy_rate_base=0.92,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.65,
            operating_margin_premium=0.70,
            
            # Add these expense ratios for operational efficiency calculations
            utility_cost_ratio=0.08,         # 8% - production equipment power
            property_tax_ratio=0.06,         # 6% - industrial zones
            insurance_cost_ratio=0.03,       # 3% - higher due to equipment/liability
            maintenance_cost_ratio=0.06,     # 6% - equipment maintenance critical
            management_fee_ratio=0.02,       # 2% - facility management
            security_ratio=0.01,             # 1% - standard security
            reserves_ratio=0.03,             # 3% - equipment replacement reserves
            labor_cost_ratio=0.35,           # 35% - production staff (if included)
            raw_materials_ratio=0.25         # 25% - materials for production
            # Total operating ratio: ~25% facility costs (excluding production labor/materials)
        ),
        
        'flex_space': BuildingConfig(
            display_name='Flex Space',
            base_cost_per_sf=110,
            cost_range=(95, 125),
            equipment_cost_per_sf=10,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.30,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.25  # Better finishes for office portion
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.07,
                testing=0.005,
                construction_management=0.025,
                startup=0.008
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
                keywords=['flex space', 'flex', 'warehouse office', 'light industrial',
                         'r&d space', 'tech space'],
                priority=17,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.30,
                'San Francisco': 1.35,
                'Chicago': 1.12,
                'Miami': 1.07
            },

            # Revenue metrics
            base_revenue_per_sf_annual=15,
            occupancy_rate_base=0.88,
            occupancy_rate_premium=0.92,
            operating_margin_base=0.60,
            operating_margin_premium=0.65,
            
            # Add these expense ratios for operational efficiency calculations
            utility_cost_ratio=0.05,         # 5% - mixed use, some office HVAC
            property_tax_ratio=0.09,         # 9% - higher value than pure warehouse
            insurance_cost_ratio=0.02,       # 2% - standard coverage
            maintenance_cost_ratio=0.04,     # 4% - office and warehouse systems
            management_fee_ratio=0.03,       # 3% - more complex management
            janitorial_ratio=0.02,           # 2% - office areas need cleaning
            security_ratio=0.01,             # 1% - access control
            reserves_ratio=0.02,             # 2% - capital reserves
            labor_cost_ratio=0.03            # 3% - facility staff
            # Total operating ratio: ~20% (between warehouse and office)
        ),
        
        'cold_storage': BuildingConfig(
            display_name='Cold Storage Facility',
            base_cost_per_sf=175,
            cost_range=(150, 200),
            equipment_cost_per_sf=45,  # Refrigeration equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.35,  # Heavy refrigeration
                electrical=0.18,  # High power for refrigeration
                plumbing=0.10,
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.015,  # More testing for systems
                construction_management=0.03,
                startup=0.02
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
                keywords=['cold storage', 'freezer', 'refrigerated', 'frozen storage',
                         'cooler', 'cold chain'],
                priority=18,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.32,
                'San Francisco': 1.38,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'blast_freezer': 50,
                'multiple_temp_zones': 30,
                'automated_retrieval': 40
            },

            # Revenue metrics
            base_revenue_per_sf_annual=18,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.55,
            operating_margin_premium=0.60,
            
            # Add these expense ratios for operational efficiency calculations
            utility_cost_ratio=0.15,         # 15% - massive refrigeration costs
            property_tax_ratio=0.07,         # 7% - specialized facility
            insurance_cost_ratio=0.03,       # 3% - higher due to product liability
            maintenance_cost_ratio=0.08,     # 8% - refrigeration equipment critical
            management_fee_ratio=0.03,       # 3% - specialized management
            security_ratio=0.02,             # 2% - temperature monitoring, security
            reserves_ratio=0.04,             # 4% - refrigeration equipment reserves
            labor_cost_ratio=0.05,           # 5% - specialized operators
            monitoring_cost_ratio=0.03       # 3% - 24/7 temperature monitoring
            # Total operating ratio: ~30% (high due to refrigeration)
        )
    },
    
    # ------------------------------------------------------------------------
    # HOSPITALITY
    # ------------------------------------------------------------------------
    BuildingType.HOSPITALITY: {
        'full_service_hotel': BuildingConfig(
            display_name='Full Service Hotel',
            base_cost_per_sf=325,
            cost_range=(275, 375),
            equipment_cost_per_sf=45,  # FF&E
            typical_floors=8,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.26,
                electrical=0.14,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.02,
                financing=0.035,
                contingency=0.09,
                testing=0.01,
                construction_management=0.035,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.30,
                    target_roi=0.11,
                )
            },
            
            nlp=NLPConfig(
                keywords=['hotel', 'full service hotel', 'convention hotel',
                         'resort hotel', 'luxury hotel'],
                priority=19,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.20
            },
            
            special_features={
                'ballroom': 50,
                'restaurant': 75,
                'spa': 60,
                'conference_center': 45,
                'rooftop_bar': 55
            },

            # Revenue metrics
            base_revenue_per_sf_annual=80,
            base_revenue_per_room_annual=120000,
            rooms_per_sf=0.002,
            occupancy_rate_base=0.75,
            occupancy_rate_premium=0.82,
            operating_margin_base=0.30,
            operating_margin_premium=0.38,
            
            # Standard expense ratios for operational efficiency calculations
            labor_cost_ratio=0.37,           # 37% - 12% rooms ops + 25% F&B ops = total labor
            food_cost_ratio=0.10,            # 10% - Food purchases for restaurants/catering
            management_fee_ratio=0.03,       # 3% - Hotel management company
            utility_cost_ratio=0.06,         # 6% - 24/7 operations, pools, kitchens
            maintenance_cost_ratio=0.04,     # 4% - Constant wear from guests
            insurance_cost_ratio=0.02,       # 2% - Property and liability
            property_tax_ratio=0.10,         # 10% - Valuable real estate
            marketing_ratio=0.08,            # 8% - Sales & marketing (higher than other types)
            reserves_ratio=0.04,             # 4% - FF&E replacement
            franchise_fee_ratio=0.06         # 6% - Franchise fees, misc expenses
        ),
        
        # Adjusted select-service hotel profile for realistic underwriting.
        # Target: NOI margin 33–36% with yield-on-cost 9–10% for downtown Nashville.
        'limited_service_hotel': BuildingConfig(
            display_name='Select Service Hotel',
            base_cost_per_sf=205,
            cost_range=(190, 230),
            equipment_cost_per_sf=28,
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.24,
                electrical=0.13,
                plumbing=0.17,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.03,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.12,
                )
            },
            
            nlp=NLPConfig(
                keywords=['limited service', 'select service', 'express hotel',
                         'budget hotel', 'economy hotel'],
                priority=20,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'breakfast_area': 20,
                'fitness_center': 15,
                'business_center': 10,
                'pool': 25
            },

            # Revenue metrics (rooms-driven)
            base_revenue_per_sf_annual=52,
            base_revenue_per_room_annual=50000,
            rooms_per_sf=1.0 / 600.0,
            occupancy_rate_base=0.72,
            occupancy_rate_premium=0.80,
            operating_margin_base=0.37,
            operating_margin_premium=0.42,
            base_adr_by_market={
                'primary': 195.0,
                'secondary': 180.0,
                'tertiary': 165.0,
            },
            base_occupancy_by_market={
                'primary': 0.72,
                'secondary': 0.68,
                'tertiary': 0.64,
            },
            expense_percentages={
                'staffing_pct': 0.30,
                'utilities_ops_pct': 0.14,
                'sales_marketing_gna_pct': 0.09,
                'management_fee_pct': 0.03,
                'franchise_fee_pct': 0.07,
                'ffe_reserve_pct': 0.04,
            },
            development_cost_per_sf_by_finish={
                'standard': 190.0,
                'premium': 220.0,
            },
            cap_rate_defaults={
                'low': 0.070,
                'base': 0.075,
                'high': 0.085,
            },
            yield_on_cost_hurdle=0.095,
            dscr_target=1.38,
            
            # Standard expense ratios for operational efficiency calculations
            labor_cost_ratio=0.24,           # Staffing + departmental labor
            food_cost_ratio=0.03,            # Continental breakfast supplies
            management_fee_ratio=0.03,       # Operator fee
            utility_cost_ratio=0.12,         # Utilities + ops
            maintenance_cost_ratio=0.05,     # PPE / ongoing capex
            insurance_cost_ratio=0.02,       # Property & liability
            property_tax_ratio=0.10,         # Typical metro rate
            marketing_ratio=0.08,            # OTA commissions, sales & marketing
            reserves_ratio=0.05,             # FF&E reserves
            franchise_fee_ratio=0.05         # Franchise & system fees
        )
    },
    
    # ------------------------------------------------------------------------
    # EDUCATIONAL
    # ------------------------------------------------------------------------
    BuildingType.EDUCATIONAL: {
        'elementary_school': BuildingConfig(
            display_name='Elementary School',
            base_cost_per_sf=285,
            cost_range=(260, 310),
            equipment_cost_per_sf=25,  # Classroom equipment, playground
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.24,  # Good ventilation crucial
                electrical=0.13,
                plumbing=0.15,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,  # Municipal bonds
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0  # Public good
                )
            },
            
            
            nlp=NLPConfig(
                keywords=['elementary school', 'primary school', 'grade school',
                         'K-5', 'K-6', 'elementary'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.18,
                'Miami': 1.10
            },
            
            special_features={
                'gymnasium': 35,
                'cafeteria': 30,
                'playground': 20,
                'computer_lab': 25,
                'library': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            base_revenue_per_student_annual=12000,
            students_per_sf=0.00667,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.05,
            operating_margin_premium=0.08
        ),
        
        'middle_school': BuildingConfig(
            display_name='Middle School',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=30,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.25,
                electrical=0.14,
                plumbing=0.15,
                finishes=0.19
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0,
                )
            },
            
            nlp=NLPConfig(
                keywords=['middle school', 'junior high', 'intermediate school',
                         'grades 6-8', 'grades 7-9'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.18,
                'Miami': 1.10
            },
            
            special_features={
                'gymnasium': 40,
                'cafeteria': 30,
                'science_labs': 35,
                'computer_lab': 25,
                'auditorium': 45,
                'athletic_field': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            base_revenue_per_student_annual=13000,
            students_per_sf=0.00625,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.05,
            operating_margin_premium=0.08
        ),
        
        'high_school': BuildingConfig(
            display_name='High School',
            base_cost_per_sf=315,
            cost_range=(290, 340),
            equipment_cost_per_sf=35,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.26,  # Labs need ventilation
                electrical=0.15,
                plumbing=0.15,
                finishes=0.18
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.075,
                permits=0.022,
                legal=0.015,
                financing=0.025,
                contingency=0.085,
                testing=0.012,
                construction_management=0.04,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.15,
                    target_roi=0.0,
                )
            },
            
            nlp=NLPConfig(
                keywords=['high school', 'secondary school', 'senior high',
                         'grades 9-12', 'preparatory school'],
                priority=2,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'stadium': 60,
                'field_house': 50,
                'performing_arts_center': 55,
                'science_labs': 40,
                'vocational_shops': 45,
                'media_center': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            base_revenue_per_student_annual=14000,
            students_per_sf=0.005,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.05,
            operating_margin_premium=0.08
        ),
        
        'university': BuildingConfig(
            display_name='University Building',
            base_cost_per_sf=375,
            cost_range=(325, 425),
            equipment_cost_per_sf=50,  # Lab equipment, technology
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.28,  # Complex systems
                electrical=0.16,
                plumbing=0.14,
                finishes=0.17
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.025,
                legal=0.02,
                financing=0.03,
                contingency=0.09,
                testing=0.015,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,  # Tax-exempt bonds
                    equity_ratio=0.15,
                    philanthropy_ratio=0.20,  # Donations
                    grants_ratio=0.05,
                    target_dscr=1.20,
                    target_roi=0.0,
                ),
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.08
                )
            },
            
            nlp=NLPConfig(
                keywords=['university', 'college', 'academic building', 'campus',
                         'lecture hall', 'classroom building', 'higher education'],
                priority=24,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.42,
                'San Francisco': 1.48,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'lecture_hall': 45,
                'research_lab': 75,
                'clean_room': 100,
                'library': 40,
                'student_center': 35
            },

            # Revenue metrics
            base_revenue_per_sf_annual=200,
            base_revenue_per_student_annual=25000,
            students_per_sf=0.004,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.15,
            operating_margin_premium=0.20
        ),
        
        'community_college': BuildingConfig(
            display_name='Community College',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=30,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.25,
                electrical=0.14,
                plumbing=0.14,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.075,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.04,
                    equity_ratio=0.25,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.0,
                )
            },
            
            nlp=NLPConfig(
                keywords=['community college', 'junior college', 'technical college',
                         'vocational school', 'trade school'],
                priority=25,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.08
            },
            
            special_features={
                'vocational_lab': 40,
                'computer_lab': 25,
                'library': 20,
                'student_services': 15
            },

            # Revenue metrics
            base_revenue_per_sf_annual=150,
            base_revenue_per_student_annual=8000,
            students_per_sf=0.005,
            occupancy_rate_base=0.85,
            occupancy_rate_premium=0.92,
            operating_margin_base=0.08,
            operating_margin_premium=0.12
        )
    },
    
    # ------------------------------------------------------------------------
    # MIXED_USE
    # ------------------------------------------------------------------------
    BuildingType.MIXED_USE: {
        'retail_residential': BuildingConfig(
            display_name='Retail with Residential Above',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=20,
            typical_floors=5,  # 1 retail + 4 residential
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.17,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.08,
                testing=0.008,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.72,
                    debt_rate=0.058,
                    equity_ratio=0.28,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            nlp=NLPConfig(
                keywords=['mixed use', 'retail residential', 'shops with apartments',
                         'ground floor retail', 'live work'],
                priority=26,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.18
            },
            
            special_features={
                'rooftop_deck': 30,
                'parking_podium': 40,
                'retail_plaza': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        ),
        
        'office_residential': BuildingConfig(
            display_name='Office with Residential',
            base_cost_per_sf=245,
            cost_range=(220, 270),
            equipment_cost_per_sf=18,
            typical_floors=8,  # 3 office + 5 residential
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.065,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.085,
                testing=0.01,
                construction_management=0.032,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.060,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['office residential', 'mixed use tower', 'office with housing',
                         'work live', 'commercial residential'],
                priority=27,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.48,
                'San Francisco': 1.52,
                'Chicago': 1.28,
                'Miami': 1.20
            },
            
            special_features={
                'amenity_deck': 35,
                'business_center': 20,
                'conference_facility': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        ),
        
        'hotel_retail': BuildingConfig(
            display_name='Hotel with Retail',
            base_cost_per_sf=295,
            cost_range=(270, 320),
            equipment_cost_per_sf=35,
            typical_floors=10,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.25,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.02,
                financing=0.032,
                contingency=0.09,
                testing=0.01,
                construction_management=0.035,
                startup=0.018
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.062,
                    equity_ratio=0.32,
                    target_dscr=1.28,
                    target_roi=0.11
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['hotel retail', 'hotel with shops', 'hospitality mixed use',
                         'hotel complex', 'resort retail'],
                priority=28,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.22
            },
            
            special_features={
                'conference_center': 45,
                'restaurant': 50,
                'spa': 55,
                'retail_arcade': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        ),
        
        'urban_mixed': BuildingConfig(
            display_name='Urban Mixed Use',
            base_cost_per_sf=265,
            cost_range=(240, 290),
            equipment_cost_per_sf=25,
            typical_floors=12,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.028,
                legal=0.02,
                financing=0.032,
                contingency=0.09,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.060,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['urban mixed', 'mixed use development', 'multi-use',
                         'live work play', 'vertical mixed'],
                priority=29,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.48,
                'San Francisco': 1.55,
                'Chicago': 1.30,
                'Miami': 1.22
            },
            
            special_features={
                'public_plaza': 40,
                'green_roof': 35,
                'parking_structure': 45,
                'transit_connection': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        ),
        
        'transit_oriented': BuildingConfig(
            display_name='Transit-Oriented Development',
            base_cost_per_sf=275,
            cost_range=(250, 300),
            equipment_cost_per_sf=22,
            typical_floors=8,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.23,
                electrical=0.15,
                plumbing=0.16,
                finishes=0.21
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.03,
                legal=0.022,
                financing=0.032,
                contingency=0.09,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.058,
                    equity_ratio=0.32,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.PPP: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,
                    equity_ratio=0.20,
                    grants_ratio=0.20,  # Transit grants
                    target_dscr=1.20,
                    target_roi=0.08
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['TOD', 'transit oriented', 'transit development', 'station area',
                         'transit village', 'metro development'],
                priority=30,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,  # No transit
                'Memphis': 0.93,
                'New York': 1.50,  # High transit value
                'San Francisco': 1.55,
                'Chicago': 1.35,
                'Miami': 1.20
            },
            
            special_features={
                'transit_plaza': 35,
                'bike_facility': 20,
                'pedestrian_bridge': 45,
                'public_art': 15
            },

            # Financial metrics
            
            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.93,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        )
    },
            
    
    # ------------------------------------------------------------------------
    # SPECIALTY
    # ------------------------------------------------------------------------
    BuildingType.SPECIALTY: {
        'data_center': BuildingConfig(
            display_name='Data Center',
            base_cost_per_sf=1200,  # Very high due to infrastructure
            cost_range=(1000, 1400),
            equipment_cost_per_sf=400,  # Servers, cooling, UPS
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.15,
                mechanical=0.40,  # Massive cooling requirements
                electrical=0.30,  # Redundant power systems
                plumbing=0.05,
                finishes=0.10
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.02,
                financing=0.04,
                contingency=0.10,
                testing=0.02,  # Critical testing
                construction_management=0.04,
                startup=0.03
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.065,
                    equity_ratio=0.40,
                    target_dscr=1.35,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['data center', 'server farm', 'colocation', 'colo',
                         'cloud facility', 'computing center', 'tier 3', 'tier 4'],
                priority=31,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.25,  # Less premium for data centers
                'San Francisco': 1.30,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'tier_4_certification': 200,
                'redundant_power': 150,
                'security_system': 75,
                'fiber_connectivity': 100
            },

            # Revenue metrics
            base_revenue_per_sf_annual=150,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.45,
            operating_margin_premium=0.55,
            
            # Add these expense ratios for operational efficiency calculations
            utility_cost_ratio=0.25,         # 25% - massive power for servers/cooling
            property_tax_ratio=0.05,         # 5% - valuable equipment
            insurance_cost_ratio=0.04,       # 4% - critical infrastructure insurance
            maintenance_cost_ratio=0.10,     # 10% - HVAC, UPS, generators critical
            management_fee_ratio=0.03,       # 3% - specialized management
            security_ratio=0.05,             # 5% - physical and cyber security
            reserves_ratio=0.05,             # 5% - equipment refresh cycle
            labor_cost_ratio=0.08,           # 8% - 24/7 NOC staff
            connectivity_ratio=0.05          # 5% - bandwidth, network costs
            # Total operating ratio: ~45% (highest due to power/cooling)
        ),
        
        'laboratory': BuildingConfig(
            display_name='Laboratory / Research Facility',
            base_cost_per_sf=450,
            cost_range=(400, 500),
            equipment_cost_per_sf=125,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.22,
                mechanical=0.32,  # Specialized ventilation
                electrical=0.18,
                plumbing=0.16,  # Gas, water, waste systems
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.09,
                permits=0.03,
                legal=0.02,
                financing=0.035,
                contingency=0.10,
                testing=0.02,
                construction_management=0.04,
                startup=0.025
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.045,
                    equity_ratio=0.10,
                    grants_ratio=0.20,  # Research grants
                    target_dscr=1.20,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['laboratory', 'lab', 'research facility', 'R&D',
                         'biotech', 'clean room', 'research center', 'testing facility'],
                priority=32,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.95,
                'Memphis': 0.93,
                'New York': 1.40,
                'San Francisco': 1.45,  # Biotech hub
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'clean_room': 150,
                'fume_hoods': 75,
                'biosafety_level_3': 200,
                'vibration_isolation': 100,
                'emergency_shower': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=75,
            occupancy_rate_base=0.88,
            occupancy_rate_premium=0.94,
            operating_margin_base=0.35,
            operating_margin_premium=0.42
        ),
        
        'self_storage': BuildingConfig(
            display_name='Self Storage Facility',
            base_cost_per_sf=65,
            cost_range=(55, 75),
            equipment_cost_per_sf=5,
            typical_floors=3,
            
            trades=TradeBreakdown(
                structural=0.35,
                mechanical=0.12,  # Minimal HVAC
                electrical=0.13,
                plumbing=0.05,   # Minimal plumbing
                finishes=0.35
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.005,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['self storage', 'storage facility', 'mini storage',
                         'storage units', 'public storage', 'boat storage', 'RV storage'],
                priority=33,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.30,
                'San Francisco': 1.35,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'climate_control': 20,
                'vehicle_storage': 15,
                'security_system': 10,
                'automated_access': 12
            },

            # Revenue metrics
            base_revenue_per_sf_annual=18,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.60,
            operating_margin_premium=0.70
        ),
        
        'car_dealership': BuildingConfig(
            display_name='Car Dealership',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=15,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.28,
                mechanical=0.20,
                electrical=0.15,
                plumbing=0.10,
                finishes=0.27  # Showroom finishes
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.028,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.22,
                    target_roi=0.10
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['car dealership', 'auto dealership', 'vehicle showroom',
                         'car showroom', 'auto mall', 'dealership'],
                priority=34,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.10
            },
            
            special_features={
                'service_center': 45,
                'detail_bay': 25,
                'parts_warehouse': 20,
                'car_wash': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=250,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0.08,
            operating_margin_premium=0.12
        ),
        
        'broadcast_facility': BuildingConfig(
            display_name='Broadcast / Studio Facility',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=75,  # Studio equipment
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.24,
                mechanical=0.26,  # Sound isolation HVAC
                electrical=0.20,  # High power for equipment
                plumbing=0.10,
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.018,
                financing=0.03,
                contingency=0.08,
                testing=0.015,
                construction_management=0.03,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.11
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['broadcast', 'studio', 'television station', 'radio station',
                         'recording studio', 'production facility', 'soundstage'],
                priority=35,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,  # Music city
                'Manchester': 0.92,
                'Memphis': 0.94,
                'New York': 1.45,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'sound_stage': 60,
                'control_room': 45,
                'green_screen': 30,
                'acoustic_treatment': 40,
                'broadcast_tower': 100
            },

            # Revenue metrics
            base_revenue_per_sf_annual=100,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.25,
            operating_margin_premium=0.35
        )
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # CIVIC
    # ------------------------------------------------------------------------
    BuildingType.CIVIC: {
        'government_building': BuildingConfig(
            display_name='Government Building',
            base_cost_per_sf=265,
            cost_range=(240, 290),
            equipment_cost_per_sf=20,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,  # Government project
                legal=0.02,
                financing=0.02,
                contingency=0.08,
                testing=0.01,
                construction_management=0.035,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,  # Municipal bonds
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0,
                )
            },
            
            nlp=NLPConfig(
                keywords=['city hall', 'courthouse', 'federal building', 'state building',
                         'municipal building', 'government center', 'capitol', 'administration'],
                priority=36,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.12
            },
            
            special_features={
                'council_chambers': 40,
                'secure_area': 35,
                'public_plaza': 25,
                'records_vault': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0,
            operating_margin_premium=0
        ),
        
        'public_safety': BuildingConfig(
            display_name='Public Safety Facility',
            base_cost_per_sf=285,
            cost_range=(260, 310),
            equipment_cost_per_sf=35,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,  # Hardened structure
                mechanical=0.24,
                electrical=0.16,  # Emergency power
                plumbing=0.14,
                finishes=0.18
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,
                legal=0.018,
                financing=0.02,
                contingency=0.085,
                testing=0.012,
                construction_management=0.035,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            nlp=NLPConfig(
                keywords=['fire station', 'police station', 'sheriff', 'emergency services',
                         'dispatch center', '911 center', 'EOC', 'public safety'],
                priority=37,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'apparatus_bay': 45,
                'dispatch_center': 50,
                'training_tower': 40,
                'emergency_generator': 35,
                'sally_port': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0,
            operating_margin_premium=0
        ),
        
        'library': BuildingConfig(
            display_name='Public Library',
            base_cost_per_sf=275,
            cost_range=(250, 300),
            equipment_cost_per_sf=25,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.24,
                electrical=0.15,
                plumbing=0.12,
                finishes=0.23
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.015,
                legal=0.015,
                financing=0.02,
                contingency=0.075,
                testing=0.01,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.15,
                    grants_ratio=0.10,  # Library grants
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['library', 'public library', 'branch library', 'main library',
                         'media center', 'learning center'],
                priority=38,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'reading_room': 20,
                'computer_lab': 25,
                'childrens_area': 20,
                'meeting_rooms': 15,
                'archives': 30
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0,
            operating_margin_premium=0
        ),
        
        'community_center': BuildingConfig(
            display_name='Community Center',
            base_cost_per_sf=245,
            cost_range=(220, 270),
            equipment_cost_per_sf=20,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.23,
                electrical=0.13,
                plumbing=0.15,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.015,
                legal=0.015,
                financing=0.02,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    grants_ratio=0.10,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.60,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    philanthropy_ratio=0.15,
                    grants_ratio=0.10,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['community center', 'rec center', 'senior center', 'youth center',
                         'cultural center', 'civic center', 'activity center'],
                priority=39,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.18,
                'Miami': 1.08
            },
            
            special_features={
                'gymnasium': 35,
                'kitchen': 25,
                'multipurpose_room': 20,
                'fitness_center': 20,
                'outdoor_pavilion': 15
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0,
            operating_margin_premium=0
        ),
        
        'courthouse': BuildingConfig(
            display_name='Courthouse',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=30,
            typical_floors=4,
            
            trades=TradeBreakdown(
                structural=0.28,  # Security requirements
                mechanical=0.24,
                electrical=0.16,
                plumbing=0.13,
                finishes=0.19
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.015,
                legal=0.025,
                financing=0.025,
                contingency=0.09,
                testing=0.012,
                construction_management=0.04,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['courthouse', 'court house', 'justice center', 'judicial center',
                         'court building', 'federal court', 'district court'],
                priority=40,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.42,
                'San Francisco': 1.45,
                'Chicago': 1.25,
                'Miami': 1.18
            },
            
            special_features={
                'courtroom': 50,
                'jury_room': 25,
                'holding_cells': 40,
                'judges_chambers': 30,
                'security_screening': 35
            },

            # Revenue metrics
            base_revenue_per_sf_annual=0,
            occupancy_rate_base=1.0,
            occupancy_rate_premium=1.0,
            operating_margin_base=0,
            operating_margin_premium=0
        )
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # RECREATION
    # ------------------------------------------------------------------------
    BuildingType.RECREATION: {
        'fitness_center': BuildingConfig(
            display_name='Fitness Center / Gym',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=35,  # Exercise equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.26,
                mechanical=0.25,  # Heavy HVAC for workout areas
                electrical=0.14,
                plumbing=0.15,  # Showers, pools
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.05,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.07,
                testing=0.008,
                construction_management=0.025,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            nlp=NLPConfig(
                keywords=['gym', 'fitness center', 'health club', 'workout',
                         'YMCA', 'athletic club', 'crossfit', 'wellness center'],
                priority=41,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.15,
                'Miami': 1.12
            },
            
            special_features={
                'pool': 45,
                'basketball_court': 30,
                'group_fitness': 20,
                'spa_area': 35,
                'juice_bar': 15
            },

            # Revenue metrics
            base_revenue_per_sf_annual=60,
            occupancy_rate_base=0.75,
            occupancy_rate_premium=0.85,
            operating_margin_base=0.20,
            operating_margin_premium=0.30
        ),
        
        'sports_complex': BuildingConfig(
            display_name='Sports Complex',
            base_cost_per_sf=225,
            cost_range=(200, 250),
            equipment_cost_per_sf=25,
            typical_floors=2,
            
            trades=TradeBreakdown(
                structural=0.28,  # Large spans
                mechanical=0.23,
                electrical=0.14,
                plumbing=0.13,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.022,
                legal=0.015,
                financing=0.028,
                contingency=0.08,
                testing=0.01,
                construction_management=0.03,
                startup=0.015
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.25,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.68,
                    debt_rate=0.062,
                    equity_ratio=0.32,
                    target_dscr=1.25,
                    target_roi=0.10
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['sports complex', 'athletic complex', 'field house',
                         'sports center', 'recreation complex', 'sportsplex'],
                priority=42,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.93,
                'Memphis': 0.91,
                'New York': 1.38,
                'San Francisco': 1.42,
                'Chicago': 1.20,
                'Miami': 1.15
            },
            
            special_features={
                'indoor_track': 35,
                'multiple_courts': 40,
                'weight_room': 25,
                'locker_complex': 30,
                'concessions': 20
            },

            # Revenue metrics
            base_revenue_per_sf_annual=40,
            occupancy_rate_base=0.70,
            occupancy_rate_premium=0.80,
            operating_margin_base=0.15,
            operating_margin_premium=0.25
        ),
        
        'aquatic_center': BuildingConfig(
            display_name='Aquatic Center',
            base_cost_per_sf=325,
            cost_range=(300, 350),
            equipment_cost_per_sf=45,  # Pool equipment
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.30,  # Heavy HVAC and dehumidification
                electrical=0.15,
                plumbing=0.18,  # Pool systems
                finishes=0.12
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.07,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.09,
                testing=0.015,  # Water quality systems
                construction_management=0.035,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.25,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    grants_ratio=0.15,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['aquatic center', 'natatorium', 'swimming pool', 'pool',
                         'water park', 'swim center', 'aquatics'],
                priority=43,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.40,
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.10  # Outdoor pools more common
            },
            
            special_features={
                'competition_pool': 60,
                'diving_well': 50,
                'lazy_river': 40,
                'water_slides': 45,
                'therapy_pool': 35
            },

            # Revenue metrics
            base_revenue_per_sf_annual=45,
            occupancy_rate_base=0.65,
            occupancy_rate_premium=0.75,
            operating_margin_base=0.10,
            operating_margin_premium=0.18
        ),
        
        'recreation_center': BuildingConfig(
            display_name='Recreation Center',
            base_cost_per_sf=215,
            cost_range=(190, 240),
            equipment_cost_per_sf=20,
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.27,
                mechanical=0.24,
                electrical=0.13,
                plumbing=0.14,
                finishes=0.22
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.02,
                legal=0.015,
                financing=0.025,
                contingency=0.075,
                testing=0.008,
                construction_management=0.03,
                startup=0.012
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    grants_ratio=0.05,
                    target_dscr=1.15,
                    target_roi=0.0
                ),
                OwnershipType.NON_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.045,
                    equity_ratio=0.15,
                    philanthropy_ratio=0.10,
                    grants_ratio=0.10,
                    target_dscr=1.10,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['rec center', 'recreation center', 'community recreation',
                         'activity center', 'parks and rec', 'leisure center'],
                priority=44,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.18,
                'Miami': 1.08
            },
            
            special_features={
                'gymnasium': 30,
                'game_room': 15,
                'craft_room': 12,
                'dance_studio': 20,
                'outdoor_courts': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=35,
            occupancy_rate_base=0.70,
            occupancy_rate_premium=0.80,
            operating_margin_base=0.12,
            operating_margin_premium=0.20
        ),
        
        'stadium': BuildingConfig(
            display_name='Stadium / Arena',
            base_cost_per_sf=425,
            cost_range=(375, 475),
            equipment_cost_per_sf=55,  # Scoreboards, sound, lighting
            typical_floors=4,  # Multiple levels of seating
            
            trades=TradeBreakdown(
                structural=0.32,  # Major structural for seating
                mechanical=0.22,
                electrical=0.18,  # Field lighting, displays
                plumbing=0.13,
                finishes=0.15
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.025,
                financing=0.035,
                contingency=0.10,
                testing=0.012,
                construction_management=0.04,
                startup=0.02
            ),
            
            ownership_types={
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.038,
                    equity_ratio=0.30,
                    target_dscr=1.20,
                    target_roi=0.0
                ),
                OwnershipType.PPP: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.045,
                    equity_ratio=0.20,
                    grants_ratio=0.15,
                    target_dscr=1.25,
                    target_roi=0.06
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['stadium', 'arena', 'coliseum', 'ballpark', 'football stadium',
                         'baseball stadium', 'soccer stadium', 'sports venue'],
                priority=45,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT, ProjectClass.RENOVATION]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.93,
                'New York': 1.45,
                'San Francisco': 1.50,
                'Chicago': 1.28,
                'Miami': 1.20
            },
            
            special_features={
                'luxury_boxes': 75,
                'club_level': 50,
                'press_box': 40,
                'video_board': 100,
                'retractable_roof': 200
            },

            # Revenue metrics
            base_revenue_per_sf_annual=250,
            base_revenue_per_seat_annual=500,
            seats_per_sf=0.05,
            occupancy_rate_base=0.40,
            occupancy_rate_premium=0.50,
            operating_margin_base=0.20,
            operating_margin_premium=0.30
        )
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # PARKING
    # ------------------------------------------------------------------------
    BuildingType.PARKING: {
        'surface_parking': BuildingConfig(
            display_name='Surface Parking Lot',
            base_cost_per_sf=18,  # Very low - just paving
            cost_range=(15, 21),
            equipment_cost_per_sf=2,  # Lighting, gates
            typical_floors=1,
            
            trades=TradeBreakdown(
                structural=0.60,  # Paving, grading
                mechanical=0.02,  # Minimal
                electrical=0.18,  # Lighting
                plumbing=0.05,   # Drainage
                finishes=0.15    # Striping, signage
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.03,
                permits=0.015,
                legal=0.01,
                financing=0.02,
                contingency=0.05,
                testing=0.005,
                construction_management=0.015,
                startup=0.005
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.30,
                    target_roi=0.15
                )
            },
            
            nlp=NLPConfig(
                keywords=['parking lot', 'surface parking', 'parking', 'surface lot',
                         'park and ride', 'parking area'],
                priority=46,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.90,
                'Memphis': 0.88,
                'New York': 1.25,
                'San Francisco': 1.30,
                'Chicago': 1.10,
                'Miami': 1.05
            },
            
            special_features={
                'covered_parking': 25,
                'valet_booth': 15,
                'ev_charging': 10,
                'security_system': 8
            },

            # Revenue metrics
            base_revenue_per_sf_annual=30,
            base_revenue_per_space_monthly=100,
            spaces_per_sf=0.003,
            occupancy_rate_base=0.80,
            occupancy_rate_premium=0.90,
            operating_margin_base=0.80,
            operating_margin_premium=0.85
        ),
        
        'parking_garage': BuildingConfig(
            display_name='Parking Garage',
            base_cost_per_sf=65,
            cost_range=(55, 75),
            equipment_cost_per_sf=8,  # Gates, equipment
            typical_floors=5,
            
            trades=TradeBreakdown(
                structural=0.45,  # Heavy concrete structure
                mechanical=0.08,  # Ventilation
                electrical=0.15,  # Lighting, controls
                plumbing=0.07,   # Minimal
                finishes=0.25    # Coatings, striping
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.04,
                permits=0.02,
                legal=0.012,
                financing=0.025,
                contingency=0.06,
                testing=0.008,
                construction_management=0.02,
                startup=0.008
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.75,
                    debt_rate=0.058,
                    equity_ratio=0.25,
                    target_dscr=1.25,
                    target_roi=0.12
                ),
                OwnershipType.GOVERNMENT: FinancingTerms(
                    debt_ratio=0.80,
                    debt_rate=0.038,
                    equity_ratio=0.20,
                    target_dscr=1.15,
                    target_roi=0.0
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['parking garage', 'parking structure', 'parking deck',
                         'parkade', 'parking ramp', 'multi-level parking'],
                priority=47,
                incompatible_classes=[]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.35,
                'San Francisco': 1.40,
                'Chicago': 1.20,
                'Miami': 1.10
            },
            
            special_features={
                'automated_system': 45,
                'ev_charging': 12,
                'car_wash': 25,
                'retail_space': 30,
                'green_roof': 20
            },

            # Revenue metrics
            base_revenue_per_sf_annual=50,
            base_revenue_per_space_monthly=150,
            spaces_per_sf=0.0033,
            occupancy_rate_base=0.85,
            occupancy_rate_premium=0.92,
            operating_margin_base=0.75,
            operating_margin_premium=0.80
        ),
        
        'underground_parking': BuildingConfig(
            display_name='Underground Parking',
            base_cost_per_sf=125,  # Expensive excavation
            cost_range=(110, 140),
            equipment_cost_per_sf=12,
            typical_floors=2,  # Below grade levels
            
            trades=TradeBreakdown(
                structural=0.40,  # Major excavation and structure
                mechanical=0.15,  # Ventilation critical
                electrical=0.15,
                plumbing=0.10,   # Drainage, pumps
                finishes=0.20
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.06,
                permits=0.025,
                legal=0.015,
                financing=0.03,
                contingency=0.08,
                testing=0.012,  # Waterproofing tests
                construction_management=0.03,
                startup=0.01
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.70,
                    debt_rate=0.062,
                    equity_ratio=0.30,
                    target_dscr=1.22,
                    target_roi=0.10
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['underground parking', 'subterranean parking', 'basement parking',
                         'below grade parking', 'underground garage'],
                priority=48,
                incompatible_classes=[ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.94,
                'Memphis': 0.92,
                'New York': 1.45,  # High land value
                'San Francisco': 1.50,
                'Chicago': 1.25,
                'Miami': 1.05  # Water table issues
            },
            
            special_features={
                'waterproofing': 35,
                'sump_pumps': 20,
                'vehicle_lifts': 30,
                'security_booth': 15,
                'ventilation_upgrade': 25
            },

            # Revenue metrics
            base_revenue_per_sf_annual=60,
            base_revenue_per_space_monthly=200,
            spaces_per_sf=0.0035,
            occupancy_rate_base=0.90,
            occupancy_rate_premium=0.95,
            operating_margin_base=0.70,
            operating_margin_premium=0.75
        ),
        
        'automated_parking': BuildingConfig(
            display_name='Automated Parking System',
            base_cost_per_sf=185,
            cost_range=(165, 205),
            equipment_cost_per_sf=65,  # Automated systems
            typical_floors=6,
            
            trades=TradeBreakdown(
                structural=0.25,
                mechanical=0.30,  # Automated systems
                electrical=0.25,  # Controls and power
                plumbing=0.05,
                finishes=0.15
            ),
            
            soft_costs=SoftCosts(
                design_fees=0.08,
                permits=0.03,
                legal=0.02,
                financing=0.035,
                contingency=0.10,
                testing=0.02,  # System testing
                construction_management=0.04,
                startup=0.025  # System commissioning
            ),
            
            ownership_types={
                OwnershipType.FOR_PROFIT: FinancingTerms(
                    debt_ratio=0.65,
                    debt_rate=0.065,
                    equity_ratio=0.35,
                    target_dscr=1.25,
                    target_roi=0.12
                )
            },
            
            # Financial metrics
            
            
            nlp=NLPConfig(
                keywords=['automated parking', 'robotic parking', 'mechanical parking',
                         'puzzle parking', 'stack parking', 'tower parking'],
                priority=49,
                incompatible_classes=[ProjectClass.RENOVATION, ProjectClass.TENANT_IMPROVEMENT]
            ),
            
            regional_multipliers={
                'Nashville': 1.03,
                'Franklin': 1.03,
                'Manchester': 0.92,
                'Memphis': 0.90,
                'New York': 1.40,  # Space premium
                'San Francisco': 1.45,
                'Chicago': 1.22,
                'Miami': 1.15
            },
            
            special_features={
                'retrieval_speed': 40,
                'redundant_systems': 35,
                'valet_interface': 20,
                'ev_charging_integration': 15
            },

            # Revenue metrics
            base_revenue_per_sf_annual=80,
            base_revenue_per_space_monthly=250,
            spaces_per_sf=0.005,
            occupancy_rate_base=0.95,
            occupancy_rate_premium=0.98,
            operating_margin_base=0.65,
            operating_margin_premium=0.72
        )
    }
}

# ============================================================================
# REGIONAL OVERRIDES
# ============================================================================

REGIONAL_OVERRIDES: Dict[str, float] = {
    'Nashville': 1.03,
    'Nashville, TN': 1.03
}

MARKET_OVERRIDES: Dict[str, float] = {
    key: value for key, value in REGIONAL_OVERRIDES.items()
}

FINISH_LEVELS: Dict[str, float] = {
    'standard': 1.00,
    'premium': 1.15,
    'luxury': 1.25
}

_FINISH_LEVEL_SYNONYMS = {
    'standard': [
        'standard',
        'base finish',
        'basic finishes'
    ],
    'premium': [
        'premium',
        'high-end',
        'upscale',
        'upgrade',
        'upgraded finishes',
        'premium finishes',
        'fit-out premium'
    ],
    'luxury': [
        'luxury',
        'deluxe',
        'top-end'
    ]
}

_FINISH_FACTOR_PATTERN = re.compile(
    r'(?:(?:^|[^0-9])(1\.[0-9]{1,2}|[0-9]\.[0-9]{1,2})x\b)|(?:x(1\.[0-9]{1,2}))',
    re.IGNORECASE
)

# ============================================================================
# MULTIPLIERS
# ============================================================================

PROJECT_CLASS_MULTIPLIERS = {
    ProjectClass.GROUND_UP: 1.00,
    ProjectClass.ADDITION: 1.15,
    ProjectClass.RENOVATION: 1.35,
    ProjectClass.TENANT_IMPROVEMENT: 0.65
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_building_config(building_type: BuildingType, subtype: str) -> Optional[BuildingConfig]:
    """Get configuration for a specific building type and subtype"""
    if building_type in MASTER_CONFIG:
        return MASTER_CONFIG[building_type].get(subtype)
    return None

def get_margin_pct(building_type: BuildingType, subtype: str) -> float:
    """Get the normalized operating margin for a building type/subtype."""
    margin: Optional[float] = None
    config = get_building_config(building_type, subtype)

    if config:
        candidate = getattr(config, 'operating_margin_base', None)

        if candidate is None and getattr(config, 'financial_metrics', None):
            candidate = config.financial_metrics.get('operating_margin')

        if candidate is None:
            candidate = getattr(config, 'operating_margin_premium', None)

        if candidate is not None:
            margin = float(candidate)

    if margin is None:
        margin = MARGINS.get(building_type, 0.20)

    margin = max(0.05, min(0.40, margin))
    return margin

def get_all_subtypes(building_type: BuildingType) -> List[str]:
    """Get all subtypes for a building type"""
    if building_type in MASTER_CONFIG:
        return list(MASTER_CONFIG[building_type].keys())
    return []

def validate_project_class(building_type: BuildingType, subtype: str, 
                          project_class: ProjectClass) -> ProjectClass:
    """Validate and correct project classification if incompatible"""
    config = get_building_config(building_type, subtype)
    if config and project_class in config.nlp.incompatible_classes:
        return ProjectClass.GROUND_UP  # Default to ground-up if incompatible
    return project_class

def get_trade_breakdown(building_type: BuildingType, subtype: str) -> Optional[TradeBreakdown]:
    """Get trade breakdown for a building type"""
    config = get_building_config(building_type, subtype)
    return config.trades if config else None

def get_soft_costs(building_type: BuildingType, subtype: str) -> Optional[SoftCosts]:
    """Get soft costs for a building type"""
    config = get_building_config(building_type, subtype)
    return config.soft_costs if config else None

def get_regional_multiplier(building_type: BuildingType, subtype: str, city: str,
                            warning_callback: Optional[Callable[[], None]] = None) -> float:
    """Get regional cost multiplier for a city"""
    config = get_building_config(building_type, subtype)
    if config:
        has_state = ',' in city if city else False
        if not has_state:
            if warning_callback:
                warning_callback()
            return 1.0

        # Clean the city and state parts from "City, State"
        city_part, state_part = [part.strip() for part in city.split(',', 1)]

        # Try exact city match first (maintains historical behavior when state provided)
        if city_part in config.regional_multipliers:
            return config.regional_multipliers[city_part]

        # Try case-insensitive city match
        for key, value in config.regional_multipliers.items():
            if key.lower() == city_part.lower():
                return value

        # Try matching on state code/name if provided in configuration
        for key, value in config.regional_multipliers.items():
            if key.lower() == state_part.lower():
                return value

        # Also try the raw location string
        if city in config.regional_multipliers:
            return config.regional_multipliers[city]

    return 1.0  # Default baseline

def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))

def infer_finish_level(text: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Infer finish level keyword and optional explicit multiplier factor from free text.
    Returns normalized title-case finish level and parsed float factor when available.
    """
    if not text:
        return (None, None)

    text_lower = text.lower()
    finish_key: Optional[str] = None

    for level in ('luxury', 'premium', 'standard'):
        for phrase in _FINISH_LEVEL_SYNONYMS.get(level, []):
            if phrase in text_lower:
                finish_key = level
                break
        if finish_key:
            break

    factor: Optional[float] = None
    match = _FINISH_FACTOR_PATTERN.search(text_lower)
    if match:
        factor_str = match.group(1) or match.group(2)
        if factor_str:
            try:
                factor = float(factor_str)
            except ValueError:
                factor = None

    finish_level = finish_key.title() if finish_key else None
    return (finish_level, factor)

def get_finish_cost_factor(finish_level: Optional[str]) -> float:
    """Return cost factor for a finish level using configured defaults when available."""
    defaults = {
        'standard': 1.00,
        'premium': 1.15,
        'luxury': 1.25,
    }
    level_map = {**defaults, **FINISH_LEVELS}
    if not finish_level:
        return level_map.get('standard', 1.0)
    key = finish_level.strip().lower()
    return level_map.get(key, level_map.get('standard', 1.0))

def get_finish_revenue_factor(
    finish_level: Optional[str],
    building_type: BuildingType,
    subtype: str
) -> float:
    """
    Return revenue factor by finish level. Defaults:
      standard=1.00, premium=1.05, luxury=1.10.
    If TYPE/subtype overrides exist in config (e.g., restaurants premium 1.08),
    prefer them. Clamp to [0.9, 1.3] for safety.
    """
    defaults = {
        'standard': 1.00,
        'premium': 1.05,
        'luxury': 1.10,
    }
    if building_type == BuildingType.RESTAURANT:
        defaults.update({
            'standard': 1.00,
            'premium': 1.08,
            'luxury': 1.12,
        })
    config = get_building_config(building_type, subtype)
    key = (finish_level or 'standard').strip().lower()

    candidate: Optional[float] = None
    if config:
        overrides = getattr(config, 'finish_revenue_factors', None)
        if overrides:
            candidate = overrides.get(key) or overrides.get(key.capitalize())

    if candidate is None:
        candidate = defaults.get(key, defaults['standard'])

    return _clamp(float(candidate), 0.9, 1.3)

def get_market_factor(location: str, warning_callback: Optional[Callable[[], None]] = None) -> float:
    """
    A revenue-oriented regional factor. Reuse get_regional_multiplier if no
    revenue map exists; otherwise prefer revenue-specific entries if present.
    Fall back to 1.0 on city-only, logging upstream warning via callback when provided.
    """
    if not location:
        return 1.0

    normalized = location.strip()
    if not normalized:
        return 1.0

    has_state = ',' in normalized
    if not has_state and warning_callback:
        warning_callback()

    lower_market = {key.lower(): value for key, value in MARKET_OVERRIDES.items()}
    value: Optional[float] = None

    if has_state:
        city_part, state_part = [part.strip() for part in normalized.split(',', 1)]
        value = lower_market.get(normalized.lower())
        if value is None:
            value = lower_market.get(city_part.lower())
        if value is None:
            value = lower_market.get(state_part.lower())
        if value is None:
            value = lower_market.get(state_part.upper())
    else:
        value = lower_market.get(normalized.lower())

    if value is None:
        override = get_regional_override(normalized)
        if override is None and has_state:
            city_part = normalized.split(',', 1)[0].strip()
            override = get_regional_override(city_part)
        value = override if override is not None else 1.0

    return value

def get_target_roi(building_type: BuildingType) -> float:
    """
    Universal ROI hurdle by type (can be tuned later):
      MULTIFAMILY=0.08, OFFICE=0.08, RETAIL=0.09, INDUSTRIAL=0.08,
      RESTAURANT=0.10, HOSPITALITY=0.10, HEALTHCARE=0.07, EDUCATIONAL=0.07,
      default 0.08
    """
    roi_map = {
        BuildingType.MULTIFAMILY: 0.08,
        BuildingType.OFFICE: 0.08,
        BuildingType.RETAIL: 0.09,
        BuildingType.INDUSTRIAL: 0.08,
        BuildingType.RESTAURANT: 0.10,
        BuildingType.HOSPITALITY: 0.10,
        BuildingType.HEALTHCARE: 0.07,
        BuildingType.EDUCATIONAL: 0.07,
    }
    return roi_map.get(building_type, 0.08)

def get_building_profile(building_type: BuildingType) -> Dict[str, float]:
    """
    Return a normalized profile with market cap rate, target yield-on-cost,
    and preferred DSCR for a building type. Defaults to an office-like profile.
    """
    default_profile = BUILDING_PROFILES.get(BuildingType.OFFICE, {
        'market_cap_rate': 0.07,
        'target_yield': 0.095,
        'target_dscr': 1.30,
    })
    profile = BUILDING_PROFILES.get(building_type, default_profile)
    return dict(profile)

def get_effective_modifiers(
    building_type: BuildingType,
    subtype: str,
    finish_level: Optional[str],
    location: str,
    warning_callback: Optional[Callable[[], None]] = None
) -> Dict[str, float]:
    """
    Compute the one true set of modifiers used engine-wide:
       cost_factor    = get_finish_cost_factor(finish_level) * get_regional_multiplier(..., warning_callback)
       revenue_factor = get_finish_revenue_factor(finish_level, building_type, subtype) * get_market_factor(location)
       margin_pct     = get_margin_pct(building_type, subtype)
    Return {"cost_factor": f1, "revenue_factor": f2, "margin_pct": m}
    Clamp cost/revenue factors to [0.7, 1.6] to avoid explosions.
    """
    finish_cost_factor = get_finish_cost_factor(finish_level)
    regional_factor = get_regional_multiplier(
        building_type,
        subtype,
        location,
        warning_callback=warning_callback
    )
    override = get_regional_override(location)
    if override is not None:
        regional_factor = override
    raw_cost_factor = finish_cost_factor * regional_factor
    cost_factor = _clamp(raw_cost_factor, 0.7, 1.6)

    finish_revenue_factor = get_finish_revenue_factor(finish_level, building_type, subtype)
    market_factor = get_market_factor(location, warning_callback=warning_callback)
    raw_revenue_factor = finish_revenue_factor * market_factor
    revenue_factor = _clamp(raw_revenue_factor, 0.7, 1.6)

    return {
        'cost_factor': cost_factor,
        'revenue_factor': revenue_factor,
        'margin_pct': get_margin_pct(building_type, subtype),
        'finish_cost_factor': finish_cost_factor,
        'regional_cost_factor': regional_factor,
        'finish_revenue_factor': finish_revenue_factor,
        'market_factor': market_factor
    }

def get_base_cost(building_type: BuildingType, subtype: str) -> float:
    """Get base construction cost per square foot"""
    config = get_building_config(building_type, subtype)
    return config.base_cost_per_sf if config else 250.0  # Default to office cost

def get_equipment_cost(building_type: BuildingType, subtype: str) -> float:
    """Get equipment cost per square foot"""
    config = get_building_config(building_type, subtype)
    return config.equipment_cost_per_sf if config else 0.0

def get_special_feature_cost(building_type: BuildingType, subtype: str, feature: str) -> float:
    """Get additional cost for special features"""
    config = get_building_config(building_type, subtype)
    if config and config.special_features:
        return config.special_features.get(feature, 0.0)
    return 0.0

def get_financing_terms(building_type: BuildingType, subtype: str, 
                       ownership: OwnershipType) -> Optional[FinancingTerms]:
    """Get financing terms for a specific ownership type"""
    config = get_building_config(building_type, subtype)
    if config:
        return config.ownership_types.get(ownership)
    return None

def get_revenue_multiplier(building_type: BuildingType, subtype: str, location: str,
                           warning_callback: Optional[Callable[[], None]] = None) -> float:
    """
    Get revenue analysis regional multiplier.
    Requires a city and state; falls back to 1.0 with a warning when state is missing.
    """
    if not location:
        if warning_callback:
            warning_callback()
        return 1.0

    normalized = location.strip()
    if ',' not in normalized:
        if warning_callback:
            warning_callback()
        return 1.0

    city_part, state_part = [part.strip() for part in normalized.split(',', 1)]
    config = get_building_config(building_type, subtype)

    if config:
        # Prefer explicit state entries if present
        for key, value in config.regional_multipliers.items():
            if key.lower() == state_part.lower():
                return value

    # No explicit state-level revenue multiplier configured, fall back to baseline
    return 1.0

def get_regional_override(location: str) -> Optional[float]:
    """Fetch a configuration-based regional override multiplier if defined."""
    if not location:
        return None

    normalized = location.strip()
    if not normalized:
        return None

    lower_map = {key.lower(): value for key, value in REGIONAL_OVERRIDES.items()}

    direct = lower_map.get(normalized.lower())
    if direct is not None:
        return direct

    if ',' in normalized:
        city_part = normalized.split(',', 1)[0].strip()
    else:
        city_part = normalized

    return lower_map.get(city_part.lower())


def resolve_quality_factor(finish_level: Optional[str],
                           building_type: BuildingType,
                           subtype: str) -> float:
    """Resolve deterministic quality factor for a finish level."""
    factor = 1.0
    if finish_level:
        level_key = finish_level.strip().lower()
        factor = FINISH_LEVELS.get(level_key, 1.0)
    
    config = get_building_config(building_type, subtype)
    if not config:
        return factor

    overrides = getattr(config, 'quality_factor_overrides', None)
    if overrides and finish_level:
        level_key = finish_level.strip().lower()
        override_value = overrides.get(level_key)
        if override_value is not None:
            factor = override_value

    min_factor = getattr(config, 'quality_factor_min', None)
    max_factor = getattr(config, 'quality_factor_max', None)

    if min_factor is not None and factor < min_factor:
        factor = min_factor
    if max_factor is not None and factor > max_factor:
        factor = max_factor

    return factor

# ============================================================================
# NLP DETECTION HELPERS
# ============================================================================

_NUMBER_TOKEN_RE = re.compile(r"\b\d[\d,]*(?:\.\d+)?k?\b", re.IGNORECASE)
_NON_ALNUM_RE = re.compile(r"[^a-z0-9\s]")

_DETECTION_PATTERNS_CACHE: Optional[Dict[str, Dict[str, Any]]] = None


def normalize_number_tokens(text: str) -> str:
    """Normalize numeric tokens (e.g., 5,000 / 5000 / 5k) to a canonical form."""
    if not text:
        return text

    def _normalize_token(match: re.Match) -> str:
        token = match.group(0)
        multiplier = 1
        if token.lower().endswith("k"):
            multiplier = 1000
            token = token[:-1]

        cleaned = token.replace(",", "")
        try:
            value = float(cleaned)
        except ValueError:
            return match.group(0)

        normalized_value = value * multiplier
        if normalized_value.is_integer():
            return str(int(normalized_value))
        return f"{normalized_value}".rstrip("0").rstrip(".")

    return _NUMBER_TOKEN_RE.sub(_normalize_token, text)


def _normalize_detection_text(value: str) -> str:
    """Lowercase, de-underscore, and strip extraneous punctuation for detection."""
    if not value:
        return ""
    normalized = value.replace("_", " ").lower()
    normalized = _NON_ALNUM_RE.sub(" ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _register_detection_entry(
    phrase_map: Dict[str, List[Tuple[Optional[str], int]]],
    token_map: Dict[str, List[Tuple[Optional[str], int]]],
    term: str,
    subtype: Optional[str],
    priority: int,
    force_phrase: Optional[bool] = None,
) -> None:
    normalized = _normalize_detection_text(term)
    if not normalized:
        return

    is_phrase = force_phrase if force_phrase is not None else (" " in normalized)
    target_map = phrase_map if is_phrase else token_map
    entries = target_map[normalized]
    candidate = (subtype, priority)
    if candidate not in entries:
        entries.append(candidate)


def build_detection_patterns() -> Dict[str, Dict[str, Any]]:
    """
    Generate phrase-first detection patterns from master configuration.

    Returns:
        Mapping of building type value to detection metadata:
        {
            "<building_type>": {
                "phrases": [...],
                "tokens": [...],
                "priority": <int>,
                "_phrase_map": {phrase: [(subtype, priority), ...]},
                "_token_map": {token: [(subtype, priority), ...]},
            }
        }
    """
    global _DETECTION_PATTERNS_CACHE
    if _DETECTION_PATTERNS_CACHE is not None:
        return _DETECTION_PATTERNS_CACHE

    patterns: Dict[str, Dict[str, Any]] = {}

    for building_type, subtypes in MASTER_CONFIG.items():
        phrase_map: Dict[str, List[Tuple[Optional[str], int]]] = defaultdict(list)
        token_map: Dict[str, List[Tuple[Optional[str], int]]] = defaultdict(list)
        priority = 0

        for subtype_key, config in subtypes.items():
            nlp_config = getattr(config, "nlp", None)
            subtype_priority = getattr(nlp_config, "priority", 0) or 0
            priority = max(priority, subtype_priority)

            # Display name is treated as a phrase
            if getattr(config, "display_name", None):
                _register_detection_entry(
                    phrase_map,
                    token_map,
                    config.display_name,
                    subtype_key,
                    subtype_priority,
                    force_phrase=True,
                )

            # Subtype key and NLP keywords
            _register_detection_entry(
                phrase_map,
                token_map,
                subtype_key,
                subtype_key,
                subtype_priority,
            )

            if nlp_config:
                for keyword in nlp_config.keywords:
                    _register_detection_entry(
                        phrase_map,
                        token_map,
                        keyword,
                        subtype_key,
                        subtype_priority,
                    )

        # General fallback token for the building type
        _register_detection_entry(
            phrase_map,
            token_map,
            building_type.value,
            None,
            priority,
        )

        sorted_phrases = sorted(
            phrase_map.keys(),
            key=lambda phrase: (-len(phrase.split()), -len(phrase), phrase),
        )
        sorted_tokens = sorted(
            token_map.keys(),
            key=lambda token: (-len(token), token),
        )

        patterns[building_type.value] = {
            "phrases": sorted_phrases,
            "tokens": sorted_tokens,
            "priority": priority,
            "_phrase_map": phrase_map,
            "_token_map": token_map,
        }

    _DETECTION_PATTERNS_CACHE = patterns
    return patterns


def _select_best_subtype(entries: List[Tuple[Optional[str], int]]) -> Optional[str]:
    if not entries:
        return None

    # Prefer explicit subtype matches ordered by priority (desc)
    ranked = sorted(
        entries,
        key=lambda item: (
            0 if item[0] else 1,  # prioritize actual subtype over generic
            -(item[1] if item[1] is not None else 0),
            item[0] or "",
        ),
    )
    for subtype, _ in ranked:
        if subtype:
            return subtype
    return ranked[0][0]


def _fallback_subtype_for_type(building_type: BuildingType) -> Optional[str]:
    subtypes = MASTER_CONFIG.get(building_type)
    if not subtypes:
        return None

    ranked = sorted(
        subtypes.items(),
        key=lambda item: (
            -(getattr(getattr(item[1], "nlp", None), "priority", 0) or 0),
            item[0],
        ),
    )
    return ranked[0][0] if ranked else None


def _match_terms(
    haystack: str,
    terms: List[str],
    term_map: Dict[str, List[Tuple[Optional[str], int]]],
    method: str,
) -> Optional[Tuple[str, Optional[str], str]]:
    for term in terms:
        if not term:
            continue
        pattern = re.compile(rf"\b{re.escape(term)}\b")
        if pattern.search(haystack):
            subtype = _select_best_subtype(term_map.get(term, []))
            return term, subtype, method
    return None


def detect_building_type_with_method(
    description: str,
) -> Optional[Tuple[BuildingType, Optional[str], str]]:
    """
    Detect building type/subtype from description, returning detection method.
    """
    if not description:
        return None

    normalized_text = _normalize_detection_text(normalize_number_tokens(description))
    if not normalized_text:
        return None

    patterns = build_detection_patterns()
    sorted_types = sorted(
        patterns.items(),
        key=lambda item: (-item[1]["priority"], item[0]),
    )

    for building_type_value, data in sorted_types:
        phrase_hit = _match_terms(
            normalized_text,
            data["phrases"],
            data["_phrase_map"],
            method="phrase",
        )
        if phrase_hit:
            _, subtype, method = phrase_hit
            building_type_enum = BuildingType(building_type_value)
            subtype = subtype or _fallback_subtype_for_type(building_type_enum)
            return building_type_enum, subtype, method

        token_hit = _match_terms(
            normalized_text,
            data["tokens"],
            data["_token_map"],
            method="token",
        )
        if token_hit:
            _, subtype, method = token_hit
            building_type_enum = BuildingType(building_type_value)
            subtype = subtype or _fallback_subtype_for_type(building_type_enum)
            return building_type_enum, subtype, method

    return None


def detect_building_type(description: str) -> Optional[Tuple[BuildingType, Optional[str]]]:
    """Detect building type/subtype using config-driven patterns."""
    result = detect_building_type_with_method(description)
    if not result:
        return None
    building_type, subtype, _method = result
    return building_type, subtype

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate that all configurations are complete and consistent"""
    errors = []
    
    for building_type, subtypes in MASTER_CONFIG.items():
        for subtype, config in subtypes.items():
            # Check trade percentages sum to 1.0
            trade_sum = (config.trades.structural + config.trades.mechanical + 
                        config.trades.electrical + config.trades.plumbing + 
                        config.trades.finishes)
            if abs(trade_sum - 1.0) > 0.01:
                errors.append(f"{building_type.value}/{subtype}: Trade percentages sum to {trade_sum:.2f}, not 1.0")
            
            # Check at least one ownership type exists
            if not config.ownership_types:
                errors.append(f"{building_type.value}/{subtype}: No ownership types defined")
            
            # Check financing ratios sum correctly
            for ownership, terms in config.ownership_types.items():
                ratio_sum = (terms.debt_ratio + terms.equity_ratio + 
                           terms.philanthropy_ratio + terms.grants_ratio)
                if abs(ratio_sum - 1.0) > 0.01:
                    errors.append(f"{building_type.value}/{subtype}/{ownership.value}: "
                                f"Financing ratios sum to {ratio_sum:.2f}, not 1.0")
    
    return errors

# Run validation on import
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration validation passed")
