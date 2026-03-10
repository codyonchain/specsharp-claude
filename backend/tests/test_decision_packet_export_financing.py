from types import SimpleNamespace

from app.services.decision_packet_export import (
    compose_decision_packet_input,
    render_decision_packet_html,
)


def _build_project_payload(include_financing_summary: bool) -> dict:
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
