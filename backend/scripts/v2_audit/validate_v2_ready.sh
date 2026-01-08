#!/bin/bash

# V2 Core Functionality Validation Script
# Must pass all tests before proceeding to Phase 3

set -e  # Exit on any error

echo "================================================"
echo "PHASE 2: V2 CORE FUNCTIONALITY VALIDATION"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL
BASE_URL="http://localhost:8001"

# Test counters
PASSED=0
FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    echo -n "Testing: $test_name... "
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected: $expected_result"
        ((FAILED++))
        return 1
    fi
}

echo "1. TESTING PROJECT CREATION WITHOUT PROJECT_TYPE"
echo "================================================"

# Test 1: Create project without project_type
PROJECT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v2/scope/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "description": "50000 sf office building in Nashville",
        "location": "Nashville, TN"
    }' 2>/dev/null)

PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('data', {}).get('project_id', '') if data.get('data') else '')" 2>/dev/null || echo "")
SUCCESS=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('success', False))" 2>/dev/null || echo "false")

run_test "Project creation without project_type" \
    "[ '$SUCCESS' = 'True' ] && [ -n '$PROJECT_ID' ]" \
    "Project should be created successfully without project_type field"

echo ""
echo "2. TESTING PROJECT LIST RETURNS DATA"
echo "====================================="

# Test 2: Project list returns data
PROJECT_COUNT=$(curl -s "$BASE_URL/api/v2/scope/projects" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

run_test "Project list returns projects" \
    "[ '$PROJECT_COUNT' -gt 0 ]" \
    "Should return at least 1 project"

# Test if projects have categories
HAS_CATEGORIES=$(curl -s "$BASE_URL/api/v2/scope/projects" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data and 'categories' in data[0]:
    print('true')
else:
    print('false')
" 2>/dev/null || echo "false")

run_test "Projects have categories field" \
    "[ '$HAS_CATEGORIES' = 'true' ]" \
    "Projects should have categories array for charts"

echo ""
echo "3. TESTING OWNER VIEW RETURNS REVENUE_ANALYSIS"
echo "==============================================="

# First, get a project ID for testing
if [ -n "$PROJECT_ID" ]; then
    OWNER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v2/scope/owner-view" \
        -H "Content-Type: application/json" \
        -d "{\"project_id\": \"$PROJECT_ID\"}" 2>/dev/null)
    HAS_REVENUE=$(echo "$OWNER_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    response_data = data.get('data', {}) if data.get('data') else data
    if 'revenue_analysis' in response_data or 'revenueAnalysis' in response_data:
        print('true')
    else:
        print('false')
except:
    print('false')
" 2>/dev/null || echo "false")

    run_test "Owner view includes revenue_analysis" \
        "[ '$HAS_REVENUE' = 'true' ]" \
        "Should return revenue_analysis field in owner view"
else
    echo -e "${YELLOW}⚠ Skipping owner view test (no project created)${NC}"
fi

echo ""
echo "4. TESTING NLP DETECTION OF DENTAL OFFICE"
echo "=========================================="

# Test 4: Dental office detection
DENTAL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v2/analyze" \
    -H "Content-Type: application/json" \
    -d '{"description": "25000 sf dental office in Nashville"}' 2>/dev/null)

BUILDING_TYPE=$(echo "$DENTAL_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Check nested structure first
    if 'data' in data and 'parsed_input' in data['data']:
        print(data['data']['parsed_input'].get('building_type', 'unknown'))
    elif 'building_type' in data:
        print(data['building_type'])
    else:
        print('unknown')
except:
    print('error')
" 2>/dev/null || echo "error")

SUBTYPE=$(echo "$DENTAL_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Check nested structure first
    if 'data' in data and 'parsed_input' in data['data']:
        print(data['data']['parsed_input'].get('subtype', 'none'))
    elif 'subtype' in data:
        print(data.get('subtype', 'none'))
    else:
        print('none')
except:
    print('error')
" 2>/dev/null || echo "error")

run_test "Dental office detected as healthcare" \
    "[ '$BUILDING_TYPE' = 'healthcare' ]" \
    "Dental office should be detected as healthcare, not office"

run_test "Dental office has dental_office subtype" \
    "[ '$SUBTYPE' = 'dental_office' ] || [ '$SUBTYPE' = 'dental' ]" \
    "Should have dental_office or dental subtype"

# Test the cost calculation for dental office
DENTAL_PROJECT=$(curl -s -X POST "$BASE_URL/api/v2/scope/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "description": "25000 sf dental office in Nashville",
        "location": "Nashville, TN"
    }' 2>/dev/null)

COST_PER_SF=$(echo "$DENTAL_PROJECT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    project_data = data.get('data', {}) if data.get('data') else data
    if 'cost_per_sqft' in project_data:
        print(int(float(project_data['cost_per_sqft'])))
    elif 'costPerSqft' in project_data:
        print(int(float(project_data['costPerSqft'])))
    else:
        print(0)
except:
    print(0)
" 2>/dev/null || echo "0")

run_test "Dental office cost > \$250/sf (healthcare rate)" \
    "[ '$COST_PER_SF' -gt 250 ]" \
    "Dental office should use healthcare rates (~\$300/sf), not office rates (~\$229/sf)"

echo ""
echo "5. ADDITIONAL V2 ENDPOINT TESTS"
echo "================================"

# Test health endpoint
HEALTH_STATUS=$(curl -s -w "%{http_code}" -o /dev/null "$BASE_URL/api/v2/health" 2>/dev/null)
run_test "V2 health endpoint returns 200" \
    "[ '$HEALTH_STATUS' = '200' ]" \
    "Health endpoint should be accessible"

# Test analyze endpoint
ANALYZE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v2/analyze" \
    -H "Content-Type: application/json" \
    -d '{"description": "100000 sf hospital with emergency department"}' 2>/dev/null)

ANALYZE_SUCCESS=$(echo "$ANALYZE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('true' if data else 'false')
except:
    print('false')
" 2>/dev/null || echo "false")

run_test "V2 analyze endpoint works" \
    "[ '$ANALYZE_SUCCESS' = 'true' ]" \
    "Analyze endpoint should return valid JSON"

echo ""
echo "================================================"
echo "VALIDATION RESULTS"
echo "================================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo "V2 backend is ready for production."
    echo "You can now proceed to Phase 3: Frontend migration"
    exit 0
else
    echo -e "${RED}✗ VALIDATION FAILED${NC}"
    echo "Fix the failing tests before proceeding."
    echo ""
    echo "Common issues:"
    echo "1. Dental office detection: Check NLP parser order (compound terms first)"
    echo "2. Owner view: Ensure revenue_analysis is calculated and returned"
    echo "3. Project list: Check if format_project_response is working"
    echo "4. Project creation: Verify calculation_data column is being used"
    exit 1
fi