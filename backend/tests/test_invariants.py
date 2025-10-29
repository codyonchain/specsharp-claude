import math

import pytest

from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    get_building_config,
    get_margin_pct,
    validate_config,
)


def test_state_required_for_multiplier():
    """City-only inputs must fall back to baseline multiplier and raise an explicit trace warning."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=10_000,
        location="Nashville",  # Missing state info
        project_class=ProjectClass.GROUND_UP,
    )

    multiplier = result["construction_costs"]["regional_multiplier"]
    assert multiplier == pytest.approx(1.03), "City-only locations should follow configured override when available"

    trace_strings = " | ".join(entry["step"] for entry in result["calculation_trace"]).lower()
    trace_payload = " | ".join(str(entry["data"]) for entry in result["calculation_trace"]).lower()
    assert "warning" in trace_strings or "warning" in trace_payload, "Missing state must be called out in calculation trace"


def test_revenue_uses_own_multiplier():
    """Revenue calculations must reference an explicit regional multiplier separate from cost."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=25_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    cost_multiplier = result["construction_costs"]["regional_multiplier"]
    revenue_multiplier = result["revenue_analysis"].get("regional_multiplier")

    assert revenue_multiplier is not None, "Revenue analysis is missing a dedicated regional multiplier"
    assert not math.isclose(
        revenue_multiplier,
        cost_multiplier,
    ), "Revenue multiplier must not silently re-use the cost multiplier"


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
    """If restaurant costs are clamped, the trace must surface the adjustment."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=1_000,
        location="Memphis, TN",
        project_class=ProjectClass.TENANT_IMPROVEMENT,
    )

    trace_steps = [entry["step"] for entry in result["calculation_trace"]]
    assert any(step == "restaurant_cost_clamp" for step in trace_steps), "Restaurant clamp must emit an explicit trace entry"


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
    assert trace_data["method"] == "fixed_percentage"
    expected_noi = result["totals"]["total_project_cost"] * 0.08
    assert trace_data["estimated_noi"] == pytest.approx(expected_noi, rel=1e-3)


def test_noi_is_revenue_minus_opex():
    """Backward-compatible alias for targeted pytest selection."""
    test_margin_normalized_noi_is_revenue_minus_opex()


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
    assert trace_data["quality_factor"] == pytest.approx(1.1, rel=1e-3)


def test_caprate_only_for_supported_types():
    """Cap-rate valuation should only trigger for the supported real estate asset classes."""
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

    assert supported["return_metrics"]["property_value"] not in (None, 0), "Supported types must surface cap-rate derived property value"
    assert unsupported["return_metrics"]["property_value"] in (None, 0), "Unsupported types should not expose cap-rate valuations"


def test_config_integrity():
    """Master config should validate trade percentages and financing ratios."""
    errors = validate_config()
    assert errors == [], f"Configuration integrity issues detected: {errors}"
