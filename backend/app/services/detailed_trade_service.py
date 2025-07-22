from typing import Dict, List, Any
import math

class DetailedTradeService:
    """Service to generate detailed trade-specific breakdowns"""
    
    def generate_detailed_electrical(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed electrical scope items"""
        
        square_footage = project_data.get('square_footage', 0)
        num_floors = project_data.get('num_floors', 1)
        building_type = project_data.get('project_type', 'commercial')
        building_mix = project_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        
        # Calculate space allocations
        warehouse_sf = square_footage * building_mix.get('warehouse', 0)
        office_sf = square_footage * building_mix.get('office', 1)
        
        electrical_items = []
        
        # Service entrance and main panel
        total_load = square_footage * 5  # 5W/sqft average
        amp_rating = math.ceil(total_load / 208 / 1.732 / 0.8)  # 208V 3-phase, 80% derating
        amp_rating = max(400, min(round(amp_rating / 100) * 100, 3000))  # Round to standard sizes
        
        electrical_items.append({
            'name': f'Service Entrance - {amp_rating}A, 208V 3-Phase',
            'quantity': 1,
            'unit': 'EA',
            'unit_cost': amp_rating * 15,  # $15 per amp
            'category': 'Service & Distribution'
        })
        
        electrical_items.append({
            'name': f'Main Distribution Panel - {amp_rating}A MLO',
            'quantity': 1,
            'unit': 'EA',
            'unit_cost': amp_rating * 8,
            'category': 'Service & Distribution'
        })
        
        # Sub-panels
        num_subpanels = math.ceil(square_footage / 15000)  # 1 per 15,000 sqft
        electrical_items.append({
            'name': 'Sub-Panel - 225A, 42 Circuit',
            'quantity': num_subpanels,
            'unit': 'EA',
            'unit_cost': 2500,
            'category': 'Service & Distribution'
        })
        
        # Feeders
        electrical_items.append({
            'name': 'Feeder Conduit & Wire - 225A',
            'quantity': num_subpanels * 150,  # 150 LF average per panel
            'unit': 'LF',
            'unit_cost': 45,
            'category': 'Service & Distribution'
        })
        
        # Branch circuits
        num_circuits = math.ceil(square_footage / 500)  # 1 circuit per 500 sqft
        electrical_items.append({
            'name': 'Branch Circuit - 20A, #12 MC Cable',
            'quantity': num_circuits,
            'unit': 'EA',
            'unit_cost': 850,  # Average 100' run at $8.50/ft
            'category': 'Branch Wiring'
        })
        
        # Lighting by area type
        if warehouse_sf > 0:
            num_highbay = math.ceil(warehouse_sf / 400)  # 1 per 400 sqft
            electrical_items.append({
                'name': 'LED High Bay Fixture - 150W',
                'quantity': num_highbay,
                'unit': 'EA',
                'unit_cost': 425,
                'category': 'Lighting'
            })
        
        if office_sf > 0:
            num_office_fixtures = math.ceil(office_sf / 100)  # 1 per 100 sqft
            electrical_items.append({
                'name': 'LED Troffer 2x4 - 40W',
                'quantity': num_office_fixtures,
                'unit': 'EA',
                'unit_cost': 185,
                'category': 'Lighting'
            })
        
        # Exterior lighting
        building_perimeter = 2 * (math.sqrt(square_footage) + math.sqrt(square_footage) * 1.2)
        num_exterior = math.ceil(building_perimeter / 50)  # 1 per 50 LF
        electrical_items.append({
            'name': 'LED Wall Pack - 40W',
            'quantity': num_exterior,
            'unit': 'EA',
            'unit_cost': 275,
            'category': 'Lighting'
        })
        
        # Receptacles
        num_standard_recep = math.ceil(office_sf / 150) + math.ceil(warehouse_sf / 1000)
        electrical_items.append({
            'name': 'Duplex Receptacle - 20A',
            'quantity': num_standard_recep,
            'unit': 'EA',
            'unit_cost': 85,
            'category': 'Devices'
        })
        
        # GFCI receptacles
        num_gfci = math.ceil(square_footage / 5000)  # Bathrooms, break rooms, etc
        electrical_items.append({
            'name': 'GFCI Receptacle - 20A',
            'quantity': num_gfci * 4,
            'unit': 'EA',
            'unit_cost': 125,
            'category': 'Devices'
        })
        
        # Equipment connections
        electrical_items.extend([
            {
                'name': 'HVAC Equipment Disconnect - 60A',
                'quantity': math.ceil(square_footage / 15000),  # Per RTU
                'unit': 'EA',
                'unit_cost': 350,
                'category': 'Equipment Connections'
            },
            {
                'name': 'Equipment Connection - Misc',
                'quantity': 10,
                'unit': 'EA',
                'unit_cost': 250,
                'category': 'Equipment Connections'
            }
        ])
        
        # Emergency systems
        electrical_items.extend([
            {
                'name': 'Exit Sign - LED',
                'quantity': math.ceil(square_footage / 2500),
                'unit': 'EA',
                'unit_cost': 165,
                'category': 'Life Safety'
            },
            {
                'name': 'Emergency Light - LED Twin Head',
                'quantity': math.ceil(square_footage / 2000),
                'unit': 'EA',
                'unit_cost': 225,
                'category': 'Life Safety'
            }
        ])
        
        # Fire alarm
        electrical_items.extend([
            {
                'name': 'Fire Alarm Control Panel',
                'quantity': 1,
                'unit': 'EA',
                'unit_cost': 4500,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Smoke Detector',
                'quantity': math.ceil(square_footage / 1000),
                'unit': 'EA',
                'unit_cost': 185,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Horn/Strobe Device',
                'quantity': math.ceil(square_footage / 2000),
                'unit': 'EA',
                'unit_cost': 165,
                'category': 'Fire Alarm'
            },
            {
                'name': 'Pull Station',
                'quantity': max(4, math.ceil(square_footage / 5000)),
                'unit': 'EA',
                'unit_cost': 125,
                'category': 'Fire Alarm'
            }
        ])
        
        # Low voltage
        electrical_items.extend([
            {
                'name': 'Data Cable - CAT6',
                'quantity': num_standard_recep * 2 * 100,  # 2 drops per outlet, 100ft avg
                'unit': 'LF',
                'unit_cost': 1.25,
                'category': 'Low Voltage'
            },
            {
                'name': 'Data Outlet - Dual CAT6',
                'quantity': num_standard_recep,
                'unit': 'EA',
                'unit_cost': 95,
                'category': 'Low Voltage'
            }
        ])
        
        # Calculate total costs
        for item in electrical_items:
            item['total_cost'] = item['quantity'] * item['unit_cost']
        
        return electrical_items
    
    def generate_detailed_hvac(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed HVAC scope items"""
        square_footage = project_data.get('square_footage', 0)
        building_mix = project_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        ceiling_height = project_data.get('ceiling_height', 10)
        
        warehouse_sf = square_footage * building_mix.get('warehouse', 0)
        office_sf = square_footage * building_mix.get('office', 1)
        
        hvac_items = []
        
        # Calculate tonnage requirements
        warehouse_tons = warehouse_sf * ceiling_height * 1.0 / 500  # 1 ton per 500 CF for warehouse
        office_tons = office_sf * 45 / 12000  # 45 BTU/sqft for office
        total_tons = warehouse_tons + office_tons
        
        # Rooftop units
        num_rtus = math.ceil(total_tons / 40)  # 40 ton max unit size
        tons_per_unit = math.ceil(total_tons / num_rtus / 5) * 5  # Round to 5 ton increments
        
        hvac_items.append({
            'name': f'Rooftop Unit - {tons_per_unit} Ton, Gas/Electric',
            'quantity': num_rtus,
            'unit': 'EA',
            'unit_cost': tons_per_unit * 1200,  # $1200/ton
            'category': 'Equipment'
        })
        
        # Curbs and accessories
        hvac_items.extend([
            {
                'name': f'Roof Curb - {tons_per_unit} Ton RTU',
                'quantity': num_rtus,
                'unit': 'EA',
                'unit_cost': 850,
                'category': 'Equipment'
            },
            {
                'name': 'RTU Electrical Connection',
                'quantity': num_rtus,
                'unit': 'EA',
                'unit_cost': 1500,
                'category': 'Equipment'
            },
            {
                'name': 'Gas Piping to RTU',
                'quantity': num_rtus * 50,  # 50 LF average
                'unit': 'LF',
                'unit_cost': 35,
                'category': 'Piping'
            }
        ])
        
        # Ductwork
        total_cfm = total_tons * 400  # 400 CFM/ton
        
        # Main trunk ducts
        hvac_items.append({
            'name': 'Supply Duct - Main Trunk (24"x16")',
            'quantity': square_footage / 100,  # LF of main trunk
            'unit': 'LF',
            'unit_cost': 85,
            'category': 'Ductwork'
        })
        
        hvac_items.append({
            'name': 'Return Duct - Main Trunk (30"x20")',
            'quantity': square_footage / 150,
            'unit': 'LF',
            'unit_cost': 95,
            'category': 'Ductwork'
        })
        
        # Branch ducts
        hvac_items.append({
            'name': 'Supply Branch Duct - Spiral (10" dia)',
            'quantity': square_footage / 50,
            'unit': 'LF',
            'unit_cost': 28,
            'category': 'Ductwork'
        })
        
        # Diffusers and grilles
        num_diffusers = math.ceil(office_sf / 200) + math.ceil(warehouse_sf / 800)
        hvac_items.extend([
            {
                'name': 'Supply Diffuser - 24"x24" Lay-in',
                'quantity': math.ceil(office_sf / 200),
                'unit': 'EA',
                'unit_cost': 165,
                'category': 'Terminals'
            },
            {
                'name': 'Supply Diffuser - Round 12"',
                'quantity': math.ceil(warehouse_sf / 800),
                'unit': 'EA',
                'unit_cost': 125,
                'category': 'Terminals'
            },
            {
                'name': 'Return Grille - 24"x24"',
                'quantity': math.ceil(square_footage / 1500),
                'unit': 'EA',
                'unit_cost': 145,
                'category': 'Terminals'
            }
        ])
        
        # VAV boxes for office areas
        if office_sf > 5000:
            num_vav = math.ceil(office_sf / 1500)
            hvac_items.append({
                'name': 'VAV Box w/ Hot Water Reheat',
                'quantity': num_vav,
                'unit': 'EA',
                'unit_cost': 1850,
                'category': 'Terminals'
            })
        
        # Exhaust fans
        hvac_items.extend([
            {
                'name': 'Restroom Exhaust Fan - 150 CFM',
                'quantity': math.ceil(square_footage / 10000) * 2,
                'unit': 'EA',
                'unit_cost': 425,
                'category': 'Exhaust'
            },
            {
                'name': 'General Exhaust Fan - 1000 CFM',
                'quantity': math.ceil(warehouse_sf / 20000),
                'unit': 'EA',
                'unit_cost': 1250,
                'category': 'Exhaust'
            }
        ])
        
        # Controls
        hvac_items.extend([
            {
                'name': 'DDC Control System',
                'quantity': 1,
                'unit': 'LS',
                'unit_cost': 15000 + (square_footage * 0.5),
                'category': 'Controls'
            },
            {
                'name': 'Thermostat - Programmable',
                'quantity': num_rtus + math.ceil(office_sf / 2500),
                'unit': 'EA',
                'unit_cost': 385,
                'category': 'Controls'
            },
            {
                'name': 'CO2 Sensor',
                'quantity': math.ceil(office_sf / 5000),
                'unit': 'EA',
                'unit_cost': 425,
                'category': 'Controls'
            }
        ])
        
        # Condensate drainage
        hvac_items.append({
            'name': 'Condensate Drain Piping',
            'quantity': num_rtus * 30,  # 30 LF per unit
            'unit': 'LF',
            'unit_cost': 18,
            'category': 'Piping'
        })
        
        # Testing and balancing
        hvac_items.append({
            'name': 'Testing & Balancing',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': square_footage * 0.35,
            'category': 'Commissioning'
        })
        
        # Calculate total costs
        for item in hvac_items:
            item['total_cost'] = item['quantity'] * item['unit_cost']
        
        return hvac_items
    
    def generate_detailed_plumbing(self, project_data: Dict) -> List[Dict[str, Any]]:
        """Generate detailed plumbing scope items"""
        square_footage = project_data.get('square_footage', 0)
        building_mix = project_data.get('building_mix', {})
        if building_mix is None:
            building_mix = {}
        special_requirements = project_data.get('special_requirements', '')
        if special_requirements is None:
            special_requirements = ''
        
        # Extract bathroom count from special requirements
        import re
        bathroom_match = re.search(r'(\d+)\s*bathroom', special_requirements, re.IGNORECASE)
        num_bathrooms = int(bathroom_match.group(1)) if bathroom_match else math.ceil(square_footage / 15000)
        
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
        supply_footage = square_footage * 0.8  # 0.8 LF per sqft average
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
        waste_footage = square_footage * 0.6
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
        plumbing_items.append({
            'name': 'Pipe Insulation - Fiberglass',
            'quantity': supply_footage * 0.6,  # Insulate 60% of supply
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
        
        # Gas piping if needed
        if 'gas' in special_requirements.lower() or project_data.get('has_gas', True):
            plumbing_items.extend([
                {
                    'name': 'Gas Pipe - 2" Black Steel',
                    'quantity': 100,
                    'unit': 'LF',
                    'unit_cost': 28,
                    'category': 'Gas Piping'
                },
                {
                    'name': 'Gas Pipe - 1" Black Steel',
                    'quantity': 200,
                    'unit': 'LF',
                    'unit_cost': 18,
                    'category': 'Gas Piping'
                },
                {
                    'name': 'Gas Shut-off Valve',
                    'quantity': 5,
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
            detailed_items = self.generate_detailed_electrical(request_data)
        elif trade.lower() == 'hvac':
            detailed_items = self.generate_detailed_hvac(request_data)
        elif trade.lower() == 'plumbing':
            detailed_items = self.generate_detailed_plumbing(request_data)
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