#!/usr/bin/env python3
"""
Test script to verify financial metrics are properly configured for all 57 subtypes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.v2.config.master_config import MASTER_CONFIG, BuildingType
from app.v2.engines.unified_engine import unified_engine

def test_all_financial_metrics():
    """Test that all subtypes have financial metrics configured."""
    
    results = {
        'configured': [],
        'missing': [],
        'errors': []
    }
    
    # Test each building type and subtype
    for building_type in BuildingType:
        if building_type not in MASTER_CONFIG:
            continue
            
        subtypes = MASTER_CONFIG[building_type]
        
        for subtype_name, config in subtypes.items():
            try:
                # Check if financial_metrics exists
                financial_metrics = getattr(config, 'financial_metrics', None)
                
                if financial_metrics:
                    # Verify required fields
                    required_fields = [
                        'primary_unit',
                        'units_per_sf',
                        'revenue_per_unit_annual',
                        'market_rate_type',
                        'market_rate_default',
                        'display_name'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in financial_metrics:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        results['errors'].append({
                            'type': building_type.value,
                            'subtype': subtype_name,
                            'missing_fields': missing_fields
                        })
                    else:
                        results['configured'].append({
                            'type': building_type.value,
                            'subtype': subtype_name,
                            'primary_unit': financial_metrics['primary_unit'],
                            'display_name': financial_metrics['display_name']
                        })
                else:
                    results['missing'].append({
                        'type': building_type.value,
                        'subtype': subtype_name
                    })
                    
            except Exception as e:
                results['errors'].append({
                    'type': building_type.value,
                    'subtype': subtype_name,
                    'error': str(e)
                })
    
    # Print results
    print("=" * 80)
    print("FINANCIAL METRICS CONFIGURATION TEST RESULTS")
    print("=" * 80)
    
    print(f"\n✅ CONFIGURED: {len(results['configured'])} subtypes")
    if results['configured']:
        for item in results['configured'][:5]:  # Show first 5
            print(f"  - {item['type']}/{item['subtype']}: {item['primary_unit']} - {item['display_name']}")
        if len(results['configured']) > 5:
            print(f"  ... and {len(results['configured']) - 5} more")
    
    print(f"\n❌ MISSING: {len(results['missing'])} subtypes")
    if results['missing']:
        for item in results['missing']:
            print(f"  - {item['type']}/{item['subtype']}")
    
    print(f"\n⚠️  ERRORS: {len(results['errors'])} subtypes")
    if results['errors']:
        for item in results['errors']:
            print(f"  - {item['type']}/{item['subtype']}: {item.get('error', 'Missing fields: ' + str(item.get('missing_fields', [])))}")
    
    return results

def test_revenue_calculation():
    """Test revenue requirement calculations for a sample project."""
    
    print("\n" + "=" * 80)
    print("REVENUE REQUIREMENT CALCULATION TEST")
    print("=" * 80)
    
    # Test cases for different building types
    test_cases = [
        {
            'building_type': BuildingType.HEALTHCARE,
            'subtype': 'hospital',
            'square_footage': 100000,
            'location': 'Nashville, TN'
        },
        {
            'building_type': BuildingType.MULTIFAMILY,
            'subtype': 'luxury_apartments',
            'square_footage': 150000,
            'location': 'New York, NY'
        },
        {
            'building_type': BuildingType.CIVIC,
            'subtype': 'library',
            'square_footage': 50000,
            'location': 'Chicago, IL'
        },
        {
            'building_type': BuildingType.PARKING,
            'subtype': 'parking_garage',
            'square_footage': 200000,
            'location': 'San Francisco, CA'
        },
        {
            'building_type': BuildingType.SPECIALTY,
            'subtype': 'data_center',
            'square_footage': 75000,
            'location': 'Austin, TX'
        }
    ]
    
    for test in test_cases:
        try:
            print(f"\nTesting: {test['building_type'].value}/{test['subtype']}")
            print(f"  Location: {test['location']}, Size: {test['square_footage']:,} SF")
            
            # Calculate project
            result = unified_engine.calculate_project(
                building_type=test['building_type'],
                subtype=test['subtype'],
                square_footage=test['square_footage'],
                location=test['location']
            )
            
            # Check for revenue requirements
            if 'revenue_requirements' in result:
                req = result['revenue_requirements']
                if req and 'display_name' in req:
                    print(f"  ✅ {req['display_name']}")
                    print(f"     Primary Unit: {req.get('primary_unit', 'N/A')}")
                    print(f"     Total Units: {req.get('total_units', 'N/A')}")
                    print(f"     Feasibility: {req.get('feasibility', {}).get('status', 'N/A')}")
                else:
                    print(f"  ⚠️  Revenue requirements incomplete")
            else:
                print(f"  ❌ No revenue requirements found")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

def main():
    """Run all tests."""
    
    # Test configuration
    config_results = test_all_financial_metrics()
    
    # Test calculations
    test_revenue_calculation()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(config_results['configured']) + len(config_results['missing']) + len(config_results['errors'])
    success_rate = (len(config_results['configured']) / total * 100) if total > 0 else 0
    
    print(f"Total Subtypes: {total}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED! All 57 subtypes have financial metrics configured.")
    elif success_rate >= 90:
        print("\n✅ MOSTLY COMPLETE: Most subtypes have financial metrics configured.")
    else:
        print("\n⚠️  NEEDS WORK: Several subtypes still need financial metrics.")

if __name__ == '__main__':
    main()