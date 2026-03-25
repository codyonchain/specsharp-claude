import asyncio
from typing import Dict, List, Optional, Tuple

import pytest
from starlette.requests import Request

from app.core.auth import build_testing_auth_context
from app.v2.api.scope import AnalyzeRequest, analyze_project


DOCK_SCOPE_SYSTEMS: Tuple[Tuple[str, str], ...] = (
    ("Structural", "Cross-dock aprons and truck court pavement transitions"),
    ("Structural", "Dock leveler pits, edge steel, and bumper support"),
    ("Finishes", "Dock doors, seals, bumpers, and edge-of-dock package"),
)
LEGACY_INCLUDED_DOCK_BASELINE = 8.0


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


def _analyze_distribution_center(
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


def _distribution_center_description(square_footage: int, dock_count: Optional[int] = None) -> str:
    dock_clause = ""
    if dock_count is not None:
        dock_clause = f", {dock_count} dock doors"

    return (
        f"New {square_footage:,} SF single-story Class A distribution center "
        f"with cross-dock loading{dock_clause}, 36-foot clear height, "
        "trailer parking, and ESFR fire protection in Nashville, TN"
    )


@pytest.mark.parametrize(
    ("square_footage", "expected_baseline_quantity", "expected_billed_quantity", "expected_total_cost"),
    (
        (200_000, 24.0, 16.0, 800_000.0),
        (220_000, 26.0, 14.0, 700_000.0),
    ),
)
def test_distribution_center_explicit_numeric_dock_count_auto_activates_pricing_in_analyze_flow(
    square_footage: int,
    expected_baseline_quantity: float,
    expected_billed_quantity: float,
    expected_total_cost: float,
):
    parsed, calculations = _analyze_distribution_center(
        _distribution_center_description(square_footage, 40),
        square_footage=square_footage,
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["extra_loading_docks"]
    legacy_billed_quantity = 40.0 - LEGACY_INCLUDED_DOCK_BASELINE

    assert parsed["building_type"] == "industrial"
    assert parsed["subtype"] == "distribution_center"
    assert parsed["loading_dock_count"] == 40
    assert parsed["dock_door_count"] == 40
    assert parsed["dock_count"] == 40
    assert sorted(breakdown_by_id) == ["extra_loading_docks"]
    assert row["requested_quantity"] == pytest.approx(40.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(expected_baseline_quantity)
    assert row["included_baseline_quantity_source"] == "size_band_default"
    assert row["included_baseline_quantity"] > LEGACY_INCLUDED_DOCK_BASELINE
    assert row["billed_quantity"] == pytest.approx(expected_billed_quantity)
    assert row["billed_quantity"] < legacy_billed_quantity
    assert row["total_cost"] == pytest.approx(expected_total_cost)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(
        expected_total_cost
    )


@pytest.mark.parametrize(
    (
        "square_footage",
        "expected_baseline_quantity",
        "expected_billed_quantity_40",
        "expected_total_cost_40",
        "expected_billed_quantity_60",
        "expected_total_cost_60",
    ),
    (
        (200_000, 24.0, 16.0, 800_000.0, 36.0, 1_800_000.0),
        (220_000, 26.0, 14.0, 700_000.0, 34.0, 1_700_000.0),
    ),
)
def test_distribution_center_higher_explicit_dock_count_prices_higher_and_preserves_scope_quantities(
    square_footage: int,
    expected_baseline_quantity: float,
    expected_billed_quantity_40: float,
    expected_total_cost_40: float,
    expected_billed_quantity_60: float,
    expected_total_cost_60: float,
):
    _, calculations_40 = _analyze_distribution_center(
        _distribution_center_description(square_footage, 40),
        square_footage=square_footage,
    )
    _, calculations_60 = _analyze_distribution_center(
        _distribution_center_description(square_footage, 60),
        square_footage=square_footage,
    )

    row_40 = _special_feature_breakdown_by_id(calculations_40)["extra_loading_docks"]
    row_60 = _special_feature_breakdown_by_id(calculations_60)["extra_loading_docks"]

    assert row_40["included_baseline_quantity"] == pytest.approx(expected_baseline_quantity)
    assert row_60["included_baseline_quantity"] == pytest.approx(expected_baseline_quantity)
    assert row_40["billed_quantity"] == pytest.approx(expected_billed_quantity_40)
    assert row_40["total_cost"] == pytest.approx(expected_total_cost_40)
    assert row_60["requested_quantity"] == pytest.approx(60.0)
    assert row_60["billed_quantity"] == pytest.approx(expected_billed_quantity_60)
    assert row_60["total_cost"] == pytest.approx(expected_total_cost_60)
    assert row_60["total_cost"] > row_40["total_cost"]
    assert calculations_60["construction_costs"]["special_features_total"] > (
        calculations_40["construction_costs"]["special_features_total"]
    )
    assert calculations_60["totals"]["hard_costs"] > calculations_40["totals"]["hard_costs"]
    assert calculations_60["totals"]["total_project_cost"] > calculations_40["totals"]["total_project_cost"]

    for trade_label, system_name in DOCK_SCOPE_SYSTEMS:
        assert _construction_view_scope_system(calculations_40, trade_label, system_name)["quantity"] == 40
        assert _construction_view_scope_system(calculations_60, trade_label, system_name)["quantity"] == 60


def test_distribution_center_without_explicit_dock_count_preserves_current_pricing_behavior():
    parsed, calculations = _analyze_distribution_center(
        "220,000 SF distribution center in Nashville, TN"
    )

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_distribution_center_qualitative_dock_language_does_not_auto_activate_pricing():
    parsed, calculations = _analyze_distribution_center(
        "220,000 SF distribution center with lots of dock doors in Nashville, TN"
    )

    assert "loading_dock_count" not in parsed
    assert _special_feature_breakdown_by_id(calculations) == {}
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(0.0)


def test_distribution_center_manual_extra_loading_docks_selection_does_not_regress():
    parsed, calculations = _analyze_distribution_center(
        _distribution_center_description(220_000, 40),
        special_features=["extra_loading_docks"],
    )

    breakdown_by_id = _special_feature_breakdown_by_id(calculations)
    row = breakdown_by_id["extra_loading_docks"]

    assert parsed["loading_dock_count"] == 40
    assert sorted(breakdown_by_id) == ["extra_loading_docks"]
    assert row["requested_quantity"] == pytest.approx(40.0)
    assert row["requested_quantity_source"] == "explicit_override:loading_dock_count"
    assert row["included_baseline_quantity"] == pytest.approx(26.0)
    assert row["billed_quantity"] == pytest.approx(14.0)
    assert row["total_cost"] == pytest.approx(700_000.0)
    assert calculations["construction_costs"]["special_features_total"] == pytest.approx(700_000.0)
