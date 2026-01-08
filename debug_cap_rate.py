#!/usr/bin/env python3
"""
Debug cap rate calculation issue
"""

import sys
import os
sys.path.append('/Users/codymarchant/specsharp/backend')

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def debug_cap_rate():
    """Debug why cap rate is showing as 0%"""
    
    engine = UnifiedEngine()
    
    result = engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype='warehouse',
        square_footage=50000,
        location='Nashville',
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT
    )
    
    print("=== CAP RATE DEBUGGING ===")
    
    # Extract values used in cap rate calculation
    total_cost = result['totals']['total_project_cost']
    print(f"Total Cost: ${total_cost:,.2f}")
    
    revenue_analysis = result.get('revenue_analysis', {})
    net_income = revenue_analysis.get('net_income', 0)
    print(f"Net Income: ${net_income:,.2f}")
    
    return_metrics = result.get('return_metrics', {})
    cap_rate = return_metrics.get('cap_rate', 0)
    print(f"Reported Cap Rate: {cap_rate}%")
    
    # Manual calculation
    if total_cost > 0 and net_income > 0:
        manual_cap_rate = (net_income / total_cost) * 100
        print(f"Manual Cap Rate: {manual_cap_rate:.2f}%")
        
        if abs(cap_rate - manual_cap_rate) > 0.01:
            print(f"❌ MISMATCH: Reported vs Manual cap rate")
            print(f"   Difference: {abs(cap_rate - manual_cap_rate):.2f} percentage points")
        else:
            print("✅ Cap rate calculation matches")
    else:
        print(f"❌ Invalid values for cap rate calculation:")
        print(f"   total_cost > 0: {total_cost > 0}")
        print(f"   net_income > 0: {net_income > 0}")
    
    # Check IRR calculation inputs
    irr = return_metrics.get('irr', 0)
    print(f"\nIRR: {irr}%")
    
    # Check if IRR function is working
    manual_irr = engine.calculate_irr(
        initial_investment=total_cost,
        annual_cash_flow=net_income,
        years=10
    )
    print(f"Manual IRR: {manual_irr * 100:.2f}%")
    
    # Check what the revenue requirements think the target ROI should be
    revenue_requirements = result.get('revenue_requirements', {})
    target_roi = revenue_requirements.get('target_roi', 0)
    required_return = revenue_requirements.get('required_value', 0)
    
    print(f"\n=== TARGET ROI ANALYSIS ===")
    print(f"Target ROI: {target_roi:.1%}")
    print(f"Required Return: ${required_return:,.2f}")
    print(f"Expected return from {target_roi:.1%} * ${total_cost:,.0f} = ${total_cost * target_roi:,.2f}")
    
    if abs(required_return - (total_cost * target_roi)) > 1:
        print("❌ Required return doesn't match target ROI * total cost")
    else:
        print("✅ Required return calculation correct")
    
    # Check all return metrics
    print(f"\n=== ALL RETURN METRICS ===")
    for key, value in return_metrics.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    debug_cap_rate()