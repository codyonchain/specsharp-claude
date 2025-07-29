"""
Share Models for SpecSharp
Handles project sharing functionality
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.db.database import Base


class ProjectShare(Base):
    """Model for shared project links"""
    __tablename__ = "project_shares"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.project_id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    view_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    project = relationship("Project", backref="shares")
    created_by = relationship("User", backref="created_shares")
    
    @property
    def is_expired(self):
        """Check if the share link has expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def share_url(self):
        """Generate the full share URL"""
        # This will be configured from environment
        base_url = "https://app.specsharp.ai"
        return f"{base_url}/share/{self.id}"
    
    def increment_views(self):
        """Increment the view counter"""
        self.view_count += 1