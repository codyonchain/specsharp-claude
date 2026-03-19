import pytest

from app.services.nlp_service import NLPService
from app.v2.config.master_config import (
    BuildingType,
    OwnershipType,
    ProjectClass,
    get_building_config,
    get_effective_modifiers,
)
from app.v2.engines.unified_engine import unified_engine


ANCHOR_DESCRIPTION = (
    "New 160,000 SF Class A office tower with conference center, fitness center, "
    "rooftop terrace, concierge lobby, and executive floor in Nashville, TN"
)


def _expected_office_economics(
    subtype: str,
    square_footage: int,
    location: str,
    finish_level=None,
):
    config = get_building_config(BuildingType.OFFICE, subtype)
    assert config is not None

    profile = dict(config.financial_metrics or {})
    sf = float(square_footage)
    rent_pgi = float(profile["base_rent_per_sf"]) * sf * float(profile["stabilized_occupancy"])
    vacancy_and_credit_loss = float(profile["vacancy_and_credit_loss_pct"]) * rent_pgi
    rent_egi = rent_pgi - vacancy_and_credit_loss

    recoverable_cam = float(getattr(config, "cam_charges_per_sf", 0.0) or 0.0) * sf
    opex = float(profile["opex_pct_of_egi"]) * rent_egi
    ti_amort = (float(profile["ti_per_sf"]) * sf) / int(profile["ti_amort_years"])
    lc_amort = (
        float(profile["lc_pct_of_lease_value"]) * rent_pgi * 10.0 / int(profile["lc_amort_years"])
    )
    revenue_factor = float(
        get_effective_modifiers(BuildingType.OFFICE, subtype, finish_level, location)["revenue_factor"]
    )
    annual_revenue = (rent_egi * revenue_factor) + recoverable_cam
    operating_expenses = (opex + ti_amort + lc_amort) * revenue_factor
    net_income = annual_revenue - operating_expenses

    return {
        "recoverable_cam": round(recoverable_cam, 2),
        "annual_revenue": round(annual_revenue, 2),
        "operating_expenses": round(operating_expenses, 2),
        "net_income": round(net_income, 2),
    }


@pytest.fixture(scope="module")
def nlp_parser() -> NLPService:
    return NLPService()


def test_fitness_word_does_not_trigger_tenant_improvement_for_office_tower(
    nlp_parser: NLPService,
):
    parsed = nlp_parser.extract_project_details(ANCHOR_DESCRIPTION)
    result = unified_engine.estimate_from_description(
        description=ANCHOR_DESCRIPTION,
        square_footage=160_000,
        location="Nashville, TN",
    )

    detection_info = result.get("detection_info") or {}
    project_info = result.get("project_info") or {}

    assert parsed["building_type"] == "office"
    assert parsed["subtype"] == "class_a"
    assert detection_info.get("detected_class") == "ground_up"
    assert project_info.get("project_class") == "ground_up"


def test_office_tower_description_preserves_parsed_floors_in_calculation(
    nlp_parser: NLPService,
):
    parsed = nlp_parser.extract_project_details(ANCHOR_DESCRIPTION)
    result = unified_engine.estimate_from_description(
        description=ANCHOR_DESCRIPTION,
        square_footage=160_000,
        location="Nashville, TN",
    )

    project_info = result.get("project_info") or {}
    construction_costs = result.get("construction_costs") or {}

    assert parsed["floors"] == 10
    assert project_info.get("floors") == parsed["floors"]
    assert construction_costs.get("base_cost_per_sf") == pytest.approx(
        construction_costs.get("original_base_cost_per_sf") * 1.10,
        rel=0,
        abs=1e-9,
    )


def test_class_a_office_cam_is_monetized_into_revenue_and_noi():
    square_footage = 120_000
    location = "Nashville, TN"
    expected = _expected_office_economics("class_a", square_footage, location)
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_a",
        square_footage=square_footage,
        location=location,
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT,
    )

    revenue = result.get("revenue_analysis") or {}
    operating_efficiency = result.get("operational_efficiency") or {}
    return_metrics = result.get("return_metrics") or {}

    assert revenue.get("cam_charges") == pytest.approx(expected["recoverable_cam"], abs=0.01)
    assert operating_efficiency.get("cam_charges") == pytest.approx(expected["recoverable_cam"], abs=0.01)
    assert revenue.get("annual_revenue") == pytest.approx(expected["annual_revenue"], abs=0.01)
    assert revenue.get("operating_expenses") == pytest.approx(expected["operating_expenses"], abs=0.01)
    assert revenue.get("net_income") == pytest.approx(expected["net_income"], abs=0.01)
    assert return_metrics.get("estimated_annual_noi") == pytest.approx(expected["net_income"], abs=0.01)


def test_class_a_anchor_description_path_monetizes_cam_and_remains_no_go():
    location = "Nashville, TN"
    square_footage = 160_000
    result = unified_engine.estimate_from_description(
        description=ANCHOR_DESCRIPTION,
        square_footage=square_footage,
        location=location,
    )

    project_info = result.get("project_info") or {}
    revenue = result.get("revenue_analysis") or {}
    operating_efficiency = result.get("operational_efficiency") or {}
    return_metrics = result.get("return_metrics") or {}
    expected = _expected_office_economics(
        "class_a",
        square_footage,
        location,
        finish_level=project_info.get("finish_level"),
    )

    assert project_info.get("subtype") == "class_a"
    assert revenue.get("cam_charges") == pytest.approx(expected["recoverable_cam"], abs=0.01)
    assert operating_efficiency.get("cam_charges") == pytest.approx(expected["recoverable_cam"], abs=0.01)
    assert revenue.get("annual_revenue") == pytest.approx(expected["annual_revenue"], abs=0.01)
    assert revenue.get("net_income") == pytest.approx(expected["net_income"], abs=0.01)
    assert return_metrics.get("estimated_annual_noi") == pytest.approx(expected["net_income"], abs=0.01)
    assert return_metrics.get("feasible") is False


def test_class_b_office_remains_rent_only_without_cam():
    square_footage = 95_000
    location = "Nashville, TN"
    expected = _expected_office_economics("class_b", square_footage, location)
    result = unified_engine.calculate_project(
        building_type=BuildingType.OFFICE,
        subtype="class_b",
        square_footage=square_footage,
        location=location,
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT,
    )

    revenue = result.get("revenue_analysis") or {}
    operating_efficiency = result.get("operational_efficiency") or {}
    return_metrics = result.get("return_metrics") or {}

    assert expected["recoverable_cam"] == 0.0
    assert revenue.get("cam_charges") == pytest.approx(0.0, abs=0.01)
    assert operating_efficiency.get("cam_charges") == pytest.approx(0.0, abs=0.01)
    assert revenue.get("annual_revenue") == pytest.approx(expected["annual_revenue"], abs=0.01)
    assert revenue.get("net_income") == pytest.approx(expected["net_income"], abs=0.01)
    assert return_metrics.get("estimated_annual_noi") == pytest.approx(expected["net_income"], abs=0.01)
