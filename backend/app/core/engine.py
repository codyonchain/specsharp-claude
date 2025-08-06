from typing import List, Dict, Any, Tuple, Optional
import hashlib
import json
import logging
from functools import lru_cache
from app.models.scope import (
    ScopeRequest, ScopeResponse, ScopeCategory,
    BuildingSystem, ProjectType, ClimateZone, ProjectClassification
)
from datetime import datetime
import uuid
import re
from app.services.detailed_trade_service import detailed_trade_service
from app.services.building_type_service import building_type_service
from app.services.restaurant_scope_service import restaurant_scope_service
from app.services.regional_requirements_service import regional_requirements_service
from app.core.cost_engine import (
    calculate_trade_cost,
    add_building_specific_items,
    add_building_specific_mechanical_items,
    BUILDING_TYPE_SPECIFICATIONS,
    BUILDING_COMPLEXITY_FACTORS,
    ScopeItem
)
from app.core.building_type_detector import determine_building_type

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
            "project_classification": {
                "ground_up": 1.0,     # Base cost for new construction
                "addition": 1.15,     # 15% premium for tie-ins, protection, limited access
                "renovation": 1.35,   # 35% premium for demo, unknowns, phased work
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
            "TN": 1.10,  # Tennessee (Nashville market - adjusted for restaurants)
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
            "NH": 1.05,  # New Hampshire
            "VT": 1.10,  # Vermont
            "ME": 1.00,  # Maine
            
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
    
    @lru_cache(maxsize=256)
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
            },
            'restaurant': {
                'structural': 20.00,  # Heavy equipment loads, grease trap requirements
                'mechanical': 35.00,  # Commercial kitchen exhaust, makeup air, heavy HVAC
                'electrical': 25.00,  # High power for kitchen equipment
                'plumbing': 30.00,   # Extensive kitchen plumbing, grease management
                'finishes': 80.00    # Kitchen equipment, dining finishes
            }
        }
    
    def _initialize_validation_ranges(self) -> Dict[str, Dict[str, float]]:
        """Initialize valid cost per SF ranges by building type"""
        return {
            'warehouse': {'min': 50, 'max': 80},
            'office': {'min': 120, 'max': 200},
            'mixed_use': {'min': 70, 'max': 130},
            'retail': {'min': 90, 'max': 150},
            'light_industrial': {'min': 60, 'max': 100},
            'restaurant': {'min': 200, 'max': 400}
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
            # Map building types to their appropriate project type multipliers
            building_to_project_type = {
                'warehouse': ProjectType.INDUSTRIAL,  # Use industrial multiplier (0.5) for warehouses
                'office': ProjectType.COMMERCIAL,     # Use commercial multiplier (1.0) for offices
                'retail': ProjectType.COMMERCIAL,
                'restaurant': ProjectType.COMMERCIAL,
                'residential': ProjectType.RESIDENTIAL,
                'multi_family_residential': ProjectType.RESIDENTIAL,
                'industrial': ProjectType.INDUSTRIAL,
                'light_industrial': ProjectType.INDUSTRIAL
            }
            for building_type, percentage in request.building_mix.items():
                type_enum = building_to_project_type.get(building_type, ProjectType.COMMERCIAL)
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
        
        # More reasonable ceiling height adjustment - cap at 20% increase
        height_adjustment = min((request.ceiling_height - 9) * 0.02, 0.20)  # 2% per foot, max 20%
        height_multiplier = 1.0 + height_adjustment
        multiplier *= height_multiplier
        
        # Apply finish level multiplier
        finish_level = getattr(request, 'finish_level', 'standard')
        finish_multipliers = {
            'basic': 0.85,     # -15% for basic finishes
            'standard': 1.0,   # baseline
            'premium': 1.25    # +25% for premium finishes
        }
        finish_multiplier = finish_multipliers.get(finish_level, 1.0)
        multiplier *= finish_multiplier
        
        # Apply project classification multiplier (ground-up, addition, renovation)
        project_classification = getattr(request, 'project_classification', 'ground_up')
        classification_multiplier = self.cost_multipliers["project_classification"].get(
            project_classification.value if hasattr(project_classification, 'value') else project_classification, 
            1.0
        )
        multiplier *= classification_multiplier
        
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
            "industrial": 1/1500,  # Same as warehouse
            "restaurant": 1/250    # Very heavy HVAC for kitchen exhaust/makeup air
        }
        
        bathroom_per_sqft = {
            "warehouse": 1/10000,  # Minimal - 1 bathroom per 10000 sqft
            "office": 1/1000,      # Standard - 1 bathroom per 1000 sqft
            "retail": 1/2000,      # Moderate - 1 bathroom per 2000 sqft
            "residential": 1/800,  # High - 1 bathroom per 800 sqft
            "industrial": 1/10000, # Same as warehouse
            "restaurant": 1/1000   # High fixture count for customers + staff
        }
        
        electrical_watts_per_sqft = {
            "warehouse": 5,        # Minimal lighting/power
            "office": 15,          # Full electrical
            "retail": 20,          # Heavy electrical
            "residential": 12,     # Moderate electrical
            "industrial": 5,       # Same as warehouse
            "restaurant": 30       # Very high for kitchen equipment
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
    
    def _apply_building_type_adjustments(self, request: ScopeRequest, category_name: str, base_cost_per_sqft: float, num_systems: int = 1) -> float:
        """Apply building type specific adjustments including service levels and features"""
        # Check if this is a restaurant
        if (request.occupancy_type == "restaurant" or 
            (request.building_mix and "restaurant" in request.building_mix and request.building_mix["restaurant"] >= 0.5)):
            
            # Get state code from location
            state = "NH"  # Default
            if request.location:
                # Extract state code from location string
                location_upper = request.location.upper()
                state_codes = ["NH", "MA", "NY", "CA", "TX", "FL", "IL", "WA", "OR", "CO"]
                for code in state_codes:
                    if code in location_upper:
                        state = code
                        break
            
            # Get service level (default to full_service if not specified)
            service_level = getattr(request, 'service_level', 'full_service')
            
            # Get base cost for this restaurant type
            restaurant_base_cost = building_type_service.get_base_cost('restaurant', state, service_level)
            
            logger.info(f"[BUILDING TYPE] Restaurant detected - State: {state}, Service: {service_level}, Base Cost: ${restaurant_base_cost}/sf")
            
            if restaurant_base_cost > 0:
                # Get trade allocations for this service level
                trade_allocations = building_type_service.get_trade_allocations('restaurant', service_level)
                
                # Map our category names to trade allocation keys
                category_mapping = {
                    'structural': 'structural',
                    'mechanical': 'mechanical', 
                    'electrical': 'electrical',
                    'plumbing': 'plumbing',
                    'finishes': 'finishes',
                    'general_conditions': 'general_conditions'
                }
                
                if category_name in category_mapping:
                    trade_key = category_mapping[category_name]
                    if trade_key in trade_allocations:
                        # Calculate the cost for this trade based on total building cost
                        trade_percentage = trade_allocations[trade_key]
                        trade_cost_per_sqft = restaurant_base_cost * trade_percentage
                        
                        # Add feature costs proportionally
                        if hasattr(request, 'building_features') and request.building_features:
                            feature_cost = building_type_service.calculate_feature_costs(
                                'restaurant', 
                                request.building_features, 
                                1.0  # Per square foot
                            )
                            # Distribute feature costs proportionally across trades
                            trade_cost_per_sqft += feature_cost * trade_percentage
                        
                        # Divide by number of systems in this category to avoid multiplication
                        trade_cost_per_sqft = trade_cost_per_sqft / num_systems
                        
                        logger.info(f"[BUILDING TYPE] Category: {category_name}, Trade %: {trade_percentage*100:.1f}%, Systems: {num_systems}, Cost/SF: ${trade_cost_per_sqft:.2f}")
                        return trade_cost_per_sqft
        
        # Return original cost if not a restaurant
        return base_cost_per_sqft
    
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
        
        # Check if we should use V2 engine for specific building types
        # Skip V2 for mixed-use buildings - they need the weighted calculation logic
        if hasattr(request, 'occupancy_type') and request.occupancy_type and request.project_type != ProjectType.MIXED_USE:
            occupancy_lower = request.occupancy_type.lower()
            logger.info(f"[SCOPE ENGINE] Occupancy type detected: {occupancy_lower}")
            
            # Use V2 engine for educational, healthcare, warehouse, industrial, hospitality, retail, and multi-family residential buildings
            if occupancy_lower in ['educational', 'healthcare', 'warehouse', 'industrial', 'multi_family_residential', 'hospitality', 'retail']:
                logger.info(f"[SCOPE ENGINE] Using V2 engine for {occupancy_lower} building")
                return self.generate_scope_v2(request)
        
        # Check if this is a restaurant project to use specialized pricing
        is_restaurant = (request.occupancy_type == "restaurant" or 
                        (request.building_mix and "restaurant" in request.building_mix and 
                         request.building_mix["restaurant"] >= 0.5))
        
        if is_restaurant:
            logger.info(f"[RESTAURANT] Processing restaurant project with service level: {getattr(request, 'service_level', 'full_service')}")
            
            # Use specialized restaurant scope service
            return self._generate_restaurant_scope(request, project_id, cost_multiplier)
        
        categories = []
        
        for category_name, base_systems in self.base_systems.items():
            systems = base_systems.copy()
            
            if request.climate_zone:
                systems = self._apply_climate_adjustments(
                    systems, category_name, request.climate_zone
                )
            
            building_systems = []
            # DEBUG: Log systems for finishes
            if category_name == "finishes":
                logger.debug(f"[FINISHES DEBUG] Processing {len(systems)} systems for finishes")
                logger.debug(f"[FINISHES DEBUG] Project type: {request.project_type}, Building mix: {request.building_mix}")
            
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
                
                # Apply restaurant or mixed-use adjustments using space type rates
                if is_restaurant and request.project_type != ProjectType.MIXED_USE:
                    # For pure restaurant projects, skip the hardcoded space rates
                    # The building type service will provide the correct rates
                    pass
                elif request.project_type == ProjectType.MIXED_USE and request.building_mix:
                    # Calculate weighted average cost based on space mix
                    weighted_rate = 0
                    logger.info(f"[MIXED-USE] Processing {category_name} for building mix: {request.building_mix}")
                    
                    for space_type, percentage in request.building_mix.items():
                        if space_type in self.space_type_rates:
                            space_rates = self.space_type_rates[space_type]
                            if category_name in space_rates:
                                rate = space_rates[category_name]
                                weighted_rate += rate * percentage
                                logger.info(f"[MIXED-USE] {space_type} ({percentage*100}%): ${rate}/SF * {percentage} = ${rate * percentage}/SF")
                            else:
                                logger.warning(f"[MIXED-USE] Category '{category_name}' not found in space rates for '{space_type}'")
                        else:
                            logger.warning(f"[MIXED-USE] Space type '{space_type}' not found in space_type_rates")
                    
                    # If we calculated a weighted rate, use it
                    if weighted_rate > 0:
                        logger.info(f"[MIXED-USE] Total weighted rate for {category_name}: ${weighted_rate:.2f}/SF")
                        
                        # Distribute the weighted rate across all systems in the category
                        num_systems = len([s for s in systems if s["base_cost_per_sqft"] > 0])
                        if num_systems > 0:
                            system_copy["base_cost_per_sqft"] = weighted_rate / num_systems
                            logger.info(f"[MIXED-USE] {system_copy['name']}: ${system_copy['base_cost_per_sqft']:.2f}/SF (${weighted_rate:.2f} / {num_systems} systems)")
                    else:
                        logger.warning(f"[MIXED-USE] No weighted rate calculated for {category_name}")
                
                elif category_name == "plumbing" and system_copy["name"] == "Fixtures" and request.project_type == ProjectType.MIXED_USE and request.building_mix:
                        mixed_reqs = self._calculate_mixed_use_requirements(request, "plumbing")
                        if "bathrooms_per_sqft" in mixed_reqs:
                            # Adjust plumbing fixtures based on bathroom requirements
                            # Base plumbing is designed for office (1/1000), so calculate adjustment factor
                            base_bathrooms_per_sqft = 1/1000  # Office baseline
                            adjustment_factor = mixed_reqs["bathrooms_per_sqft"] / base_bathrooms_per_sqft
                            system_copy["base_cost_per_sqft"] = system_copy["base_cost_per_sqft"] * adjustment_factor
                    
                elif category_name == "electrical" and "Power" in system_copy["name"] and request.project_type == ProjectType.MIXED_USE and request.building_mix:
                        mixed_reqs = self._calculate_mixed_use_requirements(request, "electrical")
                        if "watts_per_sqft" in mixed_reqs:
                            # Adjust electrical based on power requirements
                            # Base electrical is designed for office (15 watts/sqft)
                            base_watts_per_sqft = 15  # Office baseline
                            adjustment_factor = mixed_reqs["watts_per_sqft"] / base_watts_per_sqft
                            system_copy["base_cost_per_sqft"] = system_copy["base_cost_per_sqft"] * adjustment_factor
                
                # Apply building type adjustments (service levels, features)
                if is_restaurant:
                    # For restaurants, completely replace the cost with building type service cost
                    # Pass 0 as base to avoid double-counting
                    num_systems_in_category = len([s for s in systems if s.get("base_cost_per_sqft", 0) > 0])
                    # Before adjustment
                    adjusted_cost_per_sqft = self._apply_building_type_adjustments(
                        request, category_name, 0, num_systems_in_category
                    )
                    # After adjustment
                else:
                    # For other building types, adjust the base cost
                    adjusted_cost_per_sqft = self._apply_building_type_adjustments(
                        request, category_name, system_copy["base_cost_per_sqft"]
                    )
                
                # Apply category-specific finish level adjustments
                category_cost_multiplier = cost_multiplier
                if category_name == "finishes":
                    # Finishes category can have up to +35% for premium
                    finish_level = getattr(request, 'finish_level', 'standard')
                    if finish_level == 'premium':
                        # Remove the standard premium multiplier (1.25) and apply the higher one (1.35)
                        # cost_multiplier already includes 1.25, so we adjust by 1.35/1.25 = 1.08
                        category_cost_multiplier = cost_multiplier * 1.08
                
                unit_cost = round(adjusted_cost_per_sqft * category_cost_multiplier, 2)
                
                # DEBUG: Log finishes calculation
                if category_name == "finishes":
                    logger.debug(f"[FINISHES DEBUG] System: {system_copy['name']}")
                    logger.debug(f"[FINISHES DEBUG]   Base cost/SF: ${system_copy.get('base_cost_per_sqft', 0):.2f}")
                    logger.debug(f"[FINISHES DEBUG]   Adjusted cost/SF: ${adjusted_cost_per_sqft:.2f}")
                    logger.debug(f"[FINISHES DEBUG]   Multiplier: {category_cost_multiplier:.2f}")
                    logger.debug(f"[FINISHES DEBUG]   Final unit cost: ${unit_cost:.2f}")
                    logger.debug(f"[FINISHES DEBUG]   Quantity: {quantity}")
                    logger.debug(f"[FINISHES DEBUG]   Total: ${quantity * unit_cost:.2f}")
                
                # Adjust confidence score based on finish level
                confidence_score = 95  # Default high confidence
                confidence_label = "High"
                finish_level = getattr(request, 'finish_level', 'standard')
                
                if finish_level == 'premium' and category_name == "finishes":
                    # Premium finishes have more variability
                    confidence_score = 85
                    confidence_label = "Medium"
                elif finish_level == 'basic':
                    # Basic finishes are more predictable
                    confidence_score = 98
                    confidence_label = "Very High"
                
                building_system = BuildingSystem(
                    name=system_copy["name"],
                    quantity=quantity,
                    unit=system_copy["unit"],
                    unit_cost=unit_cost,
                    total_cost=round(quantity * unit_cost, 2),
                    confidence_score=confidence_score,
                    confidence_label=confidence_label,
                    specifications={
                        "base_rate": system_copy["base_cost_per_sqft"],
                        "multiplier": cost_multiplier,
                        "climate_adjusted": request.climate_zone is not None,
                        "finish_level": finish_level
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
                    'quality_level': getattr(request, 'quality_level', 'standard'),
                    'occupancy_type': getattr(request, 'occupancy_type', ''),
                    'service_level': getattr(request, 'service_level', 'full_service'),
                    'request_data': {  # Some services look for request_data
                        'occupancy_type': getattr(request, 'occupancy_type', ''),
                        'special_requirements': getattr(request, 'special_requirements', '')
                    }
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
                        
                    # Use building type service to properly categorize restaurant items
                    if is_restaurant:
                        proper_category = building_type_service.categorize_line_item(
                            item.get('name', ''), 
                            'restaurant'
                        )
                        # Map to proper category name
                        if proper_category == 'mechanical':
                            cat_name = 'Mechanical'
                        elif proper_category == 'electrical':
                            cat_name = 'Electrical'
                        elif proper_category == 'plumbing':
                            cat_name = 'Plumbing'
                        elif proper_category == 'finishes':
                            cat_name = 'Finishes'
                        elif proper_category == 'structural':
                            cat_name = 'Structural'
                        else:
                            cat_name = item.get('category', category_name.title())
                        
                        # Debug logging for restaurant categorization
                        item_name_lower = item.get('name', '').lower()
                        if any(keyword in item_name_lower for keyword in ['exhaust', 'hood', 'make-up', 'walk-in', 'kitchen', 'grease']):
                            logger.info(f"Restaurant item categorization: {item.get('name')} -> {proper_category} -> {cat_name}")
                    else:
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
                    # For restaurants, consolidate all mechanical/plumbing into main categories
                    if is_restaurant and category_name in ["mechanical", "plumbing"]:
                        # Combine all subcategories into the main trade category
                        all_systems = []
                        for cat_name, systems in category_groups.items():
                            all_systems.extend(systems)
                        
                        category = ScopeCategory(
                            name=category_name.title(),
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
                # DEBUG: Log finishes category
                if category_name == "finishes":
                    logger.debug(f"[FINISHES DEBUG] Created category with {len(building_systems)} systems")
                    for sys in building_systems:
                        logger.debug(f"[FINISHES DEBUG]   {sys.name}: ${sys.total_cost:.2f}")
                    total = sum(sys.total_cost for sys in building_systems)
                    logger.debug(f"[FINISHES DEBUG] Total finishes: ${total:.2f}")
                categories.append(category)
        
        # Add Regional Requirements (NH and TN specific)
        regional_items = regional_requirements_service.get_regional_requirements(
            location=request.location,
            square_footage=request.square_footage,
            building_type=getattr(request, 'occupancy_type', request.project_type.value),
            num_floors=request.num_floors
        )
        
        if regional_items:
            # Group regional items by category
            regional_by_category = {}
            for item in regional_items:
                if item.category not in regional_by_category:
                    regional_by_category[item.category] = []
                regional_by_category[item.category].append(item)
            
            # Create categories for regional requirements
            for category_name, items in regional_by_category.items():
                # Check if we need to add to existing category or create new
                existing_category = None
                for cat in categories:
                    if cat.name == category_name:
                        existing_category = cat
                        break
                
                if existing_category:
                    # Add to existing category
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        existing_category.systems.append(building_system)
                else:
                    # Create new category
                    building_systems = []
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        building_systems.append(building_system)
                    
                    category = ScopeCategory(
                        name=category_name,
                        systems=building_systems
                    )
                    categories.append(category)
        
        # Add General Conditions as a percentage of trade costs
        trade_subtotal = sum(
            sum(system.total_cost for system in category.systems)
            for category in categories
        )
        
        # General conditions percentage based on project size
        gc_percentage = 0.10  # Default
        
        # Check if this is a restaurant to use specific GC percentage
        if (request.occupancy_type == "restaurant" or 
            (request.building_mix and "restaurant" in request.building_mix and request.building_mix["restaurant"] >= 0.5)):
            service_level = getattr(request, 'service_level', 'full_service')
            trade_allocations = building_type_service.get_trade_allocations('restaurant', service_level)
            if 'general_conditions' in trade_allocations:
                # For restaurants, GC is already included in the base pricing
                # So we need to calculate it based on the expected total
                state = "NH"  # Default
                if request.location:
                    location_upper = request.location.upper()
                    state_codes = ["NH", "MA", "NY", "CA", "TX", "FL", "IL", "WA", "OR", "CO"]
                    for code in state_codes:
                        if code in location_upper:
                            state = code
                            break
                
                restaurant_base_cost = building_type_service.get_base_cost('restaurant', state, service_level)
                if restaurant_base_cost > 0:
                    # Add feature costs
                    if hasattr(request, 'building_features') and request.building_features:
                        feature_cost = building_type_service.calculate_feature_costs(
                            'restaurant', request.building_features, 1.0
                        )
                        restaurant_base_cost += feature_cost
                    
                    expected_total = restaurant_base_cost * request.square_footage
                    gc_percentage = trade_allocations['general_conditions']
                    gc_total = expected_total * gc_percentage
        else:
            # Non-restaurant: use size-based percentage
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
        
        # Add project classification specific items (demolition, tie-ins, etc.)
        classification_items = self._generate_classification_specific_items(request, trade_subtotal)
        if classification_items:
            categories.append(classification_items)
        
        contingency = self._calculate_contingency_percentage(request)
        
        response = ScopeResponse(
            project_id=project_id,
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=contingency
        )
        
        # Log trade allocations for restaurants
        if is_restaurant:
            logger.info("[RESTAURANT TRADE ALLOCATION SUMMARY]")
            service_level = getattr(request, 'service_level', 'full_service')
            logger.info(f"Service Level: {service_level}")
            
            # Calculate actual trade percentages
            trade_totals = {}
            subtotal = 0
            for category in categories:
                cat_total = sum(system.total_cost for system in category.systems)
                trade_totals[category.name] = cat_total
                subtotal += cat_total
            
            logger.info(f"Trade Totals:")
            for trade, total in trade_totals.items():
                percentage = (total / subtotal * 100) if subtotal > 0 else 0
                logger.info(f"  {trade}: ${total:,.0f} ({percentage:.1f}%)")
            
            # Log expected allocations
            expected_allocations = building_type_service.get_trade_allocations('restaurant', service_level)
            logger.info("Expected Allocations:")
            for trade, percentage in expected_allocations.items():
                logger.info(f"  {trade}: {percentage*100:.1f}%")
            
            # Log key restaurant items and their categorization
            logger.info("Key Restaurant Items:")
            for category in categories:
                for system in category.systems:
                    if any(keyword in system.name.lower() for keyword in ['exhaust', 'hood', 'walk-in', 'grease', 'kitchen']):
                        logger.info(f"  {system.name} -> {category.name} (${system.total_cost:,.0f})")
        
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
    
    def _generate_restaurant_scope(self, request: ScopeRequest, project_id: str, cost_multiplier: float) -> ScopeResponse:
        """Generate restaurant-specific scope using the restaurant scope service"""
        
        # Extract state from location
        state = "NH"  # Default
        if request.location:
            location_upper = request.location.upper()
            state_codes = ["NH", "MA", "NY", "CA", "TX", "FL", "IL", "WA", "OR", "CO"]
            for code in state_codes:
                if code in location_upper:
                    state = code
                    break
        
        # Prepare project data for restaurant scope service
        project_data = {
            'square_footage': request.square_footage,
            'state': state,
            'service_level': getattr(request, 'service_level', 'full_service')
        }
        
        # Generate restaurant-specific scope
        trade_scopes = restaurant_scope_service.generate_restaurant_scope(project_data)
        
        # Convert to ScopeCategory objects
        categories = []
        for trade_name, items in trade_scopes.items():
            # Convert items to BuildingSystem objects
            building_systems = []
            for item in items:
                building_system = BuildingSystem(
                    name=item['name'],
                    quantity=item['quantity'],
                    unit=item['unit'],
                    unit_cost=round(item['unit_cost'] * cost_multiplier, 2),
                    total_cost=round(item['total_cost'] * cost_multiplier, 2),
                    specifications={
                        'category': item.get('category', trade_name),
                        'base_cost': item['unit_cost'],
                        'multiplier': cost_multiplier,
                        'description': item.get('description', '')
                    }
                )
                building_systems.append(building_system)
            
            # Create category with proper name
            category_names = {
                'structural': 'Structural',
                'mechanical': 'Mechanical',
                'electrical': 'Electrical',
                'plumbing': 'Plumbing',
                'finishes': 'Finishes',
                'general_conditions': 'General Conditions'
            }
            
            category = ScopeCategory(
                name=category_names.get(trade_name, trade_name.title()),
                systems=building_systems
            )
            categories.append(category)
        
        # Add Regional Requirements (NH and TN specific) for restaurants
        regional_items = regional_requirements_service.get_regional_requirements(
            location=request.location,
            square_footage=request.square_footage,
            building_type="restaurant",
            num_floors=request.num_floors
        )
        
        if regional_items:
            # Group regional items by category
            regional_by_category = {}
            for item in regional_items:
                if item.category not in regional_by_category:
                    regional_by_category[item.category] = []
                regional_by_category[item.category].append(item)
            
            # Create categories for regional requirements
            for category_name, items in regional_by_category.items():
                # Check if we need to add to existing category or create new
                existing_category = None
                for cat in categories:
                    if cat.name == category_name:
                        existing_category = cat
                        break
                
                if existing_category:
                    # Add to existing category
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=round(item.unit_cost * cost_multiplier, 2),
                            total_cost=round(item.total_cost * cost_multiplier, 2),
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        existing_category.systems.append(building_system)
                else:
                    # Create new category
                    building_systems = []
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=round(item.unit_cost * cost_multiplier, 2),
                            total_cost=round(item.total_cost * cost_multiplier, 2),
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        building_systems.append(building_system)
                    
                    category = ScopeCategory(
                        name=category_name,
                        systems=building_systems
                    )
                    categories.append(category)
        
        # Create response
        contingency = self._calculate_contingency_percentage(request)
        
        response = ScopeResponse(
            project_id=project_id,
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=contingency
        )
        
        # Log trade allocations
        logger.info("[RESTAURANT TRADE ALLOCATION SUMMARY]")
        service_level = getattr(request, 'service_level', 'full_service')
        logger.info(f"Service Level: {service_level}")
        
        # Calculate actual trade percentages
        trade_totals = {}
        subtotal = 0
        for category in categories:
            cat_total = sum(system.total_cost for system in category.systems)
            trade_totals[category.name] = cat_total
            subtotal += cat_total
        
        logger.info(f"Trade Totals:")
        for trade, total in trade_totals.items():
            percentage = (total / subtotal * 100) if subtotal > 0 else 0
            logger.info(f"  {trade}: ${total:,.0f} ({percentage:.1f}%)")
        
        # Log expected allocations
        expected_allocations = restaurant_scope_service.trade_allocations.get(service_level, {})
        logger.info("Expected Allocations:")
        for trade, percentage in expected_allocations.items():
            logger.info(f"  {trade}: {percentage*100:.1f}%")
        
        # Log key restaurant items
        logger.info("Key Restaurant Items:")
        for category in categories:
            for system in category.systems:
                if any(keyword in system.name.lower() for keyword in ['exhaust', 'hood', 'walk-in', 'grease', 'kitchen', 'equipment package']):
                    logger.info(f"  {system.name} -> {category.name} (${system.total_cost:,.0f})")
        
        # Validate the total cost
        total_cost = response.total_cost
        cost_per_sf = total_cost / request.square_footage if request.square_footage > 0 else 0
        
        logger.info(f"Restaurant Total Cost: ${total_cost:,.0f} (${cost_per_sf:.2f}/SF)")
        
        # Check if cost is within restaurant range
        if 300 <= cost_per_sf <= 600:
            logger.info(f"Cost validation passed: ${cost_per_sf:.2f}/SF is within restaurant range $300-$600/SF")
        else:
            logger.warning(f"Cost validation warning: ${cost_per_sf:.2f}/SF is outside restaurant range $300-$600/SF")
        
        return response
    
    def _generate_classification_specific_items(self, request: ScopeRequest, trade_subtotal: float) -> Optional[ScopeCategory]:
        """Generate project classification specific items (demolition, tie-ins, etc.)"""
        classification = getattr(request, 'project_classification', 'ground_up')
        
        if classification == 'renovation':
            # Add demolition and renovation specific items
            demo_cost = trade_subtotal * 0.04  # 4% for demolition
            protection_cost = trade_subtotal * 0.02  # 2% for protection
            hazmat_cost = trade_subtotal * 0.025  # 2.5% for hazmat allowance
            phasing_cost = trade_subtotal * 0.015  # 1.5% for phasing premium
            
            systems = [
                BuildingSystem(
                    name="Selective Demolition",
                    quantity=1,
                    unit="LS",
                    unit_cost=demo_cost,
                    total_cost=demo_cost,
                    specifications={"description": "Remove existing finishes, MEP systems as required"}
                ),
                BuildingSystem(
                    name="Dust Protection & Barriers",
                    quantity=1,
                    unit="LS",
                    unit_cost=protection_cost,
                    total_cost=protection_cost,
                    specifications={"description": "Temporary walls, plastic barriers, air scrubbers"}
                ),
                BuildingSystem(
                    name="Hazardous Material Allowance",
                    quantity=1,
                    unit="LS",
                    unit_cost=hazmat_cost,
                    total_cost=hazmat_cost,
                    specifications={"description": "Asbestos, lead paint abatement allowance"}
                ),
                BuildingSystem(
                    name="Phased Construction Premium",
                    quantity=1,
                    unit="LS",
                    unit_cost=phasing_cost,
                    total_cost=phasing_cost,
                    specifications={"description": "Additional labor for occupied space work"}
                )
            ]
            
            return ScopeCategory(
                name="Renovation Specific Costs",
                systems=systems
            )
            
        elif classification == 'addition':
            # Add addition specific items
            tie_in_cost = trade_subtotal * 0.025  # 2.5% for structural tie-ins
            weather_cost = trade_subtotal * 0.01  # 1% for weather protection
            protection_cost = trade_subtotal * 0.015  # 1.5% for existing building protection
            access_cost = trade_subtotal * 0.01  # 1% for limited access premium
            
            systems = [
                BuildingSystem(
                    name="Structural Tie-Ins",
                    quantity=1,
                    unit="LS",
                    unit_cost=tie_in_cost,
                    total_cost=tie_in_cost,
                    specifications={"description": "Connect new structure to existing, reinforcement"}
                ),
                BuildingSystem(
                    name="Weather Protection at Connections",
                    quantity=1,
                    unit="LS", 
                    unit_cost=weather_cost,
                    total_cost=weather_cost,
                    specifications={"description": "Temporary roofing, wall protection during construction"}
                ),
                BuildingSystem(
                    name="Existing Building Protection",
                    quantity=1,
                    unit="LS",
                    unit_cost=protection_cost,
                    total_cost=protection_cost,
                    specifications={"description": "Protection of adjacent spaces, finishes"}
                ),
                BuildingSystem(
                    name="Limited Access Premium",
                    quantity=1,
                    unit="LS",
                    unit_cost=access_cost,
                    total_cost=access_cost,
                    specifications={"description": "Additional equipment, labor for constrained site"}
                )
            ]
            
            return ScopeCategory(
                name="Addition Specific Costs",
                systems=systems
            )
        
        # Ground-up construction doesn't need special items
        return None
    
    def _calculate_contingency_percentage(self, request: ScopeRequest) -> float:
        # Standardized 10% contingency for construction documents phase
        # This ensures consistency across all views and calculations
        return 10.0
    
    def generate_scope_v2(self, request: ScopeRequest) -> ScopeResponse:
        """Generate scope using the new cost engine with proper hierarchy"""
        project_id = self._generate_deterministic_id(request)
        
        # Determine building type
        building_type = self._determine_building_type(request)
        
        # Get location for regional adjustment
        location = request.location or "TX"
        region = self._extract_region_from_location(location)
        
        categories = []
        all_scope_items = []
        
        # Define trade categories to generate
        trades = ["structural", "mechanical", "electrical", "plumbing", "finishes"]
        
        for trade in trades:
            # Calculate trade cost using new engine
            trade_cost, scope_items = calculate_trade_cost(
                trade=trade,
                building_type=building_type,
                square_footage=request.square_footage,
                region=region,
                floors=request.num_floors or 1,
                location=location
            )
            
            # Add detailed mechanical items for specific building types
            if trade == "mechanical":
                # Get original description if available
                original_description = getattr(request, 'special_requirements', '') or ''
                scope_items = add_building_specific_mechanical_items(
                    scope_items=scope_items,
                    building_type=building_type,
                    square_footage=request.square_footage,
                    floors=request.num_floors or 1,
                    description=original_description
                )
            
            # Convert ScopeItem objects to BuildingSystem objects
            building_systems = []
            for item in scope_items:
                building_system = BuildingSystem(
                    name=item.name,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_cost=item.unit_cost,
                    total_cost=item.total_cost,
                    specifications={
                        'note': item.note,
                        'category': item.category
                    },
                    confidence_score=item.confidence_score,
                    confidence_label=item.confidence_label,
                    confidence_factors=item.confidence_factors
                )
                building_systems.append(building_system)
                all_scope_items.append(item)
            
            # Create category
            category = ScopeCategory(
                name=trade.title(),
                systems=building_systems
            )
            categories.append(category)
        
        # Add building-specific items
        additional_items = add_building_specific_items(
            building_type=building_type,
            scope_items=all_scope_items,
            square_footage=request.square_footage,
            floors=request.num_floors or 1
        )
        
        logger.info(f"[COST ENGINE V2] Adding {len(additional_items)} building-specific items for {building_type}")
        
        # Add additional items to appropriate categories
        for item in additional_items:
            # Check if this item already exists by name
            item_exists = any(existing.name == item.name for existing in all_scope_items)
            if not item_exists:
                # Find or create category
                category_found = False
                for category in categories:
                    if category.name.lower() == item.category.lower():
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            specifications={'note': item.note}
                        )
                        category.systems.append(building_system)
                        category_found = True
                        break
                
                if not category_found:
                    # Create new category if needed
                    category = ScopeCategory(
                        name=item.category,
                        systems=[BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            specifications={'note': item.note}
                        )]
                    )
                    categories.append(category)
        
        # Add Regional Requirements (NH and TN specific) for V2 engine
        regional_items = regional_requirements_service.get_regional_requirements(
            location=request.location,
            square_footage=request.square_footage,
            building_type=building_type,
            num_floors=request.num_floors
        )
        
        if regional_items:
            # Group regional items by category
            regional_by_category = {}
            for item in regional_items:
                if item.category not in regional_by_category:
                    regional_by_category[item.category] = []
                regional_by_category[item.category].append(item)
            
            # Create categories for regional requirements
            for category_name, items in regional_by_category.items():
                # Check if we need to add to existing category or create new
                existing_category = None
                for cat in categories:
                    if cat.name == category_name:
                        existing_category = cat
                        break
                
                if existing_category:
                    # Add to existing category
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        existing_category.systems.append(building_system)
                else:
                    # Create new category
                    building_systems = []
                    for item in items:
                        building_system = BuildingSystem(
                            name=item.name,
                            quantity=item.quantity,
                            unit=item.unit,
                            unit_cost=item.unit_cost,
                            total_cost=item.total_cost,
                            confidence_score=95,
                            confidence_label="High",
                            specifications={'note': item.note}
                        )
                        building_systems.append(building_system)
                    
                    category = ScopeCategory(
                        name=category_name,
                        systems=building_systems
                    )
                    categories.append(category)
        
        # Add General Conditions
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
        
        # Create response
        contingency = self._calculate_contingency_percentage(request)
        
        response = ScopeResponse(
            project_id=project_id,
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=contingency
        )
        
        # Log summary
        total_cost = response.total_cost
        cost_per_sf = total_cost / request.square_footage if request.square_footage > 0 else 0
        
        logger.info(f"[COST ENGINE V2] Building Type: {building_type}")
        logger.info(f"[COST ENGINE V2] Region: {region}")
        logger.info(f"[COST ENGINE V2] Total Cost: ${total_cost:,.0f} (${cost_per_sf:.2f}/SF)")
        
        return response
    
    def _determine_building_type(self, request: ScopeRequest) -> str:
        """Determine building type from request"""
        # Check occupancy type first
        if hasattr(request, 'occupancy_type') and request.occupancy_type:
            occupancy_mapping = {
                'warehouse': 'warehouse',
                'office': 'office',
                'retail': 'commercial',
                'restaurant': 'restaurant',
                'medical': 'healthcare',
                'healthcare': 'healthcare',  # Support both 'medical' and 'healthcare'
                'educational': 'educational',
                'industrial': 'industrial',
                'multi_family_residential': 'multi_family_residential',
                'hospitality': 'hospitality',
                'retail': 'retail'
            }
            if request.occupancy_type.lower() in occupancy_mapping:
                return occupancy_mapping[request.occupancy_type.lower()]
        
        # Check project type
        if request.project_type == ProjectType.INDUSTRIAL:
            return 'warehouse'
        elif request.project_type == ProjectType.COMMERCIAL:
            return 'commercial'
        elif request.project_type == ProjectType.RESIDENTIAL:
            return 'office'  # Use office as proxy for residential
        elif request.project_type == ProjectType.MIXED_USE and request.building_mix:
            # For mixed use, use the dominant type
            max_percentage = 0
            dominant_type = 'commercial'
            for building_type, percentage in request.building_mix.items():
                if percentage > max_percentage:
                    max_percentage = percentage
                    dominant_type = building_type
            
            # Map to our building types
            type_mapping = {
                'warehouse': 'warehouse',
                'office': 'office',
                'retail': 'commercial',
                'restaurant': 'restaurant',
                'industrial': 'warehouse'
            }
            return type_mapping.get(dominant_type, 'commercial')
        
        return 'commercial'  # Default
    
    @lru_cache(maxsize=128)
    def _extract_region_from_location(self, location: str) -> str:
        """Extract state/region code from location string"""
        if not location:
            return "TX"  # Default
        
        location_upper = location.upper()
        
        # Check for state codes
        import re
        state_match = re.search(r'\b([A-Z]{2})\b', location_upper)
        if state_match:
            state_code = state_match.group(1)
            # Verify it's a valid state code
            valid_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
                          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
            if state_code in valid_states:
                return state_code
        
        # Check for city names
        city_to_state = {
            "SAN FRANCISCO": "CA", "LOS ANGELES": "CA", "SAN DIEGO": "CA",
            "SEATTLE": "WA", "PORTLAND": "OR", "AUSTIN": "TX",
            "DALLAS": "TX", "HOUSTON": "TX", "MIAMI": "FL",
            "DENVER": "CO", "NEW YORK": "NY", "BOSTON": "MA",
            "CHICAGO": "IL", "ATLANTA": "GA", "PHOENIX": "AZ"
        }
        
        for city, state in city_to_state.items():
            if city in location_upper:
                return state
        
        return "TX"  # Default


engine = DeterministicScopeEngine()