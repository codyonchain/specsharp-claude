"""
Regional Requirements Service

Implements specific building code requirements for NH and TN markets.
These requirements are critical for 90%+ accuracy in our target markets.
"""

from typing import Dict, List, Optional
from app.models.scope import ClimateZone
from app.core.cost_engine import ScopeItem
import re


class RegionalRequirementsService:
    def __init__(self):
        self.nh_requirements = self._initialize_nh_requirements()
        self.tn_requirements = self._initialize_tn_requirements()
    
    def _initialize_nh_requirements(self) -> Dict:
        """New Hampshire specific building requirements"""
        return {
            "structural": [
                {
                    "name": "Snow Load Structural Reinforcement",
                    "description": "Enhanced structural capacity for 50-100 PSF ground snow loads",
                    "cost_per_sqft": 3.5,
                    "note": "IBC 2015 + NH amendments snow load requirements"
                },
                {
                    "name": "Deep Frost Protection Foundation",
                    "description": "Foundation depth 4-5 ft below grade for frost protection",
                    "cost_per_sqft": 2.8,
                    "note": "NH frost line depth requirements"
                },
                {
                    "name": "Snow Guards and Ice Barriers",
                    "description": "Metal roof snow retention systems",
                    "cost_per_sqft": 1.2,
                    "note": "Required for metal roofs in snow regions"
                },
                {
                    "name": "Reinforced Roof Structure",
                    "description": "Additional roof framing for snow load capacity",
                    "cost_per_sqft": 2.0,
                    "note": "Enhanced roof structure for snow accumulation"
                }
            ],
            "mechanical": [
                {
                    "name": "High-Efficiency HVAC System",
                    "description": "IECC 2018 compliant high-efficiency equipment",
                    "cost_per_sqft": 2.5,
                    "note": "NH energy code IECC 2018 requirements"
                },
                {
                    "name": "Enhanced Building Envelope",
                    "description": "R-21 walls, R-49 roof insulation per IECC 2018",
                    "cost_per_sqft": 3.0,
                    "note": "NH strict energy efficiency requirements"
                },
                {
                    "name": "Freeze Protection Systems",
                    "description": "Pipe insulation and heat tracing for freeze protection",
                    "cost_per_sqft": 1.5,
                    "note": "Required for extreme cold climate"
                }
            ],
            "site": [
                {
                    "name": "Septic System Design & Installation",
                    "description": "State-approved septic system (if no municipal sewer)",
                    "cost_per_sqft": 2.0,
                    "note": "Common requirement outside NH cities"
                },
                {
                    "name": "Insulated Slab Edge Protection",
                    "description": "Perimeter insulation for slab-on-grade foundations",
                    "cost_per_sqft": 0.8,
                    "note": "Required for frost protection"
                }
            ]
        }
    
    def _initialize_tn_requirements(self) -> Dict:
        """Tennessee/Nashville specific building requirements"""
        return {
            "structural": [
                {
                    "name": "Seismic Bracing System",
                    "description": "Seismic Design Category B/C compliance",
                    "cost_per_sqft": 2.5,
                    "note": "IBC 2018 seismic requirements for TN"
                },
                {
                    "name": "Seismic Equipment Anchorage",
                    "description": "Equipment and MEP seismic restraints",
                    "cost_per_sqft": 1.2,
                    "note": "Required seismic anchorage for equipment"
                }
            ],
            "site": [
                {
                    "name": "Storm Water Management System",
                    "description": "Retention/detention pond and drainage infrastructure",
                    "cost_per_sqft": 3.0,
                    "note": "Nashville strict storm water requirements"
                },
                {
                    "name": "Erosion Control Measures",
                    "description": "Silt fence, inlet protection, and stabilization",
                    "cost_per_sqft": 0.5,
                    "note": "Required site erosion control"
                }
            ],
            "mechanical": [
                {
                    "name": "Fire Sprinkler System",
                    "description": "Wet-pipe automatic sprinkler system",
                    "cost_per_sqft": 3.5,
                    "note": "Required for many TN occupancies"
                }
            ],
            "special": [
                {
                    "name": "Tornado Safe Room",
                    "description": "FEMA 361 compliant storm shelter",
                    "cost_lump_sum": 75000,
                    "note": "Recommended for certain building types",
                    "optional": True
                }
            ]
        }
    
    def get_state_from_location(self, location: str) -> Optional[str]:
        """Extract state code from location string"""
        if not location:
            return None
        
        # Check for state abbreviation
        state_match = re.search(r',\s*([A-Z]{2})', location)
        if state_match:
            return state_match.group(1)
        
        # Check for full state names
        location_lower = location.lower()
        if "new hampshire" in location_lower:
            return "NH"
        elif "tennessee" in location_lower:
            return "TN"
        
        return None
    
    def get_regional_requirements(self, location: str, square_footage: float, 
                                building_type: str = None, num_floors: int = 1) -> List[ScopeItem]:
        """Get all regional requirements for a given location"""
        state = self.get_state_from_location(location)
        if not state:
            return []
        
        scope_items = []
        
        if state == "NH":
            # Add NH structural requirements
            for req in self.nh_requirements["structural"]:
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Structural"
                ))
            
            # Add NH mechanical requirements
            for req in self.nh_requirements["mechanical"]:
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Mechanical"
                ))
            
            # Add NH site requirements
            for req in self.nh_requirements["site"]:
                # Septic system only for certain locations
                if req["name"] == "Septic System Design & Installation":
                    # Skip septic for major cities
                    if any(city in location.lower() for city in ["manchester", "nashua", "concord"]):
                        continue
                
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Site Work"
                ))
        
        elif state == "TN":
            # Add TN structural requirements
            for req in self.tn_requirements["structural"]:
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Structural"
                ))
            
            # Add TN site requirements
            for req in self.tn_requirements["site"]:
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Site Work"
                ))
            
            # Add TN mechanical requirements
            for req in self.tn_requirements["mechanical"]:
                scope_items.append(ScopeItem(
                    name=req["name"],
                    quantity=square_footage,
                    unit="sqft",
                    unit_cost=req["cost_per_sqft"],
                    total_cost=square_footage * req["cost_per_sqft"],
                    note=req["note"],
                    category="Mechanical"
                ))
            
            # Add optional tornado safe room for certain building types
            if building_type in ["educational", "healthcare", "office"] and num_floors > 1:
                for req in self.tn_requirements["special"]:
                    if req.get("optional", False):
                        scope_items.append(ScopeItem(
                            name=req["name"],
                            quantity=1,
                            unit="LS",
                            unit_cost=req["cost_lump_sum"],
                            total_cost=req["cost_lump_sum"],
                            note=req["note"] + " (Optional)",
                            category="Special Requirements"
                        ))
        
        return scope_items
    
    def adjust_base_costs_for_region(self, state: str, base_costs: Dict[str, float]) -> Dict[str, float]:
        """Adjust base system costs based on regional requirements"""
        adjusted_costs = base_costs.copy()
        
        if state == "NH":
            # Increase structural costs for snow loads
            if "structural" in adjusted_costs:
                adjusted_costs["structural"] *= 1.15
            
            # Increase mechanical costs for energy efficiency
            if "mechanical" in adjusted_costs:
                adjusted_costs["mechanical"] *= 1.10
            
            # Increase envelope costs for insulation
            if "envelope" in adjusted_costs:
                adjusted_costs["envelope"] *= 1.20
        
        elif state == "TN":
            # Increase structural costs for seismic
            if "structural" in adjusted_costs:
                adjusted_costs["structural"] *= 1.08
            
            # Add fire protection costs
            if "fire_protection" in adjusted_costs:
                adjusted_costs["fire_protection"] *= 1.10
        
        return adjusted_costs


regional_requirements_service = RegionalRequirementsService()