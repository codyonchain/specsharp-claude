from typing import Dict, List, Optional, Any
import io
import base64
from datetime import datetime
import json
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image as PILImage
import numpy as np
from app.services.detailed_trade_service import detailed_trade_service
from app.services.professional_trade_package import professional_trade_package_service

class TradePackageService:
    def __init__(self):
        self.trade_colors = {
            'Electrical': '#FFD700',  # Gold
            'Plumbing': '#4169E1',    # Royal Blue
            'Mechanical': '#FF4500',  # Orange Red (HVAC)
            'Structural': '#708090',  # Slate Gray
            'General': '#228B22'      # Forest Green
        }
        
    def generate_trade_package(self, project_data: Dict, trade: str) -> Dict[str, Any]:
        """Generate a complete trade package with PDF, CSV, and schematic"""
        
        # Filter scope data for the specific trade
        filtered_data = self._filter_scope_by_trade(project_data, trade)
        
        # Skip enhancement since we already have detailed categories from the engine
        # The engine already provides detailed breakdowns for electrical, hvac, and plumbing
        
        # Generate improved trade-specific schematic
        schematic_image = professional_trade_package_service.create_improved_schematic(
            project_data.get('floor_plan', {}), 
            trade,
            project_data.get('request_data', {})
        )
        
        # Generate professional PDF document
        pdf_buffer = professional_trade_package_service.generate_professional_pdf(
            filtered_data, 
            trade, 
            project_data,
            schematic_image
        )
        
        # Generate CSV data
        csv_buffer = self._generate_csv_data(filtered_data, trade)
        
        # Generate preview data
        preview_data = self._generate_preview_data(filtered_data, trade, schematic_image)
        
        return {
            'trade': trade,
            'pdf': base64.b64encode(pdf_buffer.getvalue()).decode('utf-8'),
            'csv': base64.b64encode(csv_buffer.getvalue()).decode('utf-8'),
            'schematic': schematic_image,
            'preview': preview_data,
            'summary': {
                'total_cost': filtered_data['total_cost'],
                'item_count': sum(len(cat['systems']) for cat in filtered_data['categories']),
                'categories': [cat['name'] for cat in filtered_data['categories']]
            }
        }
    
    def _filter_scope_by_trade(self, project_data: Dict, trade: str) -> Dict:
        """Filter project scope data for a specific trade"""
        
        trade_mapping = {
            'electrical': 'Electrical',
            'plumbing': 'Plumbing',
            'hvac': 'Mechanical',
            'structural': 'Structural',
            'general': None  # General contractor sees everything
        }
        
        target_category = trade_mapping.get(trade.lower())
        
        if trade.lower() == 'general' or not target_category:
            return project_data
        
        # Filter categories - now handles both old and new category structures
        filtered_categories = []
        for cat in project_data.get('categories', []):
            cat_name_lower = cat['name'].lower()
            target_lower = target_category.lower()
            
            # Match exact category name or categories that start with trade name
            if (cat_name_lower == target_lower or 
                cat_name_lower.startswith(f"{target_lower} -") or
                cat_name_lower.startswith(f"{target_lower}:")):
                filtered_categories.append(cat)
        
        # Calculate filtered totals
        subtotal = 0
        for cat in filtered_categories:
            # Calculate category subtotal from systems if not present
            if 'subtotal' in cat:
                subtotal += cat['subtotal']
            else:
                cat_subtotal = sum(sys.get('total_cost', 0) for sys in cat.get('systems', []))
                cat['subtotal'] = cat_subtotal
                subtotal += cat_subtotal
        
        contingency_amount = subtotal * (project_data.get('contingency_percentage', 10) / 100)
        total_cost = subtotal + contingency_amount
        
        return {
            **project_data,
            'categories': filtered_categories,
            'subtotal': subtotal,
            'contingency_amount': contingency_amount,
            'total_cost': total_cost
        }
    
    def _generate_trade_schematic(self, floor_plan: Dict, trade: str, request_data: Dict) -> str:
        """Generate a trade-specific schematic showing relevant elements"""
        
        fig, ax = plt.subplots(1, 1, figsize=(10, 8))
        
        # Get building dimensions
        square_footage = request_data.get('square_footage', 10000)
        aspect_ratio = 1.5  # Default aspect ratio
        
        # Calculate dimensions
        width = np.sqrt(square_footage * aspect_ratio)
        height = square_footage / width
        
        # Draw building outline
        building = patches.Rectangle((0, 0), width, height, 
                                   linewidth=2, edgecolor='black', 
                                   facecolor='white', alpha=0.8)
        ax.add_patch(building)
        
        # Add trade-specific elements
        if trade.lower() == 'electrical':
            self._add_electrical_elements(ax, width, height)
        elif trade.lower() == 'plumbing':
            self._add_plumbing_elements(ax, width, height, request_data)
        elif trade.lower() == 'hvac':
            self._add_hvac_elements(ax, width, height)
        elif trade.lower() == 'structural':
            self._add_structural_elements(ax, width, height)
        else:  # general
            self._add_all_elements(ax, width, height, request_data)
        
        # Add title and labels
        ax.set_xlim(-width*0.1, width*1.1)
        ax.set_ylim(-height*0.1, height*1.1)
        ax.set_aspect('equal')
        ax.set_title(f'{trade.upper()} Layout - {request_data.get("project_name", "Project")}', 
                    fontsize=16, fontweight='bold')
        
        # Add dimensions
        ax.text(width/2, -height*0.05, f'{width:.0f} ft', 
                ha='center', va='top', fontsize=10)
        ax.text(-width*0.05, height/2, f'{height:.0f} ft', 
                ha='right', va='center', fontsize=10, rotation=90)
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _add_electrical_elements(self, ax, width, height):
        """Add electrical elements to the schematic"""
        # Main electrical panel
        panel = patches.Rectangle((width*0.05, height*0.05), width*0.1, height*0.1,
                                linewidth=2, edgecolor='gold', facecolor='yellow', alpha=0.7)
        ax.add_patch(panel)
        ax.text(width*0.1, height*0.1, 'Main\nPanel', ha='center', va='center', fontsize=8)
        
        # Distribution points
        for i in range(3):
            for j in range(3):
                x = width * (0.2 + i * 0.3)
                y = height * (0.2 + j * 0.3)
                circle = patches.Circle((x, y), width*0.02, 
                                      edgecolor='gold', facecolor='yellow', alpha=0.5)
                ax.add_patch(circle)
                ax.text(x, y, 'JB', ha='center', va='center', fontsize=6)
    
    def _add_plumbing_elements(self, ax, width, height, request_data):
        """Add plumbing elements to the schematic"""
        # Water main entry
        main = patches.Rectangle((0, height*0.45), width*0.05, height*0.1,
                               linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.7)
        ax.add_patch(main)
        ax.text(width*0.025, height*0.5, 'Water\nMain', ha='center', va='center', fontsize=8)
        
        # Bathrooms (based on building type)
        num_bathrooms = 2 if request_data.get('square_footage', 10000) < 20000 else 4
        for i in range(num_bathrooms):
            x = width * (0.2 + (i % 2) * 0.6)
            y = height * (0.2 + (i // 2) * 0.6)
            bathroom = patches.Rectangle((x, y), width*0.15, height*0.1,
                                       linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.5)
            ax.add_patch(bathroom)
            ax.text(x + width*0.075, y + height*0.05, f'Bath {i+1}', 
                   ha='center', va='center', fontsize=8)
    
    def _add_hvac_elements(self, ax, width, height):
        """Add HVAC elements to the schematic"""
        # Rooftop units
        for i in range(2):
            x = width * (0.25 + i * 0.5)
            y = height * 0.9
            rtu = patches.Rectangle((x - width*0.1, y - height*0.05), width*0.2, height*0.1,
                                  linewidth=2, edgecolor='red', facecolor='orange', alpha=0.7)
            ax.add_patch(rtu)
            ax.text(x, y, f'RTU-{i+1}', ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Ductwork representation
        for i in range(3):
            y = height * (0.2 + i * 0.3)
            line = plt.Line2D([width*0.1, width*0.9], [y, y], 
                            linewidth=3, color='orange', alpha=0.5)
            ax.add_line(line)
    
    def _add_structural_elements(self, ax, width, height):
        """Add structural elements to the schematic"""
        # Column grid
        cols = 5
        rows = 4
        for i in range(cols):
            for j in range(rows):
                x = width * (0.1 + i * 0.8 / (cols - 1))
                y = height * (0.1 + j * 0.8 / (rows - 1))
                column = patches.Rectangle((x - width*0.02, y - height*0.02), 
                                         width*0.04, height*0.04,
                                         linewidth=1, edgecolor='gray', facecolor='darkgray')
                ax.add_patch(column)
                ax.text(x, y, f'{chr(65+i)}{j+1}', ha='center', va='center', fontsize=6)
    
    def _add_all_elements(self, ax, width, height, request_data):
        """Add all trade elements for general contractor view"""
        self._add_structural_elements(ax, width, height)
        self._add_electrical_elements(ax, width, height)
        self._add_plumbing_elements(ax, width, height, request_data)
        self._add_hvac_elements(ax, width, height)
    
    def _generate_pdf_document(self, filtered_data: Dict, trade: str, 
                              project_data: Dict, schematic_image: str) -> io.BytesIO:
        """Generate a professional PDF document for the trade package"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12
        )
        
        # Cover page
        elements.append(Paragraph(f"{trade.upper()} TRADE PACKAGE", title_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Project information
        project_info = [
            ['Project Name:', project_data.get('project_name', 'N/A')],
            ['Location:', project_data.get('request_data', {}).get('location', 'N/A')],
            ['Total Square Footage:', f"{project_data.get('request_data', {}).get('square_footage', 0):,} sq ft"],
            ['Building Type:', project_data.get('request_data', {}).get('project_type', 'N/A')],
            ['Date Generated:', datetime.now().strftime('%B %d, %Y')],
            ['Trade Total Cost:', f"${filtered_data['total_cost']:,.2f}"]
        ]
        
        info_table = Table(project_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        elements.append(PageBreak())
        
        # Scope details
        elements.append(Paragraph("SCOPE OF WORK", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        for category in filtered_data['categories']:
            elements.append(Paragraph(f"{category['name']}", styles['Heading2']))
            
            # Create table data for systems
            table_data = [['System Description', 'Qty', 'Unit', 'Unit Cost', 'Total Cost']]
            for system in category['systems']:
                # Handle both integer and float quantities properly
                qty = system['quantity']
                if isinstance(qty, int):
                    qty_str = f"{qty:,}"
                else:
                    qty_str = f"{qty:,.1f}" if qty % 1 else f"{int(qty):,}"
                
                table_data.append([
                    system['name'],
                    qty_str,
                    system['unit'],
                    f"${system['unit_cost']:,.2f}",
                    f"${system['total_cost']:,.2f}"
                ])
            
            # Add subtotal row
            table_data.append(['', '', '', 'Subtotal:', f"${category['subtotal']:,.2f}"])
            
            # Create and style the table
            t = Table(table_data, colWidths=[3*inch, 0.7*inch, 0.5*inch, 1*inch, 1.2*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 9),  # Smaller font for descriptions
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.3*inch))
        
        # Add schematic on new page
        elements.append(PageBreak())
        elements.append(Paragraph(f"{trade.upper()} LAYOUT SCHEMATIC", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Convert base64 image to PIL Image for inclusion in PDF
        if schematic_image.startswith('data:image/png;base64,'):
            image_data = base64.b64decode(schematic_image.split(',')[1])
            image_buffer = io.BytesIO(image_data)
            elements.append(Image(image_buffer, width=6*inch, height=4.5*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
    
    def _generate_csv_data(self, filtered_data: Dict, trade: str) -> io.BytesIO:
        """Generate CSV data for the trade package"""
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Write header
        writer.writerow(['Trade Package Export', trade.upper(), datetime.now().strftime('%Y-%m-%d')])
        writer.writerow([])  # Empty row
        
        # Write column headers
        writer.writerow(['Category', 'System', 'Quantity', 'Unit', 'Unit Cost', 'Total Cost'])
        
        # Write data
        for category in filtered_data['categories']:
            for system in category['systems']:
                writer.writerow([
                    category['name'],
                    system['name'],
                    system['quantity'],
                    system['unit'],
                    system['unit_cost'],
                    system['total_cost']
                ])
        
        # Write totals
        writer.writerow([])  # Empty row
        writer.writerow(['', '', '', '', 'Subtotal:', filtered_data['subtotal']])
        writer.writerow(['', '', '', '', f"Contingency ({filtered_data.get('contingency_percentage', 10)}%):", 
                        filtered_data['contingency_amount']])
        writer.writerow(['', '', '', '', 'Total:', filtered_data['total_cost']])
        
        # Convert to bytes
        byte_buffer = io.BytesIO()
        byte_buffer.write(buffer.getvalue().encode('utf-8'))
        byte_buffer.seek(0)
        
        return byte_buffer
    
    def _generate_preview_data(self, filtered_data: Dict, trade: str, schematic_image: str) -> Dict:
        """Generate preview data for UI display"""
        
        return {
            'trade': trade,
            'total_cost': filtered_data['total_cost'],
            'subtotal': filtered_data['subtotal'],
            'contingency_amount': filtered_data['contingency_amount'],
            'categories': [
                {
                    'name': cat['name'],
                    'subtotal': cat.get('subtotal', sum(sys.get('total_cost', 0) for sys in cat.get('systems', []))),
                    'system_count': len(cat.get('systems', [])),
                    'systems': [
                        {
                            'name': sys['name'],
                            'quantity': sys['quantity'],
                            'unit': sys['unit'],
                            'total_cost': sys['total_cost']
                        }
                        for sys in cat['systems'][:3]  # Preview first 3 systems
                    ]
                }
                for cat in filtered_data['categories']
            ],
            'schematic_preview': schematic_image
        }


trade_package_service = TradePackageService()