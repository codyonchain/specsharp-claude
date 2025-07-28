from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pydantic import BaseModel

from app.db.database import get_db
from app.api.endpoints.auth import get_current_user
from app.services.markup_service import markup_service


router = APIRouter()


class UserMarkupSettingsUpdate(BaseModel):
    global_overhead_percent: Optional[float] = None
    global_profit_percent: Optional[float] = None
    self_perform_markup_percent: Optional[float] = None
    subcontractor_markup_percent: Optional[float] = None
    trade_specific_markups: Optional[Dict] = None
    show_markups_in_pdf: Optional[bool] = None
    show_markup_breakdown: Optional[bool] = None


class ProjectMarkupOverridesUpdate(BaseModel):
    override_global_overhead: Optional[float] = None
    override_global_profit: Optional[float] = None
    override_self_perform: Optional[float] = None
    override_subcontractor: Optional[float] = None
    trade_overrides: Optional[Dict] = None
    trade_performance_type: Optional[Dict] = None


@router.get("/user/settings")
async def get_user_markup_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's markup settings"""
    settings = markup_service.get_user_markup_settings(db, current_user["id"])
    return {
        "global_overhead_percent": settings.global_overhead_percent,
        "global_profit_percent": settings.global_profit_percent,
        "self_perform_markup_percent": settings.self_perform_markup_percent,
        "subcontractor_markup_percent": settings.subcontractor_markup_percent,
        "trade_specific_markups": settings.trade_specific_markups or {},
        "show_markups_in_pdf": settings.show_markups_in_pdf,
        "show_markup_breakdown": settings.show_markup_breakdown
    }


@router.put("/user/settings")
async def update_user_markup_settings(
    settings_update: UserMarkupSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update user's markup settings"""
    update_dict = settings_update.dict(exclude_unset=True)
    settings = markup_service.update_user_markup_settings(db, current_user["id"], update_dict)
    
    return {
        "message": "Settings updated successfully",
        "settings": {
            "global_overhead_percent": settings.global_overhead_percent,
            "global_profit_percent": settings.global_profit_percent,
            "self_perform_markup_percent": settings.self_perform_markup_percent,
            "subcontractor_markup_percent": settings.subcontractor_markup_percent,
            "trade_specific_markups": settings.trade_specific_markups or {},
            "show_markups_in_pdf": settings.show_markups_in_pdf,
            "show_markup_breakdown": settings.show_markup_breakdown
        }
    }


@router.get("/project/{project_id}/overrides")
async def get_project_markup_overrides(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get project-specific markup overrides"""
    # First verify the user owns this project
    from app.db.models import Project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    overrides = markup_service.get_project_markup_overrides(db, project.id)
    
    if not overrides:
        return {
            "has_overrides": False,
            "overrides": {}
        }
    
    return {
        "has_overrides": True,
        "overrides": {
            "override_global_overhead": overrides.override_global_overhead,
            "override_global_profit": overrides.override_global_profit,
            "override_self_perform": overrides.override_self_perform,
            "override_subcontractor": overrides.override_subcontractor,
            "trade_overrides": overrides.trade_overrides or {},
            "trade_performance_type": overrides.trade_performance_type or {}
        }
    }


@router.put("/project/{project_id}/overrides")
async def update_project_markup_overrides(
    project_id: str,
    overrides_update: ProjectMarkupOverridesUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update project-specific markup overrides"""
    # First verify the user owns this project
    from app.db.models import Project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_dict = overrides_update.dict(exclude_unset=True)
    overrides = markup_service.update_project_markup_overrides(db, project.id, update_dict)
    
    return {
        "message": "Project overrides updated successfully",
        "overrides": {
            "override_global_overhead": overrides.override_global_overhead,
            "override_global_profit": overrides.override_global_profit,
            "override_self_perform": overrides.override_self_perform,
            "override_subcontractor": overrides.override_subcontractor,
            "trade_overrides": overrides.trade_overrides or {},
            "trade_performance_type": overrides.trade_performance_type or {}
        }
    }


@router.post("/project/{project_id}/apply-markups")
async def apply_markups_to_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Apply current markup settings to a project and return the marked up scope"""
    # First verify the user owns this project
    from app.db.models import Project
    import json
    
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Load the scope data
    scope_data = json.loads(project.scope_data)
    
    # Apply markups
    marked_up_scope = markup_service.apply_markup_to_scope(
        scope_data,
        db,
        current_user["id"],
        project.id
    )
    
    return marked_up_scope


@router.get("/trades")
async def get_available_trades():
    """Get list of available trades for markup configuration"""
    return {
        "trades": list(markup_service.TRADE_CATEGORIES.keys()),
        "trade_categories": markup_service.TRADE_CATEGORIES
    }