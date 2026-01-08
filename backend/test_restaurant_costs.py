#!/usr/bin/env python3
"""Test restaurant cost calculations after fixes"""

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def test_restaurant_costs():
    engine = UnifiedEngine()
    
    test_cases = [
        ("bar_tavern", "Bar/Tavern"),
        ("full_service", "Full Service Restaurant"),
        ("quick_service", "Quick Service Restaurant"),
        ("cafe", "Cafe/Coffee Shop")
    ]
    
    print("\n" + "="*80)
    print("RESTAURANT COST VALIDATION TEST")
    print("="*80)
    print(f"{'Subtype':<25} {'Base Cost/SF':<15} {'Total Cost/SF':<15} {'4,200 SF Total':<20}")
    print("-"*80)
    
    for subtype, name in test_cases:
        result = engine.calculate_project(
            building_type=BuildingType.RESTAURANT,
            subtype=subtype,
            project_class=ProjectClass.GROUND_UP,
            square_footage=4200,
            location="Nashville",
            floors=1,
            ownership_type=OwnershipType.FOR_PROFIT
        )
        
        base_cost = result['construction_costs']['base_cost_per_sf']
        total_cost = result['totals']['total_project_cost']
        cost_per_sf = result['totals']['cost_per_sf']
        
        print(f"{name:<25} ${base_cost:<14.0f} ${cost_per_sf:<14.0f} ${total_cost:>18,.0f}")
    
    print("-"*80)
    print("\nExpected ranges for Nashville restaurants:")
    print("  - Cafe/Coffee Shop: $300-350/SF")
    print("  - Quick Service: $325-375/SF")
    print("  - Bar/Tavern: $375-425/SF")
    print("  - Full Service: $425-475/SF")
    print("="*80)

if __name__ == "__main__":
    test_restaurant_costs()