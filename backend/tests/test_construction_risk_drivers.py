import pytest

from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.construction_risk_drivers import build_construction_risk_drivers


def _get_driver(payload, driver_id):
    drivers = payload.get("construction_risk_drivers") or []
    return next((driver for driver in drivers if driver.get("id") == driver_id), None)


def test_construction_risk_driver_ties_follow_explicit_backend_priority():
    drivers = build_construction_risk_drivers(
        {
            "construction_costs": {
                "construction_total": 1_000_000,
                "regional_multiplier": 1.10,
            },
            "soft_costs": {
                "contingency": 70_000,
            },
            "trade_breakdown": {
                "structural": 300_000,
                "mechanical": 300_000,
                "electrical": 150_000,
                "plumbing": 150_000,
                "finishes": 100_000,
            },
            "regional": {
                "location_display": "Austin, TX",
            },
            "project_info": {
                "location": "Austin, TX",
            },
        }
    )

    assert [driver["id"] for driver in drivers] == [
        "contingency_adequacy",
        "trade_procurement_concentration",
        "regional_cost_pressure",
    ]


def test_calculate_project_emits_ranked_construction_risk_drivers():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.SPECIALTY,
        subtype="data_center",
        square_footage=120_000,
        location="San Francisco, CA",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
    )

    drivers = payload.get("construction_risk_drivers")

    assert isinstance(drivers, list) and len(drivers) == 3
    assert [driver["id"] for driver in drivers] == [
        "trade_procurement_concentration",
        "regional_cost_pressure",
        "contingency_adequacy",
    ]

    for driver in drivers:
        assert driver["status"] == "supported"
        assert driver["severity"] in {"low", "moderate", "high"}
        assert isinstance(driver["affects"], list) and driver["affects"]
        assert isinstance(driver["why_this_is_showing"], str) and driver["why_this_is_showing"]
        assert isinstance(driver["verify_next"], str) and driver["verify_next"]
        assert isinstance(driver["evidence_summary"], str) and driver["evidence_summary"]

    regional_driver = _get_driver(payload, "regional_cost_pressure")
    assert regional_driver is not None
    assert regional_driver["source"] == "construction_costs.regional_multiplier"
    assert regional_driver["severity"] == "high"


def test_contingency_driver_uses_adequacy_semantics_not_inverted_risk():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
    )

    contingency_driver = _get_driver(payload, "contingency_adequacy")

    assert contingency_driver is not None
    assert contingency_driver["severity"] == "high"
    assert "5.0% of core construction" in contingency_driver["why_this_is_showing"]
    assert contingency_driver["title"] == "Contingency Adequacy"


def test_regional_driver_reports_actual_fallback_source_path():
    drivers = build_construction_risk_drivers(
        {
            "construction_costs": {},
            "regional": {
                "multiplier": 1.10,
                "location_display": "Austin, TX",
            },
            "project_info": {
                "location": "Austin, TX",
            },
        }
    )

    regional_driver = next(
        (driver for driver in drivers if driver["id"] == "regional_cost_pressure"),
        None,
    )

    assert regional_driver is not None
    assert regional_driver["source"] == "regional.multiplier"
    assert regional_driver["severity"] == "moderate"


def test_trade_driver_wording_stays_at_package_concentration_level():
    drivers = build_construction_risk_drivers(
        {
            "construction_costs": {
                "construction_total": 1_000_000,
            },
            "trade_breakdown": {
                "structural": 300_000,
                "mechanical": 300_000,
                "electrical": 150_000,
                "plumbing": 150_000,
                "finishes": 100_000,
            },
        }
    )

    trade_driver = next(
        (driver for driver in drivers if driver["id"] == "trade_procurement_concentration"),
        None,
    )

    assert trade_driver is not None
    assert "limited number of packages" in trade_driver["why_this_is_showing"]
    assert "bid coverage" not in trade_driver["verify_next"]
    assert "release timing" not in trade_driver["verify_next"]
    assert (
        trade_driver["verify_next"]
        == "Pressure-test the current basis against Structural and Mechanical and confirm where scope definition or pricing could still move."
    )


def test_regional_driver_uses_cost_side_multiplier_not_market_factor_semantics():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="full_service",
        square_footage=8_000,
        location="Dallas, TX",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
    )

    assert payload["construction_costs"]["regional_multiplier"] == pytest.approx(0.97)
    assert payload["modifiers"]["market_factor"] == pytest.approx(1.03)
    assert _get_driver(payload, "regional_cost_pressure") is None
