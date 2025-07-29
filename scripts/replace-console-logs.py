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
