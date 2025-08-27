# Frontend Code Analysis Report

## Executive Summary
The frontend exhibits similar technical debt patterns to the backend V1, with **9 components over 500 lines**, **scattered API calls**, and **duplicated building type logic**. However, it has better organization with a centralized API service, making V2 migration feasible.

## Current State Assessment

### File Organization
- **Total TypeScript/TSX files**: 83
- **Components**: 42 files
- **Services**: 3 files (api.ts, nlpService.ts, schedulingEngine.ts)
- **Pages**: 10+ files
- **Utils**: 15+ files

## Critical Issues Found

### 1. 🔴 Massive Component Files
**9 components exceed 500 lines**, with the largest being:
- `ProjectDetail.tsx`: **1,701 lines** (needs urgent splitting)
- `ScopeGenerator.tsx`: **1,383 lines** (mixed concerns)
- `HomePage.tsx`: 713 lines
- `ProgressiveProjectDetail.tsx`: 693 lines
- `Dashboard.tsx`: 660 lines

**Impact**: Difficult to maintain, test, and debug. High risk of bugs.

### 2. 🟡 API Call Patterns
**Good news**: Most API calls go through `services/api.ts`
**Bad news**: 5 components still make direct fetch calls:
- ComparisonTool.tsx
- CostDNA/CostDNADisplay.tsx
- PaymentWall.tsx
- ProjectDetail.tsx
- utils/analytics.ts

**Impact**: Inconsistent error handling, difficult V2 migration.

### 3. 🟡 Frontend Calculation Logic
**15+ files contain calculation logic**, suggesting:
- Some calculations happening in UI (should be backend-only)
- Potential discrepancies with backend calculations
- Files affected: ProjectDetail, Dashboard, TradeBreakdownView, etc.

**Impact**: Risk of calculation mismatches, maintenance burden.

### 4. 🟡 Building Type Definitions
**Multiple sources of truth**:
- `config/buildingTypes.ts` (605 lines!)
- Various utils files with type logic
- 15+ components with hardcoded building types

**Impact**: Must sync with backend V2's 13 types and 48 subtypes.

### 5. 🟢 State Management
**Simple but functional**:
- 37 files use local state (useState)
- No global state management (Context/Redux)
- Likely prop drilling in deep component trees

**Impact**: Acceptable for current scale, but may need refactoring for growth.

## Recommended Refactoring Strategy

### Phase 1: API Abstraction Layer (2 hours)
Create a V2-ready API client:

```typescript
// services/api/v2Client.ts
export class SpecSharpV2Client {
  private baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  private version = 'v2';
  
  async analyze(text: string) {
    return this.post('/analyze', { text });
  }
  
  async calculate(params: CalculationParams) {
    return this.post('/calculate', params);
  }
  
  async compare(scenarios: Scenario[]) {
    return this.post('/compare', { scenarios });
  }
  
  private async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}/api/${this.version}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.getToken()}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
}
```

### Phase 2: Extract Shared Types (1 hour)
Align with backend V2:

```typescript
// types/building.ts
export enum BuildingType {
  HEALTHCARE = 'healthcare',
  MULTIFAMILY = 'multifamily',
  OFFICE = 'office',
  RETAIL = 'retail',
  INDUSTRIAL = 'industrial',
  HOSPITALITY = 'hospitality',
  EDUCATIONAL = 'educational',
  CIVIC = 'civic',
  RECREATION = 'recreation',
  MIXED_USE = 'mixed_use',
  PARKING = 'parking',
  RESTAURANT = 'restaurant',
  SPECIALTY = 'specialty'
}

export type ProjectClass = 'ground_up' | 'addition' | 'renovation';
```

### Phase 3: Component Splitting (4-6 hours)
Priority components to split:

1. **ProjectDetail.tsx** (1,701 lines) → Split into:
   - ProjectDetailContainer.tsx (data fetching)
   - ProjectSummary.tsx (header info)
   - CostBreakdown.tsx (cost display)
   - TradeAnalysis.tsx (trade details)
   - ProjectActions.tsx (buttons/actions)

2. **ScopeGenerator.tsx** (1,383 lines) → Split into:
   - ScopeForm.tsx (main form)
   - BuildingTypeSelector.tsx
   - LocationSelector.tsx
   - ProjectClassSelector.tsx
   - useScopeGeneration.ts (custom hook)

### Phase 4: Feature Flag Implementation (30 min)
Enable gradual rollout:

```typescript
// config/features.ts
export const features = {
  useV2API: import.meta.env.VITE_USE_V2_API === 'true',
  showDebugInfo: import.meta.env.VITE_DEBUG === 'true'
};

// services/api.ts
const client = features.useV2API ? new V2Client() : new V1Client();
```

## Migration Path to V2

### Week 1: Foundation
- [ ] Create V2 API client
- [ ] Add feature flags
- [ ] Extract shared types
- [ ] Set up monitoring

### Week 2: Core Components
- [ ] Update ScopeGenerator to use V2
- [ ] Update Dashboard to use V2
- [ ] Update ProjectDetail to use V2
- [ ] Remove calculation logic from frontend

### Week 3: Testing & Rollout
- [ ] A/B test with 10% of users
- [ ] Monitor for errors
- [ ] Gradual rollout to 100%
- [ ] Remove V1 code

## Quick Wins (Can do today)

### 1. Remove Direct Fetch Calls (1 hour)
Update these 5 files to use api.ts:
- ComparisonTool.tsx
- CostDNA/CostDNADisplay.tsx
- PaymentWall.tsx
- ProjectDetail.tsx
- utils/analytics.ts

### 2. Create Building Type Constants (30 min)
Single source of truth matching backend V2.

### 3. Add Error Boundary (30 min)
Wrap main app to catch and report errors gracefully.

## Performance Opportunities

1. **Code Splitting**: Large components can be lazy loaded
2. **Memoization**: Add React.memo to expensive components
3. **Virtual Scrolling**: For long project lists in Dashboard
4. **API Caching**: Implement SWR or React Query

## Metrics & Monitoring

Current baseline:
- Largest component: 1,701 lines
- API abstraction: 60% (most through api.ts)
- Type safety: Partial (no shared types with backend)
- State management: Local only

Target after refactoring:
- Largest component: <300 lines
- API abstraction: 100%
- Type safety: Full (shared types)
- State management: Consider Zustand if needed

## Conclusion

The frontend is **more organized than expected** with a decent service layer, but needs:
1. **Urgent component splitting** (especially ProjectDetail.tsx)
2. **API consolidation** for V2 migration
3. **Type alignment** with backend V2
4. **Removal of frontend calculations**

Estimated effort for V2 migration: **2-3 days** with proper planning.

The good news: Unlike the backend, the frontend doesn't need a complete rewrite—just strategic refactoring.