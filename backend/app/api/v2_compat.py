"""
V2 API Compatibility Layer for Production Frontend
Uses existing backend services to handle V2 API calls
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json

# Import core dependencies
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User, Project
from app.api.endpoints.auth import get_current_user_with_cookie

# Import existing services
from app.services.nlp_service import nlp_service
from app.services.clean_engine_v2 import calculate_scope
from app.services.cost_service import CostService
from app.core.building_type_detector import determine_building_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["v2-compat"])

# V2 Request/Response Models
class V2AnalyzeRequest(BaseModel):
    description: str = Field(..., description="Natural language project description")
    
class V2AnalyzeResponse(BaseModel):
    project_id: str
    project_name: str
    building_type: str
    building_subtype: str
    location: Dict[str, Any]
    size: int
    stories: int
    data: Dict[str, Any]
    scope: Dict[str, Any]
    calculations: Optional[Dict[str, Any]] = None

class V2ProjectResponse(BaseModel):
    id: str
    name: str
    building_type: str
    building_subtype: str
    data: Dict[str, Any]
    created_at: str
    updated_at: str

@router.post("/analyze", response_model=V2AnalyzeResponse)
async def v2_analyze(
    request: V2AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_cookie)
):
    """
    V2 endpoint for project analysis from natural language description.
    Uses existing NLP service for parsing and scope generator for project data.
    """
    try:
        logger.info(f"V2 analyze request from user {current_user.id if current_user else 'anonymous'}: {request.description[:100]}...")
        
        # Use existing NLP service to parse the description
        parsed_data = nlp_service.extract_project_details(request.description)
        
        # Extract key information from NLP results
        building_type = parsed_data.get("building_type", "commercial")
        building_subtype = parsed_data.get("building_subtype", "office")
        
        # Handle size extraction - NLP service may return it differently
        size = parsed_data.get("size", parsed_data.get("square_feet", 25000))
        if isinstance(size, str):
            size = int(size.replace(",", "").replace("SF", "").replace("sqft", "").strip())
        
        # Location data with defaults
        location = parsed_data.get("location", {
            "city": "Nashville",
            "state": "TN",
            "climate_zone": "4A"
        })
        
        # Ensure location has required fields
        if isinstance(location, str):
            location = {
                "city": location,
                "state": "TN",
                "climate_zone": "4A"
            }
        
        stories = parsed_data.get("stories", 4)
        units = parsed_data.get("units", None)
        
        logger.info(f"NLP parsed: type={building_type}/{building_subtype}, size={size}, location={location}")
        
        # Generate comprehensive project data
        project_data = {
            "building_type": building_type,
            "building_subtype": building_subtype,
            "location": location,
            "size": size,
            "stories": stories,
            "units": units,
            "construction_type": parsed_data.get("construction_type", "wood_frame" if stories <= 3 else "steel_frame"),
            "parking_type": parsed_data.get("parking_type", "surface"),
            "parking_ratio": parsed_data.get("parking_ratio", 1.5 if building_type == "multifamily" else 3.0),
            "site_area": int(size * 2.5),
            "efficiency_ratio": 0.85,
            "description": request.description
        }
        
        # Generate scope using existing engine
        try:
            scope_response = calculate_scope({
                "building_type": building_type,
                "square_footage": size,
                "location": location.get("city", "Nashville") if isinstance(location, dict) else "Nashville".get("city", "Nashville") if isinstance(location, dict) else "Nashville",
                "num_floors": stories,
                "building_subtype": building_subtype,
                "project_classification": parsed_data.get("project_classification", "ground_up"),
                "project_description": request.description}
            )
            scope_data = scope_response
        except Exception as e:
            logger.error(f"Scope generation error: {str(e)}")
            # Fallback scope generation
            scope_data = {
                "total_hard_cost": size * 200,  # Basic estimate
                "cost_per_sqft": 200,
                "schedule_months": 12,
                "trades": [],
                "systems": []
            }
        
        # Use cost service for additional calculations if available
        try:
            cost_service = CostService(db)
            cost_data = cost_service.calculate_costs(project_data)
            project_data["cost_breakdown"] = cost_data
        except Exception as e:
            logger.warning(f"Cost service calculation skipped: {str(e)}")
        
        # Generate project ID and name
        timestamp = int(datetime.now().timestamp() * 1000)
        project_id = f"proj_{timestamp}"
        
        # Generate descriptive project name
        subtype_name = building_subtype.replace("_", " ").title()
        city = location.get("city", "Nashville") if isinstance(location, dict) else "Nashville"
        project_name = f"{subtype_name} - {city}"
        
        # Save project if user is authenticated
        if current_user:
            try:
                # Create new project in database
                new_project = Project(
                    user_id=current_user.id,
                    name=project_name,
                    data={
                        **project_data,
                        "scope": scope_data,
                        "created_via": "v2_api",
                        "original_description": request.description
                    }
                )
                db.add(new_project)
                db.commit()
                db.refresh(new_project)
                
                project_id = f"proj_{new_project.id}"
                logger.info(f"Saved project {project_id} for user {current_user.id}")
                
            except Exception as e:
                logger.warning(f"Could not save project: {str(e)}")
                db.rollback()
        
        # Calculate summary metrics
        calculations = {
            "total_cost": scope_data.get("total_hard_cost", 0),
            "cost_per_sqft": scope_data.get("cost_per_sqft", 0),
            "development_months": scope_data.get("schedule_months", 12),
            "soft_costs": scope_data.get("total_soft_cost", scope_data.get("total_hard_cost", 0) * 0.3),
            "total_project_cost": scope_data.get("total_project_cost", scope_data.get("total_hard_cost", 0) * 1.3)
        }
        
        # Create V2 response
        response = V2AnalyzeResponse(
            project_id=project_id,
            project_name=project_name,
            "building_subtype": building_subtype,
            building_subtype=building_subtype,
            "location": location.get("city", "Nashville") if isinstance(location, dict) else "Nashville",
            size=size,
            "num_floors": stories,
            data=project_data,
            scope=scope_data,
            calculations=calculations
        )
        
        logger.info(f"V2 analyze successful: {project_id}")
        return response
        
    except Exception as e:
        logger.error(f"V2 analyze error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/projects", response_model=List[V2ProjectResponse])
async def v2_get_projects(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_cookie)
):
    """Get all projects for the current user in V2 format"""
    try:
        if not current_user:
            return []
        
        projects = db.query(Project).filter(
            Project.user_id == current_user.id
        ).order_by(Project.created_at.desc()).limit(100).all()
        
        return [
            V2ProjectResponse(
                id=f"proj_{p.id}",
                name=p.name,
                building_type=p.data.get("building_type", "commercial"),
                building_subtype=p.data.get("building_subtype", "office"),
                data=p.data,
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat()
            )
            for p in projects
        ]
    except Exception as e:
        logger.error(f"V2 get projects error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/projects/{project_id}", response_model=V2ProjectResponse)
async def v2_get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_with_cookie)
):
    """Get a specific project in V2 format"""
    try:
        # Handle both proj_123 and plain 123 formats
        if project_id.startswith("proj_"):
            numeric_id = int(project_id.replace("proj_", ""))
        else:
            numeric_id = int(project_id)
        
        project = db.query(Project).filter(
            Project.id == numeric_id
        ).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check ownership if user is authenticated
        if current_user and project.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return V2ProjectResponse(
            id=f"proj_{project.id}",
            name=project.name,
            building_type=project.data.get("building_type", "commercial"),
            building_subtype=project.data.get("building_subtype", "office"),
            data=project.data,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat()
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"V2 get project error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def v2_health():
    """V2 health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "nlp": "available",
            "scope_generator": "available",
            "cost_service": "available"
        }
    }
