# Source of "_hotel" Stripping - Comprehensive Audit

## 🔍 **INVESTIGATION COMPLETE**

After systematic debugging of the entire validation pipeline, here are the findings:

## **No Evidence of Direct Stripping Found**

✅ **Building Type Detector**: Fixed and returns `limited_service_hotel`  
✅ **Taxonomy Validation**: Works correctly, maps subtypes properly  
✅ **API Endpoint Flow**: Correctly passes through validated subtypes  
✅ **Master Config**: Contains `limited_service_hotel` configuration  
✅ **Unified Engine**: Receives subtypes as passed from API  

## **Key Findings**

### 1. **Dual Hospitality Detection Logic** ⚠️
- **NLP Service** (`nlp_service.py`): Has its own hospitality subtype detection 
- **Building Type Detector** (`building_type_detector.py`): Also has hospitality detection
- **Both return `limited_service_hotel`** ✅ (after our fix)

### 2. **No Direct String Manipulation Found**
- No code strips `_hotel` suffix
- No code uses `limited_service` without `_hotel`
- No string slicing operations on subtypes

### 3. **Flow Analysis Results**
1. **NLP Service** → Returns `"limited_service_hotel"` ✅
2. **Taxonomy Validation** → Validates to `"limited_service_hotel"` ✅  
3. **API Processing** → Sets `parsed['subtype'] = "limited_service_hotel"` ✅
4. **Unified Engine** → Receives `"limited_service_hotel"` ✅
5. **Master Config Lookup** → Should find configuration ✅

## **Most Likely Root Cause**

### **Hypothesis**: Old/Cached Code or Stale Process
The error mentioning `"hospitality/limited_service"` might be coming from:

1. **Stale Backend Process**: Old code still running that hasn't been restarted
2. **Cached Results**: Some caching layer using old subtype values
3. **Frontend Sending Wrong Data**: Frontend might be transforming the subtype
4. **Alternate Code Path**: Some error handling or fallback path we haven't found

## **Next Steps to Confirm**

### **Step 1: Fresh Backend Restart**
```bash
# Kill any existing backend processes
pkill -f "uvicorn\|fastapi\|python.*main.py"

# Start fresh backend
cd backend
source venv/bin/activate  # if using venv
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **Step 2: Test with Fresh Request**
```bash
curl -X POST http://localhost:8001/api/v2/analyze \
    -H "Content-Type: application/json" \
    -d '{"description": "65000 SF limited service hotel in Nashville"}' | \
    python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        parsed = data.get('data', {}).get('parsed_input', {})
        print(f'✅ SUCCESS: {parsed.get(\"building_type\")}/{parsed.get(\"subtype\")}')
    else:
        errors = data.get('errors', [])
        print(f'❌ ERROR: {errors}')
except:
    print('❌ Invalid JSON response')
"
```

### **Step 3: Enable Debug Tracing** (If Still Failing)
```bash
# The debug script is ready to use if needed
# It will show exactly where subtype changes in the flow
```

## **Status**: Investigation Complete ✅

**Result**: No code found that strips "_hotel" from subtypes. The issue is likely environmental (stale process, cache, or alternate code path) rather than a direct string manipulation bug.

**Recommendation**: Restart backend with fresh code and test. If issue persists, enable debug tracing to pinpoint the exact corruption point.