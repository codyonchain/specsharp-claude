import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  outputDir: './reports/playwright-results',
  
  // Run tests in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Parallel workers
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration
  reporter: [
    ['html', { outputFolder: './reports/playwright-html', open: 'never' }],
    ['json', { outputFile: './reports/test-results.json' }],
    ['list']
  ],
  
  use: {
    // Base URL for tests
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:3000',
    
    // Collect trace when retrying the failed test
    trace: 'on-first-retry',
    
    // Screenshot settings for visual regression
    screenshot: {
      mode: 'only-on-failure',
      fullPage: true
    },
    
    // Video on failure
    video: 'retain-on-failure',
    
    // Visual regression settings
    ignoreHTTPSErrors: true,
  },
  
  // Visual regression comparison settings
  expect: {
    toHaveScreenshot: {
      maxDiffPixels: 100,
      threshold: 0.2,
      animations: 'disabled'
    }
  },

  // Configure projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Can add Firefox/Safari later if needed
  ],

  // Run local dev server before starting tests (only in dev)
  webServer: process.env.CI ? undefined : [
    {
      command: 'cd frontend && npm run dev',
      port: 3000,
      reuseExistingServer: true,
    },
    {
      command: 'cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8001',
      port: 8001,
      reuseExistingServer: true,
    }
  ],
});