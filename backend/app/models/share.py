"""
Pydantic models for share functionality
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional


class ShareResponse(BaseModel):
    """Response model for creating a share link"""
    share_id: str
    share_url: str
    expires_at: datetime
    created_at: datetime


class SharedProjectResponse(BaseModel):
    """Response model for viewing a shared project"""
    share_id: str
    project_id: str
    project_name: str
    shared_by: str
    shared_at: datetime
    expires_at: datetime
    project_data: Dict[str, Any]
    view_count: int