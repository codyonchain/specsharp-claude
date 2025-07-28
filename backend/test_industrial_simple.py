#!/usr/bin/env python3
"""Simple test for industrial building type"""

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
    exit(1)

# Test industrial project WITHOUT setting occupancy_type
print("\n=== Testing Industrial Building (Relying on NLP) ===")
project_data = {
    "project_name": "Advanced Manufacturing Facility",
    "project_type": "industrial",
    "square_footage": 100000,
    "location": "Dallas, TX",
    "num_floors": 1,
    "ceiling_height": 30,
    "occupancy_type": "industrial",
    "special_requirements": "Industrial manufacturing facility with 10-ton bridge crane, compressed air system, dust collection, and motor control centers"
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
    print(f"Building Type (direct): {result.get('occupancy_type', 'Not in root')}")
    print(f"Building Type (request_data): {result.get('request_data', {}).get('occupancy_type', 'Not detected')}")
    print(f"Total Cost: ${result['total_cost']:,.2f}")
    print(f"Cost per SF: ${result['cost_per_sqft']:.2f}")
    
    # Look for industrial-specific systems
    print(f"\n--- All Systems ---")
    for category in result['categories']:
        print(f"\n{category['name']} (${category['subtotal']:,.2f}):")
        for system in category['systems'][:5]:  # Show first 5 systems
            print(f"  - {system['name']}: {system['quantity']} {system['unit']} @ ${system['unit_cost']:.2f} = ${system['total_cost']:,.2f}")
        if len(category['systems']) > 5:
            print(f"  ... and {len(category['systems']) - 5} more systems")
else:
    print(f"Request failed: {response.status_code}")
    print(response.json())