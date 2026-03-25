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


def _analyze(
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
    (
        "description",
        "square_footage",
        "expected_building_type",
        "expected_subtype",
        "expected_feature_id",
        "expected_total_cost",
    ),
    (
        (
            "New 3,200 SF quick service restaurant with 2 drive-thru lanes in Nashville, TN",
            3_200,
            "restaurant",
            "quick_service",
            "double_drive_thru",
            160_000.0,
        ),
        (
            "New 2,500 SF cafe with 2 drive-thru lanes in Nashville, TN",
            2_500,
            "restaurant",
            "cafe",
            "drive_thru",
            150_000.0,
        ),
        (
            "New 18,000 SF strip center with 2 drive-thru lanes in Nashville, TN",
            18_000,
            "retail",
            "shopping_center",
            "drive_thru",
            170_000.0,
        ),
    ),
)
def test_numeric_drive_thru_lane_count_auto_activates_subtype_specific_feature_in_analyze_flow(
    description: str,
    square_footage: int,
    expected_building_type: str,
    expected_subtype: str,
    expected_feature_id: str,
    expected_total_cost: float,
):
    parsed, calculations = _analyze(
        description,
        square_footage=square_footage,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    pricing_preview_by_id = _available_special_feature_pricing_by_id(calculations)
    row = breakdown_by_id[expected_feature_id]
    preview_row = pricing_preview_by_id[expected_feature_id]

    assert parsed["building_type"] == expected_building_type
    assert parsed["subtype"] == expected_subtype
    assert parsed["drive_thru_lane_count"] == 2
    assert sorted(breakdown_by_id) == [expected_feature_id]
    assert row["requested_quantity"] == pytest.approx(2.0)
    assert row["requested_quantity_source"] == "explicit_override:drive_thru_lane_count"
    assert row["billed_quantity"] == pytest.approx(2.0)
    assert row["total_cost"] == pytest.approx(expected_total_cost)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(
        expected_total_cost
    )
    assert preview_row["requested_quantity"] == pytest.approx(row["requested_quantity"])
    assert preview_row["requested_quantity_source"] == row["requested_quantity_source"]
    assert preview_row["billed_quantity"] == pytest.approx(row["billed_quantity"])


def test_quick_service_numeric_multi_lane_count_replaces_wrong_baseline_drive_thru_selection():
    description = "New 3,200 SF quick service restaurant with 2 drive-thru lanes in Nashville, TN"
    _, corrected_calculations = _analyze(
        description,
        square_footage=3_200,
        special_features=["drive_thru"],
    )
    _, manual_double_calculations = _analyze(
        description,
        square_footage=3_200,
        special_features=["double_drive_thru"],
    )

    corrected_breakdown = _special_feature_breakdown_by_id(corrected_calculations)
    corrected_row = corrected_breakdown["double_drive_thru"]
    manual_double_row = _special_feature_breakdown_by_id(manual_double_calculations)["double_drive_thru"]

    assert sorted(corrected_breakdown) == ["double_drive_thru"]
    assert corrected_row["requested_quantity"] == pytest.approx(2.0)
    assert corrected_row["requested_quantity_source"] == "explicit_override:drive_thru_lane_count"
    assert corrected_row["total_cost"] == pytest.approx(160_000.0)
    assert corrected_calculations["construction_costs"]["special_features_total"] == pytest.approx(
        160_000.0
    )
    assert corrected_row["requested_quantity"] == pytest.approx(manual_double_row["requested_quantity"])
    assert corrected_row["billed_quantity"] == pytest.approx(manual_double_row["billed_quantity"])
    assert corrected_row["total_cost"] == pytest.approx(manual_double_row["total_cost"])


def test_quick_service_qualitative_drive_thru_language_does_not_auto_activate_pricing():
    parsed, calculations = _analyze(
        "New 3,200 SF quick service restaurant with drive thru in Nashville, TN",
        square_footage=3_200,
    )

    assert parsed["subtype"] == "quick_service"
    assert parsed["has_drive_thru"] is True
    assert "drive_thru_lane_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_quick_service_single_numeric_lane_does_not_start_baseline_visibility_cleanup():
    parsed, calculations = _analyze(
        "New 3,200 SF quick service restaurant with 1 drive-thru lane in Nashville, TN",
        square_footage=3_200,
    )

    assert parsed["subtype"] == "quick_service"
    assert parsed["drive_thru_lane_count"] == 1
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_quick_service_drive_thru_pad_language_does_not_create_lane_activation():
    parsed, calculations = _analyze(
        "New 3,200 SF quick service restaurant with 2 drive-thru pads in Nashville, TN",
        square_footage=3_200,
    )

    assert parsed["subtype"] == "quick_service"
    assert parsed["has_drive_thru"] is True
    assert "drive_thru_lane_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
