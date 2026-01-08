from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import BuildingType, ProjectClass


def test_nashville_override_emits_trace_flag():
    """
    Nashville override (city-only -> forced multiplier) must emit a trace entry.
    """
    result = unified_engine.calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=20_000,
        location="Nashville",  # Triggers hard-coded override
        project_class=ProjectClass.GROUND_UP,
    )

    trace_steps = [entry["step"].lower() for entry in result["calculation_trace"]]
    assert any("override" in step for step in trace_steps), "Regional overrides must be surfaced in calculation trace"


def test_restaurant_clamp_emits_trace_flag():
    """Restaurant clamp should always leave an audit breadcrumb in calculation trace."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=1_000,
        location="Memphis, TN",
        project_class=ProjectClass.TENANT_IMPROVEMENT,
    )

    trace_steps = [entry["step"].lower() for entry in result["calculation_trace"]]
    assert any(step == "restaurant_cost_clamp" for step in trace_steps), "Restaurant clamp adjustments must be traceable"
