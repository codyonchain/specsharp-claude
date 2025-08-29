import { test, expect } from '@playwright/test';

const API_URL = process.env.API_URL || 'http://localhost:8001';

test.describe('API Tests: residential - apartments', () => {

  test('Luxury Apartments Brentwood - API Response', async ({ request }) => {
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
        special_requirements: '250-unit luxury apartment complex with amenity deck in Brentwood TN',
        square_footage: 250000,
        location: 'Brentwood, TN',
        building_type: 'residential'
      }
    });

    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    
    // Validate response structure
    expect(data).toHaveProperty('cost_per_sqft');
    expect(data).toHaveProperty('total_cost');
    
    // Validate calculations
    const costPerSqft = data.cost_per_sqft;
    expect(costPerSqft).toBeGreaterThanOrEqual(180);
    expect(costPerSqft).toBeLessThanOrEqual(220);
    
    const totalCost = data.total_cost;
    expect(totalCost).toBeGreaterThanOrEqual(45000000);
    expect(totalCost).toBeLessThanOrEqual(55000000);
  });

});
