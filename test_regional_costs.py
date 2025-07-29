#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print('=== TESTING COMPLETE COST ESTIMATES ===')
from app.services.cost_service import cost_service
from app.services.nlp_service import nlp_service

# Test scenarios from your requirements
test_scenarios = [
    ('50000 sf medical office building in Manchester, New Hampshire', 'healthcare'),
    ('100000 sf distribution center in Nashville, Tennessee', 'warehouse'), 
    ('75000 sf office building in Dallas, Texas', 'office')
]

for description, building_type in test_scenarios:
    print()
    print(description)
    
    # Extract location and get regional multiplier
    extracted = nlp_service.extract_project_details(description)
    location = extracted.get('location', 'Unknown')
    region = cost_service._extract_region_from_location(location)
    
    # Calculate trade cost using new method
    square_footage = extracted.get('square_footage', 50000)
    total_cost, scope_items = cost_service.calculate_trade_cost_v2(
        trade='structural',
        building_type=building_type,
        square_footage=square_footage,
        location=location
    )
    
    # Calculate per SF cost
    cost_per_sf = total_cost / square_footage
    
    print(f'  Location: {location}')
    print(f'  Region: {region}')
    print(f'  Square Footage: {square_footage}')
    print(f'  Structural Cost: ${int(total_cost)}')
    print(f'  Cost per SF: ${cost_per_sf:.2f}')

print()
print('=== COST COMPARISON BY REGION ===')
scenarios = [
    ('50000 sf office in Manchester, NH', 'NH'),
    ('50000 sf office in Nashville, TN', 'TN'), 
    ('50000 sf office in Dallas, TX', 'TX')
]

for desc, expected_region in scenarios:
    extracted = nlp_service.extract_project_details(desc)
    location = extracted.get('location', 'Unknown')
    actual_region = cost_service._extract_region_from_location(location)
    
    total_cost, _ = cost_service.calculate_trade_cost_v2(
        trade='structural',
        building_type='office',
        square_footage=50000,
        location=location
    )
    
    cost_per_sf = total_cost / 50000
    print(f'{desc:<35} -> {actual_region} (${cost_per_sf:.2f}/SF)')