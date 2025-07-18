#!/bin/bash

echo "Testing SpecSharp Services..."
echo "=============================="

# Test Backend
echo -n "Backend API (http://localhost:8001): "
if curl -s http://localhost:8001/ | grep -q "SpecSharp"; then
    echo "✓ Running"
else
    echo "✗ Not responding"
fi

# Test Backend Docs
echo -n "API Documentation (http://localhost:8001/docs): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs | grep -q "200"; then
    echo "✓ Available"
else
    echo "✗ Not available"
fi

# Test Frontend
echo -n "Frontend (http://localhost:3000): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✓ Running"
else
    echo "✗ Not responding"
fi

echo ""
echo "To access SpecSharp:"
echo "1. Open your browser to http://localhost:3000"
echo "2. Register a new account"
echo "3. Start creating construction scopes!"