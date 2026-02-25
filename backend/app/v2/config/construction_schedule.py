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
    BuildingType.RETAIL: {
        "shopping_center": {
            "total_months": 20,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Pad Prep + Utility Loops",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Inline Shell + Canopy Structure",
                    "start_month": 2,
                    "duration": 7,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Storefront Envelope + Signage Raceway",
                    "start_month": 6,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Tenant Utility Rough-In + Metering",
                    "start_month": 6,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Inline Fit-Out + Common-Area Finishes",
                    "start_month": 11,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Balancing + Tenant Turnover",
                    "start_month": 14,
                    "duration": 5,
                    "color": "teal",
                },
            ]),
        },
        "big_box": {
            "total_months": 18,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Mass Grading + Heavy Slab Prep",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Long-Span Steel + Dock Aprons",
                    "start_month": 1,
                    "duration": 7,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Facade Panels + Entry Canopies",
                    "start_month": 5,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "High-Amp Service + Back-of-House MEP",
                    "start_month": 5,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Sales Floor + Front-End Buildout",
                    "start_month": 10,
                    "duration": 6,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Refrigeration Startup + Commissioning",
                    "start_month": 13,
                    "duration": 4,
                    "color": "teal",
                },
            ]),
        },
    },
    BuildingType.OFFICE: {
        "class_a": {
            "total_months": 30,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Prep + Deep Foundations",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "High-Rise Core + Structural Frame",
                    "start_month": 3,
                    "duration": 12,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Curtainwall + Exterior Performance Envelope",
                    "start_month": 9,
                    "duration": 10,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Central Plant + Vertical MEP Rough-In",
                    "start_month": 9,
                    "duration": 10,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Premium Tenant Buildout + Amenity Floors",
                    "start_month": 16,
                    "duration": 12,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Controls Integration + Commissioning",
                    "start_month": 20,
                    "duration": 9,
                    "color": "teal",
                },
            ]),
        },
        "class_b": {
            "total_months": 24,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Selective Demolition + Site Corrections",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Core Rehabilitation + Framing Repairs",
                    "start_month": 2,
                    "duration": 9,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope Renewal + Weatherproofing",
                    "start_month": 7,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Systems Replacement + Distribution Rework",
                    "start_month": 7,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Tenant Turns + Common Area Refresh",
                    "start_month": 12,
                    "duration": 10,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Testing, Balancing + Re-Occupancy Turnover",
                    "start_month": 16,
                    "duration": 7,
                    "color": "teal",
                },
            ]),
        },
    },
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
    BuildingType.HEALTHCARE: {
        "surgical_center": {
            "total_months": 15,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Design, Licensing & Infection-Control Planning",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "OR Shell + MEP Rough-In",
                    "start_month": 2,
                    "duration": 5,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Sterile Core + Recovery Buildout",
                    "start_month": 6,
                    "duration": 4,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Procedure Equipment + Controls Integration",
                    "start_month": 9,
                    "duration": 3,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Life-Safety Testing + Commissioning",
                    "start_month": 11,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Clinical Dry Runs + Opening Readiness",
                    "start_month": 12,
                    "duration": 3,
                    "color": "pink",
                },
            ]),
        },
        "imaging_center": {
            "total_months": 17,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Design, OEM Coordination & Licensing",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Shielding Prep + Power Rough-In",
                    "start_month": 3,
                    "duration": 5,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Imaging Suite Buildout",
                    "start_month": 7,
                    "duration": 4,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Magnet/CT Install + Low-Voltage Integration",
                    "start_month": 10,
                    "duration": 4,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Radiation + Systems Commissioning",
                    "start_month": 13,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Clinical Calibration + Launch",
                    "start_month": 14,
                    "duration": 3,
                    "color": "pink",
                },
            ]),
        },
        "urgent_care": {
            "total_months": 13,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Design + Permit Coordination",
                    "start_month": 0,
                    "duration": 2,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Shell Fit + MEP Rough-In",
                    "start_month": 1,
                    "duration": 4,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Exam/Triage Buildout",
                    "start_month": 5,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Point-of-Care Equipment + IT",
                    "start_month": 7,
                    "duration": 2,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "AHJ Inspections + Startup",
                    "start_month": 9,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Staff Training + Go-Live",
                    "start_month": 10,
                    "duration": 3,
                    "color": "pink",
                },
            ]),
        },
        "outpatient_clinic": {
            "total_months": 14,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Program Validation + Permitting",
                    "start_month": 0,
                    "duration": 2,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Base Build + MEP Rough-In",
                    "start_month": 1,
                    "duration": 4,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Exam Rooms + Support Spaces",
                    "start_month": 5,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Clinical Equipment + IT/Low Voltage",
                    "start_month": 7,
                    "duration": 3,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Commissioning + Compliance Signoff",
                    "start_month": 10,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Provider Onboarding + Opening",
                    "start_month": 11,
                    "duration": 3,
                    "color": "pink",
                },
            ]),
        },
        "medical_office_building": {
            "total_months": 18,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Design, Entitlements + Permits",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Shell + Vertical MEP Backbone",
                    "start_month": 2,
                    "duration": 6,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Common Areas + Tenant-Ready Buildout",
                    "start_month": 7,
                    "duration": 4,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Tenant Utility Readiness + Low Voltage",
                    "start_month": 10,
                    "duration": 4,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Systems Testing + Turnover",
                    "start_month": 13,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Tenant Mobilization + Occupancy",
                    "start_month": 14,
                    "duration": 4,
                    "color": "pink",
                },
            ]),
        },
        "dental_office": {
            "total_months": 12,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Design + Dental Board Compliance",
                    "start_month": 0,
                    "duration": 2,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Shell Prep + Plumbing/Med-Gas Rough-In",
                    "start_month": 1,
                    "duration": 3,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Operatory + Sterilization Buildout",
                    "start_month": 4,
                    "duration": 3,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Chairside Equipment + Imaging Integration",
                    "start_month": 6,
                    "duration": 2,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Life-Safety + Equipment Startup",
                    "start_month": 8,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Clinical Onboarding + Opening",
                    "start_month": 9,
                    "duration": 3,
                    "color": "pink",
                },
            ]),
        },
        "hospital": {
            "total_months": 30,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Planning, Licensing + Program Approvals",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Tower/Shell + Critical MEP Rough-In",
                    "start_month": 4,
                    "duration": 10,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Inpatient + Procedural Interior Buildout",
                    "start_month": 11,
                    "duration": 9,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Clinical Equipment + Integrated Low Voltage",
                    "start_month": 17,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Integrated Systems Commissioning",
                    "start_month": 23,
                    "duration": 4,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Operational Readiness + Service Activation",
                    "start_month": 25,
                    "duration": 5,
                    "color": "pink",
                },
            ]),
        },
        "medical_center": {
            "total_months": 24,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Program Planning + Agency Coordination",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Core/Shell + Service-Line MEP Rough-In",
                    "start_month": 3,
                    "duration": 8,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Clinical Pod Buildout",
                    "start_month": 9,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Specialty Equipment + IT Integration",
                    "start_month": 14,
                    "duration": 6,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Commissioning + Regulatory Signoff",
                    "start_month": 19,
                    "duration": 3,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Service-Line Activation",
                    "start_month": 20,
                    "duration": 4,
                    "color": "pink",
                },
            ]),
        },
        "nursing_home": {
            "total_months": 20,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Care Model Planning + Permit Review",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Residential Shell + MEP Rough-In",
                    "start_month": 2,
                    "duration": 6,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Resident Rooms + Support Buildout",
                    "start_month": 7,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Nurse Call + Resident Safety Systems",
                    "start_month": 11,
                    "duration": 4,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Life-Safety + State Inspection",
                    "start_month": 15,
                    "duration": 3,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Care Team Readiness + Occupancy",
                    "start_month": 16,
                    "duration": 4,
                    "color": "pink",
                },
            ]),
        },
        "rehabilitation": {
            "total_months": 16,
            "phases": _phases([
                {
                    "id": "design_licensing",
                    "label": "Program + Licensing Coordination",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "shell_mep_rough",
                    "label": "Shell Prep + Therapy MEP Rough-In",
                    "start_month": 2,
                    "duration": 5,
                    "color": "green",
                },
                {
                    "id": "interior_buildout",
                    "label": "Therapy Gym + Clinical Buildout",
                    "start_month": 6,
                    "duration": 4,
                    "color": "orange",
                },
                {
                    "id": "equipment_low_voltage",
                    "label": "Therapy Equipment + Clinical IT",
                    "start_month": 9,
                    "duration": 3,
                    "color": "purple",
                },
                {
                    "id": "inspections_commissioning",
                    "label": "Commissioning + Clinical Validation",
                    "start_month": 12,
                    "duration": 2,
                    "color": "teal",
                },
                {
                    "id": "staff_onboarding",
                    "label": "Therapist Onboarding + Opening",
                    "start_month": 13,
                    "duration": 3,
                    "color": "pink",
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
    BuildingType.HOSPITALITY: {
        "limited_service_hotel": {
            "total_months": 24,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Utilities & Foundations",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Podium & Guestroom Structure",
                    "start_month": 2,
                    "duration": 10,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope & Weather Tight",
                    "start_month": 7,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough-In",
                    "start_month": 8,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Guestroom & Public Area Finishes",
                    "start_month": 13,
                    "duration": 9,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "FF&E Install & Commissioning",
                    "start_month": 17,
                    "duration": 7,
                    "color": "teal",
                },
            ]),
        },
        "full_service_hotel": {
            "total_months": 32,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site, Podium & Foundations",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structure, Core & Towers",
                    "start_month": 4,
                    "duration": 14,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope, Facade & Roofing",
                    "start_month": 10,
                    "duration": 10,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "MEP Rough & Back-of-House Systems",
                    "start_month": 12,
                    "duration": 11,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Guestroom, F&B & Amenity Finishes",
                    "start_month": 19,
                    "duration": 11,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Start-Up & Opening Readiness",
                    "start_month": 24,
                    "duration": 8,
                    "color": "teal",
                },
            ]),
        },
    },
    BuildingType.EDUCATIONAL: {
        "elementary_school": {
            "total_months": 22,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Utilities + Foundations",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Classroom Wings + Commons Structure",
                    "start_month": 2,
                    "duration": 8,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Entry Canopies",
                    "start_month": 6,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Ventilation + Life-Safety Rough-In",
                    "start_month": 6,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Classroom + Shared Space Finishes",
                    "start_month": 11,
                    "duration": 8,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Startup + District Turnover",
                    "start_month": 15,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
        "middle_school": {
            "total_months": 24,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site Prep + Foundations",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Academic Blocks + Lab Wing Structure",
                    "start_month": 2,
                    "duration": 9,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Activity Core Weatherproofing",
                    "start_month": 7,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "STEM/Media Power + HVAC Rough-In",
                    "start_month": 7,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Learning Commons + Lab Fit-Out",
                    "start_month": 12,
                    "duration": 8,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Balancing + Occupancy Readiness",
                    "start_month": 16,
                    "duration": 7,
                    "color": "teal",
                },
            ]),
        },
        "high_school": {
            "total_months": 28,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Athletic Foundation Program",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Academic Core + Athletics/Arts Structure",
                    "start_month": 3,
                    "duration": 11,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Stadium/Field House Interfaces",
                    "start_month": 8,
                    "duration": 9,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Lab, Performing-Arts + Athletic MEP Rough-In",
                    "start_month": 9,
                    "duration": 10,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Academic + Program Specialty Fit-Out",
                    "start_month": 15,
                    "duration": 10,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Commissioning + Program Turnover",
                    "start_month": 19,
                    "duration": 8,
                    "color": "teal",
                },
            ]),
        },
        "university": {
            "total_months": 34,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Campus Utilities + Deep Foundations",
                    "start_month": 0,
                    "duration": 6,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Research/Lecture Structure + Core",
                    "start_month": 3,
                    "duration": 14,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "High-Performance Envelope + Roof Systems",
                    "start_month": 10,
                    "duration": 10,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Research MEP + Controls Backbone Rough-In",
                    "start_month": 10,
                    "duration": 13,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Research + Learning Space Build-Out",
                    "start_month": 18,
                    "duration": 11,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Validation, Commissioning + Occupancy Readiness",
                    "start_month": 23,
                    "duration": 10,
                    "color": "teal",
                },
            ]),
        },
        "community_college": {
            "total_months": 20,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Utility/Floor Slab Prep",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Instructional Blocks + Vocational Bays",
                    "start_month": 2,
                    "duration": 7,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Student Entry Package",
                    "start_month": 6,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Vocational/Training MEP Rough-In",
                    "start_month": 6,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Instructional + Workforce Space Fit-Out",
                    "start_month": 10,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Startup + Partner Program Turnover",
                    "start_month": 13,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
    },
    BuildingType.SPECIALTY: {
        "data_center": {
            "total_months": 26,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Utility Trunking",
                    "start_month": 0,
                    "duration": 5,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structural Shell + Raised Floor Bases",
                    "start_month": 3,
                    "duration": 10,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Security Hardening",
                    "start_month": 8,
                    "duration": 8,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Power Train + Cooling Rough-In",
                    "start_month": 8,
                    "duration": 12,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "White Space + Support Build-Out",
                    "start_month": 14,
                    "duration": 9,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Integrated Systems Commissioning",
                    "start_month": 18,
                    "duration": 8,
                    "color": "teal",
                },
            ]),
        },
        "laboratory": {
            "total_months": 22,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Core Utilities",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Structural Frame + Vibration Control",
                    "start_month": 2,
                    "duration": 9,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Pressure Boundary",
                    "start_month": 6,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Lab MEP + Exhaust Rough-In",
                    "start_month": 7,
                    "duration": 10,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Casework + Controlled Surfaces",
                    "start_month": 12,
                    "duration": 8,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Validation + Certification",
                    "start_month": 16,
                    "duration": 6,
                    "color": "teal",
                },
            ]),
        },
        "self_storage": {
            "total_months": 15,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Slab Program",
                    "start_month": 0,
                    "duration": 3,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Frame + Unit Stackout",
                    "start_month": 1,
                    "duration": 6,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Roll-Up Doors",
                    "start_month": 4,
                    "duration": 5,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Security + Climate Rough-In",
                    "start_month": 5,
                    "duration": 5,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Interior Unit Fit-Out",
                    "start_month": 8,
                    "duration": 5,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Systems Startup + Access Testing",
                    "start_month": 11,
                    "duration": 4,
                    "color": "teal",
                },
            ]),
        },
        "car_dealership": {
            "total_months": 18,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Utility Prep",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Showroom + Service Structure",
                    "start_month": 2,
                    "duration": 7,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Envelope + Storefront Package",
                    "start_month": 6,
                    "duration": 6,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Service Bay MEP Rough-In",
                    "start_month": 6,
                    "duration": 7,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Showroom + Customer Finish-Out",
                    "start_month": 10,
                    "duration": 6,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Equipment Startup + Delivery Ops Readiness",
                    "start_month": 13,
                    "duration": 5,
                    "color": "teal",
                },
            ]),
        },
        "broadcast_facility": {
            "total_months": 20,
            "phases": _phases([
                {
                    "id": "site_foundation",
                    "label": "Site + Utility Backbone",
                    "start_month": 0,
                    "duration": 4,
                    "color": "blue",
                },
                {
                    "id": "structural",
                    "label": "Studio Shell + Control Core",
                    "start_month": 2,
                    "duration": 8,
                    "color": "green",
                },
                {
                    "id": "exterior_envelope",
                    "label": "Acoustic Envelope + Weather Tight",
                    "start_month": 6,
                    "duration": 7,
                    "color": "orange",
                },
                {
                    "id": "mep_rough",
                    "label": "Low-Noise MEP + Signal Path Rough-In",
                    "start_month": 7,
                    "duration": 8,
                    "color": "purple",
                },
                {
                    "id": "interior_finishes",
                    "label": "Studio + Edit Suite Fit-Out",
                    "start_month": 11,
                    "duration": 7,
                    "color": "pink",
                },
                {
                    "id": "mep_finishes",
                    "label": "Signal Integration + Recommissioning",
                    "start_month": 14,
                    "duration": 6,
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
