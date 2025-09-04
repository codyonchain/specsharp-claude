"""
Clean API endpoint that uses the new system
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Header
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.v2.engines.unified_engine import unified_engine
from app.v2.services.phrase_parser import phrase_parser
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    MASTER_CONFIG
)
from app.core.building_taxonomy import normalize_building_type, validate_building_type
from app.db.models import Project
from app.db.database import get_db
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
        # Wrap the flattened result as 'calculations' to match frontend expectations
        return ProjectResponse(
            success=True,
            data={
                'parsed_input': parsed_with_compat,
                'calculations': result,  # Now properly structured without double nesting
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

# ============================================================================
# CRUD OPERATIONS - Complete V2 API
# ============================================================================

@router.get("/scope/projects")
async def get_all_projects(
    user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Get all projects for a user"""
    projects = db.query(Project).filter(
        Project.user_id == user_id
    ).order_by(Project.created_at.desc()).all()
    
    return ProjectResponse(
        success=True,
        data=[format_project_response(p) for p in projects]
    )

@router.get("/scope/projects/{project_id}")
async def get_single_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"]
        )
    
    return ProjectResponse(
        success=True,
        data=format_project_response(project)
    )

@router.delete("/scope/projects/{project_id}")
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"]
        )
    
    db.delete(project)
    db.commit()
    
    return ProjectResponse(
        success=True,
        data={"message": "Project deleted"}
    )

@router.post("/scope/generate")
async def generate_scope(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """Generate scope and save to database (V2 version of V1's generate)"""
    try:
        # Parse the description using phrase-first parser
        parsed = phrase_parser.parse(request.description)
        
        # Normalize building type using taxonomy
        if parsed.get('building_type'):
            canonical_type, canonical_subtype = validate_building_type(
                parsed['building_type'],
                parsed.get('subtype')
            )
            parsed['building_type'] = canonical_type
            if canonical_subtype:
                parsed['subtype'] = canonical_subtype
        
        # Calculate using unified engine
        result = unified_engine.calculate_project(
            building_type=BuildingType(parsed['building_type']),
            subtype=parsed['subtype'],
            square_footage=parsed['square_footage'],
            location=parsed['location'],
            project_class=ProjectClass(parsed.get('project_class', 'ground_up')),
            floors=parsed.get('floors'),
            ownership_type=OwnershipType(parsed.get('ownership_type', 'for_profit')),
            special_features=parsed.get('special_features', [])
        )
        
        # Create and save project to database
        project = Project(
            id=str(uuid.uuid4()),
            user_id=getattr(request, 'user_id', 'default-user'),
            project_name=parsed.get('suggested_project_name', 'Generated Project'),
            description=request.description,
            location=parsed['location'],
            square_footage=parsed['square_footage'],
            building_type=parsed['building_type'],
            occupancy_type=parsed['building_type'],  # V2 uses building_type as occupancy_type
            subtype=parsed.get('subtype'),
            total_cost=result['totals']['total_project_cost'],
            construction_cost=result['construction_costs']['construction_total'],
            cost_per_sqft=result['totals']['cost_per_sf'],
            calculation_data=result,  # Store full calculation
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(project)
        db.commit()
        db.refresh(project)
        
        return ProjectResponse(
            success=True,
            data=format_project_response(project)
        )
        
    except Exception as e:
        logger.error(f"Error in generate_scope: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

@router.post("/scope/owner-view")
async def get_owner_view(
    request: dict,
    db: Session = Depends(get_db)
):
    """Get owner-friendly view of project"""
    project_id = request.get('project_id')
    if not project_id:
        return ProjectResponse(
            success=False,
            data={},
            errors=["project_id required"]
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"]
        )
    
    # Use unified_engine for owner view calculations
    try:
        # Get ownership analysis from stored calculation data
        owner_data = project.calculation_data.get('ownership_analysis', {})
        
        return ProjectResponse(
            success=True,
            data={
                'project_id': project.id,
                'project_name': project.project_name,
                'total_cost': project.total_cost,
                'cost_per_sf': project.cost_per_sqft,
                'ownership_analysis': owner_data,
                'financial_metrics': owner_data.get('financial_metrics', {}),
                'revenue_requirements': owner_data.get('revenue_requirements', {})
            }
        )
        
    except Exception as e:
        logger.error(f"Error in get_owner_view: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

def format_project_response(project: Project) -> dict:
    """Format database project to match frontend expectations"""
    
    # Convert trade_breakdown to categories format that frontend expects
    calculation_data = project.calculation_data or {}
    trade_data = calculation_data.get('trade_breakdown', {})
    categories = []
    
    # Convert flat trade_breakdown to nested categories structure
    if isinstance(trade_data, dict):
        for trade_name, amount in trade_data.items():
            categories.append({
                'name': trade_name.replace('_', ' ').title(),
                'systems': [{
                    'name': trade_name.replace('_', ' ').title(),
                    'total_cost': amount,
                    'unit_cost': amount,
                    'quantity': 1
                }]
            })
    
    response = {
        # IDs and metadata - both snake_case and camelCase for compatibility
        'project_id': project.id,
        'projectId': project.id,
        'project_name': project.project_name,
        'projectName': project.project_name,
        'description': project.description,
        'location': project.location,
        'created_at': project.created_at.isoformat(),
        'createdAt': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat(),
        'updatedAt': project.updated_at.isoformat(),
        
        # Building info
        'square_footage': project.square_footage,
        'squareFootage': project.square_footage,
        'building_type': project.building_type,
        'buildingType': project.building_type,
        'occupancy_type': project.occupancy_type,
        'occupancyType': project.occupancy_type,
        'subtype': project.subtype,
        
        # Cost fields - both formats
        'total_cost': project.total_cost,
        'totalCost': project.total_cost,
        'cost_per_sqft': project.cost_per_sqft,
        'costPerSqft': project.cost_per_sqft,
        'construction_cost': project.construction_cost,
        'constructionCost': project.construction_cost,
        'subtotal': project.construction_cost,  # Frontend expects this field
        
        # Trade data in frontend-expected format
        'categories': categories,  # Primary format frontend uses
        'trade_packages': categories,  # Backup field name
        
        # Additional calculated fields
        'regional_multiplier': calculation_data.get('regional_multiplier', 1.0),
        'regionalMultiplier': calculation_data.get('regional_multiplier', 1.0),
        'is_healthcare': project.building_type == 'healthcare',
        'isHealthcare': project.building_type == 'healthcare',
        
        # Success flag
        'success': True
    }
    
    return response