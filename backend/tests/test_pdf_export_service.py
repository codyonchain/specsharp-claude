import io
import logging
from types import SimpleNamespace
from typing import List, Optional

import pytest
from PIL import Image, ImageDraw

from app.services.decision_packet_export import (
    render_decision_packet_html,
    sanitize_decision_packet_export,
)
from app.services import pdf_export_service as pdf_export_service_module
from app.services.pdf_export_service import PDFRenderError, ProfessionalPDFExportService
from app.v2.api import scope as scope_module


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


def _build_unsafe_decision_packet():
    return {
        "cover_summary": {
            "project_name": "Nashville Market Apartments",
            "client_name": "SpecSharp Capital",
            "location": "Nashville, TN",
            "building_type": "multifamily",
            "building_type_label": "Multifamily",
            "subtype": "market_rate_apartments",
            "subtype_label": "Market Rate Apartments",
            "project_classification": "ground_up",
            "square_footage": 250_000,
            "generated_at": "March 25, 2026",
        },
        "decision_banner": {
            "decision_status": "GO",
            "decision_reason_code": "base_value_gap_positive",
            "summary": "The current base case clears the modeled downside screen.",
            "detail": "Base and downside cases remain within the current underwriting guardrails.",
            "policy_basis_line": "Policy basis: DealShield canonical policy.",
        },
        "key_metrics": {
            "total_project_cost": 57_482_040,
            "yield_on_cost": 0.061,
            "dscr": 1.36,
            "annual_revenue": 8_400_000,
            "annual_noi": 3_218_222,
        },
        "decision_insurance": {
            "primary_control_variable": {
                "id": "tile_structural_base_carry_proxy",
                "label": "Structural Base Carry Proxy +5%",
                "impact_pct": 1.36,
                "severity": "Medium",
                "driver_tile_id": "tile_47",
            },
            "first_break_condition": {
                "summary_text": "Ugly downside compresses NOI below threshold.",
                "scenario_label": "Ugly",
                "scenario_id": "ugly",
                "observed_value": -250_000,
                "operator": "<",
                "threshold_value": 0,
            },
            "flex_before_break_pct": 0.064,
            "flex_before_break_band": "Moderate",
            "exposure_concentration_pct": 0.32,
            "break_risk": {
                "level": "Medium",
                "source": "decision_insurance.break_risk",
            },
            "ranked_likely_wrong": [
                {
                    "id": "tile_90",
                    "text": "Garage parking pricing could be light.",
                    "why": "Current rent premium assumes strong garage uptake.",
                    "driver_tile_id": "tile_90",
                    "impact_pct": 0.18,
                    "severity": "High",
                }
            ],
            "unavailable_notes": [
                "insufficient_break_risk_inputs",
            ],
            "provenance": {
                "driver_impact_source": "decision_insurance.primary_control_variable.driver_impacts",
            },
        },
        "decision_metrics_table": {
            "columns": [
                {
                    "id": "col_total_cost",
                    "label": "Total Cost",
                    "metric_ref": "totals.total_project_cost",
                },
                {
                    "id": "col_revenue",
                    "label": "Annual Revenue",
                    "metric_ref": "revenue_analysis.annual_revenue",
                },
            ],
            "rows": [
                {
                    "scenario_id": "base",
                    "cells": [
                        {"col_id": "col_total_cost", "value": 57_482_040},
                        {"col_id": "col_revenue", "value": 8_400_000},
                    ],
                },
                {
                    "scenario_id": "ugly",
                    "cells": [
                        {"col_id": "col_total_cost", "value": 60_356_142},
                        {"col_id": "col_revenue", "value": 7_476_000},
                    ],
                },
            ],
        },
        "assumptions_not_modeled": {
            "financing_summary": {
                "items": [
                    {"id": "debt_amount", "label": "Debt Amount", "value": 39_100_000, "format": "currency"},
                    {"id": "calculated_dscr", "label": "Calculated DSCR", "value": 1.36, "format": "multiple", "decimals": 2},
                ],
            },
            "financing_assumptions": {
                "debt_pct": 0.68,
                "interest_rate_pct": 0.061,
                "amort_years": 30,
                "loan_term_years": 10,
                "interest_only_months": 12,
                "annual_debt_service": 2_120_000,
                "monthly_debt_service": 176_667,
                "target_dscr": 1.25,
                "calculated_dscr": 1.36,
                "metric_refs_used": ["debt_metrics.calculated_dscr"],
            },
            "disclosures": [
                "Scenario comparisons pressure-test cost and revenue assumptions only.",
            ],
            "decision_summary": {
                "not_modeled_reason": "Construction delay impacts are not modeled in this packet.",
            },
            "not_modeled_reason": "Construction delay impacts are not modeled in this packet.",
        },
        "economics_snapshot": {
            "total_project_cost": 57_482_040,
            "cost_per_sqft": 229.93,
            "annual_revenue": 8_400_000,
            "annual_noi": 3_218_222,
            "yield_on_cost": 0.056,
            "dscr": 1.36,
            "property_value": 61_500_000,
            "target_yield": 0.06,
        },
        "revenue_required": {
            "target_yield": 0.06,
            "operating_margin": 0.38,
            "required_noi": 3_448_922,
            "current_noi": 3_218_222,
            "noi_gap": -230_700,
            "required_annual_revenue": 9_076_111,
            "current_annual_revenue": 8_400_000,
            "revenue_gap": -676_111,
            "required_revenue_per_sf": 36.30,
            "current_revenue_per_sf": 33.60,
        },
        "construction_summary": {
            "hard_costs": 41_000_000,
            "soft_costs": 8_200_000,
            "construction_total": 49_200_000,
            "total_project_cost": 57_482_040,
            "cost_per_sqft": 229.93,
            "special_features_total": 3_000_000,
            "special_features_breakdown": [
                {
                    "id": "garage_parking",
                    "label": "Garage Parking",
                    "pricing_basis": "COUNT_BASED",
                    "pricing_status": "included_in_baseline",
                    "count_pricing_mode": "overage_above_default",
                    "configured_cost_per_count": 25_000,
                    "applied_quantity": 120,
                    "requested_quantity": 220,
                    "requested_quantity_source": "explicit_override:garage_stall_count",
                    "included_baseline_quantity": 100,
                    "billed_quantity": 120,
                    "unit_label": "stall",
                    "total_cost": 3_000_000,
                }
            ],
        },
        "trade_distribution": {
            "items": [
                {"id": "structural_trade", "label": "Structure", "amount": 12_000_000, "percent": 0.29},
                {"id": "mep_trade", "label": "MEP", "amount": 8_600_000, "percent": 0.21},
            ],
        },
        "cost_build_up": {
            "items": [
                {"id": "regional_factor", "label": "Regional Factor", "multiplier": 1.08},
                {"id": "envelope_premium", "label": "Envelope Premium", "value_per_sf": 12.5},
            ],
        },
        "schedule_milestones": {
            "total_months": 24,
            "phases": [
                {"id": "sitework", "label": "Sitework", "start_month": 0, "duration_months": 3},
                {"id": "structure", "label": "Structure", "start_month": 3, "duration_months": 8},
            ],
            "milestones": [
                {"id": "vertical_complete", "label": "Vertical Complete", "date_label": "Month 12"},
            ],
        },
        "trust_sections": {
            "most_likely_wrong": [
                {
                    "id": "tile_park_rev",
                    "text": "Garage parking pricing could be light.",
                    "why": "Current rent premium assumes strong garage uptake.",
                    "driver_tile_id": "tile_90",
                }
            ],
            "question_bank": [
                {
                    "id": "qb_rev_01",
                    "driver_tile_id": "tile_90",
                    "questions": [
                        "Validate achievable garage rent premiums with recent comps.",
                    ],
                }
            ],
            "red_flags_actions": [
                {
                    "flag": "Lease-up pace is tight.",
                    "action": "Confirm absorption and concession assumptions with current comps.",
                }
            ],
        },
        "provenance": {
            "profile_id": "multifamily_market_rate_apartments_v1",
            "content_profile_id": "multifamily_market_rate_content_v3",
            "scope_items_profile_id": "scope_packet_v2",
            "decision_status": "GO",
            "decision_reason_code": "base_value_gap_positive",
            "decision_status_provenance": {
                "status_source": "canonical_policy",
                "policy_id": "decision_insurance_subtype_policy_v1",
            },
            "scenario_inputs": {
                "base": {
                    "scenario_label": "Base",
                    "applied_tile_ids": [],
                    "applied_lever_labels": [],
                    "stress_band_pct": 10,
                    "cost_anchor_used": True,
                    "cost_anchor_value": 57_482_040,
                    "revenue_anchor_used": False,
                    "revenue_anchor_value": None,
                    "explain": {
                        "short": "Base scenario (no profile levers applied; financials recomputed).",
                        "levers": [],
                    },
                },
                "ugly": {
                    "scenario_label": "Ugly",
                    "applied_tile_ids": ["tile_42"],
                    "applied_lever_labels": ["Garage rent downside"],
                    "driver": {
                        "tile_id": "tile_42",
                        "metric_ref": "revenue_analysis.annual_revenue",
                    },
                    "stress_band_pct": 10,
                    "cost_anchor_used": True,
                    "cost_anchor_value": 57_482_040,
                    "revenue_anchor_used": False,
                    "revenue_anchor_value": None,
                    "explain": {
                        "short": "Ugly scenario (profile-defined levers applied; financials recomputed).",
                        "levers": ["Driver override applied (tile tile_42)."],
                    },
                },
            },
            "dealshield_controls": {
                "stress_band_pct": 10,
                "use_cost_anchor": True,
                "anchor_total_project_cost": 57_482_040,
                "anchor_debug_flag": "true",
            },
            "context": {
                "location": "Nashville, TN",
                "square_footage": 250_000,
            },
        },
    }


def _assert_no_internal_export_tokens(text: str):
    forbidden_tokens = [
        "multifamily_market_rate_apartments_v1",
        "multifamily_market_rate_content_v3",
        "scope_packet_v2",
        "decision_insurance_subtype_policy_v1",
        "status_source",
        "profile_id",
        "content_profile_id",
        "scope_items_profile_id",
        "applied_tile_ids",
        "metric_ref",
        "driver_tile_id",
        "anchor_debug_flag",
        "tile_42",
        "tile_47",
        "tile_90",
        "Reason code:",
        "base_value_gap_positive",
    ]
    for token in forbidden_tokens:
        assert token not in text


def _build_png(has_visible_content: bool) -> bytes:
    image = Image.new("RGB", (240, 240), "white")
    if has_visible_content:
        draw = ImageDraw.Draw(image)
        draw.rectangle((24, 24, 216, 90), fill="black")
        draw.rectangle((24, 118, 180, 168), fill="#1f2937")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class FakeConsoleMessage:
    def __init__(self, message_type: str, text: str):
        self.type = message_type
        self.text = text


class FakePlaywrightContext:
    def __init__(self, chromium):
        self.chromium = chromium

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSyncPlaywright:
    def __init__(self, chromium):
        self.chromium = chromium

    def __call__(self):
        return FakePlaywrightContext(self.chromium)


class FakeBrowser:
    def __init__(self, page):
        self.page = page
        self.page_options = None
        self.closed = False

    def new_page(self, **kwargs):
        self.page_options = kwargs
        return self.page

    def close(self):
        self.closed = True


class FakeChromium:
    def __init__(self, browser):
        self.browser = browser
        self.launch_kwargs = None

    def launch(self, **kwargs):
        self.launch_kwargs = kwargs
        return self.browser


class FakePage:
    def __init__(
        self,
        render_state: dict,
        screenshot_bytes: bytes,
        pdf_bytes: bytes,
        *,
        console_messages: Optional[List[FakeConsoleMessage]] = None,
        page_errors: Optional[List[BaseException]] = None,
    ):
        self.render_state = render_state
        self.screenshot_bytes = screenshot_bytes
        self.pdf_bytes = pdf_bytes
        self.console_messages = console_messages or []
        self.page_errors = page_errors or []
        self.handlers: dict[str, list] = {}
        self.wait_until = None
        self.media = None

    def on(self, event: str, handler):
        self.handlers.setdefault(event, []).append(handler)

    def set_content(self, html: str, wait_until: Optional[str] = None):
        self.html = html
        self.wait_until = wait_until
        for message in self.console_messages:
            for handler in self.handlers.get("console", []):
                handler(message)
        for error in self.page_errors:
            for handler in self.handlers.get("pageerror", []):
                handler(error)

    def emulate_media(self, media: Optional[str] = None):
        self.media = media

    def evaluate(self, script: str):
        if "requestAnimationFrame" in script:
            return True
        return dict(self.render_state)

    def screenshot(self, **kwargs):
        self.screenshot_kwargs = kwargs
        return self.screenshot_bytes

    def pdf(self, **kwargs):
        self.pdf_kwargs = kwargs
        return self.pdf_bytes


def _install_fake_playwright(monkeypatch, service: ProfessionalPDFExportService, page: FakePage):
    browser = FakeBrowser(page)
    chromium = FakeChromium(browser)
    fake_sync_playwright = FakeSyncPlaywright(chromium)
    monkeypatch.setattr(service, "_get_sync_playwright", lambda: fake_sync_playwright)
    return browser, chromium


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
                "status_source": "canonical_policy",
                "policy_id": "decision_insurance_subtype_policy_v1",
            },
        },
    )

    assert 'class="badge go">GO<' in html
    assert "Policy basis: DealShield canonical policy." in html
    assert "Policy source:" not in html
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


def test_render_validation_accepts_meaningful_render_state():
    service = ProfessionalPDFExportService()

    service._validate_rendered_pdf_output(
        {
            "body_text_length": 220,
            "visible_text_block_count": 18,
            "section_count": 4,
            "h1_count": 1,
            "page_count": 5,
            "visible_page_count": 5,
            "scroll_height": 1800,
            "body_text_excerpt": "SpecSharp decision packet overview",
        },
        b"%PDF-1.7\n" + (b"x" * 5000),
        {"console_messages": [], "page_errors": [], "request_failures": [], "launch_options": {"args": []}},
        {"non_white_ratio": 0.04},
    )


def test_render_validation_rejects_blank_render_state():
    service = ProfessionalPDFExportService()

    with pytest.raises(PDFRenderError) as exc_info:
        service._validate_rendered_pdf_output(
            {
                "body_text_length": 0,
                "visible_text_block_count": 0,
                "section_count": 0,
                "h1_count": 0,
                "page_count": 1,
                "visible_page_count": 0,
                "scroll_height": 0,
                "body_text_excerpt": "",
            },
            b"%PDF-1.7\n" + (b"x" * 5000),
            {"console_messages": [], "page_errors": [], "request_failures": [], "launch_options": {"args": []}},
            {"non_white_ratio": 0.0},
        )

    assert "body text too short" in str(exc_info.value)
    assert "first-page screenshot nearly blank" in str(exc_info.value)


def test_render_html_to_pdf_rejects_blank_output_and_surfaces_diagnostics(monkeypatch):
    service = ProfessionalPDFExportService()
    page = FakePage(
        {
            "body_text_length": 0,
            "body_html_length": 42,
            "body_html_excerpt": "<div class=\"page\"><section></section></div>",
            "visible_text_block_count": 0,
            "section_count": 0,
            "h1_count": 0,
            "page_count": 1,
            "visible_page_count": 0,
            "scroll_height": 0,
            "body_text_excerpt": "",
        },
        _build_png(False),
        b"%PDF-1.7\n" + (b"x" * 5000),
        console_messages=[FakeConsoleMessage("error", "synthetic chromium paint failure")],
    )
    _install_fake_playwright(monkeypatch, service, page)

    with pytest.raises(PDFRenderError) as exc_info:
        service._render_html_to_pdf("<html><body>placeholder</body></html>")

    assert "html_input=text_length=11" in str(exc_info.value)
    assert "dom_html_excerpt='<div class=\"page\"><section></section></div>'" in str(exc_info.value)
    assert "synthetic chromium paint failure" in str(exc_info.value)
    assert "first-page screenshot nearly blank" in str(exc_info.value)


def test_render_html_to_pdf_logs_pre_playwright_text_summary(monkeypatch, caplog):
    service = ProfessionalPDFExportService()
    page = FakePage(
        {
            "body_text_length": 420,
            "body_html_length": 128,
            "body_html_excerpt": "<div class=\"page\"><section><h2>DealShield</h2><p>Boundary text survives.</p></section></div>",
            "visible_text_block_count": 24,
            "section_count": 6,
            "h1_count": 1,
            "page_count": 5,
            "visible_page_count": 5,
            "scroll_height": 2400,
            "body_text_excerpt": "DealShield Boundary text survives.",
        },
        _build_png(True),
        b"%PDF-1.7\n" + (b"x" * 7000),
    )
    _install_fake_playwright(monkeypatch, service, page)
    caplog.set_level(logging.INFO, logger=pdf_export_service_module.logger.name)

    service._render_html_to_pdf(
        "<html><head><style>.noise{color:red;}</style></head><body><h1>DealShield</h1><p>Boundary text survives.</p></body></html>"
    )

    assert "Chromium PDF render input summary" in caplog.text
    assert "html_text_length=34" in caplog.text
    assert "DealShield Boundary text survives." in caplog.text
    assert ".noise{color:red;}" not in caplog.text


def test_render_html_to_pdf_returns_pdf_and_uses_explicit_linux_launch_options(monkeypatch):
    monkeypatch.setattr(pdf_export_service_module.sys, "platform", "linux")
    service = ProfessionalPDFExportService()
    page = FakePage(
        {
            "body_text_length": 420,
            "body_html_length": 112,
            "body_html_excerpt": "<div class=\"page\"><section><h2>SpecSharp</h2><p>decision packet text</p></section></div>",
            "visible_text_block_count": 24,
            "section_count": 6,
            "h1_count": 1,
            "page_count": 5,
            "visible_page_count": 5,
            "scroll_height": 2400,
            "body_text_excerpt": "SpecSharp decision packet for Multifamily - Nashville, TN",
        },
        _build_png(True),
        b"%PDF-1.7\n" + (b"x" * 7000),
    )
    browser, chromium = _install_fake_playwright(monkeypatch, service, page)

    pdf_buffer = service._render_html_to_pdf("<html><body>meaningful packet</body></html>")

    assert pdf_buffer.getvalue() == b"%PDF-1.7\n" + (b"x" * 7000)
    assert chromium.launch_kwargs["headless"] is True
    assert chromium.launch_kwargs["chromium_sandbox"] is False
    assert "--no-sandbox" in chromium.launch_kwargs["args"]
    assert "--disable-dev-shm-usage" in chromium.launch_kwargs["args"]
    assert browser.page_options["viewport"] == service.PDF_VIEWPORT
    assert page.wait_until == "domcontentloaded"
    assert page.media == "screen"


def test_sanitize_decision_packet_export_strips_internal_fields_and_preserves_customer_reasoning():
    safe_packet = sanitize_decision_packet_export(_build_unsafe_decision_packet())
    packet_text = repr(safe_packet)
    html = render_decision_packet_html(safe_packet)

    _assert_no_internal_export_tokens(packet_text)
    _assert_no_internal_export_tokens(html)
    assert safe_packet["provenance"]["decision_basis"] == "Policy basis: DealShield canonical policy."
    assert safe_packet["provenance"]["assumptions_used"][0]["label"] == "Downside stress band"
    assert safe_packet["provenance"]["scenario_summaries"][1]["summary"] == "Modeled levers: Garage rent downside"
    assert safe_packet["decision_insurance"]["primary_control_variable"]["label"] == "Cost Basis Drift + Carry Risk"
    assert safe_packet["decision_metrics_table"]["columns"][0]["id"] == "metric_1"
    assert safe_packet["decision_metrics_table"]["rows"][0]["label"] == "Base"
    assert safe_packet["construction_summary"]["special_features_breakdown"][0]["detail_lines"]
    assert "Provenance / Decision Basis" in html
    assert "Question Bank" in html
    assert "Construction Cost Summary" in html


def test_generate_decision_packet_pdf_renders_customer_safe_packet_html(monkeypatch):
    service = ProfessionalPDFExportService()
    monkeypatch.setattr(
        service,
        "_summarize_pdf_structure",
        lambda pdf_bytes: {"has_font_resources": True, "has_text_operators": True},
    )
    page = FakePage(
        {
            "body_text_length": 520,
            "body_html_length": 164,
            "body_html_excerpt": "<div class=\"page\"><section><h2>Decision Packet</h2><p>Customer-safe export.</p></section></div>",
            "body_text_content_length": 520,
            "visible_text_block_count": 30,
            "section_count": 8,
            "visible_section_count": 8,
            "h1_count": 1,
            "page_count": 6,
            "visible_page_count": 6,
            "scroll_height": 2600,
            "body_text_excerpt": "SpecSharp decision packet customer-safe export",
            "anchor_probes": [
                {"found": True, "text_content_length": 24, "inner_text_length": 24, "rect_width": 800, "rect_height": 120, "offset_height": 120, "client_height": 120},
                {"found": True, "text_content_length": 18, "inner_text_length": 18, "rect_width": 800, "rect_height": 80, "offset_height": 80, "client_height": 80},
                {"found": True, "text_content_length": 22, "inner_text_length": 22, "rect_width": 700, "rect_height": 70, "offset_height": 70, "client_height": 70},
                {"found": True, "text_content_length": 20, "inner_text_length": 20, "rect_width": 700, "rect_height": 70, "offset_height": 70, "client_height": 70},
                {"found": True, "text_content_length": 16, "inner_text_length": 16, "rect_width": 0, "rect_height": 0, "offset_height": 0, "client_height": 0},
            ],
        },
        _build_png(True),
        b"%PDF-1.7\n" + (b"x" * 7000),
    )
    _install_fake_playwright(monkeypatch, service, page)

    safe_packet = sanitize_decision_packet_export(_build_unsafe_decision_packet())
    pdf_buffer = service.generate_decision_packet_pdf(safe_packet)

    assert pdf_buffer.getvalue() == b"%PDF-1.7\n" + (b"x" * 7000)
    assert "Policy basis: DealShield canonical policy." in page.html
    assert "Downside stress band" in page.html
    assert "Modeled Scenario Summaries" in page.html
    assert "Garage rent downside" in page.html
    assert "Question Bank" in page.html
    assert "Construction Cost Summary" in page.html
    _assert_no_internal_export_tokens(page.html)


@pytest.mark.asyncio
async def test_dealshield_pdf_route_uses_dedicated_renderer(monkeypatch):
    project = SimpleNamespace(project_id="project-297")
    payload = {"dealshield_tile_profile": "multifamily_apartment_v1"}
    profile = {"profile_id": "multifamily_apartment_v1"}
    view_model = {"profile_id": "multifamily_apartment_v1", "decision_status": "GO"}
    calls = []

    monkeypatch.setattr(scope_module, "_get_scoped_project", lambda db, project_id, auth: project)
    monkeypatch.setattr(scope_module, "_resolve_project_payload", lambda project_arg: dict(payload))
    monkeypatch.setattr(
        scope_module,
        "_refresh_dealshield_payload_for_project",
        lambda project_arg, payload_arg: dict(payload_arg),
    )
    monkeypatch.setattr(scope_module, "get_dealshield_profile", lambda profile_id: dict(profile))
    monkeypatch.setattr(
        scope_module,
        "build_dealshield_view_model",
        lambda project_id, payload_arg, profile_arg: dict(view_model),
    )

    def fake_generate_dealshield_pdf(arg):
        calls.append(("dealshield", arg))
        return io.BytesIO(b"%PDF-1.7\n")

    def fail_generate_decision_packet_pdf(arg):
        raise AssertionError("DealShield route should not call the decision packet PDF renderer")

    monkeypatch.setattr(scope_module.pdf_export_service, "generate_dealshield_pdf", fake_generate_dealshield_pdf)
    monkeypatch.setattr(
        scope_module.pdf_export_service,
        "generate_decision_packet_pdf",
        fail_generate_decision_packet_pdf,
    )

    response = await scope_module.export_dealshield_pdf("project-297", db=object(), auth=object())

    assert response.media_type == "application/pdf"
    assert "DealShield_" in response.headers["content-disposition"]
    assert calls == [("dealshield", view_model)]


@pytest.mark.asyncio
async def test_project_pdf_route_sends_customer_safe_decision_packet_to_renderer(monkeypatch):
    project = SimpleNamespace(project_id="project-297", name="Nashville Market Apartments")
    unsafe_packet = _build_unsafe_decision_packet()
    payload = {"dealshield_tile_profile": "multifamily_market_rate_apartments_v1"}
    captured_packets = []

    monkeypatch.setattr(scope_module, "_get_scoped_project", lambda db, project_id, auth: project)
    monkeypatch.setattr(scope_module, "format_project_response", lambda project_arg: {"project_name": "Nashville Market Apartments"})
    monkeypatch.setattr(
        scope_module,
        "hydrate_project_payload_for_packet",
        lambda project_arg, project_payload: {"project_name": "Nashville Market Apartments"},
    )
    monkeypatch.setattr(scope_module, "_resolve_project_payload", lambda project_arg: dict(payload))
    monkeypatch.setattr(
        scope_module,
        "_refresh_dealshield_payload_for_project",
        lambda project_arg, payload_arg: dict(payload_arg),
    )
    monkeypatch.setattr(
        scope_module,
        "get_dealshield_profile",
        lambda profile_id: {"profile_id": profile_id},
    )
    monkeypatch.setattr(
        scope_module,
        "build_dealshield_view_model",
        lambda project_id, payload_arg, profile_arg: {"decision_status": "GO"},
    )
    monkeypatch.setattr(
        scope_module,
        "compose_decision_packet_input",
        lambda **kwargs: unsafe_packet,
    )

    def fake_generate_decision_packet_pdf(packet):
        captured_packets.append(packet)
        return io.BytesIO(b"%PDF-1.7\n")

    monkeypatch.setattr(
        scope_module.pdf_export_service,
        "generate_decision_packet_pdf",
        fake_generate_decision_packet_pdf,
    )

    response = await scope_module.export_project_pdf("project-297", db=object(), auth=object())

    assert response.media_type == "application/pdf"
    assert captured_packets

    captured_packet = captured_packets[0]
    captured_text = repr(captured_packet)
    _assert_no_internal_export_tokens(captured_text)
    assert captured_packet["provenance"]["decision_basis"] == "Policy basis: DealShield canonical policy."
    assert captured_packet["provenance"]["scenario_summaries"][1]["summary"] == "Modeled levers: Garage rent downside"
    assert captured_packet["decision_banner"].get("decision_reason_code") in (None, "")
