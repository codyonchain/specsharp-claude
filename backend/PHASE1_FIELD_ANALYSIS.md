# Phase 1 Analysis: Three-Field Problem Deep Dive

## Executive Summary
After analyzing the high-priority files, the pattern is clear:
- **building_type** is the primary field (should be used everywhere)
- **occupancy_type** is redundant (always set to building_type value)
- **project_type** is misused (incorrectly stores building_type instead of project phase)

## File-by-File Analysis

### 1. nlp_service.py (17 occupancy_type uses)
- **Purpose**: Sets occupancy_type for backward compatibility
- **Key Finding**: Line 424 explicitly sets `occupancy_type = building_type`
- **Pattern**: Uses occupancy_type as intermediate variable, then copies to building_type
- **Can be safely replaced?**: YES - All uses can be replaced with building_type
- **Risk level**: LOW - Just variable renaming
- **Specific lines**:
  - Line 203: Hardcoded "healthcare" 
  - Line 424: `occupancy_type = building_type` (redundant copy)
  - Lines 499-507: Uses occupancy_type as variable name for building detection

### 2. scope.py (4 occupancy_type, 11 project_type uses)
- **Purpose of occupancy_type**: Only for database storage (backward compatibility)
- **Purpose of project_type**: MISUSED - stores building_type value!
- **Key Finding**: Line 345 shows `'project_type': scope_request.building_type`
- **Can be safely replaced?**: YES with migration
- **Risk level**: MEDIUM - Database has these columns
- **Specific issues**:
  - Line 63: Saves occupancy_type to DB (optional field)
  - Line 345: Incorrectly maps building_type → project_type
  - Lines 302, 313: Uses building_type as project_type value

### 3. demo.py (6 occupancy_type uses)
- **Purpose**: Uses occupancy_type as intermediate variable
- **Pattern**: Sets `occupancy_type = building_type` then uses it
- **Can be safely replaced?**: YES - Simple variable rename
- **Risk level**: LOW
- **Specific lines**:
  - Lines 86-88: Sets occupancy_type based on building_type
  - Line 113: Passes occupancy_type to ScopeRequest
  - Line 189: Maps occupancy_type back to building_type

## Data Flow Summary

### Current Flow:
```
1. Frontend sends → building_type (primary), sometimes occupancy_type
2. NLP extracts → building_type, copies to occupancy_type 
3. ScopeRequest model → expects building_type (no occupancy_type field)
4. Calculation engines → use ONLY building_type
5. Database saves → ALL THREE fields (for backward compatibility)
   - project_type = building_type (WRONG!)
   - occupancy_type = building_type (redundant)
   - building_type = building_type (correct)
```

### Problems Identified:
1. **project_type is storing the wrong data** - It stores building type instead of project phase
2. **occupancy_type is pure redundancy** - Always equals building_type
3. **Unnecessary conversions** - Code copies between fields for no reason

## Model Layer Analysis

### ScopeRequest (app/models/scope.py):
- **Only defines**: building_type and building_subtype
- **Comment says**: "Remove all legacy validators - we only use building_type now"
- **No occupancy_type field** in the model
- **No project_type field** in the model

### Database Model (app/db/models.py):
- Has all three columns for historical reasons
- Comment on occupancy_type: "Same as building_type for consistency"

## Safe Replacement Strategy

### Phase 1: Code Cleanup (Low Risk)
1. **nlp_service.py**: Replace all `occupancy_type` with `building_type`
   - Simple find/replace of variable names
   - Remove line 424 (redundant copy)
   
2. **demo.py**: Replace `occupancy_type` variable with `building_type`
   - Lines 86-88: Use building_type directly
   - Line 113: Pass building_type instead
   
3. **scope.py**: Stop setting occupancy_type and fix project_type
   - Remove occupancy_type from database saves
   - Fix line 345: Don't set project_type to building_type

### Phase 2: Database Migration (Medium Risk)
1. **Add migration** to copy existing data:
   ```sql
   -- Ensure consistency before dropping
   UPDATE projects SET building_type = occupancy_type 
   WHERE building_type IS NULL AND occupancy_type IS NOT NULL;
   ```

2. **Fix project_type data**:
   ```sql
   -- project_type should be about project phase, not building type
   -- Either fix the data or drop the column
   ALTER TABLE projects DROP COLUMN occupancy_type;
   ```

### Phase 3: Frontend Cleanup
- Update 10 files still sending occupancy_type
- Ensure all send building_type instead

## Immediate Actions

### Files to Fix First (Easy Wins):
1. **demo.py** - Just rename variables (6 lines)
2. **nlp_service.py** - Rename variables, remove redundant copy (17 lines)

### Files Needing Careful Changes:
1. **scope.py** - Update database field mapping (4 lines)
2. Database migration script needed

## Code Changes Required

### demo.py (BEFORE):
```python
if building_type == "restaurant":
    occupancy_type = "restaurant"
else:
    occupancy_type = building_type
```

### demo.py (AFTER):
```python
# Just use building_type directly, no need for occupancy_type
```

### nlp_service.py (BEFORE):
```python
extracted["occupancy_type"] = extracted["building_type"]
```

### nlp_service.py (AFTER):
```python
# Remove this line - no need to duplicate
```

### scope.py (BEFORE):
```python
'project_type': scope_request.building_type,  # WRONG!
'occupancy_type': project_data.get('occupancy_type'),
```

### scope.py (AFTER):
```python
# Don't set project_type to building_type
# Don't save occupancy_type anymore
```

## Risk Assessment

### Low Risk Changes:
- Variable renames in demo.py and nlp_service.py
- Removing redundant copies

### Medium Risk Changes:
- Database field changes (need migration)
- Frontend updates (10 files)

### High Risk Areas:
- None identified - all engines already use building_type

## Conclusion

The three-field problem is mainly about **redundancy and misuse**:
1. **occupancy_type** = always equals building_type (redundant)
2. **project_type** = incorrectly stores building_type (misused)
3. **building_type** = the correct field everything should use

Recommendation: Start with the easy wins (demo.py, nlp_service.py) then tackle database migration.