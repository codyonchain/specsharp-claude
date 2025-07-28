"""Utility functions for displaying building types in a user-friendly way"""

def get_display_building_type(request_data: dict) -> str:
    """
    Get a user-friendly display name for the building type.
    
    Args:
        request_data: The request_data dictionary from a project
        
    Returns:
        A formatted string representing the building type
    """
    occupancy_type = request_data.get('occupancy_type', '').lower()
    project_type = request_data.get('project_type', 'commercial')
    building_mix = request_data.get('building_mix', {})
    
    # For specific building types, always show their actual type
    if occupancy_type == 'healthcare':
        return 'Healthcare'
    
    if occupancy_type == 'educational':
        return 'Educational'
    
    if occupancy_type == 'retail':
        return 'Retail'
    
    if occupancy_type == 'office':
        return 'Office'
    
    if occupancy_type == 'multi_family_residential':
        return 'Multi-Family Residential'
    
    if occupancy_type == 'industrial':
        # Check for specific industrial subtypes
        building_subtype = request_data.get('building_subtype', '')
        if building_subtype == 'clean_room_pharma':
            return 'Industrial - Clean Room/Pharma'
        elif building_subtype == 'food_processing':
            return 'Industrial - Food Processing'
        elif building_subtype == 'data_center':
            return 'Industrial - Data Center'
        elif building_subtype == 'machine_shop':
            return 'Industrial - Machine Shop'
        else:
            return 'Industrial - Manufacturing'
    
    # Check if this is a restaurant
    if occupancy_type == 'restaurant' or (building_mix and building_mix.get('restaurant', 0) >= 0.5):
        # Get service level if available
        service_level = request_data.get('service_level', 'full_service')
        display_level = service_level.replace('_', ' ').title()
        return f'Restaurant - {display_level}'
    
    # For mixed use warehouse/office
    if occupancy_type == 'warehouse' and building_mix and building_mix.get('office'):
        office_percent = round(building_mix.get('office', 0) * 100)
        warehouse_percent = 100 - office_percent
        return f'Mixed Use ({warehouse_percent}% Warehouse, {office_percent}% Office)'
    
    # For pure warehouse
    if occupancy_type == 'warehouse':
        return 'Warehouse'
    
    # For mixed use projects
    if project_type == 'mixed_use' and building_mix:
        types = []
        for building_type, percentage in building_mix.items():
            percent = round(percentage * 100)
            formatted_type = building_type.replace('_', ' ').title()
            types.append(f'{percent}% {formatted_type}')
        return f'Mixed Use ({", ".join(types)})'
    
    # Default to formatted project type
    return project_type.replace('_', ' ').title()