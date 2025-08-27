#!/usr/bin/env python3
"""
Find all building type variations currently in use
"""

import os
import re
from pathlib import Path

print("=" * 80)
print("FINDING ALL BUILDING TYPE VARIATIONS")
print("=" * 80)

# Storage for found types
found_types = set()
type_locations = {}

# 1. Check V2 Master Config Enum
print("\n1. V2 Master Config Enum (BuildingType):")
print("-" * 40)

config_file = Path("/Users/codymarchant/specsharp/backend/app/v2/config/master_config.py")
if config_file.exists():
    with open(config_file) as f:
        content = f.read()
    
    # Find enum values
    enum_matches = re.findall(r'^\s*([A-Z_]+)\s*=\s*"([^"]+)"', content, re.MULTILINE)
    for enum_name, value in enum_matches:
        if 'BuildingType' in content[:content.find(enum_name)]:
            print(f"  {enum_name} = '{value}'")
            found_types.add(value)
            if value not in type_locations:
                type_locations[value] = []
            type_locations[value].append("V2 Config Enum")

# 2. Check V2 Parser outputs
print("\n2. V2 Parser Outputs:")
print("-" * 40)

parser_file = Path("/Users/codymarchant/specsharp/backend/app/v2/services/nlp_service.py")
if parser_file.exists():
    with open(parser_file) as f:
        content = f.read()
    
    # Find return statements with building types
    returns = re.findall(r"building_type['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]", content)
    for building_type in returns:
        if building_type not in ['None', 'null']:
            print(f"  Returns: '{building_type}'")
            found_types.add(building_type)
            if building_type not in type_locations:
                type_locations[building_type] = []
            type_locations[building_type].append("V2 Parser")

# 3. Check V1 building type detector
print("\n3. V1 Building Type Detector:")
print("-" * 40)

v1_detector = Path("/Users/codymarchant/specsharp/backend/app/core/building_type_detector.py")
if v1_detector.exists():
    with open(v1_detector) as f:
        content = f.read()
    
    # Find return statements
    returns = re.findall(r"return\s+['\"]([^'\"]+)['\"]", content)
    for building_type in returns:
        if building_type not in ['None', 'null', '']:
            print(f"  Returns: '{building_type}'")
            found_types.add(building_type)
            if building_type not in type_locations:
                type_locations[building_type] = []
            type_locations[building_type].append("V1 Detector")

# 4. Check Frontend TypeScript types
print("\n4. Frontend TypeScript Types:")
print("-" * 40)

frontend_types_file = Path("/Users/codymarchant/specsharp/frontend/src/v2/types/index.ts")
if frontend_types_file.exists():
    with open(frontend_types_file) as f:
        content = f.read()
    
    # Find enum values in TypeScript
    enum_matches = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
    for enum_name, value in enum_matches:
        if 'BuildingType' in content[:content.find(enum_name)] or value in found_types:
            print(f"  {enum_name} = '{value}'")
            found_types.add(value)
            if value not in type_locations:
                type_locations[value] = []
            type_locations[value].append("Frontend Types")

# 5. Search for hardcoded values
print("\n5. Hardcoded Values in Code:")
print("-" * 40)

# Common building type strings to search for
search_terms = [
    'multifamily', 'multi_family', 'multi_family_residential',
    'healthcare', 'medical',
    'educational', 'education', 
    'commercial', 'office',
    'industrial', 'warehouse', 'manufacturing',
    'retail', 'shopping',
    'hospitality', 'hotel',
    'restaurant',
    'residential', 'apartments'
]

backend_dir = Path("/Users/codymarchant/specsharp/backend")
for term in search_terms:
    # Search in Python files
    for py_file in backend_dir.rglob("*.py"):
        if '__pycache__' not in str(py_file):
            try:
                with open(py_file) as f:
                    if term in f.read().lower():
                        found_types.add(term)
                        if term not in type_locations:
                            type_locations[term] = []
                        if str(py_file).replace(str(backend_dir), '') not in type_locations[term]:
                            type_locations[term].append(str(py_file).replace(str(backend_dir), '').lstrip('/'))
            except:
                pass

# Summary
print("\n" + "=" * 80)
print("SUMMARY OF FOUND BUILDING TYPES")
print("=" * 80)

print(f"\nTotal unique types found: {len(found_types)}")
print("\nAll unique building types:")
for building_type in sorted(found_types):
    locations = type_locations.get(building_type, [])
    print(f"  • {building_type}")
    if locations and len(locations) <= 3:
        for loc in locations[:3]:
            print(f"      - {loc}")

# Identify conflicts
print("\n" + "=" * 40)
print("IDENTIFIED CONFLICTS:")
print("=" * 40)

conflicts = [
    ("multifamily", "multi_family", "multi_family_residential", "residential"),
    ("healthcare", "medical"),
    ("educational", "education"),
    ("commercial", "office"),
    ("industrial", "warehouse", "manufacturing")
]

for conflict_group in conflicts:
    found_in_group = [t for t in conflict_group if t in found_types]
    if len(found_in_group) > 1:
        print(f"\n❌ Conflict: {' vs '.join(found_in_group)}")
        print(f"   Should standardize to: '{conflict_group[0]}'")

print("\n" + "=" * 40)
print("RECOMMENDED CANONICAL TYPES:")
print("=" * 40)

canonical = [
    "residential",  # not multifamily
    "healthcare",   # not medical
    "educational",  # not education
    "commercial",   # not office
    "industrial",   # not warehouse/manufacturing
    "retail",
    "hospitality",
    "restaurant"
]

for ctype in canonical:
    print(f"  ✓ {ctype}")