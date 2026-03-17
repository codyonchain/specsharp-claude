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
        (
            BuildingType.MIXED_USE,
            "office_residential",
            "mixed_use_revenue_mix",
            ["Revenue Mix", "Blended Productivity & Burden"],
            ["Mix Source", "Mix Composition", "Revenue Factor Applied", "Blended Revenue / SF", "NOI Margin", "Expense Ratio"],
            ["Staffing Metrics", "Efficiency Score"],
        ),
        (
            BuildingType.RETAIL,
            "shopping_center",
            "retail_lease_productivity",
            ["Lease Productivity", "Operating Burden"],
            ["Effective Rent / SF", "Occupancy Assumption", "NOI Margin", "Expense Ratio"],
            ["Staffing Metrics", "Efficiency Score"],
        ),
        (
            BuildingType.RESTAURANT,
            "full_service",
            "restaurant_core_economics",
            ["Core Economics", "Operating Burden"],
            ["Sales / SF", "Prime Cost", "Labor Burden", "Food Burden", "NOI Margin"],
            ["Staffing Metrics", "Efficiency Score", "Target KPIs"],
        ),
        (
            BuildingType.PARKING,
            "parking_garage",
            "parking_space_economics",
            ["Space Economics", "Operating Burden"],
            ["Spaces", "Revenue / Space / Month", "Occupancy Assumption", "NOI Margin", "Expense Ratio"],
            ["Staffing Metrics", "Revenue / SF", "Efficiency Score"],
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
    "building_type,subtype,expected_variant",
    [
        (BuildingType.MIXED_USE, "office_residential", "mixed_use_revenue_mix"),
        (BuildingType.MIXED_USE, "retail_residential", "mixed_use_revenue_mix"),
        (BuildingType.MIXED_USE, "hotel_retail", "mixed_use_revenue_mix"),
        (BuildingType.MIXED_USE, "transit_oriented", "mixed_use_revenue_mix"),
        (BuildingType.MIXED_USE, "urban_mixed", "mixed_use_revenue_mix"),
        (BuildingType.RETAIL, "shopping_center", "retail_lease_productivity"),
        (BuildingType.RETAIL, "big_box", "retail_lease_productivity"),
        (BuildingType.RESTAURANT, "quick_service", "restaurant_core_economics"),
        (BuildingType.RESTAURANT, "full_service", "restaurant_core_economics"),
        (BuildingType.RESTAURANT, "fine_dining", "restaurant_core_economics"),
        (BuildingType.RESTAURANT, "cafe", "restaurant_core_economics"),
        (BuildingType.RESTAURANT, "bar_tavern", "restaurant_core_economics"),
        (BuildingType.PARKING, "surface_parking", "parking_space_economics"),
        (BuildingType.PARKING, "parking_garage", "parking_space_economics"),
        (BuildingType.PARKING, "underground_parking", "parking_space_economics"),
        (BuildingType.PARKING, "automated_parking", "parking_space_economics"),
    ],
)
def test_phase2_launch_families_emit_operating_model_for_all_launch_subtypes(
    building_type: BuildingType,
    subtype: str,
    expected_variant: str,
):
    result = _calculate(building_type, subtype)
    operating_model = result.get("operating_model")

    assert operating_model is not None
    assert operating_model["variant"] == expected_variant
    assert operating_model["title"] == "Operating Model"


@pytest.mark.parametrize(
    "building_type,subtype",
    [
        (BuildingType.INDUSTRIAL, "distribution_center"),
        (BuildingType.SPECIALTY, "laboratory"),
        (BuildingType.CIVIC, "library"),
        (BuildingType.EDUCATIONAL, "university"),
    ],
)
def test_remaining_unsupported_families_do_not_emit_generic_operating_model(
    building_type: BuildingType,
    subtype: str,
):
    result = _calculate(building_type, subtype)
    assert result.get("operating_model") is None
