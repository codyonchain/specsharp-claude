#!/bin/bash
#
# Deploy emergency fix to production
# Run this on the production server to fix the schema issue
#

echo "🚀 SpecSharp Emergency Schema Fix Deployment"
echo "==========================================="
echo "This script will fix the PostgreSQL schema issues"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "app/main.py" ]; then
    echo -e "${RED}❌ Error: Not in backend directory${NC}"
    echo "Please cd to the backend directory first"
    exit 1
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL not set${NC}"
    echo "Please set DATABASE_URL environment variable"
    exit 1
fi

echo -e "${GREEN}✓ Environment checked${NC}"
echo ""

# Step 1: Run emergency fix
echo "Step 1: Running emergency schema fix..."
echo "----------------------------------------"
python emergency_fix_schema.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Emergency fix failed${NC}"
    echo "Please check the error messages above"
    exit 1
fi

echo -e "${GREEN}✓ Emergency fix completed${NC}"
echo ""

# Step 2: Run migration (if exists)
if [ -f "migrations/002_add_all_missing_columns.py" ]; then
    echo "Step 2: Running comprehensive migration..."
    echo "----------------------------------------"
    python migrations/002_add_all_missing_columns.py
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️ Migration had issues (may be OK if columns already exist)${NC}"
    else
        echo -e "${GREEN}✓ Migration completed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Migration file not found, skipping${NC}"
fi

echo ""

# Step 3: Verify the fix
echo "Step 3: Verifying the fix..."
echo "----------------------------------------"
python verify_fix.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Verification failed${NC}"
    echo "The fix may not have been fully applied"
    echo "Please check the verification output above"
    exit 1
fi

echo -e "${GREEN}✓ Verification successful${NC}"
echo ""

# Step 4: Health check
echo "Step 4: Running health check..."
echo "----------------------------------------"
python db_health_check.py

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Health check found issues${NC}"
    echo "Please review the health check output above"
else
    echo -e "${GREEN}✓ Database is healthy${NC}"
fi

echo ""
echo "==========================================="
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo ""
echo "Next steps:"
echo "1. Test by logging into the application"
echo "2. Check that projects are visible"
echo "3. Try creating a new project"
echo "4. Monitor logs for any errors"
echo ""
echo "If issues persist:"
echo "• Check application logs"
echo "• Run: python db_health_check.py"
echo "• Contact support with error details"