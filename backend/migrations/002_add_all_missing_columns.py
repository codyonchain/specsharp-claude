#!/usr/bin/env python3
"""
Migration 002: Add all missing columns for cost breakdown and features
This handles both PostgreSQL (production) and SQLite (development)
"""

import os
import sys
from datetime import datetime

def run_migration():
    """Detect database type and run appropriate migration"""
    db_url = os.environ.get('DATABASE_URL', '')
    
    if 'postgresql' in db_url.lower() or 'psycopg2' in db_url.lower():
        return migrate_postgresql(db_url)
    else:
        # Default to SQLite for local development
        db_path = os.environ.get('DATABASE_PATH', 'backend/specsharp.db')
        return migrate_sqlite(db_path)

def migrate_postgresql(db_url):
    """PostgreSQL migration - production"""
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    from urllib.parse import urlparse
    
    print(f"Running PostgreSQL migration...")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Parse connection URL
    result = urlparse(db_url)
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✓ Connected to PostgreSQL")
        
        # Get existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects'
        """)
        existing_columns = set(row[0] for row in cursor.fetchall())
        print(f"✓ Found {len(existing_columns)} existing columns")
        
        # Define all columns that should exist
        columns_to_add = [
            # Cost breakdown (Critical for immediate fix)
            ('subtotal', 'FLOAT', None),
            ('contingency_percentage', 'FLOAT', '10.0'),
            ('contingency_amount', 'FLOAT', None),
            ('cost_per_sqft', 'FLOAT', None),
            
            # Project details
            ('project_classification', 'VARCHAR(50)', "'ground_up'"),
            ('description', 'TEXT', None),
            ('building_type', 'VARCHAR(100)', None),
            ('occupancy_type', 'VARCHAR(100)', None),
            ('scenario_name', 'VARCHAR(100)', None),
            
            # Team features
            ('team_id', 'INTEGER', None),
            ('created_by_id', 'INTEGER', None),
            
            # Additional data
            ('cost_data', 'TEXT', None),
        ]
        
        # Add missing columns
        added = 0
        for col_name, col_type, default in columns_to_add:
            if col_name not in existing_columns:
                try:
                    if default:
                        sql = f"ALTER TABLE projects ADD COLUMN {col_name} {col_type} DEFAULT {default}"
                    else:
                        sql = f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}"
                    
                    cursor.execute(sql)
                    print(f"  ✅ Added: {col_name} ({col_type})")
                    added += 1
                except psycopg2.errors.DuplicateColumn:
                    print(f"  ✓ Exists: {col_name}")
                except Exception as e:
                    print(f"  ⚠️ Error adding {col_name}: {e}")
            else:
                print(f"  ✓ Exists: {col_name}")
        
        if added > 0:
            print(f"\n✅ Added {added} new columns")
        
        # Update existing projects with calculated values
        print("\n📊 Updating existing projects...")
        
        # Count projects needing updates
        cursor.execute("""
            SELECT COUNT(*) FROM projects 
            WHERE (subtotal IS NULL OR cost_per_sqft IS NULL) 
            AND total_cost IS NOT NULL
        """)
        needs_update = cursor.fetchone()[0]
        
        if needs_update > 0:
            print(f"  Found {needs_update} projects needing calculations")
            
            cursor.execute("""
                UPDATE projects 
                SET 
                    subtotal = COALESCE(subtotal, total_cost / 1.1),
                    contingency_percentage = COALESCE(contingency_percentage, 10.0),
                    contingency_amount = COALESCE(contingency_amount, (total_cost / 1.1) * 0.1),
                    cost_per_sqft = COALESCE(
                        cost_per_sqft, 
                        CASE 
                            WHEN square_footage > 0 THEN total_cost / square_footage 
                            ELSE NULL 
                        END
                    ),
                    project_classification = COALESCE(project_classification, 'ground_up')
                WHERE total_cost IS NOT NULL
            """)
            
            updated = cursor.rowcount
            print(f"  ✅ Updated {updated} projects")
        else:
            print("  ✓ All projects have required values")
        
        # Add indexes for performance
        print("\n🔍 Creating indexes...")
        indexes = [
            ("idx_projects_user_id", "user_id"),
            ("idx_projects_team_id", "team_id"),
            ("idx_projects_created_at", "created_at"),
            ("idx_projects_project_classification", "project_classification"),
        ]
        
        for index_name, column in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON projects({column})")
                print(f"  ✓ Index on {column}")
            except Exception as e:
                print(f"  ⚠️ Index {index_name}: {e}")
        
        # Verify the migration
        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM projects 
            WHERE subtotal IS NOT NULL 
            AND contingency_percentage IS NOT NULL
        """)
        valid_projects = cursor.fetchone()[0]
        
        print(f"\n📊 Final Statistics:")
        print(f"  Total projects: {total_projects}")
        print(f"  Projects with cost breakdown: {valid_projects}")
        print(f"  Success rate: {(valid_projects/total_projects*100 if total_projects > 0 else 0):.1f}%")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL migration completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ PostgreSQL migration failed: {e}")
        return 1

def migrate_sqlite(db_path):
    """SQLite migration - development"""
    import sqlite3
    
    print(f"Running SQLite migration...")
    print(f"Database: {db_path}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return 1
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✓ Connected to SQLite")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(projects)")
        existing_columns = set(row[1] for row in cursor.fetchall())
        print(f"✓ Found {len(existing_columns)} existing columns")
        
        # Define columns to add
        columns_to_add = [
            ('subtotal', 'FLOAT', None),
            ('contingency_percentage', 'FLOAT', '10.0'),
            ('contingency_amount', 'FLOAT', None),
            ('cost_per_sqft', 'FLOAT', None),
            ('project_classification', 'VARCHAR', "'ground_up'"),
            ('description', 'TEXT', None),
            ('building_type', 'VARCHAR', None),
            ('occupancy_type', 'VARCHAR', None),
            ('scenario_name', 'VARCHAR', None),
            ('team_id', 'INTEGER', None),
            ('created_by_id', 'INTEGER', None),
            ('cost_data', 'TEXT', None),
        ]
        
        # Add missing columns
        added = 0
        for col_name, col_type, default in columns_to_add:
            if col_name not in existing_columns:
                try:
                    if default:
                        sql = f"ALTER TABLE projects ADD COLUMN {col_name} {col_type} DEFAULT {default}"
                    else:
                        sql = f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}"
                    
                    cursor.execute(sql)
                    print(f"  ✅ Added: {col_name}")
                    added += 1
                except Exception as e:
                    print(f"  ⚠️ Error adding {col_name}: {e}")
            else:
                print(f"  ✓ Exists: {col_name}")
        
        if added > 0:
            conn.commit()
            print(f"\n✅ Added {added} new columns")
        
        # Update existing projects
        cursor.execute("""
            UPDATE projects 
            SET 
                subtotal = COALESCE(subtotal, total_cost / 1.1),
                contingency_percentage = COALESCE(contingency_percentage, 10.0),
                contingency_amount = COALESCE(contingency_amount, (total_cost / 1.1) * 0.1),
                cost_per_sqft = COALESCE(
                    cost_per_sqft, 
                    CASE 
                        WHEN square_footage > 0 THEN total_cost / square_footage 
                        ELSE NULL 
                    END
                ),
                project_classification = COALESCE(project_classification, 'ground_up')
            WHERE total_cost IS NOT NULL
        """)
        
        updated = cursor.rowcount
        conn.commit()
        
        if updated > 0:
            print(f"  ✅ Updated {updated} projects")
        
        cursor.close()
        conn.close()
        
        print("\n✅ SQLite migration completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\n❌ SQLite migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())