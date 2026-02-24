import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_BY_PROFILE_ID,
    DECISION_INSURANCE_POLICY_ID,
)
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import office as office_tile_profiles
from app.v2.config.type_profiles.dealshield_content import office as office_content_profiles
from app.v2.config.type_profiles.scope_items import office as office_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


OFFICE_PROFILE_MAP = {
    "class_a": {
        "tile": "office_class_a_v1",
        "scope": "office_class_a_structural_v1",
    },
    "class_b": {
        "tile": "office_class_b_v1",
        "scope": "office_class_b_structural_v1",
    },
}

OFFICE_SCOPE_DEPTH_FLOOR = {
    "class_a": {
        "structural": 5,
        "mechanical": 6,
        "electrical": 6,
        "plumbing": 5,
        "finishes": 6,
    },
    "class_b": {
        "structural": 5,
        "mechanical": 5,
        "electrical": 5,
        "plumbing": 5,
        "finishes": 5,
    },
}


def _scope_trade_map(profile_id: str) -> dict[str, dict]:
    profile = office_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    return {
        trade.get("trade_key"): trade
        for trade in profile.get("trade_profiles", [])
        if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
    }


def test_office_subtypes_wire_explicit_tile_and_scope_profiles():
    for subtype, expected in OFFICE_PROFILE_MAP.items():
        config = get_building_config(BuildingType.OFFICE, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_office_registries_and_defaults_are_non_empty_and_deterministic():
    assert office_tile_profiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: expected["tile"] for subtype, expected in OFFICE_PROFILE_MAP.items()
    }
    assert office_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope"] for subtype, expected in OFFICE_PROFILE_MAP.items()
    }

    assert office_tile_profiles.DEALSHIELD_TILE_PROFILES
    assert office_content_profiles.DEALSHIELD_CONTENT_PROFILES
    assert office_scope_profiles.SCOPE_ITEM_PROFILES


def test_office_scope_profiles_meet_depth_floor_and_normalized_shares():
    for subtype, expected in OFFICE_PROFILE_MAP.items():
        trade_map = _scope_trade_map(expected["scope"])
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in OFFICE_SCOPE_DEPTH_FLOOR[subtype].items():
            items = trade_map[trade_key].get("items")
            assert isinstance(items, list) and len(items) >= minimum
            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_office_content_to_tile_integrity():
    for profile_id in OFFICE_PROFILE_MAP.values():
        resolved_profile_id = profile_id["tile"]
        tile_profile = get_dealshield_profile(resolved_profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = office_content_profiles.DEALSHIELD_CONTENT_PROFILES[resolved_profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and drivers
        for driver in drivers:
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and mlw
        for item in mlw:
            assert item.get("driver_tile_id") in tile_ids
            assert isinstance(item.get("text"), str) and item["text"].strip()
            assert isinstance(item.get("why"), str) and item["why"].strip()

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and question_bank
        for entry in question_bank:
            assert entry.get("driver_tile_id") in tile_ids
            questions = entry.get("questions")
            assert isinstance(questions, list) and questions


def test_office_class_profiles_are_authored_not_clones():
    class_a_tile = get_dealshield_profile(OFFICE_PROFILE_MAP["class_a"]["tile"])
    class_b_tile = get_dealshield_profile(OFFICE_PROFILE_MAP["class_b"]["tile"])

    class_a_primary = class_a_tile["tiles"][2]["tile_id"]
    class_b_primary = class_b_tile["tiles"][2]["tile_id"]
    assert class_a_primary != class_b_primary

    class_a_rows = {row["row_id"] for row in class_a_tile["derived_rows"]}
    class_b_rows = {row["row_id"] for row in class_b_tile["derived_rows"]}
    assert class_a_rows != class_b_rows

    class_a_content = office_content_profiles.DEALSHIELD_CONTENT_PROFILES[OFFICE_PROFILE_MAP["class_a"]["tile"]]
    class_b_content = office_content_profiles.DEALSHIELD_CONTENT_PROFILES[OFFICE_PROFILE_MAP["class_b"]["tile"]]
    assert class_a_content["most_likely_wrong"][0]["text"] != class_b_content["most_likely_wrong"][0]["text"]
    assert class_a_content["fastest_change"]["drivers"][2]["label"] != class_b_content["fastest_change"]["drivers"][2]["label"]

    class_a_scope = _scope_trade_map(OFFICE_PROFILE_MAP["class_a"]["scope"])
    class_b_scope = _scope_trade_map(OFFICE_PROFILE_MAP["class_b"]["scope"])
    class_a_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(class_a_scope.items())
    )
    class_b_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(class_b_scope.items())
    )
    assert class_a_signature != class_b_signature


def test_office_runtime_scope_depth_floor_and_trade_reconciliation():
    for subtype, expected_depth in OFFICE_SCOPE_DEPTH_FLOOR.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.OFFICE,
            subtype=subtype,
            square_footage=85_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        by_trade = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum in expected_depth.items():
            systems = by_trade[trade_key].get("systems")
            assert isinstance(systems, list) and len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)


def test_office_scenarios_emit_for_both_subtypes():
    for subtype, expected in OFFICE_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.OFFICE,
            subtype=subtype,
            square_footage=85_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected["tile"]

        scenarios = payload.get("dealshield_scenarios")
        assert isinstance(scenarios, dict)
        assert scenarios.get("profile_id") == expected["tile"]

        scenario_payloads = scenarios.get("scenarios")
        assert isinstance(scenario_payloads, dict)
        assert "base" in scenario_payloads

        profile = get_dealshield_profile(expected["tile"])
        expected_row_ids = {
            row.get("row_id")
            for row in profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        }
        assert expected_row_ids
        assert expected_row_ids.issubset(set(scenario_payloads.keys()))


def test_office_decision_insurance_contract_and_provenance():
    for subtype, expected in OFFICE_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.OFFICE,
            subtype=subtype,
            square_footage=85_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile_id = expected["tile"]
        profile = get_dealshield_profile(profile_id)
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]

        view_model = build_dealshield_view_model(
            project_id=f"office-di-{subtype}",
            payload=payload,
            profile=profile,
        )

        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)

        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy["primary_control_variable"]["tile_id"]
        assert primary_control.get("metric_ref") == policy["primary_control_variable"]["metric_ref"]

        first_break = view_model.get("first_break_condition")
        first_break_provenance = di_provenance.get("first_break_condition")
        if (
            isinstance(first_break, dict)
            and isinstance(first_break_provenance, dict)
            and first_break_provenance.get("status") == "available"
            and first_break_provenance.get("source") == "decision_insurance_policy.collapse_trigger"
        ):
            collapse_trigger = policy["collapse_trigger"]
            assert first_break.get("break_metric") == collapse_trigger["metric"]
            assert first_break.get("threshold") == collapse_trigger["threshold"]
            assert first_break.get("operator") == collapse_trigger["operator"]

        flex_band = view_model.get("flex_before_break_band")
        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_band in {"tight", "moderate", "comfortable"}
