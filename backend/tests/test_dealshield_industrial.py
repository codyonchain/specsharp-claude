from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import industrial as industrial_tile_profiles
from app.v2.config.type_profiles.scope_items import industrial as industrial_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


INDUSTRIAL_PROFILE_IDS = {
    "warehouse": "industrial_warehouse_v1",
    "distribution_center": "industrial_distribution_center_v1",
    "manufacturing": "industrial_manufacturing_v1",
    "flex_space": "industrial_flex_space_v1",
    "cold_storage": "industrial_cold_storage_v1",
}


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _profile_item_keys(profile_id: str):
    profile = industrial_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    keys = set()
    for trade_profile in profile.get("trade_profiles", []):
        for item in trade_profile.get("items", []):
            key = item.get("key")
            if isinstance(key, str) and key:
                keys.add(key)
    return keys


def test_industrial_subtypes_define_deterministic_dealshield_profile_ids():
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        config = get_building_config(BuildingType.INDUSTRIAL, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected_profile_id


def test_industrial_manufacturing_uses_structural_scope_items_profile():
    config = get_building_config(BuildingType.INDUSTRIAL, "manufacturing")
    assert config is not None
    assert config.scope_items_profile == "industrial_manufacturing_structural_v1"


def test_industrial_manufacturing_scope_profile_is_not_warehouse_clone():
    manufacturing_keys = _profile_item_keys("industrial_manufacturing_structural_v1")
    warehouse_keys = _profile_item_keys("industrial_warehouse_structural_v1")

    assert manufacturing_keys != warehouse_keys
    assert {
        "process_hvac_and_ventilation",
        "process_exhaust_and_dust_collection",
        "motor_control_centers_vfd",
        "process_water_and_treatment",
        "equipment_guards_and_safety_curbing",
    }.issubset(manufacturing_keys)
    assert {
        "tilt_wall_shell",
        "dock_pits_loading_aprons",
        "warehouse_floor_sealers",
    }.isdisjoint(manufacturing_keys)


def test_industrial_tile_profiles_and_defaults_resolve():
    assert industrial_tile_profiles.DEALSHIELD_TILE_DEFAULTS == INDUSTRIAL_PROFILE_IDS

    expected_driver_tile_by_subtype = {
        "warehouse": "structural_plus_10",
        "distribution_center": "electrical_plus_10",
        "manufacturing": "process_mep_plus_10",
        "flex_space": "office_finish_plus_10",
        "cold_storage": "equipment_plus_10",
    }

    for subtype, profile_id in INDUSTRIAL_PROFILE_IDS.items():
        profile = get_dealshield_profile(profile_id)
        assert profile["version"] == "v1"
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and profile["derived_rows"]

        tile_ids = {tile["tile_id"] for tile in profile["tiles"]}
        assert {"cost_plus_10", "revenue_minus_10"}.issubset(tile_ids)
        assert expected_driver_tile_by_subtype[subtype] in tile_ids


def test_industrial_content_profiles_resolve_and_align_with_tiles():
    for profile_id in INDUSTRIAL_PROFILE_IDS.values():
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


def test_industrial_engine_emits_dealshield_profile_for_all_subtypes():
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.INDUSTRIAL,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected_profile_id


def test_industrial_manufacturing_emits_scope_items():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="manufacturing",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    scope_items = payload.get("scope_items")
    assert isinstance(scope_items, list)
    assert scope_items
    assert any(isinstance(item.get("systems"), list) and item.get("systems") for item in scope_items)

    all_system_names = [
        str(system.get("name", "")).lower()
        for trade in scope_items
        for system in (trade.get("systems") or [])
        if isinstance(system, dict)
    ]
    assert any("process hvac" in name for name in all_system_names)
    assert any("motor control centers" in name for name in all_system_names)
    assert any("process water" in name for name in all_system_names)


def test_industrial_emits_wave1_dealshield_scenario_snapshots_and_controls():
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.INDUSTRIAL,
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


def test_industrial_decision_insurance_outputs_and_provenance():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.INDUSTRIAL,
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
