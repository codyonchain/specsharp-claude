from types import SimpleNamespace
from typing import Optional

from app.services.decision_packet_export import (
    compose_decision_packet_input,
    render_decision_packet_html,
)


def _build_project_payload(
    include_financing_summary: bool,
    include_financing_assumptions: bool = False,
    *,
    special_features_total: Optional[float] = None,
    special_features_breakdown: Optional[list[dict]] = None,
) -> dict:
    calculation_data = {
        "project_info": {
            "building_type": "multifamily",
            "subtype": "market_rate_apartments",
        },
        "totals": {
            "total_project_cost": 3_700_000,
            "cost_per_sqft": 308.33,
        },
        "ownership_analysis": {
            "financing_sources": {
                "debt_amount": 2_400_000,
                "equity_amount": 1_300_000,
            },
            "debt_metrics": {
                "calculated_dscr": 1.46,
            },
            "return_metrics": {
                "estimated_annual_noi": 430_000,
            },
            "revenue_analysis": {
                "annual_revenue": 910_000,
            },
        },
        "construction_costs": {
            "construction_total": 3_100_000,
            "special_features_total": special_features_total,
            "special_features_breakdown": special_features_breakdown or [],
        },
    }
    if include_financing_summary:
        calculation_data["financing_summary"] = {
            "family_id": "lease_rent_market_rate",
            "family_label": "Lease / Rent Market-Rate",
            "items": [
                {"id": "debt_amount", "label": "Debt Amount", "value": 2_400_000, "format": "currency"},
                {"id": "equity_amount", "label": "Equity Amount", "value": 1_300_000, "format": "currency"},
                {"id": "debt_ratio", "label": "Debt Ratio", "value": 0.649, "format": "percentage", "decimals": 1},
                {"id": "calculated_dscr", "label": "Calculated DSCR", "value": 1.46, "format": "multiple", "decimals": 2},
            ],
        }
    if include_financing_assumptions:
        calculation_data["financing_assumptions"] = {
            "debt_amount": 2_400_000,
            "equity_amount": 1_300_000,
            "debt_ratio": 0.649,
            "debt_pct": 0.649,
            "interest_rate_pct": 0.058,
            "amort_years": 30,
            "loan_term_years": 10,
            "interest_only_months": 0,
            "annual_debt_service": 168_444.85,
            "monthly_debt_service": 14_037.07,
            "target_dscr": 1.20,
            "calculated_dscr": 1.46,
        }

    return {
        "project_name": "Sunset Residences",
        "name": "Sunset Residences",
        "location": "Dallas, TX",
        "building_type": "multifamily",
        "project_classification": "ground_up",
        "square_footage": 12_000,
        "request_data": {
            "square_footage": 12_000,
            "location": "Dallas, TX",
            "building_type": "multifamily",
        },
        "calculation_data": calculation_data,
    }


def _build_dealshield_view_model() -> dict:
    return {
        "decision_status": "Needs Work",
        "decision_reason_code": "low_dscr",
        "rendered_copy": {
            "decision_status_summary": "Coverage is tight relative to current basis.",
            "decision_status_detail": "Review basis and underwriting before advancing.",
            "policy_basis_line": "Policy basis: current modeled financing summary and coverage.",
        },
        "decision_summary": {},
        "content": {},
        "provenance": {},
        "decision_table": {
            "columns": [],
            "rows": [],
        },
        "dealshield_disclosures": [
            "Not modeled: financing assumptions missing",
            "DealShield scenarios stress cost/revenue assumptions only; schedule slippage or acceleration impacts (carry, debt timing, lease-up timing) are not modeled here.",
        ],
    }


def test_packet_uses_financing_summary_when_structured_assumptions_are_absent():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-1",
    )
    project_payload = _build_project_payload(include_financing_summary=True)
    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    assumptions_section = packet["assumptions_not_modeled"]
    assert assumptions_section["financing_summary"]["family_id"] == "lease_rent_market_rate"
    assert "Not modeled: financing assumptions missing" not in assumptions_section["disclosures"]

    html = render_decision_packet_html(packet)
    assert "Financing Summary / What" in html
    assert "Current Modeled Financing Summary" in html
    assert "Debt Amount" in html
    assert "$2,400,000" in html
    assert "Calculated DSCR" in html
    assert "Structured financing assumptions such as term, amortization, IO, and layered debt are not yet modeled." in html
    assert "No financing assumptions provided." not in html


def test_packet_keeps_legacy_assumptions_fallback_without_financing_summary():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-2",
    )
    project_payload = _build_project_payload(include_financing_summary=False)
    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    assumptions_section = packet["assumptions_not_modeled"]
    assert assumptions_section["financing_summary"] == {}
    assert "Not modeled: financing assumptions missing" in assumptions_section["disclosures"]

    html = render_decision_packet_html(packet)
    assert "Assumptions / What" in html
    assert "Current Modeled Financing Summary" not in html
    assert "No financing assumptions provided." in html


def test_packet_renders_structured_financing_assumptions_from_canonical_contract():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-3",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        include_financing_assumptions=True,
    )
    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    assumptions_section = packet["assumptions_not_modeled"]
    assert assumptions_section["financing_assumptions"]["amort_years"] == 30
    assert assumptions_section["financing_assumptions"]["loan_term_years"] == 10
    assert assumptions_section["financing_assumptions"]["interest_only_months"] == 0
    assert assumptions_section["financing_assumptions"]["annual_debt_service"] == 168_444.85
    assert assumptions_section["financing_assumptions"]["calculated_dscr"] == 1.46

    html = render_decision_packet_html(packet)
    assert "Structured Financing Assumptions" in html
    assert "Amortization" in html
    assert "30 yrs" in html
    assert "Loan Term" in html
    assert "10 yrs" in html
    assert "Annual Debt Service" in html
    assert "$168,445" in html
    assert "Calculated DSCR" in html
    assert "1.46x" in html
    assert "Structured financing assumptions such as term, amortization, IO, and layered debt are not yet modeled." not in html


def test_packet_renders_status_aware_special_feature_rows_for_mixed_selected_features():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-4",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        special_features_total=120_000,
        special_features_breakdown=[
            {
                "id": "ballroom",
                "label": "Ballroom",
                "pricing_status": "included_in_baseline",
                "configured_cost_per_sf": 50,
                "cost_per_sf": 0,
                "total_cost": 0,
            },
            {
                "id": "spa",
                "label": "Spa",
                "pricing_status": "incremental",
                "configured_cost_per_sf": 60,
                "cost_per_sf": 60,
                "total_cost": 120_000,
            },
        ],
    )
    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    construction_summary = packet["construction_summary"]
    assert construction_summary["special_features_total"] == 120_000
    assert len(construction_summary["special_features_breakdown"]) == 2

    html = render_decision_packet_html(packet)
    assert "Selected Special Features" in html
    assert "Ballroom" in html
    assert "Included in baseline" in html
    assert "Spa" in html
    assert "Incremental premium applied" in html
    assert "$120,000" in html


def test_packet_keeps_all_included_special_features_visible_when_applied_total_is_zero():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-5",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        special_features_total=0,
        special_features_breakdown=[
            {
                "id": "restaurant",
                "label": "Restaurant",
                "pricing_status": "included_in_baseline",
                "configured_cost_per_sf": 40,
                "cost_per_sf": 0,
                "total_cost": 0,
            },
            {
                "id": "conference_center",
                "label": "Conference Center",
                "pricing_status": "included_in_baseline",
                "configured_cost_per_sf": 45,
                "cost_per_sf": 0,
                "total_cost": 0,
            },
        ],
    )
    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    html = render_decision_packet_html(packet)
    assert "Selected Special Features" in html
    assert "Restaurant" in html
    assert "Conference Center" in html
    assert html.count("Included in baseline") >= 2
    assert "Special Features" in html
    assert "$0" in html
