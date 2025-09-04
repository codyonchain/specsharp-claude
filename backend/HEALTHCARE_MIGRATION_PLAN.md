# Healthcare Logic Migration Plan

## Executive Summary
Migrate sophisticated healthcare calculations from `healthcare_cost_service.py` into the unified master_config system, preserving 10 facility types, equipment costs, special department premiums, and unique trade allocations.

## Current Architecture Gap Analysis

### Master Config V2 (Current - Too Simple)
```python
'healthcare': {
    base_cost: 1100-1400,  # Single range
    trades: {mechanical: 0.35},  # Basic percentages
    # NO subtypes
    # NO equipment costs  
    # NO special departments
}
```

### healthcare_cost_service.py (Sophisticated)
```python
10 Facility Types × Equipment Costs × Special Departments × Trade Variations
= Accurate healthcare pricing
```

## Migration Data Map

### 1. Facility Types & Costs
| Facility Type | Construction | Equipment | Total Range | Typical Size |
|--------------|--------------|-----------|-------------|--------------|
| **Hospital** | $850/SF | $150/SF | $900-1200 | 50K-500K SF |
| **Surgical Center** | $550/SF | $200/SF | $700-850 | 10K-50K SF |
| **Medical Center** | $750/SF | $150/SF | $850-1000 | 30K-200K SF |
| **Imaging Center** | $500/SF | $300/SF | $750-900 | 5K-20K SF |
| **Outpatient Clinic** | $380/SF | $50/SF | $400-480 | 3K-20K SF |
| **Urgent Care** | $350/SF | $75/SF | $400-475 | 3K-10K SF |
| **Medical Office** | $320/SF | $20/SF | $325-375 | 5K-100K SF |
| **Dental Office** | $300/SF | $30/SF | $315-360 | 2K-10K SF |
| **Rehabilitation** | $325/SF | $100/SF | $400-475 | 20K-100K SF |
| **Nursing Home** | $275/SF | $10/SF | $275-325 | 20K-150K SF |

### 2. Special Department Premiums (Hospitals Only)
| Department | Premium/SF | Typical % of Building | Impact on 100K SF Hospital |
|-----------|-----------|----------------------|---------------------------|
| Emergency | +$50 | 15% | +$750,000 |
| Surgery/OR | +$75 | 10% | +$750,000 |
| ICU | +$60 | 10% | +$600,000 |
| Imaging | +$40 | 5% | +$200,000 |
| Laboratory | +$25 | 5% | +$125,000 |
| **Total Premiums** | | **45%** | **+$2,425,000** |

### 3. Unique Trade Allocations
```
Standard Commercial:         Healthcare Variance:
Mechanical: 20%       →      Hospital: 35% (+75% increase!)
Electrical: 15%       →      Imaging: 22% (+47% increase!)
Structural: 15%       →      Imaging: 18% (shielding)
```

## Implementation Plan

### Phase 1: Update Master Config (Week 1)
```python
# Add to app/v2/config/master_config.py
'healthcare': {
    'subtypes': {
        'hospital': {
            'base_construction': 850,
            'equipment': 150,
            'departments': {...},
            'trades': {'mechanical': 0.35, ...}
        },
        # ... 9 more subtypes
    }
}
```

### Phase 2: Modify clean_engine_v2 (Week 1-2)
```python
# Enhance calculate_scope() to:
1. Read healthcare subtypes
2. Apply equipment costs as separate line item
3. Calculate department premiums based on building size
4. Use facility-specific trade allocations
```

### Phase 3: Testing & Validation (Week 2)
```python
# Test matrix:
for facility in ['hospital', 'surgical_center', ...]:
    for size in [min_size, typical_size, max_size]:
        old_cost = healthcare_cost_service.calculate(...)
        new_cost = clean_engine_v2.calculate(...)
        assert abs(old_cost - new_cost) < 5%  # Within tolerance
```

### Phase 4: Deprecation (Week 3)
```python
# healthcare_cost_service.py
@deprecated("Use clean_engine_v2 with master_config")
def calculate_healthcare_costs_v2(...):
    # Proxy to new system during transition
    return clean_engine_v2.calculate(...)
```

### Phase 5: Cleanup (Week 4)
- Remove healthcare_cost_service.py
- Update all imports in nlp_service, cost_service, cost_dna_service
- Archive healthcare logic documentation

## Risk Mitigation

### Critical Validations
1. **Cost Accuracy**: New system must match within 5% of current
2. **Equipment Separation**: Must remain separate line item (not in construction)
3. **Department Detection**: NLP must still identify "emergency", "surgery", etc.
4. **Trade Percentages**: Must sum to 100% for each facility type

### Rollback Plan
- Keep healthcare_cost_service.py during transition
- Feature flag: `USE_LEGACY_HEALTHCARE = True`
- A/B test with select projects

## Success Metrics
- ✅ All 10 facility types calculating correctly
- ✅ Equipment costs shown as separate line item
- ✅ Special departments detected and priced
- ✅ Trade allocations match facility type
- ✅ No regression in cost accuracy (±5%)
- ✅ Single source of truth (master_config)

## Code Changes Required

### 1. master_config.py
```python
# FROM:
BuildingType.HEALTHCARE: BuildingConfig(base_cost=1100)

# TO:
BuildingType.HEALTHCARE: HealthcareConfig(
    subtypes={...},  # 10 facility types
    equipment_costs={...},
    special_departments={...},
    trade_overrides={...}
)
```

### 2. clean_engine_v2.py
```python
def calculate_healthcare(request):
    subtype = detect_healthcare_subtype(request.description)
    base_cost = config.healthcare.subtypes[subtype].base_construction
    equipment = config.healthcare.subtypes[subtype].equipment
    
    # Apply department premiums
    if subtype == 'hospital' and 'emergency' in description:
        base_cost += config.healthcare.departments.emergency.premium
    
    # Use facility-specific trades
    trades = config.healthcare.subtypes[subtype].trades
    
    return {
        'construction': base_cost * sqft,
        'equipment': equipment * sqft,  # Separate line item!
        'trades': apply_trade_percentages(trades)
    }
```

### 3. Update Import Points
```python
# nlp_service.py
# FROM: from healthcare_cost_service import healthcare_cost_service
# TO: from clean_engine_v2 import calculate_healthcare

# cost_service.py - same change
# cost_dna_service.py - same change
```

## Timeline
- **Week 1**: Config updates + engine modifications
- **Week 2**: Testing + validation
- **Week 3**: Gradual rollout with monitoring
- **Week 4**: Complete migration + cleanup

## Expected Outcome
- **Unified Architecture**: One source of truth for all building types
- **Preserved Sophistication**: All healthcare nuances maintained
- **Better Maintenance**: Config-driven vs hard-coded
- **Cost Consistency**: Eliminates the $142/SF discrepancy
- **Future-Proof**: Easy to add new facility types or adjust costs

---
*Migration plan prepared: December 2024*
*Preserves $275-1200/SF sophisticated healthcare logic in unified architecture*