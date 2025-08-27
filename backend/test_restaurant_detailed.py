#!/usr/bin/env python3
"""Detailed test of restaurant cost calculations"""

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType
import json

def test_detailed():
    engine = UnifiedEngine()
    
    result = engine.calculate_project(
        building_type=BuildingType.RESTAURANT,
        subtype="bar_tavern",
        project_class=ProjectClass.GROUND_UP,
        square_footage=4200,
        location="Nashville",
        floors=1,
        ownership_type=OwnershipType.FOR_PROFIT
    )
    
    print("\n" + "="*80)
    print("DETAILED COST BREAKDOWN: Bar/Tavern in Nashville (4,200 SF)")
    print("="*80)
    
    print("\n1. BASE CALCULATIONS:")
    cc = result['construction_costs']
    print(f"   Base cost per SF:        ${cc['base_cost_per_sf']:,.0f}")
    print(f"   Class multiplier:        {cc['class_multiplier']:.2f}x")
    print(f"   Regional multiplier:     {cc['regional_multiplier']:.2f}x")
    print(f"   Final cost per SF:       ${cc['final_cost_per_sf']:,.0f}")
    print(f"   Construction total:      ${cc['construction_total']:,.0f}")
    print(f"   Equipment total:         ${cc['equipment_total']:,.0f}")
    
    print("\n2. HARD COSTS:")
    print(f"   Construction:            ${cc['construction_total']:,.0f}")
    print(f"   Equipment:               ${cc['equipment_total']:,.0f}")
    hc_total = cc['construction_total'] + cc['equipment_total']
    print(f"   TOTAL HARD COSTS:        ${hc_total:,.0f}")
    
    print("\n3. SOFT COSTS:")
    sc = result['soft_costs']
    for key, value in sc.items():
        print(f"   {key:<25} ${value:>12,.0f}")
    sc_total = sum(sc.values())
    print(f"   TOTAL SOFT COSTS:        ${sc_total:,.0f}")
    
    print("\n4. TOTALS:")
    totals = result['totals']
    print(f"   Total project cost:      ${totals['total_project_cost']:,.0f}")
    print(f"   Cost per SF:             ${totals['cost_per_sf']:,.0f}")
    
    print("\n5. CALCULATION CHECK:")
    print(f"   Hard costs / SF:         ${hc_total / 4200:,.0f}")
    print(f"   Soft costs / SF:         ${sc_total / 4200:,.0f}")
    print(f"   Total / SF:              ${totals['total_project_cost'] / 4200:,.0f}")
    
    print("\n6. MULTIPLIER ANALYSIS:")
    base_construction = cc['base_cost_per_sf'] * 4200
    print(f"   Base construction:       ${base_construction:,.0f}")
    print(f"   After regional (1.03x):  ${base_construction * 1.03:,.0f}")
    print(f"   Plus equipment:          ${base_construction * 1.03 + cc['equipment_total']:,.0f}")
    print(f"   Plus soft costs:         ${totals['total_project_cost']:,.0f}")
    
    print("="*80)

if __name__ == "__main__":
    test_detailed()