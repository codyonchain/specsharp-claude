#!/usr/bin/env python3
"""
Database health check - run before deployments to ensure schema sync
"""

import sys
import os
from sqlalchemy import inspect, create_engine
from tabulate import tabulate

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.models import Project, User, FloorPlan
from app.db.database import engine, SessionLocal

def check_schema_sync():
    """Ensure database schema matches SQLAlchemy models"""
    
    print("🔍 Database Schema Health Check")
    print("=" * 60)
    
    # Get database info
    db_url = settings.database_url if hasattr(settings, 'database_url') else os.environ.get('DATABASE_URL', '')
    db_type = "PostgreSQL" if "postgresql" in db_url.lower() else "SQLite"
    print(f"📊 Database Type: {db_type}")
    
    inspector = inspect(engine)
    
    # Check each model
    models_to_check = [
        (Project, 'projects'),
        (User, 'users'),
        (FloorPlan, 'floor_plans')
    ]
    
    all_good = True
    
    for model, table_name in models_to_check:
        print(f"\n📋 Checking table: {table_name}")
        print("-" * 40)
        
        # Get columns from database
        try:
            db_columns = {col['name']: col['type'] for col in inspector.get_columns(table_name)}
        except Exception as e:
            print(f"❌ Table {table_name} doesn't exist in database!")
            all_good = False
            continue
        
        # Get columns from model
        model_columns = {column.name: str(column.type) for column in model.__table__.columns}
        
        # Find differences
        missing_in_db = set(model_columns.keys()) - set(db_columns.keys())
        extra_in_db = set(db_columns.keys()) - set(model_columns.keys())
        
        if missing_in_db:
            print(f"❌ Missing columns in database:")
            for col in missing_in_db:
                print(f"   - {col} ({model_columns[col]})")
            all_good = False
        
        if extra_in_db:
            print(f"⚠️  Extra columns in database (may be OK):")
            for col in extra_in_db:
                print(f"   - {col}")
        
        if not missing_in_db and not extra_in_db:
            print(f"✅ Schema is in sync ({len(db_columns)} columns)")
    
    # Check for critical columns in projects table
    print("\n🔧 Critical Columns Check (projects table)")
    print("-" * 40)
    
    critical_columns = [
        'subtotal',
        'contingency_percentage', 
        'contingency_amount',
        'cost_per_sqft',
        'project_classification'
    ]
    
    try:
        db_columns = {col['name'] for col in inspector.get_columns('projects')}
        missing_critical = [col for col in critical_columns if col not in db_columns]
        
        if missing_critical:
            print(f"❌ Missing critical columns: {', '.join(missing_critical)}")
            print(f"   Run: python emergency_fix_schema.py")
            all_good = False
        else:
            print(f"✅ All critical columns present")
    except Exception as e:
        print(f"❌ Error checking critical columns: {e}")
        all_good = False
    
    # Test database operations
    print("\n🧪 Database Operations Test")
    print("-" * 40)
    
    db = SessionLocal()
    try:
        # Test read
        project_count = db.query(Project).count()
        user_count = db.query(User).count()
        print(f"✅ Can read: {project_count} projects, {user_count} users")
        
        # Test query with new columns
        try:
            sample = db.query(
                Project.id,
                Project.name,
                Project.subtotal,
                Project.contingency_percentage,
                Project.project_classification
            ).first()
            
            if sample:
                print(f"✅ Can query new columns")
            else:
                print(f"⚠️  No projects to test with")
        except Exception as e:
            print(f"❌ Cannot query new columns: {e}")
            all_good = False
            
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        all_good = False
    finally:
        db.close()
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("✅ DATABASE IS HEALTHY - Ready for deployment")
        return 0
    else:
        print("❌ DATABASE NEEDS ATTENTION")
        print("\nRecommended actions:")
        print("1. Run: python emergency_fix_schema.py")
        print("2. Run: python migrations/002_add_all_missing_columns.py")
        print("3. Re-run this health check")
        return 1

def show_statistics():
    """Show database statistics"""
    
    print("\n📊 Database Statistics")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        stats = []
        
        # Projects stats
        total_projects = db.query(Project).count()
        projects_with_cost = db.query(Project).filter(
            Project.subtotal.isnot(None)
        ).count()
        
        stats.append(["Total Projects", total_projects])
        stats.append(["Projects with Cost Breakdown", projects_with_cost])
        
        # Users stats
        total_users = db.query(User).count()
        active_users = db.query(User).join(Project).distinct().count()
        
        stats.append(["Total Users", total_users])
        stats.append(["Users with Projects", active_users])
        
        # Recent activity
        from datetime import datetime, timedelta
        recent_date = datetime.now() - timedelta(days=7)
        recent_projects = db.query(Project).filter(
            Project.created_at >= recent_date
        ).count()
        
        stats.append(["Projects (last 7 days)", recent_projects])
        
        print(tabulate(stats, headers=["Metric", "Count"], tablefmt="grid"))
        
        # Show sample project with costs
        sample = db.query(Project).filter(
            Project.subtotal.isnot(None)
        ).first()
        
        if sample:
            print("\n📝 Sample Project with Cost Breakdown:")
            print(f"   Name: {sample.name}")
            print(f"   Subtotal: ${sample.subtotal:,.2f}" if sample.subtotal else "   Subtotal: None")
            print(f"   Contingency: {sample.contingency_percentage}% = ${sample.contingency_amount:,.2f}" 
                  if sample.contingency_amount else "   Contingency: None")
            print(f"   Total: ${sample.total_cost:,.2f}")
            print(f"   Cost/SF: ${sample.cost_per_sqft:.2f}" if sample.cost_per_sqft else "   Cost/SF: None")
            
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    exit_code = check_schema_sync()
    
    if exit_code == 0:
        show_statistics()
    
    sys.exit(exit_code)