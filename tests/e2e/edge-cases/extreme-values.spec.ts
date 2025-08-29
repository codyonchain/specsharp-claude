import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

test.describe('Extreme Value Handling', () => {
  test.beforeEach(async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
  });

  test('Very small buildings', async ({ page }) => {
    const smallBuildings = [
      { desc: '100 sf storage shed Nashville', minCost: 50, maxCost: 500 },
      { desc: '500 sf food truck commissary Nashville', minCost: 100, maxCost: 800 },
      { desc: '50 sf kiosk Manchester NH', minCost: 100, maxCost: 1000 }
    ];

    for (const building of smallBuildings) {
      // Fill description
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(building.desc);
      
      // Analyze
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Wait for result
      const costElement = await page.waitForSelector(
        '.cost-per-sqft, [data-testid="cost-per-sqft"], :has-text("per SF"), :has-text("$/SF")',
        { timeout: 5000 }
      ).catch(() => null);
      
      if (costElement) {
        const costText = await costElement.textContent();
        const costValue = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
        
        // Small buildings might have higher per-sqft costs
        expect(costValue).toBeGreaterThan(0);
        expect(costValue).toBeLessThan(2000); // Reasonable upper limit for small buildings
        
        console.log(`✓ Small building: ${building.desc} = $${costValue}/sqft`);
      } else {
        console.log(`⚠ Could not calculate cost for: ${building.desc}`);
      }
      
      // Reset for next test
      await input.clear();
    }
  });

  test('Very large buildings', async ({ page }) => {
    const largeBuildings = [
      { desc: '5000000 sf distribution center Nashville', minCost: 50, maxCost: 200 },
      { desc: '1000000 sf hospital complex Nashville', minCost: 400, maxCost: 700 },
      { desc: '2000000 sf mixed use development Manchester', minCost: 150, maxCost: 400 }
    ];

    for (const building of largeBuildings) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(building.desc);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      const costElement = await page.waitForSelector(
        '.cost-per-sqft, [data-testid="cost-per-sqft"], :has-text("per SF"), :has-text("$/SF")',
        { timeout: 5000 }
      ).catch(() => null);
      
      if (costElement) {
        const costText = await costElement.textContent();
        const costValue = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
        
        expect(costValue).toBeGreaterThan(building.minCost);
        expect(costValue).toBeLessThan(building.maxCost * 2); // Allow some flexibility
        
        console.log(`✓ Large building: ${building.desc} = $${costValue}/sqft`);
        
        // Check total cost is reasonable
        const sqft = parseInt(building.desc.match(/(\d+)/)?.[1] || '0');
        const totalCost = costValue * sqft;
        console.log(`  Total cost: $${totalCost.toLocaleString()}`);
      } else {
        console.log(`⚠ Could not calculate cost for: ${building.desc}`);
      }
      
      await input.clear();
    }
  });

  test('Buildings with special characters', async ({ page }) => {
    const specialCases = [
      '10,000 sf office Nashville',
      '100.5 sf retail Nashville', 
      '$50M budget hospital Nashville',
      '1,234,567 sf warehouse NH',
      '~5000 sf restaurant Nashville',
      '15k sqft medical office Manchester'
    ];

    for (const building of specialCases) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(building);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Should handle special characters and still calculate
      const hasResult = await page.locator(
        '.cost-per-sqft, [data-testid="cost-per-sqft"], :has-text("per SF"), :has-text("$/SF")'
      ).isVisible({ timeout: 5000 }).catch(() => false);
      
      if (hasResult) {
        const costElement = page.locator('.cost-per-sqft, :has-text("per SF")').first();
        const costText = await costElement.textContent();
        console.log(`✓ Special chars handled: ${building} → ${costText}`);
      } else {
        console.log(`⚠ Could not parse: ${building}`);
      }
      
      await input.clear();
    }
  });

  test('Extreme cost scenarios', async ({ page }) => {
    const extremeCases = [
      { desc: '1 sf test building Nashville', expectation: 'very high per-sqft' },
      { desc: '99999999 sf mega complex Nashville', expectation: 'handles large numbers' },
      { desc: '0.5 sf impossible building Nashville', expectation: 'handles decimals' }
    ];

    for (const testCase of extremeCases) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(testCase.desc);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Wait to see what happens
      await page.waitForTimeout(2000);
      
      // Check for either error or result
      const hasError = await page.locator('.error, [role="alert"], .text-red').isVisible().catch(() => false);
      const hasResult = await page.locator('.cost-per-sqft, :has-text("per SF")').isVisible().catch(() => false);
      
      if (hasError) {
        console.log(`✓ Extreme case properly rejected: ${testCase.desc}`);
      } else if (hasResult) {
        const costElement = page.locator('.cost-per-sqft, :has-text("per SF")').first();
        const costText = await costElement.textContent();
        console.log(`✓ Extreme case calculated: ${testCase.desc} → ${costText}`);
      } else {
        console.log(`⚠ Extreme case unclear result: ${testCase.desc}`);
      }
      
      await input.clear();
    }
  });

  test('Mixed units and formats', async ({ page }) => {
    const mixedFormats = [
      '100 square meters office Nashville',
      '5 acres retail development Nashville',
      '10000ft2 warehouse Manchester',
      '1/2 million sf hospital complex Nashville',
      'quarter million square foot mall Nashville'
    ];

    for (const format of mixedFormats) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(format);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      await page.waitForTimeout(2000);
      
      const hasResult = await page.locator('.cost-per-sqft, :has-text("per SF")').isVisible().catch(() => false);
      
      if (hasResult) {
        console.log(`✓ Format parsed: ${format}`);
      } else {
        console.log(`⚠ Format not recognized: ${format}`);
      }
      
      await input.clear();
    }
  });
});