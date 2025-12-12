from typing import Dict, List, Optional, Any
import io
from datetime import datetime
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
        """Generate a premium PDF report"""
        buffer = io.BytesIO()
        
        # Create PDF with custom page setup
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
            title=f"{project_data.get('project_name', 'Construction Project')} - Cost Estimate",
            author="SpecSharp Professional",
            subject="Construction Cost Estimate"
        )
        
        # Build content
        story: List[Any] = []
        
        # Generate executive summary data
        executive_summary = executive_summary_service.generate_executive_summary(project_data)
        
        # EXECUTIVE OVERVIEW REPORT (STRICT 3 PAGES)
        story.extend(self._create_investment_decision_page(project_data, executive_summary))
        story.append(PageBreak())
        story.extend(self._create_construction_reality_page(project_data, executive_summary))
        story.append(PageBreak())
        story.extend(self._create_assumptions_next_steps_page(project_data, executive_summary))
        
        # Build PDF with custom canvas for headers/footers
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        buffer.seek(0)
        return buffer
    
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
