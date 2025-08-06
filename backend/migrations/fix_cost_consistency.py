#!/usr/bin/env python3
"""
Migration to fix cost consistency across all projects.
Ensures subtotal, contingency, and total values are properly stored.
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import Project
from app.core.config import settings

def fix_cost_consistency():
    """
    Recalculate and store cost components for all existing projects
    to ensure consistency between dashboard and detail views.
    """
    
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # First, add columns if they don't exist
        try:
            db.execute(text("""
                ALTER TABLE projects 
                ADD COLUMN IF NOT EXISTS subtotal FLOAT,
                ADD COLUMN IF NOT EXISTS contingency_percentage FLOAT DEFAULT 10.0,
                ADD COLUMN IF NOT EXISTS contingency_amount FLOAT
            """))
            db.commit()
            print("✓ Database columns added/verified")
        except Exception as e:
            print(f"Note: Column addition skipped (may already exist): {e}")
            db.rollback()
        
        # Get all projects
        projects = db.query(Project).all()
        print(f"\nProcessing {len(projects)} projects...")
        
        fixed_count = 0
        for project in projects:
            try:
                # Parse the stored scope data
                scope_data = json.loads(project.scope_data) if project.scope_data else {}
                
                # Extract cost components from scope data
                subtotal = scope_data.get('subtotal', 0)
                contingency_percentage = scope_data.get('contingency_percentage', 10.0)
                contingency_amount = scope_data.get('contingency_amount', 0)
                total_cost = scope_data.get('total_cost', 0)
                cost_per_sqft = scope_data.get('cost_per_sqft', 0)
                
                # If scope data has categories, recalculate from them
                if 'categories' in scope_data and scope_data['categories']:
                    # Recalculate subtotal from categories
                    calc_subtotal = sum(
                        sum(system.get('total_cost', 0) for system in cat.get('systems', []))
                        for cat in scope_data['categories']
                    )
                    if calc_subtotal > 0:
                        subtotal = calc_subtotal
                    
                    # Recalculate contingency
                    contingency_amount = subtotal * (contingency_percentage / 100)
                    
                    # Recalculate total
                    total_cost = subtotal + contingency_amount
                    
                    # Recalculate cost per SF
                    if project.square_footage > 0:
                        cost_per_sqft = total_cost / project.square_footage
                
                # Update the project with consistent values
                project.subtotal = subtotal
                project.contingency_percentage = contingency_percentage
                project.contingency_amount = contingency_amount
                
                # Only update total_cost and cost_per_sqft if they're currently 0 or None
                # to preserve any manual adjustments
                if not project.total_cost or project.total_cost == 0:
                    project.total_cost = total_cost
                if not project.cost_per_sqft or project.cost_per_sqft == 0:
                    project.cost_per_sqft = cost_per_sqft
                
                # Also update the scope_data to ensure consistency
                scope_data['subtotal'] = subtotal
                scope_data['contingency_percentage'] = contingency_percentage
                scope_data['contingency_amount'] = contingency_amount
                scope_data['total_cost'] = project.total_cost
                scope_data['cost_per_sqft'] = project.cost_per_sqft
                project.scope_data = json.dumps(scope_data)
                
                print(f"✓ Fixed {project.name}:")
                print(f"  - Subtotal: ${subtotal:,.2f}")
                print(f"  - Contingency ({contingency_percentage}%): ${contingency_amount:,.2f}")
                print(f"  - Total: ${project.total_cost:,.2f}")
                print(f"  - Cost/SF: ${project.cost_per_sqft:.2f}")
                
                fixed_count += 1
                
            except Exception as e:
                print(f"✗ Error processing project {project.name}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"\n✓ Successfully fixed {fixed_count} projects")
        
        # Verify consistency
        print("\n" + "="*60)
        print("VERIFICATION - Sample Projects:")
        print("="*60)
        
        sample_projects = db.query(Project).limit(5).all()
        for project in sample_projects:
            scope_data = json.loads(project.scope_data) if project.scope_data else {}
            print(f"\n{project.name}:")
            print(f"  Database total_cost: ${project.total_cost:,.2f}")
            print(f"  Scope data total_cost: ${scope_data.get('total_cost', 0):,.2f}")
            print(f"  Match: {'✓' if abs(project.total_cost - scope_data.get('total_cost', 0)) < 0.01 else '✗'}")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting cost consistency migration...")
    print("="*60)
    fix_cost_consistency()
    print("\nMigration complete!")