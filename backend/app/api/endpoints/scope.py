from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json

from app.models.scope import ScopeRequest, ScopeResponse
from app.core.engine import engine as scope_engine
from app.services.floor_plan_service import floor_plan_service
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
        print(f"Received scope request: {request.model_dump()}")
        scope_response = scope_engine.generate_scope(request)
        
        # Generate floor plan
        floor_plan_data = floor_plan_service.generate_floor_plan(
            square_footage=request.square_footage,
            project_type=request.project_type.value,
            building_mix=getattr(request, 'building_mix', None)
        )
        
        # Add floor plan to response
        scope_response.floor_plan = floor_plan_data
        
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
            scope_data=scope_response.model_dump_json(),
            user_id=current_user["id"]
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return scope_response
        
    except Exception as e:
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
    
    # Regenerate floor plan data
    floor_plan_data = floor_plan_service.generate_floor_plan(
        square_footage=project.square_footage,
        project_type=project.project_type,
        building_mix=scope_data.get('request_data', {}).get('building_mix')
    )
    
    # Add floor plan to response
    scope_data['floor_plan'] = floor_plan_data
    
    return scope_data