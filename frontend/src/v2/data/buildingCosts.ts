export const buildingCosts = {
  healthcare: {
    hospital: {
      base_cost_per_sf: 1150,  // Updated back to $1,150
      regional_multipliers: {
        'Nashville': 1.03,
        'Memphis': 0.98,
        'Knoxville': 0.95,
        'Chattanooga': 0.94
      },
      complexity_multipliers: {
        'ground_up': 1.00,
        'renovation': 0.85,
        'addition': 0.90
      },
      trade_percentages: {
        structural: 0.22,
        mechanical: 0.35,
        electrical: 0.15,
        plumbing: 0.18,
        finishes: 0.10
      }
    },
    clinic: {
      base_cost_per_sf: 850,
      // ... rest of clinic config
    }
  },
  // ... other building types
};