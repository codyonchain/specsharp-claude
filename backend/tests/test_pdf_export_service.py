import io
import logging
from types import SimpleNamespace
from typing import List, Optional

import pytest
from PIL import Image, ImageDraw

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
