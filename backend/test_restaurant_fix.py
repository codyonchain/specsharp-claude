#!/usr/bin/env python3
"""
Test script to verify restaurant cost calculation with new TN multiplier
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.engine import DeterministicScopeEngine
from app.models.scope import ScopeRequest

def test_nashville_restaurant():
    """Test restaurant project in Nashville with corrected multiplier"""
    
    # Initialize engine
    engine = DeterministicScopeEngine()
    
    # Create test request for Nashville restaurant
    request = ScopeRequest(
        project_name="Test Nashville Restaurant",
        project_type="commercial",
        square_footage=4200,
        location="Nashville, TN",
        num_floors=1,
        ceiling_height=21,
        occupancy_type="restaurant",
        service_level="full_service"
    )
    
    # Generate scope
    print("Generating scope for Nashville restaurant...")
    print(f"Square Footage: {request.square_footage}")
    print(f"Location: {request.location}")
    print(f"Service Level: full_service")
    print()
    
    # Check multiplier calculation
    multiplier = engine._calculate_multiplier(request)
    print(f"Calculated Multiplier: {multiplier}")
    
    # Get location multiplier specifically
    location_mult = engine._get_location_multiplier(request.location)
    print(f"Location Multiplier (TN): {location_mult}")
    
    # Project type multiplier
    project_mult = engine.cost_multipliers["project_type"].get(request.project_type, 1.0)
    print(f"Project Type Multiplier: {project_mult}")
    print(f"Total Multiplier: {location_mult * project_mult}")
    print()
    
    # Generate full scope
    scope_response = engine.generate_scope(request)
    
    print(f"Results:")
    print(f"Subtotal: ${scope_response.subtotal:,.2f}")
    print(f"Contingency ({scope_response.contingency_percentage}%): ${scope_response.contingency_amount:,.2f}")
    print(f"Total Cost: ${scope_response.total_cost:,.2f}")
    print(f"Cost per SF: ${scope_response.cost_per_sqft:.2f}")
    print()
    
    # Check if in target range
    target_min = 550
    target_max = 650
    in_range = target_min <= scope_response.cost_per_sqft <= target_max
    
    print(f"Target Range: ${target_min}-${target_max}/SF")
    print(f"In Range: {'✓ Yes' if in_range else '✗ No'}")
    
    if not in_range:
        print(f"WARNING: Cost per SF is outside target range!")
        if scope_response.cost_per_sqft < target_min:
            print(f"  Too low by ${target_min - scope_response.cost_per_sqft:.2f}/SF")
        else:
            print(f"  Too high by ${scope_response.cost_per_sqft - target_max:.2f}/SF")
    
    return scope_response

if __name__ == "__main__":
    test_nashville_restaurant()