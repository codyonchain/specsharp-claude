#!/usr/bin/env python3
"""
Surgical removal of financial_metrics only, line by line.
"""

def remove_financial_metrics_carefully():
    """Remove financial_metrics blocks line by line"""
    
    with open('app/v2/config/master_config.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    removed_count = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts a financial_metrics block
        if 'financial_metrics=' in line or 'financial_metrics =' in line:
            print(f"Found financial_metrics at line {i+1}")
            removed_count += 1
            
            # Skip the comment line before if it exists
            if new_lines and '# Financial metrics' in new_lines[-1]:
                new_lines.pop()
            
            # Skip this line and find the end of the block
            bracket_count = 0
            in_block = False
            i += 1
            
            while i < len(lines):
                if '{' in lines[i]:
                    bracket_count += 1
                    in_block = True
                if '}' in lines[i]:
                    bracket_count -= 1
                    if bracket_count == 0 and in_block:
                        # Found the end, skip this line too
                        i += 1
                        # Skip the comma on the next line if it exists
                        if i < len(lines) and lines[i].strip() == ',':
                            i += 1
                        break
                i += 1
            
            # Remove any trailing commas from the previous line if needed
            if new_lines and new_lines[-1].rstrip().endswith(','):
                # Check if the next non-empty line would be a closing paren or brace
                next_idx = i
                while next_idx < len(lines) and not lines[next_idx].strip():
                    next_idx += 1
                if next_idx < len(lines):
                    next_line = lines[next_idx].strip()
                    if next_line.startswith(')') or next_line.startswith('}'):
                        # Remove the trailing comma
                        new_lines[-1] = new_lines[-1].rstrip()[:-1] + '\n'
        else:
            # Keep this line
            new_lines.append(line)
            i += 1
    
    # Also remove the financial_metrics field from BuildingConfig dataclass
    final_lines = []
    for line in new_lines:
        if 'financial_metrics:' in line and 'Optional[Dict' in line:
            print("Removed financial_metrics field from BuildingConfig dataclass")
            continue
        final_lines.append(line)
    
    print(f"Removed {removed_count} financial_metrics blocks")
    
    # Write back
    with open('app/v2/config/master_config.py', 'w') as f:
        f.writelines(final_lines)
    
    return removed_count > 0

def verify_file():
    """Verify the file is valid Python"""
    import py_compile
    
    try:
        py_compile.compile('app/v2/config/master_config.py', doraise=True)
        print("✅ File is valid Python")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        # Show context
        import re
        match = re.search(r'line (\d+)', str(e))
        if match:
            line_num = int(match.group(1))
            with open('app/v2/config/master_config.py', 'r') as f:
                lines = f.readlines()
                if line_num <= len(lines):
                    print(f"Context around line {line_num}:")
                    for i in range(max(0, line_num-3), min(len(lines), line_num+2)):
                        print(f"  {i+1}: {lines[i].rstrip()}")
        return False

if __name__ == '__main__':
    print("=== SURGICAL ROLLBACK - REMOVING FINANCIAL_METRICS ===\n")
    
    if remove_financial_metrics_carefully():
        print("\nVerifying syntax...")
        if verify_file():
            print("\n✅ SUCCESS: All financial_metrics removed, file is valid")
        else:
            print("\n❌ Syntax errors remain after removal")
    else:
        print("\nNo financial_metrics found to remove")