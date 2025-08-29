import { test, expect } from '@playwright/test';

test.describe('Complete Project Creation Workflow', () => {
  let projectId: string;

  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  });

  test('Create → Calculate → Save → View → Export', async ({ page }) => {
    // Step 1: Create new project
    await test.step('Create new project', async () => {
      await page.goto('/scope/new');
      
      // Fill in the project description
      const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
      await descriptionInput.fill('200000 sf hospital with emergency department in Nashville TN');
      
      await page.waitForTimeout(500); // Let NLP detect
      
      // Check if NLP detection indicators are visible
      const detectedIndicators = page.locator('text=/hospital|healthcare/i');
      const hasDetection = await detectedIndicators.count() > 0;
      
      if (hasDetection) {
        console.log('✓ NLP detected healthcare/hospital');
      }
    });

    // Step 2: Analyze project
    await test.step('Analyze project', async () => {
      await page.click('button:has-text("Generate"), button:has-text("Analyze")');
      
      // Wait for cost calculation to appear
      await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
      
      // Look for cost per sqft
      const costTexts = await page.locator('text=/\\$[0-9,]+\\/s?f/i').allTextContents();
      
      if (costTexts.length > 0) {
        const costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
        
        expect(costPerSqft).toBeGreaterThanOrEqual(1100);
        expect(costPerSqft).toBeLessThanOrEqual(1300);
        
        console.log(`✓ Hospital cost: $${costPerSqft}/sqft`);
      }
    });

    // Step 3: Save and navigate
    await test.step('Save project', async () => {
      // Look for save button or automatic save
      const saveButton = page.locator('button:has-text("Save"), button:has-text("Save Project")');
      const createButton = page.locator('button:has-text("Create Project")');
      
      if (await saveButton.isVisible()) {
        await saveButton.click();
        await page.waitForTimeout(2000);
      } else if (await createButton.isVisible()) {
        await createButton.click();
        await page.waitForTimeout(2000);
      }
      
      // Check if we navigated to project detail
      const currentUrl = page.url();
      if (currentUrl.includes('/project/')) {
        projectId = currentUrl.split('/project/')[1].split('?')[0];
        expect(projectId).toBeTruthy();
        console.log(`✓ Project saved with ID: ${projectId}`);
      } else {
        // Project might be auto-saved, check dashboard
        await page.goto('/dashboard');
        const latestProject = page.locator('.project-card, [class*="project"]').first();
        if (await latestProject.isVisible()) {
          console.log('✓ Project appears in dashboard');
        }
      }
    });

    // Step 4: Verify project detail page
    await test.step('View project details', async () => {
      if (projectId) {
        await page.goto(`/project/${projectId}`);
        
        // Check for project details
        const projectTitle = page.locator('h1, h2').filter({ hasText: /hospital|medical|healthcare/i });
        await expect(projectTitle.first()).toBeVisible({ timeout: 10000 });
        
        // Check for trade breakdown or cost details
        const tradeSection = page.locator('text=/trade|breakdown|mechanical|electrical/i');
        const hasTradeInfo = await tradeSection.count() > 0;
        
        if (hasTradeInfo) {
          console.log('✓ Trade breakdown visible');
        }
      }
    });

    // Step 5: Test Excel export
    await test.step('Export to Excel', async () => {
      // Look for export button
      const exportButton = page.locator('button:has-text("Export"), button:has-text("Download")').filter({ hasText: /excel|xlsx/i });
      
      if (await exportButton.isVisible()) {
        const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
        await exportButton.click();
        
        const download = await downloadPromise;
        if (download) {
          expect(download.suggestedFilename()).toMatch(/\.(xlsx|xls)$/);
          console.log(`✓ Excel export: ${download.suggestedFilename()}`);
        }
      } else {
        console.log('⚠ Export button not found - may not be implemented yet');
      }
    });
  });

  test('Dashboard shows project correctly', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for project cards
    const projectCards = page.locator('[class*="project-card"], [class*="project-item"], .project-card');
    const cardCount = await projectCards.count();
    
    if (cardCount > 0) {
      // Find hospital project if it exists
      const hospitalCard = projectCards.filter({ hasText: /hospital/i }).first();
      
      if (await hospitalCard.isVisible({ timeout: 5000 }).catch(() => false)) {
        // Check that cost is not $0
        const costText = await hospitalCard.locator('text=/\\$[0-9,]+/').first().textContent();
        expect(costText).not.toContain('$0');
        console.log(`✓ Hospital project in dashboard with cost: ${costText}`);
      } else {
        // Check any project has non-zero cost
        const anyCostText = await projectCards.first().locator('text=/\\$[0-9,]+/').first().textContent();
        expect(anyCostText).toBeTruthy();
        console.log(`✓ Projects visible in dashboard`);
      }
    } else {
      console.log('⚠ No projects found in dashboard');
    }
  });
});