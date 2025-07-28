#!/usr/bin/env python
"""Test hospital scope generation with occupancy type"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.scope import ScopeRequest, ProjectType
from app.core.engine import DeterministicScopeEngine

# Create test request
request = ScopeRequest(
    project_name="Test Hospital",
    project_type=ProjectType.COMMERCIAL,
    square_footage=200000,
    location="Houston, TX",
    num_floors=4,
    occupancy_type="healthcare",
    special_requirements="emergency department, 150 patient beds, operating rooms, imaging center, laboratory, pharmacy, cafeteria"
)

print(f"Request occupancy_type: {request.occupancy_type}")
print(f"Has occupancy_type attr: {hasattr(request, 'occupancy_type')}")

# Generate scope
engine = DeterministicScopeEngine()
response = engine.generate_scope(request)

print(f"\nResponse request_data occupancy_type: {response.request_data.occupancy_type}")

# Check for elevators in mechanical category
print("\n=== CHECKING FOR ELEVATORS ===")
for category in response.categories:
    if category.name == "Mechanical":
        print(f"\nMechanical items ({len(category.systems)} total):")
        for system in category.systems:
            if 'elevator' in system.name.lower():
                print(f"  ✓ {system.name}: {system.quantity} {system.unit} @ ${system.unit_cost:,.0f} = ${system.total_cost:,.0f}")
                if hasattr(system, 'note'):
                    print(f"    Note: {system.note}")

# Check totals
print(f"\nTotal cost: ${response.total_cost:,.0f}")
print(f"Cost per SF: ${response.cost_per_sqft:.2f}")