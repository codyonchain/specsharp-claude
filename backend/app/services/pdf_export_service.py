from typing import Dict, List, Optional, Any
import io
from datetime import datetime
import logging
import sys
from pathlib import Path
import threading
import queue
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.platypus import Image as RLImage
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.utils.building_type_display import get_display_building_type
from app.utils.formatting import format_currency, format_percentage
from app.services.executive_summary_service import executive_summary_service

logger = logging.getLogger(__name__)


class ProfessionalPDFExportService:
    """Service for generating premium PDF reports"""
    
    # Brand colors (converted to RGB for PDF)
    BRAND_PRIMARY = colors.HexColor('#667EEA')
    BRAND_SECONDARY = colors.HexColor('#764BA2')
    BRAND_ACCENT = colors.HexColor('#10B981')
    BRAND_LIGHT = colors.HexColor('#F3F4F6')
    BRAND_DARK = colors.HexColor('#1F2937')
    
    def __init__(self):
        self._init_styles()
    
    def _hex(self, color: colors.Color) -> str:
        """Convert ReportLab color to #RRGGBB string"""
        hex_value = color.hexval()
        if hex_value.startswith('0x'):
            hex_value = hex_value[2:]
        return f"#{hex_value}"

    def _category_total(self, category: Dict) -> float:
        """Return total cost for a category regardless of schema shape"""
        subtotal = category.get('subtotal')
        if subtotal is not None:
            return subtotal
        systems = category.get('systems', [])
        return sum((system.get('total_cost') or 0) for system in systems)
    
    def _calculate_trade_percentage(self, category: Dict, subtotal: float, total: float) -> float:
        """Resolve trade percentage, scaling fractional inputs when needed."""
        raw_pct = category.get('percentage')
        if isinstance(raw_pct, (int, float)):
            if 0 <= raw_pct <= 1:
                return raw_pct * 100.0
            return raw_pct
        if total > 0:
            return (subtotal / total) * 100.0
        return 0.0
    
    def _init_styles(self):
        """Initialize professional PDF styles"""
        self.styles = getSampleStyleSheet()
        
        # Main title style
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.BRAND_PRIMARY,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=self.BRAND_PRIMARY,
            spaceAfter=20,
            spaceBefore=30,
            fontName='Helvetica-Bold',
            borderColor=self.BRAND_PRIMARY,
            borderWidth=2,
            borderPadding=5
        ))
        
        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=self.BRAND_DARK,
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Key metric style
        self.styles.add(ParagraphStyle(
            name='KeyMetric',
            parent=self.styles['Normal'],
            fontSize=20,
            textColor=self.BRAND_ACCENT,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Simple centered text style for cover/footer notes
        self.styles.add(ParagraphStyle(
            name='CenteredText',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#374151'),
            fontSize=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallGrey',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6B7280'),
            fontSize=9
        ))
        
        # Professional body text
        self.styles.add(ParagraphStyle(
            name='ProfessionalBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#374151'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyTextDark',
            parent=self.styles['BodyText'],
            fontSize=10,
            leading=14,
            textColor=self.BRAND_DARK
        ))

    def _brand_hex(self, c: colors.Color) -> str:
        """Return ReportLab color as hex string usable inside font tags."""
        try:
            hx = c.hexval()
            if not isinstance(hx, str):
                return "#111827"
            if hx.startswith('0x'):
                hx = hx[2:]
            if not hx.startswith('#'):
                hx = f"#{hx}"
            return hx
        except Exception:
            return "#111827"

    def _safe_table_style(self, extra: Optional[List] = None) -> TableStyle:
        base = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]
        if extra:
            base.extend(extra)
        return TableStyle(base)

    def _card(self, title: str, body_flowables: List[Any], keep_together: bool = False) -> List[Any]:
        """Wrap a set of flowables inside a branded card. Optionally keep together."""
        title_para = Paragraph(
            f"<font color='{self._brand_hex(self.BRAND_DARK)}'><b>{title.upper()}</b></font>",
            self.styles['BodyTextDark']
        )
        card_rows: List[List[Any]] = [[title_para], [Spacer(1, 0.15 * inch)]]
        for flowable in body_flowables:
            card_rows.append([flowable])

        card_table = Table(card_rows, colWidths=[6.0 * inch])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
            ('LEFTPADDING', (0, 0), (-1, -1), 18),
            ('RIGHTPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 18),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
        ]))

        block: List[Any] = [card_table, Spacer(1, 0.25 * inch)]
        if keep_together:
            return [KeepTogether(block)]
        return block

    def generate_professional_pdf(self, project_data: Dict, client_name: str = None) -> io.BytesIO:
        """Generate premium PDF via Playwright-rendered HTML."""
        executive_summary = executive_summary_service.generate_executive_summary(project_data)
        return self._render_chromium_pdf(project_data, executive_summary, client_name)

    def _render_chromium_pdf(self, project_data: Dict, executive_summary: Dict, client_name: Optional[str]) -> io.BytesIO:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError:
            backend_dir = Path(__file__).resolve().parents[2]
            candidate_paths = [
                backend_dir / "venv" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages",
                backend_dir / "venv" / "lib" / "python3.9" / "site-packages",
                backend_dir / "venv" / "lib" / "python3.10" / "site-packages",
                backend_dir / "venv" / "lib" / "python3.11" / "site-packages",
            ]
            added = False
            for site in candidate_paths:
                if site.exists() and str(site) not in sys.path:
                    sys.path.insert(0, str(site))
                    added = True
            if not added:
                raise RuntimeError(
                    "Playwright is not installed for the Python interpreter running the backend "
                    f"({sys.executable}). Install it there with:\n"
                    f"  {sys.executable} -m pip install playwright && {sys.executable} -m playwright install chromium"
                )
            try:
                from playwright.sync_api import sync_playwright  # type: ignore
            except ImportError as exc:
                raise RuntimeError(
                    "Playwright is not installed for the Python interpreter running the backend "
                    f"({sys.executable}). Install it there with:\n"
                    f"  {sys.executable} -m pip install playwright && {sys.executable} -m playwright install chromium"
                ) from exc

        html = self._render_executive_overview_html(project_data, executive_summary, client_name)

        result_queue: "queue.Queue[bytes]" = queue.Queue(maxsize=1)
        error_queue: "queue.Queue[BaseException]" = queue.Queue(maxsize=1)

        def worker():
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.set_content(html, wait_until="networkidle")
                    pdf_bytes = page.pdf(
                        format="Letter",
                        print_background=True,
                        margin={"top": "0.6in", "right": "0.6in", "bottom": "0.6in", "left": "0.6in"},
                    )
                    browser.close()
                    result_queue.put(pdf_bytes)
            except BaseException as exc:  # capture Playwright/system errors
                error_queue.put(exc)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        thread.join()

        if not error_queue.empty():
            raise error_queue.get()

        pdf_bytes = result_queue.get_nowait()

        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer

    # -----------------------------
    # HTML → Chromium PDF Rendering
    # -----------------------------

    def _dig(self, obj: Any, path: str, default: Any = None) -> Any:
        current = obj
        for part in path.split('.'):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def _fmt_money_plain(self, value: Any) -> str:
        if value is None:
            return "—"
        try:
            return format_currency(float(value))
        except Exception:
            return str(value)

    def _fmt_pct_smart(self, value: Any, digits: int = 1) -> str:
        if value is None:
            return "—"
        try:
            pct = float(value)
            if abs(pct) <= 1.5:
                pct *= 100.0
            return f"{pct:.{digits}f}%"
        except Exception:
            return str(value)

    def _fmt_num(self, value: Any, digits: int = 2) -> str:
        if value is None:
            return "—"
        try:
            return f"{float(value):.{digits}f}"
        except Exception:
            return str(value)

    def _render_executive_overview_html(self, project_data: Dict, executive_summary: Dict, client_name: Optional[str]) -> str:
        calc = (project_data or {}).get("calculation_data") or {}

        # ExecutiveView decision + underwriting data is always under ownership_analysis.*
        oa_return = self._dig(calc, "ownership_analysis.return_metrics", {}) or {}
        oa_reqs = self._dig(calc, "ownership_analysis.revenue_requirements", {}) or {}
        oa_feas_detail = oa_reqs.get("feasibility_detail") or {}

        noi = oa_return.get("estimated_annual_noi")
        irr = oa_return.get("irr")
        coc = oa_return.get("cash_on_cash_return")
        equity = self._dig(calc, "ownership_analysis.financing_sources.equity_amount")
        value = oa_return.get("property_value")
        feasible_flag = oa_return.get("feasible")
        feasibility_text = oa_reqs.get("feasibility")
        feasibility_status = oa_feas_detail.get("status") or feasibility_text
        feasibility_reco = oa_feas_detail.get("recommendation")

        # DSCR is optional (older payloads may omit it)
        dscr = self._dig(calc, "ownership_analysis.debt_metrics.calculated_dscr")
        debt_metrics = self._dig(calc, "ownership_analysis.debt_metrics", {}) or {}

        # “vs target” comparators (use only what the payload already provides)
        irr_target = oa_return.get("target_roi")
        market_cap = (
            oa_return.get("market_cap_rate")
            or oa_return.get("marketCapRate")
            or oa_return.get("market_cap")
        )
        cap_rate = oa_return.get("cap_rate")
        dscr_target = (
            debt_metrics.get("target_dscr")
            or debt_metrics.get("dscr_target")
            or debt_metrics.get("required_dscr")
            or debt_metrics.get("minimum_dscr")
            or debt_metrics.get("lender_min_dscr")
            or debt_metrics.get("dscr_requirement")
        )
        required_value = oa_reqs.get("required_value")
        gap_pct = oa_reqs.get("gap_percentage")

        overview = (executive_summary or {}).get("project_overview", {}) or {}
        cost_summary = (executive_summary or {}).get("cost_summary", {}) or {}
        major_systems = (executive_summary or {}).get("major_systems") or []
        risks = (executive_summary or {}).get("risk_factors") or []
        next_steps = (executive_summary or {}).get("next_steps") or []
        assumptions = (executive_summary or {}).get("key_assumptions") or []
        confidence = (executive_summary or {}).get("confidence_assessment", {}) or {}

        title = overview.get("name") or project_data.get("project_name") or project_data.get("name") or "Project"
        location = overview.get("location") or project_data.get("location") or "—"
        building_type = overview.get("type") or project_data.get("building_type") or project_data.get("buildingType") or "—"
        size = overview.get("size") or str(project_data.get("square_footage") or project_data.get("squareFootage") or "—")

        total_cost = cost_summary.get("total_project_cost") or project_data.get("total_cost") or project_data.get("totalCost")
        cost_psf = cost_summary.get("cost_per_sf") or project_data.get("cost_per_sqft") or project_data.get("costPerSqft")

        def esc(value: Any) -> str:
            if value is None:
                return ""
            return (
                str(value)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

        def kpi_subline(text: Optional[str]) -> str:
            return f"<div class='sub'>{esc(text)}</div>" if text else ""

        irr_sub = f"vs target {self._fmt_pct_smart(irr_target, 1)}" if irr_target is not None else ""
        dscr_sub = f"vs target {self._fmt_num(dscr_target, 2)}" if dscr_target is not None else ""
        noi_sub = ""
        if required_value is not None:
            if gap_pct is not None:
                noi_sub = f"vs required {self._fmt_money_plain(required_value)} (gap {self._fmt_pct_smart(gap_pct, 1)})"
            else:
                noi_sub = f"vs required {self._fmt_money_plain(required_value)}"
        coc_sub = ""
        if market_cap is not None:
            coc_sub = f"vs market cap {self._fmt_pct_smart(market_cap, 1)}"
        elif cap_rate is not None:
            coc_sub = f"cap rate {self._fmt_pct_smart(cap_rate, 1)}"

        major_rows = "".join(
            f"<tr><td>{esc(ms.get('system','—'))}</td><td class='r'>{esc(ms.get('cost','—'))}</td>"
            f"<td class='r'>{esc(ms.get('percentage','—'))}</td></tr>"
            for ms in major_systems[:6]
            if isinstance(ms, dict)
        ) or "<tr><td colspan='3' class='muted'>—</td></tr>"

        risk_items = "".join(
            f"<li><b>{esc(r.get('category','Risk'))}:</b> {esc(r.get('risk',''))}</li>"
            for r in risks[:6]
            if isinstance(r, dict)
        ) or "<li class='muted'>—</li>"

        next_items = "".join(f"<li>{esc(step)}</li>" for step in next_steps[:8]) or "<li class='muted'>—</li>"
        assumption_items = "".join(f"<li>{esc(a)}</li>" for a in assumptions[:10]) or "<li class='muted'>—</li>"

        # Decision/why: re-use ExecutiveView output verbatim.
        decision = "NEEDS WORK"
        if (feasible_flag is True) or (isinstance(feasibility_text, str) and feasibility_text.strip().lower() == "feasible"):
            decision = "GO"
        else:
            reco_text = (feasibility_reco or "")
            if isinstance(reco_text, str) and ("minor" in reco_text.lower() or "optimization" in reco_text.lower()):
                decision = "NEEDS WORK"
            else:
                decision = "NO-GO"

        decision_reason = feasibility_reco or (f"Feasibility: {feasibility_status}" if feasibility_status else "Decision sourced from ExecutiveView underwriting logic.")
        decision_badge_class = "needs"
        if decision == "GO":
            decision_badge_class = "go"
        elif decision == "NO-GO":
            decision_badge_class = "nogo"
        generated = datetime.now().strftime("%B %d, %Y")

        return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    @page {{ size: Letter; margin: 0.6in; }}
    :root {{
      --ink: #0f172a;          /* slate-900 */
      --muted: #475569;        /* slate-600 */
      --muted2: #64748b;       /* slate-500 */
      --border: #e2e8f0;       /* slate-200 */
      --panel: #ffffff;
      --panel2: #f8fafc;       /* slate-50 */
      --brand: #1d4ed8;        /* blue-700 */
      --brand2: #0ea5e9;       /* sky-500 */
      --shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    }}
    body {{
      font-family: Inter, system-ui, -apple-system, 'Segoe UI', 'Roboto', Arial;
      color: var(--ink);
      background: #ffffff;
      -webkit-font-smoothing: antialiased;
      text-rendering: geometricPrecision;
    }}

    .stack > * + * {{ margin-top: 12px; }}

    .top {{ display:flex; justify-content:space-between; align-items:flex-start; gap:16px; }}
    .eyebrow {{ font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted2); }}
    .h1 {{ font-size: 24px; font-weight: 900; margin: 2px 0 0 0; line-height: 1.1; }}
    .meta {{ font-size: 11px; color: var(--muted); margin-top: 6px; line-height: 1.35; }}

    .badge {{ display:inline-block; padding:7px 12px; border-radius:999px; font-weight:900; font-size:11px; letter-spacing:.06em; }}
    .badge.go {{ background:#ecfdf5; color:#065f46; border:1px solid #a7f3d0; }}
    .badge.needs {{ background:#fffbeb; color:#92400e; border:1px solid #fcd34d; }}
    .badge.nogo {{ background:#fef2f2; color:#991b1b; border:1px solid #fecaca; }}
    .banner {{
      margin-top: 14px;
      border-radius: 18px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      box-shadow: var(--shadow);
      display:flex; justify-content:space-between; gap:16px; align-items:flex-start;
      position: relative;
      overflow: hidden;
    }}
    .banner:before {{
      content:"";
      position:absolute; left:0; top:0; bottom:0; width:6px;
      background: linear-gradient(180deg, var(--brand) 0%, var(--brand2) 100%);
    }}
    .banner .title {{ font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: var(--muted2); margin:0; }}
    .banner .why {{ font-size: 12px; color: var(--muted); margin-top: 6px; line-height: 1.35; max-width: 520px; }}
    .banner .right {{ text-align:right; min-width: 160px; }}
    .card {{
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px 16px;
      background: var(--panel);
      box-shadow: var(--shadow);
      margin-top: 12px;
    }}
    .card h2 {{
      margin: 0 0 12px 0;
      font-size: 10px;
      letter-spacing: .14em;
      text-transform: uppercase;
      color: var(--muted2);
    }}
    .grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; }}
    .kpi {{
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 12px;
      background: linear-gradient(180deg, var(--panel2) 0%, #ffffff 100%);
    }}
    .kpi .label {{ font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: var(--muted2); }}
    .kpi .value {{ font-size: 20px; font-weight: 900; margin-top: 6px; line-height: 1.05; }}
    .kpi .sub {{ font-size: 11px; color: var(--muted); margin-top: 6px; }}
    table {{ width:100%; border-collapse:separate; border-spacing: 0; font-size: 11px; }}
    th, td {{ padding:10px 10px; border-bottom:1px solid var(--border); vertical-align:top; }}
    thead th {{
      position: sticky;
      top: 0;
      text-align:left;
      color: var(--muted2);
      font-size: 10px;
      letter-spacing: .12em;
      text-transform: uppercase;
      background: #ffffff;
    }}
    tbody tr:last-child td {{ border-bottom: none; }}
    .r {{ text-align:right; }}
    ul {{ margin: 0; padding-left: 18px; font-size: 12px; color: var(--ink); line-height: 1.35; }}
    li {{ margin: 6px 0; }}
    .muted {{ color: var(--muted2); }}
    .pagebreak {{ page-break-before: always; break-before: page; }}
    .footer {{
      margin-top: 14px;
      font-size: 10px;
      color: var(--muted2);
      line-height: 1.35;
      border-top: 1px solid var(--border);
      padding-top: 10px;
    }}
  </style>
</head>
<body>
  <!-- PAGE 1 -->
  <div class="top">
    <div>
      <div class="eyebrow">SpecSharp Executive Overview</div>
      <div class="h1">{esc(title)}</div>
      <div class="meta">{esc(location)} • {esc(building_type)} • {esc(size)}</div>
    </div>
    <div style="text-align:right">
      {"<div class='meta'><b>Prepared for:</b> " + esc(client_name) + "</div>" if client_name else ""}
    </div>
  </div>
  <div class="banner">
    <div>
      <p class="title">Investment Decision</p>
      <div class="why">{esc(decision_reason)}</div>
    </div>
    <div class="right">
      <div class="badge {decision_badge_class}">{esc(decision)}</div>
      <div class="meta">Generated {esc(generated)}</div>
    </div>
  </div>

  <div class="card">
    <h2>Key Investment Metrics</h2>
    <div class="grid">
      <div class="kpi"><div class="label">Total Project Cost</div><div class="value">{esc(total_cost) if total_cost is not None else "—"}</div></div>
      <div class="kpi"><div class="label">Cost per SF</div><div class="value">{esc(cost_psf) if cost_psf is not None else "—"}</div></div>
      <div class="kpi"><div class="label">Stabilized NOI (Annual)</div><div class="value">{esc(self._fmt_money_plain(noi))}</div>{kpi_subline(noi_sub)}</div>
      <div class="kpi"><div class="label">DSCR</div><div class="value">{esc(self._fmt_num(dscr, 2))}</div>{kpi_subline(dscr_sub)}</div>
      <div class="kpi"><div class="label">IRR</div><div class="value">{esc(self._fmt_pct_smart(irr, 1))}</div>{kpi_subline(irr_sub)}</div>
      <div class="kpi"><div class="label">Cash-on-Cash Return</div><div class="value">{esc(self._fmt_pct_smart(coc, 1))}</div>{kpi_subline(coc_sub)}</div>
      <div class="kpi"><div class="label">Equity Required</div><div class="value">{esc(self._fmt_money_plain(equity))}</div></div>
      <div class="kpi"><div class="label">Value @ Stabilization</div><div class="value">{esc(self._fmt_money_plain(value))}</div></div>
    </div>
  </div>

  <div class="card">
    <h2>Top Risks</h2>
    <ul>{risk_items}</ul>
  </div>

  <div class="pagebreak"></div>
  <div class="h1">Construction Reality</div>
  <div class="meta">What moves cost, confidence, and diligence next steps.</div>

  <div class="card">
    <h2>Top Cost Drivers</h2>
    <table>
      <thead><tr><th>System</th><th class="r">Cost</th><th class="r">Share</th></tr></thead>
      <tbody>{major_rows}</tbody>
    </table>
  </div>

  <div class="card">
    <h2>Confidence</h2>
    <table>
      <tbody>
        <tr><td>Overall Confidence</td><td class="r"><b>{esc(confidence.get('overall_confidence','—'))}</b></td></tr>
        <tr><td>Confidence Level</td><td class="r"><b>{esc(confidence.get('confidence_level','—'))}</b></td></tr>
        <tr><td>Data Quality</td><td class="r"><b>{esc(confidence.get('data_quality','—'))}</b></td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>Next Steps</h2>
    <ul>{next_items}</ul>
  </div>

  <div class="pagebreak"></div>
  <div class="h1">Assumptions</div>
  <div class="meta">High-impact assumptions that materially change underwriting outcomes.</div>

  <div class="card">
    <h2>Key Assumptions</h2>
    <ul>{assumption_items}</ul>
  </div>

  <div class="footer">
    Note: This executive overview is generated from provided inputs and modeled assumptions. Use for preliminary feasibility only.
    Validate pricing, schedule, and financing terms prior to investment decisions.
  </div>
</body>
</html>"""
    
    def _create_cover_page(self, project_data: Dict, client_name: str) -> List:
        """Create professional cover page"""
        elements = []
        
        # Company logo placeholder (you can add actual logo here)
        logo_placeholder = Drawing(400, 60)
        logo_rect = Rect(150, 10, 100, 40, fillColor=self.BRAND_PRIMARY, strokeColor=None)
        logo_text = String(200, 25, 'SPECSHARP', fontSize=24, fillColor=colors.white, 
                          textAnchor='middle', fontName='Helvetica-Bold')
        logo_placeholder.add(logo_rect)
        logo_placeholder.add(logo_text)
        elements.append(logo_placeholder)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Title
        elements.append(Paragraph(
            "CONSTRUCTION COST ESTIMATE",
            self.styles['MainTitle']
        ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Project name box
        project_name = project_data.get('project_name', 'Construction Project')
        elements.append(self._create_info_box(
            project_name,
            background_color=self.BRAND_LIGHT,
            text_style=ParagraphStyle(
                name='ProjectName',
                fontSize=22,
                textColor=self.BRAND_DARK,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
        ))
        
        # Reduce vertical whitespace so cover never spills into an empty Page 2
        elements.append(Spacer(1, 0.55*inch))
        
        # Key metrics boxes
        metrics_data = [
            ['TOTAL PROJECT COST', format_currency(project_data.get('total_cost', 0))],
            ['COST PER SQ FT', f"${project_data.get('cost_per_sqft', 0):.2f}"],
            ['TOTAL AREA', f"{project_data.get('request_data', {}).get('square_footage', 0):,} SF"]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2.5*inch])
        metrics_table.setStyle(self._safe_table_style([
            ('BACKGROUND', (0, 0), (-1, -1), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('FONTSIZE', (1, 0), (1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 18),
            ('TOPPADDING', (0, 0), (-1, -1), 18),
            ('GRID', (0, 0), (-1, -1), 2, colors.white),
        ]))
        
        elements.append(metrics_table)
        
        elements.append(Spacer(1, 0.65*inch))
        
        # Client information
        if client_name:
            elements.append(Paragraph(
                f"<font color='{self._brand_hex(self.BRAND_DARK)}'>Prepared for:</font>",
                self.styles['BodyTextDark']
            ))
            elements.append(Paragraph(
                f"<font size='16'><b>{client_name}</b></font>",
                self.styles['BodyTextDark']
            ))
        
        elements.append(Spacer(1, 0.25*inch))
        
        # Date and validity
        elements.append(Paragraph(
            f"<font color='#6B7280'>Generated: {datetime.now().strftime('%B %d, %Y')}</font>",
            self.styles['BodyTextDark']
        ))
        elements.append(Paragraph(
            f"<font color='#6B7280'>Valid for: 30 days</font>",
            self.styles['BodyTextDark']
        ))
        
        # SpecSharp branding at bottom of cover
        elements.append(Spacer(1, 0.45*inch))
        elements.append(Paragraph(
            "<font color='#6B7280'>Generated by SpecSharp • specsharp.ai</font>",
            self.styles['SmallGrey']
        ))

        return elements



    # ---------------------------
    # Executive Overview v2 Pages
    # ---------------------------

    def _get_calc(self, project_data: Dict) -> Dict:
        return (project_data or {}).get('calculation_data') or {}

    def _dig(self, obj: Any, path: str, default: Any = None) -> Any:
        current = obj
        for part in path.split('.'):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def _fmt_money(self, value: Any) -> str:
        if value is None:
            return "—"
        try:
            return format_currency(float(value))
        except Exception:
            return str(value)

    def _fmt_pct(self, value: Any, digits: int = 1) -> str:
        if value is None:
            return "—"
        try:
            return f"{float(value) * 100.0:.{digits}f}%"
        except Exception:
            return str(value)

    def _fmt_num(self, value: Any, digits: int = 2) -> str:
        if value is None:
            return "—"
        try:
            return f"{float(value):.{digits}f}"
        except Exception:
            return str(value)

    def _kpi_grid(self, rows: List[List[str]]) -> Table:
        table = Table(rows, colWidths=[3.2 * inch, 2.8 * inch])
        table.setStyle(self._safe_table_style([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), self.BRAND_DARK),
            ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_ACCENT),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        return table

    def _create_investment_decision_page(self, project_data: Dict, executive_summary: Dict) -> List[Any]:
        elements: List[Any] = []
        calc = self._get_calc(project_data)

        overview = (executive_summary or {}).get('project_overview', {}) or {}
        title = overview.get('name') or project_data.get('project_name') or project_data.get('name') or "Project"
        location = overview.get('location') or project_data.get('location') or "—"
        building_type = overview.get('type') or project_data.get('building_type') or project_data.get('buildingType') or "—"
        size = overview.get('size') or str(project_data.get('square_footage') or project_data.get('squareFootage') or "—")

        elements.append(Paragraph("EXECUTIVE OVERVIEW", self.styles['SectionHeader']))
        elements.append(Paragraph(f"<b>{title}</b>", self.styles['SubsectionHeader']))
        elements.append(Paragraph(f"{location} • {building_type} • {size}", self.styles['ProfessionalBody']))

        noi = self._dig(calc, 'return_metrics.estimated_annual_noi')
        dscr = self._dig(calc, 'ownership_analysis.debt_metrics.calculated_dscr')
        irr = self._dig(calc, 'return_metrics.irr')
        coc = self._dig(calc, 'return_metrics.cash_on_cash_return')
        equity = self._dig(calc, 'ownership_analysis.financing_sources.equity_amount')
        value = self._dig(calc, 'return_metrics.property_value')

        cost_summary = (executive_summary or {}).get('cost_summary', {}) or {}
        total_cost = cost_summary.get('total_project_cost') or project_data.get('total_cost') or project_data.get('totalCost')
        cost_psf = cost_summary.get('cost_per_sf') or project_data.get('cost_per_sqft') or project_data.get('costPerSqft')

        kpis = [
            ["Total Project Cost", str(total_cost) if total_cost is not None else "—"],
            ["Cost per SF", str(cost_psf) if cost_psf is not None else "—"],
            ["Stabilized NOI (Annual)", self._fmt_money(noi)],
            ["DSCR", self._fmt_num(dscr, 2)],
            ["IRR", self._fmt_pct(irr, 1)],
            ["Cash-on-Cash Return", self._fmt_pct(coc, 1)],
            ["Equity Required", self._fmt_money(equity)],
            ["Value @ Stabilization", self._fmt_money(value)],
        ]
        elements.extend(self._card("Key Investment Metrics", [self._kpi_grid(kpis)]))

        risks = (executive_summary or {}).get('risk_factors') or []
        next_steps = (executive_summary or {}).get('next_steps') or []

        risk_lines: List[Any] = []
        for risk in risks[:5]:
            if isinstance(risk, dict):
                text = f"<b>{risk.get('category', 'Risk')}:</b> {risk.get('risk', '')}"
            else:
                text = str(risk)
            risk_lines.append(Paragraph(f"• {text}", self.styles['ProfessionalBody']))
        if not risk_lines:
            risk_lines.append(Paragraph("• —", self.styles['ProfessionalBody']))

        next_lines: List[Any] = []
        for step in next_steps[:6]:
            next_lines.append(Paragraph(f"• {step}", self.styles['ProfessionalBody']))
        if not next_lines:
            next_lines.append(Paragraph("• —", self.styles['ProfessionalBody']))

        elements.extend(self._card("Top Risks", risk_lines))
        elements.extend(self._card("Next Steps", next_lines))
        return elements

    def _create_construction_reality_page(self, project_data: Dict, executive_summary: Dict) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph("CONSTRUCTION REALITY", self.styles['SectionHeader']))

        calc = self._get_calc(project_data)
        totals = self._dig(calc, 'totals', {}) or {}
        hard = totals.get('hard_cost_total') or totals.get('hard_costs')
        soft = totals.get('soft_cost_total') or totals.get('soft_costs')
        contingency = totals.get('contingency_total') or totals.get('contingency')
        total = totals.get('total_project_cost') or totals.get('total')

        if any(v is not None for v in [hard, soft, contingency, total]):
            rows = []
            if hard is not None:
                rows.append(["Hard Costs", self._fmt_money(hard)])
            if soft is not None:
                rows.append(["Soft Costs", self._fmt_money(soft)])
            if contingency is not None:
                rows.append(["Contingency", self._fmt_money(contingency)])
            if total is not None:
                rows.append(["Total", self._fmt_money(total)])
            uses_table = Table(rows, colWidths=[3.2 * inch, 2.8 * inch])
            uses_table.setStyle(self._safe_table_style([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_ACCENT),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ]))
            elements.extend(self._card("Uses of Funds", [uses_table]))
        else:
            cost_summary = (executive_summary or {}).get('cost_summary', {}) or {}
            fallback_rows = [
                ["Total Project Cost", cost_summary.get('total_project_cost', '—')],
                ["Contingency", cost_summary.get('contingency', '—')],
                ["Total w/ Contingency", cost_summary.get('total_with_contingency', '—')],
            ]
            fallback_table = Table(fallback_rows, colWidths=[3.2 * inch, 2.8 * inch])
            fallback_table.setStyle(self._safe_table_style([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_ACCENT),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ]))
            elements.extend(self._card("Cost Summary", [fallback_table]))

        major_systems = (executive_summary or {}).get('major_systems') or []
        if major_systems:
            rows = [["System", "Cost", "Share"]]
            for system in major_systems[:6]:
                if isinstance(system, dict):
                    rows.append([
                        system.get('system', '—'),
                        system.get('cost', '—'),
                        system.get('percentage', '—')
                    ])
            systems_table = Table(rows, colWidths=[3.0 * inch, 1.6 * inch, 1.4 * inch])
            systems_table.setStyle(self._safe_table_style([
                ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_LIGHT]),
            ]))
            elements.extend(self._card("Top Cost Drivers", [systems_table]))

        confidence = (executive_summary or {}).get('confidence_assessment', {}) or {}
        confidence_lines = []
        if confidence:
            confidence_lines.append(Paragraph(f"Overall Confidence: <b>{confidence.get('overall_confidence', '—')}</b>", self.styles['ProfessionalBody']))
            confidence_lines.append(Paragraph(f"Confidence Level: <b>{confidence.get('confidence_level', '—')}</b>", self.styles['ProfessionalBody']))
            confidence_lines.append(Paragraph(f"Data Quality: <b>{confidence.get('data_quality', '—')}</b>", self.styles['ProfessionalBody']))
        if confidence_lines:
            elements.extend(self._card("Confidence", confidence_lines))

        return elements

    def _create_assumptions_next_steps_page(self, project_data: Dict, executive_summary: Dict) -> List[Any]:
        elements: List[Any] = []
        elements.append(Paragraph("ASSUMPTIONS & NEXT STEPS", self.styles['SectionHeader']))

        assumptions = (executive_summary or {}).get('key_assumptions') or []
        assumption_lines = []
        for assumption in assumptions[:10]:
            assumption_lines.append(Paragraph(f"• {assumption}", self.styles['ProfessionalBody']))
        if not assumption_lines:
            assumption_lines.append(Paragraph("• —", self.styles['ProfessionalBody']))
        elements.extend(self._card("Key Assumptions", assumption_lines))

        next_steps = (executive_summary or {}).get('next_steps') or []
        step_lines = []
        for step in next_steps[:10]:
            step_lines.append(Paragraph(f"• {step}", self.styles['ProfessionalBody']))
        if not step_lines:
            step_lines.append(Paragraph("• —", self.styles['ProfessionalBody']))
        elements.extend(self._card("Next Steps", step_lines))

        elements.append(Spacer(1, 0.15 * inch))
        elements.append(Paragraph(
            "<font color='#6B7280'>Note: This Executive Overview is generated from provided inputs and modeled assumptions. "
            "Use for preliminary feasibility only. Validate pricing, schedule, and financing terms prior to investment decisions.</font>",
            self.styles['BodyTextDark']
        ))

        return elements
    def _create_info_box(self, text: str, background_color=None, text_style=None) -> Table:
        """Create a styled info box"""
        if text_style is None:
            text_style = self.styles['BodyTextDark']
        
        data = [[Paragraph(text, text_style)]]
        table = Table(data, colWidths=[6*inch])
        
        style_commands = [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]
        
        if background_color:
            style_commands.append(('BACKGROUND', (0, 0), (-1, -1), background_color))
            style_commands.append(('BOX', (0, 0), (-1, -1), 2, self.BRAND_PRIMARY))
            style_commands.append(('ROUNDEDCORNERS', [5, 5, 5, 5]))
        
        table.setStyle(TableStyle(style_commands))
        return table
    
    def _add_header_footer(self, canvas, doc):
        """Add professional header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6B7280'))
        canvas.drawString(doc.leftMargin, doc.height + doc.topMargin - 20, 
                         "SPECSHARP PROFESSIONAL ESTIMATE")
        canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin - 20,
                              datetime.now().strftime('%B %d, %Y'))
        
        # Header line
        canvas.setStrokeColor(self.BRAND_PRIMARY)
        canvas.setLineWidth(2)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 30,
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 30)
        
        # Footer branding
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#6B7280'))
        canvas.drawCentredString(
            doc.width / 2 + doc.leftMargin,
            doc.bottomMargin - 10,
            "SpecSharp Professional Estimate • specsharp.ai"
        )
        
        # Page number
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#9CA3AF'))
        canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 25,
                              f"Page {doc.page}")
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#E5E7EB'))
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, doc.bottomMargin,
                   doc.width + doc.leftMargin, doc.bottomMargin)
        
        canvas.restoreState()


# Export instance
pdf_export_service = ProfessionalPDFExportService()
