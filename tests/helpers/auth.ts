import { Page } from '@playwright/test';

// Test user configuration
export const TEST_USER = {
  id: 'test-user-123',
  email: 'test@specsharp.com',
  name: 'Test User',
  token: 'test-token-xyz'
};

/**
 * Bypass authentication for testing by setting test user in localStorage
 * This should only be used in test environments
 */
export async function bypassAuth(page: Page) {
  // Set test user and token in localStorage before navigation
  await page.addInitScript((testUser) => {
    localStorage.setItem('user', JSON.stringify(testUser));
    localStorage.setItem('token', testUser.token);
    localStorage.setItem('authToken', testUser.token);
    localStorage.setItem('isAuthenticated', 'true');
    
    // Also set in sessionStorage for components that might check there
    sessionStorage.setItem('user', JSON.stringify(testUser));
    sessionStorage.setItem('token', testUser.token);
    sessionStorage.setItem('authToken', testUser.token);
    
    // Set a flag to indicate we're in test mode
    window['__TEST_MODE__'] = true;
  }, TEST_USER);
}

/**
 * Alias for bypassAuth for consistency with new tests
 */
export async function setupTestAuth(page: Page) {
  return bypassAuth(page);
}

/**
 * Get auth headers for API requests
 */
export function getTestAuthHeaders() {
  return {
    'Authorization': `Bearer ${TEST_USER.token}`,
    'X-Test-Mode': 'true',
    'Content-Type': 'application/json'
  };
}

/**
 * Navigate directly to a protected route with auth bypass
 */
export async function navigateWithAuth(page: Page, url: string) {
  await bypassAuth(page);
  await page.goto(url);
  
  // Wait a moment for any auth checks to complete
  await page.waitForTimeout(500);
  
  // If we're redirected to login, try to bypass again
  if (page.url().includes('/login')) {
    console.log('⚠️ Redirected to login, attempting to bypass auth again');
    await page.evaluate(() => {
      const testUser = {
        id: 'test-user-123',
        email: 'test@specsharp.com',
        name: 'Test User'
      };
      localStorage.setItem('user', JSON.stringify(testUser));
      localStorage.setItem('token', 'test-token-123');
      localStorage.setItem('isAuthenticated', 'true');
    });
    
    // Try navigating again
    await page.goto(url);
  }
}

/**
 * Helper to check if we're authenticated in the test
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  return await page.evaluate(() => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    return !!(token && user);
  });
}

/**
 * Clear authentication (useful for testing logout scenarios)
 */
export async function clearAuth(page: Page) {
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}