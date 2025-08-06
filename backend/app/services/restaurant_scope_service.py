"""Restaurant-specific scope generation service with proper trade allocations"""
from typing import Dict, List, Any
import math


class RestaurantScopeService:
    """Generate restaurant-specific scope with correct items and trade allocations"""
    
    def __init__(self):
        # Restaurant base costs by state and service level (Based on RSMeans 2024)
        # These are base costs BEFORE regional multipliers
        self.base_costs = {
            'NH': {
                'quick_service': 300,   # QSR/Fast food base
                'casual_dining': 375,   # Casual dining base
                'full_service': 425,    # Full-service restaurant base
                'fine_dining': 550      # High-end restaurant base
            },
            'MA': {
                'quick_service': 300,   # Same base as NH (multiplier handles difference)
                'casual_dining': 375,
                'full_service': 425,
                'fine_dining': 550
            },
            'TN': {
                'quick_service': 300,
                'casual_dining': 375,
                'full_service': 425,
                'fine_dining': 550
            },
            # Default for all other states (use base national average)
            'default': {
                'quick_service': 300,
                'casual_dining': 375,
                'full_service': 425,
                'fine_dining': 550
            }
        }
        
        # Trade allocations by service level (MUST sum to 1.0)
        self.trade_allocations = {
            'full_service': {
                'structural': 0.10,      # 10%
                'mechanical': 0.22,      # 22%
                'electrical': 0.175,     # 17.5%
                'plumbing': 0.175,      # 17.5%
                'finishes': 0.25,       # 25%
                'general_conditions': 0.08  # 8%
            }
        }
    
    def generate_restaurant_scope(self, project_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Generate complete restaurant scope with proper allocations"""
        
        square_footage = project_data.get('square_footage', 0)
        state = project_data.get('state', 'NH')
        service_level = project_data.get('service_level', 'full_service')
        
        # Get base cost and calculate total project cost
        base_cost_per_sf = self.base_costs.get(state, self.base_costs['default']).get(service_level, 425)
        total_project_cost = base_cost_per_sf * square_footage
        
        # Get trade allocations
        allocations = self.trade_allocations.get(service_level, self.trade_allocations['full_service'])
        
        # Generate scope for each trade with proper budget
        scope = {
            'structural': self._generate_structural_items(square_footage, total_project_cost * allocations['structural']),
            'mechanical': self._generate_mechanical_items(square_footage, total_project_cost * allocations['mechanical']),
            'electrical': self._generate_electrical_items(square_footage, total_project_cost * allocations['electrical']),
            'plumbing': self._generate_plumbing_items(square_footage, total_project_cost * allocations['plumbing']),
            'finishes': self._generate_finishes_items(square_footage, total_project_cost * allocations['finishes'], service_level),
            'general_conditions': self._generate_gc_items(total_project_cost * allocations['general_conditions'])
        }
        
        return scope
    
    def _generate_mechanical_items(self, square_footage: float, budget: float) -> List[Dict[str, Any]]:
        """Generate restaurant-specific mechanical items (22% of budget)"""
        items = []
        
        # Kitchen is typically 30% of restaurant
        kitchen_sf = square_footage * 0.3
        dining_sf = square_footage * 0.7
        
        # Kitchen Ventilation System (40% of mechanical budget)
        hood_length = max(20, kitchen_sf / 40)  # Min 20 LF, typical 30-35 LF for 4000sf
        
        items.append({
            'name': 'Type I Exhaust Hood System',
            'quantity': round(hood_length, 1),
            'unit': 'LF',
            'unit_cost': 850,
            'total_cost': hood_length * 850,
            'category': 'Kitchen Ventilation'
        })
        
        # Make-up air sized for hood exhaust
        mua_cfm = hood_length * 300  # 300 CFM per linear foot
        items.append({
            'name': 'Make-up Air Unit with Heating/Cooling',
            'quantity': round(mua_cfm),
            'unit': 'CFM',
            'unit_cost': 4.50,
            'total_cost': mua_cfm * 4.50,
            'category': 'Kitchen Ventilation'
        })
        
        # Exhaust ductwork
        duct_weight = kitchen_sf * 0.5  # 0.5 lbs per SF of kitchen
        items.append({
            'name': 'Kitchen Exhaust Ductwork - Welded Black Steel',
            'quantity': round(duct_weight),
            'unit': 'LB',
            'unit_cost': 18.50,
            'total_cost': duct_weight * 18.50,
            'category': 'Kitchen Ventilation'
        })
        
        # Ansul system
        items.append({
            'name': 'Ansul Fire Suppression System',
            'quantity': round(hood_length, 1),
            'unit': 'LF',
            'unit_cost': 225,
            'total_cost': hood_length * 225,
            'category': 'Kitchen Ventilation'
        })
        
        # Walk-in Refrigeration (20% of mechanical budget)
        items.extend([
            {
                'name': 'Walk-in Cooler (10x12) with Remote Refrigeration',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 18500,
                'total_cost': 18500,
                'category': 'Refrigeration'
            },
            {
                'name': 'Walk-in Freezer (8x10) with Remote Refrigeration',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 16500,
                'total_cost': 16500,
                'category': 'Refrigeration'
            },
            {
                'name': 'Remote Refrigeration Rack System',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 12500,
                'total_cost': 12500,
                'category': 'Refrigeration'
            }
        ])
        
        # Beer cooler for bar
        if square_footage >= 3000:
            items.append({
                'name': 'Remote Beer Cooler System',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 8500,
                'total_cost': 8500,
                'category': 'Refrigeration'
            })
        
        # HVAC Systems (35% of mechanical budget)
        # Kitchen needs more cooling
        kitchen_tons = kitchen_sf / 200  # 200 SF per ton for kitchen
        dining_tons = dining_sf / 350   # 350 SF per ton for dining
        
        items.extend([
            {
                'name': 'Kitchen RTU with 100% Outside Air Capability',
                'quantity': round(kitchen_tons, 1),
                'unit': 'TON',
                'unit_cost': 2850,
                'total_cost': kitchen_tons * 2850,
                'category': 'HVAC Equipment'
            },
            {
                'name': 'Dining Area RTU Package Units',
                'quantity': round(dining_tons, 1),
                'unit': 'TON',
                'unit_cost': 2150,
                'total_cost': dining_tons * 2150,
                'category': 'HVAC Equipment'
            }
        ])
        
        # Ductwork for HVAC
        items.extend([
            {
                'name': 'Dining Area Supply/Return Ductwork',
                'quantity': dining_sf / 1000,
                'unit': 'Lot',
                'unit_cost': 4500,
                'total_cost': (dining_sf / 1000) * 4500,
                'category': 'Ductwork'
            },
            {
                'name': 'Kitchen Supply Ductwork',
                'quantity': kitchen_sf / 1000,
                'unit': 'Lot',
                'unit_cost': 3500,
                'total_cost': (kitchen_sf / 1000) * 3500,
                'category': 'Ductwork'
            }
        ])
        
        # Controls and accessories
        items.extend([
            {
                'name': 'Kitchen Hood Controls with Variable Speed',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 8500,
                'total_cost': 8500,
                'category': 'Controls'
            },
            {
                'name': 'Building Management System',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 12500,
                'total_cost': 12500,
                'category': 'Controls'
            },
            {
                'name': 'Testing and Balancing',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 8500,
                'total_cost': 8500,
                'category': 'Commissioning'
            }
        ])
        
        # Calculate current total
        current_total = sum(item['total_cost'] for item in items)
        
        # If we're under budget, add additional items to reach target
        if current_total < budget:
            remaining = budget - current_total
            items.append({
                'name': 'Additional Mechanical Systems and Equipment',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': remaining,
                'total_cost': remaining,
                'category': 'Equipment',
                'description': 'Additional mechanical equipment, controls, and accessories'
            })
        
        return items
    
    def _generate_electrical_items(self, square_footage: float, budget: float) -> List[Dict[str, Any]]:
        """Generate restaurant-specific electrical items (17.5% of budget)"""
        items = []
        
        kitchen_sf = square_footage * 0.3
        
        # Main distribution (20% of electrical budget)
        items.extend([
            {
                'name': 'Main Distribution Panel - 800A, 208V, 3-Phase',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 18500,
                'total_cost': 18500,
                'category': 'Power Distribution'
            },
            {
                'name': 'Kitchen Equipment Panel - 400A, 208V, 3-Phase',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 12500,
                'total_cost': 12500,
                'category': 'Power Distribution'
            }
        ])
        
        # Kitchen equipment power (30% of electrical budget)
        num_circuits = math.ceil(kitchen_sf / 100)  # 1 circuit per 100 SF
        items.extend([
            {
                'name': 'Kitchen Equipment Circuits - 208V 3-Phase',
                'quantity': num_circuits,
                'unit': 'EA',
                'unit_cost': 850,
                'total_cost': num_circuits * 850,
                'category': 'Kitchen Power'
            },
            {
                'name': 'Hood Control Panel with Shunt Trip',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 3500,
                'total_cost': 3500,
                'category': 'Kitchen Power'
            },
            {
                'name': 'Equipment Disconnect Switches',
                'quantity': round(square_footage * 0.005),  # 20 for 4000sf
                'unit': 'EA',
                'unit_cost': 285,
                'total_cost': round(square_footage * 0.005) * 285,
                'category': 'Kitchen Power'
            },
            {
                'name': 'Walk-in Cooler/Freezer Power and Controls',
                'quantity': 2,
                'unit': 'EA',
                'unit_cost': 2500,
                'total_cost': 5000,
                'category': 'Kitchen Power'
            }
        ])
        
        # General power and lighting (35% of electrical budget)
        items.extend([
            {
                'name': 'Dining Area Lighting - Decorative Fixtures',
                'quantity': square_footage * 0.7 / 1000,
                'unit': 'Lot',
                'unit_cost': 8500,
                'total_cost': (square_footage * 0.7 / 1000) * 8500,
                'category': 'Lighting'
            },
            {
                'name': 'Kitchen Lighting - High Output LED',
                'quantity': kitchen_sf / 1000,
                'unit': 'Lot',
                'unit_cost': 6500,
                'total_cost': (kitchen_sf / 1000) * 6500,
                'category': 'Lighting'
            },
            {
                'name': 'Emergency/Exit Lighting',
                'quantity': round(square_footage / 500),
                'unit': 'EA',
                'unit_cost': 425,
                'total_cost': round(square_footage / 500) * 425,
                'category': 'Life Safety'
            }
        ])
        
        # Low voltage systems (15% of electrical budget)
        items.extend([
            {
                'name': 'Fire Alarm System',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 12500,
                'total_cost': 12500,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Security/Camera System',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 8500,
                'total_cost': 8500,
                'category': 'Security'
            },
            {
                'name': 'Data/Communications Infrastructure',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 15000,
                'total_cost': 15000,
                'category': 'Data'
            }
        ])
        
        # Calculate current total
        current_total = sum(item['total_cost'] for item in items)
        
        # If we're under budget, add additional items to reach target
        if current_total < budget:
            remaining = budget - current_total
            items.append({
                'name': 'Additional Electrical Systems and Equipment',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': remaining,
                'total_cost': remaining,
                'category': 'Equipment',
                'description': 'Additional electrical equipment, lighting, and controls'
            })
        
        return items
    
    def _generate_plumbing_items(self, square_footage: float, budget: float) -> List[Dict[str, Any]]:
        """Generate restaurant-specific plumbing items (17.5% of budget)"""
        items = []
        
        kitchen_sf = square_footage * 0.3
        
        # Kitchen plumbing systems (40% of plumbing budget)
        items.extend([
            {
                'name': 'Grease Interceptor - 1500 Gal External',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 12500,
                'total_cost': 12500,
                'category': 'Kitchen Systems'
            },
            {
                'name': 'Kitchen Floor Drains - Heavy Duty with Trap Primers',
                'quantity': round(kitchen_sf / 500),  # 1 per 500 SF
                'unit': 'EA',
                'unit_cost': 850,
                'total_cost': round(kitchen_sf / 500) * 850,
                'category': 'Kitchen Systems'
            },
            {
                'name': 'Pre-Rinse Spray Assemblies',
                'quantity': 2,
                'unit': 'EA',
                'unit_cost': 625,
                'total_cost': 1250,
                'category': 'Kitchen Systems'
            },
            {
                'name': 'Kitchen Equipment Rough-in',
                'quantity': 12,
                'unit': 'EA',
                'unit_cost': 450,
                'total_cost': 5400,
                'category': 'Kitchen Systems'
            },
            {
                'name': 'Dishwasher Booster Heater',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 3500,
                'total_cost': 3500,
                'category': 'Kitchen Systems'
            }
        ])
        
        # Bar plumbing (10% of plumbing budget)
        items.extend([
            {
                'name': 'Bar Sink Systems with Speed Rails',
                'quantity': 3,
                'unit': 'EA',
                'unit_cost': 1250,
                'total_cost': 3750,
                'category': 'Bar Systems'
            },
            {
                'name': 'Beer Line System',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 4500,
                'total_cost': 4500,
                'category': 'Bar Systems'
            },
            {
                'name': 'Bar Equipment Connections',
                'quantity': 6,
                'unit': 'EA',
                'unit_cost': 325,
                'total_cost': 1950,
                'category': 'Bar Systems'
            }
        ])
        
        # Restroom plumbing (25% of plumbing budget)
        num_fixtures = round(square_footage / 200)  # Code-based fixture count
        items.extend([
            {
                'name': 'Water Closets - Commercial Grade',
                'quantity': round(num_fixtures * 0.6),
                'unit': 'EA',
                'unit_cost': 750,
                'total_cost': round(num_fixtures * 0.6) * 750,
                'category': 'Fixtures'
            },
            {
                'name': 'Urinals with Flush Valves',
                'quantity': round(num_fixtures * 0.2),
                'unit': 'EA',
                'unit_cost': 625,
                'total_cost': round(num_fixtures * 0.2) * 625,
                'category': 'Fixtures'
            },
            {
                'name': 'Lavatories with Sensor Faucets',
                'quantity': round(num_fixtures * 0.4),
                'unit': 'EA',
                'unit_cost': 550,
                'total_cost': round(num_fixtures * 0.4) * 550,
                'category': 'Fixtures'
            }
        ])
        
        # Water heating (10% of plumbing budget)
        items.extend([
            {
                'name': 'Water Heater - 100 Gal High Recovery',
                'quantity': 2,
                'unit': 'EA',
                'unit_cost': 3500,
                'total_cost': 7000,
                'category': 'Water Heating'
            },
            {
                'name': 'Mixing Valves and Recirculation',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 2500,
                'total_cost': 2500,
                'category': 'Water Heating'
            }
        ])
        
        # Gas piping for kitchen equipment (15% of plumbing budget)
        items.extend([
            {
                'name': 'Gas Piping to Kitchen Equipment',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.15,
                'total_cost': budget * 0.15,
                'category': 'Gas Piping'
            }
        ])
        
        # Calculate current total
        current_total = sum(item['total_cost'] for item in items)
        
        # If we're under budget, add additional items to reach target
        if current_total < budget:
            remaining = budget - current_total
            items.append({
                'name': 'Additional Plumbing Systems and Equipment',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': remaining,
                'total_cost': remaining,
                'category': 'Equipment',
                'description': 'Additional plumbing fixtures, piping, and accessories'
            })
        
        return items
    
    def _generate_finishes_items(self, square_footage: float, budget: float, service_level: str) -> List[Dict[str, Any]]:
        """Generate finishes INCLUDING kitchen equipment (25% of budget)"""
        items = []
        
        # CRITICAL: Kitchen equipment is part of finishes in restaurant budgets
        # Kitchen Equipment (40% of finishes budget for full-service)
        kitchen_equipment_budget = budget * 0.40
        items.append({
            'name': 'Commercial Kitchen Equipment Package',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': kitchen_equipment_budget,
            'total_cost': kitchen_equipment_budget,
            'category': 'Kitchen Equipment',
            'description': 'Complete cooking line, prep equipment, refrigeration, smallwares'
        })
        
        # Bar Equipment (15% of finishes budget)
        bar_equipment_budget = budget * 0.15
        items.append({
            'name': 'Bar Equipment and Fixtures Package',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': bar_equipment_budget,
            'total_cost': bar_equipment_budget,
            'category': 'Bar Equipment',
            'description': 'Bar refrigeration, glass washers, ice machines, dispensers'
        })
        
        # Dining Furniture (20% of finishes budget)
        furniture_budget = budget * 0.20
        seats = round(square_footage / 15)  # Typical 15 SF per seat
        items.append({
            'name': f'Dining Furniture Package ({seats} seats)',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': furniture_budget,
            'total_cost': furniture_budget,
            'category': 'Furniture',
            'description': 'Tables, chairs, booths, host stand, wait stations'
        })
        
        # POS and Technology (5% of finishes budget)
        items.append({
            'name': 'POS System with Kitchen Display',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': budget * 0.05,
            'total_cost': budget * 0.05,
            'category': 'Technology'
        })
        
        # Actual architectural finishes (20% of finishes budget)
        finishes_budget = budget * 0.20
        
        # Flooring
        items.append({
            'name': 'Restaurant Flooring - Quarry Tile Kitchen/LVT Dining',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': finishes_budget * 0.4 / square_footage,
            'total_cost': finishes_budget * 0.4,
            'category': 'Flooring'
        })
        
        # Wall finishes
        items.append({
            'name': 'Wall Finishes - FRP Kitchen/Decorative Dining',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': finishes_budget * 0.3 / square_footage,
            'total_cost': finishes_budget * 0.3,
            'category': 'Wall Finishes'
        })
        
        # Ceiling
        items.append({
            'name': 'Ceiling - Washable Kitchen/Acoustic Dining',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': finishes_budget * 0.3 / square_footage,
            'total_cost': finishes_budget * 0.3,
            'category': 'Ceiling'
        })
        
        return items
    
    def _generate_structural_items(self, square_footage: float, budget: float) -> List[Dict[str, Any]]:
        """Generate structural items (10% of budget)"""
        items = []
        
        # Foundation (30% of structural)
        items.append({
            'name': 'Foundation/Slab - Reinforced for Kitchen Equipment',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': budget * 0.30 / square_footage,
            'total_cost': budget * 0.30,
            'category': 'Foundation'
        })
        
        # Structural frame (40% of structural)
        items.append({
            'name': 'Structural Frame with Kitchen Hood Support',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': budget * 0.40 / square_footage,
            'total_cost': budget * 0.40,
            'category': 'Structure'
        })
        
        # Roof structure (25% of structural)
        items.append({
            'name': 'Roof Structure with Equipment Curbs',
            'quantity': square_footage,
            'unit': 'SF',
            'unit_cost': budget * 0.25 / square_footage,
            'total_cost': budget * 0.25,
            'category': 'Roof'
        })
        
        # Miscellaneous steel (5% of structural)
        items.append({
            'name': 'Miscellaneous Steel - Equipment Supports',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': budget * 0.05,
            'total_cost': budget * 0.05,
            'category': 'Steel'
        })
        
        return items
    
    def _generate_gc_items(self, budget: float) -> List[Dict[str, Any]]:
        """Generate general conditions items (8% of budget)"""
        items = [
            {
                'name': 'Project Management & Supervision',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.35,
                'total_cost': budget * 0.35,
                'category': 'Management'
            },
            {
                'name': 'Permits and Fees',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.25,
                'total_cost': budget * 0.25,
                'category': 'Permits'
            },
            {
                'name': 'Insurance and Bonds',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.20,
                'total_cost': budget * 0.20,
                'category': 'Insurance'
            },
            {
                'name': 'Temporary Facilities',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.10,
                'total_cost': budget * 0.10,
                'category': 'Temporary'
            },
            {
                'name': 'Final Cleaning and Commissioning',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': budget * 0.10,
                'total_cost': budget * 0.10,
                'category': 'Closeout'
            }
        ]
        
        return items


# Singleton instance
restaurant_scope_service = RestaurantScopeService()