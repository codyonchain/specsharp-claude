from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.db.team_models import team_members
# Import markup models to ensure they're loaded
from app.db.markup_models import UserMarkupSettings, ProjectMarkupOverrides


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OAuth fields
    oauth_provider = Column(String, nullable=True)  # 'google'
    oauth_id = Column(String, nullable=True)  # Unique ID from OAuth provider
    profile_picture = Column(String, nullable=True)  # Profile picture URL
    
    # Team association
    current_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    
    # Personal subscription (legacy - will migrate to team-based)
    estimate_count = Column(Integer, default=0)
    is_subscribed = Column(Boolean, default=False)
    subscription_status = Column(String, default="trial")  # trial, active, cancelled, expired
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_started_at = Column(DateTime(timezone=True), nullable=True)
    subscription_ends_at = Column(DateTime(timezone=True), nullable=True)
    has_completed_onboarding = Column(Boolean, default=False)
    
    # Relationships
    projects = relationship("Project", back_populates="user", foreign_keys="Project.user_id")
    current_team = relationship("Team", foreign_keys=[current_team_id])
    owned_teams = relationship("Team", back_populates="owner", foreign_keys="Team.owner_id")
    teams = relationship("Team", secondary=team_members, back_populates="members")
    created_projects = relationship("Project", back_populates="created_by", foreign_keys="Project.created_by_id")
    markup_settings = relationship("UserMarkupSettings", back_populates="user", uselist=False)


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    scenario_name = Column(String, nullable=True)  # For scenario comparisons (e.g., "Conservative", "Aggressive")
    description = Column(Text, nullable=True)  # Original input description
    project_type = Column(String, nullable=False)
    project_classification = Column(String, nullable=False, default='ground_up')  # ground_up, addition, renovation
    building_type = Column(String, nullable=True)  # Specific building type (hospital, school, etc.)
    occupancy_type = Column(String, nullable=True)  # Same as building_type for consistency
    square_footage = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    climate_zone = Column(String, nullable=True)
    num_floors = Column(Integer, default=1)
    ceiling_height = Column(Float, default=9.0)
    
    # Cost components - store all separately for consistency
    subtotal = Column(Float, nullable=True)  # Base construction cost
    contingency_percentage = Column(Float, default=10.0)  # Contingency percentage
    contingency_amount = Column(Float, nullable=True)  # Contingency amount
    total_cost = Column(Float, nullable=False)  # Final total (subtotal + contingency)
    cost_per_sqft = Column(Float, nullable=True)  # Total cost / square footage
    
    scope_data = Column(Text, nullable=False)  # Full scope response JSON
    cost_data = Column(Text, nullable=True)  # Detailed cost breakdown JSON
    
    # Legacy user association (for migration)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Team associations
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects", foreign_keys=[user_id])
    team = relationship("Team", back_populates="projects")
    created_by = relationship("User", back_populates="created_projects", foreign_keys=[created_by_id])
    floor_plans = relationship("FloorPlan", back_populates="project")
    markup_overrides = relationship("ProjectMarkupOverrides", back_populates="project", uselist=False)
    scenarios = relationship("ProjectScenario", back_populates="project", cascade="all, delete-orphan")


class FloorPlan(Base):
    __tablename__ = "floor_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    floor_plan_id = Column(String, unique=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    total_area = Column(Float, nullable=False)
    efficiency_ratio = Column(Float, nullable=False)
    svg_data = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    floor_plan_data = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="floor_plans")