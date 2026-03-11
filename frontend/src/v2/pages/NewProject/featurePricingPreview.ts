import type {
  AvailableSpecialFeaturePricing,
  SpecialFeaturePricingBasis,
  SpecialFeaturePricingCountBand,
  SpecialFeaturePricingStatus,
} from '../../types';

export type FeaturePricingStatus = SpecialFeaturePricingStatus;

export type FeatureDisplayPricing = {
  amountLabel: string;
  detailLabel?: string;
  totalCost?: number;
  isEstimate: boolean;
  isPlaceholder: boolean;
  pricingStatus: FeaturePricingStatus | null;
  pricingBasis: SpecialFeaturePricingBasis | null;
  statusLabel?: string;
};

export function indexAvailableSpecialFeaturePricing(
  rows?: AvailableSpecialFeaturePricing[] | null,
): Record<string, AvailableSpecialFeaturePricing> {
  if (!Array.isArray(rows)) {
    return {};
  }

  return rows.reduce<Record<string, AvailableSpecialFeaturePricing>>((acc, row) => {
    if (row && typeof row.id === 'string' && typeof row.pricing_status === 'string') {
      acc[row.id] = row;
    }
    return acc;
  }, {});
}

export function getFeatureDisplayPricingPreview(params: {
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  fallbackCostPerSF?: number;
  fallbackStaticCost?: number;
  usesSubtypeCostPerSF: boolean;
  hasFeatureSquareFootage: boolean;
  squareFootageSummary?: number;
}): FeatureDisplayPricing {
  const {
    backendFeaturePricing,
    fallbackCostPerSF,
    fallbackStaticCost,
    usesSubtypeCostPerSF,
    hasFeatureSquareFootage,
    squareFootageSummary,
  } = params;

  if (backendFeaturePricing?.pricing_status === 'included_in_baseline') {
    return {
      amountLabel: 'Included in baseline',
      detailLabel: 'No additional premium for this subtype',
      totalCost: 0,
      isEstimate: false,
      isPlaceholder: false,
      pricingStatus: 'included_in_baseline',
      pricingBasis: resolvePricingBasis(backendFeaturePricing) ?? null,
    };
  }

  const pricingBasis = resolvePricingBasis(backendFeaturePricing) ?? null;
  const costPerSF = backendFeaturePricing?.configured_cost_per_sf ?? fallbackCostPerSF;
  const pricingStatus = backendFeaturePricing?.pricing_status ?? null;
  const statusLabel = pricingStatus === 'incremental' ? 'Incremental premium' : undefined;

  if (pricingBasis === 'COUNT_BASED') {
    const unitLabel = backendFeaturePricing?.unit_label ?? 'item';
    const costPerCount = getConfiguredCountRate(backendFeaturePricing);
    const resolvedCount = resolveConfiguredCount({
      backendFeaturePricing,
      squareFootageSummary,
    });

    if (typeof costPerCount === 'number' && typeof resolvedCount === 'number') {
      const totalCost = costPerCount * resolvedCount;
      return {
        amountLabel: `+${formatCurrency(totalCost)}`,
        detailLabel: `${formatCurrency(costPerCount)} per ${unitLabel} × ${formatQuantityWithUnit(resolvedCount, unitLabel)}`,
        totalCost,
        isEstimate: false,
        isPlaceholder: false,
        pricingStatus,
        pricingBasis,
        statusLabel,
      };
    }

    if (typeof costPerCount === 'number') {
      return {
        amountLabel: `+${formatCurrency(costPerCount)} per ${unitLabel}`,
        detailLabel: hasFeatureSquareFootage
          ? 'Count-based premium'
          : 'Estimate until project size is provided',
        isEstimate: true,
        isPlaceholder: false,
        pricingStatus,
        pricingBasis,
        statusLabel,
      };
    }
  }

  if (usesSubtypeCostPerSF && typeof costPerSF === 'number') {
    if (hasFeatureSquareFootage && squareFootageSummary) {
      const totalCost = costPerSF * squareFootageSummary;
      return {
        amountLabel: `+${formatCurrency(totalCost)}`,
        detailLabel: `${formatCurrency(costPerSF)}/SF × ${formatNumber(squareFootageSummary)} SF`,
        totalCost,
        isEstimate: false,
        isPlaceholder: false,
        pricingStatus,
        pricingBasis,
        statusLabel,
      };
    }

    return {
      amountLabel: `+${formatCurrency(costPerSF)}/SF`,
      detailLabel: 'Estimate until project SF is provided',
      isEstimate: true,
      isPlaceholder: false,
      pricingStatus,
      pricingBasis,
      statusLabel,
    };
  }

  if (typeof fallbackStaticCost === 'number' && Number.isFinite(fallbackStaticCost)) {
    return {
      amountLabel: `+${formatCurrency(fallbackStaticCost)}`,
      detailLabel: usesSubtypeCostPerSF ? 'Estimate placeholder' : 'Static placeholder value',
      totalCost: fallbackStaticCost,
      isEstimate: true,
      isPlaceholder: true,
      pricingStatus,
      pricingBasis,
      statusLabel,
    };
  }

  return {
    amountLabel: '+—',
    detailLabel: 'Pricing unavailable',
    isEstimate: true,
    isPlaceholder: true,
    pricingStatus,
    pricingBasis,
    statusLabel,
  };
}

function getConfiguredCountRate(
  backendFeaturePricing?: AvailableSpecialFeaturePricing,
): number | undefined {
  const value = backendFeaturePricing?.configured_cost_per_count ?? backendFeaturePricing?.configured_value;
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function resolvePricingBasis(
  backendFeaturePricing?: AvailableSpecialFeaturePricing,
): SpecialFeaturePricingBasis | undefined {
  if (!backendFeaturePricing) {
    return undefined;
  }
  if (backendFeaturePricing.pricing_basis) {
    return backendFeaturePricing.pricing_basis;
  }
  if (
    typeof backendFeaturePricing.configured_cost_per_count === 'number' &&
    Number.isFinite(backendFeaturePricing.configured_cost_per_count)
  ) {
    return 'COUNT_BASED';
  }
  if (
    typeof backendFeaturePricing.configured_cost_per_sf === 'number' &&
    Number.isFinite(backendFeaturePricing.configured_cost_per_sf)
  ) {
    return 'WHOLE_PROJECT_SF';
  }
  return undefined;
}

function resolveConfiguredCount(params: {
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  squareFootageSummary?: number;
}): number | undefined {
  const { backendFeaturePricing, squareFootageSummary } = params;
  if (!backendFeaturePricing) {
    return undefined;
  }

  if (
    typeof backendFeaturePricing.configured_count === 'number' &&
    Number.isFinite(backendFeaturePricing.configured_count)
  ) {
    return backendFeaturePricing.configured_count;
  }

  if (
    typeof squareFootageSummary === 'number' &&
    squareFootageSummary > 0 &&
    Array.isArray(backendFeaturePricing.configured_count_bands)
  ) {
    const resolvedBand = backendFeaturePricing.configured_count_bands.find((band) =>
      matchesSquareFootageBand(band, squareFootageSummary)
    );
    if (resolvedBand && typeof resolvedBand.count === 'number' && Number.isFinite(resolvedBand.count)) {
      return resolvedBand.count;
    }
  }

  return undefined;
}

function matchesSquareFootageBand(
  band: SpecialFeaturePricingCountBand,
  squareFootageSummary: number,
): boolean {
  if (typeof band.max_square_footage !== 'number' || !Number.isFinite(band.max_square_footage)) {
    return true;
  }
  return squareFootageSummary <= band.max_square_footage;
}

function formatQuantityWithUnit(quantity: number, unitLabel: string): string {
  return `${formatNumber(quantity)} ${pluralizeUnitLabel(unitLabel, quantity)}`;
}

function pluralizeUnitLabel(unitLabel: string, quantity: number): string {
  if (quantity === 1) {
    return unitLabel;
  }
  if (/[^aeiou]y$/i.test(unitLabel)) {
    return `${unitLabel.slice(0, -1)}ies`;
  }
  if (/(s|x|z|ch|sh)$/i.test(unitLabel)) {
    return `${unitLabel}es`;
  }
  return `${unitLabel}s`;
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: value >= 100 ? 0 : 2,
  }).format(value);
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(value);
}
