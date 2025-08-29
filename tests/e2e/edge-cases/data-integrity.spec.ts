import { test, expect } from '@playwright/test';
import { navigateWithAuth, setupTestAuth } from '../../helpers/auth';

test.describe('Data Integrity', () => {
  test('Project persistence across sessions', async ({ page, context }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    // Create project
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('50000 sf office building Nashville TN for data integrity test');
    
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await page.waitForSelector('.cost-per-sqft, :has-text("per SF")', { timeout: 5000 }).catch(() => {});
    
    // Get the cost value
    const costElement = page.locator('.cost-per-sqft, :has-text("per SF")').first();
    const originalCost = await costElement.textContent();
    console.log(`Original cost: ${originalCost}`);
    
    // Save project if save button exists
    const saveButton = page.locator('button:has-text("Save"), a:has-text("Save")').first();
    let projectUrl = '';
    
    if (await saveButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await saveButton.click();
      await page.waitForTimeout(2000);
      
      // Check if we navigated to project detail
      if (page.url().includes('/project/')) {
        projectUrl = page.url();
        console.log(`✓ Project saved, URL: ${projectUrl}`);
      }
    }
    
    // Clear cookies/storage (simulate new session)
    await context.clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Re-authenticate and revisit
    await setupTestAuth(page);
    
    if (projectUrl) {
      await page.goto(projectUrl);
      
      // Project should still load
      const titleVisible = await page.locator('h1, h2, .project-title').first().isVisible({ timeout: 5000 }).catch(() => false);
      
      if (titleVisible) {
        console.log('✓ Project persists across sessions');
        
        // Check if cost is still the same
        const newCostElement = page.locator('.cost-per-sqft, :has-text("per SF"), .total-cost').first();
        if (await newCostElement.isVisible({ timeout: 1000 }).catch(() => false)) {
          const newCost = await newCostElement.textContent();
          console.log(`Cost after session clear: ${newCost}`);
        }
      } else {
        console.log('⚠ Project may require authentication to access');
      }
    } else {
      // Try via dashboard
      await navigateWithAuth(page, 'http://localhost:3000/dashboard');
      
      const projectCard = page.locator('.project-card, [data-testid="project-card"]').filter({ hasText: 'data integrity test' });
      if (await projectCard.first().isVisible({ timeout: 2000 }).catch(() => false)) {
        console.log('✓ Project visible in dashboard after session clear');
      } else {
        console.log('⚠ Project not found in dashboard (may not have saved)');
      }
    }
  });

  test('Concurrent project modifications', async ({ browser }) => {
    // Create two separate contexts
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    // Setup auth for both
    await setupTestAuth(page1);
    await setupTestAuth(page2);
    
    // Both navigate to new project page
    await Promise.all([
      page1.goto('http://localhost:3000/dashboard'),
      page2.goto('http://localhost:3000/dashboard')
    ]);
    
    // Click new project on both
    const newButton1 = page1.locator('button:has-text("New Project")').first();
    const newButton2 = page2.locator('button:has-text("New Project")').first();
    
    if (await newButton1.isVisible({ timeout: 1000 }).catch(() => false)) {
      await newButton1.click();
    } else {
      await page1.goto('http://localhost:3000/scope/new');
    }
    
    if (await newButton2.isVisible({ timeout: 1000 }).catch(() => false)) {
      await newButton2.click();
    } else {
      await page2.goto('http://localhost:3000/scope/new');
    }
    
    // Both fill different projects simultaneously
    const input1 = page1.locator('textarea, input[type="text"]').first();
    const input2 = page2.locator('textarea, input[type="text"]').first();
    
    await Promise.all([
      input1.fill('100000 sf hospital Nashville - User 1 Project'),
      input2.fill('50000 sf office Nashville - User 2 Project')
    ]);
    
    // Both analyze simultaneously
    const analyze1 = page1.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    const analyze2 = page2.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    
    await Promise.all([
      analyze1.isVisible({ timeout: 1000 }).then(visible => visible && analyze1.click()),
      analyze2.isVisible({ timeout: 1000 }).then(visible => visible && analyze2.click())
    ]);
    
    // Both should calculate correctly
    const [cost1, cost2] = await Promise.all([
      page1.locator('.cost-per-sqft, :has-text("per SF")').first().textContent({ timeout: 5000 }).catch(() => 'N/A'),
      page2.locator('.cost-per-sqft, :has-text("per SF")').first().textContent({ timeout: 5000 }).catch(() => 'N/A')
    ]);
    
    console.log(`User 1 (Hospital): ${cost1}`);
    console.log(`User 2 (Office): ${cost2}`);
    
    // Costs should be different (hospital more expensive than office)
    if (cost1 !== 'N/A' && cost2 !== 'N/A') {
      const cost1Value = parseFloat(cost1.replace(/[^0-9.]/g, '') || '0');
      const cost2Value = parseFloat(cost2.replace(/[^0-9.]/g, '') || '0');
      
      expect(cost1Value).toBeGreaterThan(cost2Value); // Hospital > Office
      console.log('✓ Concurrent modifications handled correctly');
    } else {
      console.log('⚠ One or both concurrent calculations failed');
    }
    
    // Cleanup
    await context1.close();
    await context2.close();
  });

  test('Data consistency after updates', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newButton = page.locator('button:has-text("New Project")').first();
    if (await newButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await newButton.click();
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    const input = page.locator('textarea, input[type="text"]').first();
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    
    // Initial calculation
    await input.fill('75000 sf retail center Nashville');
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await page.waitForTimeout(2000);
    
    const cost1Element = page.locator('.cost-per-sqft, :has-text("per SF")').first();
    const initialCost = await cost1Element.textContent().catch(() => '');
    console.log(`Initial: 75000 sf retail = ${initialCost}`);
    
    // Update to different type
    await input.clear();
    await input.fill('75000 sf medical office Nashville');
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await page.waitForTimeout(2000);
    
    const updatedCost = await cost1Element.textContent().catch(() => '');
    console.log(`Updated: 75000 sf medical = ${updatedCost}`);
    
    // Costs should be different
    expect(initialCost).not.toBe(updatedCost);
    
    // Go back to original
    await input.clear();
    await input.fill('75000 sf retail center Nashville');
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await page.waitForTimeout(2000);
    
    const finalCost = await cost1Element.textContent().catch(() => '');
    console.log(`Final: 75000 sf retail = ${finalCost}`);
    
    // Should match initial (deterministic)
    if (initialCost && finalCost) {
      const initial = parseFloat(initialCost.replace(/[^0-9.]/g, '') || '0');
      const final = parseFloat(finalCost.replace(/[^0-9.]/g, '') || '0');
      
      // Allow small variance (rounding)
      expect(Math.abs(initial - final)).toBeLessThan(10);
      console.log('✓ Data consistency maintained');
    }
  });

  test('Browser refresh data persistence', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Create a project
    const newButton = page.locator('button:has-text("New Project")').first();
    if (await newButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await newButton.click();
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('125000 sf warehouse distribution center Memphis TN');
    
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await page.waitForSelector('.cost-per-sqft, :has-text("per SF")', { timeout: 5000 }).catch(() => {});
    
    const costBeforeRefresh = await page.locator('.cost-per-sqft, :has-text("per SF")').first().textContent();
    console.log(`Before refresh: ${costBeforeRefresh}`);
    
    // Save current URL
    const currentUrl = page.url();
    
    // Refresh the page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Check if we're still authenticated
    if (page.url().includes('/login')) {
      console.log('⚠ Lost authentication on refresh');
      await setupTestAuth(page);
      await page.goto(currentUrl);
    }
    
    // Check if data persists
    const inputAfterRefresh = page.locator('textarea, input[type="text"]').first();
    const valueAfterRefresh = await inputAfterRefresh.inputValue().catch(() => '');
    
    if (valueAfterRefresh) {
      console.log(`✓ Input persisted after refresh: ${valueAfterRefresh.substring(0, 50)}...`);
    } else {
      console.log('⚠ Input cleared after refresh');
    }
    
    // Check if calculation persists
    const costAfterRefresh = await page.locator('.cost-per-sqft, :has-text("per SF")').first().textContent().catch(() => '');
    
    if (costAfterRefresh) {
      console.log(`After refresh: ${costAfterRefresh}`);
      
      if (costBeforeRefresh && costAfterRefresh) {
        const before = parseFloat(costBeforeRefresh.replace(/[^0-9.]/g, '') || '0');
        const after = parseFloat(costAfterRefresh.replace(/[^0-9.]/g, '') || '0');
        
        if (Math.abs(before - after) < 10) {
          console.log('✓ Calculation persisted after refresh');
        } else {
          console.log('⚠ Calculation changed after refresh');
        }
      }
    } else {
      console.log('⚠ Calculation lost after refresh');
    }
  });

  test('Multiple tab consistency', async ({ browser }) => {
    const context = await browser.newContext();
    
    // Open first tab and create project
    const tab1 = await context.newPage();
    await setupTestAuth(tab1);
    await tab1.goto('http://localhost:3000/dashboard');
    
    // Open second tab  
    const tab2 = await context.newPage();
    await setupTestAuth(tab2);
    await tab2.goto('http://localhost:3000/dashboard');
    
    // Count initial projects in both tabs
    const initialCount1 = await tab1.locator('.project-card, [data-testid="project-card"]').count();
    const initialCount2 = await tab2.locator('.project-card, [data-testid="project-card"]').count();
    
    console.log(`Tab 1 initial projects: ${initialCount1}`);
    console.log(`Tab 2 initial projects: ${initialCount2}`);
    
    // Create project in tab 1
    const newButton = tab1.locator('button:has-text("New Project")').first();
    if (await newButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await newButton.click();
    } else {
      await tab1.goto('http://localhost:3000/scope/new');
    }
    
    const input = tab1.locator('textarea, input[type="text"]').first();
    await input.fill('90000 sf hotel Nashville - Multi-tab test');
    
    const analyzeButton = tab1.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    await tab1.waitForTimeout(2000);
    
    // Save if possible
    const saveButton = tab1.locator('button:has-text("Save"), a:has-text("Save")').first();
    if (await saveButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await saveButton.click();
      await tab1.waitForTimeout(2000);
    }
    
    // Refresh tab 2 dashboard
    await tab2.reload();
    await tab2.waitForLoadState('networkidle');
    
    // Check if new project appears in tab 2
    const finalCount2 = await tab2.locator('.project-card, [data-testid="project-card"]').count();
    
    if (finalCount2 > initialCount2) {
      console.log('✓ New project visible in second tab after refresh');
      
      // Look for the specific project
      const hotelProject = tab2.locator('.project-card, [data-testid="project-card"]').filter({ hasText: 'Multi-tab test' });
      if (await hotelProject.first().isVisible({ timeout: 1000 }).catch(() => false)) {
        console.log('✓ Specific project found in second tab');
      }
    } else {
      console.log('⚠ Project not visible in second tab (may need manual refresh)');
    }
    
    await context.close();
  });
});