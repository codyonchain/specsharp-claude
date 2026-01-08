# Market Value Implementation Audit Summary

## ✅ CURRENT STATE ANALYSIS

### 1. Method Signature & Parameters
- **Method**: `calculate_revenue_requirements(self, total_cost: float, config, square_footage: float) -> dict`
- **Location**: Line 665 in `backend/app/v2/engines/unified_engine.py`
- **Called from**: Line 474 in `calculate_ownership_analysis`
- **Parameters available**:
  - `total_cost`: Total project cost
  - `config`: Building subtype configuration object
  - `square_footage`: Building square footage

### 2. Available Data in Context
When `calculate_revenue_requirements` is called, the following data is accessible:
- `square_footage`: Passed as parameter ✅
- `config`: Full subtype config with `base_revenue_per_sf_annual` ✅
- `building_type` & `subtype`: Available in parent scope (calculate_ownership_analysis)
- `annual_revenue`: Already calculated in parent method at line 449

### 3. Restaurant Configuration Status
**Full Service Restaurant** has these revenue fields:
- `base_revenue_per_sf_annual`: 400 ✅
- `occupancy_rate_base`: 0.85 ✅
- `occupancy_rate_premium`: 0.90 ✅
- `operating_margin_base`: 0.08 ✅
- `operating_margin_premium`: 0.12 ✅

### 4. Current Return Structure
The method currently returns:
```python
{
    'required_value': float,
    'required_revenue_per_sf': float,
    'metric_name': str,
    'target_roi': float,
    'operating_margin': float,
    'break_even_revenue': float,
    'required_monthly': float
}
```

## 🎯 IMPLEMENTATION PLAN

### Option 1: Add market_value to calculate_revenue_requirements (RECOMMENDED)
**Location**: Line 700 (just before return statement)
**Code to add**:
```python
# Calculate market value based on typical revenue for this building type
market_revenue_per_sf = getattr(config, 'base_revenue_per_sf_annual', 0)
market_value = market_revenue_per_sf * square_footage if market_revenue_per_sf > 0 else 0
```

Then add to return dict:
```python
'market_value': round(market_value, 2),
```

### Option 2: Calculate in parent method
Since `annual_revenue` is already calculated in `calculate_ownership_analysis` (line 449), we could pass it to `calculate_revenue_requirements` as a parameter. But this requires changing the method signature.

## 📋 RECOMMENDED FIX

Add these lines at line 700 in `calculate_revenue_requirements`:
```python
# Calculate market value based on typical revenue for this building type
market_revenue_per_sf = getattr(config, 'base_revenue_per_sf_annual', 0)
market_value = market_revenue_per_sf * square_footage if market_revenue_per_sf > 0 else 0

return {
    'required_value': round(required_revenue, 2),
    'required_revenue_per_sf': round(required_revenue / square_footage, 2) if square_footage > 0 else 0,
    'metric_name': 'Annual Revenue Required',
    'target_roi': target_roi,
    'operating_margin': round(operating_margin, 3),
    'break_even_revenue': round(total_cost * 0.1, 2),
    'required_monthly': round(required_revenue / 12, 2),
    'market_value': round(market_value, 2)  # ADD THIS LINE
}
```

## ✅ WHY THIS WORKS
1. `config` has `base_revenue_per_sf_annual` for restaurants (400)
2. `square_footage` is available as a parameter
3. No need to change method signatures
4. Frontend already expects `market_value` in this object
5. Calculation matches the revenue calculation logic already in the codebase
