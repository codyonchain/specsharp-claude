"""Restaurant-specific structural items"""
from typing import Dict, List, Any


def get_restaurant_structural_items(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate restaurant-specific structural items"""
    
    # Get project details
    square_footage = project_data.get('request_data', {}).get('square_footage', 4000)
    
    # Get the actual structural budget from the project data
    structural_budget = 0
    for category in project_data.get('categories', []):
        if category['name'].lower() == 'structural':
            structural_budget = category.get('subtotal', 0)
            break
    
    # If no structural budget found, use fallback calculation
    if structural_budget == 0:
        # For restaurants, structural is typically 10-12% of total project cost
        # Assuming $400/SF base for full-service restaurant
        total_project_cost = square_footage * 400
        structural_budget = total_project_cost * 0.11
    
    
    items = []
    
    # FOUNDATION (35% of structural budget)
    foundation_budget = structural_budget * 0.35
    
    # Kitchen area is typically 30% of total area
    kitchen_area = square_footage * 0.30
    dining_area = square_footage * 0.70
    
    # Reinforced kitchen slab
    kitchen_slab_cost = kitchen_area * 18.00
    items.append({
        'name': 'Reinforced Kitchen Slab for Heavy Equipment',
        'quantity': kitchen_area,
        'unit': 'SF',
        'unit_cost': 18.00,
        'total_cost': kitchen_slab_cost,
        'category': 'Foundation',
        'description': 'Thickened slab with extra rebar for kitchen equipment loads'
    })
    
    # Standard dining slab
    dining_slab_cost = dining_area * 10.00
    items.append({
        'name': 'Standard Slab - Dining Area',
        'quantity': dining_area,
        'unit': 'SF',
        'unit_cost': 10.00,
        'total_cost': dining_slab_cost,
        'category': 'Foundation',
        'description': 'Standard concrete slab for dining areas'
    })
    
    # Grease interceptor pad
    items.append({
        'name': 'Grease Interceptor Concrete Pad',
        'quantity': 1,
        'unit': 'EA',
        'unit_cost': 3500,
        'total_cost': 3500,
        'category': 'Foundation',
        'description': 'Reinforced pad for exterior grease interceptor'
    })
    
    # Walk-in cooler/freezer pads
    items.append({
        'name': 'Walk-in Cooler/Freezer Concrete Pads',
        'quantity': 2,
        'unit': 'EA',
        'unit_cost': 1850,
        'total_cost': 3700,
        'category': 'Foundation',
        'description': 'Insulated concrete pads for walk-in units'
    })
    
    # Equipment pads
    num_equipment_pads = max(4, round(square_footage / 1000))
    items.append({
        'name': 'Exterior Equipment Pads (RTUs, Condensers)',
        'quantity': num_equipment_pads,
        'unit': 'EA',
        'unit_cost': 650,
        'total_cost': num_equipment_pads * 650,
        'category': 'Foundation',
        'description': 'Concrete pads for rooftop units and condensers'
    })
    
    # STRUCTURAL FRAME (40% of structural budget)
    frame_budget = structural_budget * 0.40
    
    # Main structure with kitchen reinforcement
    main_frame_cost = square_footage * 14.00
    items.append({
        'name': 'Structural Steel Frame with Kitchen Reinforcement',
        'quantity': square_footage,
        'unit': 'SF',
        'unit_cost': 14.00,
        'total_cost': main_frame_cost,
        'category': 'Structural Frame',
        'description': 'Extra support for hood, equipment loads'
    })
    
    # Hood support steel
    hood_length = min(30, round(kitchen_area / 40))  # Typical 30 LF for 1200 SF kitchen
    items.append({
        'name': 'Kitchen Hood Support Steel',
        'quantity': hood_length,
        'unit': 'LF',
        'unit_cost': 125,
        'total_cost': hood_length * 125,
        'category': 'Structural Frame',
        'description': 'Structural steel for hood hanging and support'
    })
    
    # Walk-in structure
    items.append({
        'name': 'Walk-in Cooler/Freezer Structural Frame',
        'quantity': 2,
        'unit': 'EA',
        'unit_cost': 2500,
        'total_cost': 5000,
        'category': 'Structural Frame',
        'description': 'Reinforced framing for walk-in boxes'
    })
    
    # Bar structure reinforcement (if applicable)
    if square_footage > 3000:
        items.append({
            'name': 'Bar Area Structural Reinforcement',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': 4500,
            'total_cost': 4500,
            'category': 'Structural Frame',
            'description': 'Additional support for bar equipment and fixtures'
        })
    
    # ROOF STRUCTURE (20% of structural budget)
    roof_budget = structural_budget * 0.20
    
    # Roof deck with equipment considerations
    roof_cost = square_footage * 8.50
    items.append({
        'name': 'Roof Structure with Equipment Curbs',
        'quantity': square_footage,
        'unit': 'SF',
        'unit_cost': 8.50,
        'total_cost': roof_cost,
        'category': 'Roof Structure',
        'description': 'Reinforced roof deck for equipment loads'
    })
    
    # RTU curbs
    num_rtus = max(2, round(square_footage / 2000))
    items.append({
        'name': 'RTU Roof Curbs with Reinforcement',
        'quantity': num_rtus,
        'unit': 'EA',
        'unit_cost': 1250,
        'total_cost': num_rtus * 1250,
        'category': 'Roof Structure',
        'description': 'Structural curbs for rooftop HVAC units'
    })
    
    # Exhaust fan curbs
    items.append({
        'name': 'Exhaust Fan Curbs and Penetrations',
        'quantity': 2,
        'unit': 'EA',
        'unit_cost': 850,
        'total_cost': 1700,
        'category': 'Roof Structure',
        'description': 'Curbs for kitchen and restroom exhaust fans'
    })
    
    # Kitchen roof reinforcement
    kitchen_roof_area = kitchen_area
    items.append({
        'name': 'Kitchen Area Roof Reinforcement',
        'quantity': kitchen_roof_area,
        'unit': 'SF',
        'unit_cost': 6.50,
        'total_cost': kitchen_roof_area * 6.50,
        'category': 'Roof Structure',
        'description': 'Extra structure for kitchen equipment loads'
    })
    
    # MISCELLANEOUS (5% of structural budget)
    misc_budget = structural_budget * 0.05
    
    # Loading dock
    if square_footage >= 3500:
        items.append({
            'name': 'Loading Dock Structure',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': 8500,
            'total_cost': 8500,
            'category': 'Miscellaneous',
            'description': 'Concrete dock with bumpers and approach'
        })
    
    # Dumpster enclosure
    items.append({
        'name': 'Dumpster Enclosure Foundation & Walls',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': 4500,
        'total_cost': 4500,
        'category': 'Miscellaneous',
        'description': 'CMU enclosure with gates'
    })
    
    # Protective bollards
    num_bollards = max(6, round(square_footage / 500))
    items.append({
        'name': 'Protective Bollards',
        'quantity': num_bollards,
        'unit': 'EA',
        'unit_cost': 425,
        'total_cost': num_bollards * 425,
        'category': 'Miscellaneous',
        'description': 'Steel pipe bollards at critical locations'
    })
    
    # Patio structure (if space allows)
    if square_footage >= 4000:
        items.append({
            'name': 'Patio Pergola Structure',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': 6500,
            'total_cost': 6500,
            'category': 'Miscellaneous',
            'description': 'Steel or wood pergola for outdoor dining'
        })
    
    return items


def is_restaurant_project(project_data: Dict[str, Any]) -> bool:
    """Check if this is a restaurant project"""
    request_data = project_data.get('request_data', {})
    
    # Check occupancy type
    if request_data.get('occupancy_type') == 'restaurant':
        return True
    
    # Check building mix
    building_mix = request_data.get('building_mix', {})
    if isinstance(building_mix, dict) and building_mix.get('restaurant', 0) >= 0.5:
        return True
    
    # Check special requirements
    special_requirements = request_data.get('special_requirements', '').lower()
    if 'restaurant' in special_requirements or 'commercial kitchen' in special_requirements:
        return True
    
    return False