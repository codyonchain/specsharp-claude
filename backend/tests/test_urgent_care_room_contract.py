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


def _analyze_urgent_care(
    description: str,
    *,
    square_footage: int = 9_000,
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


def _facility_metric_entry_value(
    facility_metrics: Dict[str, object],
    entry_id: str,
) -> Optional[float]:
    for entry in facility_metrics.get("entries") or []:
        if isinstance(entry, dict) and entry.get("id") == entry_id:
            value = entry.get("value")
            if isinstance(value, (int, float)):
                return float(value)
    return None


def _operating_model_metric_value(
    operating_model: Dict[str, object],
    label: str,
) -> Optional[str]:
    for section in operating_model.get("sections") or []:
        if not isinstance(section, dict):
            continue
        for metric in section.get("metrics") or []:
            if isinstance(metric, dict) and metric.get("label") == label:
                value = metric.get("value")
                return str(value) if value is not None else None
    return None


@pytest.mark.parametrize(
    ("square_footage", "expected_baseline", "expected_size_band"),
    [
        (3_000, 6, "compact_urgent_care"),
        (4_500, 8, "small_urgent_care"),
        (6_000, 10, "standard_urgent_care"),
        (7_500, 12, "expanded_urgent_care"),
        (9_000, 14, "large_urgent_care"),
        (12_000, 18, "regional_urgent_care"),
    ],
)
def test_urgent_care_no_count_banded_exam_room_baseline_drives_visible_units_and_pricing_preview(
    square_footage: int,
    expected_baseline: int,
    expected_size_band: str,
):
    parsed, calculations = _analyze_urgent_care(
        f"New {square_footage:,} SF urgent care in Nashville, TN",
        square_footage=square_footage,
    )

    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    project_info = calculations["project_info"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]

    assert parsed["subtype"] == "urgent_care"
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert facility_metrics["units"] == expected_baseline
    assert facility_metrics["unit_label"] == "inferred exam rooms"
    assert top_level_per_unit["units"] == expected_baseline
    assert top_level_per_unit["unit_label"] == "inferred exam rooms"
    assert ownership_per_unit["units"] == expected_baseline
    assert ownership_per_unit["unit_label"] == "inferred exam rooms"
    assert project_info["unit_label"] == "inferred exam rooms"
    assert project_info["unit_count"] == expected_baseline
    assert pricing_preview["requested_quantity"] == pytest.approx(float(expected_baseline))
    assert pricing_preview["requested_quantity_source"] == "size_band_default"
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(float(expected_baseline))
    assert pricing_preview["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_preview["resolved_size_band"] == expected_size_band
    assert pricing_preview["billed_quantity"] == pytest.approx(float(expected_baseline))


def test_urgent_care_no_count_visible_contract_uses_inferred_exam_rooms():
    parsed, calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care in Nashville, TN"
    )

    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    project_info = calculations["project_info"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]

    assert parsed["subtype"] == "urgent_care"
    assert "exam_room_count" not in parsed
    assert "procedure_room_count" not in parsed
    assert "x_ray_room_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert facility_metrics["units"] == 14
    assert facility_metrics["unit_label"] == "inferred exam rooms"
    assert facility_metrics["unit_count_source"] == "inferred_exam_room_count"
    assert top_level_per_unit["units"] == 14
    assert top_level_per_unit["unit_label"] == "inferred exam rooms"
    assert top_level_per_unit["units_source"] == "inferred_exam_room_count"
    assert ownership_per_unit["units"] == 14
    assert ownership_per_unit["unit_label"] == "inferred exam rooms"
    assert project_info["unit_label"] == "inferred exam rooms"
    assert project_info["unit_count"] == 14
    assert pricing_preview["requested_quantity"] == pytest.approx(14.0)
    assert pricing_preview["requested_quantity_source"] == "size_band_default"
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(14.0)
    assert pricing_preview["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_preview["resolved_size_band"] == "large_urgent_care"
    assert pricing_preview["billed_quantity"] == pytest.approx(14.0)
    assert (
        "Primary exam-room count is inferred from square footage because no explicit exam-room count was parsed."
        in (calculations["operating_model"].get("notes") or [])
    )


def test_urgent_care_explicit_exam_room_count_auto_activates_pricing_and_visible_units():
    parsed, calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care with 12 exam rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    exam_row = breakdown_by_id["exam_rooms"]
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]
    operating_model = calculations["operating_model"]
    annual_revenue = calculations["revenue_analysis"]["annual_revenue"]

    assert parsed["exam_room_count"] == 12
    assert sorted(breakdown_by_id) == ["exam_rooms"]
    assert exam_row["requested_quantity"] == pytest.approx(12.0)
    assert exam_row["requested_quantity_source"] == "explicit_override:exam_room_count"
    assert exam_row["included_baseline_quantity"] == pytest.approx(14.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert exam_row["resolved_size_band"] == "large_urgent_care"
    assert exam_row["billed_quantity"] == pytest.approx(0.0)
    assert exam_row["total_cost"] == pytest.approx(0.0)
    assert facility_metrics["units"] == 12
    assert facility_metrics["unit_label"] == "exam rooms"
    assert facility_metrics["unit_count_source"] == "explicit_override:exam_room_count"
    assert facility_metrics["revenue_per_unit"] == pytest.approx(annual_revenue / 12.0)
    assert top_level_per_unit["units"] == 12
    assert top_level_per_unit["unit_label"] == "exam rooms"
    assert top_level_per_unit["units_source"] == "explicit_override:exam_room_count"
    assert ownership_per_unit["units"] == 12
    assert ownership_per_unit["unit_label"] == "exam rooms"
    assert pricing_preview["requested_quantity"] == pytest.approx(12.0)
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(14.0)
    assert pricing_preview["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_preview["resolved_size_band"] == "large_urgent_care"
    assert pricing_preview["billed_quantity"] == pytest.approx(0.0)
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "12"
    assert _operating_model_metric_value(operating_model, "Inferred Exam Rooms") is None


def test_urgent_care_explicit_procedure_rooms_show_separately_and_do_not_merge_into_exam_room_total():
    parsed, calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care with 10 exam rooms and 2 procedure rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    exam_row = breakdown_by_id["exam_rooms"]
    procedure_row = breakdown_by_id["procedure_room"]
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    operating_model = calculations["operating_model"]

    assert parsed["exam_room_count"] == 10
    assert parsed["procedure_room_count"] == 2
    assert sorted(breakdown_by_id) == ["exam_rooms", "procedure_room"]
    assert exam_row["requested_quantity"] == pytest.approx(10.0)
    assert exam_row["included_baseline_quantity"] == pytest.approx(14.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert exam_row["billed_quantity"] == pytest.approx(0.0)
    assert procedure_row["requested_quantity"] == pytest.approx(2.0)
    assert procedure_row["requested_quantity_source"] == "explicit_override:procedure_room_count"
    assert procedure_row["billed_quantity"] == pytest.approx(2.0)
    assert procedure_row["total_cost"] == pytest.approx(350000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(350000.0)
    assert facility_metrics["units"] == 10
    assert facility_metrics["unit_label"] == "exam rooms"
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(2.0)
    assert _facility_metric_entry_value(facility_metrics, "x_ray_rooms") is None
    assert top_level_per_unit["units"] == 10
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "10"
    assert _operating_model_metric_value(operating_model, "Procedure Rooms") == "2"
    assert _operating_model_metric_value(operating_model, "X-Ray Rooms") is None


def test_urgent_care_explicit_x_ray_rooms_auto_activate_and_stay_separate_from_exam_rooms():
    parsed, calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care with 2 x-ray rooms and 10 exam rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    exam_row = breakdown_by_id["exam_rooms"]
    x_ray_row = breakdown_by_id["x_ray"]
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    operating_model = calculations["operating_model"]

    assert parsed["exam_room_count"] == 10
    assert parsed["x_ray_room_count"] == 2
    assert sorted(breakdown_by_id) == ["exam_rooms", "x_ray"]
    assert exam_row["requested_quantity"] == pytest.approx(10.0)
    assert exam_row["included_baseline_quantity"] == pytest.approx(14.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert x_ray_row["requested_quantity"] == pytest.approx(2.0)
    assert x_ray_row["requested_quantity_source"] == "explicit_override:x_ray_room_count"
    assert x_ray_row["included_baseline_quantity"] == pytest.approx(1.0)
    assert x_ray_row["billed_quantity"] == pytest.approx(1.0)
    assert x_ray_row["total_cost"] == pytest.approx(250000.0)
    assert facility_metrics["units"] == 10
    assert facility_metrics["unit_label"] == "exam rooms"
    assert _facility_metric_entry_value(facility_metrics, "x_ray_rooms") == pytest.approx(2.0)
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") is None
    assert top_level_per_unit["units"] == 10
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "10"
    assert _operating_model_metric_value(operating_model, "X-Ray Rooms") == "2"


def test_urgent_care_below_baseline_explicit_exam_room_count_does_not_create_discount():
    _, baseline_calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care in Nashville, TN"
    )
    _, explicit_calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care with 12 exam rooms in Nashville, TN"
    )

    exam_row = _special_feature_breakdown_by_id(explicit_calculations)["exam_rooms"]

    assert baseline_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert explicit_calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert baseline_calculations["facility_metrics"]["units"] == 14
    assert exam_row["included_baseline_quantity"] == pytest.approx(14.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert exam_row["billed_quantity"] == pytest.approx(0.0)
    assert explicit_calculations["totals"]["total_project_cost"] == pytest.approx(
        baseline_calculations["totals"]["total_project_cost"]
    )
    assert explicit_calculations["revenue_analysis"]["annual_revenue"] < baseline_calculations["revenue_analysis"]["annual_revenue"]


def test_urgent_care_written_number_counts_flow_through_analyze_contract():
    parsed, calculations = _analyze_urgent_care(
        "New 9,000 SF urgent care with twelve exam rooms and two procedure rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]

    assert parsed["exam_room_count"] == 12
    assert parsed["procedure_room_count"] == 2
    assert sorted(breakdown_by_id) == ["exam_rooms", "procedure_room"]
    assert breakdown_by_id["exam_rooms"]["requested_quantity"] == pytest.approx(12.0)
    assert breakdown_by_id["procedure_room"]["requested_quantity"] == pytest.approx(2.0)
    assert facility_metrics["units"] == 12
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(2.0)
