"""
Trade cost distribution by building type.
All values are percentages of construction cost.
"""

TRADE_PERCENTAGES = {
    'education': {
        'structural': 30,
        'mechanical': 32,
        'electrical': 8,
        'plumbing': 22,
        'finishes': 8
    },
    
    'healthcare': {
        'structural': 25,
        'mechanical': 35,  # High for air handling, medical gas
        'electrical': 15,  # High for equipment power
        'plumbing': 20,   # Medical gas, special drainage
        'finishes': 5     # Medical-grade but minimal
    },
    
    'restaurant': {
        'structural': 20,
        'mechanical': 25,  # Kitchen ventilation
        'electrical': 15,
        'plumbing': 30,   # Kitchen plumbing intensive
        'finishes': 10
    },
    
    'office': {
        'structural': 35,
        'mechanical': 25,
        'electrical': 15,
        'plumbing': 10,
        'finishes': 15
    },
    
    'industrial': {
        'structural': 45,  # Heavy structure
        'mechanical': 20,
        'electrical': 20,
        'plumbing': 5,
        'finishes': 10
    },
    
    'hospitality': {
        'structural': 30,
        'mechanical': 25,
        'electrical': 12,
        'plumbing': 18,
        'finishes': 15
    },
    
    'residential': {
        'structural': 35,
        'mechanical': 20,
        'electrical': 10,
        'plumbing': 15,
        'finishes': 20  # Higher finishes for residential
    },
    
    'retail': {
        'structural': 30,
        'mechanical': 22,
        'electrical': 18,  # Display lighting
        'plumbing': 10,
        'finishes': 20    # Customer-facing finishes
    },
    
    'mixed_use': {
        'structural': 32,
        'mechanical': 24,
        'electrical': 14,
        'plumbing': 15,
        'finishes': 15
    },
    
    # Specific healthcare subtypes
    'hospital': {
        'structural': 24,
        'mechanical': 38,  # Very high for redundant systems
        'electrical': 18,
        'plumbing': 15,
        'finishes': 5
    },
    
    'surgical_center': {
        'structural': 25,
        'mechanical': 36,  # OR requirements
        'electrical': 16,
        'plumbing': 18,
        'finishes': 5
    },
    
    'medical_office': {
        'structural': 30,
        'mechanical': 28,
        'electrical': 12,
        'plumbing': 15,
        'finishes': 15
    },
    
    # Default distribution
    'default': {
        'structural': 30,
        'mechanical': 25,
        'electrical': 15,
        'plumbing': 15,
        'finishes': 15
    }
}

def get_trade_percentages(building_type: str, subtype: str = None) -> dict:
    """Get trade percentages for a building type"""
    # Try subtype first if provided
    if subtype and subtype in TRADE_PERCENTAGES:
        return TRADE_PERCENTAGES[subtype]
    
    # Then try main building type
    if building_type in TRADE_PERCENTAGES:
        return TRADE_PERCENTAGES[building_type]
    
    # Fall back to default
    return TRADE_PERCENTAGES['default']

def validate_trade_percentages(percentages: dict) -> bool:
    """Validate that trade percentages sum to 100 (excluding GC)"""
    total = sum(percentages.values())
    # Allow for small rounding errors
    return 99 <= total <= 101

def get_adjusted_percentages(building_type: str, has_special_features: list = None) -> dict:
    """Get trade percentages adjusted for special features"""
    base_percentages = get_trade_percentages(building_type)
    
    if not has_special_features:
        return base_percentages
    
    adjusted = base_percentages.copy()
    
    # Adjust based on special features
    feature_adjustments = {
        'data_center': {'mechanical': 5, 'electrical': 5, 'finishes': -10},
        'clean_room': {'mechanical': 8, 'electrical': 2, 'finishes': -10},
        'operating_rooms': {'mechanical': 5, 'electrical': 3, 'plumbing': 2, 'finishes': -10},
        'commercial_kitchen': {'mechanical': 3, 'plumbing': 5, 'electrical': 2, 'finishes': -10},
        'pool': {'mechanical': 2, 'plumbing': 3, 'structural': -5}
    }
    
    for feature in has_special_features:
        if feature in feature_adjustments:
            for trade, adjustment in feature_adjustments[feature].items():
                if trade in adjusted:
                    adjusted[trade] += adjustment
    
    # Normalize to ensure sum is 100
    total = sum(adjusted.values())
    if total != 100:
        factor = 100 / total
        for trade in adjusted:
            adjusted[trade] = round(adjusted[trade] * factor)
    
    return adjusted