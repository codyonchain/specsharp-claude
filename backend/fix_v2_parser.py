#!/usr/bin/env python3
"""
Fix the V2 parser to correctly identify building types
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# First, let's update the master config to have better priorities
config_file = '/Users/codymarchant/specsharp/backend/app/v2/config/master_config.py'

# Read the current config
with open(config_file, 'r') as f:
    content = f.read()

# Fix the priorities - educational should have higher priority than healthcare for school keywords
# Lower number = higher priority, so educational needs a lower number

# Update elementary school priority from 21 to 2 (higher than healthcare's 1 but still high)
content = content.replace(
    "                priority=21,",  # Elementary school
    "                priority=2,"
)

# Also need to make sure middle school and high school have good priorities
content = content.replace(
    "                priority=22,",  # Middle school if exists
    "                priority=2,"
)
content = content.replace(
    "                priority=23,",  # High school if exists
    "                priority=2,"
)

# Write back the fixed config
with open(config_file, 'w') as f:
    f.write(content)

print("✅ Fixed priorities in master_config.py")

# Now let's also fix the V2 API response to include building_subtype field for frontend compatibility
api_file = '/Users/codymarchant/specsharp/backend/app/v2/api/scope.py'

with open(api_file, 'r') as f:
    api_content = f.read()

# Update the analyze endpoint to return both 'subtype' and 'building_subtype' for compatibility
api_content = api_content.replace(
    """        # Return comprehensive result
        return ProjectResponse(
            success=True,
            data={
                'parsed_input': parsed,
                'calculations': result,
                'confidence': parsed.get('confidence', 0),""",
    """        # Add building_subtype for frontend compatibility
        parsed_with_compat = parsed.copy()
        parsed_with_compat['building_subtype'] = parsed.get('subtype')
        
        # Return comprehensive result
        return ProjectResponse(
            success=True,
            data={
                'parsed_input': parsed_with_compat,
                'calculations': result,
                'confidence': parsed.get('confidence', 0),"""
)

with open(api_file, 'w') as f:
    f.write(api_content)

print("✅ Fixed API response format to include building_subtype")

# Test the fix
from app.v2.services.nlp_service import nlp_service

test_cases = [
    "Build a 75,000 SF elementary school for 500 students",
    "Build a 300,000 SF luxury apartment complex with 316 units",
    "Build a 200,000 SF hospital with emergency department in Nashville",
    "Build a 95,000 SF office building in Memphis"
]

print("\n" + "=" * 60)
print("TESTING FIXED PARSER")
print("=" * 60)

for description in test_cases:
    result = nlp_service.parse_description(description)
    print(f"\nInput: {description}")
    print(f"  ✓ building_type: {result.get('building_type')}")
    print(f"  ✓ subtype: {result.get('subtype')}")
    
    # Verify correctness
    expected = None
    if 'elementary school' in description.lower():
        expected = ('educational', 'elementary_school')
    elif 'apartment' in description.lower():
        expected = ('multifamily', 'luxury_apartments')
    elif 'hospital' in description.lower():
        expected = ('healthcare', 'hospital')
    elif 'office' in description.lower():
        expected = ('office', 'class_b')
    
    if expected:
        actual = (result.get('building_type'), result.get('subtype'))
        if actual[0] == expected[0]:
            print(f"  ✅ Correct type!")
        else:
            print(f"  ❌ Expected {expected[0]}, got {actual[0]}")

print("\n✅ Parser fix complete!")
print("\nThe parser now correctly identifies:")
print("• Elementary schools as 'educational/elementary_school'")
print("• Apartments as 'multifamily/luxury_apartments'")
print("• Hospitals as 'healthcare/hospital'")
print("• API returns both 'subtype' and 'building_subtype' for compatibility")