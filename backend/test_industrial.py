#!/usr/bin/env python3
"""Test industrial building type implementation"""

import requests
import json

# API base URL
base_url = "http://localhost:8001/api/v1"

# Test credentials
test_email = "test2@example.com"
test_password = "password123"

# Login first
print("=== Logging in ===")
login_data = {
    "username": test_email,
    "password": test_password
}
login_response = requests.post(f"{base_url}/auth/token", data=login_data)
if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("Login successful!")
    headers = {"Authorization": f"Bearer {token}"}
else:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.json())
    exit(1)

# Test cases for different industrial types
test_cases = [
    {
        "name": "General Manufacturing",
        "data": {
            "project_name": "Steel Components Manufacturing",
            "project_type": "industrial",
            "square_footage": 100000,
            "location": "Dallas, TX",
            "num_floors": 1,
            "ceiling_height": 30,
            "occupancy_type": "industrial",
            "special_requirements": "Industrial manufacturing facility with heavy machinery, 10-ton bridge crane, compressed air system"
        }
    },
    {
        "name": "Clean Room / Pharmaceutical",
        "data": {
            "project_name": "Biotech Clean Room Facility",
            "project_type": "industrial",
            "square_footage": 50000,
            "location": "Boston, MA",
            "num_floors": 2,
            "ceiling_height": 12,
            "special_requirements": "Pharmaceutical manufacturing with Class 10000 clean rooms, HEPA filtration, epoxy flooring"
        }
    },
    {
        "name": "Food Processing",
        "data": {
            "project_name": "Craft Brewery Production",
            "project_type": "industrial",
            "square_footage": 75000,
            "location": "Portland, OR",
            "num_floors": 1,
            "ceiling_height": 20,
            "special_requirements": "Food and beverage processing facility with brewhouse, fermentation tanks, bottling line, cold storage"
        }
    },
    {
        "name": "Data Center",
        "data": {
            "project_name": "Enterprise Data Center",
            "project_type": "industrial",
            "square_footage": 25000,
            "location": "Austin, TX",
            "num_floors": 1,
            "ceiling_height": 14,
            "special_requirements": "Tier 3 data center with redundant power, UPS systems, CRAC units, raised floor"
        }
    }
]

# Test each case
for test_case in test_cases:
    print(f"\n=== Testing {test_case['name']} ===")
    print(f"Description: {test_case['data']['special_requirements']}")
    
    response = requests.post(
        f"{base_url}/scope/generate",
        json=test_case['data'],
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Project ID: {result['project_id']}")
        print(f"✓ Building Type: {result.get('occupancy_type', 'Not detected')}")
        print(f"✓ Total Cost: ${result['total_cost']:,.2f}")
        print(f"✓ Cost per SF: ${result['cost_per_sqft']:.2f}")
        
        # Look for specialized equipment
        print("\nSpecialized Equipment Found:")
        found_equipment = False
        for category in result['categories']:
            for system in category['systems']:
                # Check for industrial-specific items
                if any(keyword in system['name'].lower() for keyword in [
                    'compressed air', 'dust collection', 'crane', 'motor control',
                    'clean room', 'hepa', 'washdown', 'ups', 'crac', 'raised floor'
                ]):
                    print(f"  - {system['name']}: {system['quantity']} {system['unit']} = ${system['total_cost']:,.2f}")
                    found_equipment = True
        
        if not found_equipment:
            print("  - No specialized equipment found")
            
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(response.json())

print("\n=== Cost Comparison ===")
print("Expected industrial costs are typically higher due to:")
print("- Heavy structural requirements (12 lbs/SF vs 10 for office)")
print("- Specialized mechanical systems (compressed air, dust collection)")
print("- Higher electrical loads (15W/SF vs 6W/SF for office)")
print("- Process piping and specialized equipment")