import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, get_building_config
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_ID,
    get_decision_insurance_policy,
)
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import healthcare as healthcare_tile_profiles
from app.v2.config.type_profiles.scope_items import healthcare as healthcare_scope_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_scenarios import build_dealshield_scenarios
from app.v2.services.dealshield_service import build_dealshield_view_model


HEALTHCARE_PROFILE_IDS = {
    "surgical_center": "healthcare_surgical_center_v1",
    "imaging_center": "healthcare_imaging_center_v1",
    "urgent_care": "healthcare_urgent_care_v1",
    "outpatient_clinic": "healthcare_outpatient_clinic_v1",
    "medical_office_building": "healthcare_medical_office_building_v1",
    "dental_office": "healthcare_dental_office_v1",
    "hospital": "healthcare_hospital_v1",
    "medical_center": "healthcare_medical_center_v1",
    "nursing_home": "healthcare_nursing_home_v1",
    "rehabilitation": "healthcare_rehabilitation_v1",
}

HEALTHCARE_SCOPE_PROFILE_IDS = {
    "surgical_center": "healthcare_surgical_center_structural_v1",
    "imaging_center": "healthcare_imaging_center_structural_v1",
    "urgent_care": "healthcare_urgent_care_structural_v1",
    "outpatient_clinic": "healthcare_outpatient_clinic_structural_v1",
    "medical_office_building": "healthcare_medical_office_building_structural_v1",
    "dental_office": "healthcare_dental_office_structural_v1",
    "hospital": "healthcare_hospital_structural_v1",
    "medical_center": "healthcare_medical_center_structural_v1",
    "nursing_home": "healthcare_nursing_home_structural_v1",
    "rehabilitation": "healthcare_rehabilitation_structural_v1",
}

HEALTHCARE_UNIQUE_TILE_IDS = {
    "surgical_center": "or_turnover_and_sterile_core_plus_12",
    "imaging_center": "shielding_and_power_quality_plus_11",
    "urgent_care": "triage_flow_and_lab_turns_plus_10",
    "outpatient_clinic": "exam_program_and_room_standard_plus_9",
    "medical_office_building": "tenant_fitout_mep_stack_plus_10",
    "dental_office": "chairside_vacuum_and_gas_plus_11",
    "hospital": "acuity_mep_redundancy_plus_12",
    "medical_center": "service_line_power_density_plus_11",
    "nursing_home": "resident_room_life_safety_plus_9",
    "rehabilitation": "therapy_gym_mep_integration_plus_10",
}


def _tile_map(profile_id: str):
    profile = get_dealshield_profile(profile_id)
    return {tile["tile_id"]: tile for tile in profile.get("tiles", []) if isinstance(tile, dict)}


def _scope_trade_map(profile_id: str):
    profile = healthcare_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    return {
        trade.get("trade_key"): trade
        for trade in profile.get("trade_profiles", [])
        if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
    }


def _top_two_trade_keys(subtype: str):
    cfg = get_building_config(BuildingType.HEALTHCARE, subtype)
    assert cfg is not None
    shares = {
        "structural": float(cfg.trades.structural),
        "mechanical": float(cfg.trades.mechanical),
        "electrical": float(cfg.trades.electrical),
        "plumbing": float(cfg.trades.plumbing),
        "finishes": float(cfg.trades.finishes),
    }
    return [
        trade_key
        for trade_key, _share in sorted(
            shares.items(),
            key=lambda item: (-item[1], item[0]),
        )[:2]
    ]


def _resolve_metric_ref(payload, metric_ref):
    current = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def test_healthcare_subtypes_define_deterministic_scope_and_dealshield_profile_ids():
    for subtype in HEALTHCARE_PROFILE_IDS:
        config = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == HEALTHCARE_PROFILE_IDS[subtype]
        assert config.scope_items_profile == HEALTHCARE_SCOPE_PROFILE_IDS[subtype]


def test_healthcare_scope_defaults_and_profiles_resolve():
    assert healthcare_scope_profiles.SCOPE_ITEM_DEFAULTS == HEALTHCARE_SCOPE_PROFILE_IDS
    for profile_id in HEALTHCARE_SCOPE_PROFILE_IDS.values():
        profile = healthcare_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        assert isinstance(profile, dict)
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and trade_profiles


def test_healthcare_scope_profiles_have_depth_and_normalized_allocations():
    for subtype, profile_id in HEALTHCARE_SCOPE_PROFILE_IDS.items():
        trade_map = _scope_trade_map(profile_id)
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        dominant_trade_keys = set(_top_two_trade_keys(subtype))
        for trade_key, trade in trade_map.items():
            items = trade.get("items")
            assert isinstance(items, list) and items
            min_item_count = 3 if trade_key in dominant_trade_keys else 2
            assert len(items) >= min_item_count

            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_healthcare_scope_profiles_are_subtype_authored_not_clones():
    signatures = {}
    for subtype, profile_id in HEALTHCARE_SCOPE_PROFILE_IDS.items():
        trade_map = _scope_trade_map(profile_id)
        signature = tuple(
            (
                trade_key,
                tuple(
                    item.get("key")
                    for item in (trade_map[trade_key].get("items") or [])
                    if isinstance(item, dict)
                ),
            )
            for trade_key in sorted(trade_map.keys())
        )
        signatures[subtype] = signature

    assert len(set(signatures.values())) == len(signatures)


def test_healthcare_tile_profiles_and_defaults_resolve():
    assert healthcare_tile_profiles.DEALSHIELD_TILE_DEFAULTS == HEALTHCARE_PROFILE_IDS

    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        profile = get_dealshield_profile(profile_id)
        assert profile["version"] == "v1"
        assert profile["profile_id"] == profile_id
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and len(profile["derived_rows"]) >= 3

        tile_ids = {tile["tile_id"] for tile in profile["tiles"]}
        assert {"cost_plus_10", "revenue_minus_10"}.issubset(tile_ids)
        assert HEALTHCARE_UNIQUE_TILE_IDS[subtype] in tile_ids

        for row in profile["derived_rows"]:
            assert isinstance(row, dict)
            for key in ("apply_tiles", "plus_tiles"):
                tile_refs = row.get(key) if isinstance(row.get(key), list) else []
                for tile_id in tile_refs:
                    assert tile_id in tile_ids


def test_healthcare_tile_profiles_are_subtype_authored_not_clones():
    signatures = {}
    extra_row_ids = set()
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        profile = get_dealshield_profile(profile_id)
        tile_ids = tuple(sorted(tile["tile_id"] for tile in profile.get("tiles", []) if isinstance(tile, dict)))
        row_ids = tuple(
            row.get("row_id")
            for row in profile.get("derived_rows", [])
            if isinstance(row, dict)
        )
        signatures[subtype] = (tile_ids, row_ids)
        if len(row_ids) >= 3:
            extra_row_ids.add(row_ids[2])
    assert len(set(signatures.values())) == len(signatures)
    assert len(extra_row_ids) == len(HEALTHCARE_PROFILE_IDS)


def test_healthcare_content_profiles_resolve_and_align_with_tiles():
    for profile_id in HEALTHCARE_PROFILE_IDS.values():
        tile_ids = set(_tile_map(profile_id).keys())
        content = get_dealshield_content_profile(profile_id)

        assert content["version"] == "v1"
        assert content["profile_id"] == profile_id

        drivers = content.get("fastest_change", {}).get("drivers", [])
        assert isinstance(drivers, list) and len(drivers) == 3
        driver_tile_ids = {
            driver.get("tile_id")
            for driver in drivers
            if isinstance(driver, dict) and isinstance(driver.get("tile_id"), str)
        }
        assert driver_tile_ids.issubset(tile_ids)

        question_entries = content.get("question_bank", [])
        assert isinstance(question_entries, list) and len(question_entries) == 3
        question_driver_tile_ids = set()
        for entry in question_entries:
            assert isinstance(entry, dict)
            tile_id = entry.get("driver_tile_id")
            assert isinstance(tile_id, str)
            question_driver_tile_ids.add(tile_id)
            questions = entry.get("questions")
            assert isinstance(questions, list) and len(questions) >= 2
        assert question_driver_tile_ids.issubset(tile_ids)

        likely_wrong_entries = content.get("most_likely_wrong", [])
        assert isinstance(likely_wrong_entries, list) and len(likely_wrong_entries) >= 3
        likely_wrong_tile_ids = {
            entry.get("driver_tile_id")
            for entry in likely_wrong_entries
            if isinstance(entry, dict) and isinstance(entry.get("driver_tile_id"), str)
        }
        assert likely_wrong_tile_ids.issubset(tile_ids)

        mlw_texts = [
            entry.get("text")
            for entry in likely_wrong_entries
            if isinstance(entry, dict) and isinstance(entry.get("text"), str)
        ]
        assert len(mlw_texts) == len(set(mlw_texts))

        red_flags = content.get("red_flags_actions", [])
        assert isinstance(red_flags, list) and len(red_flags) >= 3


def test_healthcare_content_profiles_are_subtype_authored_not_clones():
    signatures = {}
    mlw_first_lines = []
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        content = get_dealshield_content_profile(profile_id)
        drivers = tuple(
            driver.get("tile_id")
            for driver in content.get("fastest_change", {}).get("drivers", [])
            if isinstance(driver, dict)
        )
        mlw = tuple(
            entry.get("text")
            for entry in content.get("most_likely_wrong", [])
            if isinstance(entry, dict)
        )
        signatures[subtype] = (drivers, mlw)
        if mlw:
            mlw_first_lines.append(mlw[0])

    assert len(set(signatures.values())) == len(signatures)
    assert len(mlw_first_lines) == len(set(mlw_first_lines))


def test_healthcare_profile_resolution_is_deterministic():
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        expected_scope_profile_id = HEALTHCARE_SCOPE_PROFILE_IDS[subtype]

        tile_first = get_dealshield_profile(profile_id)
        tile_second = get_dealshield_profile(profile_id)
        assert tile_first == tile_second

        content_first = get_dealshield_content_profile(profile_id)
        content_second = get_dealshield_content_profile(profile_id)
        assert content_first == content_second

        config_first = get_building_config(BuildingType.HEALTHCARE, subtype)
        config_second = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert config_first is not None and config_second is not None
        assert config_first.dealshield_tile_profile == profile_id
        assert config_second.dealshield_tile_profile == profile_id
        assert config_first.scope_items_profile == expected_scope_profile_id
        assert config_second.scope_items_profile == expected_scope_profile_id


def test_healthcare_runtime_emits_scenarios_and_truthful_provenance_for_all_subtypes():
    for subtype, expected_profile_id in HEALTHCARE_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=65_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload["dealshield_tile_profile"] == expected_profile_id

        profile = get_dealshield_profile(expected_profile_id)
        tile_map = _tile_map(expected_profile_id)
        derived_rows = profile["derived_rows"]
        expected_scenario_ids = ["base"] + [row["row_id"] for row in derived_rows]
        expected_metric_refs = [tile["metric_ref"] for tile in profile["tiles"]]

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
                assert scenario_input.get("cost_scalar") == pytest.approx(expected_cost_scalar)
            if expected_revenue_scalar is None:
                assert scenario_input.get("revenue_scalar") is None
            else:
                assert scenario_input.get("revenue_scalar") == pytest.approx(expected_revenue_scalar)

            driver_tile_ids = [
                tile_id
                for tile_id in applied_tile_ids
                if tile_map[tile_id]["metric_ref"]
                not in {"totals.total_project_cost", "revenue_analysis.annual_revenue"}
            ]
            if not driver_tile_ids:
                assert scenario_input.get("driver") is None
                continue
            assert len(driver_tile_ids) == 1
            expected_driver_tile_id = driver_tile_ids[0]
            driver_entry = scenario_input.get("driver")
            assert isinstance(driver_entry, dict)
            assert driver_entry.get("tile_id") == expected_driver_tile_id
            assert driver_entry.get("metric_ref") == tile_map[expected_driver_tile_id]["metric_ref"]
            assert (
                ("op" in driver_entry and "value" in driver_entry)
                or isinstance(driver_entry.get("transforms"), list)
            )


def test_healthcare_scenario_controls_with_anchors_emit_expected_provenance_for_all_subtypes():
    for subtype, expected_profile_id in HEALTHCARE_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=65_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        base_total_cost = float(payload["totals"]["total_project_cost"])
        base_annual_revenue = float(payload["revenue_analysis"]["annual_revenue"])
        target_cost_anchor = round(base_total_cost * 1.03, 2)
        target_revenue_anchor = round(base_annual_revenue * 1.04, 2)
        payload["dealshield_controls"] = {
            "stress_band_pct": 7,
            "use_cost_anchor": True,
            "anchor_total_project_cost": target_cost_anchor,
            "use_revenue_anchor": True,
            "anchor_annual_revenue": target_revenue_anchor,
        }

        config = get_building_config(BuildingType.HEALTHCARE, subtype)
        scenarios_bundle = build_dealshield_scenarios(
            base_payload=payload,
            building_config=config,
            engine=unified_engine,
        )
        assert scenarios_bundle["profile_id"] == expected_profile_id
        scenario_inputs = scenarios_bundle["provenance"]["scenario_inputs"]
        scenario_ids = scenarios_bundle["provenance"]["scenario_ids"]

        base_snapshot = scenarios_bundle["scenarios"]["base"]
        assert base_snapshot["totals"]["total_project_cost"] == pytest.approx(target_cost_anchor)

        for scenario_id in scenario_ids:
            scenario_input = scenario_inputs[scenario_id]
            assert scenario_input["stress_band_pct"] == 7
            assert scenario_input["cost_anchor_used"] is True
            assert scenario_input["cost_anchor_value"] == pytest.approx(target_cost_anchor)
            assert scenario_input["revenue_anchor_used"] is True
            assert scenario_input["revenue_anchor_value"] == pytest.approx(target_revenue_anchor)


def test_healthcare_di_contract_and_provenance_are_policy_driven_for_all_profiles():
    for subtype, expected_profile_id in HEALTHCARE_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=70_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload["dealshield_tile_profile"] == expected_profile_id
        profile = get_dealshield_profile(expected_profile_id)
        policy = get_decision_insurance_policy(expected_profile_id)
        assert isinstance(policy, dict)

        view_model = build_dealshield_view_model(
            project_id=f"healthcare-di-{subtype}",
            payload=payload,
            profile=profile,
        )
        assert view_model.get("decision_status") in {"GO", "Needs Work", "NO-GO", "PENDING"}
        assert isinstance(view_model.get("decision_reason_code"), str)
        assert isinstance(view_model.get("decision_status_provenance"), dict)

        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("profile_id") == expected_profile_id

        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == expected_profile_id

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy["primary_control_variable"]["tile_id"]

        pcv_provenance = di_provenance.get("primary_control_variable")
        assert isinstance(pcv_provenance, dict)
        assert pcv_provenance.get("status") == "available"
        assert pcv_provenance.get("selection_basis") == "policy_primary_control_variable"
        assert pcv_provenance.get("policy_source") == "decision_insurance_policy.primary_control_variable"

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

        view_provenance = view_model.get("provenance")
        assert isinstance(view_provenance, dict)
        assert view_provenance.get("profile_id") == expected_profile_id
        assert view_provenance.get("decision_insurance") == di_provenance
