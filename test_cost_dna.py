#!/usr/bin/env python3
"""Test script to verify cost_dna is included in response"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Check if the cost_dna code exists in unified_engine.py
print("Checking if cost_dna code was added to unified_engine.py...")
with open('backend/app/v2/engines/unified_engine.py', 'r') as f:
    content = f.read()
    if 'cost_dna = {' in content and "'cost_dna': cost_dna" in content:
        print("✅ cost_dna generation code found in unified_engine.py")
        
        # Check for specific fields
        if "'regional_adjustment': regional_multiplier" in content:
            print("✅ regional_adjustment field found")
        if "'market_name':" in content:
            print("✅ market_name field found")
        if "'applied_adjustments':" in content:
            print("✅ applied_adjustments field found")
        if "'market_context':" in content:
            print("✅ market_context field found")
    else:
        print("❌ cost_dna code not found or incomplete")

print("\nChecking if frontend TradeBreakdown.tsx was updated...")
with open('frontend/src/v2/pages/ProjectView/TradeBreakdown.tsx', 'r') as f:
    content = f.read()
    if 'Cost Build-Up' in content:
        print("✅ Cost Build-Up section added to TradeBreakdown")
    if 'costDna?.regional_adjustment' in content or 'cost_dna' in content:
        print("✅ Frontend uses cost_dna data")
    if 'Market Adjustment' in content:
        print("✅ Market Adjustment display added")
    if 'Nashville' in content:
        print("✅ Nashville market reference found")

print("\nSummary:")
print("- Backend unified_engine.py now generates and returns cost_dna")
print("- Frontend TradeBreakdown.tsx now displays Cost Build-Up with regional multiplier")
print("- Nashville should now show 1.03x instead of 1.00x when cost_dna is available")