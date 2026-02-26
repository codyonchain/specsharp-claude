from app.services.pdf_export_service import ProfessionalPDFExportService


def _build_project_payload(feasible: bool, recommendation: str):
    return {
        "project_name": "Multifamily - Nashville, TN",
        "calculation_data": {
            "ownership_analysis": {
                "return_metrics": {
                    "estimated_annual_noi": 3218222.14,
                    "irr": 5.7,
                    "cash_on_cash_return": 5.6,
                    "property_value": 58513130,
                    "feasible": feasible,
                    "target_roi": 0.06,
                },
                "revenue_requirements": {
                    "feasibility": "feasible" if feasible else "not_feasible",
                    "feasibility_detail": {
                        "status": "Feasible" if feasible else "Not Feasible",
                        "recommendation": recommendation,
                    },
                },
                "debt_metrics": {
                    "calculated_dscr": 1.36,
                    "target_dscr": 1.25,
                },
                "financing_sources": {
                    "equity_amount": 14370510,
                },
            }
        },
        "total_cost": 57482040,
        "cost_per_sqft": 261.28,
    }


def _build_exec_summary():
    return {
        "project_overview": {
            "name": "Multifamily - Nashville, TN",
            "type": "Multifamily",
            "size": "220,000 SF",
            "location": "Nashville, TN",
        },
        "cost_summary": {
            "total_project_cost": "$57,482,040",
            "cost_per_sf": "$261/SF",
        },
        "major_systems": [],
        "risk_factors": [],
        "next_steps": [],
        "key_assumptions": [],
        "confidence_assessment": {},
    }


def test_project_pdf_prefers_canonical_dealshield_decision_when_available():
    service = ProfessionalPDFExportService()
    html = service._render_executive_overview_html(
        _build_project_payload(
            feasible=False,
            recommendation="Consider phased development or value engineering to reduce costs",
        ),
        _build_exec_summary(),
        None,
        {
            "decision_status": "GO",
            "decision_reason_code": "base_value_gap_positive",
            "decision_status_provenance": {
                "status_source": "dealshield_policy_v1",
                "policy_id": "dealshield_canonical_policy_v1",
            },
        },
    )

    assert 'class="badge go">GO<' in html
    assert "Policy source: dealshield_policy_v1 (dealshield_canonical_policy_v1) · reason: base_value_gap_positive" in html
    assert "Consider phased development or value engineering to reduce costs" not in html


def test_project_pdf_falls_back_to_feasibility_when_canonical_decision_missing():
    service = ProfessionalPDFExportService()
    recommendation = "Consider phased development or value engineering to reduce costs"
    html = service._render_executive_overview_html(
        _build_project_payload(feasible=False, recommendation=recommendation),
        _build_exec_summary(),
        None,
        None,
    )

    assert 'class="badge nogo">NO-GO<' in html
    assert recommendation in html

