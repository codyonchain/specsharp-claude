"""
Share API endpoints
Handles project sharing functionality
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.db.database import get_db
from app.db.models import Project, User
from app.db.share_models import ProjectShare
from app.api.endpoints.auth import get_current_user
from app.models.share import ShareResponse, SharedProjectResponse
import json

router = APIRouter()

# Rate limiting - simple in-memory store (use Redis in production)
share_creation_cache = {}
RATE_LIMIT_SECONDS = 60  # 1 minute
MAX_SHARES_PER_MINUTE = 5


@router.post("/project/{project_id}/share", response_model=ShareResponse)
async def create_share_link(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a shareable link for a project"""
    
    # Rate limiting check
    user_key = f"user_{current_user.id}"
    now = datetime.utcnow()
    
    if user_key in share_creation_cache:
        user_shares = share_creation_cache[user_key]
        # Remove old entries
        user_shares = [ts for ts in user_shares if (now - ts).seconds < RATE_LIMIT_SECONDS]
        share_creation_cache[user_key] = user_shares
        
        if len(user_shares) >= MAX_SHARES_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many share links created. Please wait a minute."
            )
    else:
        share_creation_cache[user_key] = []
    
    # Get project and verify ownership
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have permission to share it"
        )
    
    # Create share link
    project_share = ProjectShare(
        project_id=project_id,
        created_by_id=current_user.id
    )
    
    db.add(project_share)
    db.commit()
    db.refresh(project_share)
    
    # Update rate limit cache
    share_creation_cache[user_key].append(now)
    
    # Get base URL from environment or config
    import os
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    share_url = f"{base_url}/share/{project_share.id}"
    
    return ShareResponse(
        share_id=str(project_share.id),
        share_url=share_url,
        expires_at=project_share.expires_at,
        created_at=project_share.created_at
    )


@router.get("/share/{share_id}", response_model=SharedProjectResponse)
async def get_shared_project(
    share_id: str,
    db: Session = Depends(get_db)
):
    """Get a shared project by share ID (no authentication required)"""
    
    try:
        share_uuid = uuid.UUID(share_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid share ID format"
        )
    
    # Get share link
    project_share = db.query(ProjectShare).filter(
        ProjectShare.id == share_uuid
    ).first()
    
    if not project_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    # Check if expired
    if project_share.is_expired:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This share link has expired"
        )
    
    # Check if active
    if not project_share.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This share link has been deactivated"
        )
    
    # Get project
    project = project_share.project
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Increment view count
    project_share.increment_views()
    db.commit()
    
    # Parse scope data
    scope_data = json.loads(project.scope_data) if project.scope_data else {}
    
    # Get company name from creator
    company_name = project_share.created_by.full_name or "SpecSharp User"
    if project_share.created_by.current_team:
        company_name = project_share.created_by.current_team.name
    
    return SharedProjectResponse(
        share_id=str(project_share.id),
        project_id=project.project_id,
        project_name=project.name,
        shared_by=company_name,
        shared_at=project_share.created_at,
        expires_at=project_share.expires_at,
        project_data=scope_data,
        view_count=project_share.view_count
    )


@router.get("/project/{project_id}/shares")
async def list_project_shares(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all share links for a project"""
    
    # Verify project ownership
    project = db.query(Project).filter(
        Project.project_id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get all shares
    shares = db.query(ProjectShare).filter(
        ProjectShare.project_id == project_id
    ).order_by(ProjectShare.created_at.desc()).all()
    
    # Get base URL
    import os
    base_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    return [
        {
            "share_id": str(share.id),
            "share_url": f"{base_url}/share/{share.id}",
            "created_at": share.created_at,
            "expires_at": share.expires_at,
            "view_count": share.view_count,
            "is_active": share.is_active,
            "is_expired": share.is_expired
        }
        for share in shares
    ]


@router.delete("/share/{share_id}")
async def deactivate_share(
    share_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a share link"""
    
    try:
        share_uuid = uuid.UUID(share_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid share ID format"
        )
    
    # Get share and verify ownership
    project_share = db.query(ProjectShare).filter(
        ProjectShare.id == share_uuid,
        ProjectShare.created_by_id == current_user.id
    ).first()
    
    if not project_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found or you don't have permission"
        )
    
    # Deactivate
    project_share.is_active = False
    db.commit()
    
    return {"message": "Share link deactivated successfully"}