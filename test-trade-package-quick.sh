#!/bin/bash

echo "Quick Trade Package Test"
echo "======================="

# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test2@example.com&password=password123" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Failed to authenticate"
    exit 1
fi

echo "✓ Authenticated successfully"

# Get first project
PROJECT_ID=$(curl -s -X GET http://localhost:8001/api/v1/scope/projects \
  -H "Authorization: Bearer $TOKEN" | grep -o '"project_id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$PROJECT_ID" ]; then
    echo "No projects found"
    exit 1
fi

echo "✓ Found project: $PROJECT_ID"

# Test preview endpoint
echo "Testing preview endpoint..."
PREVIEW=$(curl -s -X GET "http://localhost:8001/api/v1/trade-package/preview/$PROJECT_ID/electrical" \
  -H "Authorization: Bearer $TOKEN")

if echo "$PREVIEW" | grep -q "success"; then
    echo "✓ Preview endpoint works"
else
    echo "✗ Preview failed: $PREVIEW"
fi

# Test generation endpoint
echo "Testing generation endpoint (may take 10-30 seconds)..."
START=$(date +%s)
RESULT=$(curl -s -X POST "http://localhost:8001/api/v1/trade-package/generate/$PROJECT_ID/electrical" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")
END=$(date +%s)

echo "Request took $((END-START)) seconds"

if echo "$RESULT" | grep -q "success"; then
    echo "✓ Generation successful"
    if echo "$RESULT" | grep -q "pdf"; then
        echo "  ✓ PDF present"
    fi
    if echo "$RESULT" | grep -q "csv"; then
        echo "  ✓ CSV present"
    fi
else
    echo "✗ Generation failed"
    echo "Response: ${RESULT:0:200}..."
fi