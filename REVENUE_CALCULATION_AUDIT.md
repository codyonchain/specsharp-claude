# Revenue Calculation Location Audit

## 🎯 SUMMARY: Revenue Calculations Found in Multiple Places

### **Current State:**
- ✅ **Restaurants have revenue calculations** in unified_engine 
- ❌ **Revenue values missing** from master_config
- ✅ **Owner view engine exists** with comprehensive revenue logic
- ❌ **Restaurant revenue not in owner_metrics_config**

## 📍 REVENUE CALCULATION LOCATIONS

### **1. Unified Engine (Lines 183-211)** ⭐ **PRIMARY SOURCE**
**File:** `backend/app/v2/engines/unified_engine.py`

**Restaurant Revenue Calculation (WORKING):**
```python
if building_type == BuildingType.RESTAURANT:
    revenue_per_sf_annual = {
        'quick_service': 600,      # $600/SF/year for QSR
        'full_service': 400,       # $400/SF/year for full service  
        'bar_tavern': 350          # $350/SF/year for bars
    }.get(subtype, 400)
    
    annual_revenue = square_footage * revenue_per_sf_annual
    operating_margin = 0.08        # 8% operating margin
    
    revenue_analysis = {
        'annual_revenue': annual_revenue,
        'revenue_per_sf': revenue_per_sf_annual,
        'operating_margin': operating_margin,
        'net_income': annual_revenue * operating_margin,
        'payback_period': total_project_cost / (annual_revenue * operating_margin)
    }
```

**✅ This explains why restaurant revenue works!**

### **2. Master Config (Target ROI Only)**
**File:** `backend/app/v2/config/master_config.py`

**Restaurant Config Contains:**
- ✅ `target_roi` values (0.12 for quick_service, etc.)
- ❌ **NO revenue_per_sf values**
- ❌ **NO operating_margin values**  
- ❌ **NO occupancy_rate values**

**Example Config:**
```python
BuildingConfig(
    base_cost_per_sf=300,
    ownership_types={
        OwnershipType.FOR_PROFIT: FinancingTerms(target_roi=0.12)
    },
    # Missing revenue fields that should be here:
    # revenue_per_sf_annual=600,
    # operating_margin=0.08, 
    # occupancy_rate=0.85
)
```

### **3. Owner View Engine (Comprehensive)** 📊 **FALLBACK SYSTEM**
**File:** `backend/app/services/owner_view_engine.py`

**Revenue Calculation Formula:**
```python
# Line 383: Get revenue config
revenue_per_unit = config.get('revenue_per_unit', 500000)
occupancy_rate = config.get('occupancy_rate', 0.85)

# Line 394: Calculate annual revenue  
annual_revenue = unit_count * revenue_per_unit * occupancy_rate

# Line 398: Calculate net income
operating_margin = config.get('operating_margin', 0.15)
annual_net_income = annual_revenue * operating_margin
```

**⚠️ Problem:** Restaurants not configured in owner_view_engine

### **4. Owner Metrics Config (Healthcare Only)**
**File:** `backend/app/services/owner_metrics_config.py`

**Contains:**
- ✅ Healthcare department allocations
- ✅ Healthcare soft costs
- ❌ **NO restaurant configurations**
- ❌ **NO revenue assumptions for restaurants**

## 🔍 WHY FRONTEND GETS $0 REVENUE FOR RESTAURANTS

### **Root Cause Analysis:**

1. **Frontend calls `/api/v2/scope/owner-view`** (Line 502 in scope.py)
2. **Owner-view gets stored** `project.calculation_data['ownership_analysis']`
3. **Unified engine stores revenue** in `ownership_analysis['revenue_analysis']`
4. **But owner-view only returns** shallow `owner_data` without nested revenue_analysis

### **The Data Path Disconnect:**

**Unified Engine Stores (calculate_project):**
```python
ownership_analysis = {
    'revenue_analysis': {          # ⭐ Revenue data here
        'annual_revenue': 1200000,
        'operating_margin': 0.08,
        'net_income': 96000
    },
    'roi_analysis': {
        'financial_metrics': {...}
    }
}
```

**Owner-View Returns (scope.py:529):**
```python
return ProjectResponse(data={
    'ownership_analysis': owner_data,           # ✅ Full object
    'financial_metrics': owner_data.get('financial_metrics', {}),  # ❌ Wrong path
    'revenue_requirements': owner_data.get('revenue_requirements', {})  # ❌ Wrong path
})
```

**❌ Missing:** `owner_data.get('revenue_analysis', {})`

## 💡 SOLUTIONS

### **Option A: Fix V2 Owner-View Response (Quick Fix)**
**Modify:** `backend/app/v2/api/scope.py:529-540`

```python
return ProjectResponse(
    success=True,
    data={
        'project_id': project.id,
        'project_name': project.project_name,
        'total_cost': project.total_cost,
        'cost_per_sf': project.cost_per_sqft,
        'ownership_analysis': owner_data,
        
        # FIX: Access nested revenue_analysis
        'revenue_analysis': owner_data.get('revenue_analysis', {}),
        'financial_metrics': owner_data.get('revenue_analysis', {}).get('financial_metrics', {}),
        'revenue_requirements': owner_data.get('revenue_requirements', {}),
        
        # Also expose roi_analysis
        'roi_analysis': owner_data.get('roi_analysis', {})
    }
)
```

### **Option B: Move Revenue to Master Config (Complete)**
**Add to restaurant configs in master_config.py:**

```python
BuildingConfig(
    base_cost_per_sf=300,
    # Add revenue fields:
    revenue_per_sf_annual=600,     # For quick_service
    operating_margin=0.08,         # 8% margin
    occupancy_rate=0.85,           # 85% utilization
    # ... existing fields
)
```

**Then update unified_engine to use config values:**
```python
# Replace hardcoded values with:
revenue_per_sf_annual = building_config.revenue_per_sf_annual
operating_margin = building_config.operating_margin
```

### **Option C: Add Restaurants to Owner Metrics Config**
**Add to:** `backend/app/services/owner_metrics_config.py`

```python
OWNER_METRICS_CONFIG = {
    'restaurant': {
        'quick_service': {
            'revenue_per_sf_annual': 600,
            'operating_margin': 0.08,
            'occupancy_rate': 0.85,
            # ... department allocations
        }
    }
}
```

## 🎯 RECOMMENDED APPROACH

### **Phase 1: Quick Fix (Owner-View Response)**
✅ **Fix owner-view endpoint** to return `revenue_analysis` data
✅ **Test restaurant revenue display** works immediately  
✅ **No changes to calculation logic** needed

### **Phase 2: Data Consolidation**  
✅ **Move all revenue values** to master_config for consistency
✅ **Remove hardcoded values** from unified_engine
✅ **Single source of truth** for all revenue assumptions

## 📊 TEST CONFIRMATION

**Expected Result After Phase 1 Fix:**
1. Create restaurant project via V2
2. Call owner-view endpoint  
3. Frontend should display:
   - Annual Revenue: $1,200,000 (50k SF × $24/SF)
   - Operating Margin: 8%
   - Net Income: $96,000
   - Payback Period: ~52 years (if $5M cost)

The revenue calculations **ARE working** in unified_engine, they're just **not being returned** by the owner-view endpoint properly.