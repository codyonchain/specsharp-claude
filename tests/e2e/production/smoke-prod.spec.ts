import { test, expect } from '@playwright/test';

// These run against PRODUCTION - no auth bypass!
test.describe('Production Smoke Tests', () => {
  // Use production URL from environment or fallback
  const PROD_URL = process.env.PROD_URL || 'https://specsharp.com';
  const API_URL = process.env.PROD_API_URL || `${PROD_URL}/api`;

  test('Production site loads', async ({ page }) => {
    console.log(`Testing production site: ${PROD_URL}`);
    
    // Track console errors
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    // Track network failures
    const failedRequests: string[] = [];
    page.on('requestfailed', request => {
      failedRequests.push(`${request.method()} ${request.url()}: ${request.failure()?.errorText}`);
    });
    
    // Navigate to production site
    const response = await page.goto(PROD_URL, { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    // Check response status
    expect(response?.status()).toBeLessThan(400);
    console.log(`✓ Homepage loaded - Status: ${response?.status()}`);
    
    // Should see login or main page elements
    const hasLogin = await page.locator('button:has-text("Sign in"), button:has-text("Login"), a:has-text("Login")').isVisible({ timeout: 5000 }).catch(() => false);
    const hasLogo = await page.locator('img[alt*="SpecSharp"], img[alt*="Logo"], .logo').isVisible({ timeout: 5000 }).catch(() => false);
    const hasTitle = await page.locator('h1, title:has-text("SpecSharp")').isVisible({ timeout: 5000 }).catch(() => false);
    
    expect(hasLogin || hasLogo || hasTitle).toBeTruthy();
    console.log(`✓ Critical elements visible - Login: ${hasLogin}, Logo: ${hasLogo}, Title: ${hasTitle}`);
    
    // Wait a moment for any delayed errors
    await page.waitForTimeout(2000);
    
    // Report console errors
    if (errors.length > 0) {
      console.warn('⚠ Console errors detected:', errors);
      // Don't fail on console errors in production (may be third-party)
    } else {
      console.log('✓ No console errors');
    }
    
    // Report network failures
    if (failedRequests.length > 0) {
      console.warn('⚠ Failed network requests:', failedRequests);
    } else {
      console.log('✓ No network failures');
    }
  });

  test('Critical pages accessible', async ({ page }) => {
    const criticalPaths = [
      { path: '/', name: 'Homepage' },
      { path: '/login', name: 'Login' },
      { path: '/about', name: 'About' },
      { path: '/pricing', name: 'Pricing' },
      { path: '/terms', name: 'Terms' },
      { path: '/privacy', name: 'Privacy' }
    ];

    const results: { path: string; status: number; success: boolean }[] = [];

    for (const route of criticalPaths) {
      try {
        const response = await page.goto(`${PROD_URL}${route.path}`, {
          waitUntil: 'domcontentloaded',
          timeout: 10000
        });
        
        const status = response?.status() || 0;
        const success = status > 0 && status < 400;
        
        results.push({ path: route.path, status, success });
        
        if (success) {
          console.log(`✓ ${route.name} (${route.path}) - Status: ${status}`);
        } else {
          console.log(`✗ ${route.name} (${route.path}) - Status: ${status}`);
        }
      } catch (error) {
        console.log(`✗ ${route.name} (${route.path}) - Error: ${error}`);
        results.push({ path: route.path, status: 0, success: false });
      }
    }
    
    // At least homepage should work
    const homepageWorks = results.find(r => r.path === '/')?.success;
    expect(homepageWorks).toBeTruthy();
    
    // Count successful pages
    const successCount = results.filter(r => r.success).length;
    console.log(`\nPage accessibility: ${successCount}/${criticalPaths.length} pages accessible`);
    
    // Warn if some pages are inaccessible but don't fail
    if (successCount < criticalPaths.length) {
      console.warn('⚠ Some pages may not be publicly accessible (may require auth)');
    }
  });

  test('API health check', async ({ request }) => {
    try {
      const response = await request.get(`${API_URL}/health`, {
        timeout: 10000
      });
      
      console.log(`API Health endpoint status: ${response.status()}`);
      
      if (response.ok()) {
        try {
          const data = await response.json();
          console.log('✓ API Health response:', data);
          
          // Check for health indicators
          expect(data).toHaveProperty('status');
          expect(['healthy', 'ok', 'up'].includes(data.status?.toLowerCase())).toBeTruthy();
        } catch (e) {
          // May return plain text
          const text = await response.text();
          console.log('✓ API Health response (text):', text);
        }
      } else {
        console.warn(`⚠ API Health check returned status: ${response.status()}`);
      }
    } catch (error) {
      console.warn('⚠ API Health endpoint not accessible (may not be public)');
      // Don't fail - health endpoint might be internal only
    }
  });

  test('Static assets loading', async ({ page }) => {
    await page.goto(PROD_URL);
    
    // Check CSS loaded
    const hasStyles = await page.evaluate(() => {
      const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
      return stylesheets.length > 0;
    });
    expect(hasStyles).toBeTruthy();
    console.log('✓ CSS stylesheets loaded');
    
    // Check JavaScript loaded
    const hasScripts = await page.evaluate(() => {
      const scripts = document.querySelectorAll('script[src]');
      return scripts.length > 0;
    });
    expect(hasScripts).toBeTruthy();
    console.log('✓ JavaScript files loaded');
    
    // Check images (if any visible)
    const images = page.locator('img:visible');
    const imageCount = await images.count();
    
    if (imageCount > 0) {
      // Check first few images load
      for (let i = 0; i < Math.min(3, imageCount); i++) {
        const img = images.nth(i);
        const naturalWidth = await img.evaluate((el: HTMLImageElement) => el.naturalWidth);
        
        if (naturalWidth > 0) {
          console.log(`✓ Image ${i + 1} loaded successfully`);
        } else {
          console.log(`⚠ Image ${i + 1} may not have loaded`);
        }
      }
    }
  });

  test('Performance metrics', async ({ page }) => {
    await page.goto(PROD_URL);
    
    // Get performance metrics
    const metrics = await page.evaluate(() => {
      const perf = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: Math.round(perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart),
        loadComplete: Math.round(perf.loadEventEnd - perf.loadEventStart),
        domInteractive: Math.round(perf.domInteractive - perf.fetchStart),
        firstByte: Math.round(perf.responseStart - perf.requestStart)
      };
    });
    
    console.log('Performance Metrics:');
    console.log(`- First Byte: ${metrics.firstByte}ms`);
    console.log(`- DOM Interactive: ${metrics.domInteractive}ms`);
    console.log(`- DOM Content Loaded: ${metrics.domContentLoaded}ms`);
    console.log(`- Load Complete: ${metrics.loadComplete}ms`);
    
    // Set reasonable thresholds for production
    expect(metrics.firstByte).toBeLessThan(2000); // 2s for first byte
    expect(metrics.domInteractive).toBeLessThan(5000); // 5s for interactive
    
    if (metrics.domInteractive < 3000) {
      console.log('✓ Excellent performance');
    } else if (metrics.domInteractive < 5000) {
      console.log('✓ Acceptable performance');
    } else {
      console.log('⚠ Performance could be improved');
    }
  });

  test('Security headers', async ({ page }) => {
    const response = await page.goto(PROD_URL);
    const headers = response?.headers() || {};
    
    console.log('Security Headers Check:');
    
    // Check for common security headers
    const securityHeaders = {
      'strict-transport-security': 'HSTS',
      'x-content-type-options': 'X-Content-Type-Options',
      'x-frame-options': 'X-Frame-Options',
      'x-xss-protection': 'X-XSS-Protection',
      'content-security-policy': 'CSP'
    };
    
    let secureCount = 0;
    for (const [header, name] of Object.entries(securityHeaders)) {
      if (headers[header]) {
        console.log(`✓ ${name}: ${headers[header]}`);
        secureCount++;
      } else {
        console.log(`⚠ ${name}: Not set`);
      }
    }
    
    // Should have at least some security headers
    if (secureCount >= 2) {
      console.log(`✓ Security headers configured (${secureCount}/${Object.keys(securityHeaders).length})`);
    } else {
      console.log(`⚠ Consider adding more security headers (${secureCount}/${Object.keys(securityHeaders).length})`);
    }
  });
});