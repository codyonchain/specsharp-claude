import { BackendDataMapper } from '../backendDataMapper';

describe('BackendDataMapper office facility metrics', () => {
  it('prefers the active office facility_metrics payload over stale top-level office keys', () => {
    const analysis = {
      parsed_input: {
        building_type: 'office',
        subtype: 'class_a',
        square_footage: 160000,
        location: 'Nashville, TN',
      },
      calculations: {
        project_info: {
          building_type: 'office',
          subtype: 'class_a',
          square_footage: 160000,
          location: 'Nashville, TN',
        },
        totals: {
          total_project_cost: 74440000,
          cost_per_sf: 465.25,
        },
        revenue_analysis: {
          annual_revenue: 6692800,
          net_income: 2955200,
        },
        return_metrics: {
          estimated_annual_noi: 2955200,
        },
        facility_metrics: {
          type: 'office',
          total_square_feet: 160000,
          metrics: [
            { id: 'cost_per_sf', label: 'All-in Cost per SF', value: 465.25, unit: '$/SF' },
            { id: 'revenue_per_sf', label: 'Revenue per SF', value: 41.83, unit: '$/SF' },
            { id: 'noi_per_sf', label: 'NOI per SF', value: 18.47, unit: '$/SF' },
          ],
        },
        total_gross_sf: 123456,
        total_building_area: 123456,
        total_project_cost: 12345678,
        rent_per_sf: 9.99,
        office_rent_per_sf: 8.88,
        noi_per_sf: 7.77,
        office_noi_per_sf: 6.66,
      },
    } as any;

    const displayData = BackendDataMapper.mapToDisplay(analysis);

    expect(displayData.facilityMetrics).toMatchObject({
      buildingSize: 160000,
      costPerSf: 465.25,
      revenuePerSf: 41.83,
      noiPerSf: 18.47,
    });
    expect(displayData.facilityMetrics).not.toHaveProperty('officeRentPerSf');
    expect(displayData.facilityMetrics).not.toHaveProperty('officeNoiPerSf');
    expect(displayData.facilityMetrics?.entries).toHaveLength(3);
  });

  it('leaves restaurant facility_metrics mapping unchanged', () => {
    const analysis = {
      parsed_input: {
        building_type: 'restaurant',
        subtype: 'full_service',
        square_footage: 8000,
        location: 'Nashville, TN',
      },
      calculations: {
        project_info: {
          building_type: 'restaurant',
          subtype: 'full_service',
          square_footage: 8000,
          location: 'Nashville, TN',
        },
        totals: {
          total_project_cost: 3700000,
          cost_per_sf: 462.5,
        },
        revenue_analysis: {
          annual_revenue: 1850000,
          net_income: 430000,
        },
        return_metrics: {
          estimated_annual_noi: 430000,
        },
        facility_metrics: {
          type: 'restaurant',
          total_square_feet: 8000,
          metrics: [
            { id: 'sales_per_sf', label: 'Sales per SF', value: 231.25, unit: '$/SF' },
            { id: 'noi_per_sf', label: 'NOI per SF', value: 53.75, unit: '$/SF' },
            { id: 'cost_per_sf', label: 'All-in Cost per SF', value: 462.5, unit: '$/SF' },
          ],
        },
      },
    } as any;

    const displayData = BackendDataMapper.mapToDisplay(analysis);

    expect(displayData.facilityMetrics).toMatchObject({
      type: 'restaurant',
      restaurantSalesPerSf: 231.25,
      restaurantNoiPerSf: 53.75,
      restaurantCostPerSf: 462.5,
      revenuePerSf: 231.25,
      noiPerSf: 53.75,
      costPerSf: 462.5,
    });
  });
});
