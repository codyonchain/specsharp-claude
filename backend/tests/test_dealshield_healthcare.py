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

HEALTHCARE_PCV_LABEL_ANCHOR_TOKENS = {
    "surgical_center": ("or turnover", "sterile-core", "block utilization"),
    "imaging_center": ("shielding", "quench", "modality throughput", "uptime"),
    "urgent_care": ("walk-in acuity", "peak-hour staffing", "visit velocity"),
    "outpatient_clinic": ("referral leakage", "template utilization", "no-show drag"),
    "medical_office_building": ("ti/lc burn", "lease-up velocity", "rollover stack"),
    "dental_office": ("chair utilization", "hygiene mix", "sterilization"),
    "hospital": ("nurse staffing intensity", "los pressure", "service-line mix"),
    "medical_center": ("procedure mix", "diagnostic throughput", "care-path coordination"),
    "nursing_home": ("census mix", "agency labor dependency", "reimbursement pressure"),
    "rehabilitation": ("therapy intensity", "authorization friction", "los drift"),
}

HEALTHCARE_MLW_FIRST_ANCHOR_TOKENS = {
    "surgical_center": ("or turnover", "sterile-core sequencing", "block utilization"),
    "imaging_center": ("shielding", "quench", "modality throughput", "uptime"),
    "urgent_care": ("walk-in acuity mix", "peak-hour staffing", "visit velocity"),
    "outpatient_clinic": ("referral leakage", "provider template utilization", "no-show drag"),
    "medical_office_building": ("ti/lc burn", "lease-up velocity", "rollover stack"),
    "dental_office": ("chair utilization", "hygiene mix", "sterilization bottlenecks"),
    "hospital": ("nurse staffing intensity", "los pressure", "service-line mix"),
    "medical_center": ("procedure mix", "diagnostic throughput", "care-path coordination"),
    "nursing_home": ("census mix", "agency labor dependency", "reimbursement pressure"),
    "rehabilitation": ("therapy intensity", "authorization friction", "los drift"),
}

HEALTHCARE_SCOPE_DEPTH_MINIMUMS = {
    "surgical_center": {
        "structural": 3,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 4,
        "finishes": 3,
    },
    "imaging_center": {
        "structural": 3,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 4,
        "finishes": 3,
    },
    "urgent_care": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "outpatient_clinic": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "medical_office_building": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "dental_office": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "hospital": {
        "structural": 4,
        "mechanical": 5,
        "electrical": 5,
        "plumbing": 4,
        "finishes": 4,
    },
    "medical_center": {
        "structural": 4,
        "mechanical": 5,
        "electrical": 5,
        "plumbing": 4,
        "finishes": 4,
    },
    "nursing_home": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "rehabilitation": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
}

HEALTHCARE_RUNTIME_SCOPE_MINIMUMS = {
    subtype: {
        "structural": 5,
        "mechanical": 6 if subtype in {"surgical_center", "imaging_center", "hospital", "medical_center"} else 5,
        "electrical": 6 if subtype in {"surgical_center", "imaging_center", "hospital", "medical_center"} else 5,
        "plumbing": 6 if subtype in {"surgical_center", "imaging_center", "hospital", "medical_center"} else 5,
        "finishes": 5,
    }
    for subtype in HEALTHCARE_PROFILE_IDS.keys()
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

        minimums_by_trade = HEALTHCARE_SCOPE_DEPTH_MINIMUMS[subtype]
        for trade_key, trade in trade_map.items():
            items = trade.get("items")
            assert isinstance(items, list) and items
            assert len(items) >= minimums_by_trade[trade_key]

            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_healthcare_runtime_scope_items_emit_wow_depth_for_all_subtypes():
    for subtype, expected_by_trade in HEALTHCARE_RUNTIME_SCOPE_MINIMUMS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=90_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        emitted = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(emitted.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in expected_by_trade.items():
            systems = emitted[trade_key].get("systems")
            assert isinstance(systems, list)
            assert len(systems) >= minimum, (
                f"{subtype}::{trade_key} expected >= {minimum} runtime systems, "
                f"found {len(systems)}"
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


def test_healthcare_mlw_and_primary_control_language_is_subtype_authored_with_anchor_tokens():
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        content = get_dealshield_content_profile(profile_id)
        policy = get_decision_insurance_policy(profile_id)
        assert isinstance(policy, dict)

        mlw_entries = content.get("most_likely_wrong", [])
        assert isinstance(mlw_entries, list) and mlw_entries
        first_mlw = mlw_entries[0].get("text", "")
        assert isinstance(first_mlw, str) and first_mlw.strip()

        mlw_text = first_mlw.lower()
        for token in HEALTHCARE_MLW_FIRST_ANCHOR_TOKENS[subtype]:
            assert token in mlw_text, f"{subtype} first MLW text missing token: {token}"

        pcv_label = policy["primary_control_variable"]["label"]
        assert isinstance(pcv_label, str) and pcv_label.strip()
        normalized_label = pcv_label.lower()
        assert normalized_label.startswith("ic-first ")
        for token in HEALTHCARE_PCV_LABEL_ANCHOR_TOKENS[subtype]:
            assert token in normalized_label, f"{subtype} PCV label missing token: {token}"


def test_healthcare_first_break_semantics_align_with_metric_type():
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=70_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"healthcare-break-semantics-{subtype}",
            payload=payload,
            profile=profile,
        )
        policy = get_decision_insurance_policy(profile_id)
        collapse_trigger = policy["collapse_trigger"]
        metric = collapse_trigger.get("metric")
        threshold = collapse_trigger.get("threshold")
        operator = collapse_trigger.get("operator")

        assert metric in {"value_gap_pct", "value_gap"}
        assert isinstance(threshold, (int, float))
        assert isinstance(operator, str) and operator.strip()

        if metric == "value_gap_pct":
            assert operator in {"<=", "<"}
            assert abs(float(threshold)) <= 100.0
        else:
            assert operator in {"<=", "<"}
            assert float(threshold) <= 0.0 or abs(float(threshold)) >= 100000.0

        first_break = view_model.get("first_break_condition")
        di_provenance = view_model.get("decision_insurance_provenance") or {}
        first_break_provenance = di_provenance.get("first_break_condition") or {}
        if first_break_provenance.get("status") == "available":
            assert isinstance(first_break, dict)
            assert first_break.get("break_metric") == metric
            assert first_break.get("threshold") == threshold
            assert first_break.get("operator") == operator
            assert isinstance(first_break.get("observed_value"), (int, float))
            if metric == "value_gap_pct":
                assert isinstance(first_break.get("observed_value_pct"), (int, float))


def test_healthcare_policy_collapse_contracts_are_subtype_diverse_and_structural():
    collapse_metric_families = set()
    flex_signatures = set()

    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        policy = get_decision_insurance_policy(profile_id)
        assert isinstance(policy, dict)

        collapse_trigger = policy.get("collapse_trigger")
        assert isinstance(collapse_trigger, dict)

        metric = collapse_trigger.get("metric")
        assert metric in {"value_gap_pct", "value_gap"}
        collapse_metric_families.add(metric)

        scenario_priority = collapse_trigger.get("scenario_priority")
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

        profile = get_dealshield_profile(profile_id)
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

        flex = policy.get("flex_calibration")
        assert isinstance(flex, dict)
        tight = float(flex.get("tight_max_pct"))
        moderate = float(flex.get("moderate_max_pct"))
        fallback = float(flex.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0
        flex_signatures.add((tight, moderate, fallback))

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}
    assert len(flex_signatures) == len(HEALTHCARE_PROFILE_IDS)


def test_healthcare_policy_break_and_flex_outputs_remain_deterministic():
    for subtype, profile_id in HEALTHCARE_PROFILE_IDS.items():
        kwargs = dict(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=70_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)

        profile = get_dealshield_profile(profile_id)
        view_a = build_dealshield_view_model(
            project_id=f"healthcare-break-deterministic-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"healthcare-break-deterministic-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        assert view_a.get("first_break_condition") == view_b.get("first_break_condition")
        assert view_a.get("flex_before_break_pct") == view_b.get("flex_before_break_pct")
        assert view_a.get("flex_before_break_band") == view_b.get("flex_before_break_band")

        provenance_a = view_a.get("decision_insurance_provenance") or {}
        provenance_b = view_b.get("decision_insurance_provenance") or {}
        assert provenance_a.get("first_break_condition") == provenance_b.get("first_break_condition")
        assert provenance_a.get("flex_before_break_pct") == provenance_b.get("flex_before_break_pct")
