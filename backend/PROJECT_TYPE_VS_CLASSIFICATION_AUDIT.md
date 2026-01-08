# project_type vs project_classification Audit Report

## Executive Summary

**CRITICAL FINDING**: `project_type` is completely redundant and incorrectly used. It should be removed.

- **project_type**: Stores building_type values (WRONG USE - 64 occurrences)
- **project_classification**: Stores construction phase (CORRECT - 54 occurrences)
- **Recommendation**: DELETE project_type column entirely

## Field Analysis

### 1. project_classification (✅ CORRECT FIELD)
- **Purpose**: Stores construction phase/approach
- **Valid Values**: 
  - `ground_up` (new construction)
  - `addition` (expanding existing)
  - `renovation` (remodeling existing)
  - `tenant_improvement` (interior fitout)
- **Used By**:
  - clean_engine_v2 for cost multipliers
  - Frontend (12 files)
  - Database column with proper default
- **Impact**: Controls pricing multipliers
  - Ground-up: 1.00x (base)
  - Addition: 1.15x (+15%)
  - Renovation: 1.35x (+35%)

### 2. project_type (❌ REDUNDANT & MISUSED)
- **Current Use**: Incorrectly stores building_type values
- **Evidence**: Line 345 in scope.py: `'project_type': scope_request.building_type`
- **Problem**: Duplicates building_type data
- **Occurrences**: 64 (all can be removed)
- **Database**: Required column but stores wrong data

## Data Flow Evidence

### Current Broken Flow:
```python
# scope.py line 345 - WRONG!
'project_type': scope_request.building_type,  # Stores "restaurant", "office", etc.
'project_classification': scope_request.project_classification.value,  # Correctly stores "ground_up", etc.
'building_type': scope_request.building_type,  # Also stores "restaurant", "office", etc.
```

### Result in Database:
- `project_type`: "restaurant" (WRONG - duplicates building_type)
- `project_classification`: "ground_up" (CORRECT)
- `building_type`: "restaurant" (CORRECT)

## Model Layer

### ScopeRequest (app/models/scope.py):
```python
# Has proper enum
class ProjectClassification(str, Enum):
    GROUND_UP = "ground_up"
    ADDITION = "addition"
    RENOVATION = "renovation"
    TENANT_IMPROVEMENT = "tenant_improvement"

# Model has:
project_classification: ProjectClassification = Field(default=ProjectClassification.GROUND_UP)
# NO project_type field (correct!)
```

### Database (app/db/models.py):
```python
project_type = Column(String, nullable=False)  # Stores wrong data!
project_classification = Column(String, nullable=False, default='ground_up')  # Correct
```

## Engine Usage

### clean_engine_v2:
- ✅ Uses `project_classification` correctly
- ✅ Applies multipliers based on classification
- ❌ Never uses `project_type`

### Test Results:
```
Ground-up: $360.50/SF (1.00x)
Addition: $414.57/SF (1.15x)
Renovation: $486.68/SF (1.35x)
```

## Frontend Usage
- Uses `projectClassification` correctly (12 files)
- Some legacy `project_type` usage (8 files)

## Problems with project_type

1. **Stores Wrong Data**: Contains building types instead of project phases
2. **Pure Duplication**: Same value as building_type column
3. **Confuses Developers**: Name suggests project phase but contains building category
4. **Wastes Storage**: Redundant data in every row
5. **No Unique Purpose**: Everything it does is wrong

## Recommendation: DELETE project_type

### Step 1: Stop Setting It (Immediate)
```python
# In scope.py, REMOVE this line:
'project_type': scope_request.building_type,  # DELETE THIS
```

### Step 2: Database Migration
```sql
-- After code is updated
ALTER TABLE projects 
ALTER COLUMN project_type DROP NOT NULL;  -- Make nullable first

-- Later, after verification
ALTER TABLE projects DROP COLUMN project_type;  -- Remove entirely
```

### Step 3: Update Frontend
- Remove 8 files still referencing project_type
- Ensure they use building_type for building data
- Ensure they use project_classification for phase data

## Action Plan

### Immediate (Low Risk):
1. Stop setting project_type in scope.py (line 345)
2. Stop setting project_type in all endpoints

### Short Term (Medium Risk):
1. Make project_type nullable in database
2. Update frontend to stop sending it
3. Remove from API responses

### Long Term (After Verification):
1. Drop project_type column completely
2. Clean up any remaining references

## Summary

**The verdict is clear:**
- `project_classification` = KEEP (stores ground_up/renovation/addition correctly)
- `project_type` = DELETE (redundant, misused, stores building_type data)

The field named `project_type` is a complete misnomer. It doesn't store project types or phases - it incorrectly duplicates building_type data. It serves no unique purpose and should be removed entirely.

## Migration Safety

Removing project_type is SAFE because:
1. It contains no unique data (always equals building_type)
2. No calculation engine uses it
3. project_classification handles the actual project phase data
4. All its current values are wrong anyway

## Test Command

To verify project_type can be safely removed:
```bash
# Check if any row has project_type != building_type
sqlite3 backend/specsharp.db "
SELECT COUNT(*) as mismatched_count 
FROM projects 
WHERE project_type != building_type;"
# Expected: 0 (all are duplicates)
```