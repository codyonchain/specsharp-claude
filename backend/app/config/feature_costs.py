"""
Additional costs for special features by building type.
All values in $/SF to add to base cost.
"""

FEATURE_COSTS = {
    'education': {
        'gymnasium': 25,
        'science_labs': 20,
        'auditorium': 35,
        'cafeteria': 15,
        'library': 12,
        'computer_lab': 18,
        'athletic_field': 10,
        'music_room': 22,
        'art_room': 18,
        'special_education': 25,
        'media_center': 20,
        'playground': 8,
        'multipurpose_room': 15
    },
    
    'healthcare': {
        'emergency_department': 50,
        'operating_rooms': 75,
        'mri_suite': 40,
        'ct_scanner': 35,
        'icu': 60,
        'nicu': 65,
        'catheterization_lab': 55,
        'pharmacy': 20,
        'laboratory': 30,
        'radiology': 45,
        'oncology': 50,
        'dialysis': 40,
        'rehabilitation': 25,
        'behavioral_health': 20,
        'birthing_center': 35,
        'morgue': 15,
        'helipad': 45
    },
    
    'restaurant': {
        'drive_through': 25,
        'outdoor_seating': 15,
        'bar': 20,
        'private_dining': 10,
        'catering_kitchen': 30,
        'wine_cellar': 15,
        'wood_fired_oven': 20,
        'commercial_kitchen': 35,
        'bakery': 25,
        'prep_kitchen': 20,
        'walk_in_freezer': 30,
        'grease_trap': 10,
        'hood_system': 25
    },
    
    'hospitality': {
        'spa': 40,
        'conference_center': 25,
        'rooftop_bar': 35,
        'fitness_center': 20,
        'pool': 30,
        'restaurant': 25,
        'business_center': 15,
        'ballroom': 30,
        'kitchen': 35,
        'laundry': 20,
        'parking_garage': 25,
        'valet': 10,
        'concierge': 8
    },
    
    'office': {
        'data_center': 50,
        'trading_floor': 60,
        'executive_suite': 30,
        'fitness_center': 20,
        'cafeteria': 15,
        'conference_center': 25,
        'auditorium': 28,
        'server_room': 40,
        'call_center': 22,
        'mail_room': 10,
        'loading_dock': 12,
        'security_center': 18,
        'break_room': 8
    },
    
    'industrial': {
        'clean_room': 100,
        'cold_storage': 75,
        'loading_docks': 15,
        'crane_systems': 40,
        'hazmat_storage': 50,
        'rail_siding': 35,
        'truck_wash': 20,
        'battery_charging': 25,
        'compressed_air': 15,
        'dust_collection': 20,
        'paint_booth': 45,
        'welding_area': 30
    },
    
    'residential': {
        'pool': 25,
        'fitness_center': 20,
        'rooftop_deck': 30,
        'concierge': 10,
        'garage_parking': 35,
        'playground': 12,
        'business_center': 15,
        'community_room': 18,
        'dog_park': 8,
        'storage_units': 10,
        'mail_room': 5,
        'security_system': 12
    },
    
    'retail': {
        'loading_dock': 12,
        'storage_mezzanine': 20,
        'fitting_rooms': 15,
        'security_system': 10,
        'display_lighting': 8,
        'point_of_sale': 5,
        'stockroom': 10,
        'customer_service': 8
    },
    
    'mixed_use': {
        'retail_ground_floor': 25,
        'parking_structure': 30,
        'common_areas': 15,
        'mail_room': 8,
        'security_desk': 10,
        'shared_amenities': 20
    }
}

def get_feature_cost(building_type: str, feature: str) -> float:
    """Get cost for a specific feature"""
    # Normalize feature name (remove underscores, spaces, make lowercase)
    normalized_feature = feature.lower().replace(' ', '_').replace('-', '_')
    
    # Try exact building type match first
    if building_type in FEATURE_COSTS:
        if normalized_feature in FEATURE_COSTS[building_type]:
            return FEATURE_COSTS[building_type][normalized_feature]
    
    # Check if it's a common feature that might apply to multiple types
    common_features = {
        'fitness_center': 20,
        'loading_dock': 12,
        'parking': 25,
        'security': 10,
        'cafeteria': 15,
        'conference': 25
    }
    
    for common_feature, cost in common_features.items():
        if common_feature in normalized_feature:
            return cost
    
    return 0

def get_all_features_for_type(building_type: str) -> dict:
    """Get all available features for a building type"""
    return FEATURE_COSTS.get(building_type, {})