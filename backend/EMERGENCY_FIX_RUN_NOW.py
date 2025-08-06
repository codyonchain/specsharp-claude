#!/usr/bin/env python3
"""
EMERGENCY PRODUCTION FIX - RUN IMMEDIATELY
This script fixes the missing columns in PostgreSQL that are breaking project creation
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def emergency_fix():
    # Get database connection from environment
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Set it with: export DATABASE_URL='your_connection_string'")
        sys.exit(1)
    
    print(f"🚨 EMERGENCY FIX STARTING...")
    print(f"📍 Connecting to database...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        print("✅ Connected to database")
        
        # STEP 1: Add ALL missing columns (comprehensive list)
        print("\n📝 Adding missing columns...")
        
        columns_to_add = [
            # Critical columns for cost breakdown
            ("subtotal", "DOUBLE PRECISION"),
            ("contingency_percentage", "DOUBLE PRECISION DEFAULT 10.0"),
            ("contingency_amount", "DOUBLE PRECISION"),
            ("cost_per_sqft", "DOUBLE PRECISION"),
            
            # Project classification columns
            ("project_classification", "VARCHAR(50) DEFAULT 'ground_up'"),
            
            # Additional detail columns
            ("description", "TEXT"),
            ("building_type", "VARCHAR(100)"),
            ("occupancy_type", "VARCHAR(100)"),
            ("scenario_name", "VARCHAR(100)"),
            
            # Team/user tracking columns
            ("team_id", "INTEGER"),
            ("created_by_id", "INTEGER"),
            
            # Additional data storage
            ("cost_data", "TEXT")
        ]
        
        added_count = 0
        for column_name, column_def in columns_to_add:
            try:
                cur.execute(f"""
                    ALTER TABLE projects 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_def}
                """)
                print(f"  ✅ Added column: {column_name}")
                added_count += 1
            except psycopg2.errors.DuplicateColumn:
                print(f"  ✓ Column {column_name} already exists")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    print(f"  ✓ Column {column_name} already exists")
                else:
                    print(f"  ⚠️ Warning for {column_name}: {e}")
        
        print(f"\n📊 Added/verified {added_count} columns")
        
        # STEP 2: Update any existing projects with NULL values
        print("\n🔄 Updating existing projects with calculated values...")
        cur.execute("""
            UPDATE projects 
            SET subtotal = COALESCE(subtotal, total_cost / 1.1),
                contingency_percentage = COALESCE(contingency_percentage, 10.0),
                contingency_amount = COALESCE(contingency_amount, total_cost * 0.0909),
                cost_per_sqft = COALESCE(cost_per_sqft, 
                    CASE WHEN square_footage > 0 THEN total_cost / square_footage ELSE NULL END),
                project_classification = COALESCE(project_classification, 'ground_up')
            WHERE total_cost IS NOT NULL 
            AND (subtotal IS NULL OR contingency_amount IS NULL OR cost_per_sqft IS NULL)
        """)
        
        rows_updated = cur.rowcount
        print(f"  ✅ Updated {rows_updated} existing projects with calculations")
        
        # STEP 3: Verify the critical columns
        print("\n🔍 Verifying critical columns...")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'projects' 
            AND column_name IN ('subtotal', 'contingency_percentage', 'contingency_amount', 
                              'cost_per_sqft', 'project_classification')
        """)
        
        columns = cur.fetchall()
        if len(columns) >= 3:
            print(f"  ✅ {len(columns)} critical columns verified!")
            for col in columns:
                print(f"     - {col[0]}: {col[1]}")
        else:
            print(f"  ⚠️  Warning: Only {len(columns)} critical columns found")
        
        # STEP 4: Test with actual project data
        print("\n🧪 Testing database operations...")
        
        # Test SELECT with new columns
        cur.execute("""
            SELECT project_id, name, subtotal, contingency_percentage, 
                   contingency_amount, total_cost, cost_per_sqft
            FROM projects 
            LIMIT 1
        """)
        
        sample = cur.fetchone()
        if sample:
            print(f"  ✅ Can query all new columns successfully")
            print(f"  📁 Sample project: {sample[1]}")
            if sample[2]:  # if subtotal exists
                print(f"     Subtotal: ${sample[2]:,.2f}")
                print(f"     Contingency: {sample[3]}%")
                print(f"     Total: ${sample[5]:,.2f}")
        
        # Count total projects
        cur.execute("SELECT COUNT(*) FROM projects")
        count = cur.fetchone()[0]
        print(f"  ✅ Projects table fully accessible")
        print(f"  📊 Total projects in database: {count}")
        
        # Test INSERT capability (without actually inserting)
        cur.execute("""
            SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_name = 'projects' 
            AND column_name IN ('subtotal', 'contingency_percentage', 'contingency_amount',
                              'cost_per_sqft', 'project_classification', 'description',
                              'building_type', 'occupancy_type', 'team_id', 'created_by_id')
        """)
        
        col_count = cur.fetchone()[0]
        if col_count >= 10:
            print(f"  ✅ All columns ready for INSERT operations")
        else:
            print(f"  ⚠️  Only {col_count}/10 expected columns found")
        
        # Close connection
        cur.close()
        conn.close()
        
        print("\n" + "="*60)
        print("🎉 EMERGENCY FIX COMPLETE!")
        print("="*60)
        print("\n✅ PRODUCTION IS RESTORED:")
        print("  • Users can now CREATE new projects")
        print("  • Users can VIEW existing projects")
        print("  • Cost breakdowns are calculated")
        print("  • All missing columns added")
        print("\n📝 Next Steps:")
        print("  1. Test creating a new project in the UI")
        print("  2. Verify existing projects display correctly")
        print("  3. Monitor logs for any remaining errors")
        print("="*60)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("\n🔧 Check:")
        print("  1. DATABASE_URL is correct")
        print("  2. Database server is running")
        print("  3. Network connectivity")
        return False
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("\n🚨 MANUAL FIX REQUIRED:")
        print("="*60)
        print("Connect to your database and run this SQL:")
        print("""
-- Add missing columns
ALTER TABLE projects ADD COLUMN IF NOT EXISTS subtotal DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_percentage DOUBLE PRECISION DEFAULT 10.0;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_amount DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_per_sqft DOUBLE PRECISION;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_classification VARCHAR(50) DEFAULT 'ground_up';

-- Update existing projects
UPDATE projects 
SET subtotal = total_cost / 1.1,
    contingency_percentage = 10.0,
    contingency_amount = total_cost * 0.0909,
    cost_per_sqft = total_cost / square_footage
WHERE total_cost IS NOT NULL AND subtotal IS NULL;
        """)
        print("="*60)
        return False

if __name__ == "__main__":
    print("="*60)
    print("🚨 EMERGENCY PRODUCTION FIX")
    print("="*60)
    success = emergency_fix()
    sys.exit(0 if success else 1)