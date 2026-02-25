import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_content import mixed_use as mixed_use_content_profiles
from app.v2.config.type_profiles.decision_insurance_policy import DECISION_INSURANCE_POLICY_BY_PROFILE_ID
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import mixed_use as mixed_use_tile_profiles
from app.v2.config.type_profiles import scope_items as shared_scope_registry
from app.v2.config.type_profiles.scope_items import mixed_use as mixed_use_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_scenarios import WAVE1_PROFILES
from app.v2.services.dealshield_service import build_dealshield_view_model


MIXED_USE_PROFILE_MAP = {
    "office_residential": {
        "tile": "mixed_use_office_residential_v1",
        "scope": "mixed_use_office_residential_structural_v1",
    },
    "retail_residential": {
        "tile": "mixed_use_retail_residential_v1",
        "scope": "mixed_use_retail_residential_structural_v1",
    },
    "hotel_retail": {
        "tile": "mixed_use_hotel_retail_v1",
        "scope": "mixed_use_hotel_retail_structural_v1",
    },
    "transit_oriented": {
        "tile": "mixed_use_transit_oriented_v1",
        "scope": "mixed_use_transit_oriented_structural_v1",
    },
    "urban_mixed": {
        "tile": "mixed_use_urban_mixed_v1",
        "scope": "mixed_use_urban_mixed_structural_v1",
    },
}

MIXED_USE_SCOPE_DEPTH_FLOOR = {
    "office_residential": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "retail_residential": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "hotel_retail": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "transit_oriented": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "urban_mixed": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
}


def _scope_trade_map(profile_id: str) -> dict[str, dict]:
    profile = mixed_use_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
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


def test_mixed_use_subtypes_wire_explicit_tile_and_scope_profiles():
    for subtype, expected in MIXED_USE_PROFILE_MAP.items():
        config = get_building_config(BuildingType.MIXED_USE, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_mixed_use_registries_and_defaults_are_non_empty_and_deterministic():
    assert mixed_use_tile_profiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: expected["tile"] for subtype, expected in MIXED_USE_PROFILE_MAP.items()
    }
    assert mixed_use_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope"] for subtype, expected in MIXED_USE_PROFILE_MAP.items()
    }

    assert mixed_use_tile_profiles.DEALSHIELD_TILE_PROFILES
    assert mixed_use_content_profiles.DEALSHIELD_CONTENT_PROFILES
    assert mixed_use_scope_profiles.SCOPE_ITEM_PROFILES


def test_mixed_use_content_profiles_resolve_via_shared_registry_lookup():
    for expected in MIXED_USE_PROFILE_MAP.values():
        profile_id = expected["tile"]
        direct_profile = get_dealshield_content_profile(profile_id)
        module_profile = mixed_use_content_profiles.DEALSHIELD_CONTENT_PROFILES[profile_id]
        assert direct_profile == module_profile
        assert direct_profile.get("profile_id") == profile_id


def test_mixed_use_scope_profiles_resolve_via_shared_scope_registry_lookup():
    for subtype, expected in MIXED_USE_PROFILE_MAP.items():
        profile_id = expected["scope"]
        direct_profile = _resolve_scope_profile_from_shared_registry(profile_id)
        module_profile = mixed_use_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        assert direct_profile == module_profile

        default_profile_id = _resolve_scope_default_from_shared_registry(subtype)
        assert default_profile_id == profile_id


def test_mixed_use_tile_profiles_are_subtype_authored_not_clones():
    unique_tiles = set()
    unique_rows = set()
    for expected in MIXED_USE_PROFILE_MAP.values():
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

    assert len(unique_tiles) == len(MIXED_USE_PROFILE_MAP)
    assert len(unique_rows) == len(MIXED_USE_PROFILE_MAP)


def test_mixed_use_content_to_tile_integrity():
    first_mlw_texts = []
    for expected in MIXED_USE_PROFILE_MAP.values():
        profile_id = expected["tile"]
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = mixed_use_content_profiles.DEALSHIELD_CONTENT_PROFILES[profile_id]
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


def test_mixed_use_scope_profiles_meet_depth_floor_and_normalized_shares():
    signatures = set()
    for subtype, expected in MIXED_USE_PROFILE_MAP.items():
        trade_map = _scope_trade_map(expected["scope"])
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in MIXED_USE_SCOPE_DEPTH_FLOOR[subtype].items():
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

    assert len(signatures) == len(MIXED_USE_PROFILE_MAP)


def test_mixed_use_runtime_payload_and_view_model_resolve_profiles():
    for subtype, expected in MIXED_USE_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MIXED_USE,
            subtype=subtype,
            square_footage=125_000,
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
        for trade_key, minimum in MIXED_USE_SCOPE_DEPTH_FLOOR[subtype].items():
            systems = by_trade[trade_key].get("systems")
            assert isinstance(systems, list) and len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)

        profile = get_dealshield_profile(expected["tile"])
        view_model = build_dealshield_view_model(
            project_id=f"mixed-use-stage1-{subtype}",
            payload=payload,
            profile=profile,
        )
        assert view_model.get("tile_profile_id") == expected["tile"]
        assert view_model.get("content_profile_id") == expected["tile"]
        assert view_model.get("scope_items_profile_id") == expected["scope"]


def test_mixed_use_di_policy_and_wave1_gates_cover_all_profiles():
    for expected in MIXED_USE_PROFILE_MAP.values():
        profile_id = expected["tile"]
        assert profile_id in DECISION_INSURANCE_POLICY_BY_PROFILE_ID
        assert profile_id in WAVE1_PROFILES


def test_mixed_use_scenario_provenance_includes_split_inputs_and_source():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="office_residential",
        square_footage=140_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {
                "components": {"office": 70.0},
                "pattern": "component_percent",
            },
            "description": "Mixed-use office and residential with 70% office split",
        },
    )

    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "user_input"
    assert split.get("normalization_applied") is True
    assert split.get("value", {}).get("office") == pytest.approx(70.0)
    assert split.get("value", {}).get("residential") == pytest.approx(30.0)

    scenarios = payload.get("dealshield_scenarios")
    assert isinstance(scenarios, dict)
    provenance = scenarios.get("provenance")
    assert isinstance(provenance, dict)
    scenario_inputs = provenance.get("scenario_inputs")
    assert isinstance(scenario_inputs, dict) and scenario_inputs

    for scenario_input in scenario_inputs.values():
        assert scenario_input.get("mixed_use_split_source") == "user_input"
        split_input = scenario_input.get("mixed_use_split")
        assert isinstance(split_input, dict)
        assert split_input.get("value", {}).get("office") == pytest.approx(70.0)


def test_mixed_use_first_break_metric_units_are_truthful_per_profile():
    for subtype, expected in MIXED_USE_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MIXED_USE,
            subtype=subtype,
            square_footage=125_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected["tile"])
        view_model = build_dealshield_view_model(
            project_id=f"mixed-use-stage4-first-break-{subtype}",
            payload=payload,
            profile=profile,
        )

        first_break = view_model.get("first_break_condition")
        assert isinstance(first_break, dict)
        break_metric = first_break.get("break_metric")
        assert break_metric in {"value_gap_pct", "value_gap"}
        assert isinstance(first_break.get("threshold"), (int, float))
        assert isinstance(first_break.get("observed_value"), (int, float))

        observed_value_pct = first_break.get("observed_value_pct")
        if break_metric == "value_gap_pct":
            assert isinstance(observed_value_pct, (int, float))
        else:
            assert observed_value_pct is None or isinstance(observed_value_pct, (int, float))


def test_mixed_use_split_provenance_is_deterministic_across_recompute():
    kwargs = dict(
        building_type=BuildingType.MIXED_USE,
        subtype="retail_residential",
        square_footage=110_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {
                "components": {"retail": 40},
                "pattern": "component_percent",
            },
            "description": "mixed-use retail and residential podium with 40 percent retail",
        },
    )
    payload_a = unified_engine.calculate_project(**kwargs)
    payload_b = unified_engine.calculate_project(**kwargs)

    split_a = payload_a.get("mixed_use_split")
    split_b = payload_b.get("mixed_use_split")
    assert isinstance(split_a, dict)
    assert split_a == split_b
    assert split_a.get("source") == "user_input"
    assert split_a.get("normalization_applied") is True
    assert split_a.get("value", {}).get("retail") == pytest.approx(40.0)
    assert split_a.get("value", {}).get("residential") == pytest.approx(60.0)

    scenario_inputs_a = (
        payload_a.get("dealshield_scenarios", {})
        .get("provenance", {})
        .get("scenario_inputs", {})
    )
    scenario_inputs_b = (
        payload_b.get("dealshield_scenarios", {})
        .get("provenance", {})
        .get("scenario_inputs", {})
    )
    assert isinstance(scenario_inputs_a, dict) and scenario_inputs_a
    assert isinstance(scenario_inputs_b, dict) and scenario_inputs_b
    assert sorted(scenario_inputs_a.keys()) == sorted(scenario_inputs_b.keys())

    for scenario_id in scenario_inputs_a.keys():
        scenario_a = scenario_inputs_a[scenario_id]
        scenario_b = scenario_inputs_b[scenario_id]
        assert scenario_a.get("mixed_use_split_source") == "user_input"
        assert scenario_a.get("mixed_use_split_source") == scenario_b.get("mixed_use_split_source")

        split_input_a = scenario_a.get("mixed_use_split")
        split_input_b = scenario_b.get("mixed_use_split")
        assert isinstance(split_input_a, dict)
        assert isinstance(split_input_b, dict)
        assert split_input_a == split_input_b
        assert split_input_a.get("value", {}).get("retail") == pytest.approx(40.0)
        assert split_input_a.get("value", {}).get("residential") == pytest.approx(60.0)
