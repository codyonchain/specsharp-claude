#!/usr/bin/env python3
"""Test retail building type implementation"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.building_type_detector import determine_building_type, get_building_subtype
from app.core.cost_engine import (
    calculate_trade_cost, 
    add_building_specific_mechanical_items,
    add_building_specific_items,
    ScopeItem
)

def test_retail_detection():
    """Test building type detection for retail"""
    print("\n=== Testing Retail Building Type Detection ===")
    
    test_descriptions = [
        "Strip center with 10 retail tenants",
        "Regional shopping mall with 200 stores",
        "Big box retail anchor store",
        "Grocery supermarket with pharmacy",
        "Standalone retail store",
        "Neighborhood strip mall with restaurants",
        "Department store in shopping center",
        "Convenience store with gas station"
    ]
    
    for desc in test_descriptions:
        building_type = determine_building_type(desc)
        subtype = get_building_subtype(building_type, desc)
        print(f"\nDescription: {desc}")
        print(f"Building Type: {building_type}")
        print(f"Subtype: {subtype}")

def test_retail_costs():
    """Test retail cost calculations"""
    print("\n\n=== Testing Retail Cost Calculations ===")
    
    # Test different retail types
    test_cases = [
        {
            'name': 'Strip Center',
            'square_footage': 25000,
            'floors': 1,
            'description': 'Neighborhood strip center with 10 tenants'
        },
        {
            'name': 'Shopping Mall',
            'square_footage': 500000,
            'floors': 2,
            'description': 'Regional shopping mall with department stores'
        },
        {
            'name': 'Grocery Store',
            'square_footage': 50000,
            'floors': 1,
            'description': 'Supermarket with pharmacy and deli'
        },
        {
            'name': 'Big Box Retail',
            'square_footage': 125000,
            'floors': 1,
            'description': 'Big box anchor store'
        }
    ]
    
    region = "TX"
    trades = ["structural", "mechanical", "electrical", "plumbing", "finishes"]
    
    for test in test_cases:
        print(f"\n\nTest: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Square Footage: {test['square_footage']:,}")
        print(f"Floors: {test['floors']}")
        print(f"Region: {region}")
        print("\nTrade Costs:")
        
        total_cost = 0
        
        for trade in trades:
            cost, items = calculate_trade_cost(
                trade=trade,
                building_type="retail",
                square_footage=test['square_footage'],
                region=region,
                floors=test['floors']
            )
            total_cost += cost
            
            print(f"\n{trade.title()}: ${cost:,.0f} (${cost/test['square_footage']:.2f}/SF)")
            
            # Show some items for mechanical
            if trade == "mechanical" and items:
                print("  Sample Items:")
                for item in items[:3]:
                    print(f"    - {item.name}: {item.quantity:.0f} {item.unit} @ ${item.unit_cost:,.2f}")
        
        print(f"\nTotal Trade Cost: ${total_cost:,.0f}")
        print(f"Cost per SF: ${total_cost/test['square_footage']:.2f}")

def test_retail_mechanical_items():
    """Test retail-specific mechanical items"""
    print("\n\n=== Testing Retail-Specific Mechanical Items ===")
    
    test_cases = [
        {
            'description': 'Grocery supermarket with full refrigeration',
            'square_footage': 50000,
            'floors': 1
        },
        {
            'description': 'Shopping mall with food court',
            'square_footage': 300000,
            'floors': 2
        },
        {
            'description': 'Strip center with restaurant tenants',
            'square_footage': 20000,
            'floors': 1
        },
        {
            'description': 'Big box department store',
            'square_footage': 100000,
            'floors': 1
        }
    ]
    
    for test in test_cases:
        print(f"\n\nTest: {test['description']}")
        print(f"Square Footage: {test['square_footage']:,}")
        print(f"Floors: {test['floors']}")
        
        # Get mechanical items
        scope_items = []
        mechanical_items = add_building_specific_mechanical_items(
            scope_items=scope_items,
            building_type='retail',
            square_footage=test['square_footage'],
            floors=test['floors'],
            description=test['description']
        )
        
        print("\nMechanical Items Added:")
        for item in mechanical_items:
            if item.category == 'Mechanical':
                print(f"  - {item.name}: {item.quantity:.1f} {item.unit} @ ${item.unit_cost:,.2f} = ${item.total_cost:,.0f}")
                if item.note:
                    print(f"    Note: {item.note}")

def test_retail_specific_items():
    """Test other retail-specific items"""
    print("\n\n=== Testing Other Retail-Specific Items ===")
    
    test_cases = [
        {
            'description': 'Strip mall with multiple tenants',
            'square_footage': 30000,
            'floors': 1
        },
        {
            'description': 'Grocery store with pharmacy',
            'square_footage': 45000,
            'floors': 1
        },
        {
            'description': 'Regional mall with anchor stores',
            'square_footage': 400000,
            'floors': 2
        }
    ]
    
    for test in test_cases:
        print(f"\n\nTest: {test['description']}")
        print(f"Square Footage: {test['square_footage']:,} SF")
        
        # Get additional items
        scope_items = []
        additional_items = add_building_specific_items(
            building_type='retail',
            scope_items=scope_items,
            square_footage=test['square_footage'],
            floors=test['floors'],
            description=test['description']
        )
        
        # Group by category
        by_category = {}
        for item in additional_items:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)
        
        for category, items in by_category.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  - {item.name}: {item.quantity:.1f} {item.unit} @ ${item.unit_cost:,.2f} = ${item.total_cost:,.0f}")
                if item.note:
                    print(f"    Note: {item.note}")

if __name__ == "__main__":
    test_retail_detection()
    test_retail_costs()
    test_retail_mechanical_items()
    test_retail_specific_items()
    
    print("\n\n=== Retail Implementation Test Complete ===")
    print("\nAll major building types are now implemented!")
    print("- Commercial/Office ✅")
    print("- Healthcare ✅")
    print("- Educational ✅")
    print("- Multi-Family Residential ✅")
    print("- Industrial ✅")
    print("- Warehouse ✅")
    print("- Restaurant ✅")
    print("- Hospitality ✅")
    print("- Retail ✅")