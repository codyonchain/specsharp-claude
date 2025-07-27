from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from app.core.cost_engine import (
    calculate_trade_cost, 
    add_building_specific_items,
    BUILDING_TYPE_SPECIFICATIONS,
    BUILDING_COMPLEXITY_FACTORS,
    REGIONAL_MULTIPLIERS,
    ScopeItem
)


class CostService:
    def __init__(self):
        self.cost_database = self._load_cost_database()
        self.regional_data = self._load_regional_data()
    
    def _load_cost_database(self) -> Dict:
        return {
            "materials": {
                "concrete": {
                    "unit": "cubic_yard",
                    "base_cost": 150,
                    "description": "Ready-mix concrete",
                    "categories": ["structural", "foundation"]
                },
                "steel_beam": {
                    "unit": "ton",
                    "base_cost": 800,
                    "description": "Structural steel beams",
                    "categories": ["structural"]
                },
                "lumber_2x4": {
                    "unit": "board_foot",
                    "base_cost": 0.75,
                    "description": "2x4 lumber",
                    "categories": ["structural", "framing"]
                },
                "drywall": {
                    "unit": "sheet",
                    "base_cost": 12,
                    "description": "1/2 inch drywall sheet",
                    "categories": ["finishes"]
                },
                "insulation_fiberglass": {
                    "unit": "sqft",
                    "base_cost": 1.5,
                    "description": "R-19 fiberglass insulation",
                    "categories": ["thermal", "mechanical"]
                },
                "hvac_unit": {
                    "unit": "ton",
                    "base_cost": 1500,
                    "description": "HVAC unit per ton capacity",
                    "categories": ["mechanical"]
                },
                "electrical_panel": {
                    "unit": "unit",
                    "base_cost": 1200,
                    "description": "200 amp electrical panel",
                    "categories": ["electrical"]
                },
                "plumbing_fixture": {
                    "unit": "unit",
                    "base_cost": 350,
                    "description": "Standard plumbing fixture",
                    "categories": ["plumbing"]
                }
            },
            "labor": {
                "general_contractor": {
                    "base_rate": 75,
                    "unit": "hour",
                    "markup": 1.15
                },
                "electrician": {
                    "base_rate": 85,
                    "unit": "hour",
                    "markup": 1.1
                },
                "plumber": {
                    "base_rate": 80,
                    "unit": "hour",
                    "markup": 1.1
                },
                "hvac_technician": {
                    "base_rate": 90,
                    "unit": "hour",
                    "markup": 1.1
                },
                "carpenter": {
                    "base_rate": 65,
                    "unit": "hour",
                    "markup": 1.05
                },
                "painter": {
                    "base_rate": 55,
                    "unit": "hour",
                    "markup": 1.05
                }
            },
            "equipment": {
                "crane": {
                    "daily_rate": 2500,
                    "unit": "day",
                    "minimum_days": 1
                },
                "excavator": {
                    "daily_rate": 800,
                    "unit": "day",
                    "minimum_days": 1
                },
                "concrete_pump": {
                    "daily_rate": 1500,
                    "unit": "day",
                    "minimum_days": 1
                }
            }
        }
    
    def _load_regional_data(self) -> Dict:
        return {
            "regions": {
                "northeast": {
                    "states": ["NY", "MA", "CT", "NH", "VT", "ME", "RI", "NJ", "PA"],
                    "cost_multiplier": 1.25,
                    "labor_multiplier": 1.3,
                    "material_multiplier": 1.2
                },
                "west_coast": {
                    "states": ["CA", "OR", "WA"],
                    "cost_multiplier": 1.2,
                    "labor_multiplier": 1.25,
                    "material_multiplier": 1.15
                },
                "midwest": {
                    "states": ["IL", "IN", "MI", "OH", "WI", "MN", "IA", "MO", "ND", "SD", "NE", "KS"],
                    "cost_multiplier": 1.0,
                    "labor_multiplier": 1.0,
                    "material_multiplier": 1.0
                },
                "south": {
                    "states": ["TX", "FL", "GA", "NC", "SC", "VA", "TN", "AL", "MS", "AR", "LA", "OK"],
                    "cost_multiplier": 0.9,
                    "labor_multiplier": 0.85,
                    "material_multiplier": 0.95
                },
                "mountain": {
                    "states": ["CO", "UT", "NV", "AZ", "NM", "ID", "MT", "WY"],
                    "cost_multiplier": 0.95,
                    "labor_multiplier": 0.9,
                    "material_multiplier": 1.05
                }
            },
            "cities": {
                "New York, NY": {"multiplier": 1.35},
                "San Francisco, CA": {"multiplier": 1.3},
                "Los Angeles, CA": {"multiplier": 1.2},
                "Chicago, IL": {"multiplier": 1.15},
                "Seattle, WA": {"multiplier": 1.2},
                "Boston, MA": {"multiplier": 1.25},
                "Denver, CO": {"multiplier": 1.1},
                "Austin, TX": {"multiplier": 1.05},
                "Phoenix, AZ": {"multiplier": 0.95},
                "Houston, TX": {"multiplier": 0.95}
            }
        }
    
    def get_regional_multiplier(self, location: str) -> Tuple[float, Dict[str, float]]:
        city_data = self.regional_data["cities"].get(location)
        if city_data:
            base_multiplier = city_data["multiplier"]
            return base_multiplier, {
                "overall": base_multiplier,
                "labor": base_multiplier * 1.1,
                "material": base_multiplier * 0.95
            }
        
        state_code = location.split(", ")[-1] if ", " in location else None
        if state_code:
            for region, data in self.regional_data["regions"].items():
                if state_code in data["states"]:
                    return data["cost_multiplier"], {
                        "overall": data["cost_multiplier"],
                        "labor": data["labor_multiplier"],
                        "material": data["material_multiplier"]
                    }
        
        return 1.0, {"overall": 1.0, "labor": 1.0, "material": 1.0}
    
    def calculate_material_cost(
        self, 
        material: str, 
        quantity: float, 
        location: str
    ) -> Dict[str, float]:
        if material not in self.cost_database["materials"]:
            raise ValueError(f"Material '{material}' not found in database")
        
        material_data = self.cost_database["materials"][material]
        base_cost = material_data["base_cost"]
        
        _, multipliers = self.get_regional_multiplier(location)
        material_multiplier = multipliers["material"]
        
        unit_cost = base_cost * material_multiplier
        total_cost = unit_cost * quantity
        
        return {
            "material": material,
            "quantity": quantity,
            "unit": material_data["unit"],
            "base_unit_cost": base_cost,
            "adjusted_unit_cost": round(unit_cost, 2),
            "total_cost": round(total_cost, 2),
            "location_multiplier": material_multiplier
        }
    
    def calculate_labor_cost(
        self,
        trade: str,
        hours: float,
        location: str,
        include_markup: bool = True
    ) -> Dict[str, float]:
        if trade not in self.cost_database["labor"]:
            raise ValueError(f"Trade '{trade}' not found in database")
        
        labor_data = self.cost_database["labor"][trade]
        base_rate = labor_data["base_rate"]
        
        _, multipliers = self.get_regional_multiplier(location)
        labor_multiplier = multipliers["labor"]
        
        hourly_rate = base_rate * labor_multiplier
        if include_markup:
            hourly_rate *= labor_data["markup"]
        
        total_cost = hourly_rate * hours
        
        return {
            "trade": trade,
            "hours": hours,
            "base_rate": base_rate,
            "adjusted_rate": round(hourly_rate, 2),
            "total_cost": round(total_cost, 2),
            "location_multiplier": labor_multiplier,
            "markup_applied": include_markup
        }
    
    def estimate_system_cost(
        self,
        system_type: str,
        square_footage: float,
        location: str
    ) -> Dict[str, any]:
        system_estimates = {
            "hvac": {
                "tons_required": square_footage / 400,
                "material": "hvac_unit",
                "labor_hours_per_ton": 16,
                "trade": "hvac_technician"
            },
            "electrical": {
                "panels_required": max(1, square_footage / 5000),
                "material": "electrical_panel",
                "labor_hours_per_1000_sqft": 40,
                "trade": "electrician"
            },
            "plumbing": {
                "fixtures_per_1000_sqft": 2,
                "material": "plumbing_fixture",
                "labor_hours_per_fixture": 8,
                "trade": "plumber"
            }
        }
        
        if system_type not in system_estimates:
            raise ValueError(f"System type '{system_type}' not supported")
        
        estimate = system_estimates[system_type]
        
        if system_type == "hvac":
            quantity = estimate["tons_required"]
            labor_hours = quantity * estimate["labor_hours_per_ton"]
        elif system_type == "electrical":
            quantity = estimate["panels_required"]
            labor_hours = (square_footage / 1000) * estimate["labor_hours_per_1000_sqft"]
        else:
            quantity = (square_footage / 1000) * estimate["fixtures_per_1000_sqft"]
            labor_hours = quantity * estimate["labor_hours_per_fixture"]
        
        material_cost = self.calculate_material_cost(
            estimate["material"], quantity, location
        )
        labor_cost = self.calculate_labor_cost(
            estimate["trade"], labor_hours, location
        )
        
        return {
            "system": system_type,
            "square_footage": square_footage,
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "total_cost": round(
                material_cost["total_cost"] + labor_cost["total_cost"], 2
            )
        }
    
    def calculate_trade_cost_v2(
        self,
        trade: str,
        building_type: str,
        square_footage: float,
        location: str
    ) -> Tuple[float, List[Dict[str, any]]]:
        """
        Calculate trade cost using the new cost engine with proper hierarchy:
        1. Base material cost from specifications
        2. Building type complexity adjustment
        3. Regional multiplier
        
        Returns: (total_cost, list_of_scope_items)
        """
        # Extract region from location
        region = self._extract_region_from_location(location)
        
        # Use the new cost engine
        total_cost, scope_items = calculate_trade_cost(
            trade=trade,
            building_type=building_type,
            square_footage=square_footage,
            region=region
        )
        
        # Convert ScopeItem objects to dictionaries for JSON serialization
        scope_items_dict = []
        for item in scope_items:
            scope_items_dict.append({
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'unit_cost': item.unit_cost,
                'total_cost': item.total_cost,
                'note': item.note,
                'category': item.category
            })
        
        return total_cost, scope_items_dict
    
    def add_building_specific_items_v2(
        self,
        building_type: str,
        square_footage: float,
        existing_items: List[Dict[str, any]] = None
    ) -> List[Dict[str, any]]:
        """
        Add building-type specific scope items using the new cost engine
        """
        # Convert existing items to ScopeItem objects
        scope_items = []
        if existing_items:
            for item in existing_items:
                scope_items.append(ScopeItem(
                    name=item.get('name', ''),
                    quantity=item.get('quantity', 0),
                    unit=item.get('unit', ''),
                    unit_cost=item.get('unit_cost', 0),
                    total_cost=item.get('total_cost', 0),
                    note=item.get('note', ''),
                    category=item.get('category', '')
                ))
        
        # Add building-specific items
        updated_items = add_building_specific_items(
            building_type=building_type,
            scope_items=scope_items,
            square_footage=square_footage
        )
        
        # Convert back to dictionaries
        result = []
        for item in updated_items:
            result.append({
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'unit_cost': item.unit_cost,
                'total_cost': item.total_cost,
                'note': item.note,
                'category': item.category
            })
        
        return result
    
    def _extract_region_from_location(self, location: str) -> str:
        """Extract state/region code from location string"""
        if not location:
            return "TX"  # Default
        
        # Common state codes
        state_codes = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
                      "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                      "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                      "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                      "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
        
        location_upper = location.upper()
        
        # Check if any state code appears in the location
        for code in state_codes:
            if code in location_upper:
                return code
        
        # Check for city names and map to states
        city_to_state = {
            "SAN FRANCISCO": "CA",
            "LOS ANGELES": "CA",
            "SAN DIEGO": "CA",
            "SACRAMENTO": "CA",
            "SEATTLE": "WA",
            "PORTLAND": "OR",
            "AUSTIN": "TX",
            "DALLAS": "TX",
            "HOUSTON": "TX",
            "MIAMI": "FL",
            "DENVER": "CO",
            "NEW YORK": "NY",
            "BOSTON": "MA",
            "CHICAGO": "IL",
            "ATLANTA": "GA",
            "PHOENIX": "AZ",
            "LAS VEGAS": "NV",
            "PHILADELPHIA": "PA"
        }
        
        for city, state in city_to_state.items():
            if city in location_upper:
                return state
        
        return "TX"  # Default to Texas
    
    def get_available_building_types(self) -> List[str]:
        """Get list of available building types from the cost engine"""
        return list(BUILDING_TYPE_SPECIFICATIONS.keys())
    
    def get_building_complexity_factors(self, building_type: str) -> Dict[str, float]:
        """Get complexity factors for a specific building type"""
        return BUILDING_COMPLEXITY_FACTORS.get(building_type, BUILDING_COMPLEXITY_FACTORS["commercial"])
    
    def get_regional_multipliers(self, region: str) -> Dict[str, float]:
        """Get regional multipliers for a specific region"""
        return REGIONAL_MULTIPLIERS.get(region, {"structural": 1.0, "mechanical": 1.0, "electrical": 1.0, "plumbing": 1.0, "finishes": 1.0})


cost_service = CostService()