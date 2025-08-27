"""
Clean API endpoint that uses the new system
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.phrase_parser import phrase_parser
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    MASTER_CONFIG
)
from app.core.building_taxonomy import normalize_building_type, validate_building_type
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["v2"])

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request for natural language analysis"""
    description: str = Field(..., description="Natural language project description")
    default_location: Optional[str] = Field("Nashville", description="Default location if not detected")
    default_square_footage: Optional[int] = Field(None, description="Default square footage if not detected")

class CalculateRequest(BaseModel):
    """Request for direct calculation"""
    building_type: str = Field(..., description="Building type (e.g., 'healthcare', 'office')")
    subtype: str = Field(..., description="Building subtype (e.g., 'hospital', 'class_a')")
    square_footage: float = Field(..., gt=0, description="Total square footage")
    location: str = Field("Nashville", description="Project location for regional multiplier")
    project_class: Optional[str] = Field("ground_up", description="Project class")
    floors: Optional[int] = Field(1, ge=1, description="Number of floors")
    ownership_type: Optional[str] = Field("for_profit", description="Ownership type")
    special_features: Optional[List[str]] = Field([], description="Special features to include")

class CompareRequest(BaseModel):
    """Request for scenario comparison"""
    scenarios: List[Dict[str, Any]] = Field(..., description="List of scenarios to compare")

class ProjectResponse(BaseModel):
    """Standard project response"""
    success: bool
    data: Dict[str, Any]
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/analyze", response_model=ProjectResponse)
async def analyze_project(request: AnalyzeRequest):
    """
    Single endpoint that does everything from natural language
    No more confusion about which endpoint to use
    
    Example:
        "Build a 50,000 sf hospital with emergency department in Nashville"
    """
    try:
        # Parse the description using phrase-first parser
        parsed = phrase_parser.parse(request.description)
        
        # Normalize building type using taxonomy
        if parsed.get('building_type'):
            original_type = parsed['building_type']
            canonical_type, canonical_subtype = validate_building_type(
                parsed['building_type'],
                parsed.get('subtype')
            )
            parsed['building_type'] = canonical_type
            if canonical_subtype:
                parsed['subtype'] = canonical_subtype
            
            if original_type != canonical_type:
                logger.info(f"Normalized building type from '{original_type}' to '{canonical_type}'")
        
        # Apply defaults if needed
        if not parsed.get('square_footage') and request.default_square_footage:
            parsed['square_footage'] = request.default_square_footage
        if not parsed.get('location'):
            parsed['location'] = request.default_location
            
        # Validate we have minimum required data
        if not parsed.get('square_footage'):
            return ProjectResponse(
                success=False,
                data={},
                errors=["Could not determine square footage from description"]
            )
        
        # Convert string values to enums
        building_type = BuildingType(parsed['building_type'])
        project_class = ProjectClass(parsed.get('project_class', 'ground_up'))
        ownership_type = OwnershipType(parsed.get('ownership_type', 'for_profit'))
        
        # Calculate everything
        result = unified_engine.calculate_project(
            building_type=building_type,
            subtype=parsed['subtype'],
            square_footage=parsed['square_footage'],
            location=parsed['location'],
            project_class=project_class,
            floors=parsed.get('floors', 1),
            ownership_type=ownership_type,
            special_features=parsed.get('special_features', [])
        )
        
        # Add building_subtype for frontend compatibility
        parsed_with_compat = parsed.copy()
        parsed_with_compat['building_subtype'] = parsed.get('subtype')
        
        # Return comprehensive result
        return ProjectResponse(
            success=True,
            data={
                'parsed_input': parsed_with_compat,
                'calculations': result,
                'confidence': parsed.get('confidence', 0),
                'debug': {
                    'engine_version': 'unified_v2',
                    'config_version': '2.0',
                    'trace_count': len(result.get('calculation_trace', []))
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error in analyze_project: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.post("/calculate", response_model=ProjectResponse)
async def calculate_project(request: CalculateRequest):
    """
    Direct calculation endpoint when you know exactly what you want
    
    Example:
        {
            "building_type": "healthcare",
            "subtype": "hospital",
            "square_footage": 100000,
            "location": "Nashville",
            "project_class": "ground_up",
            "floors": 5,
            "ownership_type": "non_profit",
            "special_features": ["emergency_department", "surgical_suite"]
        }
    """
    try:
        # Convert string values to enums
        building_type = BuildingType(request.building_type)
        project_class = ProjectClass(request.project_class)
        ownership_type = OwnershipType(request.ownership_type)
        
        # Calculate
        result = unified_engine.calculate_project(
            building_type=building_type,
            subtype=request.subtype,
            square_footage=request.square_footage,
            location=request.location,
            project_class=project_class,
            floors=request.floors,
            ownership_type=ownership_type,
            special_features=request.special_features
        )
        
        return ProjectResponse(
            success=True,
            data=result
        )
        
    except ValueError as e:
        return ProjectResponse(
            success=False,
            data={},
            errors=[f"Invalid input: {str(e)}"]
        )
    except Exception as e:
        logger.error(f"Error in calculate_project: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.post("/compare", response_model=ProjectResponse)
async def compare_scenarios(request: CompareRequest):
    """
    Compare multiple project scenarios
    
    Example:
        {
            "scenarios": [
                {
                    "name": "Option A",
                    "building_type": "office",
                    "subtype": "class_a",
                    "square_footage": 50000,
                    "location": "Nashville"
                },
                {
                    "name": "Option B",
                    "building_type": "office",
                    "subtype": "class_b",
                    "square_footage": 60000,
                    "location": "Nashville"
                }
            ]
        }
    """
    try:
        result = unified_engine.calculate_comparison(request.scenarios)
        
        return ProjectResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        logger.error(f"Error in compare_scenarios: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.get("/building-types", response_model=ProjectResponse)
async def get_building_types():
    """
    Get all available building types and their subtypes
    """
    try:
        available = unified_engine.get_available_building_types()
        
        # Add display names and base costs
        enhanced = {}
        for building_type_str, subtypes in available.items():
            building_type = BuildingType(building_type_str)
            enhanced[building_type_str] = {
                'subtypes': {}
            }
            for subtype in subtypes:
                if building_type in MASTER_CONFIG:
                    config = MASTER_CONFIG[building_type].get(subtype)
                    if config:
                        enhanced[building_type_str]['subtypes'][subtype] = {
                            'display_name': config.display_name,
                            'base_cost_per_sf': config.base_cost_per_sf,
                            'cost_range': config.cost_range
                        }
        
        return ProjectResponse(
            success=True,
            data=enhanced
        )
        
    except Exception as e:
        logger.error(f"Error in get_building_types: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.get("/building-details/{building_type}/{subtype}", response_model=ProjectResponse)
async def get_building_details(building_type: str, subtype: str):
    """
    Get detailed configuration for a specific building type/subtype
    """
    try:
        building_type_enum = BuildingType(building_type)
        details = unified_engine.get_building_details(building_type_enum, subtype)
        
        if not details:
            return ProjectResponse(
                success=False,
                data={},
                errors=[f"Building type {building_type}/{subtype} not found"]
            )
        
        return ProjectResponse(
            success=True,
            data=details
        )
        
    except ValueError as e:
        return ProjectResponse(
            success=False,
            data={},
            errors=[f"Invalid building type: {str(e)}"]
        )
    except Exception as e:
        logger.error(f"Error in get_building_details: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.get("/health", response_model=ProjectResponse)
async def health_check():
    """
    Health check endpoint for V2 API
    """
    try:
        # Check that we can access the config
        building_count = len(MASTER_CONFIG)
        subtype_count = sum(len(subtypes) for subtypes in MASTER_CONFIG.values())
        
        return ProjectResponse(
            success=True,
            data={
                'status': 'healthy',
                'version': '2.0',
                'engine': 'unified',
                'building_types': building_count,
                'total_subtypes': subtype_count,
                'features': [
                    'Natural language parsing',
                    'Direct calculation',
                    'Scenario comparison',
                    'Full traceability',
                    'Ownership analysis'
                ]
            }
        )
        
    except Exception as e:
        return ProjectResponse(
            success=False,
            data={'status': 'unhealthy'},
            errors=[str(e)]
        )

@router.get("/test-nlp")
async def test_nlp(
    text: str = Query(..., description="Text to parse")
):
    """
    Test endpoint for phrase parsing (useful for debugging)
    """
    try:
        result = phrase_parser.parse(text)
        
        return ProjectResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )