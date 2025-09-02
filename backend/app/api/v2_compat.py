"""V2 API Compatibility Layer

This module provides compatibility endpoints for the V2 API that was removed.
It redirects V2 API calls to the appropriate V1 endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.db.database import get_db
from app.models.auth import User
from app.api.endpoints.auth import get_current_user_with_cookie
from app.api.endpoints.scope import generate_scope
from app.models.scope import ScopeRequest
from app.services.nlp_service import NLPService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["v2-compat"])

@router.post("/analyze")
async def analyze_compatibility(
    request: Request,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """
    V2 compatibility endpoint for /api/v2/analyze
    Translates V2 analyze requests to V1 scope generation
    """
    try:
        description = body.get("description", "")
        logger.info(f"V2 Compat: Analyzing description: {description[:100]}...")
        
        # Use NLP service to parse the description
        nlp_service = NLPService()
        parsed = nlp_service.parse_description(description)
        
        # Create a ScopeRequest from the parsed data
        scope_request = ScopeRequest(
            project_name=parsed.get("project_name", "New Project"),
            square_footage=parsed.get("square_footage", 10000),
            location=parsed.get("location", "Unknown"),
            building_type=parsed.get("building_type", "office"),
            building_subtype=parsed.get("building_subtype", "office"),
            project_classification=parsed.get("project_classification", "ground_up"),
            num_floors=parsed.get("num_floors", 1),
            ceiling_height=parsed.get("ceiling_height", 10),
            finish_level=parsed.get("finish_level", "standard"),
            special_requirements=parsed.get("special_requirements", ""),
            building_features=parsed.get("features", [])
        )
        
        # Call the V1 scope generation
        scope_response = await generate_scope(
            request=request,
            scope_request=scope_request,
            db=db,
            current_user=current_user
        )
        
        # Transform response to V2 format
        v2_response = {
            "success": True,
            "parsed_input": {
                "building_type": scope_response.request_data.get("building_type"),
                "building_subtype": scope_response.request_data.get("building_subtype"),
                "square_footage": scope_response.request_data.get("square_footage"),
                "location": scope_response.request_data.get("location"),
                "project_classification": scope_response.request_data.get("project_classification"),
                "features": scope_response.request_data.get("building_features", []),
                "original_text": description
            },
            "validation": {
                "is_valid": True,
                "messages": [],
                "confidence": 0.95
            },
            "project_id": scope_response.project_id,
            "cost_estimate": {
                "total": scope_response.total_cost,
                "per_sqft": scope_response.cost_per_sqft,
                "breakdown": scope_response.categories
            }
        }
        
        return v2_response
        
    except Exception as e:
        logger.error(f"V2 Compat analyze error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculate")
async def calculate_compatibility(
    request: Request,
    body: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """
    V2 compatibility endpoint for /api/v2/calculate
    Translates V2 calculate requests to V1 scope generation
    """
    try:
        # Extract parameters from V2 format
        building_type = body.get("building_type", "office")
        subtype = body.get("subtype", building_type)
        square_footage = body.get("square_footage", 10000)
        location = body.get("location", "Unknown")
        features = body.get("features", [])
        
        # Create a ScopeRequest
        scope_request = ScopeRequest(
            project_name=f"{building_type} Project",
            square_footage=square_footage,
            location=location,
            building_type=building_type,
            building_subtype=subtype,
            project_classification="ground_up",
            num_floors=1,
            ceiling_height=10,
            finish_level="standard",
            building_features=features
        )
        
        # Call the V1 scope generation
        scope_response = await generate_scope(
            request=request,
            scope_request=scope_request,
            db=db,
            current_user=current_user
        )
        
        # Transform to V2 format
        return {
            "success": True,
            "project_id": scope_response.project_id,
            "cost": {
                "total": scope_response.total_cost,
                "per_sqft": scope_response.cost_per_sqft,
                "categories": scope_response.categories
            }
        }
        
    except Exception as e:
        logger.error(f"V2 Compat calculate error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))