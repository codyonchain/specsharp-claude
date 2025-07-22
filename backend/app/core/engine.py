from typing import List, Dict, Any, Tuple, Optional
import hashlib
import json
import logging
from app.models.scope import (
    ScopeRequest, ScopeResponse, ScopeCategory,
    BuildingSystem, ProjectType, ClimateZone
)
from datetime import datetime
import uuid
import re
from app.services.detailed_trade_service import detailed_trade_service

logger = logging.getLogger(__name__)


class DeterministicScopeEngine:
    def __init__(self):
        self.base_systems = self._initialize_base_systems()
        self.cost_multipliers = self._initialize_cost_multipliers()
        self.regional_multipliers = self._initialize_regional_multipliers()
        self.city_multipliers = self._initialize_city_multipliers()
        self.space_type_rates = self._initialize_space_type_rates()
        self.cost_validation_ranges = self._initialize_validation_ranges()
        self.building_characteristics = self._initialize_building_characteristics()
        self.benchmark_ranges = self._initialize_benchmark_ranges()
    
    def _initialize_base_systems(self) -> Dict[str, List[Dict[str, Any]]]:
        # Base costs will be dynamically calculated based on space type
        # These are defaults for simple buildings
        return {
            "structural": [
                {"name": "Foundation/Slab", "base_cost_per_sqft": 5.0, "unit": "sqft"},
                {"name": "Structural Frame", "base_cost_per_sqft": 7.0, "unit": "sqft"},
                {"name": "Roof Structure", "base_cost_per_sqft": 2.0, "unit": "sqft"},
            ],
            "mechanical": [
                {"name": "HVAC Equipment", "base_cost_per_sqft": 4.5, "unit": "sqft"},   # RTUs, Air Handlers
                {"name": "Ductwork", "base_cost_per_sqft": 3.5, "unit": "sqft"},         # Supply/Return/Branch
                {"name": "Controls & BMS", "base_cost_per_sqft": 1.5, "unit": "sqft"},   # Thermostats, Sensors
                {"name": "Hydronic Piping", "base_cost_per_sqft": 2.0, "unit": "sqft"},  # Chilled/Hot water
                {"name": "Ventilation/Exhaust", "base_cost_per_sqft": 1.0, "unit": "sqft"}, # Fans, Louvers
            ],
            "electrical": [
                {"name": "Main Distribution", "base_cost_per_sqft": 8.0, "unit": "sqft"},
                {"name": "Lighting", "base_cost_per_sqft": 5.0, "unit": "sqft"},
                {"name": "Power Outlets", "base_cost_per_sqft": 3.5, "unit": "sqft"},
            ],
            "plumbing": [
                {"name": "Water Distribution", "base_cost_per_sqft": 1.0, "unit": "sqft"},
                {"name": "Drainage", "base_cost_per_sqft": 1.0, "unit": "sqft"},
                {"name": "Fixtures", "base_cost_per_sqft": 1.0, "unit": "sqft"},
            ],
            "finishes": [
                {"name": "Flooring", "base_cost_per_sqft": 8.0, "unit": "sqft"},
                {"name": "Wall Finishes", "base_cost_per_sqft": 7.0, "unit": "sqft"},
                {"name": "Ceiling", "base_cost_per_sqft": 5.0, "unit": "sqft"},
            ],
        }
    
    def _initialize_cost_multipliers(self) -> Dict[str, Dict[str, float]]:
        return {
            "project_type": {
                ProjectType.RESIDENTIAL: 0.9,
                ProjectType.COMMERCIAL: 1.0,
                ProjectType.INDUSTRIAL: 0.5,  # Warehouses are much cheaper
                ProjectType.MIXED_USE: 1.0,   # Will be calculated based on mix
            },
            "climate_zone": {
                ClimateZone.HOT_HUMID: 1.1,
                ClimateZone.HOT_DRY: 1.05,
                ClimateZone.TEMPERATE: 1.0,
                ClimateZone.COLD: 1.15,
                ClimateZone.VERY_COLD: 1.25,
            },
            "floor_count": {
                1: 1.0,
                2: 1.05,
                3: 1.1,
                4: 1.15,
                5: 1.2,
            },
            "ceiling_height": {
                8: 0.95,
                9: 1.0,
                10: 1.05,
                11: 1.1,
                12: 1.15,
            }
        }
    
    def _initialize_regional_multipliers(self) -> Dict[str, float]:
        """Regional cost multipliers for different states/regions"""
        return {
            # West Coast
            "CA": 1.30,  # California premium (matches V2 engine)
            "WA": 1.15,  # Washington
            "OR": 1.10,  # Oregon
            
            # Southwest/South
            "TX": 0.90,  # Texas
            "AZ": 0.95,  # Arizona
            "NV": 1.05,  # Nevada
            "FL": 0.95,  # Florida
            
            # Mountain/Central
            "CO": 1.05,  # Colorado
            "UT": 1.00,  # Utah
            
            # Northeast
            "NY": 1.50,  # New York
            "MA": 1.40,  # Massachusetts
            "CT": 1.35,  # Connecticut
            
            # Midwest
            "IL": 1.10,  # Illinois
            "OH": 0.95,  # Ohio
            "MI": 1.00,  # Michigan
        }
    
    def _initialize_city_multipliers(self) -> Dict[str, float]:
        """City-specific cost multipliers (applied on top of regional)"""
        return {
            # California cities
            "san francisco": 1.45,
            "san jose": 1.40,
            "oakland": 1.35,
            "los angeles": 1.25,
            "san diego": 1.20,
            "sacramento": 1.15,
            "fresno": 1.05,
            
            # Other major cities
            "seattle": 1.20,
            "portland": 1.15,
            "austin": 0.95,
            "dallas": 0.90,
            "houston": 0.90,
            "miami": 1.05,
            "denver": 1.10,
            "new york": 1.60,
            "boston": 1.45,
            "chicago": 1.15,
        }
    
    def _get_location_multiplier(self, location: str) -> float:
        """Extract state and city from location string and return appropriate multiplier"""
        if not location:
            return 1.0
            
        location_lower = location.lower().strip()
        
        # Extract state code (e.g., "CA" from "San Francisco, CA")
        state_match = re.search(r',\s*([A-Z]{2})$', location)
        state_code = state_match.group(1) if state_match else None
        
        # Extract city name
        city_match = re.search(r'^([^,]+)', location)
        city = city_match.group(1).lower().strip() if city_match else None
        
        # Start with base multiplier
        multiplier = 1.0
        
        # Apply state multiplier
        if state_code and state_code in self.regional_multipliers:
            multiplier = self.regional_multipliers[state_code]
        # Handle full state names
        elif location_lower == 'california':
            multiplier = self.regional_multipliers.get('CA', 1.25)
        
        # Check for city-specific override
        if city and city in self.city_multipliers:
            multiplier = self.city_multipliers[city]
        
        return multiplier
    
    def _generate_deterministic_id(self, request: ScopeRequest) -> str:
        # Include timestamp to ensure unique IDs for each generation
        request_dict = request.model_dump()
        request_dict['timestamp'] = datetime.utcnow().isoformat()
        request_str = json.dumps(request_dict, sort_keys=True, default=str)
        hash_object = hashlib.md5(request_str.encode())
        return hash_object.hexdigest()[:8]
    
    def _initialize_space_type_rates(self) -> Dict[str, Dict[str, float]]:
        """Initialize cost rates per square foot by space type"""
        return {
            'warehouse': {
                'structural': 10.00,  # Slab on grade, simple steel frame
                'mechanical': 6.00,   # Basic RTUs, minimal ductwork
                'electrical': 6.50,   # Basic lighting, minimal power
                'plumbing': 1.50,     # Minimal fixtures
                'finishes': 8.00      # Exposed structure, sealed concrete
            },
            'office': {
                'structural': 18.00,  # More complex structure
                'mechanical': 16.00,  # VAV systems, complex ductwork
                'electrical': 20.00,  # Dense power, complex lighting
                'plumbing': 5.00,     # Full restrooms, break rooms
                'finishes': 60.00     # Full interior buildout
            },
            'retail': {
                'structural': 15.00,
                'mechanical': 12.00,
                'electrical': 18.00,
                'plumbing': 4.00,
                'finishes': 45.00
            },
            'light_industrial': {
                'structural': 12.00,
                'mechanical': 8.00,
                'electrical': 10.00,
                'plumbing': 2.00,
                'finishes': 12.00
            }
        }
    
    def _initialize_validation_ranges(self) -> Dict[str, Dict[str, float]]:
        """Initialize valid cost per SF ranges by building type"""
        return {
            'warehouse': {'min': 50, 'max': 80},
            'office': {'min': 120, 'max': 200},
            'mixed_use': {'min': 70, 'max': 130},
            'retail': {'min': 90, 'max': 150},
            'light_industrial': {'min': 60, 'max': 100}
        }
    
    def _initialize_building_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize building characteristics that drive cost calculations"""
        return {
            'warehouse': {
                'occupancy_per_1000sf': 1,  # Very low occupancy
                'bathroom_fixtures_per_1000sf': 0.1,  # Minimal bathrooms
                'kitchen_type': None,  # No kitchen
                'hvac_complexity': 'basic',  # Simple rooftop units
                'electrical_density': 'low',  # Basic lighting/power
                'plumbing_complexity': 'minimal',  # Just bathrooms
                'requires_grease_trap': False,
                'requires_medical_gas': False
            },
            'office': {
                'occupancy_per_1000sf': 5,  # Moderate occupancy  
                'bathroom_fixtures_per_1000sf': 0.5,  # More bathrooms
                'kitchen_type': 'break_room',  # Simple kitchen
                'hvac_complexity': 'standard',  # VAV systems
                'electrical_density': 'high',  # Lots of workstations
                'plumbing_complexity': 'standard',  # Bathrooms + break room
                'requires_grease_trap': False,
                'requires_medical_gas': False
            },
            'retail': {
                'occupancy_per_1000sf': 8,  # High customer traffic
                'bathroom_fixtures_per_1000sf': 0.3,
                'kitchen_type': None,
                'hvac_complexity': 'standard',
                'electrical_density': 'medium',
                'plumbing_complexity': 'basic',
                'requires_grease_trap': False,
                'requires_medical_gas': False
            },
            'restaurant': {
                'occupancy_per_1000sf': 10,  # Very high occupancy
                'bathroom_fixtures_per_1000sf': 0.8,
                'kitchen_type': 'commercial',  # Full commercial kitchen!
                'hvac_complexity': 'complex',  # Kitchen exhaust
                'electrical_density': 'very_high',  # Kitchen equipment
                'plumbing_complexity': 'complex',  # Grease traps, floor drains
                'requires_grease_trap': True,
                'requires_medical_gas': False
            },
            'medical': {
                'occupancy_per_1000sf': 6,
                'bathroom_fixtures_per_1000sf': 1.0,  # Lots of exam rooms
                'kitchen_type': 'break_room',
                'hvac_complexity': 'complex',  # Special ventilation
                'electrical_density': 'very_high',  # Medical equipment
                'plumbing_complexity': 'complex',  # Med gas, special drainage
                'requires_grease_trap': False,
                'requires_medical_gas': True
            }
        }
    
    def _initialize_benchmark_ranges(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Initialize benchmark ranges for validation"""
        return {
            'warehouse': {
                'total': (50, 80),
                'structural': (10, 15),
                'mechanical': (4, 8),
                'electrical': (5, 8),
                'plumbing': (1, 3),  # KEY: Very low for warehouse!
                'finishes': (5, 10),
                'general conditions': (4, 8)
            },
            'office': {
                'total': (120, 200),
                'structural': (15, 25),
                'mechanical': (12, 20),
                'electrical': (15, 25),
                'plumbing': (5, 10),
                'finishes': (40, 80),
                'general conditions': (10, 20)
            },
            'mixed_use': {
                'total': (70, 130),
                'structural': (12, 20),
                'mechanical': (8, 15),
                'electrical': (10, 20),
                'plumbing': (3, 12),  # Depends on mix
                'finishes': (20, 40),
                'general conditions': (6, 13)
            },
            'restaurant': {
                'total': (200, 400),
                'structural': (20, 35),
                'mechanical': (35, 60),  # Kitchen exhaust
                'electrical': (25, 40),  # Kitchen equipment
                'plumbing': (30, 60),   # Commercial kitchen plumbing!
                'finishes': (60, 120),
                'general conditions': (16, 40)
            }
        }
    
    def _calculate_multiplier(self, request: ScopeRequest) -> float:
        multiplier = 1.0
        
        # Apply location multiplier first (biggest impact)
        location_multiplier = self._get_location_multiplier(request.location)
        multiplier *= location_multiplier
        
        # For mixed use, calculate weighted average
        if request.project_type == ProjectType.MIXED_USE and request.building_mix:
            weighted_multiplier = 0
            for building_type, percentage in request.building_mix.items():
                type_enum = ProjectType(building_type) if building_type in ['residential', 'commercial', 'industrial'] else ProjectType.COMMERCIAL
                weighted_multiplier += self.cost_multipliers["project_type"].get(type_enum, 1.0) * percentage
            multiplier *= weighted_multiplier
        else:
            multiplier *= self.cost_multipliers["project_type"].get(request.project_type, 1.0)
        
        # Remove climate zone multiplier - it's now handled in location
        # if request.climate_zone:
        #     multiplier *= self.cost_multipliers["climate_zone"].get(request.climate_zone, 1.0)
        
        floor_multiplier = self.cost_multipliers["floor_count"].get(
            request.num_floors, 
            1.0 + (request.num_floors - 1) * 0.05
        )
        multiplier *= floor_multiplier
        
        height_multiplier = 1.0 + (request.ceiling_height - 9) * 0.05
        multiplier *= height_multiplier
        
        return round(multiplier, 3)
    
    def _calculate_mixed_use_requirements(self, request: ScopeRequest, system_type: str) -> Dict[str, float]:
        """Calculate weighted requirements for mixed-use buildings"""
        if not request.building_mix:
            return {}
        
        # Define requirements per building type
        hvac_tons_per_sqft = {
            "warehouse": 1/1500,   # Minimal HVAC - 1 ton per 1500 sqft
            "office": 1/400,       # Full HVAC - 1 ton per 400 sqft
            "retail": 1/350,       # Heavy HVAC - 1 ton per 350 sqft
            "residential": 1/500,  # Moderate HVAC - 1 ton per 500 sqft
            "industrial": 1/1500   # Same as warehouse
        }
        
        bathroom_per_sqft = {
            "warehouse": 1/10000,  # Minimal - 1 bathroom per 10000 sqft
            "office": 1/1000,      # Standard - 1 bathroom per 1000 sqft
            "retail": 1/2000,      # Moderate - 1 bathroom per 2000 sqft
            "residential": 1/800,  # High - 1 bathroom per 800 sqft
            "industrial": 1/10000  # Same as warehouse
        }
        
        electrical_watts_per_sqft = {
            "warehouse": 5,        # Minimal lighting/power
            "office": 15,          # Full electrical
            "retail": 20,          # Heavy electrical
            "residential": 12,     # Moderate electrical
            "industrial": 5        # Same as warehouse
        }
        
        if system_type == "hvac":
            weighted_tons = 0
            for building_type, percentage in request.building_mix.items():
                tons_per_sqft = hvac_tons_per_sqft.get(building_type, hvac_tons_per_sqft["office"])
                weighted_tons += tons_per_sqft * percentage
            return {"tons_per_sqft": weighted_tons}
        
        elif system_type == "plumbing":
            weighted_bathrooms = 0
            for building_type, percentage in request.building_mix.items():
                bath_per_sqft = bathroom_per_sqft.get(building_type, bathroom_per_sqft["office"])
                weighted_bathrooms += bath_per_sqft * percentage
            return {"bathrooms_per_sqft": weighted_bathrooms}
        
        elif system_type == "electrical":
            weighted_watts = 0
            for building_type, percentage in request.building_mix.items():
                watts = electrical_watts_per_sqft.get(building_type, electrical_watts_per_sqft["office"])
                weighted_watts += watts * percentage
            return {"watts_per_sqft": weighted_watts}
        
        return {}
    
    def _apply_climate_adjustments(self, systems: List[Dict], category: str, climate_zone: ClimateZone) -> List[Dict]:
        adjusted_systems = systems.copy()
        
        if category == "mechanical" and climate_zone in [ClimateZone.HOT_HUMID, ClimateZone.HOT_DRY]:
            for system in adjusted_systems:
                if system["name"] == "HVAC System":
                    system["base_cost_per_sqft"] *= 1.2
        
        elif category == "mechanical" and climate_zone in [ClimateZone.COLD, ClimateZone.VERY_COLD]:
            for system in adjusted_systems:
                if system["name"] == "HVAC System":
                    system["base_cost_per_sqft"] *= 1.3
            
            adjusted_systems.append({
                "name": "Insulation Enhancement",
                "base_cost_per_sqft": 5.0,
                "unit": "sqft"
            })
        
        return adjusted_systems
    
    def generate_scope(self, request: ScopeRequest) -> ScopeResponse:
        project_id = self._generate_deterministic_id(request)
        cost_multiplier = self._calculate_multiplier(request)
        
        categories = []
        
        for category_name, base_systems in self.base_systems.items():
            systems = base_systems.copy()
            
            if request.climate_zone:
                systems = self._apply_climate_adjustments(
                    systems, category_name, request.climate_zone
                )
            
            building_systems = []
            for system in systems:
                # Create a copy to avoid mutating the original
                system_copy = system.copy()
                quantity = request.square_footage
                
                # Adjust structural costs based on building height
                if category_name == "structural" and request.num_floors:
                    if request.num_floors == 1:
                        # Single story is simpler
                        height_factor = 0.8
                    elif request.num_floors <= 3:
                        height_factor = 1.0
                    else:
                        height_factor = 1.2 + (request.num_floors - 3) * 0.1
                    system_copy["base_cost_per_sqft"] *= height_factor
                    
                    # Add seismic requirements for California
                    if request.location and 'ca' in request.location.lower():
                        if system_copy["name"] == "Structural Frame":
                            system_copy["base_cost_per_sqft"] *= 1.15  # 15% for seismic design
                
                if system_copy["name"] == "Roofing" or system_copy["name"] == "Roof Structure":
                    quantity = request.square_footage / request.num_floors
                
                # Apply mixed-use adjustments using space type rates
                if request.project_type == ProjectType.MIXED_USE and request.building_mix:
                    # Calculate weighted average cost based on space mix
                    weighted_rate = 0
                    for space_type, percentage in request.building_mix.items():
                        if space_type in self.space_type_rates:
                            space_rates = self.space_type_rates[space_type]
                            if category_name in space_rates:
                                weighted_rate += space_rates[category_name] * percentage
                    
                    # If we calculated a weighted rate, use it
                    if weighted_rate > 0:
                        # Distribute the weighted rate across all systems in the category
                        num_systems = len([s for s in systems if s["base_cost_per_sqft"] > 0])
                        if num_systems > 0:
                            system_copy["base_cost_per_sqft"] = weighted_rate / num_systems
                    
                    elif category_name == "plumbing" and system_copy["name"] == "Fixtures":
                        mixed_reqs = self._calculate_mixed_use_requirements(request, "plumbing")
                        if "bathrooms_per_sqft" in mixed_reqs:
                            # Adjust plumbing fixtures based on bathroom requirements
                            # Base plumbing is designed for office (1/1000), so calculate adjustment factor
                            base_bathrooms_per_sqft = 1/1000  # Office baseline
                            adjustment_factor = mixed_reqs["bathrooms_per_sqft"] / base_bathrooms_per_sqft
                            system_copy["base_cost_per_sqft"] = system_copy["base_cost_per_sqft"] * adjustment_factor
                    
                    elif category_name == "electrical" and "Power" in system_copy["name"]:
                        mixed_reqs = self._calculate_mixed_use_requirements(request, "electrical")
                        if "watts_per_sqft" in mixed_reqs:
                            # Adjust electrical based on power requirements
                            # Base electrical is designed for office (15 watts/sqft)
                            base_watts_per_sqft = 15  # Office baseline
                            adjustment_factor = mixed_reqs["watts_per_sqft"] / base_watts_per_sqft
                            system_copy["base_cost_per_sqft"] = system_copy["base_cost_per_sqft"] * adjustment_factor
                
                unit_cost = round(system_copy["base_cost_per_sqft"] * cost_multiplier, 2)
                
                building_system = BuildingSystem(
                    name=system_copy["name"],
                    quantity=quantity,
                    unit=system_copy["unit"],
                    unit_cost=unit_cost,
                    total_cost=round(quantity * unit_cost, 2),
                    specifications={
                        "base_rate": system_copy["base_cost_per_sqft"],
                        "multiplier": cost_multiplier,
                        "climate_adjusted": request.climate_zone is not None
                    }
                )
                building_systems.append(building_system)
            
            # Use detailed service for MEP categories
            if category_name in ["electrical", "mechanical", "plumbing"]:
                # Log multiplier info for electrical debugging
                if category_name == "electrical":
                    logger.error(f"[MAIN ENGINE] Location: {request.location}")
                    logger.error(f"[MAIN ENGINE] Cost multiplier: {cost_multiplier}")
                    logger.error(f"[MAIN ENGINE] Location multiplier component: {self._get_location_multiplier(request.location)}")
                
                # Generate detailed items based on trade
                project_data = {
                    'square_footage': request.square_footage,
                    'num_floors': request.num_floors,
                    'project_type': request.project_type.value,
                    'building_mix': request.building_mix or {},
                    'special_requirements': getattr(request, 'special_requirements', ''),
                    'ceiling_height': getattr(request, 'ceiling_height', 10),
                    'location': request.location,  # Critical for V2 engine!
                    'quality_level': getattr(request, 'quality_level', 'standard')
                }
                
                if category_name == "electrical":
                    detailed_items = detailed_trade_service.generate_detailed_electrical(project_data)
                elif category_name == "mechanical":
                    detailed_items = detailed_trade_service.generate_detailed_hvac(project_data)
                elif category_name == "plumbing":
                    detailed_items = detailed_trade_service.generate_detailed_plumbing(project_data)
                
                # Group by category and convert to BuildingSystem objects
                category_groups = {}
                for item in detailed_items:
                    # Skip items with zero or negative quantity
                    if item.get('quantity', 0) <= 0:
                        logger.warning(f"Skipping item with zero/negative quantity: {item.get('name', 'Unknown')}")
                        continue
                        
                    cat_name = item.get('category', category_name.title())
                    if cat_name not in category_groups:
                        category_groups[cat_name] = []
                    
                    # For electrical items from V2 engine, don't apply multiplier
                    # V2 has already factored in the location
                    if category_name == "electrical":
                        adjusted_unit_cost = round(item['unit_cost'], 2)
                    else:
                        adjusted_unit_cost = round(item['unit_cost'] * cost_multiplier, 2)
                    
                    building_system = BuildingSystem(
                        name=item['name'],
                        quantity=item['quantity'],
                        unit=item['unit'],
                        unit_cost=adjusted_unit_cost,
                        total_cost=round(item['quantity'] * adjusted_unit_cost, 2),
                        specifications={
                            'category': cat_name,
                            'base_cost': item['unit_cost'],
                            'multiplier': cost_multiplier
                        }
                    )
                    category_groups[cat_name].append(building_system)
                
                # For electrical, create a single category with all systems
                if category_name == "electrical":
                    # Combine all electrical systems into one category
                    all_systems = []
                    for cat_name, systems in category_groups.items():
                        all_systems.extend(systems)
                    
                    category = ScopeCategory(
                        name="Electrical",
                        systems=all_systems
                    )
                    categories.append(category)
                else:
                    # Create categories for each subcategory
                    trade_prefix = category_name.title()
                    for cat_name, systems in category_groups.items():
                        category = ScopeCategory(
                            name=f"{trade_prefix} - {cat_name}" if cat_name != trade_prefix else cat_name,
                            systems=systems
                        )
                        categories.append(category)
            else:
                category = ScopeCategory(
                    name=category_name.title(),
                    systems=building_systems
                )
                categories.append(category)
        
        # Add General Conditions as a percentage of trade costs
        trade_subtotal = sum(
            sum(system.total_cost for system in category.systems)
            for category in categories
        )
        
        # General conditions percentage based on project size
        if trade_subtotal < 1000000:
            gc_percentage = 0.15  # 15% for small projects
        elif trade_subtotal < 5000000:
            gc_percentage = 0.10  # 10% for medium projects
        else:
            gc_percentage = 0.08  # 8% for large projects
        
        gc_total = trade_subtotal * gc_percentage
        
        # Create general conditions category
        gc_systems = [
            BuildingSystem(
                name="Project Management & Supervision",
                quantity=1,
                unit="LS",
                unit_cost=gc_total * 0.30,
                total_cost=gc_total * 0.30
            ),
            BuildingSystem(
                name="Temporary Facilities & Equipment",
                quantity=1,
                unit="LS",
                unit_cost=gc_total * 0.20,
                total_cost=gc_total * 0.20
            ),
            BuildingSystem(
                name="Insurance & Bonds",
                quantity=1,
                unit="LS",
                unit_cost=gc_total * 0.25,
                total_cost=gc_total * 0.25
            ),
            BuildingSystem(
                name="Permits & Fees",
                quantity=1,
                unit="LS",
                unit_cost=gc_total * 0.15,
                total_cost=gc_total * 0.15
            ),
            BuildingSystem(
                name="Project Closeout & Commissioning",
                quantity=1,
                unit="LS",
                unit_cost=gc_total * 0.10,
                total_cost=gc_total * 0.10
            )
        ]
        
        gc_category = ScopeCategory(
            name="General Conditions",
            systems=gc_systems
        )
        categories.append(gc_category)
        
        contingency = self._calculate_contingency_percentage(request)
        
        response = ScopeResponse(
            project_id=project_id,
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=contingency
        )
        
        # Validate the total cost is within expected ranges
        total_cost = response.total_cost
        cost_per_sf = total_cost / request.square_footage if request.square_footage > 0 else 0
        
        building_type = request.project_type.value
        if building_type in self.cost_validation_ranges:
            valid_range = self.cost_validation_ranges[building_type]
            if cost_per_sf < valid_range['min'] or cost_per_sf > valid_range['max']:
                logger.warning(
                    f"Cost validation warning: ${cost_per_sf:.2f}/SF is outside expected range "
                    f"${valid_range['min']}-${valid_range['max']}/SF for {building_type}"
                )
                logger.warning(f"Total cost: ${total_cost:,.0f} for {request.square_footage:,.0f} SF")
        
        return response
    
    def _calculate_contingency_percentage(self, request: ScopeRequest) -> float:
        # Standardized 10% contingency for construction documents phase
        # This ensures consistency across all views and calculations
        return 10.0


engine = DeterministicScopeEngine()