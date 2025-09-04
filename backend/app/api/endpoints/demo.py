"""
Demo endpoints for unauthenticated trial experience
"""
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.database import get_db
from app.db.models import User, Project
from app.services.nlp_service import nlp_service
from app.services.climate_service import climate_service
from app.services.clean_engine_v2 import calculate_scope
from app.models.scope import ScopeRequest
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Store demo projects temporarily (in production, use Redis or similar)
demo_sessions = {}

# Maximum number of free demo estimates
MAX_DEMO_ESTIMATES = 3

@router.post("/generate")
@limiter.limit("10/minute")
async def generate_demo_scope(
    request: Request,
    response: Response,
    scope_request: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a demo scope without authentication"""
    
    # Get or create session ID
    session_id = request.cookies.get("demo_session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        # Initialize new session
        demo_sessions[session_id] = {
            "count": 0,
            "projects": [],
            "created_at": datetime.utcnow()
        }
    elif session_id not in demo_sessions:
        # Session exists but not in memory (server restart)
        demo_sessions[session_id] = {
            "count": 0,
            "projects": [],
            "created_at": datetime.utcnow()
        }
    
    # Check demo limit
    session_data = demo_sessions[session_id]
    if session_data["count"] >= MAX_DEMO_ESTIMATES:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "demo_limit_reached",
                "message": "You've used all 3 free estimates. Please sign up to continue.",
                "estimates_used": session_data["count"],
                "limit": MAX_DEMO_ESTIMATES
            }
        )
    
    try:
        # Parse the description
        description = scope_request.get("description", "")
        if not description:
            raise HTTPException(status_code=400, detail="Description is required")
        
        # Use NLP service to extract project details
        extracted_data = nlp_service.extract_project_details(description)
        print(f"[DEMO] Extracted data: {extracted_data}")
        print(f"[DEMO] Location from NLP: '{extracted_data.get('location', 'NOT FOUND')}'")
        
        # Extract building type - fallback analysis already includes it
        building_type = extracted_data.get("building_type", "commercial")
        
        # Just use building_type directly (occupancy_type was redundant)
        
        # Ensure we have required fields
        if not extracted_data.get("square_footage"):
            extracted_data["square_footage"] = 4000  # Default for demo
        if not extracted_data.get("num_floors"):
            extracted_data["num_floors"] = 1
        if not extracted_data.get("location"):
            extracted_data["location"] = "Dallas, Texas"
        
        # Determine climate zone based on location
        climate_zone = climate_service.determine_climate_zone(extracted_data["location"])
        
        # Check if it's mixed-use based on building_mix
        building_type = "commercial"
        if extracted_data.get("building_mix"):
            building_type = "mixed_use"
        
        # Create scope request
        print(f"[DEMO] Creating scope request with location: '{extracted_data['location']}'")
        scope_req = ScopeRequest(
            project_name=f"Demo: {building_type.replace('_', ' ').title()} in {extracted_data['location']}",
            building_type=building_type,
            square_footage=extracted_data["square_footage"],
            num_floors=extracted_data["num_floors"],
            # occupancy_type removed (was redundant with building_type)
            location=extracted_data["location"],
            climate_zone=climate_zone,
            special_requirements=description,
            building_mix=extracted_data.get("building_mix", None)
        )
        print(f"[DEMO] Scope request location: '{scope_req.location}'")
        
        # Generate scope using the engine
        # Convert to dict for clean_engine_v2
        request_dict = {
            'building_type': scope_req.building_type,
            'building_subtype': scope_req.building_subtype or scope_req.building_type,
            'square_footage': scope_req.square_footage,
            'location': scope_req.location,
            'num_floors': scope_req.num_floors or 1,
            'features': scope_req.building_features or [],
            'finish_level': getattr(scope_req, 'finish_level', 'standard'),
            'project_classification': str(getattr(scope_req, 'project_classification', 'ground_up')),
            'project_name': scope_req.project_name or demo['name']
        }
        
        # Calculate scope using clean_engine_v2
        calc_result = calculate_scope(request_dict)
        
        # Create a response object matching the expected format
        from app.models.scope import ScopeResponse, ScopeCategory, BuildingSystem
        from datetime import datetime
        
        categories = []
        for cat_data in calc_result.get('categories', []):
            systems = []
            for sys_data in cat_data.get('systems', []):
                systems.append(BuildingSystem(
                    name=sys_data['name'],
                    quantity=sys_data['quantity'],
                    unit=sys_data['unit'],
                    unit_cost=sys_data['unit_cost'],
                    total_cost=sys_data['total_cost'],
                    confidence_score=95,
                    confidence_label="High"
                ))
            categories.append(ScopeCategory(
                name=cat_data['name'],
                systems=systems
            ))
        
        scope_response = ScopeResponse(
            project_id=calc_result.get('project_id'),
            project_name=calc_result.get('project_name'),
            created_at=datetime.utcnow(),
            request_data=scope_req,
            categories=categories,
            contingency_percentage=calc_result.get('contingency_percentage', 10)
        )
        scope_data = scope_response.model_dump()
        print(f"[DEMO] Scope response location: '{scope_response.request_data.location}'")
        
        # Note: Demo shows base costs without contractor markup
        # Logged-in users see costs with their configured overhead & profit margins
        
        # Create demo project ID
        demo_project_id = f"demo_{session_id}_{uuid.uuid4().hex[:8]}"
        
        # Increment demo count
        session_data["count"] += 1
        
        # Store project data
        print(f"[DEMO] About to store project with location: '{extracted_data['location']}'")
        project_data = {
            "project_id": demo_project_id,
            "project_name": f"Demo: {building_type.replace('_', ' ').title()} in {extracted_data['location']}",
            "description": description,
            "square_footage": extracted_data["square_footage"],
            "num_floors": extracted_data["num_floors"],
            "location": extracted_data["location"],
            "building_type": building_type,
            "total_cost": scope_data["total_cost"],
            "cost_per_sqft": scope_data["cost_per_sqft"],
            "categories": scope_data["categories"],
            "is_demo": True,
            "created_at": datetime.utcnow().isoformat(),
            # Add note about markup
            "note": "Demo shows base construction costs. Create an account to add your overhead & profit margins."
        }
        print(f"[DEMO] Final project_data location: '{project_data['location']}'")
        
        # Add to projects list
        session_data["projects"].append(project_data)
        
        # Set session cookie
        response.set_cookie(
            key="demo_session_id",
            value=session_id,
            max_age=3600,  # 1 hour
            httponly=True,
            samesite="lax"
        )
        
        # Return the demo project data with estimate count
        return {
            **project_data,
            "estimates_used": session_data["count"],
            "estimates_remaining": MAX_DEMO_ESTIMATES - session_data["count"],
            "limit": MAX_DEMO_ESTIMATES
        }
        
    except Exception as e:
        import traceback
        print(f"Demo generation error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate demo scope: {str(e)}"
        )

@router.post("/quick-signup")
@limiter.limit("5/minute")
async def quick_signup(
    signup_data: Dict[str, Any],
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Quick signup from demo page"""
    
    from app.api.endpoints.auth import create_access_token, get_password_hash
    
    email = signup_data.get("email")
    password = signup_data.get("password")
    demo_project_id = signup_data.get("demo_project_id")
    
    if not email or not password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please login instead."
            )
        
        # Create new user
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=email.split("@")[0],  # Use email prefix as name
            is_active=True,
            estimate_count=0
        )
        db.add(user)
        db.flush()  # Flush to get user ID
        
        # Convert demo projects to real projects if exists
        session_id = request.cookies.get("demo_session_id")
        if session_id and session_id in demo_sessions:
            session_data = demo_sessions[session_id]
            
            # Convert all demo projects to real projects
            for demo_data in session_data["projects"]:
                project = Project(
                    name=demo_data["project_name"].replace("Demo: ", ""),
                    user_id=user.id,
                    square_footage=demo_data["square_footage"],
                    num_floors=demo_data["num_floors"],
                    building_type=demo_data["building_type"],
                    location=demo_data["location"],
                    project_data={
                        "request_data": {
                            "description": demo_data["description"],
                            "square_footage": demo_data["square_footage"],
                            "num_floors": demo_data["num_floors"],
                            "building_type": demo_data["building_type"],
                            "location": demo_data["location"]
                        },
                        **demo_data
                    },
                    created_at=datetime.utcnow()
                )
                db.add(project)
            
            # Set user's estimate count to match demo count
            user.estimate_count = session_data["count"]
            
            # Clean up demo session
            del demo_sessions[session_id]
        
        db.commit()
        
        # Create access token
        from datetime import timedelta
        from app.core.config import settings
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, 
            expires_delta=access_token_expires
        )
        
        # Set httpOnly cookie with the token
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Set to True in production with HTTPS
            samesite="lax",
            max_age=access_token_expires.total_seconds()
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "estimate_count": user.estimate_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Quick signup error: {str(e)}")
        print(traceback.format_exc())
        db.rollback()
        if "already exists" in str(e):
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists. Please login instead."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create account: {str(e)}"
        )

