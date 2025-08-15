"""
Regional cost multipliers for different cities/regions.
Easy to update, add new cities, or adjust values.
"""

REGIONAL_MULTIPLIERS = {
    # Northeast - Generally higher costs
    'Boston, MA': 1.18,
    'New York, NY': 1.28,
    'Manhattan, NY': 1.35,
    'Brooklyn, NY': 1.25,
    'Philadelphia, PA': 1.10,
    'Pittsburgh, PA': 1.05,
    'Hartford, CT': 1.08,
    'Newark, NJ': 1.15,
    
    # New England
    'Manchester, NH': 1.00,
    'Portland, ME': 1.02,
    'Burlington, VT': 1.05,
    'Nashua, NH': 0.98,
    'Concord, NH': 0.97,
    
    # Southeast - Generally moderate costs
    'Atlanta, GA': 1.00,
    'Miami, FL': 1.05,
    'Orlando, FL': 1.02,
    'Tampa, FL': 1.00,
    'Jacksonville, FL': 0.98,
    'Charlotte, NC': 0.98,
    'Raleigh, NC': 1.00,
    'Nashville, TN': 1.03,
    'Franklin, TN': 1.03,
    'Murfreesboro, TN': 1.01,
    'Memphis, TN': 0.95,
    'Louisville, KY': 0.96,
    
    # Midwest - Lower costs
    'Chicago, IL': 1.12,
    'Detroit, MI': 1.05,
    'Cleveland, OH': 0.98,
    'Columbus, OH': 0.98,
    'Cincinnati, OH': 0.96,
    'Indianapolis, IN': 0.95,
    'Milwaukee, WI': 1.02,
    'Minneapolis, MN': 1.08,
    'St. Louis, MO': 0.98,
    'Kansas City, MO': 0.96,
    
    # Southwest - Lower costs
    'Dallas, TX': 0.95,
    'Houston, TX': 0.97,
    'San Antonio, TX': 0.93,
    'Austin, TX': 1.02,
    'Phoenix, AZ': 0.95,
    'Tucson, AZ': 0.92,
    'Albuquerque, NM': 0.94,
    'Oklahoma City, OK': 0.92,
    
    # West Coast - Highest costs
    'San Francisco, CA': 1.35,
    'Los Angeles, CA': 1.20,
    'San Diego, CA': 1.15,
    'Sacramento, CA': 1.08,
    'San Jose, CA': 1.30,
    'Oakland, CA': 1.25,
    'Seattle, WA': 1.15,
    'Portland, OR': 1.10,
    'Denver, CO': 1.05,
    'Salt Lake City, UT': 0.98,
    'Las Vegas, NV': 1.02,
    
    # Default fallback
    'default': 1.00
}

def get_regional_multiplier(location: str) -> float:
    """Get multiplier for a location string"""
    if not location:
        return 1.00
    
    # Try exact match first
    location_lower = location.lower()
    for city, multiplier in REGIONAL_MULTIPLIERS.items():
        if city == 'default':
            continue
        city_lower = city.lower()
        # Check if city is in location or location is in city
        if city_lower in location_lower or location_lower in city_lower:
            return multiplier
    
    # Try state match for unknown cities
    state_defaults = {
        'MA': 1.15, 'NY': 1.20, 'CA': 1.18,
        'TX': 0.95, 'FL': 1.00, 'TN': 1.00,
        'NH': 1.00, 'GA': 1.00, 'IL': 1.10,
        'PA': 1.08, 'OH': 0.97, 'NC': 0.99,
        'MI': 1.05, 'WI': 1.02, 'MN': 1.08,
        'AZ': 0.94, 'NM': 0.94, 'OK': 0.92,
        'WA': 1.15, 'OR': 1.10, 'CO': 1.05,
        'UT': 0.98, 'NV': 1.02
    }
    
    for state, default_mult in state_defaults.items():
        if f', {state}' in location or f' {state}' in location:
            return default_mult
    
    return REGIONAL_MULTIPLIERS['default']