#!/usr/bin/env python3
"""Analyze the owner view response structure"""

import json
import sys

# Load the response
try:
    with open('owner_view_response.json', 'r') as f:
        data = json.load(f)
except:
    print("Could not load owner_view_response.json")
    sys.exit(1)

def print_paths(obj, path=''):
    """Print all paths in the response that contain revenue-related data"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f'{path}.{key}' if path else key
            # Look for revenue, income, margin, roi keywords
            if any(keyword in key.lower() for keyword in ['revenue', 'income', 'margin', 'roi', 'financial']):
                if isinstance(value, (int, float)):
                    print(f'{new_path}: {value}')
                else:
                    print(f'{new_path}: {type(value).__name__}')
            if isinstance(value, dict):
                print_paths(value, new_path)
            elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                print_paths(value[0], f'{new_path}[0]')

print("=== BACKEND RESPONSE STRUCTURE ===")
print_paths(data)

print("\n=== KEY PATHS FRONTEND EXPECTS ===")
expected_paths = [
    "data.roi_analysis.financial_metrics.annual_revenue",
    "data.roi_analysis.financial_metrics.annual_net_income", 
    "data.roi_analysis.unit_metrics.revenue_per_unit",
    "data.roi_analysis.financial_metrics.roi_percentage",
    "data.roi_analysis.financial_metrics.operating_margin"
]

for path in expected_paths:
    try:
        parts = path.split('.')
        current = data
        for part in parts:
            current = current[part]
        print(f"✅ {path}: {current}")
    except (KeyError, TypeError):
        print(f"❌ {path}: NOT FOUND")

print(f"\n=== STRUCTURE COMPARISON ===")
if 'data' in data:
    print("Response structure:")
    for key in data['data'].keys():
        print(f"  data.{key}")
        if isinstance(data['data'][key], dict):
            for subkey in list(data['data'][key].keys())[:5]:  # Show first 5 keys
                print(f"    data.{key}.{subkey}")
            if len(data['data'][key].keys()) > 5:
                print(f"    ... and {len(data['data'][key].keys()) - 5} more keys")