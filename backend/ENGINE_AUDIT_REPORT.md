# SpecSharp Engine Audit Report
## Multiple Calculation Engines Analysis

### Executive Summary
SpecSharp has **7 different calculation engines** competing and potentially returning different results. The primary endpoint (`/api/v1/scope`) uses `clean_engine_v2.py`, which is a standalone engine that doesn't depend on other engines.

### Engines Discovered

#### 1. **clean_engine_v2.py** (ACTIVELY USED) ✅
- **Location**: `backend/app/services/clean_engine_v2.py`
- **Size**: 553 lines
- **Last Modified**: Aug 18, 2024
- **Used By**: `/api/v1/scope/generate` endpoint (PRIMARY)
- **Dependencies**: Config files only, no other engines
- **Purpose**: Pure calculation engine with clean architecture

#### 2. **engine.py** (PARTIALLY USED) ⚠️
- **Location**: `backend/app/core/engine.py`
- **Size**: 1,748 lines
- **Last Modified**: Aug 29, 2024
- **Used By**: 
  - `comparison_service.py`
  - `demo.py` endpoint
  - `engine_selector.py` (as fallback "old engine")
- **Dependencies**: Uses `cost_engine.py` functions
- **Purpose**: Original comprehensive engine, most complex

#### 3. **unified_engine.py** (V2 ENDPOINT - UNUSED?) ❌
- **Location**: `backend/app/v2/engines/unified_engine.py`
- **Size**: 507 lines
- **Last Modified**: Sep 4, 2024
- **Used By**: V2 API endpoints (scope, comparison)
- **Purpose**: V2 architecture attempt

#### 4. **cost_engine.py** (UTILITY FUNCTIONS) 🔧
- **Location**: `backend/app/core/cost_engine.py`
- **Size**: 2,238 lines
- **Last Modified**: Jul 28, 2024
- **Used By**: 
  - `engine.py` imports functions from here
  - `cost_service.py` imports from here
- **Purpose**: Trade calculation utilities, not a complete engine

#### 5. **clean_scope_engine.py** (ENGINE SELECTOR) 🔄
- **Location**: `backend/app/core/clean_scope_engine.py`
- **Size**: 933 lines
- **Last Modified**: Aug 18, 2024
- **Used By**: `engine_selector.py` only
- **Purpose**: Alternative clean architecture implementation

#### 6. **owner_view_engine.py** (SPECIALIZED) 📊
- **Location**: `backend/app/services/owner_view_engine.py`
- **Used By**: `/api/v1/scope` endpoint (for owner view)
- **Purpose**: Owner view presentation only

#### 7. **engine_selector.py** (ROUTER) 🔀
- **Location**: `backend/app/core/engine_selector.py`
- **Purpose**: Switches between engines based on SCOPE_ENGINE_MODE env var
- **Current Mode**: "old" (defaults to using `engine.py`)
- **Not Actually Used**: No endpoint imports this

### Execution Flow Analysis

```
User Request → /api/v1/scope/generate
    ↓
scope.py endpoint
    ↓
clean_engine_v2.calculate_scope()  ← MAIN CALCULATION
    ↓
Returns calculated result
```

### The Problem

1. **Multiple Truth Sources**: 
   - `clean_engine_v2` is used by main endpoint
   - `engine.py` is used by comparison service
   - Different engines = different results

2. **Unused Code**:
   - `engine_selector.py` exists but isn't used
   - V2 unified_engine exists but V2 API not in main.py
   - `clean_scope_engine.py` only used by unused selector

3. **Confusion**:
   - 5,979 lines of engine code total
   - Only ~553 lines actually used
   - Multiple implementations of same logic

### Recommendation: Keep clean_engine_v2.py

**Reasons:**
1. **Currently Active**: Main `/api/v1/scope` endpoint uses it
2. **Clean Architecture**: No dependencies on other engines
3. **Config-Driven**: All values from config files
4. **Compact**: 553 lines vs 1,748 lines (engine.py)
5. **Recent**: Actively maintained (Aug 2024)

### Action Plan

#### Phase 1: Consolidate to clean_engine_v2
1. ✅ Identify that clean_engine_v2 is the active engine
2. 🔄 Update comparison_service to use clean_engine_v2
3. 🔄 Update demo endpoint to use clean_engine_v2
4. 🔄 Remove engine_selector (not used)

#### Phase 2: Remove Unused Engines
1. Remove `backend/app/core/engine.py` (after updating dependencies)
2. Remove `backend/app/core/engine_selector.py`
3. Remove `backend/app/core/clean_scope_engine.py`
4. Remove `backend/app/v2/engines/unified_engine.py`
5. Keep `cost_engine.py` (has utility functions that might be needed)

#### Phase 3: Clean Up Imports
1. Update all imports to point to clean_engine_v2
2. Remove references to old engines
3. Update documentation

### Current State Check

```bash
# Primary endpoint uses:
/api/v1/scope → clean_engine_v2.py ✅

# Secondary uses:
comparison_service.py → engine.py (needs update)
demo.py → engine.py (needs update)

# Unused:
- engine_selector.py
- clean_scope_engine.py  
- unified_engine.py (V2 not registered)
```

### Risk Assessment
- **Low Risk**: clean_engine_v2 is already in production
- **Medium Risk**: Comparison service might show different results after consolidation
- **Mitigation**: Test comparison service after update

### Next Steps
1. Update comparison_service.py to use clean_engine_v2
2. Update demo.py to use clean_engine_v2
3. Test all endpoints
4. Remove unused engines
5. Clean up imports