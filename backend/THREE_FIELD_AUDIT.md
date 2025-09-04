# Three-Field Problem Audit Report

## Executive Summary
SpecSharp has three overlapping fields causing confusion and potential bugs:
- **building_type**: 489 occurrences (PRIMARY FIELD)
- **occupancy_type**: 99 occurrences (LEGACY, being phased out)
- **project_type**: 64 occurrences (CONFUSED USE)

## Field Usage Analysis

### 1. building_type (489 occurrences) ✅ PRIMARY
- **Status**: This is the PRIMARY field that should be used
- **Used by**: 
  - clean_engine_v2 (34 uses)
  - unified_engine (25 uses)
  - Frontend (36 files)
  - All calculation engines
- **Purpose**: Specific building category (restaurant, healthcare, office, etc.)

### 2. occupancy_type (99 occurrences) ⚠️ LEGACY
- **Status**: LEGACY field being phased out
- **Used by**:
  - 14 backend files (mostly services)
  - 10 frontend files
  - NOT used by calculation engines
- **Database comment**: "Same as building_type for consistency"
- **Problem**: Creates confusion and duplication

### 3. project_type (64 occurrences) ❌ CONFUSED
- **Status**: MISUSED - often confused with building_type
- **Used by**:
  - 14 backend files
  - 8 frontend files
  - NOT used by calculation engines
- **Problem**: Sometimes holds building type, sometimes holds project phase

## Key Findings

### Database Schema
The Project table has ALL THREE fields:
```python
project_type = Column(String)      # Line 56
building_type = Column(String)     # Line 58  
occupancy_type = Column(String)    # Line 59 - "Same as building_type for consistency"
```

### Model Layer (ScopeRequest)
- Only defines `building_type` and `building_subtype`
- Comments say: "ProjectType enum removed - we only use building_type string now"
- All three field names are ACCEPTED (defaults to "commercial" if not provided)

### Calculation Engines
- **clean_engine_v2**: Uses ONLY `building_type` (0 uses of others)
- **unified_engine**: Uses ONLY `building_type` (0 uses of others)
- **Conclusion**: Engines are correctly standardized on building_type

### Frontend
- Primarily uses `building_type` (36 files)
- Still has legacy `occupancy_type` (10 files)  
- Some `project_type` usage (8 files)

## Conversion/Mapping Found

### In scope.py endpoint:
```python
# Line 302, 313: Converting building_type to project_type
project_type=scope_request.building_type

# Line 424: NLP service copies building_type to occupancy_type
extracted["occupancy_type"] = extracted["building_type"]
```

### Database Storage:
When saving projects, multiple fields are populated with the same value for backward compatibility.

## Files Using Multiple Fields (High Risk)

These files use 2+ field types and are HIGH RISK for bugs:

1. **app/api/endpoints/scope.py**
   - occupancy_type: 4 uses
   - building_type: 56 uses
   - project_type: 11 uses

2. **app/services/nlp_service.py**
   - occupancy_type: 17 uses
   - building_type: 20 uses
   - project_type: 15 uses

3. **app/api/endpoints/demo.py**
   - occupancy_type: 6 uses
   - building_type: 11 uses

## Problems Identified

1. **Redundant Storage**: Database stores same value in 3 fields
2. **Confusion**: Developers unsure which field to use
3. **Conversion Overhead**: Code converts between fields
4. **Legacy Burden**: Old code expects occupancy_type
5. **Misuse**: project_type sometimes holds building type, sometimes project phase

## Recommendations

### Immediate Actions
1. **Standardize on building_type** - It's already the primary field
2. **Add deprecation warnings** for occupancy_type usage
3. **Clarify project_type** - Should it be project_classification instead?

### Migration Plan
1. **Phase 1**: Update frontend to use only building_type
2. **Phase 2**: Update backend services to stop using occupancy_type
3. **Phase 3**: Database migration to drop occupancy_type column
4. **Phase 4**: Rename/repurpose project_type to avoid confusion

### Code Changes Needed

#### High Priority Files to Fix:
1. `app/services/nlp_service.py` - Remove occupancy_type logic
2. `app/api/endpoints/scope.py` - Stop setting occupancy_type
3. Frontend components using occupancy_type (10 files)

#### Database Migration:
```sql
-- After code is updated
ALTER TABLE projects DROP COLUMN occupancy_type;
-- Consider renaming project_type to project_category or removing it
```

## Testing Results

When tested:
- ScopeRequest accepts all three field names (problematic flexibility)
- clean_engine_v2 requires building_type specifically
- Database stores all three fields
- Frontend sends mixed fields

## Conclusion

The three-field problem is real and causes:
- **Code complexity**: 99 uses of occupancy_type that duplicate building_type
- **Confusion**: Developers unsure which to use
- **Bugs**: Risk of checking wrong field
- **Maintenance burden**: Triple the fields to maintain

**Solution**: Standardize on `building_type` everywhere and remove the other two through phased migration.