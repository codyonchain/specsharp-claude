#!/usr/bin/env python
"""Test building type detection priority order"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.services.nlp_service import nlp_service

def test_building_type_priority():
    """Test that building types are detected in the correct priority order"""
    print("Testing Building Type Detection Priority:")
    print("-" * 50)
    
    test_cases = [
        # Healthcare should win over generic terms
        ("Medical office building", "healthcare"),
        ("Hospital cafeteria renovation", "healthcare"),  # Hospital wins over cafeteria
        ("University hospital", "healthcare"),  # Hospital wins over university
        ("Retail pharmacy", "healthcare"),  # Pharmacy wins over retail
        
        # Educational should win after healthcare
        ("School cafeteria", "educational"),  # School wins over cafeteria
        ("Elementary school kitchen renovation", "educational"),  # School wins over kitchen
        
        # Restaurant should be detected properly
        ("Restaurant with commercial kitchen", "restaurant"),
        ("Hotel restaurant", "restaurant"),  # Restaurant wins over hotel
        
        # Warehouse/Industrial
        ("Warehouse with office space", "warehouse"),
        ("Distribution center", "warehouse"),
        
        # Retail
        ("Retail store", "retail"),
        ("Shopping mall food court", "retail"),  # Mall wins over food court
        
        # Office
        ("Corporate office building", "office"),
        ("Office space", "office"),
        
        # Generic commercial only when nothing specific matches
        ("Commercial building", "commercial"),
        ("General purpose facility", "commercial"),
    ]
    
    for description, expected in test_cases:
        result = determine_building_type(description)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{description}' → {result} (expected {expected})")

def test_building_subtypes():
    """Test building subtype detection"""
    print("\n\nTesting Building Subtypes:")
    print("-" * 50)
    
    test_cases = [
        ("urgent care clinic", "healthcare", "urgent_care"),
        ("surgery center", "healthcare", "surgery_center"),
        ("rehabilitation hospital", "healthcare", "rehabilitation"),
        ("elementary school", "educational", "elementary_school"),
        ("university campus", "educational", "higher_education"),
        ("fast food restaurant", "restaurant", "quick_service"),
        ("fine dining establishment", "restaurant", "fine_dining"),
    ]
    
    for description, building_type, expected_subtype in test_cases:
        result = get_building_subtype(building_type, description)
        status = "✓" if result == expected_subtype else "✗"
        print(f"{status} '{description}' → {result} (expected {expected_subtype})")

def test_nlp_integration():
    """Test NLP service integration with new detection"""
    print("\n\nTesting NLP Service Integration:")
    print("-" * 50)
    
    test_descriptions = [
        "100,000 SF hospital with emergency department",
        "50,000 SF elementary school with gymnasium",
        "15,000 SF restaurant with commercial kitchen and bar",
        "200,000 SF warehouse distribution center",
        "25,000 SF retail shopping center",
    ]
    
    for description in test_descriptions:
        result = nlp_service._fallback_analysis(description)
        occupancy = result.get('occupancy_type', 'not detected')
        subtype = result.get('building_subtype', 'none')
        print(f"\n'{description}'")
        print(f"  → Occupancy: {occupancy}")
        if subtype and subtype != 'none':
            print(f"  → Subtype: {subtype}")

if __name__ == "__main__":
    test_building_type_priority()
    test_building_subtypes()
    test_nlp_integration()