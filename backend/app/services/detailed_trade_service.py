from typing import Dict, List, Any
import math
from app.services.electrical_standards_service import electrical_standards_service

class DetailedTradeService:
    """Service to generate detailed trade-specific breakdowns"""
    
    def generate_detailed_electrical(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed electrical scope items using industry standards"""
        
        # Use the electrical standards service for consistent calculations
        electrical_data = electrical_standards_service.calculate_electrical_items_with_labor(project_data)
        
        # Store the electrical data in project data for later use
        project_data['_electrical_standards_data'] = electrical_data
        
        # Get the V2 calculation details
        v2_calc = electrical_data.get('v2_calculation', {})
        
        # If we have V2 calculation details, use the detailed systems
        if v2_calc and 'systems' in electrical_data:
            # Return the already-calculated systems from V2
            return electrical_data['systems']
        
        # Fall back to detailed systems
        return electrical_data['systems']
    
    def get_electrical_schedule_data(self, project_data: Dict) -> Dict[str, Any]:
        """Get the electrical schedule data from standardized calculations"""
        if '_electrical_standards_data' not in project_data:
            # Generate if not already calculated
            electrical_data = electrical_standards_service.calculate_electrical_items_with_labor(project_data)
            project_data['_electrical_standards_data'] = electrical_data
        return project_data['_electrical_standards_data']
    
    def generate_detailed_hvac(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed HVAC scope items"""
        # Extract project parameters - check both direct and request_data
        request_data = project_data.get('request_data', {})
        square_footage = project_data.get('square_footage', 0) or request_data.get('square_footage', 0)
        building_mix = project_data.get('building_mix', {}) or request_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        ceiling_height = request_data.get('ceiling_height', 10)
        
        warehouse_sf = square_footage * building_mix.get('warehouse', 0)
        office_sf = square_footage * building_mix.get('office', 1)
        restaurant_sf = square_footage * building_mix.get('restaurant', 0)
        
        # Check if this is a restaurant project
        special_requirements = request_data.get('special_requirements', '')
        occupancy_type = request_data.get('occupancy_type', '')
        is_restaurant = (
            restaurant_sf > 0 or 
            occupancy_type == 'restaurant' or
            (special_requirements and 'restaurant' in special_requirements.lower()) or
            (special_requirements and 'commercial kitchen' in special_requirements.lower())
        )
        
        hvac_items = []
        
        # Handle restaurant HVAC specially
        if is_restaurant and restaurant_sf == 0:
            # Pure restaurant, not mixed-use
            restaurant_sf = square_footage
        
        if restaurant_sf > 0:
            # Restaurant-specific HVAC calculations
            kitchen_area = restaurant_sf * 0.3  # Assume 30% is kitchen
            dining_area = restaurant_sf * 0.7   # 70% is dining
            
            # Kitchen exhaust hood system
            hood_length = math.ceil(kitchen_area / 50)  # Rough calc for hood length
            hvac_items.extend([
                {
                    'name': 'Type I Exhaust Hood System',
                    'quantity': hood_length,
                    'unit': 'LF',
                    'unit_cost': 850,
                    'category': 'Kitchen Ventilation'
                },
                {
                    'name': 'Make-up Air Unit - Kitchen',
                    'quantity': math.ceil(kitchen_area * 1.2 / 1000),  # CFM calculation
                    'unit': 'Ton',
                    'unit_cost': 3500,
                    'category': 'Kitchen Ventilation'
                },
                {
                    'name': 'Ansul Fire Suppression System',
                    'quantity': hood_length,
                    'unit': 'LF',
                    'unit_cost': 225,
                    'category': 'Kitchen Ventilation'
                },
                {
                    'name': 'Kitchen Exhaust Ductwork - Stainless',
                    'quantity': math.ceil(kitchen_area * 0.8),
                    'unit': 'LB',
                    'unit_cost': 12.50,
                    'category': 'Kitchen Ventilation'
                }
            ])
            
            # Walk-in coolers/freezers
            if restaurant_sf >= 2000:
                hvac_items.extend([
                    {
                        'name': 'Walk-in Cooler (8x10)',
                        'quantity': 1,
                        'unit': 'EA',
                        'unit_cost': 14800,
                        'category': 'Refrigeration'
                    },
                    {
                        'name': 'Walk-in Freezer (6x8)',
                        'quantity': 1,
                        'unit': 'EA',
                        'unit_cost': 12600,
                        'category': 'Refrigeration'
                    },
                    {
                        'name': 'Refrigeration Compressor/Condenser Units',
                        'quantity': 2,
                        'unit': 'EA',
                        'unit_cost': 4500,
                        'category': 'Refrigeration'
                    }
                ])
            
            # Dining area HVAC
            dining_tons = math.ceil(dining_area / 250)  # Higher load for dining
            hvac_items.extend([
                {
                    'name': 'Restaurant RTU - High Efficiency',
                    'quantity': math.ceil(dining_tons / 5),  # 5-ton units
                    'unit': 'EA',
                    'unit_cost': 9250,
                    'category': 'HVAC Equipment'
                },
                {
                    'name': 'Dining Area Ductwork',
                    'quantity': dining_area / 1000,
                    'unit': 'Lot',
                    'unit_cost': 4500,
                    'category': 'Ductwork'
                }
            ])
        
        # Simplified HVAC calculation for mixed-use
        # Warehouse: Basic RTUs, Office: VAV system
        
        # Warehouse HVAC
        warehouse_rtus = max(1, math.ceil(warehouse_sf / 8000))  # 1 RTU per 8000 SF
        hvac_items.append({
            'name': 'Rooftop Unit - 15 Ton, Gas/Electric (Warehouse)',
            'quantity': warehouse_rtus,
            'unit': 'EA',
            'unit_cost': 15000,  # $15k per unit
            'category': 'Equipment'
        })
        
        # Office HVAC (more complex)
        office_vav_units = max(1, math.ceil(office_sf / 7000))  # 1 unit per 7000 SF
        hvac_items.append({
            'name': 'VAV Air Handler - 20 Ton (Office)',
            'quantity': office_vav_units,
            'unit': 'EA',
            'unit_cost': 20000,  # $20k per unit
            'category': 'Equipment'
        })
        
        # Installation and connections
        total_units = warehouse_rtus + office_vav_units
        hvac_items.extend([
            {
                'name': 'Equipment Installation & Rigging',
                'quantity': total_units,
                'unit': 'EA',
                'unit_cost': 3500,
                'category': 'Equipment'
            },
            {
                'name': 'Electrical/Gas Connections',
                'quantity': total_units,
                'unit': 'EA',
                'unit_cost': 2000,
                'category': 'Equipment'
            }
        ])
        
        # Simplified ductwork based on space type
        # Warehouse: Basic exposed spiral duct
        hvac_items.append({
            'name': 'Warehouse Ductwork Package',
            'quantity': warehouse_sf / 1000,  # Per 1000 SF
            'unit': 'Lot',
            'unit_cost': 3000,  # $3/SF = $94.5k total
            'category': 'Ductwork'
        })
        
        # Office: Complex VAV ductwork
        hvac_items.append({
            'name': 'Office VAV Ductwork Package',
            'quantity': office_sf / 1000,  # Per 1000 SF
            'unit': 'Lot',
            'unit_cost': 5000,  # $5/SF = $67.5k total
            'category': 'Ductwork'
        })
        
        # Simplified controls and ventilation
        hvac_items.extend([
            {
                'name': 'Warehouse Controls/Ventilation Package',
                'quantity': warehouse_sf / 1000,
                'unit': 'Lot',
                'unit_cost': 2500,  # $2.5/SF total for warehouse HVAC extras
                'category': 'Controls'
            },
            {
                'name': 'Office BMS/Controls Package',
                'quantity': office_sf / 1000,
                'unit': 'Lot',
                'unit_cost': 5000,  # $5/SF total for office HVAC extras  
                'category': 'Controls'
            },
            {
                'name': 'Testing & Commissioning',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 15000,
                'category': 'Commissioning'
            }
        ])
        
        # Calculate total costs
        for item in hvac_items:
            item['total_cost'] = item['quantity'] * item['unit_cost']
        
        return hvac_items
    
    def generate_detailed_plumbing(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed plumbing scope items based on building characteristics"""
        # Extract project parameters - check both direct and request_data
        request_data = project_data.get('request_data', {})
        square_footage = project_data.get('square_footage', 0) or request_data.get('square_footage', 0)
        building_mix = project_data.get('building_mix', {}) or request_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        special_requirements = request_data.get('special_requirements', '')
        if special_requirements is None:
            special_requirements = ''
        
        # Determine if this is a restaurant or has commercial kitchen
        has_commercial_kitchen = (
            'restaurant' in building_mix or
            'commercial kitchen' in special_requirements.lower() or
            'food service' in special_requirements.lower()
        )
        
        # For mixed-use, calculate weighted plumbing complexity
        if building_mix:
            # Calculate bathrooms based on occupancy for each space type
            total_fixture_groups = 0
            plumbing_complexity_score = 0  # Track overall complexity
            
            for space_type, percentage in building_mix.items():
                space_sf = square_footage * percentage
                if space_type == 'warehouse':
                    # Minimal - 1 bathroom per 10,000 SF
                    fixture_groups = max(1, math.ceil(space_sf / 10000))
                    plumbing_complexity_score += percentage * 1  # Low complexity
                elif space_type == 'office':
                    # Standard - 1 bathroom per 2,500 SF
                    fixture_groups = max(1, math.ceil(space_sf / 2500))
                    plumbing_complexity_score += percentage * 3  # Medium complexity
                elif space_type == 'retail':
                    # Basic - 1 bathroom per 5,000 SF
                    fixture_groups = max(1, math.ceil(space_sf / 5000))
                    plumbing_complexity_score += percentage * 2  # Low-medium complexity
                elif space_type == 'restaurant':
                    # High - 1 bathroom per 1,000 SF plus kitchen needs
                    fixture_groups = max(2, math.ceil(space_sf / 1000))
                    plumbing_complexity_score += percentage * 10  # Very high complexity
                else:
                    # Default to office standard
                    fixture_groups = max(1, math.ceil(space_sf / 2500))
                    plumbing_complexity_score += percentage * 3
                total_fixture_groups += fixture_groups
            
            num_bathrooms = max(1, int(total_fixture_groups))
            is_complex_plumbing = plumbing_complexity_score > 5  # Threshold for complex plumbing
        else:
            # Default calculation for non-mixed use
            num_bathrooms = max(1, math.ceil(square_footage / 5000))
            is_complex_plumbing = False
        
        plumbing_items = []
        
        # Fixtures
        plumbing_items.extend([
            {
                'name': 'Water Closet - Floor Mount, Commercial',
                'quantity': num_bathrooms * 2,  # 2 per bathroom average
                'unit': 'EA',
                'unit_cost': 650,
                'category': 'Fixtures'
            },
            {
                'name': 'Urinal - Wall Mount w/ Flush Valve',
                'quantity': num_bathrooms,  # 1 per men's room
                'unit': 'EA',
                'unit_cost': 725,
                'category': 'Fixtures'
            },
            {
                'name': 'Lavatory - Wall Mount w/ Faucet',
                'quantity': num_bathrooms * 2,
                'unit': 'EA',
                'unit_cost': 485,
                'category': 'Fixtures'
            },
            {
                'name': 'Service Sink - Mop Sink',
                'quantity': max(1, math.ceil(square_footage / 25000)),
                'unit': 'EA',
                'unit_cost': 825,
                'category': 'Fixtures'
            }
        ])
        
        # Break room fixtures
        if building_mix.get('office', 0) > 0:
            plumbing_items.extend([
                {
                    'name': 'Kitchen Sink - Double Bowl SS',
                    'quantity': max(1, math.ceil(square_footage / 20000)),
                    'unit': 'EA',
                    'unit_cost': 925,
                    'category': 'Fixtures'
                },
                {
                    'name': 'Drinking Fountain - ADA Bi-Level',
                    'quantity': math.ceil(square_footage / 15000),
                    'unit': 'EA',
                    'unit_cost': 1450,
                    'category': 'Fixtures'
                }
            ])
        
        # Water heater
        total_fixture_units = (num_bathrooms * 6) + 4  # Approximate FU calculation
        heater_size = 50 if total_fixture_units < 50 else 75
        
        plumbing_items.append({
            'name': f'Water Heater - {heater_size} Gal, Gas',
            'quantity': 1,
            'unit': 'EA',
            'unit_cost': heater_size * 35,
            'category': 'Equipment'
        })
        
        # Piping - Supply
        # Adjust piping density based on building type
        if building_mix.get('warehouse', 0) > 0.5 and not has_commercial_kitchen:
            # Warehouse dominant - minimal piping
            supply_footage = square_footage * 0.15  # Much less piping needed
        elif has_commercial_kitchen or is_complex_plumbing:
            # Restaurant/complex - extensive piping
            supply_footage = square_footage * 1.2  # More piping for kitchen equipment
        else:
            # Standard office/retail
            supply_footage = square_footage * 0.4  # Moderate piping
        
        # Warehouse needs very simple distribution
        if building_mix.get('warehouse', 0) > 0.5:
            # Simplified piping for warehouse
            plumbing_items.extend([
                {
                    'name': 'Copper Water Pipe - Main Distribution',
                    'quantity': supply_footage * 0.2,  # Only 20% of total
                    'unit': 'LF',
                    'unit_cost': 22,  # Blended rate
                    'category': 'Piping'
                },
                {
                    'name': 'Copper Water Pipe - Branch Lines',
                    'quantity': supply_footage * 0.8,  # 80% smaller pipes
                    'unit': 'LF',
                    'unit_cost': 16,  # Blended rate for 3/4" and 1/2"
                    'category': 'Piping'
                }
            ])
        else:
            # Standard distribution for office/retail
            plumbing_items.extend([
                {
                    'name': 'Copper Water Pipe - 2"',
                    'quantity': supply_footage * 0.1,  # 10% main lines
                    'unit': 'LF',
                    'unit_cost': 38,
                    'category': 'Piping'
                },
                {
                    'name': 'Copper Water Pipe - 1"',
                    'quantity': supply_footage * 0.3,  # 30% branch lines
                    'unit': 'LF',
                    'unit_cost': 24,
                    'category': 'Piping'
                },
                {
                    'name': 'Copper Water Pipe - 3/4"',
                    'quantity': supply_footage * 0.4,  # 40% small branches
                    'unit': 'LF',
                    'unit_cost': 18,
                    'category': 'Piping'
                },
                {
                    'name': 'Copper Water Pipe - 1/2"',
                    'quantity': supply_footage * 0.2,  # 20% fixture connections
                    'unit': 'LF',
                    'unit_cost': 14,
                    'category': 'Piping'
                }
            ])
        
        # Piping - Waste
        # Adjust waste piping based on building type
        if building_mix.get('warehouse', 0) > 0.5 and not has_commercial_kitchen:
            # Warehouse dominant - minimal waste piping
            waste_footage = square_footage * 0.1  # Much less waste piping
        elif has_commercial_kitchen or is_complex_plumbing:
            # Restaurant/complex - extensive waste piping
            waste_footage = square_footage * 0.9  # More waste for kitchen drains
        else:
            # Standard office/retail
            waste_footage = square_footage * 0.3  # Moderate waste piping
        
        # Simplified waste piping for warehouse
        if building_mix.get('warehouse', 0) > 0.5:
            plumbing_items.extend([
                {
                    'name': 'Cast Iron Waste Pipe - Main',
                    'quantity': waste_footage * 0.3,  # Less main waste lines
                    'unit': 'LF',
                    'unit_cost': 38,  # Blended 4" and 3"
                    'category': 'Piping'
                },
                {
                    'name': 'PVC Waste Pipe - Branch',
                    'quantity': waste_footage * 0.7,  # More PVC branches
                    'unit': 'LF',
                    'unit_cost': 18,
                    'category': 'Piping'
                }
            ])
        else:
            plumbing_items.extend([
                {
                    'name': 'Cast Iron Waste Pipe - 4"',
                    'quantity': waste_footage * 0.2,
                    'unit': 'LF',
                    'unit_cost': 42,
                    'category': 'Piping'
                },
                {
                    'name': 'Cast Iron Waste Pipe - 3"',
                    'quantity': waste_footage * 0.3,
                    'unit': 'LF',
                    'unit_cost': 35,
                    'category': 'Piping'
                },
                {
                    'name': 'PVC Waste Pipe - 2"',
                    'quantity': waste_footage * 0.5,
                    'unit': 'LF',
                    'unit_cost': 18,
                    'category': 'Piping'
                }
            ])
        
        # Insulation
        # Only insulate hot water and exposed piping
        if building_mix.get('warehouse', 0) > 0.5:
            insulation_factor = 0.2  # Minimal insulation for warehouse
        else:
            insulation_factor = 0.6  # Standard insulation for office/retail
        
        plumbing_items.append({
            'name': 'Pipe Insulation - Fiberglass',
            'quantity': supply_footage * insulation_factor,
            'unit': 'LF',
            'unit_cost': 8.50,
            'category': 'Insulation'
        })
        
        # Floor drains
        warehouse_sf = square_footage * building_mix.get('warehouse', 0)
        num_floor_drains = math.ceil(warehouse_sf / 5000) if warehouse_sf > 0 else 2
        
        plumbing_items.append({
            'name': 'Floor Drain - 4" CI w/ Trap',
            'quantity': num_floor_drains,
            'unit': 'EA',
            'unit_cost': 385,
            'category': 'Drainage'
        })
        
        # Cleanouts
        plumbing_items.append({
            'name': 'Cleanout - 4" w/ Access Cover',
            'quantity': math.ceil(waste_footage / 100),  # Every 100 ft
            'unit': 'EA',
            'unit_cost': 225,
            'category': 'Drainage'
        })
        
        # Roof drains
        roof_area = square_footage / project_data.get('num_floors', 1)
        num_roof_drains = math.ceil(roof_area / 4000)  # 1 per 4000 sqft
        
        plumbing_items.extend([
            {
                'name': 'Roof Drain - 4" w/ Dome',
                'quantity': num_roof_drains,
                'unit': 'EA',
                'unit_cost': 625,
                'category': 'Drainage'
            },
            {
                'name': 'Overflow Drain - 4"',
                'quantity': num_roof_drains,
                'unit': 'EA',
                'unit_cost': 425,
                'category': 'Drainage'
            }
        ])
        
        # Valves and specialties
        plumbing_items.extend([
            {
                'name': 'Gate Valve - 2"',
                'quantity': 4,
                'unit': 'EA',
                'unit_cost': 285,
                'category': 'Valves'
            },
            {
                'name': 'Ball Valve - Various Sizes',
                'quantity': num_bathrooms * 6 + 10,
                'unit': 'EA',
                'unit_cost': 85,
                'category': 'Valves'
            },
            {
                'name': 'Backflow Preventer - 2"',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 2850,
                'category': 'Specialties'
            },
            {
                'name': 'Pressure Reducing Valve',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 1250,
                'category': 'Specialties'
            }
        ])
        
        # Hose bibs
        building_perimeter = 2 * (math.sqrt(square_footage) + math.sqrt(square_footage) * 1.2)
        num_hose_bibs = math.ceil(building_perimeter / 150)
        
        plumbing_items.append({
            'name': 'Hose Bibb - Frost Proof',
            'quantity': num_hose_bibs,
            'unit': 'EA',
            'unit_cost': 185,
            'category': 'Fixtures'
        })
        
        # Add restaurant/kitchen specific items if needed
        if has_commercial_kitchen:
            # Grease interceptor system
            plumbing_items.extend([
                {
                    'name': 'Grease Interceptor - 1000 Gal',
                    'quantity': 1,
                    'unit': 'EA',
                    'unit_cost': 8500,
                    'category': 'Kitchen Systems'
                },
                {
                    'name': 'Kitchen Floor Drains - Heavy Duty',
                    'quantity': math.ceil(building_mix.get('restaurant', 0) * square_footage / 500),
                    'unit': 'EA',
                    'unit_cost': 650,
                    'category': 'Kitchen Systems'
                },
                {
                    'name': 'Pre-Rinse Spray Assembly',
                    'quantity': 2,
                    'unit': 'EA',
                    'unit_cost': 485,
                    'category': 'Kitchen Systems'
                },
                {
                    'name': 'Kitchen Equipment Connections',
                    'quantity': 8,
                    'unit': 'EA',
                    'unit_cost': 325,
                    'category': 'Kitchen Systems'
                }
            ])
        
        # Gas piping if needed
        if 'gas' in special_requirements.lower() or project_data.get('has_gas', True):
            # Scale gas piping based on building type
            gas_multiplier = 1.0
            if has_commercial_kitchen:
                gas_multiplier = 3.0  # Much more gas for kitchen equipment
            elif building_mix.get('warehouse', 0) > 0.5:
                gas_multiplier = 0.5  # Less gas for warehouse
            
            plumbing_items.extend([
                {
                    'name': 'Gas Pipe - 2" Black Steel',
                    'quantity': 100 * gas_multiplier,
                    'unit': 'LF',
                    'unit_cost': 28,
                    'category': 'Gas Piping'
                },
                {
                    'name': 'Gas Pipe - 1" Black Steel',
                    'quantity': 200 * gas_multiplier,
                    'unit': 'LF',
                    'unit_cost': 18,
                    'category': 'Gas Piping'
                },
                {
                    'name': 'Gas Shut-off Valve',
                    'quantity': max(3, int(5 * gas_multiplier)),
                    'unit': 'EA',
                    'unit_cost': 125,
                    'category': 'Gas Piping'
                }
            ])
        
        # Calculate total costs
        for item in plumbing_items:
            item['total_cost'] = item['quantity'] * item['unit_cost']
        
        return plumbing_items
    
    def enhance_trade_scope(self, project_data: Dict, trade: str) -> Dict[str, Any]:
        """Enhance the basic scope with detailed trade items"""
        
        # Extract project details
        request_data = project_data.get('request_data', {})
        
        # Generate detailed items based on trade
        if trade.lower() == 'electrical':
            detailed_items = self.generate_detailed_electrical(project_data)
        elif trade.lower() == 'hvac':
            detailed_items = self.generate_detailed_hvac(project_data)
        elif trade.lower() == 'plumbing':
            detailed_items = self.generate_detailed_plumbing(project_data)
        else:
            return project_data  # Return unchanged for other trades
        
        # Group items by category
        categories = {}
        for item in detailed_items:
            cat_name = item.get('category', 'General')
            if cat_name not in categories:
                categories[cat_name] = {
                    'name': cat_name,
                    'systems': [],
                    'subtotal': 0
                }
            
            categories[cat_name]['systems'].append({
                'name': item['name'],
                'quantity': item['quantity'],
                'unit': item['unit'],
                'unit_cost': item['unit_cost'],
                'total_cost': item['total_cost'],
                'specifications': {}
            })
            categories[cat_name]['subtotal'] += item['total_cost']
        
        # Replace the generic trade category with detailed categories
        enhanced_data = project_data.copy()
        
        # Find and replace the trade category
        trade_mapping = {
            'electrical': 'Electrical',
            'plumbing': 'Plumbing',
            'hvac': 'Mechanical'
        }
        
        target_category = trade_mapping.get(trade.lower())
        if target_category:
            # Remove the generic category
            enhanced_data['categories'] = [
                cat for cat in enhanced_data['categories'] 
                if cat['name'] != target_category
            ]
            
            # Add detailed categories
            enhanced_data['categories'].extend(list(categories.values()))
            
            # Recalculate totals
            enhanced_data['subtotal'] = sum(cat['subtotal'] for cat in enhanced_data['categories'])
            enhanced_data['contingency_amount'] = enhanced_data['subtotal'] * (enhanced_data.get('contingency_percentage', 10) / 100)
            enhanced_data['total_cost'] = enhanced_data['subtotal'] + enhanced_data['contingency_amount']
            enhanced_data['cost_per_sqft'] = enhanced_data['total_cost'] / request_data.get('square_footage', 1)
        
        return enhanced_data


detailed_trade_service = DetailedTradeService()