import { test, expect } from '@playwright/test';

const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('API Tests: healthcare - medical_office', () => {

  test('Medical Office Manchester - API Response', async ({ request }) => {
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
        special_requirements: '45000 sf medical office building in Manchester NH',
        square_footage: 45000,
        location: 'Manchester, NH',
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
    expect(costPerSqft).toBeGreaterThanOrEqual(320);
    expect(costPerSqft).toBeLessThanOrEqual(380);
    
    const totalCost = data.total_cost;
    expect(totalCost).toBeGreaterThanOrEqual(14400000);
    expect(totalCost).toBeLessThanOrEqual(17100000);
  });

});
