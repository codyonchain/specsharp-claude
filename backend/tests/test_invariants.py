import math

import pytest

from app.v2.engines.unified_engine import (
    HEALTHCARE_INPATIENT_SUBTYPES,
    HEALTHCARE_SPECIAL_FEATURE_ALIASES,
    unified_engine,
)
from app.v2.config.master_config import (
    BuildingType,
    OFFICE_UNDERWRITING_CONFIG,
    ProjectClass,
    OwnershipType,
    get_building_config,
    get_margin_pct,
    validate_config,
)
from app.v2.config.construction_schedule import build_construction_schedule
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_BY_PROFILE_ID,
    DECISION_INSURANCE_POLICY_ID,
)
from app.v2.config.type_profiles.dealshield_content import healthcare as healthcare_content
from app.v2.config.type_profiles.dealshield_content import office as office_content
from app.v2.config.type_profiles.dealshield_content import specialty as specialty_content
from app.v2.config.type_profiles.dealshield_content import civic as civic_content
from app.v2.config.type_profiles.dealshield_content import mixed_use as mixed_use_content
from app.v2.config.type_profiles.dealshield_content import parking as parking_content
from app.v2.config.type_profiles.dealshield_content import recreation as recreation_content
from app.v2.config.type_profiles.scope_items import healthcare as healthcare_scope_profiles
from app.v2.config.type_profiles.scope_items import office as office_scope_profiles
from app.v2.config.type_profiles.scope_items import specialty as specialty_scope_profiles
from app.v2.config.type_profiles.scope_items import civic as civic_scope_profiles
from app.v2.config.type_profiles.scope_items import mixed_use as mixed_use_scope_profiles
from app.v2.config.type_profiles.scope_items import parking as parking_scope_profiles
from app.v2.config.type_profiles.scope_items import recreation as recreation_scope_profiles
from app.v2.services.dealshield_service import build_dealshield_view_model


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


def _evaluate_threshold_condition(operator, observed_value, threshold_value):
    if not isinstance(operator, str) or not operator.strip():
        return None
    op = operator.strip()
    if op not in {"<=", "<", ">=", ">", "=", "=="}:
        return None
    if not _is_numeric(observed_value) or not _is_numeric(threshold_value):
        return None
    observed = float(observed_value)
    threshold = float(threshold_value)
    if op == "<=":
        return observed <= threshold
    if op == "<":
        return observed < threshold
    if op == ">=":
        return observed >= threshold
    if op == ">":
        return observed > threshold
    return abs(observed - threshold) <= 1e-9


def _classify_break_risk(first_break_condition, flex_before_break_pct):
    scenario_key = None
    if isinstance(first_break_condition, dict):
        scenario_key = _normalize_scenario_key(
            first_break_condition.get("scenario_label")
        ) or _normalize_scenario_key(first_break_condition.get("scenario_id"))
    flex_normalized = _normalize_percentish_value(flex_before_break_pct)
    context = {
        "scenario_key": scenario_key,
        "flex_before_break_pct_normalized": flex_normalized,
    }
    if scenario_key == "base":
        return "High", "Base case breaks first.", context
    if flex_normalized is not None:
        if flex_normalized < 2.0:
            return "High", "<2% flex before break.", context
        if flex_normalized <= 5.0:
            return "Medium", "2-5% flex before break.", context
        return "Low", ">5% flex before break.", context
    if scenario_key == "conservative":
        return "Medium", "First break appears in conservative stress.", context
    if scenario_key == "ugly":
        return "Low", "First break appears only in ugly stress.", context
    return None, None, context


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

HEALTHCARE_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

EDUCATIONAL_PROFILE_IDS = {
    "elementary_school": "educational_elementary_school_v1",
    "middle_school": "educational_middle_school_v1",
    "high_school": "educational_high_school_v1",
    "university": "educational_university_v1",
    "community_college": "educational_community_college_v1",
}

EDUCATIONAL_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

EDUCATIONAL_SCOPE_DEPTH_FLOOR = {
    "elementary_school": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "middle_school": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "high_school": {"structural": 4, "mechanical": 4, "electrical": 4, "plumbing": 4, "finishes": 4},
    "university": {"structural": 4, "mechanical": 5, "electrical": 5, "plumbing": 4, "finishes": 4},
    "community_college": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
}

OFFICE_PROFILE_IDS = {
    "class_a": {
        "tile_profile": "office_class_a_v1",
        "scope_profile": "office_class_a_structural_v1",
    },
    "class_b": {
        "tile_profile": "office_class_b_v1",
        "scope_profile": "office_class_b_structural_v1",
    },
}

OFFICE_SCOPE_DEPTH_FLOOR = {
    "class_a": {"structural": 5, "mechanical": 6, "electrical": 6, "plumbing": 5, "finishes": 6},
    "class_b": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
}

OFFICE_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

CIVIC_PROFILE_IDS = {
    "library": {
        "tile_profile": "civic_library_v1",
        "scope_profile": "civic_library_structural_v1",
    },
    "courthouse": {
        "tile_profile": "civic_courthouse_v1",
        "scope_profile": "civic_courthouse_structural_v1",
    },
    "government_building": {
        "tile_profile": "civic_government_building_v1",
        "scope_profile": "civic_government_building_structural_v1",
    },
    "community_center": {
        "tile_profile": "civic_community_center_v1",
        "scope_profile": "civic_community_center_structural_v1",
    },
    "public_safety": {
        "tile_profile": "civic_public_safety_v1",
        "scope_profile": "civic_public_safety_structural_v1",
    },
}

CIVIC_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

CIVIC_SCOPE_DEPTH_FLOOR = {
    "library": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "courthouse": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "government_building": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "community_center": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "public_safety": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
}

RECREATION_PROFILE_IDS = {
    "fitness_center": {
        "tile_profile": "recreation_fitness_center_v1",
        "scope_profile": "recreation_fitness_center_structural_v1",
    },
    "sports_complex": {
        "tile_profile": "recreation_sports_complex_v1",
        "scope_profile": "recreation_sports_complex_structural_v1",
    },
    "aquatic_center": {
        "tile_profile": "recreation_aquatic_center_v1",
        "scope_profile": "recreation_aquatic_center_structural_v1",
    },
    "recreation_center": {
        "tile_profile": "recreation_recreation_center_v1",
        "scope_profile": "recreation_recreation_center_structural_v1",
    },
    "stadium": {
        "tile_profile": "recreation_stadium_v1",
        "scope_profile": "recreation_stadium_structural_v1",
    },
}

RECREATION_SCOPE_DEPTH_FLOOR = {
    "fitness_center": {"structural": 4, "mechanical": 5, "electrical": 4, "plumbing": 3, "finishes": 4},
    "sports_complex": {"structural": 5, "mechanical": 4, "electrical": 4, "plumbing": 3, "finishes": 4},
    "aquatic_center": {"structural": 4, "mechanical": 6, "electrical": 5, "plumbing": 5, "finishes": 4},
    "recreation_center": {"structural": 4, "mechanical": 5, "electrical": 4, "plumbing": 3, "finishes": 4},
    "stadium": {"structural": 6, "mechanical": 5, "electrical": 5, "plumbing": 4, "finishes": 5},
}

RECREATION_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

PARKING_PROFILE_IDS = {
    "surface_parking": {
        "tile_profile": "parking_surface_parking_v1",
        "scope_profile": "parking_surface_parking_structural_v1",
    },
    "parking_garage": {
        "tile_profile": "parking_parking_garage_v1",
        "scope_profile": "parking_parking_garage_structural_v1",
    },
    "underground_parking": {
        "tile_profile": "parking_underground_parking_v1",
        "scope_profile": "parking_underground_parking_structural_v1",
    },
    "automated_parking": {
        "tile_profile": "parking_automated_parking_v1",
        "scope_profile": "parking_automated_parking_structural_v1",
    },
}

PARKING_SCOPE_DEPTH_FLOOR = {
    "surface_parking": {"structural": 4, "mechanical": 3, "electrical": 4, "plumbing": 2, "finishes": 2},
    "parking_garage": {"structural": 5, "mechanical": 4, "electrical": 5, "plumbing": 2, "finishes": 3},
    "underground_parking": {"structural": 6, "mechanical": 5, "electrical": 5, "plumbing": 3, "finishes": 3},
    "automated_parking": {"structural": 5, "mechanical": 5, "electrical": 6, "plumbing": 2, "finishes": 3},
}

PARKING_PCV_GENERIC_TERMS = {
    "cost control",
    "revenue control",
    "margin control",
    "primary control variable",
    "generic",
}

MIXED_USE_PROFILE_IDS = {
    "office_residential": {
        "tile_profile": "mixed_use_office_residential_v1",
        "scope_profile": "mixed_use_office_residential_structural_v1",
    },
    "retail_residential": {
        "tile_profile": "mixed_use_retail_residential_v1",
        "scope_profile": "mixed_use_retail_residential_structural_v1",
    },
    "hotel_retail": {
        "tile_profile": "mixed_use_hotel_retail_v1",
        "scope_profile": "mixed_use_hotel_retail_structural_v1",
    },
    "transit_oriented": {
        "tile_profile": "mixed_use_transit_oriented_v1",
        "scope_profile": "mixed_use_transit_oriented_structural_v1",
    },
    "urban_mixed": {
        "tile_profile": "mixed_use_urban_mixed_v1",
        "scope_profile": "mixed_use_urban_mixed_structural_v1",
    },
}

MIXED_USE_SCOPE_DEPTH_FLOOR = {
    "office_residential": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "retail_residential": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "hotel_retail": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "transit_oriented": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    "urban_mixed": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
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


def test_full_state_name_resolves_same_as_abbreviation():
    abbreviated = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=50_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        finish_level="standard",
    )
    full_name = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=50_000,
        location="Nashville, Tennessee",
        project_class=ProjectClass.GROUND_UP,
        finish_level="standard",
    )

    assert full_name["construction_costs"]["regional_multiplier"] == pytest.approx(
        abbreviated["construction_costs"]["regional_multiplier"],
        rel=0,
        abs=1e-9,
    )
    assert full_name["modifiers"]["market_factor"] == pytest.approx(
        abbreviated["modifiers"]["market_factor"],
        rel=0,
        abs=1e-9,
    )
    assert full_name["revenue_analysis"]["annual_revenue"] == pytest.approx(
        abbreviated["revenue_analysis"]["annual_revenue"],
        rel=0,
        abs=0.01,
    )
    assert full_name["regional"]["state"] == "TN"
    assert full_name["regional"]["source"] == "metro_override"


def test_regional_payload_matches_applied_modifier_factors():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=50_000,
        location="Nashville, Tennessee",
        project_class=ProjectClass.GROUND_UP,
        finish_level="standard",
    )

    regional = payload["regional"]
    modifiers = payload["modifiers"]
    construction = payload["construction_costs"]
    revenue = payload["revenue_analysis"]

    assert regional["cost_factor"] == pytest.approx(
        construction["regional_multiplier"], rel=0, abs=1e-9
    )
    assert regional["market_factor"] == pytest.approx(
        modifiers["market_factor"], rel=0, abs=1e-9
    )
    assert revenue["market_factor"] == pytest.approx(
        modifiers["market_factor"], rel=0, abs=1e-9
    )


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

    assert base_revenue_factor == pytest.approx(
        base_modifiers["regional_multiplier"] * 1.0,
        rel=1e-9,
    ), "Base revenue factor should include regional market factor"
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
    ownership_target_roi = premium.get("ownership_analysis", {}).get("return_metrics", {}).get("target_roi")
    assert isinstance(ownership_target_roi, (int, float))
    target_roi = float(ownership_target_roi)
    expected_feasible = (npv >= 0) and ((roi_percent or 0) / 100 >= target_roi)
    assert feasible_flag == expected_feasible, "Feasibility flag must reflect ROI hurdle and NPV"


def test_feasibility_trace_target_roi_uses_subtype_financing_terms():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="luxury_apartments",
        square_footage=220_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    trace_entries = [entry for entry in payload["calculation_trace"] if entry["step"] == "feasibility_evaluated"]
    assert trace_entries, "Expected feasibility_evaluated trace entry"
    trace_target_roi = trace_entries[-1]["data"].get("target_roi")
    assert isinstance(trace_target_roi, (int, float))

    subtype_config = get_building_config(BuildingType.MULTIFAMILY, "luxury_apartments")
    assert subtype_config is not None
    financing_terms = subtype_config.ownership_types.get(OwnershipType.FOR_PROFIT)
    if financing_terms is None:
        financing_terms = next(iter(subtype_config.ownership_types.values()))
    assert financing_terms is not None
    assert isinstance(financing_terms.target_roi, (int, float))

    ownership_target_roi = payload.get("ownership_analysis", {}).get("return_metrics", {}).get("target_roi")
    assert isinstance(ownership_target_roi, (int, float))

    assert trace_target_roi == pytest.approx(float(financing_terms.target_roi), rel=0, abs=1e-12)
    assert trace_target_roi == pytest.approx(float(ownership_target_roi), rel=0, abs=1e-12)


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


def test_project_class_multiplier_is_cost_only_global_parity():
    cases = [
        (BuildingType.HEALTHCARE, "hospital", 90_000),
        (BuildingType.MULTIFAMILY, "luxury_apartments", 220_000),
        (BuildingType.OFFICE, "class_a", 180_000),
        (BuildingType.RETAIL, "shopping_center", 120_000),
        (BuildingType.INDUSTRIAL, "warehouse", 150_000),
        (BuildingType.HOSPITALITY, "full_service_hotel", 120_000),
        (BuildingType.EDUCATIONAL, "elementary_school", 90_000),
        (BuildingType.RECREATION, "aquatic_center", 60_000),
        (BuildingType.MIXED_USE, "office_residential", 150_000),
        (BuildingType.PARKING, "surface_parking", 140_000),
        (BuildingType.RESTAURANT, "full_service", 12_000),
        (BuildingType.SPECIALTY, "broadcast_facility", 90_000),
    ]

    for building_type, subtype, square_footage in cases:
        kwargs = dict(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            finish_level="standard",
        )
        ground_up = unified_engine.calculate_project(**kwargs, project_class=ProjectClass.GROUND_UP)
        renovation = unified_engine.calculate_project(**kwargs, project_class=ProjectClass.RENOVATION)
        addition = unified_engine.calculate_project(**kwargs, project_class=ProjectClass.ADDITION)

        base_construction = float(ground_up["construction_costs"]["construction_total"])
        renovation_construction = float(renovation["construction_costs"]["construction_total"])
        addition_construction = float(addition["construction_costs"]["construction_total"])
        assert renovation_construction / base_construction == pytest.approx(0.92, rel=0, abs=1e-9)
        assert addition_construction / base_construction == pytest.approx(1.12, rel=0, abs=1e-9)

        base_revenue = float(ground_up["revenue_analysis"]["annual_revenue"])
        renovation_revenue = float(renovation["revenue_analysis"]["annual_revenue"])
        addition_revenue = float(addition["revenue_analysis"]["annual_revenue"])
        assert renovation_revenue == pytest.approx(base_revenue, rel=0, abs=0.01)
        assert addition_revenue == pytest.approx(base_revenue, rel=0, abs=0.01)


def test_finish_revenue_scaling_applies_once_from_occupancy_and_revenue_factor():
    cases = [
        (BuildingType.MULTIFAMILY, "luxury_apartments", 220_000),
        (BuildingType.OFFICE, "class_a", 180_000),
        (BuildingType.INDUSTRIAL, "warehouse", 150_000),
        (BuildingType.PARKING, "surface_parking", 140_000),
        (BuildingType.RECREATION, "aquatic_center", 60_000),
        (BuildingType.RESTAURANT, "full_service", 12_000),
    ]

    for building_type, subtype, square_footage in cases:
        kwargs = dict(
            building_type=building_type,
            subtype=subtype,
            square_footage=square_footage,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        standard = unified_engine.calculate_project(**kwargs, finish_level="standard")
        premium = unified_engine.calculate_project(**kwargs, finish_level="premium")
        luxury = unified_engine.calculate_project(**kwargs, finish_level="luxury")

        std_revenue = float(standard["revenue_analysis"]["annual_revenue"])
        std_occ = float(standard["revenue_analysis"]["occupancy_rate"])
        std_rev_factor = float(standard["revenue_analysis"]["revenue_factor"])

        premium_revenue = float(premium["revenue_analysis"]["annual_revenue"])
        premium_occ = float(premium["revenue_analysis"]["occupancy_rate"])
        premium_rev_factor = float(premium["revenue_analysis"]["revenue_factor"])

        luxury_revenue = float(luxury["revenue_analysis"]["annual_revenue"])
        luxury_occ = float(luxury["revenue_analysis"]["occupancy_rate"])
        luxury_rev_factor = float(luxury["revenue_analysis"]["revenue_factor"])

        premium_ratio = premium_revenue / std_revenue if std_revenue > 0 else 1.0
        if building_type == BuildingType.OFFICE:
            expected_premium_ratio = (
                (premium_rev_factor / std_rev_factor)
                if std_rev_factor > 0
                else 1.0
            )
        else:
            expected_premium_ratio = (
                (premium_occ / std_occ) * (premium_rev_factor / std_rev_factor)
                if std_occ > 0 and std_rev_factor > 0
                else 1.0
            )
        assert premium_ratio == pytest.approx(expected_premium_ratio, rel=1e-3, abs=1e-3)

        luxury_ratio = luxury_revenue / std_revenue if std_revenue > 0 else 1.0
        if building_type == BuildingType.OFFICE:
            expected_luxury_ratio = (
                (luxury_rev_factor / std_rev_factor)
                if std_rev_factor > 0
                else 1.0
            )
        else:
            expected_luxury_ratio = (
                (luxury_occ / std_occ) * (luxury_rev_factor / std_rev_factor)
                if std_occ > 0 and std_rev_factor > 0
                else 1.0
            )
        assert luxury_ratio == pytest.approx(expected_luxury_ratio, rel=1e-3, abs=1e-3)

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
        "first_break_condition_holds",
        "flex_before_break_pct",
        "break_risk_level",
        "break_risk_reason",
        "break_risk",
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
        "first_break_condition_holds",
        "flex_before_break_pct",
        "break_risk_level",
        "break_risk_reason",
        "break_risk",
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
        (BuildingType.OFFICE, "class_a", 120_000),
        (BuildingType.OFFICE, "class_b", 120_000),
        (BuildingType.INDUSTRIAL, "warehouse", 120_000),
        (BuildingType.INDUSTRIAL, "distribution_center", 120_000),
        (BuildingType.INDUSTRIAL, "manufacturing", 120_000),
        (BuildingType.INDUSTRIAL, "flex_space", 120_000),
        (BuildingType.INDUSTRIAL, "cold_storage", 120_000),
        (BuildingType.HEALTHCARE, "surgical_center", 70_000),
        (BuildingType.HEALTHCARE, "imaging_center", 70_000),
        (BuildingType.HEALTHCARE, "urgent_care", 70_000),
        (BuildingType.HEALTHCARE, "outpatient_clinic", 70_000),
        (BuildingType.HEALTHCARE, "medical_office_building", 70_000),
        (BuildingType.HEALTHCARE, "dental_office", 70_000),
        (BuildingType.HEALTHCARE, "hospital", 70_000),
        (BuildingType.HEALTHCARE, "medical_center", 70_000),
        (BuildingType.HEALTHCARE, "nursing_home", 70_000),
        (BuildingType.HEALTHCARE, "rehabilitation", 70_000),
        (BuildingType.EDUCATIONAL, "elementary_school", 70_000),
        (BuildingType.EDUCATIONAL, "middle_school", 70_000),
        (BuildingType.EDUCATIONAL, "high_school", 70_000),
        (BuildingType.EDUCATIONAL, "university", 70_000),
        (BuildingType.EDUCATIONAL, "community_college", 70_000),
        (BuildingType.SPECIALTY, "data_center", 110_000),
        (BuildingType.SPECIALTY, "laboratory", 70_000),
        (BuildingType.SPECIALTY, "self_storage", 90_000),
        (BuildingType.SPECIALTY, "car_dealership", 65_000),
        (BuildingType.SPECIALTY, "broadcast_facility", 60_000),
        (BuildingType.MIXED_USE, "office_residential", 140_000),
        (BuildingType.MIXED_USE, "retail_residential", 140_000),
        (BuildingType.MIXED_USE, "hotel_retail", 140_000),
        (BuildingType.MIXED_USE, "transit_oriented", 140_000),
        (BuildingType.MIXED_USE, "urban_mixed", 140_000),
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

        first_break_condition_holds = view_model.get("first_break_condition_holds")
        first_break_holds_provenance = di_provenance.get("first_break_condition_holds")
        assert isinstance(first_break_holds_provenance, dict)
        expected_holds = (
            _evaluate_threshold_condition(
                first_break.get("operator"),
                first_break.get("observed_value"),
                first_break.get("threshold"),
            )
            if isinstance(first_break, dict)
            else None
        )
        assert first_break_condition_holds == expected_holds
        if isinstance(first_break, dict):
            if expected_holds is None:
                assert first_break_holds_provenance.get("status") == "unavailable"
                assert first_break_holds_provenance.get("reason") == "operator_or_numeric_inputs_unavailable"
            else:
                assert first_break_holds_provenance.get("status") == "available"
                assert first_break_holds_provenance.get("value") is expected_holds
        else:
            assert first_break_holds_provenance.get("status") == "unavailable"
            assert first_break_holds_provenance.get("reason") == "first_break_condition_unavailable"

        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_provenance.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_provenance.get("band")

        break_risk_level = view_model.get("break_risk_level")
        break_risk_reason = view_model.get("break_risk_reason")
        break_risk_payload = view_model.get("break_risk")
        expected_break_level, expected_break_reason, expected_break_context = _classify_break_risk(
            first_break_condition=first_break,
            flex_before_break_pct=view_model.get("flex_before_break_pct"),
        )
        assert break_risk_level == expected_break_level
        assert break_risk_reason == expected_break_reason
        if expected_break_level is None:
            assert break_risk_payload is None
        else:
            assert break_risk_payload == {
                "level": expected_break_level,
                "reason": expected_break_reason,
            }

        break_risk_provenance = di_provenance.get("break_risk")
        assert isinstance(break_risk_provenance, dict)
        assert break_risk_provenance.get("source") == "decision_insurance.break_risk"
        assert break_risk_provenance.get("scenario_key") == expected_break_context.get("scenario_key")
        expected_flex_normalized = expected_break_context.get("flex_before_break_pct_normalized")
        observed_flex_normalized = break_risk_provenance.get("flex_before_break_pct_normalized")
        if expected_flex_normalized is None:
            assert observed_flex_normalized is None
        else:
            assert observed_flex_normalized == pytest.approx(expected_flex_normalized)
        if expected_break_level is None:
            assert break_risk_provenance.get("status") == "unavailable"
            assert break_risk_provenance.get("reason") == "insufficient_break_risk_inputs"
        else:
            assert break_risk_provenance.get("status") == "available"
            assert break_risk_provenance.get("level") == expected_break_level
            assert break_risk_provenance.get("reason") == expected_break_reason


def test_multifamily_policy_contract_is_explicit_for_first_break_and_flex_band():
    multifamily_cases = [
        ("market_rate_apartments", "multifamily_market_rate_apartments_v1"),
        ("luxury_apartments", "multifamily_luxury_apartments_v1"),
        ("affordable_housing", "multifamily_affordable_housing_v1"),
    ]

    for subtype, expected_profile_id in multifamily_cases:
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MULTIFAMILY,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload["dealshield_tile_profile"] == expected_profile_id
        policy_cfg = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[expected_profile_id]

        profile = get_dealshield_profile(expected_profile_id)
        view_model = build_dealshield_view_model(
            project_id=f"multifamily-contract-{subtype}",
            payload=payload,
            profile=profile,
        )
        di_provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        assert di_provenance.get("profile_id") == expected_profile_id

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert primary_control.get("tile_id") == policy_cfg["primary_control_variable"]["tile_id"]

        first_break_provenance = di_provenance.get("first_break_condition")
        assert isinstance(first_break_provenance, dict)
        assert first_break_provenance.get("status") == "available"
        assert first_break_provenance.get("source") == "decision_insurance_policy.collapse_trigger"
        assert first_break_provenance.get("reason") != "no_modeled_break_condition"

        first_break = view_model.get("first_break_condition")
        assert isinstance(first_break, dict)
        collapse_trigger = policy_cfg["collapse_trigger"]
        configured_operator = collapse_trigger.get("operator")
        expected_operator = (
            configured_operator.strip()
            if isinstance(configured_operator, str) and configured_operator.strip()
            else "<="
        )
        assert first_break.get("break_metric") == collapse_trigger.get("metric")
        assert first_break.get("operator") == expected_operator
        assert first_break.get("threshold") == collapse_trigger.get("threshold")
        assert isinstance(first_break.get("observed_value"), (int, float))

        flex_provenance = di_provenance.get("flex_before_break_pct")
        assert isinstance(flex_provenance, dict)
        assert flex_provenance.get("status") == "available"
        assert flex_provenance.get("calibration_source") == "decision_insurance_policy.flex_calibration"
        assert flex_provenance.get("band") in {"tight", "moderate", "comfortable"}
        assert view_model.get("flex_before_break_band") == flex_provenance.get("band")


def test_specialty_profiles_are_wired_and_content_is_subtype_specific():
    specialty_cases = {
        "data_center": {
            "tile_profile": "specialty_data_center_v1",
            "scope_profile": "specialty_data_center_structural_v1",
        },
        "laboratory": {
            "tile_profile": "specialty_laboratory_v1",
            "scope_profile": "specialty_laboratory_structural_v1",
        },
        "self_storage": {
            "tile_profile": "specialty_self_storage_v1",
            "scope_profile": "specialty_self_storage_structural_v1",
        },
        "car_dealership": {
            "tile_profile": "specialty_car_dealership_v1",
            "scope_profile": "specialty_car_dealership_structural_v1",
        },
        "broadcast_facility": {
            "tile_profile": "specialty_broadcast_facility_v1",
            "scope_profile": "specialty_broadcast_facility_structural_v1",
        },
    }

    first_mlw_texts = []
    for subtype, expected in specialty_cases.items():
        cfg = get_building_config(BuildingType.SPECIALTY, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        profile = get_dealshield_profile(expected["tile_profile"])
        assert profile.get("profile_id") == expected["tile_profile"]
        content = specialty_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and mlw
        first_mlw_texts.append(mlw[0].get("text"))

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_specialty_scope_profiles_keep_depth_and_allocation_integrity():
    min_items_by_subtype = {
        "data_center": {
            "structural": 3,
            "mechanical": 4,
            "electrical": 4,
            "plumbing": 3,
            "finishes": 3,
        },
        "laboratory": {
            "structural": 2,
            "mechanical": 3,
            "electrical": 3,
            "plumbing": 3,
            "finishes": 2,
        },
        "self_storage": {
            "structural": 3,
            "mechanical": 3,
            "electrical": 3,
            "plumbing": 2,
            "finishes": 2,
        },
        "car_dealership": {
            "structural": 3,
            "mechanical": 3,
            "electrical": 3,
            "plumbing": 2,
            "finishes": 2,
        },
        "broadcast_facility": {
            "structural": 3,
            "mechanical": 3,
            "electrical": 3,
            "plumbing": 2,
            "finishes": 2,
        },
    }

    for subtype, trade_minimums in min_items_by_subtype.items():
        config = get_building_config(BuildingType.SPECIALTY, subtype)
        assert config is not None
        profile_id = config.scope_items_profile
        profile = specialty_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, min_items in trade_minimums.items():
            trade = by_trade[trade_key]
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= min_items
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_office_profiles_are_wired_and_registries_are_non_empty():
    assert office_content.DEALSHIELD_CONTENT_PROFILES
    assert office_scope_profiles.SCOPE_ITEM_PROFILES
    assert office_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope_profile"] for subtype, expected in OFFICE_PROFILE_IDS.items()
    }

    first_mlw_texts = []
    for subtype, expected in OFFICE_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.OFFICE, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        tile_profile = get_dealshield_profile(expected["tile_profile"])
        assert tile_profile.get("profile_id") == expected["tile_profile"]
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = office_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        first_mlw_texts.append(mlw[0].get("text"))
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for question_entry in question_bank:
            assert isinstance(question_entry, dict)
            assert question_entry.get("driver_tile_id") in tile_ids

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_office_scope_profiles_keep_depth_and_allocation_integrity():
    for subtype, expected in OFFICE_PROFILE_IDS.items():
        profile_id = expected["scope_profile"]
        profile = office_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, trade in by_trade.items():
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= OFFICE_SCOPE_DEPTH_FLOOR[subtype][trade_key]
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_office_no_clone_invariants_across_tiles_content_and_scope():
    class_a_tile = get_dealshield_profile(OFFICE_PROFILE_IDS["class_a"]["tile_profile"])
    class_b_tile = get_dealshield_profile(OFFICE_PROFILE_IDS["class_b"]["tile_profile"])

    class_a_primary = class_a_tile.get("tiles", [])[2].get("tile_id")
    class_b_primary = class_b_tile.get("tiles", [])[2].get("tile_id")
    assert class_a_primary != class_b_primary

    class_a_rows = {
        row.get("row_id")
        for row in class_a_tile.get("derived_rows", [])
        if isinstance(row, dict)
    }
    class_b_rows = {
        row.get("row_id")
        for row in class_b_tile.get("derived_rows", [])
        if isinstance(row, dict)
    }
    assert class_a_rows != class_b_rows

    class_a_content = office_content.DEALSHIELD_CONTENT_PROFILES[OFFICE_PROFILE_IDS["class_a"]["tile_profile"]]
    class_b_content = office_content.DEALSHIELD_CONTENT_PROFILES[OFFICE_PROFILE_IDS["class_b"]["tile_profile"]]
    assert class_a_content["most_likely_wrong"][0]["text"] != class_b_content["most_likely_wrong"][0]["text"]
    assert class_a_content["fastest_change"]["drivers"][2]["label"] != class_b_content["fastest_change"]["drivers"][2]["label"]

    class_a_scope = office_scope_profiles.SCOPE_ITEM_PROFILES[OFFICE_PROFILE_IDS["class_a"]["scope_profile"]]
    class_b_scope = office_scope_profiles.SCOPE_ITEM_PROFILES[OFFICE_PROFILE_IDS["class_b"]["scope_profile"]]

    class_a_signature = tuple(
        (
            trade.get("trade_key"),
            tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
        )
        for trade in class_a_scope.get("trade_profiles", [])
        if isinstance(trade, dict)
    )
    class_b_signature = tuple(
        (
            trade.get("trade_key"),
            tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
        )
        for trade in class_b_scope.get("trade_profiles", [])
        if isinstance(trade, dict)
    )
    assert class_a_signature != class_b_signature


def test_office_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for expected in OFFICE_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()

        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 35
        for generic_term in OFFICE_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_office_policy_collapse_and_metric_semantics():
    collapse_metric_families = set()

    for subtype, expected in OFFICE_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        profile = get_dealshield_profile(profile_id)
        tile_map = {
            tile.get("tile_id"): tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        tile_id = primary_control.get("tile_id")
        assert tile_id in tile_map
        assert primary_control.get("metric_ref") == tile_map[tile_id].get("metric_ref")

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

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

        if subtype == "class_a":
            assert metric == "value_gap_pct"
            assert float(threshold) >= 0.0
        else:
            assert metric == "value_gap"
            assert float(threshold) <= 0.0

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}


def test_office_underwriting_profiles_are_explicit_and_differentiated():
    assert set(OFFICE_UNDERWRITING_CONFIG.keys()) >= {"class_a", "class_b"}
    class_a_profile = OFFICE_UNDERWRITING_CONFIG["class_a"]
    class_b_profile = OFFICE_UNDERWRITING_CONFIG["class_b"]
    assert isinstance(class_a_profile, dict)
    assert isinstance(class_b_profile, dict)

    required_keys = {
        "base_rent_per_sf",
        "stabilized_occupancy",
        "vacancy_and_credit_loss_pct",
        "opex_pct_of_egi",
        "ti_per_sf",
        "ti_amort_years",
        "lc_pct_of_lease_value",
        "lc_amort_years",
        "exit_cap_rate",
        "yield_on_cost_hurdle",
        "discount_rate",
    }
    assert required_keys.issubset(set(class_a_profile.keys()))
    assert required_keys.issubset(set(class_b_profile.keys()))

    assert class_a_profile != class_b_profile
    assert class_a_profile["base_rent_per_sf"] > class_b_profile["base_rent_per_sf"]
    assert class_a_profile["stabilized_occupancy"] > class_b_profile["stabilized_occupancy"]
    assert class_a_profile["opex_pct_of_egi"] < class_b_profile["opex_pct_of_egi"]

    class_a_cfg = get_building_config(BuildingType.OFFICE, "class_a")
    class_b_cfg = get_building_config(BuildingType.OFFICE, "class_b")
    assert isinstance(class_a_cfg.financial_metrics, dict)
    assert isinstance(class_b_cfg.financial_metrics, dict)
    assert class_a_cfg.financial_metrics == class_a_profile
    assert class_b_cfg.financial_metrics == class_b_profile


def test_office_subtype_underwriting_profiles_drive_differentiated_revenue_and_noi():
    class_a_result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    class_b_result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_b",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    class_a_revenue = float(class_a_result["revenue_analysis"]["annual_revenue"])
    class_b_revenue = float(class_b_result["revenue_analysis"]["annual_revenue"])
    class_a_noi = float(class_a_result["revenue_analysis"]["net_income"])
    class_b_noi = float(class_b_result["revenue_analysis"]["net_income"])

    assert class_a_revenue > class_b_revenue
    assert class_a_noi > class_b_noi
    assert class_a_revenue != class_b_revenue
    assert class_a_noi != class_b_noi


def test_healthcare_profiles_are_wired_and_content_maps_to_tiles():
    healthcare_cases = {
        "surgical_center": {
            "tile_profile": "healthcare_surgical_center_v1",
            "scope_profile": "healthcare_surgical_center_structural_v1",
        },
        "imaging_center": {
            "tile_profile": "healthcare_imaging_center_v1",
            "scope_profile": "healthcare_imaging_center_structural_v1",
        },
        "urgent_care": {
            "tile_profile": "healthcare_urgent_care_v1",
            "scope_profile": "healthcare_urgent_care_structural_v1",
        },
        "outpatient_clinic": {
            "tile_profile": "healthcare_outpatient_clinic_v1",
            "scope_profile": "healthcare_outpatient_clinic_structural_v1",
        },
        "medical_office_building": {
            "tile_profile": "healthcare_medical_office_building_v1",
            "scope_profile": "healthcare_medical_office_building_structural_v1",
        },
        "dental_office": {
            "tile_profile": "healthcare_dental_office_v1",
            "scope_profile": "healthcare_dental_office_structural_v1",
        },
        "hospital": {
            "tile_profile": "healthcare_hospital_v1",
            "scope_profile": "healthcare_hospital_structural_v1",
        },
        "medical_center": {
            "tile_profile": "healthcare_medical_center_v1",
            "scope_profile": "healthcare_medical_center_structural_v1",
        },
        "nursing_home": {
            "tile_profile": "healthcare_nursing_home_v1",
            "scope_profile": "healthcare_nursing_home_structural_v1",
        },
        "rehabilitation": {
            "tile_profile": "healthcare_rehabilitation_v1",
            "scope_profile": "healthcare_rehabilitation_structural_v1",
        },
    }

    mlw_first_texts = []
    for subtype, expected in healthcare_cases.items():
        cfg = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        profile = get_dealshield_profile(expected["tile_profile"])
        assert profile.get("profile_id") == expected["tile_profile"]
        tile_ids = {
            tile.get("tile_id")
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = healthcare_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        mlw_first_texts.append(mlw[0].get("text"))
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for question_entry in question_bank:
            assert isinstance(question_entry, dict)
            assert question_entry.get("driver_tile_id") in tile_ids

    assert len(mlw_first_texts) == len(set(mlw_first_texts))


def test_healthcare_first_mlw_text_is_unique_across_all_subtypes():
    first_mlw_texts = []
    for profile_id in HEALTHCARE_PROFILE_IDS.values():
        content = healthcare_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        mlw_entries = content.get("most_likely_wrong")
        assert isinstance(mlw_entries, list) and mlw_entries
        first_entry = mlw_entries[0]
        assert isinstance(first_entry, dict)
        text = first_entry.get("text")
        assert isinstance(text, str) and text.strip()
        first_mlw_texts.append(text.strip())

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_healthcare_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for profile_id in HEALTHCARE_PROFILE_IDS.values():
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable", {})
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()
        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 30
        for generic_term in HEALTHCARE_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_healthcare_policy_collapse_metrics_are_mixed_and_semantically_wired():
    collapse_metric_families = set()
    flex_signatures = set()

    for profile_id in HEALTHCARE_PROFILE_IDS.values():
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        collapse_trigger = policy.get("collapse_trigger")
        assert isinstance(collapse_trigger, dict)

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
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

        if metric == "value_gap_pct":
            assert abs(float(threshold)) <= 100.0
        else:
            assert float(threshold) <= 0.0 or abs(float(threshold)) >= 100000.0

        flex_calibration = policy.get("flex_calibration")
        assert isinstance(flex_calibration, dict)
        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)
        flex_signatures.add((tight, moderate, fallback))

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}
    assert len(flex_signatures) == len(HEALTHCARE_PROFILE_IDS)


def test_healthcare_content_contract_fields_are_present_and_deterministic():
    required_keys = {"version", "profile_id", "fastest_change", "most_likely_wrong", "question_bank", "red_flags_actions"}

    for profile_id in HEALTHCARE_PROFILE_IDS.values():
        content_first = healthcare_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        content_second = healthcare_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        assert content_first == content_second
        assert required_keys.issubset(content_first.keys())

        fastest_change = content_first.get("fastest_change")
        assert isinstance(fastest_change, dict)
        drivers = fastest_change.get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3

        mlw_entries = content_first.get("most_likely_wrong")
        assert isinstance(mlw_entries, list) and len(mlw_entries) >= 3
        first_mlw = mlw_entries[0]
        assert isinstance(first_mlw, dict)
        assert isinstance(first_mlw.get("driver_tile_id"), str)
        assert isinstance(first_mlw.get("text"), str) and first_mlw.get("text").strip()

        question_bank = content_first.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        assert all(isinstance(entry, dict) and isinstance(entry.get("driver_tile_id"), str) for entry in question_bank)

        red_flags = content_first.get("red_flags_actions")
        assert isinstance(red_flags, list) and len(red_flags) >= 3
        assert all(isinstance(entry, dict) and isinstance(entry.get("flag"), str) for entry in red_flags)


def test_healthcare_scope_profiles_keep_depth_and_allocation_integrity():
    min_items_by_subtype = {
        "surgical_center": {"structural": 3, "mechanical": 4, "electrical": 4, "plumbing": 4, "finishes": 3},
        "imaging_center": {"structural": 4, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 4},
        "urgent_care": {"structural": 4, "mechanical": 4, "electrical": 4, "plumbing": 4, "finishes": 4},
        "outpatient_clinic": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
        "medical_office_building": {"structural": 4, "mechanical": 4, "electrical": 4, "plumbing": 4, "finishes": 4},
        "dental_office": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
        "hospital": {"structural": 4, "mechanical": 5, "electrical": 5, "plumbing": 4, "finishes": 4},
        "medical_center": {"structural": 4, "mechanical": 5, "electrical": 5, "plumbing": 4, "finishes": 4},
        "nursing_home": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
        "rehabilitation": {"structural": 3, "mechanical": 3, "electrical": 3, "plumbing": 3, "finishes": 3},
    }

    for subtype, profile_id in healthcare_scope_profiles.SCOPE_ITEM_DEFAULTS.items():
        cfg = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert cfg is not None
        assert cfg.scope_items_profile == profile_id

        profile = healthcare_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, trade in by_trade.items():
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= min_items_by_subtype[subtype][trade_key]
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_healthcare_runtime_scope_depth_floor_and_trade_reconciliation():
    runtime_minimums = {
        "surgical_center": {"structural": 5, "mechanical": 6, "electrical": 6, "plumbing": 6, "finishes": 5},
        "imaging_center": {"structural": 5, "mechanical": 6, "electrical": 6, "plumbing": 6, "finishes": 5},
        "urgent_care": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
        "outpatient_clinic": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
        "medical_office_building": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
        "dental_office": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
        "hospital": {"structural": 5, "mechanical": 6, "electrical": 6, "plumbing": 6, "finishes": 5},
        "medical_center": {"structural": 5, "mechanical": 6, "electrical": 6, "plumbing": 6, "finishes": 5},
        "nursing_home": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
        "rehabilitation": {"structural": 5, "mechanical": 5, "electrical": 5, "plumbing": 5, "finishes": 5},
    }

    for subtype, expected in runtime_minimums.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=120_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items
        by_trade = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum in expected.items():
            systems = by_trade[trade_key].get("systems")
            assert isinstance(systems, list)
            assert len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)


def test_healthcare_special_feature_alias_targets_exist_in_subtype_configs():
    for subtype, alias_map in HEALTHCARE_SPECIAL_FEATURE_ALIASES.items():
        cfg = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert cfg is not None
        available_feature_ids = set((cfg.special_features or {}).keys())
        assert available_feature_ids

        for legacy_id, canonical_id in alias_map.items():
            assert isinstance(legacy_id, str) and legacy_id
            assert isinstance(canonical_id, str) and canonical_id
            assert canonical_id in available_feature_ids, (
                f"Alias target '{canonical_id}' for subtype '{subtype}' "
                "must exist in the backend special_features config."
            )


def test_healthcare_operational_metric_contract_by_subtype_class():
    outpatient_subtypes = {
        "surgical_center",
        "imaging_center",
        "urgent_care",
        "outpatient_clinic",
        "medical_office_building",
        "dental_office",
    }
    inpatient_subtypes = {
        "hospital",
        "medical_center",
        "nursing_home",
        "rehabilitation",
    }

    for subtype in sorted(outpatient_subtypes | inpatient_subtypes):
        config = get_building_config(BuildingType.HEALTHCARE, subtype)
        assert config is not None
        financial_metrics = config.financial_metrics or {}
        assert financial_metrics.get("primary_unit"), f"{subtype} must define a healthcare primary unit"

        if subtype in outpatient_subtypes:
            assert (
                financial_metrics.get("units_per_sf")
                or getattr(config, "units_per_sf", None)
                or getattr(config, "beds_per_sf", None)
            ), f"{subtype} must define unit density for capacity math"

            if subtype != "dental_office":
                profile = financial_metrics.get("operational_metrics") or {}
                for required_key in (
                    "throughput_per_unit_day",
                    "utilization_target",
                    "provider_fte_per_unit",
                    "support_fte_per_provider",
                ):
                    assert required_key in profile, f"{subtype} missing operational key: {required_key}"
        else:
            assert subtype in HEALTHCARE_INPATIENT_SUBTYPES
            profile = financial_metrics.get("operational_metrics") or {}
            for required_key in (
                "throughput_per_unit_day",
                "utilization_target",
                "average_length_of_stay_days",
                "clinical_staff_fte_per_unit",
                "support_staff_fte_per_unit",
            ):
                assert required_key in profile, f"{subtype} missing inpatient operational key: {required_key}"


def test_healthcare_runtime_emits_utilization_and_efficiency_metrics_for_all_subtypes():
    healthcare_subtypes = [
        "surgical_center",
        "imaging_center",
        "urgent_care",
        "outpatient_clinic",
        "medical_office_building",
        "dental_office",
        "hospital",
        "medical_center",
        "nursing_home",
        "rehabilitation",
    ]

    for subtype in healthcare_subtypes:
        result = unified_engine.calculate_project(
            building_type=BuildingType.HEALTHCARE,
            subtype=subtype,
            square_footage=120_000 if subtype in HEALTHCARE_INPATIENT_SUBTYPES else 12_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        metrics = result.get("operational_metrics") or {}
        staffing = metrics.get("staffing") or []
        kpis = metrics.get("kpis") or []
        per_unit = metrics.get("per_unit") or {}
        facility_metrics = result.get("facility_metrics") or {}

        assert staffing, f"{subtype} must emit staffing metrics"
        assert kpis, f"{subtype} must emit KPI metrics"
        assert per_unit.get("units", 0) >= 1, f"{subtype} must emit non-zero unit count"
        assert facility_metrics.get("type") == "healthcare", f"{subtype} must emit healthcare facility metrics"

        kpi_labels = [str(entry.get("label", "")) for entry in kpis if isinstance(entry, dict)]
        assert any("Utilization" in label or "Occupancy" in label for label in kpi_labels), (
            f"{subtype} must emit utilization/occupancy KPI"
        )
        assert any(("Efficiency" in label) or ("Yield" in label) for label in kpi_labels), (
            f"{subtype} must emit efficiency KPI"
        )
        if subtype in HEALTHCARE_INPATIENT_SUBTYPES:
            occupancy_entry = next(
                (entry for entry in kpis if "Occupancy" in str(entry.get("label", ""))),
                None,
            )
            assert occupancy_entry is not None, f"{subtype} must emit occupancy KPI value"
            occupancy_pct = float(str(occupancy_entry.get("value", "0")).replace("%", ""))
            assert 0.0 <= occupancy_pct <= 100.0, (
                f"{subtype} occupancy must be bounded to 0-100, got {occupancy_pct}"
            )


def test_educational_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for profile_id in EDUCATIONAL_PROFILE_IDS.values():
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()

        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 30
        for generic_term in EDUCATIONAL_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_educational_policy_collapse_metrics_are_mixed_and_semantically_wired():
    collapse_metric_families = set()
    flex_signatures = set()

    for profile_id in EDUCATIONAL_PROFILE_IDS.values():
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
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

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)
        flex_signatures.add((tight, moderate, fallback))

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}
    assert len(flex_signatures) == len(EDUCATIONAL_PROFILE_IDS)


def test_educational_profiles_resolve_canonical_di_policy_and_deterministic_contract_provenance():
    for subtype, profile_id in EDUCATIONAL_PROFILE_IDS.items():
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"educational-invariant-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"educational-invariant-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        status_provenance = view_a.get("decision_status_provenance")
        assert isinstance(status_provenance, dict)
        assert isinstance(status_provenance.get("status_source"), str)

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "first_break_condition_holds",
            "flex_before_break_pct",
            "flex_before_break_band",
            "break_risk_level",
            "break_risk_reason",
            "break_risk",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_educational_schedule_source_and_scope_depth_invariants():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, floors in EDUCATIONAL_SCOPE_DEPTH_FLOOR.items():
        schedule = build_construction_schedule(BuildingType.EDUCATIONAL, subtype)
        assert schedule.get("building_type") == BuildingType.EDUCATIONAL.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

        payload = unified_engine.calculate_project(
            building_type=BuildingType.EDUCATIONAL,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        by_trade = {
            str(trade_block.get("trade", "")).strip().lower(): trade_block
            for trade_block in scope_items
            if isinstance(trade_block, dict) and isinstance(trade_block.get("trade"), str)
        }
        assert required_trades.issubset(by_trade.keys())

        for trade_key, minimum_items in floors.items():
            trade_block = by_trade[trade_key]
            systems = trade_block.get("systems")
            if not isinstance(systems, list):
                systems = trade_block.get("items")
            assert isinstance(systems, list)
            assert len(systems) >= minimum_items

    unknown_schedule = build_construction_schedule(
        BuildingType.EDUCATIONAL,
        "unknown_educational_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.EDUCATIONAL.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    phases = unknown_schedule.get("phases")
    assert isinstance(phases, list) and phases


def test_civic_first_mlw_text_is_unique_across_all_subtypes():
    first_mlw_texts = []

    for expected in CIVIC_PROFILE_IDS.values():
        content = civic_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        mlw_entries = content.get("most_likely_wrong")
        assert isinstance(mlw_entries, list) and mlw_entries

        first_entry = mlw_entries[0]
        assert isinstance(first_entry, dict)
        first_text = first_entry.get("text")
        assert isinstance(first_text, str) and first_text.strip()
        first_mlw_texts.append(first_text.strip())

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_civic_subtypes_do_not_leak_baseline_alias_wiring():
    for subtype, expected in CIVIC_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.CIVIC, subtype)
        assert cfg is not None

        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        assert cfg.dealshield_tile_profile != "civic_baseline_v1"
        assert cfg.scope_items_profile != "civic_baseline_structural_v1"


def test_civic_profile_resolution_is_present_and_deterministic():
    scope_defaults = civic_scope_profiles.SCOPE_ITEM_DEFAULTS.get("default_profile_by_subtype")
    assert isinstance(scope_defaults, dict)

    for subtype, expected in CIVIC_PROFILE_IDS.items():
        tile_profile_id = expected["tile_profile"]
        scope_profile_id = expected["scope_profile"]

        first_tile = get_dealshield_profile(tile_profile_id)
        second_tile = get_dealshield_profile(tile_profile_id)
        assert first_tile == second_tile
        assert first_tile.get("profile_id") == tile_profile_id

        content_first = civic_content.DEALSHIELD_CONTENT_PROFILES[tile_profile_id]
        content_second = civic_content.DEALSHIELD_CONTENT_PROFILES[tile_profile_id]
        assert content_first == content_second
        assert content_first.get("profile_id") == tile_profile_id

        scope_profile = civic_scope_profiles.SCOPE_ITEM_PROFILES[scope_profile_id]
        assert scope_profile.get("profile_id") == scope_profile_id
        assert scope_defaults.get(subtype) == scope_profile_id

        cfg = get_building_config(BuildingType.CIVIC, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == tile_profile_id
        assert cfg.scope_items_profile == scope_profile_id


def test_civic_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for expected in CIVIC_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()

        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 30
        for generic_term in CIVIC_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_civic_policy_collapse_metrics_are_mixed_and_semantically_wired():
    collapse_metric_families = set()
    flex_signatures = set()

    for expected in CIVIC_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        profile = get_dealshield_profile(profile_id)
        tile_map = {
            tile.get("tile_id"): tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        tile_id = primary_control.get("tile_id")
        assert tile_id in tile_map
        assert primary_control.get("metric_ref") == tile_map[tile_id].get("metric_ref")

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

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

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)
        flex_signatures.add((tight, moderate, fallback))

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}
    assert len(flex_signatures) == len(CIVIC_PROFILE_IDS)


def test_civic_profiles_resolve_canonical_di_policy_and_deterministic_contract_provenance():
    for subtype, expected in CIVIC_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=75_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"civic-invariant-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"civic-invariant-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        status_provenance = view_a.get("decision_status_provenance")
        assert isinstance(status_provenance, dict)
        assert isinstance(status_provenance.get("status_source"), str)

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "flex_before_break_pct",
            "flex_before_break_band",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_civic_schedule_source_and_scope_depth_invariants():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, floors in CIVIC_SCOPE_DEPTH_FLOOR.items():
        schedule = build_construction_schedule(BuildingType.CIVIC, subtype)
        assert schedule.get("building_type") == BuildingType.CIVIC.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

        payload = unified_engine.calculate_project(
            building_type=BuildingType.CIVIC,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        by_trade = {
            str(trade_block.get("trade", "")).strip().lower(): trade_block
            for trade_block in scope_items
            if isinstance(trade_block, dict) and isinstance(trade_block.get("trade"), str)
        }
        assert required_trades.issubset(by_trade.keys())

        for trade_key, minimum_items in floors.items():
            trade_block = by_trade[trade_key]
            systems = trade_block.get("systems")
            if not isinstance(systems, list):
                systems = trade_block.get("items")
            assert isinstance(systems, list)
            assert len(systems) >= minimum_items

    unknown_schedule = build_construction_schedule(
        BuildingType.CIVIC,
        "unknown_civic_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.CIVIC.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    phases = unknown_schedule.get("phases")
    assert isinstance(phases, list) and phases


def test_civic_di_policy_entries_are_available_for_all_profiles():
    for expected in CIVIC_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")
        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        assert collapse_trigger.get("metric") in {"value_gap_pct", "value_gap"}
        assert collapse_trigger.get("operator") in {"<=", "<"}


def test_recreation_first_mlw_text_is_unique_across_all_subtypes():
    first_mlw_texts = []

    for expected in RECREATION_PROFILE_IDS.values():
        content = recreation_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        mlw_entries = content.get("most_likely_wrong")
        assert isinstance(mlw_entries, list) and mlw_entries

        first_entry = mlw_entries[0]
        assert isinstance(first_entry, dict)
        first_text = first_entry.get("text")
        assert isinstance(first_text, str) and first_text.strip()
        first_mlw_texts.append(first_text.strip())

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_recreation_subtypes_do_not_leak_baseline_alias_wiring():
    for subtype, expected in RECREATION_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.RECREATION, subtype)
        assert cfg is not None

        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        assert cfg.dealshield_tile_profile != "recreation_baseline_v1"
        assert cfg.scope_items_profile != "recreation_baseline_structural_v1"


def test_recreation_profile_resolution_is_present_and_deterministic():
    scope_defaults = recreation_scope_profiles.SCOPE_ITEM_DEFAULTS.get("default_profile_by_subtype")
    assert isinstance(scope_defaults, dict)

    for subtype, expected in RECREATION_PROFILE_IDS.items():
        tile_profile_id = expected["tile_profile"]
        scope_profile_id = expected["scope_profile"]

        first_tile = get_dealshield_profile(tile_profile_id)
        second_tile = get_dealshield_profile(tile_profile_id)
        assert first_tile == second_tile
        assert first_tile.get("profile_id") == tile_profile_id

        content_first = recreation_content.DEALSHIELD_CONTENT_PROFILES[tile_profile_id]
        content_second = recreation_content.DEALSHIELD_CONTENT_PROFILES[tile_profile_id]
        assert content_first == content_second
        assert content_first.get("profile_id") == tile_profile_id

        scope_profile = recreation_scope_profiles.SCOPE_ITEM_PROFILES[scope_profile_id]
        assert scope_profile.get("profile_id") == scope_profile_id
        assert scope_defaults.get(subtype) == scope_profile_id

        cfg = get_building_config(BuildingType.RECREATION, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == tile_profile_id
        assert cfg.scope_items_profile == scope_profile_id


def test_recreation_profile_existence_and_scope_depth_invariants():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, expected in RECREATION_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        scope_profile_id = expected["scope_profile"]
        floors = RECREATION_SCOPE_DEPTH_FLOOR[subtype]

        tile_profile = get_dealshield_profile(profile_id)
        assert tile_profile.get("profile_id") == profile_id

        content_profile = recreation_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        assert content_profile.get("profile_id") == profile_id

        scope_profile = recreation_scope_profiles.SCOPE_ITEM_PROFILES[scope_profile_id]
        assert scope_profile.get("profile_id") == scope_profile_id

        trade_profiles = scope_profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5
        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert required_trades == set(by_trade.keys())

        for trade_key, minimum_items in floors.items():
            items = by_trade[trade_key].get("items")
            assert isinstance(items, list)
            assert len(items) >= minimum_items


def test_recreation_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for expected in RECREATION_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()

        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        assert len(normalized_label) >= 30
        for generic_term in RECREATION_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_recreation_policy_collapse_metrics_are_mixed_and_semantically_wired():
    collapse_metric_families = set()
    flex_signatures = set()

    for expected in RECREATION_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        profile = get_dealshield_profile(profile_id)
        tile_map = {
            tile.get("tile_id"): tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        tile_id = primary_control.get("tile_id")
        assert tile_id in tile_map
        assert primary_control.get("metric_ref") == tile_map[tile_id].get("metric_ref")

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

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

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)
        flex_signatures.add((tight, moderate, fallback))

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}
    assert len(flex_signatures) == len(RECREATION_PROFILE_IDS)


def test_recreation_profiles_resolve_canonical_di_policy_and_deterministic_contract_provenance():
    for subtype, expected in RECREATION_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.RECREATION,
            subtype=subtype,
            square_footage=95_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"recreation-invariant-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"recreation-invariant-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        status_provenance = view_a.get("decision_status_provenance")
        assert isinstance(status_provenance, dict)
        assert isinstance(status_provenance.get("status_source"), str)

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "flex_before_break_pct",
            "flex_before_break_band",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_recreation_schedule_source_and_scope_depth_invariants():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, floors in RECREATION_SCOPE_DEPTH_FLOOR.items():
        schedule = build_construction_schedule(BuildingType.RECREATION, subtype)
        assert schedule.get("building_type") == BuildingType.RECREATION.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

        payload = unified_engine.calculate_project(
            building_type=BuildingType.RECREATION,
            subtype=subtype,
            square_footage=95_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items

        by_trade = {
            str(trade_block.get("trade", "")).strip().lower(): trade_block
            for trade_block in scope_items
            if isinstance(trade_block, dict) and isinstance(trade_block.get("trade"), str)
        }
        assert required_trades.issubset(by_trade.keys())

        for trade_key, minimum_items in floors.items():
            trade_block = by_trade[trade_key]
            systems = trade_block.get("systems")
            if not isinstance(systems, list):
                systems = trade_block.get("items")
            assert isinstance(systems, list)
            assert len(systems) >= minimum_items

    unknown_schedule = build_construction_schedule(
        BuildingType.RECREATION,
        "unknown_recreation_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.RECREATION.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    phases = unknown_schedule.get("phases")
    assert isinstance(phases, list) and phases


def test_recreation_di_policy_entries_are_available_for_all_profiles():
    for expected in RECREATION_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")
        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        assert collapse_trigger.get("metric") in {"value_gap_pct", "value_gap"}
        assert collapse_trigger.get("operator") in {"<=", "<"}


def test_parking_profiles_are_wired_and_content_maps_to_tiles():
    first_mlw_texts = []

    for subtype, expected in PARKING_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.PARKING, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        profile = get_dealshield_profile(expected["tile_profile"])
        assert profile.get("profile_id") == expected["tile_profile"]
        tile_ids = {
            tile.get("tile_id")
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = parking_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        first_mlw_texts.append(mlw[0].get("text"))
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for question_entry in question_bank:
            assert isinstance(question_entry, dict)
            assert question_entry.get("driver_tile_id") in tile_ids

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_parking_scope_profiles_keep_depth_and_allocation_integrity():
    for subtype, expected in PARKING_PROFILE_IDS.items():
        profile_id = expected["scope_profile"]
        cfg = get_building_config(BuildingType.PARKING, subtype)
        assert cfg is not None
        assert cfg.scope_items_profile == profile_id
        assert parking_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype] == profile_id

        profile = parking_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in PARKING_SCOPE_DEPTH_FLOOR[subtype].items():
            items = by_trade[trade_key].get("items")
            assert isinstance(items, list)
            assert len(items) >= minimum
            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_parking_no_clone_invariants_across_tiles_content_and_scope():
    unique_tile_ids = set()
    unique_row_ids = set()
    scope_signatures = set()

    for expected in PARKING_PROFILE_IDS.values():
        tile_profile = get_dealshield_profile(expected["tile_profile"])
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        subtype_tile_ids = tile_ids - {"cost_plus_10", "revenue_minus_10"}
        assert len(subtype_tile_ids) == 1
        unique_tile_ids.update(subtype_tile_ids)

        subtype_rows = {
            row.get("row_id")
            for row in tile_profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        } - {"conservative", "ugly"}
        assert len(subtype_rows) == 1
        unique_row_ids.update(subtype_rows)

        scope_profile = parking_scope_profiles.SCOPE_ITEM_PROFILES[expected["scope_profile"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.add(signature)

    assert len(unique_tile_ids) == len(PARKING_PROFILE_IDS)
    assert len(unique_row_ids) == len(PARKING_PROFILE_IDS)
    assert len(scope_signatures) == len(PARKING_PROFILE_IDS)


def test_parking_runtime_scope_depth_floor_and_trade_reconciliation():
    for subtype, expected in PARKING_SCOPE_DEPTH_FLOOR.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.PARKING,
            subtype=subtype,
            square_footage=110_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items
        by_trade = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum in expected.items():
            systems = by_trade[trade_key].get("systems")
            if not isinstance(systems, list):
                systems = by_trade[trade_key].get("items")
            assert isinstance(systems, list)
            assert len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)


def test_parking_di_policy_labels_are_ic_first_and_non_generic():
    labels = []
    for expected in PARKING_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable", {})
        label = primary_control.get("label")
        assert isinstance(label, str) and label.strip()
        normalized_label = label.strip().lower()
        assert normalized_label.startswith("ic-first ")
        for generic_term in PARKING_PCV_GENERIC_TERMS:
            assert generic_term not in normalized_label
        labels.append(normalized_label)

    assert len(labels) == len(set(labels))


def test_parking_policy_collapse_metrics_are_mixed_and_semantically_wired():
    collapse_metric_families = set()

    for expected in PARKING_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID[profile_id]
        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")

        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        profile = get_dealshield_profile(profile_id)
        tile_map = {
            tile.get("tile_id"): tile
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        tile_id = primary_control.get("tile_id")
        assert tile_id in tile_map
        assert primary_control.get("metric_ref") == tile_map[tile_id].get("metric_ref")

        metric = collapse_trigger.get("metric")
        operator = collapse_trigger.get("operator")
        threshold = collapse_trigger.get("threshold")
        scenario_priority = collapse_trigger.get("scenario_priority")

        assert metric in {"value_gap_pct", "value_gap"}
        assert operator in {"<=", "<"}
        assert isinstance(threshold, (int, float))
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert len(set(scenario_priority)) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))

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

        tight = float(flex_calibration.get("tight_max_pct"))
        moderate = float(flex_calibration.get("moderate_max_pct"))
        fallback = float(flex_calibration.get("fallback_pct"))
        assert tight <= moderate
        assert fallback >= 0.0

        collapse_metric_families.add(metric)

    assert collapse_metric_families == {"value_gap_pct", "value_gap"}


def test_parking_profiles_resolve_canonical_di_policy_and_deterministic_contract_provenance():
    for subtype, expected in PARKING_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.PARKING,
            subtype=subtype,
            square_footage=110_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"parking-invariant-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"parking-invariant-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        status_provenance = view_a.get("decision_status_provenance")
        assert isinstance(status_provenance, dict)
        assert isinstance(status_provenance.get("status_source"), str)

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "flex_before_break_pct",
            "flex_before_break_band",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_parking_schedule_source_and_unknown_fallback_invariants():
    for subtype in PARKING_PROFILE_IDS.keys():
        schedule = build_construction_schedule(BuildingType.PARKING, subtype)
        assert schedule.get("building_type") == BuildingType.PARKING.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

    unknown_schedule = build_construction_schedule(
        BuildingType.PARKING,
        "unknown_parking_variant",
    )
    industrial_default = build_construction_schedule(BuildingType.INDUSTRIAL)
    assert unknown_schedule.get("building_type") == BuildingType.PARKING.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    assert unknown_schedule.get("total_months") == industrial_default.get("total_months")
    assert unknown_schedule.get("phases") == industrial_default.get("phases")


def test_mixed_use_profiles_are_wired_and_content_maps_to_tiles():
    first_mlw_texts = []

    for subtype, expected in MIXED_USE_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.MIXED_USE, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        profile = get_dealshield_profile(expected["tile_profile"])
        assert profile.get("profile_id") == expected["tile_profile"]
        tile_ids = {
            tile.get("tile_id")
            for tile in profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = mixed_use_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        first_mlw_texts.append(mlw[0].get("text"))
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for question_entry in question_bank:
            assert isinstance(question_entry, dict)
            assert question_entry.get("driver_tile_id") in tile_ids

    assert len(first_mlw_texts) == len(set(first_mlw_texts))


def test_mixed_use_scope_profiles_keep_depth_and_allocation_integrity():
    for subtype, expected in MIXED_USE_PROFILE_IDS.items():
        profile_id = expected["scope_profile"]
        cfg = get_building_config(BuildingType.MIXED_USE, subtype)
        assert cfg is not None
        assert cfg.scope_items_profile == profile_id
        assert mixed_use_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype] == profile_id

        profile = mixed_use_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, trade in by_trade.items():
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= MIXED_USE_SCOPE_DEPTH_FLOOR[subtype][trade_key]
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_mixed_use_no_clone_invariants_across_tiles_content_and_scope():
    unique_tile_ids = set()
    unique_row_ids = set()
    scope_signatures = set()

    for expected in MIXED_USE_PROFILE_IDS.values():
        tile_profile = get_dealshield_profile(expected["tile_profile"])
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        subtype_tile_ids = tile_ids - {"cost_plus_10", "revenue_minus_10"}
        assert len(subtype_tile_ids) == 1
        unique_tile_ids.update(subtype_tile_ids)

        subtype_rows = {
            row.get("row_id")
            for row in tile_profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        } - {"conservative", "ugly"}
        assert len(subtype_rows) == 1
        unique_row_ids.update(subtype_rows)

        scope_profile = mixed_use_scope_profiles.SCOPE_ITEM_PROFILES[expected["scope_profile"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.add(signature)

    assert len(unique_tile_ids) == len(MIXED_USE_PROFILE_IDS)
    assert len(unique_row_ids) == len(MIXED_USE_PROFILE_IDS)
    assert len(scope_signatures) == len(MIXED_USE_PROFILE_IDS)


def test_mixed_use_runtime_scope_depth_floor_and_trade_reconciliation():
    for subtype, expected in MIXED_USE_SCOPE_DEPTH_FLOOR.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.MIXED_USE,
            subtype=subtype,
            square_footage=125_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        scope_items = payload.get("scope_items")
        assert isinstance(scope_items, list) and scope_items
        by_trade = {
            str(trade.get("trade") or "").strip().lower(): trade
            for trade in scope_items
            if isinstance(trade, dict)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        trade_breakdown = payload.get("trade_breakdown") or {}
        for trade_key, minimum in expected.items():
            systems = by_trade[trade_key].get("systems")
            assert isinstance(systems, list)
            assert len(systems) >= minimum
            systems_total = sum(float(system.get("total_cost", 0.0) or 0.0) for system in systems)
            assert systems_total == pytest.approx(float(trade_breakdown.get(trade_key, 0.0) or 0.0), rel=0, abs=1e-6)


def test_mixed_use_di_policy_entries_are_available_for_all_profiles():
    for expected in MIXED_USE_PROFILE_IDS.values():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        primary_control = policy.get("primary_control_variable")
        collapse_trigger = policy.get("collapse_trigger")
        flex_calibration = policy.get("flex_calibration")
        assert isinstance(primary_control, dict)
        assert isinstance(collapse_trigger, dict)
        assert isinstance(flex_calibration, dict)

        assert collapse_trigger.get("metric") in {"value_gap_pct", "value_gap"}
        assert collapse_trigger.get("operator") in {"<=", "<"}
        scenario_priority = collapse_trigger.get("scenario_priority")
        assert isinstance(scenario_priority, list) and len(scenario_priority) == 4
        assert scenario_priority[0] == "base"
        assert {"base", "conservative", "ugly"}.issubset(set(scenario_priority))


def test_mixed_use_profiles_resolve_canonical_di_policy_and_deterministic_contract_provenance():
    for subtype, expected in MIXED_USE_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        policy = DECISION_INSURANCE_POLICY_BY_PROFILE_ID.get(profile_id)
        assert isinstance(policy, dict)

        kwargs = dict(
            building_type=BuildingType.MIXED_USE,
            subtype=subtype,
            square_footage=100_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        payload_a = unified_engine.calculate_project(**kwargs)
        payload_b = unified_engine.calculate_project(**kwargs)
        profile = get_dealshield_profile(profile_id)

        view_a = build_dealshield_view_model(
            project_id=f"mixed-use-invariant-a-{subtype}",
            payload=payload_a,
            profile=profile,
        )
        view_b = build_dealshield_view_model(
            project_id=f"mixed-use-invariant-b-{subtype}",
            payload=payload_b,
            profile=profile,
        )

        di_provenance = view_a.get("decision_insurance_provenance")
        assert isinstance(di_provenance, dict)
        policy_block = di_provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("policy_id") == DECISION_INSURANCE_POLICY_ID
        assert policy_block.get("profile_id") == profile_id

        status_provenance = view_a.get("decision_status_provenance")
        assert isinstance(status_provenance, dict)
        assert isinstance(status_provenance.get("status_source"), str)

        first_break = view_a.get("first_break_condition")
        assert isinstance(first_break, dict)
        assert first_break.get("break_metric") in {"value_gap_pct", "value_gap"}
        assert isinstance(first_break.get("threshold"), (int, float))
        assert isinstance(first_break.get("observed_value"), (int, float))

        for key in (
            "decision_status",
            "decision_reason_code",
            "first_break_condition",
            "flex_before_break_pct",
            "flex_before_break_band",
            "decision_status_provenance",
            "decision_insurance_provenance",
        ):
            assert view_a.get(key) == view_b.get(key), f"Expected deterministic equality for '{key}'"


def test_mixed_use_schedule_source_and_unknown_fallback_invariants():
    for subtype in MIXED_USE_PROFILE_IDS.keys():
        schedule = build_construction_schedule(BuildingType.MIXED_USE, subtype)
        assert schedule.get("building_type") == BuildingType.MIXED_USE.value
        assert schedule.get("schedule_source") == "subtype"
        assert schedule.get("subtype") == subtype
        phases = schedule.get("phases")
        assert isinstance(phases, list) and phases

    unknown_schedule = build_construction_schedule(
        BuildingType.MIXED_USE,
        "unknown_mixed_use_variant",
    )
    assert unknown_schedule.get("building_type") == BuildingType.MIXED_USE.value
    assert unknown_schedule.get("schedule_source") == "building_type"
    assert unknown_schedule.get("subtype") is None
    assert unknown_schedule.get("total_months") == 30


def test_mixed_use_split_provenance_surfaces_in_scenarios_and_view_model_context():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="office_residential",
        square_footage=130_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {
                "components": {"office": 65},
                "pattern": "component_percent",
            },
            "description": "mixed-use office and residential stack with 65 office share",
        },
    )

    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "user_input"
    assert split.get("normalization_applied") is True
    assert split.get("value", {}).get("office") == pytest.approx(65.0)
    assert split.get("value", {}).get("residential") == pytest.approx(35.0)

    scenario_inputs = (
        payload.get("dealshield_scenarios", {})
        .get("provenance", {})
        .get("scenario_inputs", {})
    )
    assert isinstance(scenario_inputs, dict) and scenario_inputs
    for scenario_input in scenario_inputs.values():
        assert scenario_input.get("mixed_use_split_source") == "user_input"
        scenario_split = scenario_input.get("mixed_use_split")
        assert isinstance(scenario_split, dict)
        assert scenario_split.get("value", {}).get("office") == pytest.approx(65.0)
        assert scenario_split.get("value", {}).get("residential") == pytest.approx(35.0)

    profile_id = MIXED_USE_PROFILE_IDS["office_residential"]["tile_profile"]
    profile = get_dealshield_profile(profile_id)
    view_model = build_dealshield_view_model(
        project_id="mixed-use-view-model-split-provenance",
        payload=payload,
        profile=profile,
    )
    view_provenance = view_model.get("provenance")
    assert isinstance(view_provenance, dict)
    view_scenario_inputs = view_provenance.get("scenario_inputs")
    assert isinstance(view_scenario_inputs, dict) and view_scenario_inputs
    for scenario_input in view_scenario_inputs.values():
        assert scenario_input.get("mixed_use_split_source") == "user_input"
        scenario_split = scenario_input.get("mixed_use_split")
        assert isinstance(scenario_split, dict)
        assert scenario_split.get("value", {}).get("office") == pytest.approx(65.0)
        assert scenario_split.get("value", {}).get("residential") == pytest.approx(35.0)


def test_mixed_use_split_invalid_mix_falls_back_explicitly_without_silent_coercion():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.MIXED_USE,
        subtype="urban_mixed",
        square_footage=120_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        parsed_input_overrides={
            "mixed_use_split": {
                "components": {"office": 70, "invalid_component": 30},
            },
            "description": "mixed-use urban project",
        },
    )

    split = payload.get("mixed_use_split")
    assert isinstance(split, dict)
    assert split.get("source") == "default"
    assert split.get("normalization_applied") is False
    assert isinstance(split.get("invalid_mix"), dict)
    assert split.get("invalid_mix", {}).get("reason") == "unsupported_component"

    split_value = split.get("value")
    assert isinstance(split_value, dict)
    assert split_value.get("office") == pytest.approx(50.0)
    assert split_value.get("residential") == pytest.approx(50.0)
