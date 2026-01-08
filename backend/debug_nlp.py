#!/usr/bin/env python3
"""
Debug why educational keywords aren't matching
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.v2.config.master_config import MASTER_CONFIG, BuildingType
from app.v2.services.nlp_service import NLPService

# Test case
text = "Build a 75,000 SF elementary school for 500 students"
text_lower = text.lower()

print(f"Testing: {text}")
print("=" * 60)

# Check what keywords are configured for educational
if BuildingType.EDUCATIONAL in MASTER_CONFIG:
    for subtype, config in MASTER_CONFIG[BuildingType.EDUCATIONAL].items():
        print(f"\n{subtype} keywords: {config.nlp.keywords}")
        print(f"Priority: {config.nlp.priority}")
        
        # Check which keywords match
        matches = []
        for keyword in config.nlp.keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        if matches:
            print(f"✅ MATCHES: {matches}")
        else:
            print("❌ No matches")

# Check what keywords are configured for healthcare
print("\n" + "-" * 60)
if BuildingType.HEALTHCARE in MASTER_CONFIG:
    for subtype, config in MASTER_CONFIG[BuildingType.HEALTHCARE].items():
        print(f"\n{subtype} keywords: {config.nlp.keywords}")
        print(f"Priority: {config.nlp.priority}")
        
        # Check which keywords match
        matches = []
        for keyword in config.nlp.keywords:
            if keyword.lower() in text_lower:
                matches.append(keyword)
        
        if matches:
            print(f"✅ MATCHES: {matches}")
        else:
            print("❌ No matches")

# Now test the actual NLP service detection
print("\n" + "=" * 60)
print("Testing NLP Service _detect_building_type method:")
print("-" * 60)

nlp = NLPService()

# Get all detections with their scores
detections = []

for building_type in BuildingType:
    if building_type not in MASTER_CONFIG:
        continue
        
    for subtype, config in MASTER_CONFIG[building_type].items():
        # Count keyword matches
        matches = 0
        matched_keywords = []
        for keyword in config.nlp.keywords:
            if keyword.lower() in text_lower:
                matches += 1
                matched_keywords.append(keyword)
        
        if matches > 0:
            detections.append({
                'priority': config.nlp.priority,
                'matches': matches,
                'building_type': building_type,
                'subtype': subtype,
                'keywords': matched_keywords
            })

# Sort by priority (lower number = higher priority), then by match count
detections.sort(key=lambda x: (x['priority'], -x['matches']))

print("\nAll detections (sorted by priority):")
for i, d in enumerate(detections):
    print(f"{i+1}. {d['building_type'].value}/{d['subtype']}")
    print(f"   Priority: {d['priority']}, Matches: {d['matches']}")
    print(f"   Keywords: {d['keywords']}")

if detections:
    print(f"\n🎯 Winner: {detections[0]['building_type'].value}/{detections[0]['subtype']}")

# Call the actual method
result_type, result_subtype = nlp._detect_building_type(text_lower)
print(f"\n📊 Actual NLP result: {result_type.value if result_type else None}/{result_subtype}")