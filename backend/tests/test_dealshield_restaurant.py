import pytest

from app.v2.services import dealshield_scenarios as dealshield_scenarios_module
from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.decision_insurance_policy import DECISION_INSURANCE_POLICY_BY_PROFILE_ID
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import restaurant as restaurant_tile_profiles
from app.v2.config.type_profiles.scope_items import restaurant as restaurant_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_scenarios import (
    build_dealshield_scenarios,
    refresh_dealshield_scenarios_payload,
)
from app.v2.services.dealshield_service import build_dealshield_view_model
from tests.dealshield_contract_assertions import assert_decision_insurance_truth_parity


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

RESTAURANT_SPECIAL_FEATURE_CASES = {
    "quick_service": "digital_menu_boards",
    "full_service": "private_dining",
    "fine_dining": "chef_table",
    "cafe": "bakery_display",
    "bar_tavern": "live_music_stage",
}


def _expected_special_feature_total(configured_feature, square_footage: float, pricing_status: str) -> float:
    if pricing_status == "included_in_baseline":
        return 0.0
    if isinstance(configured_feature, dict):
        if configured_feature.get("basis") == "AREA_SHARE_GSF":
            return (
                float(configured_feature["value"])
                * float(configured_feature["area_share_of_gsf"])
                * square_footage
            )
        if configured_feature.get("basis") == "COUNT_BASED":
            return float(configured_feature["value"]) * _default_count_for_feature(configured_feature)
        raise AssertionError(f"Unsupported structured restaurant feature config: {configured_feature}")
    return float(configured_feature) * square_footage


def _default_count_for_feature(configured_feature) -> float:
    count = configured_feature.get("count")
    if isinstance(count, (int, float)):
        return float(count)
    default_count_bands = configured_feature.get("default_count_bands") or []
    if default_count_bands:
        return float(default_count_bands[0]["count"])
    raise AssertionError(f"Count-based restaurant feature missing default count: {configured_feature}")


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


def _base_dscr_cell(view_model):
    rows = view_model.get("rows")
    assert isinstance(rows, list) and rows
    base_row = next(
        (
            row
            for row in rows
            if isinstance(row, dict)
            and (
                row.get("scenario_id") == "base"
                or str(row.get("label", "")).strip().lower() == "base"
            )
        ),
        None,
    )
    assert isinstance(base_row, dict)
    cells = base_row.get("cells")
    assert isinstance(cells, list)
    dscr_cell = next(
        (
            cell
            for cell in cells
            if isinstance(cell, dict)
            and (cell.get("col_id") or cell.get("tile_id") or cell.get("id")) == "dscr"
        ),
        None,
    )
    assert isinstance(dscr_cell, dict)
    return dscr_cell


def _clear_financing_assumptions_keep_dscr(payload):
    payload.pop("financing_assumptions", None)
    ownership_analysis = payload.get("ownership_analysis")
    if not isinstance(ownership_analysis, dict):
        return
    debt_metrics = ownership_analysis.get("debt_metrics")
    if not isinstance(debt_metrics, dict):
        return
    for key in (
        "debt_pct",
        "ltv",
        "interest_rate_pct",
        "amort_years",
        "loan_term_years",
        "interest_only_months",
    ):
        debt_metrics.pop(key, None)


def _is_numeric_dscr(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def test_restaurant_dscr_visibility_policy_is_type_aware():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    financing_disclosure = "Not modeled: financing assumptions missing"
    observed_numeric_with_disclosure = False
    for subtype, expected_profile_id in RESTAURANT_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=8_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        _clear_financing_assumptions_keep_dscr(payload)
        scenarios = payload.get("dealshield_scenarios", {}).get("scenarios", {})
        base_source_dscr = _resolve_metric_ref(
            scenarios.get("base", {}),
            "ownership_analysis.debt_metrics.calculated_dscr",
        )
        source_is_numeric = _is_numeric_dscr(base_source_dscr)
        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"restaurant-dscr-visible-{subtype}",
            payload=payload,
            profile=profile,
        )
        base_dscr_cell = _base_dscr_cell(view_model)
        displayed_dscr = base_dscr_cell.get("value")
        display_is_numeric = _is_numeric_dscr(displayed_dscr)
        assert display_is_numeric == source_is_numeric
        if source_is_numeric:
            observed_numeric_with_disclosure = True
        else:
            assert displayed_dscr is None
            assert base_dscr_cell.get("provenance_kind") == "missing"
        disclosures = view_model.get("dealshield_disclosures")
        assert isinstance(disclosures, list)
        if source_is_numeric:
            assert financing_disclosure in disclosures
        assert view_model.get("decision_status") in allowed_statuses
        assert isinstance(view_model.get("decision_reason_code"), str)
        assert view_model["decision_reason_code"].strip()
        assert isinstance(view_model.get("decision_status_provenance"), dict)
        assert isinstance(view_model.get("decision_insurance_provenance"), dict)
    assert observed_numeric_with_disclosure


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


def test_restaurant_full_service_policy_and_question_bank_copy():
    full_service_policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID["restaurant_full_service_v1"]
    assert (
        full_service_policy["primary_control_variable"]["label"]
        == "Labor Efficiency + Service-Flow Layout (Turns / Staffing)"
    )

    full_content = get_dealshield_content_profile("restaurant_full_service_v1")
    full_questions = [
        question
        for entry in full_content.get("question_bank", [])
        if isinstance(entry, dict)
        for question in entry.get("questions", [])
        if isinstance(question, str)
    ]
    assert (
        "Occupancy cost % at projected sales (rent + CAM + taxes + insurance) - confirm lease terms and CAM assumptions."
        in full_questions
    )
    assert (
        "Table turns by daypart + average check - what is the validated throughput under the current layout?"
        in full_questions
    )
    assert (
        "Labor model realism: FOH/BOH staffing by shift + training ramp - confirm staffing plan supports the assumed service level."
        in full_questions
    )


def test_restaurant_quick_service_policy_and_content_copy():
    quick_service_policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID["restaurant_quick_service_v1"]
    assert (
        quick_service_policy["primary_control_variable"]["label"]
        == "Prototype Buildout Spec Drift (Finish + Equipment)"
    )

    quick_content = get_dealshield_content_profile("restaurant_quick_service_v1")
    quick_questions = [
        question
        for entry in quick_content.get("question_bank", [])
        if isinstance(entry, dict)
        for question in entry.get("questions", [])
        if isinstance(question, str)
    ]
    assert (
        "Drive-thru service time target (seconds) and modeled cars/hour at peak - what is the constraint (order point, window, kitchen line)?"
        in quick_questions
    )
    assert (
        "Equipment lead times (hood, walk-in, POS) - which items are owner-furnished vs GC carry?"
        in quick_questions
    )

    quick_mlw_text = [
        entry.get("text")
        for entry in quick_content.get("most_likely_wrong", [])
        if isinstance(entry, dict)
    ]
    assert (
        "Opening ramp assumes day-1 throughput; validate drive-thru speed, peak-hour capacity, and ticket mix stabilization."
        in quick_mlw_text
    )


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
        assert_decision_insurance_truth_parity(view_model)

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
        assert expected_profile_id in DECISION_INSURANCE_POLICY_BY_PROFILE_ID
        policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[expected_profile_id]

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy_cfg["primary_control_variable"]["tile_id"]

        first_break_block = di_provenance.get("first_break_condition")
        assert isinstance(first_break_block, dict)
        if first_break_block.get("status") == "available":
            if first_break_block.get("source") == "decision_insurance_policy.collapse_trigger":
                collapse_cfg = policy_cfg["collapse_trigger"]
                expected_operator = collapse_cfg.get("operator") if isinstance(collapse_cfg.get("operator"), str) and collapse_cfg.get("operator").strip() else "<="
                first_break = view_model.get("first_break_condition")
                assert isinstance(first_break, dict)
                assert first_break.get("break_metric") == collapse_cfg.get("metric")
                assert first_break.get("operator") == expected_operator
                assert first_break.get("threshold") == collapse_cfg.get("threshold")
        else:
            assert first_break_block.get("reason") != "no_modeled_break_condition"

        flex_block = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_block, dict)
        assert flex_block.get("status") == "available"
        assert view_model.get("flex_before_break_band") in {"tight", "moderate", "comfortable"}
        assert flex_block.get("band") in {"tight", "moderate", "comfortable"}

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


@pytest.mark.parametrize("stress_band_pct", [10, 7, 5, 3])
def test_restaurant_scenario_controls_accept_allowed_stress_band_values(stress_band_pct):
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    payload["dealshield_controls"] = {
        "stress_band_pct": stress_band_pct,
    }

    config = get_building_config(BuildingType.RESTAURANT, "full_service")
    scenarios_bundle = build_dealshield_scenarios(
        base_payload=payload,
        building_config=config,
        engine=unified_engine,
    )
    scenario_inputs = scenarios_bundle["provenance"]["scenario_inputs"]
    conservative = scenario_inputs["conservative"]

    assert scenario_inputs["base"]["stress_band_pct"] == stress_band_pct
    assert conservative["stress_band_pct"] == stress_band_pct
    assert conservative["cost_scalar"] == pytest.approx(1.0 + (stress_band_pct / 100.0))
    assert conservative["revenue_scalar"] == pytest.approx(1.0 - (stress_band_pct / 100.0))


def test_restaurant_base_scenario_uses_recompute_helper_stack_before_commit(monkeypatch):
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    config = get_building_config(BuildingType.RESTAURANT, "full_service")
    original_build_bundle = dealshield_scenarios_module._build_ownership_bundle_without_trace_side_effects
    seen_scenarios = []

    def tracking_build_bundle(*args, **kwargs):
        calculation_context = kwargs.get("calculation_context") or {}
        seen_scenarios.append(calculation_context.get("scenario"))
        return original_build_bundle(*args, **kwargs)

    monkeypatch.setattr(
        dealshield_scenarios_module,
        "_build_ownership_bundle_without_trace_side_effects",
        tracking_build_bundle,
    )

    scenarios_bundle = build_dealshield_scenarios(
        base_payload=payload,
        building_config=config,
        engine=unified_engine,
    )

    assert scenarios_bundle["scenarios"]["base"]
    assert seen_scenarios
    assert seen_scenarios[0] == "base"
    assert "base" in seen_scenarios


def test_restaurant_refresh_helper_replaces_stale_stored_scenarios():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    stale_value = 999_999_999.0
    payload["dealshield_scenarios"]["scenarios"]["base"]["totals"]["total_project_cost"] = stale_value

    refreshed = refresh_dealshield_scenarios_payload(
        payload,
        building_type="restaurant",
        subtype="full_service",
        engine=unified_engine,
    )

    refreshed_value = refreshed["dealshield_scenarios"]["scenarios"]["base"]["totals"]["total_project_cost"]
    assert refreshed_value != stale_value
    assert refreshed_value == pytest.approx(payload["totals"]["total_project_cost"])


def test_restaurant_scenario_controls_with_anchors_emit_expected_provenance_for_all_subtypes():
    for subtype, expected_profile_id in RESTAURANT_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=8_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        base_total_cost = float(payload["totals"]["total_project_cost"])
        base_annual_revenue = float(payload["revenue_analysis"]["annual_revenue"])
        target_cost_anchor = round(base_total_cost * 1.04, 2)
        target_revenue_anchor = round(base_annual_revenue * 1.05, 2)
        payload["dealshield_controls"] = {
            "stress_band_pct": 7,
            "use_cost_anchor": True,
            "anchor_total_project_cost": target_cost_anchor,
            "use_revenue_anchor": True,
            "anchor_annual_revenue": target_revenue_anchor,
        }

        config = get_building_config(BuildingType.RESTAURANT, subtype)
        scenarios_bundle = build_dealshield_scenarios(
            base_payload=payload,
            building_config=config,
            engine=unified_engine,
        )

        assert scenarios_bundle["profile_id"] == expected_profile_id
        scenario_inputs = scenarios_bundle["provenance"]["scenario_inputs"]
        scenario_ids = scenarios_bundle["provenance"]["scenario_ids"]
        assert "base" in scenario_ids

        base_snapshot = scenarios_bundle["scenarios"]["base"]
        assert base_snapshot["totals"]["total_project_cost"] == pytest.approx(target_cost_anchor)

        for scenario_id in scenario_ids:
            scenario_input = scenario_inputs[scenario_id]
            assert scenario_input["stress_band_pct"] == 7
            assert scenario_input["cost_anchor_used"] is True
            assert scenario_input["cost_anchor_value"] == pytest.approx(target_cost_anchor)
            assert scenario_input["revenue_anchor_used"] is True
            assert scenario_input["revenue_anchor_value"] == pytest.approx(target_revenue_anchor)


def test_restaurant_special_features_math_and_breakdown_reconcile_for_all_subtypes():
    square_footage = 8_000
    for subtype, feature_key in RESTAURANT_SPECIAL_FEATURE_CASES.items():
        baseline = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[],
        )
        with_feature = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
            special_features=[feature_key],
        )

        config = get_building_config(BuildingType.RESTAURANT, subtype)
        configured_feature = config.special_features[feature_key]
        expected_status = (config.special_feature_pricing_statuses or {}).get(feature_key, "incremental")
        expected_delta = _expected_special_feature_total(
            configured_feature,
            square_footage,
            expected_status,
        )

        base_total = float(baseline["construction_costs"]["special_features_total"])
        feature_total = float(with_feature["construction_costs"]["special_features_total"])
        delta = feature_total - base_total
        assert delta == pytest.approx(expected_delta, rel=1e-3)

        breakdown = with_feature["construction_costs"]["special_features_breakdown"]
        assert isinstance(breakdown, list) and breakdown
        breakdown_map = {
            entry.get("id"): entry
            for entry in breakdown
            if isinstance(entry, dict) and entry.get("id")
        }
        assert feature_key in breakdown_map
        feature_entry = breakdown_map[feature_key]
        assert feature_entry.get("pricing_status") == expected_status
        if isinstance(configured_feature, dict):
            assert feature_entry.get("pricing_basis") == configured_feature.get("basis")
            assert float(feature_entry.get("configured_value", 0.0) or 0.0) == pytest.approx(
                float(configured_feature["value"]),
                rel=1e-3,
            )
            if configured_feature.get("basis") == "AREA_SHARE_GSF":
                assert float(
                    feature_entry.get("configured_area_share_of_gsf", 0.0) or 0.0
                ) == pytest.approx(
                    float(configured_feature["area_share_of_gsf"]),
                    rel=1e-3,
                )
            elif configured_feature.get("basis") == "COUNT_BASED":
                assert float(
                    feature_entry.get("configured_cost_per_count", 0.0) or 0.0
                ) == pytest.approx(
                    float(configured_feature["value"]),
                    rel=1e-3,
                )
                assert float(feature_entry.get("applied_quantity", 0.0) or 0.0) == pytest.approx(
                    _default_count_for_feature(configured_feature),
                    rel=1e-3,
                )
                assert feature_entry.get("quantity_source") in {
                    "configured_default_count",
                    "size_band_default",
                }
                assert feature_entry.get("unit_label") == configured_feature.get("unit_label")
            else:
                raise AssertionError(f"Unsupported structured restaurant feature config: {configured_feature}")
        else:
            assert float(feature_entry.get("configured_cost_per_sf", 0.0) or 0.0) == pytest.approx(
                float(configured_feature),
                rel=1e-3,
            )
            expected_applied_cost_per_sf = (
                0.0 if expected_status == "included_in_baseline" else float(configured_feature)
            )
            assert float(feature_entry.get("cost_per_sf", 0.0) or 0.0) == pytest.approx(
                expected_applied_cost_per_sf,
                rel=1e-3,
            )
        if isinstance(configured_feature, dict):
            if configured_feature.get("basis") == "AREA_SHARE_GSF":
                expected_applied_value = (
                    0.0 if expected_status == "included_in_baseline" else float(configured_feature["value"])
                )
                assert float(feature_entry.get("applied_value", 0.0) or 0.0) == pytest.approx(
                    expected_applied_value,
                    rel=1e-3,
                )
            elif configured_feature.get("basis") == "COUNT_BASED":
                expected_cost_per_count = (
                    0.0 if expected_status == "included_in_baseline" else float(configured_feature["value"])
                )
                assert float(feature_entry.get("cost_per_count", 0.0) or 0.0) == pytest.approx(
                    expected_cost_per_count,
                    rel=1e-3,
                )
        assert float(feature_entry.get("total_cost", 0.0) or 0.0) == pytest.approx(expected_delta, rel=1e-3)
        assert sum(
            float(item.get("total_cost", 0.0) or 0.0)
            for item in breakdown
            if isinstance(item, dict)
        ) == pytest.approx(feature_total, rel=1e-3)


def test_full_service_restaurant_prices_only_incremental_features_and_preserves_selected_status():
    square_footage = 8_000
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["outdoor_seating", "wine_cellar"],
    )

    config = get_building_config(BuildingType.RESTAURANT, "full_service")
    assert config is not None
    wine_cellar_rule = config.special_features["wine_cellar"]
    outdoor_seating_rule = config.special_features["outdoor_seating"]
    assert isinstance(wine_cellar_rule, dict)
    assert isinstance(outdoor_seating_rule, (int, float))
    expected_incremental_total = (
        float(wine_cellar_rule["value"])
        * (float(wine_cellar_rule["area_share_of_gsf"]) * square_footage)
    )

    assert float(result["construction_costs"]["special_features_total"]) == pytest.approx(
        expected_incremental_total,
        rel=1e-3,
    )

    breakdown = result["construction_costs"]["special_features_breakdown"]
    breakdown_by_id = {
        item["id"]: item
        for item in breakdown
        if isinstance(item, dict) and item.get("id")
    }

    included_row = breakdown_by_id["outdoor_seating"]
    assert included_row.get("pricing_status") == "included_in_baseline"
    assert float(included_row.get("configured_cost_per_sf", 0.0) or 0.0) == pytest.approx(
        float(outdoor_seating_rule),
        rel=1e-3,
    )
    assert float(included_row.get("cost_per_sf", 0.0) or 0.0) == 0.0
    assert float(included_row.get("total_cost", 0.0) or 0.0) == 0.0

    incremental_row = breakdown_by_id["wine_cellar"]
    assert incremental_row.get("pricing_status") == "incremental"
    assert incremental_row.get("pricing_basis") == "AREA_SHARE_GSF"
    assert float(incremental_row.get("configured_value", 0.0) or 0.0) == pytest.approx(
        float(wine_cellar_rule["value"]),
        rel=1e-3,
    )
    assert float(incremental_row.get("configured_area_share_of_gsf", 0.0) or 0.0) == pytest.approx(
        float(wine_cellar_rule["area_share_of_gsf"]),
        rel=1e-3,
    )
    assert float(incremental_row.get("applied_value", 0.0) or 0.0) == pytest.approx(
        float(wine_cellar_rule["value"]),
        rel=1e-3,
    )
    assert float(incremental_row.get("total_cost", 0.0) or 0.0) == pytest.approx(
        expected_incremental_total,
        rel=1e-3,
    )


def test_full_service_restaurant_included_feature_does_not_inflate_total_project_cost():
    square_footage = 6_500
    baseline = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[],
    )
    included_only = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["private_dining"],
    )
    mixed = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["private_dining", "wine_cellar"],
    )

    config = get_building_config(BuildingType.RESTAURANT, "full_service")
    assert config is not None
    wine_cellar_rule = config.special_features["wine_cellar"]
    assert isinstance(wine_cellar_rule, dict)
    expected_incremental_total = (
        float(wine_cellar_rule["value"])
        * (float(wine_cellar_rule["area_share_of_gsf"]) * square_footage)
    )

    assert float(included_only["construction_costs"]["special_features_total"]) == 0.0
    assert float(included_only["totals"]["total_project_cost"]) == pytest.approx(
        float(baseline["totals"]["total_project_cost"]),
        rel=1e-3,
    )
    assert float(mixed["construction_costs"]["special_features_total"]) == pytest.approx(
        expected_incremental_total,
        rel=1e-3,
    )
    assert float(mixed["totals"]["total_project_cost"]) - float(
        baseline["totals"]["total_project_cost"]
    ) == pytest.approx(
        expected_incremental_total,
        rel=1e-3,
    )


def test_restaurant_margin_normalized_trace_emitted_once_for_all_subtypes():
    for subtype in RESTAURANT_PROFILE_IDS:
        payload = unified_engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            square_footage=5_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        margin_traces = [
            entry
            for entry in payload.get("calculation_trace", [])
            if isinstance(entry, dict) and entry.get("step") == "margin_normalized"
        ]
        assert len(margin_traces) == 1, f"Expected exactly one margin_normalized trace for subtype={subtype}"
