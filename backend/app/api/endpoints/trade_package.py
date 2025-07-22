from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from app.services.trade_package_service import trade_package_service
from app.api.endpoints.auth import get_current_user
from app.api.endpoints.scope import get_project
from app.db.database import get_db
from sqlalchemy.orm import Session
import json
import logging
import traceback

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{project_id}/{trade}")
async def generate_trade_package(
    project_id: str,
    trade: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate a trade-specific package including PDF, CSV, and schematic"""
    
    logger.error(f"=== GENERATE PACKAGE CALLED: {trade} for {project_id} ===")
    
    try:
        # Validate trade
        valid_trades = ['electrical', 'plumbing', 'hvac', 'structural', 'general']
        if trade.lower() not in valid_trades:
            raise HTTPException(status_code=400, detail=f"Invalid trade. Must be one of: {', '.join(valid_trades)}")
        
        # Get project data
        logger.error(f"Fetching project data for ID: {project_id}")
        project_data = await get_project(project_id, db, current_user)
        
        # Log project details
        if project_data:
            logger.error(f"Project found: {getattr(project_data, 'name', 'Unknown')}")
            logger.error(f"Project type: {getattr(project_data, 'building_type', 'Unknown')}")
            logger.error(f"Project state: {getattr(project_data, 'state', 'Unknown')}")
            logger.error(f"Square footage: {getattr(project_data, 'square_footage', 'Unknown')}")
            
            # Log cost breakdown
            cost_breakdown = getattr(project_data, 'cost_breakdown', {})
            if isinstance(cost_breakdown, str):
                try:
                    cost_breakdown = json.loads(cost_breakdown)
                except:
                    cost_breakdown = {}
            
            electrical_cost = cost_breakdown.get('electrical', {}).get('total', 0)
            logger.error(f"Electrical cost in cost_breakdown: ${electrical_cost:,.2f}")
            
            # Check for electrical_cost attribute
            if hasattr(project_data, 'electrical_cost'):
                logger.error(f"Electrical cost attribute: ${getattr(project_data, 'electrical_cost', 0):,.2f}")
        else:
            logger.error("Project NOT FOUND")
        
        # Convert to dict if it's a Pydantic model
        if hasattr(project_data, 'model_dump'):
            project_dict = project_data.model_dump()
        else:
            project_dict = dict(project_data)
        
        logger.error(f"Project dict keys: {list(project_dict.keys())}")
        
        # Log electrical specific data
        if trade.lower() == 'electrical':
            logger.error("=== ELECTRICAL PACKAGE REQUESTED ===")
            if 'cost_breakdown' in project_dict:
                cb = project_dict['cost_breakdown']
                if isinstance(cb, str):
                    cb = json.loads(cb)
                logger.error(f"Electrical breakdown: {json.dumps(cb.get('electrical', {}), indent=2)}")
        
        # Generate trade package
        logger.error(f"Calling trade_package_service.generate_trade_package")
        package = trade_package_service.generate_trade_package(project_dict, trade)
        
        logger.error(f"Package generated successfully")
        return {
            'success': True,
            'package': package
        }
        
    except Exception as e:
        logger.error(f"PACKAGE GENERATION FAILED: {str(e)}")
        logger.error(f"Trade parameter: {trade}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
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