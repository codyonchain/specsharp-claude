import pytest

from app.v2.config.master_config import BuildingType, OwnershipType, ProjectClass
from app.v2.engines.unified_engine import unified_engine


def _calculate(building_type: BuildingType, subtype: str, square_footage: int = 20_000):
    return unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Dallas, TX",
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT,
    )


def _metric_labels(operating_model: dict) -> list[str]:
    return [
        metric["label"]
        for section in operating_model.get("sections", [])
        for metric in section.get("metrics", [])
    ]


@pytest.mark.parametrize(
    "building_type,subtype,expected_variant,expected_sections,required_labels,forbidden_labels",
    [
        (
            BuildingType.HEALTHCARE,
            "urgent_care",
            "healthcare_operating_model",
            ["Staffing", "Revenue Productivity", "Operating Signals"],
            ["Providers (MD/DO/NP/PA FTE)", "Revenue per Provider", "Visits / Day"],
            ["Efficiency Score", "Target KPIs"],
        ),
        (
            BuildingType.HEALTHCARE,
            "medical_office_building",
            "healthcare_operating_model",
            ["Staffing", "Revenue Productivity", "Operating Signals"],
            ["Tenant Suites", "Revenue per Tenant Suites", "Tenant Throughput Yield"],
            ["Soft Costs % of Total", "Yield on Cost"],
        ),
        (
            BuildingType.HEALTHCARE,
            "dental_office",
            "healthcare_operating_model",
            ["Staffing", "Revenue Productivity", "Operating Signals"],
            ["Operatories", "Revenue per Operatories", "Operatory Utilization"],
            ["Chair Utilization", "Ops per Provider"],
        ),
        (
            BuildingType.OFFICE,
            "class_a",
            "office_underwriting",
            ["Rent & Recoveries", "Operating Burden", "Cost Allocations"],
            ["Rent / SF", "Recoverable CAM", "NOI Margin", "Management Allocation"],
            ["Efficiency", "Efficiency Score"],
        ),
        (
            BuildingType.HOSPITALITY,
            "limited_service_hotel",
            "hospitality_keys",
            ["Key Metrics", "Operating Performance"],
            ["Rooms", "ADR", "Occupancy", "RevPAR", "NOI Margin"],
            ["Staffing Metrics", "Management"],
        ),
        (
            BuildingType.MULTIFAMILY,
            "market_rate_apartments",
            "multifamily_unit_economics",
            ["Unit Economics", "Operating Burden"],
            ["Units", "Revenue / Unit", "Average Rent", "Occupancy Assumption"],
            ["Units per Manager", "Maintenance Staff", "93%"],
        ),
        (
            BuildingType.INDUSTRIAL,
            "warehouse",
            "industrial_property_ops",
            ["Lease Productivity", "Operating Cost Mix"],
            ["Effective Rent / SF", "Property Tax", "Total Expenses"],
            ["Staffing Metrics", "Efficiency Score"],
        ),
        (
            BuildingType.INDUSTRIAL,
            "cold_storage",
            "industrial_property_ops",
            ["Lease Productivity", "Operating Cost Mix"],
            ["Effective Rent / SF", "Monitoring", "Total Expenses"],
            ["Staffing Metrics", "Efficiency Score"],
        ),
        (
            BuildingType.SPECIALTY,
            "data_center",
            "data_center_infrastructure",
            ["Asset Productivity", "Infrastructure Cost Mix"],
            ["Revenue / SF", "Connectivity", "Expense Ratio"],
            ["Efficiency Score", "Target KPIs"],
        ),
    ],
)
def test_supported_operating_model_variants_are_backend_owned_and_family_specific(
    building_type: BuildingType,
    subtype: str,
    expected_variant: str,
    expected_sections: list[str],
    required_labels: list[str],
    forbidden_labels: list[str],
):
    result = _calculate(building_type, subtype)
    operating_model = result.get("operating_model")

    assert operating_model is not None
    assert operating_model["title"] == "Operating Model"
    assert operating_model["variant"] == expected_variant
    assert [section["title"] for section in operating_model["sections"]] == expected_sections
    assert operating_model.get("notes")

    labels = _metric_labels(operating_model)
    for label in required_labels:
        assert label in labels
    for label in forbidden_labels:
        assert label not in labels


@pytest.mark.parametrize(
    "building_type,subtype",
    [
        (BuildingType.INDUSTRIAL, "distribution_center"),
        (BuildingType.RETAIL, "shopping_center"),
        (BuildingType.MIXED_USE, "office_residential"),
        (BuildingType.PARKING, "parking_garage"),
    ],
)
def test_unsupported_phase1_families_do_not_emit_generic_operating_model(
    building_type: BuildingType,
    subtype: str,
):
    result = _calculate(building_type, subtype)
    assert result.get("operating_model") is None
