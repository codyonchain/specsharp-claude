from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.db.database import get_db
from app.db.models import Project
from app.api.endpoints.auth import get_current_user
from app.services.excel_export_service import excel_export_service


router = APIRouter()


@router.get("/project/{project_id}")
async def export_project_excel(
    project_id: str,
    include_markups: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export full project data as Excel file with multiple sheets"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    
    # Generate Excel file
    excel_file = excel_export_service.generate_excel_report(scope_data, include_markups)
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_estimate_{project_id}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/project/{project_id}/trade/{trade_name}")
async def export_trade_excel(
    project_id: str,
    trade_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export specific trade package as Excel file"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user["id"]
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