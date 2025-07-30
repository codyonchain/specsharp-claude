#!/bin/bash

echo "Testing trade package generation..."
echo "================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "\n${YELLOW}1. Checking if backend is running...${NC}"
if curl -s http://localhost:8001/docs > /dev/null; then
    echo -e "${GREEN}✓ Backend is running on port 8001${NC}"
else
    echo -e "${RED}✗ Backend is not running on port 8001${NC}"
    echo "Please start the backend with: ./start-backend.sh"
    exit 1
fi

# Check if frontend is running
echo -e "\n${YELLOW}2. Checking if frontend is running...${NC}"
if curl -s http://localhost:5173 > /dev/null || curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✓ Frontend is running${NC}"
else
    echo -e "${RED}✗ Frontend is not running${NC}"
    echo "Please start the frontend with: ./start-frontend.sh"
fi

# Test authentication endpoint
echo -e "\n${YELLOW}3. Testing authentication...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8001/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test2@example.com&password=password123")

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Authentication successful${NC}"
    TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "Token obtained: ${TOKEN:0:20}..."
else
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

# Get a project ID
echo -e "\n${YELLOW}4. Getting project list...${NC}"
PROJECTS_RESPONSE=$(curl -s -X GET http://localhost:8001/api/v1/scope/projects \
  -H "Authorization: Bearer $TOKEN")

if echo "$PROJECTS_RESPONSE" | grep -q "project_id"; then
    echo -e "${GREEN}✓ Projects retrieved successfully${NC}"
    PROJECT_ID=$(echo "$PROJECTS_RESPONSE" | grep -o '"project_id":"[^"]*' | head -1 | cut -d'"' -f4)
    echo "Using project ID: $PROJECT_ID"
else
    echo -e "${RED}✗ Failed to get projects${NC}"
    echo "Response: $PROJECTS_RESPONSE"
    exit 1
fi

# Test trade package preview endpoint
echo -e "\n${YELLOW}5. Testing trade package preview endpoint...${NC}"
PREVIEW_RESPONSE=$(curl -s -X GET "http://localhost:8001/api/v1/trade-package/preview/$PROJECT_ID/electrical" \
  -H "Authorization: Bearer $TOKEN")

if echo "$PREVIEW_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Preview endpoint working${NC}"
else
    echo -e "${RED}✗ Preview endpoint failed${NC}"
    echo "Response: $PREVIEW_RESPONSE"
fi

# Test trade package generation endpoint
echo -e "\n${YELLOW}6. Testing trade package generation endpoint...${NC}"
echo "This may take up to 30 seconds..."

START_TIME=$(date +%s)
GENERATE_RESPONSE=$(curl -s -X POST "http://localhost:8001/api/v1/trade-package/generate/$PROJECT_ID/electrical" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
END_TIME=$(date +%s)

DURATION=$((END_TIME - START_TIME))
echo "Request took $DURATION seconds"

if echo "$GENERATE_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✓ Trade package generation successful${NC}"
    
    # Check if response contains expected fields
    if echo "$GENERATE_RESPONSE" | grep -q "pdf"; then
        echo -e "${GREEN}  ✓ PDF data present${NC}"
    else
        echo -e "${RED}  ✗ PDF data missing${NC}"
    fi
    
    if echo "$GENERATE_RESPONSE" | grep -q "csv"; then
        echo -e "${GREEN}  ✓ CSV data present${NC}"
    else
        echo -e "${RED}  ✗ CSV data missing${NC}"
    fi
    
    if echo "$GENERATE_RESPONSE" | grep -q "schematic"; then
        echo -e "${GREEN}  ✓ Schematic data present${NC}"
    else
        echo -e "${RED}  ✗ Schematic data missing${NC}"
    fi
else
    echo -e "${RED}✗ Trade package generation failed${NC}"
    echo "Response: ${GENERATE_RESPONSE:0:500}..."
fi

echo -e "\n${YELLOW}Test complete!${NC}"