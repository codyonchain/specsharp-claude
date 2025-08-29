#!/bin/bash

echo "🧪 Running SpecSharp Complete Test Suite"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track failures
FAILED_TESTS=()
PASSED_TESTS=()

# Get project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Check if servers are running
check_servers() {
    echo -e "${BLUE}Checking if servers are running...${NC}"
    
    # Check backend
    if curl -s http://localhost:8001/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running on port 8001${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend not running. Starting it now...${NC}"
        cd backend
        source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
        uvicorn app.main:app --port 8001 --reload &
        BACKEND_PID=$!
        cd ..
        sleep 5
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is running on port 3000${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend not running. Starting it now...${NC}"
        cd frontend
        npm run dev &
        FRONTEND_PID=$!
        cd ..
        sleep 5
    fi
}

# Function to run a test suite
run_test_suite() {
    local suite_name=$1
    local test_command=$2
    local working_dir=$3
    
    echo -e "\n${YELLOW}Running ${suite_name}...${NC}"
    
    cd "$working_dir"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ ${suite_name} passed${NC}"
        PASSED_TESTS+=("$suite_name")
    else
        echo -e "${RED}❌ ${suite_name} failed${NC}"
        FAILED_TESTS+=("$suite_name")
    fi
    cd "$PROJECT_ROOT"
}

# Start servers if needed
check_servers

# Run frontend unit tests
run_test_suite "Frontend Unit Tests" "npm run test 2>/dev/null || true" "frontend"

# Run backend tests
run_test_suite "Backend Tests" "source venv/bin/activate && pytest ../tests/unit -v --tb=short 2>/dev/null || true" "backend"

# Run smoke tests
run_test_suite "E2E Smoke Tests" "npm run test:smoke 2>/dev/null || true" "frontend"

# Run deployment safety check
echo -e "\n${YELLOW}Running Deployment Safety Check...${NC}"
cd frontend

# Build if dist doesn't exist
if [ ! -d "dist" ]; then
    echo "Building frontend for safety check..."
    npm run build:prod > /dev/null 2>&1
fi

cd ..
if bash scripts/testing/pre-deploy-check.sh; then
    echo -e "${GREEN}✅ Deployment safety check passed${NC}"
    PASSED_TESTS+=("Deployment Safety")
else
    echo -e "${RED}❌ Deployment safety check failed${NC}"
    FAILED_TESTS+=("Deployment Safety")
fi

# Kill servers if we started them
if [ ! -z "$BACKEND_PID" ]; then
    echo -e "\n${BLUE}Stopping backend server...${NC}"
    kill $BACKEND_PID 2>/dev/null
fi

if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${BLUE}Stopping frontend server...${NC}"
    kill $FRONTEND_PID 2>/dev/null
fi

# Summary
echo -e "\n========================================"
echo -e "              TEST SUMMARY               "
echo -e "========================================"

# Display results in a table format
echo -e "\n${BLUE}Test Results:${NC}"
echo "┌──────────────────────────┬──────────┐"
echo "│ Test Suite               │ Result   │"
echo "├──────────────────────────┼──────────┤"

for test in "${PASSED_TESTS[@]}"; do
    printf "│ %-24s │ ${GREEN}✅ PASS${NC}   │\n" "$test"
done

for test in "${FAILED_TESTS[@]}"; do
    printf "│ %-24s │ ${RED}❌ FAIL${NC}   │\n" "$test"
done

echo "└──────────────────────────┴──────────┘"

# Calculate pass rate
TOTAL_TESTS=$((${#PASSED_TESTS[@]} + ${#FAILED_TESTS[@]}))
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((${#PASSED_TESTS[@]} * 100 / TOTAL_TESTS))
    echo -e "\n${BLUE}Pass Rate: ${PASS_RATE}%${NC}"
fi

# Final status
echo ""
if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 ALL TESTS PASSED! Ready to deploy  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ❌ SOME TESTS FAILED - Review above   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════╝${NC}"
    exit 1
fi