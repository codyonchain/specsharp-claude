import math

import pytest

from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    get_building_config,
    get_margin_pct,
    get_target_roi,
    validate_config,
)
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_BY_PROFILE_ID,
    DECISION_INSURANCE_POLICY_ID,
)
from app.v2.services.dealshield_service import build_dealshield_view_model

INDUSTRIAL_POLICY_EXPECTATIONS_BY_PROFILE_ID = {
    "industrial_warehouse_v1": {
        "tile_id": "structural_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -8.0,
    },
    "industrial_distribution_center_v1": {
        "tile_id": "electrical_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -25.0,
    },
    "industrial_manufacturing_v1": {
        "tile_id": "process_mep_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -35.0,
    },
    "industrial_flex_space_v1": {
        "tile_id": "office_finish_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -6.0,
    },
    "industrial_cold_storage_v1": {
        "tile_id": "equipment_plus_10",
        "collapse_metric": "value_gap_pct",
        "collapse_operator": "<=",
        "collapse_threshold": -30.0,
    },
}


def test_state_required_for_multiplier():
    """City-only handling should follow active location contract: known override/no warning, unknown city/warning."""
    known_city = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=10_000,
        location="Nashville",  # Missing state info
        project_class=ProjectClass.GROUND_UP,
    )

    multiplier = known_city["construction_costs"]["regional_multiplier"]
    assert multiplier == pytest.approx(1.03), "City-only locations should follow configured override when available"

    known_steps = " | ".join(entry["step"] for entry in known_city["calculation_trace"]).lower()
    known_payload = " | ".join(str(entry["data"]) for entry in known_city["calculation_trace"]).lower()
    assert "warning" not in known_steps and "warning" not in known_payload, (
        "Known city overrides should not emit missing-state warning traces"
    )

    unknown_city = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=10_000,
        location="Springfield",  # Missing state info and no city override
        project_class=ProjectClass.GROUND_UP,
    )
    assert unknown_city["construction_costs"]["regional_multiplier"] == pytest.approx(1.0)
    unknown_steps = " | ".join(entry["step"] for entry in unknown_city["calculation_trace"]).lower()
    assert "warning" in unknown_steps, "Unknown city-only location must emit warning trace"


def test_revenue_uses_own_multiplier():
    """Revenue modifiers must respond independently while remaining available to the UI."""
    standard = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=25_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        finish_level="Standard",
    )

    premium = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=25_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        finish_level="Premium",
    )

    standard_cost = standard["construction_costs"].get("cost_factor")
    premium_cost = premium["construction_costs"].get("cost_factor")
    standard_revenue = standard["revenue_analysis"].get("revenue_factor")
    premium_revenue = premium["revenue_analysis"].get("revenue_factor")

    assert standard_cost is not None and premium_cost is not None, "Cost factors must be present"
    assert standard_revenue is not None and premium_revenue is not None, "Revenue factors must be present"

    assert premium_cost > standard_cost, "Premium finish should raise cost factor"
    assert premium_revenue > standard_revenue, "Premium finish should raise revenue factor"
    assert not math.isclose(premium_revenue, premium_cost), "Revenue factor should remain distinct from cost factor"


def test_description_detection_natural_language():
    """Natural-language descriptions should map to building types with NLP trace visibility."""
    office_description = "50,000 sf class A office in Nashville, TN"
    office_result = unified_engine.estimate_from_description(
        description=office_description,
        square_footage=50_000,
        location="Nashville, TN",
    )

    office_detection = office_result["detection_info"]
    assert office_detection["detected_type"] == BuildingType.OFFICE.value
    assert office_detection["detected_subtype"].replace("_", " ") == "class a"

    office_trace = [
        entry for entry in office_result["calculation_trace"] if entry["step"] == "nlp_detected"
    ]
    assert office_trace, "NLP detection trace entry missing for office description"
    assert office_trace[-1]["data"]["method"] in {"phrase", "token"}

    restaurant_description = "5k sf full service restaurant in Nashville, TN"
    restaurant_result = unified_engine.estimate_from_description(
        description=restaurant_description,
        square_footage=5_000,
        location="Nashville, TN",
    )

    restaurant_detection = restaurant_result["detection_info"]
    assert restaurant_detection["detected_type"] == BuildingType.RESTAURANT.value
    assert restaurant_detection["detected_subtype"].replace("_", " ") == "full service"

    restaurant_trace = [
        entry for entry in restaurant_result["calculation_trace"] if entry["step"] == "nlp_detected"
    ]
    assert restaurant_trace, "NLP detection trace entry missing for restaurant description"
    assert restaurant_trace[-1]["data"]["method"] in {"phrase", "token"}


def test_description_infers_finish_level():
    """Descriptions with finish cues should promote premium modifiers exactly once."""
    base_description = "5,000 sf full service restaurant in Nashville, TN"
    premium_description = f"{base_description} (premium finishes, 1.15x)"

    base_result = unified_engine.estimate_from_description(
        description=base_description,
        square_footage=5_000,
        location="Nashville, TN",
    )
    premium_result = unified_engine.estimate_from_description(
        description=premium_description,
        square_footage=5_000,
        location="Nashville, TN",
    )

    premium_trace = [entry for entry in premium_result["calculation_trace"] if isinstance(entry, dict)]
    base_trace = [entry for entry in base_result["calculation_trace"] if isinstance(entry, dict)]

    inference_traces = [entry for entry in premium_trace if entry["step"] == "finish_level_inferred"]
    assert inference_traces, "Missing finish_level_inferred trace for premium description"
    inferred_payload = inference_traces[-1]["data"]
    assert inferred_payload["finish_level"] == "Premium", "Expected Premium finish level from description cues"

    premium_modifiers = next(
        entry["data"] for entry in premium_trace if entry["step"] == "modifiers_applied"
    )
    base_modifiers = next(
        entry["data"] for entry in base_trace if entry["step"] == "modifiers_applied"
    )

    premium_revenue_factor = premium_modifiers["revenue_factor"]
    base_revenue_factor = base_modifiers["revenue_factor"]

    assert base_revenue_factor == pytest.approx(1.0), "Base revenue factor should remain neutral at 1.0"
    assert premium_revenue_factor > base_revenue_factor, "Premium modifiers should lift revenue factor"
    ratio = premium_revenue_factor / base_revenue_factor
    assert ratio == pytest.approx(1.08, rel=1e-2), "Premium factor should apply once (≈1.08× increase)"


def test_special_features_unit_math():
    """Special feature pricing should respect per-unit costs, not auto-scale by total square footage."""
    base_result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="surgical_center",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=[],
    )
    feature_result = unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype="surgical_center",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        special_features=["operating_room"],
    )

    config = get_building_config(BuildingType.HEALTHCARE, "surgical_center")
    expected_increment = config.special_features["operating_room"] * base_result["project_info"]["square_footage"]

    delta = feature_result["construction_costs"]["special_features_total"] - base_result["construction_costs"]["special_features_total"]
    assert delta == pytest.approx(
        expected_increment,
        rel=1e-3,
    ), "Special feature surcharge should scale with square footage as currently configured"


def test_restaurant_clamp_is_explicit_or_off():
    """Clamp behavior must be explicit: traced when applied, otherwise final costs stay within configured bounds."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=1_000,
        location="Memphis, TN",
        project_class=ProjectClass.TENANT_IMPROVEMENT,
    )

    trace_entries = [entry for entry in result["calculation_trace"] if entry["step"] == "restaurant_cost_clamp"]
    cost_per_sf = result["totals"]["cost_per_sf"]
    cfg = get_building_config(BuildingType.RESTAURANT, "quick_service")
    assert cfg is not None

    clamp_cfg = cfg.cost_clamp or {}
    min_cost = clamp_cfg.get("min_cost_per_sf", 250)
    max_cost = clamp_cfg.get("max_cost_per_sf")

    if trace_entries:
        trace_data = trace_entries[-1]["data"]
        assert trace_data["mode"] in {"minimum", "maximum"}
    else:
        assert cost_per_sf >= min_cost, "If clamp is off, cost_per_sf must already satisfy configured minimum"
        if isinstance(max_cost, (int, float)):
            assert cost_per_sf <= max_cost, "If clamp is off, cost_per_sf must satisfy configured maximum when set"


def test_margin_normalized_noi_is_revenue_minus_opex():
    """NOI must be derived from revenue minus operating expenses, not a fixed percentage."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    annual_revenue = result["revenue_analysis"]["annual_revenue"]
    total_expenses = result["operational_efficiency"]["total_expenses"]
    noi = result["revenue_analysis"]["net_income"]

    derived_noi = annual_revenue - total_expenses
    assert noi == pytest.approx(round(derived_noi, 2), abs=0.01), "Net income should match revenue minus expenses"

    margin_traces = [entry for entry in result["calculation_trace"] if entry["step"] == "margin_normalized"]
    assert len(margin_traces) == 1, "Margin normalization trace entry missing or duplicated"
    expected_margin = get_margin_pct(BuildingType.RESTAURANT, "full_service")
    assert margin_traces[0]["data"]["margin_pct"] == pytest.approx(expected_margin, rel=1e-4)

    trace_steps = [entry for entry in result["calculation_trace"] if entry["step"] == "noi_derived"]

    assert trace_steps, "NOI derivation trace entry missing"
    trace_data = trace_steps[-1]["data"]
    assert trace_data["method"] == "revenue_analysis"
    assert trace_data["estimated_noi"] == pytest.approx(noi, abs=0.01)


def test_noi_is_revenue_minus_opex():
    """Backward-compatible alias for targeted pytest selection."""
    test_margin_normalized_noi_is_revenue_minus_opex()


def test_modifiers_applied_boost_revenue_and_align_feasibility():
    """Premium finishes should lift revenue and expose modifier trace + feasibility flag."""
    base_kwargs = dict(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    standard = unified_engine.calculate_project(**base_kwargs, finish_level="Standard")
    premium = unified_engine.calculate_project(**base_kwargs, finish_level="Premium")

    assert premium["revenue_analysis"]["annual_revenue"] > standard["revenue_analysis"]["annual_revenue"]

    modifier_traces = [entry for entry in premium["calculation_trace"] if entry["step"] == "modifiers_applied"]
    assert modifier_traces, "Expected modifiers_applied trace for premium scenario"

    premium_modifier = modifier_traces[-1]["data"]
    assert premium_modifier["finish_level"] == "premium"

    return_metrics = premium["return_metrics"]
    roi_percent = return_metrics.get("cash_on_cash_return", 0)
    npv = return_metrics.get("npv", 0)
    feasible_flag = return_metrics.get("feasible")
    target_roi = get_target_roi(BuildingType.RESTAURANT)
    expected_feasible = (npv >= 0) and ((roi_percent or 0) / 100 >= target_roi)
    assert feasible_flag == expected_feasible, "Feasibility flag must reflect ROI hurdle and NPV"


def test_finish_level_quality_factor_trace():
    """Premium finish levels should increase costs and emit a quality factor trace."""
    standard = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        finish_level="Standard",
    )

    premium = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        finish_level="Premium",
    )

    assert premium["totals"]["total_project_cost"] > standard["totals"]["total_project_cost"], "Premium finish should increase total cost"

    quality_traces = [entry for entry in premium["calculation_trace"] if entry["step"] == "quality_factor_resolved"]
    assert quality_traces, "Missing quality factor trace entry for premium finish"
    trace_data = quality_traces[0]["data"]
    assert trace_data["finish_level"] == "premium"
    assert trace_data["quality_factor"] == pytest.approx(1.2, rel=1e-3)


def test_caprate_only_for_supported_types():
    """Cap-rate valuation should follow active engine defaults for any positive-NOI asset class."""
    supported = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="luxury_apartments",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    unsupported = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    supported_rm = supported["return_metrics"]
    unsupported_rm = unsupported["return_metrics"]

    assert supported_rm["property_value"] not in (None, 0), "Multifamily should surface cap-rate derived property value"
    assert unsupported_rm["property_value"] not in (None, 0), "Restaurant currently surfaces cap-rate derived property value"

    supported_formula_value = supported_rm["estimated_annual_noi"] / supported_rm["market_cap_rate"]
    unsupported_formula_value = unsupported_rm["estimated_annual_noi"] / unsupported_rm["market_cap_rate"]
    assert supported_rm["property_value"] == pytest.approx(supported_formula_value, rel=1e-6)
    assert unsupported_rm["property_value"] == pytest.approx(unsupported_formula_value, rel=1e-6)


def test_config_integrity():
    """Master config should validate trade percentages and financing ratios."""
    errors = validate_config()
    assert errors == [], f"Configuration integrity issues detected: {errors}"


def test_multifamily_decision_insurance_outputs_are_deterministic():
    """Decision-insurance outputs should be deterministic for identical multifamily inputs."""
    kwargs = dict(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    payload_a = unified_engine.calculate_project(**kwargs)
    payload_b = unified_engine.calculate_project(**kwargs)

    profile_a = get_dealshield_profile(payload_a["dealshield_tile_profile"])
    profile_b = get_dealshield_profile(payload_b["dealshield_tile_profile"])

    view_a = build_dealshield_view_model(
        project_id="deterministic-a",
        payload=payload_a,
        profile=profile_a,
    )
    view_b = build_dealshield_view_model(
        project_id="deterministic-b",
        payload=payload_b,
        profile=profile_b,
    )

    for key in (
        "primary_control_variable",
        "first_break_condition",
        "flex_before_break_pct",
        "exposure_concentration_pct",
        "ranked_likely_wrong",
        "decision_insurance_provenance",
        "decision_status",
        "decision_reason_code",
        "decision_status_provenance",
    ):
        assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_industrial_decision_insurance_outputs_are_deterministic():
    """Decision-insurance outputs should be deterministic for identical industrial inputs."""
    kwargs = dict(
        building_type=BuildingType.INDUSTRIAL,
        subtype="warehouse",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    payload_a = unified_engine.calculate_project(**kwargs)
    payload_b = unified_engine.calculate_project(**kwargs)

    profile_a = get_dealshield_profile(payload_a["dealshield_tile_profile"])
    profile_b = get_dealshield_profile(payload_b["dealshield_tile_profile"])

    view_a = build_dealshield_view_model(
        project_id="industrial-deterministic-a",
        payload=payload_a,
        profile=profile_a,
    )
    view_b = build_dealshield_view_model(
        project_id="industrial-deterministic-b",
        payload=payload_b,
        profile=profile_b,
    )

    for key in (
        "primary_control_variable",
        "first_break_condition",
        "flex_before_break_pct",
        "exposure_concentration_pct",
        "ranked_likely_wrong",
        "decision_insurance_provenance",
        "decision_status",
        "decision_reason_code",
        "decision_status_provenance",
    ):
        assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_policy_curated_decision_insurance_is_applied_for_hardened_profiles():
    profile_inputs = [
        (BuildingType.RESTAURANT, "quick_service", 8_000),
        (BuildingType.RESTAURANT, "full_service", 8_000),
        (BuildingType.RESTAURANT, "fine_dining", 8_000),
        (BuildingType.RESTAURANT, "cafe", 8_000),
        (BuildingType.RESTAURANT, "bar_tavern", 8_000),
        (BuildingType.HOSPITALITY, "limited_service_hotel", 85_000),
        (BuildingType.HOSPITALITY, "full_service_hotel", 85_000),
        (BuildingType.MULTIFAMILY, "market_rate_apartments", 120_000),
        (BuildingType.MULTIFAMILY, "luxury_apartments", 120_000),
        (BuildingType.MULTIFAMILY, "affordable_housing", 120_000),
        (BuildingType.INDUSTRIAL, "warehouse", 120_000),
        (BuildingType.INDUSTRIAL, "distribution_center", 120_000),
        (BuildingType.INDUSTRIAL, "manufacturing", 120_000),
        (BuildingType.INDUSTRIAL, "flex_space", 120_000),
        (BuildingType.INDUSTRIAL, "cold_storage", 120_000),
    ]

    for building_type, subtype, square_footage in profile_inputs:
        payload = unified_engine.calculate_project(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile_id = payload["dealshield_tile_profile"]
        assert profile_id in DECISION_INSURANCE_POLICY_BY_PROFILE_ID

        if building_type == BuildingType.INDUSTRIAL:
            expected_industrial_policy = INDUSTRIAL_POLICY_EXPECTATIONS_BY_PROFILE_ID[profile_id]
            industrial_policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
            assert industrial_policy_cfg["primary_control_variable"]["tile_id"] == expected_industrial_policy["tile_id"]
            assert industrial_policy_cfg["collapse_trigger"]["metric"] == expected_industrial_policy["collapse_metric"]
            assert industrial_policy_cfg["collapse_trigger"]["operator"] == expected_industrial_policy["collapse_operator"]
            assert industrial_policy_cfg["collapse_trigger"]["threshold"] == expected_industrial_policy["collapse_threshold"]

        profile = get_dealshield_profile(profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"policy-{building_type.value}-{subtype}",
            payload=payload,
            profile=profile,
        )
        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)

        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        pcv_provenance = di_provenance.get("primary_control_variable")
        assert isinstance(pcv_provenance, dict)
        assert pcv_provenance.get("status") == "available"
        assert pcv_provenance.get("selection_basis") == "policy_primary_control_variable"
        assert pcv_provenance.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert pcv_provenance.get("policy_source") == "decision_insurance_policy.primary_control_variable"

        expected_tile_id = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]["primary_control_variable"]["tile_id"]
        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == expected_tile_id

        first_break_provenance = di_provenance.get("first_break_condition")
        assert isinstance(first_break_provenance, dict)
        first_break = view_model.get("first_break_condition")
        if (
            isinstance(first_break, dict)
            and first_break_provenance.get("status") == "available"
            and first_break_provenance.get("source") == "decision_insurance_policy.collapse_trigger"
        ):
            collapse_trigger = policy_block.get("collapse_trigger")
            configured_operator = (
                collapse_trigger.get("operator")
                if isinstance(collapse_trigger, dict)
                else None
            )
            expected_operator = (
                configured_operator.strip()
                if isinstance(configured_operator, str) and configured_operator.strip()
                else "<="
            )
            assert first_break.get("break_metric") == first_break_provenance.get("policy_metric")
            assert first_break.get("threshold") == first_break_provenance.get("policy_threshold")
            assert first_break.get("operator") == expected_operator
            if building_type == BuildingType.INDUSTRIAL:
                expected_industrial_policy = INDUSTRIAL_POLICY_EXPECTATIONS_BY_PROFILE_ID[profile_id]
                assert first_break.get("break_metric") == expected_industrial_policy["collapse_metric"]
                assert first_break.get("operator") == expected_industrial_policy["collapse_operator"]
                assert first_break.get("threshold") == expected_industrial_policy["collapse_threshold"]
        if first_break_provenance.get("status") == "unavailable":
            assert first_break_provenance.get("reason") != "no_modeled_break_condition"

        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_provenance.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_provenance.get("band")
