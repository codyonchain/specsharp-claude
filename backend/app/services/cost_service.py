from typing import Dict, List, Optional, Tuple, Any
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
from app.services.healthcare_cost_service import healthcare_cost_service
from app.services.healthcare_classifier import HealthcareFacilityClassifier


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
        
        location_upper = location.upper()
        
        # State abbreviations to full names mapping
        state_mapping = {
            'AL': 'AL', 'ALABAMA': 'AL',
            'AK': 'AK', 'ALASKA': 'AK',
            'AZ': 'AZ', 'ARIZONA': 'AZ',
            'AR': 'AR', 'ARKANSAS': 'AR',
            'CA': 'CA', 'CALIFORNIA': 'CA',
            'CO': 'CO', 'COLORADO': 'CO',
            'CT': 'CT', 'CONNECTICUT': 'CT',
            'DE': 'DE', 'DELAWARE': 'DE',
            'FL': 'FL', 'FLORIDA': 'FL',
            'GA': 'GA', 'GEORGIA': 'GA',
            'HI': 'HI', 'HAWAII': 'HI',
            'ID': 'ID', 'IDAHO': 'ID',
            'IL': 'IL', 'ILLINOIS': 'IL',
            'IN': 'IN', 'INDIANA': 'IN',
            'IA': 'IA', 'IOWA': 'IA',
            'KS': 'KS', 'KANSAS': 'KS',
            'KY': 'KY', 'KENTUCKY': 'KY',
            'LA': 'LA', 'LOUISIANA': 'LA',
            'ME': 'ME', 'MAINE': 'ME',
            'MD': 'MD', 'MARYLAND': 'MD',
            'MA': 'MA', 'MASSACHUSETTS': 'MA',
            'MI': 'MI', 'MICHIGAN': 'MI',
            'MN': 'MN', 'MINNESOTA': 'MN',
            'MS': 'MS', 'MISSISSIPPI': 'MS',
            'MO': 'MO', 'MISSOURI': 'MO',
            'MT': 'MT', 'MONTANA': 'MT',
            'NE': 'NE', 'NEBRASKA': 'NE',
            'NV': 'NV', 'NEVADA': 'NV',
            'NH': 'NH', 'NEW HAMPSHIRE': 'NH',
            'NJ': 'NJ', 'NEW JERSEY': 'NJ',
            'NM': 'NM', 'NEW MEXICO': 'NM',
            'NY': 'NY', 'NEW YORK': 'NY',
            'NC': 'NC', 'NORTH CAROLINA': 'NC',
            'ND': 'ND', 'NORTH DAKOTA': 'ND',
            'OH': 'OH', 'OHIO': 'OH',
            'OK': 'OK', 'OKLAHOMA': 'OK',
            'OR': 'OR', 'OREGON': 'OR',
            'PA': 'PA', 'PENNSYLVANIA': 'PA',
            'RI': 'RI', 'RHODE ISLAND': 'RI',
            'SC': 'SC', 'SOUTH CAROLINA': 'SC',
            'SD': 'SD', 'SOUTH DAKOTA': 'SD',
            'TN': 'TN', 'TENNESSEE': 'TN',
            'TX': 'TX', 'TEXAS': 'TX',
            'UT': 'UT', 'UTAH': 'UT',
            'VT': 'VT', 'VERMONT': 'VT',
            'VA': 'VA', 'VIRGINIA': 'VA',
            'WA': 'WA', 'WASHINGTON': 'WA',
            'WV': 'WV', 'WEST VIRGINIA': 'WV',
            'WI': 'WI', 'WISCONSIN': 'WI',
            'WY': 'WY', 'WYOMING': 'WY'
        }
        
        # First, try to extract state from "City, State" format
        if ', ' in location:
            parts = location.split(', ')
            if len(parts) >= 2:
                state_part = parts[-1].strip().upper()
                if state_part in state_mapping:
                    return state_mapping[state_part]
        
        # Check for exact state name matches (word boundaries)
        location_words = location_upper.replace(',', ' ').split()
        for word in location_words:
            if word in state_mapping:
                return state_mapping[word]
        
        # Check for multi-word state names
        for state_name, state_code in state_mapping.items():
            if len(state_name.split()) > 1:  # Multi-word states
                if state_name in location_upper:
                    return state_code
        
        # City-specific mappings for our primary markets
        city_to_state = {
            "MANCHESTER": "NH",  # New Hampshire (primary market)
            "NASHUA": "NH",
            "CONCORD": "NH", 
            "PORTSMOUTH": "NH",
            "SALEM": "NH",
            "NASHVILLE": "TN",  # Tennessee (primary market)
            "FRANKLIN": "TN",   # Franklin, TN (Nashville suburb)
            "MURFREESBORO": "TN",
            "KNOXVILLE": "TN",
            "MEMPHIS": "TN",
            # Other major cities
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
            "BOSTON": "MA",
            "CHICAGO": "IL",
            "ATLANTA": "GA",
            "PHOENIX": "AZ",
            "LAS VEGAS": "NV",
            "PHILADELPHIA": "PA"
        }
        
        # Check for city matches
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
    
    def is_healthcare_facility(self, description: str, building_type: str = None) -> bool:
        """
        Check if the project is a healthcare facility
        """
        if not description:
            return False
        
        description_lower = description.lower()
        
        # Check for healthcare keywords
        healthcare_keywords = [
            'hospital', 'medical', 'healthcare', 'health care', 'clinic',
            'surgical', 'surgery', 'urgent care', 'emergency', 'patient',
            'nursing', 'rehabilitation', 'rehab', 'dental', 'imaging',
            'radiology', 'mri', 'ct scan', 'laboratory', 'pharmacy',
            'ambulatory', 'outpatient', 'inpatient', 'icu', 'nicu'
        ]
        
        for keyword in healthcare_keywords:
            if keyword in description_lower:
                return True
        
        # Check building type if provided
        if building_type and 'medical' in building_type.lower():
            return True
        
        return False
    
    def calculate_with_healthcare(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate costs with healthcare-specific breakdown if applicable
        
        Returns a dual-view structure for healthcare facilities
        """
        description = project_data.get('description', '')
        building_type = project_data.get('building_type', '')
        square_feet = project_data.get('square_footage', 0)
        location = project_data.get('location', '')
        
        # Standard calculation (always performed)
        standard_result = {
            'trades': {},
            'subtotal': 0,
            'contingency': 0,
            'total': 0,
            'cost_per_sf': 0
        }
        
        # Calculate standard trade costs
        trades = ['structural', 'mechanical', 'electrical', 'plumbing', 'finishes']
        total_cost = 0
        
        for trade in trades:
            trade_cost, _ = self.calculate_trade_cost_v2(
                trade=trade,
                building_type=building_type or 'commercial',
                square_footage=square_feet,
                location=location
            )
            standard_result['trades'][trade] = trade_cost
            total_cost += trade_cost
        
        standard_result['subtotal'] = total_cost
        standard_result['contingency'] = total_cost * 0.10
        standard_result['total'] = total_cost * 1.10
        standard_result['cost_per_sf'] = standard_result['total'] / square_feet if square_feet > 0 else 0
        
        # Check if this is a healthcare facility
        if self.is_healthcare_facility(description, building_type):
            # Get healthcare-specific costs
            healthcare_result = healthcare_cost_service.calculate_healthcare_costs_v2(
                description=description,
                square_feet=int(square_feet),
                location=location
            )
            
            return {
                'standard_view': standard_result,
                'healthcare_view': healthcare_result,
                'display_mode': 'dual',
                'building_classification': healthcare_result.get('facility_type'),
                'is_healthcare': True
            }
        
        return {
            'standard_view': standard_result,
            'display_mode': 'single',
            'is_healthcare': False
        }


cost_service = CostService()