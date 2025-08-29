#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const testDataPath = path.join(__dirname, '../../tests/config/test-data.json');
const testData = JSON.parse(fs.readFileSync(testDataPath, 'utf-8'));

// Template for E2E building type tests
const e2eTestTemplate = (buildingType, subtype, testCases) => `import { test, expect } from '@playwright/test';
import { TestDataManager } from '../../config/helpers';

const testData = TestDataManager.getInstance();

test.describe('${buildingType} - ${subtype} Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test2@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button:has-text("Login")');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    
    // Navigate to new project
    await page.goto('/scope/new');
  });
${testCases.map(tc => `
  test('${tc.name} - Cost Calculation', async ({ page }) => {
    // Fill in the project description
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    await descriptionInput.fill('${tc.input.description}');
    
    // Click analyze
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    
    // Wait for results
    await page.waitForSelector('text=/\\\\$[0-9,]+/', { timeout: 15000 });
    
    // Get calculated values - look for cost per sqft display
    const costTexts = await page.locator('text=/\\\\$[0-9,]+\\\\/s?f/i').allTextContents();
    
    if (costTexts.length > 0) {
      // Parse the first cost per sqft value found
      const costPerSqft = parseFloat(costTexts[0].replace(/[^0-9.]/g, ''));
      
      // Validate cost is within expected range
      expect(costPerSqft).toBeGreaterThanOrEqual(${tc.expected.calculations.costPerSqft.min});
      expect(costPerSqft).toBeLessThanOrEqual(${tc.expected.calculations.costPerSqft.max});
    }
    
    // Validate total cost if visible
    const totalCostElement = page.locator('text=/Total.*\\\\$[0-9,]+[MK]?/i');
    if (await totalCostElement.isVisible()) {
      const totalCostText = await totalCostElement.textContent();
      let totalCost = parseFloat(totalCostText.replace(/[^0-9.MK]/g, ''));
      
      // Convert M (millions) or K (thousands) to actual number
      if (totalCostText.includes('M')) totalCost *= 1000000;
      if (totalCostText.includes('K')) totalCost *= 1000;
      
      expect(totalCost).toBeGreaterThanOrEqual(${tc.expected.calculations.totalCost.min});
      expect(totalCost).toBeLessThanOrEqual(${tc.expected.calculations.totalCost.max});
    }
  });
${tc.expected.trades ? `
  test('${tc.name} - Trade Breakdown', async ({ page }) => {
    // Create project first
    const descriptionInput = page.locator('textarea[placeholder*="describe"], textarea[placeholder*="natural language"]').first();
    await descriptionInput.fill('${tc.input.description}');
    await page.click('button:has-text("Generate"), button:has-text("Analyze")');
    await page.waitForSelector('text=/\\\\$[0-9,]+/', { timeout: 15000 });
    
    // Navigate to details if button exists
    const viewDetailsBtn = page.locator('button:has-text("View Details"), button:has-text("View Breakdown")');
    if (await viewDetailsBtn.isVisible()) {
      await viewDetailsBtn.click();
      await page.waitForTimeout(1000); // Wait for navigation
      
      // Check trade percentages${Object.entries(tc.expected.trades).map(([trade, exp]) => `
      const ${trade}Text = await page.locator('text=/${trade}/i').first().textContent();
      if (${trade}Text) {
        const ${trade}Pct = parseFloat(${trade}Text.replace(/[^0-9.]/g, '')) / 100;
        expect(Math.abs(${trade}Pct - ${exp.percentage})).toBeLessThanOrEqual(${exp.tolerance});
      }`).join('')}
    }
  });` : ''}
`).join('')}
});
`;

// Template for API integration tests
const apiTestTemplate = (buildingType, subtype, testCases) => `import { test, expect } from '@playwright/test';

const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('API Tests: ${buildingType} - ${subtype}', () => {
${testCases.map(tc => `
  test('${tc.name} - API Response', async ({ request }) => {
    // First login to get token
    const loginResponse = await request.post(\`\${API_URL}/api/v1/auth/token\`, {
      form: {
        username: 'test2@example.com',
        password: 'password123'
      }
    });
    
    const { access_token } = await loginResponse.json();
    
    // Now make the scope request
    const response = await request.post(\`\${API_URL}/api/v1/scope/generate\`, {
      headers: {
        'Authorization': \`Bearer \${access_token}\`
      },
      data: {
        special_requirements: '${tc.input.description}',
        square_footage: ${tc.input.sqft},
        location: '${tc.input.location}',
        building_type: '${tc.input.building_type}'
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Validate response structure
    expect(data).toHaveProperty('cost_per_sqft');
    expect(data).toHaveProperty('total_cost');
    
    // Validate calculations
    const costPerSqft = data.cost_per_sqft;
    expect(costPerSqft).toBeGreaterThanOrEqual(${tc.expected.calculations.costPerSqft.min});
    expect(costPerSqft).toBeLessThanOrEqual(${tc.expected.calculations.costPerSqft.max});
    
    const totalCost = data.total_cost;
    expect(totalCost).toBeGreaterThanOrEqual(${tc.expected.calculations.totalCost.min});
    expect(totalCost).toBeLessThanOrEqual(${tc.expected.calculations.totalCost.max});
  });
`).join('')}
});
`;

// Create directories if they don't exist
const e2eDir = path.join(__dirname, '../../tests/e2e/building-types');
const apiDir = path.join(__dirname, '../../tests/integration/api');

if (!fs.existsSync(e2eDir)) {
  fs.mkdirSync(e2eDir, { recursive: true });
}
if (!fs.existsSync(apiDir)) {
  fs.mkdirSync(apiDir, { recursive: true });
}

// Generate test files
console.log('🚀 Generating test files from test data...\n');

let generatedCount = 0;

Object.entries(testData.buildingTypes).forEach(([type, subtypes]) => {
  Object.entries(subtypes).forEach(([subtype, data]) => {
    // Generate E2E test
    const e2eContent = e2eTestTemplate(type, subtype, data.testCases);
    const e2eFilePath = path.join(e2eDir, `${type}-${subtype}.spec.ts`);
    
    fs.writeFileSync(e2eFilePath, e2eContent);
    console.log(`✅ Generated E2E test: ${type}-${subtype}.spec.ts`);
    
    // Generate API test
    const apiContent = apiTestTemplate(type, subtype, data.testCases);
    const apiFilePath = path.join(apiDir, `${type}-${subtype}.test.ts`);
    
    fs.writeFileSync(apiFilePath, apiContent);
    console.log(`✅ Generated API test: ${type}-${subtype}.test.ts`);
    
    generatedCount += 2;
  });
});

console.log('\n✨ Test generation complete!');
console.log(`Generated ${generatedCount} test files`);
console.log(`  - ${generatedCount/2} E2E test suites in tests/e2e/building-types/`);
console.log(`  - ${generatedCount/2} API test suites in tests/integration/api/`);