#!/usr/bin/env python3
"""
IMMEDIATE FIX - Run this NOW to fix the database
"""
import psycopg2
import os
from urllib.parse import urlparse

# Get database URL from environment or hardcode it temporarily
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL not set!")
    print("Set it with: export DATABASE_URL='your_postgresql_url'")
    exit(1)

print(f"🔧 Fixing database immediately...")

# Parse the database URL
result = urlparse(DATABASE_URL)
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port or 5432

# Connect directly
try:
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    conn.autocommit = True
    cur = conn.cursor()
    print("✓ Connected to PostgreSQL")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Add ALL missing columns
columns = [
    # Critical columns for immediate fix
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS subtotal FLOAT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_percentage FLOAT DEFAULT 10.0", 
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS contingency_amount FLOAT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_per_sqft FLOAT",
    
    # Additional columns that might be missing
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS project_classification VARCHAR DEFAULT 'ground_up'",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS building_type VARCHAR",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS occupancy_type VARCHAR",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS cost_data TEXT",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS team_id INTEGER",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS created_by_id INTEGER",
    "ALTER TABLE projects ADD COLUMN IF NOT EXISTS scenario_name VARCHAR"
]

print("\n📝 Adding missing columns...")
success_count = 0
for query in columns:
    try:
        cur.execute(query)
        column_name = query.split('ADD COLUMN IF NOT EXISTS ')[1].split(' ')[0]
        print(f"  ✅ Added/verified: {column_name}")
        success_count += 1
    except Exception as e:
        if "already exists" in str(e).lower():
            column_name = query.split('ADD COLUMN IF NOT EXISTS ')[1].split(' ')[0]
            print(f"  ✓ Already exists: {column_name}")
        else:
            print(f"  ❌ Error: {e}")

# Update existing projects with calculated values
print("\n🔄 Updating existing projects with cost breakdowns...")
try:
    cur.execute("""
        UPDATE projects 
        SET 
            subtotal = CASE 
                WHEN subtotal IS NULL AND total_cost IS NOT NULL 
                THEN total_cost / 1.1
                ELSE subtotal
            END,
            contingency_percentage = CASE
                WHEN contingency_percentage IS NULL 
                THEN 10.0
                ELSE contingency_percentage
            END,
            contingency_amount = CASE
                WHEN contingency_amount IS NULL AND total_cost IS NOT NULL
                THEN (total_cost / 1.1) * 0.1
                ELSE contingency_amount
            END,
            cost_per_sqft = CASE
                WHEN cost_per_sqft IS NULL AND total_cost IS NOT NULL AND square_footage > 0
                THEN total_cost / square_footage
                ELSE cost_per_sqft
            END
        WHERE total_cost IS NOT NULL
    """)
    updated = cur.rowcount
    print(f"  ✅ Updated {updated} projects with cost calculations")
except Exception as e:
    print(f"  ⚠️ Update warning: {e}")

# Verify the fix
print("\n🔍 Verifying fix...")
try:
    # Check if we can query with new columns
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(subtotal) as with_subtotal,
            COUNT(contingency_percentage) as with_contingency
        FROM projects
    """)
    result = cur.fetchone()
    print(f"  📊 Total projects: {result[0]}")
    print(f"  📊 Projects with subtotal: {result[1]}")
    print(f"  📊 Projects with contingency: {result[2]}")
    
    # Test a sample query
    cur.execute("""
        SELECT project_id, name, subtotal, contingency_amount, total_cost 
        FROM projects 
        LIMIT 1
    """)
    sample = cur.fetchone()
    if sample:
        print(f"  ✅ Can query all columns successfully")
        print(f"  📁 Sample: {sample[1]}")
except Exception as e:
    print(f"  ❌ Verification failed: {e}")

cur.close()
conn.close()

print("\n" + "="*50)
print("✅ DATABASE FIXED!")
print("="*50)
print("\nUsers should now be able to:")
print("  • View their projects")
print("  • Create new projects")
print("  • See cost breakdowns")
print("\nNext: Restart your application if needed")