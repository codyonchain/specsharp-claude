/**
 * Comprehensive Building Type Test Suite
 * Validates all building types/subtypes across backend and frontend
 * Ensures PROJECT_CODING_STANDARDS.md compliance
 */

import { BackendDataMapper } from '../utils/backendDataMapper';
import { formatters } from '../utils/formatters';

// Define all building type/subtype combinations to test
const BUILDING_MATRIX = [
  // Healthcare
  { type: 'healthcare', subtype: 'hospital', expectedUnits: 'Beds', minCostPerSF: 400 },
  { type: 'healthcare', subtype: 'medical_office', expectedUnits: 'Exam Rooms', minCostPerSF: 250 },
  { type: 'healthcare', subtype: 'urgent_care', expectedUnits: 'Treatment Bays', minCostPerSF: 275 },
  
  // Educational
  { type: 'educational', subtype: 'elementary', expectedUnits: 'Classrooms', minCostPerSF: 200 },
  { type: 'educational', subtype: 'high_school', expectedUnits: 'Students', minCostPerSF: 225 },
  { type: 'educational', subtype: 'university', expectedUnits: 'Students', minCostPerSF: 275 },
  
  // Multifamily
  { type: 'multifamily', subtype: 'luxury_apartments', expectedUnits: 'Units', minCostPerSF: 180 },
  { type: 'multifamily', subtype: 'affordable_housing', expectedUnits: 'Units', minCostPerSF: 140 },
  { type: 'multifamily', subtype: 'mixed_use', expectedUnits: 'Units', minCostPerSF: 200 },
  
  // Office
  { type: 'office', subtype: 'class_a', expectedUnits: 'Workstations', minCostPerSF: 250 },
  { type: 'office', subtype: 'class_b', expectedUnits: 'Workstations', minCostPerSF: 180 },
  { type: 'office', subtype: 'creative_office', expectedUnits: 'Workstations', minCostPerSF: 220 },
];

// Test API endpoint
const API_BASE = 'http://localhost:8001/api/v2';

interface TestResult {
  building: string;
  subtype: string;
  passed: boolean;
  errors: string[];
  warnings: string[];
}

class ComprehensiveBuildingTest {
  private results: TestResult[] = [];
  
  /**
   * Run all tests for all building type combinations
   */
  async runAllTests(): Promise<void> {
    console.log('🏗️  Starting Comprehensive Building Type Tests');
    console.log('=' .repeat(60));
    
    for (const config of BUILDING_MATRIX) {
      await this.testBuildingType(config);
    }
    
    this.printReport();
  }
  
  /**
   * Test a single building type/subtype combination
   */
  private async testBuildingType(config: any): Promise<void> {
    const result: TestResult = {
      building: config.type,
      subtype: config.subtype,
      passed: true,
      errors: [],
      warnings: []
    };
    
    try {
      // 1. Make API call
      const response = await fetch(`${API_BASE}/scope/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: `Build a 100000 square foot ${config.subtype} ${config.type} building in Nashville`,
          building_type: config.type,
          building_subtype: config.subtype,
          square_footage: 100000,
          location: 'Nashville, TN'
        })
      });
      
      if (!response.ok) {
        result.errors.push(`API call failed: ${response.status}`);
        result.passed = false;
        this.results.push(result);
        return;
      }
      
      const data = await response.json();
      
      // 2. Validate response structure
      this.validateResponseStructure(data, result);
      
      // 3. Check calculations consistency
      this.validateCalculations(data, result, config);
      
      // 4. Check for hardcoded values
      this.checkForHardcodedValues(data, result);
      
      // 5. Validate department allocations
      this.validateDepartments(data, result);
      
      // 6. Validate trade breakdowns
      this.validateTrades(data, result);
      
      // 7. Check equipment costs
      this.validateEquipment(data, result);
      
      // 8. Validate financial metrics
      this.validateFinancials(data, result);
      
      // 9. Test frontend mapping
      this.testFrontendMapping(data, result, config);
      
    } catch (error) {
      result.errors.push(`Test failed: ${error}`);
      result.passed = false;
    }
    
    this.results.push(result);
  }
  
  /**
   * Validate response has all required fields
   */
  private validateResponseStructure(data: any, result: TestResult): void {
    const requiredPaths = [
      'calculations.totals.total_project_cost',
      'calculations.totals.hard_costs',
      'calculations.totals.soft_costs',
      'calculations.totals.cost_per_sf',
      'calculations.construction_costs.construction_total',
      'calculations.construction_costs.equipment_total',
      'calculations.trade_breakdown',
      'calculations.soft_costs',
      'calculations.ownership_analysis'
    ];
    
    for (const path of requiredPaths) {
      if (!this.getNestedValue(data, path)) {
        result.errors.push(`Missing required field: ${path}`);
        result.passed = false;
      }
    }
  }
  
  /**
   * Validate calculations are consistent
   */
  private validateCalculations(data: any, result: TestResult, config: any): void {
    const calcs = data.calculations;
    
    // Check cost per SF is reasonable
    const costPerSF = calcs.totals.cost_per_sf;
    if (costPerSF < config.minCostPerSF) {
      result.warnings.push(`Cost per SF (${costPerSF}) below expected minimum (${config.minCostPerSF})`);
    }
    
    // Check totals add up
    const hardCosts = calcs.totals.hard_costs || 0;
    const softCosts = calcs.totals.soft_costs || 0;
    const totalProject = calcs.totals.total_project_cost || 0;
    
    const calculatedTotal = hardCosts + softCosts;
    if (Math.abs(calculatedTotal - totalProject) > 1) {
      result.errors.push(`Total mismatch: ${hardCosts} + ${softCosts} = ${calculatedTotal}, but total is ${totalProject}`);
      result.passed = false;
    }
    
    // Check construction + equipment = hard costs
    const construction = calcs.construction_costs.construction_total || 0;
    const equipment = calcs.construction_costs.equipment_total || 0;
    const features = calcs.construction_costs.special_features_total || 0;
    
    const calculatedHard = construction + equipment + features;
    if (Math.abs(calculatedHard - hardCosts) > 1) {
      result.errors.push(`Hard costs mismatch: ${construction} + ${equipment} + ${features} = ${calculatedHard}, but hard_costs is ${hardCosts}`);
      result.passed = false;
    }
  }
  
  /**
   * Check for hardcoded values that violate standards
   */
  private checkForHardcodedValues(data: any, result: TestResult): void {
    const jsonString = JSON.stringify(data);
    const forbiddenValues = [
      { value: '3500', context: 'Hardcoded rent' },
      { value: '1100', context: 'Hardcoded unit size' },
      { value: '0.93', context: 'Hardcoded occupancy' },
      { value: 'NaN', context: 'Calculation error' },
      { value: 'undefined', context: 'Missing data' }
    ];
    
    for (const forbidden of forbiddenValues) {
      if (jsonString.includes(forbidden.value)) {
        result.warnings.push(`Found potential hardcoded value: ${forbidden.context} (${forbidden.value})`);
      }
    }
  }
  
  /**
   * Validate department allocations
   */
  private validateDepartments(data: any, result: TestResult): void {
    const departments = data.calculations.department_allocation || [];
    
    if (departments.length === 0) {
      result.errors.push('No department allocation found');
      result.passed = false;
      return;
    }
    
    // Check percentages sum to 100
    const totalPercent = departments.reduce((sum: number, dept: any) => 
      sum + (dept.percent || 0), 0);
    
    if (Math.abs(totalPercent - 1.0) > 0.01) {
      result.errors.push(`Department percentages sum to ${totalPercent * 100}%, not 100%`);
      result.passed = false;
    }
    
    // Check amounts are present
    for (const dept of departments) {
      if (!dept.amount || dept.amount <= 0) {
        result.errors.push(`Department ${dept.name} has invalid amount: ${dept.amount}`);
        result.passed = false;
      }
    }
  }
  
  /**
   * Validate trade breakdowns
   */
  private validateTrades(data: any, result: TestResult): void {
    const trades = data.calculations.trade_breakdown || {};
    const constructionTotal = data.calculations.construction_costs.construction_total || 0;
    
    // Sum all trades
    const tradeSum = Object.values(trades).reduce((sum: number, amount: any) => 
      sum + (typeof amount === 'number' ? amount : 0), 0);
    
    // Trades should sum to construction total (not including equipment)
    if (Math.abs(tradeSum - constructionTotal) > 1) {
      result.errors.push(`Trade sum (${tradeSum}) doesn't match construction total (${constructionTotal})`);
      result.passed = false;
    }
    
    // Check each trade is reasonable (> 0, < 50% of total)
    for (const [trade, amount] of Object.entries(trades)) {
      const tradeAmount = amount as number;
      if (tradeAmount <= 0) {
        result.errors.push(`Trade ${trade} has invalid amount: ${tradeAmount}`);
        result.passed = false;
      }
      if (tradeAmount > constructionTotal * 0.5) {
        result.warnings.push(`Trade ${trade} is > 50% of construction total`);
      }
    }
  }
  
  /**
   * Validate equipment costs
   */
  private validateEquipment(data: any, result: TestResult): void {
    const equipment = data.calculations.construction_costs.equipment_total || 0;
    const buildingType = data.project_info.building_type;
    
    // Equipment should be present for most building types
    if (equipment <= 0 && buildingType !== 'warehouse') {
      result.warnings.push(`No equipment cost found for ${buildingType}`);
    }
    
    // Equipment should be reasonable (5-15% of construction)
    const construction = data.calculations.construction_costs.construction_total || 0;
    const equipmentPercent = equipment / construction;
    
    if (equipmentPercent > 0.25) {
      result.warnings.push(`Equipment cost seems high: ${(equipmentPercent * 100).toFixed(1)}% of construction`);
    }
  }
  
  /**
   * Validate financial metrics
   */
  private validateFinancials(data: any, result: TestResult): void {
    const ownership = data.calculations.ownership_analysis || {};
    
    // Check ROI exists and is reasonable
    const roi = ownership.roi;
    if (roi === undefined || roi === null) {
      result.errors.push('ROI not calculated');
      result.passed = false;
    } else if (roi < -0.5 || roi > 1.0) {
      result.warnings.push(`ROI seems unrealistic: ${(roi * 100).toFixed(1)}%`);
    }
    
    // Check investment decision
    const decision = ownership.investment_decision;
    if (!decision || !['GO', 'NO-GO'].includes(decision)) {
      result.errors.push(`Invalid investment decision: ${decision}`);
      result.passed = false;
    }
    
    // Check NPV and IRR exist
    if (ownership.npv === undefined) {
      result.warnings.push('NPV not calculated');
    }
    if (ownership.irr === undefined) {
      result.warnings.push('IRR not calculated');
    }
    
    // Check annual revenue for revenue-generating buildings
    const revenueTypes = ['multifamily', 'office', 'retail'];
    if (revenueTypes.includes(data.project_info.building_type)) {
      if (!ownership.annual_revenue || ownership.annual_revenue <= 0) {
        result.errors.push('No annual revenue for revenue-generating building');
        result.passed = false;
      }
    }
  }
  
  /**
   * Test frontend mapping
   */
  private testFrontendMapping(data: any, result: TestResult, config: any): void {
    try {
      // Test BackendDataMapper
      const displayData = BackendDataMapper.mapToDisplay(data);
      
      // Check unit label matches expected
      if (displayData.unitLabel !== config.expectedUnits) {
        result.errors.push(`Unit label mismatch: got "${displayData.unitLabel}", expected "${config.expectedUnits}"`);
        result.passed = false;
      }
      
      // Check all formatters work without errors
      const testValues = [
        displayData.totalCost,
        displayData.costPerUnit,
        displayData.roi,
        displayData.npv,
        displayData.annualRevenue
      ];
      
      for (const value of testValues) {
        if (value !== undefined && value !== null) {
          try {
            formatters.currency(value);
            formatters.percentage(value);
          } catch (e) {
            result.warnings.push(`Formatter error: ${e}`);
          }
        }
      }
      
      // Check for frontend calculations (forbidden)
      const forbiddenPatterns = [
        /const\s+\w+\s*=\s*\w+\s*[\*\/\+\-]\s*\w+/g,  // Math operations
        /\b(3500|2200|1100|0\.93)\b/g,  // Hardcoded values
        /reduce\s*\(/g,  // Array reduction (summing)
      ];
      
      // This would need actual component code to test
      // For now, just flag as needing manual review
      result.warnings.push('Frontend calculation check requires manual review');
      
    } catch (error) {
      result.errors.push(`Frontend mapping failed: ${error}`);
      result.passed = false;
    }
  }
  
  /**
   * Helper to get nested object value by path
   */
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }
  
  /**
   * Print test report
   */
  private printReport(): void {
    console.log('\n' + '=' .repeat(60));
    console.log('📊 TEST RESULTS SUMMARY');
    console.log('=' .repeat(60));
    
    const passed = this.results.filter(r => r.passed).length;
    const failed = this.results.filter(r => !r.passed).length;
    const warnings = this.results.reduce((sum, r) => sum + r.warnings.length, 0);
    
    console.log(`✅ Passed: ${passed}/${this.results.length}`);
    console.log(`❌ Failed: ${failed}/${this.results.length}`);
    console.log(`⚠️  Total Warnings: ${warnings}`);
    
    // Print detailed results
    console.log('\n📋 DETAILED RESULTS:');
    console.log('-' .repeat(60));
    
    for (const result of this.results) {
      const status = result.passed ? '✅' : '❌';
      console.log(`\n${status} ${result.building}/${result.subtype}`);
      
      if (result.errors.length > 0) {
        console.log('  Errors:');
        for (const error of result.errors) {
          console.log(`    ❌ ${error}`);
        }
      }
      
      if (result.warnings.length > 0) {
        console.log('  Warnings:');
        for (const warning of result.warnings) {
          console.log(`    ⚠️  ${warning}`);
        }
      }
      
      if (result.passed && result.warnings.length === 0) {
        console.log('  ✨ All tests passed perfectly!');
      }
    }
    
    // Print recommendations
    console.log('\n' + '=' .repeat(60));
    console.log('📝 RECOMMENDATIONS:');
    console.log('-' .repeat(60));
    
    if (failed > 0) {
      console.log('🔴 Critical issues found that need immediate attention');
      console.log('   - Fix calculation inconsistencies');
      console.log('   - Ensure all required fields are present');
      console.log('   - Remove hardcoded values from frontend');
    }
    
    if (warnings > 0) {
      console.log('🟡 Warnings that should be reviewed:');
      console.log('   - Check cost calculations for accuracy');
      console.log('   - Verify financial metrics are realistic');
      console.log('   - Review department/trade allocations');
    }
    
    if (failed === 0 && warnings === 0) {
      console.log('🎉 Excellent! All building types pass comprehensive testing.');
      console.log('   The application follows PROJECT_CODING_STANDARDS.md perfectly.');
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log('✨ Test suite completed at', new Date().toLocaleTimeString());
    console.log('=' .repeat(60));
  }
}

// Export test runner
export const runComprehensiveTests = async () => {
  const tester = new ComprehensiveBuildingTest();
  await tester.runAllTests();
};

// Run tests if this file is executed directly
if (require.main === module) {
  runComprehensiveTests().catch(console.error);
}