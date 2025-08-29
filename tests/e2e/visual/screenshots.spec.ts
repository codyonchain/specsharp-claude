import { test, expect } from '@playwright/test';
import { navigateWithAuth } from '../../helpers/auth';

test.describe('Visual Regression', () => {
  test('Dashboard visual consistency', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Wait for any animations to complete
    await page.waitForTimeout(1000);
    
    // Hide dynamic content for consistent screenshots
    await page.evaluate(() => {
      // Hide timestamps and dates
      document.querySelectorAll('.timestamp, .date, [data-testid="timestamp"]').forEach(el => {
        (el as HTMLElement).style.visibility = 'hidden';
      });
      
      // Hide any loading spinners
      document.querySelectorAll('.spinner, .loading').forEach(el => {
        (el as HTMLElement).style.display = 'none';
      });
    });
    
    // Take screenshot
    await expect(page).toHaveScreenshot('dashboard.png', {
      fullPage: true,
      animations: 'disabled',
      mask: [page.locator('.timestamp')],
      maxDiffPixelRatio: 0.05
    });
  });

  test('New project form visual', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    // Wait for form to render
    await page.waitForTimeout(1000);
    
    await expect(page).toHaveScreenshot('new-project-form.png', {
      fullPage: false,
      clip: { x: 0, y: 0, width: 1200, height: 800 },
      animations: 'disabled'
    });
  });

  test('Calculation results visual', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    // Fill and analyze
    const input = page.locator('textarea, input[type="text"]').first();
    await input.fill('100000 sf office building Nashville TN');
    
    const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
    if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await analyzeButton.click();
    }
    
    // Wait for calculation
    await page.waitForSelector('.cost-per-sqft, :has-text("per SF")', { timeout: 5000 }).catch(() => {});
    await page.waitForTimeout(1000);
    
    // Hide dynamic values for consistent screenshots
    await page.evaluate(() => {
      // Replace actual numbers with placeholders
      document.querySelectorAll('.cost-per-sqft, .total-cost').forEach(el => {
        const text = el.textContent || '';
        if (text.includes('$')) {
          el.textContent = '$XXX';
        }
      });
      
      // Hide timestamps
      document.querySelectorAll('.timestamp, .date').forEach(el => {
        (el as HTMLElement).style.visibility = 'hidden';
      });
    });
    
    await expect(page).toHaveScreenshot('calculation-results.png', {
      fullPage: true,
      animations: 'disabled'
    });
  });

  test('Mobile responsive views', async ({ page }) => {
    const viewports = [
      { name: 'iphone-12', width: 390, height: 844 },
      { name: 'ipad', width: 768, height: 1024 },
      { name: 'desktop', width: 1920, height: 1080 }
    ];

    for (const viewport of viewports) {
      await page.setViewportSize(viewport);
      await navigateWithAuth(page, 'http://localhost:3000/dashboard');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500);
      
      // Hide dynamic content
      await page.evaluate(() => {
        document.querySelectorAll('.timestamp, .date').forEach(el => {
          (el as HTMLElement).style.visibility = 'hidden';
        });
      });
      
      await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
        fullPage: false,
        animations: 'disabled'
      });
      
      console.log(`✓ Captured ${viewport.name} screenshot (${viewport.width}x${viewport.height})`);
    }
  });

  test('Dark mode visual consistency', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Check if dark mode toggle exists
    const darkModeToggle = page.locator('[aria-label*="dark"], [aria-label*="theme"], button:has-text("Dark")').first();
    
    if (await darkModeToggle.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Enable dark mode
      await darkModeToggle.click();
      await page.waitForTimeout(500);
      
      await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
        fullPage: true,
        animations: 'disabled'
      });
      
      console.log('✓ Dark mode screenshot captured');
    } else {
      // Try adding dark mode class manually
      await page.evaluate(() => {
        document.documentElement.classList.add('dark');
        document.body.classList.add('dark-mode');
      });
      
      await page.waitForTimeout(500);
      
      const isDark = await page.evaluate(() => {
        const styles = window.getComputedStyle(document.body);
        return styles.backgroundColor !== 'rgb(255, 255, 255)';
      });
      
      if (isDark) {
        await expect(page).toHaveScreenshot('dashboard-dark-mode.png', {
          fullPage: true,
          animations: 'disabled'
        });
        console.log('✓ Dark mode screenshot captured (manual)');
      } else {
        console.log('⚠ Dark mode not available');
      }
    }
  });

  test('Component states visual', async ({ page }) => {
    await navigateWithAuth(page, 'http://localhost:3000/dashboard');
    
    // Navigate to new project
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await navigateWithAuth(page, 'http://localhost:3000/scope/new');
    }
    
    const input = page.locator('textarea, input[type="text"]').first();
    
    // Capture different input states
    
    // Empty state
    await expect(input).toHaveScreenshot('input-empty.png');
    
    // Focused state
    await input.focus();
    await expect(input).toHaveScreenshot('input-focused.png');
    
    // Filled state
    await input.fill('Sample project description');
    await expect(input).toHaveScreenshot('input-filled.png');
    
    // Error state (if validation exists)
    await input.clear();
    await input.fill('!!!');
    await input.blur();
    await page.waitForTimeout(500);
    
    const hasError = await page.locator('.error, .text-red').first().isVisible({ timeout: 1000 }).catch(() => false);
    if (hasError) {
      await expect(input).toHaveScreenshot('input-error.png');
      console.log('✓ Error state captured');
    }
    
    console.log('✓ Component state screenshots captured');
  });
});