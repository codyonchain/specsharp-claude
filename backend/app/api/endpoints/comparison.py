from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.services.comparison_service import comparison_service
from app.api.endpoints.auth import get_current_user
from app.api.endpoints.scope import get_project
from app.db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter()


class ScenarioModification(BaseModel):
    name: str = Field(..., description="Name for this scenario")
    square_footage: float = Field(None, gt=0, le=1000000)
    building_mix: Dict[str, float] = Field(None, description="Building type percentages")
    features: Dict[str, Any] = Field(None, description="Feature modifications")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Increased Warehouse",
                "square_footage": 50000,
                "building_mix": {
                    "warehouse": 0.8,
                    "office": 0.2
                },
                "features": {
                    "bathrooms": 4,
                    "dock_doors": 6
                }
            }
        }


class ComparisonRequest(BaseModel):
    scenarios: List[ScenarioModification] = Field(..., min_items=1, max_items=3)


@router.post("/compare/{project_id}")
async def create_comparison(
    project_id: str,
    request: ComparisonRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a what-if comparison between multiple scenarios"""
    
    try:
        # Get base project data
        project_data = await get_project(project_id, db, current_user)
        
        # Convert to dict if it's a Pydantic model
        if hasattr(project_data, 'model_dump'):
            project_dict = project_data.model_dump()
        else:
            project_dict = dict(project_data)
        
        # Create scenario modifications list
        scenario_mods = [mod.model_dump(exclude_none=True) for mod in request.scenarios]
        
        # Generate comparison
        comparison_result = comparison_service.create_scenario_comparison(
            project_dict, 
            scenario_mods
        )
        
        return {
            'success': True,
            'comparison': comparison_result
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        error_detail = f"Error creating comparison: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)  # Log to console for debugging
        raise HTTPException(status_code=500, detail=f"Error creating comparison: {str(e)}")


@router.get("/templates")
async def get_comparison_templates(
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get pre-defined comparison templates"""
    
    templates = [
        {
            "name": "Cost Optimization",
            "description": "Compare different building mixes to find the most cost-effective option",
            "scenarios": [
                {
                    "name": "Warehouse Heavy (80/20)",
                    "building_mix": {"warehouse": 0.8, "office": 0.2}
                },
                {
                    "name": "Balanced (60/40)",
                    "building_mix": {"warehouse": 0.6, "office": 0.4}
                },
                {
                    "name": "Office Heavy (40/60)",
                    "building_mix": {"warehouse": 0.4, "office": 0.6}
                }
            ]
        },
        {
            "name": "Size Analysis",
            "description": "Compare different building sizes to understand cost scaling",
            "scenarios": [
                {
                    "name": "Small (-25%)",
                    "square_footage_multiplier": 0.75
                },
                {
                    "name": "Base Size",
                    "square_footage_multiplier": 1.0
                },
                {
                    "name": "Large (+25%)",
                    "square_footage_multiplier": 1.25
                }
            ]
        },
        {
            "name": "Feature Impact",
            "description": "Compare the cost impact of adding different features",
            "scenarios": [
                {
                    "name": "Basic",
                    "features": {"bathrooms": 2, "dock_doors": 2}
                },
                {
                    "name": "Standard",
                    "features": {"bathrooms": 4, "dock_doors": 4}
                },
                {
                    "name": "Enhanced",
                    "features": {"bathrooms": 6, "dock_doors": 6, "break_room": True}
                }
            ]
        }
    ]
    
    return {
        'success': True,
        'templates': templates
    }