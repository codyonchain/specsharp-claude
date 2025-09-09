#!/bin/bash

echo "======================================"
echo "OWNER VIEW ENDPOINT TEST"
echo "======================================"
echo ""

# Get a project ID
PROJECT_ID=$(curl -s http://localhost:8001/api/v2/scope/projects | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data and len(data) > 0:
    # Find a healthcare project for better revenue data
    for p in data:
        if p.get('building_type') == 'healthcare':
            print(p.get('project_id'))
            break
    else:
        print(data[0].get('project_id', ''))
" 2>/dev/null)

if [ -z "$PROJECT_ID" ]; then
    echo "No projects found. Creating a test project..."
    PROJECT_ID=$(curl -s -X POST http://localhost:8001/api/v2/scope/generate \
        -H "Content-Type: application/json" \
        -d '{"description": "4200 sf restaurant in Nashville"}' | python3 -c "
        import sys, json
        data = json.load(sys.stdin)
        print(data.get('data', {}).get('project_id', ''))
    ")
fi

echo "Testing with Project ID: $PROJECT_ID"
echo ""

# Test the owner-view endpoint
echo "Testing POST /api/v2/scope/owner-view:"
echo "--------------------------------------"
curl -s -X POST http://localhost:8001/api/v2/scope/owner-view \
    -H "Content-Type: application/json" \
    -d "{\"project_id\": \"$PROJECT_ID\"}" | python3 -c "
import sys, json

data = json.load(sys.stdin)
if not data.get('success'):
    print('❌ Request failed:', data.get('errors', data.get('error')))
    sys.exit(1)

owner_data = data.get('data', {})
print('✅ Owner View Data Retrieved Successfully!')
print()

# Project Summary
summary = owner_data.get('project_summary', {})
print('PROJECT SUMMARY:')
print(f'  Name: {owner_data.get(\"project_name\", \"N/A\")}')
print(f'  Total Cost: \${summary.get(\"total_project_cost\", 0):,.2f}')
print(f'  Construction Cost: \${summary.get(\"construction_cost\", 0):,.2f}')
print(f'  Cost/SF: \${summary.get(\"total_cost_per_sqft\", 0):,.2f}')
print(f'  Square Footage: {summary.get(\"square_footage\", 0):,.0f} SF')
print()

# Revenue Analysis
revenue = owner_data.get('revenue_analysis', {})
print('REVENUE ANALYSIS:')
print(f'  Annual Revenue: \${revenue.get(\"annual_revenue\", 0):,.2f}')
print(f'  Operating Margin: {revenue.get(\"operating_margin\", 0)*100:.1f}%')
print(f'  Net Income (NOI): \${revenue.get(\"net_income\", 0):,.2f}')
print(f'  Estimated NOI: \${revenue.get(\"estimated_annual_noi\", 0):,.2f}')
print()

# Ownership Analysis
ownership = owner_data.get('ownership_analysis', {})
if ownership:
    print('OWNERSHIP ANALYSIS:')
    
    # Financing
    financing = ownership.get('financing_sources', {})
    if financing:
        print('  Financing Sources:')
        print(f'    Debt: \${financing.get(\"debt_amount\", 0):,.2f}')
        print(f'    Equity: \${financing.get(\"equity_amount\", 0):,.2f}')
    
    # Debt Metrics
    debt = ownership.get('debt_metrics', {})
    if debt:
        print('  Debt Metrics:')
        print(f'    Annual Debt Service: \${debt.get(\"annual_debt_service\", 0):,.2f}')
        print(f'    DSCR: {debt.get(\"calculated_dscr\", 0):.2f}')
    
    # Return Metrics
    returns = ownership.get('return_metrics', {})
    if returns:
        print('  Return Metrics:')
        print(f'    NOI: \${returns.get(\"estimated_annual_noi\", 0):,.2f}')
        print(f'    Cash-on-Cash Return: {returns.get(\"cash_on_cash_return\", 0)*100:.1f}%')
        print(f'    Target ROI: {returns.get(\"target_roi\", 0)*100:.1f}%')
else:
    print('⚠️  No ownership analysis data available')

print()
print('======================================')
print('TEST COMPLETE')
print('======================================')
"

echo ""
echo "Testing URL parameter version:"
echo "-------------------------------"
curl -s -X POST "http://localhost:8001/api/v2/scope/projects/$PROJECT_ID/owner-view" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        print('✅ URL parameter version works!')
        revenue = data.get('data', {}).get('revenue_analysis', {})
        print(f'   Annual Revenue: \${revenue.get(\"annual_revenue\", 0):,.2f}')
    else:
        print('❌ URL parameter version failed:', data.get('errors'))
except Exception as e:
    print('❌ Error:', e)
"