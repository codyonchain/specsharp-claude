export const runDiagnostics = () => {
  console.group('🏥 SPECSHARP DIAGNOSTICS');
  
  // Check localStorage
  const projects = localStorage.getItem('specsharp_projects');
  if (projects) {
    const parsed = JSON.parse(projects);
    console.log('Total Projects:', parsed.length);
    
    parsed.forEach((project: any, index: number) => {
      console.group(`Project ${index + 1}: ${project.id}`);
      console.log('Description:', project.description);
      console.log('Building Type (parsed_input):', project.analysis?.parsed_input?.building_type || 'NOT SET');
      console.log('Building Subtype (parsed_input):', project.analysis?.parsed_input?.subtype || 'NOT SET');
      console.log('Building Type (calculations):', project.analysis?.calculations?.project_info?.building_type || 'NOT SET');
      console.log('Square Footage:', project.analysis?.parsed_input?.square_footage);
      
      // Check for healthcare-specific items that shouldn't be in apartments
      const softCosts = project.analysis?.calculations?.soft_costs;
      const hasHealthcareItems = !!(
        softCosts?.['Medical Equipment'] ||
        softCosts?.['Healthcare IT Systems'] ||
        softCosts?.['Clinical Planning']
      );
      
      console.log('Has Healthcare-specific Soft Costs?:', 
        hasHealthcareItems ? 'YES ❌ (PROBLEM!)' : 'NO ✅');
      
      // Check trade breakdown for healthcare-specific items
      const tradeBreakdown = project.analysis?.calculations?.trade_breakdown;
      const hasMedicalGas = !!(tradeBreakdown?.['Medical Gas Systems']);
      console.log('Has Medical Gas Systems in Trades?:', 
        hasMedicalGas ? 'YES ❌ (PROBLEM!)' : 'NO ✅');
      
      console.groupEnd();
    });
  } else {
    console.log('No projects in localStorage');
  }
  
  console.groupEnd();
};

// Add to window for easy console access
if (typeof window !== 'undefined') {
  (window as any).diagnose = runDiagnostics;
  console.log('💡 Diagnostics loaded! Type "diagnose()" in console to run diagnostics');
}