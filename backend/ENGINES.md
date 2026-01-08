# SpecSharp Calculation Engines

## Active Engines (DO NOT DELETE)

### 1. clean_engine_v2.py
- **Path**: `app/services/clean_engine_v2.py`
- **Purpose**: Primary calculation engine for V1 API
- **Used by**: 
  - `/api/v1/scope/generate`
  - `/api/v1/comparison/*`
  - `/api/v1/demo/*`
- **Status**: ✅ Production

### 2. unified_engine.py
- **Path**: `app/v2/engines/unified_engine.py`
- **Purpose**: V2 API calculation engine
- **Used by**: 
  - `/api/v2/analyze`
  - `/api/v2/calculate`
  - `scenario_service.py`
- **Status**: ✅ Production

### 3. owner_view_engine.py
- **Path**: `app/services/owner_view_engine.py`
- **Purpose**: Specialized calculations for owner view
- **Used by**: Owner view endpoints
- **Status**: ✅ Production

### 4. cost_engine.py
- **Path**: `app/core/cost_engine.py`
- **Purpose**: Utility functions for trade calculations
- **Used by**: Various services
- **Status**: ✅ Utility library

## Removed Engines (Cleanup completed 2025-09-04)
- ~~engine.py~~ - Was broken, used deprecated occupancy_type field (1,748 lines)
- ~~engine_selector.py~~ - Unused router mechanism (202 lines)
- ~~clean_scope_engine.py~~ - Alternative implementation never adopted (933 lines)

**Total removed**: 2,883 lines of dead code

## Architecture Notes
- V1 API uses clean_engine_v2
- V2 API uses unified_engine  
- Both are active and necessary
- Comparison service has been updated to use clean_engine_v2
- Future: Consider merging V1 and V2 into single unified API

## Testing Verification
All endpoints tested and working after cleanup:
- ✅ V1 scope generation
- ✅ V1 comparison service
- ✅ V2 analyze endpoint
- ✅ Demo endpoints