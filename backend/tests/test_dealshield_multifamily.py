from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.dealshield_content import multifamily as multifamily_content_profiles
from app.v2.config.type_profiles.decision_insurance_policy import DECISION_INSURANCE_POLICY_BY_PROFILE_ID
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import multifamily as multifamily_tile_profiles
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


MULTIFAMILY_PROFILE_IDS = {
    "market_rate_apartments": "multifamily_market_rate_apartments_v1",
    "luxury_apartments": "multifamily_luxury_apartments_v1",
    "affordable_housing": "multifamily_affordable_housing_v1",
}

MULTIFAMILY_POLICY_EXPECTATIONS = {
    "multifamily_market_rate_apartments_v1": {
        "primary_tile_id": "structural_carry_proxy_plus_5",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": 6.0,
        "scenario_priority": ["base", "conservative", "structural_carry_proxy_stress", "ugly"],
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 5.0, "fallback_pct": 3.5},
    },
    "multifamily_luxury_apartments_v1": {
        "primary_tile_id": "amenity_finish_plus_15",
        "collapse_metric": "value_gap",
        "collapse_operator": "<=",
        "collapse_threshold": 250000.0,
        "scenario_priority": ["base", "conservative", "amenity_overrun", "amenity_system_stress"],
        "flex_calibration": {"tight_max_pct": 1.5, "moderate_max_pct": 4.5, "fallback_pct": 2.0},
    },
    "multifamily_affordable_housing_v1": {
        "primary_tile_id": "compliance_electrical_plus_8",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": 8.0,
        "scenario_priority": ["base", "conservative", "compliance_delay", "funding_gap"],
        "flex_calibration": {"tight_max_pct": 2.0, "moderate_max_pct": 4.5, "fallback_pct": 3.0},
    },
}


def test_multifamily_policy_entries_are_explicit_and_subtype_specific():
    assert set(MULTIFAMILY_POLICY_EXPECTATIONS.keys()) == set(MULTIFAMILY_PROFILE_IDS.values())
    for profile_id, expected in MULTIFAMILY_POLICY_EXPECTATIONS.items():
        assert profile_id in DECISION_INSURANCE_POLICY_BY_PROFILE_ID
        policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]

        primary_control = policy_cfg.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == expected["primary_tile_id"]
        assert isinstance(primary_control.get("metric_ref"), str) and primary_control.get("metric_ref").strip()
        assert isinstance(primary_control.get("label"), str) and primary_control.get("label").strip()

        collapse_trigger = policy_cfg.get("collapse_trigger")
        assert isinstance(collapse_trigger, dict)
        assert collapse_trigger.get("metric") == expected["collapse_metric"]
        assert collapse_trigger.get("operator") == expected["collapse_operator"]
        assert collapse_trigger.get("threshold") == expected["collapse_threshold"]
        assert collapse_trigger.get("scenario_priority") == expected["scenario_priority"]

        flex_calibration = policy_cfg.get("flex_calibration")
        assert flex_calibration == expected["flex_calibration"]
        assert set(flex_calibration.keys()) == {"tight_max_pct", "moderate_max_pct", "fallback_pct"}


def _tile_map(profile_id: str):
    profile = get_dealshield_profile(profile_id)
    return {tile["tile_id"]: tile for tile in profile.get("tiles", []) if isinstance(tile, dict)}


def _is_revenue_like_metric(metric_ref: str) -> bool:
    metric = (metric_ref or "").strip().lower()
    return metric.startswith("revenue_analysis.") or any(
        keyword in metric for keyword in ("revenue", "rent", "occupancy", "absorption")
    )


def _row_implies_revenue(row_id: str, row_label: str) -> bool:
    text = f"{row_id} {row_label}".lower()
    return any(keyword in text for keyword in ("lease", "rent", "revenue", "absorption", "occupancy", "demand"))


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


def test_multifamily_tile_profiles_are_subtype_authored_not_clones():
    market_profile = get_dealshield_profile("multifamily_market_rate_apartments_v1")
    luxury_profile = get_dealshield_profile("multifamily_luxury_apartments_v1")
    affordable_profile = get_dealshield_profile("multifamily_affordable_housing_v1")

    assert market_profile != luxury_profile
    assert market_profile != affordable_profile
    assert luxury_profile != affordable_profile

    market_tile_ids = {tile["tile_id"] for tile in market_profile["tiles"]}
    luxury_tile_ids = {tile["tile_id"] for tile in luxury_profile["tiles"]}
    affordable_tile_ids = {tile["tile_id"] for tile in affordable_profile["tiles"]}

    assert "structural_carry_proxy_plus_5" in market_tile_ids
    assert "amenity_finish_plus_15" in luxury_tile_ids
    assert "compliance_electrical_plus_8" in affordable_tile_ids

    assert "amenity_finish_plus_15" not in market_tile_ids
    assert "compliance_electrical_plus_8" not in market_tile_ids
    assert "structural_carry_proxy_plus_5" not in luxury_tile_ids
    assert "compliance_electrical_plus_8" not in luxury_tile_ids
    assert "structural_carry_proxy_plus_5" not in affordable_tile_ids
    assert "amenity_finish_plus_15" not in affordable_tile_ids

    market_rows = {row["row_id"] for row in market_profile["derived_rows"]}
    luxury_rows = {row["row_id"] for row in luxury_profile["derived_rows"]}
    affordable_rows = {row["row_id"] for row in affordable_profile["derived_rows"]}

    assert "structural_carry_proxy_stress" in market_rows
    assert "amenity_overrun" in luxury_rows
    assert "compliance_delay" in affordable_rows
    assert "amenity_system_stress" in luxury_rows


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


def test_multifamily_content_profiles_are_subtype_authored_not_clones():
    market_content = get_dealshield_content_profile("multifamily_market_rate_apartments_v1")
    luxury_content = get_dealshield_content_profile("multifamily_luxury_apartments_v1")
    affordable_content = get_dealshield_content_profile("multifamily_affordable_housing_v1")

    assert market_content != luxury_content
    assert market_content != affordable_content
    assert luxury_content != affordable_content

    market_driver_tile_ids = {
        driver["tile_id"]
        for driver in market_content.get("fastest_change", {}).get("drivers", [])
    }
    luxury_driver_tile_ids = {
        driver["tile_id"]
        for driver in luxury_content.get("fastest_change", {}).get("drivers", [])
    }
    affordable_driver_tile_ids = {
        driver["tile_id"]
        for driver in affordable_content.get("fastest_change", {}).get("drivers", [])
    }

    assert "structural_carry_proxy_plus_5" in market_driver_tile_ids
    assert "amenity_finish_plus_15" in luxury_driver_tile_ids
    assert "compliance_electrical_plus_8" in affordable_driver_tile_ids

    market_question_ids = {q["id"] for q in market_content.get("question_bank", [])}
    luxury_question_ids = {q["id"] for q in luxury_content.get("question_bank", [])}
    affordable_question_ids = {q["id"] for q in affordable_content.get("question_bank", [])}
    assert market_question_ids != luxury_question_ids
    assert market_question_ids != affordable_question_ids
    assert luxury_question_ids != affordable_question_ids

    assert (
        multifamily_content_profiles.DEALSHIELD_CONTENT_PROFILES[
            "multifamily_market_rate_apartments_v1"
        ]["profile_id"]
        == "multifamily_market_rate_apartments_v1"
    )
    assert (
        multifamily_content_profiles.DEALSHIELD_CONTENT_PROFILES[
            "multifamily_luxury_apartments_v1"
        ]["profile_id"]
        == "multifamily_luxury_apartments_v1"
    )
    assert (
        multifamily_content_profiles.DEALSHIELD_CONTENT_PROFILES[
            "multifamily_affordable_housing_v1"
        ]["profile_id"]
        == "multifamily_affordable_housing_v1"
    )


def test_multifamily_content_driver_tile_ids_exist_in_tile_profiles():
    for profile_id in MULTIFAMILY_PROFILE_IDS.values():
        tile_ids = set(_tile_map(profile_id).keys())
        content_profile = get_dealshield_content_profile(profile_id)

        referenced_tile_ids = set()
        referenced_tile_ids.update(
            driver.get("tile_id")
            for driver in content_profile.get("fastest_change", {}).get("drivers", [])
            if isinstance(driver, dict)
        )
        referenced_tile_ids.update(
            entry.get("driver_tile_id")
            for entry in content_profile.get("most_likely_wrong", [])
            if isinstance(entry, dict)
        )
        referenced_tile_ids.update(
            entry.get("driver_tile_id")
            for entry in content_profile.get("question_bank", [])
            if isinstance(entry, dict)
        )
        referenced_tile_ids.discard(None)
        assert referenced_tile_ids.issubset(tile_ids)


def test_multifamily_tile_labels_align_with_metric_ref_class():
    trade_keyword_map = {
        "structural": {"structural", "shell", "frame", "site", "carry"},
        "mechanical": {"mechanical", "mep", "system"},
        "electrical": {"electrical", "power", "life-safety", "compliance"},
        "plumbing": {"plumbing", "water", "utility", "compliance"},
        "finishes": {"finish", "interior", "amenity", "fit-out"},
    }

    for profile_id in MULTIFAMILY_PROFILE_IDS.values():
        for tile in _tile_map(profile_id).values():
            label = str(tile.get("label", "")).lower()
            metric_ref = str(tile.get("metric_ref", "")).lower()
            assert label
            assert metric_ref

            if metric_ref.startswith("totals.") or metric_ref.startswith("construction_costs."):
                assert any(token in label for token in ("cost", "sf", "project", "total"))
            elif metric_ref.startswith("trade_breakdown."):
                trade_key = metric_ref.split(".", 1)[1]
                expected_tokens = trade_keyword_map.get(trade_key, {trade_key})
                assert any(token in label for token in expected_tokens)
            elif _is_revenue_like_metric(metric_ref):
                assert any(token in label for token in ("revenue", "rent", "occupancy", "lease"))
            else:
                raise AssertionError(f"Unexpected metric_ref class for tile: {metric_ref}")


def test_multifamily_row_labels_do_not_imply_revenue_without_revenue_metric():
    for profile_id in MULTIFAMILY_PROFILE_IDS.values():
        profile = get_dealshield_profile(profile_id)
        tile_by_id = _tile_map(profile_id)

        for row in profile.get("derived_rows", []):
            assert isinstance(row, dict)
            row_id = str(row.get("row_id", ""))
            row_label = str(row.get("label", ""))
            tile_ids = list(row.get("apply_tiles", [])) + list(row.get("plus_tiles", []))
            row_has_revenue_metric = any(
                _is_revenue_like_metric(str(tile_by_id[tile_id].get("metric_ref", "")))
                for tile_id in tile_ids
                if tile_id in tile_by_id
            )

            if _row_implies_revenue(row_id, row_label):
                assert row_has_revenue_metric


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
        assert expected_profile_id in DECISION_INSURANCE_POLICY_BY_PROFILE_ID
        policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[expected_profile_id]
        expected_policy = MULTIFAMILY_POLICY_EXPECTATIONS[expected_profile_id]
        collapse_cfg = policy_cfg["collapse_trigger"]

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy_cfg["primary_control_variable"]["tile_id"]
        assert primary_control.get("tile_id") == expected_policy["primary_tile_id"]

        first_break_block = di_provenance.get("first_break_condition")
        assert isinstance(first_break_block, dict)
        if first_break_block.get("status") == "available":
            if first_break_block.get("source") == "decision_insurance_policy.collapse_trigger":
                configured_operator = collapse_cfg.get("operator")
                expected_operator = (
                    configured_operator.strip()
                    if isinstance(configured_operator, str) and configured_operator.strip()
                    else "<="
                )
                first_break = view_model.get("first_break_condition")
                assert isinstance(first_break, dict)
                assert first_break.get("break_metric") == collapse_cfg.get("metric")
                assert first_break.get("operator") == expected_operator
                assert first_break.get("threshold") == collapse_cfg.get("threshold")
                assert isinstance(first_break.get("observed_value"), (int, float))
        else:
            assert first_break_block.get("reason") != "no_modeled_break_condition"

        flex_block = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_block, dict)
        assert flex_block.get("status") == "available"
        assert view_model.get("flex_before_break_band") in {"tight", "moderate", "comfortable"}
        assert flex_block.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_block.get("band")

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
            if first_break_block.get("source") == "decision_insurance_policy.collapse_trigger":
                expected_operator = collapse_cfg.get("operator")
                expected_operator = (
                    expected_operator.strip()
                    if isinstance(expected_operator, str) and expected_operator.strip()
                    else "<="
                )
                assert first_break.get("break_metric") == expected_policy["collapse_metric"]
                assert first_break.get("operator") == expected_operator
                assert first_break.get("threshold") == expected_policy["collapse_threshold"]
            assert isinstance(first_break.get("observed_value"), (int, float))

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
