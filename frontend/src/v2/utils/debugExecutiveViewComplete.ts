export const debugExecutiveViewComplete = (project: any) => {
  console.group('🔍 Executive View Complete Debug');
  
  console.log('1. Raw project data:', project);
  
  const buildingType = project?.analysis?.parsed?.building_type;
  const buildingSubtype = project?.analysis?.parsed?.building_subtype;
  
  console.log('2. Building Type:', buildingType);
  console.log('3. Building Subtype:', buildingSubtype);
  
  // Check if it's detecting as multifamily
  if (buildingType === 'multifamily') {
    console.log('✅ Correctly identified as MULTIFAMILY');
  } else {
    console.error('❌ NOT identified as multifamily, got:', buildingType);
  }
  
  // Check calculations
  console.log('4. Calculations:', project?.analysis?.calculations);
  
  // Check what getMetrics would return
  const isMultifamily = buildingType === 'multifamily';
  console.log('5. Should show apartment metrics?', isMultifamily);
  
  console.groupEnd();
};