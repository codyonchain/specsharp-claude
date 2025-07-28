#!/usr/bin/env python3
"""Test industrial building type detection"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.building_type_detector import determine_building_type, get_building_subtype

# Test descriptions
test_descriptions = [
    "Industrial manufacturing facility with heavy machinery",
    "Pharmaceutical manufacturing with clean rooms",
    "Food processing plant with refrigeration",
    "Data center with server rooms",
    "Warehouse for storage and distribution",
    "Office building with conference rooms",
]

print("=== Testing Building Type Detection ===\n")

for desc in test_descriptions:
    building_type = determine_building_type(desc)
    subtype = get_building_subtype(building_type, desc)
    print(f"Description: {desc}")
    print(f"Building Type: {building_type}")
    if subtype:
        print(f"Subtype: {subtype}")
    print("-" * 50)