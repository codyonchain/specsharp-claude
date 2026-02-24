"""V2 healthcare calculation tests.

These tests validate the active healthcare path:
NLPService -> unified_engine -> V2 master_config-backed outputs.
"""

import pytest

from app.services.nlp_service import NLPService
from app.v2.config.master_config import (
    BuildingType,
    OwnershipType,
    ProjectClass,
    get_building_config,
)
from app.v2.engines.unified_engine import unified_engine


@pytest.fixture
def nlp_service():
    return NLPService()


def _calculate_healthcare(
    subtype: str,
    square_footage: int = 10000,
    location: str = "Nashville, TN",
    project_class: ProjectClass = ProjectClass.GROUND_UP,
    special_features=None,
):
    return unified_engine.calculate_project(
        building_type=BuildingType.HEALTHCARE,
        subtype=subtype,
        square_footage=square_footage,
        location=location,
        project_class=project_class,
        ownership_type=OwnershipType.FOR_PROFIT,
        special_features=special_features or [],
    )


@pytest.mark.parametrize(
    "description,expected_subtype",
    [
        ("New 50000 sf hospital addition in Manchester NH", "hospital"),
        ("Build 20000 sf outpatient clinic in Nashville", "outpatient_clinic"),
        ("New urgent care center 8000 square feet", "urgent_care"),
        ("15000 sf surgical center with 4 operating rooms", "surgical_center"),
        ("Dental office 5000 square feet", "dental_office"),
    ],
)
def test_nlp_detects_active_healthcare_subtypes(nlp_service, description, expected_subtype):
    parsed = nlp_service.extract_project_details(description)
    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == expected_subtype
    assert parsed["square_footage"] is not None
    assert parsed["location"] is not None


@pytest.mark.parametrize(
    "subtype",
    ["hospital", "outpatient_clinic", "urgent_care", "surgical_center", "medical_office_building", "dental_office"],
)
def test_engine_base_cost_matches_v2_config(subtype):
    cfg = get_building_config(BuildingType.HEALTHCARE, subtype)
    assert cfg is not None, f"Missing V2 config for subtype '{subtype}'"

    result = _calculate_healthcare(subtype=subtype)
    assert result["construction_costs"]["base_cost_per_sf"] == cfg.base_cost_per_sf
    assert result["project_info"]["building_type"] == "healthcare"
    assert result["project_info"]["subtype"] == subtype


def test_healthcare_equipment_is_soft_cost_not_hard_cost():
    result = _calculate_healthcare(subtype="hospital", square_footage=12000)

    equipment_total = result["construction_costs"]["equipment_total"]
    hard_costs = result["totals"]["hard_costs"]
    soft_costs = result["totals"]["soft_costs"]
    construction_total = result["construction_costs"]["construction_total"]
    special_features_total = result["construction_costs"]["special_features_total"]

    assert equipment_total > 0
    assert "medical_equipment" in result["soft_costs"]
    assert result["soft_costs"]["medical_equipment"] == pytest.approx(equipment_total, rel=0, abs=1e-6)
    assert hard_costs == pytest.approx(construction_total + special_features_total, rel=0, abs=1e-6)
    assert soft_costs == pytest.approx(sum(result["soft_costs"].values()), rel=0, abs=1e-6)


def test_hospital_trade_breakdown_matches_config_percentages():
    cfg = get_building_config(BuildingType.HEALTHCARE, "hospital")
    assert cfg is not None

    result = _calculate_healthcare(subtype="hospital", square_footage=20000)
    construction_total = result["construction_costs"]["construction_total"]
    trades = result["trade_breakdown"]

    assert construction_total > 0
    assert trades["mechanical"] == pytest.approx(construction_total * cfg.trades.mechanical, rel=0, abs=1e-6)
    assert trades["electrical"] == pytest.approx(construction_total * cfg.trades.electrical, rel=0, abs=1e-6)
    assert trades["plumbing"] == pytest.approx(construction_total * cfg.trades.plumbing, rel=0, abs=1e-6)
    assert trades["finishes"] == pytest.approx(construction_total * cfg.trades.finishes, rel=0, abs=1e-6)

    trade_sum = sum(trades.values())
    assert trade_sum == pytest.approx(construction_total, rel=0, abs=1e-6)


def test_project_class_multipliers_order_total_cost_per_sf():
    ground_up = _calculate_healthcare("hospital", project_class=ProjectClass.GROUND_UP)
    addition = _calculate_healthcare("hospital", project_class=ProjectClass.ADDITION)
    renovation = _calculate_healthcare("hospital", project_class=ProjectClass.RENOVATION)

    ground_up_psf = ground_up["totals"]["cost_per_sf"]
    addition_psf = addition["totals"]["cost_per_sf"]
    renovation_psf = renovation["totals"]["cost_per_sf"]

    assert addition_psf > ground_up_psf > renovation_psf


def test_special_features_increase_hard_costs_for_hospital():
    square_footage = 10000
    no_features = _calculate_healthcare(
        subtype="hospital",
        square_footage=square_footage,
        special_features=[],
    )
    with_features = _calculate_healthcare(
        subtype="hospital",
        square_footage=square_footage,
        special_features=["emergency_department", "icu"],
    )

    expected_feature_cost = square_footage * (50 + 60)

    assert with_features["construction_costs"]["special_features_total"] == pytest.approx(
        expected_feature_cost, rel=0, abs=1e-6
    )
    assert with_features["totals"]["hard_costs"] > no_features["totals"]["hard_costs"]
    assert with_features["totals"]["total_project_cost"] > no_features["totals"]["total_project_cost"]


def test_outpatient_profile_emits_facility_metrics():
    result = _calculate_healthcare(subtype="urgent_care", square_footage=9000)
    cfg = get_building_config(BuildingType.HEALTHCARE, "urgent_care")
    assert cfg is not None

    metrics = result.get("facility_metrics")
    assert metrics is not None
    assert metrics["type"] == "healthcare"
    assert metrics["unit_label"] == cfg.financial_metrics["primary_unit"]
    assert metrics["units"] >= 1
    assert metrics["revenue_per_unit"] == cfg.financial_metrics["revenue_per_unit_annual"]
