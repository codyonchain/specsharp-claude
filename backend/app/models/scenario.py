"""Project scenario models for comparison engine"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base
import uuid


class ProjectScenario(Base):
    """Model for project scenarios - variations of a base project"""
    __tablename__ = "project_scenarios"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)  # "Luxury Finish", "Standard Build", etc.
    description = Column(Text)
    
    # Store modifications as JSON
    modifications = Column(JSON, default={})
    
    # Calculated results after modifications
    total_cost = Column(Float)
    construction_cost = Column(Float)
    soft_costs = Column(Float)
    cost_per_sqft = Column(Float)
    
    # Financial metrics
    roi = Column(Float)
    npv = Column(Float)
    irr = Column(Float)
    payback_period = Column(Float)
    dscr = Column(Float)
    
    # Revenue metrics
    annual_revenue = Column(Float)
    monthly_revenue = Column(Float)
    noi = Column(Float)
    
    # Building metrics (may be modified)
    square_footage = Column(Float)
    unit_count = Column(Integer)
    finish_level = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    is_base = Column(Boolean, default=False)  # Mark if this is the base scenario
    
    # Store full calculation results for quick retrieval
    calculation_results = Column(JSON)
    
    # Relationships
    project = relationship("Project", back_populates="scenarios")
    comparisons = relationship("ScenarioComparison", back_populates="scenario", cascade="all, delete-orphan")


class ScenarioComparison(Base):
    """Model for storing scenario comparison results"""
    __tablename__ = "scenario_comparisons"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scenario_id = Column(String, ForeignKey("project_scenarios.id"), nullable=False)
    comparison_name = Column(String)
    
    # Store comparison data
    scenario_ids = Column(JSON)  # List of scenario IDs being compared
    metrics_comparison = Column(JSON)  # Dict of metric_name: [values]
    winner_by_metric = Column(JSON)  # Dict of metric: winning_scenario_id
    
    # Delta analysis
    cost_deltas = Column(JSON)  # Cost differences from base
    roi_deltas = Column(JSON)  # ROI differences from base
    timeline_deltas = Column(JSON)  # Timeline impacts
    
    # Export tracking
    last_exported_at = Column(DateTime)
    export_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    project = relationship("Project")
    scenario = relationship("ProjectScenario", back_populates="comparisons")


class ScenarioModification(Base):
    """Track individual modifications in scenarios"""
    __tablename__ = "scenario_modifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_id = Column(String, ForeignKey("project_scenarios.id"), nullable=False)
    
    parameter = Column(String, nullable=False)  # "finish_level", "unit_count", etc.
    original_value = Column(JSON)
    new_value = Column(JSON)
    
    # Impact analysis
    cost_impact = Column(Float)  # Dollar impact
    timeline_impact = Column(Float)  # Days impact
    roi_impact = Column(Float)  # ROI percentage point impact
    impact_description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scenario = relationship("ProjectScenario")


# Define modification options for different building types
SCENARIO_MODIFICATIONS = {
    "multifamily": {
        "finish_level": {
            "options": ["standard", "mid_range", "luxury"],
            "impact": {
                "standard": {"cost_multiplier": 1.0, "roi_adjustment": 0},
                "mid_range": {"cost_multiplier": 1.15, "roi_adjustment": 0.01},
                "luxury": {"cost_multiplier": 1.35, "roi_adjustment": 0.02}
            }
        },
        "unit_count": {
            "min": 50, "max": 500, "step": 10,
            "impact": "linear"  # Cost scales linearly with units
        },
        "parking_ratio": {
            "min": 0.5, "max": 2.0, "step": 0.1,
            "cost_per_space": 25000  # Underground parking cost
        },
        "amenity_package": {
            "options": ["basic", "standard", "premium"],
            "impact": {
                "basic": {"cost_add": 0, "rent_premium": 0},
                "standard": {"cost_add": 500000, "rent_premium": 0.05},
                "premium": {"cost_add": 1500000, "rent_premium": 0.12}
            }
        }
    },
    "restaurant": {
        "kitchen_grade": {
            "options": ["standard", "premium", "michelin"],
            "impact": {
                "standard": {"cost_multiplier": 1.0, "revenue_multiplier": 1.0},
                "premium": {"cost_multiplier": 1.25, "revenue_multiplier": 1.15},
                "michelin": {"cost_multiplier": 1.6, "revenue_multiplier": 1.4}
            }
        },
        "seating_capacity": {
            "min": 50, "max": 300, "step": 10,
            "cost_per_seat": 8000,
            "revenue_per_seat": 25000  # Annual
        },
        "bar_included": {
            "options": [True, False],
            "impact": {
                True: {"cost_add": 150000, "revenue_add": 0.25},
                False: {"cost_add": 0, "revenue_add": 0}
            }
        },
        "outdoor_seating": {
            "options": [True, False],
            "impact": {
                True: {"cost_add": 75000, "capacity_add": 0.3},
                False: {"cost_add": 0, "capacity_add": 0}
            }
        }
    },
    "office": {
        "building_class": {
            "options": ["A", "B", "C"],
            "impact": {
                "A": {"cost_multiplier": 1.3, "rent_psf": 45},
                "B": {"cost_multiplier": 1.0, "rent_psf": 35},
                "C": {"cost_multiplier": 0.85, "rent_psf": 25}
            }
        },
        "floor_count": {
            "min": 1, "max": 50, "step": 1,
            "cost_impact": "nonlinear"  # Economies of scale
        },
        "parking_included": {
            "options": [True, False],
            "impact": {
                True: {"cost_add": 2000000, "rent_premium": 0.08},
                False: {"cost_add": 0, "rent_premium": 0}
            }
        },
        "sustainability_cert": {
            "options": ["none", "LEED_Silver", "LEED_Gold", "LEED_Platinum"],
            "impact": {
                "none": {"cost_multiplier": 1.0, "rent_premium": 0},
                "LEED_Silver": {"cost_multiplier": 1.05, "rent_premium": 0.05},
                "LEED_Gold": {"cost_multiplier": 1.10, "rent_premium": 0.08},
                "LEED_Platinum": {"cost_multiplier": 1.15, "rent_premium": 0.12}
            }
        }
    },
    "healthcare": {
        "facility_type": {
            "options": ["clinic", "hospital", "surgical_center"],
            "impact": {
                "clinic": {"cost_multiplier": 1.0, "revenue_multiplier": 1.0},
                "hospital": {"cost_multiplier": 1.8, "revenue_multiplier": 2.2},
                "surgical_center": {"cost_multiplier": 1.5, "revenue_multiplier": 1.8}
            }
        },
        "bed_count": {
            "min": 10, "max": 500, "step": 10,
            "cost_per_bed": 450000,
            "revenue_per_bed": 550000  # Annual
        },
        "imaging_center": {
            "options": [True, False],
            "impact": {
                True: {"cost_add": 3000000, "revenue_add": 0.35},
                False: {"cost_add": 0, "revenue_add": 0}
            }
        }
    },
    "retail": {
        "anchor_tenant": {
            "options": ["none", "grocery", "department_store", "big_box"],
            "impact": {
                "none": {"cost_multiplier": 1.0, "occupancy": 0.85},
                "grocery": {"cost_multiplier": 1.1, "occupancy": 0.95},
                "department_store": {"cost_multiplier": 1.15, "occupancy": 0.92},
                "big_box": {"cost_multiplier": 0.9, "occupancy": 0.98}
            }
        },
        "tenant_mix": {
            "options": ["local", "regional", "national"],
            "impact": {
                "local": {"rent_multiplier": 0.85, "ti_allowance": 30},
                "regional": {"rent_multiplier": 1.0, "ti_allowance": 50},
                "national": {"rent_multiplier": 1.2, "ti_allowance": 75}
            }
        }
    }
}