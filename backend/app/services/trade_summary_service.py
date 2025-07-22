from typing import Dict, List, Any
import math
from app.services.detailed_trade_service import detailed_trade_service

class TradeSummaryService:
    """Service to generate trade summaries with key metrics"""
    
    def generate_trade_summaries(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate summary information for each trade with key quantities"""
        
        if project_data is None:
            return []
        
        # First enhance with detailed trade data if applicable
        enhanced_data = project_data.copy()
        for trade in ['electrical', 'hvac', 'plumbing']:
            # Check if we have this trade in categories
            has_trade = any(cat['name'].lower() == trade or 
                           (trade == 'hvac' and cat['name'].lower() == 'mechanical')
                           for cat in project_data.get('categories', []))
            if has_trade:
                enhanced_data = detailed_trade_service.enhance_trade_scope(enhanced_data, trade)
        
        # Get detailed scope
        categories = enhanced_data.get('categories', [])
        request_data = enhanced_data.get('request_data', {})
        
        # Initialize summaries
        summaries = []
        
        # Process each trade
        trade_processors = {
            'Electrical': self._process_electrical,
            'Mechanical': self._process_hvac,
            'Plumbing': self._process_plumbing,
            'Structural': self._process_structural,
            'General Conditions': self._process_general_conditions
        }
        
        # First, collect all categories that belong to each trade
        trade_categories = {
            'Electrical': [],
            'Mechanical': [],
            'Plumbing': [],
            'Structural': [],
            'General Conditions': []
        }
        
        # Group categories by trade
        for category in categories:
            category_name = category['name']
            matched = False
            
            # Check if this category belongs to a specific trade
            for trade, processor in trade_processors.items():
                if trade in category_name or (trade == 'Mechanical' and 'HVAC' in category_name):
                    trade_categories[trade].append(category)
                    matched = True
                    break
            
            # If not matched to a specific trade, use generic handler
            if not matched:
                summary = self._process_generic_trade(category, request_data)
                summaries.append(summary)
        
        # Process each trade with all its categories combined
        for trade, categories_list in trade_categories.items():
            if categories_list:
                # Combine all categories for this trade
                combined_category = self._combine_categories(categories_list, trade)
                summary = trade_processors[trade](combined_category, request_data)
                summaries.append(summary)
        
        return summaries
    
    def _combine_categories(self, categories: List[Dict], trade_name: str) -> Dict[str, Any]:
        """Combine multiple categories into a single category for a trade"""
        combined_systems = []
        total_subtotal = 0
        
        for category in categories:
            combined_systems.extend(category.get('systems', []))
            total_subtotal += category.get('subtotal', 0)
        
        return {
            'name': trade_name,
            'systems': combined_systems,
            'subtotal': total_subtotal
        }
    
    def _process_electrical(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process electrical trade summary"""
        
        # Extract key quantities from systems
        service_size = "800A"  # Default
        fixture_count = 0
        circuit_count = 0
        panel_count = 0
        
        for system in category.get('systems', []):
            name = system['name'].lower()
            
            if 'service entrance' in name:
                # Extract amp rating from name
                import re
                amp_match = re.search(r'(\d+)A', system['name'])
                if amp_match:
                    service_size = f"{amp_match.group(1)}A"
            
            if 'fixture' in name or 'light' in name or 'led' in name:
                fixture_count += int(system.get('quantity', 0))
            
            if 'circuit' in name and 'branch' in name:
                circuit_count += int(system.get('quantity', 0))
            
            if 'panel' in name and 'sub' not in name.lower():
                panel_count += int(system.get('quantity', 0))
        
        # If no specific counts found, estimate based on square footage
        if fixture_count == 0:
            square_footage = request_data.get('square_footage', 0)
            fixture_count = math.ceil(square_footage / 200)  # 1 per 200 sqft
        
        if circuit_count == 0:
            circuit_count = math.ceil(request_data.get('square_footage', 0) / 500)
        
        return {
            'trade': 'Electrical',
            'total_cost': category['subtotal'],
            'key_metrics': [
                {'label': 'Service Size', 'value': service_size, 'unit': ''},
                {'label': 'Light Fixtures', 'value': fixture_count, 'unit': 'fixtures'},
                {'label': 'Branch Circuits', 'value': circuit_count, 'unit': 'circuits'},
                {'label': 'Electrical Panels', 'value': panel_count + math.ceil(request_data.get('square_footage', 0) / 15000), 'unit': 'panels'}
            ],
            'systems': category.get('systems', []),
            'category_data': category
        }
    
    def _process_hvac(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process HVAC/Mechanical trade summary"""
        
        rtu_count = 0
        rtu_tonnage = 0
        ductwork_lf = 0
        thermostat_count = 0
        diffuser_count = 0
        
        for system in category.get('systems', []):
            name = system['name'].lower()
            
            if 'rooftop unit' in name or 'rtu' in name:
                rtu_count += int(system.get('quantity', 0))
                # Extract tonnage
                import re
                ton_match = re.search(r'(\d+)\s*ton', name)
                if ton_match:
                    rtu_tonnage += int(ton_match.group(1)) * system.get('quantity', 0)
            
            if 'duct' in name and ('supply' in name or 'return' in name):
                ductwork_lf += system.get('quantity', 0)
            
            if 'thermostat' in name:
                thermostat_count += int(system.get('quantity', 0))
            
            if 'diffuser' in name or 'grille' in name:
                diffuser_count += int(system.get('quantity', 0))
        
        # Calculate if not found
        if rtu_count == 0:
            square_footage = request_data.get('square_footage', 0)
            total_tons = square_footage / 400  # Rule of thumb
            rtu_count = math.ceil(total_tons / 30)  # 30 ton units
            rtu_tonnage = int(total_tons)
        
        if ductwork_lf == 0:
            ductwork_lf = int(request_data.get('square_footage', 0) * 1.2)  # Estimate
        
        return {
            'trade': 'HVAC',
            'total_cost': category['subtotal'],
            'key_metrics': [
                {'label': 'Rooftop Units', 'value': rtu_count, 'unit': f'units ({rtu_tonnage} tons)'},
                {'label': 'Ductwork', 'value': f"{ductwork_lf:,}", 'unit': 'LF'},
                {'label': 'Thermostats', 'value': thermostat_count or rtu_count + 2, 'unit': 'controls'},
                {'label': 'Diffusers/Grilles', 'value': diffuser_count or math.ceil(request_data.get('square_footage', 0) / 400), 'unit': 'terminals'}
            ],
            'systems': category.get('systems', []),
            'category_data': category
        }
    
    def _process_plumbing(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process plumbing trade summary"""
        
        bathroom_count = 0
        fixture_count = 0
        piping_lf = 0
        water_heater_count = 0
        
        for system in category.get('systems', []):
            name = system['name'].lower()
            quantity = system.get('quantity', 0)
            
            if 'water closet' in name:
                bathroom_count = max(bathroom_count, math.ceil(quantity / 2))
            
            if any(fixture in name for fixture in ['closet', 'lavatory', 'urinal', 'sink', 'fountain']):
                fixture_count += int(quantity)
            
            if 'pipe' in name and system.get('unit', '').upper() == 'LF':
                piping_lf += quantity
            
            if 'water heater' in name:
                water_heater_count += int(quantity)
        
        # Estimate if not found
        if bathroom_count == 0:
            bathroom_count = max(2, math.ceil(request_data.get('square_footage', 0) / 15000))
        
        if piping_lf == 0:
            piping_lf = int(request_data.get('square_footage', 0) * 1.4)  # Supply + waste estimate
        
        return {
            'trade': 'Plumbing',
            'total_cost': category['subtotal'],
            'key_metrics': [
                {'label': 'Bathrooms', 'value': bathroom_count, 'unit': 'complete'},
                {'label': 'Total Fixtures', 'value': fixture_count or bathroom_count * 6, 'unit': 'fixtures'},
                {'label': 'Piping', 'value': f"{piping_lf:,}", 'unit': 'LF'},
                {'label': 'Water Heaters', 'value': water_heater_count or 1, 'unit': f'{50 if fixture_count < 20 else 75} gal'}
            ],
            'systems': category.get('systems', []),
            'category_data': category
        }
    
    def _process_structural(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process structural trade summary"""
        
        steel_tons = 0
        concrete_cy = 0
        rebar_tons = 0
        
        for system in category.get('systems', []):
            name = system['name'].lower()
            
            if 'steel' in name and 'ton' in system.get('unit', '').lower():
                steel_tons += system.get('quantity', 0)
            
            if 'concrete' in name and ('cy' in system.get('unit', '').lower() or 'cubic' in name):
                concrete_cy += system.get('quantity', 0)
            
            if 'rebar' in name:
                rebar_tons += system.get('quantity', 0)
        
        # Estimate based on building size if not found
        square_footage = request_data.get('square_footage', 0)
        if steel_tons == 0:
            steel_tons = square_footage * 8 / 2000  # 8 lbs/sqft estimate
        
        if concrete_cy == 0:
            # Slab on grade estimate
            slab_thickness = 6  # inches
            concrete_cy = (square_footage * slab_thickness / 12) / 27
        
        return {
            'trade': 'Structural',
            'total_cost': category['subtotal'],
            'key_metrics': [
                {'label': 'Structural Steel', 'value': f"{steel_tons:.1f}", 'unit': 'tons'},
                {'label': 'Concrete', 'value': f"{concrete_cy:.0f}", 'unit': 'CY'},
                {'label': 'Rebar', 'value': f"{rebar_tons or concrete_cy * 0.02:.1f}", 'unit': 'tons'},
                {'label': 'Building Area', 'value': f"{square_footage:,}", 'unit': 'SF'}
            ],
            'systems': category.get('systems', []),
            'category_data': category
        }
    
    def _process_general_conditions(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process general conditions summary"""
        
        project_duration = math.ceil(request_data.get('square_footage', 10000) / 5000) * 2  # months
        
        # Extract key items
        supervision_months = 0
        equipment_months = 0
        
        for system in category.get('systems', []):
            name = system['name'].lower()
            if 'supervision' in name or 'superintendent' in name:
                supervision_months = system.get('quantity', 0)
            if 'equipment' in name and 'month' in system.get('unit', '').lower():
                equipment_months = system.get('quantity', 0)
        
        return {
            'trade': 'General Conditions',
            'total_cost': category['subtotal'],
            'key_metrics': [
                {'label': 'Project Duration', 'value': project_duration, 'unit': 'months'},
                {'label': 'Site Supervision', 'value': supervision_months or project_duration, 'unit': 'months'},
                {'label': 'Temporary Facilities', 'value': 'Included', 'unit': ''},
                {'label': 'Equipment & Tools', 'value': equipment_months or project_duration, 'unit': 'months'}
            ],
            'systems': category.get('systems', []),
            'category_data': category
        }
    
    def _process_generic_trade(self, category: Dict, request_data: Dict) -> Dict[str, Any]:
        """Process generic trade summary"""
        
        # Count major items
        major_items = []
        system_count = len(category.get('systems', []))
        
        # Get top 3 items by cost
        systems = sorted(category.get('systems', []), 
                        key=lambda x: x.get('total_cost', 0), 
                        reverse=True)[:3]
        
        for system in systems:
            major_items.append({
                'label': system['name'][:30] + ('...' if len(system['name']) > 30 else ''),
                'value': f"{system.get('quantity', 0):.0f}",
                'unit': system.get('unit', '')
            })
        
        # Add total item count
        if len(major_items) < 4:
            major_items.append({
                'label': 'Total Items',
                'value': system_count,
                'unit': 'systems'
            })
        
        return {
            'trade': category['name'],
            'total_cost': category['subtotal'],
            'key_metrics': major_items[:4],  # Limit to 4 metrics
            'systems': category.get('systems', []),
            'category_data': category
        }


trade_summary_service = TradeSummaryService()