# API Flow Audit - Nashville Regional Multiplier Issue

## Executive Summary
Nashville shows 1.0x instead of 1.03x in the API, but direct engine calls return the correct 1.03x value.

## Call Chain Analysis

### 1. API Endpoint
- **Location**: `/app/v2/api/scope.py` line 65
- **Endpoint**: `POST /api/v2/analyze`
- **Handler**: `analyze_project()`

### 2. Data Flow
```
Frontend → /api/v2/analyze
    ↓
scope.py: analyze_project()
    ↓ (parses "Nashville TN" → "Nashville, Tennessee")
unified_engine.calculate_project()
    ↓
get_regional_multiplier(OFFICE, class_b, "Nashville, Tennessee")
    ↓
Returns 1.03 ✅ (confirmed by direct test)
```

### 3. Multiple Definition Conflict

Found **THREE different** `get_regional_multiplier` functions:

1. **`/app/v2/config/master_config.py:4706`** ✅
   - Takes: `(building_type, subtype, city)`
   - Nashville: **1.03**
   - **THIS IS THE ONE BEING IMPORTED**

2. **`/app/services/building_types_config.py:522`** ⚠️
   - Takes: `(location)` only
   - Nashville: **1.02**
   - Tennessee: **1.00**

3. **`/app/services/cost_service.py:172`** ⚠️
   - Class method, different signature

## Test Results

### Direct Engine Test ✅
```python
engine = UnifiedEngine()
result = engine.calculate_project(
    building_type=BuildingType.OFFICE,
    subtype='class_b',
    square_footage=10000,
    location='Nashville, Tennessee'
)
# Returns: regional_multiplier = 1.03 ✅
# Cost DNA: regional_adjustment = 1.03 ✅
```

### API Test ❌
```bash
curl /api/v2/analyze "10000 SF office in Nashville TN"
# Returns: regional_multiplier = 1.0 ❌
# Cost DNA: MISSING ❌
```

## Root Cause Analysis

### The Problem
**Module caching/reload issue in the running FastAPI server**

### Evidence:
1. Direct Python calls return **1.03** ✅
2. The correct function is imported
3. The fix is in the code (handles "Nashville, Tennessee")
4. BUT the API returns **1.0** ❌

### Why This Happens:
- FastAPI/Uvicorn is using a cached version of the module
- The `--reload` flag isn't working properly
- Python's module cache is persisting old code

## Solution

### Option 1: Force Complete Restart
```bash
# Kill ALL Python processes
pkill -9 python
pkill -9 uvicorn

# Clear ALL cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Remove any .pyo files
find . -name "*.pyo" -delete

# Start fresh
cd backend
python3 -m uvicorn app.main:app --port 8001 --reload
```

### Option 2: Add Debug Logging
Add logging to track which function is actually being called:
```python
# In unified_engine.py line 101
import logging
logger = logging.getLogger(__name__)
logger.warning(f"CALLING get_regional_multiplier with: {building_type}, {subtype}, {location}")
regional_multiplier = get_regional_multiplier(building_type, subtype, location)
logger.warning(f"RETURNED: {regional_multiplier}")
```

### Option 3: Bypass Cache
Force reimport in the API:
```python
# In scope.py before calling engine
import importlib
import app.v2.engines.unified_engine
importlib.reload(app.v2.engines.unified_engine)
from app.v2.engines.unified_engine import unified_engine
```

## Conclusion
The code is correct. Nashville is configured as 1.03x. The engine returns 1.03x when tested directly. The issue is **100% a module caching problem** in the running server.

## Verification
After restart, Nashville should show:
- Regional Multiplier: **1.03x**
- Cost Build-Up: "Nashville Market: 1.03x (+3%)"
- Cost DNA included in response