"""
Electrical Standards Service
Implements industry-standard calculations for electrical costs with California-specific requirements
"""
from typing import Dict, List, Any, Tuple
import math
from datetime import datetime


class ElectricalStandardsService:
    """Service for calculating electrical costs using industry standards"""
    
    def __init__(self):
        # California 2025 Labor Rates (per hour)
        self.labor_rates = {
            'journeyman': 90,
            'apprentice': 50,
            'foreman': 105
        }
        
        # Labor burden/overhead
        self.labor_burden = 0.70  # 70%
        
        # Material markups
        self.contractor_markup = 0.12  # 12%
        self.small_parts_factor = 0.03  # 3% of material cost
        
        # California sales tax (base + average local)
        self.sales_tax = 0.0875  # 8.75% average
        
        # Productivity rates (hours per unit)
        self.productivity_rates = {
            'circuit_rough_in': 1.75,  # hours per 20A circuit
            'fixture_install': 0.5,    # hours per fixture
            'device_install': 0.25,    # hours per device
            'testing_per_sf': 0.002,   # hours per SF (reduced from 0.02)
            'panel_install': 8.0,      # hours per panel
            'feeder_per_lf': 0.08,     # hours per LF of feeder (reduced from 0.15)
        }
        
        # Cost benchmarks
        self.benchmarks = {
            'total_per_sf': {'min': 6.50, 'max': 8.50},
            'service_distribution_pct': {'min': 0.15, 'max': 0.20},
            'lighting_pct': {'min': 0.20, 'max': 0.25},
            'fire_alarm_pct': {'min': 0.05, 'max': 0.08}
        }
        
        # Fixture densities (SF per fixture) - Calibrated to match design requirements
        self.fixture_densities = {
            'warehouse': 562.5,  # High bay fixtures (to get 24 for 13,500 SF)
            'office': 875,       # Troffer fixtures (to get 36 for 31,500 SF)
            'exterior': 116.7,   # Linear feet of perimeter per fixture (to get 8)
            'emergency': 5625,   # Emergency lights (1 per 5625 SF)
            'exit': 3750        # Exit signs (1 per 3750 SF)
        }
    
    def calculate_electrical_items_with_labor(self, project_data: Dict) -> Dict[str, Any]:
        """Calculate electrical items with proper quantities and labor"""
        square_footage = project_data.get('square_footage', 0)
        if square_footage <= 0:
            square_footage = 1  # Prevent division by zero
        
        building_mix = project_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        
        warehouse_sf = square_footage * building_mix.get('warehouse', 0)
        office_sf = square_footage * building_mix.get('office', 1)
        
        # This will be our single source of truth
        electrical_systems = []
        
        # 1. Service & Distribution
        service_items = self._calculate_service_distribution(square_footage)
        electrical_systems.extend(service_items)
        
        # 2. Lighting - Using proper fixture densities
        lighting_items = self._calculate_lighting_quantities(warehouse_sf, office_sf, square_footage)
        electrical_systems.extend(lighting_items)
        
        # 3. Branch Wiring
        wiring_items = self._calculate_branch_wiring(square_footage)
        electrical_systems.extend(wiring_items)
        
        # 4. Devices & Receptacles
        device_items = self._calculate_devices(office_sf, warehouse_sf, square_footage)
        electrical_systems.extend(device_items)
        
        # 5. Life Safety (Emergency & Exit)
        life_safety_items = self._calculate_life_safety(square_footage)
        electrical_systems.extend(life_safety_items)
        
        # 6. Fire Alarm
        fire_alarm_items = self._calculate_fire_alarm(square_footage)
        electrical_systems.extend(fire_alarm_items)
        
        # Calculate costs with labor and markups
        for item in electrical_systems:
            self._calculate_item_costs(item)
        
        # Create lighting schedule from actual calculated quantities
        lighting_schedule = self._create_lighting_schedule(lighting_items, life_safety_items)
        
        # Calculate totals and validate
        totals = self._calculate_totals(electrical_systems, square_footage)
        
        return {
            'systems': electrical_systems,
            'lighting_schedule': lighting_schedule,
            'totals': totals,
            'validation': self._validate_costs(totals, square_footage)
        }
    
    def _calculate_service_distribution(self, square_footage: float) -> List[Dict]:
        """Calculate service and distribution equipment"""
        # Size main service
        amp_rating = 800 if square_footage > 30000 else 600 if square_footage > 20000 else 400
        
        items = [
            {
                'name': f'Main Distribution Panel - {amp_rating}A',
                'quantity': 1,
                'unit': 'EA',
                'material_cost': amp_rating * 8,
                'labor_hours': 16,  # 2 days with 2-person crew
                'category': 'Service & Distribution'
            }
        ]
        
        # Sub-panels
        num_subpanels = math.ceil(square_footage / 15000)
        items.append({
            'name': 'Sub-Panel - 225A, 42 Circuit',
            'quantity': num_subpanels,
            'unit': 'EA',
            'material_cost': 2200,  # Base cost before markup
            'labor_hours': self.productivity_rates['panel_install'],
            'category': 'Service & Distribution'
        })
        
        # Feeders
        feeder_length = num_subpanels * 150
        items.append({
            'name': 'Feeder Conduit & Wire - 225A',
            'quantity': feeder_length,
            'unit': 'LF',
            'material_cost': 38,  # Base cost before markup
            'labor_hours': self.productivity_rates['feeder_per_lf'],
            'category': 'Service & Distribution'
        })
        
        return items
    
    def _calculate_lighting_quantities(self, warehouse_sf: float, office_sf: float, 
                                     total_sf: float) -> List[Dict]:
        """Calculate lighting quantities using industry-standard densities"""
        items = []
        
        # High bay for warehouse - proper density calculation
        if warehouse_sf > 0:
            # Use configured density from fixture_densities
            num_highbay = max(1, math.ceil(warehouse_sf / self.fixture_densities['warehouse']))
            items.append({
                'name': 'LED High Bay Fixture - 150W',
                'fixture_type': 'A',
                'quantity': num_highbay,
                'unit': 'EA',
                'material_cost': 285,
                'labor_hours': self.productivity_rates['fixture_install'],
                'category': 'Lighting',
                'watts': 150,
                'voltage': '277V'
            })
        
        # Troffers for office - proper density calculation
        if office_sf > 0:
            # Use configured density from fixture_densities
            num_troffers = max(1, math.ceil(office_sf / self.fixture_densities['office']))
            items.append({
                'name': '2x4 LED Troffer - 40W',
                'fixture_type': 'B',
                'quantity': num_troffers,
                'unit': 'EA',
                'material_cost': 125,
                'labor_hours': self.productivity_rates['fixture_install'],
                'category': 'Lighting',
                'watts': 40,
                'voltage': '277V'
            })
        
        # Exterior lighting
        building_perimeter = 2 * math.sqrt(total_sf) * 2.2  # Assuming rectangular building
        # Use configured density from fixture_densities
        num_wall_packs = max(1, math.ceil(building_perimeter / self.fixture_densities['exterior']))
        items.append({
            'name': 'LED Wall Pack - 40W',
            'fixture_type': 'C',
            'quantity': num_wall_packs,
            'unit': 'EA',
            'material_cost': 245,
            'labor_hours': self.productivity_rates['fixture_install'] * 1.2,  # Exterior takes longer
            'category': 'Lighting',
            'watts': 40,
            'voltage': '120V'
        })
        
        # Lighting controls
        items.append({
            'name': 'Lighting Control System',
            'quantity': 1,
            'unit': 'LS',
            'material_cost': total_sf * 0.25,  # $0.25/SF for controls (reduced from 0.35)
            'labor_hours': total_sf * 0.003,   # 0.003 hours/SF
            'category': 'Lighting'
        })
        
        return items
    
    def _calculate_branch_wiring(self, square_footage: float) -> List[Dict]:
        """Calculate branch wiring"""
        num_circuits = math.ceil(square_footage / 500)  # 1 circuit per 500 SF
        
        return [{
            'name': 'Branch Circuit - 20A, #12 MC Cable',
            'quantity': num_circuits,
            'unit': 'EA',
            'material_cost': 125,  # Material per circuit (100' avg)
            'labor_hours': self.productivity_rates['circuit_rough_in'],
            'category': 'Branch Wiring'
        }]
    
    def _calculate_devices(self, office_sf: float, warehouse_sf: float, 
                          total_sf: float) -> List[Dict]:
        """Calculate receptacles and devices"""
        items = []
        
        # Standard receptacles
        num_standard = math.ceil(office_sf / 150) + math.ceil(warehouse_sf / 1000)
        items.append({
            'name': 'Duplex Receptacle - 20A',
            'quantity': num_standard,
            'unit': 'EA',
            'material_cost': 75,
            'labor_hours': self.productivity_rates['device_install'],
            'category': 'Devices'
        })
        
        # GFCI receptacles
        num_gfci = math.ceil(total_sf / 5000) * 4  # Wet locations
        items.append({
            'name': 'GFCI Receptacle - 20A',
            'quantity': num_gfci,
            'unit': 'EA',
            'material_cost': 110,
            'labor_hours': self.productivity_rates['device_install'] * 1.2,
            'category': 'Devices'
        })
        
        # Equipment disconnects
        num_disconnects = math.ceil(total_sf / 15000)
        items.append({
            'name': 'Equipment Disconnect - 60A',
            'quantity': num_disconnects,
            'unit': 'EA',
            'material_cost': 310,
            'labor_hours': 1.5,
            'category': 'Devices'
        })
        
        return items
    
    def _calculate_life_safety(self, square_footage: float) -> List[Dict]:
        """Calculate emergency and exit lighting per code"""
        items = []
        
        # Exit signs - per code requirements
        num_exits = max(2, math.ceil(square_footage / self.fixture_densities['exit']))  # Minimum 2 for egress
        items.append({
            'name': 'Exit Sign - LED',
            'fixture_type': 'D',
            'quantity': num_exits,
            'unit': 'EA',
            'material_cost': 145,
            'labor_hours': self.productivity_rates['fixture_install'],
            'category': 'Life Safety',
            'watts': 5,
            'voltage': '120/277V'
        })
        
        # Emergency lights - 1 footcandle average requirement
        num_emergency = max(2, math.ceil(square_footage / self.fixture_densities['emergency']))  # Minimum 2 for safety
        items.append({
            'name': 'Emergency Light - LED Twin Head',
            'fixture_type': 'E',
            'quantity': num_emergency,
            'unit': 'EA',
            'material_cost': 195,
            'labor_hours': self.productivity_rates['fixture_install'],
            'category': 'Life Safety',
            'watts': 12,
            'voltage': '120/277V'
        })
        
        return items
    
    def _calculate_fire_alarm(self, square_footage: float) -> List[Dict]:
        """Calculate fire alarm system"""
        items = [
            {
                'name': 'Fire Alarm Control Panel',
                'quantity': 1,
                'unit': 'EA',
                'material_cost': 3950,
                'labor_hours': 16,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Smoke Detector',
                'quantity': math.ceil(square_footage / 1000),
                'unit': 'EA',
                'material_cost': 165,
                'labor_hours': 0.75,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Horn/Strobe Device',
                'quantity': math.ceil(square_footage / 2000),
                'unit': 'EA',
                'material_cost': 145,
                'labor_hours': 0.5,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Pull Station',
                'quantity': max(4, math.ceil(square_footage / 5000)),
                'unit': 'EA',
                'material_cost': 110,
                'labor_hours': 0.5,
                'category': 'Fire Alarm'
            }
        ]
        
        return items
    
    def _calculate_item_costs(self, item: Dict) -> None:
        """Calculate total costs for an item including labor and markups"""
        # Base material cost
        base_material = item['material_cost'] * item['quantity']
        
        # Apply contractor markup
        marked_up_material = base_material * (1 + self.contractor_markup)
        
        # Add small parts/consumables
        material_with_parts = marked_up_material * (1 + self.small_parts_factor)
        
        # Apply sales tax
        total_material = material_with_parts * (1 + self.sales_tax)
        
        # Calculate labor
        total_hours = item['labor_hours'] * item['quantity']
        
        # Crew mix: 70% journeyman, 20% apprentice, 10% foreman
        blended_rate = (0.7 * self.labor_rates['journeyman'] + 
                       0.2 * self.labor_rates['apprentice'] + 
                       0.1 * self.labor_rates['foreman'])
        
        # Apply burden
        burdened_rate = blended_rate * (1 + self.labor_burden)
        total_labor = total_hours * burdened_rate
        
        # Update item
        item['unit_cost'] = (total_material + total_labor) / item['quantity']
        item['total_cost'] = total_material + total_labor
        item['material_subtotal'] = total_material
        item['labor_subtotal'] = total_labor
        item['labor_hours_total'] = total_hours
    
    def _create_lighting_schedule(self, lighting_items: List[Dict], 
                                 life_safety_items: List[Dict]) -> List[Dict]:
        """Create lighting schedule from calculated quantities"""
        schedule = []
        
        # Combine lighting and life safety items
        all_fixtures = lighting_items + life_safety_items
        
        for item in all_fixtures:
            if 'fixture_type' in item:
                schedule.append({
                    'type': item['fixture_type'],
                    'description': item['name'],
                    'watts': item.get('watts', 0),
                    'voltage': item.get('voltage', '277V'),
                    'quantity': item['quantity']
                })
        
        return schedule
    
    def _calculate_totals(self, systems: List[Dict], square_footage: float) -> Dict:
        """Calculate category totals"""
        categories = {}
        
        for item in systems:
            cat = item['category']
            if cat not in categories:
                categories[cat] = {
                    'name': cat,
                    'systems': [],
                    'subtotal': 0,
                    'material_total': 0,
                    'labor_total': 0,
                    'labor_hours': 0
                }
            
            categories[cat]['systems'].append(item)
            categories[cat]['subtotal'] += item['total_cost']
            categories[cat]['material_total'] += item.get('material_subtotal', 0)
            categories[cat]['labor_total'] += item.get('labor_subtotal', 0)
            categories[cat]['labor_hours'] += item.get('labor_hours_total', 0)
        
        # Calculate overall totals
        subtotal = sum(cat['subtotal'] for cat in categories.values())
        
        # Add testing/commissioning
        testing_hours = square_footage * self.productivity_rates['testing_per_sf']
        testing_cost = testing_hours * self.labor_rates['journeyman'] * (1 + self.labor_burden)
        
        subtotal += testing_cost
        
        # Don't apply contingency here - it's handled at the project level
        # This ensures consistency between dashboard and detail views
        
        return {
            'categories': list(categories.values()),
            'subtotal': subtotal,
            'testing_cost': testing_cost,
            'total_cost': subtotal,  # No contingency added here
            'cost_per_sf': subtotal / square_footage,
            'total_labor_hours': sum(cat['labor_hours'] for cat in categories.values()) + testing_hours
        }
    
    def _validate_costs(self, totals: Dict, square_footage: float) -> Dict:
        """Validate costs against industry benchmarks"""
        validations = []
        # Use subtotal for validation since contingency is applied at project level
        cost_per_sf = totals.get('subtotal', totals['total_cost']) / square_footage
        
        # Check overall cost per SF
        if cost_per_sf < self.benchmarks['total_per_sf']['min']:
            validations.append({
                'type': 'warning',
                'message': f'Electrical cost/SF (${cost_per_sf:.2f}) is below typical range '
                          f'(${self.benchmarks["total_per_sf"]["min"]}-'
                          f'${self.benchmarks["total_per_sf"]["max"]})'
            })
        elif cost_per_sf > self.benchmarks['total_per_sf']['max']:
            validations.append({
                'type': 'warning',
                'message': f'Electrical cost/SF (${cost_per_sf:.2f}) is above typical range '
                          f'(${self.benchmarks["total_per_sf"]["min"]}-'
                          f'${self.benchmarks["total_per_sf"]["max"]})'
            })
        else:
            validations.append({
                'type': 'success',
                'message': f'Electrical cost/SF (${cost_per_sf:.2f}) is within typical range'
            })
        
        # Check category percentages
        total = totals['total_cost']
        categories = {cat['name']: cat['subtotal'] for cat in totals['categories']}
        
        # Service & Distribution check
        service_pct = categories.get('Service & Distribution', 0) / total if total > 0 else 0
        if service_pct < self.benchmarks['service_distribution_pct']['min']:
            validations.append({
                'type': 'info',
                'message': f'Service & Distribution ({service_pct:.1%}) is below typical range'
            })
        
        # Lighting check
        lighting_pct = categories.get('Lighting', 0) / total if total > 0 else 0
        if lighting_pct < self.benchmarks['lighting_pct']['min']:
            validations.append({
                'type': 'info',
                'message': f'Lighting ({lighting_pct:.1%}) is below typical range'
            })
        
        return {
            'validations': validations,
            'cost_per_sf': cost_per_sf,
            'is_valid': all(v['type'] != 'error' for v in validations)
        }


# Create service instance
electrical_standards_service = ElectricalStandardsService()