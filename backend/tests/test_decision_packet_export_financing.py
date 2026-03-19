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


def test_packet_remaps_market_rate_multifamily_primary_control_label_for_export():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-export-market-rate-label",
    )
    project_payload = _build_project_payload(include_financing_summary=True)
    dealshield_view_model = _build_dealshield_view_model()
    dealshield_view_model["tile_profile_id"] = "multifamily_market_rate_apartments_v1"
    dealshield_view_model["primary_control_variable"] = {
        "label": "Structural Base Carry Proxy +5%",
        "impact_pct": 1.36,
        "severity": "Med",
    }
    dealshield_view_model["break_risk"] = {"level": "Medium"}
    dealshield_view_model["provenance"] = {
        "profile_id": "multifamily_market_rate_apartments_v1",
    }

    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        dealshield_view_model,
        "SpecSharp Capital",
    )

    html = render_decision_packet_html(packet)

    assert "Cost Basis Drift + Carry Risk" in html
    assert "Structural Base Carry Proxy +5%" not in html


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


def test_packet_preserves_structured_special_feature_metadata_for_launch_migration_rows():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=52_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-structured-special-feature-metadata",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        special_features_total=67_000,
        special_features_breakdown=[
            {
                "id": "breakfast_area",
                "label": "Breakfast Area",
                "pricing_basis": "AREA_SHARE_GSF",
                "pricing_status": "incremental",
                "configured_value": 20,
                "configured_area_share_of_gsf": 0.05,
                "applied_quantity": 2_600,
                "total_cost": 52_000,
            },
            {
                "id": "concierge",
                "label": "Concierge",
                "pricing_basis": "COUNT_BASED",
                "pricing_status": "incremental",
                "configured_value": 15_000,
                "configured_cost_per_count": 15_000,
                "applied_quantity": 1,
                "unit_label": "desk",
                "total_cost": 15_000,
            },
        ],
    )

    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "limited_service_hotel"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    rows = packet["construction_summary"]["special_features_breakdown"]
    rows_by_id = {row["id"]: row for row in rows}

    breakfast_area = rows_by_id["breakfast_area"]
    assert breakfast_area["pricing_basis"] == "AREA_SHARE_GSF"
    assert breakfast_area["applied_quantity"] == 2_600
    assert breakfast_area["configured_area_share_of_gsf"] == 0.05
    assert breakfast_area["display_pricing_status"] == "incremental"

    concierge = rows_by_id["concierge"]
    assert concierge["pricing_basis"] == "COUNT_BASED"
    assert concierge["applied_quantity"] == 1
    assert concierge["configured_cost_per_count"] == 15_000
    assert concierge["unit_label"] == "desk"
    assert concierge["display_pricing_status"] == "incremental"


def test_packet_renders_structured_special_feature_details_for_area_share_and_count_based_rows():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=52_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-structured-special-feature-html",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        special_features_total=82_000,
        special_features_breakdown=[
            {
                "id": "breakfast_area",
                "label": "Breakfast Area",
                "pricing_basis": "AREA_SHARE_GSF",
                "pricing_status": "incremental",
                "configured_value": 20,
                "configured_area_share_of_gsf": 0.05,
                "applied_quantity": 2_600,
                "total_cost": 52_000,
            },
            {
                "id": "digital_menu_boards",
                "label": "Digital Menu Boards",
                "pricing_basis": "COUNT_BASED",
                "pricing_status": "incremental",
                "configured_value": 15_000,
                "configured_cost_per_count": 15_000,
                "applied_quantity": 2,
                "unit_label": "board",
                "total_cost": 30_000,
            },
        ],
    )

    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "quick_service"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    html = render_decision_packet_html(packet)
    assert "Pricing Detail" in html
    assert "Basis: Area-share of project GSF" in html
    assert "$20.00 per feature-area SF × 2,600 SF assumed feature area" in html
    assert "Assumed feature area = 5% of project GSF" in html
    assert "Basis: Count-based" in html
    assert "$15,000 per board × 2 boards" in html


def test_packet_renders_count_overage_features_as_incremental_premiums_when_billed_quantity_exists():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="retail",
        square_footage=95_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-special-feature-overage-display",
    )
    project_payload = _build_project_payload(
        include_financing_summary=True,
        special_features_total=130_000,
        special_features_breakdown=[
            {
                "id": "loading_dock",
                "label": "Loading Dock",
                "pricing_basis": "COUNT_BASED",
                "pricing_status": "included_in_baseline",
                "count_pricing_mode": "overage_above_default",
                "configured_value": 65_000,
                "configured_cost_per_count": 65_000,
                "applied_quantity": 2,
                "requested_quantity": 4,
                "requested_quantity_source": "explicit_override:loading_dock_count",
                "included_baseline_quantity": 2,
                "billed_quantity": 2,
                "unit_label": "dock",
                "total_cost": 130_000,
            },
        ],
    )

    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "shopping_center"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    rows = packet["construction_summary"]["special_features_breakdown"]
    assert rows[0]["pricing_status"] == "included_in_baseline"
    assert rows[0]["display_pricing_status"] == "incremental"

    html = render_decision_packet_html(packet)
    assert "Incremental premium applied" in html
    assert "$65,000 per dock × 2 docks" in html
    assert "Baseline includes 2 docks" in html
    assert "You specified 4 docks" in html
    assert "Pricing includes 2 additional docks" in html


def test_packet_html_includes_shared_spacing_tokens_and_splits_packet_into_realistic_page_buckets():
    project = SimpleNamespace(
        name="Sunset Residences",
        location="Dallas, TX",
        building_type="multifamily",
        square_footage=12_000,
        total_cost=3_700_000,
        cost_per_sqft=308.33,
        project_id="proj-6",
    )
    project_payload = _build_project_payload(include_financing_summary=True)
    project_payload["calculation_data"]["construction_schedule"] = {
        "total_months": 18,
        "phases": [
            {"label": "Sitework", "start_month": 0, "duration_months": 3},
            {"label": "Structure", "start_month": 3, "duration_months": 6},
            {"label": "Interiors", "start_month": 9, "duration_months": 6},
            {"label": "Closeout", "start_month": 15, "duration_months": 3},
        ],
    }
    project_payload["calculation_data"]["construction_costs"]["cost_build_up"] = [
        {"label": "Regional Factor", "multiplier": 1.08},
        {"label": "Envelope Premium", "value_per_sf": 12.5},
    ]
    project_payload["calculation_data"]["trade_breakdown"] = {
        "structural": 1_100_000,
        "mechanical": 640_000,
        "electrical": 420_000,
    }

    packet = compose_decision_packet_input(
        project,
        project_payload,
        {"subtype": "market_rate_apartments"},
        _build_dealshield_view_model(),
        "SpecSharp Capital",
    )

    html = render_decision_packet_html(packet)

    assert ".subsection {" in html
    assert ".decision-table th, .decision-table td {" in html
    assert ".simple-table thead th {" in html
    assert ".schedule-layout {" in html
    assert "class=\"schedule-section\"" in html
    assert "class=\"simple-table schedule-table\"" in html
    assert "class=\"bullet-list milestone-list\"" in html

    page_breaks = []
    search_from = 0
    marker = '<div class="page page-break">'
    while True:
        next_break = html.find(marker, search_from)
        if next_break == -1:
            break
        page_breaks.append(next_break)
        search_from = next_break + 1

    assert len(page_breaks) == 5

    page_2 = html[page_breaks[0]:page_breaks[1]]
    page_3 = html[page_breaks[1]:page_breaks[2]]
    page_4 = html[page_breaks[2]:page_breaks[3]]
    page_5 = html[page_breaks[3]:page_breaks[4]]
    page_6 = html[page_breaks[4]:]

    assert "Key Metrics Strip" in page_2
    assert "Decision Insurance / Downside Summary" in page_2
    assert "Decision Metrics Table" in page_2
    assert "Financing Summary / What’s Not Modeled" not in page_2

    assert "Financing Summary / What’s Not Modeled" in page_3
    assert "Economics Snapshot" in page_3
    assert "Revenue Required to Hit Target Yield" not in page_3

    assert "Revenue Required to Hit Target Yield" in page_4
    assert "Construction Cost Summary" in page_4
    assert "Trade Distribution / Top Cost Drivers" in page_4
    assert "Schedule + Key Milestones" not in page_4

    assert "Schedule + Key Milestones" in page_5
    assert "Cost Build-Up Analysis" in page_5
    assert "Most Likely Wrong" in page_5
    assert "Question Bank" in page_5
    assert "Red Flags + Actions" in page_5

    assert "Provenance" in page_6
    assert "Most Likely Wrong" not in page_6
