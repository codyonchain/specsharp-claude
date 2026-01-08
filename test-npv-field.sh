#!/bin/bash

echo "Testing NPV field in owner-view endpoint..."

# Get an existing project ID
PROJECT_ID=$(psql $DATABASE_URL -t -c "SELECT project_id FROM projects LIMIT 1;" 2>/dev/null || sqlite3 backend/specsharp.db "SELECT project_id FROM projects LIMIT 1;" 2>/dev/null | tr -d ' ')

if [ -z "$PROJECT_ID" ]; then
    echo "No projects found in database"
    exit 1
fi

echo "Using project ID: $PROJECT_ID"

# Call the owner-view endpoint
echo "Calling owner-view endpoint..."
RESPONSE=$(curl -s -X POST http://localhost:8001/api/v2/scope/owner-view \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": \"$PROJECT_ID\"}")

echo "Full response:"
echo "$RESPONSE" | python -m json.tool 2>/dev/null || echo "$RESPONSE"

echo ""
echo "Checking for NPV field in response..."
echo "$RESPONSE" | python -c "
import json
import sys
data = json.load(sys.stdin)
if 'data' in data:
    owner_data = data['data']
    # Check ownership_analysis.return_metrics.npv
    if 'ownership_analysis' in owner_data:
        if 'return_metrics' in owner_data['ownership_analysis']:
            metrics = owner_data['ownership_analysis']['return_metrics']
            print(f'Found NPV: {metrics.get(\"npv\", \"NOT FOUND\")}')
            print(f'Found IRR: {metrics.get(\"irr\", \"NOT FOUND\")}')
            print(f'Found ten_year_npv (old field): {metrics.get(\"ten_year_npv\", \"NOT FOUND\")}')
        else:
            print('No return_metrics in ownership_analysis')
    else:
        print('No ownership_analysis in response')
else:
    print('No data field in response')
"