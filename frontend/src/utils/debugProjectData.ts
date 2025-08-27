/**
 * Debug utility to log project data structure
 */
export function debugProjectData(project: any, label: string = 'Project Data') {
  console.group(`🔍 ${label}`);
  
  // Log basic info
  console.log('ID:', project?.id || project?.project_id);
  console.log('Name:', project?.name);
  console.log('Type:', project?.building_type || project?.project_type);
  console.log('Square Footage:', project?.square_footage);
  console.log('Location:', project?.location);
  
  // Log cost data with all possible field names
  console.group('💰 Cost Data:');
  console.log('total_project_cost:', project?.total_project_cost);
  console.log('totalCost:', project?.totalCost);
  console.log('total_cost:', project?.total_cost);
  console.log('cost_breakdown.total:', project?.cost_breakdown?.total);
  console.log('costBreakdown.total:', project?.costBreakdown?.total);
  console.groupEnd();
  
  // Log construction costs
  console.group('🏗️ Construction Costs:');
  console.log('construction_cost:', project?.construction_cost);
  console.log('constructionCost:', project?.constructionCost);
  console.log('soft_costs:', project?.soft_costs);
  console.log('softCosts:', project?.softCosts);
  console.log('contingency:', project?.contingency);
  console.log('contingency_amount:', project?.contingency_amount);
  console.groupEnd();
  
  // Log per-sqft costs
  console.group('📊 Per Square Foot:');
  console.log('cost_per_sqft:', project?.cost_per_sqft);
  console.log('costPerSqft:', project?.costPerSqft);
  console.log('cost_breakdown.costPerSqft:', project?.cost_breakdown?.costPerSqft);
  console.groupEnd();
  
  // Log financial metrics
  console.group('📈 Financial Metrics:');
  console.log('roi:', project?.roi);
  console.log('payback_period:', project?.payback_period);
  console.log('paybackPeriod:', project?.paybackPeriod);
  console.groupEnd();
  
  // Log the full object
  console.log('Full Project Object:', project);
  
  console.groupEnd();
  
  // Return the most likely total cost
  return {
    totalCost: project?.total_project_cost || 
               project?.totalCost || 
               project?.total_cost || 
               project?.cost_breakdown?.total ||
               project?.costBreakdown?.total ||
               0,
    costPerSqft: project?.cost_per_sqft || 
                 project?.costPerSqft || 
                 project?.cost_breakdown?.costPerSqft ||
                 project?.costBreakdown?.costPerSqft ||
                 0,
    squareFootage: project?.square_footage || 0
  };
}