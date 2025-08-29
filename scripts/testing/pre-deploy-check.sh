#!/bin/bash

echo "🔍 Pre-deployment safety check..."

# Check that test files are NOT in build output
if [ -d "frontend/dist" ]; then
  echo "Checking frontend build for test files..."
  if find frontend/dist -name "*.test.*" -o -name "*.spec.*" | grep -q .; then
    echo "❌ ERROR: Test files found in build output!"
    exit 1
  fi
  echo "✅ Frontend build is clean"
fi

# Check that test directories are NOT in backend deployment
if [ -d "backend/app/tests" ]; then
  echo "❌ ERROR: Test directory found in backend/app!"
  echo "Tests should be in root/tests, not backend/app/tests"
  exit 1
fi

# Check that test files are not in backend app directory
if find backend/app -name "test_*.py" -o -name "*_test.py" | grep -q .; then
  echo "❌ ERROR: Test files found in backend/app directory!"
  echo "Tests should be in root/tests, not backend/app"
  exit 1
fi

# Verify test directory is at root level
if [ ! -d "tests" ]; then
  echo "⚠️  WARNING: No tests directory found at root level"
  echo "Tests should be in root/tests/ directory"
fi

# Check that vitest config doesn't get deployed
if [ -f "frontend/dist/vitest.config.ts" ]; then
  echo "❌ ERROR: Vitest config found in build output!"
  exit 1
fi

# Check that playwright config doesn't get deployed
if [ -f "frontend/dist/playwright.config.ts" ]; then
  echo "❌ ERROR: Playwright config found in build output!"
  exit 1
fi

echo "✅ Build is clean - no test files will be deployed"
echo ""
echo "📊 Test infrastructure location summary:"
echo "  - Tests: ./tests/ (root level)"
echo "  - Frontend app: ./frontend/src/ (no tests here)"
echo "  - Backend app: ./backend/app/ (no tests here)"
echo ""
echo "This ensures test files are never deployed to production."