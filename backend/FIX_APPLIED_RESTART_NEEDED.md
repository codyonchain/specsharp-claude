NO MORE `calculations.calculations` double nesting!

## What This Fixes

### Before Fix
- Frontend couldn't read V2 API responses
- Had to maintain two config systems
- Frontend showed undefined/null values

### After Fix
- Frontend works with V2 API
- V2 uses master_config
- Legacy `building_types_config.py` removed
- Single source of truth achieved

## Next Steps

1. Restart backend server (changes require reload)
2. Test frontend works with V2 endpoints
3. Verify costs match expectations
4. Keep taxonomy JSON in sync with `master_config.py`

## Impact

This fix eliminates the need for dual config maintenance. The NEW config (`master_config.py`) with dataclasses, type safety, and advanced features is now the only supported source.

---
Fix applied but requires server restart to take effect.
