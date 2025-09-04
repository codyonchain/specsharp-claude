# SpecSharp Calculation Engine

## Current Architecture (as of 2025-09-04)

SpecSharp uses a single calculation engine for all cost estimations:

### Primary Engine
- **File**: `backend/app/services/clean_engine_v2.py`
- **Function**: `calculate_scope()`
- **Configuration**: Reads from `backend/app/configs/`
- **Used By**: All API endpoints

### Consolidation Status

#### ✅ Completed
1. **Updated comparison_service.py** - Now uses clean_engine_v2 instead of old engine.py
2. **Updated demo.py** - Now uses clean_engine_v2 instead of old engine.py
3. **Created backups** - All deprecated engines backed up to `backend/deprecated_engines/`
4. **Verified no orphaned references** - No remaining imports of old engines

#### ⚠️ Known Issues
1. **comparison_service.py** - Needs additional work to fully adapt to clean_engine_v2's response format
   - Categories structure differs slightly
   - Missing 'subtotal' field in category data
   - Workaround: Add proper field mapping

### Removed Engines
The following engines were deprecated and backed up:
- **engine.py** (1,748 lines) - Original complex engine
- **unified_engine.py** (507 lines) - Unused V2 attempt  
- **clean_scope_engine.py** (933 lines) - Alternative implementation
- **engine_selector.py** (202 lines) - Unused router

Total: **3,390 lines** of unused engine code identified

### API Endpoints
- `/api/v1/scope/generate` - Main calculation endpoint ✅
- `/api/v1/scope/compare` - Comparison service (partial update)
- `/api/demo/*` - Demo endpoints ✅

### Testing Results
```
✅ clean_engine_v2 works: $350.00/SF
✅ No remaining references to old engines found
⚠️  Comparison service needs response format fixes
```

### Next Steps
1. Fix comparison service to handle clean_engine_v2 response format
2. After verification period, remove deprecated engines:
   ```bash
   rm backend/app/core/engine.py
   rm backend/app/core/engine_selector.py
   rm backend/app/core/clean_scope_engine.py
   rm backend/app/v2/engines/unified_engine.py
   ```
3. Remove backup folder after confirming stability:
   ```bash
   rm -rf backend/deprecated_engines
   ```

### Rollback Plan
If issues arise:
```bash
# Restore from backup
cp backend/deprecated_engines/engine.py.backup backend/app/core/engine.py
cp backend/deprecated_engines/engine_selector.py.backup backend/app/core/engine_selector.py
cp backend/deprecated_engines/clean_scope_engine.py.backup backend/app/core/clean_scope_engine.py
cp backend/deprecated_engines/unified_engine.py.backup backend/app/v2/engines/unified_engine.py

# Revert import changes
git checkout -- backend/app/services/comparison_service.py
git checkout -- backend/app/api/endpoints/demo.py
```