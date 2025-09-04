# Engine Consolidation Status Report

## ✅ Successfully Consolidated

### Primary Calculation Engine: clean_engine_v2.py
- **Status**: ACTIVE and WORKING
- **Used by**: 
  - `/api/v1/scope/generate` - Main endpoint ✅
  - `/api/v1/comparison/*` - Comparison service (fixed) ✅
  - `/api/v1/demo/*` - Demo endpoints (fixed) ✅

### Updates Made:
1. **comparison_service.py** - Updated to use clean_engine_v2 with adapter for categories
2. **demo.py** - Updated to use clean_engine_v2

## ⚠️ Engines That MUST BE KEPT

### 1. unified_engine.py (V2 API)
- **Location**: `app/v2/engines/unified_engine.py`
- **Status**: ACTIVELY USED
- **Used by**:
  - `/api/v2/*` endpoints (registered in main.py)
  - `scenario_service.py`
- **Decision**: DO NOT REMOVE - V2 API depends on it

### 2. cost_engine.py (Utility Functions)
- **Location**: `app/core/cost_engine.py`
- **Status**: Contains utility functions
- **Used by**: Various services for trade calculations
- **Decision**: KEEP - Has useful utilities

## 🗑️ Safe to Remove

### 1. engine.py
- **Location**: `app/core/engine.py`
- **Status**: BROKEN (expects occupancy_type field that doesn't exist)
- **Used by**: Only engine_selector.py (which is also unused)
- **Decision**: SAFE TO REMOVE

### 2. engine_selector.py
- **Location**: `app/core/engine_selector.py`
- **Status**: NOT USED by any active endpoint
- **Decision**: SAFE TO REMOVE

### 3. clean_scope_engine.py
- **Location**: `app/core/clean_scope_engine.py`
- **Status**: Only used by engine_selector.py (unused)
- **Decision**: SAFE TO REMOVE

## Summary

### Keep These (4 engines):
1. **clean_engine_v2.py** - Primary calculation engine ✅
2. **unified_engine.py** - V2 API engine (active) ⚠️
3. **cost_engine.py** - Utility functions ⚠️
4. **owner_view_engine.py** - Specialized view engine ⚠️

### Remove These (3 engines):
1. **engine.py** - Broken and unused (~1,748 lines)
2. **engine_selector.py** - Unused router (~202 lines)
3. **clean_scope_engine.py** - Unused alternative (~933 lines)

**Total lines to remove**: ~2,883 lines

## Final Removal Commands

```bash
# These are SAFE to remove:
rm app/core/engine.py
rm app/core/engine_selector.py
rm app/core/clean_scope_engine.py

# Already backed up to:
# deprecated_engines/engine.py.backup
# deprecated_engines/engine_selector.py.backup
# deprecated_engines/clean_scope_engine.py.backup
```

## Testing Verification

All tests passing:
- ✅ clean_engine_v2 works: $350.00/SF
- ✅ Comparison service works (2 scenarios generated)
- ✅ No orphaned references to removable engines

## Rollback Plan

If any issues:
```bash
cp deprecated_engines/engine.py.backup app/core/engine.py
cp deprecated_engines/engine_selector.py.backup app/core/engine_selector.py
cp deprecated_engines/clean_scope_engine.py.backup app/core/clean_scope_engine.py
```