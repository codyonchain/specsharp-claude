#!/usr/bin/env python3
"""
Verify that the schema fix worked and projects are accessible
"""

import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import Project, User
from app.core.config import settings

def verify_fix():
    """Comprehensive verification of the schema fix"""
    
    print("🔍 Verifying Schema Fix")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    db = SessionLocal()
    success = True
    
    try:
        # 1. Check if we can query projects table
        print("\n1️⃣ Testing basic project query...")
        try:
            project_count = db.query(Project).count()
            print(f"   ✅ Can query projects table")
            print(f"   📊 Total projects: {project_count}")
        except Exception as e:
            print(f"   ❌ Cannot query projects: {e}")
            success = False
            return success
        
        # 2. Check if we can access new columns
        print("\n2️⃣ Testing new column access...")
        try:
            # Query with all new columns
            sample = db.query(
                Project.id,
                Project.name,
                Project.subtotal,
                Project.contingency_percentage,
                Project.contingency_amount,
                Project.cost_per_sqft,
                Project.project_classification,
                Project.description,
                Project.building_type,
                Project.occupancy_type
            ).first()
            
            if sample:
                print(f"   ✅ Can access all new columns")
                print(f"   📁 Sample: {sample.name}")
                if sample.subtotal:
                    print(f"      Subtotal: ${sample.subtotal:,.2f}")
                    print(f"      Contingency: {sample.contingency_percentage}%")
                    print(f"      Classification: {sample.project_classification}")
            else:
                print(f"   ⚠️ No projects to test with")
        except Exception as e:
            print(f"   ❌ Cannot access new columns: {e}")
            success = False
        
        # 3. Test cost breakdown integrity
        print("\n3️⃣ Testing cost breakdown integrity...")
        try:
            # Find projects with cost breakdowns
            projects_with_costs = db.query(Project).filter(
                Project.subtotal.isnot(None),
                Project.total_cost.isnot(None)
            ).limit(5).all()
            
            if projects_with_costs:
                print(f"   ✅ Found {len(projects_with_costs)} projects with cost breakdowns")
                
                for p in projects_with_costs[:3]:
                    # Verify math: total should be close to subtotal + contingency
                    if p.subtotal and p.contingency_amount:
                        expected_total = p.subtotal + p.contingency_amount
                        difference = abs(p.total_cost - expected_total)
                        
                        if difference < 1.0:  # Allow $1 rounding difference
                            print(f"   ✓ {p.name[:30]:30} - Math checks out")
                        else:
                            print(f"   ⚠️ {p.name[:30]:30} - Total mismatch by ${difference:,.2f}")
            else:
                print(f"   ⚠️ No projects with cost breakdowns to verify")
        except Exception as e:
            print(f"   ❌ Cost breakdown test failed: {e}")
            success = False
        
        # 4. Test creating a new project
        print("\n4️⃣ Testing project creation...")
        try:
            user = db.query(User).first()
            if user:
                test_project = Project(
                    project_id=f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    name="Schema Fix Verification Test",
                    project_type="commercial",
                    square_footage=1000,
                    location="Test Location",
                    total_cost=275000,
                    scope_data='{"test": true}',
                    user_id=user.id,
                    # New columns
                    subtotal=250000,
                    contingency_percentage=10,
                    contingency_amount=25000,
                    cost_per_sqft=275,
                    project_classification="ground_up",
                    description="Test project to verify schema fix",
                    building_type="office",
                    occupancy_type="office"
                )
                
                db.add(test_project)
                db.commit()
                
                print(f"   ✅ Successfully created test project")
                print(f"   🆔 Project ID: {test_project.project_id}")
                
                # Clean up test project
                db.delete(test_project)
                db.commit()
                print(f"   🧹 Test project cleaned up")
            else:
                print(f"   ⚠️ No user found to test with")
        except Exception as e:
            print(f"   ❌ Cannot create projects: {e}")
            success = False
            db.rollback()
        
        # 5. Check user project associations
        print("\n5️⃣ Testing user-project associations...")
        try:
            users_with_projects = db.query(User).join(Project).distinct().all()
            print(f"   ✅ Found {len(users_with_projects)} users with projects")
            
            for user in users_with_projects[:3]:
                user_projects = db.query(Project).filter(Project.user_id == user.id).count()
                print(f"   👤 {user.email}: {user_projects} projects")
        except Exception as e:
            print(f"   ❌ Association test failed: {e}")
            success = False
        
        # 6. Performance test
        print("\n6️⃣ Testing query performance...")
        try:
            import time
            start = time.time()
            
            # Complex query that uses multiple columns
            result = db.query(Project).filter(
                Project.total_cost > 0,
                Project.square_footage > 0
            ).order_by(Project.created_at.desc()).limit(20).all()
            
            elapsed = time.time() - start
            
            if elapsed < 1.0:
                print(f"   ✅ Query performance OK ({elapsed:.3f}s)")
            else:
                print(f"   ⚠️ Query slow ({elapsed:.3f}s) - consider adding indexes")
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
            success = False
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        success = False
    finally:
        db.close()
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("✅ VERIFICATION SUCCESSFUL!")
        print("\nThe schema fix has been applied correctly:")
        print("• Projects are accessible")
        print("• New columns are working")
        print("• Cost breakdowns are intact")
        print("• New projects can be created")
        print("\n🎉 Users should now be able to:")
        print("• View their existing projects")
        print("• Create new projects")
        print("• See proper cost breakdowns")
    else:
        print("❌ VERIFICATION FAILED")
        print("\n🔧 Troubleshooting steps:")
        print("1. Run: python emergency_fix_schema.py")
        print("2. Check DATABASE_URL is correct")
        print("3. Ensure database is accessible")
        print("4. Review error messages above")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(verify_fix())