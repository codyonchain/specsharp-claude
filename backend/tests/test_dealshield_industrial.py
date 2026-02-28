from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.decision_insurance_policy import DECISION_INSURANCE_POLICY_BY_PROFILE_ID
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

INDUSTRIAL_POLICY_EXPECTATIONS = {
    "warehouse": {
        "tile_id": "structural_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -8.0,
    },
    "distribution_center": {
        "tile_id": "electrical_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -25.0,
    },
    "manufacturing": {
        "tile_id": "process_mep_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -35.0,
    },
    "flex_space": {
        "tile_id": "office_finish_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -6.0,
    },
    "cold_storage": {
        "tile_id": "equipment_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -30.0,
    },
}

INDUSTRIAL_PRIMARY_CONTROL_LABELS = {
    "warehouse": "Sitework + Shell Basis + Lease-Up Assumptions",
    "distribution_center": "IC-First Power Density + Sortation Throughput Control",
    "manufacturing": "IC-First Process Utility Drift + Commissioning Yield Control",
    "flex_space": "IC-First Office/Finish Creep + Tenant-Mix Control",
    "cold_storage": "IC-First Refrigeration Plant + Envelope + Commissioning Ramp",
}

INDUSTRIAL_SCOPE_PROFILE_IDS = {
    "distribution_center": "industrial_distribution_center_structural_v1",
    "flex_space": "industrial_flex_space_structural_v1",
}


def _is_numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _normalize_scenario_key(value):
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace(" ", "_")
    return normalized if normalized else None


def _normalize_percentish_value(value):
    if not _is_numeric(value):
        return None
    parsed = float(value)
    if abs(parsed) <= 1.5:
        return parsed * 100.0
    return parsed


def _classify_break_risk(first_break_condition, flex_before_break_pct):
    scenario_key = None
    if isinstance(first_break_condition, dict):
        scenario_key = _normalize_scenario_key(
            first_break_condition.get("scenario_label")
        ) or _normalize_scenario_key(first_break_condition.get("scenario_id"))
    flex_normalized = _normalize_percentish_value(flex_before_break_pct)
    if scenario_key == "base":
        return "High", "Base case breaks first."
    if flex_normalized is not None:
        if flex_normalized < 2.0:
            return "High", "<2% flex before break."
        if flex_normalized <= 5.0:
            return "Medium", "2-5% flex before break."
        return "Low", ">5% flex before break."
    if scenario_key == "conservative":
        return "Medium", "First break appears in conservative stress."
    if scenario_key == "ugly":
        return "Low", "First break appears only in ugly stress."
    return None, None


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


def _payload_system_names(payload):
    scope_items = payload.get("scope_items")
    assert isinstance(scope_items, list)
    assert scope_items
    assert any(isinstance(item.get("systems"), list) and item.get("systems") for item in scope_items)

    return [
        str(system.get("name", "")).lower()
        for trade in scope_items
        for system in (trade.get("systems") or [])
        if isinstance(system, dict)
    ]


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


def test_industrial_dscr_visibility_policy_is_type_aware():
    allowed_statuses = {"GO", "Needs Work", "NO-GO", "PENDING"}
    financing_disclosure = "Not modeled: financing assumptions missing"
    observed_numeric_with_disclosure = False
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.INDUSTRIAL,
            subtype=subtype,
            square_footage=120_000,
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
            project_id=f"industrial-dscr-visible-{subtype}",
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


def test_industrial_subtypes_define_deterministic_dealshield_profile_ids():
    for subtype, expected_profile_id in INDUSTRIAL_PROFILE_IDS.items():
        config = get_building_config(BuildingType.INDUSTRIAL, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected_profile_id


def test_industrial_manufacturing_uses_structural_scope_items_profile():
    config = get_building_config(BuildingType.INDUSTRIAL, "manufacturing")
    assert config is not None
    assert config.scope_items_profile == "industrial_manufacturing_structural_v1"


def test_industrial_distribution_center_and_flex_space_use_scope_items_profiles():
    for subtype, expected_profile_id in INDUSTRIAL_SCOPE_PROFILE_IDS.items():
        config = get_building_config(BuildingType.INDUSTRIAL, subtype)
        assert config is not None
        assert config.scope_items_profile == expected_profile_id


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


def test_industrial_distribution_center_and_flex_scope_profiles_are_subtype_authored():
    warehouse_keys = _profile_item_keys("industrial_warehouse_structural_v1")
    distribution_center_keys = _profile_item_keys("industrial_distribution_center_structural_v1")
    flex_space_keys = _profile_item_keys("industrial_flex_space_structural_v1")

    assert distribution_center_keys != warehouse_keys
    assert flex_space_keys != warehouse_keys

    assert {
        "cross_dock_aprons_and_truck_courts",
        "material_handling_motor_control_centers",
        "sortation_conveyor_power_distribution",
        "dock_door_air_curtains_and_heaters",
    }.issubset(distribution_center_keys)
    assert {
        "dock_pits_loading_aprons",
        "warehouse_floor_sealers",
    }.isdisjoint(distribution_center_keys)

    assert {
        "office_partitions_and_gypsum_assemblies",
        "storefront_glazing_and_entry_systems",
        "office_showroom_vav_and_split_systems",
        "mixed_use_hvac_controls_and_zoning",
    }.issubset(flex_space_keys)
    assert {
        "tilt_wall_shell",
        "warehouse_floor_sealers",
    }.isdisjoint(flex_space_keys)


def test_industrial_scope_profiles_preserve_shared_rendering_shape():
    expected_trade_keys = {"structural", "mechanical", "electrical", "plumbing", "finishes"}
    scope_profile_ids = {
        get_building_config(BuildingType.INDUSTRIAL, subtype).scope_items_profile
        for subtype in INDUSTRIAL_PROFILE_IDS.keys()
    }

    for profile_id in scope_profile_ids:
        profile = industrial_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        trade_keys = {
            trade_profile.get("trade_key")
            for trade_profile in trade_profiles
            if isinstance(trade_profile, dict)
        }
        assert trade_keys == expected_trade_keys

        for trade_profile in trade_profiles:
            items = trade_profile.get("items")
            assert isinstance(items, list) and len(items) >= 2
            share_total = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert abs(share_total - 1.0) <= 1e-9


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
        decision_columns = profile.get("decision_table_columns")
        assert isinstance(decision_columns, list) and decision_columns
        dscr_columns = [
            column
            for column in decision_columns
            if isinstance(column, dict) and column.get("id") == "dscr"
        ]
        assert len(dscr_columns) == 1
        assert dscr_columns[0].get("label") == "Debt Lens: DSCR"

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


def test_industrial_content_question_bank_includes_ic_reality_checks():
    for profile_id in INDUSTRIAL_PROFILE_IDS.values():
        content_profile = get_dealshield_content_profile(profile_id)
        question_bank = content_profile.get("question_bank")
        assert isinstance(question_bank, list) and question_bank
        questions = [
            question
            for entry in question_bank
            if isinstance(entry, dict)
            for question in (entry.get("questions") or [])
            if isinstance(question, str)
        ]
        normalized_questions = " ".join(question.lower() for question in questions)
        assert "term" in normalized_questions
        assert "credit" in normalized_questions
        assert "cap" in normalized_questions


def test_industrial_di_policy_labels_are_subtype_specific():
    observed_labels = []
    for subtype, profile_id in INDUSTRIAL_PROFILE_IDS.items():
        policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy_cfg.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert label == INDUSTRIAL_PRIMARY_CONTROL_LABELS[subtype]
        assert isinstance(label, str)
        if subtype == "warehouse":
            assert not label.lower().startswith("ic-first ")
        else:
            assert label.lower().startswith("ic-first ")
        observed_labels.append(label.lower())

    assert len(observed_labels) == len(set(observed_labels))


def test_industrial_warehouse_content_uses_warehouse_native_copy():
    content_profile = get_dealshield_content_profile(INDUSTRIAL_PROFILE_IDS["warehouse"])

    fastest_change = content_profile.get("fastest_change")
    assert isinstance(fastest_change, dict)
    drivers = fastest_change.get("drivers")
    assert isinstance(drivers, list) and len(drivers) >= 3
    assert [driver.get("label") for driver in drivers[:3]] == [
        "Confirm sitework/civil allowances + utility routing",
        "Validate rent/SF and absorption (broker comps + active tenants)",
        "Confirm dock count/clear height as it affects rent",
    ]

    most_likely_wrong = content_profile.get("most_likely_wrong")
    assert isinstance(most_likely_wrong, list) and most_likely_wrong
    assert any(
        entry.get("text")
        == "Lease-up is modeled smoothly; real absorption is lumpy (LOIs, TI decisions, broker cycles)."
        for entry in most_likely_wrong
        if isinstance(entry, dict)
    )


def test_industrial_cold_storage_content_uses_cold_storage_native_fastest_change_copy():
    content_profile = get_dealshield_content_profile(INDUSTRIAL_PROFILE_IDS["cold_storage"])

    fastest_change = content_profile.get("fastest_change")
    assert isinstance(fastest_change, dict)
    drivers = fastest_change.get("drivers")
    assert isinstance(drivers, list) and len(drivers) >= 3
    assert [driver.get("label") for driver in drivers[:3]] == [
        "Confirm refrigeration package scope + inclusions (vendor vs GC carry)",
        "Confirm utility commitment + backup power assumptions",
        "Validate ramp-to-stabilization assumptions (commissioning curve)",
    ]


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


def test_industrial_distribution_center_and_flex_space_emit_subtype_specific_scope_items():
    distribution_payload = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="distribution_center",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    distribution_names = _payload_system_names(distribution_payload)
    assert any("cross-dock aprons" in name for name in distribution_names)
    assert any("sortation conveyor power" in name for name in distribution_names)
    assert any("material-handling motor control centers" in name for name in distribution_names)
    assert {
        "cross_dock_aprons_and_truck_courts",
        "sortation_conveyor_power_distribution",
        "material_handling_motor_control_centers",
    }.issubset(_profile_item_keys("industrial_distribution_center_structural_v1"))

    flex_payload = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="flex_space",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    flex_names = _payload_system_names(flex_payload)
    assert any("office and showroom partitions" in name for name in flex_names)
    assert any("storefront glazing" in name for name in flex_names)
    assert any("office/showroom vav and split-system conditioning" in name for name in flex_names)
    assert {
        "office_partitions_and_gypsum_assemblies",
        "storefront_glazing_and_entry_systems",
        "office_showroom_vav_and_split_systems",
    }.issubset(_profile_item_keys("industrial_flex_space_structural_v1"))


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
        assert "first_break_condition_holds" in view_model
        assert "flex_before_break_pct" in view_model
        assert "break_risk_level" in view_model
        assert "break_risk_reason" in view_model
        assert "break_risk" in view_model
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
        expected_policy = INDUSTRIAL_POLICY_EXPECTATIONS[subtype]

        assert policy_cfg["primary_control_variable"]["tile_id"] == expected_policy["tile_id"]
        collapse_cfg = policy_cfg["collapse_trigger"]
        assert collapse_cfg.get("metric") == expected_policy["collapse_metric"]
        assert collapse_cfg.get("operator") == expected_policy["collapse_operator"]
        assert collapse_cfg.get("threshold") == expected_policy["collapse_threshold"]

        flex_calibration = policy_cfg["flex_calibration"]
        assert isinstance(flex_calibration, dict)
        assert isinstance(flex_calibration.get("tight_max_pct"), (int, float))
        assert isinstance(flex_calibration.get("moderate_max_pct"), (int, float))
        assert isinstance(flex_calibration.get("fallback_pct"), (int, float))
        assert float(flex_calibration["tight_max_pct"]) <= float(flex_calibration["moderate_max_pct"])

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy_cfg["primary_control_variable"]["tile_id"]

        first_break_block = di_provenance.get("first_break_condition")
        assert isinstance(first_break_block, dict)
        if first_break_block.get("status") == "available":
            if first_break_block.get("source") == "decision_insurance_policy.collapse_trigger":
                expected_operator = collapse_cfg.get("operator") if isinstance(collapse_cfg.get("operator"), str) and collapse_cfg.get("operator").strip() else "<="
                first_break = view_model.get("first_break_condition")
                assert isinstance(first_break, dict)
                assert first_break.get("break_metric") == collapse_cfg.get("metric")
                assert first_break.get("operator") == expected_operator
                assert first_break.get("threshold") == collapse_cfg.get("threshold")
                assert first_break_block.get("policy_metric") == collapse_cfg.get("metric")
                assert first_break_block.get("policy_threshold") == collapse_cfg.get("threshold")
                assert first_break_block.get("policy_operator") == expected_operator
        else:
            assert first_break_block.get("reason") != "no_modeled_break_condition"

        flex_block = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_block, dict)
        assert flex_block.get("status") == "available"
        assert flex_block.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert view_model.get("flex_before_break_band") in {"tight", "moderate", "comfortable"}
        assert flex_block.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_block.get("band")

        first_break_holds_block = di_provenance.get("first_break_condition_holds")
        assert isinstance(first_break_holds_block, dict)
        if isinstance(view_model.get("first_break_condition"), dict):
            assert first_break_holds_block.get("source") == "decision_insurance.first_break_condition"
        else:
            assert first_break_holds_block.get("status") == "unavailable"
            assert first_break_holds_block.get("reason") == "first_break_condition_unavailable"

        break_risk_block = di_provenance.get("break_risk")
        assert isinstance(break_risk_block, dict)
        assert break_risk_block.get("source") == "decision_insurance.break_risk"
        if view_model.get("break_risk") is not None:
            assert break_risk_block.get("level") == view_model.get("break_risk_level")
            assert break_risk_block.get("reason") == view_model.get("break_risk_reason")

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
            "first_break_condition_holds",
            "flex_before_break_pct",
            "break_risk",
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
        first_break_holds = view_model.get("first_break_condition_holds")
        if first_break is not None:
            assert isinstance(first_break, dict)
            assert isinstance(first_break.get("observed_value"), (int, float))
            if first_break.get("break_metric") == "value_gap_pct":
                assert isinstance(first_break.get("observed_value_pct"), (int, float))
            first_break_operator = first_break.get("operator")
            first_break_observed = float(first_break["observed_value"])
            first_break_threshold = float(first_break.get("threshold", 0.0))
            if first_break_operator == "<=":
                assert first_break_observed <= first_break_threshold
                assert first_break_holds is True
            elif first_break_operator == "<":
                assert first_break_observed < first_break_threshold
                assert first_break_holds is True
            elif first_break_operator == ">=":
                assert first_break_observed >= first_break_threshold
                assert first_break_holds is True
            elif first_break_operator == ">":
                assert first_break_observed > first_break_threshold
                assert first_break_holds is True
        else:
            assert first_break_holds is None

        flex_before_break = view_model.get("flex_before_break_pct")
        if flex_before_break is not None:
            assert isinstance(flex_before_break, (int, float))
            assert flex_before_break >= 0

        expected_break_risk_level, expected_break_risk_reason = _classify_break_risk(
            first_break_condition=first_break,
            flex_before_break_pct=flex_before_break,
        )
        assert view_model.get("break_risk_level") == expected_break_risk_level
        assert view_model.get("break_risk_reason") == expected_break_risk_reason
        if expected_break_risk_level is None:
            assert view_model.get("break_risk") is None
        else:
            assert view_model.get("break_risk") == {
                "level": expected_break_risk_level,
                "reason": expected_break_risk_reason,
            }

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
