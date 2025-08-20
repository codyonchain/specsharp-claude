/**
 * Test file to verify V2 API works
 * Run with: npm run test:v2
 */

import { api } from './api/client';
import { BuildingType, ProjectClass } from './types';

async function testV2API() {
  console.log('Testing V2 API...\n');

  try {
    // 1. Test health endpoint
    console.log('1. Testing health check...');
    const health = await api.health();
    console.log('✅ Health:', health);

    // 2. Test NLP analysis
    console.log('\n2. Testing NLP analysis...');
    const analysis = await api.analyzeProject('Build a 200,000 square foot hospital in Nashville');
    console.log('✅ Analysis:', {
      building_type: analysis.parsed_input.building_type,
      subtype: analysis.parsed_input.subtype,
      total_cost: analysis.calculations.totals.total_project_cost,
      cost_per_sf: analysis.calculations.totals.cost_per_sf,
      confidence: analysis.confidence
    });

    // 3. Test direct calculation
    console.log('\n3. Testing direct calculation...');
    const calculation = await api.calculateProject({
      building_type: BuildingType.MULTIFAMILY,
      subtype: 'luxury_apartments',
      square_footage: 100000,
      location: 'Nashville',
      project_class: ProjectClass.GROUND_UP,
      floors: 5
    });
    console.log('✅ Calculation:', {
      total_cost: calculation.totals.total_project_cost,
      cost_per_sf: calculation.totals.cost_per_sf
    });

    // 4. Test comparison
    console.log('\n4. Testing scenario comparison...');
    const comparison = await api.compareScenarios([
      {
        name: 'Option A',
        building_type: BuildingType.OFFICE,
        subtype: 'class_a',
        square_footage: 50000,
        location: 'Nashville'
      },
      {
        name: 'Option B',
        building_type: BuildingType.OFFICE,
        subtype: 'class_b',
        square_footage: 60000,
        location: 'Nashville'
      }
    ]);
    console.log('✅ Comparison:', comparison.summary);

    console.log('\n✅ All V2 API tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

// Run if executed directly
if (import.meta.env.DEV) {
  testV2API();
}

export { testV2API };