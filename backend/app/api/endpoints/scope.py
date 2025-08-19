from fastapi import APIRouter, HTTPException, Depends, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_
from typing import List, Optional, Dict
import json
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from app.models.scope import ScopeRequest, ScopeResponse
from app.services.clean_engine_v2 import calculate_scope
from app.services.owner_view_engine import OwnerViewOrchestrator

import logging
logger = logging.getLogger(__name__)

from app.services.floor_plan_service import floor_plan_service
from app.services.architectural_floor_plan_service import architectural_floor_plan_service
from app.services.markup_service import markup_service
from app.services.nlp_service import nlp_service
from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.utils.cost_validation import (
    validate_project_costs, 
    detect_cost_discrepancy, 
    log_cost_calculation,
    CostValidationError
)
from app.db.database import get_db
from app.db.models import Project, User
from app.api.endpoints.auth import get_current_user_with_cookie
import logging
import traceback
from sqlalchemy.exc import OperationalError

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)


def create_project_safely(db, project_data):
    """Create a project, handling missing columns in production database"""
    # Essential fields that should always exist
    essential_fields = {
        'project_id': project_data.get('project_id'),
        'name': project_data.get('name'),
        'project_type': project_data.get('project_type'),
        'square_footage': project_data.get('square_footage'),
        'location': project_data.get('location'),
        'total_cost': project_data.get('total_cost'),
        'scope_data': project_data.get('scope_data'),
        'user_id': project_data.get('user_id'),
        'num_floors': project_data.get('num_floors', 1),
        'ceiling_height': project_data.get('ceiling_height', 9.0),
    }
    
    # Optional fields that might not exist in production
    optional_fields = {
        'description': project_data.get('description'),
        'project_classification': project_data.get('project_classification', 'ground_up'),
        'building_type': project_data.get('building_type'),
        'occupancy_type': project_data.get('occupancy_type'),
        'climate_zone': project_data.get('climate_zone'),
        'subtotal': project_data.get('subtotal'),
        'contingency_percentage': project_data.get('contingency_percentage', 10.0),
        'contingency_amount': project_data.get('contingency_amount'),
        'cost_per_sqft': project_data.get('cost_per_sqft'),
        'cost_data': project_data.get('cost_data'),
        'team_id': project_data.get('team_id'),
        'created_by_id': project_data.get('created_by_id'),
        'scenario_name': project_data.get('scenario_name'),
    }
    
    # Try to create with all fields first
    try:
        all_fields = {**essential_fields, **optional_fields}
        db_project = Project(**all_fields)
        return db_project
    except Exception as e:
        logger.warning(f"Failed to create project with all fields: {str(e)}")
        # Fall back to essential fields only
        db_project = Project(**essential_fields)
        # Set optional fields using setattr to avoid constructor issues
        for field, value in optional_fields.items():
            try:
                setattr(db_project, field, value)
            except:
                logger.debug(f"Skipping field {field} - not in database schema")
        return db_project

async def invalidate_project_cache(project_id: str, user_id: int):
    """Helper to invalidate cache for a specific project"""
    try:
        # Clear the specific project cache
        cache_key = f"specsharp-cache:get_project:{project_id}"
        await FastAPICache.clear(namespace=cache_key)
    except Exception as e:
        print(f"Cache invalidation failed: {e}")


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
        logger.info(f"Scope generation request: {scope_request.building_type}/{scope_request.building_subtype} - {scope_request.square_footage} sqft in {scope_request.location}")
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
        
        # Track generation time
        start_time = time.time()
        
        
        # Check if building type is already provided by the form
        # Also check for the legacy 'subtype' field
        if not scope_request.building_subtype and hasattr(scope_request, 'subtype'):
            scope_request.building_subtype = scope_request.subtype
            logger.error(f"📝 Using legacy 'subtype' field: {scope_request.subtype}")
        
        if scope_request.building_type and scope_request.building_type != 'commercial' and scope_request.building_subtype:
            # Form has already provided specific building type and subtype
            logger.info(f"Using form-provided types: {scope_request.building_type}/{scope_request.building_subtype}")
        elif scope_request.special_requirements:
            # Try NLP detection from description
            description = scope_request.special_requirements
            logger.info(f"Attempting NLP detection on: {description[:100]}")
            
            # Use the original building type detection
            building_type = determine_building_type(description)
            subtype = get_building_subtype(description, building_type) if building_type else None
            
            logger.info(f"NLP detected: {building_type}/{subtype}")
            
            # If detection failed completely, return an error
            if not building_type or building_type == 'other':
                # Check if form provided a fallback
                if not scope_request.building_type or scope_request.building_type == 'commercial':
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Could not determine building type",
                            "message": "Please be more specific. Try including terms like 'apartment', 'office', 'hospital', 'hotel', 'warehouse', 'school', 'restaurant', etc.",
                            "detected_type": building_type,
                            "description": description,
                            "suggestions": [
                                "Include the primary use of the building",
                                "Use specific terms like 'office building', 'apartment complex', 'medical office'",
                                "Mention if it's residential, commercial, healthcare, education, etc."
                            ]
                        }
                    )
            else:
                # Use detected values
                scope_request.building_type = building_type
                logger.info(f"[NLP] Updated building_type to: {building_type}")
                
                if subtype:
                    scope_request.building_subtype = subtype
                    logger.info(f"[NLP] Updated building_subtype to: {subtype}")
            
            # Also check for unit mix if multifamily
            if scope_request.building_type == 'multifamily':
                nlp_result = nlp_service._fallback_analysis(description)
                if nlp_result.get('unit_mix'):
                    # Store unit mix data in request for later use
                    if not hasattr(scope_request, 'unit_mix'):
                        scope_request.unit_mix = nlp_result['unit_mix']
        else:
            # No description provided - check if form provided building type
            if not scope_request.building_type or scope_request.building_type == 'commercial':
                # Default commercial type needs a subtype
                if not scope_request.building_subtype or scope_request.building_subtype == 'office':
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "Building type required",
                            "message": "Please provide a description of your project or select a specific building type.",
                            "suggestions": [
                                "Add a project description",
                                "Select a building type from the dropdown",
                                "Include details like 'office building', 'apartment complex', etc."
                            ]
                        }
                    )
            # Form has provided building type, continue with it
            logger.info(f"Using form-provided type without description: {scope_request.building_type}/{scope_request.building_subtype}")
        
        # Detect project classification from special requirements if not explicitly set
        if scope_request.special_requirements and hasattr(scope_request, 'project_classification'):
            nlp_result = nlp_service.extract_project_details(scope_request.special_requirements)
            detected_classification = nlp_result.get('project_classification')
            if detected_classification:
                from app.models.scope import ProjectClassification
                scope_request.project_classification = ProjectClassification(detected_classification)
                logger.error(f"[NLP] Detected project classification: {detected_classification}")
        
        # Auto-generate project name if not provided
        if not scope_request.project_name:
            # Use special requirements or build a description from the request data
            description = scope_request.special_requirements or f"{scope_request.square_footage} sf {scope_request.building_type} in {scope_request.location}"
            
            # Extract details for name generation
            parsed_data = {
                "building_type": scope_request.building_type,
                "building_subtype": getattr(scope_request, 'building_subtype', ''),
                "location": scope_request.location,
                "square_footage": scope_request.square_footage,
                "project_classification": getattr(scope_request, 'project_classification', 'ground_up')
            }
            
            # Generate smart project name
            generated_name = nlp_service.generate_project_name(description, parsed_data)
            scope_request.project_name = generated_name
            logger.info(f"[NLP] Auto-generated project name: {generated_name}")
        
        # Convert ScopeRequest to dict for clean engine
        clean_request = {
            "building_type": scope_request.building_type,
            "building_subtype": getattr(scope_request, 'building_subtype', scope_request.building_type),
            "square_footage": scope_request.square_footage,
            "location": scope_request.location,
            "num_floors": getattr(scope_request, 'num_floors', 1),
            "finish_level": getattr(scope_request, 'finish_level', 'standard'),
            "project_classification": getattr(scope_request, 'project_classification', 'ground_up').value if hasattr(getattr(scope_request, 'project_classification', 'ground_up'), 'value') else getattr(scope_request, 'project_classification', 'ground_up'),
            "project_description": getattr(scope_request, 'special_requirements', None),
            "project_name": getattr(scope_request, 'project_name', None),
            "features": getattr(scope_request, 'building_features', []) or []
        }
        
        # Only extract from special requirements if no features provided
        if not clean_request["features"] and hasattr(scope_request, 'special_requirements') and scope_request.special_requirements:
            # Basic feature extraction as fallback
            feature_keywords = {
                'gymnasium': ['gym', 'gymnasium', 'athletic'],
                'science_labs': ['science', 'lab', 'laboratory'],
                'cafeteria': ['cafeteria', 'dining', 'food service'],
                'auditorium': ['auditorium', 'theater', 'assembly'],
                'library': ['library', 'media center']
            }
            
            req_lower = scope_request.special_requirements.lower()
            for feature, keywords in feature_keywords.items():
                if any(keyword in req_lower for keyword in keywords):
                    clean_request["features"].append(feature)
        
        # Call clean engine
        result = calculate_scope(clean_request)
        
        # Create request_data with all necessary fields
        request_data_dict = result.get('request_data', clean_request)
        request_data_dict.update({
            'building_type': result['building_type'],
            'building_subtype': result['building_subtype'],
            'square_footage': result['square_footage'],
            'location': result['location'],
            'num_floors': result.get('num_floors', 1),
            'project_classification': result.get('project_classification', 'ground_up')
        })
        
        # Convert dict result to ScopeResponse object
        scope_response = ScopeResponse(
            project_id=result['project_id'],
            project_name=result['project_name'],
            created_at=result['created_at'],
            request_data=ScopeRequest(**request_data_dict),
            cost_per_sqft=result['cost_per_sqft'],
            subtotal=result['subtotal'],
            total_cost=result['total_cost'],
            categories=result['categories'],
            calculation_breakdown=result.get('calculation_breakdown')
        )
        
        logger.info(f"Scope response generated: {request_data_dict['building_type']}/{request_data_dict['building_subtype']} - ${scope_response.cost_per_sqft}/SF, Total: ${scope_response.total_cost:,.2f}")
        
        # Generate architectural floor plan with error handling
        try:
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.building_type,
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
                project_type=scope_request.building_type,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            scope_response.floor_plan = floor_plan_data
        
        # Clean Engine V2 already provides all trade breakdowns
        scope_dict = scope_response.model_dump()
        
        # Update scope_response for storage
        scope_response_dict = scope_response.model_dump()
        
        # Skip Cost DNA generation - clean engine handles all cost calculation
        scope_response_dict['cost_dna'] = None
        scope_response_dict['confidence_score'] = 95  # High confidence with clean engine
        
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
        project_data = {
            'project_id': scope_response.project_id,
            'name': scope_request.project_name,
            'description': scope_request.special_requirements,  # Store the original input description
            'project_type': scope_request.building_type,  # Using building_type as project_type is removed
            'project_classification': scope_request.project_classification.value,  # This is always present with default
            'building_type': scope_request.building_type,  # Store DETECTED building type
            'building_subtype': getattr(scope_request, 'building_subtype', None),  # Store DETECTED subtype
            'square_footage': scope_request.square_footage,
            'location': scope_request.location,
            'climate_zone': scope_request.climate_zone.value if scope_request.climate_zone else None,
            'num_floors': scope_request.num_floors,
            'ceiling_height': scope_request.ceiling_height,
            # Store all cost components for consistency across views
            'subtotal': scope_response.subtotal,
            'contingency_percentage': 0.0,  # No contingency for pure construction costs
            'contingency_amount': 0.0,  # No contingency for pure construction costs
            'total_cost': scope_response_dict.get('total_cost', scope_response.total_cost),
            'cost_per_sqft': scope_response.cost_per_sqft,  # ALWAYS use Clean Engine's pure construction cost
            'scope_data': json.dumps(scope_response_dict, default=str),  # Save complete data including trade summaries
            'cost_data': json.dumps(scope_response.calculation_breakdown, default=str) if hasattr(scope_response, 'calculation_breakdown') and scope_response.calculation_breakdown else None,
            'user_id': current_user.id,
            'created_by_id': current_user.id,
            'team_id': user.current_team_id  # Associate with user's current team
        }
        
        db_project = create_project_safely(db, project_data)
        
        # Validate cost consistency before saving
        try:
            validate_project_costs(db_project)
        except CostValidationError as e:
            logger.error(f"Cost validation failed for new project: {e}")
            # Continue anyway but log the issue for investigation
        
        # Log cost calculation for audit trail
        log_cost_calculation(
            project_id=db_project.project_id,
            project_name=db_project.name,
            subtotal=db_project.subtotal,
            total_cost=db_project.total_cost,
            cost_per_sqft=db_project.cost_per_sqft,
            square_footage=db_project.square_footage
        )
        
        db.add(db_project)
        
        # Increment user's estimate count
        user.estimate_count = (user.estimate_count or 0) + 1
        
        db.commit()
        db.refresh(db_project)
        
        # CRITICAL FIX: cost_per_sqft must be CONSTRUCTION COST ONLY (no GC, no contingency)
        # Override whatever was calculated and use the clean engine's pure construction cost
        
        print(f"🔧 DEBUG: Original cost_per_sqft from scope_response: ${scope_response.cost_per_sqft}")
        print(f"🔧 DEBUG: Modified cost_per_sqft in scope_response_dict: ${scope_response_dict.get('cost_per_sqft', 'MISSING')}")
        
        # Force the cost_per_sqft to be the clean engine result
        scope_response_dict['cost_per_sqft'] = scope_response.cost_per_sqft
        
        print(f"🔧 FINAL: Set cost_per_sqft to ${scope_response_dict['cost_per_sqft']}/SF")
        
        # Return the complete response with trade summaries
        return scope_response_dict
        
    except Exception as e:
        import traceback
        logger.error(f"=== SCOPE GENERATION FAILED ===")
        logger.error(f"Error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error generating scope: {str(e)}")


@router.post("/validate-description")
async def validate_description(description: str = Body(..., description="Project description to validate")):
    """Test what building type would be detected from a description"""
    building_type, subtype = detect_building_type(description)
    
    return {
        "description": description,
        "detected_type": building_type,
        "detected_subtype": subtype,
        "valid": building_type is not None,
        "suggestions": [] if building_type else [
            "Try adding building type keywords",
            "Be more specific about the use case",
            "Include terms like 'apartment', 'office', 'hospital', 'hotel', 'school', etc.",
            "Mention the primary function: residential, commercial, healthcare, education",
            "Examples: '200 unit luxury apartment complex', '50,000 sf medical office building'"
        ]
    }


@router.post("/owner-view")
async def get_owner_view(
    building_type: Optional[str] = Body(None, description="Building type (e.g., 'healthcare')"),
    subtype: Optional[str] = Body(None, description="Building subtype (e.g., 'hospital')"),
    description: Optional[str] = Body(None, description="Natural language description for NLP detection"),
    construction_cost: float = Body(..., description="Hard construction costs"),
    square_footage: float = Body(..., description="Total square footage"),
    trade_breakdown: Optional[Dict[str, float]] = Body(None, description="Optional trade cost breakdown"),
    ownership_type: Optional[str] = Body("for_profit", description="Ownership type (for_profit, non_profit, government, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Generate owner view with soft costs, department allocation, and ROI analysis
    
    Request body example:
    {
        "building_type": "healthcare",  // optional if description provided
        "subtype": "hospital",  // optional if description provided
        "description": "300 bed hospital with emergency department",  // optional, uses NLP to detect type
        "construction_cost": 100000000,
        "square_footage": 200000,
        "ownership_type": "non_profit",  // optional, defaults to "for_profit"
        "trade_breakdown": {  // optional
            "structural": 25000000,
            "mechanical": 35000000,
            "electrical": 15000000,
            "plumbing": 20000000,
            "finishes": 5000000
        }
    }
    """
    try:
        # If description is provided, use NLP detection
        if description and not (building_type and subtype):
            detected_type, detected_subtype = detect_building_type(description)
            building_type = building_type or detected_type
            subtype = subtype or detected_subtype
            logger.info(f"NLP detected building type: {building_type}/{subtype} from description: {description[:100]}")
        
        # Ensure we have building_type and subtype
        if not building_type:
            building_type = "office"  # Default fallback
        if not subtype:
            subtype = "class_b"  # Default fallback
        
        # Create orchestrator with detected or provided types
        orchestrator = OwnerViewOrchestrator(building_type, subtype)
        
        # Generate complete owner view with ownership type
        owner_view = orchestrator.get_complete_owner_view(
            construction_cost=construction_cost,
            square_footage=square_footage,
            trade_breakdown=trade_breakdown,
            ownership_type=ownership_type
        )
        
        # Log the request
        logger.info(f"Owner view generated for {building_type}/{subtype}: ${construction_cost:,.0f} for {square_footage:,.0f} SF")
        
        # Add detected types to the response
        if description:
            message = f"Owner view generated for {building_type}/{subtype} (detected from description)"
        else:
            message = f"Owner view generated for {building_type}/{subtype}"
        
        return {
            "success": True,
            "data": owner_view,
            "message": message,
            "detected_type": building_type,
            "detected_subtype": subtype
        }
        
    except Exception as e:
        logger.error(f"Error generating owner view: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate owner view: {str(e)}"
        )


@router.get("/projects/{project_id}/owner-view")
async def get_project_owner_view(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get owner view for an existing project
    """
    try:
        # Get project from database
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Parse building type and subtype from project metadata
        scope_data = json.loads(project.scope_data) if project.scope_data else {}
        
        # Extract building type and subtype
        building_type = scope_data.get('building_type', 'healthcare')
        subtype = scope_data.get('building_subtype') or scope_data.get('subtype') or 'hospital'
        
        # Get construction cost and square footage from project
        construction_cost = project.total_cost
        square_footage = project.square_footage if project.square_footage else 200000
        
        # Get trade breakdown if available from scope_data
        trade_breakdown = None
        if 'trade_costs' in scope_data:
            trade_breakdown = scope_data['trade_costs']
        elif 'breakdown' in scope_data:
            # Try to extract trade costs from breakdown
            breakdown = scope_data['breakdown']
            if isinstance(breakdown, dict):
                trade_breakdown = {}
                for key, value in breakdown.items():
                    if key.lower() in ['structural', 'mechanical', 'electrical', 'plumbing', 'finishes']:
                        trade_breakdown[key.lower()] = value.get('subtotal', 0) if isinstance(value, dict) else value
        
        # Generate owner view
        orchestrator = OwnerViewOrchestrator(building_type, subtype)
        owner_view = orchestrator.get_complete_owner_view(
            construction_cost=construction_cost,
            square_footage=square_footage,
            trade_breakdown=trade_breakdown
        )
        
        # Add project info to response
        owner_view['project_info'] = {
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'created_at': project.created_at.isoformat() if project.created_at else None
        }
        
        return {
            "success": True,
            "data": owner_view,
            "project_id": project_id,
            "message": f"Owner view generated for project {project_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting owner view for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get owner view: {str(e)}"
        )


@router.get("/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    try:
        # Log the request for debugging
        logger.info(f"Fetching projects for user: {current_user.email} (ID: {current_user.id}), skip={skip}, limit={limit}")
        
        # Validate pagination parameters
        if limit > 100:
            limit = 100  # Max limit
        if skip < 0:
            skip = 0
        
        # Get user's current team
        user = current_user  # current_user is already the User object
        
        # Base query for projects - if user has a team, get all team projects
        if user.current_team_id:
            logger.info(f"User has team_id: {user.current_team_id}, fetching team projects")
            base_query = db.query(Project).filter(
                Project.team_id == user.current_team_id
            )
            projects_query = db.query(Project, User.full_name.label('creator_name')).join(
                User, Project.created_by_id == User.id, isouter=True
            ).filter(
                Project.team_id == user.current_team_id
            )
        else:
            # Fallback to user's personal projects
            logger.info(f"User has no team, fetching personal projects for user_id: {current_user.id}")
            base_query = db.query(Project).filter(
                Project.user_id == current_user.id
            )
            projects_query = db.query(Project, User.full_name.label('creator_name')).join(
                User, Project.created_by_id == User.id, isouter=True
            ).filter(
                Project.user_id == current_user.id
            )
        
        # Get total count
        total = base_query.count()
        logger.info(f"Found {total} total projects for user {current_user.email}")
        
        # Get paginated projects ordered by created_at descending
        projects = projects_query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
        
        items = [
            {
                "id": p.Project.id,
                "project_id": p.Project.project_id,
                "name": p.Project.name,
                "project_type": p.Project.project_type,
                "project_classification": getattr(p.Project, 'project_classification', 'ground_up'),  # Handle missing column
                "building_type": p.Project.building_type,
                "occupancy_type": p.Project.occupancy_type,
                "description": p.Project.description,
                "square_footage": p.Project.square_footage,
                "location": p.Project.location,
                # Include all cost components for consistency
                "subtotal": p.Project.subtotal,
                "contingency_percentage": p.Project.contingency_percentage,
                "contingency_amount": p.Project.contingency_amount,
                "total_cost": p.Project.total_cost,
                "cost_per_sqft": p.Project.cost_per_sqft,
                "created_at": p.Project.created_at,
                "created_by": p.creator_name or "Unknown",
                "scope_data": json.loads(p.Project.scope_data) if p.Project.scope_data else {}
            }
            for p in projects
        ]
    
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error fetching projects for user {current_user.email}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return empty list instead of error to prevent frontend crash
        return {
            "items": [],
            "total": 0,
            "skip": skip,
            "limit": limit,
            "error": str(e)  # Include error for debugging
        }


@router.get("/projects/search")
async def search_projects(
    q: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Search projects by name or description"""
    # Validate pagination parameters
    if limit > 100:
        limit = 100  # Max limit
    if skip < 0:
        skip = 0
    
    # Get user's current team
    user = current_user
    
    # Base query for search
    search_term = f"%{q}%"
    if user.current_team_id:
        base_query = db.query(Project).filter(
            Project.team_id == user.current_team_id,
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.location.ilike(search_term)
            )
        )
        projects_query = db.query(Project, User.full_name.label('creator_name')).join(
            User, Project.created_by_id == User.id, isouter=True
        ).filter(
            Project.team_id == user.current_team_id,
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.location.ilike(search_term)
            )
        )
    else:
        base_query = db.query(Project).filter(
            Project.user_id == current_user.id,
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.location.ilike(search_term)
            )
        )
        projects_query = db.query(Project, User.full_name.label('creator_name')).join(
            User, Project.created_by_id == User.id, isouter=True
        ).filter(
            Project.user_id == current_user.id,
            or_(
                Project.name.ilike(search_term),
                Project.description.ilike(search_term),
                Project.location.ilike(search_term)
            )
        )
    
    # Get total count
    total = base_query.count()
    
    # Get paginated results ordered by created_at descending
    projects = projects_query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()
    
    items = [
        {
            "id": p.Project.id,
            "project_id": p.Project.project_id,
            "name": p.Project.name,
            "project_type": p.Project.project_type,
            "project_classification": p.Project.project_classification,  # Add this field
            "building_type": p.Project.building_type,
            "occupancy_type": p.Project.occupancy_type,
            "description": p.Project.description,
            "square_footage": p.Project.square_footage,
            "location": p.Project.location,
            # Include all cost components for consistency
            "subtotal": p.Project.subtotal,
            "contingency_percentage": p.Project.contingency_percentage,
            "contingency_amount": p.Project.contingency_amount,
            "total_cost": p.Project.total_cost,
            "cost_per_sqft": p.Project.cost_per_sqft,
            "created_at": p.Project.created_at,
            "created_by": p.creator_name or "Unknown",
            "scope_data": json.loads(p.Project.scope_data) if p.Project.scope_data else {}
        }
        for p in projects
    ]
    
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "query": q
    }


@router.get("/projects/{project_id}", response_model=ScopeResponse)
@cache(expire=300)  # Cache for 5 minutes
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    # Debug logging for authentication issues
    logger.info(f"get_project called: project_id={project_id}, user={current_user.email}, user_id={current_user.id}")
    
    # Get ALL columns including cost components for consistency
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    # DEVELOPMENT WORKAROUND: If project not found with user filter, try without it
    # This allows testing with projects created by different users
    if not project:
        import os
        if os.getenv("ENVIRONMENT", "development") == "development":
            logger.warning(f"Project {project_id} not found for user {current_user.id}, trying without user filter (DEV MODE)")
            project = db.query(Project).filter(Project.project_id == project_id).first()
            if project:
                logger.warning(f"Found project {project_id} owned by user_id={project.user_id} (DEV MODE OVERRIDE)")
        
        if not project:
            logger.error(f"Project {project_id} not found at all")
            raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse stored scope data efficiently
    scope_data = json.loads(project.scope_data)
    
    # Detect any discrepancies between stored JSON and database values
    if 'total_cost' in scope_data:
        discrepancy = detect_cost_discrepancy(
            stored_total=project.total_cost,
            calculated_total=scope_data.get('total_cost', 0),
            project_id=project.project_id,
            project_name=project.name
        )
        if discrepancy:
            logger.warning(f"Correcting cost discrepancy of ${discrepancy:.2f} for project {project.project_id}")
    
    # CRITICAL: Override scope data with database values to ensure consistency
    # These values are the source of truth and MUST match what's shown in dashboard
    scope_data['subtotal'] = project.subtotal if project.subtotal is not None else scope_data.get('subtotal', 0)
    scope_data['contingency_percentage'] = project.contingency_percentage if project.contingency_percentage is not None else scope_data.get('contingency_percentage', 10)
    scope_data['contingency_amount'] = project.contingency_amount if project.contingency_amount is not None else scope_data.get('contingency_amount', 0)
    scope_data['total_cost'] = project.total_cost
    scope_data['cost_per_sqft'] = project.cost_per_sqft
    
    # Add top-level building info for frontend display
    scope_data['building_type'] = project.building_type if hasattr(project, 'building_type') else scope_data.get('request_data', {}).get('building_type')
    scope_data['building_subtype'] = scope_data.get('request_data', {}).get('building_subtype')
    scope_data['square_footage'] = project.square_footage
    
    # Add calculation breakdown if stored in database
    if hasattr(project, 'cost_data') and project.cost_data:
        try:
            scope_data['calculation_breakdown'] = json.loads(project.cost_data)
        except (json.JSONDecodeError, TypeError):
            logger.warning(f"Could not parse cost_data for project {project.project_id}")
    
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
    
    # Clean Engine V2 already provides all trade breakdowns
    
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
    
    # Invalidate cache
    await invalidate_project_cache(project_id, current_user.id)
    
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
    
    # Convert to clean engine format
    clean_request = {
        "building_type": scope_request.building_type,
        "building_subtype": getattr(scope_request, 'building_subtype', scope_request.building_type),
        "square_footage": scope_request.square_footage,
        "location": scope_request.location,
        "num_floors": getattr(scope_request, 'num_floors', 1),
        "finish_level": getattr(scope_request, 'finish_level', 'standard'),
        "project_classification": getattr(scope_request, 'project_classification', 'ground_up').value if hasattr(getattr(scope_request, 'project_classification', 'ground_up'), 'value') else getattr(scope_request, 'project_classification', 'ground_up'),
        "project_name": getattr(scope_request, 'project_name', None),
        "features": getattr(scope_request, 'building_features', []) or []
    }
    
    result = calculate_scope(clean_request)
    
    new_scope_response = ScopeResponse(
        project_id=result['project_id'],
        project_name=result['project_name'],
        created_at=result['created_at'],
        building_type=result['building_type'],
        building_subtype=result['building_subtype'],
        square_footage=result['square_footage'],
        location=result['location'],
        num_floors=result.get('num_floors', 1),
        cost_per_sqft=result['cost_per_sqft'],
        subtotal=result['subtotal'],
        contingency_percentage=result['contingency_percentage'],
        contingency_amount=result['contingency_amount'],
        total_cost=result['total_cost'],
        categories=result['categories'],
        request_data=result.get('request_data', clean_request)
    )
    
    # Generate floor plan
    if 'floor_plan' not in scope_data or not scope_data.get('floor_plan'):
        try:
            floor_plan_data = architectural_floor_plan_service.generate_architectural_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.building_type,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            new_scope_response.floor_plan = floor_plan_data
        except Exception as e:
            floor_plan_data = floor_plan_service.generate_floor_plan(
                square_footage=scope_request.square_footage,
                project_type=scope_request.building_type,
                building_mix=getattr(scope_request, 'building_mix', None)
            )
            new_scope_response.floor_plan = floor_plan_data
    else:
        new_scope_response.floor_plan = scope_data['floor_plan']
    
    # Clean Engine V2 already provides all trade breakdowns
    
    # Update the project in database
    project.scope_data = new_scope_response.model_dump_json()
    db.commit()
    
    # Invalidate cache
    await invalidate_project_cache(project_id, current_user.id)
    
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
    
    # Create the duplicate using safe method
    duplicate_data = {
        'project_id': new_project_id,
        'name': duplicate_name or f"{original_project.name} (Copy)",
        'description': getattr(original_project, 'description', None),
        'project_type': original_project.project_type,
        'building_type': getattr(original_project, 'building_type', None),
        'occupancy_type': getattr(original_project, 'occupancy_type', None),
        'square_footage': original_project.square_footage,
        'location': original_project.location,
        'climate_zone': original_project.climate_zone,
        'num_floors': original_project.num_floors,
        'ceiling_height': original_project.ceiling_height,
        # Copy all cost components
        'subtotal': getattr(original_project, 'subtotal', None),
        'contingency_percentage': getattr(original_project, 'contingency_percentage', 10.0),
        'contingency_amount': getattr(original_project, 'contingency_amount', None),
        'total_cost': original_project.total_cost,
        'cost_per_sqft': getattr(original_project, 'cost_per_sqft', None),
        'scope_data': original_project.scope_data,
        'cost_data': getattr(original_project, 'cost_data', None),
        'user_id': current_user.id,
        'created_by_id': current_user.id,
        'team_id': getattr(current_user, 'current_team_id', None)
    }
    
    duplicate = create_project_safely(db, duplicate_data)
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    # Return the new project data
    scope_data = json.loads(duplicate.scope_data)
    # Update the project_id in the response
    scope_data['project_id'] = new_project_id
    scope_data['project_name'] = duplicate.name
    
    return scope_data


# Debug endpoint removed - electrical services have been migrated to Clean Engine V2
# @router.get("/debug/electrical/{project_id}")
# async def debug_electrical(
#     project_id: str,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user_with_cookie)
# ):
#     """Debug endpoint to verify electrical calculations"""
#     from app.services.electrical_standards_service import electrical_standards_service
#     from app.services.electrical_v2_service import electrical_v2_service
#     
#     # Get project
#     project = await get_project(project_id, db, current_user)
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
#     
#     # Convert to dict
#     if hasattr(project, 'model_dump'):
#         project_dict = project.model_dump()
#     else:
#         project_dict = dict(project)
#     
#     # Extract key data
#     request_data = project_dict.get('request_data', {})
#     cost_breakdown = project_dict.get('cost_breakdown', {})
#     if isinstance(cost_breakdown, str):
#         try:
#             cost_breakdown = json.loads(cost_breakdown)
#         except:
#             cost_breakdown = {}
#     
#     # Run V2 calculation directly
#     v2_result = electrical_v2_service.calculate_electrical_cost(project_dict)
#     
#     # Get stored electrical cost
#     stored_electrical = cost_breakdown.get('electrical', {}).get('total', 0)
#     
#     return {
#         "project_id": project_id,
#         "building_type": request_data.get('building_type', 'Unknown'),
#         "state": request_data.get('state', project_dict.get('state', 'Unknown')),
#         "location": project_dict.get('location', 'Unknown'),
#         "square_footage": request_data.get('square_footage', 0),
#         "building_mix": request_data.get('building_mix', {}),
#         "stored_electrical_cost": stored_electrical,
#         "v2_calculation": {
#             "total_cost": v2_result.get('total', 0),
#             "base_cost": v2_result.get('subtotal', 0),
#             "regional_multiplier": v2_result.get('regional_multiplier', 1.0),
#             "cost_per_sf": v2_result.get('cost_per_sf', 0),
#             "regional_tier": v2_result.get('regional_tier', 'Unknown')
#         },
#         "expected_range": {
#             "min": 700000,
#             "max": 850000,
#             "note": "For 45k SF mixed-use in CA"
#         }
#     }


@router.get("/debug/user-projects")
async def debug_user_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Debug endpoint to check user's projects and authentication state"""
    try:
        # Log the request
        logger.info(f"Debug endpoint called by user: {current_user.email} (ID: {current_user.id})")
        
        # Get all projects for this user
        user_projects = db.query(Project).filter(
            Project.user_id == current_user.id
        ).all()
        
        # Get projects if user has a team
        team_projects = []
        if current_user.current_team_id:
            team_projects = db.query(Project).filter(
                Project.team_id == current_user.current_team_id
            ).all()
        
        # Get total count in database
        total_projects = db.query(Project).count()
        
        return {
            "debug_info": {
                "user": {
                    "id": current_user.id,
                    "email": current_user.email,
                    "oauth_provider": current_user.oauth_provider,
                    "current_team_id": current_user.current_team_id,
                    "created_at": str(current_user.created_at)
                },
                "projects": {
                    "user_projects_count": len(user_projects),
                    "team_projects_count": len(team_projects),
                    "total_in_database": total_projects,
                    "user_project_ids": [p.project_id for p in user_projects[:10]],  # First 10
                    "user_project_names": [p.name for p in user_projects[:10]]
                },
                "authentication": {
                    "authenticated": True,
                    "method": "OAuth" if current_user.oauth_provider else "Standard"
                }
            },
            "projects_list": [
                {
                    "project_id": p.project_id,
                    "name": p.name,
                    "created_at": str(p.created_at),
                    "user_id": p.user_id,
                    "team_id": p.team_id
                } for p in user_projects[:20]  # Return first 20 for inspection
            ]
        }
    except Exception as e:
        logger.error(f"Debug endpoint error: {str(e)}")
        return {
            "error": str(e),
            "user_email": getattr(current_user, 'email', 'Unknown'),
            "authenticated": False
        }