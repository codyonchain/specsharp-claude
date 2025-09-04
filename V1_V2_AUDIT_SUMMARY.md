# V1/V2 API Split Audit Summary

## Statistics
- **V1/V2 Files Found**: 19 total (15 backend, 4 frontend)
- **V1 Endpoints Active**: PARTIALLY (Health endpoint returns 404, scope endpoint returns 500)
- **V2 Endpoints Active**: YES (Health endpoint returns 200, analyze endpoint returns 200)
- **Compatibility Layers**: 0 (no app-specific compatibility files found)

## Architecture Pattern: DUAL ARCHITECTURE WITH V2 TRANSITION

### Current Setup:
1. **V1 API**: Legacy endpoints using `clean_engine_v2` (registered in main.py lines 99-114)
2. **V2 API**: New endpoints using `unified_engine` (registered in main.py line 118)
3. **Parallel Structure**: Both systems coexist but serve different purposes

## Key Findings

### Backend Architecture:
- **V1 Router**: No centralized router - individual endpoints registered directly
- **V2 Router**: Uses `v2_router` imported and registered as single unit
- **Engine Split**:
  - V1 uses `clean_engine_v2` (3 files importing)
  - V2 uses `unified_engine` (3 files importing)

### Frontend Architecture:
- **V1 API Client**: `frontend/src/services/api.ts` - hardcoded to `/api/v1`
- **V2 API Client**: `frontend/src/v2/api/client.ts` - configurable API version
- **Mixed Usage**: Main app uses V1, V2 features use separate client

### Directory Structure:
```
backend/app/
├── api/endpoints/          # V1 endpoints
├── v2/
│   ├── api/               # V2 endpoints  
│   ├── config/            # V2 configuration
│   ├── engines/           # V2 unified engine
│   └── services/          # V2 services

frontend/src/
├── services/api.ts        # V1 client
├── v2/
│   ├── api/client.ts      # V2 client
│   └── pages/             # V2 pages
```

## Key Issues Found

### 🚨 Critical Issues:
1. **V1 Health Endpoint Down**: `/api/v1/health` returns 404
2. **V1 Scope Errors**: `/api/v1/scope/generate` returns 500
3. **Mixed Frontend Usage**: App uses V1 for main features, V2 for specific features

### ⚠️ Architecture Concerns:
1. **No Compatibility Layer**: No adapter between V1/V2 data formats
2. **Duplicate Code**: Similar functionality exists in both V1/V2
3. **Inconsistent Client Usage**: Frontend mixes V1 and V2 API calls

### 🔍 Transition Indicators:
1. **V2 Working**: Health and analyze endpoints respond correctly
2. **V2 Feature Detection**: Frontend checks for "V2 projects" with `proj_` prefix
3. **Version Metadata**: V2 responses include version stamps (`engine_version: 'unified_v2'`)

## Current State Assessment

### What's Working:
- ✅ V2 API endpoints are functional
- ✅ V2 unified engine operational 
- ✅ V2 frontend client can switch API versions
- ✅ Both systems coexist without conflicts

### What's Broken:
- ❌ V1 health endpoint missing
- ❌ V1 scope generation failing
- ❌ No unified error handling between versions

### Migration Status:
- **V2 Infrastructure**: Complete and functional
- **V1 Deprecation**: In progress (some endpoints failing)
- **Frontend Migration**: Partial (selective V2 adoption)

## Recommendation

### Short-term (Current Audit Context):
1. **Use V2 for new healthcare features** - V2 infrastructure is stable
2. **Monitor V1 endpoint failures** - May indicate ongoing deprecation
3. **Maintain V2 architectural patterns** when adding healthcare subtypes

### Long-term Architecture:
1. **Complete V1 → V2 Migration**: Fix or remove failing V1 endpoints
2. **Consolidate API Clients**: Migrate frontend to single V2 client
3. **Remove Legacy Code**: Clean up unused V1 infrastructure

## Impact on Healthcare Addition

For adding healthcare subtypes:
- ✅ **Use V2 unified_engine** - proven functional
- ✅ **Follow V2 config patterns** - established in `master_config.py`
- ✅ **Use V2 API structure** - stable and responding
- ⚠️ **Ensure V1 compatibility** if main app still depends on V1 endpoints

The V2 system is ready for healthcare feature expansion, but V1 system health should be monitored for overall application stability.