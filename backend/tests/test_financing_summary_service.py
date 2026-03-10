import pytest

from app.v2.config.master_config import BuildingType, get_building_config
from app.v2.services.financing_summary_service import (
    HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID,
    HOSPITALITY_FAMILY_ID,
    LEASE_RENT_MARKET_RATE_FAMILY_ID,
    MIXED_USE_BLENDED_FAMILY_ID,
    OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID,
    SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID,
    build_financing_summary,
    resolve_financing_family,
)


def _build_payload(
    *,
    building_type: str,
    subtype: str,
    debt_amount: float = 2_400_000,
    equity_amount: float = 1_300_000,
    grants_amount: float = 0,
    philanthropy_amount: float = 0,
    total_project_cost: float = 3_700_000,
    annual_debt_service: float = 295_000,
    calculated_dscr: float = 1.46,
    target_dscr: float = 1.3,
    yield_on_cost: float = 0.116,
    market_cap_rate: float = 0.065,
    cap_rate_spread_bps: float = 510,
):
    return {
        "project_info": {
            "building_type": building_type,
            "subtype": subtype,
        },
        "totals": {
            "total_project_cost": total_project_cost,
        },
        "ownership_analysis": {
            "financing_sources": {
                "debt_amount": debt_amount,
                "equity_amount": equity_amount,
                "grants_amount": grants_amount,
                "philanthropy_amount": philanthropy_amount,
                "total_sources": debt_amount + equity_amount + grants_amount + philanthropy_amount,
            },
            "debt_metrics": {
                "annual_debt_service": annual_debt_service,
                "calculated_dscr": calculated_dscr,
                "target_dscr": target_dscr,
            },
            "yield_on_cost": yield_on_cost,
            "market_cap_rate": market_cap_rate,
            "cap_rate_spread_bps": cap_rate_spread_bps,
        },
    }


def _item_ids(summary):
    return [item["id"] for item in summary["items"]]


@pytest.mark.parametrize(
    ("building_type", "subtype", "ownership_type", "expected_family"),
    [
        ("multifamily", "market_rate_apartments", "for_profit", LEASE_RENT_MARKET_RATE_FAMILY_ID),
        ("hospitality", "limited_service_hotel", "for_profit", HOSPITALITY_FAMILY_ID),
        ("restaurant", "full_service", "for_profit", OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID),
        ("mixed_use", "urban_mixed", "for_profit", MIXED_USE_BLENDED_FAMILY_ID),
        ("parking", "parking_garage", "for_profit", HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID),
        ("multifamily", "affordable_housing", "non_profit", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        ("healthcare", "hospital", "non_profit", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        ("specialty", "self_storage", "for_profit", LEASE_RENT_MARKET_RATE_FAMILY_ID),
    ],
)
def test_resolve_financing_family_routes_key_building_families(
    building_type, subtype, ownership_type, expected_family
):
    payload = _build_payload(building_type=building_type, subtype=subtype)
    family_id = resolve_financing_family(
        payload,
        parsed_input={
            "building_type": building_type,
            "subtype": subtype,
            "ownership_type": ownership_type,
        },
    )

    assert family_id == expected_family


def test_build_financing_summary_keeps_market_rate_fields_that_are_safe_now():
    payload = _build_payload(
        building_type="multifamily",
        subtype="market_rate_apartments",
    )

    summary = build_financing_summary(
        payload,
        parsed_input={
            "building_type": "multifamily",
            "subtype": "market_rate_apartments",
            "ownership_type": "for_profit",
        },
    )

    assert summary["family_id"] == LEASE_RENT_MARKET_RATE_FAMILY_ID
    assert _item_ids(summary) == [
        "debt_amount",
        "equity_amount",
        "debt_ratio",
        "annual_debt_service",
        "calculated_dscr",
        "target_dscr",
        "yield_on_cost",
        "market_cap_rate",
        "cap_rate_spread_bps",
    ]


def test_build_financing_summary_hides_dscr_and_yield_fields_for_subsidized_family():
    payload = _build_payload(
        building_type="multifamily",
        subtype="affordable_housing",
        grants_amount=600_000,
        philanthropy_amount=350_000,
    )

    summary = build_financing_summary(
        payload,
        parsed_input={
            "building_type": "multifamily",
            "subtype": "affordable_housing",
            "ownership_type": "non_profit",
        },
    )

    assert summary["family_id"] == SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID
    assert _item_ids(summary) == [
        "debt_amount",
        "equity_amount",
        "grants_amount",
        "philanthropy_amount",
        "debt_ratio",
    ]


@pytest.mark.parametrize(
    ("building_type", "subtype", "expected_family"),
    [
        (BuildingType.MULTIFAMILY, "market_rate_apartments", LEASE_RENT_MARKET_RATE_FAMILY_ID),
        (BuildingType.MULTIFAMILY, "affordable_housing", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        (BuildingType.HOSPITALITY, "limited_service_hotel", HOSPITALITY_FAMILY_ID),
        (BuildingType.RESTAURANT, "full_service", OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID),
        (BuildingType.MIXED_USE, "transit_oriented", MIXED_USE_BLENDED_FAMILY_ID),
        (BuildingType.PARKING, "parking_garage", HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID),
        (BuildingType.HEALTHCARE, "hospital", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        (BuildingType.SPECIALTY, "self_storage", LEASE_RENT_MARKET_RATE_FAMILY_ID),
        (BuildingType.SPECIALTY, "laboratory", HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID),
        (BuildingType.INDUSTRIAL, "cold_storage", HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID),
        (BuildingType.CIVIC, "library", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        (BuildingType.EDUCATIONAL, "university", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
        (BuildingType.RECREATION, "fitness_center", SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID),
    ],
)
def test_building_config_declares_financing_presentation_family(
    building_type, subtype, expected_family
):
    config = get_building_config(building_type, subtype)

    assert config is not None
    assert config.financing_presentation_family == expected_family


def test_resolve_financing_family_prefers_explicit_config_over_old_ownership_heuristics():
    payload = _build_payload(
        building_type="specialty",
        subtype="laboratory",
    )

    family_id = resolve_financing_family(
        payload,
        parsed_input={
            "building_type": "specialty",
            "subtype": "laboratory",
            "ownership_type": "non_profit",
        },
    )

    assert family_id == HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID
