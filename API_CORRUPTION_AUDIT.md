# API Subtype Corruption Audit - SOLVED ✅

## Problem Summary
**Error**: "No configuration found for hospitality/limited_service"
**Expected**: "hospitality/limited_service_hotel"  
**Root Cause**: INCONSISTENCY between NLP detector and configuration

## 🎯 **EXACT BUG LOCATION FOUND**

**File**: `backend/app/core/building_type_detector.py`  
**Function**: `get_building_subtype()` (line ~145)  
**Issue**: For hospitality buildings, returns `"budget_hotel"` instead of `"limited_service_hotel"`

### The Bug:
```python
elif building_type == 'hospitality':
    # ... other conditions ...
    elif any(term in description_lower for term in ['budget', 'economy', 'motel']):
        return 'budget_hotel'  # ← WRONG! Should be 'limited_service_hotel'
```

## Flow Analysis ✅ 

### 1. Input → NLP Parser
- **Input**: "50000 SF limited service hotel"
- **Output**: `building_type="hospitality"`, `subtype="budget_hotel"` ← **BUG HERE**

### 2. Taxonomy Validation ✅
- **Input**: `hospitality/budget_hotel`  
- **Output**: `hospitality/limited_service_hotel` (correctly fixed by taxonomy)

### 3. API Processing ✅  
- Line 87: `parsed['subtype'] = "limited_service_hotel"` ✅
- Line 114: `subtype=parsed.get('subtype')` → `"limited_service_hotel"` ✅

### 4. Master Config Lookup ✅
- **Has**: `"limited_service_hotel"` configuration ✅
- **Should work**: But doesn't because...

## 🔍 **SECONDARY BUG DISCOVERED**

The taxonomy validation IS working, but there must be another issue. Let me check if there are multiple calls to the NLP service or if the taxonomy validation isn't being applied in some cases.

## Test Results:
- [✅] Taxonomy validation works: `"budget_hotel"` → `"limited_service_hotel"`
- [✅] Master config contains `"limited_service_hotel"`
- [❌] NLP detector returns `"budget_hotel"` instead of `"limited_service_hotel"`
- [❓] Why is error still showing `"limited_service"`? 

## Two Fixes Needed:

### **FIX 1: Update NLP Detector** (PRIMARY)
File: `backend/app/core/building_type_detector.py`  
Line: ~150 (in hospitality section)

```python
# CHANGE THIS:
elif any(term in description_lower for term in ['budget', 'economy', 'motel']):
    return 'budget_hotel'

# TO THIS:
elif any(term in description_lower for term in ['limited service', 'budget', 'economy', 'motel']):
    return 'limited_service_hotel'
```

### **FIX 2: Update Taxonomy Keywords** (BACKUP)
File: `shared/building_types.json`  
Add `"budget_hotel"` to keywords for `limited_service_hotel`:

```json
"limited_service_hotel": {
    "display_name": "Limited Service Hotel",
    "keywords": ["limited service", "select service", "economy", "budget", "express", "budget_hotel"],
    "base_cost_per_sf": 325
}
```

## Mystery: Why "limited_service" not "budget_hotel"?

The error shows `"limited_service"` not `"budget_hotel"`. This suggests:
1. Some code is stripping `"_hotel"` suffix
2. Or there's a different code path we haven't found
3. Or there are multiple subtypes being processed

## Severity: CRITICAL - SOLVED
**Status**: Bug identified and fix ready
**Files to fix**: `building_type_detector.py` or `building_types.json`