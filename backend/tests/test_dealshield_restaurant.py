from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import restaurant as restaurant_tile_profiles
from app.v2.config.type_profiles.scope_items import restaurant as restaurant_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


RESTAURANT_PROFILE_IDS = {
    "quick_service": "restaurant_quick_service_v1",
    "full_service": "restaurant_full_service_v1",
    "fine_dining": "restaurant_fine_dining_v1",
    "cafe": "restaurant_cafe_v1",
    "bar_tavern": "restaurant_bar_tavern_v1",
}

RESTAURANT_SCOPE_PROFILE_IDS = {
    "quick_service": "restaurant_quick_service_structural_v1",
    "full_service": "restaurant_full_service_structural_v1",
    "fine_dining": "restaurant_fine_dining_structural_v1",
    "cafe": "restaurant_cafe_structural_v1",
    "bar_tavern": "restaurant_bar_tavern_structural_v1",
}


def _profile_item_keys(profile_id: str):
    profile = restaurant_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
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


def test_restaurant_subtypes_define_deterministic_scope_and_dealshield_profile_ids():
    for subtype in RESTAURANT_PROFILE_IDS:
        config = get_building_config(BuildingType.RESTAURANT, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == RESTAURANT_PROFILE_IDS[subtype]
        assert config.scope_items_profile == RESTAURANT_SCOPE_PROFILE_IDS[subtype]


def test_restaurant_scope_defaults_and_profiles_resolve():
    assert restaurant_scope_profiles.SCOPE_ITEM_DEFAULTS == RESTAURANT_SCOPE_PROFILE_IDS

    for profile_id in RESTAURANT_SCOPE_PROFILE_IDS.values():
        profile = restaurant_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        assert isinstance(profile, dict)
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and trade_profiles


def test_restaurant_scope_profiles_are_subtype_authored_not_clones():
    quick_keys = _profile_item_keys("restaurant_quick_service_structural_v1")
    full_keys = _profile_item_keys("restaurant_full_service_structural_v1")
    fine_keys = _profile_item_keys("restaurant_fine_dining_structural_v1")
    cafe_keys = _profile_item_keys("restaurant_cafe_structural_v1")
    bar_keys = _profile_item_keys("restaurant_bar_tavern_structural_v1")

    assert full_keys != quick_keys
    assert fine_keys != quick_keys
    assert cafe_keys != quick_keys
    assert bar_keys != quick_keys

    assert "dining_room_finishes_package" in full_keys
    assert "curated_exterior_lighting_signage_allowance" in fine_keys
    assert "espresso_bar_power_rough_in" in cafe_keys
    assert "nightlife_lighting_signage_allowance" in bar_keys

    assert "dining_room_finishes_package" not in quick_keys
    assert "espresso_bar_power_rough_in" not in full_keys
    assert "nightlife_lighting_signage_allowance" not in cafe_keys


def test_restaurant_tile_profiles_and_defaults_resolve():
    assert restaurant_tile_profiles.DEALSHIELD_TILE_DEFAULTS == RESTAURANT_PROFILE_IDS

    expected_unique_tile = {
        "quick_service": "prototype_finish_rework_plus_10",
        "full_service": "service_labor_and_layout_plus_12",
        "fine_dining": "curated_mep_and_controls_plus_12",
        "cafe": "espresso_line_equipment_plus_8",
        "bar_tavern": "entertainment_and_life_safety_plus_10",
    }

    for subtype, profile_id in RESTAURANT_PROFILE_IDS.items():
        profile = get_dealshield_profile(profile_id)
        assert profile["version"] == "v1"
        assert profile["profile_id"] == profile_id
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and profile["derived_rows"]

        tile_ids = {tile["tile_id"] for tile in profile["tiles"]}
        assert {"cost_plus_10", "revenue_minus_10"}.issubset(tile_ids)
        assert expected_unique_tile[subtype] in tile_ids


def test_restaurant_tile_profiles_are_subtype_authored_not_clones():
    quick_profile = get_dealshield_profile("restaurant_quick_service_v1")
    full_profile = get_dealshield_profile("restaurant_full_service_v1")
    fine_profile = get_dealshield_profile("restaurant_fine_dining_v1")
    cafe_profile = get_dealshield_profile("restaurant_cafe_v1")
    bar_profile = get_dealshield_profile("restaurant_bar_tavern_v1")

    assert quick_profile != full_profile
    assert quick_profile != fine_profile
    assert quick_profile != cafe_profile
    assert quick_profile != bar_profile

    assert "prototype_rework" in {row["row_id"] for row in quick_profile["derived_rows"]}
    assert "service_flow_disruption" in {row["row_id"] for row in full_profile["derived_rows"]}
    assert "chef_table_commissioning_drag" in {row["row_id"] for row in fine_profile["derived_rows"]}
    assert "morning_peak_shortfall" in {row["row_id"] for row in cafe_profile["derived_rows"]}
    assert "late_night_compliance_push" in {row["row_id"] for row in bar_profile["derived_rows"]}


def test_restaurant_content_profiles_resolve_and_align_with_tiles():
    for profile_id in RESTAURANT_PROFILE_IDS.values():
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


def test_restaurant_content_profiles_are_subtype_authored_not_clones():
    quick_content = get_dealshield_content_profile("restaurant_quick_service_v1")
    full_content = get_dealshield_content_profile("restaurant_full_service_v1")
    fine_content = get_dealshield_content_profile("restaurant_fine_dining_v1")
    cafe_content = get_dealshield_content_profile("restaurant_cafe_v1")
    bar_content = get_dealshield_content_profile("restaurant_bar_tavern_v1")

    assert quick_content != full_content
    assert full_content != fine_content
    assert fine_content != cafe_content
    assert cafe_content != bar_content

    quick_driver_tiles = {d["tile_id"] for d in quick_content.get("fastest_change", {}).get("drivers", [])}
    full_driver_tiles = {d["tile_id"] for d in full_content.get("fastest_change", {}).get("drivers", [])}
    fine_driver_tiles = {d["tile_id"] for d in fine_content.get("fastest_change", {}).get("drivers", [])}
    cafe_driver_tiles = {d["tile_id"] for d in cafe_content.get("fastest_change", {}).get("drivers", [])}
    bar_driver_tiles = {d["tile_id"] for d in bar_content.get("fastest_change", {}).get("drivers", [])}

    assert "prototype_finish_rework_plus_10" in quick_driver_tiles
    assert "service_labor_and_layout_plus_12" in full_driver_tiles
    assert "curated_mep_and_controls_plus_12" in fine_driver_tiles
    assert "espresso_line_equipment_plus_8" in cafe_driver_tiles
    assert "entertainment_and_life_safety_plus_10" in bar_driver_tiles


def test_restaurant_engine_emits_profiles_for_all_subtypes_and_dealshield_alignment():
    for subtype, profile_id in RESTAURANT_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=8_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )

        assert payload.get("dealshield_tile_profile") == profile_id
        assert isinstance(payload.get("scope_items"), list) and payload["scope_items"]

        profile = get_dealshield_profile(profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"restaurant-{subtype}",
            payload=payload,
            profile=profile,
        )

        assert view_model.get("profile_id") == profile_id
        assert view_model.get("tile_profile_id") == profile_id
        assert isinstance(view_model.get("rows"), list) and view_model["rows"]
        assert isinstance(view_model.get("content"), dict)
        assert view_model["content"].get("profile_id") == profile_id


def test_restaurant_emits_wave1_dealshield_scenario_snapshots():
    for subtype, expected_profile_id in RESTAURANT_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=8_000,
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


def test_restaurant_decision_insurance_outputs_and_provenance():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    for subtype, expected_profile_id in RESTAURANT_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=8_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"restaurant-di-{subtype}",
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
