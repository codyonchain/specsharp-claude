from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import logging

from app.db.database import get_db
from app.db.models import Project, User
from app.api.endpoints.auth import get_current_user_with_cookie
from app.services.excel_export_service import excel_export_service

logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/project/{project_id}")
async def export_project_excel(
    project_id: str,
    include_markups: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Export full project data as Excel file with multiple sheets"""
    logger.info(f"Excel export requested for project {project_id} by user {current_user.id}")
    
    try:
        # Get project
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.user_id == current_user.id
        ).first()
        
        if not project:
            logger.error(f"Project {project_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Parse scope data
        scope_data = json.loads(project.scope_data)
        logger.info(f"Project data loaded successfully, generating Excel file")
        
        # Generate Excel file
        excel_file = excel_export_service.generate_excel_report(scope_data, include_markups)
        logger.info(f"Excel file generated successfully")
        
        # Create filename
        filename = f"{project.name.replace(' ', '_')}_estimate_{project_id}.xlsx"
        
        return StreamingResponse(
            excel_file,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error exporting Excel for project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to export Excel: {str(e)}")


@router.get("/project/{project_id}/trade/{trade_name}")
async def export_trade_excel(
    project_id: str,
    trade_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Export specific trade package as Excel file"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    
    # Find trade data
    trade_data = None
    for category in scope_data.get('categories', []):
        if category['name'].lower() == trade_name.lower():
            trade_data = category
            break
    
    if not trade_data:
        # Check trade summaries
        trade_summaries = scope_data.get('trade_summaries', {})
        if trade_name in trade_summaries:
            # Build trade data from summary
            trade_systems = []
            for category in scope_data.get('categories', []):
                # Map categories to trades
                category_name = category['name'].lower()
                if (trade_name == 'structural' and 'structural' in category_name) or \
                   (trade_name == 'mechanical' and ('mechanical' in category_name or 'hvac' in category_name)) or \
                   (trade_name == 'electrical' and 'electrical' in category_name) or \
                   (trade_name == 'plumbing' and 'plumbing' in category_name) or \
                   (trade_name == 'finishes' and 'finish' in category_name):
                    trade_systems.extend(category.get('systems', []))
                    if not trade_data:
                        trade_data = {
                            'name': trade_name.title(),
                            'systems': trade_systems,
                            'subtotal': category.get('subtotal', 0)
                        }
                        if 'markup_details' in category:
                            trade_data['markup_details'] = category['markup_details']
                    else:
                        trade_data['systems'].extend(category.get('systems', []))
                        trade_data['subtotal'] += category.get('subtotal', 0)
    
    if not trade_data:
        raise HTTPException(status_code=404, detail=f"Trade '{trade_name}' not found in project")
    
    # Generate Excel file
    excel_file = excel_export_service.generate_trade_excel(trade_data, trade_name, scope_data)
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_{trade_name}_package.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/extract/{project_id}/{trade_name}")
async def extract_trade_for_subs(
    project_id: str,
    trade_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Extract trade-specific scope for subcontractors (no pricing)"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    
    # Extract trade-specific data
    trade_data = None
    trade_systems = []
    
    # Look for trade in categories
    for category in scope_data.get('categories', []):
        category_name = category.get('name', '').lower()
        # Map category names to trades
        if (trade_name.lower() == 'mechanical' and 'mechanical' in category_name) or \
           (trade_name.lower() == 'electrical' and 'electrical' in category_name) or \
           (trade_name.lower() == 'plumbing' and 'plumbing' in category_name) or \
           (trade_name.lower() == 'fire protection' and 'fire' in category_name) or \
           (trade_name.lower() == 'structural' and ('structural' in category_name or 'steel' in category_name)) or \
           (trade_name.lower() == 'finishes' and 'finish' in category_name) or \
           (trade_name.lower() == category_name):
            trade_systems.extend(category.get('systems', []))
            if not trade_data:
                trade_data = {
                    'name': trade_name,
                    'systems': trade_systems,
                    'category': category.get('name', trade_name)
                }
            else:
                trade_data['systems'].extend(category.get('systems', []))
    
    if not trade_data:
        raise HTTPException(status_code=404, detail=f"Trade '{trade_name}' not found in project")
    
    # Generate Excel file without pricing
    from app.services.excel_extract_service import excel_extract_service
    excel_file = excel_extract_service.generate_subcontractor_scope(
        trade_data, 
        trade_name, 
        project
    )
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_{trade_name}_Scope_for_Subs.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )