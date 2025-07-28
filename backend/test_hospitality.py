#!/usr/bin/env python3
"""Test hospitality building type implementation"""

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

def test_hospitality_detection():
    """Test building type detection for hospitality"""
    print("\n=== Testing Hospitality Building Type Detection ===")
    
    test_descriptions = [
        "150 room hotel in downtown Austin",
        "Luxury resort with 200 guest rooms and spa",
        "Budget motel with 50 rooms",
        "Extended stay hotel with 80 suites", 
        "Boutique hotel with 40 rooms",
        "Conference hotel with 250 rooms and meeting space",
        "Mixed use building with 100 room hotel and retail"
    ]
    
    for desc in test_descriptions:
        building_type = determine_building_type(desc)
        subtype = get_building_subtype(building_type, desc)
        print(f"\nDescription: {desc}")
        print(f"Building Type: {building_type}")
        print(f"Subtype: {subtype}")

def test_hospitality_costs():
    """Test hospitality cost calculations"""
    print("\n\n=== Testing Hospitality Cost Calculations ===")
    
    # Test parameters
    square_footage = 67500  # 150 rooms * 450 SF/room
    floors = 5
    region = "TX"
    
    trades = ["structural", "mechanical", "electrical", "plumbing", "finishes"]
    
    print(f"\nTest Building: 150-room hotel")
    print(f"Square Footage: {square_footage:,}")
    print(f"Floors: {floors}")
    print(f"Region: {region}")
    print("\nTrade Costs:")
    
    total_cost = 0
    all_items = []
    
    for trade in trades:
        cost, items = calculate_trade_cost(
            trade=trade,
            building_type="hospitality",
            square_footage=square_footage,
            region=region,
            floors=floors
        )
        total_cost += cost
        all_items.extend(items)
        
        print(f"\n{trade.title()}:")
        print(f"  Total: ${cost:,.0f} (${cost/square_footage:.2f}/SF)")
        
        # Show key items for mechanical trade
        if trade == "mechanical":
            print("  Key Items:")
            for item in items[:5]:  # Show first 5 items
                print(f"    - {item.name}: {item.quantity:.0f} {item.unit} @ ${item.unit_cost:,.2f} = ${item.total_cost:,.0f}")
    
    print(f"\nTotal Trade Cost: ${total_cost:,.0f}")
    print(f"Cost per SF: ${total_cost/square_footage:.2f}")

def test_hospitality_mechanical_items():
    """Test hospitality-specific mechanical items"""
    print("\n\n=== Testing Hospitality-Specific Mechanical Items ===")
    
    # Test with different descriptions
    test_cases = [
        {
            'description': '150 room hotel with restaurant and pool',
            'square_footage': 67500,
            'floors': 5
        },
        {
            'description': '200 room luxury resort with spa',
            'square_footage': 100000,  # 500 SF/room for luxury
            'floors': 3
        },
        {
            'description': 'Budget motel with 50 rooms',
            'square_footage': 20000,  # 400 SF/room for budget
            'floors': 2
        }
    ]
    
    for test in test_cases:
        print(f"\n\nTest: {test['description']}")
        print(f"Square Footage: {test['square_footage']:,}")
        print(f"Floors: {test['floors']}")
        
        # Start with empty scope items
        scope_items = []
        
        # Add mechanical items
        mechanical_items = add_building_specific_mechanical_items(
            scope_items=scope_items,
            building_type='hospitality',
            square_footage=test['square_footage'],
            floors=test['floors'],
            description=test['description']
        )
        
        print("\nMechanical Items Added:")
        for item in mechanical_items:
            if item.category == 'Mechanical':
                print(f"  - {item.name}: {item.quantity:.0f} {item.unit} @ ${item.unit_cost:,.2f} = ${item.total_cost:,.0f}")
                if item.note:
                    print(f"    Note: {item.note}")

def test_hospitality_specific_items():
    """Test other hospitality-specific items"""
    print("\n\n=== Testing Other Hospitality-Specific Items ===")
    
    square_footage = 67500  # 150 rooms
    floors = 5
    
    # Get additional items
    scope_items = []
    additional_items = add_building_specific_items(
        building_type='hospitality',
        scope_items=scope_items,
        square_footage=square_footage,
        floors=floors
    )
    
    print(f"\nAdditional Items for 150-room hotel ({square_footage:,} SF):")
    
    # Group by category
    by_category = {}
    for item in additional_items:
        if item.category not in by_category:
            by_category[item.category] = []
        by_category[item.category].append(item)
    
    for category, items in by_category.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  - {item.name}: {item.quantity:.0f} {item.unit} @ ${item.unit_cost:,.2f} = ${item.total_cost:,.0f}")
            if item.note:
                print(f"    Note: {item.note}")

if __name__ == "__main__":
    test_hospitality_detection()
    test_hospitality_costs()
    test_hospitality_mechanical_items()
    test_hospitality_specific_items()
    
    print("\n\n=== Hospitality Implementation Test Complete ===")