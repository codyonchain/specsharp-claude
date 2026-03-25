import asyncio
from typing import Dict, List, Optional, Tuple

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.v2.api.scope import AnalyzeRequest, analyze_project


DOCK_SCOPE_SYSTEMS: Tuple[Tuple[str, str], ...] = (
    ("Structural", "Dock pits and localized loading apron interface"),
    ("Finishes", "Dock doors, bumpers, seals, and safety bollards"),
)
WAREHOUSE_BASELINE_DOCKS_AT_220K = 6.0


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


def _analyze_warehouse(
    description: str,
    *,
    square_footage: int = 220_000,
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


def _warehouse_description(square_footage: int, dock_count: Optional[int] = None) -> str:
    dock_clause = ""
    if dock_count is not None:
        dock_clause = f" with {dock_count} dock doors,"

    return (
        f"New {square_footage:,} SF single-story Class A warehouse"
        f"{dock_clause} 32-foot clear height, trailer parking, "
        "and ESFR fire protection in Nashville, TN"
    )


def test_warehouse_explicit_numeric_dock_count_auto_activates_pricing_in_analyze_flow():
    parsed, calculations = _analyze_warehouse(_warehouse_description(220_000, 10))

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["loading_docks"]

    assert parsed["building_type"] == "industrial"
    assert parsed["subtype"] == "warehouse"
    assert parsed["loading_dock_count"] == 10
    assert parsed["dock_door_count"] == 10
    assert parsed["dock_count"] == 10
    assert sorted(breakdown_by_id) == ["loading_docks"]
    assert row["requested_quantity"] == pytest.approx(10.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert row["included_baseline_quantity_source"] == "default_count_rule:dock_count"
    assert row["billed_quantity"] == pytest.approx(4.0)
    assert row["total_cost"] == pytest.approx(260_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(260_000.0)

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert _construction_view_scope_system(calculations, trade_label, system_name)["quantity"] == 10


def test_warehouse_higher_explicit_dock_count_prices_higher_and_preserves_scope_quantities():
    _, calculations_10 = _analyze_warehouse(_warehouse_description(220_000, 10))
    _, calculations_20 = _analyze_warehouse(
        "New 220,000 SF Class A warehouse with 20 loading docks and rear-load configuration "
        "in Nashville, TN"
    )

    row_10 = _special_feature_breakdown_by_id(calculations_10)["loading_docks"]
    row_20 = _special_feature_breakdown_by_id(calculations_20)["loading_docks"]

    assert row_10["included_baseline_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert row_20["included_baseline_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert row_10["billed_quantity"] == pytest.approx(4.0)
    assert row_10["total_cost"] == pytest.approx(260_000.0)
    assert row_20["requested_quantity"] == pytest.approx(20.0)
    assert row_20["billed_quantity"] == pytest.approx(14.0)
    assert row_20["total_cost"] == pytest.approx(910_000.0)
    assert row_20["total_cost"] > row_10["total_cost"]
    assert calculations_20["construction_costs"]["special_features_total"] > (
        calculations_10["construction_costs"]["special_features_total"]
    )
    assert calculations_20["totals"]["hard_costs"] > calculations_10["totals"]["hard_costs"]
    assert calculations_20["totals"]["total_project_cost"] > calculations_10["totals"]["total_project_cost"]

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert _construction_view_scope_system(calculations_10, trade_label, system_name)["quantity"] == 10
        assert _construction_view_scope_system(calculations_20, trade_label, system_name)["quantity"] == 20


def test_warehouse_without_explicit_dock_count_preserves_no_premium_behavior_and_aligned_baseline():
    parsed, calculations = _analyze_warehouse("220,000 SF warehouse in Nashville, TN")

    pricing_by_id = _available_special_feature_pricing_by_id(calculations)
    dock_pricing_row = pricing_by_id["loading_docks"]

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)
    assert dock_pricing_row["requested_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert dock_pricing_row["requested_quantity_source"] == "default_count_rule:dock_count"
    assert dock_pricing_row["included_baseline_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert dock_pricing_row["included_baseline_quantity_source"] == "default_count_rule:dock_count"

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert (
            _construction_view_scope_system(calculations, trade_label, system_name)["quantity"]
            == WAREHOUSE_BASELINE_DOCKS_AT_220K
        )


def test_warehouse_qualitative_dock_language_does_not_auto_activate_pricing():
    parsed, calculations = _analyze_warehouse(
        "220,000 SF warehouse with lots of loading docks and rear-load configuration in Nashville, TN"
    )

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_warehouse_manual_loading_docks_selection_does_not_regress():
    parsed, calculations = _analyze_warehouse(
        "New 220,000 SF Class A warehouse with 20 loading docks and rear-load configuration "
        "in Nashville, TN",
        special_features=["loading_docks"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["loading_docks"]

    assert parsed["loading_dock_count"] == 20
    assert sorted(breakdown_by_id) == ["loading_docks"]
    assert row["requested_quantity"] == pytest.approx(20.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(WAREHOUSE_BASELINE_DOCKS_AT_220K)
    assert row["included_baseline_quantity_source"] == "default_count_rule:dock_count"
    assert row["billed_quantity"] == pytest.approx(14.0)
    assert row["total_cost"] == pytest.approx(910_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(910_000.0)
