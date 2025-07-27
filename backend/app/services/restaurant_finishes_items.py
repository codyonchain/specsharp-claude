"""Restaurant-specific finishes items including kitchen equipment"""
from typing import Dict, List, Any


def get_restaurant_finishes_items(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate restaurant-specific finishes items including kitchen equipment"""
    
    # Get project details
    square_footage = project_data.get('request_data', {}).get('square_footage', 4000)
    
    # Get the actual finishes budget from the project data
    # First check if we have a finishes category in the categories
    finishes_budget = 0
    for category in project_data.get('categories', []):
        if category['name'].lower() == 'finishes':
            finishes_budget = category.get('subtotal', 0)
            break
    
    # If no finishes budget found, use fallback calculation
    if finishes_budget == 0:
        # Calculate budget allocations
        # For finishes trade (25% of total project cost)
        # Assuming $400/SF base for full-service restaurant
        total_project_cost = square_footage * 400
        finishes_budget = total_project_cost * 0.25
    
    print(f"[DEBUG] Restaurant finishes budget: ${finishes_budget:,.2f}")
    
    items = []
    
    # KITCHEN EQUIPMENT (40% of finishes budget)
    kitchen_equipment_budget = finishes_budget * 0.40
    items.append({
        'name': 'Commercial Kitchen Equipment Package',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': kitchen_equipment_budget,
        'total_cost': kitchen_equipment_budget,
        'category': 'Kitchen Equipment',
        'description': 'Complete cooking line including range, grill, fryer, convection ovens, salamander, prep equipment, refrigeration, dishwasher, and smallwares'
    })
    
    # BAR EQUIPMENT (15% of finishes budget)
    bar_equipment_budget = finishes_budget * 0.15
    items.append({
        'name': 'Bar Equipment and Fixtures Package',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': bar_equipment_budget,
        'total_cost': bar_equipment_budget,
        'category': 'Bar Equipment',
        'description': 'Bar refrigeration units, glass washers, ice machines, beer tap system, speed rails, and bar tools'
    })
    
    # DINING FURNITURE (20% of finishes budget)
    seats = round(square_footage / 15)  # Typical 15 SF per seat
    furniture_budget = finishes_budget * 0.20
    items.append({
        'name': f'Dining Furniture Package ({seats} seats)',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': furniture_budget,
        'total_cost': furniture_budget,
        'category': 'Furniture',
        'description': 'Dining tables, chairs, booths, host stand, wait stations, and decorative elements'
    })
    
    # POS SYSTEM (5% of finishes budget)
    pos_budget = finishes_budget * 0.05
    items.append({
        'name': 'POS System with Kitchen Display',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': pos_budget,
        'total_cost': pos_budget,
        'category': 'Technology',
        'description': '4 POS terminals, kitchen display system, printers, and software setup'
    })
    
    # ARCHITECTURAL FINISHES (20% of finishes budget)
    arch_finishes_budget = finishes_budget * 0.20
    
    # Flooring
    items.append({
        'name': 'Restaurant Flooring - Quarry Tile Kitchen/LVT Dining',
        'quantity': square_footage,
        'unit': 'SF',
        'unit_cost': (arch_finishes_budget * 0.40) / square_footage,
        'total_cost': arch_finishes_budget * 0.40,
        'category': 'Flooring',
        'description': 'Non-slip quarry tile in kitchen areas, luxury vinyl tile in dining areas'
    })
    
    # Wall finishes
    wall_area = square_footage * 3  # Approximate wall area
    items.append({
        'name': 'Wall Finishes - FRP Kitchen/Decorative Dining',
        'quantity': wall_area,
        'unit': 'SF',
        'unit_cost': (arch_finishes_budget * 0.30) / wall_area,
        'total_cost': arch_finishes_budget * 0.30,
        'category': 'Wall Finishes',
        'description': 'Fiberglass reinforced panels in kitchen, decorative finishes in dining'
    })
    
    # Ceiling
    items.append({
        'name': 'Ceiling - Washable Kitchen/Acoustic Dining',
        'quantity': square_footage,
        'unit': 'SF',
        'unit_cost': (arch_finishes_budget * 0.30) / square_footage,
        'total_cost': arch_finishes_budget * 0.30,
        'category': 'Ceiling',
        'description': 'Washable vinyl-faced tiles in kitchen, acoustic tiles in dining'
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