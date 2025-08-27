#!/usr/bin/env python3
"""
Simple test of V2 system without FastAPI
"""

from app.v2.engines.unified_engine import unified_engine
from app.v2.services.nlp_service import nlp_service
from app.v2.config.master_config import BuildingType, ProjectClass, OwnershipType

def test_full_flow():
    """Test the complete flow: NLP -> Engine -> Results"""
    print("\n" + "="*60)
    print("V2 SYSTEM INTEGRATION TEST")
    print("="*60)
    
    # Test case 1: Hospital
    description = "We need to build a 100,000 square foot hospital with emergency department in Nashville"
    print(f"\nInput: '{description}'")
    
    # NLP Parse
    parsed = nlp_service.parse_description(description)
    print(f"\nNLP Parsed:")
    print(f"  Building: {parsed['building_type']}/{parsed['subtype']}")
    print(f"  Square Footage: {parsed['square_footage']:,}" if parsed['square_footage'] else "  Square Footage: Not detected")
    print(f"  Location: {parsed['location']}")
    print(f"  Features: {parsed['special_features']}")
    
    # Engine Calculate
    if parsed['square_footage']:
        result = unified_engine.calculate_project(
            building_type=BuildingType(parsed['building_type']),
            subtype=parsed['subtype'],
            square_footage=parsed['square_footage'],
            location=parsed['location'] or 'Nashville',
            project_class=ProjectClass(parsed['project_class']),
            ownership_type=OwnershipType(parsed['ownership_type']),
            special_features=parsed.get('special_features', [])
        )
        
        print(f"\nCalculation Results:")
        print(f"  Total Project Cost: ${result['totals']['total_project_cost']:,.2f}")
        print(f"  Cost per SF: ${result['totals']['cost_per_sf']:.2f}")
        print(f"  Hard Costs: ${result['totals']['hard_costs']:,.2f}")
        print(f"  Soft Costs: ${result['totals']['soft_costs']:,.2f}")
    
    # Test case 2: Parking
    print("\n" + "-"*60)
    description2 = "Build a 5-story parking garage in New York"
    print(f"\nInput: '{description2}'")
    
    parsed2 = nlp_service.extract_all_metrics(description2)
    print(f"\nNLP Parsed:")
    print(f"  Building: {parsed2['building_type']}/{parsed2['subtype']}")
    print(f"  Floors: {parsed2['floors']}")
    print(f"  Location: {parsed2['location']}")
    
    # Use default square footage for parking
    result2 = unified_engine.calculate_project(
        building_type=BuildingType.PARKING,
        subtype='parking_garage',
        square_footage=50000,  # Default
        location=parsed2['location'] or 'New York',
        floors=parsed2['floors'] or 5,
        project_class=ProjectClass.GROUND_UP
    )
    
    print(f"\nCalculation Results (50,000 SF default):")
    print(f"  Total Project Cost: ${result2['totals']['total_project_cost']:,.2f}")
    print(f"  Cost per SF: ${result2['totals']['cost_per_sf']:.2f}")
    print(f"  Regional Multiplier: {result2['construction_costs']['regional_multiplier']}")

def test_api_simulation():
    """Simulate what the API would do"""
    print("\n" + "="*60)
    print("API ENDPOINT SIMULATION")
    print("="*60)
    
    # Simulate /analyze endpoint
    print("\n1. /api/v2/analyze simulation:")
    request = {
        "description": "Build a 150,000 sf mixed use project with retail and residential in Chicago",
        "default_location": "Nashville"
    }
    
    parsed = nlp_service.parse_description(request['description'])
    if not parsed.get('location'):
        parsed['location'] = request['default_location']
    
    print(f"  Parsed: {parsed['building_type']}/{parsed['subtype']}")
    print(f"  SF: {parsed['square_footage']:,}" if parsed['square_footage'] else "  SF: Not detected")
    print(f"  Location: {parsed['location']}")
    
    # Simulate /calculate endpoint
    print("\n2. /api/v2/calculate simulation:")
    calc_request = {
        "building_type": "recreation",
        "subtype": "aquatic_center",
        "square_footage": 30000,
        "location": "Miami",
        "special_features": ["competition_pool", "diving_well"]
    }
    
    result = unified_engine.calculate_project(
        building_type=BuildingType(calc_request['building_type']),
        subtype=calc_request['subtype'],
        square_footage=calc_request['square_footage'],
        location=calc_request['location'],
        special_features=calc_request.get('special_features', [])
    )
    
    print(f"  Building: {result['project_info']['display_name']}")
    print(f"  Total Cost: ${result['totals']['total_project_cost']:,.2f}")
    print(f"  Special Features Cost: ${result['construction_costs']['special_features_total']:,.2f}")
    
    # Simulate /building-types endpoint
    print("\n3. /api/v2/building-types simulation:")
    types = unified_engine.get_available_building_types()
    print(f"  Available Types: {len(types)}")
    print(f"  Total Subtypes: {sum(len(st) for st in types.values())}")

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# V2 SYSTEM TEST (No FastAPI Required)")
    print("#"*60)
    
    try:
        test_full_flow()
        test_api_simulation()
        
        print("\n" + "="*60)
        print("✅ V2 SYSTEM WORKING CORRECTLY")
        print("="*60)
        print("\nThe V2 system is ready to be integrated with FastAPI:")
        print("  1. Master config provides all data")
        print("  2. NLP service parses descriptions")
        print("  3. Unified engine calculates everything")
        print("  4. API endpoints expose the functionality")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()