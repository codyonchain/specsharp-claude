#!/usr/bin/env python3
"""
Test script to diagnose warehouse expense ratio and investment calculations
"""

import sys
import os
sys.path.append('/Users/codymarchant/specsharp/backend')

from app.v2.engines.unified_engine import UnifiedEngine
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def test_warehouse_investment():
    """Test a simple warehouse to see why it's not investable"""
    
    engine = UnifiedEngine()
    
    # Test a 50,000 SF warehouse in Nashville (should be profitable)
    result = engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype='warehouse',
        square_footage=50000,
        location='Nashville',
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT
    )
    
    print("=== WAREHOUSE TEST RESULTS ===")
    print(f"Building: {result['project_info']['display_name']}")
    print(f"Size: {result['project_info']['square_footage']:,} SF")
    print(f"Location: {result['project_info']['location']}")
    print()
    
    # Construction costs
    print("=== CONSTRUCTION COSTS ===")
    print(f"Base cost per SF: ${result['construction_costs']['base_cost_per_sf']}")
    print(f"Final cost per SF: ${result['construction_costs']['final_cost_per_sf']:.2f}")
    print(f"Total project cost: ${result['totals']['total_project_cost']:,.0f}")
    print()
    
    # Revenue analysis
    if 'revenue_analysis' in result and result['revenue_analysis']:
        print("=== REVENUE ANALYSIS ===")
        revenue = result['revenue_analysis']
        print(f"Annual revenue: ${revenue['annual_revenue']:,.0f}")
        print(f"Revenue per SF: ${revenue['revenue_per_sf']:.2f}")
        print(f"Operating margin: {revenue['operating_margin']:.1%}")
        print(f"Net income: ${revenue['net_income']:,.0f}")
        print(f"Occupancy rate: {revenue['occupancy_rate']:.1%}")
        print()
    
    # Operational efficiency (expense breakdown)
    if 'operational_efficiency' in result and result['operational_efficiency']:
        print("=== EXPENSE BREAKDOWN ===")
        oe = result['operational_efficiency']
        print(f"Total expenses: ${oe['total_expenses']:,.0f}")
        print(f"Expense ratio: {oe['expense_ratio']:.1%}")
        print(f"Operating margin: {oe['operating_margin']:.1%}")
        print(f"Efficiency score: {oe['efficiency_score']:.1f}%")
        print()
        
        # Individual expense categories
        print("=== INDIVIDUAL EXPENSES ===")
        expense_categories = [
            'utility_cost', 'property_tax', 'insurance_cost', 'maintenance_cost',
            'management_fee', 'security', 'reserves', 'labor_cost'
        ]
        
        total_detailed = 0
        for category in expense_categories:
            if category in oe and oe[category] > 0:
                amount = oe[category]
                ratio = amount / revenue['annual_revenue'] if 'revenue_analysis' in result else 0
                print(f"{category}: ${amount:,.0f} ({ratio:.1%})")
                total_detailed += amount
        
        print(f"Total detailed expenses: ${total_detailed:,.0f}")
        print()
    
    # Investment metrics
    if 'return_metrics' in result and result['return_metrics']:
        print("=== INVESTMENT METRICS ===")
        metrics = result['return_metrics']
        print(f"Cap rate: {metrics['cap_rate']:.2f}%")
        print(f"Cash-on-cash return: {metrics['cash_on_cash_return']:.2f}%")
        print(f"IRR: {metrics['irr']:.2f}%")
        print(f"NPV: ${metrics['npv']:,.0f}")
        print(f"Payback period: {metrics['payback_period']} years")
        print()
    
    # Revenue requirements
    if 'revenue_requirements' in result and result['revenue_requirements']:
        print("=== REVENUE REQUIREMENTS ===")
        rr = result['revenue_requirements']
        print(f"Required annual return: ${rr['required_value']:,.0f}")
        print(f"Actual net income: ${rr.get('actual_net_income', 0):,.0f}")
        print(f"Feasibility: {rr['feasibility']}")
        print(f"Gap: ${rr['gap']:,.0f}")
        print(f"Gap percentage: {rr['gap_percentage']:.1f}%")
        print()
    
    # Market comparison
    print("=== MARKET COMPARISON ===")
    if 'revenue_analysis' in result and result['revenue_analysis']:
        revenue = result['revenue_analysis']
        project_cost = result['totals']['total_project_cost']
        annual_revenue = revenue['annual_revenue']
        
        print(f"Project cost: ${project_cost:,.0f}")
        print(f"Annual revenue: ${annual_revenue:,.0f}")
        print(f"Revenue/Cost ratio: {annual_revenue/project_cost:.2f}x")
        
        # Market expectations for warehouse
        print(f"Expected warehouse rent: $6-10/SF/year")
        print(f"Expected cap rate: 6-8%")
        print(f"Expected expense ratio: 15-20%")
        
        market_revenue_low = 50000 * 6  # $6/SF
        market_revenue_high = 50000 * 10  # $10/SF
        print(f"Market revenue range: ${market_revenue_low:,.0f} - ${market_revenue_high:,.0f}")
        
        if annual_revenue < market_revenue_low:
            print("⚠️  WARNING: Projected revenue below market expectations!")
        elif annual_revenue > market_revenue_high:
            print("✅ Revenue above market expectations")
        else:
            print("✅ Revenue within market range")

if __name__ == "__main__":
    test_warehouse_investment()