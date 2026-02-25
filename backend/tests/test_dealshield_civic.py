import math

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.construction_schedule import build_construction_schedule
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_BY_PROFILE_ID,
    DECISION_INSURANCE_POLICY_ID,
    get_decision_insurance_policy,
)
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import civic as civic_tiles
from app.v2.config.type_profiles.dealshield_content import civic as civic_content
from app.v2.config.type_profiles.scope_items import civic as civic_scope
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


CIVIC_PROFILE_MAP = {
    "library": {
        "tile": "civic_library_v1",
        "scope": "civic_library_structural_v1",
    },
    "courthouse": {
        "tile": "civic_courthouse_v1",
        "scope": "civic_courthouse_structural_v1",
    },
    "government_building": {
        "tile": "civic_government_building_v1",
        "scope": "civic_government_building_structural_v1",
    },
    "community_center": {
        "tile": "civic_community_center_v1",
        "scope": "civic_community_center_structural_v1",
    },
    "public_safety": {
        "tile": "civic_public_safety_v1",
        "scope": "civic_public_safety_structural_v1",
    },
}


CIVIC_SCOPE_MIN_ITEMS_BY_SUBTYPE = {
    "library": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "courthouse": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "government_building": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "community_center": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "public_safety": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
}


def test_civic_subtypes_wire_scope_and_tile_profiles_explicitly():
    for subtype, expected in CIVIC_PROFILE_MAP.items():
        cfg = get_building_config(BuildingType.CIVIC, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile"]
        assert cfg.scope_items_profile == expected["scope"]


def test_civic_defaults_map_to_matching_profile_ids():
    assert civic_tiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: values["tile"] for subtype, values in CIVIC_PROFILE_MAP.items()
    }
    scope_defaults = civic_scope.SCOPE_ITEM_DEFAULTS.get("default_profile_by_subtype")
    assert isinstance(scope_defaults, dict)
    assert scope_defaults == {
        subtype: values["scope"] for subtype, values in CIVIC_PROFILE_MAP.items()
    }


def test_civic_tile_profiles_are_subtype_authored_not_clones():
    primary_tile_ids = []
    derived_row_signatures = []

    for subtype, expected in CIVIC_PROFILE_MAP.items():
        profile = get_dealshield_profile(expected["tile"])
        assert profile.get("profile_id") == expected["tile"]

        tiles = profile.get("tiles")
        assert isinstance(tiles, list) and len(tiles) >= 4
        tile_ids = [tile.get("tile_id") for tile in tiles if isinstance(tile, dict)]
        assert all(isinstance(tile_id, str) and tile_id for tile_id in tile_ids)
        assert len(tile_ids) == len(set(tile_ids))

        rows = profile.get("derived_rows")
        assert isinstance(rows, list) and rows
        row_ids = tuple(
            row.get("row_id")
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        )
        assert "conservative" in row_ids
        assert "ugly" in row_ids
        assert any(row_id not in {"conservative", "ugly"} for row_id in row_ids)

        primary_tile_ids.append(tile_ids[0])
        derived_row_signatures.append((subtype, row_ids))

    assert len(primary_tile_ids) == len(set(primary_tile_ids))
    assert len({rows for _, rows in derived_row_signatures}) == len(derived_row_signatures)


def test_civic_content_to_tile_integrity():
    for profile_id, content_profile in civic_content.DEALSHIELD_CONTENT_PROFILES.items():
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        drivers = content_profile.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content_profile.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        for entry in mlw:
            assert isinstance(entry, dict)
            assert isinstance(entry.get("text"), str) and entry.get("text").strip()
            assert isinstance(entry.get("why"), str) and entry.get("why").strip()
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content_profile.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for group in question_bank:
            assert isinstance(group, dict)
            assert group.get("driver_tile_id") in tile_ids
            questions = group.get("questions")
            assert isinstance(questions, list) and questions


def test_civic_scope_profile_trade_item_depth_and_allocation_sum():
    for subtype, expected in CIVIC_PROFILE_MAP.items():
        profile = civic_scope.SCOPE_ITEM_PROFILES[expected["scope"]]
        assert profile.get("profile_id") == expected["scope"]

        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5
        trade_map = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, min_items in CIVIC_SCOPE_MIN_ITEMS_BY_SUBTYPE[subtype].items():
            trade = trade_map[trade_key]
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= min_items

            total_share = 0.0
            for item in items:
                assert isinstance(item, dict)
                allocation = item.get("allocation")
                assert isinstance(allocation, dict)
                assert allocation.get("type") == "share_of_trade"
                share = allocation.get("share")
                assert isinstance(share, (int, float))
                total_share += float(share)

            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total must equal 1.0, got {total_share}"
            )


def test_civic_no_clone_signatures_across_tile_content_and_scope():
    first_mlw_texts = []
    scope_signatures = []

    for subtype, expected in CIVIC_PROFILE_MAP.items():
        tile_profile = get_dealshield_profile(expected["tile"])
        tiles = tile_profile.get("tiles")
        assert isinstance(tiles, list) and tiles

        content_profile = civic_content.DEALSHIELD_CONTENT_PROFILES[expected["tile"]]
        mlw = content_profile.get("most_likely_wrong")
        assert isinstance(mlw, list) and mlw
        first_mlw_text = mlw[0].get("text")
        assert isinstance(first_mlw_text, str) and first_mlw_text.strip()
        first_mlw_texts.append(first_mlw_text.strip())

        scope_profile = civic_scope.SCOPE_ITEM_PROFILES[expected["scope"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.append(signature)

    assert len(first_mlw_texts) == len(set(first_mlw_texts))
    assert len(scope_signatures) == len(set(scope_signatures))


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_civic_runtime_emits_scenarios_and_truthful_provenance_for_all_profiles():
    for subtype, expected in CIVIC_PROFILE_MAP.items():
        expected_profile_id = expected["tile"]
        payload = unified_engine.calculate_project(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=65_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected_profile_id

        profile = get_dealshield_profile(expected_profile_id)
        derived_rows = profile.get("derived_rows", [])
        expected_scenario_ids = ["base"] + [
            row.get("row_id")
            for row in derived_rows
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        ]
        expected_metric_refs = [
            tile.get("metric_ref")
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("metric_ref"), str)
        ]

        scenarios_bundle = payload.get("dealshield_scenarios")
        assert isinstance(scenarios_bundle, dict)
        assert scenarios_bundle.get("profile_id") == expected_profile_id

        scenarios = scenarios_bundle.get("scenarios")
        assert isinstance(scenarios, dict)
        assert set(scenarios.keys()) == set(expected_scenario_ids)

        provenance = scenarios_bundle.get("provenance")
        assert isinstance(provenance, dict)
        assert provenance.get("profile_id") == expected_profile_id
        assert provenance.get("scenario_ids") == expected_scenario_ids
        assert provenance.get("tile_metric_refs") == expected_metric_refs

        scenario_inputs = provenance.get("scenario_inputs")
        assert isinstance(scenario_inputs, dict)
        assert set(scenario_inputs.keys()) == set(expected_scenario_ids)
        assert scenario_inputs["base"]["applied_tile_ids"] == []
        assert scenario_inputs["base"]["stress_band_pct"] == 10

        for scenario_id, scenario_payload in scenarios.items():
            for metric_ref in expected_metric_refs:
                resolved = _resolve_metric_ref(scenario_payload, metric_ref)
                if metric_ref == "revenue_analysis.annual_revenue" and not isinstance(resolved, (int, float)):
                    revenue_factor = _resolve_metric_ref(scenario_payload, "modifiers.revenue_factor")
                    assert isinstance(revenue_factor, (int, float)), (
                        f"{expected_profile_id}:{scenario_id} missing revenue fallback for {metric_ref}"
                    )
                    continue
                assert isinstance(resolved, (int, float)), (
                    f"{expected_profile_id}:{scenario_id} missing numeric metric {metric_ref}"
                )

        for row in derived_rows:
            if not isinstance(row, dict):
                continue
            scenario_id = row.get("row_id")
            assert isinstance(scenario_id, str)
            scenario_input = scenario_inputs[scenario_id]
            applied_tile_ids = list(row.get("apply_tiles") or []) + list(row.get("plus_tiles") or [])
            assert scenario_input.get("applied_tile_ids") == applied_tile_ids
            assert scenario_input.get("stress_band_pct") == 10


def test_civic_decision_insurance_contract_and_provenance_are_policy_driven_and_deterministic():
    for subtype, expected in CIVIC_PROFILE_MAP.items():
        expected_profile_id = expected["tile"]
        policy = get_decision_insurance_policy(expected_profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=75_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(expected_profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"civic-di-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"civic-di-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("enabled") is True
        assert di_provenance.get("profile_id") == expected_profile_id

        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == expected_profile_id

        primary_control = view_a.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy["primary_control_variable"]["tile_id"]
        assert primary_control.get("metric_ref") == policy["primary_control_variable"]["metric_ref"]

        first_break = view_a.get("first_break_condition")
        first_break_provenance = di_provenance.get("first_break_condition")
        assert isinstance(first_break_provenance, dict)
        assert first_break_provenance.get("source") == "decision_insurance_policy.collapse_trigger"
        if first_break_provenance.get("status") == "available":
            assert isinstance(first_break, dict)
            assert first_break.get("break_metric") == policy["collapse_trigger"]["metric"]
            assert first_break.get("operator") == policy["collapse_trigger"]["operator"]
            assert first_break.get("threshold") == policy["collapse_trigger"]["threshold"]

        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_provenance.get("band") in {"tight", "moderate", "comfortable"}
        assert view_a.get("flex_before_break_band") == flex_provenance.get("band")

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "flex_before_break_pct",
            "flex_before_break_band",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_civic_first_break_unit_semantics_match_metric_family():
    for subtype, expected in CIVIC_PROFILE_MAP.items():
        policy = get_decision_insurance_policy(expected["tile"])
        assert isinstance(policy, dict)
        collapse_trigger = policy.get("collapse_trigger")
        assert isinstance(collapse_trigger, dict)
        policy_metric = collapse_trigger.get("metric")
        policy_threshold = float(collapse_trigger.get("threshold"))

        payload = unified_engine.calculate_project(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=70_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected["tile"])
        view_model = build_dealshield_view_model(
            project_id=f"civic-first-break-units-{subtype}",
            payload=payload,
            profile=profile,
        )

        first_break = view_model.get("first_break_condition")
        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        first_break_provenance = di_provenance.get("first_break_condition")
        assert isinstance(first_break_provenance, dict)
        assert policy_metric in {"value_gap_pct", "value_gap"}

        if policy_metric == "value_gap_pct":
            assert abs(policy_threshold) <= 100.0
        else:
            assert abs(policy_threshold) >= 1_000.0 or math.isclose(policy_threshold, 0.0, abs_tol=1e-9)

        if not isinstance(first_break, dict):
            assert first_break_provenance.get("status") in {"unavailable", "not_modeled"}
            continue

        metric = first_break.get("break_metric")
        threshold = float(first_break.get("threshold"))
        observed_value = float(first_break.get("observed_value"))
        observed_value_pct = first_break.get("observed_value_pct")
        assert isinstance(observed_value_pct, (int, float))
        assert metric == policy_metric
        assert math.isclose(threshold, policy_threshold, rel_tol=1e-9, abs_tol=1e-9)

        if metric == "value_gap_pct":
            assert math.isclose(
                observed_value,
                float(observed_value_pct),
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
        else:
            assert abs(observed_value) >= 1_000.0
            assert not math.isclose(
                abs(observed_value),
                abs(float(observed_value_pct)),
                rel_tol=1e-6,
                abs_tol=1e-6,
            )


def test_civic_schedule_source_is_subtype_specific_with_unknown_subtype_fallback():
    for subtype in CIVIC_PROFILE_MAP:
        schedule = build_construction_schedule(BuildingType.CIVIC, subtype)
        assert schedule.get("building_type") == BuildingType.CIVIC.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

    unknown_schedule = build_construction_schedule(
        BuildingType.CIVIC,
        "unknown_civic_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.CIVIC.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    phases = unknown_schedule.get("phases")
    assert isinstance(phases, list) and phases


def test_civic_runtime_scope_depth_and_trade_presence_in_payload():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, expected in CIVIC_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=70_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        by_trade = {
            str(trade_block.get("trade", "")).strip().lower(): trade_block
            for trade_block in scope_items
            if isinstance(trade_block, dict) and isinstance(trade_block.get("trade"), str)
        }
        assert set(by_trade.keys()) == required_trades

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum_items in CIVIC_SCOPE_MIN_ITEMS_BY_SUBTYPE[subtype].items():
            trade_block = by_trade[trade_key]
            systems = trade_block.get("systems")
            if not isinstance(systems, list):
                systems = trade_block.get("items")
            assert isinstance(systems, list)
            assert len(systems) >= minimum_items

            systems_total = sum(
                float(system.get("total_cost", 0.0) or 0.0)
                for system in systems
                if isinstance(system, dict)
            )
            assert math.isclose(
                systems_total,
                float(trade_breakdown.get(trade_key, 0.0) or 0.0),
                rel_tol=0,
                abs_tol=1e-6,
            )

        assert payload.get("dealshield_tile_profile") == expected["tile"]


def test_civic_decision_insurance_policy_entries_are_available_for_all_profiles():
    for expected in CIVIC_PROFILE_MAP.values():
        profile_id = expected["tile"]
        by_lookup = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        by_getter = get_decision_insurance_policy(profile_id)

        assert isinstance(by_lookup, dict)
        assert isinstance(by_getter, dict)
        assert by_lookup == by_getter

        collapse_trigger = by_lookup.get("collapse_trigger")
        assert isinstance(collapse_trigger, dict)
        assert collapse_trigger.get("metric") in {"value_gap_pct", "value_gap"}
