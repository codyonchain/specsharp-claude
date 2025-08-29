import { test, expect } from '@playwright/test';
import { TestDataManager } from '../../config/helpers';

const testManager = TestDataManager.getInstance();
const allTestCases = testManager.getAllTestCases();

// This runs ALL test cases in one file using parameterization
test.describe('Parameterized Building Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login once before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  allTestCases.forEach((testCase) => {
    test(`${testCase.id}: validates calculations`, async ({ page }) => {
      // Navigate to new project page
      await page.goto('/scope/new');
      
      // Fill in the description
      const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
      await descriptionInput.fill(testCase.input.description);
      
      // Click analyze/generate
      await page.click('button:has-text("Generate"), button:has-text("Analyze")');
      
      // Wait for results to appear
      await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
      
      // Get cost per sqft text
      const costTexts = await page.locator('text=/\\$[0-9,]+\\/s?f/i').allTextContents();
      
      if (costTexts.length > 0) {
        const costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
        
        const validation = testManager.validateResult(
          { costPerSqft },
          testCase.expected
        );
        
        if (validation.errors.length > 0) {
          console.log(`Test ${testCase.id} validation errors:`, validation.errors);
        }
        
        expect(validation.errors).toHaveLength(0);
      } else {
        // If no cost found, fail the test with helpful message
        throw new Error(`No cost per sqft found for test case: ${testCase.id}`);
      }
    });
  });
});

// Separate smoke test for critical paths only
test.describe('Critical Path Tests @critical', () => {
  const criticalCases = testManager.getCriticalTestCases();
  
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  criticalCases.forEach((testCase) => {
    test(`Critical: ${testCase.name}`, async ({ page }) => {
      await page.goto('/scope/new');
      
      const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
      await descriptionInput.fill(testCase.input.description);
      
      await page.click('button:has-text("Generate"), button:has-text("Analyze")');
      
      // Wait for results
      await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
      
      // Validate multiple aspects if available
      const costTexts = await page.locator('text=/\\$[0-9,]+\\/s?f/i').allTextContents();
      const totalTexts = await page.locator('text=/Total.*\\$[0-9,]+[MK]?/i').allTextContents();
      
      const actual: any = {};
      
      if (costTexts.length > 0) {
        actual.costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
      }
      
      if (totalTexts.length > 0) {
        let totalCost = parseFloat(totalTexts[0].replace(/[^0-9.MK]/g, ''));
        if (totalTexts[0].includes('M')) totalCost *= 1000000;
        if (totalTexts[0].includes('K')) totalCost *= 1000;
        actual.totalCost = totalCost;
      }
      
      const validation = testManager.validateResult(actual, testCase.expected);
      
      // Provide detailed error message for debugging
      if (validation.errors.length > 0) {
        console.log(`
          Test Case: ${testCase.name} (${testCase.id})
          Input: ${testCase.input.description}
          Expected: ${JSON.stringify(testCase.expected.calculations, null, 2)}
          Actual: ${JSON.stringify(actual, null, 2)}
          Errors: ${validation.errors.join(', ')}
        `);
      }
      
      expect(validation.errors).toHaveLength(0);
    });
  });
});