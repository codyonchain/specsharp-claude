export interface MultifamilyMetrics {
  units: number;
  monthlyRent: number;
  annualRevenue: number;
  revenuePerUnit: number;
  noi: number;
  capRate: number;
  metrics: Record<string, string | number>;
}

export const getMultifamilyMetrics = (squareFootage: number, subtype: string): MultifamilyMetrics => {
  const avgUnitSize = subtype === 'luxury_apartments' ? 1100 : 
                      subtype === 'affordable_housing' ? 750 : 
                      subtype === 'senior_living' ? 950 :
                      subtype === 'student_housing' ? 850 : 900;
  
  const units = Math.round(squareFootage / avgUnitSize);
  
  const monthlyRents: Record<string, number> = {
    luxury_apartments: 3500,
    market_rate_apartments: 2200,
    affordable_housing: 1200,
    senior_living: 2800,
    student_housing: 1500
  };
  
  const monthlyRent = monthlyRents[subtype] || 2000;
  const occupancyRate = 0.93; // 93% stabilized occupancy
  const noiMargin = subtype === 'luxury_apartments' ? 0.60 : 
                    subtype === 'affordable_housing' ? 0.45 : 0.55;
  
  const annualRevenue = units * monthlyRent * 12 * occupancyRate;
  const noi = annualRevenue * noiMargin;
  
  return {
    units,
    monthlyRent,
    annualRevenue,
    revenuePerUnit: monthlyRent * 12,
    noi,
    capRate: 0.055, // 5.5% cap rate for luxury
    metrics: {
      'Total Units': units,
      'Avg Unit Size': `${avgUnitSize} SF`,
      'Monthly Rent': `$${monthlyRent.toLocaleString()}`,
      'Annual Revenue': `$${(annualRevenue / 1000000).toFixed(1)}M`,
      'Stabilized Occupancy': '93%',
      'NOI Margin': `${(noiMargin * 100).toFixed(0)}%`,
      'Net Operating Income': `$${(noi / 1000000).toFixed(1)}M`
    }
  };
};

export const getMultifamilyDepartments = () => {
  return [
    {
      name: 'Residential Units',
      percent: 0.70,
      description: 'Individual apartment units including bedrooms, bathrooms, kitchens',
      icon: 'Home'
    },
    {
      name: 'Common Areas & Lobbies',
      percent: 0.20,
      description: 'Hallways, lobbies, mail rooms, elevators, stairwells',
      icon: 'Users'
    },
    {
      name: 'Amenities & Recreation',
      percent: 0.10,
      description: 'Pool, gym, clubhouse, business center, outdoor spaces',
      icon: 'Shield'
    }
  ];
};

export const getMultifamilyDecisionPoints = (
  totalCost: number, 
  units: number, 
  monthlyRent: number,
  subtype: string
): string[] => {
  const costPerUnit = totalCost / units;
  
  return [
    `Cost per unit: ${new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(costPerUnit)}`,
    `${units} units with monthly rent of ${new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(monthlyRent)}`,
    subtype === 'luxury_apartments' ? 
      'Premium amenities justify 25% rent premium over market' :
      'Strategic positioning for workforce housing demand',
    'Consider phased leasing strategy over 18-24 months for stabilization'
  ];
};