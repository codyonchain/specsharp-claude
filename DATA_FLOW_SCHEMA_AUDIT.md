# Comprehensive Data Flow & Schema Audit Results

## 🚨 CRITICAL FINDINGS

### 1. **Database Schema vs Model Mismatch**
**Database Schema (SQLite):**
- `project_type VARCHAR NOT NULL` ❌
- Has 2 existing projects that need preservation

**Python Model:**
- `project_type = Column(String, nullable=True)` ✅
- Marked as DEPRECATED

**Impact:** Inserts will fail if project_type not provided

### 2. **Field Name Disconnects**

| Database/Model | Frontend Expects | Status |
|---------------|------------------|---------|
| `name` | `project_name` | ❌ Mismatch |
| `project_id` | `project_id` | ✅ Match |
| `subtotal` | `construction_cost` | ❌ Mismatch |
| `total_cost` | `total_cost` | ✅ Match |
| N/A | `categories` | ❌ Missing |
| N/A | `calculation_data` | ❌ Not a field |

### 3. **Data Storage Pattern**

**Current Storage:**
- `scope_data`: 14KB JSON string (full calculation)
- `cost_data`: 283 bytes JSON string (partial data)
- No `calculation_data` field exists in database

**Access Pattern:**
```python
# Data must be retrieved as:
import json
scope_data = json.loads(project.scope_data)
revenue = scope_data['ownership_analysis']['revenue_analysis']
```

### 4. **Revenue Data Flow**

**✅ Working Path:**
1. **Unified Engine calculates** (lines 183-211):
   - Annual revenue: $2,480,000 (6200 SF × $400/SF)
   - Operating margin: 8%
   - Net income: $198,400

2. **Stored in database** as JSON:
   ```json
   {
     "ownership_analysis": {
       "revenue_analysis": {
         "annual_revenue": 2480000,
         "operating_margin": 0.08,
         "net_income": 198400
       }
     }
   }
   ```

3. **Owner-view endpoint retrieves** (scope.py:528-576):
   - ✅ Correctly parses JSON from scope_data
   - ✅ Extracts revenue_analysis
   - ✅ Flattens fields for frontend

**❌ Broken Path:**
- Frontend expects `project.calculation_data` but it doesn't exist
- Must use parsed `scope_data` instead

## 📊 AUDIT RESULTS

### **Database Queries:**
```sql
-- Schema shows:
CREATE TABLE projects (
    project_type VARCHAR NOT NULL,  -- Problem!
    scope_data TEXT NOT NULL,        -- JSON storage
    cost_data TEXT,                  -- JSON storage
    ...
)

-- Sample data:
project_id | scope_data_size | cost_data_size
d8a26ed0  | 14050 bytes     | 283 bytes
7035caf8  | 14049 bytes     | 283 bytes
```

### **Frontend Expectations:**
```javascript
// Frontend accesses:
project.project_name      // ❌ Model has 'name'
project.categories        // ❌ Must parse from JSON
project.calculation_data  // ❌ Field doesn't exist
project.total_cost       // ✅ Exists
```

### **API Test Results:**
```json
// ✅ /api/v2/analyze returns:
{
  "success": true,
  "data": {
    "calculations": {
      "revenue_analysis": {
        "annual_revenue": 2480000,
        "operating_margin": 0.08
      }
    }
  }
}
```

## 🔧 REQUIRED FIXES

### **Priority 1: Critical Schema Fix**
```python
# In scope.py generate_scope(), add:
project_type='commercial',  # Always provide to avoid NOT NULL error
```

### **Priority 2: Field Name Mapping**
```python
# In format_project_response(), ensure:
'project_name': project.name,  # Map name → project_name
'construction_cost': project.subtotal,  # Map subtotal → construction_cost
```

### **Priority 3: JSON Data Access**
```python
# Owner-view must parse JSON:
scope_data = json.loads(project.scope_data)
revenue_data = scope_data.get('ownership_analysis', {}).get('revenue_analysis', {})
```

### **Priority 4: Frontend Compatibility**
```python
# Return both formats for compatibility:
{
  'name': project.name,
  'project_name': project.name,  # Duplicate for frontend
  'subtotal': value,
  'construction_cost': value,    # Duplicate for frontend
  'categories': parsed_categories # Parse from trade_breakdown
}
```

## 🎯 DECISION MATRIX

| Issue | Option A | Option B | Recommendation |
|-------|----------|----------|----------------|
| **Schema Mismatch** | Run migration to fix | Always provide value | **B - Safer** |
| **Field Names** | Fix all frontend code | Add aliases in API | **B - Backward compatible** |
| **Data Storage** | Keep JSON in scope_data | Add calculation_data field | **A - Working now** |
| **Revenue Path** | Flatten in API response | Fix frontend navigation | **A - Already done** |

## ✅ CURRENT WORKING STATE

**What's Working:**
1. Revenue calculations in unified_engine ✅
2. JSON storage in scope_data ✅
3. Owner-view parsing and flattening ✅
4. API returns revenue data ✅

**What's Broken:**
1. project_type NOT NULL constraint ❌
2. Field name mismatches ❌
3. Frontend expects calculation_data field ❌

## 🚀 ACTION ITEMS

### **Immediate Fixes Needed:**
1. **Always provide project_type** to avoid database errors
2. **Map field names** in format_project_response()
3. **Parse JSON properly** in all retrieval endpoints
4. **Test with existing projects** (2 in database)

### **Long-term Improvements:**
1. Consider migration to make project_type nullable
2. Standardize field names across system
3. Add proper calculation_data field if needed
4. Remove deprecated fields (project_type, occupancy_type)

## 📝 NOTES

- Database has 2 existing projects that must be preserved
- scope_data contains full 14KB calculation results
- cost_data seems redundant at only 283 bytes
- Revenue data IS being calculated correctly
- Field mapping is the main issue preventing display

The system is **fundamentally working** but has **field mapping issues** preventing proper data display in frontend.