from functools import lru_cache

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.engines.unified_engine import unified_engine


TRADE_LABELS = {
    "structural": "Structural",
    "mechanical": "Mechanical",
    "electrical": "Electrical",
    "plumbing": "Plumbing",
    "finishes": "Finishes",
}


def _default_count_baseline(rule, square_footage):
    bands = rule.get("default_count_bands") or []
    for band in bands:
        max_square_footage = band.get("max_square_footage")
        if max_square_footage is None or square_footage <= float(max_square_footage):
            return int(band["count"])

    default_count_rule = rule.get("default_count_rule") or {}
    if default_count_rule.get("type") == "dock_count":
        params = default_count_rule.get("params") or {}
        default_min = int(round(float(params.get("default_min", 1) or 1)))
        default_sf_per_dock = float(params.get("default_sf_per_dock", 10000.0) or 10000.0)
        return max(default_min, int(round(square_footage / default_sf_per_dock)))

    raise AssertionError("No matching warehouse dock baseline contract found")


def _scope_items_by_trade(payload):
    scope_items = payload.get("scope_items")
    assert isinstance(scope_items, list) and scope_items

    by_trade = {}
    for trade in scope_items:
        trade_label = trade.get("trade")
        systems = trade.get("systems") or []
        by_trade[trade_label] = {
            system["name"]: system
            for system in systems
            if isinstance(system, dict) and isinstance(system.get("name"), str)
        }
    return by_trade


def _trade_mix(payload):
    trade_breakdown = payload["trade_breakdown"]
    total = sum(float(value) for value in trade_breakdown.values())
    return {
        trade_key: float(trade_breakdown[trade_key]) / total
        for trade_key in TRADE_LABELS
    }


def _hard_cost_per_sf(payload, square_footage):
    return sum(float(value) for value in payload["trade_breakdown"].values()) / square_footage


@lru_cache(maxsize=None)
def _anchor_payload(subtype):
    return unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype=subtype,
        square_footage=150_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )


def test_warehouse_trade_weights_rebalanced_for_shell_story():
    config = get_building_config(BuildingType.INDUSTRIAL, "warehouse")

    assert config.trades.structural == pytest.approx(0.45)
    assert config.trades.mechanical == pytest.approx(0.12)
    assert config.trades.electrical == pytest.approx(0.19)
    assert config.trades.plumbing == pytest.approx(0.07)
    assert config.trades.finishes == pytest.approx(0.17)

    total = (
        config.trades.structural
        + config.trades.mechanical
        + config.trades.electrical
        + config.trades.plumbing
        + config.trades.finishes
    )
    assert total == pytest.approx(1.0)
    assert config.trades.structural < 0.48
    assert config.trades.finishes < 0.21
    assert config.trades.plumbing > 0.05


def test_warehouse_anchor_scope_rows_sum_cleanly_and_align_dock_default_with_baseline():
    payload = _anchor_payload("warehouse")
    scope_by_trade = _scope_items_by_trade(payload)
    config = get_building_config(BuildingType.INDUSTRIAL, "warehouse")

    for trade_key, trade_label in TRADE_LABELS.items():
        systems = scope_by_trade[trade_label].values()
        assert sum(float(system["total_cost"]) for system in systems) == pytest.approx(
            payload["trade_breakdown"][trade_key]
        )

    dock_baseline = _default_count_baseline(config.special_features["loading_docks"], 150_000)
    structural_dock_row = scope_by_trade["Structural"]["Dock pits and localized loading apron interface"]

    assert dock_baseline == 4
    assert structural_dock_row["quantity"] == dock_baseline
    assert structural_dock_row["total_cost"] / payload["trade_breakdown"]["structural"] == pytest.approx(0.10)
    assert _default_count_baseline(config.special_features["loading_docks"], 220_000) == 6


def test_warehouse_anchor_finishes_read_like_a_shell_not_a_support_space_package():
    payload = _anchor_payload("warehouse")
    scope_by_trade = _scope_items_by_trade(payload)
    finishes = scope_by_trade["Finishes"]

    office_row = finishes["Limited shipping office / restroom finish package"]
    floor_row = finishes["Warehouse floor sealer, striping, and wear protection"]
    dock_row = finishes["Dock doors, bumpers, seals, and safety bollards"]
    shell_row = finishes["Protective painting, interior doors, and shell accessory allowance"]

    assert office_row["quantity"] == pytest.approx(7_500.0)
    assert floor_row["quantity"] == pytest.approx(142_500.0)
    assert dock_row["quantity"] == 4
    assert shell_row["quantity"] == pytest.approx(142_500.0)

    assert office_row["total_cost"] / payload["trade_breakdown"]["finishes"] == pytest.approx(0.14)
    assert floor_row["total_cost"] / payload["trade_breakdown"]["finishes"] == pytest.approx(0.50)
    assert office_row["total_cost"] < dock_row["total_cost"] < floor_row["total_cost"]
    assert _hard_cost_per_sf(payload, 150_000) == pytest.approx(108.15)
    assert 100.0 < _hard_cost_per_sf(payload, 150_000) < 115.0


def test_distribution_center_remains_meaningfully_more_logistics_heavy_than_warehouse():
    warehouse_payload = _anchor_payload("warehouse")
    distribution_payload = _anchor_payload("distribution_center")

    warehouse_mix = _trade_mix(warehouse_payload)
    distribution_mix = _trade_mix(distribution_payload)
    warehouse_scope = _scope_items_by_trade(warehouse_payload)
    distribution_scope = _scope_items_by_trade(distribution_payload)

    assert warehouse_mix["structural"] == pytest.approx(0.45)
    assert warehouse_mix["finishes"] == pytest.approx(0.17)
    assert distribution_mix["structural"] == pytest.approx(0.50)
    assert distribution_mix["electrical"] == pytest.approx(0.20)

    assert warehouse_mix["structural"] < distribution_mix["structural"]
    assert warehouse_mix["electrical"] < distribution_mix["electrical"]
    assert warehouse_mix["plumbing"] > distribution_mix["plumbing"]

    assert warehouse_scope["Structural"]["Dock pits and localized loading apron interface"]["quantity"] == 4
    assert distribution_scope["Structural"]["Cross-dock aprons and truck court pavement transitions"]["quantity"] == 18
    assert distribution_scope["Structural"]["Dock leveler pits, edge steel, and bumper support"]["quantity"] == 18
    assert distribution_scope["Finishes"]["Dock doors, seals, bumpers, and edge-of-dock package"]["quantity"] == 18
    assert "Sortation conveyor power distribution and feeders" in distribution_scope["Electrical"]
    assert _hard_cost_per_sf(distribution_payload, 150_000) == pytest.approx(118.45)
    assert _hard_cost_per_sf(distribution_payload, 150_000) > _hard_cost_per_sf(warehouse_payload, 150_000)
