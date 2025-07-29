#!/usr/bin/env python3
"""
Create database indexes for optimizing project queries.
Run this script to add indexes to the projects table.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def create_indexes():
    """Create database indexes for better query performance"""
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    indexes = [
        # Index on user_id for faster user project lookups
        {
            "name": "idx_projects_user_id",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id)"
        },
        # Index on created_at DESC for sorting
        {
            "name": "idx_projects_created_at",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at DESC)"
        },
        # Index on team_id for team project lookups
        {
            "name": "idx_projects_team_id",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_team_id ON projects(team_id)"
        },
        # Composite index for team + created_at
        {
            "name": "idx_projects_team_created",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_team_created ON projects(team_id, created_at DESC)"
        },
        # Composite index for user + created_at
        {
            "name": "idx_projects_user_created",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at DESC)"
        },
        # Index for search functionality
        {
            "name": "idx_projects_name",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name)"
        },
        {
            "name": "idx_projects_location",
            "sql": "CREATE INDEX IF NOT EXISTS idx_projects_location ON projects(location)"
        }
    ]
    
    with engine.connect() as conn:
        for index in indexes:
            try:
                conn.execute(text(index["sql"]))
                conn.commit()
                print(f"✅ Created index: {index['name']}")
            except ProgrammingError as e:
                if "already exists" in str(e):
                    print(f"ℹ️  Index already exists: {index['name']}")
                else:
                    print(f"❌ Error creating index {index['name']}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error creating index {index['name']}: {e}")
    
    print("\n✨ Index creation complete!")
    
    # Show current indexes
    print("\n📊 Current indexes on projects table:")
    try:
        with engine.connect() as conn:
            # PostgreSQL query
            if "postgresql" in settings.DATABASE_URL:
                result = conn.execute(text("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = 'projects'
                    ORDER BY indexname
                """))
            else:
                # SQLite query
                result = conn.execute(text("""
                    SELECT name, sql 
                    FROM sqlite_master 
                    WHERE type = 'index' AND tbl_name = 'projects'
                    ORDER BY name
                """))
            
            for row in result:
                print(f"  - {row[0]}")
    except Exception as e:
        print(f"Could not list indexes: {e}")

if __name__ == "__main__":
    print("🚀 Creating database indexes for SpecSharp...")
    create_indexes()