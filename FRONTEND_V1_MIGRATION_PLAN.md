# Frontend V1 Usage Migration Plan

## V1 Dependencies Found

### Critical V1 API Usage: 13 total calls across 8 files

**Core API Client:**
- `frontend/src/services/api.ts` - **MAIN ISSUE**: Hardcoded to `/api/v1` 
  - Line 4: `? ${import.meta.env.VITE_API_URL}/api/v1`
  - Line 5: `: 'http://localhost:8001/api/v1'`
  - Used by **11 major components**

**Components Using V1 Client:**
1. `frontend/src/components/Dashboard.tsx` - **CRITICAL** (main app entry)
2. `frontend/src/components/ScopeGenerator.tsx` - **CRITICAL** (project creation)
3. `frontend/src/components/ProjectDetail.tsx` - **CRITICAL** (project view)
4. `frontend/src/components/ScenarioBuilder.tsx`
5. `frontend/src/components/SharedProjectView.tsx`
6. `frontend/src/components/OnboardingFlow.tsx`
7. `frontend/src/components/MarkupSettings.tsx`
8. `frontend/src/components/TeamSettings.tsx`
9. `frontend/src/components/TradePackageModal.tsx`
10. `frontend/src/pages/ComparisonPage.tsx`
11. `frontend/src/pages/DemoPage.tsx`

**Direct Hardcoded V1 Calls:**
- `ComparisonTool.tsx`: `http://localhost:8001/api/v1/comparison/compare/`
- `CostDNA/CostDNADisplay.tsx`: `/api/v1/cost-dna/generate`
- `ProjectDetail.tsx`: `http://localhost:8001/api/v1/scope/owner-view`
- `PaymentWall.tsx`: `http://localhost:8001/api/v1/subscription/create`
- `Login.tsx`: `/api/v1/oauth/login/google`

## Critical Components Using V1

### 🚨 **MISSION-CRITICAL COMPONENTS:**
1. **Dashboard** - Main app entry point, loads all projects
2. **ScopeGenerator** - Creates new projects (healthcare will use this)
3. **ProjectDetail** - Displays project results and costs

### ⚠️ **HIGH-IMPACT COMPONENTS:**
4. **ScenarioBuilder** - Project modifications
5. **ComparisonTool** - Project comparisons
6. **SharedProjectView** - Shared project access

## Backend V1 Endpoint Issues

### V1 Endpoint Status:
- **❌ /api/v1/health**: Returns 404 (no health endpoint registered)
- **❌ /api/v1/scope/generate**: Returns 500 (clean_engine_v2 import issues)
- **✅ V1 endpoints registered**: Lines 99-114 in main.py

### V1 Engine Dependencies:
- `backend/app/api/endpoints/scope.py` imports `clean_engine_v2`
- `clean_engine_v2` is imported by **4 services** including:
  - `nlp_service.py` (healthcare cost calculation)
  - `cost_service.py` (main cost calculations)
  - `cost_dna_service.py` (cost DNA generation)

## Healthcare-Related Issues

### ✅ **No Direct Frontend Healthcare Dependencies**
- No healthcare service imports found in frontend
- Healthcare calculations happen in backend services

### ⚠️ **Backend Healthcare Dependencies:**
- **3 services** import `healthcare_cost_service`:
  - `nlp_service.py` - Line: `healthcare_details = healthcare_cost_service.get_healthcare_cost(`
  - `cost_service.py` - Line: `healthcare_result = healthcare_cost_service.calculate_healthcare_costs_v2(`
  - `cost_dna_service.py` - Line: `healthcare_data = healthcare_cost_service.get_healthcare_cost(description)`

## Migration Strategy

### Phase 1: Fix V1 Backend Issues ⚠️ **REQUIRED FIRST**
Since V2 exists and works, but main frontend depends on V1:

1. **Fix V1 Health Endpoint**
   - Add health endpoint to any V1 router
   - Or remove health checks from frontend

2. **Fix V1 Scope Generation Errors**
   - Debug `clean_engine_v2` import issues
   - Ensure `healthcare_cost_service` is working
   - Or migrate scope generation to use V2

### Phase 2: Frontend Migration Options

#### Option A: Minimal Change (Recommended)
**Change only the base URL in api.ts:**
```typescript
// Line 4-5 in frontend/src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v2`  // Changed from v1
  : 'http://localhost:8001/api/v2';           // Changed from v1
```

**Requirements:**
- V2 must provide **all endpoints** that V1 currently provides
- V2 response formats must match V1 or frontend needs updates

#### Option B: Selective Migration  
**Keep V1 for storage, use V2 for calculations:**
- V1: `/api/v1/scope/projects` (CRUD operations)
- V2: `/api/v2/analyze`, `/api/v2/calculate` (calculations)

This matches the current V2 client design pattern.

#### Option C: Complete V2 Migration
**Migrate all components to use V2 client:**
- Replace all `from '../services/api'` with V2 client
- Update all components to use V2 response formats
- Most complex but cleanest long-term

## Immediate Action Plan

### 🚨 **PRIORITY 1: Keep App Working**
1. **Fix V1 backend issues** (scope generation 500 error)
2. **Add missing V1 health endpoint** 
3. **Verify healthcare calculations work** in V1

### 📋 **PRIORITY 2: Healthcare Implementation**
Since healthcare will use **ScopeGenerator → V1 → clean_engine_v2**:
1. **Ensure clean_engine_v2 supports healthcare** 
2. **Fix healthcare_cost_service dependencies**
3. **Test healthcare projects through current V1 flow**

### 🔄 **PRIORITY 3: Future Migration** 
1. **Migrate api.ts base URL** from v1 to v2 (single line change)
2. **Ensure V2 provides all required endpoints**
3. **Update response format handling** if needed

## Files to Modify (Priority Order)

### Immediate Fixes:
- [ ] **backend/app/api/endpoints/scope.py** - Fix clean_engine_v2 issues
- [ ] **backend/app/services/clean_engine_v2.py** - Fix healthcare integration
- [ ] **backend/app/services/healthcare_cost_service.py** - Verify working

### V1→V2 Migration:
- [ ] **frontend/src/services/api.ts** - Change base URL (lines 4-5)
- [ ] **backend/app/v2/api/scope.py** - Add missing V1 endpoints to V2
- [ ] Update hardcoded URLs in components

### Testing Requirements
- [ ] **Dashboard loads** and displays projects
- [ ] **ScopeGenerator creates projects** (especially healthcare)  
- [ ] **ProjectDetail shows** cost breakdowns
- [ ] **Healthcare calculations** produce correct costs
- [ ] **All V1 endpoints** return 200 status

## Conclusion

The frontend depends heavily on V1, but V1 backend is partially broken. **Fix V1 first** to keep the app working, then migrate to V2. Healthcare implementation should work through the current V1 flow once backend issues are resolved.