"""
Centralized building type detection module
Ensures consistent detection across backend services
"""

def determine_building_type(description: str) -> str:
    """
    Determine building type from description using priority order.
    Specific types are checked before generic to avoid false matches.
    
    Args:
        description: Natural language description of the building
        
    Returns:
        Building type: 'healthcare', 'educational', 'restaurant', 'warehouse', 'retail', or 'commercial'
    """
    if not description:
        return 'commercial'
        
    description_lower = description.lower()
    
    # Check in priority order - specific types BEFORE generic
    
    # 1. Healthcare (FIRST PRIORITY)
    if any(term in description_lower for term in [
        'hospital', 'medical', 'healthcare', 'health care', 'clinic', 
        'surgery center', 'surgery', 'surgical', 'patient', 'beds', 
        'operating room', 'or suite', 'emergency', 'emergency department',
        'imaging', 'radiology', 'laboratory', 'lab', 'pharmacy', 
        'rehabilitation', 'rehab', 'urgent care', 'doctor', 'nurse',
        'icu', 'intensive care', 'recovery', 'treatment'
    ]):
        return 'healthcare'
    
    # 2. Educational
    if any(term in description_lower for term in [
        'school', 'elementary', 'middle school', 'high school',
        'classroom', 'education', 'educational', 'academy', 
        'university', 'college', 'campus', 'student', 'teaching',
        'kindergarten', 'preschool', 'daycare', 'learning center'
    ]):
        return 'educational'
    
    # 3. Restaurant (but not if it's primarily something else)
    # Skip if it's a mall/shopping center food court
    if 'mall' not in description_lower and 'shopping center' not in description_lower:
        if any(term in description_lower for term in [
            'restaurant', 'dining', 'food service', 'cafe',
            'cafeteria', 'food court', 'bar', 'brewery', 'bistro',
            'grill', 'diner', 'tavern', 'pub', 'eatery', 'pizzeria',
            'steakhouse', 'buffet', 'catering'
        ]):
            return 'restaurant'
    
    # Also check for standalone restaurant keywords
    if any(term in description_lower for term in [
        'restaurant', 'bistro', 'diner', 'tavern', 'pub', 
        'pizzeria', 'steakhouse'
    ]):
        return 'restaurant'
    
    # 4. Warehouse
    if any(term in description_lower for term in [
        'warehouse', 'distribution', 'storage', 'logistics',
        'fulfillment', 'industrial', 'manufacturing', 'factory',
        'processing', 'assembly', 'production', 'depot'
    ]):
        return 'warehouse'
    
    # 5. Retail
    if any(term in description_lower for term in [
        'retail', 'store', 'shop', 'mall', 'shopping',
        'boutique', 'showroom', 'market', 'outlet', 'department store',
        'convenience store', 'grocery', 'supermarket'
    ]):
        return 'retail'
    
    # 6. Office (before defaulting to commercial)
    if any(term in description_lower for term in [
        'office', 'corporate', 'headquarters', 'workspace',
        'business center', 'professional', 'administrative'
    ]):
        return 'office'
    
    # Default to commercial only if nothing else matches
    return 'commercial'


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
    
    return ''