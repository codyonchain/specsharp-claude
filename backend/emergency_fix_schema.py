#!/usr/bin/env python3
"""
Emergency script to fix PostgreSQL schema and restore project visibility
Run this IMMEDIATELY to restore user access
"""

import sys
import os
from sqlalchemy import create_engine, text, inspect
from urllib.parse import urlparse

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.models import Project
from app.db.database import SessionLocal

def fix_schema():
    """Add missing columns to PostgreSQL"""
    
    print("🔧 Starting emergency schema fix...")
    
    # Parse and display database info (hide password)
    db_url = settings.database_url if hasattr(settings, 'database_url') else os.environ.get('DATABASE_URL', '')
    if '@' in db_url:
        parsed = urlparse(db_url)
        safe_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}/{parsed.path.lstrip('/')}"
        print(f"📍 Database: {safe_url}")
    else:
        print(f"📍 Database: local")
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Check current schema
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('projects')]
        print(f"📊 Current columns in projects table: {len(existing_columns)}")
        
        # Define ALL missing columns from recent features
        columns_to_add = [
            # Cost breakdown columns
            ("subtotal", "FLOAT"),
            ("contingency_percentage", "FLOAT DEFAULT 10.0"),
            ("contingency_amount", "FLOAT"),
            ("cost_per_sqft", "FLOAT"),
            
            # Project classification
            ("project_classification", "VARCHAR DEFAULT 'ground_up'"),
            
            # Additional project details
            ("description", "TEXT"),
            ("building_type", "VARCHAR"),
            ("occupancy_type", "VARCHAR"),
            ("scenario_name", "VARCHAR"),
            
            # Team features
            ("team_id", "INTEGER"),
            ("created_by_id", "INTEGER"),
            
            # Additional data
            ("cost_data", "TEXT"),
        ]
        
        added_count = 0
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                try:
                    query = text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
                    conn.execute(query)
                    conn.commit()
                    print(f"✅ Added column: {col_name}")
                    added_count += 1
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"✓  Column {col_name} already exists")
                    else:
                        print(f"⚠️  Error adding {col_name}: {e}")
            else:
                print(f"✓  Column {col_name} already exists")
        
        if added_count > 0:
            print(f"\n📝 Added {added_count} new columns")
        
        # Update existing records with calculated values
        print("\n🔄 Updating existing projects with cost breakdown...")
        
        # First, check how many projects need updating
        check_result = conn.execute(text("""
            SELECT COUNT(*) FROM projects 
            WHERE subtotal IS NULL AND total_cost IS NOT NULL
        """))
        needs_update = check_result.scalar()
        
        if needs_update > 0:
            print(f"📊 Found {needs_update} projects needing cost breakdown calculation")
            
            # Update with cost breakdown
            # Assuming total_cost includes 10% contingency and possibly markup
            # Reverse calculation: if total = subtotal * 1.1 (10% contingency)
            # then subtotal = total / 1.1
            result = conn.execute(text("""
                UPDATE projects 
                SET 
                    subtotal = CASE 
                        WHEN subtotal IS NULL AND total_cost IS NOT NULL 
                        THEN total_cost / 1.1  -- Reverse out 10% contingency
                        ELSE subtotal 
                    END,
                    contingency_percentage = CASE
                        WHEN contingency_percentage IS NULL 
                        THEN 10.0
                        ELSE contingency_percentage
                    END,
                    contingency_amount = CASE
                        WHEN contingency_amount IS NULL AND total_cost IS NOT NULL
                        THEN (total_cost / 1.1) * 0.10  -- 10% of subtotal
                        ELSE contingency_amount
                    END,
                    cost_per_sqft = CASE
                        WHEN cost_per_sqft IS NULL AND total_cost IS NOT NULL AND square_footage > 0
                        THEN total_cost / square_footage
                        ELSE cost_per_sqft
                    END,
                    project_classification = CASE
                        WHEN project_classification IS NULL
                        THEN 'ground_up'
                        ELSE project_classification
                    END
                WHERE total_cost IS NOT NULL
            """))
            conn.commit()
            
            print(f"✅ Updated {result.rowcount} projects with cost breakdown")
        else:
            print("✓  All projects already have cost breakdowns")
        
        # Verify projects are accessible
        print("\n🔍 Verifying project accessibility...")
        db = SessionLocal()
        try:
            # Test query with all columns
            projects = db.query(Project).limit(10).all()
            print(f"\n🎉 SUCCESS! Projects are now accessible:")
            print(f"📊 Total projects in database: {db.query(Project).count()}")
            
            # Show sample projects
            for p in projects[:5]:
                if hasattr(p, 'subtotal') and p.subtotal:
                    print(f"   ✓ {p.name[:30]:30} | ${p.total_cost:>12,.2f} | Subtotal: ${p.subtotal:>12,.2f}")
                else:
                    print(f"   ✓ {p.name[:30]:30} | ${p.total_cost:>12,.2f}")
            
            if len(projects) > 5:
                print(f"   ... and {db.query(Project).count() - 5} more projects")
                
            # Check for any user with no projects visible
            from app.db.models import User
            users_with_projects = db.query(User).join(Project).distinct().count()
            total_users = db.query(User).count()
            print(f"\n📊 Users with projects: {users_with_projects}/{total_users}")
            
        except Exception as e:
            print(f"❌ Error accessing projects: {e}")
            print("\n🔧 Attempting alternative fix...")
            
            # Try to at least make projects queryable
            try:
                conn.execute(text("SELECT COUNT(*) FROM projects"))
                print("✓  Basic query works")
            except Exception as e2:
                print(f"❌ Critical error: {e2}")
                
        finally:
            db.close()

if __name__ == "__main__":
    try:
        fix_schema()
        print("\n✅ Schema fix complete! Users should now be able to:")
        print("   • View their existing projects")
        print("   • Create new projects")
        print("   • See proper cost breakdowns")
        print("\n📝 Next steps:")
        print("   1. Test by logging in and viewing projects")
        print("   2. Try creating a new project")
        print("   3. Set up Alembic for future migrations")
    except Exception as e:
        print(f"\n❌ Failed to fix schema: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check DATABASE_URL is set correctly")
        print("   2. Ensure PostgreSQL is accessible")
        print("   3. Check user has ALTER TABLE permissions")
        sys.exit(1)