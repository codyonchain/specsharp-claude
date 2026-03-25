import asyncio
import json
from typing import Dict, List, Optional, Tuple

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.services.nlp_service import NLPService
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


def _analyze_imaging_center(
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


def _visible_imaging_payload(calculations: Dict[str, object]) -> str:
    visible_payload = {
        "facility_metrics": calculations.get("facility_metrics"),
        "operational_metrics": calculations.get("operational_metrics"),
        "project_info": calculations.get("project_info"),
    }
    return json.dumps(visible_payload, sort_keys=True).lower()


def test_imaging_center_mri_suite_count_auto_activates_pricing_and_visible_contract_in_analyze_flow():
    parsed, calculations = _analyze_imaging_center(
        "New 12,000 SF imaging center with 2 MRI suites in Nashville, TN",
        square_footage=12_000,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    mri_row = breakdown_by_id["mri_suite"]
    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]
    modality_program = facility_metrics["imaging_modality_program"]

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "imaging_center"
    assert parsed["mri_suite_count"] == 2
    assert sorted(breakdown_by_id) == ["mri_suite"]
    assert mri_row["requested_quantity"] == pytest.approx(2.0)
    assert mri_row["requested_quantity_source"] == "explicit_override:mri_suite_count"
    assert mri_row["included_baseline_quantity"] == pytest.approx(1.0)
    assert mri_row["billed_quantity"] == pytest.approx(1.0)
    assert mri_row["total_cost"] == pytest.approx(850_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(850_000.0)
    assert facility_metrics["unit_label"] == "specified modality suites"
    assert facility_metrics["units"] == 2
    assert _facility_metric_entry_value(facility_metrics, "mri_suites") == pytest.approx(2.0)
    assert _facility_metric_entry_value(facility_metrics, "total_specified_modality_suites") == pytest.approx(2.0)
    assert modality_program["state"] == "explicit_modality_counts"
    assert modality_program["mri_suites"] == 2
    assert modality_program["total_specified_modality_suites"] == 2
    assert per_unit["unit_label"] == "specified modality suites"
    assert per_unit["units"] == 2
    assert per_unit["units_source"] == "explicit_modality_counts"
    assert "cost_per_unit" not in per_unit
    assert "annual_revenue_per_unit" not in per_unit
    assert "scan rooms" not in _visible_imaging_payload(calculations)


def test_imaging_center_combined_mri_and_ct_counts_auto_activate_together_without_scan_room_fallback():
    parsed, calculations = _analyze_imaging_center(
        "New 12,000 SF imaging center with 1 CT suite and 2 MRI suites in Nashville, TN",
        square_footage=12_000,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]
    modality_program = facility_metrics["imaging_modality_program"]
    mri_row = breakdown_by_id["mri_suite"]
    ct_row = breakdown_by_id["ct_suite"]

    assert parsed["mri_suite_count"] == 2
    assert parsed["ct_suite_count"] == 1
    assert sorted(breakdown_by_id) == ["ct_suite", "mri_suite"]
    assert mri_row["requested_quantity"] == pytest.approx(2.0)
    assert mri_row["billed_quantity"] == pytest.approx(1.0)
    assert mri_row["total_cost"] == pytest.approx(850_000.0)
    assert ct_row["requested_quantity"] == pytest.approx(1.0)
    assert ct_row["billed_quantity"] == pytest.approx(0.0)
    assert ct_row["total_cost"] == pytest.approx(0.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(850_000.0)
    assert facility_metrics["unit_label"] == "specified modality suites"
    assert facility_metrics["units"] == 3
    assert _facility_metric_entry_value(facility_metrics, "mri_suites") == pytest.approx(2.0)
    assert _facility_metric_entry_value(facility_metrics, "ct_suites") == pytest.approx(1.0)
    assert _facility_metric_entry_value(facility_metrics, "total_specified_modality_suites") == pytest.approx(3.0)
    assert modality_program["state"] == "explicit_modality_counts"
    assert modality_program["mri_suites"] == 2
    assert modality_program["ct_suites"] == 1
    assert modality_program["total_specified_modality_suites"] == 3
    assert per_unit["unit_label"] == "specified modality suites"
    assert per_unit["units"] == 3
    assert per_unit["units_source"] == "explicit_modality_counts"
    assert "cost_per_unit" not in per_unit
    assert "annual_revenue_per_unit" not in per_unit
    assert "scan rooms" not in _visible_imaging_payload(calculations)


def test_imaging_center_no_count_case_surfaces_unspecified_modality_program_without_numeric_units():
    parsed, calculations = _analyze_imaging_center(
        "New 12,000 SF imaging center in Nashville, TN",
        square_footage=12_000,
    )

    facility_metrics = calculations["facility_metrics"]
    per_unit = calculations["operational_metrics"]["per_unit"]
    project_info = calculations["project_info"]
    modality_program = facility_metrics["imaging_modality_program"]

    assert parsed["subtype"] == "imaging_center"
    assert "mri_suite_count" not in parsed
    assert "ct_suite_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert facility_metrics["unit_label"] == "unspecified modality program"
    assert "units" not in facility_metrics
    assert modality_program["state"] == "unspecified_modality_program"
    assert modality_program["total_specified_modality_suites"] is None
    assert per_unit["unit_label"] == "unspecified modality program"
    assert per_unit["units_source"] == "unspecified_modality_program"
    assert "units" not in per_unit
    assert project_info["unit_label"] == "unspecified modality program"
    assert project_info["unit_count_source"] == "unspecified_modality_program"
    assert project_info.get("unit_count") is None
    assert "scan rooms" not in _visible_imaging_payload(calculations)


def test_imaging_center_room_language_stays_out_of_scope_for_this_contract_reset():
    parsed = NLPService().extract_project_details(
        "New 12,000 SF imaging center with MRI and CT rooms in Nashville, TN"
    )

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "imaging_center"
    assert "mri_suite_count" not in parsed
    assert "ct_suite_count" not in parsed
