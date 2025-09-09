#!/usr/bin/env python3
"""
Remove misplaced financial_metrics that were added outside BuildingConfig.
They were already properly added inside BuildingConfig, so these are duplicates.
"""

def cleanup_misplaced_metrics():
    """Remove financial_metrics blocks that appear outside BuildingConfig."""
    
    with open('app/v2/config/master_config.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a misplaced financial_metrics
        if i > 0 and 'financial_metrics={' in line:
            # Check if previous lines show we're outside a BuildingConfig
            # Look for pattern: ) then }, then financial_metrics
            is_misplaced = False
            
            # Check backwards for closing BuildingConfig
            for j in range(max(0, i-3), i):
                if ')' in lines[j]:
                    # Found closing paren, check if followed by },
                    for k in range(j+1, min(j+3, i)):
                        if '},' in lines[k]:
                            is_misplaced = True
                            break
                    if is_misplaced:
                        break
            
            if is_misplaced:
                print(f"Removing misplaced financial_metrics at line {i+1}")
                removed_count += 1
                
                # Skip this block (from # Financial metrics to closing },)
                # First skip any comment line before
                if i > 0 and '# Financial metrics' in lines[i-1]:
                    new_lines = new_lines[:-1]  # Remove the comment line we already added
                
                # Now skip until we find the closing },
                bracket_count = 1
                i += 1
                while i < len(lines) and bracket_count > 0:
                    if '{' in lines[i]:
                        bracket_count += 1
                    if '}' in lines[i]:
                        bracket_count -= 1
                    i += 1
                
                # Skip the trailing comma if present
                if i < len(lines) and lines[i].strip() == ',':
                    i += 1
                    
                continue
        
        new_lines.append(line)
        i += 1
    
    if removed_count > 0:
        print(f"\nRemoved {removed_count} misplaced financial_metrics blocks")
        with open('app/v2/config/master_config.py', 'w') as f:
            f.writelines(new_lines)
        return True
    else:
        print("No misplaced blocks found")
        return False

def verify_syntax():
    """Verify the file has no syntax errors."""
    import py_compile
    try:
        py_compile.compile('app/v2/config/master_config.py', doraise=True)
        print("✅ No syntax errors found")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        # Extract line number from error
        import re
        match = re.search(r'line (\d+)', str(e))
        if match:
            line_num = int(match.group(1))
            with open('app/v2/config/master_config.py', 'r') as f:
                lines = f.readlines()
                print(f"  Line {line_num}: {lines[line_num-1].strip()}")
                if line_num > 1:
                    print(f"  Line {line_num-1}: {lines[line_num-2].strip()}")
        return False

if __name__ == '__main__':
    print("Cleaning up misplaced financial_metrics blocks...")
    
    # First verify current state
    print("\nInitial syntax check:")
    has_errors = not verify_syntax()
    
    if has_errors:
        # Clean up misplaced blocks
        if cleanup_misplaced_metrics():
            print("\nPost-cleanup syntax check:")
            if verify_syntax():
                print("\n✅ SUCCESS: File is now valid!")
            else:
                print("\n❌ Still has errors, manual intervention needed")
    else:
        print("File is already valid, no cleanup needed")