import { test, expect } from '@playwright/test';
import { setupTestAuth } from '../../helpers/auth';

test.describe('Performance with Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await setupTestAuth(page);
  });

  test('Authenticated page load times', async ({ page }) => {
    const metrics: Record<string, number> = {};
    
    // Dashboard (should skip login)
    const dashStart = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    await page.waitForLoadState('networkidle');
    metrics.dashboardAuth = Date.now() - dashStart;
    
    // Should NOT redirect to login
    expect(page.url()).toContain('/dashboard');
    expect(metrics.dashboardAuth).toBeLessThan(3000); // 3 seconds max
    
    // New project page
    const newStart = Date.now();
    await page.goto('http://localhost:3000/scope/new');
    await page.waitForLoadState('networkidle');
    metrics.newProjectAuth = Date.now() - newStart;
    
    // Should load quickly without auth redirect
    expect(metrics.newProjectAuth).toBeLessThan(2500);
    
    // Project list (if exists)
    const listStart = Date.now();
    await page.goto('http://localhost:3000/dashboard');
    await page.waitForLoadState('domcontentloaded');
    metrics.projectList = Date.now() - listStart;
    
    expect(metrics.projectList).toBeLessThan(2000);
    
    console.log('Authenticated load times (ms):', metrics);
    console.log(`Average: ${Math.round(Object.values(metrics).reduce((a, b) => a + b, 0) / Object.keys(metrics).length)}ms`);
  });

  test('Calculation performance with saved auth', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    
    // Click new project if needed
    const newProjectButton = page.locator('button:has-text("New Project"), button:has-text("Create First Project")');
    if (await newProjectButton.first().isVisible({ timeout: 1000 }).catch(() => false)) {
      await newProjectButton.first().click();
      await page.waitForLoadState('networkidle');
    } else {
      await page.goto('http://localhost:3000/scope/new');
    }
    
    // Measure calculation time
    const calcTimes: number[] = [];
    
    const testCases = [
      '100000 sf office Nashville',
      '50000 sf retail Memphis',  
      '200000 sf hospital Nashville'
    ];
    
    for (const description of testCases) {
      // Find the input field
      const input = page.locator('textarea, input[type="text"]').first();
      await input.fill(description);
      
      const start = Date.now();
      
      // Try different analyze button selectors
      const analyzeButton = page.locator('button:has-text("Analyze"), a:has-text("Analyze")').first();
      if (await analyzeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await analyzeButton.click();
      }
      
      // Wait for result (cost display)
      await page.waitForSelector('.cost-per-sqft, [data-testid="cost-per-sqft"], :has-text("per SF")', { 
        timeout: 5000 
      }).catch(() => {
        console.log(`Could not find cost for: ${description}`);
      });
      
      const time = Date.now() - start;
      calcTimes.push(time);
      
      console.log(`Calculation for "${description}": ${time}ms`);
      
      // Clear for next test
      await input.clear();
    }
    
    // All calculations should be fast
    const avgTime = calcTimes.reduce((a, b) => a + b, 0) / calcTimes.length;
    expect(avgTime).toBeLessThan(3000);
    
    console.log(`Average calculation time: ${Math.round(avgTime)}ms`);
  });

  test('Multiple authenticated sessions', async ({ browser }) => {
    // Create multiple authenticated contexts
    const contexts = await Promise.all([
      browser.newContext(),
      browser.newContext(),
      browser.newContext()
    ]);
    
    const pages = await Promise.all(
      contexts.map(ctx => ctx.newPage())
    );
    
    // Setup auth for all
    await Promise.all(
      pages.map(page => setupTestAuth(page))
    );
    
    // All should access dashboard without login
    const start = Date.now();
    await Promise.all(
      pages.map(page => page.goto('http://localhost:3000/dashboard'))
    );
    
    // Wait for all to load
    await Promise.all(
      pages.map(page => page.waitForLoadState('networkidle'))
    );
    
    const loadTime = Date.now() - start;
    
    // All 3 should load reasonably quickly
    expect(loadTime).toBeLessThan(5000);
    
    // Verify none redirected to login
    for (let i = 0; i < pages.length; i++) {
      const url = pages[i].url();
      expect(url).toContain('/dashboard');
      console.log(`Session ${i + 1}: ${url}`);
    }
    
    console.log(`3 concurrent auth sessions loaded in: ${loadTime}ms`);
    console.log(`Average per session: ${Math.round(loadTime / 3)}ms`);
    
    // Cleanup
    await Promise.all(contexts.map(ctx => ctx.close()));
  });

  test('Memory usage with auth', async ({ page }) => {
    // Navigate to dashboard multiple times
    const navigationCount = 10;
    const times: number[] = [];
    
    for (let i = 0; i < navigationCount; i++) {
      const start = Date.now();
      await page.goto('http://localhost:3000/dashboard');
      await page.waitForLoadState('domcontentloaded');
      times.push(Date.now() - start);
      
      // Small delay between navigations
      await page.waitForTimeout(100);
    }
    
    // Check if performance degrades over time
    const firstHalf = times.slice(0, 5).reduce((a, b) => a + b, 0) / 5;
    const secondHalf = times.slice(5).reduce((a, b) => a + b, 0) / 5;
    
    // Second half shouldn't be significantly slower (no memory leak)
    const degradation = ((secondHalf - firstHalf) / firstHalf) * 100;
    
    console.log(`First 5 navigations avg: ${Math.round(firstHalf)}ms`);
    console.log(`Last 5 navigations avg: ${Math.round(secondHalf)}ms`);
    console.log(`Performance degradation: ${degradation.toFixed(1)}%`);
    
    // Allow up to 50% degradation (some slowdown is normal)
    expect(degradation).toBeLessThan(50);
  });

  test('API response times with auth', async ({ page, request }) => {
    const API_URL = 'http://localhost:8001';
    const apiTimes: Record<string, number> = {};
    
    // Test different endpoints
    const endpoints = [
      { path: '/health', method: 'GET' },
      { path: '/api/v1/scope/projects', method: 'GET' },
      { path: '/api/v1/scope/generate', method: 'POST', data: { description: 'test' } }
    ];
    
    for (const endpoint of endpoints) {
      const start = Date.now();
      
      if (endpoint.method === 'GET') {
        await request.get(`${API_URL}${endpoint.path}`, {
          headers: { 'X-Test-Mode': 'true' }
        }).catch(err => console.log(`Error on ${endpoint.path}:`, err.message));
      } else {
        await request.post(`${API_URL}${endpoint.path}`, {
          headers: { 'X-Test-Mode': 'true', 'Content-Type': 'application/json' },
          data: endpoint.data
        }).catch(err => console.log(`Error on ${endpoint.path}:`, err.message));
      }
      
      apiTimes[endpoint.path] = Date.now() - start;
    }
    
    console.log('API response times:', apiTimes);
    
    // All API calls should be reasonably fast
    Object.values(apiTimes).forEach(time => {
      expect(time).toBeLessThan(2000);
    });
  });
});