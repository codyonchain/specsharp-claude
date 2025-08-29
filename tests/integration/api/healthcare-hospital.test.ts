import { test, expect } from '@playwright/test';

const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('API Tests: healthcare - hospital', () => {

  test('Large Hospital Nashville - API Response', async ({ request }) => {
    // First login to get token
    const loginResponse = await request.post(`${API_URL}/api/v1/auth/token`, {
      form: {
        username: 'test2@example.com',
        password: 'password123'
      }
    });
    
    const { access_token } = await loginResponse.json();
    
    // Now make the scope request
    const response = await request.post(`${API_URL}/api/v1/scope/generate`, {
      headers: {
        'Authorization': `Bearer ${access_token}`
      },
      data: {
        special_requirements: '200000 sf hospital with emergency department in Nashville TN',
        square_footage: 200000,
        location: 'Nashville, TN',
        building_type: 'healthcare'
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Validate response structure
    expect(data).toHaveProperty('cost_per_sqft');
    expect(data).toHaveProperty('total_cost');
    
    // Validate calculations
    const costPerSqft = data.cost_per_sqft;
    expect(costPerSqft).toBeGreaterThanOrEqual(1100);
    expect(costPerSqft).toBeLessThanOrEqual(1200);
    
    const totalCost = data.total_cost;
    expect(totalCost).toBeGreaterThanOrEqual(220000000);
    expect(totalCost).toBeLessThanOrEqual(240000000);
  });

});
