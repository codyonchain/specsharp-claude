"""
Construction schedule configuration used by the V2 engine.
Each building type maps to the total duration and the major overlapping phases
that display on the Construction Schedule card.
"""

from typing import Dict, Any, List, Optional

from .master_config import BuildingType

PhaseConfig = Dict[str, Any]
ScheduleConfig = Dict[str, Any]


def _phases(phases: List[PhaseConfig]) -> List[PhaseConfig]:
    """
    Helper that ensures every phase config has the keys we're expecting.
    Makes the configs a little easier to read below.
    """
    normalized: List[PhaseConfig] = []
    for phase in phases:
        normalized.append({
            "id": phase["id"],
            "label": phase["label"],
            "duration": phase["duration"],
            "start_month": phase.get("start_month", 0),
            "color": phase.get("color"),
        })
    return normalized


CONSTRUCTION_SCHEDULES: Dict[BuildingType, ScheduleConfig] = {
    BuildingType.OFFICE: {
        "total_months": 27,
        "phases": _phases([
            {
                "id": "site_foundation",
                "label": "Site Foundation",
                "start_month": 0,
                "duration": 5,
                "color": "blue",
            },
            {
                "id": "structural",
                "label": "Structural",
                "start_month": 3,
                "duration": 11,
                "color": "green",
            },
            {
                "id": "exterior_envelope",
                "label": "Exterior Envelope",
                "start_month": 8,
                "duration": 9,
                "color": "orange",
            },
            {
                "id": "mep_rough",
                "label": "MEP Rough",
                "start_month": 8,
                "duration": 9,
                "color": "purple",
            },
            {
                "id": "interior_finishes",
                "label": "Interior Finishes",
                "start_month": 14,
                "duration": 12,
                "color": "pink",
            },
            {
                "id": "mep_finishes",
                "label": "MEP Finishes",
                "start_month": 17,
                "duration": 9,
                "color": "teal",
            },
        ]),
    },
    BuildingType.MULTIFAMILY: {
        "total_months": 30,
        "phases": _phases([
            {
                "id": "site_foundation",
                "label": "Site & Podium Work",
                "start_month": 0,
                "duration": 6,
                "color": "blue",
            },
            {
                "id": "structural",
                "label": "Structure & Garage",
                "start_month": 4,
                "duration": 14,
                "color": "green",
            },
            {
                "id": "exterior_envelope",
                "label": "Exterior Envelope",
                "start_month": 10,
                "duration": 10,
                "color": "orange",
            },
            {
                "id": "mep_rough",
                "label": "MEP Rough",
                "start_month": 12,
                "duration": 10,
                "color": "purple",
            },
            {
                "id": "interior_finishes",
                "label": "Interior Finishes",
                "start_month": 18,
                "duration": 12,
                "color": "pink",
            },
            {
                "id": "mep_finishes",
                "label": "Commissioning & Punch",
                "start_month": 22,
                "duration": 8,
                "color": "teal",
            },
        ]),
    },
    BuildingType.INDUSTRIAL: {
        "total_months": 18,
        "phases": _phases([
            {
                "id": "site_foundation",
                "label": "Site & Foundations",
                "start_month": 0,
                "duration": 4,
                "color": "blue",
            },
            {
                "id": "structural",
                "label": "Steel & Structure",
                "start_month": 2,
                "duration": 8,
                "color": "green",
            },
            {
                "id": "exterior_envelope",
                "label": "Skin & Envelope",
                "start_month": 6,
                "duration": 6,
                "color": "orange",
            },
            {
                "id": "mep_rough",
                "label": "MEP Rough",
                "start_month": 7,
                "duration": 6,
                "color": "purple",
            },
            {
                "id": "interior_finishes",
                "label": "Interior Fit-Out",
                "start_month": 10,
                "duration": 6,
                "color": "pink",
            },
            {
                "id": "mep_finishes",
                "label": "Systems & Commissioning",
                "start_month": 12,
                "duration": 5,
                "color": "teal",
            },
        ]),
    },
    BuildingType.RESTAURANT: {
        "total_months": 14,
        "phases": _phases([
            {
                "id": "site_foundation",
                "label": "Site Foundation & Utilities",
                "start_month": 0,
                "duration": 3,
                "color": "blue",
            },
            {
                "id": "structural",
                "label": "Structure & Shell",
                "start_month": 2,
                "duration": 5,
                "color": "green",
            },
            {
                "id": "exterior_envelope",
                "label": "Exterior & Weather Tight",
                "start_month": 6,
                "duration": 3,
                "color": "orange",
            },
            {
                "id": "mep_rough",
                "label": "Kitchen & MEP Rough-In",
                "start_month": 7,
                "duration": 4,
                "color": "purple",
            },
            {
                "id": "interior_finishes",
                "label": "Interior & Kitchen Finishes",
                "start_month": 9,
                "duration": 4,
                "color": "pink",
            },
            {
                "id": "mep_finishes",
                "label": "MEP Finishes & Commissioning",
                "start_month": 11,
                "duration": 3,
                "color": "teal",
            },
        ]),
    },
    BuildingType.HEALTHCARE: {
        "total_months": 16,
        "phases": _phases([
            {
                "id": "design_licensing",
                "label": "Design & Licensing",
                "start_month": 0,
                "duration": 3,
                "color": "blue",
            },
            {
                "id": "shell_mep_rough",
                "label": "Shell & MEP Rough-In",
                "start_month": 2,
                "duration": 5,
                "color": "green",
            },
            {
                "id": "interior_buildout",
                "label": "Interior Buildout & Finishes",
                "start_month": 7,
                "duration": 4,
                "color": "orange",
            },
            {
                "id": "equipment_low_voltage",
                "label": "Equipment & Low Voltage",
                "start_month": 10,
                "duration": 3,
                "color": "purple",
            },
            {
                "id": "inspections_commissioning",
                "label": "Inspections & Commissioning",
                "start_month": 12,
                "duration": 2,
                "color": "teal",
            },
            {
                "id": "staff_onboarding",
                "label": "Staff Onboarding & Soft Opening",
                "start_month": 13,
                "duration": 3,
                "color": "pink",
            },
        ]),
    },
}

# Building types that should reuse an existing construction schedule
CONSTRUCTION_SCHEDULE_FALLBACKS: Dict[BuildingType, BuildingType] = {
    BuildingType.RETAIL: BuildingType.OFFICE,
    BuildingType.HOSPITALITY: BuildingType.MULTIFAMILY,
    BuildingType.EDUCATIONAL: BuildingType.MULTIFAMILY,
    BuildingType.MIXED_USE: BuildingType.MULTIFAMILY,
    BuildingType.CIVIC: BuildingType.OFFICE,
    BuildingType.RECREATION: BuildingType.OFFICE,
    BuildingType.SPECIALTY: BuildingType.OFFICE,
    BuildingType.PARKING: BuildingType.INDUSTRIAL,
}


CONSTRUCTION_SUBTYPE_SCHEDULES: Dict[BuildingType, Dict[str, ScheduleConfig]] = {
    BuildingType.INDUSTRIAL: {
        "warehouse": {
            "total_months": 16,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site & Foundations",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Steel & Structure",
                    "start_month": 2,
                    "duration": 7,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Skin & Envelope",
                    "start_month": 5,
                    "duration": 5,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough",
                    "start_month": 6,
                    "duration": 5,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Interior Fit-Out",
                    "start_month": 9,
                    "duration": 5,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems & Commissioning",
                    "start_month": 11,
                    "duration": 4,
                    "color": "teal",
                },
            ]),
        },
        "distribution_center": {
            "total_months": 20,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site, Courts & Foundations",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Steel & Structural Frame",
                    "start_month": 2,
                    "duration": 9,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope & Dock Package",
                    "start_month": 6,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough",
                    "start_month": 7,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Sortation & Interior Fit-Out",
                    "start_month": 10,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Integration & Commissioning",
                    "start_month": 13,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
        "manufacturing": {
            "total_months": 24,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site, Foundations & Process Bases",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structural Frame & Crane Supports",
                    "start_month": 3,
                    "duration": 11,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope & Utility Entry",
                    "start_month": 8,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Process MEP Rough",
                    "start_month": 8,
                    "duration": 10,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Production Fit-Out",
                    "start_month": 14,
                    "duration": 8,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Startup, Testing & Commissioning",
                    "start_month": 17,
                    "duration": 7,
                    "color": "teal",
                },
            ]),
        },
        "flex_space": {
            "total_months": 19,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site & Foundations",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Shell Structure",
                    "start_month": 2,
                    "duration": 8,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope & Storefront Openings",
                    "start_month": 6,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Mixed-Use MEP Rough",
                    "start_month": 7,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Office/Showroom Interior Fit-Out",
                    "start_month": 10,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Tenant Commissioning",
                    "start_month": 13,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
        "cold_storage": {
            "total_months": 22,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site, Insulated Slab & Foundations",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structural Shell",
                    "start_month": 2,
                    "duration": 9,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope & Insulated Panels",
                    "start_month": 7,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Refrigeration & MEP Rough",
                    "start_month": 8,
                    "duration": 9,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Cold Room Build-Out",
                    "start_month": 13,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Balancing & Commissioning",
                    "start_month": 16,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
    },
    BuildingType.MULTIFAMILY: {
        "market_rate_apartments": {
            "total_months": 28,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site & Podium Work",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure & Garage",
                    "start_month": 4,
                    "duration": 13,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior Envelope",
                    "start_month": 9,
                    "duration": 9,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough",
                    "start_month": 11,
                    "duration": 9,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Interior Finishes",
                    "start_month": 16,
                    "duration": 11,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Commissioning & Punch",
                    "start_month": 20,
                    "duration": 8,
                    "color": "teal",
                },
            ]),
        },
        "luxury_apartments": {
            "total_months": 34,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site, Podium & Amenity Bases",
                    "start_month": 0,
                    "duration": 7,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure, Garage & Amenity Decks",
                    "start_month": 4,
                    "duration": 16,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior Envelope",
                    "start_month": 11,
                    "duration": 11,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough",
                    "start_month": 13,
                    "duration": 11,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Premium Interiors & Amenities",
                    "start_month": 20,
                    "duration": 13,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Commissioning & Turnover",
                    "start_month": 24,
                    "duration": 10,
                    "color": "teal",
                },
            ]),
        },
        "affordable_housing": {
            "total_months": 26,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site & Foundations",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure & Core",
                    "start_month": 3,
                    "duration": 12,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior Envelope",
                    "start_month": 8,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough",
                    "start_month": 10,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Interior Finishes",
                    "start_month": 15,
                    "duration": 10,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Commissioning & Punch",
                    "start_month": 19,
                    "duration": 7,
                    "color": "teal",
                },
            ]),
        },
    },
    BuildingType.RESTAURANT: {
        "quick_service": {
            "total_months": 12,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Foundation & Utilities",
                    "start_month": 0,
                    "duration": 2,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Shell & Core",
                    "start_month": 1,
                    "duration": 4,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Storefront & Weather Tight",
                    "start_month": 4,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Kitchen/MEP Rough-In",
                    "start_month": 5,
                    "duration": 3,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Interior Fit-Out & Finishes",
                    "start_month": 7,
                    "duration": 3,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Equipment Startup & Commissioning",
                    "start_month": 9,
                    "duration": 3,
                    "color": "teal",
                },
            ]),
        },
        "full_service": {
            "total_months": 15,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Foundation & Utilities",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure & Shell",
                    "start_month": 2,
                    "duration": 5,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior & Storefront",
                    "start_month": 6,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Kitchen & Dining MEP Rough-In",
                    "start_month": 6,
                    "duration": 5,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Dining Room & Kitchen Finishes",
                    "start_month": 9,
                    "duration": 5,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Final Trim & Commissioning",
                    "start_month": 12,
                    "duration": 3,
                    "color": "teal",
                },
            ]),
        },
        "fine_dining": {
            "total_months": 17,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Foundation & Utilities",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Shell, Structure & Specialty Framing",
                    "start_month": 2,
                    "duration": 6,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Architectural Exterior Package",
                    "start_month": 7,
                    "duration": 4,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Advanced Kitchen/MEP Rough-In",
                    "start_month": 7,
                    "duration": 6,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Premium Interior & Kitchen Finishes",
                    "start_month": 10,
                    "duration": 6,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Commissioning & Fine-Tuning",
                    "start_month": 14,
                    "duration": 3,
                    "color": "teal",
                },
            ]),
        },
        "cafe": {
            "total_months": 11,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Foundation & Utilities",
                    "start_month": 0,
                    "duration": 2,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Shell & Storefront Structure",
                    "start_month": 1,
                    "duration": 4,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior Envelope",
                    "start_month": 4,
                    "duration": 2,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Espresso/MEP Rough-In",
                    "start_month": 4,
                    "duration": 3,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Cafe Interior Finishes",
                    "start_month": 6,
                    "duration": 3,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Startup & Commissioning",
                    "start_month": 8,
                    "duration": 3,
                    "color": "teal",
                },
            ]),
        },
        "bar_tavern": {
            "total_months": 16,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Foundation & Utilities",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure, Shell & Stage Support",
                    "start_month": 2,
                    "duration": 5,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Exterior & Acoustic Envelope",
                    "start_month": 6,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Bar/AV/MEP Rough-In",
                    "start_month": 6,
                    "duration": 5,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Bar Build-Out & Interior Finishes",
                    "start_month": 9,
                    "duration": 5,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Life-Safety Testing & Commissioning",
                    "start_month": 12,
                    "duration": 4,
                    "color": "teal",
                },
            ]),
        },
    },
}


def _normalize_building_type(building_type: BuildingType) -> BuildingType:
    if isinstance(building_type, BuildingType):
        return building_type
    try:
        return BuildingType(str(building_type))
    except (ValueError, TypeError):
        return BuildingType.OFFICE


def _resolve_building_type_schedule(building_type: BuildingType) -> ScheduleConfig:
    schedule_config = CONSTRUCTION_SCHEDULES.get(building_type)
    if not schedule_config:
        fallback_type = CONSTRUCTION_SCHEDULE_FALLBACKS.get(building_type)
        if fallback_type:
            schedule_config = CONSTRUCTION_SCHEDULES.get(fallback_type)
    if not schedule_config:
        schedule_config = CONSTRUCTION_SCHEDULES.get(BuildingType.OFFICE, {})
    return schedule_config


def build_construction_schedule(
    building_type: BuildingType,
    subtype: Optional[str] = None,
) -> Dict[str, Any]:
    resolved_building_type = _normalize_building_type(building_type)
    subtype_key = subtype.strip().lower() if isinstance(subtype, str) and subtype.strip() else None

    schedule_source = "building_type"
    resolved_subtype = None

    schedule_config = None
    subtype_overrides = CONSTRUCTION_SUBTYPE_SCHEDULES.get(resolved_building_type)
    if subtype_key and isinstance(subtype_overrides, dict):
        schedule_config = subtype_overrides.get(subtype_key)
        if schedule_config:
            schedule_source = "subtype"
            resolved_subtype = subtype_key

    if not schedule_config:
        schedule_config = _resolve_building_type_schedule(resolved_building_type)

    total_months = int(schedule_config.get("total_months", 0) or 0)
    phases_payload: List[Dict[str, Any]] = []
    for phase in schedule_config.get("phases", []):
        start_month = int(phase.get("start_month", 0) or 0)
        duration = int(phase.get("duration", 0) or 0)
        end_month = start_month + duration
        if total_months:
            end_month = min(end_month, total_months)
        phase_payload = {
            "id": phase.get("id"),
            "label": phase.get("label"),
            "start_month": start_month,
            "duration_months": duration,
            "end_month": end_month,
        }
        color = phase.get("color")
        if color:
            phase_payload["color"] = color
        phases_payload.append(phase_payload)

    return {
        "building_type": resolved_building_type.value,
        "subtype": resolved_subtype,
        "schedule_source": schedule_source,
        "total_months": total_months,
        "phases": phases_payload,
    }
