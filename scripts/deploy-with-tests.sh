#!/bin/bash

echo "🚀 SpecSharp Deployment Pipeline"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Track deployment readiness
READY_TO_DEPLOY=true

echo ""
echo -e "${BLUE}Step 1: Running Complete Test Suite${NC}"
echo "--------------------------------------"
bash scripts/testing/run-all-tests.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Tests failed - deployment aborted${NC}"
    READY_TO_DEPLOY=false
fi

echo ""
echo -e "${BLUE}Step 2: Generating Test Report${NC}"
echo "-------------------------------"
node scripts/testing/final-report.js
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Test report indicates issues${NC}"
    READY_TO_DEPLOY=false
fi

echo ""
echo -e "${BLUE}Step 3: Build Verification${NC}"
echo "--------------------------"

# Check for test mode code in production
echo "Checking for test mode code..."
grep -r "TESTING.*true" backend/app --include="*.py" | grep -v "test_" > /tmp/test-mode-check.txt
if [ -s /tmp/test-mode-check.txt ]; then
    echo -e "${RED}❌ Found test mode code in production:${NC}"
    cat /tmp/test-mode-check.txt
    READY_TO_DEPLOY=false
else
    echo -e "${GREEN}✅ No test mode code found${NC}"
fi

# Check for auth bypass
echo "Checking for auth bypass..."
grep -r "AUTH_BYPASS_ENABLED" backend/app --include="*.py" > /tmp/auth-bypass-check.txt
if [ -s /tmp/auth-bypass-check.txt ]; then
    echo -e "${YELLOW}⚠️  Auth bypass code found - ensure it's disabled in production${NC}"
    head -3 /tmp/auth-bypass-check.txt
fi

# Build frontend
echo ""
echo -e "${BLUE}Step 4: Building Frontend${NC}"
echo "------------------------"
cd frontend

# Check if build script exists
if [ -f "package.json" ] && grep -q "build" package.json; then
    npm run build
    
    # Check build size
    if [ -d "dist" ] || [ -d "build" ]; then
        BUILD_DIR=$([ -d "dist" ] && echo "dist" || echo "build")
        BUILD_SIZE=$(du -sh $BUILD_DIR | cut -f1)
        echo -e "${GREEN}✅ Frontend built successfully (Size: $BUILD_SIZE)${NC}"
        
        # Check for console.log in production build
        echo "Checking for console.log in build..."
        grep -r "console.log" $BUILD_DIR --include="*.js" | head -5 > /tmp/console-check.txt
        if [ -s /tmp/console-check.txt ]; then
            echo -e "${YELLOW}⚠️  Found console.log in production build${NC}"
        fi
    else
        echo -e "${RED}❌ Build directory not found${NC}"
        READY_TO_DEPLOY=false
    fi
else
    echo -e "${YELLOW}⚠️  No build script found${NC}"
fi

cd "$PROJECT_ROOT"

echo ""
echo -e "${BLUE}Step 5: Environment Check${NC}"
echo "------------------------"

# Check critical environment variables
echo "Checking environment configuration..."

if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${RED}❌ ENVIRONMENT is already set to production!${NC}"
    echo "   Ensure you're not running this in production"
fi

if [ "$TESTING" = "true" ]; then
    echo -e "${RED}❌ TESTING is set to true!${NC}"
    echo "   This must be false for production"
    READY_TO_DEPLOY=false
fi

echo ""
echo "================================"
echo -e "${CYAN}📋 DEPLOYMENT CHECKLIST${NC}"
echo "================================"

# Show checklist summary
checklist_items=(
    "All tests passing"
    "No test code in production"
    "Frontend builds successfully"
    "Auth bypass disabled"
    "Environment variables ready"
    "Database backup completed"
    "Monitoring configured"
    "Rollback plan ready"
)

for item in "${checklist_items[@]}"; do
    echo "⬜ $item"
done

echo ""
echo "================================"
echo -e "${CYAN}🚀 DEPLOYMENT DECISION${NC}"
echo "================================"

if [ "$READY_TO_DEPLOY" = true ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - READY TO DEPLOY!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the deployment checklist above"
    echo "2. Set production environment variables:"
    echo "   export ENVIRONMENT=production"
    echo "   export TESTING=false"
    echo "3. Run deployment command:"
    echo "   npm run deploy:production"
    echo "4. Run production smoke tests:"
    echo "   PROD_URL=https://specsharp.com npm run test:production"
    echo ""
    echo -e "${GREEN}Good luck with your deployment! 🚀${NC}"
    exit 0
else
    echo -e "${RED}❌ DEPLOYMENT BLOCKED - ISSUES DETECTED${NC}"
    echo ""
    echo "Please resolve the issues above before deploying:"
    echo "1. Fix any failing tests"
    echo "2. Remove test code from production"
    echo "3. Ensure auth bypass is disabled"
    echo "4. Review the test report:"
    echo "   cat tests/reports/final-report.md"
    echo ""
    echo -e "${YELLOW}⚠️  Do not deploy until all issues are resolved${NC}"
    exit 1
fi