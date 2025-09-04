# Healthcare Service Audit Report

## Executive Summary
⚠️ **DUAL ARCHITECTURE DETECTED**: Healthcare calculations are being handled by TWO different systems, producing different results.

## Current State

### healthcare_cost_service.py
- **Status**: ✅ ACTIVELY USED
- **Last modified**: Recent (uses building_type parameter after occupancy_type removal)
- **Imported by**:
  - `nlp_service.py` - For healthcare facility detection
  - `cost_service.py` - For healthcare cost calculations
  - `cost_dna_service.py` - For healthcare cost DNA
- **Methods**: Complex healthcare-specific calculations including:
  - `calculate_healthcare_costs_v2()` - Market-specific costs
  - `determine_facility_type()` - Facility classification
  - Equipment costs, compliance requirements, special spaces

### clean_engine_v2.py
- **Status**: ✅ ALSO HANDLES HEALTHCARE
- **Used by**: Main API endpoints (`scope.py`)
- **Healthcare handling**: Basic logic for healthcare in multiple places
- **Result**: Different cost calculations than healthcare_cost_service

## Architecture Comparison

### Test Results (50,000 SF Hospital in Nashville)
- **clean_engine_v2**: $1,184.50/SF ($59.2M total)
- **healthcare_cost_service**: $1,041.91/SF ($52.1M total)
- **Difference**: $142.59/SF (13.7% variance) ⚠️

### Key Differences
1. **healthcare_cost_service**:
   - Sophisticated healthcare-specific logic
   - Handles 10+ facility types (hospital, surgical center, imaging, etc.)
   - Equipment costs calculated separately
   - Market-specific adjustments
   - Compliance requirements (CON, licensing)

2. **clean_engine_v2**:
   - Generic building type handling
   - Basic healthcare multipliers
   - No specialized facility subtypes
   - Simpler calculation model

## Problem Analysis

### Current Flow
```
User Input → scope.py → clean_engine_v2 → Generic calculation
                ↓
        nlp_service.py → healthcare_cost_service → Specialized but unused
```

### Issues Identified
1. **Inconsistent Results**: Two systems producing different costs
2. **Wasted Computation**: healthcare_cost_service does complex calculations in NLP but results aren't used
3. **Feature Loss**: Healthcare-specific features (equipment, compliance) not reaching users
4. **Maintenance Burden**: Two separate systems to maintain

## Code Dependencies

### Files Using healthcare_cost_service:
1. **nlp_service.py:201** - Detects healthcare and gets detailed analysis
2. **cost_service.py:604** - Uses V2 calculation for healthcare facilities  
3. **cost_dna_service.py** - Gets healthcare cost DNA

### Critical Question
❓ **Which path does the API actually use?**
- `scope.py` → Uses `clean_engine_v2` ✅
- `cost_service.py` → Uses `healthcare_cost_service` but is cost_service called by scope.py?

## Recommendation

### ⚠️ DO NOT DELETE healthcare_cost_service.py YET

### Immediate Actions Needed:
1. **DETERMINE TRUTH**: Which calculation should be authoritative?
   - If healthcare needs specialized handling → Integrate healthcare_cost_service INTO clean_engine_v2
   - If generic is sufficient → Remove healthcare_cost_service

2. **CHECK PRODUCTION**: 
   - Are healthcare projects showing $1,184/SF or $1,041/SF?
   - Which number do users expect?

3. **UNIFY ARCHITECTURE**:
   ```python
   # Option A: Use specialized service
   if building_type == 'healthcare':
       return healthcare_cost_service.calculate_healthcare_costs_v2(...)
   
   # Option B: Migrate logic to clean_engine_v2
   # Copy sophisticated healthcare logic into unified engine
   ```

### Migration Path (Recommended)
1. **Phase 1**: Verify which costs are correct with business team
2. **Phase 2**: If healthcare_cost_service is more accurate:
   - Modify clean_engine_v2 to call healthcare_cost_service for healthcare
   - Test thoroughly
3. **Phase 3**: Once unified and tested:
   - Consider full integration or keeping as specialized module
4. **Phase 4**: Remove duplicate logic

## Risk Assessment
- **High Risk**: Deleting healthcare_cost_service now would:
  - Break nlp_service.py healthcare detection
  - Break cost_service.py if it's used anywhere
  - Lose sophisticated healthcare calculation logic
  - Potentially give incorrect healthcare estimates

- **Low Risk**: Keep both temporarily while unifying

## Conclusion
The healthcare_cost_service is **NOT dead code** - it's actively used but in a **disconnected architecture**. The main API uses clean_engine_v2 while specialized services use healthcare_cost_service, creating inconsistency. This needs architectural unification, not deletion.

---
*Audit completed: December 2024*