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


def _analyze_surgical_center(
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


def test_surgical_center_explicit_or_count_auto_activates_operating_room_pricing_in_analyze_flow():
    parsed, calculations = _analyze_surgical_center(
        "24,000 SF ambulatory surgery center with 4 ORs in Nashville, TN",
        square_footage=24_000,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["operating_room"]

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "surgical_center"
    assert parsed["operating_room_count"] == 4
    assert sorted(breakdown_by_id) == ["operating_room"]
    assert row["requested_quantity"] == pytest.approx(4.0)
    assert row["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert row["included_baseline_quantity"] == pytest.approx(5.0)
    assert row["billed_quantity"] == pytest.approx(0.0)
    assert row["total_cost"] == pytest.approx(0.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_surgical_center_higher_explicit_or_count_prices_higher_in_analyze_flow():
    _, calculations_no_count = _analyze_surgical_center(
        "32,000 SF surgical center in Nashville, TN",
        square_footage=32_000,
    )
    parsed_8, calculations_8 = _analyze_surgical_center(
        "32,000 SF surgical center with 8 operating rooms in Nashville, TN",
        square_footage=32_000,
    )

    row_8 = _special_feature_breakdown_by_id(calculations_8)["operating_room"]

    assert parsed_8["operating_room_count"] == 8
    assert row_8["requested_quantity"] == pytest.approx(8.0)
    assert row_8["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert row_8["included_baseline_quantity"] == pytest.approx(7.0)
    assert row_8["billed_quantity"] == pytest.approx(1.0)
    assert row_8["total_cost"] == pytest.approx(450_000.0)
    assert calculations_no_count["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert calculations_8["construction_costs"]["special_features_total"] > (
        calculations_no_count["construction_costs"]["special_features_total"]
    )
    assert calculations_8["totals"]["total_project_cost"] > calculations_no_count["totals"]["total_project_cost"]


def test_surgical_center_hyphen_or_shorthand_parses_and_flows_through_backend_outputs():
    parsed, calculations = _analyze_surgical_center(
        "6-OR ASC with pre-op and recovery space in Nashville, TN",
        square_footage=24_000,
    )

    row = _special_feature_breakdown_by_id(calculations)["operating_room"]
    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]

    assert parsed["subtype"] == "surgical_center"
    assert parsed["operating_room_count"] == 6
    assert row["requested_quantity"] == pytest.approx(6.0)
    assert row["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert row["included_baseline_quantity"] == pytest.approx(5.0)
    assert row["billed_quantity"] == pytest.approx(1.0)
    assert row["total_cost"] == pytest.approx(450_000.0)
    assert facility_metrics["units"] == 6
    assert facility_metrics["unit_label"] == "operating rooms"
    assert per_unit["units"] == 6
    assert per_unit["unit_label"] == "operating rooms"


def test_surgical_center_without_explicit_or_count_preserves_default_behavior():
    parsed, calculations = _analyze_surgical_center(
        "24,000 SF ambulatory surgery center in Nashville, TN",
        square_footage=24_000,
    )

    assert "operating_room_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert calculations["facility_metrics"]["units"] == 5
    assert calculations["operational_metrics"]["per_unit"]["units"] == 5

    _, calculations_32k = _analyze_surgical_center(
        "32,000 SF surgical center in Nashville, TN",
        square_footage=32_000,
    )

    assert calculations_32k["facility_metrics"]["units"] == 7
    assert calculations_32k["operational_metrics"]["per_unit"]["units"] == 7


def test_surgical_center_manual_operating_room_selection_still_works_with_explicit_or_count():
    parsed, calculations = _analyze_surgical_center(
        "32,000 SF surgical center with 8 operating rooms in Nashville, TN",
        square_footage=32_000,
        special_features=["operating_room"],
    )

    row = _special_feature_breakdown_by_id(calculations)["operating_room"]

    assert parsed["operating_room_count"] == 8
    assert row["requested_quantity"] == pytest.approx(8.0)
    assert row["requested_quantity_source"] == "explicit_override:operating_room_count"
    assert row["included_baseline_quantity"] == pytest.approx(7.0)
    assert row["billed_quantity"] == pytest.approx(1.0)
    assert row["total_cost"] == pytest.approx(450_000.0)


def test_surgical_center_visible_backend_unit_outputs_follow_explicit_or_count():
    _, calculations = _analyze_surgical_center(
        "32,000 SF surgical center with 8 operating rooms in Nashville, TN",
        square_footage=32_000,
    )

    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]

    assert facility_metrics["units"] == 8
    assert facility_metrics["unit_label"] == "operating rooms"
    assert facility_metrics["cost_per_unit"] == pytest.approx(
        calculations["totals"]["total_project_cost"] / 8.0
    )
    assert per_unit["units"] == 8
    assert per_unit["unit_label"] == "operating rooms"


def test_surgical_center_below_baseline_explicit_or_count_does_not_create_discount():
    _, baseline_calculations = _analyze_surgical_center(
        "24,000 SF ambulatory surgery center in Nashville, TN",
        square_footage=24_000,
    )
    _, explicit_calculations = _analyze_surgical_center(
        "24,000 SF ambulatory surgery center with 4 ORs in Nashville, TN",
        square_footage=24_000,
    )

    assert baseline_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert explicit_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert explicit_calculations["totals"]["total_project_cost"] == pytest.approx(
        baseline_calculations["totals"]["total_project_cost"]
    )
