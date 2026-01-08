#!/usr/bin/env python3
"""
Diagnostic tool to test the parser behavior
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.services.nlp_service import nlp_service

def test_parser():
    """Test the parser with various building descriptions"""
    
    test_cases = [
        "Build a 75,000 SF elementary school for 500 students",
        "Build a 300,000 SF luxury apartment complex with 316 units",
        "Build a 200,000 SF hospital with emergency department in Nashville",
        "Build a 95,000 SF office building in Memphis",
        "Build a 50,000 SF high school with gymnasium",
        "Build a 25,000 SF medical office building",
        "Build a 150,000 SF warehouse with 10 loading docks",
        "Build a 10,000 SF restaurant with full kitchen and bar"
    ]
    
    print("=" * 80)
    print("TESTING BUILDING TYPE DETECTION")
    print("=" * 80)
    
    for description in test_cases:
        print(f"\nInput: {description}")
        print("-" * 40)
        
        # Test building type detector
        building_type = determine_building_type(description)
        subtype = get_building_subtype(building_type, description)
        
        print(f"Building Type Detector:")
        print(f"  Type: {building_type}")
        print(f"  Subtype: {subtype}")
        
        # Test NLP service extraction
        extracted = nlp_service.extract_project_details(description)
        print(f"\nNLP Service Extraction:")
        print(f"  Building Type: {extracted.get('building_type', 'not detected')}")
        print(f"  Occupancy Type: {extracted.get('occupancy_type', 'not detected')}")
        print(f"  Healthcare?: {extracted.get('is_healthcare', False)}")
        print(f"  Location: {extracted.get('location', 'not detected')}")
        print(f"  Square Footage: {extracted.get('square_footage', 'not detected')}")
        
        # Show the expected vs actual
        expected_type = None
        if 'school' in description.lower():
            expected_type = 'educational'
        elif 'apartment' in description.lower():
            expected_type = 'multi_family_residential'
        elif 'hospital' in description.lower():
            expected_type = 'healthcare'
        elif 'office' in description.lower():
            expected_type = 'office'
        elif 'warehouse' in description.lower():
            expected_type = 'warehouse'
        elif 'restaurant' in description.lower():
            expected_type = 'restaurant'
        
        if expected_type and building_type != expected_type:
            print(f"\n❌ MISMATCH: Expected '{expected_type}', got '{building_type}'")
        else:
            print(f"\n✅ CORRECT: Type is '{building_type}'")

if __name__ == "__main__":
    test_parser()