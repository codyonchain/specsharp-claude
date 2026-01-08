export const debugProjectData = (project: any) => {
  console.group('🔍 Project Data Structure');
  console.log('Building Type:', project.analysis?.parsed?.building_type);
  console.log('Building Subtype:', project.analysis?.parsed?.building_subtype);
  console.log('Construction Total:', project.analysis?.calculations?.construction_costs?.construction_total);
  console.log('Soft Costs Total:', project.analysis?.calculations?.soft_costs?.total);
  console.log('Trade Breakdown:', project.analysis?.calculations?.trade_breakdown);
  console.log('Full Project:', project);
  console.groupEnd();
};