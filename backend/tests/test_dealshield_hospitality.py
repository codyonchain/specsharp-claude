import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import hospitality as hospitality_tile_profiles
from app.v2.config.type_profiles.scope_items import hospitality as hospitality_scope_profiles
from app.v2.engines.unified_engine import build_construction_schedule, unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


HOSPITALITY_PROFILE_IDS = {
    "limited_service_hotel": "hospitality_limited_service_hotel_v1",
    "full_service_hotel": "hospitality_full_service_hotel_v1",
}

HOSPITALITY_SCOPE_PROFILE_IDS = {
    "limited_service_hotel": "hospitality_limited_service_hotel_structural_v1",
    "full_service_hotel": "hospitality_full_service_hotel_structural_v1",
}

HOSPITALITY_SUBTYPE_SCHEDULE_MONTHS = {
    "limited_service_hotel": 24,
    "full_service_hotel": 32,
}

HOSPITALITY_SPECIAL_FEATURE_CASES = {
    "limited_service_hotel": "breakfast_area",
    "full_service_hotel": "ballroom",
}


def _profile_item_keys(profile_id: str):
    profile = hospitality_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    keys = set()
    for trade_profile in profile.get("trade_profiles", []):
        for item in trade_profile.get("items", []):
            key = item.get("key")
            if isinstance(key, str) and key:
                keys.add(key)
    return keys


def _tile_map(profile_id: str):
    profile = get_dealshield_profile(profile_id)
    return {tile["tile_id"]: tile for tile in profile.get("tiles", []) if isinstance(tile, dict)}


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_hospitality_subtypes_define_deterministic_scope_and_dealshield_profile_ids():
    for subtype in HOSPITALITY_PROFILE_IDS:
        config = get_building_config(BuildingType.HOSPITALITY, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == HOSPITALITY_PROFILE_IDS[subtype]
        assert config.scope_items_profile == HOSPITALITY_SCOPE_PROFILE_IDS[subtype]


def test_hospitality_scope_defaults_and_profiles_resolve():
    assert hospitality_scope_profiles.SCOPE_ITEM_DEFAULTS == HOSPITALITY_SCOPE_PROFILE_IDS

    for profile_id in HOSPITALITY_SCOPE_PROFILE_IDS.values():
        profile = hospitality_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        assert isinstance(profile, dict)
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and trade_profiles


def test_hospitality_scope_profiles_are_subtype_authored_not_clones():
    limited_keys = _profile_item_keys("hospitality_limited_service_hotel_structural_v1")
    full_keys = _profile_item_keys("hospitality_full_service_hotel_structural_v1")

    assert limited_keys != full_keys

    assert "guestroom_hvac_allowance" in limited_keys
    assert "restroom_groups" in limited_keys
    assert "ballroom_and_back_of_house_foundations" in full_keys
    assert "ballroom_prefunction_finishes" in full_keys

    assert "ballroom_and_back_of_house_foundations" not in limited_keys
    assert "ballroom_prefunction_finishes" not in limited_keys
    assert "guestroom_hvac_allowance" not in full_keys
    assert "restroom_groups" not in full_keys


def test_hospitality_tile_profiles_and_defaults_resolve():
    assert hospitality_tile_profiles.DEALSHIELD_TILE_DEFAULTS == HOSPITALITY_PROFILE_IDS

    expected_unique_tile = {
        "limited_service_hotel": "guestroom_turnover_and_ffe_plus_10",
        "full_service_hotel": "ballroom_and_fnb_fitout_plus_12",
    }

    for subtype, profile_id in HOSPITALITY_PROFILE_IDS.items():
        profile = get_dealshield_profile(profile_id)
        assert profile["version"] == "v1"
        assert profile["profile_id"] == profile_id
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and profile["derived_rows"]

        tile_ids = {tile["tile_id"] for tile in profile["tiles"]}
        assert {"cost_plus_10", "revenue_minus_10"}.issubset(tile_ids)
        assert expected_unique_tile[subtype] in tile_ids


def test_hospitality_tile_profiles_are_subtype_authored_not_clones():
    limited_profile = get_dealshield_profile("hospitality_limited_service_hotel_v1")
    full_profile = get_dealshield_profile("hospitality_full_service_hotel_v1")

    assert limited_profile != full_profile

    limited_row_ids = {row["row_id"] for row in limited_profile["derived_rows"]}
    full_row_ids = {row["row_id"] for row in full_profile["derived_rows"]}

    assert "seasonal_ramp_pressure" in limited_row_ids
    assert "banquet_program_delay" in full_row_ids


def test_hospitality_content_profiles_resolve_and_align_with_tiles():
    for profile_id in HOSPITALITY_PROFILE_IDS.values():
        tile_ids = set(_tile_map(profile_id).keys())
        content_profile = get_dealshield_content_profile(profile_id)

        assert content_profile["version"] == "v1"
        assert content_profile["profile_id"] == profile_id

        drivers = content_profile.get("fastest_change", {}).get("drivers", [])
        assert isinstance(drivers, list) and drivers

        driver_tile_ids = {
            driver.get("tile_id")
            for driver in drivers
            if isinstance(driver, dict)
        }
        driver_tile_ids.discard(None)
        assert driver_tile_ids.issubset(tile_ids)

        question_tile_ids = {
            entry.get("driver_tile_id")
            for entry in content_profile.get("question_bank", [])
            if isinstance(entry, dict)
        }
        question_tile_ids.discard(None)
        assert question_tile_ids.issubset(tile_ids)

        likely_wrong_tile_ids = {
            entry.get("driver_tile_id")
            for entry in content_profile.get("most_likely_wrong", [])
            if isinstance(entry, dict)
        }
        likely_wrong_tile_ids.discard(None)
        assert likely_wrong_tile_ids.issubset(tile_ids)


def test_hospitality_content_profiles_are_subtype_authored_not_clones():
    limited_content = get_dealshield_content_profile("hospitality_limited_service_hotel_v1")
    full_content = get_dealshield_content_profile("hospitality_full_service_hotel_v1")

    assert limited_content != full_content

    limited_driver_tiles = {
        d["tile_id"]
        for d in limited_content.get("fastest_change", {}).get("drivers", [])
    }
    full_driver_tiles = {
        d["tile_id"]
        for d in full_content.get("fastest_change", {}).get("drivers", [])
    }

    assert "guestroom_turnover_and_ffe_plus_10" in limited_driver_tiles
    assert "ballroom_and_fnb_fitout_plus_12" in full_driver_tiles


def test_hospitality_emits_wave1_dealshield_scenario_snapshots_and_provenance():
    for subtype, expected_profile_id in HOSPITALITY_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HOSPITALITY,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected_profile_id

        scenarios_bundle = payload.get("dealshield_scenarios")
        assert isinstance(scenarios_bundle, dict)
        assert scenarios_bundle.get("profile_id") == expected_profile_id

        profile = get_dealshield_profile(expected_profile_id)
        expected_scenario_ids = ["base"] + [row["row_id"] for row in profile["derived_rows"]]

        scenarios = scenarios_bundle.get("scenarios")
        assert isinstance(scenarios, dict)
        assert set(expected_scenario_ids).issubset(set(scenarios.keys()))

        metric_refs = [tile["metric_ref"] for tile in profile["tiles"]]
        for scenario_id in expected_scenario_ids:
            snapshot = scenarios.get(scenario_id)
            assert isinstance(snapshot, dict)
            for metric_ref in metric_refs:
                value = _resolve_metric_ref(snapshot, metric_ref)
                assert isinstance(value, (int, float))

        provenance = scenarios_bundle.get("provenance")
        assert isinstance(provenance, dict)
        assert provenance.get("profile_id") == expected_profile_id
        scenario_inputs = provenance.get("scenario_inputs")
        assert isinstance(scenario_inputs, dict)
        for scenario_id in expected_scenario_ids:
            scenario_input = scenario_inputs.get(scenario_id)
            assert isinstance(scenario_input, dict)
            assert scenario_input.get("stress_band_pct") in {3, 5, 7, 10}
            assert scenario_input.get("cost_anchor_used") in {True, False}
            assert scenario_input.get("revenue_anchor_used") in {True, False}


def test_hospitality_decision_insurance_outputs_and_provenance():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    for subtype, expected_profile_id in HOSPITALITY_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HOSPITALITY,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"hospitality-di-{subtype}",
            payload=payload,
            profile=profile,
        )

        assert "primary_control_variable" in view_model
        assert "first_break_condition" in view_model
        assert "flex_before_break_pct" in view_model
        assert "exposure_concentration_pct" in view_model
        assert "ranked_likely_wrong" in view_model
        assert "decision_insurance_provenance" in view_model
        assert view_model.get("decision_status") in allowed_statuses
        assert isinstance(view_model.get("decision_reason_code"), str)
        assert view_model["decision_reason_code"].strip()
        assert isinstance(view_model.get("decision_status_provenance"), dict)
        assert view_model.get("tile_profile_id") == expected_profile_id
        assert isinstance(view_model.get("content_profile_id"), str)
        assert view_model["content_profile_id"].strip()
        assert "scope_items_profile_id" in view_model

        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("enabled") is True
        assert di_provenance.get("profile_id") == expected_profile_id

        model_provenance = view_model.get("provenance")
        assert isinstance(model_provenance, dict)
        assert model_provenance.get("decision_insurance") == di_provenance
        assert model_provenance.get("decision_status") in allowed_statuses
        assert isinstance(model_provenance.get("decision_reason_code"), str)
        assert model_provenance.get("decision_reason_code")
        assert isinstance(model_provenance.get("decision_status_provenance"), dict)
        assert model_provenance.get("profile_id") == expected_profile_id
        assert isinstance(model_provenance.get("content_profile_id"), str)
        assert model_provenance.get("content_profile_id")
        assert "scope_items_profile_id" in model_provenance

        decision_summary = view_model.get("decision_summary")
        assert isinstance(decision_summary, dict)
        assert decision_summary.get("decision_status") in allowed_statuses
        assert isinstance(decision_summary.get("decision_reason_code"), str)
        assert decision_summary.get("decision_reason_code")
        assert isinstance(decision_summary.get("decision_status_provenance"), dict)

        for key in (
            "primary_control_variable",
            "first_break_condition",
            "flex_before_break_pct",
            "exposure_concentration_pct",
            "ranked_likely_wrong",
        ):
            assert key in di_provenance
            block = di_provenance.get(key)
            assert isinstance(block, dict)
            assert block.get("status") in {"available", "unavailable"}
            if block.get("status") == "unavailable":
                reason = block.get("reason")
                assert isinstance(reason, str) and reason.strip()


def test_hospitality_construction_schedule_uses_subtype_source_for_known_subtypes():
    for subtype, expected_total_months in HOSPITALITY_SUBTYPE_SCHEDULE_MONTHS.items():
        schedule = build_construction_schedule(
            BuildingType.HOSPITALITY,
            subtype=subtype,
        )
        assert isinstance(schedule, dict)
        assert schedule.get("building_type") == BuildingType.HOSPITALITY.value
        assert schedule.get("subtype") == subtype
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("total_months") == expected_total_months


def test_hospitality_special_features_math_and_breakdown_reconcile_for_both_subtypes():
    square_footage = 85_000
    for subtype, feature_key in HOSPITALITY_SPECIAL_FEATURE_CASES.items():
        baseline = unified_engine.calculate_project(
            building_type=BuildingType.HOSPITALITY,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[],
        )
        with_feature = unified_engine.calculate_project(
            building_type=BuildingType.HOSPITALITY,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[feature_key],
        )

        config = get_building_config(BuildingType.HOSPITALITY, subtype)
        expected_delta = float(config.special_features[feature_key]) * square_footage

        baseline_special_features_total = float(baseline["construction_costs"]["special_features_total"])
        feature_special_features_total = float(with_feature["construction_costs"]["special_features_total"])
        special_features_delta = feature_special_features_total - baseline_special_features_total
        assert special_features_delta > 0
        assert special_features_delta == pytest.approx(expected_delta, rel=1e-3)

        baseline_total_project_cost = float(baseline["totals"]["total_project_cost"])
        feature_total_project_cost = float(with_feature["totals"]["total_project_cost"])
        total_project_cost_delta = feature_total_project_cost - baseline_total_project_cost
        assert total_project_cost_delta == pytest.approx(expected_delta, rel=1e-3)

        breakdown = with_feature["construction_costs"].get("special_features_breakdown")
        assert isinstance(breakdown, list) and breakdown
        breakdown_map = {
            item["id"]: item
            for item in breakdown
            if isinstance(item, dict) and item.get("id")
        }
        assert feature_key in breakdown_map
        assert float(breakdown_map[feature_key].get("cost_per_sf", 0.0)) == float(config.special_features[feature_key])
        assert float(breakdown_map[feature_key].get("total_cost", 0.0)) == pytest.approx(expected_delta, rel=1e-3)

        summed_breakdown_total = sum(
            float(item.get("total_cost", 0.0) or 0.0)
            for item in breakdown
            if isinstance(item, dict)
        )
        assert summed_breakdown_total == pytest.approx(feature_special_features_total, rel=1e-3)
