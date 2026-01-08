#!/usr/bin/env python3
"""
Rollback script to remove all financial_metrics additions while preserving Sprint 1-3 working code.
"""

import re

def clean_financial_metrics():
    """Remove all financial_metrics blocks from master_config.py"""
    
    # Read the file
    with open('app/v2/config/master_config.py', 'r') as f:
        content = f.read()
    
    original_length = len(content)
    
    # Pattern 1: Remove financial_metrics blocks within BuildingConfig
    # Matches: financial_metrics={...},
    pattern1 = r',?\s*financial_metrics\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\},?'
    content = re.sub(pattern1, '', content, flags=re.DOTALL)
    
    # Pattern 2: Remove any # Financial metrics comments
    pattern2 = r'\n\s*#\s*Financial metrics\s*\n'
    content = re.sub(pattern2, '\n', content, flags=re.MULTILINE)
    
    # Pattern 3: Remove financial_metrics field from BuildingConfig dataclass if present
    pattern3 = r'^\s*financial_metrics:\s*Optional\[Dict\[str,\s*any\]\].*?\n'
    content = re.sub(pattern3, '', content, flags=re.MULTILINE)
    
    # Pattern 4: Clean up any multiple blank lines
    content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n', content)
    
    # Pattern 5: Clean up any double commas or trailing commas before closing parens
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r',\s*\)', ')', content)
    
    # Pattern 6: Fix any broken f-strings from previous attempts
    # Fix the specific error at line 4701
    content = re.sub(
        r'errors\.append\(f".*?Trade percentages sum to \{trade_sum:\.2f\},\s*\n\s*not 1\.0"\)',
        'errors.append(f"{building_type.value}/{subtype}: Trade percentages sum to {trade_sum:.2f}, not 1.0")',
        content,
        flags=re.DOTALL
    )
    
    removed_chars = original_length - len(content)
    
    # Write back
    with open('app/v2/config/master_config.py', 'w') as f:
        f.write(content)
    
    print(f"Removed {removed_chars} characters related to financial_metrics")
    return removed_chars > 0

def verify_sprint1_intact():
    """Verify that Sprint 1 fixes (base_revenue_per_sf_annual) are still present"""
    
    import sys
    sys.path.insert(0, '.')
    
    try:
        from app.v2.config.master_config import MASTER_CONFIG, BuildingType
        
        count = 0
        missing = []
        
        for bt in BuildingType:
            for subtype, config in MASTER_CONFIG.get(bt, {}).items():
                if hasattr(config, 'base_revenue_per_sf_annual'):
                    if config.base_revenue_per_sf_annual is not None:
                        count += 1
                else:
                    missing.append(f"{bt.value}/{subtype}")
        
        print(f"\n✅ {count} subtypes still have base_revenue_per_sf_annual (Sprint 1 intact)")
        
        if missing:
            print(f"⚠️  {len(missing)} subtypes missing base_revenue_per_sf_annual:")
            for m in missing[:5]:
                print(f"    - {m}")
            if len(missing) > 5:
                print(f"    ... and {len(missing) - 5} more")
        
        return count > 0
        
    except Exception as e:
        print(f"❌ Error verifying Sprint 1 fixes: {e}")
        return False

def verify_syntax():
    """Verify the file has no syntax errors"""
    import py_compile
    
    try:
        py_compile.compile('app/v2/config/master_config.py', doraise=True)
        print("✅ master_config.py is valid Python (no syntax errors)")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error in master_config.py: {e}")
        return False

def main():
    print("=== ROLLBACK SPRINT 3.5 - REMOVING FINANCIAL_METRICS ===\n")
    
    # Step 1: Clean financial_metrics
    print("Step 1: Removing all financial_metrics blocks...")
    if clean_financial_metrics():
        print("   ✅ Cleaned financial_metrics")
    else:
        print("   ⚠️  No financial_metrics found to remove")
    
    # Step 2: Verify syntax
    print("\nStep 2: Verifying Python syntax...")
    syntax_ok = verify_syntax()
    
    if syntax_ok:
        # Step 3: Verify Sprint 1 is intact
        print("\nStep 3: Verifying Sprint 1 fixes are intact...")
        sprint1_ok = verify_sprint1_intact()
        
        if sprint1_ok:
            print("\n✅ ROLLBACK SUCCESSFUL!")
            print("   - All financial_metrics removed")
            print("   - Sprint 1 revenue fixes intact")
            print("   - No syntax errors")
        else:
            print("\n⚠️  ROLLBACK PARTIAL: Sprint 1 fixes may need attention")
    else:
        print("\n❌ ROLLBACK FAILED: Syntax errors remain")
        print("   Manual intervention required")

if __name__ == '__main__':
    main()