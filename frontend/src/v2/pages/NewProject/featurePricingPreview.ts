export type FeaturePricingStatus = 'included_in_baseline' | 'incremental';

export interface AvailableSpecialFeaturePricing {
  id: string;
  label: string;
  pricing_status: FeaturePricingStatus;
  configured_cost_per_sf: number;
}

export type FeatureDisplayPricing = {
  amountLabel: string;
  detailLabel?: string;
  totalCost?: number;
  isEstimate: boolean;
  isPlaceholder: boolean;
  pricingStatus: FeaturePricingStatus | null;
  statusLabel?: string;
};

export function indexAvailableSpecialFeaturePricing(
  rows?: AvailableSpecialFeaturePricing[] | null,
): Record<string, AvailableSpecialFeaturePricing> {
  if (!Array.isArray(rows)) {
    return {};
  }

  return rows.reduce<Record<string, AvailableSpecialFeaturePricing>>((acc, row) => {
    if (
      row &&
      typeof row.id === 'string' &&
      typeof row.pricing_status === 'string' &&
      typeof row.configured_cost_per_sf === 'number' &&
      Number.isFinite(row.configured_cost_per_sf)
    ) {
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
    };
  }

  const costPerSF = backendFeaturePricing?.configured_cost_per_sf ?? fallbackCostPerSF;
  const pricingStatus = backendFeaturePricing?.pricing_status ?? null;
  const statusLabel = pricingStatus === 'incremental' ? 'Incremental premium' : undefined;

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
        statusLabel,
      };
    }

    return {
      amountLabel: `+${formatCurrency(costPerSF)}/SF`,
      detailLabel: 'Estimate until project SF is provided',
      isEstimate: true,
      isPlaceholder: false,
      pricingStatus,
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
      statusLabel,
    };
  }

  return {
    amountLabel: '+—',
    detailLabel: 'Pricing unavailable',
    isEstimate: true,
    isPlaceholder: true,
    pricingStatus,
    statusLabel,
  };
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
