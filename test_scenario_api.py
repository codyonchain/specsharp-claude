#!/usr/bin/env python3
"""Test script for scenario API endpoints"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:8001/api/v1"

# Test credentials
EMAIL = "test2@example.com"
PASSWORD = "password123"

def login():
    """Login and get access token"""
    print("Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={"username": EMAIL, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Login successful")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def get_projects(token):
    """Get user's projects"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/scope/projects", headers=headers)
    if response.status_code == 200:
        projects = response.json()
        print(f"✓ Found {len(projects)} projects")
        return projects
    else:
        print(f"✗ Failed to get projects: {response.status_code}")
        return []

def test_scenario_calculation(token, project_id):
    """Test scenario impact calculation"""
    print(f"\nTesting scenario calculation for project {project_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test modifications
    modifications = {
        "modifications": {
            "square_footage": 10000,
            "finish_level": "Premium",
            "parking_type": "Garage",
            "floors": 3,
            "project_classification": "addition"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/projects/{project_id}/calculate-scenario",
        headers=headers,
        json=modifications
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✓ Scenario calculation successful:")
        print(f"  Total Cost: ${result.get('total_cost', 0):,.0f}")
        print(f"  Cost/SF: ${result.get('cost_per_sqft', 0):,.0f}")
        print(f"  Cost Delta: ${result.get('cost_delta', 0):,.0f}")
        return True
    else:
        print(f"✗ Scenario calculation failed: {response.status_code}")
        print(response.text)
        return False

def test_scenario_creation(token, project_id):
    """Test creating a scenario"""
    print(f"\nTesting scenario creation for project {project_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create a test scenario
    scenario_data = {
        "name": f"Test Scenario {datetime.now().strftime('%H:%M:%S')}",
        "description": "Testing scenario API functionality",
        "modifications": {
            "square_footage": 8000,
            "finish_level": "Luxury",
            "parking_type": "Underground",
            "floors": 5
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/projects/{project_id}/scenarios",
        headers=headers,
        json=scenario_data
    )
    
    if response.status_code == 200:
        scenario = response.json()
        print("✓ Scenario created successfully:")
        print(f"  ID: {scenario.get('id')}")
        print(f"  Name: {scenario.get('name')}")
        print(f"  Total Cost: ${scenario.get('total_cost', 0):,.0f}")
        return scenario.get('id')
    else:
        print(f"✗ Scenario creation failed: {response.status_code}")
        print(response.text)
        return None

def test_scenario_list(token, project_id):
    """Test listing scenarios"""
    print(f"\nTesting scenario list for project {project_id}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/projects/{project_id}/scenarios",
        headers=headers
    )
    
    if response.status_code == 200:
        scenarios = response.json()
        print(f"✓ Found {len(scenarios)} scenarios:")
        for scenario in scenarios:
            print(f"  - {scenario.get('name')} (Base: {scenario.get('is_base', False)})")
        return scenarios
    else:
        print(f"✗ Failed to list scenarios: {response.status_code}")
        print(response.text)
        return []

def test_scenario_comparison(token, project_id, scenario_ids):
    """Test comparing scenarios"""
    if len(scenario_ids) < 2:
        print("\n⚠ Need at least 2 scenarios to compare")
        return
    
    print(f"\nTesting scenario comparison...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    comparison_data = {
        "scenario_ids": scenario_ids[:2],  # Compare first 2 scenarios
        "name": "Test Comparison"
    }
    
    response = requests.post(
        f"{BASE_URL}/projects/{project_id}/compare",
        headers=headers,
        json=comparison_data
    )
    
    if response.status_code == 200:
        comparison = response.json()
        print("✓ Scenario comparison successful:")
        print(f"  Best Overall: {comparison.get('best_overall_scenario')}")
        print(f"  Lowest Cost: {comparison.get('lowest_cost_scenario')}")
        print(f"  Best ROI: {comparison.get('best_roi_scenario')}")
        return True
    else:
        print(f"✗ Scenario comparison failed: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("Testing Scenario API Endpoints")
    print("=" * 50)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Get projects
    projects = get_projects(token)
    if not projects:
        print("\n❌ No projects found. Please create a project first.")
        return
    
    # Use the first project for testing
    project = projects[0]
    project_id = project.get("project_id")
    print(f"\nUsing project: {project.get('name')} (ID: {project_id})")
    
    # Test scenario calculation
    test_scenario_calculation(token, project_id)
    
    # Test scenario creation
    scenario_id = test_scenario_creation(token, project_id)
    
    # Test scenario list
    scenarios = test_scenario_list(token, project_id)
    
    # Test scenario comparison if we have scenarios
    if scenarios:
        scenario_ids = [s.get('id') for s in scenarios if s.get('id')]
        test_scenario_comparison(token, project_id, scenario_ids)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()