#!/bin/bash

echo "🔐 Running Tests with Auth Bypass"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Set test environment
export ENVIRONMENT=development
export TESTING=true
export NODE_ENV=test
export REACT_APP_TESTING=true

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

# Function to check if port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Kill existing processes on our ports
echo "Cleaning up existing processes..."
if check_port 8001; then
    echo "  Killing process on port 8001..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    sleep 1
fi

if check_port 3000; then
    echo "  Killing process on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start backend in test mode
echo -e "${YELLOW}Starting backend with auth bypass...${NC}"
cd backend
ENVIRONMENT=development TESTING=true uvicorn app.main:app --reload --port 8001 > ../backend-test.log 2>&1 &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Wait for backend
echo "  Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Backend ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "  ${RED}✗ Backend failed to start${NC}"
        echo "  Check backend-test.log for errors"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Start frontend in test mode  
echo -e "${YELLOW}Starting frontend with auth bypass...${NC}"
cd ../frontend
REACT_APP_TESTING=true npm run dev > ../frontend-test.log 2>&1 &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

# Wait for frontend
echo "  Waiting for frontend to start..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Frontend ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "  ${RED}✗ Frontend failed to start${NC}"
        echo "  Check frontend-test.log for errors"
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Run tests
echo ""
echo -e "${YELLOW}Running test suite...${NC}"
echo "================================="
cd "$PROJECT_ROOT"

# Track test results
FAILED_TESTS=""
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run a test and track results
run_test() {
    local test_name=$1
    local test_path=$2
    
    echo ""
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo "  Path: $test_path"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if TESTING=true npx playwright test "$test_path" --config=tests/playwright.config.ts --reporter=line; then
        echo -e "  ${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "  ${RED}✗ FAILED${NC}"
        FAILED_TESTS="$FAILED_TESTS\n  - $test_name"
    fi
}

# Run test groups
echo ""
echo "🧪 Running API Integration Tests"
echo "---------------------------------"
run_test "API Calculations with Auth" "tests/integration/api/calculations-with-auth.test.ts"

echo ""
echo "🧪 Running Performance Tests"
echo "----------------------------"
run_test "Performance with Auth" "tests/e2e/regression/performance-with-auth.spec.ts"

echo ""
echo "🧪 Running Critical Path Tests"
echo "------------------------------"
run_test "Full Flow with Auth" "tests/e2e/critical-paths/full-flow-with-auth.spec.ts"
run_test "Data Validation" "tests/e2e/critical-paths/data-validation.spec.ts"
run_test "Trade Breakdown" "tests/e2e/critical-paths/trade-breakdown.spec.ts"

# Cleanup
echo ""
echo -e "${YELLOW}Cleaning up...${NC}"
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
sleep 1

# Final report
echo ""
echo "================================="
echo "📊 Test Results Summary"
echo "================================="
echo "Total Tests Run: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$((TOTAL_TESTS - PASSED_TESTS))${NC}"

if [ -n "$FAILED_TESTS" ]; then
    echo ""
    echo -e "${RED}Failed Tests:${NC}"
    echo -e "$FAILED_TESTS"
    echo ""
    echo "💡 Tips for debugging:"
    echo "  1. Check backend-test.log and frontend-test.log"
    echo "  2. Run individual tests with --headed flag"
    echo "  3. Check test screenshots in tests/reports/"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ All tests passed with auth bypass!${NC}"
    echo ""
    echo "Auth bypass successfully:"
    echo "  • Skipped OAuth login flows"
    echo "  • Accessed protected routes directly"
    echo "  • Maintained session across tests"
    echo "  • API calls authenticated properly"
fi

exit 0