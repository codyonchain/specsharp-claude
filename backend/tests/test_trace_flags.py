from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import BuildingType, ProjectClass


def test_nashville_override_emits_trace_flag():
    """
    Nashville city-only resolution should be visible in active trace/metadata outputs.
    """
    result = unified_engine.calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=20_000,
        location="Nashville",  # Triggers hard-coded override
        project_class=ProjectClass.GROUND_UP,
    )

    trace_steps = [entry["step"].lower() for entry in result["calculation_trace"]]
    assert "modifiers_applied" in trace_steps, "Modifier resolution must be surfaced in calculation trace"
    assert result["regional"]["source"] == "city_inferred", "City-only Nashville input must resolve through inferred city metadata"
    assert result["regional_applied"] is True, "Regional metadata payload must remain enabled in result contract"


def test_restaurant_clamp_emits_trace_flag():
    """Clamp trace should appear only when restaurant cost-per-sf is forced to clamp bounds."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="quick_service",
        square_footage=1_000,
        location="Memphis, TN",
        project_class=ProjectClass.TENANT_IMPROVEMENT,
    )

    trace_steps = [entry["step"].lower() for entry in result["calculation_trace"]]
    total_cost_per_sf = result["totals"]["cost_per_sf"]
    assert 250 <= total_cost_per_sf <= 700, "Fixture should stay within configured quick-service clamp band"
    assert all(step != "restaurant_cost_clamp" for step in trace_steps), "Clamp trace should only appear when a clamp adjustment is applied"
