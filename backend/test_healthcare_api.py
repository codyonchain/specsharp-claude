#!/usr/bin/env python3
"""
Test Healthcare API Integration
Tests the new /calculate-with-healthcare endpoint
"""

import requests
import json
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8001/api/v1"

# Test cases for healthcare detection and cost calculation
TEST_CASES = [
    {
        "name": "Nashville Hospital",
        "data": {
            "description": "50,000 sf hospital with emergency department and surgical suite",
            "building_type": "medical",
            "square_footage": 50000,
            "location": "Nashville, TN"
        },
        "expected": {
            "is_healthcare": True,
            "has_dual_view": True,
            "facility_type": "general_hospital"
        }
    },
    {
        "name": "Manchester Medical Office",
        "data": {
            "description": "15,000 sf medical office building",
            "building_type": "medical",
            "square_footage": 15000,
            "location": "Manchester, NH"
        },
        "expected": {
            "is_healthcare": True,
            "has_dual_view": True,
            "facility_type": "medical_office"
        }
    },
    {
        "name": "Franklin Urgent Care",
        "data": {
            "description": "8,000 sf urgent care with x-ray",
            "building_type": "medical",
            "square_footage": 8000,
            "location": "Franklin, TN"
        },
        "expected": {
            "is_healthcare": True,
            "has_dual_view": True,
            "facility_type": "urgent_care"
        }
    },
    {
        "name": "Regular Office Building",
        "data": {
            "description": "75,000 sf office building",
            "building_type": "commercial",
            "square_footage": 75000,
            "location": "Nashville, TN"
        },
        "expected": {
            "is_healthcare": False,
            "has_dual_view": False,
            "facility_type": None
        }
    },
    {
        "name": "Mixed Use with Medical",
        "data": {
            "description": "100,000 sf mixed use 60% warehouse 40% medical office",
            "building_type": "mixed_use",
            "square_footage": 100000,
            "location": "Nashua, NH"
        },
        "expected": {
            "is_healthcare": True,
            "has_dual_view": True,
            "facility_type": "medical_office"
        }
    }
]

def get_auth_token() -> str:
    """Get authentication token"""
    # Login first
    login_data = {
        "username": "test2@example.com",
        "password": "password123"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Failed to authenticate: {response.status_code}")
        print(response.text)
        return None

def test_healthcare_endpoint(token: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Test the healthcare calculation endpoint"""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/cost/calculate-with-healthcare",
        json=test_case["data"],
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return None

def validate_response(result: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    """Validate the API response against expected values"""
    
    checks = []
    
    # Check if healthcare detection is correct
    is_healthcare = result.get("is_healthcare", False)
    checks.append(("Healthcare Detection", is_healthcare == expected["is_healthcare"]))
    
    # Check display mode
    has_dual = result.get("display_mode") == "dual"
    checks.append(("Dual View Mode", has_dual == expected["has_dual_view"]))
    
    # Check facility type if healthcare
    if expected["facility_type"]:
        facility_type = result.get("building_classification")
        checks.append(("Facility Type", facility_type == expected["facility_type"]))
    
    # Check for healthcare view data
    if expected["is_healthcare"]:
        has_healthcare_view = "healthcare_view" in result
        checks.append(("Healthcare View Data", has_healthcare_view))
        
        if has_healthcare_view:
            hv = result["healthcare_view"]
            checks.append(("Has Construction Data", "construction" in hv))
            checks.append(("Has Equipment Data", "equipment" in hv))
            checks.append(("Has Project Total", "project_total" in hv))
    
    # Check for standard view
    has_standard_view = "standard_view" in result
    checks.append(("Standard View Data", has_standard_view))
    
    return checks

def main():
    print("=" * 80)
    print("HEALTHCARE API INTEGRATION TEST")
    print("=" * 80)
    
    # Get authentication token
    print("\n1. Authenticating...")
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Exiting.")
        return
    print("✓ Authentication successful")
    
    # Run test cases
    print("\n2. Running test cases...")
    print("-" * 80)
    
    for test_case in TEST_CASES:
        print(f"\nTest: {test_case['name']}")
        print(f"  Description: {test_case['data']['description']}")
        print(f"  Location: {test_case['data']['location']}")
        
        result = test_healthcare_endpoint(token, test_case)
        
        if result:
            checks = validate_response(result, test_case["expected"])
            
            all_passed = all(check[1] for check in checks)
            status = "✓ PASSED" if all_passed else "✗ FAILED"
            
            print(f"  Result: {status}")
            for check_name, passed in checks:
                symbol = "✓" if passed else "✗"
                print(f"    {symbol} {check_name}")
            
            # Show cost details if healthcare
            if result.get("is_healthcare") and "healthcare_view" in result:
                hv = result["healthcare_view"]
                if "construction" in hv:
                    print(f"    Construction: ${hv['construction']['total']:,.0f} (${hv['construction']['cost_per_sf']:.0f}/SF)")
                if "equipment" in hv:
                    print(f"    Equipment: ${hv['equipment']['total']:,.0f}")
                if "project_total" in hv:
                    print(f"    Total: ${hv['project_total']['all_in_total']:,.0f} (${hv['project_total']['all_in_cost_per_sf']:.0f}/SF)")
        else:
            print("  Result: ✗ API ERROR")
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()