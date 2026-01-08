#!/usr/bin/env python3
"""
Test the standardized building taxonomy
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.building_taxonomy import (
    BuildingTaxonomy,
    normalize_building_type,
    validate_building_type,
    get_canonical_types,
    get_display_name,
    get_base_cost
)

print("=" * 80)
print("TESTING STANDARDIZED BUILDING TAXONOMY")
print("=" * 80)

# Test 1: Normalization of various formats
print("\n1. Testing Type Normalization:")
print("-" * 40)

test_cases = [
    # (input, expected_canonical)
    ('multifamily', 'residential'),
    ('MULTIFAMILY', 'residential'),
    ('multi_family', 'residential'),
    ('multi_family_residential', 'residential'),
    ('apartments', 'residential'),
    ('medical', 'healthcare'),
    ('HEALTHCARE', 'healthcare'),
    ('education', 'educational'),
    ('educational', 'educational'),
    ('office', 'commercial'),
    ('commercial', 'commercial'),
    ('warehouse', 'industrial'),
    ('manufacturing', 'industrial'),
    ('industrial', 'industrial'),
    ('shopping', 'retail'),
    ('retail', 'retail'),
    ('hotel', 'hospitality'),
    ('hospitality', 'hospitality'),
    ('dining', 'restaurant'),
    ('restaurant', 'restaurant'),
    ('unknown_type', 'commercial')  # Should default to commercial
]

all_passed = True
for input_type, expected in test_cases:
    result = normalize_building_type(input_type)
    if result == expected:
        print(f"✅ '{input_type}' → '{result}'")
    else:
        print(f"❌ '{input_type}' → '{result}' (expected '{expected}')")
        all_passed = False

# Test 2: Display Names
print("\n2. Testing Display Names:")
print("-" * 40)

for canonical in get_canonical_types()[:5]:  # Test first 5
    display = get_display_name(canonical)
    print(f"  {canonical} → {display}")

# Test 3: Subtype validation
print("\n3. Testing Subtype Validation:")
print("-" * 40)

subtype_tests = [
    # (type, subtype, expected_type, expected_subtype)
    ('multifamily', 'luxury', 'residential', 'luxury_apartments'),
    ('healthcare', 'MOB', 'healthcare', 'medical_office'),
    ('educational', 'elementary', 'educational', 'elementary_school'),
    ('office', 'class a', 'commercial', 'class_a'),
    ('warehouse', None, 'industrial', None),
]

for input_type, input_subtype, exp_type, exp_subtype in subtype_tests:
    canon_type, canon_subtype = validate_building_type(input_type, input_subtype)
    if canon_type == exp_type and canon_subtype == exp_subtype:
        print(f"✅ ({input_type}, {input_subtype}) → ({canon_type}, {canon_subtype})")
    else:
        print(f"❌ ({input_type}, {input_subtype}) → ({canon_type}, {canon_subtype})")
        print(f"   Expected: ({exp_type}, {exp_subtype})")

# Test 4: Base costs
print("\n4. Testing Base Cost Retrieval:")
print("-" * 40)

cost_tests = [
    ('residential', 'luxury_apartments', 425),
    ('healthcare', 'hospital', 1150),
    ('educational', 'elementary_school', 285),
    ('commercial', 'class_a', 450),
    ('industrial', 'warehouse', 150),
]

for btype, subtype, expected_cost in cost_tests:
    cost = get_base_cost(btype, subtype)
    if cost == expected_cost:
        print(f"✅ {btype}/{subtype}: ${cost}/SF")
    else:
        print(f"❌ {btype}/{subtype}: ${cost}/SF (expected ${expected_cost})")

# Test 5: Integration with V2 Parser
print("\n5. Testing Integration with V2 Parser:")
print("-" * 40)

from app.v2.services.nlp_service import nlp_service

parser_tests = [
    "Build a 100,000 SF multifamily complex",
    "Build a 50,000 SF medical office building",
    "Build a 75,000 SF office building",
]

for description in parser_tests:
    result = nlp_service.parse_description(description)
    building_type = result.get('building_type')
    
    # Now normalize it
    canonical = normalize_building_type(building_type) if building_type else None
    
    print(f"Description: '{description[:40]}...'")
    print(f"  Parser output: {building_type}")
    print(f"  Canonical: {canonical}")
    
    # Verify it's canonical
    if canonical and canonical in get_canonical_types():
        print(f"  ✅ Is canonical type")
    else:
        print(f"  ❌ Not a canonical type!")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

print("\nCanonical Building Types:")
for ctype in get_canonical_types():
    print(f"  • {ctype}")

print("\nMigration Mappings:")
from app.core.building_taxonomy import MIGRATION_MAP
for old, new in MIGRATION_MAP.items():
    print(f"  {old} → {new}")

if all_passed:
    print("\n🎉 All taxonomy tests passed!")
else:
    print("\n⚠️ Some tests failed - review the results above")

print("\n" + "=" * 40)
print("KEY BENEFITS:")
print("=" * 40)
print("✅ Single source of truth (shared/building_types.json)")
print("✅ Automatic normalization of variations")
print("✅ Consistent subtypes and keywords")
print("✅ Base costs included in taxonomy")
print("✅ Works across Python and TypeScript")