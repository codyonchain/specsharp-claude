#!/usr/bin/env python3
"""
Remove duplicate financial_metrics from BuildingConfig entries.
Keep only the first one found within each BuildingConfig.
"""

import re

def remove_duplicate_financial_metrics():
    """Remove duplicate financial_metrics within BuildingConfigs."""
    
    with open('app/v2/config/master_config.py', 'r') as f:
        content = f.read()
    
    # Pattern to find each BuildingConfig block
    # Match from 'subtype': BuildingConfig( to the closing ),
    pattern = r"'(\w+)':\s*BuildingConfig\((.*?\n\s*\),"
    
    changes_made = 0
    
    def process_config(match):
        nonlocal changes_made
        subtype = match.group(1)
        config_content = match.group(2)
        
        # Count financial_metrics in this config
        count = config_content.count('financial_metrics=')
        
        if count > 1:
            print(f"Found {count} financial_metrics in {subtype}, keeping first one")
            changes_made += 1
            
            # Keep only the first financial_metrics
            parts = config_content.split('financial_metrics=')
            
            # First part + first financial_metrics block
            result = parts[0] + 'financial_metrics='
            
            # Find the end of the first financial_metrics block
            remaining = parts[1]
            bracket_count = 0
            in_block = False
            end_pos = 0
            
            for i, char in enumerate(remaining):
                if char == '{':
                    bracket_count += 1
                    in_block = True
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0 and in_block:
                        end_pos = i + 1
                        # Include the comma after the closing bracket
                        if i + 1 < len(remaining) and remaining[i + 1] == ',':
                            end_pos = i + 2
                        break
            
            # Add the first financial_metrics block
            result += remaining[:end_pos]
            
            # Skip any other financial_metrics blocks in the remaining content
            remaining_after = remaining[end_pos:]
            
            # Remove any additional financial_metrics blocks
            while 'financial_metrics=' in remaining_after:
                # Find start of next financial_metrics
                fm_start = remaining_after.find('financial_metrics=')
                
                # Add content before this financial_metrics
                result += remaining_after[:fm_start]
                
                # Skip this financial_metrics block
                remaining_after = remaining_after[fm_start + len('financial_metrics='):]
                
                # Find end of this block
                bracket_count = 0
                in_block = False
                end_pos = 0
                
                for i, char in enumerate(remaining_after):
                    if char == '{':
                        bracket_count += 1
                        in_block = True
                    elif char == '}':
                        bracket_count -= 1
                        if bracket_count == 0 and in_block:
                            end_pos = i + 1
                            # Skip comma too
                            if i + 1 < len(remaining_after) and remaining_after[i + 1] == ',':
                                end_pos = i + 2
                            # Skip following newline too
                            while end_pos < len(remaining_after) and remaining_after[end_pos] in '\n\r':
                                end_pos += 1
                            break
                
                remaining_after = remaining_after[end_pos:]
            
            # Add any remaining content
            result += remaining_after
            
            return f"'{subtype}': BuildingConfig({result}\n        ),"
        
        return match.group(0)
    
    # Process all BuildingConfig blocks
    new_content = re.sub(pattern, process_config, content, flags=re.DOTALL)
    
    if changes_made > 0:
        print(f"\nRemoved duplicates from {changes_made} configs")
        with open('app/v2/config/master_config.py', 'w') as f:
            f.write(new_content)
        return True
    else:
        print("No duplicate financial_metrics found")
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
        # Show the error location
        import re
        match = re.search(r'line (\d+)', str(e))
        if match:
            line_num = int(match.group(1))
            with open('app/v2/config/master_config.py', 'r') as f:
                lines = f.readlines()
                if line_num <= len(lines):
                    print(f"  Line {line_num}: {lines[line_num-1].strip()}")
        return False

if __name__ == '__main__':
    print("Removing duplicate financial_metrics...")
    
    # Check initial state
    print("\nInitial syntax check:")
    has_errors = not verify_syntax()
    
    if has_errors:
        # Remove duplicates
        if remove_duplicate_financial_metrics():
            print("\nPost-cleanup syntax check:")
            verify_syntax()
    else:
        print("No syntax errors - checking for duplicates anyway...")
        remove_duplicate_financial_metrics()
        print("\nFinal syntax check:")
        verify_syntax()