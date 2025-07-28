#!/usr/bin/env python3
"""Test multi-family residential through the API"""

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

# Test multi-family residential project
print("\n=== Testing Multi-Family Residential Project ===")
project_data = {
    "project_name": "Sunset Ridge Apartments",
    "project_type": "commercial",
    "square_footage": 150000,
    "location": "Austin, TX",
    "num_floors": 4,
    "ceiling_height": 9,
    "special_requirements": "New 150,000 sq ft apartment complex with 120 units: 60 1BR, 40 2BR, 20 3BR. Include fitness center, pool, and 180 parking spaces. 4 stories with elevators."
}

print(f"Request data: {json.dumps(project_data, indent=2)}")

response = requests.post(
    f"{base_url}/scope/generate",
    json=project_data,
    headers=headers
)

if response.status_code == 200:
    result = response.json()
    print(f"\nProject ID: {result['project_id']}")
    print(f"Building Type: {result.get('occupancy_type', 'Not detected')}")
    print(f"Total Cost: ${result['total_cost']:,.2f}")
    print(f"Cost per SF: ${result['cost_per_sqft']:.2f}")
    print(f"\n--- Cost Breakdown ---")
    for category in result['categories']:
        print(f"\n{category['name']}:")
        print(f"  Subtotal: ${category['subtotal']:,.2f}")
        if category['systems']:
            print("  Systems:")
            for system in category['systems'][:3]:  # Show first 3 systems
                print(f"    - {system['name']}: {system['quantity']} {system['unit']} @ ${system['unit_cost']:.2f} = ${system['total_cost']:,.2f}")
            if len(category['systems']) > 3:
                print(f"    ... and {len(category['systems']) - 3} more systems")
else:
    print(f"Request failed: {response.status_code}")
    print(response.json())