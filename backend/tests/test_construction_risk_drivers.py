import pytest

from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.construction_risk_drivers import build_construction_risk_drivers


def _get_driver(payload, driver_id):
    drivers = payload.get("construction_risk_drivers") or []
    return next((driver for driver in drivers if driver.get("id") == driver_id), None)


def _source_parts(driver):
    raw_source = driver.get("source") or ""
    return {part.strip() for part in str(raw_source).split(",") if part.strip()}


def test_construction_risk_driver_ties_follow_explicit_backend_priority():
    drivers = build_construction_risk_drivers(
        {
            "project_info": {
                "building_type": "healthcare",
                "subtype": "hospital",
                "location": "Austin, TX",
            },
            "construction_costs": {
                "construction_total": 1_000_000,
                "equipment_total": 120_000,
                "regional_multiplier": 1.10,
            },
            "soft_costs": {
                "contingency": 70_000,
            },
            "trade_breakdown": {
                "structural": 300_000,
                "mechanical": 300_000,
                "electrical": 200_000,
                "plumbing": 100_000,
                "finishes": 100_000,
            },
            "scope_items": [
                {
                    "trade": "Mechanical",
                    "systems": [
                        {
                            "name": "Central plant and redundant AHU package",
                            "total_cost": 100_000,
                        }
                    ],
                },
                {
                    "trade": "Structural",
                    "systems": [
                        {
                            "name": "Tower mat foundations and podium structure",
                            "total_cost": 80_000,
                        }
                    ],
                },
            ],
            "regional": {
                "location_display": "Austin, TX",
            },
        }
    )

    assert [driver["id"] for driver in drivers] == [
        "contingency_adequacy",
        "critical_systems_scope_burden",
        "trade_procurement_concentration",
        "regional_cost_pressure",
    ]


def test_calculate_project_emits_stage2_drivers_for_data_center():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.SPECIALTY,
        subtype="data_center",
        square_footage=120_000,
        location="San Francisco, CA",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
    )

    drivers = payload.get("construction_risk_drivers")

    assert isinstance(drivers, list) and len(drivers) == 4
    assert [driver["id"] for driver in drivers] == [
        "critical_systems_scope_burden",
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

    critical_driver = _get_driver(payload, "critical_systems_scope_burden")
    assert critical_driver is not None
    assert critical_driver["severity"] == "high"
    assert "Central Plant Chillers" in critical_driver["why_this_is_showing"]
    assert "Equipment allowance:" in critical_driver["evidence_summary"]
    assert critical_driver["source"] == "scope_items,construction_costs.equipment_total"

    trade_driver = _get_driver(payload, "trade_procurement_concentration")
    assert trade_driver is not None
    assert "Lead systems:" in trade_driver["evidence_summary"]
    assert "UPS, Switchgear + Distribution" in trade_driver["verify_next"]

    regional_driver = _get_driver(payload, "regional_cost_pressure")
    assert regional_driver is not None
    assert regional_driver["source"] == (
        "construction_costs.regional_multiplier,construction_costs.construction_total"
    )
    assert "Location-driven uplift:" in regional_driver["evidence_summary"]

    contingency_driver = _get_driver(payload, "contingency_adequacy")
    assert contingency_driver is not None
    assert "Equipment allowance:" in contingency_driver["evidence_summary"]
    assert {
        "soft_costs.contingency",
        "construction_costs.construction_total",
    }.issubset(_source_parts(contingency_driver))


def test_contingency_driver_keeps_adequacy_semantics_for_simple_restaurant_case():
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
    assert _source_parts(contingency_driver) == {
        "soft_costs.contingency",
        "construction_costs.construction_total",
    }


def test_contingency_driver_adds_optional_enrichment_sources_for_high_complexity_case():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.SPECIALTY,
        subtype="data_center",
        square_footage=120_000,
        location="San Francisco, CA",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
    )

    contingency_driver = _get_driver(payload, "contingency_adequacy")

    assert contingency_driver is not None
    assert {
        "soft_costs.contingency",
        "construction_costs.construction_total",
        "construction_costs.equipment_total",
        "scope_items",
    }.issubset(_source_parts(contingency_driver))
    assert "Equipment allowance:" in contingency_driver["evidence_summary"]


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
    assert "bid coverage" not in regional_driver["why_this_is_showing"]


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
            "scope_items": [
                {
                    "trade": "Structural",
                    "systems": [
                        {
                            "name": "Foundations and slab system",
                            "total_cost": 120_000,
                        }
                    ],
                },
                {
                    "trade": "Mechanical",
                    "systems": [
                        {
                            "name": "HVAC distribution and terminals",
                            "total_cost": 90_000,
                        }
                    ],
                },
            ],
        }
    )

    trade_driver = next(
        (driver for driver in drivers if driver["id"] == "trade_procurement_concentration"),
        None,
    )

    assert trade_driver is not None
    assert "limited number of packages" in trade_driver["why_this_is_showing"]
    assert "Lead systems:" in trade_driver["evidence_summary"]
    assert "bid coverage" not in trade_driver["verify_next"]
    assert "lead time" not in trade_driver["verify_next"].lower()
    assert "field condition" not in trade_driver["verify_next"].lower()
    assert (
        trade_driver["verify_next"]
        == "Pressure-test the current basis against Structural and Mechanical, especially Foundations and slab system and HVAC distribution and terminals, and confirm where scope definition or owner standards could still move."
    )


@pytest.mark.parametrize(
    "building_type, subtype, square_footage, location, special_features",
    [
        (BuildingType.HOSPITALITY, "limited_service_hotel", 80_000, "Nashville, TN", None),
        (BuildingType.MULTIFAMILY, "luxury_apartments", 120_000, "Dallas, TX", ["parking_garage"]),
    ],
)
def test_critical_systems_driver_omits_low_signal_families(
    building_type,
    subtype,
    square_footage,
    location,
    special_features,
):
    payload = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location=location,
        project_class=ProjectClass.GROUND_UP,
        floors=1,
        special_features=special_features,
    )

    assert _get_driver(payload, "critical_systems_scope_burden") is None


def test_critical_systems_driver_appears_for_selected_flex_case():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="flex_space",
        square_footage=90_000,
        location="Dallas, TX",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
        special_features=["clean_room"],
    )

    critical_driver = _get_driver(payload, "critical_systems_scope_burden")

    assert critical_driver is not None
    assert critical_driver["severity"] == "moderate"
    assert "Clean Room" in critical_driver["why_this_is_showing"]
    assert "scope_items,construction_costs.special_features_breakdown" == critical_driver["source"]


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
