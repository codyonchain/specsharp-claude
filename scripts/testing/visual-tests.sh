#!/bin/bash

echo "📸 Running Visual Regression & Accessibility Tests"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_ROOT"

# Set testing environment
export TESTING=true
export NODE_ENV=test

# Function to check if services are running
check_services() {
    curl -s http://localhost:3000 > /dev/null 2>&1
    FRONTEND_STATUS=$?
    
    curl -s http://localhost:8001/health > /dev/null 2>&1
    BACKEND_STATUS=$?
    
    if [ $FRONTEND_STATUS -ne 0 ] || [ $BACKEND_STATUS -ne 0 ]; then
        echo -e "${YELLOW}⚠ Services not running. Start them with:${NC}"
        echo "  ./start-all.sh"
        echo "  or"
        echo "  TESTING=true ./start-backend.sh &"
        echo "  REACT_APP_TESTING=true ./start-frontend.sh &"
        return 1
    fi
    return 0
}

# Check if services are running
if ! check_services; then
    echo -e "${RED}✗ Please start services before running visual tests${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Services are running${NC}"
echo ""

# Handle update mode
if [ "$1" == "update" ] || [ "$1" == "--update-snapshots" ]; then
    echo -e "${YELLOW}📸 UPDATING BASELINE SCREENSHOTS${NC}"
    echo "================================="
    echo "This will replace all existing baseline images."
    echo ""
    
    TESTING=true npx playwright test tests/e2e/visual/ --update-snapshots
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Baseline screenshots updated successfully${NC}"
        echo ""
        echo "New baselines saved to:"
        echo "  tests/e2e/visual/**/*.png"
    else
        echo -e "${RED}✗ Failed to update baseline screenshots${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}📸 VISUAL REGRESSION TESTING${NC}"
    echo "=============================="
    echo "Comparing against baseline screenshots..."
    echo ""
    
    TESTING=true npx playwright test tests/e2e/visual/
    VISUAL_EXIT=$?
    
    if [ $VISUAL_EXIT -eq 0 ]; then
        echo -e "${GREEN}✓ Visual regression tests passed${NC}"
    else
        echo -e "${RED}✗ Visual differences detected${NC}"
        echo ""
        echo "To update baselines, run:"
        echo "  bash scripts/testing/visual-tests.sh update"
        echo ""
        echo "To view diff report:"
        echo "  npx playwright show-report tests/reports/playwright-html"
    fi
fi

echo ""
echo -e "${BLUE}♿ ACCESSIBILITY TESTING${NC}"
echo "========================"
echo "Running WCAG 2.0 AA compliance tests..."
echo ""

TESTING=true npx playwright test tests/e2e/accessibility/
A11Y_EXIT=$?

if [ $A11Y_EXIT -eq 0 ]; then
    echo -e "${GREEN}✓ Accessibility tests passed${NC}"
else
    echo -e "${YELLOW}⚠ Accessibility issues found${NC}"
    echo ""
    echo "Common fixes:"
    echo "  • Add alt text to images"
    echo "  • Ensure proper color contrast (4.5:1 for normal text)"
    echo "  • Add labels to form inputs"
    echo "  • Ensure keyboard navigation works"
fi

echo ""
echo "================================="
echo -e "${BLUE}📊 TEST SUMMARY${NC}"
echo "================================="

# Calculate results
TOTAL_TESTS=2
PASSED_TESTS=0
FAILED_TESTS=0

if [ ${VISUAL_EXIT:-0} -eq 0 ]; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "Visual Regression: ${GREEN}PASSED${NC}"
else
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "Visual Regression: ${RED}FAILED${NC}"
fi

if [ ${A11Y_EXIT:-0} -eq 0 ]; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "Accessibility:     ${GREEN}PASSED${NC}"
else
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "Accessibility:     ${YELLOW}WARNINGS${NC}"
fi

echo ""
echo "Total: $PASSED_TESTS passed, $FAILED_TESTS with issues"

# Overall exit code
if [ $FAILED_TESTS -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠ Some tests need attention${NC}"
    
    # Don't fail CI for accessibility warnings
    if [ ${A11Y_EXIT:-0} -ne 0 ] && [ ${VISUAL_EXIT:-0} -eq 0 ]; then
        echo "Accessibility warnings don't block deployment"
        exit 0
    else
        exit 1
    fi
else
    echo ""
    echo -e "${GREEN}✅ All visual and accessibility tests passed!${NC}"
    exit 0
fi