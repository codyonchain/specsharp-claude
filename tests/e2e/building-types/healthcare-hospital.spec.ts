import { test, expect } from '@playwright/test';
import { TestDataManager } from '../../config/helpers';

const testData = TestDataManager.getInstance();

test.describe('healthcare - hospital Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Navigate to new project
    await page.goto('/scope/new');
  });

  test('Large Hospital Nashville - Cost Calculation', async ({ page }) => {
    // Fill in the project description
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    await descriptionInput.fill('200000 sf hospital with emergency department in Nashville TN');
    
    // Click analyze
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    
    // Wait for results
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    // Get calculated values - look for cost per sqft display
    const costTexts = await page.locator('text=/\\$[0-9,]+\\/s?f/i').allTextContents();
    
    if (costTexts.length > 0) {
      // Parse the first cost per sqft value found
      const costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
      
      // Validate cost is within expected range
      expect(costPerSqft).toBeGreaterThanOrEqual(1100);
      expect(costPerSqft).toBeLessThanOrEqual(1200);
    }
    
    // Validate total cost if visible
    const totalCostElement = page.locator('text=/Total.*\\$[0-9,]+[MK]?/i');
    if (await totalCostElement.isVisible()) {
      const totalCostText = await totalCostElement.textContent();
      let totalCost = parseFloat(totalCostText.replace(/[^0-9.MK]/g, ''));
      
      // Convert M (millions) or K (thousands) to actual number
      if (totalCostText.includes('M')) totalCost *= 1000000;
      if (totalCostText.includes('K')) totalCost *= 1000;
      
      expect(totalCost).toBeGreaterThanOrEqual(220000000);
      expect(totalCost).toBeLessThanOrEqual(240000000);
    }
  });

  test('Large Hospital Nashville - Trade Breakdown', async ({ page }) => {
    // Create project first
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    await descriptionInput.fill('200000 sf hospital with emergency department in Nashville TN');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    // Navigate to details if button exists
    const viewDetailsBtn = page.locator('button:has-text("View Details"), button:has-text("View Breakdown")');
    if (await viewDetailsBtn.isVisible()) {
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000); // Wait for navigation
      
      // Check trade percentages
      const mechanicalText = await page.locator('text=/mechanical/i').first().textContent();
      if (mechanicalText) {
        const mechanicalPct = parseFloat(mechanicalText.replace(/[^0-9.]/g, '')) / 100;
        expect(Math.abs(mechanicalPct - 0.32)).toBeLessThanOrEqual(0.02);
      }
      const electricalText = await page.locator('text=/electrical/i').first().textContent();
      if (electricalText) {
        const electricalPct = parseFloat(electricalText.replace(/[^0-9.]/g, '')) / 100;
        expect(Math.abs(electricalPct - 0.12)).toBeLessThanOrEqual(0.02);
      }
      const plumbingText = await page.locator('text=/plumbing/i').first().textContent();
      if (plumbingText) {
        const plumbingPct = parseFloat(plumbingText.replace(/[^0-9.]/g, '')) / 100;
        expect(Math.abs(plumbingPct - 0.08)).toBeLessThanOrEqual(0.01);
      }
      const structuralText = await page.locator('text=/structural/i').first().textContent();
      if (structuralText) {
        const structuralPct = parseFloat(structuralText.replace(/[^0-9.]/g, '')) / 100;
        expect(Math.abs(structuralPct - 0.25)).toBeLessThanOrEqual(0.02);
      }
    }
  });

});
