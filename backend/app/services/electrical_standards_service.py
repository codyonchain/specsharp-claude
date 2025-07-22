"""
Electrical Standards Service V2 Wrapper
Bridges the new V2 calculation engine with the existing system
"""
from typing import Dict, List, Any
import math
import logging
from .electrical_v2_service import electrical_v2_service

logger = logging.getLogger(__name__)


class ElectricalStandardsServiceV2:
    """Service that wraps the V2 engine for backward compatibility"""
    
    def __init__(self):
        self.v2_engine = electrical_v2_service
    
    def calculate_electrical_items_with_labor(self, project_data: Dict) -> Dict[str, Any]:
        """Calculate electrical items using the V2 engine"""
        
        logger.error("=== USING V2 ELECTRICAL ENGINE ===")
        logger.error(f"Project data keys: {list(project_data.keys())}")
        
        # Check if location is provided for proper regional calculation
        if 'location' not in project_data:
            # Try to get from request_data or default to moderate tier
            project_data['location'] = project_data.get('request_data', {}).get('location', '')
        
        # Log project details - check both root and request_data
        request_data = project_data.get('request_data', {})
        logger.error(f"Building type: {project_data.get('project_type', request_data.get('building_type', 'Unknown'))}")
        logger.error(f"Square footage: {project_data.get('square_footage', request_data.get('square_footage', 0))}")
        logger.error(f"Location: {project_data.get('location', request_data.get('location', 'Unknown'))}")
        logger.error(f"Building mix: {project_data.get('building_mix', request_data.get('building_mix', {}))}")
        
        # Run V2 calculation
        v2_result = self.v2_engine.calculate_electrical_cost(project_data)
        
        # Log V2 results
        logger.error(f"V2 result keys: {list(v2_result.keys())}")
        logger.error(f"V2 total cost: ${v2_result.get('total', 0):,.2f}")
        logger.error(f"V2 base cost: ${v2_result.get('base_cost', 0):,.2f}")
        logger.error(f"V2 raw_subtotal: ${v2_result.get('raw_subtotal', 'NOT FOUND')}")
        logger.error(f"V2 subtotal: ${v2_result.get('subtotal', 0):,.2f}")
        logger.error(f"V2 regional multiplier: {v2_result.get('regional_multiplier', 1.0)}")
        
        # Convert V2 results to legacy format
        electrical_systems = []
        
        # Note: V2 engine returns base costs without regional multiplier for individual systems
        # The main engine will apply its own regional multiplier
        
        # 1. Service & Distribution
        service_data = v2_result['service_distribution']
        electrical_systems.append({
            'name': f'Main Distribution Panel - {service_data["service_amps"]}A',
            'quantity': 1,
            'unit': 'EA',
            'unit_cost': service_data['service_cost'],
            'total_cost': service_data['service_cost'],
            'category': 'Service & Distribution'
        })
        
        if service_data['num_panels'] > 0:
            electrical_systems.append({
                'name': 'Sub-Panel - 200A, 42 Circuit',
                'quantity': service_data['num_panels'],
                'unit': 'EA',
                'unit_cost': service_data['panel_cost'] / service_data['num_panels'],
                'total_cost': service_data['panel_cost'],
                'category': 'Service & Distribution'
            })
        
        if service_data.get('transformer_cost', 0) > 0:
            electrical_systems.append({
                'name': 'Transformer - 75kVA Dry Type',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': service_data['transformer_cost'],
                'total_cost': service_data['transformer_cost'],
                'category': 'Service & Distribution'
            })
        
        # 2. Lighting from space calculations
        lighting_schedule = []
        fixture_type_map = {
            'LED High Bay 150W': 'A',
            '2x4 LED Troffer': 'B',
            'LED Wall Pack': 'C',
            'Track Lighting': 'T',
            'Decorative Pendant': 'P'
        }
        
        for space_calc in v2_result['space_calculations']:
            # Add base electrical infrastructure for this space
            space_type = space_calc['type'].title()
            base_infrastructure_cost = space_calc['base_cost']
            
            # Distribute base cost across infrastructure categories
            electrical_systems.append({
                'name': f'{space_type} - Conduit & Wire',
                'quantity': space_calc['area'],
                'unit': 'SF',
                'unit_cost': base_infrastructure_cost * 0.4 / space_calc['area'],
                'total_cost': base_infrastructure_cost * 0.4,
                'category': 'Infrastructure'
            })
            
            electrical_systems.append({
                'name': f'{space_type} - Branch Panels & Feeders',
                'quantity': space_calc['area'] / 5000,  # 1 per 5000 SF
                'unit': 'EA',
                'unit_cost': base_infrastructure_cost * 0.3 / (space_calc['area'] / 5000),
                'total_cost': base_infrastructure_cost * 0.3,
                'category': 'Infrastructure'
            })
            
            electrical_systems.append({
                'name': f'{space_type} - Grounding & Bonding',
                'quantity': space_calc['area'],
                'unit': 'SF',
                'unit_cost': base_infrastructure_cost * 0.15 / space_calc['area'],
                'total_cost': base_infrastructure_cost * 0.15,
                'category': 'Infrastructure'
            })
            
            electrical_systems.append({
                'name': f'{space_type} - Labor & Installation',
                'quantity': space_calc['area'],
                'unit': 'SF',
                'unit_cost': base_infrastructure_cost * 0.15 / space_calc['area'],
                'total_cost': base_infrastructure_cost * 0.15,
                'category': 'Infrastructure'
            })
            
            for fixture in space_calc['fixtures']['fixtures']:
                fixture_name = fixture['type']
                electrical_systems.append({
                    'name': fixture_name,
                    'quantity': fixture['quantity'],
                    'unit': fixture.get('unit', 'EA'),
                    'unit_cost': fixture['unit_cost'],
                    'total_cost': fixture['total_cost'],
                    'category': 'Lighting'
                })
                
                # Add to lighting schedule if it's a standard fixture
                if fixture_name in fixture_type_map:
                    lighting_schedule.append({
                        'type': fixture_type_map[fixture_name],
                        'description': fixture_name,
                        'quantity': int(fixture['quantity']),
                        'watts': self._get_fixture_watts(fixture_name),
                        'voltage': '277V' if 'High Bay' in fixture_name or 'Troffer' in fixture_name else '120V'
                    })
            
            # Add receptacles and circuits
            if space_calc['fixtures']['receptacles'] > 0:
                electrical_systems.append({
                    'name': f'Receptacles - {space_calc["type"].title()}',
                    'quantity': space_calc['fixtures']['receptacles'],
                    'unit': 'EA',
                    'unit_cost': space_calc['fixtures']['receptacle_cost'] / space_calc['fixtures']['receptacles'],
                    'total_cost': space_calc['fixtures']['receptacle_cost'],
                    'category': 'Devices'
                })
            
            if space_calc['fixtures']['circuits'] > 0:
                electrical_systems.append({
                    'name': f'Branch Circuits - {space_calc["type"].title()}',
                    'quantity': space_calc['fixtures']['circuits'],
                    'unit': 'EA',
                    'unit_cost': space_calc['fixtures']['circuit_cost'] / space_calc['fixtures']['circuits'],
                    'total_cost': space_calc['fixtures']['circuit_cost'],
                    'category': 'Branch Wiring'
                })
            
            if space_calc['fixtures']['data_drops'] > 0:
                electrical_systems.append({
                    'name': f'Data/Communications - {space_calc["type"].title()}',
                    'quantity': space_calc['fixtures']['data_drops'],
                    'unit': 'EA',
                    'unit_cost': space_calc['fixtures']['data_cost'] / space_calc['fixtures']['data_drops'],
                    'total_cost': space_calc['fixtures']['data_cost'],
                    'category': 'Low Voltage'
                })
        
        # 3. Special Systems
        for system in v2_result['special_systems']['systems']:
            category = 'Special Systems'
            if 'Fire Alarm' in system['name']:
                category = 'Fire Alarm'
            elif 'Emergency' in system['name'] or 'Life Safety' in system['name']:
                category = 'Life Safety'
                
                # Add exit signs and emergency lights to schedule
                square_footage = project_data.get('square_footage', 0)
                num_exits = max(2, math.ceil(square_footage / 3750))
                num_emergency = max(2, math.ceil(square_footage / 5625))
                
                lighting_schedule.extend([
                    {
                        'type': 'D',
                        'description': 'Exit Sign - LED',
                        'quantity': num_exits,
                        'watts': 5,
                        'voltage': '120/277V'
                    },
                    {
                        'type': 'E',
                        'description': 'Emergency Light - LED Twin Head',
                        'quantity': num_emergency,
                        'watts': 12,
                        'voltage': '120/277V'
                    }
                ])
            
            electrical_systems.append({
                'name': system['name'],
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': system['cost'],
                'total_cost': system['cost'],
                'category': category
            })
        
        # Calculate category totals
        categories = {}
        for item in electrical_systems:
            cat = item['category']
            if cat not in categories:
                categories[cat] = {
                    'name': cat,
                    'systems': [],
                    'subtotal': 0
                }
            categories[cat]['systems'].append(item)
            categories[cat]['subtotal'] += item['total_cost']
        
        # Add exterior lighting to schedule if not already present
        if not any(s['type'] == 'C' for s in lighting_schedule):
            lighting_schedule.append({
                'type': 'C',
                'description': 'LED Wall Pack - 40W',
                'quantity': 8,
                'watts': 40,
                'voltage': '120V'
            })
        
        # Calculate the totals properly
        raw_subtotal = v2_result.get('raw_subtotal', 0)
        if raw_subtotal == 0:
            # Fallback: calculate from subtotal by removing regional multiplier
            raw_subtotal = v2_result.get('subtotal', 0) / v2_result.get('regional_multiplier', 1.0)
        
        logger.error(f"[WRAPPER] Using raw_subtotal: ${raw_subtotal:,.2f}")
        logger.error(f"[WRAPPER] Total systems cost: ${sum(cat['subtotal'] for cat in categories.values()):,.2f}")
        
        return {
            'systems': electrical_systems,
            'lighting_schedule': lighting_schedule,
            'totals': {
                'categories': list(categories.values()),
                'subtotal': raw_subtotal,
                'testing_cost': 0,  # Included in special systems
                'total_cost': raw_subtotal,
                'cost_per_sf': raw_subtotal / max(project_data.get('square_footage', 1), 1)
            },
            'validation': {
                'validations': v2_result['validations'],
                'cost_per_sf': v2_result['cost_per_sf'],
                'is_valid': all(v['type'] != 'error' for v in v2_result['validations'])
            },
            'v2_calculation': v2_result  # Include full V2 results for reference
        }
    
    def _get_fixture_watts(self, fixture_name: str) -> int:
        """Get wattage for fixture type"""
        watts_map = {
            'LED High Bay 150W': 150,
            '2x4 LED Troffer': 40,
            'LED Wall Pack': 40,
            'Exit Sign - LED': 5,
            'Emergency Light - LED Twin Head': 12
        }
        
        for key, watts in watts_map.items():
            if key in fixture_name:
                return watts
        return 40  # Default


# Create service instance
electrical_standards_service = ElectricalStandardsServiceV2()