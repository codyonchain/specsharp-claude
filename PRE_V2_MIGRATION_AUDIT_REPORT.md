# Pre-V2 Migration Comprehensive Audit Report

## Executive Summary

**Migration Readiness: ⚠️ NOT READY - Critical Issues Found**

### 🚨 Critical Blockers
1. **Database constraint error**: `project_type NOT NULL` causing inserts to fail
2. **Field mapping mismatches**: All 5 critical fields have naming discrepancies
3. **V2 project list endpoint**: Returns "Internal Server Error"

## Part 1: Frontend API Inventory ✅

### API Endpoints Called by Frontend
- `/api/v1/auth/me`
- `/api/v1/comparison/compare/{id}`
- `/api/v1/comparison/templates`
- `/api/v1/cost-dna/generate`
- `/api/v1/oauth/login/google`
- `/api/v1/subscription/create`
- `/api/v2/calculate`
- `/api/v2/compare`
- `/api/v2/export/comparison`
- `/api/v2/scope/owner-view`

### Components Making API Calls
- `ComparisonTool.tsx`
- `CostDNA/CostDNADisplay.tsx`
- `OAuthDebugger.tsx`
- `PaymentWall.tsx`
- `ProjectDetail.tsx`
- `ScenarioBuilder.tsx`

### Services Making API Calls
- `api.ts` (main service, configured for v2)
- `authService.ts`
- `scenarioApi.ts`

## Part 2: Frontend Data Access Patterns ✅

### Most Accessed Fields
- `project.building_type`
- `project.building_subtype`
- `project.categories` ❌ (not provided by V2)
- `project.description`
- `project.location`
- `project.square_footage`
- `project.subtotal`
- `project.total_cost`
- `project.request_data`

## Part 3: V2 Endpoint Completeness ✅

### V2 Endpoints Available
✅ `/api/v2/analyze` - Natural language analysis
✅ `/api/v2/calculate` - Detailed calculations
✅ `/api/v2/compare` - Scenario comparison
✅ `/api/v2/building-types` - List building types
✅ `/api/v2/building-details/{type}/{subtype}` - Building details
✅ `/api/v2/health` - Health check
✅ `/api/v2/scope/projects` - List projects
✅ `/api/v2/scope/projects/{id}` - Get/delete project
✅ `/api/v2/scope/generate` - Generate project
✅ `/api/v2/scope/owner-view` - Owner view

### Missing V1 Endpoints in V2
- ❌ `/api/v1/auth/*` endpoints
- ❌ `/api/v1/comparison/templates`
- ❌ `/api/v1/cost-dna/generate`
- ❌ `/api/v1/subscription/*` endpoints

## Part 4: V2 Response Format Issues ❌

### Test Results

#### `/api/v2/analyze` ✅
- **Status**: Working
- **Returns**: Proper structure with calculations and revenue data
- **Revenue**: ✅ $2.48M calculated for dental office

#### `/api/v2/scope/generate` ❌
- **Status**: FAILING
- **Error**: `NOT NULL constraint failed: projects.project_type`
- **Cause**: Missing required field in database insert

#### `/api/v2/scope/projects` ❌
- **Status**: FAILING  
- **Error**: "Internal Server Error"
- **Impact**: Cannot list projects

## Part 5: Database & Model Alignment ❌

### Database Schema Issues
| Field | Database | Model | Status |
|-------|----------|-------|--------|
| `project_type` | NOT NULL | nullable=True | ❌ MISMATCH |
| `project_classification` | NOT NULL | default='ground_up' | ⚠️ OK with default |
| `scope_data` | NOT NULL | nullable=False | ✅ OK |

### Data Storage
- Projects store calculation in `scope_data` as JSON (14KB)
- Also duplicated in `cost_data` (14KB)
- No `calculation_data` field exists

## Part 6: Field Mapping Matrix ❌

| Frontend Expects | V2 Returns | Database Has | Status |
|-----------------|------------|--------------|---------|
| `project_name` | `name` | `name` | ❌ MISMATCH |
| `construction_cost` | `subtotal` | `subtotal` | ❌ MISMATCH |
| `categories` | `trade_breakdown` | JSON in scope_data | ❌ MISMATCH |
| `totalCost` | `total_cost` | `total_cost` | ❌ MISMATCH |
| `costPerSqft` | `cost_per_sqft` | `cost_per_sqft` | ❌ MISMATCH |

## Part 7: Migration Risks 🔴

### High Risk Areas
1. **Hardcoded URLs**: 10+ files with hardcoded API paths
2. **Field name dependencies**: All major components expect different field names
3. **Database constraints**: Will break on NULL project_type
4. **Missing auth endpoints**: No V2 auth implementation

### Hardcoded Dependencies Found
- `config/api.ts`: `http://localhost:8001`
- `v2/api/client.ts`: Mixed V1/V2 references
- Multiple components with direct `/api/v1/` calls

## Part 8: Pre-Migration Checklist

### Database Ready ❌
- [ ] Fix `project_type` NOT NULL constraint
- [ ] Verify all existing projects valid
- [ ] Create backup

### V2 Endpoints Complete ⚠️
- [x] `/api/v2/scope/generate` - EXISTS but FAILING
- [x] `/api/v2/scope/projects` - EXISTS but ERROR  
- [x] `/api/v2/scope/projects/{id}` - EXISTS
- [x] `/api/v2/scope/owner-view` - EXISTS

### Frontend Ready ❌
- [ ] Fix field name mappings
- [ ] Update response transformations
- [ ] Handle V2 error formats

### Data Flow Verified ⚠️
- [x] NLP → unified_engine → database - WORKS
- [x] Revenue calculations present - WORKS
- [ ] Database insert - FAILING
- [ ] Project list retrieval - FAILING

## Critical Issues to Fix Before Migration

### Priority 1: Database Issues 🚨
```python
# In V2 scope.py generate_scope(), add:
project_type='commercial',  # MUST provide to avoid NOT NULL error
```

### Priority 2: Field Mapping 🚨
```python
# In format_project_response(), ensure ALL these mappings:
{
    'project_name': project.name,  # Add alias
    'projectName': project.name,   # Add camelCase
    'construction_cost': project.subtotal,  # Add alias
    'constructionCost': project.subtotal,   # Add camelCase
    'categories': convert_trade_breakdown_to_categories(trade_data),  # Convert format
}
```

### Priority 3: Fix Project List Endpoint 🚨
Debug why `/api/v2/scope/projects` returns Internal Server Error

### Priority 4: Auth Migration Path ⚠️
Plan for missing auth endpoints or keep V1 auth active

## Migration Readiness Score

| Component | Score | Status |
|-----------|-------|--------|
| Frontend API Calls | 8/10 | ✅ Mostly ready |
| V2 Endpoints | 6/10 | ⚠️ Critical failures |
| Database Schema | 3/10 | ❌ Blocking issues |
| Field Mapping | 2/10 | ❌ All mismatched |
| Overall | **4.75/10** | **❌ NOT READY** |

## Recommendation

**DO NOT PROCEED WITH V2 MIGRATION** until:
1. Fix database constraint issues
2. Resolve field mapping discrepancies
3. Debug failing endpoints
4. Add comprehensive error handling

## Next Steps

1. **Fix project_type constraint** - Add default value or make nullable
2. **Debug project list endpoint** - Check for user_id requirements
3. **Create field mapping layer** - Add all required aliases
4. **Test complete flow** - Ensure create → list → view → update works
5. **Plan auth migration** - Decide on V1/V2 auth strategy

---

*Audit completed: 2025-09-08*
*Next audit recommended after fixes: Before any production deployment*