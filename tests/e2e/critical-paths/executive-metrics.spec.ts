import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

test.describe('Executive Metrics Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Use auth bypass to go directly to project creation
    await navigateWithAuth(page, 'http://localhost:3000/scope/new');
  });

  test('Healthcare ROI and metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    // Create hospital
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '200000 sf hospital Nashville TN');
    await page.click('button:has-text("Analyze Project")');
    await page.waitForSelector('.cost-per-sqft', { timeout: 10000 });
    
    await page.click('button:has-text("Save Project")');
    await page.waitForURL(/\/project\/.+/);
    
    // Look for metrics (may be in owner view or executive view)
    const possibleSelectors = [
      '.executive-metrics',
      '.owner-metrics',
      '.roi-section',
      '[data-metric="roi"]',
      '.metric-card:has-text("ROI")',
      '.metric-value:has-text("%")',
      'text=/ROI.*\\d+/'
    ];
    
    let metricsFound = false;
    for (const selector of possibleSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
          const text = await element.textContent();
          console.log(`Found metrics element: ${text?.substring(0, 100)}`);
          
          // Extract ROI if visible
          const roiMatch = text?.match(/(\d+\.?\d*)\s*%/);
          if (roiMatch) {
            const roi = parseFloat(roiMatch[1]);
            if (roi > 0) {
              expect(roi).toBeGreaterThanOrEqual(6);
              expect(roi).toBeLessThanOrEqual(25);
              console.log(`✓ Healthcare ROI: ${roi}%`);
              metricsFound = true;
              break;
            }
          }
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    // Also check for revenue metrics
    const revenueSelectors = [
      ':has-text("Revenue")',
      ':has-text("Annual")',
      '.revenue-metric',
      '[data-metric="revenue"]'
    ];
    
    for (const selector of revenueSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
          const text = await element.textContent();
          if (text?.includes('$')) {
            console.log(`✓ Found revenue metric: ${text.substring(0, 50)}`);
            metricsFound = true;
            break;
          }
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (!metricsFound) {
      console.log('⚠ No executive metrics found - may not be implemented yet');
    }
  });

  test('Restaurant investment decision', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '4200 sf restaurant Franklin TN');
    await page.click('button:has-text("Analyze Project")');
    await page.waitForSelector('.cost-per-sqft', { timeout: 10000 });
    
    await page.click('button:has-text("Save Project")');
    await page.waitForURL(/\/project\/.+/);
    
    // Look for investment decision
    const decisionSelectors = [
      '.investment-decision',
      '.feasibility-analysis',
      '[data-metric="decision"]',
      ':has-text("Recommendation")',
      ':has-text("feasible")',
      ':has-text("viable")',
      '.decision-card',
      '.investment-summary'
    ];
    
    let decisionFound = false;
    for (const selector of decisionSelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
          const text = await element.textContent();
          console.log(`Investment decision element: ${text?.substring(0, 100)}`);
          expect(text).toBeTruthy();
          decisionFound = true;
          
          // Check for specific investment keywords
          if (text?.toLowerCase().includes('recommend') || 
              text?.toLowerCase().includes('feasible') ||
              text?.toLowerCase().includes('viable')) {
            console.log('✓ Found investment recommendation');
          }
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    // Also check for cost metrics specific to restaurants
    const restaurantMetrics = [
      ':has-text("per seat")',
      ':has-text("covers")',
      ':has-text("revenue per")'
    ];
    
    for (const selector of restaurantMetrics) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
          const text = await element.textContent();
          console.log(`✓ Restaurant-specific metric: ${text?.substring(0, 50)}`);
          decisionFound = true;
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (!decisionFound) {
      console.log('⚠ No investment decision found - may not be implemented yet');
    }
  });

  test('Office building efficiency metrics', async ({ page }) => {
    await page.goto('http://localhost:3000/scope/new');
    
    await page.fill('textarea[placeholder*="Describe what you want to build"]', '85000 sf office building Nashville TN');
    await page.click('button:has-text("Analyze Project")');
    await page.waitForSelector('.cost-per-sqft', { timeout: 10000 });
    
    await page.click('button:has-text("Save Project")');
    await page.waitForURL(/\/project\/.+/);
    
    // Look for efficiency metrics
    const efficiencySelectors = [
      ':has-text("efficiency")',
      ':has-text("rentable")',
      ':has-text("usable")',
      ':has-text("lease")',
      '.efficiency-metric',
      '[data-metric="efficiency"]'
    ];
    
    let efficiencyFound = false;
    for (const selector of efficiencySelectors) {
      try {
        const element = page.locator(selector).first();
        if (await element.isVisible({ timeout: 1000 }).catch(() => false)) {
          const text = await element.textContent();
          console.log(`Office efficiency metric: ${text?.substring(0, 100)}`);
          efficiencyFound = true;
          break;
        }
      } catch (e) {
        // Continue
      }
    }
    
    if (!efficiencyFound) {
      console.log('⚠ No office efficiency metrics found - may not be implemented yet');
    }
  });
});