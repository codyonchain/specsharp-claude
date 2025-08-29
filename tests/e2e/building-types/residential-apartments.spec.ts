import { test, expect } from '@playwright/test';
import { TestDataManager } from '../../config/helpers';

const testData = TestDataManager.getInstance();

test.describe('residential - apartments Tests', () => {
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

  test('Luxury Apartments Brentwood - Cost Calculation', async ({ page }) => {
    // Fill in the project description
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    await descriptionInput.fill('250-unit luxury apartment complex with amenity deck in Brentwood TN');
    
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
      expect(costPerSqft).toBeGreaterThanOrEqual(180);
      expect(costPerSqft).toBeLessThanOrEqual(220);
    }
    
    // Validate total cost if visible
    const totalCostElement = page.locator('text=/Total.*\\$[0-9,]+[MK]?/i');
    if (await totalCostElement.isVisible()) {
      const totalCostText = await totalCostElement.textContent();
      let totalCost = parseFloat(totalCostText.replace(/[^0-9.MK]/g, ''));
      
      // Convert M (millions) or K (thousands) to actual number
      if (totalCostText.includes('M')) totalCost *= 1000000;
      if (totalCostText.includes('K')) totalCost *= 1000;
      
      expect(totalCost).toBeGreaterThanOrEqual(45000000);
      expect(totalCost).toBeLessThanOrEqual(55000000);
    }
  });


});
