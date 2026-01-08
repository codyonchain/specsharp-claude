#!/usr/bin/env python3
"""
Remove ALL misplaced financial_metrics blocks that appear outside BuildingConfig.
These are the ones causing syntax errors.
"""

import re

def remove_misplaced_financial_metrics():
    """Remove all financial_metrics blocks that appear after BuildingConfig closes."""
    
    with open('app/v2/config/master_config.py', 'r') as f:
        lines = f.readlines()
    
    # Track lines to remove
    lines_to_remove = set()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for pattern: },\n<optional whitespace>\n# Financial metrics\nfinancial_metrics={
        if '},' in line and i + 3 < len(lines):
            # Check if next non-empty lines are financial_metrics
            next_line_idx = i + 1
            
            # Skip empty lines
            while next_line_idx < len(lines) and lines[next_line_idx].strip() == '':
                next_line_idx += 1
            
            # Check for # Financial metrics comment
            if next_line_idx < len(lines) and '# Financial metrics' in lines[next_line_idx]:
                comment_line = next_line_idx
                next_line_idx += 1
                
                # Skip more empty lines
                while next_line_idx < len(lines) and lines[next_line_idx].strip() == '':
                    next_line_idx += 1
                
                # Check for financial_metrics={
                if next_line_idx < len(lines) and 'financial_metrics={' in lines[next_line_idx]:
                    print(f"Found misplaced financial_metrics at line {next_line_idx + 1}")
                    
                    # Mark all lines of this block for removal
                    # Remove from comment to closing },
                    lines_to_remove.add(comment_line)
                    
                    # Find the end of this block
                    bracket_count = 0
                    j = next_line_idx
                    while j < len(lines):
                        lines_to_remove.add(j)
                        if '{' in lines[j]:
                            bracket_count += 1
                        if '}' in lines[j]:
                            bracket_count -= 1
                            if bracket_count == 0:
                                # Found the closing bracket
                                # Also remove trailing comma if on next line
                                if j + 1 < len(lines) and lines[j + 1].strip() == ',':
                                    lines_to_remove.add(j + 1)
                                break
                        j += 1
                    
                    i = j + 1
                    continue
        
        i += 1
    
    # Create new file without the removed lines
    new_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            new_lines.append(line)
    
    print(f"Removing {len(lines_to_remove)} lines total")
    
    # Write back
    with open('app/v2/config/master_config.py', 'w') as f:
        f.writelines(new_lines)
    
    return len(lines_to_remove) > 0

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

def count_financial_metrics():
    """Count how many subtypes have financial_metrics properly configured."""
    with open('app/v2/config/master_config.py', 'r') as f:
        content = f.read()
    
    # Count subtypes with financial_metrics inside their BuildingConfig
    import re
    
    # Pattern to find subtype with financial_metrics
    pattern = r"'(\w+)':\s*BuildingConfig\([^)]*financial_metrics=\{"
    matches = re.findall(pattern, content, re.DOTALL)
    
    print(f"Found {len(matches)} subtypes with financial_metrics properly configured")
    if matches:
        print("Configured subtypes:", ', '.join(sorted(set(matches))))
    
    return len(matches)

if __name__ == '__main__':
    print("Fixing misplaced financial_metrics blocks...")
    
    # First check current state
    print("\nInitial syntax check:")
    has_errors = not verify_syntax()
    
    if has_errors:
        # Remove misplaced blocks
        if remove_misplaced_financial_metrics():
            print("\nPost-fix syntax check:")
            if verify_syntax():
                print("\n✅ SUCCESS: All syntax errors fixed!")
                print("\nCounting properly configured financial_metrics:")
                count_financial_metrics()
            else:
                print("\n❌ Still has syntax errors")
    else:
        print("No syntax errors found")
        print("\nCounting properly configured financial_metrics:")
        count_financial_metrics()