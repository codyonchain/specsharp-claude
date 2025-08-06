#!/usr/bin/env python3
"""
Add project_classification column to projects table if it doesn't exist.
Run this migration in production to fix the missing column issue.
"""

import sqlite3
import sys
import os

def check_column_exists(conn, table_name, column_name):
    """Check if a column exists in a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    for column in columns:
        if column[1] == column_name:
            return True
    return False

def add_project_classification_column():
    """Add project_classification column to projects table"""
    
    # Database path - adjust this for your production environment
    db_path = os.environ.get('DATABASE_PATH', '../specsharp.db')
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        print("Set DATABASE_PATH environment variable to the correct database location")
        return 1
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Check if column already exists
        if check_column_exists(conn, 'projects', 'project_classification'):
            print("✓ Column 'project_classification' already exists in projects table")
            return 0
        
        # Add the column with a default value
        print("Adding project_classification column to projects table...")
        cursor = conn.cursor()
        cursor.execute("""
            ALTER TABLE projects 
            ADD COLUMN project_classification VARCHAR DEFAULT 'ground_up'
        """)
        
        conn.commit()
        print("✓ Successfully added project_classification column")
        
        # Verify the column was added
        if check_column_exists(conn, 'projects', 'project_classification'):
            print("✓ Verified: Column exists after migration")
        else:
            print("ERROR: Column was not added successfully")
            return 1
            
        conn.close()
        return 0
        
    except Exception as e:
        print(f"ERROR: Migration failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(add_project_classification_column())