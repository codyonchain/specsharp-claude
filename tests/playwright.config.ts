import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  outputDir: './reports/playwright-results',

  // Keep launch coverage serial enough to preserve a truthful signal.
  fullyParallel: false,

  // Fail the build on CI if you accidentally left test.only
  forbidOnly: !!process.env.CI,

  // Avoid masking flake with retries in the primary launch signal.
  retries: 0,

  // Parallel workers
  workers: 1,

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: './reports/playwright-html', open: 'never' }],
    ['json', { outputFile: './reports/test-results.json' }],
    ['list']
  ],

  use: {
    // Base URL for tests
    baseURL: process.env.TEST_BASE_URL || 'http://localhost:3000',

    // Collect trace on failure without relying on retries.
    trace: 'retain-on-failure',

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
  ],

  // Local runs use the same server commands CI maps to this suite.
  webServer: process.env.CI ? undefined : [
    {
      command: 'npm run frontend:test',
      url: 'http://localhost:3000',
      reuseExistingServer: true,
      timeout: 120 * 1000,
    },
    {
      command: 'npm run backend:test',
      url: 'http://127.0.0.1:8001/health',
      reuseExistingServer: true,
      timeout: 120 * 1000,
    }
  ],
});
