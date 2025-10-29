import pytest

from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import BuildingType, ProjectClass


GOLDEN_CASES = [
    {
        "case": "A",
        "description": "5,000 sf full service restaurant in Nashville, TN",
        "square_footage": 5_000,
        "location": "Nashville, TN",
        "expected": {
            "total_cost": 2_464_645.00,
            "total_revenue": 1_751_000.00,
            "noi": 140_080.00,
            "roi": 5.68,
            "payback": 17.6,
            "cost_multiplier": 1.03,
            "revenue_multiplier": 1.03,
        },
    },
    {
        "case": "B",
        "description": "50,000 sf class A office in Nashville, TN",
        "square_footage": 50_000,
        "location": "Nashville, TN",
        "expected": {
            "total_cost": 15_234_375.00,
            "total_revenue": 1_903_440.00,
            "noi": 761_376.00,
            "roi": 5.00,
            "payback": 20.0,
            "cost_multiplier": 1.03,
            "revenue_multiplier": 1.03,
        },
    },
    {
        "case": "C",
        "description": "75,000 sf warehouse with 10 percent office in Nashville, TN",
        "square_footage": 75_000,
        "location": "Nashville, TN",
        "expected": {
            "total_cost": 8_156_006.25,
            "total_revenue": 580_920.00,
            "noi": 232_368.00,
            "roi": 2.85,
            "payback": 35.1,
            "cost_multiplier": 1.03,
            "revenue_multiplier": 1.03,
        },
    },
    {
        "case": "D",
        "description": "65,000 sf middle school for 800 students in Bedford, NH",
        "square_footage": 65_000,
        "location": "Bedford, NH",
        "expected": {
            "total_cost": 26_244_725.00,
            "total_revenue": None,
            "noi": None,
            "roi": None,
            "payback": None,
            "cost_multiplier": 1.00,
            "revenue_multiplier": None,
        },
    },
    {
        "case": "E",
        "description": "120,000 sf warehouse with twenty four docks in La Vergne, TN",
        "square_footage": 120_000,
        "location": "La Vergne, TN",
        "expected": {
            "total_cost": 12_687_000.00,
            "total_revenue": 902_400.00,
            "noi": 360_960.00,
            "roi": 2.85,
            "payback": 35.1,
            "cost_multiplier": 1.00,
            "revenue_multiplier": 1.00,
        },
    },
]


@pytest.mark.parametrize("case_data", GOLDEN_CASES, ids=[c["case"] for c in GOLDEN_CASES])
def test_revenue_golden_cases(case_data):
    """Golden-case regression guardrails for TN / NH focus projects."""
    description = case_data["description"]
    square_footage = case_data["square_footage"]
    location = case_data["location"]
    expected = case_data["expected"]

    result = unified_engine.estimate_from_description(
        description=description,
        square_footage=square_footage,
        location=location,
    )

    totals = result["totals"]
    revenue = result["revenue_analysis"]
    returns = result["return_metrics"]

    assert totals["total_project_cost"] == pytest.approx(expected["total_cost"], rel=1e-3)

    if expected["total_revenue"] is None:
        assert revenue.get("annual_revenue") in (None, 0), "Expected no revenue projection for civic/education cases"
    else:
        assert revenue.get("annual_revenue") == pytest.approx(expected["total_revenue"], rel=1e-3)

    if expected["noi"] is None:
        assert revenue.get("net_income") in (None, 0), "Expected no NOI when revenue is missing"
    else:
        assert revenue.get("net_income") == pytest.approx(expected["noi"], rel=1e-3)

    if expected["roi"] is None:
        assert returns.get("cash_on_cash_return") in (None, 0), "ROI should be absent when revenue is not modelled"
    else:
        assert returns.get("cash_on_cash_return") == pytest.approx(expected["roi"], rel=1e-2)

    if expected["payback"] is None:
        assert returns.get("payback_period") in (None, 0), "Payback should be absent when ROI is not available"
    else:
        assert returns.get("payback_period") == pytest.approx(expected["payback"], rel=1e-2)

    cost_multiplier = result["construction_costs"]["regional_multiplier"]
    assert cost_multiplier == pytest.approx(expected["cost_multiplier"], rel=1e-3)

    revenue_multiplier = revenue.get("regional_multiplier")
    if expected["revenue_multiplier"] is None:
        assert revenue_multiplier in (None, 0), "Expected revenue multiplier to be absent"
    else:
        assert revenue_multiplier is not None, "Revenue calculations must expose an explicit regional multiplier"
        assert revenue_multiplier == pytest.approx(expected["revenue_multiplier"], rel=1e-3)


def test_city_only_location_warns_and_defaults():
    """Locations without state metadata must fall back to 1.0 and flag the issue."""
    result = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=5_000,
        location="Nashville",
        project_class=ProjectClass.GROUND_UP,
    )

    multiplier = result["construction_costs"]["regional_multiplier"]
    assert multiplier == pytest.approx(1.03), "City-only locations should follow configured override when available"

    trace_steps = " | ".join(entry["step"] for entry in result["calculation_trace"])
    trace_payload = " | ".join(str(entry["data"]) for entry in result["calculation_trace"])
    combined_trace = f"{trace_steps} | {trace_payload}".lower()
    assert "warning" in combined_trace or "city-only" in combined_trace, "City-only location must record a warning in calculation trace"
