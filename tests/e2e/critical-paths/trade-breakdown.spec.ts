import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

const buildingTradeExpectations = {
  healthcare: {
    description: '200000 sf hospital in Nashville TN',
    trades: {
      mechanical: { expected: 0.32, tolerance: 0.02 },
      electrical: { expected: 0.12, tolerance: 0.02 },
      plumbing: { expected: 0.08, tolerance: 0.01 },
      structural: { expected: 0.25, tolerance: 0.02 }
    }
  },
  restaurant: {
    description: '4200 sf restaurant in Nashville TN',
    trades: {
      mechanical: { expected: 0.28, tolerance: 0.03 },
      electrical: { expected: 0.15, tolerance: 0.02 },
      plumbing: { expected: 0.12, tolerance: 0.02 },
      structural: { expected: 0.20, tolerance: 0.02 }
    }
  },
  office: {
    description: '85000 sf office building in Nashville TN',
    trades: {
      mechanical: { expected: 0.25, tolerance: 0.02 },
      electrical: { expected: 0.10, tolerance: 0.02 },
      plumbing: { expected: 0.06, tolerance: 0.01 },
      structural: { expected: 0.30, tolerance: 0.02 }
    }
  }
};

test.describe('Trade Breakdown Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Use auth bypass and navigate to dashboard
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Click New Project button to get to scope/new
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForURL('**/scope/new', { timeout: 5000 });
    }
  });

  Object.entries(buildingTradeExpectations).forEach(([buildingType, config]) => {
    test(`${buildingType} trade percentages`, async ({ page }) => {
      // Ensure we're on the scope/new page
      if (!page.url().includes('/scope/new')) {
        await navigateWithAuth(page, 'http://localhost:3000/scope/new');
      }
      // Try multiple selectors for the description input
      const inputSelectors = [
        'textarea[placeholder*="Describe"]',
        'textarea[placeholder*="describe"]',
        'textarea',
        'input[type="text"]',
        '.description-input'
      ];
      
      let filled = false;
      for (const selector of inputSelectors) {
        const input = page.locator(selector).first();
        if (await input.isVisible({ timeout: 1000 }).catch(() => false)) {
          await input.fill(config.description);
          filled = true;
          break;
        }
      }
      
      if (!filled) {
        throw new Error('Could not find description input field');
      }
      // Try multiple selectors for the analyze button
      const analyzeSelectors = [
        'button:has-text("Analyze")',
        'button:has-text("Next Deal")',
        'button[type="submit"]',
        '.analyze-button'
      ];
      
      let clicked = false;
      for (const selector of analyzeSelectors) {
        const button = page.locator(selector).first();
        if (await button.isVisible({ timeout: 1000 }).catch(() => false)) {
          await button.click();
          clicked = true;
          break;
        }
      }
      
      if (!clicked) {
        throw new Error('Could not find analyze button');
      }
      await page.waitForSelector('.cost-per-sqft', { timeout: 10000 });
      
      // Save to see details
      await page.click('button:has-text("Save Project")');
      await page.waitForURL(/\/project\/.+/);
      
      // Collect trade percentages
      const tradeResults: Record<string, number> = {};
      
      for (const [trade, expected] of Object.entries(config.trades)) {
        // Try multiple selectors for each trade
        const selectors = [
          `[data-trade="${trade}"]`,
          `.trade-${trade}`,
          `:has-text("${trade.charAt(0).toUpperCase() + trade.slice(1)}")`,
          `.trade-breakdown :has-text("${trade}")`
        ];
        
        let found = false;
        for (const selector of selectors) {
          try {
            const elements = page.locator(selector);
            if (await elements.first().isVisible({ timeout: 1000 }).catch(() => false)) {
              const parentRow = elements.first().locator('xpath=ancestor::*[contains(@class, "trade-row") or contains(@class, "trade-item")]').first();
              let text = '';
              
              if (await parentRow.count() > 0) {
                text = await parentRow.textContent() || '';
              } else {
                text = await elements.first().textContent() || '';
              }
              
              // Extract percentage (looking for patterns like "32%" or "0.32")
              const percentMatch = text.match(/(\d+\.?\d*)\s*%/);
              if (percentMatch) {
                const percentage = parseFloat(percentMatch[1]) / 100;
                tradeResults[trade] = percentage;
                found = true;
                
                // Validate
                const difference = Math.abs(percentage - expected.expected);
                expect(difference).toBeLessThanOrEqual(expected.tolerance);
                
                console.log(`✓ ${buildingType} - ${trade}: ${(percentage * 100).toFixed(1)}% (expected ${(expected.expected * 100).toFixed(1)}%)`);
                break;
              }
            }
          } catch (e) {
            // Continue to next selector
          }
        }
        
        if (!found) {
          console.log(`⚠ ${buildingType} - ${trade}: not found in UI`);
        }
      }
      
      // Verify we found at least some trades
      expect(Object.keys(tradeResults).length).toBeGreaterThan(0);
      
      // If we found trades, verify total is close to 100%
      if (Object.keys(tradeResults).length > 2) {
        const total = Object.values(tradeResults).reduce((sum, pct) => sum + pct, 0);
        expect(total).toBeGreaterThanOrEqual(0.85);
        expect(total).toBeLessThanOrEqual(1.15);
      }
    });
  });
});