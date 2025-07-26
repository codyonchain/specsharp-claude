from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.scope import ScopeRequest, ScopeResponse
from app.core.engine import engine as scope_engine
from app.services.floor_plan_service import floor_plan_service
from app.services.architectural_floor_plan_service import architectural_floor_plan_service
from app.services.trade_summary_service import trade_summary_service
from app.db.database import get_db
from app.db.models import Project
from app.api.endpoints.auth import get_current_user

router = APIRouter()


@router.post("/generate", response_model=ScopeResponse)
async def generate_scope(
    request: ScopeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"=== SCOPE GENERATION STARTED ===")
        logger.error(f"Request data: {request.model_dump()}")
        
        scope_response = scope_engine.generate_scope(request)
        
        # Generate architectural floor plan with error handling
        try:
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=request.square_footage,
                project_type=request.project_type.value,
                building_mix=getattr(request, 'building_mix', None)
            )
            scope_response.floor_plan = floor_plan_data
        except Exception as e:
            print(f"Error generating floor plan: {e}")
            import traceback
            traceback.print_exc()
            # Use old floor plan service as fallback
            floor_plan_data = floor_plan_service.generate_floor_plan(
                square_footage=request.square_footage,
                project_type=request.project_type.value,
                building_mix=getattr(request, 'building_mix', None)
            )
            scope_response.floor_plan = floor_plan_data
        
        # Generate trade summaries
        scope_dict = scope_response.model_dump()
        scope_dict['trade_summaries'] = trade_summary_service.generate_trade_summaries(scope_dict)
        
        # Update scope_response with trade summaries for storage
        scope_response_dict = scope_response.model_dump()
        scope_response_dict['trade_summaries'] = scope_dict['trade_summaries']
        
        # Always create a new project with unique ID
        db_project = Project(
            project_id=scope_response.project_id,
            name=request.project_name,
            project_type=request.project_type.value,
            square_footage=request.square_footage,
            location=request.location,
            climate_zone=request.climate_zone.value if request.climate_zone else None,
            num_floors=request.num_floors,
            ceiling_height=request.ceiling_height,
            total_cost=scope_response.total_cost,
            scope_data=json.dumps(scope_response_dict, default=str),  # Save complete data including trade summaries
            user_id=current_user["id"]
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Return the complete response with trade summaries
        return scope_response_dict
        
    except Exception as e:
        import traceback
        logger.error(f"=== SCOPE GENERATION FAILED ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating scope: {str(e)}")


@router.get("/projects", response_model=List[dict])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    projects = db.query(Project).filter(
        Project.user_id == current_user["id"]
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.id,
            "project_id": p.project_id,
            "name": p.name,
            "project_type": p.project_type,
            "square_footage": p.square_footage,
            "location": p.location,
            "total_cost": p.total_cost,
            "created_at": p.created_at
        }
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ScopeResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse stored scope data
    scope_data = json.loads(project.scope_data)
    
    # Check if floor plan already exists in stored data
    if 'floor_plan' not in scope_data or not scope_data.get('floor_plan'):
        # Generate floor plan if missing
        try:
            request_data = scope_data.get('request_data', {})
            building_mix = request_data.get('building_mix') if request_data else None
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=project.square_footage,
                project_type=project.project_type,
                building_mix=building_mix
            )
        except Exception as e:
            print(f"Error generating architectural floor plan: {e}")
            # Fallback to old service
            request_data = scope_data.get('request_data', {})
            building_mix = request_data.get('building_mix') if request_data else None
            floor_plan_data = floor_plan_service.generate_floor_plan(
                square_footage=project.square_footage,
                project_type=project.project_type,
                building_mix=building_mix
            )
        scope_data['floor_plan'] = floor_plan_data
    
    # Generate trade summaries
    scope_data['trade_summaries'] = trade_summary_service.generate_trade_summaries(scope_data)
    
    return scope_data


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a project by ID"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete the project
    db.delete(project)
    db.commit()
    
    return {"message": "Project deleted successfully", "project_id": project_id}


@router.post("/projects/{project_id}/recalculate", response_model=ScopeResponse)
async def recalculate_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Recalculate an existing project with the latest pricing engine"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse stored scope data to get original request
    scope_data = json.loads(project.scope_data)
    request_data = scope_data.get('request_data', {})
    
    # Reconstruct the ScopeRequest
    scope_request = ScopeRequest(**request_data)
    
    # Regenerate the scope with current engine
    new_scope_response = scope_engine.generate_scope(scope_request)
    
    # Generate floor plan
    if 'floor_plan' not in scope_data or not scope_data.get('floor_plan'):
        try:
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.project_type.value,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            new_scope_response.floor_plan = floor_plan_data
        except Exception as e:
            floor_plan_data = floor_plan_service.generate_floor_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.project_type.value,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            new_scope_response.floor_plan = floor_plan_data
    else:
        new_scope_response.floor_plan = scope_data['floor_plan']
    
    # Generate trade summaries
    new_scope_response.trade_summaries = trade_summary_service.generate_trade_summaries(
        json.loads(new_scope_response.model_dump_json())
    )
    
    # Update the project in database
    project.scope_data = new_scope_response.model_dump_json()
    db.commit()
    
    return new_scope_response


@router.get("/debug/electrical/{project_id}")
async def debug_electrical(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Debug endpoint to verify electrical calculations"""
    from app.services.electrical_standards_service import electrical_standards_service
    from app.services.electrical_v2_service import electrical_v2_service
    
    # Get project
    project = await get_project(project_id, db, current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Convert to dict
    if hasattr(project, 'model_dump'):
        project_dict = project.model_dump()
    else:
        project_dict = dict(project)
    
    # Extract key data
    request_data = project_dict.get('request_data', {})
    cost_breakdown = project_dict.get('cost_breakdown', {})
    if isinstance(cost_breakdown, str):
        try:
            cost_breakdown = json.loads(cost_breakdown)
        except:
            cost_breakdown = {}
    
    # Run V2 calculation directly
    v2_result = electrical_v2_service.calculate_electrical_cost(project_dict)
    
    # Get stored electrical cost
    stored_electrical = cost_breakdown.get('electrical', {}).get('total', 0)
    
    return {
        "project_id": project_id,
        "building_type": request_data.get('building_type', 'Unknown'),
        "state": request_data.get('state', project_dict.get('state', 'Unknown')),
        "location": project_dict.get('location', 'Unknown'),
        "square_footage": request_data.get('square_footage', 0),
        "building_mix": request_data.get('building_mix', {}),
        "stored_electrical_cost": stored_electrical,
        "v2_calculation": {
            "total_cost": v2_result.get('total', 0),
            "base_cost": v2_result.get('subtotal', 0),
            "regional_multiplier": v2_result.get('regional_multiplier', 1.0),
            "cost_per_sf": v2_result.get('cost_per_sf', 0),
            "regional_tier": v2_result.get('regional_tier', 'Unknown')
        },
        "expected_range": {
            "min": 700000,
            "max": 850000,
            "note": "For 45k SF mixed-use in CA"
        }
    }