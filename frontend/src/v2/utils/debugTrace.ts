// Debug utility to trace data flow
export const debugTrace = (location: string, data: any) => {
  console.group(`🔍 DEBUG: ${location}`);
  console.log('Building Type:', data.building_type || data.buildingType || 'NOT SET');
  console.log('Building Subtype:', data.building_subtype || data.buildingSubtype || 'NOT SET');
  console.log('Full Data:', data);
  console.groupEnd();
};