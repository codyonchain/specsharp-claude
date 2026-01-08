export const findMissingFeatures = (project: any) => {
  console.group('🔍 MISSING FEATURES CHECK');
  
  // Check what data we have
  console.log('Project data:', project);
  
  // Check for special features in various places
  const possibleLocations = [
    'analysis.special_features',
    'analysis.specialFeatures',
    'analysis.parsed.special_features',
    'analysis.parsed.specialFeatures',
    'analysis.calculations.special_features',
    'analysis.calculations.specialFeatures',
    'special_features',
    'specialFeatures'
  ];
  
  possibleLocations.forEach(path => {
    const value = path.split('.').reduce((obj, key) => obj?.[key], project);
    if (value) {
      console.log(`✅ Found at ${path}:`, value);
    }
  });
  
  // Check calculations
  if (project?.analysis?.calculations) {
    console.log('Calculations:', project.analysis.calculations);
    if (project.analysis.calculations.special_features_cost) {
      console.log('✅ Special features cost:', project.analysis.calculations.special_features_cost);
    }
  }
  
  console.groupEnd();
};