"""Pydantic schemas for project scenarios"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class ScenarioModificationSchema(BaseModel):
    """Schema for a single modification"""
    parameter: str
    original_value: Any
    new_value: Any
    cost_impact: Optional[float] = None
    timeline_impact: Optional[float] = None
    roi_impact: Optional[float] = None
    impact_description: Optional[str] = None


class ScenarioCreate(BaseModel):
    """Schema for creating a new scenario"""
    name: str = Field(..., description="Scenario name e.g. 'Luxury Finish'")
    description: Optional[str] = Field(None, description="Detailed description")
    modifications: Dict[str, Any] = Field(..., description="Modifications from base project")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Premium Build",
                "description": "Higher-end finishes with amenity package",
                "modifications": {
                    "finish_level": "luxury",
                    "amenity_package": "premium",
                    "parking_ratio": 1.5
                }
            }
        }


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario"""
    name: Optional[str] = None
    description: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None


class ScenarioResponse(BaseModel):
    """Response schema for scenario data"""
    id: str
    project_id: int
    name: str
    description: Optional[str]
    modifications: Dict[str, Any]
    is_base: bool
    
    # Financial metrics
    total_cost: float
    construction_cost: float
    soft_costs: float
    cost_per_sqft: float
    roi: float
    npv: float
    irr: float
    payback_period: float
    dscr: float
    
    # Revenue metrics
    annual_revenue: float
    monthly_revenue: float
    noi: float
    
    # Building metrics
    square_footage: float
    unit_count: Optional[int]
    finish_level: Optional[str]
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ScenarioComparisonRequest(BaseModel):
    """Request for comparing scenarios"""
    scenario_ids: List[str] = Field(..., min_items=2, max_items=5)
    name: Optional[str] = Field(None, description="Name for this comparison")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_ids": ["scenario-1-id", "scenario-2-id", "scenario-3-id"],
                "name": "Q4 Board Presentation Options"
            }
        }


class MetricComparison(BaseModel):
    """Comparison of a single metric across scenarios"""
    metric_name: str
    values: List[float]  # One value per scenario
    winner_scenario_id: str
    winner_scenario_name: str
    best_value: float
    worst_value: float
    delta_from_base: List[float]  # Delta from first scenario


class ScenarioComparisonResponse(BaseModel):
    """Response for scenario comparison"""
    comparison_name: Optional[str]
    scenario_ids: List[str]
    scenario_names: List[str]
    
    # Metric comparisons
    metrics_comparison: Dict[str, List[float]]
    winner_by_metric: Dict[str, str]
    
    # Delta analysis
    cost_deltas: Dict[str, float]  # scenario_id: delta from base
    roi_deltas: Dict[str, float]
    timeline_deltas: Dict[str, float]
    
    # Summary insights
    best_overall_scenario: str
    best_roi_scenario: str
    lowest_cost_scenario: str
    fastest_payback_scenario: str
    
    # Detailed comparisons
    metric_details: List[MetricComparison]
    
    class Config:
        json_schema_extra = {
            "example": {
                "comparison_name": "Q4 Board Options",
                "scenario_ids": ["base", "luxury", "standard"],
                "scenario_names": ["Base Design", "Luxury Finish", "Standard Build"],
                "metrics_comparison": {
                    "total_cost": [15000000, 18000000, 13500000],
                    "roi": [0.082, 0.095, 0.075],
                    "payback_years": [8.2, 7.5, 9.1]
                },
                "winner_by_metric": {
                    "roi": "Luxury Finish",
                    "total_cost": "Standard Build",
                    "payback": "Luxury Finish"
                },
                "cost_deltas": {
                    "luxury": 3000000,
                    "standard": -1500000
                },
                "roi_deltas": {
                    "luxury": 0.013,
                    "standard": -0.007
                },
                "best_overall_scenario": "Luxury Finish",
                "best_roi_scenario": "Luxury Finish",
                "lowest_cost_scenario": "Standard Build",
                "fastest_payback_scenario": "Luxury Finish"
            }
        }


class ScenarioExportRequest(BaseModel):
    """Request for exporting scenario comparison"""
    scenario_ids: List[str] = Field(..., min_items=1, max_items=5)
    format: str = Field(..., pattern="^(pdf|excel|pptx)$")
    include_charts: bool = Field(True, description="Include visualization charts")
    include_details: bool = Field(True, description="Include detailed breakdowns")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scenario_ids": ["scenario-1", "scenario-2"],
                "format": "pdf",
                "include_charts": True,
                "include_details": True
            }
        }