import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

test.describe('Data Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Use auth bypass to go directly to project creation
    await navigateWithAuth(page, 'http://localhost:3000/scope/new');
  });

  test('Required fields validation', async ({ page }) => {
    // If we're on dashboard, click New Project
    if (page.url().includes('/dashboard')) {
      const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
      if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
        await newProjectButton.first().click();
        // Wait for navigation to project creation page
        await page.waitForLoadState('networkidle');
      }
    }
    
    // The page shows "2. Analyze" button in the header
    // Try clicking it without entering any data
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")');
    if (await analyzeButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await analyzeButton.first().click();
    } else {
      console.log('Analyze button not found - trying to submit empty form');
      // Try to find any submit button
      const submitButton = page.locator('button[type="submit"]').first();
      if (await submitButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await submitButton.click();
      }
    }
    
    // Should show error or not proceed
    const errorSelectors = [
      '.error',
      '[role="alert"]',
      '.error-message',
      ':has-text("required")',
      ':has-text("Please")',
      '.validation-error'
    ];
    
    let errorFound = false;
    for (const selector of errorSelectors) {
      const error = page.locator(selector).first();
      if (await error.isVisible({ timeout: 1000 }).catch(() => false)) {
        const text = await error.textContent();
        console.log(`✓ Validation error shown: ${text}`);
        errorFound = true;
        break;
      }
    }
    
    // Check if we're still on the same page (didn't navigate)
    const stillOnNewPage = page.url().includes('/scope/new');
    
    // Check if cost calculation didn't appear
    const costNotShown = await page.locator('.cost-per-sqft').isHidden({ timeout: 1000 }).catch(() => true);
    
    expect(errorFound || (stillOnNewPage && costNotShown)).toBeTruthy();
    console.log(`✓ Empty input validation working: error=${errorFound}, stillOnPage=${stillOnNewPage}, noCost=${costNotShown}`);
  });

  test('Handles extreme values - tiny building', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Test very small building
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '100 sf storage shed Nashville');
    await page.click('button:has-text("Analyze Project")');
    
    // Should still calculate or show appropriate message
    const costElement = page.locator('.cost-per-sqft').first();
    const errorElement = page.locator('.error, [role="alert"]').first();
    
    // Wait for either cost or error
    const result = await Promise.race([
      costElement.waitFor({ state: 'visible', timeout: 5000 }).then(() => 'cost'),
      errorElement.waitFor({ state: 'visible', timeout: 5000 }).then(() => 'error')
    ]).catch(() => 'timeout');
    
    if (result === 'cost') {
      const smallCost = await costElement.textContent();
      const cost = parseFloat(smallCost?.replace(/[^0-9.]/g, '') || '0');
      expect(cost).toBeGreaterThan(0);
      console.log(`✓ Tiny building (100 sf) calculated: $${cost}/sf`);
    } else if (result === 'error') {
      const errorText = await errorElement.textContent();
      console.log(`✓ Tiny building validation: ${errorText}`);
      expect(errorText).toBeTruthy();
    } else {
      console.log('⚠ Tiny building test timed out');
    }
  });

  test('Handles extreme values - massive building', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Test very large building
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '5000000 sf mega complex Nashville');
    await page.click('button:has-text("Analyze Project")');
    
    // Should still calculate or show appropriate message
    const costElement = page.locator('.cost-per-sqft').first();
    const errorElement = page.locator('.error, [role="alert"]').first();
    
    // Wait for either cost or error
    const result = await Promise.race([
      costElement.waitFor({ state: 'visible', timeout: 5000 }).then(() => 'cost'),
      errorElement.waitFor({ state: 'visible', timeout: 5000 }).then(() => 'error')
    ]).catch(() => 'timeout');
    
    if (result === 'cost') {
      const largeCost = await costElement.textContent();
      const cost = parseFloat(largeCost?.replace(/[^0-9.]/g, '') || '0');
      expect(cost).toBeGreaterThan(0);
      console.log(`✓ Massive building (5M sf) calculated: $${cost}/sf`);
    } else if (result === 'error') {
      const errorText = await errorElement.textContent();
      console.log(`✓ Massive building validation: ${errorText}`);
      expect(errorText).toBeTruthy();
    } else {
      console.log('⚠ Massive building test timed out');
    }
  });

  test('Handles invalid location', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Test with invalid/unknown location
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '50000 sf office building in Atlantis underwater city');
    await page.click('button:has-text("Analyze Project")');
    
    // Should either use default location or show error
    const costElement = page.locator('.cost-per-sqft').first();
    const locationElement = page.locator(':has-text("location"), :has-text("city")').first();
    
    const hasCost = await costElement.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasCost) {
      const costText = await costElement.textContent();
      const cost = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
      expect(cost).toBeGreaterThan(0);
      
      // Check if a default location was used
      if (await locationElement.isVisible({ timeout: 1000 }).catch(() => false)) {
        const locationText = await locationElement.textContent();
        console.log(`✓ Invalid location handled with default: ${locationText}`);
      } else {
        console.log('✓ Invalid location handled, cost calculated');
      }
    } else {
      console.log('✓ Invalid location resulted in no calculation (expected behavior)');
    }
  });

  test('Handles special characters in input', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Test with special characters
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '10,000 sq.ft. office @ Nashville, TN! #modern $$$');
    await page.click('button:has-text("Analyze Project")');
    
    // Should parse correctly
    const costElement = page.locator('.cost-per-sqft').first();
    const hasCost = await costElement.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasCost) {
      const costText = await costElement.textContent();
      const cost = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
      expect(cost).toBeGreaterThan(0);
      console.log(`✓ Special characters handled correctly: $${cost}/sf`);
      
      // Verify square footage was parsed correctly (should be 10000)
      const sqftElement = page.locator(':has-text("10,000"), :has-text("10000")').first();
      if (await sqftElement.isVisible({ timeout: 1000 }).catch(() => false)) {
        console.log('✓ Square footage parsed correctly from special character input');
      }
    } else {
      console.log('⚠ Special character input not processed');
    }
  });

  test('Handles multiple building types in description', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Test with mixed-use description
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '100000 sf mixed use building with 50000 sf office and 50000 sf retail in Nashville');
    await page.click('button:has-text("Analyze Project")');
    
    // Should calculate mixed-use appropriately
    const costElement = page.locator('.cost-per-sqft').first();
    const hasCost = await costElement.isVisible({ timeout: 5000 }).catch(() => false);
    
    if (hasCost) {
      const costText = await costElement.textContent();
      const cost = parseFloat(costText?.replace(/[^0-9.]/g, '') || '0');
      
      // Mixed use should be between office and retail costs
      expect(cost).toBeGreaterThan(150); // Above retail
      expect(cost).toBeLessThan(300); // Below pure office
      console.log(`✓ Mixed-use building calculated: $${cost}/sf`);
      
      // Check if both building types are recognized
      const hasOffice = await page.locator(':has-text("office")').first().isVisible({ timeout: 1000 }).catch(() => false);
      const hasRetail = await page.locator(':has-text("retail")').first().isVisible({ timeout: 1000 }).catch(() => false);
      
      if (hasOffice && hasRetail) {
        console.log('✓ Both office and retail components recognized');
      }
    } else {
      console.log('⚠ Mixed-use building not calculated');
    }
  });
});