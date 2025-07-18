from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    projects = relationship("Project", back_populates="user")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    project_type = Column(String, nullable=False)
    square_footage = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    climate_zone = Column(String, nullable=True)
    num_floors = Column(Integer, default=1)
    ceiling_height = Column(Float, default=9.0)
    total_cost = Column(Float, nullable=False)
    scope_data = Column(Text, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="projects")
    floor_plans = relationship("FloorPlan", back_populates="project")


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