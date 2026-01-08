#!/usr/bin/env python3
"""
Test the V2 API endpoints locally
"""

import json
from app.v2.api.scope import (
    analyze_project,
    calculate_project,
    compare_scenarios,
    get_building_types,
    get_building_details,
    health_check,
    test_nlp,
    AnalyzeRequest,
    CalculateRequest,
    CompareRequest
)
import asyncio

async def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    result = await health_check()
    print(f"Success: {result.success}")
    print(f"Version: {result.data['version']}")
    print(f"Engine: {result.data['engine']}")
    print(f"Building Types: {result.data['building_types']}")
    print(f"Total Subtypes: {result.data['total_subtypes']}")

async def test_analyze():
    """Test natural language analysis"""
    print("\n" + "="*60)
    print("TEST 2: Natural Language Analysis")
    print("="*60)
    
    request = AnalyzeRequest(
        description="We need to build a 100,000 square foot hospital with emergency department in Nashville",
        default_location="Nashville"
    )
    
    result = await analyze_project(request)
    print(f"Success: {result.success}")
    if result.success:
        print(f"Detected Type: {result.data['parsed_input']['building_type']}/{result.data['parsed_input']['subtype']}")
        print(f"Square Footage: {result.data['parsed_input']['square_footage']:,}")
        print(f"Location: {result.data['parsed_input']['location']}")
        print(f"Total Cost: ${result.data['calculations']['totals']['total_project_cost']:,.2f}")
        print(f"Cost per SF: ${result.data['calculations']['totals']['cost_per_sf']:.2f}")
        print(f"Confidence: {result.data['confidence']:.2f}")

async def test_calculate():
    """Test direct calculation"""
    print("\n" + "="*60)
    print("TEST 3: Direct Calculation")
    print("="*60)
    
    request = CalculateRequest(
        building_type="parking",
        subtype="parking_garage",
        square_footage=50000,
        location="New York",
        project_class="ground_up",
        floors=5,
        ownership_type="for_profit",
        special_features=["ev_charging", "automated_system"]
    )
    
    result = await calculate_project(request)
    print(f"Success: {result.success}")
    if result.success:
        print(f"Building: {result.data['project_info']['display_name']}")
        print(f"Location: {result.data['project_info']['location']}")
        print(f"Base Cost/SF: ${result.data['construction_costs']['base_cost_per_sf']}")
        print(f"Regional Multiplier: {result.data['construction_costs']['regional_multiplier']}")
        print(f"Total Cost: ${result.data['totals']['total_project_cost']:,.2f}")

async def test_compare():
    """Test scenario comparison"""
    print("\n" + "="*60)
    print("TEST 4: Scenario Comparison")
    print("="*60)
    
    request = CompareRequest(
        scenarios=[
            {
                "name": "Option A - Class A Office",
                "building_type": "office",
                "subtype": "class_a",
                "square_footage": 50000,
                "location": "Nashville",
                "project_class": "ground_up"
            },
            {
                "name": "Option B - Class B Office",
                "building_type": "office",
                "subtype": "class_b",
                "square_footage": 60000,
                "location": "Nashville",
                "project_class": "ground_up"
            },
            {
                "name": "Option C - Renovation",
                "building_type": "office",
                "subtype": "class_a",
                "square_footage": 50000,
                "location": "Nashville",
                "project_class": "renovation"
            }
        ]
    )
    
    result = await compare_scenarios(request)
    print(f"Success: {result.success}")
    if result.success:
        print(f"Scenarios Compared: {result.data['summary']['total_scenarios']}")
        print(f"Lowest Cost: {result.data['summary']['lowest_cost_scenario']}")
        print(f"Highest Cost: {result.data['summary']['highest_cost_scenario']}")
        print(f"Cost Range: ${result.data['summary']['cost_range']['min']:,.0f} - ${result.data['summary']['cost_range']['max']:,.0f}")

async def test_building_types():
    """Test getting building types"""
    print("\n" + "="*60)
    print("TEST 5: Get Building Types")
    print("="*60)
    
    result = await get_building_types()
    print(f"Success: {result.success}")
    if result.success:
        for building_type, info in list(result.data.items())[:3]:
            print(f"\n{building_type.upper()}:")
            for subtype, details in list(info['subtypes'].items())[:2]:
                print(f"  - {subtype}: {details['display_name']} (${details['base_cost_per_sf']}/SF)")

async def test_building_details():
    """Test getting building details"""
    print("\n" + "="*60)
    print("TEST 6: Get Building Details")
    print("="*60)
    
    result = await get_building_details("healthcare", "hospital")
    print(f"Success: {result.success}")
    if result.success:
        print(f"Display Name: {result.data['display_name']}")
        print(f"Base Cost: ${result.data['base_cost_per_sf']}/SF")
        print(f"Cost Range: ${result.data['cost_range'][0]}-${result.data['cost_range'][1]}/SF")
        print(f"Typical Floors: {result.data['typical_floors']}")
        print(f"Special Features: {', '.join(result.data['special_features'][:3])}...")

async def test_nlp_endpoint():
    """Test NLP parsing endpoint"""
    print("\n" + "="*60)
    print("TEST 7: Test NLP Parsing")
    print("="*60)
    
    text = "Build a 5-story parking garage with 500 spaces in downtown Chicago"
    result = await test_nlp(text=text)
    print(f"Success: {result.success}")
    if result.success:
        print(f"Text: '{text}'")
        print(f"Building Type: {result.data.get('building_type')}/{result.data.get('subtype')}")
        print(f"Floors: {result.data.get('floors')}")
        print(f"Location: {result.data.get('location')}")

async def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# V2 API TEST SUITE")
    print("#"*60)
    
    try:
        await test_health()
        await test_analyze()
        await test_calculate()
        await test_compare()
        await test_building_types()
        await test_building_details()
        await test_nlp_endpoint()
        
        print("\n" + "="*60)
        print("✅ ALL V2 API TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())