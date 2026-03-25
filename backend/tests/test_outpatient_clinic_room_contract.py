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


def _analyze_outpatient_clinic(
    description: str,
    *,
    square_footage: int = 18_000,
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
    ("square_footage", "expected_exam_rooms", "expected_size_band"),
    [
        (4_500, 8, "compact_clinic"),
        (6_000, 8, "compact_clinic"),
        (10_000, 16, "standard_clinic"),
        (12_000, 16, "standard_clinic"),
        (18_000, 28, "expanded_clinic"),
    ],
)
def test_outpatient_clinic_no_count_visible_contract_uses_banded_exam_room_baseline(
    square_footage: int,
    expected_exam_rooms: int,
    expected_size_band: str,
):
    parsed, calculations = _analyze_outpatient_clinic(
        f"New {square_footage:,} SF outpatient clinic in Nashville, TN",
        square_footage=square_footage,
    )

    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    project_info = calculations["project_info"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]
    procedure_pricing_preview = _available_special_feature_pricing_by_id(calculations)["procedure_room"]
    operating_model = calculations["operating_model"]

    assert parsed["subtype"] == "outpatient_clinic"
    assert "exam_room_count" not in parsed
    assert "procedure_room_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert facility_metrics["units"] == expected_exam_rooms
    assert facility_metrics["unit_label"] == "exam rooms"
    assert facility_metrics["unit_count_source"] == "size_band_default"
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") is None
    assert top_level_per_unit["units"] == expected_exam_rooms
    assert top_level_per_unit["unit_label"] == "exam rooms"
    assert top_level_per_unit["units_source"] == "size_band_default"
    assert ownership_per_unit["units"] == expected_exam_rooms
    assert ownership_per_unit["unit_label"] == "exam rooms"
    assert project_info["unit_label"] == "exam rooms"
    assert project_info["unit_count"] == expected_exam_rooms
    assert project_info["unit_count_source"] == "size_band_default"
    assert pricing_preview["requested_quantity"] == pytest.approx(float(expected_exam_rooms))
    assert pricing_preview["requested_quantity_source"] == "size_band_default"
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(float(expected_exam_rooms))
    assert pricing_preview["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_preview["resolved_size_band"] == expected_size_band
    assert pricing_preview["billed_quantity"] == pytest.approx(float(expected_exam_rooms))
    assert procedure_pricing_preview["requested_quantity"] == pytest.approx(0.0)
    assert procedure_pricing_preview["requested_quantity_source"] == "explicit_count_required"
    assert procedure_pricing_preview["billed_quantity"] == pytest.approx(0.0)
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == str(expected_exam_rooms)
    assert _operating_model_metric_value(operating_model, "Inferred Exam Rooms") is None
    assert (
        "Primary exam-room count uses the outpatient size-band baseline because no explicit exam-room count was parsed."
        in (operating_model.get("notes") or [])
    )


def test_outpatient_clinic_explicit_exam_room_count_auto_activates_pricing_and_visible_units():
    parsed, calculations = _analyze_outpatient_clinic(
        "New 18,000 SF outpatient clinic with 16 exam rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    exam_row = breakdown_by_id["exam_rooms"]
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    ownership_per_unit = calculations["ownership_analysis"]["operational_metrics"]["per_unit"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]
    procedure_pricing_preview = _available_special_feature_pricing_by_id(calculations)["procedure_room"]
    operating_model = calculations["operating_model"]
    annual_revenue = calculations["revenue_analysis"]["annual_revenue"]

    assert parsed["exam_room_count"] == 16
    assert sorted(breakdown_by_id) == ["exam_rooms"]
    assert exam_row["requested_quantity"] == pytest.approx(16.0)
    assert exam_row["requested_quantity_source"] == "explicit_override:exam_room_count"
    assert exam_row["included_baseline_quantity"] == pytest.approx(28.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert exam_row["resolved_size_band"] == "expanded_clinic"
    assert exam_row["billed_quantity"] == pytest.approx(0.0)
    assert exam_row["total_cost"] == pytest.approx(0.0)
    assert facility_metrics["units"] == 16
    assert facility_metrics["unit_label"] == "exam rooms"
    assert facility_metrics["unit_count_source"] == "explicit_override:exam_room_count"
    assert facility_metrics["revenue_per_unit"] == pytest.approx(annual_revenue / 16.0)
    assert top_level_per_unit["units"] == 16
    assert top_level_per_unit["unit_label"] == "exam rooms"
    assert top_level_per_unit["units_source"] == "explicit_override:exam_room_count"
    assert ownership_per_unit["units"] == 16
    assert ownership_per_unit["unit_label"] == "exam rooms"
    assert pricing_preview["requested_quantity"] == pytest.approx(16.0)
    assert pricing_preview["included_baseline_quantity"] == pytest.approx(28.0)
    assert pricing_preview["included_baseline_quantity_source"] == "size_band_default"
    assert pricing_preview["resolved_size_band"] == "expanded_clinic"
    assert pricing_preview["billed_quantity"] == pytest.approx(0.0)
    assert procedure_pricing_preview["requested_quantity"] == pytest.approx(0.0)
    assert procedure_pricing_preview["requested_quantity_source"] == "explicit_count_required"
    assert procedure_pricing_preview["billed_quantity"] == pytest.approx(0.0)
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "16"
    assert _operating_model_metric_value(operating_model, "Procedure Rooms") is None


def test_outpatient_clinic_explicit_exam_and_procedure_counts_stay_separate_and_change_analyzed_totals():
    _, baseline_calculations = _analyze_outpatient_clinic(
        "New 18,000 SF outpatient clinic in Nashville, TN"
    )
    parsed, calculations = _analyze_outpatient_clinic(
        "New 18,000 SF outpatient clinic with 12 exam rooms and 4 procedure rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    exam_row = breakdown_by_id["exam_rooms"]
    procedure_row = breakdown_by_id["procedure_room"]
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    operating_model = calculations["operating_model"]

    assert parsed["exam_room_count"] == 12
    assert parsed["procedure_room_count"] == 4
    assert sorted(breakdown_by_id) == ["exam_rooms", "procedure_room"]
    assert exam_row["requested_quantity"] == pytest.approx(12.0)
    assert exam_row["included_baseline_quantity"] == pytest.approx(28.0)
    assert exam_row["included_baseline_quantity_source"] == "size_band_default"
    assert exam_row["billed_quantity"] == pytest.approx(0.0)
    assert procedure_row["requested_quantity"] == pytest.approx(4.0)
    assert procedure_row["requested_quantity_source"] == "explicit_override:procedure_room_count"
    assert procedure_row["billed_quantity"] == pytest.approx(4.0)
    assert procedure_row["total_cost"] == pytest.approx(700000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(700000.0)
    assert calculations["totals"]["total_project_cost"] > baseline_calculations["totals"]["total_project_cost"]
    assert facility_metrics["units"] == 12
    assert facility_metrics["unit_label"] == "exam rooms"
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(4.0)
    assert top_level_per_unit["units"] == 12
    assert top_level_per_unit["unit_label"] == "exam rooms"
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "12"
    assert _operating_model_metric_value(operating_model, "Procedure Rooms") == "4"


def test_outpatient_clinic_reversed_order_parses_both_room_counts():
    parsed, calculations = _analyze_outpatient_clinic(
        "New outpatient clinic with 3 procedure rooms and 14 exam rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]

    assert parsed["subtype"] == "outpatient_clinic"
    assert parsed["procedure_room_count"] == 3
    assert parsed["exam_room_count"] == 14
    assert sorted(breakdown_by_id) == ["exam_rooms", "procedure_room"]
    assert breakdown_by_id["exam_rooms"]["requested_quantity"] == pytest.approx(14.0)
    assert breakdown_by_id["procedure_room"]["requested_quantity"] == pytest.approx(3.0)
    assert facility_metrics["units"] == 14
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(3.0)


def test_outpatient_clinic_procedure_only_input_keeps_fallback_exam_rooms_and_prices_only_procedure_rooms():
    parsed, calculations = _analyze_outpatient_clinic(
        "New 18,000 SF outpatient clinic with 3 procedure rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]
    top_level_per_unit = calculations["operational_metrics"]["per_unit"]
    pricing_preview = _available_special_feature_pricing_by_id(calculations)["exam_rooms"]
    operating_model = calculations["operating_model"]

    assert "exam_room_count" not in parsed
    assert parsed["procedure_room_count"] == 3
    assert sorted(breakdown_by_id) == ["procedure_room"]
    assert breakdown_by_id["procedure_room"]["requested_quantity"] == pytest.approx(3.0)
    assert breakdown_by_id["procedure_room"]["requested_quantity_source"] == "explicit_override:procedure_room_count"
    assert breakdown_by_id["procedure_room"]["billed_quantity"] == pytest.approx(3.0)
    assert facility_metrics["units"] == 28
    assert facility_metrics["unit_label"] == "exam rooms"
    assert facility_metrics["unit_count_source"] == "size_band_default"
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(3.0)
    assert top_level_per_unit["units"] == 28
    assert top_level_per_unit["units_source"] == "size_band_default"
    assert pricing_preview["requested_quantity"] == pytest.approx(28.0)
    assert pricing_preview["requested_quantity_source"] == "size_band_default"
    assert _operating_model_metric_value(operating_model, "Exam Rooms") == "28"
    assert _operating_model_metric_value(operating_model, "Procedure Rooms") == "3"


def test_outpatient_clinic_ancillary_imaging_and_lab_mentions_do_not_create_fake_quantitative_room_outputs():
    parsed, calculations = _analyze_outpatient_clinic(
        "New multispecialty clinic with 20 exam rooms, imaging, and lab in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]
    project_info = calculations["project_info"]
    operating_model = calculations["operating_model"]

    assert parsed["subtype"] == "outpatient_clinic"
    assert parsed["exam_room_count"] == 20
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") is None
    assert _facility_metric_entry_value(facility_metrics, "x_ray_rooms") is None
    assert project_info["unit_label"] == "exam rooms"
    assert project_info["unit_count"] == 20
    assert "laboratory" not in breakdown_by_id
    assert "hc_outpatient_imaging_pod" not in breakdown_by_id
    assert _operating_model_metric_value(operating_model, "Procedure Rooms") is None


def test_outpatient_clinic_written_number_counts_flow_through_analyze_contract():
    parsed, calculations = _analyze_outpatient_clinic(
        "New 18,000 SF outpatient clinic with sixteen exam rooms and four procedure rooms in Nashville, TN"
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]

    assert parsed["exam_room_count"] == 16
    assert parsed["procedure_room_count"] == 4
    assert sorted(breakdown_by_id) == ["exam_rooms", "procedure_room"]
    assert breakdown_by_id["exam_rooms"]["requested_quantity"] == pytest.approx(16.0)
    assert breakdown_by_id["procedure_room"]["requested_quantity"] == pytest.approx(4.0)
    assert facility_metrics["units"] == 16
    assert _facility_metric_entry_value(facility_metrics, "procedure_rooms") == pytest.approx(4.0)
