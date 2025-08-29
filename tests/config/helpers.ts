import testData from './test-data.json';

export class TestDataManager {
  private static instance: TestDataManager;
  
  static getInstance(): TestDataManager {
    if (!this.instance) {
      this.instance = new TestDataManager();
    }
    return this.instance;
  }

  getAllTestCases(): TestCase[] {
    const cases: TestCase[] = [];
    
    Object.entries(testData.buildingTypes).forEach(([type, subtypes]) => {
      Object.entries(subtypes).forEach(([subtype, data]) => {
        cases.push(...(data as any).testCases);
      });
    });
    
    return cases;
  }

  getTestCase(id: string): TestCase | undefined {
    return this.getAllTestCases().find(tc => tc.id === id);
  }

  getCriticalTestCases(): TestCase[] {
    // Return only the most important test cases for smoke testing
    return [
      this.getTestCase('hospital-nashville-200k'),
      this.getTestCase('qsr-nashville-4200'),
      this.getTestCase('medical-office-manchester-45k'),
      this.getTestCase('restaurant-franklin-4200'),
      this.getTestCase('office-nashville-85k'),
    ].filter(Boolean) as TestCase[];
  }

  validateResult(actual: any, expected: any): TestResult {
    const errors: string[] = [];
    
    // Check cost per sqft
    if (expected.calculations?.costPerSqft) {
      const { min, max } = expected.calculations.costPerSqft;
      if (actual.costPerSqft < min || actual.costPerSqft > max) {
        errors.push(
          `Cost/sqft ${actual.costPerSqft} outside range ${min}-${max}`
        );
      }
    }
    
    // Check total cost
    if (expected.calculations?.totalCost) {
      const { min, max } = expected.calculations.totalCost;
      if (actual.totalCost < min || actual.totalCost > max) {
        errors.push(
          `Total cost ${actual.totalCost} outside range ${min}-${max}`
        );
      }
    }
    
    // Check trade percentages
    if (expected.trades && actual.trades) {
      Object.entries(expected.trades).forEach(([trade, exp]) => {
        const actualPct = actual.trades[trade];
        const { percentage, tolerance } = exp as any;
        
        if (Math.abs(actualPct - percentage) > tolerance) {
          errors.push(
            `${trade} trade ${actualPct.toFixed(2)} outside tolerance of ${percentage} ± ${tolerance}`
          );
        }
      });
    }
    
    return {
      passed: errors.length === 0,
      errors,
      actual,
      expected
    };
  }

  getTestEnvironment() {
    return testData.environments.test;
  }

  getBuildingTypeTestCases(buildingType: string): TestCase[] {
    const cases: TestCase[] = [];
    const typeData = testData.buildingTypes[buildingType as keyof typeof testData.buildingTypes];
    
    if (typeData) {
      Object.values(typeData).forEach((subtypeData: any) => {
        cases.push(...subtypeData.testCases);
      });
    }
    
    return cases;
  }
}

export interface TestCase {
  id: string;
  name: string;
  input: {
    description: string;
    sqft: number;
    location: string;
    building_type: string;
    subtype: string;
  };
  expected: {
    calculations?: {
      costPerSqft?: { min: number; max: number };
      totalCost?: { min: number; max: number };
      constructionCost?: { min: number; max: number };
    };
    trades?: Record<string, {
      percentage: number;
      tolerance: number;
    }>;
    executiveMetrics?: {
      roi?: { min: number; max: number };
      capRate?: { min: number; max: number };
      breakEvenYears?: { min: number; max: number };
    };
  };
}

export interface TestResult {
  passed: boolean;
  errors: string[];
  actual: any;
  expected: any;
}

// Helper functions for common test operations
export async function waitForElement(page: any, selector: string, timeout = 10000) {
  return page.waitForSelector(selector, { timeout });
}

export async function fillProjectDescription(page: any, description: string) {
  const selector = 'textarea[placeholder*="describe"], input[placeholder*="describe"]';
  await page.fill(selector, description);
}

export async function clickAnalyzeButton(page: any) {
  await page.click('button:has-text("Analyze")');
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}