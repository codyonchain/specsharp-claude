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
