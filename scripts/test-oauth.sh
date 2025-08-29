#!/bin/bash

echo "🔐 Testing Google OAuth Locally"
echo "================================"
echo ""

# Check if credentials are configured
if grep -q "your-actual-client-id" .env.oauth-test 2>/dev/null; then
    echo "❌ Please add your Google OAuth credentials to .env.oauth-test"
    echo ""
    echo "   1. Go to: https://console.cloud.google.com/apis/credentials"
    echo "   2. Create OAuth 2.0 Client ID (Web application)"
    echo "   3. Add authorized redirect URIs:"
    echo "      - http://localhost:8001/api/v1/oauth/callback/google"
    echo "   4. Copy Client ID and Client Secret to .env.oauth-test"
    echo ""
    exit 1
else
    echo "✅ OAuth credentials appear to be configured"
fi

# Backup current env
if [ -f .env ]; then
    cp .env .env.backup
    echo "✅ Backed up current .env to .env.backup"
fi

# Use OAuth test config
cp .env.oauth-test .env
echo "✅ Using OAuth test configuration"

# Log OAuth configuration status
echo ""
echo "Testing OAuth configuration..."
cd backend 2>/dev/null || true
python3 -c "
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')
from app.core.oauth_config import OAuthConfig
OAuthConfig.log_oauth_status()
" 2>&1 | tail -20

echo ""
echo "Starting backend server with OAuth enabled..."
echo "=============================================="
echo ""

# Kill any existing backend process on port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Start backend with OAuth
cd backend 2>/dev/null || cd .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo ""

# Wait for backend to start
sleep 5

# Test OAuth endpoint
echo "Testing OAuth endpoint..."
echo "========================="
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" http://localhost:8001/api/v1/oauth/login/google)
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "307" ] || [ "$HTTP_STATUS" = "302" ]; then
    echo "✅ OAuth endpoint returned redirect (status $HTTP_STATUS)"
    echo "   This means OAuth is working!"
elif [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ OAuth endpoint returned success"
    echo "Response:"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
else
    echo "❌ OAuth endpoint returned unexpected status: $HTTP_STATUS"
    echo "Response:"
    echo "$BODY"
fi

echo ""
echo "📝 Next Steps:"
echo "=============="
echo "1. Visit http://localhost:3000 in your browser"
echo "2. Click 'Sign in with Google'"
echo "3. Complete OAuth flow with your Google account"
echo "4. Verify you're logged in successfully"
echo ""
echo "To test auth bypass mode instead:"
echo "  1. Press Ctrl+C to stop"
echo "  2. Run: ENVIRONMENT=development TESTING=true ./start-backend.sh"
echo ""
echo "Press Ctrl+C to stop the server..."
echo ""

# Trap Ctrl+C to clean up
trap "echo 'Stopping...'; kill $BACKEND_PID 2>/dev/null; exit" INT

# Wait for backend process
wait $BACKEND_PID