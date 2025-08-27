#!/bin/bash

echo "🚀 Migrating to V2..."
echo ""

# Backup current main.tsx
cp src/main.tsx src/main-v1-backup.tsx

# Use V2 as main
cp src/main-v2.tsx src/main.tsx

echo "✅ Migration complete!"
echo ""
echo "To run V2:"
echo "  npm run dev"
echo ""
echo "To rollback to V1:"
echo "  cp src/main-v1-backup.tsx src/main.tsx"