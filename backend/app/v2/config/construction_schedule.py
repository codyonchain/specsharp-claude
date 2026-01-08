"""
Construction schedule configuration used by the V2 engine.
Each building type maps to the total duration and the major overlapping phases
that display on the Construction Schedule card.
"""

from typing import Dict, Any, List

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
