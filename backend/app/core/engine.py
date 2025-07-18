from typing import List, Dict, Any, Tuple, Optional
import hashlib
import json
from app.models.scope import (
    ScopeRequest, ScopeResponse, ScopeCategory,
    BuildingSystem, ProjectType, ClimateZone
)
from datetime import datetime
import uuid
import re


class DeterministicScopeEngine:
    def __init__(self):
        self.base_systems = self._initialize_base_systems()
        self.cost_multipliers = self._initialize_cost_multipliers()
        self.regional_multipliers = self._initialize_regional_multipliers()
        self.city_multipliers = self._initialize_city_multipliers()
    
    def _initialize_base_systems(self) -> Dict[str, List[Dict[str, Any]]]:
        # National average base costs per square foot
        return {
            "structural": [
                {"name": "Foundation", "base_cost_per_sqft": 12.0, "unit": "sqft"},  # National avg
                {"name": "Framing", "base_cost_per_sqft": 18.0, "unit": "sqft"},     # National avg
                {"name": "Roofing", "base_cost_per_sqft": 8.0, "unit": "sqft"},      # Reduced
            ],
            "mechanical": [
                {"name": "HVAC System", "base_cost_per_sqft": 15.0, "unit": "sqft"}, # National avg
                {"name": "Ductwork", "base_cost_per_sqft": 0.0, "unit": "sqft"},     # Included in HVAC
                {"name": "Controls", "base_cost_per_sqft": 0.0, "unit": "sqft"},     # Included in HVAC
            ],
            "electrical": [
                {"name": "Main Distribution", "base_cost_per_sqft": 5.0, "unit": "sqft"},
                {"name": "Lighting", "base_cost_per_sqft": 3.0, "unit": "sqft"},
                {"name": "Power Outlets", "base_cost_per_sqft": 2.0, "unit": "sqft"},
            ],
            "plumbing": [
                {"name": "Water Distribution", "base_cost_per_sqft": 2.0, "unit": "sqft"},
                {"name": "Drainage", "base_cost_per_sqft": 2.0, "unit": "sqft"},
                {"name": "Fixtures", "base_cost_per_sqft": 2.0, "unit": "sqft"},
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
            "CA": 1.25,  # California average
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
        
        # Check for city-specific override
        if city and city in self.city_multipliers:
            multiplier = self.city_multipliers[city]
        
        return multiplier
    
    def _generate_deterministic_id(self, request: ScopeRequest) -> str:
        # Include timestamp to ensure unique IDs for each generation
        request_dict = request.model_dump()
        request_dict['timestamp'] = datetime.utcnow().isoformat()
        request_str = json.dumps(request_dict, sort_keys=True)
        hash_object = hashlib.md5(request_str.encode())
        return hash_object.hexdigest()[:8]
    
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
                if system_copy["name"] == "Roofing":
                    quantity = request.square_footage / request.num_floors
                
                # Apply mixed-use adjustments
                if request.project_type == ProjectType.MIXED_USE and request.building_mix:
                    if category_name == "mechanical" and system_copy["name"] == "HVAC System":
                        mixed_reqs = self._calculate_mixed_use_requirements(request, "hvac")
                        if "tons_per_sqft" in mixed_reqs:
                            # Adjust HVAC cost based on weighted tonnage requirements
                            # Base HVAC is designed for office (1/400), so calculate adjustment factor
                            base_tons_per_sqft = 1/400  # Office baseline
                            adjustment_factor = mixed_reqs["tons_per_sqft"] / base_tons_per_sqft
                            system_copy["base_cost_per_sqft"] = system_copy["base_cost_per_sqft"] * adjustment_factor
                    
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
            
            category = ScopeCategory(
                name=category_name.title(),
                systems=building_systems
            )
            categories.append(category)
        
        response = ScopeResponse(
            project_id=project_id,
            project_name=request.project_name,
            created_at=datetime.utcnow(),
            request_data=request,
            categories=categories,
            contingency_percentage=self._calculate_contingency_percentage(request)
        )
        
        return response
    
    def _calculate_contingency_percentage(self, request: ScopeRequest) -> float:
        base_contingency = 10.0
        
        if request.project_type == ProjectType.INDUSTRIAL:
            base_contingency = 8.0  # Warehouses are simpler, less contingency needed
        elif request.project_type == ProjectType.MIXED_USE:
            # Calculate weighted contingency based on mix
            if request.building_mix:
                weighted_contingency = 0
                contingency_map = {
                    "warehouse": 8.0,
                    "industrial": 8.0,
                    "office": 10.0,
                    "retail": 12.0,
                    "residential": 12.0
                }
                for building_type, percentage in request.building_mix.items():
                    weighted_contingency += contingency_map.get(building_type, 10.0) * percentage
                base_contingency = weighted_contingency
            else:
                base_contingency = 10.0
        elif request.project_type == ProjectType.COMMERCIAL:
            base_contingency = 10.0
        elif request.project_type == ProjectType.RESIDENTIAL:
            base_contingency = 12.0
        
        if request.num_floors > 5:
            base_contingency += 2.0
        
        if request.special_requirements and "LEED" in request.special_requirements:
            base_contingency += 3.0
        
        return min(base_contingency, 20.0)


engine = DeterministicScopeEngine()