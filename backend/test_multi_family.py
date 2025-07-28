#!/usr/bin/env python3
"""Test script for multi-family residential building type"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.services.nlp_service import nlp_service

# Test descriptions
test_descriptions = [
    "100 unit apartment complex with fitness center and pool",
    "50 unit condo building with underground parking",
    "120 units: 60 1BR, 40 2BR, 20 3BR with clubhouse and leasing office",
    "Luxury apartment building with 200 units and rooftop deck",
    "Mixed income housing development with 80 affordable units",
    "Senior living facility with 60 apartments",
    "Student housing complex near university with 150 units",
    "Single family home in suburbs",  # Should NOT be multi-family
    "Office building with 50,000 square feet",  # Should NOT be multi-family
]

print("=== Testing Building Type Detection ===\n")

for desc in test_descriptions:
    building_type = determine_building_type(desc)
    subtype = get_building_subtype(building_type, desc)
    print(f"Description: {desc}")
    print(f"Building Type: {building_type}")
    if subtype:
        print(f"Subtype: {subtype}")
    print("-" * 50)

print("\n=== Testing Unit Mix Parser ===\n")

# Test unit mix parsing
unit_mix_tests = [
    "120 units: 60 1BR, 40 2BR, 20 3BR",
    "100 apartments with 50 studios, 30 one-bedroom, 20 two-bedroom",
    "50 unit complex with 150 parking spaces",
    "80 unit building with fitness center, pool, and business center",
    "200 luxury apartments with rooftop deck and dog park",
]

for desc in unit_mix_tests:
    unit_mix = nlp_service.parse_unit_mix(desc)
    print(f"Description: {desc}")
    print(f"Total Units: {unit_mix['total_units']}")
    print(f"Unit Breakdown: {unit_mix['unit_breakdown']}")
    print(f"Amenities: {unit_mix['amenity_spaces']}")
    print(f"Parking Spaces: {unit_mix['parking_spaces']}")
    print(f"Average Unit Size: {unit_mix['average_unit_size']} SF")
    print("-" * 50)

print("\n=== Testing NLP Service Extraction ===\n")

# Test full NLP extraction
nlp_test = "New 150,000 sq ft apartment complex in Austin TX with 120 units: 60 1BR, 40 2BR, 20 3BR. Include fitness center, pool, and 180 parking spaces. 4 stories with elevators."

result = nlp_service._fallback_analysis(nlp_test)
print(f"Description: {nlp_test}")
print(f"Occupancy Type: {result.get('occupancy_type')}")
print(f"Project Type: {result.get('project_type')}")
print(f"Extracted Details: {result.get('extracted_details')}")
if result.get('unit_mix'):
    print(f"Unit Mix: {result.get('unit_mix')}")