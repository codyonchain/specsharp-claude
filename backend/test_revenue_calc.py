#!/usr/bin/env python
"""Test revenue calculation for restaurant projects"""

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass
import json

# Create the engine
engine = UnifiedEngine()

# Calculate the project directly
result = engine.calculate_project(
    building_type=BuildingType.RESTAURANT,
    subtype='full_service',
    square_footage=4200,
    location='Franklin, TN',
    project_class=ProjectClass.GROUND_UP
)

# Print what's calculated
print('=== CALCULATED DATA ===')
print(f'Building Type: {result.get("building_type")}')
print(f'Square Footage: {result.get("square_footage")}')
print(f'Total Cost: ${result.get("total_cost", 0):,.2f}')
print(f'Cost per SF: ${result.get("cost_per_sqft", 0):.2f}')
print()

# Check revenue analysis at top level
if 'revenue_analysis' in result:
    print('=== REVENUE ANALYSIS (Top Level) ===')
    print(json.dumps(result['revenue_analysis'], indent=2))
else:
    print('NO revenue_analysis at top level')
    
print()

# Check ownership analysis
if 'ownership_analysis' in result:
    print('=== OWNERSHIP ANALYSIS ===')
    ownership = result['ownership_analysis']
    if 'revenue_analysis' in ownership:
        print('Has revenue_analysis in ownership:')
        print(json.dumps(ownership['revenue_analysis'], indent=2))
    if 'roi_analysis' in ownership:
        print('Has roi_analysis in ownership:')
        print(json.dumps(ownership['roi_analysis'], indent=2))
else:
    print('NO ownership_analysis')
    
print()

# Check roi_analysis at top level
if 'roi_analysis' in result:
    print('=== ROI ANALYSIS (Top Level) ===')
    print(json.dumps(result['roi_analysis'], indent=2))
    
print()

# Check calculation_data
if 'calculation_data' in result:
    print('=== CALCULATION_DATA ===')
    calc_data = result['calculation_data']
    if 'revenue_analysis' in calc_data:
        print('Has revenue_analysis in calculation_data:')
        print(json.dumps(calc_data['revenue_analysis'], indent=2))
    if 'ownership_analysis' in calc_data:
        print('Has ownership_analysis in calculation_data')
        if 'revenue_analysis' in calc_data['ownership_analysis']:
            print('Has revenue_analysis in ownership_analysis:')
            print(json.dumps(calc_data['ownership_analysis']['revenue_analysis'], indent=2))