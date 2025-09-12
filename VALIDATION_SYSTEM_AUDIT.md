# Validation System Audit Report

## Problem Summary
Error: "No configuration found for hospitality/limited_service"
- Expected: "hospitality/limited_service_hotel"
- Actual: "hospitality/limited_service" (missing "_hotel")

## Flow Analysis Completed ✓

### 1. Input → NLP Parser
- NLP returns building_type + subtype (need to test actual output)

### 2. Taxonomy Validation ✓
- Location: `backend/app/core/building_taxonomy.py`
- Function: `validate_building_type(building_type, subtype)`
- **CONFIRMED WORKING**: Correctly maps "limited_service" → "limited_service_hotel"
- **TEST RESULT**: Returns `('hospitality', 'limited_service_hotel')` ✓

### 3. API Endpoint Processing ✓
- Location: `backend/app/v2/api/scope.py` lines 81-87
- Calls `validate_building_type()` and stores result in `parsed['subtype']`
- **ISSUE**: Something between line 87 and 114 corrupts the subtype

### 4. Master Config Lookup ✓
- Location: `backend/app/v2/config/master_config.py`
- Function: `get_building_config(building_type, subtype)`
- **CONFIRMED**: Contains "limited_service_hotel" configuration ✓
- **TEST NEEDED**: Direct lookup with "limited_service" vs "limited_service_hotel"

### 5. Unified Engine ✓
- Location: `backend/app/v2/engines/unified_engine.py` line 76
- Throws error when `get_building_config()` returns None

## Root Cause Hypothesis

The subtype gets corrupted **between** API validation (line 87) and engine call (line 114).

**Suspect locations:**
1. Line 107: `BuildingType(parsed['building_type'])` - might modify parsed dict?
2. Line 114: `parsed.get('subtype')` - retrieval issue?
3. NLP service might be re-parsing or modifying the subtype

## Investigation Status

✅ **CONFIRMED WORKING**:
- Taxonomy validation correctly maps "limited_service" → "limited_service_hotel"
- Master config contains "limited_service_hotel" definition
- Unified engine properly throws error when config not found

❓ **NEEDS TESTING**:
- What does NLP service actually return for "50000 SF limited service hotel"?
- Does `BuildingType()` enum conversion affect the parsed dict?
- What's the exact value of `parsed.get('subtype')` at line 114?

## Next Steps

1. Test NLP service output directly
2. Add debug logging to trace exact subtype value at each step
3. Identify the exact line where "_hotel" gets stripped

## Severity: CRITICAL
This breaks all limited service hotel cost calculations.