#!/usr/bin/env python3
"""Test the simplified phrase-first parser"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.v2.services.phrase_parser import phrase_parser

print("=" * 80)
print("PHRASE-FIRST PARSER TEST")
print("=" * 80)

test_cases = [
    {
        'description': "Build a 75,000 SF elementary school for 500 students",
        'expected_type': 'educational',
        'expected_subtype': 'elementary_school',
        'expected_sf': 75000
    },
    {
        'description': "Build a 300,000 SF luxury apartment complex with 316 units",
        'expected_type': 'residential',
        'expected_subtype': 'luxury_apartments',
        'expected_sf': 300000
    },
    {
        'description': "Build a 200,000 SF hospital with emergency department in Nashville",
        'expected_type': 'healthcare',
        'expected_subtype': 'hospital',
        'expected_sf': 200000,
        'expected_location': 'Nashville'
    },
    {
        'description': "Build a 50,000 SF medical office building",
        'expected_type': 'healthcare',
        'expected_subtype': 'medical_office',
        'expected_sf': 50000
    },
    {
        'description': "Build a 95,000 SF class A office building in Memphis",
        'expected_type': 'commercial',
        'expected_subtype': 'class_a',
        'expected_sf': 95000,
        'expected_location': 'Memphis'
    },
    {
        'description': "Build a 150,000 SF distribution center with loading docks",
        'expected_type': 'industrial',
        'expected_subtype': 'warehouse',
        'expected_sf': 150000
    },
    {
        'description': "Build a 25,000 SF urgent care center",
        'expected_type': 'healthcare',
        'expected_subtype': 'urgent_care',
        'expected_sf': 25000
    },
    {
        'description': "Build a 40,000 SF middle school gymnasium",
        'expected_type': 'educational',
        'expected_subtype': 'middle_school',
        'expected_sf': 40000
    },
    {
        'description': "Build a 10,000 SF fine dining restaurant",
        'expected_type': 'restaurant',
        'expected_subtype': 'fine_dining',
        'expected_sf': 10000
    },
    {
        'description': "Renovate 30,000 SF office building to coworking space",
        'expected_type': 'commercial',
        'expected_subtype': 'coworking',
        'expected_sf': 30000,
        'expected_class': 'renovation'
    }
]

all_passed = True

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test['description'][:50]}...")
    print("-" * 60)
    
    result = phrase_parser.parse(test['description'])
    
    print(f"  Parsed:")
    print(f"    Type: {result['building_type']}")
    print(f"    Subtype: {result['subtype']}")
    print(f"    SF: {result['square_footage']:,}")
    print(f"    Location: {result['location']}")
    print(f"    Project Class: {result.get('project_class', 'ground_up')}")
    print(f"    Floors: {result['floors']}")
    
    # Check results
    passed = True
    
    if result['building_type'] != test['expected_type']:
        print(f"  ❌ Type mismatch: expected '{test['expected_type']}', got '{result['building_type']}'")
        passed = False
    else:
        print(f"  ✅ Type correct: {result['building_type']}")
    
    if result['subtype'] != test['expected_subtype']:
        print(f"  ❌ Subtype mismatch: expected '{test['expected_subtype']}', got '{result['subtype']}'")
        passed = False
    else:
        print(f"  ✅ Subtype correct: {result['subtype']}")
    
    if result['square_footage'] != test['expected_sf']:
        print(f"  ❌ SF mismatch: expected {test['expected_sf']:,}, got {result['square_footage']:,}")
        passed = False
    else:
        print(f"  ✅ Square footage correct: {result['square_footage']:,}")
    
    if 'expected_location' in test and result['location'] != test['expected_location']:
        print(f"  ❌ Location mismatch: expected '{test['expected_location']}', got '{result['location']}'")
        passed = False
    elif 'expected_location' in test:
        print(f"  ✅ Location correct: {result['location']}")
    
    if 'expected_class' in test and result.get('project_class') != test['expected_class']:
        print(f"  ❌ Class mismatch: expected '{test['expected_class']}', got '{result.get('project_class')}'")
        passed = False
    elif 'expected_class' in test:
        print(f"  ✅ Project class correct: {result.get('project_class')}")
    
    if not passed:
        all_passed = False

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if all_passed:
    print("🎉 ALL TESTS PASSED!")
    print("\nPhrase-first matching is working correctly:")
    print("• 'elementary school' correctly matches to educational/elementary_school")
    print("• 'luxury apartment' correctly matches to residential/luxury_apartments")
    print("• 'medical office building' correctly matches to healthcare/medical_office")
    print("• 'class A office' correctly matches to commercial/class_a")
    print("• 'distribution center' correctly matches to industrial/warehouse")
else:
    print("⚠️ Some tests failed - review results above")

print("\n" + "=" * 40)
print("BENEFITS OF PHRASE-FIRST PARSER:")
print("=" * 40)
print("✅ PREDICTABLE - Phrases always match before keywords")
print("✅ SIMPLE - No complex NLP or weighted priorities")
print("✅ MAINTAINABLE - Just add phrases to the mapping")
print("✅ TAXONOMY-ENFORCED - Always returns canonical types")
print("✅ TRANSPARENT - Easy to see why something matched")
print("✅ FAST - Simple dictionary lookups, no regex for matching")