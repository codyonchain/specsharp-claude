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
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from app.config.regional_multipliers import resolve_location_context

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

    # Config-driven behavior selectors (safe defaults)
    scope_profile: Optional[str] = None
    scope_defaults: Dict[str, Any] = field(default_factory=dict)
    cost_clamp: Dict[str, Any] = field(default_factory=dict)
    finish_level_multipliers: Dict[str, Any] = field(default_factory=dict)
    facility_metrics_profile: Optional[str] = None
    exclude_from_facility_opex: List[str] = field(default_factory=list)


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


# Imported after config types to avoid circular import during module initialization.
from app.v2.config.subtypes.industrial import (
    warehouse as industrial_warehouse,
    distribution_center as industrial_distribution_center,
    manufacturing as industrial_manufacturing,
    flex_space as industrial_flex_space,
    cold_storage as industrial_cold_storage,
)
from app.v2.config.subtypes.healthcare import (
    dental_office as healthcare_dental_office,
    hospital as healthcare_hospital,
    imaging_center as healthcare_imaging_center,
    medical_center as healthcare_medical_center,
    medical_office_building as healthcare_medical_office_building,
    nursing_home as healthcare_nursing_home,
    outpatient_clinic as healthcare_outpatient_clinic,
    rehabilitation as healthcare_rehabilitation,
    surgical_center as healthcare_surgical_center,
    urgent_care as healthcare_urgent_care,
)
from app.v2.config.subtypes.restaurant import (
    bar_tavern as restaurant_bar_tavern,
    cafe as restaurant_cafe,
    fine_dining as restaurant_fine_dining,
    full_service as restaurant_full_service,
    quick_service as restaurant_quick_service,
)
from app.v2.config.subtypes.specialty import (
    broadcast_facility as specialty_broadcast_facility,
    car_dealership as specialty_car_dealership,
    data_center as specialty_data_center,
    laboratory as specialty_laboratory,
    self_storage as specialty_self_storage,
)
from app.v2.config.subtypes.hospitality import (
    full_service_hotel as hospitality_full_service_hotel,
    limited_service_hotel as hospitality_limited_service_hotel,
)
from app.v2.config.subtypes.multifamily import (
    affordable_housing as multifamily_affordable_housing,
    luxury_apartments as multifamily_luxury_apartments,
    market_rate_apartments as multifamily_market_rate_apartments,
)
from app.v2.config.subtypes.office import (
    class_a as office_class_a,
    class_b as office_class_b,
)
from app.v2.config.subtypes.retail import (
    big_box as retail_big_box,
    shopping_center as retail_shopping_center,
)
from app.v2.config.subtypes.parking import (
    surface_parking as parking_surface_parking,
    parking_garage as parking_parking_garage,
    underground_parking as parking_underground_parking,
    automated_parking as parking_automated_parking,
)
from app.v2.config.subtypes.educational import (
    community_college as educational_community_college,
    elementary_school as educational_elementary_school,
    high_school as educational_high_school,
    middle_school as educational_middle_school,
    university as educational_university,
)
from app.v2.config.subtypes.mixed_use import (
    hotel_retail as mixed_use_hotel_retail,
    office_residential as mixed_use_office_residential,
    retail_residential as mixed_use_retail_residential,
    transit_oriented as mixed_use_transit_oriented,
    urban_mixed as mixed_use_urban_mixed,
)
from app.v2.config.subtypes.civic import (
    community_center as civic_community_center,
    courthouse as civic_courthouse,
    government_building as civic_government_building,
    library as civic_library,
    public_safety as civic_public_safety,
)
from app.v2.config.subtypes.recreation import (
    aquatic_center as recreation_aquatic_center,
    fitness_center as recreation_fitness_center,
    recreation_center as recreation_recreation_center,
    sports_complex as recreation_sports_complex,
    stadium as recreation_stadium,
)
from app.v2.config.type_profiles import (
    multifamily as profile_multifamily,
    office as profile_office,
    retail as profile_retail,
    industrial as profile_industrial,
    hospitality as profile_hospitality,
    restaurant as profile_restaurant,
    healthcare as profile_healthcare,
    educational as profile_educational,
    mixed_use as profile_mixed_use,
    specialty as profile_specialty,
    civic as profile_civic,
    recreation as profile_recreation,
    parking as profile_parking,
)

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
    building_type: profile
    for building_type, profile in (
        profile_multifamily.CONFIG,
        profile_office.CONFIG,
        profile_retail.CONFIG,
        profile_industrial.CONFIG,
        profile_hospitality.CONFIG,
        profile_restaurant.CONFIG,
        profile_healthcare.CONFIG,
        profile_educational.CONFIG,
        profile_mixed_use.CONFIG,
        profile_specialty.CONFIG,
        profile_civic.CONFIG,
        profile_recreation.CONFIG,
        profile_parking.CONFIG,
    )
}

MASTER_CONFIG: Dict[BuildingType, Dict[str, BuildingConfig]] = {
    # ------------------------------------------------------------------------
    # HEALTHCARE
    # ------------------------------------------------------------------------
    BuildingType.HEALTHCARE: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            healthcare_dental_office.CONFIG,
            healthcare_hospital.CONFIG,
            healthcare_imaging_center.CONFIG,
            healthcare_medical_center.CONFIG,
            healthcare_medical_office_building.CONFIG,
            healthcare_nursing_home.CONFIG,
            healthcare_outpatient_clinic.CONFIG,
            healthcare_rehabilitation.CONFIG,
            healthcare_surgical_center.CONFIG,
            healthcare_urgent_care.CONFIG,
        )
        if _building_type == BuildingType.HEALTHCARE
    },
    
    # ------------------------------------------------------------------------
    # MULTIFAMILY
    # ------------------------------------------------------------------------
    BuildingType.MULTIFAMILY: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            multifamily_affordable_housing.CONFIG,
            multifamily_luxury_apartments.CONFIG,
            multifamily_market_rate_apartments.CONFIG,
        )
        if _building_type == BuildingType.MULTIFAMILY
    },
    
    # ------------------------------------------------------------------------
    # OFFICE
    # ------------------------------------------------------------------------
    BuildingType.OFFICE: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            office_class_a.CONFIG,
            office_class_b.CONFIG,
        )
        if _building_type == BuildingType.OFFICE
    },
    
    # ------------------------------------------------------------------------
    # RETAIL
    # ------------------------------------------------------------------------
    BuildingType.RETAIL: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            retail_shopping_center.CONFIG,
            retail_big_box.CONFIG,
        )
        if _building_type == BuildingType.RETAIL
    },
    
    # ------------------------------------------------------------------------
    # RESTAURANT
    # ------------------------------------------------------------------------
    BuildingType.RESTAURANT: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            restaurant_quick_service.CONFIG,
            restaurant_full_service.CONFIG,
            restaurant_fine_dining.CONFIG,
            restaurant_bar_tavern.CONFIG,
            restaurant_cafe.CONFIG,
        )
        if _building_type == BuildingType.RESTAURANT
    },
    
    # ------------------------------------------------------------------------
    # INDUSTRIAL
    # ------------------------------------------------------------------------
    BuildingType.INDUSTRIAL: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            industrial_warehouse.CONFIG,
            industrial_distribution_center.CONFIG,
            industrial_manufacturing.CONFIG,
            industrial_flex_space.CONFIG,
            industrial_cold_storage.CONFIG,
        )
        if _building_type == BuildingType.INDUSTRIAL
    },
    
    # ------------------------------------------------------------------------
    # HOSPITALITY
    # ------------------------------------------------------------------------
    BuildingType.HOSPITALITY: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            hospitality_full_service_hotel.CONFIG,
            hospitality_limited_service_hotel.CONFIG,
        )
        if _building_type == BuildingType.HOSPITALITY
    },
    
    # ------------------------------------------------------------------------
    # EDUCATIONAL
    # ------------------------------------------------------------------------
    BuildingType.EDUCATIONAL: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            educational_elementary_school.CONFIG,
            educational_middle_school.CONFIG,
            educational_high_school.CONFIG,
            educational_university.CONFIG,
            educational_community_college.CONFIG,
        )
        if _building_type == BuildingType.EDUCATIONAL
    },
    
    # ------------------------------------------------------------------------
    # MIXED_USE
    # ------------------------------------------------------------------------
    BuildingType.MIXED_USE: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            mixed_use_retail_residential.CONFIG,
            mixed_use_office_residential.CONFIG,
            mixed_use_hotel_retail.CONFIG,
            mixed_use_urban_mixed.CONFIG,
            mixed_use_transit_oriented.CONFIG,
        )
        if _building_type == BuildingType.MIXED_USE
    },
            
    
    # ------------------------------------------------------------------------
    # SPECIALTY
    # ------------------------------------------------------------------------
    BuildingType.SPECIALTY: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            specialty_broadcast_facility.CONFIG,
            specialty_car_dealership.CONFIG,
            specialty_data_center.CONFIG,
            specialty_laboratory.CONFIG,
            specialty_self_storage.CONFIG,
        )
        if _building_type == BuildingType.SPECIALTY
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # CIVIC
    # ------------------------------------------------------------------------
    BuildingType.CIVIC: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            civic_community_center.CONFIG,
            civic_courthouse.CONFIG,
            civic_government_building.CONFIG,
            civic_library.CONFIG,
            civic_public_safety.CONFIG,
        )
        if _building_type == BuildingType.CIVIC
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # RECREATION
    # ------------------------------------------------------------------------
    BuildingType.RECREATION: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            recreation_aquatic_center.CONFIG,
            recreation_recreation_center.CONFIG,
            recreation_fitness_center.CONFIG,
            recreation_sports_complex.CONFIG,
            recreation_stadium.CONFIG,
        )
        if _building_type == BuildingType.RECREATION
    },
            
            # Financial metrics
            
    
    # ------------------------------------------------------------------------
    # PARKING
    # ------------------------------------------------------------------------
    BuildingType.PARKING: {
        subtype_key: config
        for _building_type, subtype_key, config in (
            parking_surface_parking.CONFIG,
            parking_parking_garage.CONFIG,
            parking_underground_parking.CONFIG,
            parking_automated_parking.CONFIG,
        )
        if _building_type == BuildingType.PARKING
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
    ProjectClass.ADDITION:  1.12,
    ProjectClass.RENOVATION:  0.92,
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
    """Get regional cost multiplier for a city."""
    context = resolve_location_context(city or "")
    state = context.get("state")
    if not state and warning_callback:
        warning_callback()
    return float(context.get("multiplier", 1.0))

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
    Revenue-oriented regional factor that mirrors the global resolver
    while still allowing explicit overrides.
    """
    if not location:
        return 1.0

    normalized = location.strip()
    context = resolve_location_context(normalized)
    state = context.get("state")
    if not state and warning_callback:
        warning_callback()

    base_market = float(context.get("market_factor", 1.0) or 1.0)
    value: float = base_market

    lower_market = {key.lower(): val for key, val in MARKET_OVERRIDES.items()}
    override_lookup: Optional[float] = None

    if normalized:
        override_lookup = lower_market.get(normalized.lower())
    if override_lookup is None and context.get("city") and state:
        city_state_key = f"{context['city']}, {state}".lower()
        override_lookup = lower_market.get(city_state_key)
    if override_lookup is None and state:
        override_lookup = lower_market.get(state.lower()) or lower_market.get(state.upper())

    if override_lookup is not None:
        value = override_lookup

    override = get_regional_override(normalized)
    if override is None and context.get("city"):
        override = get_regional_override(context["city"])
    if override is not None:
        value = override

    return float(value)

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
    raw_revenue_factor = finish_revenue_factor
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
