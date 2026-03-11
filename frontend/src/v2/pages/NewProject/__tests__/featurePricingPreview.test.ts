import { describe, expect, it } from 'vitest';

import {
  getFeatureDisplayPricingPreview,
  indexAvailableSpecialFeaturePricing,
} from '../featurePricingPreview';

describe('featurePricingPreview', () => {
  it('renders included-in-baseline features from backend-provided pricing status', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'bar',
        label: 'Bar',
        pricing_status: 'included_in_baseline',
        configured_cost_per_sf: 35,
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.bar,
      fallbackCostPerSF: 35,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 8000,
    });

    expect(pricing.pricingStatus).toBe('included_in_baseline');
    expect(pricing.amountLabel).toBe('Included in baseline');
    expect(pricing.totalCost).toBe(0);
  });

  it('renders incremental premiums from backend-provided pricing status', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'spa',
        label: 'Spa',
        pricing_status: 'incremental',
        configured_cost_per_sf: 60,
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.spa,
      fallbackCostPerSF: 60,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 10000,
    });

    expect(pricing.pricingStatus).toBe('incremental');
    expect(pricing.statusLabel).toBe('Incremental premium');
    expect(pricing.amountLabel).toBe('+$600,000');
  });

  it('preserves additive fallback behavior when backend pricing status is absent', () => {
    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: undefined,
      fallbackCostPerSF: 40,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 5000,
    });

    expect(pricing.pricingStatus).toBeNull();
    expect(pricing.statusLabel).toBeUndefined();
    expect(pricing.amountLabel).toBe('+$200,000');
  });
});
