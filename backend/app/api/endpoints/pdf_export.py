from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.db.database import get_db
from app.db.models import Project, User
from app.api.endpoints.auth import get_current_user_with_cookie
from app.services.pdf_export_service import pdf_export_service
from app.services.excel_export_service_v2 import excel_export_service_v2


router = APIRouter()


@router.get("/project/{project_id}/pdf")
async def export_project_pdf(
    project_id: str,
    client_name: str = Query(None, description="Client name for the report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Export project as professional PDF report"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    
    # Generate PDF file
    pdf_file = pdf_export_service.generate_professional_pdf(scope_data, client_name)
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_professional_estimate_{project_id}.pdf"
    
    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/project/{project_id}/excel-pro")
async def export_project_excel_professional(
    project_id: str,
    client_name: str = Query(None, description="Client name for the report"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_cookie)
):
    """Export project as professional Excel report with enhanced formatting"""
    # Get project
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    
    # Generate professional Excel file
    excel_file = excel_export_service_v2.generate_professional_excel(scope_data, client_name)
    
    # Create filename
    filename = f"{project.name.replace(' ', '_')}_professional_estimate_{project_id}.xlsx"
    
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )