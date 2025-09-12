#!/usr/bin/env python3
"""
Test multiple building types to find investment viability issues
"""

import sys
import os
sys.path.append('/Users/codymarchant/specsharp/backend')

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def test_building_type(building_type, subtype, sf, location="Nashville", expected_cap_rate=None):
    """Test a building type and return key metrics"""
    
    engine = UnifiedEngine()
    
    result = engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=sf,
        location=location,
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT
    )
    
    # Extract key metrics
    total_cost = result['totals']['total_project_cost']
    
    revenue_analysis = result.get('revenue_analysis', {})
    annual_revenue = revenue_analysis.get('annual_revenue', 0)
    net_income = revenue_analysis.get('net_income', 0)
    
    return_metrics = result.get('return_metrics', {})
    cap_rate = return_metrics.get('cap_rate', 0)
    irr = return_metrics.get('irr', 0)
    
    revenue_requirements = result.get('revenue_requirements', {})
    feasibility = revenue_requirements.get('feasibility', 'Unknown')
    required_return = revenue_requirements.get('required_value', 0)
    gap = revenue_requirements.get('gap', 0)
    
    operational_efficiency = result.get('operational_efficiency', {})
    expense_ratio = operational_efficiency.get('expense_ratio', 0)
    
    return {
        'building': f"{result['project_info']['display_name']}",
        'size': f"{sf:,} SF",
        'total_cost': total_cost,
        'cost_per_sf': total_cost / sf,
        'annual_revenue': annual_revenue,
        'net_income': net_income,
        'cap_rate': cap_rate,
        'irr': irr,
        'expense_ratio': expense_ratio,
        'feasibility': feasibility,
        'required_return': required_return,
        'actual_return': net_income,
        'gap': gap,
        'expected_cap_rate': expected_cap_rate
    }

def main():
    """Test various building types"""
    
    print("=== BUILDING TYPE INVESTMENT VIABILITY ANALYSIS ===\n")
    
    # Test cases: building_type, subtype, square_footage, expected_cap_rate
    test_cases = [
        (BuildingType.INDUSTRIAL, 'warehouse', 50000, 7.0),  # 6-8% market cap rate
        (BuildingType.OFFICE, 'class_a', 25000, 7.5),        # 7-9% market cap rate
        (BuildingType.MULTIFAMILY, 'market_rate', 30000, 6.0), # 5-7% market cap rate
        (BuildingType.RETAIL, 'neighborhood_center', 15000, 8.0), # 7-9% market cap rate
        (BuildingType.RESTAURANT, 'casual_dining', 4000, 10.0),   # 8-12% for restaurants
    ]
    
    results = []
    
    for building_type, subtype, sf, expected_cap in test_cases:
        try:
            result = test_building_type(building_type, subtype, sf, expected_cap_rate=expected_cap)
            results.append(result)
            
            print(f"📊 {result['building']} ({result['size']})")
            print(f"   Cost: ${result['total_cost']:,.0f} (${result['cost_per_sf']:.0f}/SF)")
            print(f"   Revenue: ${result['annual_revenue']:,.0f}")
            print(f"   Net Income: ${result['actual_return']:,.0f}")
            print(f"   Cap Rate: {result['cap_rate']:.1f}% (Expected: {result['expected_cap_rate']:.1f}%)")
            print(f"   IRR: {result['irr']:.1f}%")
            print(f"   Expense Ratio: {result['expense_ratio']:.1%}")
            print(f"   Required Return: ${result['required_return']:,.0f}")
            print(f"   Gap: ${result['gap']:,.0f}")
            print(f"   Feasibility: {result['feasibility']}")
            
            # Analysis
            if result['cap_rate'] >= result['expected_cap_rate'] * 0.8:  # Within 20% of expected
                print("   ✅ Cap rate reasonable")
            else:
                print(f"   ❌ Cap rate too low (actual: {result['cap_rate']:.1f}%, expected: {result['expected_cap_rate']:.1f}%)")
            
            if result['feasibility'] == 'Feasible':
                print("   ✅ Project shows as investable")
            else:
                print(f"   ❌ Project shows as NOT investable")
            
            print()
            
        except Exception as e:
            print(f"❌ Error testing {building_type.value}/{subtype}: {e}")
            print()
    
    # Summary
    print("=== SUMMARY ===")
    investable_count = sum(1 for r in results if r['feasibility'] == 'Feasible')
    total_count = len(results)
    
    print(f"Investable projects: {investable_count}/{total_count}")
    
    if investable_count == 0:
        print("🚨 CRITICAL: NO PROJECTS SHOWING AS INVESTABLE")
        print("   This suggests systematic issues with:")
        print("   1. Target ROI expectations too high")
        print("   2. Revenue projections too low") 
        print("   3. Expense ratios too high")
        print("   4. Cost calculations inflated")
    
    # Find buildings with highest gaps
    if results:
        worst_gap = min(results, key=lambda x: x['gap'])
        print(f"\nWorst performer: {worst_gap['building']}")
        print(f"   Gap: ${worst_gap['gap']:,.0f}")
        print(f"   Required: ${worst_gap['required_return']:,.0f}")
        print(f"   Actual: ${worst_gap['actual_return']:,.0f}")

if __name__ == "__main__":
    main()