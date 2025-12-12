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
        
        # EXECUTIVE OVERVIEW (max 3 pages)
        # Page 1: Cover
        story.extend(self._create_cover_page(project_data, client_name))
        story.append(PageBreak())

        # Page 2: Executive Overview (no charts, no detailed breakdown)
        story.extend(self._create_executive_overview_page(project_data, executive_summary))
        story.append(PageBreak())

        # Page 3: Assumptions & Notes
        story.extend(self._create_assumptions_page(project_data, executive_summary))
        
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

    def _create_executive_overview_page(self, project_data: Dict, executive_summary: Dict) -> List:
        """Create a concise executive overview page without charts/detail tables."""
        elements: List[Any] = []

        elements.append(Paragraph("EXECUTIVE OVERVIEW", self.styles['SectionHeader']))

        # Project overview (2-column table)
        overview = executive_summary.get('project_overview', {}) or {}
        overview_rows: List[List[str]] = []
        for key, value in overview.items():
            label = key.replace('_', ' ').title() + ':'
            overview_rows.append([label, str(value)])
        if overview_rows:
            overview_table = Table(overview_rows, colWidths=[2*inch, 4*inch])
            overview_table.setStyle(self._safe_table_style([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('TEXTCOLOR', (0, 0), (0, -1), self.BRAND_DARK),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.extend(self._card("Project Overview", [overview_table], keep_together=True))

        # Cost snapshot metrics
        total_cost = (
            project_data.get('construction_total')
            or project_data.get('total_cost')
            or 0
        )
        cost_per_sqft = project_data.get('cost_per_sqft') or 0
        request_data = project_data.get('request_data') or {}
        square_footage = request_data.get('square_footage') or 0
        snapshot_rows = [
            ['Total Project Cost', format_currency(total_cost)],
            ['Cost per SF', f"${cost_per_sqft:,.2f}"],
            ['Total Area', f"{square_footage:,.0f} SF" if isinstance(square_footage, (int, float)) else str(square_footage)],
        ]
        snapshot_table = Table(snapshot_rows, colWidths=[2.5*inch, 3.5*inch])
        snapshot_table.setStyle(self._safe_table_style([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_ACCENT),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        elements.extend(self._card("Cost Snapshot", [snapshot_table], keep_together=True))

        # Top trades (table only, no pie chart)
        categories = project_data.get('categories', []) or []
        cat_totals = [
            (cat.get('name', 'Trade'), self._category_total(cat))
            for cat in categories
        ]
        cat_totals = [(name, total) for name, total in cat_totals if total and total > 0]
        cat_totals.sort(key=lambda item: item[1], reverse=True)
        top_trades = cat_totals[:6]
        if top_trades:
            trade_rows = [['Trade', 'Cost', 'Share']]
            denominator = float(total_cost) if total_cost else sum(total for _, total in top_trades) or 1.0
            for name, subtotal in top_trades:
                pct = (float(subtotal) / denominator) * 100.0 if denominator else 0.0
                trade_rows.append([name, format_currency(subtotal), f"{pct:.1f}%"])
            trade_table = Table(trade_rows, colWidths=[2.6*inch, 2.0*inch, 1.4*inch])
            trade_table.setStyle(self._safe_table_style([
                ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.BRAND_LIGHT]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ]))
            elements.extend(self._card("Top Trade Drivers", [trade_table]))

        return elements
    
    def _create_executive_summary_page(self, project_data: Dict, executive_summary: Dict) -> List:
        """Create executive summary page"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        # Project overview section
        elements.append(Paragraph("Project Overview", self.styles['SubsectionHeader']))
        
        overview_data = []
        overview = executive_summary.get('project_overview', {})
        for key, value in overview.items():
            overview_data.append([key.replace('_', ' ').title() + ':', str(value)])
        
        overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
        overview_table.setStyle(self._safe_table_style([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.BRAND_DARK),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(KeepTogether([overview_table]))
        elements.append(Spacer(1, 0.3*inch))
        
        # Cost summary with visual emphasis
        # Build a premium "Cost Summary" card that keeps chart + table together
        cost_summary_flowables: List[Any] = []

        # Create pie chart for trade distribution
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 100
        pie.y = 20
        pie.width = 150
        pie.height = 150
        
        # Add data to pie chart
        categories = project_data.get('categories', [])
        category_totals = [(cat, self._category_total(cat)) for cat in categories]
        non_zero_totals = [(cat, total) for cat, total in category_totals if total > 0]
        pie_source = non_zero_totals if non_zero_totals else category_totals
        pie.data = [total for _, total in pie_source] or [1]
        pie.labels = [
            f"{cat['name']}\n({format_percentage(total / max(project_data.get('total_cost', 1), 1), 0)})"
            for cat, total in pie_source
        ]
        
        # Professional colors for pie slices
        pie.slices.strokeWidth = 0.5
        pie.slices.strokeColor = colors.white
        slice_colors = [
            self.BRAND_PRIMARY, self.BRAND_SECONDARY, self.BRAND_ACCENT,
            colors.HexColor('#F59E0B'), colors.HexColor('#EF4444'),
            colors.HexColor('#8B5CF6'), colors.HexColor('#EC4899')
        ]

        for i, (cat, _) in enumerate(pie_source):
            pie.slices[i].fillColor = slice_colors[i % len(slice_colors)]
            pie.slices[i].labelRadius = 1.2
            pie.slices[i].fontName = 'Helvetica'
            pie.slices[i].fontSize = 9

        drawing.add(pie)
        cost_summary_flowables.append(drawing)
        
        # Trade breakdown table
        total_construction = (
            project_data.get('construction_total')
            or project_data.get('total_cost')
            or sum(total for _, total in category_totals)
            or 0
        )

        trade_data = [['Trade', 'Cost', 'Percentage']]
        for cat, subtotal in category_totals:
            pct_value = self._calculate_trade_percentage(cat, subtotal, total_construction)
            trade_data.append([
                cat.get('name', 'Trade'),
                format_currency(subtotal),
                f"{pct_value:.1f}%"
            ])
        
        trade_data.append([
            'TOTAL',
            format_currency(total_construction),
            '100.0%' if total_construction > 0 else '—'
        ])

        trade_table = Table(trade_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        trade_table.setStyle(self._safe_table_style([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('ALIGN', (1, 1), (2, -1), 'RIGHT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, self.BRAND_LIGHT]),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FEF3C7')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, self.BRAND_DARK),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        cost_summary_flowables.append(Spacer(1, 0.2*inch))
        cost_summary_flowables.append(trade_table)

        # Allow splitting when the trade table spans many rows
        keep_cost_summary_together = len(category_totals) <= 6
        elements.extend(self._card("Cost Summary", cost_summary_flowables, keep_together=keep_cost_summary_together))
        
        # Developer-specific metrics
        developer_metrics = executive_summary.get('developer_metrics', {})
        if developer_metrics:
            dev_flowables: List[Any] = []

            # Create metrics table
            metrics_data = []
            if 'cost_per_room' in developer_metrics:
                metrics_data.append(['Cost per Room:', developer_metrics['cost_per_room']])
                metrics_data.append(['Total Rooms:', str(developer_metrics.get('rooms_count', 'N/A'))])
            elif 'cost_per_bed' in developer_metrics:
                metrics_data.append(['Cost per Bed:', developer_metrics['cost_per_bed']])
                metrics_data.append(['Total Beds:', str(developer_metrics.get('beds_count', 'N/A'))])
            elif 'cost_per_unit' in developer_metrics:
                metrics_data.append(['Cost per Unit:', developer_metrics['cost_per_unit']])
                metrics_data.append(['Total Units:', str(developer_metrics.get('units_count', 'N/A'))])
            elif 'cost_per_student' in developer_metrics:
                metrics_data.append(['Cost per Student:', developer_metrics['cost_per_student']])
                metrics_data.append(['Student Capacity:', str(developer_metrics.get('student_capacity', 'N/A'))])
            elif 'cost_per_rsf' in developer_metrics:
                metrics_data.append(['Cost per RSF:', developer_metrics['cost_per_rsf']])
                metrics_data.append(['Rentable SF:', developer_metrics.get('rsf', 'N/A')])
                if 'cost_per_desk' in developer_metrics:
                    metrics_data.append(['Cost per Desk:', developer_metrics['cost_per_desk']])
                    metrics_data.append(['Desk Capacity:', str(developer_metrics.get('desk_capacity', 'N/A'))])

            if metrics_data:
                dev_metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
                dev_metrics_table.setStyle(self._safe_table_style([
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('TEXTCOLOR', (1, 0), (1, -1), self.BRAND_ACCENT),
                    ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                    ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F4F8')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))

                dev_flowables.append(dev_metrics_table)
                elements.extend(self._card("Developer Metrics", dev_flowables, keep_together=True))
        
        return elements
    
    def _create_cost_breakdown_page(self, project_data: Dict) -> List:
        """Create detailed cost breakdown page"""
        elements = []
        
        elements.append(Paragraph("DETAILED COST BREAKDOWN", self.styles['SectionHeader']))
        
        # Create detailed breakdown by category
        for category in project_data.get('categories', []):
            trade_name = category.get('name', 'Trade')
            category_subtotal = self._category_total(category)
            systems = category.get('systems') or []
            placeholder_scope = False
            if len(systems) == 1:
                system = systems[0]
                system_name = (system.get('name') or '').strip().lower()
                quantity = system.get('quantity')
                trade_normalized = (trade_name or '').strip().lower()
                if (not system_name or system_name.startswith(trade_normalized)) and (quantity in (None, 1)):
                    placeholder_scope = True
            
            if not systems or placeholder_scope:
                elements.extend(self._card(
                    f"{trade_name}",
                    [Paragraph(f"<b>Total:</b> {format_currency(category_subtotal)}", self.styles['BodyTextDark'])],
                    keep_together=True
                ))
                continue

            # Build a "card" per trade so tables never awkwardly split
            trade_flowables: List[Any] = []
            
            # Systems table
            systems_data = [['System', 'Quantity', 'Unit', 'Unit Cost', 'Total Cost']]
            
            for system in systems:
                quantity = system.get('quantity') or 0
                unit = system.get('unit') or ''
                unit_cost = system.get('unit_cost') or 0
                total_cost = system.get('total_cost') or 0
                systems_data.append([
                    system.get('name', 'System'),
                    f"{quantity:,.0f}" if isinstance(quantity, (int, float)) else str(quantity),
                    unit,
                    f"${unit_cost:,.2f}",
                    format_currency(total_cost)
                ])
            
            # Add subtotal
            systems_data.append([
                'Subtotal',
                '',
                '',
                '',
                format_currency(category_subtotal)
            ])
            
            systems_table = Table(systems_data, colWidths=[2.5*inch, 1*inch, 0.7*inch, 1*inch, 1.3*inch])
            systems_table.setStyle(self._safe_table_style([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.BRAND_SECONDARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Data
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F9FAFB')]),

                # Subtotal row
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), self.BRAND_LIGHT),
                ('LINEABOVE', (0, -1), (-1, -1), 1, self.BRAND_DARK),

                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            trade_flowables.append(systems_table)
            elements.extend(self._card(f"{trade_name} Systems", trade_flowables))

        return elements
    
    def _create_trade_analysis_page(self, project_data: Dict) -> List:
        """Create trade analysis page with charts"""
        elements = []
        
        elements.append(Paragraph("TRADE ANALYSIS", self.styles['SectionHeader']))
        
        # Cost comparison bar chart
        drawing = Drawing(500, 250)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 150
        bc.width = 400
        
        categories = project_data.get('categories', [])
        category_totals = [self._category_total(cat) for cat in categories]
        bc.data = [category_totals]
        bc.categoryAxis.categoryNames = [cat['name'] for cat in categories]
        
        bc.bars[0].fillColor = self.BRAND_PRIMARY
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = (max(category_totals) * 1.2) if category_totals else 0
        bc.valueAxis.labelTextFormat = '$%0.0f'
        bc.categoryAxis.labels.angle = 30
        bc.categoryAxis.labels.boxAnchor = 'ne'
        
        drawing.add(bc)
        elements.append(drawing)
        
        # Trade summaries
        elements.append(Paragraph("Trade Package Summaries", self.styles['SubsectionHeader']))
        
        trade_summaries = project_data.get('trade_summaries', {})
        for trade, summary in trade_summaries.items():
            elements.append(Paragraph(
                f"<font color='{self._hex(self.BRAND_PRIMARY)}'><b>{trade.upper()}</b></font> - " + 
                f"<font color='{self._hex(self.BRAND_ACCENT)}'>{format_currency(summary.get('total', 0))}</font>",
                self.styles['BodyTextDark']
            ))
            
            if 'description' in summary:
                elements.append(Paragraph(
                    summary['description'],
                    self.styles['ProfessionalBody']
                ))
            
            elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_assumptions_page(self, project_data: Dict, executive_summary: Dict) -> List:
        """Create assumptions and notes page"""
        elements = []
        
        elements.append(Paragraph("ASSUMPTIONS & NOTES", self.styles['SectionHeader']))
        
        # Key assumptions
        elements.append(Paragraph("Key Assumptions", self.styles['SubsectionHeader']))
        
        assumptions = executive_summary.get('key_assumptions', [])
        for assumption in assumptions:
            elements.append(Paragraph(
                f"• {assumption}",
                self.styles['ProfessionalBody']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Exclusions
        elements.append(Paragraph("Exclusions", self.styles['SubsectionHeader']))
        
        exclusions = [
            "Site acquisition costs",
            "Financing and interest charges",
            "Professional fees (architectural, engineering, legal)",
            "Permits and regulatory fees",
            "Furniture, fixtures, and equipment (FF&E)",
            "Landscaping and exterior site work",
            "Utility connection fees",
            "Testing and commissioning"
        ]
        
        for exclusion in exclusions:
            elements.append(Paragraph(
                f"• {exclusion}",
                self.styles['ProfessionalBody']
            ))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms and conditions
        elements.append(Paragraph("Terms & Conditions", self.styles['SubsectionHeader']))
        
        elements.append(Paragraph(
            "This estimate is valid for 30 days from the date of generation. Prices are subject to change based on market conditions, "
            "material availability, and labor rates. This estimate is for budgetary purposes only and should not be considered a "
            "firm bid or contract price.",
            self.styles['ProfessionalBody']
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
