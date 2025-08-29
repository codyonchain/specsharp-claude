import { test, expect } from '@playwright/test';

test.describe('Smoke Tests @smoke', () => {
  test('Application loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/SpecSharp/);
    
    // Should see either login or dashboard
    const loginVisible = await page.locator('button:has-text("Login")').isVisible().catch(() => false);
    const dashboardVisible = await page.locator('h1:has-text("Cost Estimates")').isVisible().catch(() => false);
    
    expect(loginVisible || dashboardVisible).toBeTruthy();
    console.log('✅ Application loads successfully');
  });

  test('Critical calculations work', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Test hospital (most complex)
    await page.goto('/scope/new');
    const descInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    
    await descInput.fill('200000 sf hospital Nashville');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    const hospitalCostText = await page.locator('text=/\\$[0-9,]+\\/s?f/i').first().textContent();
    const hospitalCost = parseFloat(hospitalCostText?.replace(/[^0-9.]/g, '') || '0');
    expect(hospitalCost).toBeGreaterThan(1000); // Should be 1000+ per sqft
    console.log(`✅ Hospital calculation: $${hospitalCost}/sqft`);
    
    // Test restaurant (common use case)
    await page.goto('/scope/new');
    await descInput.fill('4200 sf restaurant Nashville');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\$[0-9,]+/', { timeout: 15000 });
    
    const restaurantCostText = await page.locator('text=/\\$[0-9,]+\\/s?f/i').first().textContent();
    const restaurantCost = parseFloat(restaurantCostText?.replace(/[^0-9.]/g, '') || '0');
    expect(restaurantCost).toBeGreaterThan(300); // Should be 300+ per sqft
    console.log(`✅ Restaurant calculation: $${restaurantCost}/sqft`);
  });

  test('Dashboard accessible', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    await expect(page.locator('h1')).toContainText(/Dashboard|Cost Estimates|Projects/i);
    
    // Check if projects are visible
    const projectCards = await page.locator('[class*="project"]').count();
    console.log(`✅ Dashboard accessible with ${projectCards} projects`);
  });

  test('API health check', async ({ request }) => {
    const response = await request.get('http://localhost:8001/docs');
    
    expect(response.ok()).toBeTruthy();
    expect(response.status()).toBe(200);
    console.log('✅ API is healthy');
  });
  
  test('New project page loads', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Navigate to new project
    await page.goto('/scope/new');
    
    // Check for description input
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]');
    await expect(descriptionInput.first()).toBeVisible();
    
    // Check for examples
    const exampleCount = await page.locator('text=/Nashville|Manchester|Nashua/i').count();
    expect(exampleCount).toBeGreaterThan(0);
    console.log(`✅ New project page loads with ${exampleCount} examples`);
  });
});