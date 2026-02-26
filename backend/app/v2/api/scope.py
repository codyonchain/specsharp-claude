"""
Clean API endpoint that uses the new system
"""

import os
import json
from fastapi import APIRouter, HTTPException, Query, Depends, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from app.v2.engines.unified_engine import (
    unified_engine,
    build_project_timeline,
    build_construction_schedule,
)
from app.services.nlp_service import NLPService
nlp_service = NLPService()
from app.v2.config.master_config import (
    BuildingType,
    ProjectClass,
    OwnershipType,
    MASTER_CONFIG
)
from app.v2.services.industrial_override_extractor import extract_industrial_overrides
from app.v2.services.dealshield_service import build_dealshield_view_model, DealShieldResolutionError
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.core.building_taxonomy import normalize_building_type, validate_building_type
from app.db.models import Project
from app.db.database import get_db
from app.services.pdf_export_service import pdf_export_service
from app.config.regional_multipliers import _location_has_explicit_state
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["v2"])
DEBUG_TRACE_ENABLED = os.getenv("SPECSHARP_DEBUG_TRACE", "0").lower() in {"1", "true", "yes", "on"}


def _infer_revenue_driver(building_type: Optional[str]) -> str:
    mapping = {
        "restaurant": "sales_per_sf",
        "hospitality": "adr_x_occupancy",
        "multifamily": "rent_per_unit",
        "healthcare": "per_bed_or_procedure",
        "office": "rent_profile_sf",
        "industrial": "flex_mix_sf",
        "retail": "sales_per_sf",
    }
    normalized = (building_type or "").strip().lower()
    return mapping.get(normalized, "per_sf")


def _collect_trace_assertions(calculation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    assertions: List[Dict[str, Any]] = []
    totals = calculation_data.get("totals") or {}
    for key in ("hard_costs", "soft_costs", "total_project_cost"):
        value = totals.get(key)
        if isinstance(value, (int, float)):
            assertions.append({
                "check": f"{key}_non_negative",
                "value": value,
                "status": "pass" if value >= 0 else "fail"
            })
    trades = calculation_data.get("trade_breakdown")
    construction_total = (calculation_data.get("construction_costs") or {}).get("construction_total")
    if isinstance(trades, dict) and isinstance(construction_total, (int, float)):
        trade_sum = sum(float(v or 0) for v in trades.values())
        variance = abs(trade_sum - construction_total)
        status = "pass"
        if construction_total:
            ratio = variance / max(abs(construction_total), 1.0)
            status = "pass" if ratio <= 0.02 else "warn"
        assertions.append({
            "check": "trade_breakdown_matches_construction_total",
            "value": {"trade_sum": trade_sum, "construction_total": construction_total},
            "status": status
        })
    departments = calculation_data.get("department_allocation")
    if isinstance(departments, list) and departments:
        total_pct = sum(float(item.get("percent") or 0) for item in departments if isinstance(item, dict))
        assertions.append({
            "check": "department_allocation_sum",
            "value": total_pct,
            "status": "pass" if 0.95 <= total_pct <= 1.05 else "warn"
        })
    scope_items = calculation_data.get("scope_items")
    if isinstance(scope_items, list) and scope_items:
        seen = set()
        duplicates = []
        for item in scope_items:
            trade_name = item.get("trade") if isinstance(item, dict) else None
            systems = item.get("systems") if isinstance(item, dict) else None
            if not isinstance(trade_name, str) or not isinstance(systems, list):
                continue
            for system in systems:
                system_name = system.get("name") if isinstance(system, dict) else None
                if not isinstance(system_name, str):
                    continue
                key = (trade_name.strip().lower(), system_name.strip().lower())
                if key in seen:
                    duplicates.append({"trade": trade_name, "system": system_name})
                else:
                    seen.add(key)
        assertions.append({
            "check": "scope_item_duplicates",
            "value": duplicates,
            "status": "pass" if not duplicates else "warn"
        })
    return assertions


def _build_debug_trace_payload(payload: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not DEBUG_TRACE_ENABLED or not isinstance(payload, dict):
        return None

    calculations = payload.get("calculation_data")
    if isinstance(calculations, dict):
        calc_context = calculations
    else:
        calc_context = payload

    project_info = calc_context.get("project_info")
    if not isinstance(project_info, dict):
        return None

    modifiers = calc_context.get("modifiers") or {}
    revenue_block = (
        calc_context.get("revenue_analysis")
        or (calc_context.get("ownership_analysis") or {}).get("revenue_analysis")
        or {}
    )
    return_metrics = (
        calc_context.get("return_metrics")
        or (calc_context.get("ownership_analysis") or {}).get("return_metrics")
        or {}
    )
    profile = calc_context.get("profile") or {}
    construction_costs = calc_context.get("construction_costs") or {}
    trace_entries = calc_context.get("calculation_trace") or []

    fallback_entries: List[Dict[str, Any]] = []
    for entry in trace_entries:
        if not isinstance(entry, dict):
            continue
        step = entry.get("step")
        if not isinstance(step, str):
            continue
        lowered = step.lower()
        if any(keyword in lowered for keyword in ("warning", "fallback", "clamp", "adjusted")):
            fallback_entries.append({
                "step": step,
                "data": entry.get("data")
            })

    debug_trace = {
        "engine_used": "unified_engine.calculate_project",
        "config": {
            "building_type": project_info.get("building_type"),
            "subtype": project_info.get("subtype"),
            "project_class": project_info.get("project_class"),
            "square_footage": project_info.get("square_footage"),
            "finish_level": project_info.get("finish_level"),
            "finish_level_source": project_info.get("finish_level_source"),
            "floors": project_info.get("floors"),
        },
        "multipliers": {
            "cost_factor": modifiers.get("cost_factor"),
            "finish_cost_factor": modifiers.get("finish_cost_factor"),
            "cost_region_factor": modifiers.get("regional_cost_factor"),
            "revenue_factor": modifiers.get("revenue_factor"),
            "finish_revenue_factor": modifiers.get("finish_revenue_factor"),
            "revenue_region_factor": modifiers.get("market_factor"),
            "quality_factor": construction_costs.get("quality_factor"),
        },
        "revenue_model": {
            "driver": _infer_revenue_driver(project_info.get("building_type")),
            "annual_revenue": revenue_block.get("annual_revenue"),
            "revenue_per_sf": revenue_block.get("revenue_per_sf"),
            "operating_margin": revenue_block.get("operating_margin"),
            "occupancy_rate": revenue_block.get("occupancy_rate"),
            "market_factor": modifiers.get("market_factor"),
        },
        "valuation_model": {
            "method": "cap_rate" if return_metrics.get("property_value") else "yield_on_cost",
            "property_value": return_metrics.get("property_value"),
            "market_cap_rate": return_metrics.get("market_cap_rate") or profile.get("market_cap_rate"),
            "target_yield": profile.get("target_yield"),
            "yield_on_cost": calc_context.get("yield_on_cost"),
        },
        "fallbacks_used": fallback_entries,
        "assertions": _collect_trace_assertions(calc_context),
    }
    return debug_trace


def _ensure_city_state_format(location: Optional[str]) -> None:
    """Validate that location strings are provided in 'City, ST' format."""
    if not location or not _location_has_explicit_state(location):
        raise HTTPException(
            status_code=400,
            detail="Location must be provided as 'City, ST' (e.g., 'Dallas, TX')."
        )


def _project_class_from_payload(payload: Dict[str, Any]) -> ProjectClass:
    """Normalize project class strings from UI/NLP into ProjectClass enums."""
    raw_value = None
    if isinstance(payload, dict):
        # Accept BOTH legacy keys + NLP keys
        raw_value = (
            payload.get("project_classification")
            or payload.get("projectClassification")
            or payload.get("project_class")          # legacy
            or payload.get("projectClass")           # legacy
            or payload.get("project_type")
            or payload.get("projectType")
            or payload.get("project_classification".upper())  # defensive
        )

        # Also allow nested aliases if a caller passes full request dict
        parsed = payload.get("parsed_input") or payload.get("parsedInput")
        if not raw_value and isinstance(parsed, dict):
            raw_value = (
                parsed.get("project_classification")
                or parsed.get("projectClassification")
                or parsed.get("project_class")
                or parsed.get("projectClass")
            )

    if not raw_value:
        return ProjectClass.GROUND_UP

    key = str(raw_value).strip().lower().replace("-", "_").replace(" ", "_")

    if key in {"ground_up", "groundup", "ground", "greenfield", "new", "new_build", "newbuild"}:
        return ProjectClass.GROUND_UP
    if key in {"renovation", "reno", "remodel", "tenant_improvement", "tenantimprovement", "ti", "fitout", "fit_out"}:
        return ProjectClass.RENOVATION
    if key in {"addition", "add", "expansion"}:
        return ProjectClass.ADDITION

    return ProjectClass.GROUND_UP

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalyzeRequest(BaseModel):
    """Request for natural language analysis"""
    model_config = ConfigDict(populate_by_name=True)
    description: str = Field(..., description="Natural language project description")
    default_location: Optional[str] = Field(None, description="Default location if not detected")
    default_square_footage: Optional[float] = Field(None, description="Default square footage if not detected")
    location: Optional[str] = Field(None, description="Explicit location override")
    square_footage: Optional[float] = Field(
        None,
        alias="squareFootage",
        validation_alias=AliasChoices("square_footage", "squareFootage"),
        description="Explicit square footage override"
    )
    finish_level: Optional[str] = Field(
        None,
        alias="finishLevel",
        validation_alias=AliasChoices("finishLevel", "finish_level"),
        description="Finish level selection (Standard, Premium, Luxury)"
    )
    project_class: Optional[str] = Field(
        None,
        alias="projectClass",
        validation_alias=AliasChoices("project_class", "projectClass"),
        description="Project class (ground_up, renovation, addition)"
    )
    special_features: List[str] = Field(
        default_factory=list,
        description="Special feature IDs to price into the estimate"
    )

class CalculateRequest(BaseModel):
    """Request for direct calculation"""
    model_config = ConfigDict(populate_by_name=True)
    building_type: str = Field(..., description="Building type (e.g., 'healthcare', 'office')")
    subtype: str = Field(..., description="Building subtype (e.g., 'hospital', 'class_a')")
    square_footage: float = Field(..., gt=0, description="Total square footage")
    location: str = Field(..., description="Project location for regional multiplier ('City, ST')")
    project_class: Optional[str] = Field("ground_up", description="Project class")
    floors: Optional[int] = Field(1, ge=1, description="Number of floors")
    ownership_type: Optional[str] = Field("for_profit", description="Ownership type")
    special_features: Optional[List[str]] = Field([], description="Special features to include")
    finish_level: Optional[str] = Field(
        None,
        alias="finishLevel",
        validation_alias=AliasChoices("finishLevel", "finish_level"),
        description="Finish level (Standard, Premium, Luxury)"
    )

class CompareRequest(BaseModel):
    """Request for scenario comparison"""
    scenarios: List[Dict[str, Any]] = Field(..., description="List of scenarios to compare")

class DealShieldControlsUpdateRequest(BaseModel):
    """Request for persisting DealShield control selections."""
    stress_band_pct: int = Field(10, description="Stress band percentage (10, 7, 5, 3)")
    anchor_total_project_cost: Optional[float] = Field(None, description="Optional cost anchor value")
    use_cost_anchor: bool = Field(False, description="Whether to apply cost anchor")
    anchor_annual_revenue: Optional[float] = Field(None, description="Optional revenue anchor value")
    use_revenue_anchor: bool = Field(False, description="Whether to apply revenue anchor")

class ProjectResponse(BaseModel):
    """Standard project response"""
    success: bool
    data: Dict[str, Any]
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    debug_trace: Optional[Dict[str, Any]] = None

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
        logger.info(
            "[scope.analyze][REQ] project_class=%s project_classification=%s raw=%s",
            getattr(request, "project_class", None),
            getattr(request, "project_classification", None),
            request.model_dump() if hasattr(request, "model_dump") else request.dict(),
        )
        # Parse the description using phrase-first parser
        parsed = nlp_service.extract_project_details(request.description)
        parsed['special_features'] = request.special_features or []
        overrides = extract_industrial_overrides(request.description)
        if overrides:
            parsed.update(overrides)
        override_keys = [
            "dock_doors", "dock_count",
            "office_sf", "office_percent", "office_pct",
            "mezzanine_sf", "mezzanine_percent",
            "clear_height", "clear_height_ft",
            "finish_level", "finish_level_source",
        ]
        sf_list = parsed.get('special_features') or []
        if not isinstance(sf_list, list):
            sf_list = list(sf_list) if sf_list else []
        parsed_overrides = {k: parsed.get(k) for k in override_keys if k in parsed}
        sf_list.append({"__parsed_input__": parsed_overrides})
        parsed['special_features'] = sf_list
        
        # Normalize building type using taxonomy
        if parsed.get('building_type'):
            original_type = parsed['building_type']
            original_subtype = parsed.get('subtype')
            canonical_type, canonical_subtype = validate_building_type(
                parsed['building_type'],
                parsed.get('subtype')
            )
            parsed['building_type'] = canonical_type
            if canonical_subtype:
                parsed['subtype'] = canonical_subtype
                parsed['building_subtype'] = canonical_subtype
            else:
                # Prevent invalid cross-type pairs from reaching the engine.
                parsed.pop('subtype', None)
                parsed.pop('building_subtype', None)

            if original_type != canonical_type:
                logger.info(f"Normalized building type from '{original_type}' to '{canonical_type}'")
            if original_subtype and not canonical_subtype:
                logger.info(
                    "Dropped invalid subtype '%s' for canonical type '%s'",
                    original_subtype,
                    canonical_type,
                )
        
        # Apply explicit overrides and defaults
        if request.square_footage:
            parsed['square_footage'] = request.square_footage
        elif not parsed.get('square_footage') and request.default_square_footage:
            parsed['square_footage'] = request.default_square_footage

        if request.location:
            parsed['location'] = request.location
        elif not parsed.get('location') and request.default_location:
            parsed['location'] = request.default_location

        finish_override = (request.finish_level or "").strip().lower() if request.finish_level else None
        if finish_override:
            parsed['finish_level'] = finish_override

        if 'finish_level' not in parsed or not parsed['finish_level']:
            parsed['finish_level'] = 'standard'

        # Respect explicit project class selection from client-side configuration
        override_class = getattr(request, "project_class", None) or getattr(request, "project_classification", None)
        if override_class:
            parsed["project_class"] = override_class
            parsed["project_classification"] = override_class
            logger.info("[scope.analyze][OVERRIDE_APPLIED] override_class=%s", override_class)

        finish_level_value = parsed.get('finish_level', 'standard')
        finish_level_source = 'explicit' if finish_override else (
            'description' if parsed.get('finish_level') not in (None, '', 'standard') and not finish_override else 'default'
        )
        parsed['finish_level_source'] = finish_level_source

        # Validate we have minimum required data
        if not parsed.get('square_footage'):
            return ProjectResponse(
                success=False,
                data={},
                errors=["Could not determine square footage from description"]
            )
        
        # Convert string values to enums
        building_type = BuildingType(parsed['building_type'])
        logger.info(
            "[scope.analyze][PRE_NORM] parsed.project_class=%s parsed.project_classification=%s",
            parsed.get("project_class"),
            parsed.get("project_classification"),
        )
        normalized_override = parsed.get("project_class") or parsed.get("project_classification")
        if normalized_override:
            project_class = _project_class_from_payload({
                "project_class": normalized_override,
                "project_classification": normalized_override,
            })
        else:
            project_class = _project_class_from_payload(parsed)
        logger.info("[scope.analyze][POST_NORM] project_class_enum=%s", project_class)
        ownership_type = OwnershipType(parsed.get('ownership_type', 'for_profit'))
        
        # Calculate everything
        final_location = (parsed.get('location') or '').strip()
        _ensure_city_state_format(final_location)
        parsed['location'] = final_location

        logger.info(
            "[SUBTYPE_TRACE][scope_api] building_type=%s subtype=%s building_subtype=%s location=%s raw_prompt=%s",
            parsed.get('building_type'),
            parsed.get('subtype'),
            parsed.get('building_subtype'),
            parsed.get('location'),
            request.description,
        )
        result = unified_engine.calculate_project(
            building_type=building_type,
            subtype=parsed.get('subtype'),  # Use .get() to handle missing subtype
            square_footage=parsed['square_footage'],
            location=final_location,
            project_class=project_class,
            floors=parsed.get('floors', 1),
            ownership_type=ownership_type,
            finish_level=finish_level_value,
            finish_level_source=finish_level_source,
            special_features=parsed.get('special_features', []),
            parsed_input_overrides=parsed
        )
        
        # Add building_subtype for frontend compatibility
        parsed_with_compat = parsed.copy()
        parsed_with_compat['building_subtype'] = parsed.get('subtype')
        parsed_with_compat['finish_level'] = parsed.get('finish_level', 'standard')
        parsed_with_compat['finish_level_source'] = finish_level_source
        
        response_data = {
            'parsed_input': parsed_with_compat,
            'calculations': result,  # Now properly structured without double nesting
            'confidence': parsed.get('confidence', 0),
            'debug': {
                'engine_version': 'unified_v2',
                'config_version': '2.0',
                'trace_count': len(result.get('calculation_trace', []))
            }
        }
        return ProjectResponse(
            success=True,
            data=response_data,
            debug_trace=_build_debug_trace_payload(result)
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
        
        location_value = request.location.strip()
        _ensure_city_state_format(location_value)

        # Calculate
        result = unified_engine.calculate_project(
            building_type=building_type,
            subtype=request.subtype,
            square_footage=request.square_footage,
            location=location_value,
            project_class=project_class,
            floors=request.floors,
            ownership_type=ownership_type,
            finish_level=request.finish_level,
            finish_level_source='explicit' if request.finish_level else None,
            special_features=request.special_features
        )
        
        return ProjectResponse(
            success=True,
            data=result,
            debug_trace=_build_debug_trace_payload(result)
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
    
    formatted = format_project_response(project)
    return ProjectResponse(
        success=True,
        data=formatted,
        debug_trace=_build_debug_trace_payload(formatted)
    )


def _normalize_dealshield_controls_payload(raw_controls: Dict[str, Any]) -> Dict[str, Any]:
    allowed_stress_bands = {10, 7, 5, 3}
    raw_band = raw_controls.get("stress_band_pct")
    stress_band_pct = 10
    if isinstance(raw_band, (int, float)) and not isinstance(raw_band, bool):
        candidate = int(float(raw_band))
        if candidate in allowed_stress_bands:
            stress_band_pct = candidate

    def _normalize_optional_number(value: Any) -> Optional[float]:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            parsed = float(value)
            if parsed == parsed and parsed not in (float("inf"), float("-inf")):
                return parsed
        return None

    normalized_cost_anchor = _normalize_optional_number(raw_controls.get("anchor_total_project_cost"))
    normalized_revenue_anchor = _normalize_optional_number(raw_controls.get("anchor_annual_revenue"))

    return {
        "stress_band_pct": stress_band_pct,
        "anchor_total_project_cost": normalized_cost_anchor,
        "use_cost_anchor": bool(raw_controls.get("use_cost_anchor")) and normalized_cost_anchor is not None,
        "anchor_annual_revenue": normalized_revenue_anchor,
        "use_revenue_anchor": bool(raw_controls.get("use_revenue_anchor")) and normalized_revenue_anchor is not None,
    }


def _resolve_dealshield_building_context(
    project: Project,
    payload: Dict[str, Any],
) -> tuple[Optional[str], Optional[str]]:
    project_info = payload.get("project_info") if isinstance(payload.get("project_info"), dict) else {}
    parsed_input = payload.get("parsed_input") if isinstance(payload.get("parsed_input"), dict) else {}
    request_data = payload.get("request_data") if isinstance(payload.get("request_data"), dict) else {}

    building_type = (
        project_info.get("building_type")
        or parsed_input.get("building_type")
        or request_data.get("building_type")
        or getattr(project, "building_type", None)
    )
    subtype = (
        project_info.get("subtype")
        or parsed_input.get("subtype")
        or parsed_input.get("building_subtype")
        or request_data.get("subtype")
        or request_data.get("building_subtype")
    )
    if isinstance(building_type, str):
        building_type = building_type.strip()
    if isinstance(subtype, str):
        subtype = subtype.strip()
    return building_type, subtype


@router.post("/scope/projects/{project_id}/dealshield/controls", response_model=ProjectResponse)
async def update_dealshield_controls(
    project_id: str,
    request: DealShieldControlsUpdateRequest,
    db: Session = Depends(get_db),
):
    """Persist DealShield controls to project calculation_data and rebuild scenario snapshots."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project and project_id.isdigit():
        project = db.query(Project).filter(Project.id == int(project_id)).first()

    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"],
        )

    try:
        payload = _resolve_project_payload(project)
        if not isinstance(payload, dict):
            payload = {}

        normalized_controls = _normalize_dealshield_controls_payload(request.model_dump())
        payload["dealshield_controls"] = normalized_controls

        profile_id = payload.get("dealshield_tile_profile")
        if isinstance(profile_id, str) and profile_id.strip():
            from app.v2.services.dealshield_scenarios import (
                build_dealshield_scenarios,
                DealShieldScenarioError,
            )

            building_type, subtype = _resolve_dealshield_building_context(project, payload)
            if not building_type or not subtype:
                raise ValueError("Unable to resolve building type/subtype for DealShield scenario rebuild")

            canonical_type, canonical_subtype = validate_building_type(building_type, subtype)
            subtype_key = canonical_subtype or subtype
            building_type_enum = BuildingType(canonical_type)
            building_config = MASTER_CONFIG.get(building_type_enum, {}).get(subtype_key)
            if building_config is None:
                raise ValueError(
                    f"Unable to resolve building config for DealShield scenario rebuild ({canonical_type}/{subtype_key})"
                )

            try:
                payload["dealshield_scenarios"] = build_dealshield_scenarios(
                    payload,
                    building_config,
                    unified_engine,
                )
            except DealShieldScenarioError as exc:
                raise ValueError(str(exc)) from exc

        project.calculation_data = json.dumps(payload)
        db.commit()
        db.refresh(project)
    except Exception as exc:
        logger.error("Failed to persist DealShield controls for project %s: %s", project_id, str(exc))
        db.rollback()
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(exc)],
        )

    return ProjectResponse(
        success=True,
        data={
            "project_id": project.project_id or project_id,
            "dealshield_controls": normalized_controls,
            "dealshield_scenarios_present": isinstance(
                (payload.get("dealshield_scenarios") or {}).get("scenarios"),
                dict,
            ),
        },
    )


@router.get("/scope/projects/{project_id}/dealshield", response_model=ProjectResponse)
async def get_dealshield_view(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get DealShield scenario table view model for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project and project_id.isdigit():
        project = db.query(Project).filter(Project.id == int(project_id)).first()

    if not project:
        return ProjectResponse(
            success=False,
            data={},
            errors=["Project not found"]
        )

    payload = _resolve_project_payload(project)
    profile_id = payload.get("dealshield_tile_profile")
    if not isinstance(profile_id, str) or not profile_id.strip():
        return ProjectResponse(
            success=False,
            data={},
            errors=["DealShield not available for this project"]
        )

    try:
        profile = get_dealshield_profile(profile_id)
    except Exception as exc:
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(exc)]
        )

    try:
        view_model = build_dealshield_view_model(project.project_id or project_id, payload, profile)
    except DealShieldResolutionError as exc:
        return ProjectResponse(
            success=False,
            data={},
            errors=[str(exc)]
        )

    return ProjectResponse(
        success=True,
        data=view_model
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
        parsed['special_features'] = request.special_features or []
        overrides = extract_industrial_overrides(request.description)
        if overrides:
            parsed.update(overrides)
        sf_list = parsed.get('special_features') or []
        if not isinstance(sf_list, list):
            sf_list = list(sf_list) if sf_list else []
        override_keys = [
            "dock_doors", "dock_count",
            "office_sf", "office_percent", "office_pct",
            "mezzanine_sf", "mezzanine_percent",
            "finish_level", "finish_level_source",
        ]
        parsed_overrides = {k: parsed.get(k) for k in override_keys if k in parsed}
        sf_list.append({"__parsed_input__": parsed_overrides})
        parsed['special_features'] = sf_list
        
        # Add any missing fields from request
        if request.location:
            parsed['location'] = request.location
        elif not parsed.get('location') and hasattr(request, 'default_location'):
            parsed['location'] = request.default_location

        if request.square_footage:
            parsed['square_footage'] = request.square_footage
        elif not parsed.get('square_footage') and hasattr(request, 'default_square_footage'):
            parsed['square_footage'] = request.default_square_footage

        finish_override = (request.finish_level or "").strip().lower() if getattr(request, 'finish_level', None) else None
        if finish_override:
            parsed['finish_level'] = finish_override

        if 'finish_level' not in parsed or not parsed['finish_level']:
            parsed['finish_level'] = 'standard'

        override_class = getattr(request, "project_class", None) or getattr(request, "project_classification", None)
        if override_class:
            parsed['project_class'] = override_class
            parsed['project_classification'] = override_class
            logger.info("[scope.generate] project_class override: %s", override_class)

        # Normalize project class from any payload/NLP alias
        if override_class:
            project_class_enum = _project_class_from_payload({
                "project_class": override_class,
                "project_classification": override_class
            })
        else:
            project_class_enum = _project_class_from_payload(parsed)
        project_class_str = project_class_enum.value  # 'ground_up' / 'renovation' / 'addition'

        # Keep both fields so older logic + newer logic both work
        parsed["project_class"] = project_class_str
        parsed["project_classification"] = project_class_str

        finish_level_value = parsed.get('finish_level', 'standard')
        finish_level_source = 'explicit' if finish_override else (
            'description' if parsed.get('finish_level') not in (None, '', 'standard') and not finish_override else 'default'
        )
        parsed['finish_level_source'] = finish_level_source
        
        # Normalize building type using taxonomy
        if parsed.get('building_type'):
            original_subtype = parsed.get('subtype')
            canonical_type, canonical_subtype = validate_building_type(
                parsed['building_type'],
                parsed.get('subtype')
            )
            parsed['building_type'] = canonical_type
            if canonical_subtype:
                parsed['subtype'] = canonical_subtype
                parsed['building_subtype'] = canonical_subtype
            else:
                parsed.pop('subtype', None)
                parsed.pop('building_subtype', None)

            if original_subtype and not canonical_subtype:
                logger.info(
                    "Dropped invalid subtype '%s' for canonical type '%s' in /generate",
                    original_subtype,
                    canonical_type,
                )
        
        # Use unified engine for calculations
        building_type_enum = BuildingType(parsed.get('building_type', 'office'))
        logger.info(
            "[scope.generate] class_enum=%s class_str=%s parsed.project_class=%s parsed.project_classification=%s request.project_class=%s",
            project_class_enum,
            project_class_str,
            parsed.get("project_class"),
            parsed.get("project_classification"),
            getattr(request, "project_class", None),
        )

        result = unified_engine.calculate_project(
            building_type=building_type_enum,
            subtype=parsed.get('subtype'),
            square_footage=parsed.get('square_footage', 10000),
            location=parsed.get('location', 'Nashville, TN'),
            project_class=project_class_enum,
            floors=parsed.get('floors', 1),
            ownership_type=OwnershipType(parsed.get('ownership_type', 'for_profit')),
            finish_level=finish_level_value,
            finish_level_source=finish_level_source,
            special_features=parsed.get('special_features', []),
            parsed_input_overrides=parsed
        )

        # Embed request metadata into stored result so downstream consumers can hydrate it
        if isinstance(result, dict):
            req_block = {
                "project_classification": project_class_str,
                "project_class": project_class_str,
                "building_type": parsed.get("building_type"),
                "subtype": parsed.get("subtype"),
                "square_footage": parsed.get("square_footage"),
                "location": parsed.get("location"),
                "floors": parsed.get("floors", 1),
                "finish_level": finish_level_value,
                "finish_level_source": finish_level_source,
                "special_features": parsed.get("special_features", []),
            }

            # Store both for compatibility
            result.setdefault("request_data", req_block)
            result.setdefault("parsed_input", parsed.copy())
            result["parsed_input"]["project_classification"] = project_class_str
            result["parsed_input"]["project_class"] = project_class_str
            result["project_classification"] = project_class_str
        
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
        project_timeline = build_project_timeline(building_type_enum, None)
        construction_schedule = build_construction_schedule(
            building_type_enum,
            subtype=parsed.get('subtype'),
        )
        calculations_block = None
        if isinstance(result, dict) and 'calculations' in result:
            calculations_block = result['calculations']
        elif isinstance(result, dict):
            calculations_block = result
        else:
            calculations_block = {}
        if isinstance(calculations_block, dict) and 'project_timeline' not in calculations_block:
            calculations_block['project_timeline'] = project_timeline
        if isinstance(calculations_block, dict) and 'construction_schedule' not in calculations_block:
            calculations_block['construction_schedule'] = construction_schedule
        if isinstance(result, dict) and 'calculations' in result:
            result['calculations'] = calculations_block
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
            project_classification=project_class_str,
            
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
        formatted = format_project_response(project)
        return ProjectResponse(
            success=True,
            data=formatted,
            debug_trace=_build_debug_trace_payload(formatted)
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

@router.get("/pdf/project/{project_id}/pdf")
async def export_project_pdf(
    project_id: str,
    client_name: Optional[str] = Query(None, alias="client_name"),
    db: Session = Depends(get_db)
):
    """Generate a PDF report for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project and project_id.isdigit():
        project = db.query(Project).filter(Project.id == int(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_payload = format_project_response(project)
    calculation_data = project_payload.get('calculation_data') or {}

    request_data = (
        calculation_data.get('request_data') or
        calculation_data.get('parsed_input') or
        calculation_data.get('request_payload') or
        {}
    )
    if not isinstance(request_data, dict):
        request_data = {}

    request_data.setdefault('square_footage', project_payload.get('square_footage') or project.square_footage or 0)
    request_data.setdefault('location', project_payload.get('location') or project.location or 'Unknown')
    request_data.setdefault('building_type', calculation_data.get('project_info', {}).get('building_type') or project_payload.get('building_type'))
    request_data.setdefault(
        'num_floors',
        request_data.get('floors') or
        calculation_data.get('project_info', {}).get('floors') or
        project_payload.get('floors') or
        1
    )
    project_payload['request_data'] = request_data

    project_name = project_payload.get('project_name') or project_payload.get('name') or f"project_{project_id}"
    project_payload['project_name'] = project_name

    canonical_dealshield_view_model = None
    payload = _resolve_project_payload(project)
    profile_id = payload.get("dealshield_tile_profile")
    if isinstance(profile_id, str) and profile_id.strip():
        try:
            profile = get_dealshield_profile(profile_id)
            canonical_dealshield_view_model = build_dealshield_view_model(project.project_id or project_id, payload, profile)
        except DealShieldResolutionError as exc:
            logger.warning(
                "DealShield canonical decision unavailable during project PDF export for %s: %s",
                project_id,
                str(exc),
            )
        except Exception as exc:
            logger.warning(
                "DealShield view model build failed during project PDF export for %s: %s",
                project_id,
                str(exc),
            )

    try:
        pdf_buffer = pdf_export_service.generate_professional_pdf(
            project_payload,
            client_name,
            dealshield_view_model=canonical_dealshield_view_model,
        )
    except Exception as exc:
        logger.error(f"Failed to generate PDF for project {project_id}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report")

    safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in project_name).strip() or "SpecSharp_Project"
    filename = f"{safe_name.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    pdf_bytes = pdf_buffer.getvalue()

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/scope/projects/{project_id}/dealshield/pdf")
async def export_dealshield_pdf(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Generate a DealShield PDF report for a project."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project and project_id.isdigit():
        project = db.query(Project).filter(Project.id == int(project_id)).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    payload = _resolve_project_payload(project)
    profile_id = payload.get("dealshield_tile_profile")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise HTTPException(status_code=400, detail="DealShield not available for this project")

    try:
        profile = get_dealshield_profile(profile_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        view_model = build_dealshield_view_model(project.project_id or project_id, payload, profile)
        pdf_buffer = pdf_export_service.generate_dealshield_pdf(view_model)
    except DealShieldResolutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Failed to generate DealShield PDF for project {project_id}: {exc}")
        raise HTTPException(status_code=500, detail="Failed to generate DealShield PDF report") from exc

    filename = f"DealShield_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
    pdf_bytes = pdf_buffer.getvalue()

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

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


def _resolve_project_payload(project: Project) -> Dict[str, Any]:
    project_payload = format_project_response(project)
    calculation_data = project_payload.get("calculation_data")
    if isinstance(calculation_data, dict) and calculation_data:
        return calculation_data
    scope_data = project_payload.get("scope_data")
    if isinstance(scope_data, dict) and scope_data:
        return scope_data
    cost_data = project_payload.get("cost_data")
    if isinstance(cost_data, dict) and cost_data:
        return cost_data
    return {}


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

    # Derive simple scope_items from trade data if not already present
    scope_items = calculation_data.get('scope_items')
    if not scope_items:
        derived_scope_items = []

        if isinstance(trade_data, dict) and trade_data:
            # V2 format – use trade_breakdown dict
            for trade_name, amount in trade_data.items():
                display_name = trade_name.replace('_', ' ').title()
                derived_scope_items.append({
                    'trade': display_name,
                    'systems': [{
                        'name': display_name,
                        'quantity': 1,
                        'unit': 'LUMP SUM',
                        'unit_cost': amount,
                        'total_cost': amount
                    }]
                })
        elif categories:
            # V1 fallback – use categories list
            for category in categories:
                if not isinstance(category, dict) or 'name' not in category:
                    continue
                display_name = category['name']
                value = category.get('value', 0)
                derived_scope_items.append({
                    'trade': display_name,
                    'systems': [{
                        'name': display_name,
                        'quantity': 1,
                        'unit': 'LUMP SUM',
                        'unit_cost': value,
                        'total_cost': value
                    }]
                })

        if derived_scope_items:
            scope_items = derived_scope_items
            calculation_data['scope_items'] = derived_scope_items
    else:
        # Ensure scope_items is at least a list
        if not isinstance(scope_items, list):
            scope_items = []
            calculation_data['scope_items'] = scope_items
    
    # Extract subtype from calculation data
    subtype = calculation_data.get('project_info', {}).get('subtype', '')
    if not subtype and calculation_data.get('parsed_input'):
        subtype = calculation_data.get('parsed_input', {}).get('subtype', '')
    
    # Stable project classification for all frontend consumers
    calc_project_class = (calculation_data.get("project_info") or {}).get("project_class")
    stored_req_class = (calculation_data.get("request_data") or {}).get("project_classification")
    db_class = getattr(project, "project_classification", None)

    project_classification = (
        db_class
        or stored_req_class
        or calc_project_class
        or "ground_up"
    )
    if hasattr(project_classification, "value"):
        project_classification = project_classification.value
    project_classification = str(project_classification)

    request_data = calculation_data.get("request_data") or calculation_data.get("parsed_input") or {}
    if not isinstance(request_data, dict):
        request_data = {}

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
        
        # Scope items derived from trades
        'scope_items': calculation_data.get('scope_items', []),
        
        # Building info
        'building_type': project.building_type,
        'buildingType': project.building_type,
        'occupancy_type': project.occupancy_type,
        'occupancyType': project.occupancy_type,
        'subtype': subtype,
        # Project class (stable)
        "project_classification": project_classification,
        "projectClassification": project_classification,
        
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
        # Request data hydration (for UI + PDF + legacy)
        "request_data": request_data,
        
        # Success flag
        'success': True
    }
