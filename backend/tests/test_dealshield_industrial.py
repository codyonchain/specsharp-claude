from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import industrial as industrial_tile_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


INDUSTRIAL_PROFILE_IDS = {
    "warehouse": "industrial_warehouse_v1",
    "distribution_center": "industrial_distribution_center_v1",
    "manufacturing": "industrial_manufacturing_v1",
    "flex_space": "industrial_flex_space_v1",
    "cold_storage": "industrial_cold_storage_v1",
}


def test_industrial_subtypes_define_deterministic_dealshield_profile_ids():
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        config = get_building_config(BuildingType.INDUSTRIAL, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected_profile_id


def test_industrial_tile_profiles_and_defaults_resolve():
    assert industrial_tile_profiles.DEALSHIELD_TILE_DEFAULTS == INDUSTRIAL_PROFILE_IDS

    expected_driver_tile_by_subtype = {
        "warehouse": "structural_plus_10",
        "distribution_center": "structural_plus_10",
        "manufacturing": "structural_plus_10",
        "flex_space": "structural_plus_10",
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


def test_industrial_decision_insurance_outputs_and_provenance():
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

        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("enabled") is True
        assert di_provenance.get("profile_id") == expected_profile_id

        model_provenance = view_model.get("provenance")
        assert isinstance(model_provenance, dict)
        assert model_provenance.get("decision_insurance") == di_provenance

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
