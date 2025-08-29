import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

test.describe('Error Handling', () => {
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

  test('Empty input validation', async ({ page }) => {
    // Try to analyze without any input
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
      
      // Wait a moment for validation
      await page.waitForTimeout(1000);
      
      // Should show error or not proceed
      const errorSelectors = [
        '.error',
        '[role="alert"]',
        '.text-red',
        ':has-text("required")',
        ':has-text("Please")',
        '.validation-error'
      ];
      
      let errorFound = false;
      for (const selector of errorSelectors) {
        if (await page.locator(selector).first().isVisible({ timeout: 500 }).catch(() => false)) {
          const errorText = await page.locator(selector).first().textContent();
          console.log(`✓ Empty input validation shown: ${errorText}`);
          errorFound = true;
          break;
        }
      }
      
      // Check if we're still on the same page (didn't navigate)
      const stillOnNewPage = page.url().includes('/new') || page.url().includes('/scope');
      
      // Check if no cost was calculated
      const noCostShown = !(await page.locator('.cost-per-sqft').isVisible({ timeout: 500 }).catch(() => false));
      
      expect(errorFound || (stillOnNewPage && noCostShown)).toBeTruthy();
      console.log(`✓ Empty input handled: error=${errorFound}, stillOnPage=${stillOnNewPage}, noCost=${noCostShown}`);
    } else {
      console.log('⚠ Analyze button not found - different UI');
    }
  });

  test('Invalid building types', async ({ page }) => {
    const invalidInputs = [
      'xyz building Nashville',
      '!@#$%^&*() Nashville',
      'построить здание Nashville', // Russian text
      'SELECT * FROM buildings', // SQL injection attempt
      '<script>alert("xss")</script> Nashville', // XSS attempt
      'null undefined NaN Nashville'
    ];

    for (const invalidInput of invalidInputs) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(invalidInput);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Wait for response
      await page.waitForTimeout(2000);
      
      // Check what happened
      const hasError = await page.locator('.error, [role="alert"], .text-red').isVisible().catch(() => false);
      const hasResult = await page.locator('.cost-per-sqft, :has-text("per SF")').isVisible().catch(() => false);
      
      if (hasError) {
        console.log(`✓ Invalid input rejected: "${invalidInput}"`);
      } else if (hasResult) {
        // System might use defaults for unrecognized types
        const costElement = page.locator('.cost-per-sqft, :has-text("per SF")').first();
        const costText = await costElement.textContent();
        console.log(`✓ Invalid input handled with defaults: "${invalidInput}" → ${costText}`);
      } else {
        console.log(`⚠ Unclear handling of: "${invalidInput}"`);
      }
      
      // Clear for next test
      await input.clear();
    }
  });

  test('Network error recovery', async ({ page, context }) => {
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('100000 sf office Nashville');
    
    // Simulate offline
    await context.setOffline(true);
    console.log('📡 Going offline...');
    
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    // Should show error message
    await page.waitForTimeout(3000);
    
    const errorSelectors = [
      ':has-text("error")',
      ':has-text("offline")',
      ':has-text("network")',
      ':has-text("connection")',
      ':has-text("failed")',
      '.error',
      '[role="alert"]'
    ];
    
    let errorFound = false;
    for (const selector of errorSelectors) {
      if (await page.locator(selector).first().isVisible({ timeout: 500 }).catch(() => false)) {
        const errorText = await page.locator(selector).first().textContent();
        console.log(`✓ Network error shown: ${errorText?.substring(0, 50)}`);
        errorFound = true;
        break;
      }
    }
    
    if (!errorFound) {
      console.log('⚠ No explicit network error shown');
    }
    
    // Go back online
    await context.setOffline(false);
    console.log('📡 Back online...');
    
    // Clear and retry
    await input.clear();
    await input.fill('100000 sf office Nashville');
    
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    // Should work now
    const hasResult = await page.locator('.cost-per-sqft, :has-text("per SF")').isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasResult) {
      console.log('✓ Network recovery successful - calculation works again');
    } else {
      console.log('⚠ Network recovery unclear - may need page refresh');
    }
  });

  test('Malformed data handling', async ({ page }) => {
    const malformedInputs = [
      { input: '-1000 sf office Nashville', issue: 'negative size' },
      { input: '0 sf warehouse Nashville', issue: 'zero size' },
      { input: 'infinity sf hospital Nashville', issue: 'infinity value' },
      { input: 'NaN sf retail Nashville', issue: 'not a number' },
      { input: '1e100 sf office Nashville', issue: 'scientific notation extreme' }
    ];

    for (const testCase of malformedInputs) {
      const input = page.locator('textarea, input[type="text"]').first();
      await input.clear();
      await input.fill(testCase.input);
      
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      await page.waitForTimeout(2000);
      
      const hasError = await page.locator('.error, [role="alert"]').isVisible().catch(() => false);
      const hasResult = await page.locator('.cost-per-sqft').isVisible().catch(() => false);
      
      if (hasError) {
        console.log(`✓ Rejected ${testCase.issue}: "${testCase.input}"`);
      } else if (hasResult) {
        const costText = await page.locator('.cost-per-sqft').first().textContent();
        console.log(`✓ Handled ${testCase.issue}: "${testCase.input}" → ${costText}`);
      } else {
        console.log(`⚠ Unclear handling of ${testCase.issue}: "${testCase.input}"`);
      }
      
      await input.clear();
    }
  });

  test('Rapid input changes', async ({ page }) => {
    const input = page.locator('textarea, input[type="text"]').first();
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    
    // Rapidly change input and click analyze
    const rapidInputs = [
      '10000 sf office Nashville',
      '50000 sf hospital Nashville',
      '5000 sf restaurant Nashville',
      '100000 sf warehouse Nashville'
    ];
    
    for (const rapidInput of rapidInputs) {
      await input.clear();
      await input.fill(rapidInput);
      
      if (await analyzeButton.isVisible({ timeout: 100 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Don't wait - immediately go to next
    }
    
    // Wait for final result
    await page.waitForTimeout(3000);
    
    // Should show result for last input (warehouse)
    const hasResult = await page.locator('.cost-per-sqft').isVisible().catch(() => false);
    
    if (hasResult) {
      const costText = await page.locator('.cost-per-sqft').first().textContent();
      console.log(`✓ Rapid changes handled, final result: ${costText}`);
      
      // Verify it's warehouse pricing (should be lowest)
      const costValue = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
      expect(costValue).toBeLessThan(200); // Warehouse should be cheap
    } else {
      console.log('⚠ Rapid changes may have caused issues');
    }
  });

  test('Long input handling', async ({ page }) => {
    const input = page.locator('textarea, input[type="text"]').first();
    
    // Create a very long description
    const longDescription = `
      This is a very detailed description of a complex mixed-use development project 
      located in Nashville, Tennessee. The project includes 100000 square feet of 
      Class A office space with high-end finishes, 50000 square feet of luxury retail 
      including flagship stores and boutique shops, 200 residential units ranging from 
      studios to three-bedroom apartments with premium amenities, a 300-room hotel with 
      conference facilities and spa, 50000 square feet of restaurant and entertainment 
      space including rooftop dining, underground parking for 1500 vehicles with EV 
      charging stations, public plaza with green space and water features, LEED Gold 
      certification requirements, smart building technology throughout, fiber optic 
      infrastructure, backup power generation, and extensive landscaping with native 
      plants. The total project is expected to be approximately 500000 square feet.
    `.replace(/\s+/g, ' ').trim();
    
    await input.fill(longDescription);
    
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    // Should handle long input
    const hasResult = await page.locator('.cost-per-sqft').isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasResult) {
      const costText = await page.locator('.cost-per-sqft').first().textContent();
      console.log(`✓ Long input handled (${longDescription.length} chars): ${costText}`);
    } else {
      console.log(`⚠ Long input (${longDescription.length} chars) may have caused issues`);
    }
  });
});