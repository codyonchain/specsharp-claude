#!/usr/bin/env python3
"""
Trace return metrics calculation step by step
"""

import sys
import os
sys.path.append('/Users/codymarchant/specsharp/backend')

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def trace_return_metrics():
    """Trace return metrics through both calculation paths"""
    
    engine = UnifiedEngine()
    
    # First, test the calculate_ownership_analysis directly
    print("=== TESTING calculate_ownership_analysis DIRECTLY ===")
    
    calculations = {
        'building_type': 'industrial',
        'subtype': 'warehouse',
        'square_footage': 50000,
        'total_cost': 5437338,  # Approximate from previous test
        'subtotal': 5000000,    # Approximate construction cost
        'regional_multiplier': 1.03
    }
    
    ownership_data = engine.calculate_ownership_analysis(calculations)
    
    print("Return metrics from calculate_ownership_analysis:")
    return_metrics = ownership_data.get('return_metrics', {})
    for key, value in return_metrics.items():
        print(f"  {key}: {value}")
    
    print(f"\nRevenue analysis:")
    revenue_analysis = ownership_data.get('revenue_analysis', {})
    print(f"  Annual revenue: ${revenue_analysis.get('annual_revenue', 0):,.0f}")
    print(f"  Net income: ${revenue_analysis.get('net_income', 0):,.0f}")
    
    # Now test full calculation
    print("\n=== TESTING FULL calculate_project ===")
    
    result = engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype='warehouse',
        square_footage=50000,
        location='Nashville',
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT
    )
    
    print("Return metrics from full calculation:")
    full_return_metrics = result.get('return_metrics', {})
    for key, value in full_return_metrics.items():
        print(f"  {key}: {value}")
    
    # Check ownership_analysis separately
    print("\nOwnership analysis return metrics:")
    ownership_analysis = result.get('ownership_analysis', {})
    if ownership_analysis and 'return_metrics' in ownership_analysis:
        oa_return_metrics = ownership_analysis['return_metrics']
        for key, value in oa_return_metrics.items():
            print(f"  {key}: {value}")
    else:
        print("  No return_metrics in ownership_analysis")
    
    # Check what gets flattened to top level
    print("\nTop-level return metrics (flattened):")
    top_level_return_metrics = result.get('return_metrics', {})
    for key, value in top_level_return_metrics.items():
        print(f"  {key}: {value}")
    
    # Check if values match
    print("\n=== COMPARISON ===")
    if ownership_data and 'return_metrics' in ownership_data:
        direct_cap_rate = ownership_data['return_metrics'].get('cap_rate', 'N/A')
        full_cap_rate = result.get('return_metrics', {}).get('cap_rate', 'N/A')
        
        print(f"Direct calc cap rate: {direct_cap_rate}")
        print(f"Full calc cap rate: {full_cap_rate}")
        
        if direct_cap_rate != full_cap_rate:
            print("❌ Cap rates don't match - something is overwriting values!")
        else:
            print("✅ Cap rates match")

if __name__ == "__main__":
    trace_return_metrics()