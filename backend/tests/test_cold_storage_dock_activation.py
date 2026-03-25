import asyncio
from typing import Dict, List, Optional, Tuple

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.v2.api.scope import AnalyzeRequest, analyze_project


DOCK_SCOPE_SYSTEMS: Tuple[Tuple[str, str], ...] = (
    ("Structural", "Cold dock pits, aprons, and canopies"),
    ("Finishes", "Cold dock doors, seals, and high-speed door package"),
)
COLD_STORAGE_BASELINE_DOCKS_AT_120K = 12.0
COLD_STORAGE_BASELINE_DOCKS_AT_150K = 15.0


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


def _analyze_cold_storage(
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


def _construction_view_scope_system(
    calculations: Dict[str, object],
    trade_label: str,
    system_name: str,
) -> Dict[str, object]:
    for trade in calculations["construction_view_scope_items"]:
        if not isinstance(trade, dict) or trade.get("trade") != trade_label:
            continue
        for system in trade.get("systems") or []:
            if isinstance(system, dict) and system.get("name") == system_name:
                return system
    raise AssertionError(f"Missing scope system: {trade_label} / {system_name}")


def test_cold_storage_explicit_numeric_dock_count_auto_activates_pricing_in_analyze_flow():
    parsed, calculations = _analyze_cold_storage(
        "New 120,000 SF cold storage facility with 12 dock doors in Nashville, TN",
        square_footage=120_000,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["loading_docks"]

    assert parsed["building_type"] == "industrial"
    assert parsed["subtype"] == "cold_storage"
    assert parsed["loading_dock_count"] == 12
    assert parsed["dock_door_count"] == 12
    assert parsed["dock_count"] == 12
    assert parsed["dock_doors"] == 12
    assert sorted(breakdown_by_id) == ["loading_docks"]
    assert row["requested_quantity"] == pytest.approx(12.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(COLD_STORAGE_BASELINE_DOCKS_AT_120K)
    assert row["included_baseline_quantity_source"] == "default_count_rule:dock_count"
    assert row["billed_quantity"] == pytest.approx(0.0)
    assert row["total_cost"] == pytest.approx(0.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert _construction_view_scope_system(calculations, trade_label, system_name)["quantity"] == 12


def test_cold_storage_higher_explicit_dock_count_prices_higher_and_preserves_scope_quantities():
    _, calculations_18 = _analyze_cold_storage(
        "150,000 SF cold storage building with 18 dock positions and freezer/cooler zones in Nashville, TN",
        square_footage=150_000,
    )
    _, calculations_20 = _analyze_cold_storage(
        "150,000 SF refrigerated warehouse with 20 loading docks in Nashville, TN",
        square_footage=150_000,
    )

    row_18 = _special_feature_breakdown_by_id(calculations_18)["loading_docks"]
    row_20 = _special_feature_breakdown_by_id(calculations_20)["loading_docks"]

    assert row_18["requested_quantity_source"] == "explicit_override:dock_doors"
    assert row_18["included_baseline_quantity"] == pytest.approx(COLD_STORAGE_BASELINE_DOCKS_AT_150K)
    assert row_18["billed_quantity"] == pytest.approx(3.0)
    assert row_18["total_cost"] == pytest.approx(300_000.0)
    assert row_20["requested_quantity"] == pytest.approx(20.0)
    assert row_20["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row_20["included_baseline_quantity"] == pytest.approx(COLD_STORAGE_BASELINE_DOCKS_AT_150K)
    assert row_20["billed_quantity"] == pytest.approx(5.0)
    assert row_20["total_cost"] == pytest.approx(500_000.0)
    assert row_20["total_cost"] > row_18["total_cost"]
    assert calculations_20["construction_costs"]["special_features_total"] > (
        calculations_18["construction_costs"]["special_features_total"]
    )
    assert calculations_20["totals"]["hard_costs"] > calculations_18["totals"]["hard_costs"]
    assert calculations_20["totals"]["total_project_cost"] > calculations_18["totals"]["total_project_cost"]

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert _construction_view_scope_system(calculations_18, trade_label, system_name)["quantity"] == 18
        assert _construction_view_scope_system(calculations_20, trade_label, system_name)["quantity"] == 20


def test_cold_storage_without_explicit_dock_count_preserves_no_premium_behavior_and_aligned_baseline():
    parsed, calculations = _analyze_cold_storage(
        "150,000 SF refrigerated warehouse in Nashville, TN",
        square_footage=150_000,
    )

    pricing_by_id = _available_special_feature_pricing_by_id(calculations)
    dock_pricing_row = pricing_by_id["loading_docks"]

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert dock_pricing_row["requested_quantity"] == pytest.approx(COLD_STORAGE_BASELINE_DOCKS_AT_150K)
    assert dock_pricing_row["requested_quantity_source"] == "default_count_rule:dock_count"
    assert dock_pricing_row["included_baseline_quantity"] == pytest.approx(
        COLD_STORAGE_BASELINE_DOCKS_AT_150K
    )
    assert dock_pricing_row["included_baseline_quantity_source"] == "default_count_rule:dock_count"

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert (
            _construction_view_scope_system(calculations, trade_label, system_name)["quantity"]
            == COLD_STORAGE_BASELINE_DOCKS_AT_150K
        )


def test_cold_storage_qualitative_dock_language_does_not_auto_activate_pricing():
    parsed, calculations = _analyze_cold_storage(
        "150,000 SF refrigerated warehouse with lots of loading docks in Nashville, TN",
        square_footage=150_000,
    )

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_cold_storage_manual_loading_docks_selection_does_not_regress():
    parsed, calculations = _analyze_cold_storage(
        "150,000 SF cold storage building with 18 dock positions and freezer/cooler zones in Nashville, TN",
        square_footage=150_000,
        special_features=["loading_docks"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["loading_docks"]

    assert parsed["dock_doors"] == 18
    assert sorted(breakdown_by_id) == ["loading_docks"]
    assert row["requested_quantity"] == pytest.approx(18.0)
    assert row["requested_quantity_source"] == "explicit_override:dock_doors"
    assert row["included_baseline_quantity"] == pytest.approx(COLD_STORAGE_BASELINE_DOCKS_AT_150K)
    assert row["included_baseline_quantity_source"] == "default_count_rule:dock_count"
    assert row["billed_quantity"] == pytest.approx(3.0)
    assert row["total_cost"] == pytest.approx(300_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(300_000.0)
