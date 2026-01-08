"""
Centralized building type detection module
Ensures consistent detection across backend services
"""
from functools import lru_cache


@lru_cache(maxsize=1000)
def determine_building_type(description: str) -> str:
    """
    Determine building type from description using priority order.
    Specific types are checked before generic to avoid false matches.
    
    Args:
        description: Natural language description of the building
        
    Returns:
        Building type: 'multi_family_residential', 'healthcare', 'educational', 'restaurant', 'warehouse', 'retail', 'office', or 'commercial'
    """
    if not description:
        return 'commercial'
        
    description_lower = description.lower()
    
    # Check in priority order - specific types BEFORE generic
    
    # 1. Multi-family Residential (HIGHEST PRIORITY)
    if any(term in description_lower for term in [
        'apartment', 'apartments', 'condo', 'condominium', 'multi-family',
        'multifamily', 'multi family', '1br', '2br', '3br',
        'studio', 'loft', 'duplex', 'triplex', 'fourplex', 'townhome',
        'townhouse', 'residential complex', 'housing complex', 'senior living',
        'assisted living', 'affordable housing', 'mixed income', 'luxury rental',
        'rental property', 'lease', 'amenity', 'amenities',
        'clubhouse', 'leasing office', 'property management'
    ]):
        # Double-check it's not a single-family home or retail tenant
        if not any(term in description_lower for term in [
            'single family', 'single-family', 'detached home', 'sfh',
            'retail tenant', 'strip center', 'strip mall', 'shopping'
        ]):
            return 'multi_family_residential'
    
    # 2. Healthcare
    if any(term in description_lower for term in [
        'hospital', 'medical', 'healthcare', 'health care', 'clinic', 
        'surgery center', 'surgery', 'surgical', 'patient', 'beds', 
        'operating room', 'or suite', 'emergency', 'emergency department',
        'imaging', 'radiology', 'laboratory', 'lab',
        'rehabilitation', 'rehab', 'urgent care', 'doctor', 'nurse',
        'icu', 'intensive care', 'recovery', 'treatment'
    ]):
        # Don't classify as healthcare if it's just a pharmacy in a retail store
        if 'pharmacy' in description_lower and any(term in description_lower for term in ['grocery', 'supermarket', 'retail']):
            pass  # Let it fall through to retail
        else:
            return 'healthcare'
    
    # 2. Educational
    if any(term in description_lower for term in [
        'school', 'elementary', 'middle school', 'high school',
        'classroom', 'education', 'educational', 'academy', 
        'university', 'college', 'campus', 'student', 'teaching',
        'kindergarten', 'preschool', 'daycare', 'learning center'
    ]):
        return 'educational'
    
    # 3. Hospitality/Hotel
    if any(term in description_lower for term in [
        'hotel', 'motel', 'inn', 'resort', 'hospitality',
        'guest room', 'guest rooms', 'guestroom', 'guestrooms',
        'lodging', 'accommodation', 'suite', 'suites',
        'room hotel', 'rooms hotel', 'bed hotel', 'beds hotel',
        'extended stay', 'boutique hotel', 'conference hotel',
        'business hotel', 'luxury hotel', 'budget hotel'
    ]):
        return 'hospitality'
    
    # 4. Restaurant (but be more restrictive to avoid false positives)
    # Skip if it's a mall/shopping center food court or part of another building type
    if 'mall' not in description_lower and 'shopping center' not in description_lower:
        # Check for explicit restaurant keywords
        if any(term in description_lower for term in [
            'restaurant', 'bistro', 'diner', 'tavern', 'pub', 
            'pizzeria', 'steakhouse', 'brewery', 'buffet'
        ]):
            # Double-check it's not part of a larger facility
            if not any(term in description_lower for term in [
                'office building', 'apartment', 'hotel', 'hospital', 
                'school', 'warehouse', 'industrial'
            ]):
                return 'restaurant'
        
        # Only consider broader terms if there are strong restaurant indicators
        elif any(term in description_lower for term in ['commercial kitchen', 'food service facility', 'full-service dining']):
            return 'restaurant'
    
    # 5. Industrial (highest priority among industrial types)
    if any(term in description_lower for term in [
        'industrial', 'manufacturing', 'factory', 'plant',
        'processing', 'assembly', 'production', 'fabrication',
        'clean room', 'pharmaceutical', 'pharma', 'biotech',
        'food processing', 'beverage', 'brewery', 'bottling',
        'data center', 'server room', 'machine shop', 'foundry'
    ]):
        # Don't classify as industrial if it's a grocery/supermarket
        if any(term in description_lower for term in ['grocery', 'supermarket']):
            pass  # Let it fall through to retail
        else:
            return 'industrial'
    
    # 6. Warehouse (generic storage/distribution)
    if any(term in description_lower for term in [
        'warehouse', 'distribution', 'storage', 'logistics',
        'fulfillment', 'depot', 'distribution center'
    ]):
        return 'warehouse'
    
    # 7. Retail (but be careful with specific keywords)
    # Skip if it's primarily a restaurant
    if 'restaurant' not in description_lower:
        if any(term in description_lower for term in [
            'retail', 'store', 'shop', 'mall', 'shopping',
            'boutique', 'showroom', 'market', 'outlet', 'department store',
            'convenience store', 'grocery', 'supermarket', 'strip center',
            'strip mall', 'shopping center', 'anchor', 'inline retail'
        ]):
            return 'retail'
    
    # 8. Office (before defaulting to commercial)
    if any(term in description_lower for term in [
        'office', 'corporate', 'headquarters', 'workspace',
        'business center', 'professional', 'administrative'
    ]):
        return 'office'
    
    # Default to commercial only if nothing else matches
    return 'commercial'


@lru_cache(maxsize=1000)
def get_building_subtype(building_type: str, description: str) -> str:
    """
    Get more specific subtype based on building type and description
    
    Args:
        building_type: Main building type
        description: Natural language description
        
    Returns:
        Building subtype or empty string if none
    """
    description_lower = description.lower()
    
    if building_type == 'healthcare':
        if 'urgent care' in description_lower:
            return 'urgent_care'
        elif 'surgery center' in description_lower:
            return 'surgery_center'
        elif 'clinic' in description_lower:
            return 'clinic'
        elif 'rehab' in description_lower or 'rehabilitation' in description_lower:
            return 'rehabilitation'
        else:
            return 'hospital'
    
    elif building_type == 'educational':
        if 'elementary' in description_lower:
            return 'elementary_school'
        elif 'middle school' in description_lower:
            return 'middle_school'
        elif 'high school' in description_lower:
            return 'high_school'
        elif 'university' in description_lower or 'college' in description_lower:
            return 'higher_education'
        elif 'preschool' in description_lower or 'daycare' in description_lower:
            return 'early_childhood'
        else:
            return 'k12_school'
    
    elif building_type == 'restaurant':
        if any(term in description_lower for term in ['fast food', 'quick service', 'qsr']):
            return 'quick_service'
        elif any(term in description_lower for term in ['fine dining', 'upscale', 'white tablecloth']):
            return 'fine_dining'
        elif any(term in description_lower for term in ['casual dining', 'family restaurant']):
            return 'casual_dining'
        elif 'bar' in description_lower or 'tavern' in description_lower:
            return 'bar_tavern'
        else:
            return 'full_service'
    
    elif building_type == 'industrial':
        if any(term in description_lower for term in ['clean room', 'pharma', 'pharmaceutical', 'biotech']):
            return 'clean_room_pharma'
        elif any(term in description_lower for term in ['food', 'beverage', 'brewery', 'bottling']):
            return 'food_processing'
        elif 'data center' in description_lower:
            return 'data_center'
        elif any(term in description_lower for term in ['machine shop', 'fabrication', 'metalwork']):
            return 'machine_shop'
        else:
            return 'general_manufacturing'
    
    elif building_type == 'hospitality':
        # Check for full service indicators (luxury, upscale, full amenities)
        if any(term in description_lower for term in [
            'luxury', 'five star', '5 star', 'resort', 'convention',
            'full service', 'full-service', 'boutique', 'upscale',
            'conference', 'business', 'design hotel'
        ]):
            return 'full_service_hotel'
        
        # Check for limited service indicators (budget, economy, basic)
        elif any(term in description_lower for term in [
            'limited service', 'limited-service', 'select service',
            'budget', 'economy', 'motel', 'express', 'value',
            'extended stay', 'residence inn'
        ]):
            return 'limited_service_hotel'
        
        # Default to limited service (more common type)
        else:
            return 'limited_service_hotel'
    
    elif building_type == 'retail':
        if any(term in description_lower for term in ['grocery', 'supermarket', 'food market']):
            return 'grocery_store'
        elif any(term in description_lower for term in ['strip center', 'strip mall', 'neighborhood center', 'inline retail']):
            return 'strip_center'
        elif any(term in description_lower for term in ['regional mall', 'shopping mall', 'mall']):
            return 'shopping_mall'
        elif any(term in description_lower for term in ['big box', 'anchor tenant', 'department store']):
            return 'big_box'
        elif any(term in description_lower for term in ['standalone', 'single tenant', 'pad site']):
            return 'standalone_retail'
        else:
            return 'general_retail'
    
    return ''