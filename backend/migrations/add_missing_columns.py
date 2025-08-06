#!/usr/bin/env python3
"""
Add all missing columns to production database.
This migration adds columns that exist in the model but not in production.
"""

import os
import sys

def run_migration():
    """Run migration based on database type"""
    db_url = os.environ.get('DATABASE_URL', '')
    
    if 'postgresql' in db_url or 'psycopg2' in db_url:
        return migrate_postgresql()
    else:
        return migrate_sqlite()

def migrate_postgresql():
    """PostgreSQL migration"""
    import psycopg2
    from psycopg2 import sql
    import os
    from urllib.parse import urlparse
    
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return 1
    
    # Parse database URL
    result = urlparse(db_url)
    
    try:
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        cursor = conn.cursor()
        
        print("Connected to PostgreSQL database")
        
        # Get existing columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'projects'
        """)
        existing_columns = set(row[0] for row in cursor.fetchall())
        
        # Define columns to add with their types and defaults
        columns_to_add = [
            ('project_classification', 'VARCHAR', "'ground_up'"),
            ('subtotal', 'FLOAT', 'NULL'),
            ('contingency_percentage', 'FLOAT', '10.0'),
            ('contingency_amount', 'FLOAT', 'NULL'),
            ('cost_per_sqft', 'FLOAT', 'NULL'),
            ('cost_data', 'TEXT', 'NULL'),
            ('team_id', 'INTEGER', 'NULL'),
            ('created_by_id', 'INTEGER', 'NULL'),
            ('scenario_name', 'VARCHAR', 'NULL'),
            ('description', 'TEXT', 'NULL'),
            ('building_type', 'VARCHAR', 'NULL'),
            ('occupancy_type', 'VARCHAR', 'NULL'),
        ]
        
        # Add missing columns
        for column_name, column_type, default_value in columns_to_add:
            if column_name not in existing_columns:
                try:
                    if default_value == 'NULL':
                        alter_sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}"
                    else:
                        alter_sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                    
                    print(f"Adding column {column_name}...")
                    cursor.execute(alter_sql)
                    conn.commit()
                    print(f"✓ Added column {column_name}")
                except psycopg2.errors.DuplicateColumn:
                    print(f"✓ Column {column_name} already exists")
                except Exception as e:
                    print(f"✗ Error adding {column_name}: {str(e)}")
            else:
                print(f"✓ Column {column_name} already exists")
        
        # Update existing projects to calculate missing cost fields if needed
        print("\nUpdating cost calculations for existing projects...")
        cursor.execute("""
            UPDATE projects 
            SET 
                subtotal = COALESCE(subtotal, total_cost / 1.1),
                contingency_percentage = COALESCE(contingency_percentage, 10.0),
                contingency_amount = COALESCE(contingency_amount, total_cost - (total_cost / 1.1)),
                cost_per_sqft = COALESCE(cost_per_sqft, total_cost / NULLIF(square_footage, 0))
            WHERE subtotal IS NULL OR cost_per_sqft IS NULL
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        print(f"✓ Updated {rows_updated} projects with calculated values")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Migration completed successfully!")
        return 0
        
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        return 1

def migrate_sqlite():
    """SQLite migration"""
    import sqlite3
    
    db_path = os.environ.get('DATABASE_PATH', 'specsharp.db')
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        return 1
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Connected to SQLite database")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(projects)")
        existing_columns = set(row[1] for row in cursor.fetchall())
        
        # Define columns to add
        columns_to_add = [
            ('project_classification', 'VARCHAR', "'ground_up'"),
            ('subtotal', 'FLOAT', 'NULL'),
            ('contingency_percentage', 'FLOAT', '10.0'),
            ('contingency_amount', 'FLOAT', 'NULL'),
            ('cost_per_sqft', 'FLOAT', 'NULL'),
            ('cost_data', 'TEXT', 'NULL'),
            ('team_id', 'INTEGER', 'NULL'),
            ('created_by_id', 'INTEGER', 'NULL'),
            ('scenario_name', 'VARCHAR', 'NULL'),
            ('description', 'TEXT', 'NULL'),
            ('building_type', 'VARCHAR', 'NULL'),
            ('occupancy_type', 'VARCHAR', 'NULL'),
        ]
        
        # Add missing columns
        for column_name, column_type, default_value in columns_to_add:
            if column_name not in existing_columns:
                try:
                    if default_value == 'NULL':
                        alter_sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}"
                    else:
                        alter_sql = f"ALTER TABLE projects ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
                    
                    print(f"Adding column {column_name}...")
                    cursor.execute(alter_sql)
                    conn.commit()
                    print(f"✓ Added column {column_name}")
                except Exception as e:
                    print(f"✗ Error adding {column_name}: {str(e)}")
            else:
                print(f"✓ Column {column_name} already exists")
        
        # Update existing projects
        print("\nUpdating cost calculations for existing projects...")
        cursor.execute("""
            UPDATE projects 
            SET 
                subtotal = COALESCE(subtotal, total_cost / 1.1),
                contingency_percentage = COALESCE(contingency_percentage, 10.0),
                contingency_amount = COALESCE(contingency_amount, total_cost - (total_cost / 1.1)),
                cost_per_sqft = COALESCE(cost_per_sqft, total_cost / NULLIF(square_footage, 0))
            WHERE subtotal IS NULL OR cost_per_sqft IS NULL
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        print(f"✓ Updated {rows_updated} projects with calculated values")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Migration completed successfully!")
        return 0
        
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(run_migration())