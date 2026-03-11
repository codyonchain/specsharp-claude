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

  it('indexes count-based backend pricing rows without requiring configured_cost_per_sf', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'hc_asc_hybrid_or_cath_lab',
        label: 'Hybrid OR / Cath Lab',
        pricing_status: 'incremental',
        pricing_basis: 'COUNT_BASED',
        configured_cost_per_count: 950000,
        configured_count: 1,
        unit_label: 'lab',
      },
    ]);

    expect(pricingById.hc_asc_hybrid_or_cath_lab).toBeDefined();
    expect(pricingById.hc_asc_hybrid_or_cath_lab.configured_cost_per_count).toBe(950000);
  });

  it('renders count-based incremental premiums from backend preview metadata', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'operating_room',
        label: 'Operating Room',
        pricing_status: 'incremental',
        pricing_basis: 'COUNT_BASED',
        configured_cost_per_count: 450000,
        configured_count_bands: [
          { label: 'small_asc', max_square_footage: 12000, count: 2 },
          { label: 'mid_asc', max_square_footage: 20000, count: 4 },
          { label: 'large_asc', count: 6 },
        ],
        unit_label: 'room',
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.operating_room,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 18000,
    });

    expect(pricing.pricingStatus).toBe('incremental');
    expect(pricing.pricingBasis).toBe('COUNT_BASED');
    expect(pricing.amountLabel).toBe('+$1,800,000');
    expect(pricing.detailLabel).toBe('$450,000 per room × 4 rooms');
    expect(pricing.totalCost).toBe(1800000);
    expect(pricing.explanationLines).toBeUndefined();
  });

  it('renders count-based included features as included in baseline', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'mri_suite',
        label: 'MRI Suite',
        pricing_status: 'included_in_baseline',
        pricing_basis: 'COUNT_BASED',
        configured_cost_per_count: 850000,
        configured_count: 1,
        unit_label: 'suite',
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.mri_suite,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 12000,
    });

    expect(pricing.pricingStatus).toBe('included_in_baseline');
    expect(pricing.pricingBasis).toBe('COUNT_BASED');
    expect(pricing.amountLabel).toBe('Included in baseline');
    expect(pricing.totalCost).toBe(0);
    expect(pricing.detailLabel).toBe('No additional premium for this subtype');
  });

  it('renders area-share incremental premiums from backend preview metadata', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'spa',
        label: 'Spa',
        pricing_status: 'incremental',
        pricing_basis: 'AREA_SHARE_GSF',
        configured_value: 60,
        configured_area_share_of_gsf: 0.04,
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.spa,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 85000,
    });

    expect(pricing.pricingStatus).toBe('incremental');
    expect(pricing.pricingBasis).toBe('AREA_SHARE_GSF');
    expect(pricing.statusLabel).toBe('Incremental premium');
    expect(pricing.amountLabel).toBe('+$204,000');
    expect(pricing.detailLabel).toBe(
      '$60.00 per feature-area SF × 3,400 SF assumed feature area'
    );
    expect(pricing.explanationLines).toEqual(['Assumed feature area = 4% of project GSF']);
    expect(pricing.totalCost).toBe(204000);
  });

  it('renders area-share included features as included in baseline', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'ballroom',
        label: 'Ballroom',
        pricing_status: 'included_in_baseline',
        pricing_basis: 'AREA_SHARE_GSF',
        configured_value: 50,
        configured_area_share_of_gsf: 0.08,
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.ballroom,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 85000,
    });

    expect(pricing.pricingStatus).toBe('included_in_baseline');
    expect(pricing.pricingBasis).toBe('AREA_SHARE_GSF');
    expect(pricing.amountLabel).toBe('Included in baseline');
    expect(pricing.detailLabel).toBe('No additional premium for this subtype');
    expect(pricing.explanationLines).toEqual(['Assumed feature area = 8% of project GSF']);
    expect(pricing.totalCost).toBe(0);
  });

  it('renders overage-mode count-based pricing with baseline, requested, and billed quantities', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'operating_room',
        label: 'Operating Room',
        pricing_status: 'included_in_baseline',
        pricing_basis: 'COUNT_BASED',
        count_pricing_mode: 'overage_above_default',
        configured_cost_per_count: 450000,
        requested_quantity: 6,
        requested_quantity_source: 'explicit_override:operating_room_count',
        included_baseline_quantity: 4,
        billed_quantity: 2,
        unit_label: 'room',
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.operating_room,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 18000,
    });

    expect(pricing.pricingStatus).toBe('incremental');
    expect(pricing.pricingBasis).toBe('COUNT_BASED');
    expect(pricing.statusLabel).toBe('Incremental premium');
    expect(pricing.amountLabel).toBe('+$900,000');
    expect(pricing.detailLabel).toBe('$450,000 per room × 2 rooms');
    expect(pricing.explanationLines).toEqual([
      'Baseline includes 4 rooms',
      'You specified 6 rooms',
      'Pricing includes 2 additional rooms',
    ]);
  });

  it('renders overage-mode no-overage cases without billing extra quantity', () => {
    const pricingById = indexAvailableSpecialFeaturePricing([
      {
        id: 'mri_suite',
        label: 'MRI Suite',
        pricing_status: 'included_in_baseline',
        pricing_basis: 'COUNT_BASED',
        count_pricing_mode: 'overage_above_default',
        configured_cost_per_count: 850000,
        requested_quantity: 1,
        requested_quantity_source: 'explicit_override:mri_suite_count',
        included_baseline_quantity: 1,
        billed_quantity: 0,
        unit_label: 'suite',
      },
    ]);

    const pricing = getFeatureDisplayPricingPreview({
      backendFeaturePricing: pricingById.mri_suite,
      usesSubtypeCostPerSF: true,
      hasFeatureSquareFootage: true,
      squareFootageSummary: 12000,
    });

    expect(pricing.pricingStatus).toBe('included_in_baseline');
    expect(pricing.amountLabel).toBe('Included in baseline');
    expect(pricing.detailLabel).toBe('No additional premium for this subtype');
    expect(pricing.explanationLines).toEqual([
      'Baseline includes 1 suite',
      'You specified 1 suite',
      'No additional suites priced',
    ]);
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
    expect(pricing.pricingBasis).toBeNull();
    expect(pricing.statusLabel).toBeUndefined();
    expect(pricing.amountLabel).toBe('+$200,000');
  });
});
