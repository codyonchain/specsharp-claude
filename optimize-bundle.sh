#!/bin/bash

echo "🚀 SpecSharp Bundle Optimization Script"
echo "======================================"

cd frontend

# Install dependencies if needed
echo "📦 Installing dependencies..."
npm install

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist

# Build the project
echo "🔨 Building production bundle..."
npm run build

# Analyze bundle size
echo ""
echo "📊 Bundle Analysis:"
echo "==================="

if [ -d "dist/assets" ]; then
    echo "JavaScript bundles:"
    ls -lh dist/assets/*.js | awk '{print $9 ": " $5}'
    
    echo ""
    echo "CSS bundles:"
    ls -lh dist/assets/*.css 2>/dev/null | awk '{print $9 ": " $5}' || echo "No separate CSS files found"
    
    echo ""
    echo "Total bundle size:"
    du -sh dist/assets
    
    echo ""
    echo "Largest files:"
    find dist -type f -exec ls -lh {} \; | sort -k5 -hr | head -10
else
    echo "❌ Build failed or dist/assets not found"
fi

echo ""
echo "✅ Optimization complete!"
echo ""
echo "💡 Next steps:"
echo "1. Review the bundle sizes above"
echo "2. Run 'npm run preview' to test the production build"
echo "3. Check browser DevTools Network tab for actual load times"
echo "4. Consider further optimizations if bundles > 500KB"