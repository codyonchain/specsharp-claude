import math

import pytest

from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType, get_building_config
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.dealshield_service import build_dealshield_view_model


def _expected_payment_metrics(assumptions):
    debt_amount = assumptions["debt_amount"]
    interest_rate = assumptions["interest_rate_pct"]
    amort_months = int(assumptions["amort_years"] * 12)
    monthly_rate = interest_rate / 12
    if monthly_rate <= 0:
        monthly_payment = debt_amount / amort_months
    else:
        monthly_payment = debt_amount * monthly_rate / (1 - math.pow(1 + monthly_rate, -amort_months))
    return monthly_payment * 12, monthly_payment


@pytest.mark.parametrize(
    ("building_type", "subtype", "square_footage", "expected_amort", "expected_term", "expected_io"),
    [
        (BuildingType.MULTIFAMILY, "market_rate_apartments", 120_000, 30, 10, 0),
        (BuildingType.HOSPITALITY, "limited_service_hotel", 80_000, 25, 10, 12),
        (BuildingType.MIXED_USE, "retail_residential", 120_000, 30, 10, 0),
        (BuildingType.MIXED_USE, "office_residential", 120_000, 30, 10, 0),
        (BuildingType.MIXED_USE, "urban_mixed", 120_000, 30, 10, 0),
    ],
)
def test_rollout_subtypes_emit_structured_financing_assumptions_with_amortizing_debt_service(
    building_type, subtype, square_footage, expected_amort, expected_term, expected_io
):
    payload = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )

    assumptions = payload.get("financing_assumptions")
    assert isinstance(assumptions, dict)
    assert assumptions["amort_years"] == expected_amort
    assert assumptions["loan_term_years"] == expected_term
    assert assumptions["interest_only_months"] == expected_io

    expected_annual_debt_service, expected_monthly_debt_service = _expected_payment_metrics(assumptions)
    debt_metrics = payload["ownership_analysis"]["debt_metrics"]
    flat_proxy = assumptions["debt_amount"] * assumptions["interest_rate_pct"]
    actual_noi = payload["ownership_analysis"]["return_metrics"]["estimated_annual_noi"]
    expected_dscr = actual_noi / expected_annual_debt_service if expected_annual_debt_service else 0.0

    assert math.isclose(assumptions["annual_debt_service"], expected_annual_debt_service, rel_tol=1e-9)
    assert math.isclose(assumptions["monthly_debt_service"], expected_monthly_debt_service, rel_tol=1e-9)
    assert math.isclose(debt_metrics["annual_debt_service"], expected_annual_debt_service, rel_tol=1e-9)
    assert math.isclose(debt_metrics["monthly_debt_service"], expected_monthly_debt_service, rel_tol=1e-9)
    assert assumptions["annual_debt_service"] > flat_proxy
    assert math.isclose(debt_metrics["calculated_dscr"], expected_dscr, rel_tol=1e-9)
    assert math.isclose(assumptions["calculated_dscr"], expected_dscr, rel_tol=1e-9)
    assert math.isclose(assumptions["target_dscr"], debt_metrics["target_dscr"], rel_tol=1e-9)


@pytest.mark.parametrize(
    ("building_type", "subtype"),
    [
        (BuildingType.MULTIFAMILY, "market_rate_apartments"),
        (BuildingType.HOSPITALITY, "limited_service_hotel"),
    ],
)
def test_dealshield_view_model_adopts_structured_financing_assumptions_for_rollout_subtypes(
    building_type, subtype
):
    payload = unified_engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=100_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    config = get_building_config(building_type, subtype)
    profile = get_dealshield_profile(config.dealshield_tile_profile)

    view_model = build_dealshield_view_model(
        project_id=f"stage3a-{building_type.value}-{subtype}",
        payload=payload,
        profile=profile,
    )

    financing_assumptions = view_model.get("financing_assumptions")
    assert isinstance(financing_assumptions, dict)
    assert financing_assumptions["interest_rate_pct"] == payload["financing_assumptions"]["interest_rate_pct"]
    assert financing_assumptions["amort_years"] == payload["financing_assumptions"]["amort_years"]
    assert financing_assumptions["loan_term_years"] == payload["financing_assumptions"]["loan_term_years"]
    assert financing_assumptions["interest_only_months"] == payload["financing_assumptions"]["interest_only_months"]
    assert financing_assumptions["annual_debt_service"] == payload["financing_assumptions"]["annual_debt_service"]
    assert financing_assumptions["calculated_dscr"] == payload["financing_assumptions"]["calculated_dscr"]

    disclosures = view_model.get("dealshield_disclosures")
    assert isinstance(disclosures, list)
    assert "Not modeled: financing assumptions missing" not in disclosures


def test_non_rollout_subtypes_keep_flat_proxy_and_do_not_emit_structured_financing_assumptions():
    payload = unified_engine.calculate_project(
        building_type=BuildingType.RETAIL,
        subtype="shopping_center",
        square_footage=75_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
    )
    config = get_building_config(BuildingType.RETAIL, "shopping_center")
    terms = config.ownership_types[OwnershipType.FOR_PROFIT]
    debt_metrics = payload["ownership_analysis"]["debt_metrics"]
    debt_amount = payload["ownership_analysis"]["financing_sources"]["debt_amount"]

    assert "financing_assumptions" not in payload
    assert math.isclose(debt_metrics["annual_debt_service"], debt_amount * terms.debt_rate, rel_tol=1e-9)
