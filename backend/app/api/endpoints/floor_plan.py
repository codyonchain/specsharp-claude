from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import uuid
from typing import Optional
import os

from app.models.floor_plan import FloorPlanRequest, FloorPlanResponse
from app.services.sketcher import FloorPlanGenerator
from app.db.database import get_db
from app.db.models import FloorPlan as DBFloorPlan, Project
from app.api.endpoints.auth import get_current_user

router = APIRouter()
floor_plan_generator = FloorPlanGenerator()


@router.post("/generate", response_model=FloorPlanResponse)
async def generate_floor_plan(
    request: FloorPlanRequest,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        floor_plan = floor_plan_generator.generate(request)
        
        db_floor_plan = DBFloorPlan(
            floor_plan_id=floor_plan.id,
            project_id=None,
            total_area=floor_plan.total_area,
            efficiency_ratio=floor_plan.efficiency_ratio,
            svg_data=floor_plan.svg_data,
            floor_plan_data=json.dumps(floor_plan.model_dump())
        )
        
        if project_id:
            project = db.query(Project).filter(
                Project.project_id == project_id,
                Project.user_id == current_user["id"]
            ).first()
            if project:
                db_floor_plan.project_id = project.id
        
        db.add(db_floor_plan)
        db.commit()
        db.refresh(db_floor_plan)
        
        return floor_plan
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating floor plan: {str(e)}")


@router.get("/plans/{floor_plan_id}", response_model=FloorPlanResponse)
async def get_floor_plan(
    floor_plan_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    floor_plan = db.query(DBFloorPlan).filter(
        DBFloorPlan.floor_plan_id == floor_plan_id
    ).first()
    
    if not floor_plan:
        raise HTTPException(status_code=404, detail="Floor plan not found")
    
    if floor_plan.project:
        if floor_plan.project.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return json.loads(floor_plan.floor_plan_data)


@router.get("/plans/{floor_plan_id}/image")
async def get_floor_plan_image(
    floor_plan_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    floor_plan = db.query(DBFloorPlan).filter(
        DBFloorPlan.floor_plan_id == floor_plan_id
    ).first()
    
    if not floor_plan:
        raise HTTPException(status_code=404, detail="Floor plan not found")
    
    if floor_plan.project:
        if floor_plan.project.user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
    if floor_plan.image_path and os.path.exists(floor_plan.image_path):
        return FileResponse(floor_plan.image_path, media_type="image/png")
    
    raise HTTPException(status_code=404, detail="Floor plan image not found")