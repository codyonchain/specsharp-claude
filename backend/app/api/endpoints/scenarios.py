"""API endpoints for project scenario management and comparison"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user_with_cookie
from app.db.models import User, Project
from app.models.scenario import ProjectScenario, ScenarioComparison, ScenarioModification, SCENARIO_MODIFICATIONS
from app.services.scenario_service import ScenarioService
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioComparisonRequest,
    ScenarioComparisonResponse,
    ScenarioExportRequest
)

router = APIRouter()
scenario_service = ScenarioService()


@router.post("/projects/{project_id}/scenarios", response_model=ScenarioResponse)
async def create_scenario(
    request: Request,
    project_id: str,
    scenario_data: ScenarioCreate,
    db: Session = Depends(get_db)
):
    """Create a new scenario from a base project"""
    
    # Get the base project (temporary - no auth for testing)
    project = db.query(Project).filter(
        Project.project_id == project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create the scenario
    scenario = scenario_service.create_scenario(
        db=db,
        project=project,
        name=scenario_data.name,
        description=scenario_data.description,
        modifications=scenario_data.modifications,
        user_id=project.user_id  # Use project owner's ID for testing
    )
    
    return scenario


@router.get("/projects/{project_id}/scenarios", response_model=List[ScenarioResponse])
async def list_scenarios(
    request: Request,
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get all scenarios for a project"""
    
    # For testing - get any project with this ID
    project = db.query(Project).filter(
        Project.project_id == project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all scenarios including the base
    scenarios = db.query(ProjectScenario).filter(
        ProjectScenario.project_id == project.id
    ).order_by(ProjectScenario.created_at).all()
    
    # If no scenarios exist, create the base scenario from current project
    if not scenarios:
        base_scenario = scenario_service.create_base_scenario(db, project, project.user_id)
        scenarios = [base_scenario]
    
    return scenarios


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    request: Request,
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Get a specific scenario"""
    
    scenario = db.query(ProjectScenario).join(Project).filter(
        ProjectScenario.id == scenario_id,
        Project.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    return scenario


@router.put("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    request: Request,
    scenario_id: str,
    scenario_update: ScenarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Update a scenario's modifications and recalculate"""
    
    scenario = db.query(ProjectScenario).join(Project).filter(
        ProjectScenario.id == scenario_id,
        Project.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if scenario.is_base:
        raise HTTPException(status_code=400, detail="Cannot modify base scenario")
    
    # Update and recalculate
    updated_scenario = scenario_service.update_scenario(
        db=db,
        scenario=scenario,
        modifications=scenario_update.modifications,
        name=scenario_update.name,
        description=scenario_update.description
    )
    
    return updated_scenario


@router.delete("/scenarios/{scenario_id}")
async def delete_scenario(
    request: Request,
    scenario_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Delete a scenario"""
    
    scenario = db.query(ProjectScenario).join(Project).filter(
        ProjectScenario.id == scenario_id,
        Project.user_id == current_user.id
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    if scenario.is_base:
        raise HTTPException(status_code=400, detail="Cannot delete base scenario")
    
    db.delete(scenario)
    db.commit()
    
    return {"message": "Scenario deleted successfully"}


@router.post("/projects/{project_id}/compare", response_model=ScenarioComparisonResponse)
async def compare_scenarios(
    request: Request,
    project_id: str,
    comparison_request: ScenarioComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Generate side-by-side comparison of scenarios"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the scenarios
    scenarios = db.query(ProjectScenario).filter(
        ProjectScenario.id.in_(comparison_request.scenario_ids),
        ProjectScenario.project_id == project.id
    ).all()
    
    if len(scenarios) != len(comparison_request.scenario_ids):
        raise HTTPException(status_code=404, detail="One or more scenarios not found")
    
    # Generate comparison
    comparison = scenario_service.compare_scenarios(
        scenarios=scenarios,
        comparison_name=comparison_request.name
    )
    
    # Save comparison to database
    db_comparison = ScenarioComparison(
        project_id=project.id,
        scenario_id=scenarios[0].id,  # Primary scenario
        comparison_name=comparison_request.name,
        scenario_ids=comparison_request.scenario_ids,
        metrics_comparison=comparison.metrics_comparison,
        winner_by_metric=comparison.winner_by_metric,
        cost_deltas=comparison.cost_deltas,
        roi_deltas=comparison.roi_deltas,
        timeline_deltas=comparison.timeline_deltas,
        created_by=current_user.id
    )
    
    db.add(db_comparison)
    db.commit()
    
    return comparison


@router.post("/projects/{project_id}/export-comparison")
async def export_comparison(
    request: Request,
    project_id: str,
    export_request: ScenarioExportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Export scenario comparison as PDF, Excel, or PowerPoint"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the scenarios
    scenarios = db.query(ProjectScenario).filter(
        ProjectScenario.id.in_(export_request.scenario_ids),
        ProjectScenario.project_id == project.id
    ).all()
    
    if not scenarios:
        raise HTTPException(status_code=404, detail="Scenarios not found")
    
    # Generate export based on format
    if export_request.format == "pdf":
        export_data = scenario_service.export_comparison_pdf(
            scenarios=scenarios,
            project=project
        )
        content_type = "application/pdf"
        filename = f"{project.name}_scenario_comparison.pdf"
        
    elif export_request.format == "excel":
        export_data = scenario_service.export_comparison_excel(
            scenarios=scenarios,
            project=project
        )
        content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = f"{project.name}_scenario_comparison.xlsx"
        
    elif export_request.format == "pptx":
        export_data = scenario_service.export_comparison_pptx(
            scenarios=scenarios,
            project=project
        )
        content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = f"{project.name}_scenario_comparison.pptx"
        
    else:
        raise HTTPException(status_code=400, detail="Invalid export format")
    
    # Update export tracking
    comparison = db.query(ScenarioComparison).filter(
        ScenarioComparison.project_id == project.id,
        ScenarioComparison.scenario_ids.contains(export_request.scenario_ids)
    ).first()
    
    if comparison:
        comparison.last_exported_at = datetime.utcnow()
        comparison.export_count = (comparison.export_count or 0) + 1
        db.commit()
    
    return {
        "data": export_data,
        "content_type": content_type,
        "filename": filename
    }


@router.get("/projects/{project_id}/modification-options")
async def get_modification_options(
    request: Request,
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Get available modification options for a project's building type"""
    
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get the building type from project
    building_type = project.building_type or project.project_type
    
    # Return modification options for this building type
    options = SCENARIO_MODIFICATIONS.get(building_type, {})
    
    return {
        "building_type": building_type,
        "modification_options": options
    }


@router.post("/projects/{project_id}/calculate-scenario")
async def calculate_scenario_impact(
    request: Request,
    project_id: str,
    modifications: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Calculate the impact of scenario modifications without saving"""
    
    # Get the base project
    project = db.query(Project).filter(
        Project.project_id == project_id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate the modified project costs
    modified_results = scenario_service.calculate_scenario_impact(
        project=project,
        modifications=modifications.get("modifications", {})
    )
    
    return modified_results