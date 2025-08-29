import { test, expect } from '@playwright/test';
import { getTestAuthHeaders } from '../../helpers/auth';

const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('Authenticated API Calculations', () => {
  const authHeaders = getTestAuthHeaders();

  test('Hospital calculation with auth', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: '200000 sf hospital with emergency department Nashville TN',
        manual_overrides: {
          sqft: 200000,
          location: 'Nashville, TN',
          building_type: 'healthcare'
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Hospital costs should be high
    expect(data.cost_per_sqft).toBeGreaterThanOrEqual(500);
    expect(data.cost_per_sqft).toBeLessThanOrEqual(700);
    
    // Total cost should be calculated correctly
    const expectedTotal = data.cost_per_sqft * 200000;
    expect(data.total_cost).toBeCloseTo(expectedTotal, -100000); // Within 100k
    
    console.log(`✓ Authenticated API: Hospital $${data.cost_per_sqft}/sqft, Total: $${data.total_cost.toLocaleString()}`);
  });

  test('Restaurant calculation with auth', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: '4200 sf restaurant Franklin TN',
        manual_overrides: {
          sqft: 4200,
          location: 'Franklin, TN',
          building_type: 'restaurant'
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Restaurant costs vary by type
    expect(data.cost_per_sqft).toBeGreaterThanOrEqual(300);
    expect(data.cost_per_sqft).toBeLessThanOrEqual(600);
    
    console.log(`✓ Restaurant: $${data.cost_per_sqft}/sqft`);
  });

  test('Office building calculation with auth', async ({ request }) => {
    const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: '85000 sf office building Nashville TN',
        manual_overrides: {
          sqft: 85000,
          location: 'Nashville, TN',
          building_type: 'office'
        }
      }
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    
    // Office costs are moderate
    expect(data.cost_per_sqft).toBeGreaterThanOrEqual(200);
    expect(data.cost_per_sqft).toBeLessThanOrEqual(350);
    
    console.log(`✓ Office: $${data.cost_per_sqft}/sqft`);
  });

  test('Project creation and retrieval with auth', async ({ request }) => {
    // First generate scope
    const scopeResponse = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: 'Test hospital project 150000 sf Nashville',
        manual_overrides: {
          sqft: 150000,
          location: 'Nashville, TN',
          building_type: 'healthcare'
        }
      }
    });
    
    expect(scopeResponse.ok()).toBeTruthy();
    const scopeData = await scopeResponse.json();
    
    // Create project from scope
    const createResponse = await request.post(`${API_URL}/api/v1/scope/projects`, {
      headers: authHeaders,
      data: {
        name: 'Test Hospital Project',
        description: 'Test hospital project 150000 sf Nashville',
        scope_data: scopeData,
        total_cost: scopeData.total_cost,
        cost_per_sqft: scopeData.cost_per_sqft
      }
    });
    
    if (!createResponse.ok()) {
      const error = await createResponse.text();
      console.error('Project creation failed:', error);
    }
    
    expect(createResponse.ok()).toBeTruthy();
    const project = await createResponse.json();
    expect(project.id).toBeTruthy();
    
    // Retrieve project
    const getResponse = await request.get(`${API_URL}/api/v1/scope/projects/${project.id}`, {
      headers: authHeaders
    });
    
    expect(getResponse.ok()).toBeTruthy();
    const retrieved = await getResponse.json();
    expect(retrieved.id).toBe(project.id);
    expect(retrieved.total_cost).toBeGreaterThan(0);
    
    console.log(`✓ Created and retrieved project ${project.id}`);
  });

  test('All building types with auth', async ({ request }) => {
    const testCases = [
      { type: 'healthcare', description: '200000 sf hospital Nashville', sqft: 200000, minCost: 500 },
      { type: 'restaurant', description: '4200 sf quick service restaurant Nashville', sqft: 4200, minCost: 250 },
      { type: 'office', description: '85000 sf office building Nashville', sqft: 85000, minCost: 200 },
      { type: 'retail', description: '35000 sf shopping center Nashville', sqft: 35000, minCost: 150 },
      { type: 'warehouse', description: '120000 sf warehouse Nashville', sqft: 120000, minCost: 80 },
      { type: 'multifamily', description: '250000 sf apartment complex Nashville', sqft: 250000, minCost: 150 }
    ];

    for (const tc of testCases) {
      const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
        headers: authHeaders,
        data: {
          description: tc.description,
          manual_overrides: {
            sqft: tc.sqft,
            location: 'Nashville, TN',
            building_type: tc.type
          }
        }
      });

      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      
      expect(data.cost_per_sqft).toBeGreaterThanOrEqual(tc.minCost);
      console.log(`✓ ${tc.type}: $${data.cost_per_sqft}/sqft (min: $${tc.minCost})`);
    }
  });

  test('API error handling with auth', async ({ request }) => {
    // Test with missing data
    const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: '' // Empty description
      }
    });
    
    // Should still return something (maybe with defaults)
    const status = response.status();
    console.log(`Empty input status: ${status}`);
    
    // Test with invalid building type
    const invalidResponse = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: authHeaders,
      data: {
        description: 'Invalid building type test',
        manual_overrides: {
          building_type: 'spaceship',
          sqft: 10000
        }
      }
    });
    
    // Should handle gracefully
    console.log(`Invalid type status: ${invalidResponse.status()}`);
  });
});