from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from app.models.scope import CostBreakdown
from app.api.endpoints.auth import get_current_user

router = APIRouter()


class CostUpdateRequest(BaseModel):
    category: str
    item_name: str
    new_cost: float = Field(gt=0)


class CostDatabase:
    def __init__(self):
        self.regional_multipliers = {
            "New York, NY": 1.3,
            "San Francisco, CA": 1.25,
            "Los Angeles, CA": 1.15,
            "Chicago, IL": 1.1,
            "Houston, TX": 0.95,
            "Phoenix, AZ": 0.9,
            "Philadelphia, PA": 1.05,
            "San Antonio, TX": 0.85,
            "San Diego, CA": 1.2,
            "Dallas, TX": 0.95,
            "Austin, TX": 1.0,
            "Seattle, WA": 1.15,
            "Denver, CO": 1.05,
            "Boston, MA": 1.25,
            "Miami, FL": 1.1,
        }
        
        self.material_costs = {
            "concrete": {"unit": "cubic_yard", "base_cost": 150},
            "steel": {"unit": "ton", "base_cost": 800},
            "lumber": {"unit": "board_foot", "base_cost": 0.75},
            "drywall": {"unit": "sheet", "base_cost": 12},
            "insulation": {"unit": "sqft", "base_cost": 1.5},
            "roofing_shingle": {"unit": "square", "base_cost": 350},
            "flooring_tile": {"unit": "sqft", "base_cost": 5},
            "paint": {"unit": "gallon", "base_cost": 35},
            "electrical_wire": {"unit": "foot", "base_cost": 2},
            "plumbing_pipe": {"unit": "foot", "base_cost": 8},
        }
        
        self.labor_rates = {
            "general_contractor": {"unit": "hour", "base_rate": 75},
            "electrician": {"unit": "hour", "base_rate": 85},
            "plumber": {"unit": "hour", "base_rate": 80},
            "carpenter": {"unit": "hour", "base_rate": 65},
            "painter": {"unit": "hour", "base_rate": 55},
            "hvac_technician": {"unit": "hour", "base_rate": 90},
            "mason": {"unit": "hour", "base_rate": 70},
            "roofer": {"unit": "hour", "base_rate": 60},
        }


cost_db = CostDatabase()


@router.get("/regional-multipliers", response_model=Dict[str, float])
async def get_regional_multipliers(
    current_user: dict = Depends(get_current_user)
):
    return cost_db.regional_multipliers


@router.get("/materials", response_model=Dict[str, Dict[str, Any]])
async def get_material_costs(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    materials = cost_db.material_costs.copy()
    
    if location:
        multiplier = cost_db.regional_multipliers.get(location, 1.0)
        for material, data in materials.items():
            data["adjusted_cost"] = round(data["base_cost"] * multiplier, 2)
            data["location_multiplier"] = multiplier
    
    return materials


@router.get("/labor", response_model=Dict[str, Dict[str, Any]])
async def get_labor_rates(
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    labor = cost_db.labor_rates.copy()
    
    if location:
        multiplier = cost_db.regional_multipliers.get(location, 1.0)
        for trade, data in labor.items():
            data["adjusted_rate"] = round(data["base_rate"] * multiplier, 2)
            data["location_multiplier"] = multiplier
    
    return labor


@router.post("/calculate-breakdown", response_model=List[CostBreakdown])
async def calculate_cost_breakdown(
    scope_data: dict,
    current_user: dict = Depends(get_current_user)
):
    try:
        categories = scope_data.get("categories", [])
        total_cost = scope_data.get("total_cost", 0)
        
        breakdowns = []
        
        for category in categories:
            items = []
            for system in category.get("systems", []):
                items.append({
                    "name": system["name"],
                    "quantity": system["quantity"],
                    "unit": system["unit"],
                    "unit_cost": system["unit_cost"],
                    "total_cost": system["total_cost"]
                })
            
            percentage = (category["subtotal"] / total_cost * 100) if total_cost > 0 else 0
            
            breakdown = CostBreakdown(
                category=category["name"],
                items=items,
                subtotal=category["subtotal"],
                percentage_of_total=round(percentage, 2)
            )
            breakdowns.append(breakdown)
        
        return breakdowns
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error calculating breakdown: {str(e)}")