#!/usr/bin/env python3
"""
Test script for Healthcare Cost Service v2 with market-specific costs
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.healthcare_cost_service import healthcare_cost_service

def test_healthcare_v2():
    """Test the new market-specific healthcare cost calculations"""
    
    test_cases = [
        {
            "description": "50,000 sf hospital with emergency department and surgical suite in Nashville TN",
            "square_feet": 50000,
            "location": "Nashville, TN"
        },
        {
            "description": "15,000 sf medical office building in Manchester NH",
            "square_feet": 15000,
            "location": "Manchester, NH"
        },
        {
            "description": "8,000 sf urgent care with x-ray in Franklin TN",
            "square_feet": 8000,
            "location": "Franklin, TN"
        },
        {
            "description": "25,000 sf ambulatory surgery center with 4 ORs in Nashua NH",
            "square_feet": 25000,
            "location": "Nashua, NH"
        },
        {
            "description": "100,000 sf pediatric hospital with NICU and emergency department in Murfreesboro TN",
            "square_feet": 100000,
            "location": "Murfreesboro, TN"
        },
        {
            "description": "12,000 sf imaging center with MRI and CT in Concord NH",
            "square_feet": 12000,
            "location": "Concord, NH"
        }
    ]
    
    print("=" * 80)
    print("HEALTHCARE COST SERVICE V2 - MARKET-SPECIFIC TESTING")
    print("=" * 80)
    
    for case in test_cases:
        try:
            result = healthcare_cost_service.calculate_healthcare_costs_v2(
                case["description"],
                case["square_feet"],
                case["location"]
            )
            
            print(f"\n{'-'*60}")
            print(f"Project: {case['description']}")
            print(f"Location: {result['market']}")
            print(f"Facility Type: {result['facility_type']}")
            print(f"Square Feet: {case['square_feet']:,}")
            print(f"\nClassification Details:")
            print(f"  - Complexity: {result['classification']['complexity_multiplier']:.2f}x")
            
            if result['special_spaces']:
                print(f"  - Special Spaces: {', '.join(result['special_spaces'])}")
            
            print(f"\nConstruction Costs:")
            print(f"  - Base Cost/SF: ${result['construction']['base_cost_per_sf']:.0f}")
            print(f"  - Subtotal: ${result['construction']['subtotal']:,.0f}")
            print(f"  - Contingency: ${result['construction']['contingency']:,.0f}")
            print(f"  - Total: ${result['construction']['total']:,.0f}")
            print(f"  - Cost/SF: ${result['construction']['cost_per_sf']:.0f}")
            
            print(f"\nTrade Breakdown:")
            for trade, cost in result['construction']['trades'].items():
                percentage = (cost / result['construction']['subtotal']) * 100
                print(f"  - {trade.replace('_', ' ').title()}: ${cost:,.0f} ({percentage:.1f}%)")
            
            if result['equipment']['total'] > 0:
                print(f"\nEquipment Costs:")
                print(f"  - Total: ${result['equipment']['total']:,.0f}")
                print(f"  - Cost/SF: ${result['equipment']['cost_per_sf']:.0f}")
                
                if result['equipment']['items']:
                    print(f"  - Items:")
                    for item in result['equipment']['items'][:3]:  # Show first 3 items
                        print(f"    • {item['name']}: ${item['cost']:,.0f}")
            
            print(f"\nProject Total:")
            print(f"  - Construction Only: ${result['project_total']['construction_only']:,.0f}")
            print(f"  - Equipment Only: ${result['project_total']['equipment_only']:,.0f}")
            print(f"  - All-In Total: ${result['project_total']['all_in_total']:,.0f}")
            print(f"  - All-In Cost/SF: ${result['project_total']['all_in_cost_per_sf']:.0f}")
            
            if result['compliance']:
                print(f"\nCompliance Requirements:")
                compliance_items = list(result['compliance'].items())[:3]  # Show first 3
                for req_type, req_value in compliance_items:
                    print(f"  • {req_type}: {req_value}")
            
        except Exception as e:
            print(f"\n{'-'*60}")
            print(f"ERROR for: {case['description']}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TESTING COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_healthcare_v2()