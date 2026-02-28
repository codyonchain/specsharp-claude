import math

from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.construction_schedule import build_construction_schedule
from app.v2.config.type_profiles.dealshield_content import educational as educational_content
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_ID,
    get_decision_insurance_policy,
)
from app.v2.config.type_profiles.scope_items import educational as educational_scope_profiles
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model
from tests.dealshield_contract_assertions import assert_decision_insurance_truth_parity


EDUCATIONAL_PROFILE_IDS = {
    "elementary_school": {
        "tile_profile": "educational_elementary_school_v1",
        "scope_profile": "educational_elementary_school_structural_v1",
    },
    "middle_school": {
        "tile_profile": "educational_middle_school_v1",
        "scope_profile": "educational_middle_school_structural_v1",
    },
    "high_school": {
        "tile_profile": "educational_high_school_v1",
        "scope_profile": "educational_high_school_structural_v1",
    },
    "university": {
        "tile_profile": "educational_university_v1",
        "scope_profile": "educational_university_structural_v1",
    },
    "community_college": {
        "tile_profile": "educational_community_college_v1",
        "scope_profile": "educational_community_college_structural_v1",
    },
}

EDUCATIONAL_SCOPE_DEPTH_FLOORS = {
    "elementary_school": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "middle_school": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "high_school": {
        "structural": 4,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 4,
        "finishes": 4,
    },
    "university": {
        "structural": 4,
        "mechanical": 5,
        "electrical": 5,
        "plumbing": 4,
        "finishes": 4,
    },
    "community_college": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
}


def _profile_tile_ids(profile):
    return {
        tile.get("tile_id")
        for tile in profile.get("tiles", [])
        if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
    }


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_educational_subtype_wiring_is_explicit():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.EDUCATIONAL, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        tile_profile = get_dealshield_profile(expected["tile_profile"])
        assert tile_profile.get("profile_id") == expected["tile_profile"]
        assert _profile_tile_ids(tile_profile)

        assert educational_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype] == expected["scope_profile"]
        assert expected["scope_profile"] in educational_scope_profiles.SCOPE_ITEM_PROFILES


def test_educational_profiles_are_not_clones_across_tiles_content_and_scope():
    primary_tile_ids = []
    subtype_row_ids = []
    first_mlw_texts = []
    scope_signatures = []

    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        tile_profile = get_dealshield_profile(expected["tile_profile"])
        tile_ids = _profile_tile_ids(tile_profile)
        primary_tiles = sorted(tile_ids - {"cost_plus_10", "revenue_minus_10"})
        assert len(primary_tiles) == 1
        primary_tile_ids.append(primary_tiles[0])

        row_ids = {
            row.get("row_id")
            for row in tile_profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        }
        subtype_rows = sorted(row_ids - {"conservative", "ugly"})
        assert len(subtype_rows) == 1
        subtype_row_ids.append(subtype_rows[0])

        content = educational_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        first_mlw_texts.append(content["most_likely_wrong"][0]["text"])

        scope_profile = educational_scope_profiles.SCOPE_ITEM_PROFILES[expected["scope_profile"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.append(signature)

    assert len(primary_tile_ids) == len(set(primary_tile_ids))
    assert len(subtype_row_ids) == len(set(subtype_row_ids))
    assert len(first_mlw_texts) == len(set(first_mlw_texts))
    assert len(scope_signatures) == len(set(scope_signatures))


def test_educational_content_references_existing_tile_ids():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = _profile_tile_ids(tile_profile)
        assert tile_ids

        content = educational_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids
            assert isinstance(entry.get("text"), str) and entry.get("text").strip()
            assert isinstance(entry.get("why"), str) and entry.get("why").strip()

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for entry in question_bank:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids
            questions = entry.get("questions")
            assert isinstance(questions, list) and questions
            assert all(isinstance(question, str) and question.strip() for question in questions)


def test_educational_content_profiles_resolve_from_shared_registry():
    for expected in EDUCATIONAL_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        content_profile = get_dealshield_content_profile(profile_id)
        assert isinstance(content_profile, dict)
        assert content_profile.get("profile_id") == profile_id


def test_educational_scope_profiles_keep_depth_floors_and_allocation_sum_to_one():
    for subtype, floors in EDUCATIONAL_SCOPE_DEPTH_FLOORS.items():
        profile_id = educational_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype]
        profile = educational_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum_items in floors.items():
            items = by_trade[trade_key].get("items")
            assert isinstance(items, list)
            assert len(items) >= minimum_items
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_educational_runtime_emits_scenarios_and_truthful_provenance_for_all_subtypes():
    required_runtime_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        expected_profile_id = expected["tile_profile"]
        payload = unified_engine.calculate_project(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=75_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload["dealshield_tile_profile"] == expected_profile_id
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list)
        assert scope_items, f"{subtype} should emit non-empty scope_items from authored scope profile"

        runtime_by_trade = {
            str(trade_block.get("trade", "")).strip().lower(): trade_block
            for trade_block in scope_items
            if isinstance(trade_block, dict) and isinstance(trade_block.get("trade"), str)
        }
        assert required_runtime_trades.issubset(runtime_by_trade.keys()), (
            f"{subtype} missing required runtime trades: "
            f"{sorted(required_runtime_trades - set(runtime_by_trade.keys()))}"
        )

        floors = EDUCATIONAL_SCOPE_DEPTH_FLOORS[subtype]
        for trade_key in required_runtime_trades:
            trade_block = runtime_by_trade[trade_key]
            systems = trade_block.get("systems")
            if not isinstance(systems, list):
                systems = trade_block.get("items")
            assert isinstance(systems, list)
            assert len(systems) >= floors[trade_key], (
                f"{subtype}:{trade_key} expected floor {floors[trade_key]}, got {len(systems)}"
            )

        profile = get_dealshield_profile(expected_profile_id)
        tile_map = {
            tile["tile_id"]: tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        derived_rows = profile.get("derived_rows", [])
        expected_scenario_ids = ["base"] + [row["row_id"] for row in derived_rows if isinstance(row, dict)]
        expected_metric_refs = [
            tile.get("metric_ref")
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict)
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
                assert isinstance(resolved, (int, float)), (
                    f"{expected_profile_id}:{scenario_id} missing numeric metric {metric_ref}"
                )

        for row in derived_rows:
            if not isinstance(row, dict):
                continue
            scenario_id = row["row_id"]
            scenario_input = scenario_inputs[scenario_id]
            applied_tile_ids = list(row.get("apply_tiles") or []) + list(row.get("plus_tiles") or [])
            assert scenario_input["applied_tile_ids"] == applied_tile_ids
            assert scenario_input["stress_band_pct"] == 10

            expected_cost_scalar = 1.1 if "cost_plus_10" in applied_tile_ids else None
            expected_revenue_scalar = 0.9 if "revenue_minus_10" in applied_tile_ids else None
            if expected_cost_scalar is None:
                assert scenario_input.get("cost_scalar") is None
            else:
                assert scenario_input.get("cost_scalar") == expected_cost_scalar
            if expected_revenue_scalar is None:
                assert scenario_input.get("revenue_scalar") is None
            else:
                assert scenario_input.get("revenue_scalar") == expected_revenue_scalar

            driver_tile_ids = [
                tile_id
                for tile_id in applied_tile_ids
                if tile_map[tile_id]["metric_ref"]
                not in {"totals.total_project_cost", "revenue_analysis.annual_revenue", "modifiers.revenue_factor"}
            ]
            assert len(driver_tile_ids) <= 1


def test_educational_di_contract_and_provenance_are_policy_driven_for_all_profiles():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        expected_profile_id = expected["tile_profile"]
        payload = unified_engine.calculate_project(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected_profile_id)
        policy = get_decision_insurance_policy(expected_profile_id)
        assert isinstance(policy, dict)

        view_model = build_dealshield_view_model(
            project_id=f"educational-di-{subtype}",
            payload=payload,
            profile=profile,
        )
        assert_decision_insurance_truth_parity(view_model)
        assert view_model.get("decision_status") in {"GO", "Needs Work", "NO-GO", "PENDING"}
        assert isinstance(view_model.get("decision_reason_code"), str)
        assert isinstance(view_model.get("decision_status_provenance"), dict)

        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("enabled") is True
        assert di_provenance.get("profile_id") == expected_profile_id

        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == expected_profile_id

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy["primary_control_variable"]["tile_id"]

        first_break = view_model.get("first_break_condition")
        first_break_provenance = di_provenance.get("first_break_condition")
        assert isinstance(first_break_provenance, dict)
        assert first_break_provenance.get("source") == "decision_insurance_policy.collapse_trigger"
        if first_break_provenance.get("status") == "available":
            assert isinstance(first_break, dict)
            assert first_break.get("break_metric") == policy["collapse_trigger"]["metric"]
            assert first_break.get("threshold") == policy["collapse_trigger"]["threshold"]
            assert first_break.get("operator") == policy["collapse_trigger"]["operator"]
        else:
            assert first_break_provenance.get("reason") != "no_modeled_break_condition"

        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_provenance.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_provenance.get("band")


def test_educational_decision_status_and_provenance_are_deterministic():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        expected_profile_id = expected["tile_profile"]
        kwargs = dict(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(expected_profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"educational-deterministic-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"educational-deterministic-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

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


def test_educational_first_break_unit_semantics_match_metric_family():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected["tile_profile"])
        view_model = build_dealshield_view_model(
            project_id=f"educational-first-break-units-{subtype}",
            payload=payload,
            profile=profile,
        )

        first_break = view_model.get("first_break_condition")
        assert isinstance(first_break, dict)
        metric = first_break.get("break_metric")
        threshold = float(first_break.get("threshold"))
        observed_value = float(first_break.get("observed_value"))
        observed_value_pct = first_break.get("observed_value_pct")
        assert isinstance(observed_value_pct, (int, float))

        if metric == "value_gap_pct":
            assert abs(threshold) <= 100.0
            assert math.isclose(
                observed_value,
                float(observed_value_pct),
                rel_tol=1e-9,
                abs_tol=1e-9,
            )
        else:
            assert metric == "value_gap"
            assert abs(threshold) >= 1_000.0 or math.isclose(threshold, 0.0, abs_tol=1e-9)
            assert abs(observed_value) >= 1_000.0
            assert not math.isclose(
                abs(observed_value),
                abs(float(observed_value_pct)),
                rel_tol=1e-6,
                abs_tol=1e-6,
            )


def test_educational_schedule_source_is_subtype_specific_with_unknown_subtype_fallback():
    for subtype in EDUCATIONAL_PROFILE_IDS:
        schedule = build_construction_schedule(BuildingType.EDUCATIONAL, subtype)
        assert schedule.get("building_type") == BuildingType.EDUCATIONAL.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

    unknown_schedule = build_construction_schedule(
        BuildingType.EDUCATIONAL,
        "unknown_educational_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.EDUCATIONAL.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    phases = unknown_schedule.get("phases")
    assert isinstance(phases, list) and phases
