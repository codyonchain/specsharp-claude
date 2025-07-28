#!/usr/bin/env python
"""Test what's being stored in the database for hospital projects"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Project
from app.core.config import settings

# Create database connection
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Find recent hospital projects
projects = db.query(Project).filter(
    Project.scope_data.like('%hospital%')
).order_by(Project.created_at.desc()).limit(5).all()

print(f"Found {len(projects)} hospital projects\n")

for project in projects:
    print(f"Project: {project.name}")
    print(f"ID: {project.project_id}")
    print(f"Type: {project.project_type}")
    
    # Parse scope data
    scope_data = json.loads(project.scope_data)
    request_data = scope_data.get('request_data', {})
    
    print(f"Occupancy Type in request_data: {request_data.get('occupancy_type', 'NOT FOUND')}")
    print(f"Square Footage: {request_data.get('square_footage', 0):,}")
    print(f"Floors: {request_data.get('num_floors', 1)}")
    
    # Check for elevators in mechanical
    elevator_count = 0
    for category in scope_data.get('categories', []):
        if category.get('name') == 'Mechanical':
            for system in category.get('systems', []):
                if 'elevator' in system.get('name', '').lower():
                    elevator_count += 1
                    print(f"  ✓ Found elevator: {system['name']}")
    
    if elevator_count == 0:
        print("  ✗ No elevators found in Mechanical category")
    
    print("-" * 50)

db.close()