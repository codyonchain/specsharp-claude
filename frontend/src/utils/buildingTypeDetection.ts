/**
 * Building type detection utilities
 */

export function determineOccupancyType(description: string): string {
  if (!description) {
    return 'commercial';
  }
  
  const descriptionLower = description.toLowerCase();
  
  // Check in priority order - specific types BEFORE generic
  
  // 1. Healthcare (FIRST PRIORITY)
  const healthcareKeywords = [
    'hospital', 'medical', 'healthcare', 'health care', 'clinic', 
    'surgery center', 'surgery', 'surgical', 'patient', 'beds', 
    'operating room', 'or suite', 'emergency', 'emergency department',
    'imaging', 'radiology', 'laboratory', 'lab', 'pharmacy', 
    'rehabilitation', 'rehab', 'urgent care', 'doctor', 'nurse',
    'icu', 'intensive care', 'recovery', 'treatment'
  ];
  if (healthcareKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected healthcare facility');
    return 'healthcare';
  }
  
  // 2. Educational
  const educationalKeywords = [
    'school', 'elementary', 'middle school', 'high school',
    'classroom', 'education', 'educational', 'academy', 
    'university', 'college', 'campus', 'student', 'teaching',
    'kindergarten', 'preschool', 'daycare', 'learning center'
  ];
  if (educationalKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected educational facility');
    return 'educational';
  }
  
  // 3. Restaurant
  const restaurantKeywords = [
    'restaurant', 'dining', 'food service', 'kitchen', 'cafe',
    'cafeteria', 'food court', 'bar', 'brewery', 'bistro',
    'grill', 'diner', 'tavern', 'pub', 'eatery', 'pizzeria',
    'steakhouse', 'buffet', 'catering'
  ];
  if (restaurantKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected restaurant');
    return 'restaurant';
  }
  
  // 4. Warehouse
  const warehouseKeywords = [
    'warehouse', 'distribution', 'storage', 'logistics',
    'fulfillment', 'industrial', 'manufacturing', 'factory',
    'processing', 'assembly', 'production', 'depot'
  ];
  if (warehouseKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected warehouse/industrial facility');
    return 'warehouse';
  }
  
  // 5. Retail
  const retailKeywords = [
    'retail', 'store', 'shop', 'mall', 'shopping',
    'boutique', 'showroom', 'market', 'outlet', 'department store',
    'convenience store', 'grocery', 'supermarket'
  ];
  if (retailKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected retail space');
    return 'retail';
  }
  
  // 6. Office (before defaulting to commercial)
  const officeKeywords = [
    'office', 'corporate', 'headquarters', 'workspace',
    'business center', 'professional', 'administrative'
  ];
  if (officeKeywords.some(keyword => descriptionLower.includes(keyword))) {
    console.log('[Building Detection] Detected office building');
    return 'office';
  }
  
  // Default to commercial only if nothing else matches
  console.log('[Building Detection] Defaulting to commercial');
  return 'commercial';
}

export function getProjectTypeFromOccupancy(occupancyType: string): string {
  switch (occupancyType.toLowerCase()) {
    case 'warehouse':
    case 'industrial':
    case 'manufacturing':
      return 'industrial';
    case 'residential':
    case 'apartment':
    case 'home':
      return 'residential';
    default:
      return 'commercial';
  }
}