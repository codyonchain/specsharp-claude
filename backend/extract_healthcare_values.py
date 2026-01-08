"""Extract all healthcare values from healthcare_cost_service for migration to master config."""

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("EXTRACTING HEALTHCARE VALUES FOR CONFIG MIGRATION")
print("=" * 70)

# Import the service to get actual values
try:
    from app.services.healthcare_cost_service import (
        HEALTHCARE_BASE_COSTS,
        HEALTHCARE_TRADE_BREAKDOWNS,
        HEALTHCARE_KEYWORDS,
        HealthcareFacilityType
    )
    
    print("\n1. FACILITY TYPES AND BASE CONSTRUCTION COSTS:")
    print("-" * 50)
    for facility_type, base_cost in HEALTHCARE_BASE_COSTS.items():
        print(f"  {facility_type:30} ${base_cost}/SF (construction only)")
    
    print("\n2. EQUIPMENT COSTS (from comments):")
    print("-" * 50)
    equipment_costs = {
        "hospital": 150,  # $150-300/SF
        "medical_center": 150,
        "surgical_center": 200,  # $200-300/SF
        "imaging_center": 300,
        "medical_office": 20,  # $10-30/SF
        "dental_office": 30,
        "outpatient_clinic": 50,
        "urgent_care": 75,
        "rehabilitation": 100,
        "nursing_home": 10
    }
    for facility, cost in equipment_costs.items():
        print(f"  {facility:30} ${cost}/SF")
    
    print("\n3. SPECIAL DEPARTMENT PREMIUMS:")
    print("-" * 50)
    special_dept_costs = {
        "emergency_department": 50,  # From line 221
        "operating_room/surgery": 75,  # From line 224
        "imaging_suite": 40,  # From line 227
        "laboratory": 25,  # From line 230
        "specialty_services": 30  # From line 233
    }
    for dept, premium in special_dept_costs.items():
        print(f"  {dept:30} +${premium}/SF")
    
    print("\n4. TRADE BREAKDOWNS BY FACILITY TYPE:")
    print("-" * 50)
    for facility_type, trades in HEALTHCARE_TRADE_BREAKDOWNS.items():
        print(f"\n  {facility_type}:")
        for trade, pct in trades.items():
            print(f"    {trade:20} {pct*100:5.1f}%")
    
    print("\n5. HEALTHCARE KEYWORDS (for detection):")
    print("-" * 50)
    for facility_type, keywords in HEALTHCARE_KEYWORDS.items():
        print(f"\n  {facility_type}:")
        print(f"    {', '.join(keywords[:5])}...")
        
except ImportError as e:
    print(f"Error importing healthcare service: {e}")

# Generate suggested master_config structure
print("\n" + "=" * 70)
print("SUGGESTED MASTER CONFIG STRUCTURE")
print("=" * 70)

suggested_config = {
    "healthcare": {
        "name": "Healthcare",
        "base_cost": {"min": 275, "max": 1200},  # Wide range for all subtypes
        "subtypes": {
            "hospital": {
                "name": "Hospital (Full Service)",
                "base_construction_cost": 850,
                "equipment_cost": 150,
                "total_cost_range": {"min": 900, "max": 1200},
                "size_range": {"min": 50000, "max": 500000},
                "special_departments": {
                    "emergency": {"premium_per_sf": 50, "typical_pct_of_building": 0.15},
                    "surgery": {"premium_per_sf": 75, "typical_pct_of_building": 0.10},
                    "imaging": {"premium_per_sf": 40, "typical_pct_of_building": 0.05},
                    "icu": {"premium_per_sf": 60, "typical_pct_of_building": 0.10},
                    "laboratory": {"premium_per_sf": 25, "typical_pct_of_building": 0.05}
                },
                "trade_breakdown": {
                    "structural": 0.15,
                    "mechanical": 0.35,
                    "electrical": 0.20,
                    "plumbing": 0.15,
                    "finishes": 0.08,
                    "general_conditions": 0.07
                }
            },
            "surgical_center": {
                "name": "Ambulatory Surgical Center",
                "base_construction_cost": 550,
                "equipment_cost": 200,
                "total_cost_range": {"min": 700, "max": 850},
                "size_range": {"min": 10000, "max": 50000},
                "trade_breakdown": {
                    "structural": 0.12,
                    "mechanical": 0.38,
                    "electrical": 0.18,
                    "plumbing": 0.14,
                    "finishes": 0.10,
                    "general_conditions": 0.08
                }
            },
            "medical_center": {
                "name": "Medical Center",
                "base_construction_cost": 750,
                "equipment_cost": 150,
                "total_cost_range": {"min": 850, "max": 1000},
                "size_range": {"min": 30000, "max": 200000}
            },
            "imaging_center": {
                "name": "Diagnostic Imaging Center",
                "base_construction_cost": 500,
                "equipment_cost": 300,
                "total_cost_range": {"min": 750, "max": 900},
                "size_range": {"min": 5000, "max": 20000},
                "trade_breakdown": {
                    "structural": 0.18,  # Heavy shielding
                    "mechanical": 0.30,
                    "electrical": 0.22,  # High power needs
                    "plumbing": 0.10,
                    "finishes": 0.12,
                    "general_conditions": 0.08
                }
            },
            "outpatient_clinic": {
                "name": "Outpatient Clinic",
                "base_construction_cost": 380,
                "equipment_cost": 50,
                "total_cost_range": {"min": 400, "max": 480},
                "size_range": {"min": 3000, "max": 20000},
                "trade_breakdown": {
                    "structural": 0.12,
                    "mechanical": 0.28,
                    "electrical": 0.15,
                    "plumbing": 0.12,
                    "finishes": 0.20,
                    "general_conditions": 0.13
                }
            },
            "urgent_care": {
                "name": "Urgent Care Center",
                "base_construction_cost": 350,
                "equipment_cost": 75,
                "total_cost_range": {"min": 400, "max": 475},
                "size_range": {"min": 3000, "max": 10000}
            },
            "medical_office": {
                "name": "Medical Office Building",
                "base_construction_cost": 320,
                "equipment_cost": 20,
                "total_cost_range": {"min": 325, "max": 375},
                "size_range": {"min": 5000, "max": 100000},
                "trade_breakdown": {
                    "structural": 0.12,
                    "mechanical": 0.25,
                    "electrical": 0.14,
                    "plumbing": 0.11,
                    "finishes": 0.25,
                    "general_conditions": 0.13
                }
            },
            "dental_office": {
                "name": "Dental Office",
                "base_construction_cost": 300,
                "equipment_cost": 30,
                "total_cost_range": {"min": 315, "max": 360},
                "size_range": {"min": 2000, "max": 10000}
            },
            "rehabilitation": {
                "name": "Rehabilitation Center",
                "base_construction_cost": 325,
                "equipment_cost": 100,
                "total_cost_range": {"min": 400, "max": 475},
                "size_range": {"min": 20000, "max": 100000}
            },
            "nursing_home": {
                "name": "Nursing Home / Senior Care",
                "base_construction_cost": 275,
                "equipment_cost": 10,
                "total_cost_range": {"min": 275, "max": 325},
                "size_range": {"min": 20000, "max": 150000}
            }
        }
    }
}

print(json.dumps(suggested_config, indent=2))

print("\n" + "=" * 70)
print("KEY INSIGHTS FOR MIGRATION")
print("=" * 70)

print("""
1. COST STRUCTURE:
   - Base construction costs: $275-850/SF (facility dependent)
   - Equipment costs: $10-300/SF (separate line item)
   - Special departments: $25-75/SF premiums
   - Total range: $285-1200/SF all-in

2. TRADE ALLOCATION DIFFERENCES:
   - Hospitals: 35% mechanical (vs 20% commercial) due to medical gas
   - Surgical: 38% mechanical for OR precise HVAC
   - Imaging: 18% structural for shielding, 22% electrical for power

3. SPECIAL SPACES (for hospitals):
   - Emergency Dept: 15% of building area, +$50/SF
   - Operating Rooms: 10% of building area, +$75/SF
   - ICU: 10% of building area, +$60/SF
   - Imaging: 5% of building area, +$40/SF
   - Laboratory: 5% of building area, +$25/SF

4. EQUIPMENT COSTS (major differentiator):
   - Imaging Centers: $300/SF (MRI, CT equipment)
   - Surgical Centers: $200/SF (OR equipment)
   - Hospitals: $150/SF (general medical equipment)
   - Urgent Care: $75/SF (basic diagnostic)
   - Medical Office: $20/SF (exam room basics)

5. SIZE RANGES:
   - Hospitals: 50,000-500,000 SF
   - Medical Centers: 30,000-200,000 SF
   - Surgical Centers: 10,000-50,000 SF
   - Medical Offices: 5,000-100,000 SF
   - Urgent Care: 3,000-10,000 SF
""")