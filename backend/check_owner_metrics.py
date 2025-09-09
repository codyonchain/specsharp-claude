#!/usr/bin/env python3
"""Check owner_metrics_config structure"""

import sys
sys.path.append('backend')

print("=== OWNER_METRICS_CONFIG STRUCTURE ===")

try:
    from app.services.owner_metrics_config import OWNER_METRICS
    print("Found OWNER_METRICS in app.services:")
    for building_type in OWNER_METRICS.keys():
        print(f"  - {building_type}: {len(OWNER_METRICS[building_type])} subtypes")
        for subtype in list(OWNER_METRICS[building_type].keys())[:3]:
            print(f"    • {subtype}")
            # Show what data is available
            subtype_data = OWNER_METRICS[building_type][subtype]
            print(f"      Keys: {list(subtype_data.keys())}")
except ImportError as e:
    print(f"app.services.owner_metrics_config not found: {e}")

try:
    from app.config.owner_metrics_config import OWNER_METRICS
    print("\nFound OWNER_METRICS in app.config:")
    for building_type in OWNER_METRICS.keys():
        print(f"  - {building_type}: {len(OWNER_METRICS[building_type])} subtypes")
        for subtype in list(OWNER_METRICS[building_type].keys())[:3]:
            print(f"    • {subtype}")
except ImportError as e:
    print(f"app.config.owner_metrics_config not found: {e}")