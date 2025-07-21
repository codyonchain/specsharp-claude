from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.services.trade_package_service import trade_package_service
from app.api.endpoints.auth import get_current_user
from app.api.endpoints.scope import get_project
from app.db.database import get_db
from sqlalchemy.orm import Session
import json

router = APIRouter()


@router.post("/generate/{project_id}/{trade}")
async def generate_trade_package(
    project_id: str,
    trade: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate a trade-specific package including PDF, CSV, and schematic"""
    
    try:
        # Validate trade
        valid_trades = ['electrical', 'plumbing', 'hvac', 'structural', 'general']
        if trade.lower() not in valid_trades:
            raise HTTPException(status_code=400, detail=f"Invalid trade. Must be one of: {', '.join(valid_trades)}")
        
        # Get project data
        project_data = await get_project(project_id, db, current_user)
        
        # Convert to dict if it's a Pydantic model
        if hasattr(project_data, 'model_dump'):
            project_dict = project_data.model_dump()
        else:
            project_dict = dict(project_data)
        
        # Generate trade package
        package = trade_package_service.generate_trade_package(project_dict, trade)
        
        return {
            'success': True,
            'package': package
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating trade package: {str(e)}")


@router.get("/preview/{project_id}/{trade}")
async def preview_trade_package(
    project_id: str,
    trade: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a preview of the trade package without generating files"""
    
    try:
        # Validate trade
        valid_trades = ['electrical', 'plumbing', 'hvac', 'structural', 'general']
        if trade.lower() not in valid_trades:
            raise HTTPException(status_code=400, detail=f"Invalid trade. Must be one of: {', '.join(valid_trades)}")
        
        # Get project data
        project_data = await get_project(project_id, db, current_user)
        
        # Convert to dict if it's a Pydantic model
        if hasattr(project_data, 'model_dump'):
            project_dict = project_data.model_dump()
        else:
            project_dict = dict(project_data)
        
        # Generate preview only
        filtered_data = trade_package_service._filter_scope_by_trade(project_dict, trade)
        preview = trade_package_service._generate_preview_data(filtered_data, trade, "")
        
        return {
            'success': True,
            'preview': preview
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")