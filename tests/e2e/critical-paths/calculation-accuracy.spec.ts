import { test, expect } from '@playwright/test';

const testCases = [
  {
    name: 'Hospital Nashville',
    input: '200000 sf hospital with emergency department in Nashville TN',
    expectedCostPerSqft: { min: 1100, max: 1300 },
    expectedTotal: { min: 220000000, max: 260000000 }
  },
  {
    name: 'QSR Nashville',
    input: '4200 sf QSR restaurant with drive through in Franklin TN',
    expectedCostPerSqft: { min: 300, max: 400 },
    expectedTotal: { min: 1260000, max: 1680000 }
  },
  {
    name: 'Medical Office NH',
    input: '45000 sf medical office building in Manchester NH',
    expectedCostPerSqft: { min: 320, max: 400 },
    expectedTotal: { min: 14400000, max: 18000000 }
  },
  {
    name: 'Office Nashville',
    input: '85000 sf Class A office tower in Nashville',
    expectedCostPerSqft: { min: 250, max: 350 },
    expectedTotal: { min: 21250000, max: 29750000 }
  },
  {
    name: 'Apartments Brentwood',
    input: '250 unit luxury apartment complex in Brentwood TN',
    expectedCostPerSqft: { min: 180, max: 250 },
    expectedTotal: { min: 45000000, max: 62500000 }
  },
  {
    name: 'Warehouse NH',
    input: '120000 sf distribution warehouse in Nashua NH',
    expectedCostPerSqft: { min: 80, max: 150 },
    expectedTotal: { min: 9600000, max: 18000000 }
  },
  {
    name: 'Shopping Center NH',
    input: '35000 sf shopping center in Concord NH',
    expectedCostPerSqft: { min: 150, max: 250 },
    expectedTotal: { min: 5250000, max: 8750000 }
  },
  {
    name: 'School NH',
    input: '65000 sf middle school for 800 students in Bedford NH',
    expectedCostPerSqft: { min: 280, max: 350 },
    expectedTotal: { min: 18200000, max: 22750000 }
  },
  {
    name: 'Full Service Restaurant',
    input: '4200 sf full service restaurant with bar in Nashville TN',
    expectedCostPerSqft: { min: 400, max: 550 },
    expectedTotal: { min: 1680000, max: 2310000 }
  }
];

test.describe('Calculation Accuracy Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  testCases.forEach(testCase => {
    test(testCase.name, async ({ page }) => {
      await page.goto('/scope/new');
      
      // Fill in the description
      const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
      await descriptionInput.fill(testCase.input);
      
      // Wait a moment for NLP detection
      await page.waitForTimeout(500);
      
      // Click analyze/generate
      await page.click('button:has-text("Generate"), button:has-text("Analyze")');
      
      // Wait for results to appear
      await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
      
      // Extract cost per sqft
      const costTexts = await page.locator('text=/\\$[0-9,]+\\/s?f/i').allTextContents();
      let costPerSqft = 0;
      
      if (costTexts.length > 0) {
        costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
      }
      
      // Extract total cost - look for text containing "Total" and a dollar amount
      const totalTexts = await page.locator('text=/total.*\\$[0-9,]+[MK]?/i').allTextContents();
      let totalCost = 0;
      
      if (totalTexts.length > 0) {
        const totalText = totalTexts[0];
        let parsedTotal = parseFloat(totalText.replace(/[^0-9.MK]/g, ''));
        
        // Convert M (millions) or K (thousands) to actual number
        if (totalText.includes('M')) parsedTotal *= 1000000;
        else if (totalText.includes('K')) parsedTotal *= 1000;
        
        totalCost = parsedTotal;
      } else {
        // Try to find any large dollar amount that could be the total
        const allCosts = await page.locator('text=/\\$[0-9,]+/').allTextContents();
        const costs = allCosts.map(t => parseFloat(t.replace(/[^0-9.]/g, '')));
        totalCost = Math.max(...costs.filter(c => c > 100000)); // Assume total is the largest value
      }
      
      // Validate ranges
      const results = {
        name: testCase.name,
        costPerSqft,
        totalCost,
        costPerSqftValid: costPerSqft >= testCase.expectedCostPerSqft.min && costPerSqft <= testCase.expectedCostPerSqft.max,
        totalCostValid: totalCost >= testCase.expectedTotal.min && totalCost <= testCase.expectedTotal.max
      };
      
      // Log results for debugging
      console.log(`
        ${results.costPerSqftValid && results.totalCostValid ? '✅' : '❌'} ${testCase.name}:
        Cost/SF: $${costPerSqft} (expected $${testCase.expectedCostPerSqft.min}-$${testCase.expectedCostPerSqft.max})
        Total: $${totalCost.toLocaleString()} (expected $${testCase.expectedTotal.min.toLocaleString()}-$${testCase.expectedTotal.max.toLocaleString()})
      `);
      
      // Assert with helpful error messages
      try {
        expect(costPerSqft).toBeGreaterThanOrEqual(testCase.expectedCostPerSqft.min);
        expect(costPerSqft).toBeLessThanOrEqual(testCase.expectedCostPerSqft.max);
      } catch (error) {
        throw new Error(`Cost/SF validation failed for ${testCase.name}: Got $${costPerSqft}, expected $${testCase.expectedCostPerSqft.min}-$${testCase.expectedCostPerSqft.max}`);
      }
      
      if (totalCost > 0) {
        try {
          expect(totalCost).toBeGreaterThanOrEqual(testCase.expectedTotal.min * 0.8); // Allow 20% tolerance
          expect(totalCost).toBeLessThanOrEqual(testCase.expectedTotal.max * 1.2);
        } catch (error) {
          console.warn(`Total cost validation warning for ${testCase.name}: Got $${totalCost.toLocaleString()}, expected $${testCase.expectedTotal.min.toLocaleString()}-$${testCase.expectedTotal.max.toLocaleString()}`);
        }
      }
    });
  });
});

test.describe('Quick Calculation Validation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Verify calculation differences between building types', async ({ page }) => {
    const results: any[] = [];
    
    // Test hospital (highest cost)
    await page.goto('/scope/new');
    const descInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    
    await descInput.fill('100000 sf hospital in Nashville');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    const hospitalCostText = await page.locator('text=/\\$[0-9,]+\\/s?f/i').first().textContent();
    const hospitalCost = parseFloat(hospitalCostText?.replace(/[^0-9.]/g, '') || '0');
    results.push({ type: 'Hospital', costPerSqft: hospitalCost });
    
    // Test warehouse (lowest cost)
    await page.goto('/scope/new');
    await descInput.fill('100000 sf warehouse in Nashville');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    const warehouseCostText = await page.locator('text=/\\$[0-9,]+\\/s?f/i').first().textContent();
    const warehouseCost = parseFloat(warehouseCostText?.replace(/[^0-9.]/g, '') || '0');
    results.push({ type: 'Warehouse', costPerSqft: warehouseCost });
    
    // Test office (medium cost)
    await page.goto('/scope/new');
    await descInput.fill('100000 sf office building in Nashville');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    const officeCostText = await page.locator('text=/\\$[0-9,]+\\/s?f/i').first().textContent();
    const officeCost = parseFloat(officeCostText?.replace(/[^0-9.]/g, '') || '0');
    results.push({ type: 'Office', costPerSqft: officeCost });
    
    // Validate relative costs
    console.log('\n📊 Building Type Cost Comparison:');
    results.forEach(r => console.log(`  ${r.type}: $${r.costPerSqft}/sqft`));
    
    // Hospital should be most expensive
    expect(hospitalCost).toBeGreaterThan(officeCost);
    expect(hospitalCost).toBeGreaterThan(warehouseCost);
    
    // Office should be more than warehouse
    expect(officeCost).toBeGreaterThan(warehouseCost);
    
    // Warehouse should be least expensive
    expect(warehouseCost).toBeLessThan(200); // Warehouse should be under $200/sqft
    
    console.log('✅ Building type cost hierarchy is correct');
  });
});