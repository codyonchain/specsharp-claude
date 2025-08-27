/**
 * Test Runner for Comprehensive Building Tests
 * Run with: node run-building-tests.js
 */

import fetch from 'node-fetch';

// Test configuration
const API_BASE = 'http://localhost:8001/api/v2';

// Building matrix to test
const BUILDING_MATRIX = [
  // Healthcare
  { type: 'healthcare', subtype: 'hospital', expectedUnits: 'Beds', minCostPerSF: 400 },
  { type: 'healthcare', subtype: 'medical_office', expectedUnits: 'Exam Rooms', minCostPerSF: 250 },
  { type: 'healthcare', subtype: 'urgent_care', expectedUnits: 'Treatment Bays', minCostPerSF: 275 },
  
  // Educational - using subtypes that backend recognizes
  { type: 'educational', subtype: 'school', expectedUnits: 'Classrooms', minCostPerSF: 200 },
  { type: 'educational', subtype: 'university', expectedUnits: 'Students', minCostPerSF: 275 },
  
  // Multifamily
  { type: 'multifamily', subtype: 'luxury_apartments', expectedUnits: 'Units', minCostPerSF: 180 },
  { type: 'multifamily', subtype: 'apartments', expectedUnits: 'Units', minCostPerSF: 140 },
  
  // Office
  { type: 'office', subtype: 'general', expectedUnits: 'Workstations', minCostPerSF: 180 },
];

// Test results storage
const results = [];

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

/**
 * Test a single building configuration
 */
async function testBuildingType(config) {
  const result = {
    building: config.type,
    subtype: config.subtype,
    passed: true,
    errors: [],
    warnings: []
  };
  
  console.log(`\n${colors.cyan}Testing ${config.type}/${config.subtype}...${colors.reset}`);
  
  try {
    // Make API call
    const response = await fetch(`${API_BASE}/scope/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description: `Build a 100000 square foot ${config.subtype} ${config.type} building in Nashville`,
        square_footage: 100000,
        location: 'Nashville, TN'
      })
    });
    
    if (!response.ok) {
      result.errors.push(`API call failed: ${response.status}`);
      result.passed = false;
      return result;
    }
    
    const data = await response.json();
    
    // Validate calculations
    const calcs = data.calculations || {};
    const totals = calcs.totals || {};
    
    // Check cost per SF
    if (totals.cost_per_sf < config.minCostPerSF) {
      result.warnings.push(`Cost/SF ($${totals.cost_per_sf}) below expected minimum ($${config.minCostPerSF})`);
    }
    
    // Check totals math
    const hardCosts = totals.hard_costs || 0;
    const softCosts = totals.soft_costs || 0;
    const totalProject = totals.total_project_cost || 0;
    
    if (Math.abs(hardCosts + softCosts - totalProject) > 1) {
      result.errors.push(`Total mismatch: ${hardCosts} + ${softCosts} ≠ ${totalProject}`);
      result.passed = false;
    }
    
    // Check for equipment costs
    const equipment = calcs.construction_costs?.equipment_total || 0;
    if (equipment <= 0 && config.type !== 'warehouse') {
      result.warnings.push('No equipment cost found');
    }
    
    // Check departments sum to 100%
    const departments = calcs.department_allocation || [];
    if (departments.length > 0) {
      const deptSum = departments.reduce((sum, dept) => sum + (dept.percent || 0), 0);
      if (Math.abs(deptSum - 1.0) > 0.01) {
        result.errors.push(`Departments sum to ${(deptSum * 100).toFixed(1)}%, not 100%`);
        result.passed = false;
      }
    }
    
    // Check trades sum to construction total
    const trades = calcs.trade_breakdown || {};
    const tradeSum = Object.values(trades).reduce((sum, val) => sum + (val || 0), 0);
    const constructionTotal = calcs.construction_costs?.construction_total || 0;
    
    if (Math.abs(tradeSum - constructionTotal) > 1) {
      result.errors.push(`Trades sum ($${tradeSum}) ≠ construction total ($${constructionTotal})`);
      result.passed = false;
    }
    
    // Check financial metrics exist
    const ownership = calcs.ownership_analysis || {};
    if (ownership.roi === undefined) {
      result.errors.push('ROI not calculated');
      result.passed = false;
    }
    if (!ownership.investment_decision) {
      result.errors.push('Investment decision missing');
      result.passed = false;
    }
    
    // Check for hardcoded values
    const jsonString = JSON.stringify(data);
    if (jsonString.includes('3500') || jsonString.includes('1100')) {
      result.warnings.push('Possible hardcoded values detected');
    }
    if (jsonString.includes('NaN') || jsonString.includes('null')) {
      result.errors.push('Invalid values (NaN/null) in response');
      result.passed = false;
    }
    
  } catch (error) {
    result.errors.push(`Test failed: ${error.message}`);
    result.passed = false;
  }
  
  return result;
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log(`${colors.bold}${colors.blue}${'='.repeat(60)}`);
  console.log('🏗️  COMPREHENSIVE BUILDING TYPE TEST SUITE');
  console.log(`${'='.repeat(60)}${colors.reset}\n`);
  
  // Test each building configuration
  for (const config of BUILDING_MATRIX) {
    const result = await testBuildingType(config);
    results.push(result);
    
    // Print immediate result
    if (result.passed) {
      console.log(`${colors.green}✅ PASSED${colors.reset}`);
    } else {
      console.log(`${colors.red}❌ FAILED${colors.reset}`);
      result.errors.forEach(err => console.log(`   ${colors.red}• ${err}${colors.reset}`));
    }
    if (result.warnings.length > 0) {
      result.warnings.forEach(warn => console.log(`   ${colors.yellow}⚠ ${warn}${colors.reset}`));
    }
  }
  
  // Print summary
  printSummary();
}

/**
 * Print test summary
 */
function printSummary() {
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const totalWarnings = results.reduce((sum, r) => sum + r.warnings.length, 0);
  
  console.log(`\n${colors.bold}${colors.blue}${'='.repeat(60)}`);
  console.log('📊 TEST RESULTS SUMMARY');
  console.log(`${'='.repeat(60)}${colors.reset}\n`);
  
  console.log(`${colors.green}✅ Passed: ${passed}/${results.length}${colors.reset}`);
  console.log(`${colors.red}❌ Failed: ${failed}/${results.length}${colors.reset}`);
  console.log(`${colors.yellow}⚠️  Warnings: ${totalWarnings}${colors.reset}`);
  
  // List failures
  if (failed > 0) {
    console.log(`\n${colors.red}${colors.bold}Failed Tests:${colors.reset}`);
    results.filter(r => !r.passed).forEach(r => {
      console.log(`${colors.red}  • ${r.building}/${r.subtype}${colors.reset}`);
      r.errors.forEach(err => console.log(`    - ${err}`));
    });
  }
  
  // Recommendations
  console.log(`\n${colors.cyan}${colors.bold}RECOMMENDATIONS:${colors.reset}`);
  if (failed > 0) {
    console.log('🔴 Fix critical calculation errors');
    console.log('🔴 Ensure all financial metrics are calculated');
    console.log('🔴 Remove any NaN/null values from responses');
  }
  if (totalWarnings > 0) {
    console.log('🟡 Review cost calculations for accuracy');
    console.log('🟡 Add equipment costs where missing');
    console.log('🟡 Check for hardcoded values in backend');
  }
  if (failed === 0 && totalWarnings === 0) {
    console.log('🎉 All tests passed! System is working perfectly.');
  }
  
  console.log(`\n${colors.blue}${'='.repeat(60)}${colors.reset}`);
  console.log(`✨ Tests completed at ${new Date().toLocaleTimeString()}`);
}

// Run the tests
runAllTests().catch(error => {
  console.error(`${colors.red}Fatal error: ${error.message}${colors.reset}`);
  process.exit(1);
});