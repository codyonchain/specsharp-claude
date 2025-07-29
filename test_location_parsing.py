#!/usr/bin/env python3
"""
Comprehensive test suite for location parsing in SpecSharp
Tests both demo and main app endpoints to ensure location parsing works correctly.

CRITICAL BUG FIXED: Portland was returning Louisiana due to substring matching "la" in "portland"
"""

import requests
import json
from typing import Dict, Any, Optional, Tuple
import sys
import os

# Add backend path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.nlp_service import nlp_service

# Test configuration
BACKEND_URL = "http://localhost:8001"
DEMO_ENDPOINT = f"{BACKEND_URL}/api/v1/demo/generate"
SCOPE_ENDPOINT = f"{BACKEND_URL}/api/v1/scope/generate"

# Test cases focused on realistic user inputs: (description, expected_state, expected_city)
TEST_CASES = [
    # CRITICAL BUG TEST - Portland should be Oregon, NOT Louisiana
    ("50000 sf retail center in Portland", "Oregon", "Portland"),  # Edge case that was broken
    
    # == MOST COMMON: City + State (comma separated) ==
    ("50000 sf office in Houston, Texas", "Texas", "Houston"),
    ("warehouse in Phoenix, Arizona", "Arizona", "Phoenix"),
    ("hospital in Los Angeles, California", "California", "Los Angeles"),
    ("retail in Miami, Florida", "Florida", "Miami"),
    ("office in Denver, Colorado", "Colorado", "Denver"),
    ("warehouse in Austin, Texas", "Texas", "Austin"),
    ("retail in Boston, Massachusetts", "Massachusetts", "Boston"),
    ("manufacturing in Detroit, Michigan", "Michigan", "Detroit"),
    ("data center in Atlanta, Georgia", "Georgia", "Atlanta"),
    ("office building in Seattle, Washington", "Washington", "Seattle"),
    
    # == VERY COMMON: City + State Abbreviation ==
    ("hospital in Phoenix, AZ", "Arizona", "Phoenix"),
    ("office in Denver, CO", "Colorado", "Denver"),  
    ("warehouse in Miami, FL", "Florida", "Miami"),
    ("retail in Austin, TX", "Texas", "Austin"),
    ("data center in Raleigh, NC", "North Carolina", "Raleigh"),
    ("office in Las Vegas, NV", "Nevada", "Las Vegas"),
    ("warehouse in Nashville, TN", "Tennessee", "Nashville"),
    ("manufacturing in Cleveland, OH", "Ohio", "Cleveland"),
    
    # == COMMON: State Only ==
    ("25000 sf office in Texas", "Texas", None),
    ("warehouse in California", "California", None),
    ("manufacturing facility in Texas", "Texas", None),
    ("data center in California", "California", None),
    ("30000 sf warehouse in Florida", "Florida", None),
    ("office building in New York", "New York", None),
    ("hospital in North Carolina", "North Carolina", None),
    ("retail center in Arizona", "Arizona", None),
    
    # == COMMON: State Abbreviations Only ==
    ("office in TX", "Texas", None),
    ("warehouse in CA", "California", None),
    ("retail in FL", "Florida", None),
    ("hospital in NY", "New York", None),
    ("manufacturing in IL", "Illinois", None),
    ("data center in NV", "Nevada", None),
    ("office in MA", "Massachusetts", None),
    ("warehouse in AZ", "Arizona", None),
    
    # == MAJOR UNAMBIGUOUS METROS ==
    ("office in Manhattan", None, "Manhattan"),     # Clear NYC reference
    ("warehouse in Chicago", None, "Chicago"),      # Unambiguous major city
    ("retail in Houston", None, "Houston"),         # Unambiguous major city  
    ("office in Dallas", None, "Dallas"),           # Unambiguous major city
    ("warehouse in Atlanta", None, "Atlanta"),      # Unambiguous major city
    ("data center in Seattle", None, "Seattle"),    # Unambiguous major city
    
    # == MULTI-WORD LOCATIONS ==
    ("office in New York, NY", "New York", "New York"),
    ("warehouse in Las Vegas, Nevada", "Nevada", "Las Vegas"),
    ("retail in Virginia Beach, VA", "Virginia", "Virginia Beach"),
    ("hospital in Colorado Springs, Colorado", "Colorado", "Colorado Springs"),
    ("office in New Hampshire", "New Hampshire", None),
    ("warehouse in North Carolina", "North Carolina", None),
    ("retail in South Dakota", "South Dakota", None),
    
    # == NO LOCATION (Graceful Handling) ==
    ("50000 sf hospital", None, None),
    ("warehouse 30000 sf with loading docks", None, None),
    ("office building with parking", None, None),
    ("retail center", None, None),
    
    # == COMPLEX DESCRIPTIONS (Real User Examples) ==
    ("2-story 50000 sf retail center with restaurant space in Houston, TX", "Texas", "Houston"),
    ("Mixed-use office (60%) warehouse (40%) 150000 sf in Denver, Colorado", "Colorado", "Denver"),
    ("Hospital complex 200000 sf with parking garage in Phoenix, Arizona", "Arizona", "Phoenix"),
    ("Multi-tenant office building 75000 sf in downtown Austin, TX", "Texas", "Austin"),
    ("Industrial warehouse with 30-foot ceilings in Miami, FL", "Florida", "Miami"),
]

def extract_location_from_nlp(description: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract location using the NLP service directly.
    Returns (state, city) tuple.
    """
    try:
        extracted = nlp_service.extract_project_details(description)
        location = extracted.get("location")
        
        if not location:
            return (None, None)
        
        if "," in location:
            # Format: "City, State"
            parts = location.split(",", 1)
            city = parts[0].strip()
            state = parts[1].strip()
            return (state, city)
        else:
            # Just state or just city
            # Check if it's a known state
            states = {
                'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
                'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
                'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
                'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
                'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
                'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
                'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
                'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
                'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
                'West Virginia', 'Wisconsin', 'Wyoming'
            }
            
            if location in states:
                return (location, None)
            else:
                return (None, location)
    
    except Exception as e:
        print(f"Error extracting location from '{description}': {e}")
        return (None, None)

def test_demo_endpoint(description: str) -> Dict[str, Any]:
    """Test the demo endpoint with a description."""
    try:
        response = requests.post(
            DEMO_ENDPOINT,
            json={"description": description},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Demo endpoint error {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        print(f"Demo endpoint exception: {e}")
        return {"error": str(e)}

def run_location_parsing_tests():
    """Run comprehensive location parsing tests."""
    print("=" * 80)
    print("SPECSHARP LOCATION PARSING TEST SUITE")
    print("=" * 80)
    print(f"Testing {len(TEST_CASES)} location parsing scenarios...")
    print()
    
    passed = 0
    failed = 0
    critical_bug_fixed = False
    
    for i, (description, expected_state, expected_city) in enumerate(TEST_CASES, 1):
        print(f"Test {i:2d}: {description}")
        
        # Test NLP service directly
        actual_state, actual_city = extract_location_from_nlp(description)
        
        # Check results
        state_ok = actual_state == expected_state
        city_ok = actual_city == expected_city
        
        if state_ok and city_ok:
            print(f"         ✅ PASS: {actual_city or 'None'}, {actual_state or 'None'}")
            passed += 1
            
            # Check if this is the critical bug test
            if "Portland" in description and actual_state == "Oregon":
                critical_bug_fixed = True
                print(f"         🎉 CRITICAL BUG FIXED: Portland now correctly returns Oregon!")
        else:
            print(f"         ❌ FAIL: Expected ({expected_city}, {expected_state})")
            print(f"                  Got      ({actual_city}, {actual_state})")
            failed += 1
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(TEST_CASES)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    print(f"Success Rate: {passed/len(TEST_CASES)*100:.1f}%")
    print()
    
    if critical_bug_fixed:
        print("🎉 CRITICAL BUG STATUS: FIXED ✅")
        print("   Portland now correctly returns Oregon, not Louisiana!")
    else:
        print("❌ CRITICAL BUG STATUS: NOT FIXED")
        print("   Portland is still not returning Oregon correctly!")
    
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Location parsing is working correctly.")
        return True
    else:
        print(f"⚠️  {failed} TESTS FAILED. Location parsing needs more work.")
        return False

def test_demo_endpoint_integration():
    """Test the actual demo endpoint to ensure it works end-to-end."""
    print("=" * 80)
    print("DEMO ENDPOINT INTEGRATION TEST")
    print("=" * 80)
    
    critical_test = "50000 sf retail center in Portland"
    print(f"Testing critical case: {critical_test}")
    
    result = test_demo_endpoint(critical_test)
    
    if "error" in result:
        print(f"❌ Demo endpoint failed: {result['error']}")
        return False
    
    location = result.get("location", "Unknown")
    print(f"Demo endpoint returned location: {location}")
    
    if "Oregon" in location and "Portland" in location:
        print("🎉 DEMO ENDPOINT WORKING: Portland correctly shows Oregon!")
        return True
    elif "Louisiana" in location:
        print("❌ DEMO ENDPOINT BROKEN: Portland still shows Louisiana!")
        return False
    else:
        print(f"⚠️  DEMO ENDPOINT UNCLEAR: Got '{location}' for Portland")
        return False

if __name__ == "__main__":
    print("Starting SpecSharp Location Parsing Tests...")
    print()
    
    # Test 1: NLP Service Direct Tests
    nlp_success = run_location_parsing_tests()
    
    # Test 2: Demo Endpoint Integration Test
    demo_success = test_demo_endpoint_integration()
    
    # Final result
    print("=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if nlp_success and demo_success:
        print("🎉 ALL TESTS PASSED! Location parsing bug is FIXED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED. Location parsing needs more work.")
        if not nlp_success:
            print("   - NLP service location parsing has issues")
        if not demo_success:
            print("   - Demo endpoint integration has issues")
        sys.exit(1)