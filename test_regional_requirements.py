#!/usr/bin/env python3
"""Test script to verify regional requirements in scope generation"""

import requests
import json
from typing import Dict, List

BASE_URL = "http://localhost:8001/api/v1"

# Test credentials
USERNAME = "test2@example.com"
PASSWORD = "password123"

def authenticate() -> str:
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Authentication failed: {response.status_code} - {response.text}")
        return None

def generate_scope(token: str, project_data: Dict) -> Dict:
    """Generate scope for a project"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/scope/generate",
        headers=headers,
        json=project_data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Scope generation failed: {response.status_code} - {response.text}")
        return None

def check_for_regional_items(scope_response: Dict, required_items: List[str]) -> Dict[str, bool]:
    """Check if scope contains required regional items"""
    found_items = {}
    
    # Extract all item names from the scope
    all_items = []
    if scope_response and "categories" in scope_response:
        for category in scope_response["categories"]:
            for system in category.get("systems", []):
                all_items.append(system.get("name", "").lower())
                # Also check notes for specific requirements
                if "note" in system:
                    all_items.append(system["note"].lower())
    
    # Check for each required item
    for item in required_items:
        found = False
        for scope_item in all_items:
            if item.lower() in scope_item:
                found = True
                break
        found_items[item] = found
    
    return found_items

def print_test_results(test_name: str, location: str, results: Dict[str, bool]):
    """Print test results in a formatted way"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"Location: {location}")
    print(f"{'='*60}")
    
    all_passed = True
    for item, found in results.items():
        status = "✓ FOUND" if found else "✗ MISSING"
        print(f"{status}: {item}")
        if not found:
            all_passed = False
    
    print(f"\nOverall: {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

def main():
    # Get authentication token
    print("Authenticating...")
    token = authenticate()
    if not token:
        print("Authentication failed. Exiting.")
        return
    
    print("Authentication successful!")
    
    # Test Case 1: NH Office Building
    print("\n\n" + "="*80)
    print("TEST CASE 1: 50,000 SF Office Building in Manchester, NH")
    print("="*80)
    
    nh_office_data = {
        "project_name": "NH Office Test",
        "project_description": "50,000 sf office building in Manchester, New Hampshire",
        "location": "Manchester, NH",
        "square_footage": 50000,
        "project_type": "commercial",
        "occupancy_type": "office",
        "num_floors": 3,
        "ceiling_height": 10,
        "foundation_type": "slab_on_grade",
        "finish_level": "standard"
    }
    
    nh_office_scope = generate_scope(token, nh_office_data)
    
    nh_required_items = [
        "snow load",
        "frost protection",
        "deep foundation",
        "insulation enhancement",
        "high efficiency",
        "snow guards",
        "reinforced roof"
    ]
    
    if nh_office_scope:
        nh_results = check_for_regional_items(nh_office_scope, nh_required_items)
        nh_passed = print_test_results("NH Office Building", "Manchester, NH", nh_results)
        
        # Print full scope for debugging
        print("\nFull scope items:")
        for category in nh_office_scope.get("categories", []):
            print(f"\nCategory: {category.get('name')}")
            for system in category.get("systems", []):
                print(f"  - {system.get('name')} (${system.get('unit_cost')}/sqft)")
    
    # Test Case 2: TN Office Building
    print("\n\n" + "="*80)
    print("TEST CASE 2: 50,000 SF Office Building in Nashville, TN")
    print("="*80)
    
    tn_office_data = {
        "project_name": "TN Office Test",
        "project_description": "50,000 sf office building in Nashville, Tennessee",
        "location": "Nashville, TN",
        "square_footage": 50000,
        "project_type": "commercial",
        "occupancy_type": "office",
        "num_floors": 3,
        "ceiling_height": 10,
        "foundation_type": "slab_on_grade",
        "finish_level": "standard"
    }
    
    tn_office_scope = generate_scope(token, tn_office_data)
    
    tn_required_items = [
        "seismic",
        "storm water",
        "retention",
        "erosion control",
        "fire sprinkler"
    ]
    
    if tn_office_scope:
        tn_results = check_for_regional_items(tn_office_scope, tn_required_items)
        tn_passed = print_test_results("TN Office Building", "Nashville, TN", tn_results)
        
        # Print full scope for debugging
        print("\nFull scope items:")
        for category in tn_office_scope.get("categories", []):
            print(f"\nCategory: {category.get('name')}")
            for system in category.get("systems", []):
                print(f"  - {system.get('name')} (${system.get('unit_cost')}/sqft)")
    
    # Test Case 3: NH Warehouse
    print("\n\n" + "="*80)
    print("TEST CASE 3: 100,000 SF Warehouse in Nashua, NH")
    print("="*80)
    
    nh_warehouse_data = {
        "project_name": "NH Warehouse Test",
        "project_description": "100,000 sf warehouse in Nashua, New Hampshire",
        "location": "Nashua, NH",
        "square_footage": 100000,
        "project_type": "industrial",
        "occupancy_type": "warehouse",
        "num_floors": 1,
        "ceiling_height": 24,
        "foundation_type": "slab_on_grade",
        "finish_level": "basic"
    }
    
    nh_warehouse_scope = generate_scope(token, nh_warehouse_data)
    
    if nh_warehouse_scope:
        nh_warehouse_results = check_for_regional_items(nh_warehouse_scope, nh_required_items)
        nh_warehouse_passed = print_test_results("NH Warehouse", "Nashua, NH", nh_warehouse_results)
    
    # Test Case 4: TN Warehouse
    print("\n\n" + "="*80)
    print("TEST CASE 4: 100,000 SF Warehouse in Nashville, TN")
    print("="*80)
    
    tn_warehouse_data = {
        "project_name": "TN Warehouse Test",
        "project_description": "100,000 sf warehouse in Nashville, Tennessee",
        "location": "Nashville, TN", 
        "square_footage": 100000,
        "project_type": "industrial",
        "occupancy_type": "warehouse",
        "num_floors": 1,
        "ceiling_height": 24,
        "foundation_type": "slab_on_grade",
        "finish_level": "basic"
    }
    
    tn_warehouse_scope = generate_scope(token, tn_warehouse_data)
    
    if tn_warehouse_scope:
        tn_warehouse_results = check_for_regional_items(tn_warehouse_scope, tn_required_items)
        tn_warehouse_passed = print_test_results("TN Warehouse", "Nashville, TN", tn_warehouse_results)

if __name__ == "__main__":
    main()