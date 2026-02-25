import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_content import parking as parking_content_profiles
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import parking as parking_tile_profiles
from app.v2.config.type_profiles import scope_items as shared_scope_registry
from app.v2.config.type_profiles.scope_items import parking as parking_scope_profiles
from app.v2.engines.unified_engine import unified_engine


PARKING_PROFILE_MAP = {
    "surface_parking": {
        "tile": "parking_surface_parking_v1",
        "scope": "parking_surface_parking_structural_v1",
    },
    "parking_garage": {
        "tile": "parking_parking_garage_v1",
        "scope": "parking_parking_garage_structural_v1",
    },
    "underground_parking": {
        "tile": "parking_underground_parking_v1",
        "scope": "parking_underground_parking_structural_v1",
    },
    "automated_parking": {
        "tile": "parking_automated_parking_v1",
        "scope": "parking_automated_parking_structural_v1",
    },
}


PARKING_SCOPE_DEPTH_FLOOR = {
    "surface_parking": {"structural": 4, "mechanical": 3, "electrical": 4, "plumbing": 2, "finishes": 2},
    "parking_garage": {"structural": 5, "mechanical": 4, "electrical": 5, "plumbing": 2, "finishes": 3},
    "underground_parking": {"structural": 6, "mechanical": 5, "electrical": 5, "plumbing": 3, "finishes": 3},
    "automated_parking": {"structural": 5, "mechanical": 5, "electrical": 6, "plumbing": 2, "finishes": 3},
}


def _scope_trade_map(profile_id: str) -> dict[str, dict]:
    profile = parking_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    return {
        trade.get("trade_key"): trade
        for trade in profile.get("trade_profiles", [])
        if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
    }


def _resolve_scope_profile_from_shared_registry(profile_id: str) -> dict:
    for source in shared_scope_registry.SCOPE_ITEM_PROFILE_SOURCES:
        if isinstance(source, dict) and profile_id in source:
            return source[profile_id]
    raise KeyError(profile_id)


def _resolve_scope_default_from_shared_registry(subtype: str) -> str:
    for source in shared_scope_registry.SCOPE_ITEM_DEFAULT_SOURCES:
        if isinstance(source, dict) and subtype in source:
            return source[subtype]
    raise KeyError(subtype)


def test_parking_subtypes_wire_explicit_tile_and_scope_profiles():
    for subtype, expected in PARKING_PROFILE_MAP.items():
        config = get_building_config(BuildingType.PARKING, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_parking_registries_and_defaults_are_non_empty_and_deterministic():
    assert parking_tile_profiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: expected["tile"] for subtype, expected in PARKING_PROFILE_MAP.items()
    }
    assert parking_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope"] for subtype, expected in PARKING_PROFILE_MAP.items()
    }

    assert parking_tile_profiles.DEALSHIELD_TILE_PROFILES
    assert parking_content_profiles.DEALSHIELD_CONTENT_PROFILES
    assert parking_scope_profiles.SCOPE_ITEM_PROFILES


def test_parking_content_profiles_resolve_via_shared_registry_lookup():
    for expected in PARKING_PROFILE_MAP.values():
        profile_id = expected["tile"]
        direct_profile = get_dealshield_content_profile(profile_id)
        module_profile = parking_content_profiles.DEALSHIELD_CONTENT_PROFILES[profile_id]
        assert direct_profile == module_profile
        assert direct_profile.get("profile_id") == profile_id


def test_parking_scope_profiles_resolve_via_shared_scope_registry_lookup():
    for subtype, expected in PARKING_PROFILE_MAP.items():
        profile_id = expected["scope"]
        direct_profile = _resolve_scope_profile_from_shared_registry(profile_id)
        module_profile = parking_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        assert direct_profile == module_profile

        default_profile_id = _resolve_scope_default_from_shared_registry(subtype)
        assert default_profile_id == profile_id


def test_parking_tile_profiles_are_subtype_authored_not_clones():
    unique_tiles = set()
    unique_rows = set()

    for expected in PARKING_PROFILE_MAP.values():
        profile = get_dealshield_profile(expected["tile"])
        assert profile["version"] == "v1"

        tile_ids = [tile["tile_id"] for tile in profile["tiles"]]
        assert {"cost_plus_10", "revenue_minus_10"}.issubset(set(tile_ids))
        unique_tile_ids = [tile_id for tile_id in tile_ids if tile_id not in {"cost_plus_10", "revenue_minus_10"}]
        assert len(unique_tile_ids) == 1
        unique_tiles.add(unique_tile_ids[0])

        row_ids = {row["row_id"] for row in profile.get("derived_rows", []) if isinstance(row, dict)}
        subtype_rows = row_ids - {"conservative", "ugly"}
        assert len(subtype_rows) == 1
        unique_rows.update(subtype_rows)

    assert len(unique_tiles) == len(PARKING_PROFILE_MAP)
    assert len(unique_rows) == len(PARKING_PROFILE_MAP)


def test_parking_content_to_tile_integrity():
    first_mlw_texts = []
    for expected in PARKING_PROFILE_MAP.values():
        profile_id = expected["tile"]
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = parking_content_profiles.DEALSHIELD_CONTENT_PROFILES[profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        first_mlw_texts.append(mlw[0].get("text"))
        for item in mlw:
            assert item.get("driver_tile_id") in tile_ids
            assert isinstance(item.get("text"), str) and item["text"].strip()
            assert isinstance(item.get("why"), str) and item["why"].strip()

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for entry in question_bank:
            assert entry.get("driver_tile_id") in tile_ids
            questions = entry.get("questions")
            assert isinstance(questions, list) and len(questions) >= 2

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_parking_scope_profiles_meet_depth_floor_and_normalized_shares():
    signatures = set()

    for subtype, expected in PARKING_PROFILE_MAP.items():
        trade_map = _scope_trade_map(expected["scope"])
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in PARKING_SCOPE_DEPTH_FLOOR[subtype].items():
            items = trade_map[trade_key].get("items")
            assert isinstance(items, list) and len(items) >= minimum
            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total expected 1.0, got {total_share}"
            )

        signature = tuple(
            (trade_key, tuple(item["key"] for item in trade_map[trade_key].get("items", [])))
            for trade_key in sorted(trade_map.keys())
        )
        signatures.add(signature)

    assert len(signatures) == len(PARKING_PROFILE_MAP)


def test_parking_runtime_payload_and_scope_trade_reconciliation():
    for subtype, expected in PARKING_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.PARKING,
            subtype=subtype,
            square_footage=110_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )

        assert payload.get("dealshield_tile_profile") == expected["tile"]
        assert payload.get("scope_items_profile") == expected["scope"]

        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items
        by_trade = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum in PARKING_SCOPE_DEPTH_FLOOR[subtype].items():
            systems = by_trade[trade_key].get("systems")
            if not isinstance(systems, list):
                systems = by_trade[trade_key].get("items")
            assert isinstance(systems, list) and len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)


def test_parking_runtime_emits_scenario_snapshots_and_provenance():
    for subtype, expected in PARKING_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.PARKING,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scenario_block = payload.get("dealshield_scenarios")
        assert isinstance(scenario_block, dict)
        assert scenario_block.get("profile_id") == expected["tile"]

        scenarios = scenario_block.get("scenarios")
        assert isinstance(scenarios, dict)
        assert {"base", "conservative", "ugly"}.issubset(set(scenarios.keys()))
        assert len(scenarios) == 4

        provenance = scenario_block.get("provenance")
        assert isinstance(provenance, dict)
        assert provenance.get("profile_id") == expected["tile"]
        scenario_inputs = provenance.get("scenario_inputs")
        assert isinstance(scenario_inputs, dict)
        assert set(scenario_inputs.keys()) == set(scenarios.keys())


def test_parking_economics_survive_ownership_fallback_without_nulling_revenue_or_noi():
    for subtype in PARKING_PROFILE_MAP.keys():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.PARKING,
            subtype=subtype,
            square_footage=95_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            ownership_type="public",
        )

        revenue = payload.get("revenue_analysis")
        assert isinstance(revenue, dict)
        assert isinstance(revenue.get("annual_revenue"), (int, float))
        assert isinstance(revenue.get("net_income"), (int, float))
        assert revenue.get("annual_revenue") is not None
        assert revenue.get("net_income") is not None

        return_metrics = payload.get("return_metrics")
        assert isinstance(return_metrics, dict)
        assert isinstance(return_metrics.get("estimated_annual_noi"), (int, float))

        ownership = payload.get("ownership_analysis")
        assert isinstance(ownership, dict)
        debt_metrics = ownership.get("debt_metrics")
        assert isinstance(debt_metrics, dict)
        assert isinstance(debt_metrics.get("calculated_dscr"), (int, float))
