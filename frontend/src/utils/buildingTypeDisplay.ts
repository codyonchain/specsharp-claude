/**
 * Utility function to get a user-friendly display name for the building type
 */
export const getDisplayBuildingType = (requestData: any): string => {
  const occupancyType = requestData?.occupancy_type?.toLowerCase();
  
  // For specific building types, always show their actual type
  if (occupancyType === 'healthcare') {
    return 'Healthcare';
  }
  
  if (occupancyType === 'educational') {
    return 'Educational';
  }
  
  if (occupancyType === 'retail') {
    return 'Retail';
  }
  
  if (occupancyType === 'office') {
    return 'Office';
  }
  
  // Check if this is a restaurant
  if (occupancyType === 'restaurant' || 
      (requestData.building_mix && requestData.building_mix.restaurant >= 0.5)) {
    // Get service level if available
    const serviceLevel = requestData.service_level || 'full_service';
    const displayLevel = serviceLevel.replace('_', ' ')
      .split(' ')
      .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    return `Restaurant - ${displayLevel}`;
  }
  
  // For mixed use warehouse/office
  if (occupancyType === 'warehouse' && requestData.building_mix && requestData.building_mix.office) {
    const officePercent = Math.round(requestData.building_mix.office * 100);
    const warehousePercent = 100 - officePercent;
    return `Mixed Use (${warehousePercent}% Warehouse, ${officePercent}% Office)`;
  }
  
  // For pure warehouse
  if (occupancyType === 'warehouse') {
    return 'Warehouse';
  }
  
  // For mixed use projects
  if (requestData.project_type === 'mixed_use' && requestData.building_mix) {
    const types = Object.entries(requestData.building_mix)
      .map(([type, percentage]) => `${Math.round((percentage as number) * 100)}% ${type.charAt(0).toUpperCase() + type.slice(1)}`)
      .join(', ');
    return `Mixed Use (${types})`;
  }
  
  // Default to formatted project type
  return requestData.project_type.replace('_', ' ')
    .split(' ')
    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};