import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_BY_PROFILE_ID,
    DECISION_INSURANCE_POLICY_ID,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import retail as retail_tile_profiles
from app.v2.config.type_profiles.dealshield_content import retail as retail_content_profiles
from app.v2.config.type_profiles.scope_items import retail as retail_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


RETAIL_PROFILE_MAP = {
    "shopping_center": {
        "tile": "retail_shopping_center_v1",
        "scope": "retail_shopping_center_structural_v1",
    },
    "big_box": {
        "tile": "retail_big_box_v1",
        "scope": "retail_big_box_structural_v1",
    },
}

RETAIL_SCOPE_DEPTH_FLOOR = {
    "shopping_center": {
        "structural": 4,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 3,
        "finishes": 4,
    },
    "big_box": {
        "structural": 5,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 3,
        "finishes": 4,
    },
}

RETAIL_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}


def _scope_trade_map(profile_id: str) -> dict[str, dict]:
    profile = retail_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    return {
        trade.get("trade_key"): trade
        for trade in profile.get("trade_profiles", [])
        if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
    }


def test_retail_subtypes_wire_explicit_tile_and_scope_profiles():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        config = get_building_config(BuildingType.RETAIL, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_retail_registries_and_defaults_are_non_empty_and_deterministic():
    assert retail_tile_profiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: expected["tile"] for subtype, expected in RETAIL_PROFILE_MAP.items()
    }
    assert retail_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope"] for subtype, expected in RETAIL_PROFILE_MAP.items()
    }

    assert retail_tile_profiles.DEALSHIELD_TILE_PROFILES
    assert retail_content_profiles.DEALSHIELD_CONTENT_PROFILES
    assert retail_scope_profiles.SCOPE_ITEM_PROFILES


def test_retail_content_profiles_resolve_via_shared_registry_lookup():
    for expected in RETAIL_PROFILE_MAP.values():
        profile_id = expected["tile"]
        direct_profile = get_dealshield_content_profile(profile_id)
        module_profile = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[profile_id]
        assert direct_profile == module_profile
        assert direct_profile.get("profile_id") == profile_id


def test_retail_scope_profiles_meet_depth_floor_and_normalized_shares():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        trade_map = _scope_trade_map(expected["scope"])
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in RETAIL_SCOPE_DEPTH_FLOOR[subtype].items():
            items = trade_map[trade_key].get("items")
            assert isinstance(items, list) and len(items) >= minimum
            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_retail_content_to_tile_integrity():
    for profile_id in RETAIL_PROFILE_MAP.values():
        resolved_profile_id = profile_id["tile"]
        tile_profile = get_dealshield_profile(resolved_profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[resolved_profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and drivers
        for driver in drivers:
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
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


def test_retail_profiles_are_authored_not_clones():
    shopping_tile = get_dealshield_profile(RETAIL_PROFILE_MAP["shopping_center"]["tile"])
    big_box_tile = get_dealshield_profile(RETAIL_PROFILE_MAP["big_box"]["tile"])

    assert shopping_tile["tiles"][2]["tile_id"] != big_box_tile["tiles"][2]["tile_id"]

    shopping_rows = {row["row_id"] for row in shopping_tile["derived_rows"]}
    big_box_rows = {row["row_id"] for row in big_box_tile["derived_rows"]}
    assert shopping_rows != big_box_rows

    shopping_content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[RETAIL_PROFILE_MAP["shopping_center"]["tile"]]
    big_box_content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[RETAIL_PROFILE_MAP["big_box"]["tile"]]
    assert shopping_content["most_likely_wrong"][0]["text"] != big_box_content["most_likely_wrong"][0]["text"]
    assert shopping_content["fastest_change"]["drivers"][2]["label"] != big_box_content["fastest_change"]["drivers"][2]["label"]

    shopping_scope = _scope_trade_map(RETAIL_PROFILE_MAP["shopping_center"]["scope"])
    big_box_scope = _scope_trade_map(RETAIL_PROFILE_MAP["big_box"]["scope"])
    shopping_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(shopping_scope.items())
    )
    big_box_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(big_box_scope.items())
    )
    assert shopping_signature != big_box_signature


def test_retail_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for expected in RETAIL_PROFILE_MAP.values():
        profile_id = expected["tile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()

        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 35
        for generic_term in RETAIL_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_retail_policy_collapse_and_flex_semantics():
    collapse_metric_families = set()

    for subtype, expected in RETAIL_PROFILE_MAP.items():
        profile_id = expected["tile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        profile = get_dealshield_profile(profile_id)
        tile_map = {
            tile.get("tile_id"): tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        tile_id = primary_control.get("tile_id")
        assert tile_id in tile_map
        assert primary_control.get("metric_ref") == tile_map[tile_id].get("metric_ref")

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

        row_ids = {
            row.get("row_id")
            for row in profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        }
        subtype_rows = [
            scenario_id for scenario_id in scenario_priority
            if scenario_id not in {"base", "conservative", "ugly"}
        ]
        assert len(subtype_rows) == 1
        assert subtype_rows[0] in row_ids

        if subtype == "shopping_center":
            assert metric == "value_gap_pct"
            assert float(threshold) > 0.0
        else:
            assert metric == "value_gap"
            assert float(threshold) <= 0.0

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}


def test_retail_runtime_scope_depth_floor_and_trade_reconciliation():
    for subtype, expected_depth in RETAIL_SCOPE_DEPTH_FLOOR.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RETAIL,
            subtype=subtype,
            square_footage=120_000,
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


def test_retail_scenarios_emit_for_both_subtypes():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RETAIL,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected["tile"]

        scenarios = payload.get("dealshield_scenarios")
        assert isinstance(scenarios, dict)
        assert scenarios.get("profile_id") == expected["tile"]

        scenario_ids = scenarios.get("scenario_ids")
        if not isinstance(scenario_ids, list):
            provenance = scenarios.get("provenance")
            scenario_ids = provenance.get("scenario_ids") if isinstance(provenance, dict) else None
        assert isinstance(scenario_ids, list)
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_ids))

        profile = get_dealshield_profile(expected["tile"])
        subtype_rows = {
            row.get("row_id")
            for row in profile.get("derived_rows", [])
            if isinstance(row, dict)
            and isinstance(row.get("row_id"), str)
            and row.get("row_id") not in {"conservative", "ugly"}
        }
        assert len(subtype_rows) == 1
        assert subtype_rows.issubset(set(scenario_ids))


def test_retail_decision_insurance_contract_and_provenance_is_deterministic():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        payload_a = unified_engine.calculate_project(
            building_type=BuildingType.RETAIL,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_b = unified_engine.calculate_project(
            building_type=BuildingType.RETAIL,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )

        profile_id = expected["tile"]
        profile = get_dealshield_profile(profile_id)
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]

        view_model_a = build_dealshield_view_model(
            project_id=f"retail-policy-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_model_b = build_dealshield_view_model(
            project_id=f"retail-policy-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        for view_model in (view_model_a, view_model_b):
            assert view_model.get("scope_items_profile_id") == expected["scope"]
            assert view_model.get("decision_status") in {"GO", "Needs Work", "NO-GO", "PENDING"}
            assert isinstance(view_model.get("decision_reason_code"), str) and view_model.get("decision_reason_code")

            status_provenance = view_model.get("decision_status_provenance")
            assert isinstance(status_provenance, dict)
            assert status_provenance.get("status_source") == "dealshield_policy_v1"
            assert isinstance(status_provenance.get("policy_id"), str) and status_provenance.get("policy_id")

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

            flex_band = view_model.get("flex_before_break_band")
            assert flex_band in {"tight", "moderate", "comfortable"}

        assert view_model_a.get("decision_status") == view_model_b.get("decision_status")
        assert view_model_a.get("decision_reason_code") == view_model_b.get("decision_reason_code")
        assert view_model_a.get("decision_status_provenance") == view_model_b.get("decision_status_provenance")
