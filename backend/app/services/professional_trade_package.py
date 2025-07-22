from typing import Dict, List, Optional, Any, Tuple
import io
import base64
from datetime import datetime
import json
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Arc
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFont


class ProfessionalTradePackageService:
    """Service for generating professional trade package PDFs matching industry standards"""
    
    def __init__(self):
        self.trade_colors = {
            'electrical': '#FFD700',  # Gold
            'plumbing': '#4169E1',    # Royal Blue
            'mechanical': '#FF4500',  # Orange Red (HVAC)
            'structural': '#708090',  # Slate Gray
            'general': '#228B22'      # Forest Green
        }
        
        self.trade_display_names = {
            'electrical': 'Electrical',
            'plumbing': 'Plumbing',
            'mechanical': 'Mechanical (HVAC)',
            'hvac': 'Mechanical (HVAC)',
            'structural': 'Structural',
            'general': 'General Contractor'
        }
    
    def generate_professional_pdf(self, filtered_data: Dict, trade: str, 
                                 project_data: Dict, schematic_image: str) -> io.BytesIO:
        """Generate a professional PDF document for the trade package"""
        
        buffer = io.BytesIO()
        
        # Create custom canvas for watermark
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Container for all pages
        elements = []
        
        # Define professional styles
        styles = self._create_professional_styles()
        
        # Page 1: Cover Sheet
        elements.extend(self._create_cover_sheet(filtered_data, trade, project_data, styles))
        elements.append(PageBreak())
        
        # Page 2+: Detailed Pricing
        elements.extend(self._create_detailed_pricing(filtered_data, trade, styles))
        
        # Trade-specific pages
        if trade.lower() == 'electrical':
            elements.append(PageBreak())
            elements.extend(self._create_electrical_schedules(filtered_data, styles))
        elif trade.lower() in ['mechanical', 'hvac']:
            elements.append(PageBreak())
            elements.extend(self._create_mechanical_schedules(filtered_data, styles))
        elif trade.lower() == 'plumbing':
            elements.append(PageBreak())
            elements.extend(self._create_plumbing_schedules(filtered_data, styles))
        
        # Last Page: Terms & Conditions
        elements.append(PageBreak())
        elements.extend(self._create_terms_conditions(trade, styles))
        
        # Build PDF with watermark
        doc.build(elements, onFirstPage=self._add_watermark, onLaterPages=self._add_watermark)
        
        buffer.seek(0)
        return buffer
    
    def _create_professional_styles(self) -> Dict[str, ParagraphStyle]:
        """Create professional typography styles"""
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'CompanyName': ParagraphStyle(
                'CompanyName',
                parent=styles['Title'],
                fontSize=28,
                textColor=colors.HexColor('#1976d2'),
                alignment=TA_CENTER,
                spaceAfter=6
            ),
            'DocumentTitle': ParagraphStyle(
                'DocumentTitle',
                parent=styles['Title'],
                fontSize=20,
                textColor=colors.HexColor('#333333'),
                alignment=TA_CENTER,
                spaceAfter=20
            ),
            'SectionHeading': ParagraphStyle(
                'SectionHeading',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1976d2'),
                spaceBefore=12,
                spaceAfter=8,
                borderWidth=1,
                borderColor=colors.HexColor('#1976d2'),
                borderPadding=4
            ),
            'InfoBoxHeading': ParagraphStyle(
                'InfoBoxHeading',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#ffffff'),
                alignment=TA_LEFT,
                leftIndent=0
            ),
            'InfoBoxContent': ParagraphStyle(
                'InfoBoxContent',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_LEFT,
                leftIndent=0
            ),
            'BulletItem': ParagraphStyle(
                'BulletItem',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                bulletIndent=10
            ),
            'Disclaimer': ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=TA_CENTER
            )
        }
        
        # Merge with default styles
        for name, style in custom_styles.items():
            styles.add(style)
        
        return styles
    
    def _create_cover_sheet(self, filtered_data: Dict, trade: str, 
                           project_data: Dict, styles: Dict) -> List:
        """Create professional cover sheet"""
        elements = []
        
        # Company Header
        elements.append(Paragraph("SpecSharp", styles['CompanyName']))
        elements.append(Paragraph("Construction Cost Estimation Platform", styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Document Title
        trade_name = self.trade_display_names.get(trade.lower(), trade.title())
        elements.append(Paragraph(f"{trade_name} Trade Package", styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Project Information Box
        project_info = self._create_project_info_table(project_data, filtered_data, styles)
        elements.append(project_info)
        elements.append(Spacer(1, 0.3*inch))
        
        # Scope of Work Included
        elements.append(Paragraph("SCOPE OF WORK INCLUDED:", styles['SectionHeading']))
        scope_items = self._get_scope_inclusions(trade)
        for item in scope_items:
            elements.append(Paragraph(f"• {item}", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Scope Exclusions
        elements.append(Paragraph("SCOPE EXCLUSIONS:", styles['SectionHeading']))
        exclusion_items = self._get_scope_exclusions(trade)
        for item in exclusion_items:
            elements.append(Paragraph(f"• {item}", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Clarifications & Assumptions
        elements.append(Paragraph("CLARIFICATIONS & ASSUMPTIONS:", styles['SectionHeading']))
        clarifications = self._get_clarifications(trade)
        for item in clarifications:
            elements.append(Paragraph(f"• {item}", styles['BulletItem']))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y')} | Page 1",
            styles['Disclaimer']
        ))
        
        return elements
    
    def _create_project_info_table(self, project_data: Dict, filtered_data: Dict, 
                                  styles: Dict) -> Table:
        """Create project information table"""
        request_data = project_data.get('request_data', {})
        
        # Create info box with blue header
        data = [
            [Paragraph("PROJECT INFORMATION", styles['InfoBoxHeading']), ""],
            ["Project Name:", project_data.get('project_name', 'N/A')],
            ["Location:", request_data.get('location', 'N/A')],
            ["Building Type:", request_data.get('project_type', 'N/A').replace('_', ' ').title()],
            ["Square Footage:", f"{request_data.get('square_footage', 0):,} SF"],
            ["Number of Floors:", str(request_data.get('num_floors', 1))],
            ["", ""],
            ["Trade Package Total:", f"${filtered_data.get('total_cost', 0):,.2f}"],
            ["Cost per SF:", f"${filtered_data.get('total_cost', 0) / request_data.get('square_footage', 1):.2f}"]
        ]
        
        table = Table(data, colWidths=[2.5*inch, 3.5*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Content formatting
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            
            # Highlight totals
            ('BACKGROUND', (0, -2), (-1, -1), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
            
            # Box styling
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
            ('GRID', (0, 1), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        return table
    
    def _create_detailed_pricing(self, filtered_data: Dict, trade: str, styles: Dict) -> List:
        """Create detailed pricing pages"""
        elements = []
        
        # Page header
        elements.append(Paragraph(f"{self.trade_display_names.get(trade.lower(), trade.title())} - Detailed Pricing", 
                                styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Summary table
        summary_data = [
            ["Category", "Subtotal", "% of Total"]
        ]
        
        total_subtotal = filtered_data.get('subtotal', 0)
        
        for category in filtered_data.get('categories', []):
            cat_subtotal = category.get('subtotal', 0)
            percentage = (cat_subtotal / total_subtotal * 100) if total_subtotal > 0 else 0
            summary_data.append([
                category['name'],
                f"${cat_subtotal:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Detailed breakdown by category
        for category in filtered_data.get('categories', []):
            # Category header
            elements.append(Paragraph(category['name'], styles['SectionHeading']))
            
            # Systems table
            systems_data = [
                ["Description", "Quantity", "Unit", "Unit Price", "Total"]
            ]
            
            for system in category.get('systems', []):
                systems_data.append([
                    system['name'],
                    f"{system['quantity']:,}" if isinstance(system['quantity'], int) else f"{system['quantity']:,.1f}",
                    system['unit'],
                    f"${system['unit_cost']:,.2f}",
                    f"${system['total_cost']:,.2f}"
                ])
            
            # Add category subtotal
            systems_data.append([
                "Category Subtotal", "", "", "", f"${category.get('subtotal', 0):,.2f}"
            ])
            
            systems_table = Table(systems_data, colWidths=[3*inch, 0.8*inch, 0.6*inch, 1*inch, 1.1*inch])
            systems_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -2), 0.5, colors.lightgrey),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            
            elements.append(KeepTogether([systems_table, Spacer(1, 0.2*inch)]))
        
        # Grand total section
        elements.append(Spacer(1, 0.3*inch))
        total_data = [
            ["", "", "", "Subtotal:", f"${filtered_data.get('subtotal', 0):,.2f}"],
            ["", "", "", f"Contingency ({filtered_data.get('contingency_percentage', 10)}%):", 
             f"${filtered_data.get('contingency_amount', 0):,.2f}"],
            ["", "", "", "TOTAL:", f"${filtered_data.get('total_cost', 0):,.2f}"]
        ]
        
        total_table = Table(total_data, colWidths=[3*inch, 0.8*inch, 0.6*inch, 1.5*inch, 1.1*inch])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica'),
            ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTSIZE', (-2, -1), (-1, -1), 12),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (3, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (-2, -1), (-1, -1), 2, colors.black),
            ('BACKGROUND', (-2, -1), (-1, -1), colors.HexColor('#e3f2fd')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(total_table)
        
        return elements
    
    def _create_electrical_schedules(self, filtered_data: Dict, styles: Dict) -> List:
        """Create electrical-specific schedules"""
        elements = []
        
        elements.append(Paragraph("Electrical Schedules", styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Panel Schedule Template
        elements.append(Paragraph("Panel Schedule", styles['SectionHeading']))
        panel_data = [
            ["Circuit", "Description", "Load (VA)", "Breaker", "Wire Size"],
            ["1", "Lighting - Zone 1", "1,800", "20A", "#12"],
            ["3", "Lighting - Zone 2", "1,800", "20A", "#12"],
            ["5", "Receptacles - Office", "1,500", "20A", "#12"],
            ["7", "HVAC Unit 1", "4,800", "30A", "#10"],
            ["9", "SPARE", "-", "20A", "-"],
            ["", "Panel Total:", "9,900 VA", "", ""]
        ]
        
        panel_table = Table(panel_data, colWidths=[0.8*inch, 2.5*inch, 1*inch, 0.8*inch, 0.9*inch])
        panel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(panel_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Fixture Schedule
        elements.append(Paragraph("Lighting Fixture Schedule", styles['SectionHeading']))
        fixture_data = [
            ["Type", "Description", "Watts", "Voltage", "Qty"],
            ["A", "LED High Bay - 150W", "150", "277V", "24"],
            ["B", "2x4 LED Troffer - 40W", "40", "277V", "36"],
            ["C", "Wall Pack - 40W", "40", "120V", "8"],
            ["D", "Exit Sign - LED", "5", "120/277V", "12"],
            ["E", "Emergency Light", "12", "120/277V", "8"]
        ]
        
        fixture_table = Table(fixture_data, colWidths=[0.8*inch, 2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        fixture_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(fixture_table)
        
        return elements
    
    def _create_mechanical_schedules(self, filtered_data: Dict, styles: Dict) -> List:
        """Create mechanical/HVAC-specific schedules"""
        elements = []
        
        elements.append(Paragraph("Mechanical Equipment Schedule", styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Equipment Schedule
        elements.append(Paragraph("HVAC Equipment Schedule", styles['SectionHeading']))
        equipment_data = [
            ["Tag", "Equipment Type", "Capacity", "Model", "Location"],
            ["RTU-1", "Rooftop Unit", "40 Ton", "Carrier 48TC", "Roof"],
            ["RTU-2", "Rooftop Unit", "40 Ton", "Carrier 48TC", "Roof"],
            ["EF-1", "Exhaust Fan", "1,000 CFM", "Greenheck SWB", "Roof"],
            ["EF-2", "Exhaust Fan", "500 CFM", "Greenheck CW", "Wall"],
            ["VAV-1", "VAV Box w/ Reheat", "800 CFM", "Price SDR", "Ceiling"]
        ]
        
        equipment_table = Table(equipment_data, colWidths=[0.8*inch, 1.8*inch, 1*inch, 1.5*inch, 0.9*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff4500')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(equipment_table)
        
        return elements
    
    def _create_plumbing_schedules(self, filtered_data: Dict, styles: Dict) -> List:
        """Create plumbing-specific schedules"""
        elements = []
        
        elements.append(Paragraph("Plumbing Schedules", styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Fixture Count Summary
        elements.append(Paragraph("Fixture Count Summary", styles['SectionHeading']))
        fixture_data = [
            ["Fixture Type", "Men's", "Women's", "Unisex", "Total"],
            ["Water Closets", "2", "3", "1", "6"],
            ["Urinals", "2", "-", "-", "2"],
            ["Lavatories", "2", "2", "1", "5"],
            ["Service Sinks", "-", "-", "2", "2"],
            ["Kitchen Sinks", "-", "-", "1", "1"],
            ["Drinking Fountains", "-", "-", "2", "2"]
        ]
        
        fixture_table = Table(fixture_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        fixture_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4169e1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(fixture_table)
        
        return elements
    
    def _create_terms_conditions(self, trade: str, styles: Dict) -> List:
        """Create terms and conditions page"""
        elements = []
        
        elements.append(Paragraph("Terms & Conditions", styles['DocumentTitle']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Payment Terms
        elements.append(Paragraph("PAYMENT TERMS", styles['SectionHeading']))
        elements.append(Paragraph("• Net 30 days from invoice date", styles['BulletItem']))
        elements.append(Paragraph("• 10% retainage held until project completion", styles['BulletItem']))
        elements.append(Paragraph("• Progress payments based on work completed", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Warranty
        elements.append(Paragraph("WARRANTY", styles['SectionHeading']))
        elements.append(Paragraph("• One (1) year warranty on all labor", styles['BulletItem']))
        elements.append(Paragraph("• Manufacturer's warranty on all materials and equipment", styles['BulletItem']))
        elements.append(Paragraph("• Warranty period begins at substantial completion", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Insurance Requirements
        elements.append(Paragraph("INSURANCE REQUIREMENTS", styles['SectionHeading']))
        elements.append(Paragraph("• General Liability: $2,000,000 per occurrence", styles['BulletItem']))
        elements.append(Paragraph("• Workers Compensation: As required by state law", styles['BulletItem']))
        elements.append(Paragraph("• Additional insured endorsement required", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Schedule Assumptions
        elements.append(Paragraph("SCHEDULE ASSUMPTIONS", styles['SectionHeading']))
        elements.append(Paragraph("• Normal working hours: 7:00 AM - 3:30 PM, Monday-Friday", styles['BulletItem']))
        elements.append(Paragraph("• No premium time included in base bid", styles['BulletItem']))
        elements.append(Paragraph("• Continuous access to work areas", styles['BulletItem']))
        elements.append(Paragraph("• Dry and weather-tight conditions", styles['BulletItem']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Add/Deduct Unit Pricing
        elements.append(Paragraph("ADD/DEDUCT UNIT PRICING", styles['SectionHeading']))
        
        unit_pricing = self._get_unit_pricing(trade)
        pricing_data = [["Description", "Add", "Deduct"]]
        pricing_data.extend(unit_pricing)
        
        pricing_table = Table(pricing_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        pricing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(pricing_table)
        
        # Validity
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(
            "This proposal is valid for 30 days from the date of issue.",
            styles['Normal']
        ))
        
        return elements
    
    def _get_scope_inclusions(self, trade: str) -> List[str]:
        """Get trade-specific scope inclusions"""
        inclusions = {
            'electrical': [
                "All materials and labor for complete electrical systems",
                "Main service entrance and distribution equipment",
                "Branch circuit wiring and devices",
                "Lighting fixtures and controls",
                "Fire alarm system",
                "Testing and commissioning",
                "As-built drawings"
            ],
            'mechanical': [
                "All HVAC equipment and materials",
                "Ductwork and insulation",
                "Controls and thermostats",
                "Equipment startup and commissioning",
                "Test and balance report",
                "One year maintenance agreement",
                "Operating and maintenance manuals"
            ],
            'plumbing': [
                "All plumbing fixtures and trim",
                "Water distribution piping",
                "Sanitary waste and vent piping",
                "Storm drainage system",
                "Natural gas piping",
                "Pipe insulation",
                "Testing and inspections"
            ],
            'structural': [
                "Foundations and footings",
                "Structural steel frame",
                "Metal deck and concrete slabs",
                "Miscellaneous metals",
                "Fireproofing as required",
                "Anchor bolts and embeds",
                "Shop drawings and engineering"
            ]
        }
        
        return inclusions.get(trade.lower(), [
            "All labor and materials as specified",
            "Coordination with other trades",
            "Clean up of work areas",
            "Safety compliance"
        ])
    
    def _get_scope_exclusions(self, trade: str) -> List[str]:
        """Get trade-specific scope exclusions"""
        exclusions = {
            'electrical': [
                "Temporary power for construction",
                "Utility company fees and connections",
                "Low voltage systems (security, data, AV)",
                "Lightning protection",
                "Photovoltaic systems",
                "Generator systems (unless specified)"
            ],
            'mechanical': [
                "Electrical connections (by others)",
                "Structural supports beyond standard hangers",
                "Fire dampers in rated walls",
                "Kitchen exhaust hoods",
                "Refrigeration systems",
                "Building automation beyond HVAC"
            ],
            'plumbing': [
                "Site utilities beyond 5' from building",
                "Fire sprinkler systems",
                "Medical gas systems",
                "Electrical connections to equipment",
                "Water treatment systems",
                "Sump pumps and ejectors (unless noted)"
            ],
            'structural': [
                "Excavation and backfill",
                "Dewatering",
                "Concrete testing",
                "Special inspections",
                "Architectural metals",
                "Metal building systems"
            ]
        }
        
        return exclusions.get(trade.lower(), [
            "Permits and fees",
            "Bonds (unless specified)",
            "Premium time labor",
            "Winter conditions",
            "Rock excavation"
        ])
    
    def _get_clarifications(self, trade: str) -> List[str]:
        """Get trade-specific clarifications"""
        clarifications = {
            'electrical': [
                "All work per current NEC and local codes",
                "Normal working hours assumed (7 AM - 3:30 PM)",
                "Building will be weather-tight prior to rough-in",
                "Adequate laydown and storage area provided",
                "3-phase power available at site"
            ],
            'mechanical': [
                "Design based on ASHRAE standards",
                "Roof structure adequate for equipment loads",
                "Natural gas available at property line",
                "Electrical power provided to unit disconnects",
                "Controls specified as DDC system"
            ],
            'plumbing': [
                "Water and sewer available at property line",
                "Fixtures to be commercial grade",
                "All work per current IPC and local codes",
                "Sleeve and core drilling by others",
                "Adequate ceiling space for piping"
            ],
            'structural': [
                "Design based on current IBC",
                "Soil bearing capacity as noted in geotech report",
                "No unusual site conditions anticipated",
                "Shop drawings required prior to fabrication",
                "Field welding by certified welders only"
            ]
        }
        
        base_clarifications = [
            "Pricing based on plans and specifications dated " + datetime.now().strftime('%B %d, %Y'),
            "Continuous and uninterrupted access to work areas",
            "No asbestos or hazardous materials present",
            "Sales tax included where applicable"
        ]
        
        return clarifications.get(trade.lower(), []) + base_clarifications
    
    def _get_unit_pricing(self, trade: str) -> List[List[str]]:
        """Get trade-specific unit pricing for add/deduct"""
        pricing = {
            'electrical': [
                ["Additional 20A Circuit", "$850.00", "$680.00"],
                ["Duplex Receptacle", "$125.00", "$100.00"],
                ["2x4 LED Fixture", "$225.00", "$180.00"],
                ["Switch/Dimmer", "$95.00", "$75.00"],
                ["Data Outlet (Cat6)", "$185.00", "$150.00"]
            ],
            'mechanical': [
                ["Additional Ton of Cooling", "$1,500.00", "$1,200.00"],
                ["VAV Box w/ Reheat", "$2,200.00", "$1,750.00"],
                ["Supply/Return Diffuser", "$185.00", "$150.00"],
                ["Thermostat Zone", "$550.00", "$440.00"],
                ["Linear Ft of Ductwork", "$45.00", "$36.00"]
            ],
            'plumbing': [
                ["Water Closet", "$850.00", "$680.00"],
                ["Lavatory", "$650.00", "$520.00"],
                ["Floor Drain", "$425.00", "$340.00"],
                ["Hose Bibb", "$325.00", "$260.00"],
                ["Gas Connection", "$450.00", "$360.00"]
            ],
            'structural': [
                ["Ton of Structural Steel", "$3,200.00", "$2,560.00"],
                ["CY of Concrete", "$185.00", "$148.00"],
                ["SF of Metal Deck", "$8.50", "$6.80"],
                ["LF of Foundation", "$125.00", "$100.00"],
                ["Embed Plate", "$275.00", "$220.00"]
            ]
        }
        
        return pricing.get(trade.lower(), [
            ["Additional Work Hour", "$95.00", "$76.00"],
            ["Material Handling", "$125.00", "$100.00"],
            ["Equipment Day", "$850.00", "$680.00"]
        ])
    
    def _add_watermark(self, canvas_obj, doc):
        """Add watermark to each page"""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 40)
        canvas_obj.setFillColorRGB(0.9, 0.9, 0.9)
        canvas_obj.rotate(45)
        canvas_obj.drawCentredString(
            400, 100,
            "PRELIMINARY - NOT FOR CONSTRUCTION"
        )
        canvas_obj.restoreState()
        
        # Add page numbers
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColorRGB(0.4, 0.4, 0.4)
        canvas_obj.drawRightString(
            letter[0] - inch,
            0.75 * inch,
            f"Page {canvas_obj._pageNumber}"
        )
    
    def create_improved_schematic(self, floor_plan: Dict, trade: str, 
                                 request_data: Dict) -> str:
        """Create improved, clearer trade schematics"""
        fig, ax = plt.subplots(1, 1, figsize=(11, 8.5))
        
        # Get building dimensions
        square_footage = request_data.get('square_footage', 10000)
        aspect_ratio = 1.5
        width = np.sqrt(square_footage / aspect_ratio)
        height = width * aspect_ratio
        
        # Scale to fit page with margins
        scale = min(9 / (width / 100), 6.5 / (height / 100))
        width_scaled = width * scale / 100
        height_scaled = height * scale / 100
        
        # Center the building
        x_offset = (11 - width_scaled) / 2
        y_offset = (8.5 - height_scaled) / 2
        
        # Draw building outline
        building = FancyBboxPatch(
            (x_offset, y_offset), width_scaled, height_scaled,
            boxstyle="round,pad=0.1",
            linewidth=2, edgecolor='black',
            facecolor='white', alpha=0.9
        )
        ax.add_patch(building)
        
        # Add trade-specific elements
        if trade.lower() == 'electrical':
            self._add_electrical_schematic(ax, x_offset, y_offset, width_scaled, height_scaled)
        elif trade.lower() in ['mechanical', 'hvac']:
            self._add_mechanical_schematic(ax, x_offset, y_offset, width_scaled, height_scaled)
        elif trade.lower() == 'plumbing':
            self._add_plumbing_schematic(ax, x_offset, y_offset, width_scaled, height_scaled)
        
        # Add title and legend
        ax.text(5.5, 7.8, f"{self.trade_display_names.get(trade.lower(), trade)} Schematic",
                fontsize=16, ha='center', weight='bold')
        
        self._add_legend(ax, trade)
        
        # Add scale
        ax.text(x_offset, y_offset - 0.3, f"Scale: 1/8\" = 1'-0\"", fontsize=10)
        
        # Configure plot
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 8.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        # Convert to base64
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    
    def _add_electrical_schematic(self, ax, x, y, w, h):
        """Add electrical schematic elements"""
        # Main panel
        panel = Rectangle((x + 0.2, y + h - 0.6), 0.3, 0.5,
                         facecolor='yellow', edgecolor='black', linewidth=2)
        ax.add_patch(panel)
        ax.text(x + 0.35, y + h - 0.35, 'MDP', ha='center', va='center', fontsize=8, weight='bold')
        
        # Distribution lines
        for i in range(3):
            y_pos = y + h * (0.7 - i * 0.25)
            ax.plot([x + 0.5, x + w - 0.5], [y_pos, y_pos], 'k-', linewidth=1.5)
            ax.plot([x + w * 0.3, x + w * 0.3], [y_pos, y_pos - 0.2], 'k-', linewidth=1)
            ax.plot([x + w * 0.7, x + w * 0.7], [y_pos, y_pos - 0.2], 'k-', linewidth=1)
            
            # Panels
            panel = Rectangle((x + w * 0.3 - 0.1, y_pos - 0.3), 0.2, 0.2,
                            facecolor='yellow', edgecolor='black')
            ax.add_patch(panel)
            ax.text(x + w * 0.3, y_pos - 0.2, f'P{i+1}', ha='center', va='center', fontsize=6)
    
    def _add_mechanical_schematic(self, ax, x, y, w, h):
        """Add mechanical/HVAC schematic elements"""
        # RTUs on roof
        for i in range(2):
            x_pos = x + w * (0.3 + i * 0.4)
            rtu = Rectangle((x_pos - 0.15, y + h - 0.3), 0.3, 0.25,
                           facecolor='orange', edgecolor='black', linewidth=2)
            ax.add_patch(rtu)
            ax.text(x_pos, y + h - 0.175, f'RTU-{i+1}', ha='center', va='center', fontsize=6, weight='bold')
            
            # Ductwork
            ax.plot([x_pos, x_pos], [y + h - 0.3, y + h * 0.7], 'b-', linewidth=3)
            ax.plot([x_pos, x + w * 0.2], [y + h * 0.7, y + h * 0.7], 'b-', linewidth=3)
            ax.plot([x_pos, x + w * 0.8], [y + h * 0.7, y + h * 0.7], 'b-', linewidth=3)
    
    def _add_plumbing_schematic(self, ax, x, y, w, h):
        """Add plumbing schematic elements"""
        # Water heater
        wh = Circle((x + 0.3, y + 0.3), 0.15, facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.add_patch(wh)
        ax.text(x + 0.3, y + 0.3, 'WH', ha='center', va='center', fontsize=6, weight='bold')
        
        # Main water line
        ax.plot([x + 0.45, x + w - 0.2], [y + 0.3, y + 0.3], 'b-', linewidth=2)
        
        # Risers
        for i in range(2):
            x_pos = x + w * (0.3 + i * 0.4)
            ax.plot([x_pos, x_pos], [y + 0.3, y + h - 0.3], 'b-', linewidth=1.5)
            ax.plot([x_pos - 0.1, x_pos + 0.1], [y + h * 0.5, y + h * 0.5], 'b-', linewidth=1)
    
    def _add_legend(self, ax, trade):
        """Add legend for symbols"""
        legend_items = {
            'electrical': [
                ('yellow', 'Electrical Panel'),
                ('black line', 'Power Distribution'),
            ],
            'mechanical': [
                ('orange', 'HVAC Equipment'),
                ('blue line', 'Ductwork'),
            ],
            'plumbing': [
                ('blue', 'Water Lines'),
                ('light blue', 'Equipment'),
            ]
        }
        
        items = legend_items.get(trade.lower(), [])
        if items:
            legend_elements = []
            for color, label in items:
                if 'line' in color:
                    element = Line2D([0], [0], color=color.split()[0], linewidth=2, label=label)
                else:
                    element = Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black', label=label)
                legend_elements.append(element)
            
            ax.legend(handles=legend_elements, loc='lower right', frameon=True, 
                     fancybox=True, shadow=True)


# Create service instance
professional_trade_package_service = ProfessionalTradePackageService()