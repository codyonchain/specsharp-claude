import asyncio
from typing import Dict, List, Optional, Tuple

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.v2.api.scope import AnalyzeRequest, analyze_project


def _build_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/v2/analyze",
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("localhost", 8000),
            "scheme": "http",
            "root_path": "",
            "http_version": "1.1",
        }
    )


def _analyze_dental_office(
    description: str,
    *,
    square_footage: int,
    special_features: Optional[List[str]] = None,
) -> Tuple[Dict[str, object], Dict[str, object]]:
    payload = AnalyzeRequest(
        description=description,
        squareFootage=square_footage,
        location="Nashville, TN",
        projectClass="ground_up",
        special_features=special_features or [],
    )

    response = asyncio.run(
        analyze_project(
            _build_request(),
            payload,
            build_testing_auth_context(),
        )
    )

    assert response.success is True, response.errors
    return response.data["parsed_input"], response.data["calculations"]


def _special_feature_breakdown_by_id(calculations: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    breakdown = calculations["construction_costs"]["special_features_breakdown"]
    return {
        row["id"]: row
        for row in breakdown
        if isinstance(row, dict) and row.get("id")
    }


def _available_special_feature_pricing_by_id(
    calculations: Dict[str, object],
) -> Dict[str, Dict[str, object]]:
    pricing_rows = calculations["project_info"]["available_special_feature_pricing"]
    return {
        row["id"]: row
        for row in pricing_rows
        if isinstance(row, dict) and row.get("id")
    }


@pytest.mark.parametrize(
    ("square_footage", "expected_baseline"),
    (
        (4_500, 8),
        (6_000, 8),
        (7_500, 10),
    ),
)
def test_dental_office_no_count_visible_outputs_follow_operatory_baseline_contract(
    square_footage: int,
    expected_baseline: int,
):
    description = f"New {square_footage:,} SF dental office in Nashville, TN"
    parsed, calculations = _analyze_dental_office(
        description,
        square_footage=square_footage,
    )

    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    operatory_pricing = _available_special_feature_pricing_by_id(calculations)["operatory"]

    assert parsed["subtype"] == "dental_office"
    assert "operatory_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert facility_metrics["units"] == expected_baseline
    assert facility_metrics["unit_label"] == "operatories"
    assert top_level_per_unit["units"] == expected_baseline
    assert top_level_per_unit["unit_label"] == "operatories"
    assert ownership_per_unit["units"] == expected_baseline
    assert ownership_per_unit["unit_label"] == "operatories"
    assert operatory_pricing["requested_quantity"] == pytest.approx(float(expected_baseline))
    assert operatory_pricing["requested_quantity_source"] == "size_band_default"
    assert operatory_pricing["included_baseline_quantity"] == pytest.approx(float(expected_baseline))
    assert operatory_pricing["included_baseline_quantity_source"] == "size_band_default"
    assert operatory_pricing["billed_quantity"] == pytest.approx(float(expected_baseline))


def test_dental_office_explicit_operatory_count_auto_activates_pricing_and_visible_units_in_analyze_flow():
    parsed, calculations = _analyze_dental_office(
        "New 6,000 SF dental office with 12 operatories in Nashville, TN",
        square_footage=6_000,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    operatory_row = breakdown_by_id["operatory"]
    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["operatory"]

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "dental_office"
    assert parsed["operatory_count"] == 12
    assert sorted(breakdown_by_id) == ["operatory"]
    assert operatory_row["requested_quantity"] == pytest.approx(12.0)
    assert operatory_row["requested_quantity_source"] == "explicit_override:operatory_count"
    assert operatory_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert operatory_row["included_baseline_quantity_source"] == "size_band_default"
    assert operatory_row["billed_quantity"] == pytest.approx(4.0)
    assert operatory_row["total_cost"] == pytest.approx(180_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(180_000.0)
    assert facility_metrics["units"] == 12
    assert facility_metrics["unit_label"] == "operatories"
    assert per_unit["units"] == 12
    assert per_unit["unit_label"] == "operatories"
    assert pricing_preview["requested_quantity"] == pytest.approx(12.0)
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(8.0)
    assert pricing_preview["billed_quantity"] == pytest.approx(4.0)


def test_dental_office_below_baseline_explicit_operatory_count_shows_visible_count_without_discount():
    _, baseline_calculations = _analyze_dental_office(
        "New 6,000 SF dental office in Nashville, TN",
        square_footage=6_000,
    )
    parsed, explicit_calculations = _analyze_dental_office(
        "New 6,000 SF dental office with 6 operatories in Nashville, TN",
        square_footage=6_000,
    )

    operatory_row = _special_feature_breakdown_by_id(explicit_calculations)["operatory"]

    assert parsed["operatory_count"] == 6
    assert baseline_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert explicit_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert operatory_row["requested_quantity"] == pytest.approx(6.0)
    assert operatory_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert operatory_row["billed_quantity"] == pytest.approx(0.0)
    assert operatory_row["total_cost"] == pytest.approx(0.0)
    assert explicit_calculations["facility_metrics"]["units"] == 6
    assert explicit_calculations["operational_metrics"]["per_unit"]["units"] == 6
    assert explicit_calculations["totals"]["total_project_cost"] == pytest.approx(
        baseline_calculations["totals"]["total_project_cost"]
    )


def test_dental_office_explicit_operatory_count_prices_only_overage_above_same_baseline():
    parsed, calculations = _analyze_dental_office(
        "New 4,500 SF dental office with 10 operatories in Nashville, TN",
        square_footage=4_500,
    )

    operatory_row = _special_feature_breakdown_by_id(calculations)["operatory"]

    assert parsed["operatory_count"] == 10
    assert operatory_row["requested_quantity"] == pytest.approx(10.0)
    assert operatory_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert operatory_row["billed_quantity"] == pytest.approx(2.0)
    assert operatory_row["total_cost"] == pytest.approx(90_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(90_000.0)
    assert calculations["facility_metrics"]["units"] == 10
    assert calculations["operational_metrics"]["per_unit"]["units"] == 10


def test_dental_office_manual_operatory_selection_still_works_with_explicit_count():
    parsed, calculations = _analyze_dental_office(
        "New 6,000 SF dental office with 12 operatories in Nashville, TN",
        square_footage=6_000,
        special_features=["operatory"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    operatory_row = breakdown_by_id["operatory"]

    assert parsed["operatory_count"] == 12
    assert sorted(breakdown_by_id) == ["operatory"]
    assert operatory_row["requested_quantity"] == pytest.approx(12.0)
    assert operatory_row["included_baseline_quantity"] == pytest.approx(8.0)
    assert operatory_row["billed_quantity"] == pytest.approx(4.0)
    assert operatory_row["total_cost"] == pytest.approx(180_000.0)
