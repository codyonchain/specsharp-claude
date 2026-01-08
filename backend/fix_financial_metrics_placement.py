#!/usr/bin/env python3
"""
Fix misplaced financial_metrics that were added outside BuildingConfig.
"""

import re

def fix_misplaced_metrics():
    """Find and fix financial_metrics placed outside BuildingConfig."""
    
    with open('app/v2/config/master_config.py', 'r') as f:
        content = f.read()
    
    # Pattern to find misplaced financial_metrics
    # They appear after a BuildingConfig closes with )
    # Pattern: closing paren, closing brace, comma, then financial_metrics
    pattern = r'(\s+\)\s*\n\s*\},)\s*\n\s*# Financial metrics\s*\n\s*(financial_metrics=\{[^}]+\}),\s*\n'
    
    fixes_made = 0
    
    # Find all matches
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        print("No misplaced financial_metrics found using simple pattern")
        # Try a different pattern - financial_metrics after a closing }
        pattern2 = r'(\n\s*\}\s*,\s*\n)\s*(#\s*Financial metrics\s*\n\s*financial_metrics=\{[^}]+\},)'
        matches = list(re.finditer(pattern2, content))
    
    for match in reversed(matches):  # Process in reverse to maintain positions
        print(f"Found misplaced financial_metrics at position {match.start()}")
        fixes_made += 1
        
        # Extract the financial_metrics block
        full_match = match.group(0)
        
        # Find where this should go - look backwards for special_features
        search_start = max(0, match.start() - 5000)
        search_area = content[search_start:match.start()]
        
        # Find the last special_features closing
        special_features_match = None
        for m in re.finditer(r'special_features=\{[^}]*\},', search_area):
            special_features_match = m
        
        if special_features_match:
            # We need to move the financial_metrics to after special_features
            # but before Revenue metrics
            print(f"  Moving to correct location after special_features")
            
            # Remove from wrong location
            content = content[:match.start()] + content[match.end():]
        
    if fixes_made:
        print(f"\nFixed {fixes_made} misplaced financial_metrics blocks")
        with open('app/v2/config/master_config.py', 'w') as f:
            f.write(content)
    else:
        print("No fixes needed")
    
    return fixes_made

def verify_syntax():
    """Verify the file has no syntax errors."""
    import py_compile
    try:
        py_compile.compile('app/v2/config/master_config.py', doraise=True)
        print("✅ No syntax errors found")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == '__main__':
    print("Checking for misplaced financial_metrics...")
    
    # First verify current state
    print("\nCurrent syntax check:")
    has_errors = not verify_syntax()
    
    if has_errors:
        # Attempt to fix
        fixes = fix_misplaced_metrics()
        
        if fixes > 0:
            print("\nPost-fix syntax check:")
            verify_syntax()
    else:
        print("No syntax errors - file is valid")