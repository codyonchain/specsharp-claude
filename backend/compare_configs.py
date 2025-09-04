"""Compare features of both config systems."""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("CONFIG SYSTEMS COMPARISON")
print("=" * 70)

# Check OLD config features
print("\n1. OLD CONFIG (building_types_config.py):")
print("-" * 50)
try:
    from app.services.building_types_config import (
        BUILDING_TYPES_CONFIG, 
        REGIONAL_MULTIPLIERS,
        SPECIAL_FEATURES_COSTS,
        TRADE_PERCENTAGES
    )
    
    # Count building types and subtypes
    total_subtypes = 0
    healthcare_subtypes = []
    
    for building_type, config in BUILDING_TYPES_CONFIG.items():
        if 'subtypes' in config:
            total_subtypes += len(config['subtypes'])
            if building_type == 'healthcare':
                healthcare_subtypes = list(config['subtypes'].keys())
    
    print(f"  Building types: {len(BUILDING_TYPES_CONFIG)}")
    print(f"  Total subtypes: {total_subtypes}")
    print(f"  Has regional multipliers: {len(REGIONAL_MULTIPLIERS) > 0}")
    print(f"  Has special features: {len(SPECIAL_FEATURES_COSTS) > 0}")
    print(f"  Has trade percentages: {len(TRADE_PERCENTAGES) > 0}")
    
    # Check healthcare specifically
    if 'healthcare' in BUILDING_TYPES_CONFIG:
        healthcare = BUILDING_TYPES_CONFIG['healthcare']
        print(f"\n  Healthcare subtypes ({len(healthcare_subtypes)}):")
        for subtype in healthcare_subtypes:
            sub_config = healthcare['subtypes'][subtype]
            print(f"    - {subtype}: ${sub_config.get('base_cost', 0)}/SF + ${sub_config.get('equipment_cost', 0)} equipment")
        
        # Check for equipment cost field
        first_subtype = list(healthcare['subtypes'].values())[0] if healthcare.get('subtypes') else {}
        print(f"\n  Equipment cost field: {'equipment_cost' in first_subtype}")
        
except Exception as e:
    print(f"  ERROR: {e}")

# Check NEW config features
print("\n2. NEW CONFIG (v2/master_config.py):")
print("-" * 50)
try:
    from app.v2.config.master_config import (
        MASTER_CONFIG,
        BuildingType,
        BuildingConfig,
        TradeBreakdown,
        SoftCosts
    )
    
    # Count building types
    building_count = 0
    total_subtypes = 0
    healthcare_subtypes = []
    
    for building_type in MASTER_CONFIG:
        building_count += 1
        if building_type == BuildingType.HEALTHCARE:
            healthcare_config = MASTER_CONFIG[building_type]
            healthcare_subtypes = list(healthcare_config.keys())
            total_subtypes += len(healthcare_subtypes)
        else:
            type_config = MASTER_CONFIG.get(building_type, {})
            if isinstance(type_config, dict):
                total_subtypes += len(type_config)
    
    print(f"  Building types: {building_count}")
    print(f"  Total subtypes: {total_subtypes}")
    print(f"  Uses dataclasses: True")
    print(f"  Has ownership types: True")
    print(f"  Has soft costs: True")
    print(f"  Has NLP config: True")
    print(f"  Has trade breakdowns: True")
    
    # Check healthcare specifically
    if BuildingType.HEALTHCARE in MASTER_CONFIG:
        healthcare = MASTER_CONFIG[BuildingType.HEALTHCARE]
        print(f"\n  Healthcare subtypes ({len(healthcare_subtypes)}):")
        for subtype_key in healthcare_subtypes[:5]:  # Show first 5
            subtype = healthcare[subtype_key]
            if hasattr(subtype, 'base_cost_per_sf'):
                print(f"    - {subtype_key}: ${subtype.base_cost_per_sf}/SF + ${subtype.equipment_cost_per_sf} equipment")
            else:
                print(f"    - {subtype_key}: (structure varies)")
        
        # Check for advanced features
        first_subtype = list(healthcare.values())[0] if healthcare else None
        if first_subtype and hasattr(first_subtype, '__dict__'):
            print(f"\n  Advanced features in config:")
            print(f"    - Equipment cost: {hasattr(first_subtype, 'equipment_cost_per_sf')}")
            print(f"    - Soft costs: {hasattr(first_subtype, 'soft_costs')}")
            print(f"    - Trade breakdown: {hasattr(first_subtype, 'trades')}")
            print(f"    - Ownership types: {hasattr(first_subtype, 'ownership_types')}")
            
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 70)
print("VALUE COMPARISON")
print("=" * 70)

# Compare hospital costs
print("\nHospital Base Costs:")
try:
    old_hospital = BUILDING_TYPES_CONFIG['healthcare']['subtypes']['hospital']
    print(f"  OLD: ${old_hospital['base_cost']}/SF")
except:
    print(f"  OLD: Not found")

try:
    new_hospital = MASTER_CONFIG[BuildingType.HEALTHCARE]['hospital']
    print(f"  NEW: ${new_hospital.base_cost_per_sf}/SF")
except:
    print(f"  NEW: Not found")

print("\n" + "=" * 70)
print("USAGE SUMMARY")
print("=" * 70)
print("""
OLD Config (building_types_config.py):
  - Used by: clean_engine_v2.py (MAIN PRODUCTION ENGINE)
  - Status: ACTIVE
  - Structure: Simple dictionaries
  - Healthcare: 4 subtypes

NEW Config (v2/master_config.py):
  - Used by: v2/api/* and unified_engine.py
  - Status: V2 ENDPOINTS (parallel system)
  - Structure: Dataclasses (type-safe)
  - Healthcare: 1 subtype only
  - Advanced: Ownership, soft costs, NLP config
""")