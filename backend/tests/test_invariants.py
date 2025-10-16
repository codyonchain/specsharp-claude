import math

import pytest

from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    get_building_config,
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
    expected_increment = config.special_features["operating_room"]

    delta = feature_result["construction_costs"]["special_features_total"] - base_result["construction_costs"]["special_features_total"]
    assert delta == pytest.approx(
        expected_increment,
        rel=1e-3,
    ), "Operating room surcharge should be per unit, not per square foot"


def test_restaurant_clamp_is_explicit_or_off():
    """If restaurant costs are clamped, the trace must surface the adjustment."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=1_000,
        location="Memphis, TN",
        project_class=ProjectClass.TENANT_IMPROVEMENT,
    )

    trace_steps = [entry["step"].lower() for entry in result["calculation_trace"]]
    assert any("restaurant cost too" in step for step in trace_steps), "Restaurant clamp must emit an explicit trace entry"


def test_noi_is_revenue_minus_opex():
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
    assert noi == pytest.approx(
        derived_noi,
        rel=1e-3,
    ), "NOI should reconcile to revenue minus OPEX"


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
