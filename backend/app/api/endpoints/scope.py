from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List
import json
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.scope import ScopeRequest, ScopeResponse
from app.core.engine import engine as scope_engine
from app.services.floor_plan_service import floor_plan_service
from app.services.architectural_floor_plan_service import architectural_floor_plan_service
from app.services.trade_summary_service import trade_summary_service
from app.services.markup_service import markup_service
from app.services.nlp_service import nlp_service
from app.db.database import get_db
from app.db.models import Project, User
from app.api.endpoints.auth import get_current_user_with_cookie

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=ScopeResponse)
@limiter.limit("20/minute")
async def generate_scope(
    request: Request,
    scope_request: ScopeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    import logging
    import time
    logger = logging.getLogger(__name__)
    
    try:
        # Check if user has reached free estimate limit
        user = current_user  # current_user is now the actual User object
        
        # Check subscription status and estimate limit
        # TEMPORARILY DISABLED FOR TESTING - Re-enable by uncommenting below
        # FREE_ESTIMATE_LIMIT = 3
        # if not user.is_subscribed and user.estimate_count >= FREE_ESTIMATE_LIMIT:
        #     raise HTTPException(
        #         status_code=403, 
        #         detail={
        #             "error": "Free estimate limit reached",
        #             "message": "You've used all 3 free estimates. Please subscribe to continue.",
        #             "estimate_count": user.estimate_count,
        #             "limit": FREE_ESTIMATE_LIMIT
        #         }
        #     )
        logger.error(f"=== SCOPE GENERATION STARTED ===")
        logger.error(f"Request data: {scope_request.model_dump()}")
        
        # Track generation time
        start_time = time.time()
        
        # If occupancy_type is not set or is default, detect from special_requirements
        if (scope_request.occupancy_type == "office" or not scope_request.occupancy_type) and scope_request.special_requirements:
            nlp_result = nlp_service._fallback_analysis(scope_request.special_requirements)
            detected_occupancy = nlp_result.get('occupancy_type')
            if detected_occupancy and detected_occupancy != 'commercial':
                scope_request.occupancy_type = detected_occupancy
                logger.error(f"[NLP] Updated occupancy_type to: {detected_occupancy}")
                
                # Also extract unit mix if multi-family residential
                if detected_occupancy == 'multi_family_residential' and nlp_result.get('unit_mix'):
                    # Store unit mix data in request for later use
                    if not hasattr(scope_request, 'unit_mix'):
                        scope_request.unit_mix = nlp_result['unit_mix']
        
        scope_response = scope_engine.generate_scope(scope_request)
        
        # Generate architectural floor plan with error handling
        try:
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.project_type.value,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            scope_response.floor_plan = floor_plan_data
        except Exception as e:
            print(f"Error generating floor plan: {e}")
            import traceback
            traceback.print_exc()
            # Use old floor plan service as fallback
            floor_plan_data = floor_plan_service.generate_floor_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.project_type.value,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            scope_response.floor_plan = floor_plan_data
        
        # Generate trade summaries
        scope_dict = scope_response.model_dump()
        scope_dict['trade_summaries'] = trade_summary_service.generate_trade_summaries(scope_dict)
        
        # Update scope_response with trade summaries for storage
        scope_response_dict = scope_response.model_dump()
        scope_response_dict['trade_summaries'] = scope_dict['trade_summaries']
        
        # Apply markups to the scope
        scope_response_dict = markup_service.apply_markup_to_scope(
            scope_response_dict,
            db,
            current_user.id,
            None  # No project ID yet as we're creating new
        )
        
        # Calculate generation time
        generation_time = round(time.time() - start_time, 2)
        scope_response_dict['generation_time_seconds'] = generation_time
        
        # Always create a new project with unique ID
        db_project = Project(
            project_id=scope_response.project_id,
            name=scope_request.project_name,
            description=scope_request.special_requirements,  # Store the original input description
            project_type=scope_request.project_type.value,
            building_type=scope_request.occupancy_type,  # Store specific building type
            occupancy_type=scope_request.occupancy_type,
            square_footage=scope_request.square_footage,
            location=scope_request.location,
            climate_zone=scope_request.climate_zone.value if scope_request.climate_zone else None,
            num_floors=scope_request.num_floors,
            ceiling_height=scope_request.ceiling_height,
            total_cost=scope_response_dict.get('total_cost', scope_response.total_cost),
            cost_per_sqft=scope_response_dict.get('cost_per_sqft', scope_response.cost_per_sqft),
            scope_data=json.dumps(scope_response_dict, default=str),  # Save complete data including trade summaries
            cost_data=json.dumps(scope_response.cost_breakdown, default=str) if hasattr(scope_response, 'cost_breakdown') else None,
            user_id=current_user.id,
            created_by_id=current_user.id,
            team_id=user.current_team_id  # Associate with user's current team
        )
        
        db.add(db_project)
        
        # Increment user's estimate count
        user.estimate_count = (user.estimate_count or 0) + 1
        
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
    current_user: User = Depends(get_current_user_with_cookie)
):
    # Get user's current team
    user = current_user  # current_user is already the User object
    
    # Query projects - if user has a team, get all team projects
    if user.current_team_id:
        projects_query = db.query(Project, User.full_name.label('creator_name')).join(
            User, Project.created_by_id == User.id, isouter=True
        ).filter(
            Project.team_id == user.current_team_id
        )
    else:
        # Fallback to user's personal projects
        projects_query = db.query(Project, User.full_name.label('creator_name')).join(
            User, Project.created_by_id == User.id, isouter=True
        ).filter(
            Project.user_id == current_user.id
        )
    
    projects = projects_query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": p.Project.id,
            "project_id": p.Project.project_id,
            "name": p.Project.name,
            "project_type": p.Project.project_type,
            "building_type": p.Project.building_type,
            "occupancy_type": p.Project.occupancy_type,
            "description": p.Project.description,
            "square_footage": p.Project.square_footage,
            "location": p.Project.location,
            "total_cost": p.Project.total_cost,
            "cost_per_sqft": p.Project.cost_per_sqft,
            "created_at": p.Project.created_at,
            "created_by": p.creator_name or "Unknown",
            "scope_data": json.loads(p.Project.scope_data) if p.Project.scope_data else {}
        }
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ScopeResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
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
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Delete a project by ID"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
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
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Recalculate an existing project with the latest pricing engine"""
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
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


@router.post("/projects/{project_id}/duplicate")
async def duplicate_project(
    project_id: str,
    duplicate_name: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Duplicate an existing project"""
    # Find the original project
    original_project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not original_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate a new unique project ID
    import uuid
    new_project_id = str(uuid.uuid4())[:8]
    
    # Create the duplicate
    duplicate = Project(
        project_id=new_project_id,
        name=duplicate_name or f"{original_project.name} (Copy)",
        description=original_project.description,
        project_type=original_project.project_type,
        building_type=original_project.building_type,
        occupancy_type=original_project.occupancy_type,
        square_footage=original_project.square_footage,
        location=original_project.location,
        climate_zone=original_project.climate_zone,
        num_floors=original_project.num_floors,
        ceiling_height=original_project.ceiling_height,
        total_cost=original_project.total_cost,
        cost_per_sqft=original_project.cost_per_sqft,
        scope_data=original_project.scope_data,
        cost_data=original_project.cost_data,
        user_id=current_user.id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    # Return the new project data
    scope_data = json.loads(duplicate.scope_data)
    # Update the project_id in the response
    scope_data['project_id'] = new_project_id
    scope_data['project_name'] = duplicate.name
    
    return scope_data


@router.get("/debug/electrical/{project_id}")
async def debug_electrical(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
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