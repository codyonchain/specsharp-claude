from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class ProjectType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    MIXED_USE = "mixed_use"


class ClimateZone(str, Enum):
    HOT_HUMID = "hot_humid"
    HOT_DRY = "hot_dry"
    TEMPERATE = "temperate"
    COLD = "cold"
    VERY_COLD = "very_cold"


class BuildingSystem(BaseModel):
    name: str
    quantity: float = Field(gt=0)
    unit: str
    unit_cost: float = Field(ge=0)
    total_cost: float = Field(ge=0)
    specifications: Dict[str, Any] = {}
    confidence_score: int = Field(default=95, ge=0, le=100)
    confidence_label: str = Field(default="High")
    confidence_factors: Optional[Dict[str, Any]] = None
    
    @validator('total_cost', always=True)
    def calculate_total_cost(cls, v, values):
        if 'quantity' in values and 'unit_cost' in values:
            return round(values['quantity'] * values['unit_cost'], 2)
        return v


class ScopeRequest(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: ProjectType
    square_footage: float = Field(..., gt=0, le=1000000)
    location: str = Field(..., min_length=1)
    climate_zone: Optional[ClimateZone] = None
    num_floors: int = Field(default=1, ge=1, le=100)
    ceiling_height: float = Field(default=9.0, gt=0, le=30)
    occupancy_type: str = Field(default="office")
    special_requirements: Optional[str] = None
    budget_constraint: Optional[float] = Field(None, gt=0)
    building_mix: Optional[Dict[str, float]] = None
    service_level: Optional[str] = None  # e.g., "full_service" for restaurants
    building_features: Optional[List[str]] = None  # e.g., ["commercial_kitchen", "full_bar"]
    unit_mix: Optional[Dict[str, Any]] = None  # For multi-family residential
    
    @validator('building_mix')
    def validate_building_mix(cls, v, values):
        if v is not None:
            total = sum(v.values())
            if abs(total - 1.0) > 0.01:  # Allow small floating point errors
                raise ValueError(f"Building mix percentages must sum to 1.0 (100%), got {total}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_name": "Downtown Office Building",
                "project_type": "commercial",
                "square_footage": 50000,
                "location": "Seattle, WA",
                "num_floors": 5,
                "ceiling_height": 10,
                "occupancy_type": "office",
                "special_requirements": "LEED Gold certification required"
            }
        }


class ScopeCategory(BaseModel):
    name: str
    systems: List[BuildingSystem]
    subtotal: float = Field(default=0.0, ge=0)
    
    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        if 'systems' in values:
            return round(sum(system.total_cost for system in values['systems']), 2)
        return v


class ScopeResponse(BaseModel):
    project_id: str
    project_name: str
    created_at: datetime
    request_data: ScopeRequest
    categories: List[ScopeCategory]
    subtotal: float = Field(default=0.0, ge=0)
    contingency_percentage: float = Field(default=10.0, ge=0, le=50)
    contingency_amount: float = Field(default=0.0, ge=0)
    total_cost: float = Field(default=0.0, ge=0)
    cost_per_sqft: float = Field(default=0.0, ge=0)
    floor_plan: Optional[Dict[str, Any]] = None
    
    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        if 'categories' in values:
            return round(sum(cat.subtotal for cat in values['categories']), 2)
        return v
    
    @validator('contingency_amount', always=True)
    def calculate_contingency(cls, v, values):
        if 'subtotal' in values and 'contingency_percentage' in values:
            return round(values['subtotal'] * values['contingency_percentage'] / 100, 2)
        return v
    
    @validator('total_cost', always=True)
    def calculate_total(cls, v, values):
        if 'subtotal' in values and 'contingency_amount' in values:
            return round(values['subtotal'] + values['contingency_amount'], 2)
        return v
    
    @validator('cost_per_sqft', always=True)
    def calculate_cost_per_sqft(cls, v, values):
        if 'total_cost' in values and 'request_data' in values:
            request_data = values['request_data']
            if hasattr(request_data, 'square_footage') and request_data.square_footage > 0:
                return round(values['total_cost'] / request_data.square_footage, 2)
        return v


class CostBreakdown(BaseModel):
    category: str
    items: List[Dict[str, Any]]
    subtotal: float = Field(ge=0)
    percentage_of_total: float = Field(ge=0, le=100)