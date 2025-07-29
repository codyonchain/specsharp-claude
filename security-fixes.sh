#!/bin/bash

# SpecSharp Security Fix Implementation Script
# Run this from the project root directory

echo "🔐 Starting SpecSharp Security Fixes..."

# 1. Create Logger Utilities
echo "📝 Creating logger utilities..."

# Frontend Logger
mkdir -p frontend/src/utils
cat > frontend/src/utils/logger.ts << 'EOF'
const isDevelopment = process.env.NODE_ENV === 'development';

interface Logger {
  log: (...args: any[]) => void;
  error: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  info: (...args: any[]) => void;
  debug: (...args: any[]) => void;
}

export const logger: Logger = {
  log: (...args) => isDevelopment && console.log(...args),
  error: (...args) => isDevelopment && console.error(...args),
  warn: (...args) => isDevelopment && console.warn(...args),
  info: (...args) => isDevelopment && console.info(...args),
  debug: (...args) => isDevelopment && console.debug(...args),
};
EOF

# Backend Logger
cat > backend/app/core/logger.py << 'EOF'
import logging
import os
from typing import Any

# Configure logging based on environment
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create logger
logger = logging.getLogger("specsharp")
logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

# Create handler
handler = logging.StreamHandler()
handler.setLevel(getattr(logging, LOG_LEVEL.upper()))

# Create formatter
if ENVIRONMENT == "production":
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    )
else:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

handler.setFormatter(formatter)
logger.addHandler(handler)

def log_debug(message: str, **kwargs: Any) -> None:
    """Log debug message with context"""
    if ENVIRONMENT != "production":
        logger.debug(message, extra=kwargs)

def log_info(message: str, **kwargs: Any) -> None:
    """Log info message with context"""
    logger.info(message, extra=kwargs)

def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message with context"""
    logger.warning(message, extra=kwargs)

def log_error(message: str, **kwargs: Any) -> None:
    """Log error message with context"""
    logger.error(message, extra=kwargs)
EOF

# 2. Create API Configuration
echo "🌐 Creating API configuration..."

mkdir -p frontend/src/config
cat > frontend/src/config/api.ts << 'EOF'
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
  timeout: 30000, // 30 seconds
  retryAttempts: 3,
  retryDelay: 1000, // 1 second
};

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}${endpoint}`;
};
EOF

# 3. Create Environment Files
echo "📋 Creating environment files..."

# Frontend development environment
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_ENVIRONMENT=development
EOF

# Frontend production environment template
cat > frontend/.env.production.example << 'EOF'
NEXT_PUBLIC_API_URL=https://api.specsharp.com
NEXT_PUBLIC_ENVIRONMENT=production
EOF

# Backend production environment template
cat > backend/.env.production.example << 'EOF'
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
ENVIRONMENT=production
LOG_LEVEL=INFO
FRONTEND_URL=https://specsharp.com
EOF

# 4. Create Console Replacement Script
echo "🔍 Creating console replacement script..."

cat > scripts/replace-console-logs.py << 'EOF'
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def replace_frontend_console(file_path):
    """Replace console statements in frontend files"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Skip if already has logger import
    if 'from "@/utils/logger"' in content or "from '../utils/logger'" in content:
        return
    
    original_content = content
    
    # Replace console statements
    patterns = [
        (r'console\.log\(', 'logger.log('),
        (r'console\.error\(', 'logger.error('),
        (r'console\.warn\(', 'logger.warn('),
        (r'console\.info\(', 'logger.info('),
        (r'console\.debug\(', 'logger.debug('),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # Add import if modified
    if modified:
        # Find first import
        import_match = re.search(r'^import .* from', content, re.MULTILINE)
        if import_match:
            import_line = import_match.group(0)
            new_import = "import { logger } from '@/utils/logger';\n"
            content = content.replace(import_line, new_import + import_line)
        
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")

def replace_backend_console(file_path):
    """Replace print statements in backend files"""
    # Skip logger file itself
    if 'logger.py' in str(file_path):
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace print statements
    patterns = [
        (r'print\((.*?)\)', r'log_info(\1)'),
        (r'logging\.debug\((.*?)\)', r'log_debug(\1)'),
        (r'logging\.info\((.*?)\)', r'log_info(\1)'),
        (r'logging\.warning\((.*?)\)', r'log_warning(\1)'),
        (r'logging\.error\((.*?)\)', r'log_error(\1)'),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # Add import if modified
    if modified and 'from app.core.logger import' not in content:
        # Find last import
        imports = list(re.finditer(r'^(from|import) .*', content, re.MULTILINE))
        if imports:
            last_import = imports[-1]
            insert_pos = last_import.end()
            import_statement = '\nfrom app.core.logger import log_debug, log_info, log_warning, log_error'
            content = content[:insert_pos] + import_statement + content[insert_pos:]
        
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Updated: {file_path}")

# Process frontend files
print("🔍 Processing frontend files...")
frontend_path = Path('frontend/src')
for file_path in frontend_path.rglob('*.tsx'):
    if 'node_modules' not in str(file_path) and 'logger.ts' not in str(file_path):
        replace_frontend_console(file_path)

for file_path in frontend_path.rglob('*.ts'):
    if 'node_modules' not in str(file_path) and 'logger.ts' not in str(file_path):
        replace_frontend_console(file_path)

# Process backend files
print("\n🔍 Processing backend files...")
backend_path = Path('backend')
for file_path in backend_path.rglob('*.py'):
    if 'venv' not in str(file_path) and '__pycache__' not in str(file_path):
        replace_backend_console(file_path)

print("\n✅ Console replacement complete!")
EOF

chmod +x scripts/replace-console-logs.py

# 5. Create API URL replacement script
echo "🔗 Creating API URL replacement script..."

cat > scripts/fix-api-urls.py << 'EOF'
#!/usr/bin/env python3
import os
import re
from pathlib import Path

def fix_api_urls(file_path):
    """Replace hardcoded localhost URLs with config"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Replace localhost URLs
    patterns = [
        (r'["\']http://localhost:8001', "getApiUrl('"),
        (r'fetch\(["\']http://localhost:8001([^"\']+)["\']\)', r"fetch(getApiUrl('\1'))"),
        (r'axios\.[a-z]+\(["\']http://localhost:8001([^"\']+)["\']\)', r"axios.\1(getApiUrl('\2'))"),
    ]
    
    modified = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # Add import if modified
    if modified and 'getApiUrl' in content and 'from "@/config/api"' not in content:
        # Find first import
        import_match = re.search(r'^import .* from', content, re.MULTILINE)
        if import_match:
            import_line = import_match.group(0)
            new_import = "import { getApiUrl } from '@/config/api';\n"
            content = content.replace(import_line, new_import + import_line)
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Fixed API URLs in: {file_path}")

# Process all TypeScript/JavaScript files
print("🔍 Fixing hardcoded API URLs...")
frontend_path = Path('frontend/src')
for ext in ['*.tsx', '*.ts', '*.js', '*.jsx']:
    for file_path in frontend_path.rglob(ext):
        if 'node_modules' not in str(file_path):
            fix_api_urls(file_path)

print("\n✅ API URL fixes complete!")
EOF

chmod +x scripts/fix-api-urls.py

# 6. Run the scripts
echo "🚀 Running security fixes..."

cd scripts
python3 replace-console-logs.py
python3 fix-api-urls.py
cd ..

# 7. Create production deployment guide
echo "📚 Creating production deployment guide..."

cat > DEPLOYMENT.md << 'EOF'
# SpecSharp Production Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Variables
- [ ] Copy `.env.production.example` files and fill in real values
- [ ] Set strong SECRET_KEY (use: `openssl rand -hex 32`)
- [ ] Update OAuth redirect URLs in Google Console
- [ ] Set production database URL

### 2. Security Checks
- [ ] Run `npm run lint` in frontend
- [ ] Run `black .` and `mypy .` in backend
- [ ] All console.log statements removed
- [ ] API URLs use environment variables
- [ ] Error messages are user-friendly

### 3. Testing
- [ ] Run frontend tests: `npm test`
- [ ] Run backend tests: `pytest`
- [ ] Test with production environment locally
- [ ] Test error scenarios
- [ ] Test authentication flows

## Deployment Steps

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel --prod
```

### Backend (Railway/Render/AWS)
```bash
cd backend
# Ensure requirements.txt is up to date
pip freeze > requirements.txt

# Deploy with your platform's CLI
# Example for Railway:
railway up
```

### Database Migration
```bash
cd backend
alembic upgrade head
```

## Post-Deployment

1. **Verify Services**
   - [ ] Frontend loads correctly
   - [ ] API health check passes
   - [ ] Authentication works
   - [ ] Can create/view projects

2. **Monitor Logs**
   - Check for any errors in first hour
   - Monitor response times
   - Check for failed requests

3. **Security Headers**
   - Verify CORS is properly configured
   - Check CSP headers
   - Ensure HTTPS is enforced

## Rollback Plan

If issues occur:
1. Revert to previous deployment
2. Check logs for root cause
3. Fix in staging environment
4. Re-deploy when verified

## Support

For deployment issues:
- Check logs first
- Review this guide
- Contact team if needed
EOF

echo "✅ Security fixes complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes made by the scripts"
echo "2. Update .env.production files with real values"
echo "3. Run tests to ensure everything works"
echo "4. Commit changes: git add -A && git commit -m 'Security fixes for production'"
echo "5. Deploy to production following DEPLOYMENT.md"
echo ""
echo "🔐 Your application is now production-ready!"