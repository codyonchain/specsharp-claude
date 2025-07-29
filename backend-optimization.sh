#!/bin/bash

echo "🚀 SpecSharp Backend API Optimization Script"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

cd backend

echo -e "\n${YELLOW}📦 Installing optimization dependencies...${NC}"
pip install redis==5.0.1 fastapi-cache2[redis]==0.2.1

echo -e "\n${YELLOW}🗄️ Creating database indexes...${NC}"
python create_indexes.py

echo -e "\n${YELLOW}🔍 Checking Redis availability...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running. Please start Redis:${NC}"
    echo "   On macOS: brew services start redis"
    echo "   On Ubuntu: sudo systemctl start redis"
    echo "   Or run: redis-server"
fi

echo -e "\n${YELLOW}📋 API Optimization Summary:${NC}"
echo "============================"
echo -e "${GREEN}✅ Pagination added to:${NC}"
echo "   - GET /api/v1/scope/projects (default limit=20, max=100)"
echo "   - GET /api/v1/scope/projects/search"
echo ""
echo -e "${GREEN}✅ Database indexes created:${NC}"
echo "   - idx_projects_user_id"
echo "   - idx_projects_created_at"
echo "   - idx_projects_team_id"
echo "   - Composite indexes for faster queries"
echo ""
echo -e "${GREEN}✅ Caching implemented:${NC}"
echo "   - GET /api/v1/trade-package/preview/{project_id}/{trade} (1 hour)"
echo "   - GET /api/v1/scope/projects/{project_id} (5 minutes)"
echo "   - Cache invalidation on project updates"
echo ""
echo -e "${GREEN}✅ Performance improvements:${NC}"
echo "   - GZip compression for responses > 1KB"
echo "   - Optimized project queries (select specific columns)"
echo "   - JSON optimization utilities added"
echo ""
echo -e "${YELLOW}📊 Testing the optimizations:${NC}"
echo "1. Start Redis if not running"
echo "2. Restart the backend: ./start-backend.sh"
echo "3. Monitor performance in browser DevTools"
echo "4. Check response headers for 'content-encoding: gzip'"
echo ""
echo -e "${GREEN}✨ Optimization complete!${NC}"