#!/usr/bin/env python3
"""Test confidence scoring system"""

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

# Test cases for confidence scoring
test_cases = [
    {
        "name": "Simple Office - High Confidence",
        "data": {
            "project_name": "Standard Office Building",
            "project_type": "commercial",
            "square_footage": 50000,
            "location": "Dallas, TX",
            "num_floors": 3,
            "ceiling_height": 9,
            "occupancy_type": "office",
            "special_requirements": "Standard office building with typical systems"
        }
    },
    {
        "name": "Complex Healthcare - Lower Confidence",
        "data": {
            "project_name": "Advanced Medical Center",
            "project_type": "commercial",
            "square_footage": 150000,
            "location": "San Francisco, CA",
            "num_floors": 5,
            "ceiling_height": 12,
            "occupancy_type": "healthcare",
            "special_requirements": "Hospital with clean rooms, medical gas, advanced HVAC"
        }
    },
    {
        "name": "Volatile Market Industrial",
        "data": {
            "project_name": "NYC Manufacturing Facility",
            "project_type": "industrial",
            "square_footage": 100000,
            "location": "New York, NY",
            "num_floors": 2,
            "ceiling_height": 20,
            "occupancy_type": "industrial",
            "special_requirements": "Industrial facility with specialized equipment"
        }
    }
]

# Test each case
for test_case in test_cases:
    print(f"\n=== {test_case['name']} ===")
    print(f"Location: {test_case['data']['location']}")
    print(f"Building Type: {test_case['data']['occupancy_type']}")
    
    response = requests.post(
        f"{base_url}/scope/generate",
        json=test_case['data'],
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Project ID: {result['project_id']}")
        print(f"✓ Total Cost: ${result['total_cost']:,.2f}")
        
        # Analyze confidence scores
        confidence_summary = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "No Data": 0
        }
        
        total_items = 0
        sample_items = []
        
        for category in result['categories']:
            for system in category['systems']:
                total_items += 1
                label = system.get('confidence_label', 'No Data')
                score = system.get('confidence_score', 0)
                
                if label in confidence_summary:
                    confidence_summary[label] += 1
                else:
                    confidence_summary["No Data"] += 1
                
                # Collect samples of each confidence level
                if len(sample_items) < 5 and label != 'High':
                    sample_items.append({
                        'name': system['name'],
                        'score': score,
                        'label': label,
                        'factors': system.get('confidence_factors', {})
                    })
        
        print(f"\n--- Confidence Summary ---")
        print(f"Total Items: {total_items}")
        for label, count in confidence_summary.items():
            if count > 0:
                percentage = (count / total_items) * 100
                print(f"{label}: {count} items ({percentage:.1f}%)")
        
        if sample_items:
            print(f"\n--- Lower Confidence Items ---")
            for item in sample_items:
                print(f"\n{item['name']} - {item['label']} ({item['score']}%)")
                factors = item.get('factors', {})
                if factors and 'adjustments' in factors:
                    for adj in factors['adjustments']:
                        print(f"  • {adj['reason']}: {adj['adjustment']:+d} points")
    else:
        print(f"✗ Request failed: {response.status_code}")
        print(response.json())

print("\n=== Confidence Scoring Analysis Complete ===")
print("The confidence scoring system considers:")
print("• Building type complexity")
print("• Quantity reasonableness")
print("• Regional market volatility")
print("• Specialized system complexity")
print("• Material price volatility")