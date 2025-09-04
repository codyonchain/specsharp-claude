# Config Architecture Verification Report

## Critical Discovery: DUAL CONFIG SYSTEM! ⚠️

### Two Separate Config Systems Found:

1. **OLD CONFIG** (`app/services/building_types_config.py`)
   - Used by: `clean_engine_v2.py` ✅
   - Status: ACTIVE IN PRODUCTION
   - Healthcare subtypes: 4 (hospital, medical_office, urgent_care, surgery_center)

2. **NEW CONFIG** (`app/v2/config/master_config.py`)
   - Used by: Unknown/V2 system
   - Status: Appears unused by main engine
   - Healthcare subtypes: 1 (hospital only)
   - Uses dataclasses and more sophisticated structure

## Current Active Config Format (OLD - What's Actually Used)

```python
# app/services/building_types_config.py
BUILDING_TYPES_CONFIG = {
    'healthcare': {
        'display_name': 'Healthcare Facilities',
        'subtypes': {
            'hospital': {
                'name': 'Hospital',
                'base_cost': 950,        # Simple number
                'equipment_cost': 200,    # Already supported!
                'typical_floors': 5,
                'keywords': [...]
            },
            'medical_office': {...},
            'urgent_care': {...},
            'surgery_center': {...}
        }
    }
}
```

## New V2 Config Format (NOT Currently Used by Engine)

```python
# app/v2/config/master_config.py
BuildingType.HEALTHCARE: {
    'hospital': BuildingConfig(
        display_name='Hospital',
        base_cost_per_sf=1150,          # Different value!
        cost_range=(1050, 1250),
        equipment_cost_per_sf=200,      # Same field, different name
        typical_floors=5,
        trades=TradeBreakdown(...),     # More sophisticated
        soft_costs=SoftCosts(...),
        ownership_types={...},
        nlp=NLPConfig(...),
    )
}
```

## Key Findings

### ✅ Good News
1. **Equipment costs already supported** in OLD config
2. **Healthcare subtypes already exist** (4 types in old, need to add 6 more)
3. **clean_engine_v2 already reads equipment_cost** field
4. **No frontend changes needed** - equipment already handled

### ⚠️ Concerns
1. **Two different config systems** - which is source of truth?
2. **Different cost values** - Old: $950/SF hospital, New: $1150/SF hospital
3. **Field name differences** - `equipment_cost` vs `equipment_cost_per_sf`
4. **V2 config more sophisticated** but not used by production engine

## Safe Migration Paths

### Option A: Update OLD Config (RECOMMENDED - Immediate Fix)
```python
# Add to app/services/building_types_config.py
'healthcare': {
    'subtypes': {
        # Add missing 6 subtypes here
        'imaging_center': {
            'name': 'Imaging Center',
            'base_cost': 500,         # From healthcare_cost_service
            'equipment_cost': 300,    # From healthcare_cost_service
            'typical_floors': 1
        },
        'dental_office': {...},
        'rehabilitation': {...},
        'nursing_home': {...},
        # etc.
    }
}
```
**Pros**: Works immediately, no code changes needed
**Cons**: Maintains dual config system

### Option B: Migrate Engine to V2 Config (Long-term Solution)
1. Update master_config.py with all 10 healthcare subtypes
2. Modify clean_engine_v2 to use master_config instead of building_types_config
3. Deprecate old config system

**Pros**: Single source of truth, more sophisticated
**Cons**: Requires engine code changes, testing

### Option C: Hybrid Approach (Safest)
1. First: Add subtypes to OLD config (immediate fix)
2. Then: Plan migration to V2 config system
3. Finally: Deprecate old config after validation

## Special Features Support

### Current Support in OLD Config
```python
FEATURE_COSTS = {
    'healthcare': {
        'emergency_department': 50,   # Already there!
        'operating_rooms': 75,
        'medical_imaging': 45,
        'laboratory': 30,
        'icu': 65
    }
}
```

## Recommended Immediate Actions

### 1. Add Missing Subtypes to OLD Config
```python
# Add to building_types_config.py
'imaging_center': {
    'name': 'Diagnostic Imaging Center',
    'base_cost': 500,
    'equipment_cost': 300,
    'typical_floors': 1,
    'keywords': ['imaging', 'mri', 'ct scan', 'radiology']
},
'dental_office': {
    'name': 'Dental Office',
    'base_cost': 300,
    'equipment_cost': 30,
    'typical_floors': 1,
    'keywords': ['dental', 'dentist', 'orthodontic']
},
'rehabilitation': {
    'name': 'Rehabilitation Center',
    'base_cost': 325,
    'equipment_cost': 100,
    'typical_floors': 2,
    'keywords': ['rehab', 'rehabilitation', 'physical therapy']
},
'nursing_home': {
    'name': 'Senior Care Facility',
    'base_cost': 275,
    'equipment_cost': 10,
    'typical_floors': 2,
    'keywords': ['nursing home', 'assisted living', 'senior care']
},
'outpatient_clinic': {
    'name': 'Outpatient Clinic',
    'base_cost': 380,
    'equipment_cost': 50,
    'typical_floors': 1,
    'keywords': ['clinic', 'outpatient', 'ambulatory']
},
'medical_center': {
    'name': 'Medical Center',
    'base_cost': 750,
    'equipment_cost': 150,
    'typical_floors': 4,
    'keywords': ['medical center', 'health center']
}
```

### 2. No Engine Changes Needed!
- clean_engine_v2 already reads equipment_cost
- Already handles subtypes
- Already applies feature costs

### 3. Test Immediately
```python
# Should work with no code changes:
calculate_scope({
    'building_type': 'healthcare',
    'building_subtype': 'imaging_center',  # New subtype
    'square_footage': 10000,
    'location': 'Nashville'
})
```

## Conclusion

The system is **MORE READY** than expected:
- ✅ Equipment costs already supported
- ✅ Subtypes already working
- ✅ Special features already implemented
- ⚠️ Just need to add 6 missing subtypes to OLD config
- ⚠️ Need to resolve dual config system eventually

**Immediate win**: Add subtypes to `building_types_config.py` and sophisticated healthcare works TODAY!

---
*Report generated: December 2024*