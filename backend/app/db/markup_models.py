from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


class UserMarkupSettings(Base):
    """Store user's default markup preferences"""
    __tablename__ = "user_markup_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Global markups
    global_overhead_percent = Column(Float, default=10.0)  # Default 10% overhead
    global_profit_percent = Column(Float, default=10.0)    # Default 10% profit
    
    # Self-perform vs subcontractor markups
    self_perform_markup_percent = Column(Float, default=15.0)      # When doing work in-house
    subcontractor_markup_percent = Column(Float, default=20.0)     # When subcontracting
    
    # Per-trade overrides (JSON object with trade names as keys)
    # Example: {"electrical": {"overhead": 12, "profit": 12}, "plumbing": {"overhead": 8, "profit": 10}}
    trade_specific_markups = Column(JSON, default={})
    
    # Display preferences
    show_markups_in_pdf = Column(Boolean, default=True)
    show_markup_breakdown = Column(Boolean, default=False)  # Show overhead/profit separately
    
    user = relationship("User", back_populates="markup_settings")


class ProjectMarkupOverrides(Base):
    """Store project-specific markup overrides"""
    __tablename__ = "project_markup_overrides"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True)
    
    # Project-specific overrides (if different from user defaults)
    override_global_overhead = Column(Float, nullable=True)
    override_global_profit = Column(Float, nullable=True)
    override_self_perform = Column(Float, nullable=True)
    override_subcontractor = Column(Float, nullable=True)
    
    # Per-trade overrides for this project
    trade_overrides = Column(JSON, default={})
    
    # Which trades are self-performed vs subcontracted
    # Example: {"electrical": "subcontract", "carpentry": "self_perform"}
    trade_performance_type = Column(JSON, default={})
    
    project = relationship("Project", back_populates="markup_overrides")