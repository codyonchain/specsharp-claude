"""
The single engine that handles ALL calculations.
This replaces: engine.py, clean_engine_v2.py, cost_engine.py, 
clean_scope_engine.py, owner_view_engine.py, engine_selector.py
"""

from datetime import datetime, date
from app.config.regional_multipliers import resolve_location_context
from app.v2.config.master_config import (
    MASTER_CONFIG,
    BuildingType,
    ProjectClass,
    OwnershipType,
    PROJECT_CLASS_MULTIPLIERS,
    PROJECT_TIMELINES,
    get_building_config,
    get_effective_modifiers,
    get_margin_pct,
    get_target_roi,
    detect_building_type_with_method,
    resolve_quality_factor,
    validate_project_class,
    infer_finish_level,
    get_building_profile,
)
from app.v2.config.construction_schedule import (
    build_construction_schedule as _build_construction_schedule,
)
from app.v2.config.type_profiles import scope_items
from app.services.nlp_service import NLPService
# from app.v2.services.financial_analyzer import FinancialAnalyzer  # TODO: Implement this
from typing import Optional, Dict, Any, List, Tuple
from copy import deepcopy
from dataclasses import asdict, replace
import math
import logging
import re

logger = logging.getLogger(__name__)

MIXED_USE_SPLIT_COMPONENTS: Tuple[str, ...] = ("office", "residential", "retail", "hotel", "transit")
MIXED_USE_DEFAULT_SPLIT_BY_SUBTYPE: Dict[str, Tuple[str, str]] = {
    "office_residential": ("office", "residential"),
    "retail_residential": ("retail", "residential"),
    "hotel_retail": ("hotel", "retail"),
    "transit_oriented": ("transit", "residential"),
    "urban_mixed": ("office", "residential"),
}
MIXED_USE_COST_COMPONENT_MULTIPLIERS: Dict[str, float] = {
    "office": 1.08,
    "residential": 1.00,
    "retail": 1.04,
    "hotel": 1.12,
    "transit": 1.10,
}
MIXED_USE_REVENUE_COMPONENT_MULTIPLIERS: Dict[str, float] = {
    "office": 1.00,
    "residential": 0.97,
    "retail": 1.08,
    "hotel": 1.12,
    "transit": 0.93,
}


def _humanize_special_feature_label(feature_id: str) -> str:
    """Convert config feature keys into user-facing labels."""
    if not isinstance(feature_id, str):
        return "Special Feature"
    tokens = feature_id.replace("-", "_").split("_")
    words = [token for token in tokens if token]
    if not words:
        return "Special Feature"
    return " ".join(word[:1].upper() + word[1:] for word in words)


# Legacy frontend healthcare special-feature IDs mapped to canonical backend subtype keys.
HEALTHCARE_SPECIAL_FEATURE_ALIASES: Dict[str, Dict[str, str]] = {
    "surgical_center": {
        "surgery": "operating_room",
        "surgical_suite": "operating_room",
        "or_suite": "operating_room",
        "or": "operating_room",
    },
    "imaging_center": {
        "imaging": "mri_suite",
        "imaging_suite": "mri_suite",
    },
    "urgent_care": {
        "lab": "laboratory",
    },
    "outpatient_clinic": {
        "lab": "laboratory",
    },
    "medical_office_building": {
        "medical_center_ambulatory_tower_fitout": "ambulatory_buildout",
        "medical_center_infusion_suite": "ambulatory_buildout",
    },
    "dental_office": {
        "laboratory": "lab",
    },
    "hospital": {
        "emergency": "emergency_department",
        "imaging": "imaging_suite",
        "surgery": "surgical_suite",
        "operating_room": "surgical_suite",
        "or_suite": "surgical_suite",
        "lab": "laboratory",
        "hospital_pharmacy_cleanroom": "pharmacy",
        "hospital_central_plant_redundancy": "cathlab",
    },
    "medical_center": {
        "emergency_department": "emergency",
        "imaging_suite": "imaging",
        "surgical_suite": "surgery",
        "lab": "laboratory",
        "medical_center_infusion_suite": "specialty_clinic",
        "medical_center_ambulatory_tower_fitout": "specialty_clinic",
    },
    "nursing_home": {
        "nursing_memory_care_wing": "memory_care",
        "nursing_rehab_gym": "therapy_room",
        "nursing_nurse_call_upgrade": "therapy_room",
        "nursing_wander_management_system": "memory_care",
        "nursing_dining_household_model": "dining_hall",
    },
    "rehabilitation": {
        "rehab_hydrotherapy_pool": "hydrotherapy",
        "rehab_gait_training_lab": "assessment_suite",
        "rehab_adl_apartment": "treatment_rooms",
        "rehab_therapy_gym_expansion": "therapy_gym",
        "rehab_speech_neuro_suite": "treatment_rooms",
    },
}

HEALTHCARE_INPATIENT_SUBTYPES = {
    "hospital",
    "medical_center",
    "nursing_home",
    "rehabilitation",
}

HEALTHCARE_OPERATIONAL_METRIC_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "surgical_center": {
        "throughput_per_unit_day": 2.4,
        "operating_days_per_year": 250,
        "utilization_target": 0.74,
        "provider_fte_per_unit": 0.85,
        "support_fte_per_provider": 2.1,
        "specialist_fte_per_unit": 1.6,
        "specialist_label": "Perioperative Staff FTE",
        "throughput_label": "Cases / Day",
        "utilization_label": "OR Utilization",
        "efficiency_label": "Turnover Efficiency",
        "efficiency_green_threshold": 85.0,
        "efficiency_yellow_threshold": 70.0,
    },
    "imaging_center": {
        "throughput_per_unit_day": 11.0,
        "operating_days_per_year": 310,
        "utilization_target": 0.76,
        "provider_fte_per_unit": 0.22,
        "support_fte_per_provider": 1.7,
        "specialist_fte_per_unit": 0.95,
        "specialist_label": "Imaging Tech FTE",
        "throughput_label": "Scans / Day",
        "utilization_label": "Scanner Utilization",
        "efficiency_label": "Scan Throughput Efficiency",
        "efficiency_green_threshold": 84.0,
        "efficiency_yellow_threshold": 68.0,
    },
    "urgent_care": {
        "throughput_per_unit_day": 13.0,
        "operating_days_per_year": 365,
        "utilization_target": 0.72,
        "provider_fte_per_unit": 0.33,
        "support_fte_per_provider": 1.2,
        "specialist_fte_per_unit": 0.08,
        "specialist_label": "On-Site Lab/Imaging FTE",
        "throughput_label": "Visits / Day",
        "utilization_label": "Exam Room Utilization",
        "efficiency_label": "Door-to-Provider Efficiency",
        "efficiency_green_threshold": 83.0,
        "efficiency_yellow_threshold": 67.0,
    },
    "outpatient_clinic": {
        "throughput_per_unit_day": 9.0,
        "operating_days_per_year": 260,
        "utilization_target": 0.78,
        "provider_fte_per_unit": 0.3,
        "support_fte_per_provider": 1.4,
        "specialist_fte_per_unit": 0.05,
        "specialist_label": "Care Coordination FTE",
        "throughput_label": "Visits / Day",
        "utilization_label": "Exam Room Utilization",
        "efficiency_label": "Visit Throughput Efficiency",
        "efficiency_green_threshold": 84.0,
        "efficiency_yellow_threshold": 69.0,
    },
    "medical_office_building": {
        "throughput_per_unit_day": 18.0,
        "operating_days_per_year": 260,
        "utilization_target": 0.83,
        "provider_fte_per_unit": 1.1,
        "support_fte_per_provider": 1.5,
        "specialist_fte_per_unit": 0.25,
        "specialist_label": "Specialty Suite FTE",
        "throughput_label": "Tenant Encounters / Day",
        "utilization_label": "Suite Utilization",
        "efficiency_label": "Tenant Throughput Yield",
        "efficiency_green_threshold": 86.0,
        "efficiency_yellow_threshold": 72.0,
    },
    "dental_office": {
        "throughput_per_unit_day": 8.0,
        "operating_days_per_year": 240,
        "utilization_target": 0.82,
        "provider_fte_per_unit": 0.55,
        "support_fte_per_provider": 1.3,
        "specialist_fte_per_unit": 0.1,
        "specialist_label": "Hygiene/Assist FTE",
        "throughput_label": "Chair Visits / Day",
        "utilization_label": "Operatory Utilization",
        "efficiency_label": "Chair Turnover Efficiency",
        "efficiency_green_threshold": 85.0,
        "efficiency_yellow_threshold": 70.0,
    },
    "hospital": {
        "throughput_per_unit_day": 0.95,
        "operating_days_per_year": 365,
        "utilization_target": 0.82,
        "average_length_of_stay_days": 4.6,
        "clinical_staff_fte_per_unit": 1.58,
        "support_staff_fte_per_unit": 0.92,
        "throughput_label": "Average Daily Census",
        "utilization_label": "Licensed Bed Occupancy",
        "staffing_intensity_label": "FTE per Licensed Bed",
        "efficiency_label": "LOS Throughput Efficiency",
        "efficiency_green_threshold": 84.0,
        "efficiency_yellow_threshold": 70.0,
    },
    "medical_center": {
        "throughput_per_unit_day": 0.92,
        "operating_days_per_year": 365,
        "utilization_target": 0.80,
        "average_length_of_stay_days": 4.4,
        "clinical_staff_fte_per_unit": 1.38,
        "support_staff_fte_per_unit": 0.82,
        "throughput_label": "Average Daily Census",
        "utilization_label": "Service-Line Bed Occupancy",
        "staffing_intensity_label": "FTE per Licensed Bed",
        "efficiency_label": "Clinical Throughput Efficiency",
        "efficiency_green_threshold": 83.0,
        "efficiency_yellow_threshold": 69.0,
    },
    "nursing_home": {
        "throughput_per_unit_day": 0.97,
        "operating_days_per_year": 365,
        "utilization_target": 0.90,
        "average_length_of_stay_days": 27.0,
        "clinical_staff_fte_per_unit": 0.62,
        "support_staff_fte_per_unit": 0.48,
        "throughput_label": "Average Daily Census",
        "utilization_label": "Resident Bed Occupancy",
        "staffing_intensity_label": "FTE per Licensed Bed",
        "efficiency_label": "Resident Throughput Efficiency",
        "efficiency_green_threshold": 82.0,
        "efficiency_yellow_threshold": 68.0,
    },
    "rehabilitation": {
        "throughput_per_unit_day": 0.9,
        "operating_days_per_year": 365,
        "utilization_target": 0.84,
        "average_length_of_stay_days": 17.0,
        "clinical_staff_fte_per_unit": 1.05,
        "support_staff_fte_per_unit": 0.55,
        "throughput_label": "Average Daily Census",
        "utilization_label": "Program Bed Occupancy",
        "staffing_intensity_label": "FTE per Licensed Bed",
        "efficiency_label": "Therapy Throughput Efficiency",
        "efficiency_green_threshold": 82.0,
        "efficiency_yellow_threshold": 67.0,
    },
}

HEALTHCARE_HIGH_ACUITY_SCOPE_SUBTYPES = {
    "surgical_center",
    "imaging_center",
    "hospital",
    "medical_center",
}

HEALTHCARE_SCOPE_MIN_SYSTEMS_BY_TRADE = {
    "structural": 5,
    "mechanical": 5,
    "electrical": 5,
    "plumbing": 5,
    "finishes": 5,
}

HEALTHCARE_SCOPE_MIN_SYSTEMS_HIGH_ACUITY_OVERRIDES = {
    "mechanical": 6,
    "electrical": 6,
    "plumbing": 6,
}

HEALTHCARE_SCOPE_DEPTH_LABELS_BY_CARE_GROUP: Dict[str, Dict[str, List[str]]] = {
    "acuity": {
        "structural": [
            "Interdisciplinary Shaft + Opening Reinforcing",
            "Equipment Anchorage + Vibration Support",
            "Heavy Utility Corridor Framing",
        ],
        "mechanical": [
            "Isolation Pressurization Control Loops",
            "Airside Redundancy + N+1 Controls",
            "Terminal Unit Balancing + TAB Allowance",
        ],
        "electrical": [
            "Critical Branch Segregation + Transfer Logic",
            "Selective Coordination + Arc Study Scope",
            "Low-Voltage Clinical Backbone + Head-End",
        ],
        "plumbing": [
            "Medical Gas Zoning + Alarm Panels",
            "Critical Drainage + Neutralization Loops",
            "Domestic Recirculation + Thermal Holdback",
        ],
        "finishes": [
            "Infection-Control Transition Detailing",
            "Clinical Wall Protection + Corner Guard Package",
            "Door/Hardware Pressure-Rating Coordination",
        ],
    },
    "ambulatory": {
        "structural": [
            "Exam Pod Framing + Door Header Coordination",
            "Procedure-Room Blocking + Support Steel",
            "MEP Penetration Framing + Firestopping Prep",
        ],
        "mechanical": [
            "Room-Level Ventilation Zoning + Controls",
            "Outside Air Balancing + Commissioning Scope",
            "Comfort Reheat + Diffuser Optimization",
        ],
        "electrical": [
            "Procedure Power Branching + Isolated Grounds",
            "Lighting Controls + Patient/Staff Mode Scenes",
            "Low-Voltage Data + Security Interface",
        ],
        "plumbing": [
            "Hot-Water Loop Balancing + Mixing Valves",
            "Point-of-Use Fixtures + Backflow Protection",
            "Special Waste + Trench Coordination",
        ],
        "finishes": [
            "High-Cleanability Surface Package",
            "Wayfinding + Front-of-House Finish Layer",
            "Acoustic Treatment + Privacy Assemblies",
        ],
    },
    "post_acute": {
        "structural": [
            "Resident-Wing Reinforcing + Lift Path Support",
            "Therapy Equipment Anchorage + Slab Prep",
            "Roof Penetration Framing + Safety Access",
        ],
        "mechanical": [
            "Resident Comfort Zoning + Night Setback",
            "Humidity + Fresh-Air Control Sequencing",
            "Therapy Space Ventilation + Controls",
        ],
        "electrical": [
            "Nurse Call Backbone + Device Distribution",
            "Life-Safety Branch Segregation + Panels",
            "Resident Room Lighting + Controls",
        ],
        "plumbing": [
            "Hydrotherapy + Specialty Fixture Rough-In",
            "Domestic Hot Water Recirc + Balancing",
            "Sanitary Branch Coordination + Access Points",
        ],
        "finishes": [
            "Resident Durability Package + Wall Protection",
            "Slip-Resistance Flooring + Transition Details",
            "Acoustic + Comfort Finish Coordination",
        ],
    },
}

# SELECTOR_REGISTRY (Phase 4)
# - id: construction_schedule_by_building_type
#   location: build_construction_schedule (top)
#   selector_type: routing
#   keys: building_type -> CONSTRUCTION_SCHEDULES; fallback via CONSTRUCTION_SCHEDULE_FALLBACKS; default OFFICE
#   current_behavior: Selects a construction schedule by building type with fallback to OFFICE when missing.
#   move_to_config: other
#   parity_fixture_hint: schedule_office_fallback
# - id: project_timeline_by_building_type
#   location: build_project_timeline (top)
#   selector_type: routing
#   keys: building_type -> PROJECT_TIMELINES; defaults to hardcoded milestones when missing
#   current_behavior: Routes timeline milestones per building type or uses default milestones.
#   move_to_config: other
#   parity_fixture_hint: timeline_default_milestones
# - id: project_class_normalization
#   location: UnifiedEngine._normalize_project_class
#   selector_type: routing
#   keys: project_class string variants -> ProjectClass enum values
#   current_behavior: Normalizes raw project class inputs to canonical ProjectClass values.
#   move_to_config: other
#   parity_fixture_hint: project_class_string_aliases
# - id: project_class_multiplier_map
#   location: UnifiedEngine.calculate_project (project class multiplier)
#   selector_type: routing
#   keys: project_class -> PROJECT_CLASS_MULTIPLIERS
#   current_behavior: Applies a project-class complexity multiplier to base cost.
#   move_to_config: other
#   parity_fixture_hint: project_class_multiplier_ground_up
# - id: office_height_premium
#   location: UnifiedEngine.calculate_project (height premium)
#   selector_type: conditional_branch
#   keys: building_type=OFFICE; floor_count thresholds (>4, >8)
#   current_behavior: Adds capped height premium multipliers for taller office buildings.
#   move_to_config: other
#   parity_fixture_hint: office_height_premium_10_floors
# - id: healthcare_medical_office_margin_override
#   location: UnifiedEngine.calculate_project (modifiers override)
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE; subtype=medical_office_building
#   current_behavior: Forces margin_pct override from config when medical office has operating margin configured.
#   move_to_config: other
#   parity_fixture_hint: healthcare_medical_office_margin
# - id: industrial_flex_scope_finishes_delta
#   location: UnifiedEngine.calculate_project (scope rollup)
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; subtype=flex_space
#   current_behavior: Reconciles finishes totals from scope items into construction costs for flex space.
#   move_to_config: scope_profile
#   parity_fixture_hint: industrial_flex_finishes_delta
# - id: healthcare_equipment_soft_cost
#   location: UnifiedEngine.calculate_project (soft cost split)
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE
#   current_behavior: Treats equipment as a soft cost for healthcare instead of hard cost.
#   move_to_config: scope_defaults
#   parity_fixture_hint: healthcare_equipment_soft_cost
# - id: restaurant_cost_clamp
#   location: UnifiedEngine.calculate_project (restaurant clamp)
#   selector_type: clamp
#   keys: building_type=RESTAURANT; subtype!=fine_dining
#   current_behavior: Clamps restaurant total cost per SF to 250-700, with fine dining exempt from max.
#   move_to_config: cost_clamp
#   parity_fixture_hint: restaurant_cost_clamp_standard
# - id: industrial_flex_revenue_per_sf_totals
#   location: UnifiedEngine.calculate_project (totals payload)
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; subtype=flex_space
#   current_behavior: Adds revenue_per_sf and annual_revenue to totals for industrial flex space.
#   move_to_config: other
#   parity_fixture_hint: industrial_flex_revenue_per_sf
# - id: facility_metrics_restaurant
#   location: UnifiedEngine.calculate_project (facility metrics)
#   selector_type: routing
#   keys: building_type=RESTAURANT
#   current_behavior: Builds restaurant facility metrics payload (sales/noi/cost per SF).
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: facility_metrics_restaurant
# - id: facility_metrics_healthcare_outpatient
#   location: UnifiedEngine.calculate_project (facility metrics)
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE; facility_metrics_profile=healthcare_outpatient
#   current_behavior: Builds outpatient healthcare facility metrics (units, cost per unit, revenue per unit).
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: facility_metrics_healthcare_outpatient
# - id: hospitality_metrics_passthrough
#   location: UnifiedEngine.calculate_project (hospitality passthrough)
#   selector_type: conditional_branch
#   keys: building_type name contains HOSPITALITY or HOTEL
#   current_behavior: Copies hospitality financial metrics into top-level response fields.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: hospitality_metrics_passthrough
# - id: industrial_scope_items_shell_subtypes
#   location: UnifiedEngine._build_scope_items
#   selector_type: subtype_list
#   keys: building_type=INDUSTRIAL; scope_profile in industrial_shell/industrial_flex/industrial_cold_storage
#   current_behavior: Enables industrial scope item generation only for shell subtypes.
#   move_to_config: scope_profile
#   parity_fixture_hint: industrial_scope_shell
# - id: industrial_scope_flex_space_split
#   location: UnifiedEngine._build_scope_items
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; scope_profile=industrial_flex
#   current_behavior: Splits office vs warehouse areas and applies flex-specific finishes uplift/systems.
#   move_to_config: scope_profile
#   parity_fixture_hint: industrial_scope_flex
# - id: industrial_scope_cold_storage_conceptual
#   location: UnifiedEngine._build_scope_items
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; scope_profile=industrial_cold_storage
#   current_behavior: Uses conceptual cold-storage systems with blast freezer detection.
#   move_to_config: scope_profile
#   parity_fixture_hint: industrial_scope_cold_storage
# - id: office_operating_expense_overrides
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=OFFICE
#   current_behavior: Applies office-specific operating expense, CAM, and staffing overrides.
#   move_to_config: other
#   parity_fixture_hint: office_operating_expense_overrides
# - id: industrial_occupancy_rate_selection
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL
#   current_behavior: Selects occupancy rate from base/premium industrial config with 0.95 fallback.
#   move_to_config: other
#   parity_fixture_hint: industrial_occupancy_rate
# - id: restaurant_full_service_finish_overrides
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=RESTAURANT; subtype=full_service
#   current_behavior: Overrides occupancy and margin from finish-level overrides for full-service restaurants.
#   move_to_config: finish_level_multipliers
#   parity_fixture_hint: restaurant_full_service_finish_overrides
# - id: hospitality_financials_overrides
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=HOSPITALITY
#   current_behavior: Applies hospitality financial overrides to occupancy/margin when provided.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: hospitality_financials_overrides
# - id: industrial_operating_margin_override
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL
#   current_behavior: Forces industrial margin to configured operating_margin_base when present.
#   move_to_config: other
#   parity_fixture_hint: industrial_operating_margin_override
# - id: industrial_cold_storage_tenant_utilities
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; subtype=cold_storage; scenario in tenant_paid_utilities/nnn_utilities/cold_storage_nnn
#   current_behavior: Adjusts margin for tenant-paid utilities and suppresses utility ratio in efficiency config.
#   move_to_config: other
#   parity_fixture_hint: industrial_cold_storage_nnn
# - id: office_staffing_costs_from_expenses
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=OFFICE
#   current_behavior: Derives property management and maintenance staffing costs from office expenses.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: office_staffing_costs
# - id: unit_derivation_multifamily
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=MULTIFAMILY
#   current_behavior: Estimates units from units_per_sf when not provided.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: multifamily_unit_estimate
# - id: unit_derivation_healthcare_outpatient
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE; facility_metrics_profile=healthcare_outpatient
#   current_behavior: Derives outpatient units and per-unit cost/revenue when financial_metrics present.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: healthcare_unit_estimate
# - id: healthcare_outpatient_sensitivity_tiles
#   location: UnifiedEngine.calculate_ownership_analysis
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE; facility_metrics_profile=healthcare_outpatient
#   current_behavior: Builds outpatient-specific sensitivity tiles instead of generic NOI adjustments.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: healthcare_outpatient_sensitivity
# - id: revenue_by_type_healthcare
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=HEALTHCARE; subtype=medical_office_building for MOB revenue path
#   current_behavior: Computes revenue via beds/visits/procedures/scans or per-SF, with MOB override.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_healthcare_medical_office
# - id: revenue_by_type_multifamily
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=MULTIFAMILY
#   current_behavior: Calculates revenue from units per SF and monthly rent.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_multifamily_units
# - id: revenue_by_type_hospitality
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=HOSPITALITY
#   current_behavior: Uses hospitality financials (ADR/occupancy/rooms) or room-based fallback.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_hospitality
# - id: revenue_by_type_office
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=OFFICE
#   current_behavior: Builds office financials from profile inputs and uses EGI as revenue.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_office_profile
# - id: revenue_by_type_educational
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=EDUCATIONAL
#   current_behavior: Calculates revenue per student.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_educational
# - id: revenue_by_type_parking
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=PARKING
#   current_behavior: Calculates revenue per space with monthly rate if available.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_parking
# - id: revenue_by_type_recreation
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=RECREATION
#   current_behavior: Uses revenue per seat when configured, else per-SF revenue.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_recreation
# - id: revenue_by_type_civic
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=CIVIC
#   current_behavior: Returns zero revenue for civic projects.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_civic_zero
# - id: revenue_by_type_industrial_default
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=INDUSTRIAL; subtype=flex_space for office rent uplift
#   current_behavior: Calculates industrial revenue per SF with flex-space rent blending.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_industrial_flex
# - id: revenue_by_type_default_other
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: conditional_branch
#   keys: building_type=other (retail/restaurant/mixed_use/etc.)
#   current_behavior: Defaults to base_revenue_per_sf_annual for remaining types.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: revenue_default_per_sf
# - id: restaurant_full_service_finish_multipliers
#   location: UnifiedEngine._calculate_revenue_by_type
#   selector_type: subtype_map
#   keys: building_type=RESTAURANT; subtype=full_service; finish_level in standard/premium/luxury
#   current_behavior: Applies finish-level revenue, occupancy, and margin adjustments for full service.
#   move_to_config: finish_level_multipliers
#   parity_fixture_hint: restaurant_full_service_finish_levels
# - id: operational_metrics_restaurant
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=restaurant
#   current_behavior: Formats restaurant-specific staffing, revenue ratios, and KPIs.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_restaurant
# - id: operational_metrics_healthcare_outpatient
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=healthcare; facility_metrics_profile=healthcare_outpatient
#   current_behavior: Builds outpatient clinic staffing/revenue KPIs based on visits and rooms.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_healthcare_outpatient
# - id: operational_metrics_healthcare_inpatient
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=healthcare; subtype=other
#   current_behavior: Uses inpatient-style staffing and KPI defaults for healthcare non-outpatient.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_healthcare_inpatient
# - id: operational_metrics_multifamily
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=multifamily
#   current_behavior: Formats multifamily staffing, revenue, and NOI KPIs.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_multifamily
# - id: operational_metrics_office
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=office
#   current_behavior: Formats office staffing, revenue per SF, and efficiency KPIs.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_office
# - id: operational_metrics_generic_other
#   location: UnifiedEngine.calculate_operational_metrics_for_display
#   selector_type: conditional_branch
#   keys: building_type=other
#   current_behavior: Uses generic staffing/revenue/KPI formatting for non-specific types.
#   move_to_config: facility_metrics_profile
#   parity_fixture_hint: operational_metrics_generic
# - id: manufacturing_exclude_from_facility_opex
#   location: UnifiedEngine.calculate_operational_efficiency
#   selector_type: conditional_branch
#   keys: exclude_from_facility_opex configured
#   current_behavior: Excludes labor/materials ratios from facility opex for manufacturing.
#   move_to_config: exclude_from_facility_opex
#   parity_fixture_hint: manufacturing_exclude_opex
# - id: building_type_string_map
#   location: UnifiedEngine._get_building_enum
#   selector_type: routing
#   keys: building_type string -> BuildingType enum
#   current_behavior: Maps string building types to enum values for ownership analysis.
#   move_to_config: other
#   parity_fixture_hint: building_type_string_map
# - id: exit_cap_discount_by_type_name
#   location: UnifiedEngine.get_exit_cap_and_discount_rate
#   selector_type: conditional_branch
#   keys: building_type name contains MULTIFAMILY/INDUSTRIAL/WAREHOUSE/OFFICE/HOSPITALITY/HOTEL
#   current_behavior: Picks exit cap and discount rates by building type name; defaults otherwise.
#   move_to_config: other
#   parity_fixture_hint: exit_cap_discount_defaults
# - id: project_class_keyword_inference
#   location: UnifiedEngine.estimate_from_description
#   selector_type: conditional_branch
#   keys: description keywords -> project_class (renovation/addition/tenant_improvement/ground_up)
#   current_behavior: Infers project class from description keywords.
#   move_to_config: other
#   parity_fixture_hint: project_class_description_keywords
# - id: market_rate_subtype_quality_adjustment
#   location: UnifiedEngine.get_market_rate
#   selector_type: conditional_branch
#   keys: subtype contains luxury/class_a vs affordable/class_c
#   current_behavior: Adjusts market rate up or down based on subtype quality keywords.
#   move_to_config: other
#   parity_fixture_hint: market_rate_quality_adjustment


def _add_months(base_date: date, months: int) -> date:
    """Add months to a date without relying on external libs."""
    month = base_date.month - 1 + months
    year = base_date.year + month // 12
    month = month % 12 + 1
    day = min(base_date.day, 28)  # avoid month-end overflow
    return date(year, month, day)


def _month_to_quarter_string(d: date) -> str:
    """Convert a date to a quarter string like 'Q1 2025'."""
    quarter = (d.month - 1) // 3 + 1
    return f"Q{quarter} {d.year}"


def build_construction_schedule(
    building_type: BuildingType,
    subtype: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Build the construction schedule payload (total duration + phase timings)
    for the Construction Schedule card.
    """
    return _build_construction_schedule(building_type=building_type, subtype=subtype)


def build_project_timeline(building_type: BuildingType, start_date: Optional[date] = None) -> Dict[str, str]:
    """
    Build a project timeline dictionary for the Executive View "Key Milestones" card.
    Returns milestone names mapped to quarter strings (e.g., 'Q1 2025').
    """
    base_date = start_date or date(2025, 1, 1)

    config = PROJECT_TIMELINES.get(building_type)
    milestones = None
    timeline_details: List[Dict[str, str]] = []
    if config:
        ground_up = config.get("ground_up", {})
        milestones = ground_up.get("milestones")

    timeline: Dict[str, str] = {}
    if isinstance(milestones, dict):
        iterable = milestones.items()
        for key, offset_months in iterable:
            milestone_date = _add_months(base_date, int(offset_months))
            timeline[key] = _month_to_quarter_string(milestone_date)
    elif isinstance(milestones, list):
        for entry in milestones:
            if not isinstance(entry, dict):
                continue
            milestone_id = entry.get("id") or entry.get("key")
            offset_value = entry.get("offset_months")
            if offset_value is None:
                offset_value = entry.get("month")
            if milestone_id is None or offset_value is None:
                continue
            milestone_date = _add_months(base_date, int(offset_value))
            quarter_label = _month_to_quarter_string(milestone_date)
            timeline[milestone_id] = quarter_label
            label = entry.get("label")
            if label:
                timeline_details.append({
                    "id": milestone_id,
                    "label": label,
                    "date": quarter_label,
                })
    else:
        defaults = {
            "groundbreaking": 0,
            "structure_complete": 8,
            "substantial_completion": 18,
            "grand_opening": 24,
        }
        for key, offset_months in defaults.items():
            milestone_date = _add_months(base_date, int(offset_months))
            timeline[key] = _month_to_quarter_string(milestone_date)

    if timeline_details:
        timeline["_details"] = timeline_details

    return timeline

class UnifiedEngine:
    def _normalize_project_class(self, value: Any) -> str:
        """
        Map various project_type/project_class inputs into the string values
        expected by ProjectClass enums (e.g. 'ground_up').
        """
        raw = value
        if isinstance(value, dict):
            raw = (
                value.get("project_type")
                or value.get("projectType")
                or value.get("project_class")
                or value.get("projectClass")
            )
        if not raw:
            return "ground_up"

        s = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
        if s in ("groundup", "ground_up", "ground"):
            return "ground_up"
        if s in ("renovation", "reno", "remodel"):
            return "renovation"
        if s in ("addition", "add", "expansion"):
            return "addition"
        if s in ("tenant_improvement", "tenant", "ti"):
            return "tenant_improvement"
        return "ground_up"

    @staticmethod
    def _normalize_special_feature_key(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip().lower().replace("-", "_").replace(" ", "_")

    def _normalize_healthcare_special_feature_id(
        self,
        subtype: Any,
        feature_id: Any,
        available_feature_keys: List[str],
    ) -> Optional[str]:
        normalized_feature = self._normalize_special_feature_key(feature_id)
        if not normalized_feature:
            return None

        available_by_normalized: Dict[str, str] = {}
        for raw_key in available_feature_keys:
            normalized_key = self._normalize_special_feature_key(raw_key)
            if normalized_key:
                available_by_normalized[normalized_key] = raw_key

        if normalized_feature in available_by_normalized:
            return available_by_normalized[normalized_feature]

        subtype_key = self._normalize_special_feature_key(subtype)
        subtype_aliases = HEALTHCARE_SPECIAL_FEATURE_ALIASES.get(subtype_key, {})
        canonical_candidate = subtype_aliases.get(normalized_feature)
        if not canonical_candidate:
            return None

        canonical_normalized = self._normalize_special_feature_key(canonical_candidate)
        return available_by_normalized.get(canonical_normalized)
    """
    One engine to rule them all.
    Single source of truth for all cost calculations.
    """
    
    def __init__(self):
        """Initialize the unified engine"""
        self.config = MASTER_CONFIG
        self.calculation_trace = []  # Track every calculation for debugging
        self._nlp_service = NLPService()
        # self.financial_analyzer = FinancialAnalyzer()  # TODO: Add financial analyzer
        
    def calculate_project(self, 
                         building_type: BuildingType,
                         subtype: str,
                         square_footage: float,
                         location: str,
                         project_class: ProjectClass = ProjectClass.GROUND_UP,
                         floors: int = 1,
                         ownership_type: OwnershipType = OwnershipType.FOR_PROFIT,
                         finish_level: Optional[str] = None,
                         special_features: List[str] = None,
                         finish_level_source: Optional[str] = None,
                         parsed_input_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        The master calculation method.
        Everything goes through here.
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype (e.g., 'hospital', 'class_a')
            square_footage: Total square footage
            location: City/location for regional multiplier
            project_class: Ground-up, renovation, etc.
            floors: Number of floors
            ownership_type: For-profit, non-profit, etc.
            finish_level: Optional finish quality override
            special_features: List of special features to add
            finish_level_source: Trace provenance for finish level selection
            parsed_input_overrides: Optional parsed input dict for scope overrides
            
        Returns:
            Comprehensive cost breakdown dictionary
        """
        
        # Normalize project class input if provided as a raw string
        if isinstance(project_class, str):
            normalized_class = self._normalize_project_class(project_class)
            try:
                project_class = ProjectClass(normalized_class)
            except ValueError:
                project_class = ProjectClass.GROUND_UP
        self._log_trace("project_class_normalized", {
            'project_class': project_class.value if isinstance(project_class, ProjectClass) else str(project_class),
        })
        try:
            raw_project_type = None
            if isinstance(special_features, dict):  # not likely, but guard
                raw_project_type = special_features.get("project_type")
            if raw_project_type is None:
                raw_project_type = getattr(project_class, "value", project_class)
            print("[SpecSharp][UnifiedEngine] project_class=", raw_project_type)
        except Exception:
            pass

        # Clear trace for new calculation
        self.calculation_trace = []
        self._log_trace("calculation_start", {
            'building_type': building_type.value,
            'subtype': subtype,
            'square_footage': square_footage,
            'location': location
        })

        normalized_finish_level = finish_level.lower().strip() if isinstance(finish_level, str) and finish_level.strip() else None
        inferred_source = finish_level_source if finish_level_source in {'explicit', 'description', 'default'} else None

        if inferred_source == 'explicit':
            finish_source = 'explicit'
        elif inferred_source == 'description':
            finish_source = 'description'
        elif inferred_source == 'default':
            finish_source = 'default'
        elif normalized_finish_level:
            finish_source = 'explicit'
        else:
            finish_source = 'default'

        if not normalized_finish_level:
            normalized_finish_level = 'standard'

        self._log_trace("finish_level_source", {
            'source': finish_source,
            'finish_level': normalized_finish_level or 'standard'
        })
        quality_factor = resolve_quality_factor(normalized_finish_level, building_type, subtype)
        self._log_trace("quality_factor_resolved", {
            'finish_level': normalized_finish_level or 'standard',
            'quality_factor': round(quality_factor, 4)
        })

        city_only_warning_logged = False

        def _city_only_warning():
            nonlocal city_only_warning_logged
            if not city_only_warning_logged:
                self._log_trace("warning", {
                    'message': 'City-only location used default regional multiplier'
                })
                city_only_warning_logged = True
        
        # Get configuration
        if isinstance(subtype, dict):
            subtype = (
                subtype.get("id")
                or subtype.get("key")
                or subtype.get("value")
                or subtype.get("subtype")
            )
        logger.info(
            "[SUBTYPE_TRACE][engine_entry] building_type=%s subtype_raw=%s subtype_normalized=%s",
            getattr(building_type, "value", building_type),
            subtype,
            (subtype.lower().strip() if isinstance(subtype, str) else subtype),
        )
        building_config = get_building_config(building_type, subtype)
        if not building_config:
            raise ValueError(f"No configuration found for {building_type.value}/{subtype}")

        # Normalize ownership type and gracefully fall back when the requested
        # ownership type is not configured for this subtype.
        if isinstance(ownership_type, str):
            try:
                ownership_type = OwnershipType(ownership_type)
            except ValueError:
                ownership_type = OwnershipType.FOR_PROFIT

        if isinstance(getattr(building_config, "ownership_types", None), dict) and building_config.ownership_types:
            if ownership_type not in building_config.ownership_types:
                fallback_ownership = next(iter(building_config.ownership_types.keys()))
                self._log_trace(
                    "ownership_type_fallback",
                    {
                        "requested": getattr(ownership_type, "value", str(ownership_type)),
                        "fallback": getattr(fallback_ownership, "value", str(fallback_ownership)),
                        "building_type": building_type.value,
                        "subtype": subtype,
                    },
                )
                ownership_type = fallback_ownership
        
        # Validate and adjust project class if incompatible
        original_class = project_class
        project_class = validate_project_class(building_type, subtype, project_class)
        if project_class != original_class:
            self._log_trace("project_class_adjusted", {
                'original': original_class.value,
                'adjusted': project_class.value,
                'reason': 'Incompatible with building type'
            })
        
        # Base construction cost calculation with finish level adjustment
        original_base_cost_per_sf = building_config.base_cost_per_sf

        # Height premium for office towers: add modest multipliers for taller structures
        height_factor = 1.0
        if building_type == BuildingType.OFFICE:
            try:
                floor_count = int(floors or building_config.typical_floors or 1)
            except (TypeError, ValueError):
                floor_count = 1

            extra_premium = 0.0
            if floor_count > 4:
                extra_premium += max(0, min(floor_count, 8) - 4) * 0.02  # 2% per floor from 5-8
            if floor_count > 8:
                extra_premium += max(0, min(floor_count, 12) - 8) * 0.01  # 1% per floor from 9-12

            height_factor = 1.0 + min(extra_premium, 0.20)  # Cap at +20%

        base_cost_per_sf = original_base_cost_per_sf * height_factor
        self._log_trace("base_cost_retrieved", {
            'base_cost_per_sf': original_base_cost_per_sf,
            'quality_factor': round(quality_factor, 4),
            'height_factor': round(height_factor, 4),
            'adjusted_base_cost_per_sf': round(base_cost_per_sf, 4)
        })
        
        # Apply project class multiplier (treated as complexity factor)
        class_multiplier = PROJECT_CLASS_MULTIPLIERS[project_class]
        complexity_factor = class_multiplier
        cost_after_complexity = base_cost_per_sf * complexity_factor
        self._log_trace("project_class_multiplier_applied", {
            'multiplier': complexity_factor,
            'adjusted_cost_per_sf': round(cost_after_complexity, 4)
        })

        modifiers = get_effective_modifiers(
            building_type,
            subtype,
            normalized_finish_level,
            location,
            warning_callback=_city_only_warning
        )
        margin_pct_override = None
        try:
            cfg_margin = getattr(building_config, 'operating_margin_base', None)
            if cfg_margin is not None:
                margin_pct_override = float(cfg_margin)
        except (TypeError, ValueError):
            margin_pct_override = None
        if (
            building_type == BuildingType.HEALTHCARE
            and subtype == 'medical_office_building'
            and margin_pct_override is not None
        ):
            modifiers = {**modifiers, 'margin_pct': margin_pct_override}

        self._log_trace("finish_cost_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'factor': round(modifiers.get('finish_cost_factor', 1.0), 4)
        })

        finish_cost_factor = modifiers.get('finish_cost_factor', 1.0)
        if not finish_cost_factor:
            finish_cost_factor = 1.0
        cost_factor = modifiers['cost_factor']
        if finish_cost_factor:
            regional_multiplier_effective = cost_factor / finish_cost_factor
        else:
            regional_multiplier_effective = cost_factor

        cost_after_regional = cost_after_complexity * regional_multiplier_effective
        regional_context = resolve_location_context(location)
        final_cost_per_sf = cost_after_regional * finish_cost_factor
        self._log_trace("modifiers_applied", {
            'finish_level': normalized_finish_level or 'standard',
            'cost_factor': round(cost_factor, 4),
            'regional_multiplier': round(regional_multiplier_effective, 4),
            'revenue_factor': round(modifiers['revenue_factor'], 4),
            'margin_pct': round(modifiers['margin_pct'], 4)
        })

        mixed_use_split_contract: Optional[Dict[str, Any]] = None
        if building_type == BuildingType.MIXED_USE:
            description_for_split = None
            if isinstance(parsed_input_overrides, dict):
                raw_description = parsed_input_overrides.get("description")
                if isinstance(raw_description, str) and raw_description.strip():
                    description_for_split = raw_description.strip()
            mixed_use_split_contract = self._resolve_mixed_use_split_contract(
                subtype=subtype,
                parsed_input_overrides=parsed_input_overrides,
                description=description_for_split,
            )
            split_value = mixed_use_split_contract.get("value") if isinstance(mixed_use_split_contract, dict) else None
            split_cost_factor = self._mixed_use_weighted_factor(
                split_value if isinstance(split_value, dict) else {},
                MIXED_USE_COST_COMPONENT_MULTIPLIERS,
            )
            split_revenue_factor = self._mixed_use_weighted_factor(
                split_value if isinstance(split_value, dict) else {},
                MIXED_USE_REVENUE_COMPONENT_MULTIPLIERS,
            )
            if split_cost_factor <= 0:
                split_cost_factor = 1.0
            if split_revenue_factor <= 0:
                split_revenue_factor = 1.0
            final_cost_per_sf = final_cost_per_sf * split_cost_factor
            mixed_use_split_contract["cost_factor_applied"] = round(split_cost_factor, 6)
            mixed_use_split_contract["revenue_factor_applied"] = round(split_revenue_factor, 6)
            self._log_trace("mixed_use_split_resolved", {
                "source": mixed_use_split_contract.get("source"),
                "normalization_applied": bool(mixed_use_split_contract.get("normalization_applied")),
                "cost_factor_applied": round(split_cost_factor, 6),
                "revenue_factor_applied": round(split_revenue_factor, 6),
                "value": split_value,
                "invalid_mix": mixed_use_split_contract.get("invalid_mix"),
            })
        
        # Calculate base construction cost
        construction_cost = final_cost_per_sf * square_footage
        
        # Calculate equipment cost with finish/regional adjustments
        equipment_multiplier = modifiers.get('finish_cost_factor', 1.0)
        equipment_cost = building_config.equipment_cost_per_sf * equipment_multiplier * square_footage
        
        # Add special features if any
        special_features_cost = 0
        special_features_breakdown: List[Dict[str, Any]] = []
        special_features_breakdown_by_id: Dict[str, Dict[str, Any]] = {}
        if special_features and building_config.special_features:
            healthcare_applied_feature_ids: set = set()
            available_feature_keys = list(building_config.special_features.keys())
            for feature in special_features:
                if isinstance(feature, dict):
                    continue
                raw_feature_key = self._normalize_special_feature_key(feature)
                canonical_feature_key = feature
                if building_type == BuildingType.HEALTHCARE:
                    canonical_feature_key = self._normalize_healthcare_special_feature_id(
                        subtype=subtype,
                        feature_id=feature,
                        available_feature_keys=available_feature_keys,
                    )
                    if canonical_feature_key is None:
                        continue
                    if canonical_feature_key in healthcare_applied_feature_ids:
                        continue
                    healthcare_applied_feature_ids.add(canonical_feature_key)
                    if raw_feature_key and raw_feature_key != self._normalize_special_feature_key(canonical_feature_key):
                        self._log_trace("special_feature_alias_normalized", {
                            'feature': feature,
                            'canonical_feature': canonical_feature_key,
                            'subtype': subtype,
                        })

                if canonical_feature_key in building_config.special_features:
                    cost_per_sf = float(building_config.special_features[canonical_feature_key])
                    feature_cost = cost_per_sf * square_footage
                    special_features_cost += feature_cost
                    row = special_features_breakdown_by_id.get(canonical_feature_key)
                    if row is None:
                        row = {
                            'id': canonical_feature_key,
                            'cost_per_sf': cost_per_sf,
                            'total_cost': 0.0,
                            'label': _humanize_special_feature_label(canonical_feature_key),
                        }
                        special_features_breakdown_by_id[canonical_feature_key] = row
                        special_features_breakdown.append(row)
                    row['total_cost'] = float(row['total_cost']) + feature_cost
                    self._log_trace("special_feature_applied", {
                        'feature': canonical_feature_key,
                        'cost_per_sf': cost_per_sf,
                        'total_cost': feature_cost
                    })
        if special_features_breakdown:
            special_features_cost = sum(float(item.get('total_cost', 0.0) or 0.0) for item in special_features_breakdown)
        
        # Calculate trade breakdown
        trades = self._calculate_trades(construction_cost, building_config.trades)
        
        # Scope items are config-driven via scope_items_profile; engine applies
        # generic allocation rules with deterministic fallbacks.
        scope_context = self._resolve_scope_context(special_features)
        def _extract_scenario_key(source: Optional[Dict[str, Any]]) -> Optional[str]:
            if not isinstance(source, dict):
                return None
            for key in ("scenario", "scenario_key", "scenarioName", "scenarioKey"):
                value = source.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip().lower()
            nested = source.get('__parsed_input__')
            if isinstance(nested, dict):
                nested_value = _extract_scenario_key(nested)
                if nested_value:
                    return nested_value
            parsed_nested = source.get('parsed_input') or source.get('parsedInput')
            if isinstance(parsed_nested, dict):
                nested_value = _extract_scenario_key(parsed_nested)
                if nested_value:
                    return nested_value
            return None
        scenario_key = None
        for candidate in (parsed_input_overrides, scope_context):
            scenario_key = _extract_scenario_key(candidate)
            if scenario_key:
                break
        scenario_key_normalized = (scenario_key or '').strip().lower() if scenario_key else None
        if isinstance(parsed_input_overrides, dict):
            # Merge parsed_input so explicit overrides (e.g. dock_doors) are honored downstream
            scope_context = {**(scope_context or {}), **parsed_input_overrides}
        scope_items = self._build_scope_items(
            building_type=building_type,
            subtype=subtype,
            trades=trades,
            square_footage=square_footage,
            scope_context=scope_context
        )

        # Apply flex-specific finishes delta to rollups so office uplift affects totals
        if building_type == BuildingType.INDUSTRIAL:
            subtype_value = subtype.value if hasattr(subtype, "value") else subtype
            subtype_key = (subtype_value or "").lower().strip() if isinstance(subtype_value, str) else str(subtype_value or "").lower().strip()
            scope_config = get_building_config(building_type, subtype_key)
            scope_profile = getattr(scope_config, "scope_profile", None) if scope_config else None
            if scope_profile == "industrial_flex":
                finishes_item = next((item for item in scope_items if item.get("trade") == "Finishes"), None)
                systems = finishes_item.get("systems", []) if isinstance(finishes_item, dict) else []
                finishes_total_effective = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
                baseline_finishes = float(trades.get("finishes", 0.0) or 0.0)
                if finishes_total_effective > 0 and finishes_total_effective != baseline_finishes:
                    delta = finishes_total_effective - baseline_finishes
                    trades["finishes"] = finishes_total_effective
                    construction_cost += delta
                    if square_footage > 0:
                        final_cost_per_sf = construction_cost / square_footage

        # Calculate soft costs (after any flex adjustments)
        soft_costs = self._calculate_soft_costs(construction_cost, building_config.soft_costs)
        
        # For healthcare facilities, equipment is a soft cost (medical equipment)
        # For other building types, it's part of hard costs
        if building_type == BuildingType.HEALTHCARE:
            soft_costs['medical_equipment'] = equipment_cost
            total_hard_costs = construction_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        else:
            total_hard_costs = construction_cost + equipment_cost + special_features_cost
            total_soft_costs = sum(soft_costs.values())
        
        total_project_cost = total_hard_costs + total_soft_costs
        
        # Validate restaurant costs are within reasonable ranges
        if building_type == BuildingType.RESTAURANT:
            cost_per_sf = total_project_cost / square_footage
            raw_cost_clamp = getattr(building_config, "cost_clamp", None)
            cost_clamp = raw_cost_clamp or {}
            min_cost = cost_clamp.get("min_cost_per_sf", 250)
            max_cost = cost_clamp.get("max_cost_per_sf", 700) if raw_cost_clamp is None else cost_clamp.get("max_cost_per_sf")
            
            if isinstance(min_cost, (int, float)) and cost_per_sf < min_cost:
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'minimum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': min_cost
                })
                # Adjust costs proportionally
                adjustment_factor = (min_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = min_cost * square_footage
            elif isinstance(max_cost, (int, float)) and cost_per_sf > max_cost:
                self._log_trace("restaurant_cost_clamp", {
                    'mode': 'maximum',
                    'original_cost_per_sf': cost_per_sf,
                    'target_cost_per_sf': max_cost
                })
                # Cap costs proportionally
                adjustment_factor = (max_cost * square_footage) / total_project_cost
                total_hard_costs *= adjustment_factor
                total_soft_costs *= adjustment_factor
                total_project_cost = max_cost * square_footage
        
        # Calculate ownership/financing analysis with enhanced financial metrics
        ownership_bundle = self._build_ownership_bundle(
            building_config=building_config,
            ownership_type=ownership_type,
            total_project_cost=total_project_cost,
            calculation_context={
                'building_type': building_type.value,
                'subtype': subtype,
                'square_footage': square_footage,
                'total_cost': total_project_cost,
                'subtotal': construction_cost,  # Construction cost before contingency
                'modifiers': modifiers,
                'quality_factor': quality_factor,
                'finish_level': normalized_finish_level,
                'regional_context': regional_context,
                'location': location,
                'scenario': scenario_key,
                'mixed_use_split': mixed_use_split_contract,
                'ownership_type': ownership_type.value if hasattr(ownership_type, 'value') else ownership_type,
            },
        )
        ownership_analysis = ownership_bundle['ownership_analysis']
        revenue_data = ownership_bundle['revenue_data']
        flex_revenue_per_sf = ownership_bundle['flex_revenue_per_sf']
        
        # Financial requirements removed - was only partially implemented for hospital
        
        # Generate cost DNA for transparency
        cost_dna = {
            'base_cost': base_cost_per_sf,
            'finish_adjustment': finish_cost_factor,
            'regional_adjustment': regional_multiplier_effective,
            'complexity_factor': complexity_factor,
            'final_cost': final_cost_per_sf,
            'location': location,
            'market_name': location.split(',')[0] if location else 'Nashville',  # Extract city name
            'building_type': building_type.value if hasattr(building_type, 'value') else str(building_type),
            'subtype': subtype,
            'detected_factors': [],  # Will be populated with special features
            'applied_adjustments': {
                'base': base_cost_per_sf,
                'after_finish': cost_after_complexity,
                'after_class': cost_after_complexity,
                'after_complexity': cost_after_complexity,
                'after_finish_factor': final_cost_per_sf,
                'after_regional': cost_after_regional,
                'final': final_cost_per_sf
            },
            'market_context': {
                'market': location.split(',')[0] if location else 'Nashville',
                'index': modifiers.get('market_factor', 1.0),
                'comparison': 'above national average' if modifiers.get('market_factor', 1.0) > 1.0 else 'below national average' if modifiers.get('market_factor', 1.0) < 1.0 else 'at national average',
                'percentage_difference': round((modifiers.get('market_factor', 1.0) - 1.0) * 100, 1)
            }
        }
        
        # Add special features if present
        if special_features:
            cost_dna['detected_factors'] = list(special_features) if isinstance(special_features, (list, dict)) else [special_features]

        cost_build_up = [
            {
                'label': 'Base Cost',
                'value_per_sf': base_cost_per_sf
            },
            {
                'label': 'Regional',
                'multiplier': regional_multiplier_effective
            },
            {
                'label': 'Complexity',
                'multiplier': complexity_factor
            }
        ]

        display_finish_level = (normalized_finish_level or 'standard').lower()
        if display_finish_level != 'standard':
            cost_build_up.append({
                'label': 'Finish Level',
                'multiplier': finish_cost_factor
            })
        
        # Ensure the build-up array always has something meaningful so frontend visuals don't break
        fallback_cost_build_up = cost_build_up if cost_build_up else [
            {'label': 'Base Cost', 'value_per_sf': original_base_cost_per_sf},
            {'label': 'Regional', 'multiplier': regional_multiplier_effective},
            {'label': 'Complexity', 'multiplier': complexity_factor},
        ]
        if not cost_build_up and display_finish_level != 'standard':
            fallback_cost_build_up.append({'label': 'Finish Level', 'multiplier': finish_cost_factor})

        profile = get_building_profile(building_type)

        # Surface sensitivity analysis for frontend quick sensitivity tiles
        sensitivity_analysis = None
        if ownership_analysis and isinstance(ownership_analysis, dict):
            # For healthcare (outpatient / urgent care) this will contain a base object
            # and a scenarios list. For other types it may be missing or None.
            sensitivity_analysis = ownership_analysis.get('sensitivity_analysis')

        city_value = regional_context.get('city')
        state_value = regional_context.get('state')
        pretty_location = None
        if city_value and state_value:
            pretty_location = f"{city_value.title()}, {state_value}"
        elif city_value:
            pretty_location = city_value.title()
        regional_cost_factor = regional_context.get('cost_factor')
        regional_market_factor = regional_context.get('market_factor', 1.0)
        regional_payload = {
            'city': city_value.title() if city_value else None,
            'state': state_value,
            'source': regional_context.get('source'),
            'multiplier': regional_multiplier_effective,
            'cost_factor': regional_cost_factor if regional_cost_factor is not None else regional_multiplier_effective,
            'market_factor': regional_market_factor,
            'location_display': pretty_location or regional_context.get('location_display') or location
        }

        # Build comprehensive response - FLATTENED structure to match frontend expectations
        totals_payload = {
            'hard_costs': total_hard_costs,
            'soft_costs': total_soft_costs,
            'total_project_cost': total_project_cost,
            'cost_per_sf': total_project_cost / square_footage if square_footage > 0 else 0
        }
        if scenario_key:
            totals_payload['scenario_key'] = scenario_key
        if isinstance(mixed_use_split_contract, dict):
            totals_payload['mixed_use_split_source'] = mixed_use_split_contract.get('source')

        if (
            flex_revenue_per_sf is not None
            and building_type == BuildingType.INDUSTRIAL
            and isinstance(subtype, str)
            and subtype.strip().lower() == 'flex_space'
            and square_footage > 0
        ):
            totals_payload['revenue_per_sf'] = flex_revenue_per_sf
            totals_payload['annual_revenue'] = flex_revenue_per_sf * float(square_footage)

        result = {
            'project_info': {
                'building_type': building_type.value,
                'subtype': subtype,
                'display_name': building_config.display_name,
                'project_class': project_class.value,
                'square_footage': square_footage,
                'location': location,
                'floors': floors,
                'typical_floors': building_config.typical_floors,
                'finish_level': normalized_finish_level or 'standard',
                'finish_level_source': finish_source,
                'available_special_features': list(building_config.special_features.keys()) if building_config.special_features else [],
                'mixed_use_split': mixed_use_split_contract,
            },
            'profile': {
                'building_type': building_type.value,
                'market_cap_rate': profile.get('market_cap_rate'),
                'target_yield': profile.get('target_yield'),
                'target_dscr': profile.get('target_dscr'),
            },
            'modifiers': modifiers,
            'mixed_use_split': mixed_use_split_contract,
            'regional': regional_payload,
            # Flatten calculations to top level to match frontend CalculationResult interface
            'construction_costs': {
                'base_cost_per_sf': base_cost_per_sf,
                'original_base_cost_per_sf': original_base_cost_per_sf,
                'class_multiplier': class_multiplier,
                'regional_multiplier': regional_multiplier_effective,
                'finish_cost_factor': finish_cost_factor,
                'cost_factor': cost_factor,
                'quality_factor': quality_factor,
                'final_cost_per_sf': final_cost_per_sf,
                'construction_total': construction_cost,
                'equipment_total': equipment_cost,
                'special_features_total': special_features_cost,
                'special_features_breakdown': special_features_breakdown,
                'cost_build_up': fallback_cost_build_up
            },
            'cost_dna': cost_dna,  # Add cost DNA for transparency
            'trade_breakdown': trades,
            'scope_items': scope_items,
            'soft_costs': soft_costs,
            'totals': totals_payload,
            'ownership_analysis': ownership_analysis,
            # Add revenue_analysis at top level for easy access
            'revenue_analysis': ownership_analysis.get('revenue_analysis', {}) if ownership_analysis else {},
            # Add revenue_requirements at top level for easy access
            'revenue_requirements': ownership_analysis.get('revenue_requirements', {}) if ownership_analysis else {},
            # Add roi_analysis at top level for frontend compatibility
            'roi_analysis': ownership_analysis.get('roi_analysis', {}) if ownership_analysis else {},
            # Add operational efficiency at top level
            'operational_efficiency': ownership_analysis.get('operational_efficiency', {}) if ownership_analysis else {},
            # Add return metrics at top level for investment visibility
            'return_metrics': ownership_analysis.get('return_metrics', {}) if ownership_analysis else {},
            # Add roi metrics at top level for investment analysis
            'roi_metrics': ownership_analysis.get('roi_metrics', {}) if ownership_analysis else {},
            # Add department and operational metrics at top level for easy frontend access
            'department_allocation': ownership_analysis.get('department_allocation', []) if ownership_analysis else [],
            'operational_metrics': ownership_analysis.get('operational_metrics', {}) if ownership_analysis else {},
            # Expose sensitivity analysis at the top level for the v2 frontend
            'sensitivity_analysis': sensitivity_analysis,
            'regional_applied': True,
            'calculation_trace': self.calculation_trace,
            'timestamp': datetime.now().isoformat()
        }

        profile_id = getattr(building_config, "dealshield_tile_profile", None)
        if isinstance(profile_id, str) and profile_id.strip():
            result["dealshield_tile_profile"] = profile_id
            if profile_id in {
                "industrial_warehouse_v1",
                "industrial_distribution_center_v1",
                "industrial_manufacturing_v1",
                "industrial_flex_space_v1",
                "industrial_cold_storage_v1",
                "healthcare_surgical_center_v1",
                "healthcare_imaging_center_v1",
                "healthcare_medical_office_building_v1",
                "healthcare_outpatient_clinic_v1",
                "healthcare_dental_office_v1",
                "healthcare_hospital_v1",
                "healthcare_medical_center_v1",
                "healthcare_nursing_home_v1",
                "healthcare_rehabilitation_v1",
                "healthcare_urgent_care_v1",
                "restaurant_quick_service_v1",
                "restaurant_full_service_v1",
                "restaurant_fine_dining_v1",
                "restaurant_cafe_v1",
                "restaurant_bar_tavern_v1",
                "hospitality_limited_service_hotel_v1",
                "hospitality_full_service_hotel_v1",
                "office_class_a_v1",
                "office_class_b_v1",
                "retail_shopping_center_v1",
                "retail_big_box_v1",
                "multifamily_market_rate_apartments_v1",
                "multifamily_luxury_apartments_v1",
                "multifamily_affordable_housing_v1",
                "specialty_data_center_v1",
                "specialty_laboratory_v1",
                "specialty_self_storage_v1",
                "specialty_car_dealership_v1",
                "specialty_broadcast_facility_v1",
                "educational_elementary_school_v1",
                "educational_middle_school_v1",
                "educational_high_school_v1",
                "educational_university_v1",
                "educational_community_college_v1",
                "civic_library_v1",
                "civic_courthouse_v1",
                "civic_government_building_v1",
                "civic_community_center_v1",
                "civic_public_safety_v1",
                "recreation_fitness_center_v1",
                "recreation_sports_complex_v1",
                "recreation_aquatic_center_v1",
                "recreation_recreation_center_v1",
                "recreation_stadium_v1",
                "parking_surface_parking_v1",
                "parking_parking_garage_v1",
                "parking_underground_parking_v1",
                "parking_automated_parking_v1",
                "mixed_use_office_residential_v1",
                "mixed_use_retail_residential_v1",
                "mixed_use_hotel_retail_v1",
                "mixed_use_transit_oriented_v1",
                "mixed_use_urban_mixed_v1",
            }:
                from app.v2.services.dealshield_scenarios import (
                    build_dealshield_scenarios,
                    DealShieldScenarioError,
                )
                try:
                    result["dealshield_scenarios"] = build_dealshield_scenarios(
                        result,
                        building_config,
                        self,
                    )
                except DealShieldScenarioError as exc:
                    raise ValueError(f"DealShield scenario build failed: {exc}") from exc

        scope_items_profile_id = getattr(building_config, "scope_items_profile", None)
        if isinstance(scope_items_profile_id, str) and scope_items_profile_id.strip():
            resolved_scope_profile_id = scope_items_profile_id.strip()
            result["scope_items_profile"] = resolved_scope_profile_id
            result["scope_items_profile_id"] = resolved_scope_profile_id

        scope_profile_id = getattr(building_config, "scope_profile", None)
        if isinstance(scope_profile_id, str) and scope_profile_id.strip():
            result["scope_profile_id"] = scope_profile_id.strip()

        revenue_block = result.get('revenue_analysis')
        if isinstance(revenue_block, dict):
            revenue_block.setdefault('market_factor', regional_market_factor)
        if ownership_analysis and isinstance(ownership_analysis, dict):
            nested_revenue = ownership_analysis.get('revenue_analysis')
            if isinstance(nested_revenue, dict):
                nested_revenue.setdefault('market_factor', regional_market_factor)

        facility_metrics_payload = None
        if building_type == BuildingType.RESTAURANT:
            total_sf = float(square_footage) if square_footage else 0.0
            revenue_block = result.get('revenue_analysis') or {}
            return_block = result.get('return_metrics') or {}
            totals_block = result.get('totals') or {}
            annual_revenue_value = revenue_block.get('annual_revenue')
            annual_noi_value = return_block.get('estimated_annual_noi')
            total_cost_value = totals_block.get('total_project_cost')

            def _per_sf(value: Optional[float]) -> float:
                if not value or not total_sf:
                    return 0.0
                try:
                    return float(value) / float(total_sf)
                except (TypeError, ZeroDivisionError):
                    return 0.0

            facility_metrics_payload = {
                'type': 'restaurant',
                'metrics': [
                    {
                        'id': 'sales_per_sf',
                        'label': 'Sales per SF',
                        'value': _per_sf(annual_revenue_value),
                        'unit': '$/SF'
                    },
                    {
                        'id': 'noi_per_sf',
                        'label': 'NOI per SF',
                        'value': _per_sf(annual_noi_value),
                        'unit': '$/SF'
                    },
                    {
                        'id': 'cost_per_sf',
                        'label': 'All-in Cost per SF',
                        'value': _per_sf(total_cost_value),
                        'unit': '$/SF'
                    }
                ],
                'total_square_feet': total_sf
            }
        elif building_type == BuildingType.HEALTHCARE:
            financial_metrics_cfg = self._get_healthcare_financial_metrics(building_config)
            primary_unit_label = financial_metrics_cfg.get('primary_unit', 'Units')
            facility_profile = getattr(building_config, "facility_metrics_profile", None)
            computed_units = self._resolve_healthcare_units(building_config, square_footage)
            cost_per_unit = total_project_cost / computed_units if computed_units else 0
            annual_revenue_value = self._coerce_number((result.get('revenue_analysis') or {}).get('annual_revenue')) or 0.0

            revenue_per_unit_cfg = self._coerce_number(financial_metrics_cfg.get('revenue_per_unit_annual'))
            if revenue_per_unit_cfg is not None and facility_profile == "healthcare_outpatient":
                revenue_per_unit = revenue_per_unit_cfg
            else:
                revenue_per_unit = annual_revenue_value / computed_units if computed_units else 0

            facility_metrics_payload = {
                'type': 'healthcare',
                'units': computed_units,
                'unit_label': primary_unit_label,
                'cost_per_unit': cost_per_unit,
                'revenue_per_unit': revenue_per_unit,
            }
        elif building_type == BuildingType.OFFICE:
            total_sf = float(square_footage) if square_footage else 0.0
            revenue_block = result.get('revenue_analysis') or {}
            return_block = result.get('return_metrics') or {}
            totals_block = result.get('totals') or {}

            annual_revenue_value = self._coerce_number(revenue_block.get('annual_revenue')) or 0.0
            annual_noi_value = (
                self._coerce_number(return_block.get('estimated_annual_noi'))
                or self._coerce_number(revenue_block.get('net_income'))
                or 0.0
            )
            total_cost_value = self._coerce_number(totals_block.get('total_project_cost')) or 0.0

            def _per_sf_non_negative(value: Optional[float]) -> float:
                if total_sf <= 0:
                    return 0.0
                try:
                    per_sf_value = float(value or 0.0) / total_sf
                except (TypeError, ValueError, ZeroDivisionError):
                    return 0.0
                return max(0.0, per_sf_value)

            facility_metrics_payload = {
                'type': 'office',
                'metrics': [
                    {
                        'id': 'cost_per_sf',
                        'label': 'All-in Cost per SF',
                        'value': _per_sf_non_negative(total_cost_value),
                        'unit': '$/SF',
                    },
                    {
                        'id': 'revenue_per_sf',
                        'label': 'Revenue per SF',
                        'value': _per_sf_non_negative(annual_revenue_value),
                        'unit': '$/SF',
                    },
                    {
                        'id': 'noi_per_sf',
                        'label': 'NOI per SF',
                        'value': _per_sf_non_negative(annual_noi_value),
                        'unit': '$/SF',
                    },
                ],
                'total_square_feet': total_sf,
            }

        if facility_metrics_payload:
            result['facility_metrics'] = facility_metrics_payload
        
        # Financial requirements removed - was only partially implemented
        
        self._log_trace("calculation_end", {
            'total_project_cost': total_project_cost,
            'cost_per_sf': total_project_cost / square_footage
        })

        try:
            building_type_name = building_type.name if hasattr(building_type, 'name') else str(building_type)
        except Exception:
            building_type_name = str(building_type)
        if isinstance(building_type_name, str) and (
            'HOSPITALITY' in building_type_name.upper() or 'HOTEL' in building_type_name.upper()
        ):
            hospitality_metrics = None
            if revenue_data and isinstance(revenue_data, dict):
                hospitality_metrics = revenue_data.get('hospitality_financials')
            if not hospitality_metrics and ownership_analysis:
                hospitality_metrics = ownership_analysis.get('hospitality_financials')
            if not hospitality_metrics:
                hospitality_metrics = result.get('hospitality_financials')
            if hospitality_metrics:
                key_map = {
                    'rooms': 'rooms',
                    'adr': 'adr',
                    'occupancy': 'occupancy',
                    'revpar': 'revpar',
                    'cost_per_key': 'cost_per_key'
                }
                for source_key, dest_key in key_map.items():
                    metric_value = hospitality_metrics.get(source_key)
                    if metric_value is None:
                        continue
                    try:
                        result[dest_key] = float(metric_value)
                    except (TypeError, ValueError):
                        result[dest_key] = metric_value
                if 'cost_per_key' not in result or result['cost_per_key'] in (None, 0):
                    rooms_metric = hospitality_metrics.get('rooms') or result.get('rooms')
                    if rooms_metric not in (None, 0):
                        try:
                            result['cost_per_key'] = float(total_project_cost) / float(rooms_metric)
                        except (TypeError, ValueError, ZeroDivisionError):
                            pass
                result['hospitality_financials'] = hospitality_metrics
        
        return result
    
    def _calculate_trades(self, construction_cost: float, trades_config: Any) -> Dict[str, float]:
        """Calculate trade breakdown costs"""
        trades = {}
        trades_dict = asdict(trades_config)
        
        for trade, percentage in trades_dict.items():
            trades[trade] = construction_cost * percentage
            
        self._log_trace("trade_breakdown_calculated", {
            'total': construction_cost,
            'trades': len(trades)
        })
        
        return trades
    
    def _calculate_soft_costs(self, construction_cost: float, soft_costs_config: Any) -> Dict[str, float]:
        """Calculate soft costs"""
        soft_costs = {}
        soft_costs_dict = asdict(soft_costs_config)
        
        for cost_type, rate in soft_costs_dict.items():
            soft_costs[cost_type] = construction_cost * rate
            
        self._log_trace("soft_costs_calculated", {
            'base': construction_cost,
            'total_soft': sum(soft_costs.values())
        })
        
        return soft_costs
    
    def _resolve_scope_context(self, special_features: Optional[Any]) -> Optional[Dict[str, Any]]:
        """
        Attempt to derive a context dictionary for scope generation overrides.
        Accepts dict-like special_features or any embedded dicts within the list.
        """
        context: Dict[str, Any] = {}
        
        if isinstance(special_features, dict):
            context.update(special_features)
            nested = special_features.get("__parsed_input__")
            if isinstance(nested, dict):
                context.update(nested)
        elif isinstance(special_features, list):
            for feature in special_features:
                if isinstance(feature, dict):
                    context.update(feature)
                    nested = feature.get("__parsed_input__")
                    if isinstance(nested, dict):
                        context.update(nested)
        
        return context or None

    @staticmethod
    def _safe_unit_cost(total: float, qty: float) -> float:
        if not qty:
            return 0.0
        try:
            return float(total) / float(qty)
        except (TypeError, ValueError, ZeroDivisionError):
            return 0.0

    def _collect_scope_override_sources(
        self, scope_context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        if not isinstance(scope_context, dict):
            return sources

        sources.append(scope_context)

        potential_nested_keys = [
            "parsed_input",
            "parsedInput",
            "request_data",
            "requestData",
            "input_overrides",
            "overrides",
            "scope_overrides",
            "context",
            "__parsed_input__",
        ]
        for key in potential_nested_keys:
            nested_value = scope_context.get(key)
            if isinstance(nested_value, dict):
                sources.append(nested_value)

        calculations_ctx = scope_context.get("calculations")
        if isinstance(calculations_ctx, dict):
            for calc_key in ("parsed_input", "parsedInput", "request_data", "requestData"):
                calc_nested = calculations_ctx.get(calc_key)
                if isinstance(calc_nested, dict):
                    sources.append(calc_nested)

        return sources

    @staticmethod
    def _coerce_number(value: Any) -> Optional[float]:
        if value is None:
            return None
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            cleaned = stripped.replace("%", "").replace(",", "")
            try:
                return float(cleaned)
            except ValueError:
                return None
        return None

    def _get_override_number(self, sources: List[Dict[str, Any]], keys: List[str]) -> Optional[float]:
        for source in sources:
            for key in keys:
                if key in source:
                    number = self._coerce_number(source.get(key))
                    if number is not None:
                        return number
        return None

    def _get_percent_override(self, sources: List[Dict[str, Any]], keys: List[str]) -> Optional[float]:
        value = self._get_override_number(sources, keys)
        if value is None:
            return None
        percent = float(value)
        if percent > 1.0:
            percent = percent / 100.0
        return max(percent, 0.0)

    @staticmethod
    def _default_mixed_use_pair(subtype: Any) -> Tuple[str, str]:
        subtype_key = (str(subtype) if subtype is not None else "").strip().lower()
        return MIXED_USE_DEFAULT_SPLIT_BY_SUBTYPE.get(subtype_key, ("office", "residential"))

    def _default_mixed_use_split_value(self, subtype: Any) -> Dict[str, float]:
        primary, secondary = self._default_mixed_use_pair(subtype)
        value = {component: 0.0 for component in MIXED_USE_SPLIT_COMPONENTS}
        value[primary] = 50.0
        value[secondary] = 50.0
        return value

    @staticmethod
    def _coerce_mixed_use_split_value(raw_value: Any) -> Optional[float]:
        if raw_value is None:
            return None
        if isinstance(raw_value, bool):
            return None
        if isinstance(raw_value, (int, float)):
            value = float(raw_value)
        elif isinstance(raw_value, str):
            cleaned = raw_value.strip().replace("%", "").replace(",", "")
            if not cleaned:
                return None
            try:
                value = float(cleaned)
            except ValueError:
                return None
        else:
            return None
        if not math.isfinite(value):
            return None
        return value

    def _extract_mixed_use_split_components(
        self,
        split_source: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, float]], bool, Optional[str]]:
        components_source: Dict[str, Any] = {}
        if isinstance(split_source.get("components"), dict):
            components_source = dict(split_source.get("components") or {})
        else:
            components_source = dict(split_source)

        allowed_keys = set()
        for component in MIXED_USE_SPLIT_COMPONENTS:
            allowed_keys.update({
                component,
                f"{component}_pct",
                f"{component}_percent",
                f"{component}_share",
            })
        unknown_keys = [
            key for key in components_source.keys()
            if isinstance(key, str) and key not in allowed_keys and key not in {"pattern", "source", "normalization_applied"}
        ]
        if unknown_keys:
            return None, False, "unsupported_component"

        extracted: Dict[str, float] = {}
        for component in MIXED_USE_SPLIT_COMPONENTS:
            raw_value = None
            for key in (
                component,
                f"{component}_pct",
                f"{component}_percent",
                f"{component}_share",
            ):
                if key in components_source:
                    raw_value = components_source.get(key)
                    break
            coerced = self._coerce_mixed_use_split_value(raw_value)
            if coerced is None:
                continue
            if coerced < 0:
                return None, False, "negative_component_value"
            extracted[component] = coerced

        if not extracted:
            return None, False, "missing_components"

        total = sum(extracted.values())
        fraction_notation = total > 0 and total <= 1.0001 and all(value <= 1.0001 for value in extracted.values())
        if fraction_notation:
            extracted = {component: value * 100.0 for component, value in extracted.items()}

        return extracted, fraction_notation, None

    def _normalize_mixed_use_split_components(
        self,
        components: Dict[str, float],
        subtype: Any,
    ) -> Tuple[Optional[Dict[str, float]], bool, bool, Optional[str]]:
        if not isinstance(components, dict) or not components:
            return None, False, False, "missing_components"

        unknown_components = [key for key in components.keys() if key not in MIXED_USE_SPLIT_COMPONENTS]
        if unknown_components:
            return None, False, False, "unsupported_component"

        normalized: Dict[str, float] = {}
        for component, raw_value in components.items():
            value = self._coerce_mixed_use_split_value(raw_value)
            if value is None:
                return None, False, False, "non_numeric_component"
            if value < 0:
                return None, False, False, "negative_component_value"
            normalized[component] = value

        normalization_applied = False
        inference_applied = False

        if len(normalized) == 1:
            component, value = next(iter(normalized.items()))
            if value > 100.0:
                return None, False, False, "single_component_exceeds_100"
            primary, secondary = self._default_mixed_use_pair(subtype)
            counterpart = secondary if component == primary else primary
            if counterpart == component:
                counterpart = next(
                    (candidate for candidate in MIXED_USE_SPLIT_COMPONENTS if candidate != component),
                    "residential",
                )
            normalized[counterpart] = max(0.0, 100.0 - value)
            inference_applied = True
            normalization_applied = True

        total = sum(normalized.values())
        if total <= 0:
            return None, False, inference_applied, "non_positive_total"

        if not math.isclose(total, 100.0, rel_tol=0.0, abs_tol=1e-9):
            scale = 100.0 / total
            normalized = {
                component: (value * scale)
                for component, value in normalized.items()
            }
            normalization_applied = True

        rounded = {
            component: round(value, 2)
            for component, value in normalized.items()
        }
        rounded_total = sum(rounded.values())
        if not math.isclose(rounded_total, 100.0, rel_tol=0.0, abs_tol=1e-9):
            largest_component = max(rounded.keys(), key=lambda key: rounded[key])
            rounded[largest_component] = round(rounded[largest_component] + (100.0 - rounded_total), 2)
            normalization_applied = True

        final_total = sum(rounded.values())
        if not math.isclose(final_total, 100.0, rel_tol=0.0, abs_tol=0.05):
            return None, normalization_applied, inference_applied, "unable_to_normalize_to_100"

        canonical = {component: 0.0 for component in MIXED_USE_SPLIT_COMPONENTS}
        for component, value in rounded.items():
            canonical[component] = value
        return canonical, normalization_applied, inference_applied, None

    def _parse_mixed_use_split_from_description(
        self,
        description: Any,
        subtype: Any,
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(description, str) or not description.strip():
            return None

        text_lower = description.lower()
        component_pattern = r"(office|residential|retail|hotel|transit)"
        pair_components = self._default_mixed_use_pair(subtype)

        labeled_matches = re.findall(
            rf"(\d{{1,3}}(?:\.\d+)?)\s*%\s*{component_pattern}\b",
            text_lower,
        )
        if labeled_matches:
            components: Dict[str, float] = {}
            for pct_text, component in labeled_matches:
                try:
                    pct_value = float(pct_text)
                except ValueError:
                    continue
                components[component] = components.get(component, 0.0) + pct_value
            if components:
                return {
                    "components": components,
                    "pattern": "component_percent",
                }

        ratio_match = re.search(
            r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*/\s*(\d{1,3}(?:\.\d+)?)(?!\d)",
            text_lower,
        )
        if ratio_match:
            return {
                "components": {
                    pair_components[0]: float(ratio_match.group(1)),
                    pair_components[1]: float(ratio_match.group(2)),
                },
                "pattern": "ratio_pair",
            }

        mostly_match = re.search(rf"\bmostly\s+{component_pattern}\b", text_lower)
        if mostly_match:
            dominant = mostly_match.group(1)
            counterpart = next(
                (candidate for candidate in pair_components if candidate != dominant),
                pair_components[0],
            )
            if counterpart == dominant:
                counterpart = next(
                    (candidate for candidate in MIXED_USE_SPLIT_COMPONENTS if candidate != dominant),
                    "residential",
                )
            return {
                "components": {dominant: 70.0, counterpart: 30.0},
                "pattern": "mostly_component",
            }

        heavy_match = re.search(rf"\b{component_pattern}[-\s]?heavy\b", text_lower)
        if heavy_match:
            dominant = heavy_match.group(1)
            counterpart = next(
                (candidate for candidate in pair_components if candidate != dominant),
                pair_components[0],
            )
            if counterpart == dominant:
                counterpart = next(
                    (candidate for candidate in MIXED_USE_SPLIT_COMPONENTS if candidate != dominant),
                    "residential",
                )
            return {
                "components": {dominant: 70.0, counterpart: 30.0},
                "pattern": "heavy_component",
            }

        if re.search(r"\bbalanced\b", text_lower):
            return {
                "components": {
                    pair_components[0]: 50.0,
                    pair_components[1]: 50.0,
                },
                "pattern": "balanced_pair",
            }

        return None

    def _resolve_mixed_use_split_contract(
        self,
        subtype: Any,
        parsed_input_overrides: Optional[Dict[str, Any]],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        default_value = self._default_mixed_use_split_value(subtype)
        contract: Dict[str, Any] = {
            "value": default_value,
            "source": "default",
            "normalization_applied": False,
        }

        candidate_source = "default"
        candidate_payload: Optional[Dict[str, Any]] = None
        candidate_pattern: Optional[str] = None

        if isinstance(parsed_input_overrides, dict):
            explicit_split = parsed_input_overrides.get("mixed_use_split")
            nlp_split_hint = parsed_input_overrides.get("mixed_use_split_hint")
            if isinstance(explicit_split, dict):
                candidate_source = "user_input"
                candidate_payload = explicit_split
                candidate_pattern = explicit_split.get("pattern") if isinstance(explicit_split.get("pattern"), str) else None
            elif isinstance(nlp_split_hint, dict):
                candidate_source = "nlp_detected"
                candidate_payload = nlp_split_hint
                candidate_pattern = nlp_split_hint.get("pattern") if isinstance(nlp_split_hint.get("pattern"), str) else None
            else:
                direct_components = {
                    key: parsed_input_overrides.get(key)
                    for key in (
                        "office",
                        "residential",
                        "retail",
                        "hotel",
                        "transit",
                        "office_pct",
                        "residential_pct",
                        "retail_pct",
                        "hotel_pct",
                        "transit_pct",
                    )
                    if key in parsed_input_overrides
                }
                if direct_components:
                    candidate_source = "user_input"
                    candidate_payload = direct_components

        if candidate_payload is None:
            parsed_candidate = self._parse_mixed_use_split_from_description(description, subtype)
            if isinstance(parsed_candidate, dict):
                candidate_source = "nlp_detected"
                candidate_payload = parsed_candidate
                candidate_pattern = parsed_candidate.get("pattern") if isinstance(parsed_candidate.get("pattern"), str) else None

        if candidate_payload is None:
            return contract

        extracted_components, fraction_notation, extraction_error = self._extract_mixed_use_split_components(candidate_payload)
        if extraction_error or extracted_components is None:
            contract["invalid_mix"] = {
                "reason": extraction_error or "invalid_candidate",
                "source": candidate_source,
            }
            return contract

        normalized_value, normalized_applied, inference_applied, normalization_error = self._normalize_mixed_use_split_components(
            extracted_components,
            subtype,
        )
        if normalization_error or normalized_value is None:
            contract["invalid_mix"] = {
                "reason": normalization_error or "invalid_candidate",
                "source": candidate_source,
                "input": extracted_components,
            }
            return contract

        contract["value"] = normalized_value
        contract["source"] = candidate_source
        contract["normalization_applied"] = bool(normalized_applied or fraction_notation)
        if inference_applied:
            contract["inference_applied"] = True
        if candidate_pattern:
            contract["pattern"] = candidate_pattern
        return contract

    @staticmethod
    def _mixed_use_weighted_factor(
        split_value: Dict[str, Any],
        multiplier_by_component: Dict[str, float],
    ) -> float:
        if not isinstance(split_value, dict):
            return 1.0
        weighted = 0.0
        total_share = 0.0
        for component in MIXED_USE_SPLIT_COMPONENTS:
            raw_share = split_value.get(component, 0.0)
            try:
                share_pct = float(raw_share)
            except (TypeError, ValueError):
                continue
            if share_pct <= 0:
                continue
            weighted += (share_pct / 100.0) * float(multiplier_by_component.get(component, 1.0))
            total_share += share_pct
        if total_share <= 0:
            return 1.0
        return weighted

    def _get_healthcare_financial_metrics(self, subtype_config: Any) -> Dict[str, Any]:
        if subtype_config is None:
            return {}
        financial_metrics = getattr(subtype_config, "financial_metrics", None)
        return dict(financial_metrics) if isinstance(financial_metrics, dict) else {}

    def _resolve_healthcare_units(
        self,
        subtype_config: Any,
        square_footage: float,
        *,
        fallback_units: Optional[int] = None,
    ) -> int:
        if isinstance(fallback_units, int) and fallback_units > 0:
            return fallback_units

        sf_value = self._coerce_number(square_footage) or 0.0
        if sf_value <= 0:
            return 1

        financial_metrics = self._get_healthcare_financial_metrics(subtype_config)
        units_per_sf = self._coerce_number(financial_metrics.get("units_per_sf"))
        if units_per_sf is None:
            units_per_sf = self._coerce_number(getattr(subtype_config, "units_per_sf", None))
        if units_per_sf is None:
            units_per_sf = self._coerce_number(getattr(subtype_config, "beds_per_sf", None))
        if units_per_sf is None or units_per_sf <= 0:
            return 1

        derived_units = int(round(sf_value * float(units_per_sf)))
        return max(1, derived_units)

    def _resolve_healthcare_operational_profile(
        self,
        subtype_key: str,
        subtype_config: Any,
    ) -> Dict[str, Any]:
        subtype_normalized = (subtype_key or "").strip().lower()
        profile = dict(HEALTHCARE_OPERATIONAL_METRIC_DEFAULTS.get(subtype_normalized, {}))
        financial_metrics = self._get_healthcare_financial_metrics(subtype_config)
        configured_profile = financial_metrics.get("operational_metrics")
        if isinstance(configured_profile, dict):
            for key, value in configured_profile.items():
                if value is not None:
                    profile[key] = value
        return profile

    def _resolve_office_sf(
        self,
        square_footage: float,
        override_sources: List[Dict[str, Any]],
        params: Dict[str, Any],
    ) -> float:
        override_keys = params.get("override_keys") if isinstance(params.get("override_keys"), list) else []
        office_sf_override = self._get_override_number(override_sources, override_keys)
        if office_sf_override is not None:
            office_sf_value = float(office_sf_override)
            if office_sf_value > 0.0:
                return office_sf_value

        percent_override_keys = (
            params.get("percent_override_keys") if isinstance(params.get("percent_override_keys"), list) else []
        )
        office_pct_override = self._get_override_number(override_sources, percent_override_keys)
        percent: Optional[float] = None
        if office_pct_override is not None:
            percent_value = float(office_pct_override)
            if 0.0 <= percent_value <= 1.0:
                percent = percent_value

        if percent is None:
            percent = float(params.get("default_percent", 0.05) or 0.05)

        default_min_sf = float(params.get("default_min_sf", 1500.0) or 1500.0)
        return max(default_min_sf, square_footage * percent)

    def _resolve_scope_item_quantity(
        self,
        quantity_rule: Dict[str, Any],
        square_footage: float,
        override_sources: List[Dict[str, Any]],
        *,
        item_key: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> Any:
        rule_type = str(quantity_rule.get("type") or "").strip().lower()
        params = quantity_rule.get("params") if isinstance(quantity_rule.get("params"), dict) else {}

        if rule_type == "sf":
            return float(square_footage)

        if rule_type == "dock_count":
            override_keys = params.get("override_keys") if isinstance(params.get("override_keys"), list) else []
            override_value = self._get_override_number(override_sources, override_keys)
            if override_value is not None:
                return max(0, int(round(override_value)))
            default_min = int(params.get("default_min", 0) or 0)
            default_sf_per_dock = float(params.get("default_sf_per_dock", 10000.0) or 10000.0)
            if default_sf_per_dock <= 0:
                return default_min
            return max(default_min, int(round(square_footage / default_sf_per_dock)))

        if rule_type == "mezz_sf":
            override_keys = params.get("override_keys") if isinstance(params.get("override_keys"), list) else []
            override_value = self._get_override_number(override_sources, override_keys)
            if override_value is not None:
                return max(0.0, float(override_value))

            percent_override_keys = (
                params.get("percent_override_keys") if isinstance(params.get("percent_override_keys"), list) else []
            )
            pct_override = self._get_percent_override(override_sources, percent_override_keys)
            if pct_override is not None:
                return max(0.0, square_footage * pct_override)

            return max(0.0, float(params.get("default_sf", 0.0) or 0.0))

        if rule_type == "constant":
            return params.get("value", 1.0) or 1.0

        if rule_type == "rtu_count":
            sf_per_unit = float(params.get("sf_per_unit", 15000.0) or 15000.0)
            minimum = int(params.get("minimum", 1) or 1)
            if sf_per_unit <= 0:
                return minimum
            return max(minimum, int(round(square_footage / sf_per_unit)))

        if rule_type == "exhaust_fan_count":
            sf_per_unit = float(params.get("sf_per_unit", 40000.0) or 40000.0)
            minimum = int(params.get("minimum", 1) or 1)
            if sf_per_unit <= 0:
                return minimum
            return max(minimum, int(round(square_footage / sf_per_unit)))

        if rule_type == "restroom_groups":
            sf_per_group = float(params.get("sf_per_group", 25000.0) or 25000.0)
            minimum = int(params.get("minimum", 1) or 1)
            if sf_per_group <= 0:
                return minimum
            return max(minimum, int(math.ceil(square_footage / sf_per_group)))

        if rule_type == "office_sf":
            return self._resolve_office_sf(square_footage, override_sources, params)

        if rule_type == "warehouse_sf":
            office_params = {
                "override_keys": (
                    params.get("office_override_keys")
                    if isinstance(params.get("office_override_keys"), list)
                    else []
                ),
                "percent_override_keys": (
                    params.get("office_percent_override_keys")
                    if isinstance(params.get("office_percent_override_keys"), list)
                    else []
                ),
                "default_percent": float(params.get("default_percent", 0.05) or 0.05),
                "default_min_sf": float(params.get("default_min_sf", 1500.0) or 1500.0),
            }
            office_sf = self._resolve_office_sf(square_footage, override_sources, office_params)
            return max(0.0, square_footage - office_sf) if square_footage > office_sf else square_footage

        resolved_item_key = item_key or "unknown"
        resolved_profile_id = profile_id or "unknown"
        raise ValueError(
            f"Unsupported quantity_rule.type: {rule_type or 'unknown'} (item key: {resolved_item_key}, "
            f"profile: {resolved_profile_id})"
        )

    def _load_scope_item_profile(self, profile_id: str, building_type: BuildingType) -> Optional[Dict[str, Any]]:
        profile_sources: List[Dict[str, Dict[str, Any]]] = []
        profile_sources.extend(scope_items.SCOPE_ITEM_PROFILE_SOURCES)
        if building_type == BuildingType.EDUCATIONAL:
            try:
                from app.v2.config.type_profiles.scope_items import educational as educational_scope_items

                profile_sources.append(educational_scope_items.SCOPE_ITEM_PROFILES)
            except Exception:
                pass
        if building_type == BuildingType.SPECIALTY:
            try:
                from app.v2.config.type_profiles.scope_items import specialty as specialty_scope_items

                profile_sources.append(specialty_scope_items.SCOPE_ITEM_PROFILES)
            except Exception:
                pass
        if building_type == BuildingType.RETAIL:
            try:
                from app.v2.config.type_profiles.scope_items import retail as retail_scope_items

                profile_sources.append(retail_scope_items.SCOPE_ITEM_PROFILES)
            except Exception:
                pass

        for source in profile_sources:
            profile = source.get(profile_id)
            if isinstance(profile, dict):
                return deepcopy(profile)
        return None

    def _resolve_scope_item_defaults(self, default_key: str) -> Dict[str, Any]:
        default_sources: List[Dict[str, Any]] = []
        default_sources.extend(scope_items.SCOPE_ITEM_DEFAULT_SOURCES)
        try:
            from app.v2.config.type_profiles.scope_items import educational as educational_scope_items

            default_sources.append(educational_scope_items.SCOPE_ITEM_DEFAULTS)
        except Exception:
            pass
        try:
            from app.v2.config.type_profiles.scope_items import specialty as specialty_scope_items

            default_sources.append(specialty_scope_items.SCOPE_ITEM_DEFAULTS)
        except Exception:
            pass
        try:
            from app.v2.config.type_profiles.scope_items import retail as retail_scope_items

            default_sources.append(retail_scope_items.SCOPE_ITEM_DEFAULTS)
        except Exception:
            pass
        for source in default_sources:
            if not isinstance(source, dict):
                continue
            default_value = source.get(default_key)
            if isinstance(default_value, dict):
                return default_value
        return {}

    def _apply_scope_item_overrides(
        self,
        profile: Dict[str, Any],
        profile_overrides: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not isinstance(profile_overrides, dict):
            return profile

        disabled_keys_raw = profile_overrides.get("disabled_items", profile_overrides.get("disable_items", []))
        disabled_keys = set(disabled_keys_raw) if isinstance(disabled_keys_raw, list) else set()

        share_overrides_raw = profile_overrides.get("share_overrides", profile_overrides.get("shares", {}))
        share_overrides = share_overrides_raw if isinstance(share_overrides_raw, dict) else {}
        extra_items = profile_overrides.get("extra_items")

        def _apply_overrides_to_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            filtered_items: List[Dict[str, Any]] = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                key = item.get("key")
                if key in disabled_keys:
                    continue

                cloned_item = deepcopy(item)
                if key in share_overrides:
                    share_value = self._coerce_number(share_overrides.get(key))
                    if share_value is not None:
                        allocation = cloned_item.get("allocation")
                        if isinstance(allocation, dict) and allocation.get("type") == "share_of_trade":
                            allocation["share"] = max(0.0, float(share_value))
                filtered_items.append(cloned_item)

            if isinstance(extra_items, list):
                for extra in extra_items:
                    if not isinstance(extra, dict):
                        continue
                    if not {"key", "label", "unit", "allocation", "quantity_rule"}.issubset(set(extra.keys())):
                        continue
                    if extra.get("key") in disabled_keys:
                        continue
                    filtered_items.append(deepcopy(extra))
            return filtered_items

        trade_profiles = profile.get("trade_profiles")
        if isinstance(trade_profiles, list):
            for trade_profile in trade_profiles:
                if not isinstance(trade_profile, dict):
                    continue
                items = trade_profile.get("items")
                if not isinstance(items, list):
                    continue
                trade_profile["items"] = _apply_overrides_to_items(items)
            return profile

        items = profile.get("items")
        if isinstance(items, list):
            profile["items"] = _apply_overrides_to_items(items)
        return profile

    def _resolve_healthcare_scope_subtype_from_profile(self, profile_id: str) -> Optional[str]:
        if not isinstance(profile_id, str):
            return None
        prefix = "healthcare_"
        suffix = "_structural_v1"
        if not (profile_id.startswith(prefix) and profile_id.endswith(suffix)):
            return None
        subtype = profile_id[len(prefix):-len(suffix)]
        return subtype if subtype else None

    def _resolve_healthcare_scope_group(self, subtype: str) -> str:
        if subtype in {"nursing_home", "rehabilitation"}:
            return "post_acute"
        if subtype in {"urgent_care", "outpatient_clinic", "medical_office_building", "dental_office"}:
            return "ambulatory"
        return "acuity"

    def _resolve_healthcare_scope_target_depth(self, subtype: str, trade_key: str) -> int:
        target = int(HEALTHCARE_SCOPE_MIN_SYSTEMS_BY_TRADE.get(trade_key, 5))
        if subtype in HEALTHCARE_HIGH_ACUITY_SCOPE_SUBTYPES:
            target = int(HEALTHCARE_SCOPE_MIN_SYSTEMS_HIGH_ACUITY_OVERRIDES.get(trade_key, target))
        return max(1, target)

    def _apply_healthcare_scope_depth_uplift(
        self,
        profile_id: str,
        trade_key: str,
        systems: List[Dict[str, Any]],
        square_footage: float,
    ) -> List[Dict[str, Any]]:
        subtype = self._resolve_healthcare_scope_subtype_from_profile(profile_id)
        if subtype is None:
            return systems

        target_depth = self._resolve_healthcare_scope_target_depth(subtype, trade_key)
        if len(systems) >= target_depth:
            return systems

        care_group = self._resolve_healthcare_scope_group(subtype)
        label_bank = HEALTHCARE_SCOPE_DEPTH_LABELS_BY_CARE_GROUP.get(care_group, {}).get(trade_key, [])
        if not label_bank:
            return systems

        existing_labels = {str(system.get("name") or "").strip().lower() for system in systems}
        candidate_labels = [label for label in label_bank if label.strip().lower() not in existing_labels]
        if not candidate_labels:
            return systems

        shortfall = min(target_depth - len(systems), len(candidate_labels))
        if shortfall <= 0:
            return systems

        donor_idx = max(
            range(len(systems)),
            key=lambda idx: float(systems[idx].get("total_cost", 0.0) or 0.0),
        )
        donor = systems[donor_idx]
        donor_total = float(donor.get("total_cost", 0.0) or 0.0)
        if donor_total <= 0:
            return systems

        reserve_fraction = min(0.28, 0.06 * shortfall)
        reserve_total = donor_total * reserve_fraction
        if reserve_total <= 0:
            return systems

        donor_quantity_raw = donor.get("quantity", square_footage)
        donor_quantity = float(donor_quantity_raw or 0.0)
        donor_unit = str(donor.get("unit") or "SF")

        donor_new_total = donor_total - reserve_total
        donor["total_cost"] = donor_new_total
        donor["unit_cost"] = self._safe_unit_cost(donor_new_total, donor_quantity)

        per_detail_cost = reserve_total / shortfall
        for idx in range(shortfall):
            label = candidate_labels[idx]
            systems.append(
                {
                    "name": label,
                    "quantity": donor_quantity_raw,
                    "unit": donor_unit,
                    "unit_cost": self._safe_unit_cost(per_detail_cost, donor_quantity),
                    "total_cost": per_detail_cost,
                }
            )

        return systems

    def _build_scope_items_for_trade_profile(
        self,
        trade_profile: Dict[str, Any],
        trades: Dict[str, float],
        square_footage: float,
        override_sources: List[Dict[str, Any]],
        profile_id: str,
    ) -> Optional[Dict[str, Any]]:
        trade_key = str(trade_profile.get("trade_key") or "").strip().lower()
        if not trade_key:
            return None

        trade_total = float(trades.get(trade_key, 0.0) or 0.0)
        if trade_total <= 0:
            return None

        items = trade_profile.get("items")
        if not isinstance(items, list) or not items:
            return None

        quantity_by_key: Dict[str, Any] = {}
        ordered_items: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            key = str(item.get("key") or "").strip()
            if not key:
                continue
            quantity_rule = item.get("quantity_rule")
            if not isinstance(quantity_rule, dict):
                continue
            quantity_by_key[key] = self._resolve_scope_item_quantity(
                quantity_rule,
                float(square_footage),
                override_sources,
                item_key=key,
                profile_id=profile_id,
            )
            ordered_items.append(item)

        share_by_key: Dict[str, float] = {}
        for item in ordered_items:
            allocation = item.get("allocation")
            if not isinstance(allocation, dict):
                continue
            if allocation.get("type") != "share_of_trade":
                continue
            key = str(item.get("key") or "").strip()
            share_by_key[key] = max(0.0, float(allocation.get("share", 0.0) or 0.0))

        conditional_rescales = trade_profile.get("conditional_rescales")
        if isinstance(conditional_rescales, list):
            for rule in conditional_rescales:
                if not isinstance(rule, dict):
                    continue
                trigger_key = str(rule.get("trigger_item_key") or "").strip()
                if not trigger_key:
                    continue
                if float(quantity_by_key.get(trigger_key, 0.0) or 0.0) <= 0:
                    continue
                target_item_keys = rule.get("target_item_keys")
                if not isinstance(target_item_keys, list) or not target_item_keys:
                    continue
                remaining_share = float(rule.get("remaining_share", 1.0) or 1.0)
                target_total = sum(float(share_by_key.get(str(key), 0.0) or 0.0) for key in target_item_keys)
                if target_total <= 0:
                    continue
                scale = remaining_share / target_total
                for key in target_item_keys:
                    key_name = str(key)
                    if key_name in share_by_key:
                        share_by_key[key_name] = share_by_key[key_name] * scale

        systems: List[Dict[str, Any]] = []
        for item in ordered_items:
            key = str(item.get("key") or "").strip()
            quantity = quantity_by_key.get(key, 0.0)
            numeric_quantity = float(quantity or 0.0)
            if item.get("omit_if_zero_quantity") and numeric_quantity <= 0:
                continue

            share = float(share_by_key.get(key, 0.0) or 0.0)
            total_cost = trade_total * share
            unit = str(item.get("unit") or "LS")
            label = str(item.get("label") or key)

            systems.append({
                "name": label,
                "quantity": quantity,
                "unit": unit,
                "unit_cost": self._safe_unit_cost(total_cost, numeric_quantity),
                "total_cost": total_cost,
            })

        if not systems:
            return None

        systems = self._apply_healthcare_scope_depth_uplift(
            profile_id=profile_id,
            trade_key=trade_key,
            systems=systems,
            square_footage=square_footage,
        )

        trade_label = str(trade_profile.get("trade_label") or trade_key.replace("_", " ").title())
        return {"trade": trade_label, "systems": systems}

    def _build_scope_items_from_profile(
        self,
        building_type: BuildingType,
        profile_id: str,
        trades: Dict[str, float],
        square_footage: float,
        scope_context: Optional[Dict[str, Any]],
        profile_overrides: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        profile = self._load_scope_item_profile(profile_id, building_type)
        if not profile:
            return []

        profile = self._apply_scope_item_overrides(profile, profile_overrides)
        override_sources = self._collect_scope_override_sources(scope_context)
        built_scope_items: List[Dict[str, Any]] = []

        trade_profiles = profile.get("trade_profiles")
        if isinstance(trade_profiles, list):
            for trade_profile in trade_profiles:
                if not isinstance(trade_profile, dict):
                    continue
                built = self._build_scope_items_for_trade_profile(
                    trade_profile=trade_profile,
                    trades=trades,
                    square_footage=square_footage,
                    override_sources=override_sources,
                    profile_id=profile_id,
                )
                if built:
                    built_scope_items.append(built)
        else:
            built = self._build_scope_items_for_trade_profile(
                trade_profile=profile,
                trades=trades,
                square_footage=square_footage,
                override_sources=override_sources,
                profile_id=profile_id,
            )
            if built:
                built_scope_items.append(built)

        if not built_scope_items:
            return []

        self._log_trace("scope_items_profile_applied", {
            "profile_id": profile_id,
            "trades": len(built_scope_items),
        })
        return built_scope_items

    def _build_scope_items(
        self,
        building_type: BuildingType,
        subtype: str,
        trades: Dict[str, float],
        square_footage: float,
        scope_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Scope items are config-driven via scope_items_profile; engine applies
        generic allocation rules and deterministic fallbacks.
        """
        scope_items: List[Dict[str, Any]] = []

        if not trades or square_footage <= 0:
            return scope_items

        subtype_key = (subtype or "").lower().strip()
        scope_config = get_building_config(building_type, subtype_key)
        scope_profile = getattr(scope_config, "scope_profile", None) if scope_config else None
        scope_items_profile = getattr(scope_config, "scope_items_profile", None) if scope_config else None
        scope_items_overrides = getattr(scope_config, "scope_items_overrides", None) if scope_config else None

        if isinstance(scope_items_profile, str) and scope_items_profile.strip():
            profile_scope_items = self._build_scope_items_from_profile(
                building_type=building_type,
                profile_id=scope_items_profile.strip(),
                trades=trades,
                square_footage=float(square_footage),
                scope_context=scope_context,
                profile_overrides=scope_items_overrides,
            )
            if profile_scope_items:
                return profile_scope_items

        if building_type == BuildingType.INDUSTRIAL and scope_profile in ("industrial_flex", "industrial_cold_storage"):
            sf = float(square_footage)
            is_flex = scope_profile == "industrial_flex"
            is_cold_storage = scope_profile == "industrial_cold_storage"
            override_sources = self._collect_scope_override_sources(scope_context)

            def _scope_has_keyword(value: Any, keyword_parts: List[str]) -> bool:
                if not value:
                    return False
                if isinstance(value, str):
                    lowered = value.lower()
                    return all(part in lowered for part in keyword_parts)
                if isinstance(value, list):
                    return any(_scope_has_keyword(item, keyword_parts) for item in value)
                if isinstance(value, dict):
                    return any(_scope_has_keyword(item, keyword_parts) for item in value.values())
                return False

            has_blast_freezer_feature = _scope_has_keyword(scope_context, ["blast", "freezer"])

            office_sf = 0.0
            warehouse_sf_for_flex = None

            if is_flex:
                office_share_override = self._get_percent_override(override_sources, [
                    "office_share",
                    "officeShare",
                    "office_split",
                    "officeSplit",
                ])
                if office_share_override is None:
                    office_share_value = 0.0
                else:
                    office_share_value = float(office_share_override)
                office_share_value = max(0.0, min(1.0, office_share_value))
                total_sf = float(sf)
                office_sf = round(total_sf * office_share_value, 2)
                warehouse_sf_for_flex = round(total_sf - office_sf, 2)
            mezz_sf = 0.0

            dock_override = self._get_override_number(override_sources, [
                "dock_doors",
                "dock_count",
                "dockDoors",
                "dockCount",
            ])
            if is_flex:
                dock_count = None
                if dock_override is not None:
                    dock_count = max(0, int(round(dock_override)))
            else:
                dock_count = None

            restroom_groups = max(1, int(round(sf / 25000.0)))

            structural_total = float(trades.get("structural", 0.0) or 0.0)
            if structural_total > 0:
                if is_flex:
                    include_docks = bool(dock_count and dock_count > 0)
                    flex_share_defaults = self._resolve_scope_item_defaults(
                        "industrial_flex_structural_shares",
                    )
                    slab_share = float(flex_share_defaults.get("slab", 0.0) or 0.0)
                    shell_share = float(flex_share_defaults.get("shell", 0.0) or 0.0)
                    foundations_share = float(flex_share_defaults.get("foundations", 0.0) or 0.0)
                    dock_share_default = float(flex_share_defaults.get("dock", 0.0) or 0.0)
                    dock_share = dock_share_default if include_docks else 0.0

                    if not include_docks:
                        base_total = slab_share + shell_share + foundations_share
                        if base_total > 0:
                            scale = 1.0 / base_total
                            slab_share *= scale
                            shell_share *= scale
                            foundations_share *= scale
                    mezz_share = 0.0

                    slab_total = structural_total * slab_share
                    shell_total = structural_total * shell_share
                    foundations_total = structural_total * foundations_share
                    docks_total = structural_total * dock_share if include_docks else 0.0

                    structural_systems = [
                        {
                            "name": 'Concrete slab on grade (6")',
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(slab_total, sf),
                            "total_cost": slab_total,
                        },
                        {
                            "name": "Tilt-wall panels / structural shell",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(shell_total, sf),
                            "total_cost": shell_total,
                        },
                        {
                            "name": "Foundations, footings, and thickened slabs",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(foundations_total, sf),
                            "total_cost": foundations_total,
                        },
                    ]

                    if include_docks and dock_count:
                        structural_systems.append({
                            "name": "Dock pits and loading aprons",
                            "quantity": dock_count,
                            "unit": "EA",
                            "unit_cost": self._safe_unit_cost(docks_total, dock_count),
                            "total_cost": docks_total,
                        })

                    scope_items.append({
                        "trade": "Structural",
                        "systems": structural_systems,
                    })
                elif is_cold_storage:
                    structural_entries = [
                        ('Concrete slab on grade (conceptual)', 0.4),
                        ('Foundations & thickened slabs (conceptual)', 0.3),
                        ('Structural shell (conceptual)', 0.3),
                    ]
                    structural_systems = []
                    total_share = sum(entry[1] for entry in structural_entries)
                    for name, share in structural_entries:
                        portion = structural_total * (share / total_share if total_share else 0)
                        structural_systems.append({
                            "name": name,
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(portion, sf),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })

                    scope_items.append({
                        "trade": "Structural",
                        "systems": structural_systems,
                    })

            mechanical_total = float(trades.get("mechanical", 0.0) or 0.0)
            if mechanical_total > 0:
                if is_cold_storage:
                    mechanical_entries: List[Tuple[str, float]] = [
                        ("Industrial refrigeration system (conceptual)", 0.45),
                        ("Evaporators & condensers (conceptual)", 0.30),
                        ("Temperature zone controls (conceptual)", 0.25),
                    ]
                    if has_blast_freezer_feature:
                        mechanical_entries.append(("Blast freezer systems (conceptual)", 0.20))
                    total_share = sum(entry[1] for entry in mechanical_entries)
                    mechanical_systems = []
                    for name, share in mechanical_entries:
                        portion = mechanical_total * (share / total_share if total_share else 0)
                        mechanical_systems.append({
                            "name": name,
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": self._safe_unit_cost(portion, 1),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Mechanical",
                        "systems": mechanical_systems,
                    })
                else:
                    rtu_count = max(1, int(round(sf / 15000.0)))
                    exhaust_fans = max(1, int(round(sf / 40000.0)))

                    rtu_share = 0.50
                    exhaust_share = 0.20
                    distribution_share = 0.30

                    rtu_total = mechanical_total * rtu_share
                    exhaust_total = mechanical_total * exhaust_share
                    distribution_total = mechanical_total * distribution_share

                    mechanical_systems = [
                        {
                            "name": "Rooftop units (RTUs) & primary heating/cooling equipment",
                            "quantity": rtu_count,
                            "unit": "EA",
                            "unit_cost": self._safe_unit_cost(rtu_total, rtu_count),
                            "total_cost": rtu_total,
                        },
                        {
                            "name": "Make-up air units and exhaust fans",
                            "quantity": exhaust_fans,
                            "unit": "EA",
                            "unit_cost": self._safe_unit_cost(exhaust_total, exhaust_fans),
                            "total_cost": exhaust_total,
                        },
                        {
                            "name": "Ductwork, distribution, and ventilation",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(distribution_total, sf),
                            "total_cost": distribution_total,
                        },
                    ]

                    scope_items.append({
                        "trade": "Mechanical",
                        "systems": mechanical_systems,
                    })

            electrical_total = float(trades.get("electrical", 0.0) or 0.0)
            if electrical_total > 0:
                if is_cold_storage:
                    electrical_entries = [
                        ("High-capacity power distribution (conceptual)", 0.45),
                        ("Controls & monitoring systems (conceptual)", 0.30),
                        ("Backup power allowance (conceptual)", 0.25),
                    ]
                    total_share = sum(share for _, share in electrical_entries)
                    electrical_systems = []
                    for name, share in electrical_entries:
                        portion = electrical_total * (share / total_share if total_share else 0)
                        electrical_systems.append({
                            "name": name,
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": self._safe_unit_cost(portion, 1),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Electrical",
                        "systems": electrical_systems,
                    })
                else:
                    lighting_share = 0.45
                    power_share = 0.35
                    service_share = 0.20

                    lighting_total = electrical_total * lighting_share
                    power_total = electrical_total * power_share
                    service_total = electrical_total * service_share

                    electrical_systems = [
                        {
                            "name": "High-bay lighting & controls",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(lighting_total, sf),
                            "total_cost": lighting_total,
                        },
                        {
                            "name": "Power distribution, panels, and branch circuits",
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(power_total, sf),
                            "total_cost": power_total,
                        },
                        {
                            "name": "Main electrical service and switchgear",
                            "quantity": 1,
                            "unit": "LS",
                            "unit_cost": self._safe_unit_cost(service_total, 1),
                            "total_cost": service_total,
                        },
                    ]

                    scope_items.append({
                        "trade": "Electrical",
                        "systems": electrical_systems,
                    })

            plumbing_total = float(trades.get("plumbing", 0.0) or 0.0)
            if plumbing_total > 0:
                restroom_share = 0.50
                domestic_share = 0.20
                esfr_share = 0.30

                restroom_total = plumbing_total * restroom_share
                domestic_total = plumbing_total * domestic_share
                esfr_total = plumbing_total * esfr_share

                plumbing_systems = [
                    {
                        "name": "Restroom groups (fixtures, waste, vent)",
                        "quantity": restroom_groups,
                        "unit": "EA",
                        "unit_cost": self._safe_unit_cost(restroom_total, restroom_groups),
                        "total_cost": restroom_total,
                    },
                    {
                        "name": "Domestic water, hose bibs, and roof drains",
                        "quantity": sf,
                        "unit": "SF",
                        "unit_cost": self._safe_unit_cost(domestic_total, sf),
                        "total_cost": domestic_total,
                    },
                    {
                        "name": "Fire protection – ESFR sprinkler system",
                        "quantity": sf,
                        "unit": "SF",
                        "unit_cost": self._safe_unit_cost(esfr_total, sf),
                        "total_cost": esfr_total,
                    },
                ]

                scope_items.append({
                    "trade": "Plumbing",
                    "systems": plumbing_systems,
                })

            finishes_total = float(trades.get("finishes", 0.0) or 0.0)
            if finishes_total > 0:
                if is_flex:
                    OFFICE_FINISHES_UPLIFT = 1.6
                    total_sf_value = float(sf)
                    office_area = office_sf
                    warehouse_area = warehouse_sf_for_flex if warehouse_sf_for_flex is not None else max(0.0, round(total_sf_value - office_area, 2))
                    finishes_systems: List[Dict[str, Any]] = []
                    base_unit_cost = self._safe_unit_cost(finishes_total, total_sf_value) if total_sf_value > 0 else 0.0
                    office_unit_cost = base_unit_cost * OFFICE_FINISHES_UPLIFT if office_area > 0 else 0.0
                    warehouse_unit_cost = base_unit_cost

                    if office_area > 0:
                        office_total = office_unit_cost * office_area
                        finishes_systems.append({
                            "name": "Office/showroom interior buildout allowance (conceptual)",
                            "quantity": office_area,
                            "unit": "SF",
                            "unit_cost": office_unit_cost,
                            "total_cost": office_total,
                        })
                    if warehouse_area > 0:
                        warehouse_total = warehouse_unit_cost * warehouse_area
                        finishes_systems.append({
                            "name": "Warehouse interior fit-out allowance (conceptual)",
                            "quantity": warehouse_area,
                            "unit": "SF",
                            "unit_cost": warehouse_unit_cost,
                            "total_cost": warehouse_total,
                        })
                    if finishes_systems:
                        scope_items.append({
                            "trade": "Finishes",
                            "systems": finishes_systems,
                        })
                elif is_cold_storage:
                    finishes_entries = [
                        ("Insulated panel walls & ceilings (conceptual)", 0.6),
                        ("Sanitary / food-grade finishes (conceptual)", 0.4),
                    ]
                    total_share = sum(entry[1] for entry in finishes_entries)
                    finishes_systems = []
                    for name, share in finishes_entries:
                        portion = finishes_total * (share / total_share if total_share else 0)
                        finishes_systems.append({
                            "name": name,
                            "quantity": sf,
                            "unit": "SF",
                            "unit_cost": self._safe_unit_cost(portion, sf),
                            "total_cost": portion,
                            "notes": "Conceptual / pre-design"
                        })
                    scope_items.append({
                        "trade": "Finishes",
                        "systems": finishes_systems,
                    })

        return scope_items

    def _build_ownership_bundle(
        self,
        building_config: Any,
        ownership_type: OwnershipType,
        total_project_cost: float,
        calculation_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        ownership_analysis = None
        revenue_data = None
        flex_revenue_per_sf = None

        if ownership_type in building_config.ownership_types:
            revenue_data = self.calculate_ownership_analysis(calculation_context)

            revenue_analysis_for_financing = revenue_data.get('revenue_analysis') if revenue_data else None
            if revenue_data:
                flex_metric = revenue_data.get('flex_revenue_per_sf')
                if isinstance(flex_metric, (int, float)):
                    flex_revenue_per_sf = flex_metric

            ownership_analysis = self._calculate_ownership(
                total_project_cost,
                building_config.ownership_types[ownership_type],
                revenue_analysis=revenue_analysis_for_financing
            )

            if revenue_data and 'revenue_analysis' in revenue_data:
                ownership_analysis['revenue_analysis'] = revenue_data['revenue_analysis']
                ownership_analysis['return_metrics'].update(revenue_data['return_metrics'])
                ownership_analysis['roi_analysis'] = {
                    'financial_metrics': {
                        'annual_revenue': revenue_data['revenue_analysis']['annual_revenue'],
                        'operating_margin': revenue_data['revenue_analysis']['operating_margin'],
                        'net_income': revenue_data['revenue_analysis']['net_income']
                    }
                }
                ownership_analysis['revenue_requirements'] = revenue_data.get('revenue_requirements', {})
                ownership_analysis['operational_efficiency'] = revenue_data.get('operational_efficiency', {})
                ownership_analysis['operational_metrics'] = revenue_data.get('operational_metrics', {})
                if 'sensitivity_analysis' in revenue_data:
                    ownership_analysis['sensitivity_analysis'] = revenue_data.get('sensitivity_analysis')
                if 'yield_on_cost' in revenue_data:
                    ownership_analysis['yield_on_cost'] = revenue_data.get('yield_on_cost')
                if 'market_cap_rate' in revenue_data:
                    ownership_analysis['market_cap_rate'] = revenue_data.get('market_cap_rate')
                if 'cap_rate_spread_bps' in revenue_data:
                    ownership_analysis['cap_rate_spread_bps'] = revenue_data.get('cap_rate_spread_bps')

                actual_noi = (
                    revenue_data.get('return_metrics', {}).get('estimated_annual_noi')
                    or revenue_data['revenue_analysis'].get('net_income')
                )
                debt_metrics = ownership_analysis.get('debt_metrics') or {}
                annual_debt_service = debt_metrics.get('annual_debt_service', 0)
                if actual_noi is not None:
                    recalculated_dscr = actual_noi / annual_debt_service if annual_debt_service else 0
                    debt_metrics['calculated_dscr'] = recalculated_dscr
                    debt_metrics['dscr_meets_target'] = recalculated_dscr >= debt_metrics.get('target_dscr', 0)
                    ownership_analysis['debt_metrics'] = debt_metrics
                    ownership_analysis['return_metrics']['estimated_annual_noi'] = actual_noi
                    self._log_trace("dscr_recalculated_from_revenue", {
                        'actual_noi': actual_noi,
                        'annual_debt_service': annual_debt_service,
                        'calculated_dscr': recalculated_dscr
                    })

        return {
            'ownership_analysis': ownership_analysis,
            'revenue_data': revenue_data,
            'flex_revenue_per_sf': flex_revenue_per_sf,
        }
    
    def _calculate_ownership(
        self,
        total_cost: float,
        financing_terms: Any,
        revenue_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate ownership/financing metrics with DSCR tied to revenue NOI when available."""
        
        # Calculate debt and equity
        debt_amount = total_cost * financing_terms.debt_ratio
        equity_amount = total_cost * financing_terms.equity_ratio
        philanthropy_amount = total_cost * financing_terms.philanthropy_ratio
        grants_amount = total_cost * financing_terms.grants_ratio
        
        # Calculate debt service
        annual_debt_service = debt_amount * financing_terms.debt_rate
        monthly_debt_service = annual_debt_service / 12
        
        # Prefer NOI from revenue analysis when available so DSCR matches frontend revenue panel
        noi_from_revenue = None
        if revenue_analysis and isinstance(revenue_analysis.get('net_income'), (int, float)):
            noi_from_revenue = float(revenue_analysis['net_income'])
        
        fallback_noi = total_cost * getattr(financing_terms, 'noi_percentage', 0.08)
        estimated_annual_noi = noi_from_revenue if noi_from_revenue is not None else fallback_noi
        dscr = estimated_annual_noi / annual_debt_service if annual_debt_service > 0 else 0
        
        self._log_trace("noi_derived", {
            'total_project_cost': total_cost,
            'estimated_noi': estimated_annual_noi,
            'method': 'revenue_analysis' if noi_from_revenue is not None else 'fixed_percentage'
        })

        result = {
            'financing_sources': {
                'debt_amount': debt_amount,
                'equity_amount': equity_amount,
                'philanthropy_amount': philanthropy_amount,
                'grants_amount': grants_amount,
                'total_sources': debt_amount + equity_amount + philanthropy_amount + grants_amount
            },
            'debt_metrics': {
                'debt_rate': financing_terms.debt_rate,
                'annual_debt_service': annual_debt_service,
                'monthly_debt_service': monthly_debt_service,
                'target_dscr': financing_terms.target_dscr,
                'calculated_dscr': dscr,
                'dscr_meets_target': dscr >= financing_terms.target_dscr
            },
            'return_metrics': {
                'target_roi': financing_terms.target_roi,
                'estimated_annual_noi': estimated_annual_noi,
                'cash_on_cash_return': (estimated_annual_noi - annual_debt_service) / equity_amount if equity_amount > 0 else 0
            }
        }
        
        self._log_trace("ownership_analysis_calculated", {
            'total_project_cost': total_cost,
            'debt_ratio': financing_terms.debt_ratio,
            'dscr': dscr
        })
        
        return result
    
    def _log_trace(self, step: str, data: Dict[str, Any]):
        """Log calculation steps for debugging and transparency"""
        trace_entry = {
            'step': step,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        self.calculation_trace.append(trace_entry)
        logger.debug(f"Calculation trace: {step} - {data}")
    
    def calculate_comparison(self, 
                           scenarios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate and compare multiple scenarios
        
        Args:
            scenarios: List of scenario dictionaries with calculation parameters
            
        Returns:
            Comparison results with all scenarios
        """
        results = []
        
        for i, scenario in enumerate(scenarios):
            try:
                # Convert string types to enums
                building_type = BuildingType(scenario['building_type'])
                project_class = ProjectClass(scenario.get('project_class', 'ground_up'))
                ownership_type = OwnershipType(scenario.get('ownership_type', 'for_profit'))
                
                # Calculate scenario
                result = self.calculate_project(
                    building_type=building_type,
                    subtype=scenario['subtype'],
                    square_footage=scenario['square_footage'],
                    location=scenario['location'],
                    project_class=project_class,
                    floors=scenario.get('floors', 1),
                    ownership_type=ownership_type,
                    finish_level=scenario.get('finish_level') or scenario.get('finishLevel'),
                    special_features=scenario.get('special_features', [])
                )
                
                result['scenario_name'] = scenario.get('name', f'Scenario {i+1}')
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error calculating scenario {i+1}: {str(e)}")
                results.append({
                    'scenario_name': scenario.get('name', f'Scenario {i+1}'),
                    'error': str(e)
                })
        
        # Find best/worst scenarios
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            lowest_cost = min(valid_results, key=lambda x: x['totals']['total_project_cost'])
            highest_cost = max(valid_results, key=lambda x: x['totals']['total_project_cost'])
        else:
            lowest_cost = highest_cost = None
        
        return {
            'scenarios': results,
            'summary': {
                'total_scenarios': len(scenarios),
                'successful_calculations': len(valid_results),
                'lowest_cost_scenario': lowest_cost['scenario_name'] if lowest_cost else None,
                'highest_cost_scenario': highest_cost['scenario_name'] if highest_cost else None,
                'cost_range': {
                    'min': lowest_cost['totals']['total_project_cost'] if lowest_cost else 0,
                    'max': highest_cost['totals']['total_project_cost'] if highest_cost else 0
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_ownership_analysis(self, calculations: dict) -> dict:
        """Calculate ownership and revenue analysis using master_config data"""
        
        building_type = calculations.get('building_type')
        subtype = calculations.get('subtype')
        square_footage = calculations.get('square_footage', 0)
        total_cost = calculations.get('total_cost', 0)
        construction_cost = calculations.get('subtotal', 0)
        total_project_cost = total_cost
        
        # Get the config for this building/subtype
        building_enum = self._get_building_enum(building_type)
        if not building_enum or building_enum not in MASTER_CONFIG:
            return self._empty_ownership_analysis()
        
        subtype_config = MASTER_CONFIG[building_enum].get(subtype)
        if not subtype_config:
            return self._empty_ownership_analysis()

        ownership_type_value = calculations.get('ownership_type')
        resolved_ownership_type = OwnershipType.FOR_PROFIT
        if isinstance(ownership_type_value, OwnershipType):
            resolved_ownership_type = ownership_type_value
        elif isinstance(ownership_type_value, str):
            try:
                resolved_ownership_type = OwnershipType(ownership_type_value)
            except ValueError:
                resolved_ownership_type = OwnershipType.FOR_PROFIT

        financing_terms_for_gate = None
        ownership_terms = getattr(subtype_config, 'ownership_types', None)
        if isinstance(ownership_terms, dict) and ownership_terms:
            financing_terms_for_gate = ownership_terms.get(resolved_ownership_type)
            if financing_terms_for_gate is None:
                financing_terms_for_gate = next(iter(ownership_terms.values()))
        
        scenario_value = (
            calculations.get('scenario')
            or calculations.get('scenario_key')
            or calculations.get('scenarioName')
            or calculations.get('scenarioKey')
        )
        scenario_key_normalized = (
            scenario_value.strip().lower()
            if isinstance(scenario_value, str) and scenario_value.strip()
            else None
        )
        provided_quality_factor = calculations.get('quality_factor')
        finish_level = calculations.get('finish_level')
        normalized_finish_level = finish_level.lower() if isinstance(finish_level, str) else None

        modifiers = calculations.get('modifiers') or {}
        revenue_factor = float(modifiers.get('revenue_factor', 1.0) or 1.0)
        margin_pct = float(modifiers.get('margin_pct', get_margin_pct(building_enum, subtype)))
        office_operating_expense_override = None
        office_cam_charges = None
        staffing_pct_pm = None
        staffing_pct_maintenance = None
        if building_enum == BuildingType.OFFICE:
            if getattr(subtype_config, 'operating_expense_per_sf', None) and square_footage > 0:
                office_operating_expense_override = square_footage * float(subtype_config.operating_expense_per_sf)
            if getattr(subtype_config, 'cam_charges_per_sf', None) and square_footage > 0:
                office_cam_charges = square_footage * float(subtype_config.cam_charges_per_sf)
            staffing_pct_pm = getattr(subtype_config, 'staffing_pct_property_mgmt', None)
            staffing_pct_maintenance = getattr(subtype_config, 'staffing_pct_maintenance', None)

        base_cost_psf = subtype_config.base_cost_per_sf
        if provided_quality_factor is not None:
            quality_factor = provided_quality_factor
        else:
            actual_cost_psf = construction_cost / square_footage if square_footage > 0 else base_cost_psf
            quality_factor = pow(actual_cost_psf / base_cost_psf, 0.5) if base_cost_psf > 0 else 1.0
            if quality_factor is None:
                quality_factor = 1.0

        if normalized_finish_level in ("premium", "luxury"):
            is_premium = True
        else:
            is_premium = quality_factor > 1.2

        # Industrial occupancy should follow config's base/premium rates.
        if building_enum == BuildingType.INDUSTRIAL:
            occ_base = getattr(subtype_config, "occupancy_rate_base", None)
            occ_premium = getattr(subtype_config, "occupancy_rate_premium", None)
            if is_premium and isinstance(occ_premium, (int, float)):
                occupancy_rate = float(occ_premium)
            elif isinstance(occ_base, (int, float)):
                occupancy_rate = float(occ_base)
            else:
                occupancy_rate = 0.95
        else:
            occupancy_rate = subtype_config.occupancy_rate_premium if is_premium else subtype_config.occupancy_rate_base
            if occupancy_rate is None:
                occupancy_rate = 0.85

        annual_revenue = self._calculate_revenue_by_type(
            building_enum, subtype_config, square_footage, quality_factor, occupancy_rate, calculations
        )
        
        # Apply revenue modifiers
        annual_revenue *= revenue_factor
        finish_occ_override = calculations.get('restaurant_finish_occupancy_override')
        if isinstance(finish_occ_override, (int, float)):
            occupancy_rate = float(finish_occ_override)
        finish_margin_override = calculations.get('restaurant_finish_margin_override')
        if isinstance(finish_margin_override, (int, float)):
            margin_pct = float(finish_margin_override)
        hospitality_financials = calculations.get('hospitality_financials') if building_enum == BuildingType.HOSPITALITY else None
        hospitality_expense_pct = None
        if hospitality_financials:
            hospitality_financials['annual_revenue'] = annual_revenue
            derived_occupancy = hospitality_financials.get('occupancy')
            if isinstance(derived_occupancy, (int, float)):
                occupancy_rate = derived_occupancy
            expense_override = hospitality_financials.get('expense_pct')
            if isinstance(expense_override, (int, float)):
                hospitality_expense_pct = max(0.0, min(float(expense_override), 0.95))
        
        margin_pct = margin_pct if margin_pct else get_margin_pct(building_enum, subtype)
        if hospitality_expense_pct is not None:
            margin_pct = 1 - hospitality_expense_pct
        # For industrial, enforce the configured operating margin (NNN style).
        if building_enum == BuildingType.INDUSTRIAL:
            industrial_margin = getattr(subtype_config, "operating_margin_base", None)
            if isinstance(industrial_margin, (int, float)) and industrial_margin > 0:
                margin_pct = float(industrial_margin)
        utility_ratio = float(getattr(subtype_config, 'utility_cost_ratio', 0.0) or 0.0)
        tenant_paid_utilities = (
            building_enum == BuildingType.INDUSTRIAL
            and isinstance(subtype, str)
            and subtype.strip().lower() == 'cold_storage'
            and scenario_key_normalized in {'tenant_paid_utilities', 'nnn_utilities', 'cold_storage_nnn'}
        )
        if tenant_paid_utilities and utility_ratio > 0:
            margin_pct = min(0.995, margin_pct + utility_ratio)
        self._log_trace("margin_normalized", {
            'building_type': building_enum.value,
            'subtype': subtype,
            'margin_pct': round(margin_pct, 4)
        })
        office_financials = calculations.get('office_financials') if building_enum == BuildingType.OFFICE else None
        if hospitality_financials and hospitality_expense_pct is not None:
            total_expenses = round(annual_revenue * hospitality_expense_pct, 2)
        elif office_financials:
            annual_revenue = office_financials.get('egi', annual_revenue)
            total_expenses = round(
                office_financials.get('opex', 0.0)
                + office_financials.get('ti_amort', 0.0)
                + office_financials.get('lc_amort', 0.0),
                2
            )
            derived_margin = office_financials.get('noi_margin')
            if isinstance(derived_margin, (int, float)):
                margin_pct = float(derived_margin)
            elif annual_revenue > 0:
                margin_pct = max(0.05, min(0.65, 1 - (total_expenses / annual_revenue)))
        elif office_operating_expense_override is not None:
            total_expenses = round(office_operating_expense_override, 2)
            if annual_revenue > 0:
                margin_pct = max(0.05, min(0.65, 1 - (total_expenses / annual_revenue)))
        else:
            total_expenses = round(annual_revenue * (1 - margin_pct), 2)

        net_income = round(annual_revenue - total_expenses, 2)
        if hospitality_financials:
            hospitality_financials['total_operating_expenses'] = total_expenses
            hospitality_financials['annual_noi'] = net_income
            hospitality_financials['noi_margin'] = margin_pct
            rooms_value = hospitality_financials.get('rooms')
            adr_value = hospitality_financials.get('adr')
            occupancy_value = hospitality_financials.get('occupancy')
            revpar_value = hospitality_financials.get('revpar')
            if rooms_value is not None:
                calculations['rooms'] = float(rooms_value)
                total_cost_value = (
                    calculations.get('total_project_cost')
                    or calculations.get('total_cost')
                    or total_cost
                )
                if isinstance(total_cost_value, (int, float)) and total_cost_value > 0:
                    try:
                        calculations['cost_per_key'] = float(total_cost_value) / float(rooms_value)
                    except (TypeError, ValueError, ZeroDivisionError):
                        pass
            if adr_value is not None:
                calculations['adr'] = float(adr_value)
            if occupancy_value is not None:
                calculations['occupancy'] = float(occupancy_value)
                if adr_value is not None:
                    calculations['revpar'] = float(adr_value) * float(occupancy_value)
            elif revpar_value is not None:
                calculations['revpar'] = float(revpar_value)
            key_map = {
                'rooms': 'rooms',
                'adr': 'adr',
                'occupancy': 'occupancy',
                'revpar': 'revpar',
                'cost_per_key': 'cost_per_key'
            }
            for source_key, dest_key in key_map.items():
                hosp_value = hospitality_financials.get(source_key)
                if hosp_value is None:
                    continue
                try:
                    calculations[dest_key] = float(hosp_value)
                except (TypeError, ValueError):
                    calculations[dest_key] = hosp_value
        cam_charges_value = round(office_cam_charges, 2) if office_cam_charges is not None else round(float(calculations.get('cam_charges', 0) or 0), 2)
        market_cap_rate_config = getattr(subtype_config, 'market_cap_rate', None)
        yield_on_cost = net_income / total_cost if total_cost > 0 else 0
        cap_rate_spread_bps = None
        if isinstance(market_cap_rate_config, (int, float)):
            cap_rate_spread_bps = int(round((yield_on_cost - market_cap_rate_config) * 10000))

        property_mgmt_staff_cost = None
        maintenance_staff_cost = None
        if building_enum == BuildingType.OFFICE and total_expenses > 0:
            prop_pct = float(staffing_pct_pm or 0.06)
            maint_pct = float(staffing_pct_maintenance or 0.12)
            property_mgmt_staff_cost = round(total_expenses * prop_pct, 2)
            maintenance_staff_cost = round(total_expenses * maint_pct, 2)

        efficiency_config = subtype_config
        if tenant_paid_utilities and utility_ratio > 0:
            try:
                efficiency_config = replace(subtype_config, utility_cost_ratio=0.0)
            except TypeError:
                efficiency_config = subtype_config

        operational_efficiency = self.calculate_operational_efficiency(
            revenue=annual_revenue,
            config=efficiency_config,
            subtype=subtype,
            margin_pct=margin_pct,
            total_expenses_override=total_expenses
        )
        total_expenses = operational_efficiency.get('total_expenses', total_expenses)
        operating_margin = round(margin_pct, 3) if annual_revenue > 0 else 0
        expense_ratio = round(1 - margin_pct, 3) if annual_revenue > 0 else 0
        operational_efficiency['operating_margin'] = operating_margin
        operational_efficiency['expense_ratio'] = expense_ratio
        operational_efficiency['efficiency_score'] = round(margin_pct * 100, 1) if annual_revenue > 0 else 0
        if property_mgmt_staff_cost is not None:
            operational_efficiency['property_mgmt_staffing'] = property_mgmt_staff_cost
        if maintenance_staff_cost is not None:
            operational_efficiency['maintenance_staffing'] = maintenance_staff_cost
        operational_efficiency['cam_charges'] = cam_charges_value
        
        # Standard projection period for IRR calculation
        years = 10

        property_value = 0
        market_cap_rate = None
        exit_cap_rate, discount_rate = self.get_exit_cap_and_discount_rate(building_enum)

        if net_income <= 0 or total_cost <= 0:
            npv = -total_cost
            irr = 0.0
            market_cap_rate = exit_cap_rate
        else:
            market_cap_rate = exit_cap_rate
            terminal_value = net_income / exit_cap_rate if exit_cap_rate > 0 else 0
            property_value = terminal_value
            cashflows = self.build_unlevered_cashflows_with_exit(
                total_project_cost=total_cost,
                annual_noi=net_income,
                years=years,
                exit_cap_rate=exit_cap_rate
            )
            if not cashflows:
                npv = property_value - total_cost
                irr = 0.0
            else:
                try:
                    npv = self.calculate_npv(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        years=years,
                        discount_rate=discount_rate,
                        cashflows=cashflows
                    )
                except OverflowError:
                    npv = property_value - total_cost

                try:
                    irr = self.calculate_irr(
                        initial_investment=total_cost,
                        annual_cash_flow=net_income,
                        years=years,
                        cashflows=cashflows
                    )
                except OverflowError:
                    irr = 0.0
        
        revenue_requirements = self.calculate_revenue_requirements(
            total_cost=total_cost,
            config=subtype_config,
            square_footage=square_footage,
            actual_annual_revenue=annual_revenue,
            actual_net_income=net_income,
            margin_pct=margin_pct
        )
        
        # Calculate payback period
        payback_period = round(total_cost / net_income, 1) if net_income > 0 else 999

        healthcare_profile = building_enum == BuildingType.HEALTHCARE
        healthcare_outpatient_profile = (
            healthcare_profile
            and getattr(subtype_config, "facility_metrics_profile", None) == "healthcare_outpatient"
        )
        
        # Derive units for display/per-unit metrics when not provided.
        units = calculations.get('units')
        if not units:
            units = 0
            if (
                building_enum == BuildingType.MULTIFAMILY
                and hasattr(subtype_config, 'units_per_sf')
                and square_footage > 0
            ):
                try:
                    units_estimate = float(subtype_config.units_per_sf) * float(square_footage)
                    units = max(1, int(round(units_estimate)))
                except (TypeError, ValueError):
                    units = 0
            elif healthcare_profile:
                units = self._resolve_healthcare_units(
                    subtype_config,
                    square_footage,
                    fallback_units=None,
                )
                if units:
                    calculations['units'] = units
                    fm = self._get_healthcare_financial_metrics(subtype_config)
                    unit_label_value = fm.get('primary_unit', 'units')
                    calculations.setdefault('unit_label', unit_label_value)
                    calculations.setdefault('unit_type', unit_label_value)
            if (
                units
                and healthcare_outpatient_profile
                and hasattr(subtype_config, 'financial_metrics')
                and isinstance(subtype_config.financial_metrics, dict)
            ):
                fm = subtype_config.financial_metrics
                unit_label_value = fm.get('primary_unit', 'units')
                calculations.setdefault('unit_label', unit_label_value)
                calculations.setdefault('unit_type', unit_label_value)
                total_cost_value = total_cost
                annual_revenue_value = annual_revenue
                if units > 0:
                    calculations['cost_per_unit'] = total_cost_value / units if units else 0
                    calculations['revenue_per_unit'] = annual_revenue_value / units if units else 0
        
        # Calculate display-ready operational metrics
        operational_metrics = self.calculate_operational_metrics_for_display(
            building_type=building_type,
            subtype=subtype,
            operational_efficiency=operational_efficiency,
            square_footage=square_footage,
            annual_revenue=annual_revenue,
            units=units
        )
        
        # Surface per-unit data for downstream cards (MF heavy).
        operational_metrics.setdefault('per_unit', {})
        if healthcare_profile and (not units or units <= 0):
            units = self._resolve_healthcare_units(
                subtype_config,
                square_footage,
                fallback_units=None,
            )
        operational_metrics['per_unit'].setdefault('units', units or 0)
        if units and units > 0:
            cost_per_unit = total_cost / units
            annual_revenue_per_unit = annual_revenue / units
            monthly_revenue_per_unit = annual_revenue_per_unit / 12.0
            operational_metrics['per_unit'].update({
                'cost_per_unit': round(cost_per_unit, 2),
                'annual_revenue_per_unit': round(annual_revenue_per_unit, 2),
                'monthly_revenue_per_unit': round(monthly_revenue_per_unit, 2),
            })
        
        # Underwriting refinement metrics: yield gap, break-even occupancy, sensitivity
        building_profile = get_building_profile(building_enum)
        target_yield = building_profile.get('target_yield') if building_profile else None
        yield_gap_bps = None
        if isinstance(target_yield, (int, float)):
            try:
                yield_gap_bps = int(round((target_yield - yield_on_cost) * 10000))
            except (TypeError, ValueError):
                yield_gap_bps = None

        break_even_occupancy_for_yield = None
        if (
            isinstance(target_yield, (int, float))
            and yield_on_cost > 0
            and isinstance(occupancy_rate, (int, float))
        ):
            try:
                occ_required = occupancy_rate * (target_yield / yield_on_cost)
                break_even_occupancy_for_yield = max(0.0, min(1.0, float(occ_required)))
            except (TypeError, ValueError, ZeroDivisionError):
                break_even_occupancy_for_yield = None

        sensitivity_analysis = None
        if total_cost > 0:
            try:
                base_yoc = yield_on_cost
                subtype_normalized = subtype.strip().lower() if isinstance(subtype, str) else ''
                if healthcare_outpatient_profile:
                    base_revenue = float(annual_revenue or 0)
                    base_margin = (float(net_income) / base_revenue) if base_revenue else 0.0
                    asc_mode = subtype_normalized == 'surgical_center'

                    def build_tile(label: str, scenario_yield: Optional[float]):
                        if scenario_yield is None:
                            return {'label': label, 'yield_on_cost': None, 'yield_delta': None}
                        delta = scenario_yield - base_yoc
                        return {
                            'label': label,
                            'yield_on_cost': round(scenario_yield, 4),
                            'yield_delta': round(delta, 4) if delta is not None else None,
                            'yield_delta_bps': int(round(delta * 10000)) if delta is not None else None
                        }

                    def yield_from_revenue(revenue_value: float, margin_value: float) -> Optional[float]:
                        if total_cost <= 0:
                            return None
                        noi_value = revenue_value * margin_value
                        return noi_value / total_cost if total_cost else None

                    visits_up_revenue = base_revenue * 1.05
                    visits_down_revenue = base_revenue * 0.95
                    reimbursement_up_revenue = base_revenue * 1.02
                    labor_margin = max(0.0, base_margin - 0.02)

                    visits_up_yield = yield_from_revenue(visits_up_revenue, base_margin)
                    visits_down_yield = yield_from_revenue(visits_down_revenue, base_margin)
                    reimbursement_yield = yield_from_revenue(reimbursement_up_revenue, base_margin)
                    labor_yield = yield_from_revenue(base_revenue, labor_margin)

                    sensitivity_analysis = {
                        'base': {'yield_on_cost': round(base_yoc, 4)},
                        'revenue_up_10': {
                            'yield_on_cost': round(visits_up_yield, 4) if visits_up_yield is not None else None,
                            'label': 'IF Case Volume +5%' if asc_mode else 'IF Visits / Day +5%'
                        },
                        'revenue_down_10': {
                            'yield_on_cost': round(visits_down_yield, 4) if visits_down_yield is not None else None,
                            'label': 'IF Case Volume -5%' if asc_mode else 'IF Visits / Day -5%'
                        },
                        'cost_up_10': {
                            'yield_on_cost': round(labor_yield, 4) if labor_yield is not None else None,
                            'label': 'IF Operating Costs +2 pts' if asc_mode else 'IF Labor Cost +2 pts'
                        },
                        'cost_down_10': {
                            'yield_on_cost': round(reimbursement_yield, 4) if reimbursement_yield is not None else None,
                            'label': 'IF Reimbursement +2%'
                        },
                        'scenarios': [
                            build_tile('IF Case Volume +5%' if asc_mode else 'IF Visits / Day +5%', visits_up_yield),
                            build_tile('IF Case Volume -5%' if asc_mode else 'IF Visits / Day -5%', visits_down_yield),
                            build_tile('IF Reimbursement +2%', reimbursement_yield),
                            build_tile('IF Operating Costs +2 pts' if asc_mode else 'IF Labor Cost +2 pts', labor_yield),
                        ]
                    }
                else:
                    noi_up = net_income * 1.10
                    noi_down = net_income * 0.90
                    total_cost_up = total_cost * 1.10
                    total_cost_down = total_cost * 0.90

                    sensitivity_analysis = {
                        'base': {'yield_on_cost': round(base_yoc, 4)},
                        'revenue_up_10': {
                            'yield_on_cost': round(noi_up / total_cost, 4)
                            if total_cost > 0 else None
                        },
                        'revenue_down_10': {
                            'yield_on_cost': round(noi_down / total_cost, 4)
                            if total_cost > 0 else None
                        },
                        'cost_up_10': {
                            'yield_on_cost': round(net_income / total_cost_up, 4)
                            if total_cost_up > 0 else None
                        },
                        'cost_down_10': {
                            'yield_on_cost': round(net_income / total_cost_down, 4)
                            if total_cost_down > 0 else None
                        },
                    }
            except Exception:
                sensitivity_analysis = None

        cash_on_cash_return_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0
        cap_rate_pct = round((net_income / total_cost) * 100, 2) if total_cost > 0 else 0

        target_roi = getattr(financing_terms_for_gate, "target_roi", None)
        if not isinstance(target_roi, (int, float)):
            target_roi = get_target_roi(building_enum)
        feasible = (npv >= 0) and ((cash_on_cash_return_pct / 100) >= target_roi)

        self._log_trace("feasibility_evaluated", {
            'roi': cash_on_cash_return_pct,
            'target_roi': target_roi,
            'npv': npv,
            'feasible': feasible
        })

        default_vacancy_rate = 0.0
        if isinstance(occupancy_rate, (int, float)):
            default_vacancy_rate = max(0.0, min(1.0, 1.0 - occupancy_rate))

        underwriting = calculations.get('underwriting')
        if not underwriting:
            underwriting = {
                'effective_gross_income': round(annual_revenue, 2),
                'underwritten_operating_expenses': round(total_expenses, 2),
                'underwritten_noi': round(net_income, 2),
                'vacancy_rate': default_vacancy_rate,
                'collection_loss': 0.0,
                'management_fee': 0.0,
                'capex_reserve': 0.0,
            }

        project_timeline = build_project_timeline(building_enum, None)
        construction_schedule = build_construction_schedule(building_enum, subtype=subtype)

        return {
            'revenue_analysis': {
                'annual_revenue': round(annual_revenue, 2),
                'revenue_per_sf': round(annual_revenue / square_footage, 2) if square_footage > 0 else 0,
                'operating_margin': operating_margin,
                'net_income': round(net_income, 2),
                'underwritten_noi': round(underwriting.get('underwritten_noi', net_income), 2),
                'operating_expenses': round(total_expenses, 2),
                'cam_charges': cam_charges_value,
                'occupancy_rate': occupancy_rate,
                'quality_factor': round(quality_factor, 2),
                'is_premium': is_premium,
                'revenue_factor': round(revenue_factor, 4),
                'finish_revenue_factor': round(modifiers.get('finish_revenue_factor', 1.0), 4),
                'regional_multiplier': round(modifiers.get('market_factor', 1.0), 4)
            },
            'return_metrics': {
                'estimated_annual_noi': round(net_income, 2),
                'cash_on_cash_return': cash_on_cash_return_pct,
                'cap_rate': cap_rate_pct,
                'npv': npv,
                'irr': round(irr * 100, 2),  # Convert to percentage
                'payback_period': payback_period,
                'property_value': property_value,  # Always include the value
                'market_cap_rate': market_cap_rate,  # Always include the rate
                'is_multifamily': building_enum == BuildingType.MULTIFAMILY,  # Debug flag
                'feasible': feasible
            },
            'yield_on_cost': round(yield_on_cost, 4),
            'yield_gap_bps': yield_gap_bps,
            'break_even_occupancy_for_target_yield': break_even_occupancy_for_yield,
            'market_cap_rate': round(market_cap_rate_config, 4) if isinstance(market_cap_rate_config, (int, float)) else None,
            'cap_rate_spread_bps': cap_rate_spread_bps,
            'revenue_requirements': revenue_requirements,
            'operational_efficiency': operational_efficiency,  # Keep raw data
            'operational_metrics': operational_metrics,  # ADD formatted display data
            'underwriting': underwriting,
            'sensitivity_analysis': sensitivity_analysis,
            'project_timeline': project_timeline,
            'construction_schedule': construction_schedule,
            'hospitality_financials': calculations.get('hospitality_financials'),
            'flex_revenue_per_sf': calculations.get('flex_revenue_per_sf'),
        }

    def _calculate_revenue_by_type(self, building_enum, config, square_footage, quality_factor, occupancy_rate, calculation_context: Optional[Dict[str, Any]] = None):
        """Calculate revenue based on the specific building type's metrics"""
        
        # Initialize base_revenue to avoid uninitialized variable
        base_revenue = 0
        context = calculation_context or {}
        subtype_key = (str(context.get('subtype')) if context.get('subtype') is not None else '').strip().lower()
        finish_level_value = context.get('finish_level') or context.get('finishLevel') or 'standard'
        if isinstance(finish_level_value, str):
            finish_level_value = finish_level_value.strip().lower() or 'standard'
        else:
            finish_level_value = 'standard'
        regional_ctx = context.get('regional_context') or {}
        market_factor = regional_ctx.get('market_factor')
        if not isinstance(market_factor, (int, float)):
            modifiers_ctx = context.get('modifiers') or {}
            market_factor = modifiers_ctx.get('market_factor', 1.0)
        try:
            market_factor = float(market_factor)
        except (TypeError, ValueError):
            market_factor = 1.0
        if market_factor <= 0:
            market_factor = 1.0
        
        # Healthcare - uses beds, visits, procedures, or scans
        if building_enum == BuildingType.HEALTHCARE:
            financial_metrics_cfg = self._get_healthcare_financial_metrics(config)
            facility_profile = getattr(config, "facility_metrics_profile", None)
            market_rate_type = str(financial_metrics_cfg.get("market_rate_type") or "").strip().lower()

            outpatient_capacity_revenue = None
            if facility_profile == "healthcare_outpatient" and market_rate_type == "revenue_per_visit":
                units = self._resolve_healthcare_units(config, square_footage)
                throughput_profile = self._resolve_healthcare_operational_profile(subtype_key, config)
                throughput_per_unit_day = self._coerce_number(throughput_profile.get("throughput_per_unit_day"))
                operating_days = self._coerce_number(throughput_profile.get("operating_days_per_year"))
                if operating_days is None:
                    operating_days = self._coerce_number(financial_metrics_cfg.get("operating_days_per_year"))
                if operating_days is None:
                    operating_days = self._coerce_number(getattr(config, "days_per_year", None))
                operating_days = max(1.0, float(operating_days or 260.0))
                reimbursement_per_visit = self._coerce_number(financial_metrics_cfg.get("market_rate_default"))
                if reimbursement_per_visit is None:
                    reimbursement_per_visit = self._coerce_number(getattr(config, "base_revenue_per_visit", None))

                if (
                    throughput_per_unit_day is not None
                    and throughput_per_unit_day > 0
                    and reimbursement_per_visit is not None
                    and reimbursement_per_visit > 0
                    and units > 0
                ):
                    annual_visit_capacity = float(units) * float(throughput_per_unit_day) * float(operating_days)
                    outpatient_capacity_revenue = annual_visit_capacity * float(reimbursement_per_visit)
                    context["healthcare_capacity_revenue"] = {
                        "mode": "outpatient_visit_capacity",
                        "units": units,
                        "throughput_per_unit_day": float(throughput_per_unit_day),
                        "operating_days_per_year": float(operating_days),
                        "annual_visit_capacity": annual_visit_capacity,
                        "reimbursement_per_visit": float(reimbursement_per_visit),
                    }
            if outpatient_capacity_revenue is not None:
                base_revenue = outpatient_capacity_revenue
            elif hasattr(config, 'base_revenue_per_bed_annual') and config.base_revenue_per_bed_annual and hasattr(config, 'beds_per_sf') and config.beds_per_sf:
                beds = square_footage * config.beds_per_sf
                base_revenue = beds * config.base_revenue_per_bed_annual
            elif hasattr(config, 'base_revenue_per_visit') and config.base_revenue_per_visit and hasattr(config, 'visits_per_day') and config.visits_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_visits = config.visits_per_day * config.days_per_year
                base_revenue = annual_visits * config.base_revenue_per_visit
            elif hasattr(config, 'base_revenue_per_procedure') and config.base_revenue_per_procedure and hasattr(config, 'procedures_per_day') and config.procedures_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_procedures = config.procedures_per_day * config.days_per_year
                base_revenue = annual_procedures * config.base_revenue_per_procedure
            elif hasattr(config, 'base_revenue_per_scan') and config.base_revenue_per_scan and hasattr(config, 'scans_per_day') and config.scans_per_day and hasattr(config, 'days_per_year') and config.days_per_year:
                annual_scans = config.scans_per_day * config.days_per_year
                base_revenue = annual_scans * config.base_revenue_per_scan
            elif hasattr(config, 'base_revenue_per_sf_annual') and config.base_revenue_per_sf_annual:
                base_revenue = square_footage * config.base_revenue_per_sf_annual
            else:
                # Fallback for healthcare with missing revenue config
                base_revenue = 0
            if subtype_key == 'medical_office_building':
                base_revenue_per_sf = getattr(config, 'base_revenue_per_sf_annual', None)
                operating_margin_base = getattr(config, 'operating_margin_base', None)
                annual_revenue = 0.0
                if base_revenue_per_sf and square_footage:
                    try:
                        annual_revenue = float(base_revenue_per_sf) * float(square_footage)
                    except (TypeError, ValueError):
                        annual_revenue = 0.0
                if operating_margin_base is not None and annual_revenue:
                    try:
                        noi = float(annual_revenue) * float(operating_margin_base)
                    except (TypeError, ValueError):
                        noi = 0.0
                else:
                    noi = 0.0
                adjusted_annual_revenue = annual_revenue * market_factor
                adjusted_noi = (noi * market_factor) if noi is not None else 0.0
                context['mob_revenue'] = {
                    'annual_revenue': adjusted_annual_revenue,
                    'operating_margin': operating_margin_base,
                    'net_operating_income': adjusted_noi
                }
                return adjusted_annual_revenue
        
        # Multifamily - uses monthly rent per unit
        elif building_enum == BuildingType.MULTIFAMILY:
            units = square_footage * config.units_per_sf
            monthly_rent = config.base_revenue_per_unit_monthly
            base_revenue = units * monthly_rent * 12
        
        # Hospitality - use ADR x occupancy x room count with expense profiling
        elif building_enum == BuildingType.HOSPITALITY:
            hospitality_financials = self._build_hospitality_financials(
                config=config,
                square_footage=square_footage,
                context=context
           )
            if hospitality_financials:
                context['hospitality_financials'] = hospitality_financials
                base_revenue = hospitality_financials.get('annual_room_revenue', 0)
                occupancy_rate = 1.0  # Occupancy already captured in the revenue model
            else:
                rooms = square_footage * getattr(config, 'rooms_per_sf', 0)
                base_revenue = rooms * getattr(config, 'base_revenue_per_room_annual', 0)
        
        # Office - leverage Class A profile for PGI/EGI/NOI
        elif building_enum == BuildingType.OFFICE:
            office_profile = {}
            profile_source = getattr(config, 'financial_metrics', None)
            if isinstance(profile_source, dict):
                office_profile = dict(profile_source)
            if office_profile:
                base_rent = office_profile.get('base_rent_per_sf')
                try:
                    if base_rent is not None:
                        office_profile['base_rent_per_sf'] = float(base_rent) * float(quality_factor or 1.0)
                except (TypeError, ValueError):
                    pass
                office_financials = self._build_office_financials(square_footage, office_profile)
            else:
                office_financials = {}
            if office_financials:
                context['office_financials'] = office_financials
                context['stabilized_revenue'] = office_financials.get('egi')
                context['stabilized_noi'] = office_financials.get('noi')
                context['rent_per_sf'] = office_financials.get('rent_per_sf')
                context['noi_per_sf'] = office_financials.get('noi_per_sf')
                context['operating_margin'] = office_financials.get('noi_margin')
                context['office_total_expenses'] = (
                    office_financials.get('opex', 0.0)
                    + office_financials.get('ti_amort', 0.0)
                    + office_financials.get('lc_amort', 0.0)
                )
                context['office_pgi'] = office_financials.get('pgi')
                context['office_vacancy_and_credit_loss'] = office_financials.get('vacancy_and_credit_loss')
            base_revenue = office_financials.get('egi', square_footage * getattr(config, 'base_revenue_per_sf_annual', 0))
            quality_factor = 1.0
            occupancy_rate = 1.0
        
        # Educational - uses revenue per student
        elif building_enum == BuildingType.EDUCATIONAL:
            students = square_footage * config.students_per_sf
            base_revenue = students * config.base_revenue_per_student_annual
        
        # Parking - uses revenue per space
        elif building_enum == BuildingType.PARKING:
            if hasattr(config, 'base_revenue_per_space_monthly'):
                spaces = square_footage * config.spaces_per_sf
                base_revenue = spaces * config.base_revenue_per_space_monthly * 12
            else:
                base_revenue = 0
        
        # Recreation - special handling for stadium
        elif building_enum == BuildingType.RECREATION:
            per_seat_annual = getattr(config, 'base_revenue_per_seat_annual', None)
            seats_per_sf = getattr(config, 'seats_per_sf', None)
            per_sf_annual = getattr(config, 'base_revenue_per_sf_annual', 0)
            if isinstance(per_seat_annual, (int, float)) and isinstance(seats_per_sf, (int, float)):
                seats = square_footage * float(seats_per_sf)
                base_revenue = seats * float(per_seat_annual)
            else:
                base_revenue = square_footage * float(per_sf_annual or 0)
        
        # Civic - no revenue (government funded)
        elif building_enum == BuildingType.CIVIC:
            return 0

        # Mixed-use - split-aware revenue with deterministic normalization/inference fallback.
        elif building_enum == BuildingType.MIXED_USE:
            base_psf = getattr(config, 'base_revenue_per_sf_annual', 0) or 0
            base_revenue = square_footage * float(base_psf)

            split_block = context.get("mixed_use_split")
            if not isinstance(split_block, dict):
                project_info = context.get("project_info")
                if isinstance(project_info, dict) and isinstance(project_info.get("mixed_use_split"), dict):
                    split_block = project_info.get("mixed_use_split")

            split_source = "default"
            split_value: Dict[str, float] = self._default_mixed_use_split_value(subtype_key)
            normalization_applied = False
            invalid_mix = None

            if isinstance(split_block, dict):
                split_source = (
                    split_block.get("source")
                    if isinstance(split_block.get("source"), str) and split_block.get("source").strip()
                    else split_source
                )
                candidate_source = split_block.get("value") if isinstance(split_block.get("value"), dict) else split_block
                extracted_components, fraction_notation, extraction_error = self._extract_mixed_use_split_components(
                    candidate_source if isinstance(candidate_source, dict) else {}
                )
                if extraction_error or extracted_components is None:
                    invalid_mix = {
                        "reason": extraction_error or "invalid_split_payload",
                        "source": split_source,
                    }
                else:
                    normalized_split, normalized_applied, _inference_applied, normalization_error = (
                        self._normalize_mixed_use_split_components(extracted_components, subtype_key)
                    )
                    if normalization_error or normalized_split is None:
                        invalid_mix = {
                            "reason": normalization_error or "invalid_split_payload",
                            "source": split_source,
                            "input": extracted_components,
                        }
                    else:
                        split_value = normalized_split
                        normalization_applied = bool(
                            split_block.get("normalization_applied") or normalized_applied or fraction_notation
                        )

            revenue_split_factor = self._mixed_use_weighted_factor(
                split_value,
                MIXED_USE_REVENUE_COMPONENT_MULTIPLIERS,
            )
            base_revenue = base_revenue * revenue_split_factor
            context["mixed_use_split_applied"] = {
                "value": split_value,
                "source": split_source,
                "normalization_applied": normalization_applied,
                "revenue_factor_applied": round(revenue_split_factor, 6),
                "invalid_mix": invalid_mix,
            }

        # Default - uses revenue per SF (Office, Retail, Restaurant, etc.)
        else:
            # Industrial revenue is tied directly to square footage rents (NNN).
            if building_enum == BuildingType.INDUSTRIAL:
                base_psf = getattr(config, 'base_revenue_per_sf_annual', None)
                if base_psf is None:
                    # Fallback if config missing: assume ~$12/SF EGI at 95% occ.
                    base_psf = 11.5

                if subtype_key == 'flex_space':
                    OFFICE_RENT_UPLIFT = 1.35

                    office_share_value = None
                    parsed_input_candidates: List[Dict[str, Any]] = []

                    parsed_input_direct = context.get('parsed_input') or context.get('parsedInput')
                    if isinstance(parsed_input_direct, dict):
                        parsed_input_candidates.append(parsed_input_direct)

                    request_payload = context.get('request_payload') or context.get('requestPayload')
                    if isinstance(request_payload, dict):
                        nested_parsed = request_payload.get('parsed_input') or request_payload.get('parsedInput')
                        if isinstance(nested_parsed, dict):
                            parsed_input_candidates.append(nested_parsed)

                    for candidate in parsed_input_candidates:
                        if 'office_share' in candidate:
                            office_share_value = candidate.get('office_share')
                            break

                    flex_office_share = None
                    if office_share_value is not None:
                        try:
                            flex_office_share = float(office_share_value)
                        except (TypeError, ValueError):
                            flex_office_share = None
                    if flex_office_share is not None:
                        flex_office_share = max(0.0, min(1.0, flex_office_share))
                        office_psf = base_psf * OFFICE_RENT_UPLIFT
                        blended_psf = ((1.0 - flex_office_share) * base_psf) + (flex_office_share * office_psf)
                        base_psf = blended_psf
                        context['flex_revenue_per_sf'] = blended_psf

                base_revenue = square_footage * base_psf
            else:
                base_revenue = square_footage * config.base_revenue_per_sf_annual

        # Apply finish-level revenue/margin adjustments for full-service restaurants
        if building_enum == BuildingType.RESTAURANT and subtype_key == 'full_service':
            standard_defaults = {
                "revenue_multiplier": 1.00,
                "occupancy_rate": 0.80,
                "operating_margin": 0.10,
            }
            finish_level_multipliers = getattr(config, "finish_level_multipliers", None) or {}
            standard_entry = {**standard_defaults, **(finish_level_multipliers.get("standard") or {})}
            selected_entry = {**standard_entry, **(finish_level_multipliers.get(finish_level_value) or {})}
            finish_rev_multiplier = selected_entry.get("revenue_multiplier", 1.00)
            adjusted_occupancy = selected_entry.get("occupancy_rate", 0.80)
            adjusted_margin = selected_entry.get("operating_margin")
            base_revenue *= finish_rev_multiplier
            occupancy_rate = adjusted_occupancy
            if adjusted_margin is not None:
                context['restaurant_finish_margin_override'] = adjusted_margin
            context['restaurant_finish_occupancy_override'] = occupancy_rate

        # Apply quality factor and occupancy
        # Ensure no None values
        base_revenue = (base_revenue or 0) * market_factor
        quality_factor = quality_factor or 1.0
        occupancy_rate = occupancy_rate or 0.85
        
        adjusted_revenue = base_revenue * quality_factor * occupancy_rate
        
        return adjusted_revenue

    def _build_office_financials(self, square_footage: float, office_profile: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        Build a simple Class A office underwriting model using configured profile inputs.
        Returns PGI/EGI/NOI plus the major expense components so downstream callers
        can keep NOI, rent-per-SF, and margin in sync with the UI.
        """
        if not square_footage or not office_profile:
            return {}

        try:
            sf = float(square_footage)
        except (TypeError, ValueError):
            return {}
        if sf <= 0:
            return {}

        def _to_float(name: str, default: float = 0.0) -> float:
            value = office_profile.get(name, default)
            try:
                return float(value)
            except (TypeError, ValueError):
                return default

        base_rent_per_sf = _to_float("base_rent_per_sf")
        stabilized_occupancy = _to_float("stabilized_occupancy")
        vacancy_credit_pct = _to_float("vacancy_and_credit_loss_pct")
        opex_pct = _to_float("opex_pct_of_egi")

        ti_per_sf = _to_float("ti_per_sf")
        ti_amort_years = int(office_profile.get("ti_amort_years", 10) or 10)
        lc_pct_of_lease_value = _to_float("lc_pct_of_lease_value")
        lc_amort_years = int(office_profile.get("lc_amort_years", 10) or 10)

        pgi = base_rent_per_sf * sf * stabilized_occupancy
        vacancy_and_credit_loss = vacancy_credit_pct * pgi
        egi = pgi - vacancy_and_credit_loss

        opex = opex_pct * egi
        ti_amort = 0.0
        if ti_per_sf > 0 and ti_amort_years > 0:
            ti_amort = (ti_per_sf * sf) / ti_amort_years

        lc_amort = 0.0
        if lc_pct_of_lease_value > 0 and lc_amort_years > 0:
            assumed_lease_term_years = 10
            total_commissions = lc_pct_of_lease_value * pgi * assumed_lease_term_years
            lc_amort = total_commissions / lc_amort_years

        total_expenses = opex + ti_amort + lc_amort
        noi = egi - total_expenses
        noi_margin = (noi / egi) if egi > 0 else 0.0

        rent_per_sf = (pgi / sf) if sf > 0 else 0.0
        noi_per_sf = (noi / sf) if sf > 0 else 0.0

        return {
            "pgi": pgi,
            "vacancy_and_credit_loss": vacancy_and_credit_loss,
            "egi": egi,
            "opex": opex,
            "ti_amort": ti_amort,
            "lc_amort": lc_amort,
            "noi": noi,
            "noi_margin": noi_margin,
            "rent_per_sf": rent_per_sf,
            "noi_per_sf": noi_per_sf,
        }

    def _build_hospitality_financials(self, config, square_footage: float, context: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Derive select-service hotel revenue + expense assumptions from config."""
        modifiers = context.get('modifiers') or {}

        def _first_number(*candidates) -> Optional[float]:
            for candidate in candidates:
                if candidate is None:
                    continue
                try:
                    value = float(candidate)
                except (TypeError, ValueError):
                    continue
                return value
            return None

        rooms_override = _first_number(
            context.get('rooms'),
            context.get('room_count'),
            context.get('keys'),
            modifiers.get('rooms'),
            modifiers.get('room_count'),
            modifiers.get('keys')
        )
        rooms_per_sf = getattr(config, 'rooms_per_sf', None)
        if rooms_override is not None:
            rooms = max(0.0, rooms_override)
        elif rooms_per_sf and square_footage:
            try:
                rooms = max(0.0, float(rooms_per_sf) * float(square_footage))
            except (TypeError, ValueError):
                rooms = 0.0
        else:
            rooms = 0.0

        adr_override = _first_number(
            context.get('adr'),
            context.get('average_daily_rate'),
            context.get('room_rate'),
            context.get('hotel_adr'),
            modifiers.get('adr'),
            modifiers.get('adr_override')
        )
        occupancy_override = _first_number(
            context.get('hotel_occupancy'),
            context.get('occupancy'),
            context.get('occupancy_rate_override'),
            context.get('occupancy_rate'),
            modifiers.get('occupancy'),
            modifiers.get('hotel_occupancy')
        )

        base_adr = None
        base_adr_by_market = getattr(config, 'base_adr_by_market', None)
        if isinstance(base_adr_by_market, dict):
            base_adr = (
                base_adr_by_market.get('primary')
                or next(iter(base_adr_by_market.values()), None)
            )
        base_occupancy = None
        base_occ_by_market = getattr(config, 'base_occupancy_by_market', None)
        if isinstance(base_occ_by_market, dict):
            base_occupancy = (
                base_occ_by_market.get('primary')
                or next(iter(base_occ_by_market.values()), None)
            )
        if base_occupancy is None:
            base_occupancy = getattr(config, 'occupancy_rate_base', None)

        if base_adr is None:
            annual_room_rev = getattr(config, 'base_revenue_per_room_annual', None)
            if annual_room_rev and base_occupancy:
                try:
                    base_adr = float(annual_room_rev) / (365.0 * float(base_occupancy))
                except (TypeError, ValueError, ZeroDivisionError):
                    base_adr = None

        adr = float(adr_override) if adr_override is not None else float(base_adr or 0.0)

        if occupancy_override is not None:
            occupancy = float(occupancy_override)
        else:
            occupancy = float(base_occupancy or 0.0)
        if occupancy > 1 and occupancy <= 100:
            occupancy = occupancy / 100.0
        occupancy = max(0.0, min(occupancy, 1.0))

        if rooms <= 0 or adr <= 0 or occupancy <= 0:
            annual_room_revenue = 0.0
        else:
            annual_room_revenue = rooms * adr * occupancy * 365.0

        expense_percentages = getattr(config, 'expense_percentages', None) or {}
        total_expense_pct = 0.0
        if isinstance(expense_percentages, dict):
            for value in expense_percentages.values():
                if isinstance(value, (int, float)):
                    total_expense_pct += float(value)
        if total_expense_pct <= 0:
            fallback_margin = getattr(config, 'operating_margin_base', None)
            if isinstance(fallback_margin, (int, float)) and fallback_margin > 0:
                total_expense_pct = max(0.0, 1.0 - float(fallback_margin))
        total_expense_pct = max(0.0, min(total_expense_pct, 0.95))

        total_operating_expenses = annual_room_revenue * total_expense_pct
        annual_noi = annual_room_revenue - total_operating_expenses
        noi_margin = (annual_noi / annual_room_revenue) if annual_room_revenue > 0 else 0.0

        return {
            'rooms': rooms,
            'adr': adr,
            'occupancy': occupancy,
            'annual_room_revenue': annual_room_revenue,
            'total_operating_expenses': total_operating_expenses,
            'annual_noi': annual_noi,
            'noi_margin': noi_margin,
            'expense_pct': total_expense_pct
        }

    def _get_building_enum(self, building_type_str: str):
        """Convert string building type to BuildingType enum"""
        type_map = {
            'healthcare': BuildingType.HEALTHCARE,
            'multifamily': BuildingType.MULTIFAMILY,
            'office': BuildingType.OFFICE,
            'retail': BuildingType.RETAIL,
            'restaurant': BuildingType.RESTAURANT,
            'industrial': BuildingType.INDUSTRIAL,
            'hospitality': BuildingType.HOSPITALITY,
            'educational': BuildingType.EDUCATIONAL,
            'mixed_use': BuildingType.MIXED_USE,
            'specialty': BuildingType.SPECIALTY,
            'civic': BuildingType.CIVIC,
            'recreation': BuildingType.RECREATION,
            'parking': BuildingType.PARKING
        }
        return type_map.get(building_type_str.lower())

    def _empty_ownership_analysis(self):
        """Return empty ownership analysis structure"""
        return {
            'revenue_analysis': {
                'annual_revenue': 0,
                'revenue_per_sf': 0,
                'operating_margin': 0,
                'net_income': 0,
                'occupancy_rate': 0,
                'quality_factor': 1.0,
                'is_premium': False
            },
            'return_metrics': {
                'estimated_annual_noi': 0,
                'cash_on_cash_return': 0,
                'cap_rate': 0,
                'npv': 0,
                'irr': 0,
                'payback_period': 999
            },
            'revenue_requirements': {
                'required_value': 0,
                'metric_name': 'Annual Revenue Required',
                'target_roi': 0,
                'operating_margin': 0,
                'break_even_revenue': 0,
                'required_monthly': 0
            },
            'operational_efficiency': {
                'total_expenses': 0,
                'operating_margin': 0,
                'efficiency_score': 0,
                'expense_ratio': 0
            }
        }

    def get_exit_cap_and_discount_rate(self, building_type) -> Tuple[float, float]:
        """
        Simple fallback mapping for exit cap and discount rate by building type.
        This keeps assumptions centralized until we migrate them into master_config.
        """
        exit_cap = 0.07
        discount_rate = 0.08

        try:
            bt_name = building_type.name.upper()
        except AttributeError:
            bt_name = str(building_type).upper()

        if "MULTIFAMILY" in bt_name:
            exit_cap = 0.055
            discount_rate = 0.075
        elif "INDUSTRIAL" in bt_name or "WAREHOUSE" in bt_name:
            exit_cap = 0.0675
            discount_rate = 0.08
        elif "OFFICE" in bt_name:
            # Class A office assumptions calibrated for strong urban markets.
            exit_cap = 0.0675
            discount_rate = 0.0825
        elif "HOSPITALITY" in bt_name or "HOTEL" in bt_name:
            # Select-service hotel underwriting assumptions
            exit_cap = 0.085
            discount_rate = 0.10

        return exit_cap, discount_rate

    def build_unlevered_cashflows_with_exit(
        self,
        total_project_cost: float,
        annual_noi: float,
        years: int,
        exit_cap_rate: float,
    ) -> List[float]:
        """
        Build a standard unlevered cashflow stream for IRR/NPV with a terminal value.
        Year 0: negative total project cost
        Years 1..years-1: stabilized NOI
        Year `years`: NOI + sale proceeds (NOI / exit cap)
        """
        if total_project_cost is None or annual_noi is None:
            return []

        try:
            total_cost_value = float(total_project_cost)
            noi_value = float(annual_noi)
        except (TypeError, ValueError):
            return []

        try:
            years_int = int(years)
        except (TypeError, ValueError):
            years_int = 10

        years_int = years_int if years_int > 0 else 10

        cashflows: List[float] = [-total_cost_value]

        # Intermediate years receive stabilized NOI
        for _ in range(max(years_int - 1, 0)):
            cashflows.append(noi_value)

        terminal_value = noi_value / float(exit_cap_rate) if exit_cap_rate and exit_cap_rate > 0 else 0.0
        cashflows.append(noi_value + terminal_value)
        return cashflows
    
    def calculate_npv(self, initial_investment: float, annual_cash_flow: float, 
                      years: int, discount_rate: float, cashflows: Optional[List[float]] = None) -> float:
        """Calculate Net Present Value using discount rate from config"""
        if cashflows:
            npv = 0.0
            rate = discount_rate if isinstance(discount_rate, (int, float)) else 0.0
            for year, cashflow in enumerate(cashflows):
                if year == 0:
                    npv += cashflow
                else:
                    npv += cashflow / ((1 + rate) ** year)
            return round(npv, 2)

        npv = -initial_investment
        for year in range(1, years + 1):
            npv += annual_cash_flow / ((1 + discount_rate) ** year)
        return round(npv, 2)

    def calculate_irr(self, initial_investment: float, annual_cash_flow: float, 
                      years: int = 10, cashflows: Optional[List[float]] = None) -> float:
        """Calculate Internal Rate of Return using Newton-Raphson approximation"""
        if cashflows:
            rate = 0.1
            for _ in range(50):
                npv = 0.0
                dnpv = 0.0
                for year, cashflow in enumerate(cashflows):
                    if year == 0:
                        npv += cashflow
                        continue
                    npv += cashflow / ((1 + rate) ** year)
                    dnpv -= year * cashflow / ((1 + rate) ** (year + 1))
                if abs(npv) < 0.01:
                    break
                if dnpv == 0:
                    break
                rate = rate - npv / dnpv
                if rate < -0.99:
                    rate = -0.99
                elif rate > 10:
                    rate = 10
            return round(rate, 4)

        # Simple approximation for constant cash flows
        if annual_cash_flow <= 0 or initial_investment <= 0:
            return 0.0
        
        # Newton-Raphson method for IRR
        rate = 0.1  # Initial guess
        for _ in range(20):  # Max iterations
            npv = -initial_investment
            dnpv = 0
            for year in range(1, years + 1):
                npv += annual_cash_flow / ((1 + rate) ** year)
                dnpv -= year * annual_cash_flow / ((1 + rate) ** (year + 1))
            
            if abs(npv) < 0.01:  # Converged
                break
            
            rate = rate - npv / dnpv if dnpv != 0 else rate
        
        return round(rate, 4)
    
    def calculate_irr_with_terminal_value(self, initial_investment: float, annual_cash_flow: float,
                                         terminal_value: float, years: int = 10) -> float:
        """
        Calculate IRR including terminal value (property sale) at end of investment period.
        Used for real estate investments where property value is realized at exit.
        """
        if initial_investment <= 0:
            return 0.0

        try:
            total_cost_value = float(initial_investment)
            noi_value = float(annual_cash_flow)
            terminal_value = float(terminal_value) if terminal_value is not None else 0.0
        except (TypeError, ValueError):
            return 0.0

        try:
            years_int = int(years)
        except (TypeError, ValueError):
            years_int = 10

        years_int = years_int if years_int > 0 else 10
        cashflows = [-total_cost_value]
        for _ in range(max(years_int - 1, 0)):
            cashflows.append(noi_value)
        cashflows.append(noi_value + terminal_value)

        return self.calculate_irr(
            initial_investment=total_cost_value,
            annual_cash_flow=noi_value,
            years=years_int,
            cashflows=cashflows
        )

    def calculate_revenue_requirements(
        self,
        total_cost: float,
        config,
        square_footage: float,
        actual_annual_revenue: float = 0,
        actual_net_income: float = 0,
        margin_pct: Optional[float] = None
    ) -> dict:
        """
        Calculate revenue requirements comparing actual projected returns to required returns.
        This determines true feasibility based on whether the project meets ROI targets.
        """
        
        # Target ROI (use config if available, otherwise default)
        target_roi = getattr(config, 'target_roi', 0.08)
        
        # Calculate required annual return (what investor needs)
        required_annual_return = total_cost * target_roi
        
        # Use ACTUAL projected revenue and profit from the project
        # This is what the project will actually generate
        
        # For feasibility, compare actual profit to required return
        # NOT theoretical market capacity
        if actual_net_income > 0:
            gap = actual_net_income - required_annual_return
            gap_percentage = (gap / required_annual_return) * 100 if required_annual_return > 0 else 0
            
            # Feasibility based on whether actual returns meet requirements
            if gap >= 0:
                feasibility = 'Feasible'
            elif gap >= -required_annual_return * 0.2:  # Within 20% of target
                feasibility = 'Marginal'
            else:
                feasibility = 'Not Feasible'
        else:
            gap = -required_annual_return
            gap_percentage = -100
            feasibility = 'Not Feasible'
        
        # Normalize operating margin using provided margin or config hints
        normalized_margin = margin_pct
        if normalized_margin is None and getattr(config, 'operating_margin_base', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_base')
        if normalized_margin is None and getattr(config, 'financial_metrics', None):
            normalized_margin = config.financial_metrics.get('operating_margin')
        if normalized_margin is None and getattr(config, 'operating_margin_premium', None) is not None:
            normalized_margin = getattr(config, 'operating_margin_premium')
        if normalized_margin is None:
            normalized_margin = 0.20
        normalized_margin = max(0.05, min(0.40, normalized_margin))
        operating_margin = normalized_margin
        
        # Simple payback calculation using actual net income
        simple_payback_years = round(total_cost / actual_net_income, 1) if actual_net_income > 0 else 999
        
        # ALWAYS return this exact structure
        # The Revenue Requirements card expects these exact fields
        return {
            # Core fields for Revenue Requirements card
            'required_value': round(required_annual_return, 2),
            'market_value': round(actual_annual_revenue, 2),  # Now shows actual projected revenue
            'feasibility': feasibility,
            'gap': round(gap, 2),
            'gap_percentage': round(gap_percentage, 1),
            
            # Additional fields for debugging/clarity
            'actual_net_income': round(actual_net_income, 2),
            
            # Additional display fields
            'metric_name': 'Annual Return Required',
            'required_revenue_per_sf': round(required_annual_return / square_footage, 2) if square_footage > 0 else 0,
            'actual_revenue_per_sf': round(actual_annual_revenue / square_footage, 2) if square_footage > 0 else 0,
            'target_roi': target_roi,
            'operating_margin': round(operating_margin, 3),
            'break_even_revenue': round(total_cost * 0.1, 2),  # Simple 10% of cost
            'required_monthly': round(required_annual_return / 12, 2),
            
            # Simple payback for the card
            'simple_payback_years': simple_payback_years,
            
            # Detailed feasibility for additional context
            'feasibility_detail': {
                'status': feasibility,
                'gap': round(gap, 2),
                'recommendation': self._get_revenue_feasibility_recommendation(gap, square_footage)
            }
        }

    def calculate_operational_metrics_for_display(self, building_type: str, subtype: str, 
                                                 operational_efficiency: dict, 
                                                 square_footage: float, 
                                                 annual_revenue: float, 
                                                 units: int = 0) -> dict:
        """
        Calculate display-ready operational metrics based on building type.
        Returns formatted metrics ready for frontend display.
        """
        
        # Base metrics all building types have
        operational_metrics = {
            'staffing': [],
            'revenue': {},
            'kpis': []
        }
        
        # SAFETY CHECK - Handle None/empty operational_efficiency
        if not operational_efficiency:
            return operational_metrics
        
        # SAFETY CHECK - Ensure numeric values aren't None
        annual_revenue = float(annual_revenue or 0)
        square_footage = float(square_footage or 1)  # Avoid division by zero
        units = int(units or 0)
        
        # Get data from operational_efficiency with safe defaults
        labor_cost = float(operational_efficiency.get('labor_cost', 0) or 0)
        total_expenses = float(operational_efficiency.get('total_expenses', 0) or 0)
        operating_margin = float(operational_efficiency.get('operating_margin', 0) or 0)
        efficiency_score = float(operational_efficiency.get('efficiency_score', 0) or 0)
        expense_ratio = float(operational_efficiency.get('expense_ratio', 0) or 0)
        
        # Building-type specific metrics
        if building_type == 'restaurant':
            food_cost = float(operational_efficiency.get('food_cost', 0) or 0)
            beverage_cost = float(operational_efficiency.get('beverage_cost', 0) or 0)
            
            # Calculate restaurant-specific metrics
            food_cost_ratio = (food_cost / annual_revenue) if annual_revenue > 0 else 0
            labor_cost_ratio = (labor_cost / annual_revenue) if annual_revenue > 0 else 0
            prime_cost_ratio = food_cost_ratio + labor_cost_ratio
            
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Labor % of Revenue', 'value': f'{labor_cost_ratio * 100:.1f}%'}
            ]
            
            operational_metrics['revenue'] = {
                'Food Cost': f'{food_cost_ratio * 100:.1f}%',
                'Beverage Cost': f'{(beverage_cost / annual_revenue * 100):.1f}%' if annual_revenue > 0 else '0%',
                'Labor Cost': f'{labor_cost_ratio * 100:.1f}%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Food Cost Ratio',
                    'value': f'{food_cost_ratio * 100:.0f}%',
                    'color': 'green' if (food_cost_ratio or 0) < 0.28 else 'yellow' if (food_cost_ratio or 0) < 0.32 else 'red'
                },
                {
                    'label': 'Prime Cost',
                    'value': f'{prime_cost_ratio * 100:.0f}%',
                    'color': 'green' if (prime_cost_ratio or 0) < 0.60 else 'yellow' if (prime_cost_ratio or 0) < 0.65 else 'red'
                },
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                }
            ]
            
        elif building_type == 'healthcare':
            subtype_value = (
                operational_efficiency.get('building_subtype')
                or operational_efficiency.get('subtype')
                or subtype
            )
            subtype_normalized = str(subtype_value or "").strip().lower()
            subtype_config = None
            facility_metrics_profile = None
            building_enum = self._get_building_enum(building_type)
            if building_enum:
                subtype_key = subtype_value if isinstance(subtype_value, str) else subtype_normalized
                subtype_key = subtype_key if isinstance(subtype_key, str) else str(subtype_key or "")
                subtype_config = get_building_config(building_enum, subtype_key.strip().lower())
                facility_metrics_profile = (
                    getattr(subtype_config, "facility_metrics_profile", None) if subtype_config else None
                )
            financial_metrics_cfg = self._get_healthcare_financial_metrics(subtype_config)
            operational_profile = self._resolve_healthcare_operational_profile(subtype_normalized, subtype_config)
            resolved_units = self._resolve_healthcare_units(
                subtype_config,
                square_footage,
                fallback_units=units if units > 0 else None,
            )
            unit_label = str(financial_metrics_cfg.get("primary_unit") or "units")
            revenue_per_unit_cfg = self._coerce_number(financial_metrics_cfg.get("revenue_per_unit_annual"))
            operational_metrics.setdefault("per_unit", {})
            operational_metrics["per_unit"].update(
                {
                    "units": max(1, int(resolved_units)),
                    "unit_label": unit_label,
                    "unit_type": unit_label,
                }
            )

            is_inpatient = (
                subtype_normalized in HEALTHCARE_INPATIENT_SUBTYPES
                or facility_metrics_profile != "healthcare_outpatient"
            )
            is_outpatient = not is_inpatient

            def _threshold_color(value: float, green_threshold: float, yellow_threshold: float) -> str:
                if value >= green_threshold:
                    return "green"
                if value >= yellow_threshold:
                    return "yellow"
                return "red"

            operating_days = self._coerce_number(operational_profile.get("operating_days_per_year"))
            if operating_days is None:
                operating_days = self._coerce_number(financial_metrics_cfg.get("operating_days_per_year"))
            if operating_days is None:
                operating_days = self._coerce_number(getattr(subtype_config, "days_per_year", None))
            if operating_days is None:
                operating_days = 365.0 if is_inpatient else 260.0
            operating_days = max(1.0, float(operating_days))

            throughput_per_unit_day = self._coerce_number(operational_profile.get("throughput_per_unit_day"))
            if throughput_per_unit_day is None:
                throughput_per_unit_day = 1.0 if is_inpatient else 8.0
            throughput_per_unit_day = max(0.1, float(throughput_per_unit_day))

            utilization_target = self._coerce_number(operational_profile.get("utilization_target"))
            if utilization_target is None:
                utilization_target = self._coerce_number(financial_metrics_cfg.get("target_occupancy"))
            if utilization_target is None:
                utilization_target = self._coerce_number(getattr(subtype_config, "occupancy_rate_base", None))
            if utilization_target is None:
                utilization_target = 0.85 if is_inpatient else 0.75
            utilization_target = max(0.35, min(float(utilization_target), 0.98))

            efficiency_label = str(operational_profile.get("efficiency_label") or "Operational Efficiency")
            efficiency_green = self._coerce_number(operational_profile.get("efficiency_green_threshold"))
            efficiency_yellow = self._coerce_number(operational_profile.get("efficiency_yellow_threshold"))
            efficiency_green = float(efficiency_green) if efficiency_green is not None else 84.0
            efficiency_yellow = float(efficiency_yellow) if efficiency_yellow is not None else 70.0

            if is_outpatient:
                reimbursement_per_visit = self._coerce_number(financial_metrics_cfg.get("market_rate_default"))
                if reimbursement_per_visit is None:
                    reimbursement_per_visit = self._coerce_number(getattr(subtype_config, "base_revenue_per_visit", None))
                if reimbursement_per_visit is None and revenue_per_unit_cfg is not None and resolved_units > 0:
                    reimbursement_per_visit = max(
                        1.0,
                        float(revenue_per_unit_cfg) / max(1.0, throughput_per_unit_day * operating_days),
                    )
                if reimbursement_per_visit is None:
                    reimbursement_per_visit = 120.0

                throughput_capacity_per_day = float(resolved_units) * throughput_per_unit_day
                annual_throughput = annual_revenue / float(reimbursement_per_visit) if reimbursement_per_visit > 0 else 0.0
                throughput_per_day = annual_throughput / operating_days if operating_days > 0 else 0.0
                utilization_pct = (
                    (throughput_per_day / throughput_capacity_per_day) * 100.0
                    if throughput_capacity_per_day > 0
                    else 0.0
                )
                utilization_pct = max(0.0, min(utilization_pct, 100.0))

                provider_fte_per_unit = self._coerce_number(operational_profile.get("provider_fte_per_unit"))
                if provider_fte_per_unit is None:
                    provider_fte_per_unit = 0.35
                support_fte_per_provider = self._coerce_number(operational_profile.get("support_fte_per_provider"))
                if support_fte_per_provider is None:
                    support_fte_per_provider = 1.2
                specialist_fte_per_unit = self._coerce_number(operational_profile.get("specialist_fte_per_unit"))
                specialist_fte_per_unit = float(specialist_fte_per_unit or 0.0)
                specialist_label = str(operational_profile.get("specialist_label") or "Specialty Staff FTE")

                providers = max(1, int(round(float(resolved_units) * float(provider_fte_per_unit))))
                support_staff = max(1, int(round(float(providers) * float(support_fte_per_provider))))
                specialist_staff = max(0, int(round(float(resolved_units) * specialist_fte_per_unit)))
                total_fte = providers + support_staff + specialist_staff
                staffing_intensity = float(total_fte) / float(resolved_units) if resolved_units > 0 else 0.0

                staffing_rows = [
                    {'label': 'Providers (MD/DO/NP/PA FTE)', 'value': str(providers)},
                    {'label': 'Support Staff (FTE)', 'value': str(support_staff)},
                    {'label': f'{unit_label.title()}', 'value': str(resolved_units)},
                ]
                if specialist_staff > 0:
                    staffing_rows.append({'label': specialist_label, 'value': str(specialist_staff)})
                operational_metrics['staffing'] = staffing_rows

                revenue_per_provider = annual_revenue / providers if providers else None
                revenue_per_unit = annual_revenue / resolved_units if resolved_units else None
                revenue_per_sf = annual_revenue / square_footage if square_footage else None
                labor_ratio_pct = (labor_cost / annual_revenue * 100.0) if annual_revenue else None
                revenue_block = {}
                if revenue_per_provider is not None:
                    revenue_block['Revenue per Provider'] = f'${revenue_per_provider:,.0f}'
                if revenue_per_unit is not None:
                    revenue_block[f'Revenue per {unit_label.title()}'] = f'${revenue_per_unit:,.0f}'
                if revenue_per_sf is not None:
                    revenue_block['Revenue per SF'] = f'${revenue_per_sf:,.0f}'
                if labor_ratio_pct is not None:
                    revenue_block['Labor Cost Ratio'] = f'{labor_ratio_pct:.0f}%'
                revenue_block['Operating Margin'] = f'{operating_margin * 100:.1f}%'
                operational_metrics['revenue'] = revenue_block

                throughput_label = str(operational_profile.get("throughput_label") or "Visits / Day")
                utilization_label = str(operational_profile.get("utilization_label") or "Capacity Utilization")
                throughput_efficiency = (
                    (utilization_pct / (utilization_target * 100.0)) * 100.0 if utilization_target > 0 else 0.0
                )
                throughput_efficiency = max(0.0, min(throughput_efficiency, 120.0))
                staffing_intensity_green = float(operational_profile.get("staffing_intensity_green_threshold") or 3.0)
                staffing_intensity_yellow = float(operational_profile.get("staffing_intensity_yellow_threshold") or 2.0)

                operational_metrics['kpis'] = [
                    {
                        'label': throughput_label,
                        'value': f'{throughput_per_day:,.1f}',
                        'color': 'green' if throughput_per_day >= throughput_capacity_per_day * 0.7 else 'yellow',
                    },
                    {
                        'label': utilization_label,
                        'value': f'{utilization_pct:.0f}%',
                        'color': _threshold_color(
                            utilization_pct,
                            utilization_target * 100.0,
                            utilization_target * 85.0,
                        ),
                    },
                    {
                        'label': 'Staffing Intensity',
                        'value': f'{staffing_intensity:.2f} FTE/{unit_label}',
                        'color': _threshold_color(
                            staffing_intensity,
                            staffing_intensity_green,
                            staffing_intensity_yellow,
                        ),
                    },
                    {
                        'label': efficiency_label,
                        'value': f'{throughput_efficiency:.0f}%',
                        'color': _threshold_color(
                            throughput_efficiency,
                            efficiency_green,
                            efficiency_yellow,
                        ),
                    },
                ]
            else:
                beds = max(1, resolved_units)
                revenue_per_bed = revenue_per_unit_cfg
                if revenue_per_bed is None:
                    revenue_per_bed = self._coerce_number(getattr(subtype_config, "base_revenue_per_bed_annual", None))
                observed_revenue_per_bed = (annual_revenue / beds) if beds and annual_revenue > 0 else None
                target_revenue_per_bed = (
                    annual_revenue / (beds * utilization_target)
                    if beds and annual_revenue > 0 and utilization_target > 0
                    else None
                )
                if revenue_per_bed is None:
                    if target_revenue_per_bed is not None and target_revenue_per_bed > 0:
                        revenue_per_bed = target_revenue_per_bed
                    elif observed_revenue_per_bed is not None and observed_revenue_per_bed > 0:
                        revenue_per_bed = observed_revenue_per_bed
                    else:
                        revenue_per_bed = 0.0
                else:
                    configured_revenue_per_bed = float(revenue_per_bed)
                    if target_revenue_per_bed is not None and target_revenue_per_bed > 0:
                        variance_ratio = (
                            abs(configured_revenue_per_bed - target_revenue_per_bed) / target_revenue_per_bed
                        )
                        if variance_ratio > 1.0:
                            configured_weight = 0.05
                        elif variance_ratio > 0.5:
                            configured_weight = 0.15
                        elif variance_ratio > 0.25:
                            configured_weight = 0.30
                        else:
                            configured_weight = 0.50
                        revenue_per_bed = (
                            configured_revenue_per_bed * configured_weight
                            + target_revenue_per_bed * (1.0 - configured_weight)
                        )
                    elif observed_revenue_per_bed is not None and observed_revenue_per_bed > 0:
                        revenue_per_bed = configured_revenue_per_bed * 0.6 + observed_revenue_per_bed * 0.4
                    else:
                        revenue_per_bed = configured_revenue_per_bed
                revenue_per_bed = max(float(revenue_per_bed or 0.0), 1.0)

                avg_daily_census = annual_revenue / revenue_per_bed if revenue_per_bed > 0 else 0.0
                max_plausible_census = float(beds) * 0.97
                avg_daily_census = max(0.0, min(avg_daily_census, max_plausible_census))
                occupancy_pct = (avg_daily_census / beds * 100.0) if beds > 0 else 0.0
                occupancy_pct = max(0.0, min(occupancy_pct, 100.0))

                average_los_days = self._coerce_number(operational_profile.get("average_length_of_stay_days"))
                average_los_days = max(float(average_los_days or 4.5), 1.0)
                admissions_per_day = avg_daily_census / average_los_days

                clinical_staff_per_unit = self._coerce_number(operational_profile.get("clinical_staff_fte_per_unit"))
                support_staff_per_unit = self._coerce_number(operational_profile.get("support_staff_fte_per_unit"))
                clinical_staff_per_unit = float(clinical_staff_per_unit if clinical_staff_per_unit is not None else 1.2)
                support_staff_per_unit = float(support_staff_per_unit if support_staff_per_unit is not None else 0.7)
                clinical_fte = max(1, int(round(beds * clinical_staff_per_unit)))
                support_fte = max(1, int(round(beds * support_staff_per_unit)))
                total_fte = clinical_fte + support_fte
                staffing_intensity = float(total_fte) / float(beds) if beds else 0.0

                staffing_intensity_label = str(
                    operational_profile.get("staffing_intensity_label") or "FTE per Licensed Bed"
                )
                throughput_label = str(operational_profile.get("throughput_label") or "Average Daily Census")
                utilization_label = str(operational_profile.get("utilization_label") or "Bed Occupancy")

                operational_metrics['staffing'] = [
                    {'label': 'Clinical Staff (FTE)', 'value': str(clinical_fte)},
                    {'label': 'Support Staff (FTE)', 'value': str(support_fte)},
                    {'label': f'{unit_label.title()}', 'value': str(beds)},
                ]
                operational_metrics['revenue'] = {
                    'Revenue per Employee': f'${annual_revenue / total_fte:,.0f}' if total_fte > 0 else 'N/A',
                    f'Revenue per {unit_label.title()}': f'${annual_revenue / beds:,.0f}' if beds > 0 else 'N/A',
                    'Labor Cost Ratio': f'{(labor_cost / annual_revenue * 100):.0f}%' if annual_revenue > 0 else 'N/A',
                    'Operating Margin': f'{operating_margin * 100:.1f}%'
                }

                inpatient_efficiency = (
                    (occupancy_pct / (utilization_target * 100.0)) * 100.0 if utilization_target > 0 else 0.0
                )
                inpatient_efficiency = max(0.0, min(inpatient_efficiency, 115.0))
                admissions_per_100_beds = (admissions_per_day / beds * 100.0) if beds > 0 else 0.0
                operational_metrics['kpis'] = [
                    {
                        'label': throughput_label,
                        'value': f'{avg_daily_census:,.1f}',
                        'color': 'green' if avg_daily_census >= beds * 0.75 else 'yellow',
                    },
                    {
                        'label': utilization_label,
                        'value': f'{occupancy_pct:.0f}%',
                        'color': _threshold_color(
                            occupancy_pct,
                            utilization_target * 100.0,
                            utilization_target * 85.0,
                        ),
                    },
                    {
                        'label': 'Admissions / Day',
                        'value': f'{admissions_per_day:,.1f}',
                        'color': (
                            'green'
                            if admissions_per_100_beds >= 1.8
                            else 'yellow'
                            if admissions_per_100_beds >= 1.0
                            else 'red'
                        ),
                    },
                    {
                        'label': staffing_intensity_label,
                        'value': f'{staffing_intensity:.2f}',
                        'color': 'green' if staffing_intensity >= 1.2 else 'yellow' if staffing_intensity >= 0.8 else 'red',
                    },
                    {
                        'label': efficiency_label,
                        'value': f'{inpatient_efficiency:.0f}%',
                        'color': _threshold_color(
                            inpatient_efficiency,
                            efficiency_green,
                            efficiency_yellow,
                        ),
                    },
                ]
            
        elif building_type == 'multifamily':
            # Use units if provided, otherwise estimate
            if units == 0:
                units = round(square_footage / 1000)  # Average apartment size
            
            units_per_manager = 50  # Industry standard
            maintenance_staff = max(1, round(units / 30))  # 1 per 30 units
            
            operational_metrics['staffing'] = [
                {'label': 'Units per Manager', 'value': str(units_per_manager)},
                {'label': 'Maintenance Staff', 'value': str(maintenance_staff)}
            ]
            
            operational_metrics['revenue'] = {
                'Revenue per Unit': f'${annual_revenue / units:,.0f}/yr' if units > 0 else 'N/A',
                'Average Rent': f'${annual_revenue / units / 12:,.0f}/mo' if units > 0 else 'N/A',
                'Occupancy Target': '93%',
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'NOI Margin',
                    'value': f'{operating_margin * 100:.0f}%',
                    'color': 'green' if (operating_margin or 0) > 0.60 else 'yellow' if (operating_margin or 0) > 0.50 else 'red'
                },
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.40 else 'yellow' if (expense_ratio or 0) < 0.50 else 'red'
                }
            ]
            
        elif building_type == 'office':
            property_mgmt_staffing = float(
                operational_efficiency.get('property_mgmt_staffing', operational_efficiency.get('management_fee', 0)) or 0
            )
            maintenance_staffing = float(
                operational_efficiency.get('maintenance_staffing', operational_efficiency.get('maintenance_cost', 0)) or 0
            )
            cam_charges = float(operational_efficiency.get('cam_charges', 0) or 0)
            rent_per_sf = (annual_revenue / square_footage) if square_footage > 0 else 0
            operating_expenses_per_sf = (total_expenses / square_footage) if square_footage > 0 else 0
            cam_per_sf = (cam_charges / square_footage) if square_footage > 0 else 0

            operational_metrics['staffing'] = [
                {'label': 'Property Mgmt', 'value': f'${property_mgmt_staffing:,.0f}'},
                {'label': 'Maintenance', 'value': f'${maintenance_staffing:,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Rent per SF': f'${rent_per_sf:.2f}/yr' if square_footage > 0 else 'N/A',
                'Operating Expenses': f'${total_expenses:,.0f} (${operating_expenses_per_sf:.2f}/SF)',
                'CAM Charges': (
                    f'${cam_charges:,.0f} (${cam_per_sf:.2f}/SF)' if cam_charges > 0 and square_footage > 0 else 'Included in lease'
                ),
                'Operating Margin': f'{operating_margin * 100:.1f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Efficiency',
                    'value': f'{efficiency_score:.0f}%',
                    'color': 'green' if (efficiency_score or 0) > 15 else 'yellow' if (efficiency_score or 0) > 10 else 'red'
                },
                {
                    'label': 'Expense/SF',
                    'value': f'${operating_expenses_per_sf:.2f}' if square_footage > 0 else 'N/A',
                    'color': 'yellow'
                }
            ]
            
        else:
            # Generic metrics for other building types
            operational_metrics['staffing'] = [
                {'label': 'Labor Cost', 'value': f'${labor_cost:,.0f}'},
                {'label': 'Management', 'value': f'${operational_efficiency.get("management_fee", 0):,.0f}'}
            ]
            
            operational_metrics['revenue'] = {
                'Total Expenses': f'${total_expenses:,.0f}',
                'Operating Margin': f'{operating_margin * 100:.1f}%',
                'Efficiency Score': f'{efficiency_score:.0f}%'
            }
            
            operational_metrics['kpis'] = [
                {
                    'label': 'Expense Ratio',
                    'value': f'{expense_ratio * 100:.0f}%',
                    'color': 'green' if (expense_ratio or 0) < 0.80 else 'yellow' if (expense_ratio or 0) < 0.90 else 'red'
                }
            ]
        
        return operational_metrics

    def calculate_operational_efficiency(
        self,
        revenue: float,
        config,
        subtype: str = None,
        margin_pct: Optional[float] = None,
        total_expenses_override: Optional[float] = None
    ) -> dict:
        """Calculate operational efficiency metrics from config ratios and normalized margin."""
        result = {
            'total_expenses': 0,
            'operating_margin': 0,
            'efficiency_score': 0,
            'expense_ratio': 0
        }
        
        # For manufacturing, separate facility expenses from business operations
        exclude_from_facility_opex = getattr(config, 'exclude_from_facility_opex', None)
        if not isinstance(exclude_from_facility_opex, (list, tuple)):
            exclude_from_facility_opex = []
        
        # Calculate each expense category from config
        expense_mappings = [
            ('labor_cost', 'labor_cost_ratio'),
            ('utility_cost', 'utility_cost_ratio'),
            ('maintenance_cost', 'maintenance_cost_ratio'),
            ('management_fee', 'management_fee_ratio'),
            ('insurance_cost', 'insurance_cost_ratio'),
            ('property_tax', 'property_tax_ratio'),
            ('supply_cost', 'supply_cost_ratio'),
            ('food_cost', 'food_cost_ratio'),
            ('beverage_cost', 'beverage_cost_ratio'),
            ('franchise_fee', 'franchise_fee_ratio'),
            ('equipment_lease', 'equipment_lease_ratio'),
            ('marketing_cost', 'marketing_ratio'),
            ('reserves', 'reserves_ratio'),
            ('security', 'security_ratio'),
            ('supplies', 'supplies_ratio'),
            ('janitorial', 'janitorial_ratio'),
            ('rooms_operations', 'rooms_operations_ratio'),
            ('food_beverage', 'food_beverage_ratio'),
            ('sales_marketing', 'sales_marketing_ratio'),
            ('floor_plan_interest', 'floor_plan_interest_ratio'),
            ('materials', 'materials_ratio'),
            ('raw_materials', 'raw_materials_ratio'),  # Added this mapping
            ('program_costs', 'program_costs_ratio'),
            ('equipment', 'equipment_ratio'),
            ('chemicals', 'chemicals_ratio'),
            ('event_costs', 'event_costs_ratio'),
            ('software_fees', 'software_fees_ratio'),
            ('other_expenses', 'other_expenses_ratio'),
            ('monitoring_cost', 'monitoring_cost_ratio'),  # Added for cold storage
            ('connectivity', 'connectivity_ratio'),  # Added for data center
        ]
        
        # Calculate expenses
        expense_details = {}
        raw_total_expenses = 0
        for name, attr in expense_mappings:
            # Skip business operation expenses for manufacturing
            if attr in exclude_from_facility_opex:
                continue
                
            if hasattr(config, attr):
                ratio = getattr(config, attr)
                if ratio and ratio > 0:
                    cost = revenue * ratio
                    expense_details[name] = cost
                    raw_total_expenses += cost

        # Determine target expenses based on provided overrides or margin
        if total_expenses_override is not None:
            target_total_expenses = round(total_expenses_override, 2)
        elif margin_pct is not None and revenue > 0:
            target_total_expenses = round(revenue * (1 - margin_pct), 2)
        else:
            target_total_expenses = round(raw_total_expenses, 2)

        # Scale detailed expenses to match the normalized total
        if raw_total_expenses > 0 and target_total_expenses > 0:
            scale_factor = target_total_expenses / raw_total_expenses
            scaled_sum = 0
            for key, value in expense_details.items():
                scaled_value = round(value * scale_factor, 2)
                expense_details[key] = scaled_value
                scaled_sum += scaled_value

            # Adjust for rounding drift by applying difference to the first key
            adjustment = round(target_total_expenses - scaled_sum, 2)
            if adjustment and expense_details:
                first_key = next(iter(expense_details))
                expense_details[first_key] = round(expense_details[first_key] + adjustment, 2)
        elif not expense_details and target_total_expenses > 0:
            # If no detailed breakdown but expenses exist, record as generic operating expense
            expense_details['operating_expenses'] = target_total_expenses

        result.update({key: value for key, value in expense_details.items()})
        result['total_expenses'] = target_total_expenses

        if revenue > 0:
            normalized_margin = margin_pct if margin_pct is not None else (1 - (target_total_expenses / revenue))
            normalized_margin = max(0.0, normalized_margin)
            result['operating_margin'] = round(normalized_margin, 3)
            result['efficiency_score'] = round(normalized_margin * 100, 1)
            result['expense_ratio'] = round(1 - normalized_margin, 3)
        else:
            result['operating_margin'] = round(margin_pct or 0, 3) if margin_pct is not None else 0
            result['efficiency_score'] = 0
            result['expense_ratio'] = 0
        
        return result
    
    def get_available_building_types(self) -> Dict[str, List[str]]:
        """
        Get all available building types and their subtypes
        
        Returns:
            Dictionary mapping building types to their subtypes
        """
        available = {}
        for building_type in BuildingType:
            if building_type in self.config:
                available[building_type.value] = list(self.config[building_type].keys())
        return available
    
    def get_building_details(self, building_type: BuildingType, subtype: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed configuration for a specific building type/subtype
        
        Args:
            building_type: Type from BuildingType enum
            subtype: Specific subtype
            
        Returns:
            Building configuration details or None if not found
        """
        config = get_building_config(building_type, subtype)
        if not config:
            return None
            
        # Convert to dictionary for easier consumption
        return {
            'display_name': config.display_name,
            'base_cost_per_sf': config.base_cost_per_sf,
            'cost_range': config.cost_range,
            'equipment_cost_per_sf': config.equipment_cost_per_sf,
            'typical_floors': config.typical_floors,
            'trades': asdict(config.trades),
            'soft_costs': asdict(config.soft_costs),
            'ownership_types': list(config.ownership_types.keys()),
            'special_features': list(config.special_features.keys()) if config.special_features else [],
            'nlp_keywords': config.nlp.keywords,
            'regional_multipliers': config.regional_multipliers
        }
    
    def estimate_from_description(self, 
                                 description: str,
                                 square_footage: float,
                                 location: str = "Nashville",
                                 finish_level: Optional[str] = None) -> Dict[str, Any]:
        """
        Estimate costs from a natural language description
        
        Args:
            description: Natural language project description
            square_footage: Total square footage
            location: City/location for regional multiplier
            finish_level: Optional explicit finish level override
            
        Returns:
            Cost estimate with detected building type
        """
        parsed_details = self._nlp_service.extract_project_details(description)
        detection = detect_building_type_with_method(description)

        parsed_building_type = parsed_details.get("building_type") if isinstance(parsed_details, dict) else None
        parsed_subtype = parsed_details.get("subtype") if isinstance(parsed_details, dict) else None
        parsed_alias_mapping = parsed_details.get("subtype_alias_mapping") if isinstance(parsed_details, dict) else None
        parsed_split_hint = parsed_details.get("mixed_use_split_hint") if isinstance(parsed_details, dict) else None
        parsed_detection_source = parsed_details.get("detection_source") if isinstance(parsed_details, dict) else None
        parsed_detection_conflict = (
            parsed_details.get("detection_conflict_resolution") if isinstance(parsed_details, dict) else None
        )

        building_type = None
        subtype = parsed_subtype if isinstance(parsed_subtype, str) and parsed_subtype.strip() else None
        detection_method = "nlp_service"
        detection_source = (
            parsed_detection_source
            if isinstance(parsed_detection_source, str) and parsed_detection_source.strip()
            else "nlp_service.detect_building_type_with_subtype"
        )
        detection_conflict_outcome = (
            parsed_detection_conflict
            if isinstance(parsed_detection_conflict, str) and parsed_detection_conflict.strip()
            else "none"
        )

        if isinstance(parsed_building_type, str) and parsed_building_type.strip():
            try:
                building_type = BuildingType(parsed_building_type.strip())
            except ValueError:
                building_type = None

        if detection:
            detected_type, detected_subtype, detected_method = detection
            if building_type is None:
                building_type = detected_type
                detection_conflict_outcome = "master_detector_selected"
            elif detected_type != building_type:
                if detection_conflict_outcome == "none":
                    detection_conflict_outcome = f"parser_precedence_over_{detected_type.value}"
            detection_method = detected_method
            if subtype is None and isinstance(detected_subtype, str) and detected_subtype.strip():
                subtype = detected_subtype
            elif (
                isinstance(detected_subtype, str)
                and detected_subtype.strip()
                and isinstance(subtype, str)
                and subtype.strip()
                and subtype.strip().lower() != detected_subtype.strip().lower()
            ):
                if detection_conflict_outcome == "none":
                    detection_conflict_outcome = f"parser_subtype_precedence_over_{detected_subtype.strip().lower()}"
            detection_source = f"{detection_source}+master_config.detect_building_type_with_method"

        if building_type is None or subtype is None:
            return {
                'error': 'Could not detect building type from description',
                'description': description
            }

        # Detect project class from keywords
        description_lower = description.lower()
        if 'renovation' in description_lower or 'remodel' in description_lower:
            project_class = ProjectClass.RENOVATION
        elif 'addition' in description_lower or 'expansion' in description_lower:
            project_class = ProjectClass.ADDITION
        elif 'tenant improvement' in description_lower or 'ti' in description_lower:
            project_class = ProjectClass.TENANT_IMPROVEMENT
        else:
            project_class = ProjectClass.GROUND_UP
        
        inferred_finish_level, explicit_factor = infer_finish_level(description)
        finish_source = 'default'
        finish_for_calculation: Optional[str] = None

        if finish_level:
            finish_for_calculation = finish_level
            finish_source = 'explicit'
        elif inferred_finish_level:
            finish_for_calculation = inferred_finish_level
            finish_source = 'description'

        parsed_input_overrides: Dict[str, Any] = {
            "description": description,
        }
        if isinstance(parsed_split_hint, dict):
            parsed_input_overrides["mixed_use_split_hint"] = parsed_split_hint
        if isinstance(parsed_alias_mapping, dict):
            parsed_input_overrides["subtype_alias_mapping"] = parsed_alias_mapping
        office_share = parsed_details.get("office_share") if isinstance(parsed_details, dict) else None
        if isinstance(office_share, (int, float)):
            parsed_input_overrides["office_share"] = float(office_share)

        # Calculate with detected parameters
        result = self.calculate_project(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location=location,
            project_class=project_class,
            finish_level=finish_for_calculation,
            finish_level_source=finish_source,
            parsed_input_overrides=parsed_input_overrides,
        )

        self._log_trace("nlp_detected", {
            'building_type': building_type.value,
            'subtype': subtype,
            'method': detection_method
        })

        if inferred_finish_level or explicit_factor is not None:
            self._log_trace("finish_level_inferred", {
                'from': 'description',
                'finish_level': inferred_finish_level,
                'explicit_factor': explicit_factor
            })
        if explicit_factor is not None:
            self._log_trace("finish_factor_inferred", {
                'factor': explicit_factor
            })
        
        # Add detection info
        result['detection_info'] = {
            'detected_type': building_type.value,
            'detected_subtype': subtype,
            'detected_class': project_class.value,
            'original_description': description,
            'method': detection_method,
            'detection_source': detection_source,
            'detection_conflict_outcome': detection_conflict_outcome,
            'subtype_alias_mapping': parsed_alias_mapping if isinstance(parsed_alias_mapping, dict) else None,
        }
        if isinstance(result.get('mixed_use_split'), dict):
            result['detection_info']['mixed_use_split_source'] = result['mixed_use_split'].get('source')

        return result
    
    # REMOVED DUPLICATE calculate_revenue_requirements - using the one at line 710
    # REMOVED DUPLICATE calculate_operational_efficiency - using the one at line 977
    
    def get_market_rate(self, building_type: str, subtype: str, location: str, 
                        rate_type: str, default_rate: float) -> float:
        """
        Get market-specific rates based on location.
        """
        context = resolve_location_context(location or "")
        multiplier = context.get('market_factor', context.get('multiplier', 1.0))
        
        # Apply multiplier to default rate
        adjusted_rate = default_rate * multiplier
        
        # Add some variance based on building quality/class
        if 'luxury' in subtype.lower() or 'class_a' in subtype.lower():
            adjusted_rate *= 1.15
        elif 'affordable' in subtype.lower() or 'class_c' in subtype.lower():
            adjusted_rate *= 0.75
        
        return adjusted_rate
    
    def format_financial_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the financial requirements for display.
        Add visual indicators and recommendations.
        """
        if not requirements:
            return {}
        
        # Add visual status indicators
        feasibility = requirements.get('feasibility', {}).get('status', 'Unknown')
        
        if feasibility == 'Feasible':
            requirements['overall_status'] = {
                'status': 'success',
                'message': 'Market rates support project requirements',
                'icon': '✅'
            }
        elif 'Optimization' in feasibility:
            requirements['overall_status'] = {
                'status': 'warning',
                'message': 'Consider value engineering or phasing',
                'icon': '⚠️'
            }
        else:
            requirements['overall_status'] = {
                'status': 'error',
                'message': 'Significant gap between cost and market',
                'icon': '❌'
            }
        
        return requirements
    
    def _get_revenue_feasibility_recommendation(self, gap: float, square_footage: float) -> str:
        """Generate feasibility recommendations for revenue requirements."""
        if gap >= 0:
            return "Project meets market revenue expectations"
        elif abs(gap) < 1000000:
            return "Minor revenue optimization needed through operational efficiency"
        elif abs(gap) < 5000000:
            return "Consider phased development or value engineering to reduce costs"
        else:
            return "Significant restructuring required to achieve feasibility"
    
    def _get_feasibility_recommendation(self, gap: float, unit_type: str) -> str:
        """Generate feasibility recommendations based on gap analysis."""
        if gap <= 0:
            return f"Project is financially feasible at current market rates"
        elif gap < 1000000:
            return f"Minor optimization needed: Consider value engineering or phasing"
        elif gap < 5000000:
            return f"Moderate gap: Explore alternative financing or reduce scope"
        else:
            return f"Significant feasibility gap: Major restructuring required"
    
    def _get_efficiency_rating(self, score: float) -> str:
        """Convert efficiency score to rating."""
        if score >= 90:
            return 'Excellent'
        elif score >= 75:
            return 'Good'
        elif score >= 60:
            return 'Average'
        elif score >= 45:
            return 'Below Average'
        else:
            return 'Poor'
    
    def _get_efficiency_recommendations(self, score: float) -> List[str]:
        """Generate efficiency recommendations based on score."""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider operational improvements to increase efficiency")
            recommendations.append("Review staffing levels and automation opportunities")
        elif score < 75:
            recommendations.append("Explore revenue optimization strategies")
            recommendations.append("Benchmark against industry best practices")
        elif score < 90:
            recommendations.append("Minor optimizations could improve margins")
            recommendations.append("Consider premium service offerings")
        else:
            recommendations.append("Maintain current operational excellence")
            recommendations.append("Share best practices across portfolio")
        
        return recommendations

    # REMOVED calculate_financial_requirements - was only partially implemented for hospital
    # This feature should be rebuilt properly after launch based on user needs
    
    # REMOVED DUPLICATE get_market_rate - using the one at line 1134
    
    # REMOVED assess_feasibility - was part of financial requirements feature
    # This was only partially implemented and should be rebuilt properly after launch

# Create a singleton instance
unified_engine = UnifiedEngine()
