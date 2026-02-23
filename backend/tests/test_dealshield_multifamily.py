from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import multifamily as multifamily_tile_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


MULTIFAMILY_PROFILE_IDS = {
    "market_rate_apartments": "multifamily_market_rate_apartments_v1",
    "luxury_apartments": "multifamily_luxury_apartments_v1",
    "affordable_housing": "multifamily_affordable_housing_v1",
}


def test_multifamily_subtypes_define_deterministic_dealshield_profile_ids():
    for subtype, expected_profile_id in MULTIFAMILY_PROFILE_IDS.items():
        config = get_building_config(BuildingType.MULTIFAMILY, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected_profile_id


def test_multifamily_tile_profiles_and_defaults_resolve():
    assert multifamily_tile_profiles.DEALSHIELD_TILE_DEFAULTS == MULTIFAMILY_PROFILE_IDS

    for profile_id in MULTIFAMILY_PROFILE_IDS.values():
        profile = get_dealshield_profile(profile_id)
        assert profile["version"] == "v1"
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and profile["derived_rows"]
        tile_ids = {tile["tile_id"] for tile in profile["tiles"]}
        assert {"cost_plus_10", "cost_per_sf_plus_10", "finishes_plus_10"}.issubset(tile_ids)


def test_multifamily_content_profiles_resolve_and_align_with_tiles():
    for profile_id in MULTIFAMILY_PROFILE_IDS.values():
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {tile["tile_id"] for tile in tile_profile["tiles"]}

        content_profile = get_dealshield_content_profile(profile_id)
        assert content_profile["version"] == "v1"
        assert content_profile["profile_id"] == profile_id

        fastest_change = content_profile.get("fastest_change", {})
        drivers = fastest_change.get("drivers", [])
        assert isinstance(drivers, list) and drivers
        for driver in drivers:
            assert driver["tile_id"] in tile_ids


def test_multifamily_dealshield_view_model_is_available():
    for subtype, expected_profile_id in MULTIFAMILY_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected_profile_id

        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"test-{subtype}",
            payload=payload,
            profile=profile,
        )

        assert view_model.get("profile_id") == expected_profile_id
        assert isinstance(view_model.get("rows"), list) and view_model["rows"]
        assert isinstance(view_model.get("columns"), list) and view_model["columns"]
        assert isinstance(view_model.get("content"), dict)
        assert view_model["content"].get("profile_id") == expected_profile_id
        provenance = view_model.get("provenance", {})
        assert provenance.get("profile_id") == expected_profile_id
        assert "decision_summary" in view_model
        assert "value_gap" in view_model
        assert "value_gap_pct" in view_model


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_multifamily_emits_dealshield_scenario_snapshots():
    for subtype, expected_profile_id in MULTIFAMILY_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
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


def test_multifamily_decision_insurance_outputs_and_provenance():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    for subtype, expected_profile_id in MULTIFAMILY_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"test-di-{subtype}",
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

        primary_control = view_model.get("primary_control_variable")
        if primary_control is not None:
            assert isinstance(primary_control, dict)
            assert primary_control.get("tile_id")
            assert primary_control.get("metric_ref")
            assert isinstance(primary_control.get("impact_pct"), (int, float))
            assert primary_control.get("severity") in {"Low", "Med", "High"}

        first_break = view_model.get("first_break_condition")
        if first_break is not None:
            assert isinstance(first_break, dict)
            assert first_break.get("break_metric") == "value_gap"
            assert first_break.get("operator") == "<="
            assert first_break.get("threshold") == 0.0
            assert isinstance(first_break.get("observed_value"), (int, float))
            assert first_break["observed_value"] <= 0

        flex_before_break = view_model.get("flex_before_break_pct")
        if flex_before_break is not None:
            assert isinstance(flex_before_break, (int, float))
            assert flex_before_break >= 0

        concentration = view_model.get("exposure_concentration_pct")
        if concentration is not None:
            assert isinstance(concentration, (int, float))
            assert 0 <= concentration <= 100

        ranked_likely_wrong = view_model.get("ranked_likely_wrong")
        assert isinstance(ranked_likely_wrong, list)
        assert ranked_likely_wrong
        for entry in ranked_likely_wrong:
            assert isinstance(entry, dict)
            assert "text" in entry
            assert "impact_pct" in entry
            assert entry.get("severity") in {"Low", "Med", "High", "Unknown"}


def test_multifamily_special_feature_increases_total_project_cost_for_each_subtype():
    subtype_feature_map = {
        "market_rate_apartments": "parking_garage",
        "luxury_apartments": "parking_garage",
        "affordable_housing": "parking_garage",
    }

    for subtype, feature in subtype_feature_map.items():
        baseline = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[],
        )
        with_feature = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[feature],
        )

        assert with_feature["construction_costs"]["special_features_total"] > baseline["construction_costs"]["special_features_total"]
        assert with_feature["totals"]["total_project_cost"] > baseline["totals"]["total_project_cost"]

        config = get_building_config(BuildingType.MULTIFAMILY, subtype)
        assert config is not None
        expected_single_total = float(config.special_features[feature]) * 120_000.0

        breakdown = with_feature["construction_costs"].get("special_features_breakdown")
        assert isinstance(breakdown, list)
        assert breakdown
        breakdown_by_id = {item["id"]: item for item in breakdown if isinstance(item, dict) and item.get("id")}
        assert feature in breakdown_by_id
        single_entry = breakdown_by_id[feature]
        assert single_entry.get("cost_per_sf") == float(config.special_features[feature])
        assert abs(float(single_entry.get("total_cost", 0.0)) - expected_single_total) < 1e-6
        assert isinstance(single_entry.get("label"), str) and single_entry["label"].strip()

        breakdown_total = sum(float(item.get("total_cost", 0.0)) for item in breakdown if isinstance(item, dict))
        assert abs(breakdown_total - float(with_feature["construction_costs"]["special_features_total"])) < 1e-6

        available_features = list((config.special_features or {}).keys())
        assert len(available_features) >= 2
        selected_multi = available_features[:2]
        multi_feature = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=selected_multi,
        )
        multi_breakdown = multi_feature["construction_costs"].get("special_features_breakdown")
        assert isinstance(multi_breakdown, list)
        assert len(multi_breakdown) >= 2

        multi_breakdown_by_id = {
            item["id"]: item
            for item in multi_breakdown
            if isinstance(item, dict) and item.get("id")
        }
        for selected_feature in selected_multi:
            assert selected_feature in multi_breakdown_by_id
            assert abs(
                float(multi_breakdown_by_id[selected_feature].get("total_cost", 0.0))
                - float(config.special_features[selected_feature]) * 120_000.0
            ) < 1e-6

        expected_multi_total = sum(float(config.special_features[key]) * 120_000.0 for key in selected_multi)
        assert abs(float(multi_feature["construction_costs"]["special_features_total"]) - expected_multi_total) < 1e-6
        summed_multi_breakdown = sum(
            float(item.get("total_cost", 0.0))
            for item in multi_breakdown
            if isinstance(item, dict)
        )
        assert abs(summed_multi_breakdown - float(multi_feature["construction_costs"]["special_features_total"])) < 1e-6
