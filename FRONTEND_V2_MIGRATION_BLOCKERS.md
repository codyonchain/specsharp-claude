# Frontend V1→V2 Migration Blocker Analysis

## 🚨 CRITICAL FINDING: Missing CRUD Endpoints in V2

### Frontend Requirements vs V2 Availability

**Frontend Needs These V1 Endpoints:**
- ✅ `/scope/generate` (POST) - Create new project  
- ❌ `/scope/projects` (GET) - Get all projects **MISSING IN V2**
- ❌ `/scope/projects/{id}` (GET) - Get specific project **MISSING IN V2**  
- ❌ `/scope/projects/{id}` (DELETE) - Delete project **MISSING IN V2**
- ❌ `/scope/owner-view` (POST) - Get owner view **MISSING IN V2**
- ❌ `/comparison/compare/{id}` (POST) - Compare projects **MISSING IN V2**
- ✅ `/oauth/login/google` (GET) - OAuth login (V1 only)

**V2 Currently Provides:**
- ✅ `/health` (GET) - 200 status
- ✅ `/analyze` (POST) - 200 status (equivalent to /scope/generate)
- ✅ `/calculate` (POST) - 405 (requires POST data)
- ✅ `/building-types` (GET) - 200 status
- ❌ No project CRUD operations
- ❌ No comparison operations

## 🔧 Current Frontend API Usage

### Service Methods Actually Called:
```typescript
// From services/api.ts (V1 client)
authService.getCurrentUser()
authService.isAuthenticated()  
authService.logout()
scopeService.deleteProject()      // ❌ Missing in V2
scopeService.duplicateProject()   // ❌ Missing in V2  
scopeService.generate()           // ✅ V2 has /analyze
scopeService.getProject()         // ❌ Missing in V2
scopeService.getProjects()        // ❌ Missing in V2
scopeService.updateProjectName()  // ❌ Missing in V2
```

### Components Using V1 Client (13 files):
**🚨 CRITICAL:**
- `Dashboard.tsx` - **Loads all projects** (scopeService.getProjects)
- `ScopeGenerator.tsx` - **Creates projects** (scopeService.generate)  
- `ProjectDetail.tsx` - **Views projects** (scopeService.getProject)

**⚠️ HIGH IMPACT:**
- `ScenarioBuilder.tsx`, `SharedProjectView.tsx`, `ComparisonPage.tsx`

**📝 LOW IMPACT:**
- `MarkupSettings.tsx`, `OnboardingFlow.tsx`, `TeamSettings.tsx`, etc.

### Hardcoded V1 URLs (7 locations):
```typescript
// Direct fetch calls bypassing api.ts
'/api/v1/cost-dna/generate'           // CostDNADisplay.tsx
'/api/v1/scope/owner-view'            // ProjectDetail.tsx  
'/api/v1/comparison/compare/{id}'     // ComparisonTool.tsx
'/api/v1/comparison/templates'        // ComparisonTool.tsx
'/api/v1/subscription/create'         // PaymentWall.tsx
'/api/v1/oauth/login/google'          // Login.tsx
```

## 🎯 Backend Migration Status

### V1 Dependencies (8 files still importing clean_engine_v2):
**🚨 ACTIVE V1 ENDPOINTS:**
- `backend/app/api/endpoints/scope.py` - **MAIN ISSUE**
- `backend/app/api/endpoints/demo.py`
- `backend/app/services/comparison_service.py`

**📝 TEST FILES:**
- Various test files (can be updated later)

### V2 is Modern and Complete:
**✅ V2 Uses:**
- `unified_engine` (modern calculation engine)
- `master_config` (centralized configuration)
- Clean imports with no legacy dependencies

**❌ V1 Uses:**
- `clean_engine_v2` (legacy calculation engine)
- `healthcare_cost_service` (old healthcare calculations)
- Mixed configuration sources

## 🚧 Migration Blockers Summary

### 1. **MISSING V2 PROJECT CRUD** (Critical Blocker)
V2 has calculation endpoints but no project storage endpoints:
- No `/scope/projects` to list projects
- No `/scope/projects/{id}` to get/delete projects  
- No owner-view functionality
- No project duplication/update

### 2. **Response Format Differences**
- V1 returns: `{project_id, project_name, created_at, building_type, ...}`
- V2 returns: `{success, data: {parsed_input, calculations, ...}, errors, warnings}`
- Frontend expects V1 format for project data

### 3. **Missing Business Logic**
- V2 focused on calculations, not project management
- No user/project relationship handling
- No project storage/persistence logic

## 💡 SOLUTION: 3-Phase Migration Strategy

### Phase 1: **Make V1 Use V2 Engine** (Quick Win)
**Goal:** Keep frontend working, eliminate legacy engines

```bash
# In backend/app/api/endpoints/scope.py:
# Replace:
from app.services.clean_engine_v2 import calculate_scope

# With:
from app.v2.engines.unified_engine import unified_engine
# Adapter function to match V1 interface
```

**Benefits:**
- ✅ Frontend keeps working unchanged
- ✅ Eliminates clean_engine_v2 dependencies
- ✅ Uses unified_engine + master_config
- ✅ Easier to implement healthcare features

### Phase 2: **Add Missing V2 Endpoints**
**Goal:** Make V2 feature-complete for project management

```python
# Add to backend/app/v2/api/scope.py:
@router.get("/scope/projects")           # List projects
@router.get("/scope/projects/{id}")      # Get project  
@router.delete("/scope/projects/{id}")   # Delete project
@router.post("/scope/owner-view")        # Owner view
```

### Phase 3: **Migrate Frontend to V2**
**Goal:** Use modern V2 API exclusively

```typescript
// Change frontend/src/services/api.ts base URL:
const API_BASE_URL = '${VITE_API_URL}/api/v2'  // Changed from v1
```

## 🎯 Immediate Action Plan

### Priority 1: Phase 1 Implementation 
**Make V1 endpoints use unified_engine:**

1. **Create adapter in V1 scope.py:**
```python
from app.v2.engines.unified_engine import unified_engine

def calculate_scope(request):
    # Adapter: convert V1 request → V2 analyze → V1 response
    v2_result = unified_engine.analyze(request.description)
    return convert_v2_to_v1_format(v2_result)
```

2. **Update other V1 services:**
   - Replace healthcare_cost_service with master_config lookups
   - Update comparison_service to use unified_engine

3. **Test critical frontend flows:**
   - Dashboard loads projects ✅
   - ScopeGenerator creates projects ✅  
   - ProjectDetail shows costs ✅

### Priority 2: Healthcare Implementation
With unified_engine powering V1 endpoints:
- ✅ Healthcare subtypes work through existing frontend
- ✅ Regional multipliers handled correctly
- ✅ Cost calculations use master_config

### Priority 3: V2 Migration Prep
- Add missing V2 CRUD endpoints
- Test response format compatibility
- Plan frontend migration

## 🏁 End State
After migration:
- ❌ Delete: `clean_engine_v2.py`, `healthcare_cost_service.py`
- ❌ Delete: All `/api/v1` endpoints  
- ✅ Keep: `unified_engine`, `master_config` only
- ✅ Frontend: Uses `/api/v2` exclusively

**Phase 1 gets us 80% of the benefits with 20% of the effort.**