"""Restaurant-specific mechanical items including kitchen ventilation and HVAC"""
from typing import Dict, List, Any
import math


def get_restaurant_mechanical_items(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate restaurant-specific mechanical items"""
    
    # Get project details
    square_footage = project_data.get('request_data', {}).get('square_footage', 4000)
    
    # Get the actual mechanical budget from the project data
    # First check if we have a mechanical category in the categories
    mechanical_budget = 0
    for category in project_data.get('categories', []):
        cat_name = category['name'].lower()
        if cat_name == 'mechanical' or cat_name.startswith('mechanical'):
            mechanical_budget = category.get('subtotal', 0)
            break
    
    # If no mechanical budget found, use fallback calculation
    if mechanical_budget == 0:
        # Calculate budget allocations
        # For mechanical trade (22% of total project cost)
        # Assuming $400/SF base for full-service restaurant
        total_project_cost = square_footage * 400
        mechanical_budget = total_project_cost * 0.22
    
    print(f"[DEBUG] Restaurant mechanical budget: ${mechanical_budget:,.2f}")
    
    # Kitchen is typically 30% of restaurant
    kitchen_sf = square_footage * 0.3
    dining_sf = square_footage * 0.7
    
    items = []
    
    # KITCHEN VENTILATION SYSTEM (40% of mechanical budget)
    
    # Type I Exhaust Hood System
    hood_length = max(25, kitchen_sf / 40)  # Min 25 LF, typically 30 LF for 4000sf
    items.append({
        'name': 'Type I Exhaust Hood System',
        'quantity': round(hood_length, 1),
        'unit': 'LF',
        'unit_cost': 850,
        'total_cost': hood_length * 850,
        'category': 'Kitchen Ventilation',
        'description': 'Stainless steel Type I exhaust hood with integral filters, lights, and vapor proof construction'
    })
    
    # Make-up Air Unit
    mua_cfm = hood_length * 300  # 300 CFM per linear foot of hood
    items.append({
        'name': 'Make-up Air Unit with Gas Heat',
        'quantity': round(mua_cfm),
        'unit': 'CFM',
        'unit_cost': 4.50,
        'total_cost': mua_cfm * 4.50,
        'category': 'Kitchen Ventilation',
        'description': 'Tempered make-up air unit with modulating gas heat for kitchen hood compensation'
    })
    
    # Ansul Fire Suppression System
    items.append({
        'name': 'Ansul Fire Suppression System',
        'quantity': round(hood_length, 1),
        'unit': 'LF',
        'unit_cost': 225,
        'total_cost': hood_length * 225,
        'category': 'Kitchen Ventilation',
        'description': 'Wet chemical fire suppression system for cooking equipment protection'
    })
    
    # Kitchen Exhaust Ductwork
    duct_weight = kitchen_sf * 0.5  # 0.5 lbs per SF of kitchen
    items.append({
        'name': 'Kitchen Exhaust Ductwork - Welded Black Steel',
        'quantity': round(duct_weight),
        'unit': 'LB',
        'unit_cost': 18.50,
        'total_cost': duct_weight * 18.50,
        'category': 'Kitchen Ventilation',
        'description': 'Fully welded black steel ductwork, liquid tight, with access doors'
    })
    
    # REFRIGERATION SYSTEMS (25% of mechanical budget)
    
    # Walk-in Cooler
    items.append({
        'name': 'Walk-in Cooler (10x12) with Remote Condensing Unit',
        'quantity': 1,
        'unit': 'EA',
        'unit_cost': 18500,
        'total_cost': 18500,
        'category': 'Refrigeration',
        'description': '10x12 walk-in cooler with 4" insulated panels, self-closing door, and remote refrigeration'
    })
    
    # Walk-in Freezer
    items.append({
        'name': 'Walk-in Freezer (8x10) with Remote Condensing Unit',
        'quantity': 1,
        'unit': 'EA',
        'unit_cost': 16500,
        'total_cost': 16500,
        'category': 'Refrigeration',
        'description': '8x10 walk-in freezer with 5" insulated panels, heated door, and remote refrigeration'
    })
    
    # Remote Refrigeration Rack
    items.append({
        'name': 'Remote Refrigeration Rack System',
        'quantity': 1,
        'unit': 'EA',
        'unit_cost': 12500,
        'total_cost': 12500,
        'category': 'Refrigeration',
        'description': 'Parallel rack refrigeration system with digital controls and heat reclaim'
    })
    
    # Beer Cooler (for restaurants with bar)
    if square_footage >= 3000:
        items.append({
            'name': 'Remote Beer Cooler System',
            'quantity': 1,
            'unit': 'EA',
            'unit_cost': 8500,
            'total_cost': 8500,
            'category': 'Refrigeration',
            'description': 'Walk-in beer cooler with glycol system for draft lines'
        })
    
    # HVAC SYSTEMS (30% of mechanical budget)
    
    # Kitchen RTU with 100% Outside Air
    kitchen_tons = kitchen_sf / 200  # Kitchen needs more cooling - 200 SF/ton
    items.append({
        'name': 'Kitchen RTU with 100% Outside Air Capability',
        'quantity': round(kitchen_tons, 1),
        'unit': 'TON',
        'unit_cost': 2850,
        'total_cost': kitchen_tons * 2850,
        'category': 'HVAC Equipment',
        'description': 'Rooftop unit designed for kitchen with 100% OA capability and grease filters'
    })
    
    # Dining Area RTUs
    dining_tons = dining_sf / 350  # Standard 350 SF/ton for dining
    num_units = math.ceil(dining_tons / 5)  # Use 5-ton units
    items.append({
        'name': 'Dining Area RTU Package (5-ton units)',
        'quantity': num_units,
        'unit': 'EA',
        'unit_cost': 10750,  # 5 tons x $2150/ton
        'total_cost': num_units * 10750,
        'category': 'HVAC Equipment',
        'description': 'High-efficiency rooftop units with economizer and demand ventilation'
    })
    
    # DUCTWORK AND DISTRIBUTION (15% of mechanical budget)
    
    # Dining Area Ductwork
    items.append({
        'name': 'Dining Area Supply/Return Ductwork',
        'quantity': dining_sf / 1000,
        'unit': 'Lot',
        'unit_cost': 4500,
        'total_cost': (dining_sf / 1000) * 4500,
        'category': 'Ductwork',
        'description': 'Insulated spiral duct with diffusers and grilles'
    })
    
    # Kitchen Supply Ductwork
    items.append({
        'name': 'Kitchen Supply Ductwork - Stainless',
        'quantity': kitchen_sf / 1000,
        'unit': 'Lot',
        'unit_cost': 3500,
        'total_cost': (kitchen_sf / 1000) * 3500,
        'category': 'Ductwork',
        'description': 'Stainless steel supply ductwork for kitchen area'
    })
    
    # CONTROLS AND ACCESSORIES (10% of mechanical budget)
    
    # Kitchen Hood Controls
    items.append({
        'name': 'Kitchen Hood Controls with Variable Speed',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': 8500,
        'total_cost': 8500,
        'category': 'Controls',
        'description': 'Demand ventilation controls with temperature and smoke sensors'
    })
    
    # Building Management System
    items.append({
        'name': 'Restaurant BMS/Controls Package',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': 15000,
        'total_cost': 15000,
        'category': 'Controls',
        'description': 'DDC controls with kitchen integration and energy management'
    })
    
    # Testing and Balancing
    items.append({
        'name': 'Testing and Balancing',
        'quantity': 1,
        'unit': 'LS',
        'unit_cost': 8500,
        'total_cost': 8500,
        'category': 'Commissioning',
        'description': 'Complete air and water balance with certified reports'
    })
    
    # Calculate current total and add adjustment if needed
    current_total = sum(item['total_cost'] for item in items)
    if current_total < mechanical_budget:
        # Add miscellaneous mechanical items to reach budget
        remaining = mechanical_budget - current_total
        items.append({
            'name': 'Additional Mechanical Equipment and Accessories',
            'quantity': 1,
            'unit': 'LS',
            'unit_cost': remaining,
            'total_cost': remaining,
            'category': 'Equipment',
            'description': 'Pipe insulation, vibration isolation, access panels, and accessories'
        })
    
    return items