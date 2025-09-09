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
from app.services.nlp_service import NLPService
nlp_service = NLPService()
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

router = APIRouter(tags=["v2"])

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
        parsed = nlp_service.extract_project_details(request.description)
        
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
            subtype=parsed.get('subtype'),  # Use .get() to handle missing subtype
            square_footage=parsed['square_footage'],
            location=parsed.get('location', 'Nashville, TN'),  # Use .get() with default
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
        result = nlp_service.extract_project_details(text)
        
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
    user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """
    Get all projects for a user. Returns empty array if no user_id provided.
    Handles missing user gracefully to prevent 500 errors.
    """
    try:
        if user_id:
            # Get projects for specific user
            projects = db.query(Project).filter(
                Project.user_id == user_id
            ).order_by(Project.created_at.desc()).all()
        else:
            # In development/testing, return recent projects if no user_id
            # In production, you might want to return empty array instead
            projects = db.query(Project).order_by(
                Project.created_at.desc()
            ).limit(20).all()
            
            # Alternative: Return empty array if no user
            # projects = []
        
        # Format each project using the improved format_project_response
        formatted_projects = []
        for p in projects:
            try:
                formatted_projects.append(format_project_response(p))
            except Exception as format_error:
                logger.error(f"Error formatting project {p.project_id}: {str(format_error)}")
                # Skip projects that can't be formatted
                continue
        return formatted_projects
        
    except Exception as e:
        logger.error(f"Error fetching projects: {str(e)}")
        # Return empty array instead of raising error
        return []

@router.get("/scope/projects/{project_id}")
async def get_single_project(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get a single project by ID"""
    # Try to find by project_id (string) first, then by id (if numeric)
    project = db.query(Project).filter(Project.project_id == project_id).first()
    
    # If not found and project_id is numeric, try searching by id
    if not project and project_id.isdigit():
        project = db.query(Project).filter(Project.id == int(project_id)).first()
    
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
    """Generate scope and save to database using V2 engine"""
    try:
        # Parse the description using NLP
        parsed = nlp_service.extract_project_details(request.description)
        
        # Add any missing fields from request
        if not parsed.get('location') and hasattr(request, 'default_location'):
            parsed['location'] = request.default_location
        if not parsed.get('square_footage') and hasattr(request, 'default_square_footage'):
            parsed['square_footage'] = request.default_square_footage
        
        # Normalize building type using taxonomy
        if parsed.get('building_type'):
            canonical_type, canonical_subtype = validate_building_type(
                parsed['building_type'],
                parsed.get('subtype')
            )
            parsed['building_type'] = canonical_type
            if canonical_subtype:
                parsed['subtype'] = canonical_subtype
            
            # Log normalization for debugging
            if parsed.get('building_type') != canonical_type:
                logger.info(f"Normalized building type from '{parsed.get('building_type')}' to '{canonical_type}'")
        
        # Use unified engine for calculations
        result = unified_engine.calculate_project(
            building_type=BuildingType(parsed.get('building_type', 'office')),
            subtype=parsed.get('subtype'),
            square_footage=parsed.get('square_footage', 10000),
            location=parsed.get('location', 'Nashville, TN'),
            project_class=ProjectClass(parsed.get('project_class', 'ground_up')),
            floors=parsed.get('floors', 1),
            ownership_type=OwnershipType(parsed.get('ownership_type', 'for_profit')),
            special_features=parsed.get('special_features', [])
        )
        
        # Generate unique project ID
        project_id = f"proj_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        # Generate project name if not provided
        project_name = parsed.get('suggested_project_name')
        if not project_name:
            building_type_display = parsed.get('building_type', 'Office').replace('_', ' ').title()
            location_short = parsed.get('location', 'Unknown')[:20]
            project_name = f"{building_type_display} - {location_short}"
        
        # Create project with new schema
        import json
        project = Project(
            # Required fields
            project_id=project_id,
            name=project_name,
            description=request.description,
            location=parsed.get('location', 'Nashville, TN'),
            square_footage=parsed.get('square_footage', 10000),
            building_type=parsed.get('building_type', 'office'),
            occupancy_type=parsed.get('building_type', 'office'),  # Keep same as building_type for now
            
            # Cost fields
            total_cost=result.get('totals', {}).get('total_project_cost', 0),
            subtotal=result.get('construction_costs', {}).get('construction_total', 0),
            cost_per_sqft=result.get('totals', {}).get('cost_per_sf', 0),
            
            # NEW: Use calculation_data column for all calculation results
            calculation_data=json.dumps(result),  # Store entire result as JSON
            
            # Legacy fields for backward compatibility (will remove in Phase 3)
            scope_data=json.dumps(result),  # Keep for now
            cost_data=json.dumps(result.get('construction_costs', {})),  # Keep for now
            
            # Nullable fields - NOT including project_type or project_classification!
            # These are now handled by building_type
            
            # User tracking (if available)
            user_id=getattr(request, 'user_id', None),
            team_id=getattr(request, 'team_id', None),
            created_by_id=getattr(request, 'user_id', None),
            
            # Timestamps
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        db.add(project)
        db.commit()
        db.refresh(project)
        
        # Return formatted response
        return ProjectResponse(
            success=True,
            data=format_project_response(project)
        )
        
    except Exception as e:
        logger.error(f"Error generating scope: {str(e)}")
        db.rollback()
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

async def _get_owner_view_impl(project_id: str, db: Session):
    """Implementation of owner view logic"""
    if not project_id:
        return ProjectResponse(
            success=False,
            data={},
            errors=["project_id required"]
        )
    
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"]
        )
    
    # Process the owner view data
    return await _process_owner_view_data(project)

@router.post("/scope/projects/{project_id}/owner-view")
async def get_owner_view_by_id(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get owner view data for a project by ID in URL"""
    return await _get_owner_view_impl(project_id, db)

@router.get("/scope/projects/{project_id}/owner-view")
async def get_owner_view_by_id_get(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get owner view data for a project by ID in URL (GET version)"""
    return await _get_owner_view_impl(project_id, db)

@router.post("/scope/owner-view")
async def get_owner_view(
    request: dict,
    db: Session = Depends(get_db)
):
    """Get owner-friendly view of project with ID in body"""
    project_id = request.get('project_id')
    return await _get_owner_view_impl(project_id, db)

# Process owner view data for a project
async def _process_owner_view_data(project):
    """Process and return owner view data for a project"""
    # Use unified_engine for owner view calculations
    try:
        # Parse stored calculation data - check all possible sources
        import json
        calculation_data = {}
        
        # First try calculation_data column (V2 projects)
        if hasattr(project, 'calculation_data') and project.calculation_data:
            try:
                calculation_data = json.loads(project.calculation_data) if isinstance(project.calculation_data, str) else project.calculation_data
            except:
                pass
        
        # Fall back to scope_data or cost_data (legacy projects)
        if not calculation_data:
            scope_data = json.loads(project.scope_data) if project.scope_data else {}
            cost_data = json.loads(project.cost_data) if project.cost_data else {}
            calculation_data = cost_data if cost_data else scope_data
        
        # Extract ownership and revenue data from V2 structure
        owner_data = calculation_data.get('ownership_analysis', {})
        
        # V2 stores revenue_analysis inside ownership_analysis
        revenue_data = owner_data.get('revenue_analysis', {}) if owner_data else {}
        
        # If no revenue data in ownership, check top level
        if not revenue_data:
            revenue_data = calculation_data.get('revenue_analysis', {})
        
        # Extract return metrics which contain revenue calculations
        return_metrics = owner_data.get('return_metrics', {})
        
        roi_data = calculation_data.get('roi_analysis', {})
        
        # Build comprehensive owner view response
        # Extract actual revenue values from return_metrics if available
        annual_noi = return_metrics.get('estimated_annual_noi', 0)
        cash_on_cash = return_metrics.get('cash_on_cash_return', 0)
        
        # Calculate revenue values if we have NOI
        if annual_noi > 0:
            # Typical restaurant/retail has 8-10% margin, so revenue = NOI / margin
            estimated_margin = 0.08  # 8% default margin
            estimated_revenue = annual_noi / estimated_margin if estimated_margin > 0 else 0
            estimated_net_income = annual_noi
        else:
            estimated_revenue = revenue_data.get('annual_revenue', 0)
            estimated_net_income = revenue_data.get('net_income', 0)
            estimated_margin = revenue_data.get('operating_margin', 0.08)
        
        owner_view_response = {
            'project_id': project.project_id,
            'project_name': project.name,
            'project_summary': {
                'total_project_cost': project.total_cost,
                'construction_cost': project.subtotal,
                'total_cost_per_sqft': project.cost_per_sqft,
                'square_footage': project.square_footage
            },
            'ownership_analysis': owner_data,
            
            # Revenue analysis - both nested and flat for compatibility
            'revenue_analysis': {
                'annual_revenue': estimated_revenue,
                'operating_margin': estimated_margin,
                'net_income': estimated_net_income,
                'estimated_annual_noi': annual_noi,
                'cash_on_cash_return': cash_on_cash,
                **revenue_data  # Include any existing revenue data
            },
            'annual_revenue': estimated_revenue,
            'operating_margin': estimated_margin,
            'net_income': estimated_net_income,
            
            # ROI analysis - structured for frontend
            'roi_analysis': roi_data if roi_data else {
                'financial_metrics': {
                    'annual_revenue': estimated_revenue,
                    'operating_margin': estimated_margin,
                    'net_income': estimated_net_income,
                    'estimated_annual_noi': annual_noi,
                    'cash_on_cash_return': cash_on_cash
                }
            },
            'financial_metrics': {
                'annual_revenue': estimated_revenue,
                'operating_margin': estimated_margin,
                'net_income': estimated_net_income,
                'estimated_annual_noi': annual_noi,
                'cash_on_cash_return': cash_on_cash
            },
            'revenue_requirements': owner_data.get('revenue_requirements', {})
        }
        
        return ProjectResponse(
            success=True,
            data=owner_view_response
        )
        
    except Exception as e:
        logger.error(f"Error in get_owner_view: {str(e)}")
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(e)]
        )

def format_project_response(project: Project) -> dict:
    """
    Format database project to match frontend expectations.
    Provides both snake_case and camelCase for compatibility.
    """
    import json
    
    # UPDATED: Check calculation_data column first, then fall back to legacy columns
    calculation_data = {}
    if hasattr(project, 'calculation_data') and project.calculation_data:
        # New calculation_data column - stored as JSON text, needs parsing
        try:
            calculation_data = json.loads(project.calculation_data) if isinstance(project.calculation_data, str) else project.calculation_data
        except (json.JSONDecodeError, TypeError):
            # If parsing fails, fall back to scope_data
            if project.scope_data:
                calculation_data = json.loads(project.scope_data)
    elif project.scope_data:
        # Legacy text column - needs parsing
        calculation_data = json.loads(project.scope_data)
    elif project.cost_data:
        # Fallback to cost_data
        calculation_data = json.loads(project.cost_data)
    
    # Extract trade breakdown from stored data - handle both V1 and V2 formats
    trade_data = calculation_data.get('trade_breakdown', {})
    
    # Convert trade_breakdown dict to categories array format for frontend
    categories = []
    
    # First check if we have categories in V1 format (nested structure)
    if 'categories' in calculation_data and isinstance(calculation_data['categories'], list):
        # V1 format - categories is already an array with nested systems
        for category in calculation_data['categories']:
            if isinstance(category, dict) and 'name' in category:
                # Calculate total value from systems or use subtotal
                value = category.get('subtotal', 0) or category.get('subtotal_with_markup', 0)
                categories.append({
                    'name': category['name'],
                    'value': value,
                    'systems': category.get('systems', [{
                        'name': category['name'],
                        'total_cost': value,
                        'unit_cost': value,
                        'quantity': 1
                    }])
                })
    elif trade_data:
        # V2 format - trade_breakdown is a flat dictionary
        for trade_name, amount in trade_data.items():
            categories.append({
                'name': trade_name.replace('_', ' ').title(),
                'value': amount,
                'systems': [{
                    'name': trade_name.replace('_', ' ').title(),
                    'total_cost': amount,
                    'unit_cost': amount,
                    'quantity': 1
                }]
            })
    
    # Extract subtype from calculation data
    subtype = calculation_data.get('project_info', {}).get('subtype', '')
    if not subtype and calculation_data.get('parsed_input'):
        subtype = calculation_data.get('parsed_input', {}).get('subtype', '')
    
    return {
        # IDs - both formats
        'id': project.id,
        'project_id': project.project_id,
        'projectId': project.project_id,
        
        # Names - all variations frontend might expect
        'name': project.name,
        'project_name': project.name,
        'projectName': project.name,
        
        # Costs - both snake_case and camelCase
        'total_cost': project.total_cost,
        'totalCost': project.total_cost,
        'cost_per_sqft': project.cost_per_sqft,
        'costPerSqft': project.cost_per_sqft,
        'subtotal': project.subtotal,
        'construction_cost': project.subtotal,
        'constructionCost': project.subtotal,
        
        # Trade data - all formats frontend might use
        'categories': categories,
        'trade_breakdown': trade_data,
        'trade_packages': categories,
        'tradePackages': categories,
        
        # Building info
        'building_type': project.building_type,
        'buildingType': project.building_type,
        'occupancy_type': project.occupancy_type,
        'occupancyType': project.occupancy_type,
        'subtype': subtype,
        
        # Other project fields
        'square_footage': project.square_footage,
        'squareFootage': project.square_footage,
        'location': project.location,
        'description': project.description,
        
        # Timestamps
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'createdAt': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None,
        'updatedAt': project.updated_at.isoformat() if project.updated_at else None,
        
        # Include full calculation data for components that need it
        'calculation_data': calculation_data,
        'scope_data': calculation_data,  # Legacy compatibility
        
        # Success flag
        'success': True
    }