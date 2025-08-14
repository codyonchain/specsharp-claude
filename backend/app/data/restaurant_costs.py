"""
Restaurant construction cost data
Based on RSMeans 2024 data and industry benchmarks
Uses base costs + regional multipliers approach
"""

# Base construction costs per SF (no equipment, no regional adjustment)
BASE_CONSTRUCTION_COSTS = {
    'quick_service': {
        'base': 280,
        'with_drive_through': 315,  # +$35/SF for drive-through infrastructure
    },
    'full_service': {
        'base': 225,  # Casual dining
        'casual': 225,
        'upscale': 275  # Higher-end casual
    },
    'fine_dining': {
        'base': 350,
        'steakhouse': 375,
        'chef_driven': 400
    },
    'specialty': {
        'pizza': 240,
        'coffee_shop': 200,
        'brewery': 300,
        'food_hall_per_vendor': 180,
        'ghost_kitchen': 220
    }
}

# Regional multipliers (Nashville = 1.00 baseline)
REGIONAL_MULTIPLIERS = {
    'nashville_tn': 1.00,  # Baseline
    'franklin_tn': 1.02,   # 2% premium area
    'murfreesboro_tn': 0.97,  # 3% less expensive
    'brentwood_tn': 1.04,  # 4% premium area
    'manchester_nh': 0.95,  # 5% less than Nashville
    'nashua_nh': 0.93,     # 7% less than Nashville
    'concord_nh': 0.91,    # 9% less than Nashville
    'default': 1.00        # Default to Nashville baseline
}

# Legacy structure for compatibility - will be calculated from base + multiplier
RESTAURANT_COSTS = {}

# Build the legacy structure
for city, multiplier in REGIONAL_MULTIPLIERS.items():
    RESTAURANT_COSTS[city] = {
        'quick_service': {
            'base': int(BASE_CONSTRUCTION_COSTS['quick_service']['base'] * multiplier),
            'with_drive_through': int(BASE_CONSTRUCTION_COSTS['quick_service']['with_drive_through'] * multiplier),
            'franchise_premium': 1.15 if city != 'default' else 1.10
        },
        'full_service': {
            'base': int(BASE_CONSTRUCTION_COSTS['full_service']['base'] * multiplier),
            'casual': int(BASE_CONSTRUCTION_COSTS['full_service']['casual'] * multiplier),
            'upscale': int(BASE_CONSTRUCTION_COSTS['full_service']['upscale'] * multiplier)
        },
        'fine_dining': {
            'base': int(BASE_CONSTRUCTION_COSTS['fine_dining']['base'] * multiplier),
            'steakhouse': int(BASE_CONSTRUCTION_COSTS['fine_dining']['steakhouse'] * multiplier),
            'chef_driven': int(BASE_CONSTRUCTION_COSTS['fine_dining']['chef_driven'] * multiplier)
        },
        'specialty': {
            'pizza': int(BASE_CONSTRUCTION_COSTS['specialty']['pizza'] * multiplier),
            'coffee_shop': int(BASE_CONSTRUCTION_COSTS['specialty']['coffee_shop'] * multiplier),
            'brewery': int(BASE_CONSTRUCTION_COSTS['specialty']['brewery'] * multiplier),
            'food_hall_per_vendor': int(BASE_CONSTRUCTION_COSTS['specialty']['food_hall_per_vendor'] * multiplier),
            'ghost_kitchen': int(BASE_CONSTRUCTION_COSTS['specialty']['ghost_kitchen'] * multiplier)
        }
    }

# Kitchen equipment costs (FIXED - not affected by region)
KITCHEN_EQUIPMENT = {
    'qsr_basic': {
        'grill': 12000,
        'fryer': 8000,
        'refrigeration': 15000,
        'prep_equipment': 8000,
        'ventilation_hood': 10000
    },
    'full_service': {
        'grill_station': 25000,
        'fryer_station': 15000,
        'refrigeration': 35000,
        'prep_stations': 20000,
        'dish_machine': 25000,
        'ventilation_system': 30000,
        'small_equipment': 30000
    },
    'fine_dining': {
        'premium_grill_station': 45000,
        'specialized_cooking': 35000,
        'refrigeration': 50000,
        'prep_stations': 35000,
        'dish_systems': 40000,
        'ventilation_system': 45000,
        'specialty_equipment': 50000,
        'wine_storage': 20000
    },
    'pizza': {
        'pizza_oven': 35000,
        'dough_mixer': 8000,
        'prep_table': 12000,
        'refrigeration': 15000
    },
    'brewery': {
        'brewing_system_7bbl': 150000,
        'fermenters': 45000,
        'keg_system': 25000,
        'cold_storage': 35000
    },
    'coffee': {
        'espresso_machines': 25000,
        'grinders': 8000,
        'brewing_equipment': 12000,
        'refrigeration': 8000,
        'display_cases': 6000
    },
    'bar': {
        'basic': 35000,
        'full': 75000,
        'premium': 125000
    }
}

# Drive-through costs (infrastructure, not equipment)
DRIVE_THROUGH_COSTS = {
    'basic': {
        'canopy': 12000,
        'menu_boards': 8000,
        'ordering_system': 15000,
        'window_setup': 5000,
        'pavement_marking': 5000
    },
    'premium': {
        'canopy': 20000,
        'digital_menu_boards': 15000,
        'ordering_system': 25000,
        'window_setup': 8000,
        'pavement_marking': 7000
    }
}

# Seating ratios by restaurant type
SEATING_RATIOS = {
    'quick_service': {'sf_per_seat': 15, 'max_seats': 60},
    'full_service': {'sf_per_seat': 20, 'max_seats': None},
    'fine_dining': {'sf_per_seat': 25, 'max_seats': None},
    'bar_focused': {'sf_per_seat': 18, 'max_seats': None},
    'coffee_shop': {'sf_per_seat': 20, 'max_seats': 40},
    'pizza': {'sf_per_seat': 18, 'max_seats': None}
}

# Trade percentage breakdowns (percentages of construction cost)
TRADE_PERCENTAGES = {
    'quick_service': {
        'structural': 0.12,
        'mechanical': 0.28,  # Heavy HVAC for kitchen
        'electrical': 0.20,
        'plumbing': 0.18,
        'finishes': 0.14,
        'general_conditions': 0.08
    },
    'full_service': {
        'structural': 0.10,
        'mechanical': 0.26,
        'electrical': 0.18,
        'plumbing': 0.18,
        'finishes': 0.22,  # Higher finishes
        'general_conditions': 0.06
    },
    'fine_dining': {
        'structural': 0.08,
        'mechanical': 0.24,
        'electrical': 0.16,
        'plumbing': 0.15,
        'finishes': 0.30,  # Premium finishes
        'general_conditions': 0.07
    },
    'specialty': {
        'structural': 0.12,
        'mechanical': 0.25,
        'electrical': 0.18,
        'plumbing': 0.17,
        'finishes': 0.20,
        'general_conditions': 0.08
    }
}

# Feature adjustments (multiplicative)
FEATURE_ADJUSTMENTS = {
    'outdoor_seating': 1.05,  # 5% premium
    'rooftop_dining': 1.08,   # 8% premium
    'waterfront': 1.06,        # 6% premium
    'historic_building': 1.10, # 10% premium for renovation constraints
    'franchise': 1.05,         # 5% for franchise standards
    'drive_through': 1.12      # 12% for drive-through (if not already in base)
}

def get_restaurant_cost(city: str, restaurant_type: str, features: list = None) -> dict:
    """
    Get restaurant construction cost for a specific city and type
    
    Args:
        city: City key (e.g., 'nashville_tn')
        restaurant_type: Type category ('quick_service', 'full_service', 'fine_dining', 'specialty')
        features: List of features (e.g., ['drive_through', 'outdoor_seating'])
    
    Returns:
        Dictionary with cost breakdown
    """
    if city not in RESTAURANT_COSTS:
        city = 'default'
    
    city_costs = RESTAURANT_COSTS[city]
    
    # Get the appropriate cost category
    if restaurant_type in city_costs:
        cost_category = city_costs[restaurant_type]
    elif restaurant_type in ['coffee_shop', 'pizza', 'brewery', 'ghost_kitchen', 'food_hall_per_vendor']:
        # These are specialty subtypes
        specialty = city_costs.get('specialty', {})
        if restaurant_type in specialty:
            # Return a dict-like structure for compatibility
            cost_category = {'base': specialty[restaurant_type]}
        else:
            cost_category = city_costs.get('full_service', city_costs['quick_service'])
    else:
        # Default to full_service if type not found
        cost_category = city_costs.get('full_service', city_costs['quick_service'])
    
    # Get base cost
    features = features or []
    
    # Check for specific sub-types
    if 'drive_through' in features and 'with_drive_through' in cost_category:
        base_cost = cost_category['with_drive_through']
        applied_features = ['drive_through']
    else:
        base_cost = cost_category.get('base', 300)
        applied_features = []
        # Apply drive-through adjustment if not in base
        if 'drive_through' in features and restaurant_type != 'quick_service':
            base_cost = int(base_cost * FEATURE_ADJUSTMENTS['drive_through'])
            applied_features.append('drive_through')
    
    # Apply other feature adjustments
    adjusted_cost = base_cost
    for feature in features:
        if feature in FEATURE_ADJUSTMENTS and feature not in applied_features:
            adjusted_cost = int(adjusted_cost * FEATURE_ADJUSTMENTS[feature])
            applied_features.append(feature)
    
    # Get trade percentages
    trade_pct = TRADE_PERCENTAGES.get(restaurant_type, TRADE_PERCENTAGES['full_service'])
    
    return {
        'base_cost_per_sf': base_cost,
        'adjusted_cost_per_sf': adjusted_cost,
        'trade_percentages': trade_pct,
        'applied_features': applied_features,
        'regional_multiplier': REGIONAL_MULTIPLIERS.get(city, 1.0)
    }

# Equipment cost helper
def get_equipment_cost_per_sf(restaurant_type: str, square_feet: int) -> float:
    """
    Get equipment cost per SF for a restaurant type
    Equipment costs are FIXED and not affected by regional multipliers
    
    Returns cost per SF for equipment and FF&E
    """
    equipment_ranges = {
        'quick_service': (50, 70),     # $50-70/SF
        'full_service': (40, 50),       # $40-50/SF (casual dining)
        'fine_dining': (80, 100),       # $80-100/SF
        'coffee_shop': (40, 60),        # $40-60/SF
        'pizza': (45, 55),               # $45-55/SF
        'brewery': (60, 80),             # $60-80/SF (includes brewing equipment)
        'ghost_kitchen': (65, 75)        # $65-75/SF (equipment-heavy)
    }
    
    # Get the midpoint of the range
    if restaurant_type in equipment_ranges:
        low, high = equipment_ranges[restaurant_type]
        return (low + high) / 2
    else:
        return 45  # Default $45/SF for unknown types