import type {
  AvailableSpecialFeaturePricing,
  SpecialFeatureBreakdownRow,
  SpecialFeatureCountPricingMode,
  SpecialFeaturePricingBasis,
  SpecialFeaturePricingCountBand,
  SpecialFeaturePricingStatus,
} from '../../types';

export type FeaturePricingStatus = SpecialFeaturePricingStatus;

export type FeatureDisplayPricing = {
  amountLabel: string;
  detailLabel?: string;
  explanationLines?: string[];
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
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  fallbackCostPerSF?: number;
  fallbackStaticCost?: number;
  usesSubtypeCostPerSF: boolean;
  hasFeatureSquareFootage: boolean;
  squareFootageSummary?: number;
}): FeatureDisplayPricing {
  const {
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    fallbackCostPerSF,
    fallbackStaticCost,
    usesSubtypeCostPerSF,
    hasFeatureSquareFootage,
    squareFootageSummary,
  } = params;

  const pricingBasis =
    resolvePricingBasis({
      backendAppliedFeaturePricing,
      backendFeaturePricing,
    }) ?? null;
  const sourcePricingStatus =
    backendAppliedFeaturePricing?.pricing_status ??
    backendFeaturePricing?.pricing_status ??
    null;

  const overageDisplayPricing = resolveOverageFeatureDisplayPricing({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    pricingBasis,
    sourcePricingStatus,
  });
  if (overageDisplayPricing) {
    return overageDisplayPricing;
  }

  const areaShareDisplayPricing = resolveAreaShareFeatureDisplayPricing({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    pricingBasis,
    sourcePricingStatus,
    hasFeatureSquareFootage,
    squareFootageSummary,
  });
  if (areaShareDisplayPricing) {
    return areaShareDisplayPricing;
  }

  if (sourcePricingStatus === 'included_in_baseline') {
    return {
      amountLabel: 'Included in baseline',
      detailLabel: 'No additional premium for this subtype',
      totalCost: 0,
      isEstimate: false,
      isPlaceholder: false,
      pricingStatus: 'included_in_baseline',
      pricingBasis,
    };
  }

  const costPerSF = backendFeaturePricing?.configured_cost_per_sf ?? fallbackCostPerSF;
  const pricingStatus = sourcePricingStatus;
  const statusLabel = pricingStatus === 'incremental' ? 'Incremental premium' : undefined;

  if (pricingBasis === 'COUNT_BASED') {
    const unitLabel =
      backendAppliedFeaturePricing?.unit_label ?? backendFeaturePricing?.unit_label ?? 'item';
    const costPerCount = getConfiguredCountRate({
      backendAppliedFeaturePricing,
      backendFeaturePricing,
    });
    const resolvedCount = resolveConfiguredCount({
      backendAppliedFeaturePricing,
      backendFeaturePricing,
      squareFootageSummary,
    });
    const appliedTotalCost = resolveAppliedCountTotalCost({
      backendAppliedFeaturePricing,
      costPerCount,
      resolvedCount,
    });

    if (
      typeof costPerCount === 'number' &&
      typeof resolvedCount === 'number' &&
      typeof appliedTotalCost === 'number'
    ) {
      return {
        amountLabel: `+${formatCurrency(appliedTotalCost)}`,
        detailLabel: `${formatCurrency(costPerCount)} per ${unitLabel} × ${formatQuantityWithUnit(resolvedCount, unitLabel)}`,
        totalCost: appliedTotalCost,
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
  params: {
    backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
    backendFeaturePricing?: AvailableSpecialFeaturePricing;
  },
): number | undefined {
  const { backendAppliedFeaturePricing, backendFeaturePricing } = params;
  const appliedValue =
    backendAppliedFeaturePricing?.cost_per_count ??
    backendAppliedFeaturePricing?.configured_cost_per_count;
  if (typeof appliedValue === 'number' && Number.isFinite(appliedValue)) {
    return appliedValue;
  }
  const value = backendFeaturePricing?.configured_cost_per_count ?? backendFeaturePricing?.configured_value;
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function resolvePricingBasis(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
}): SpecialFeaturePricingBasis | undefined {
  const { backendAppliedFeaturePricing, backendFeaturePricing } = params;
  if (backendAppliedFeaturePricing?.pricing_basis) {
    return backendAppliedFeaturePricing.pricing_basis;
  }
  if (
    typeof backendAppliedFeaturePricing?.configured_area_share_of_gsf === 'number' &&
    Number.isFinite(backendAppliedFeaturePricing.configured_area_share_of_gsf)
  ) {
    return 'AREA_SHARE_GSF';
  }
  if (
    typeof backendAppliedFeaturePricing?.configured_cost_per_count === 'number' ||
    typeof backendAppliedFeaturePricing?.cost_per_count === 'number'
  ) {
    return 'COUNT_BASED';
  }
  if (
    typeof backendAppliedFeaturePricing?.configured_cost_per_sf === 'number' ||
    typeof backendAppliedFeaturePricing?.cost_per_sf === 'number'
  ) {
    return 'WHOLE_PROJECT_SF';
  }
  if (!backendFeaturePricing) {
    return undefined;
  }
  if (backendFeaturePricing.pricing_basis) {
    return backendFeaturePricing.pricing_basis;
  }
  if (
    typeof backendFeaturePricing.configured_area_share_of_gsf === 'number' &&
    Number.isFinite(backendFeaturePricing.configured_area_share_of_gsf)
  ) {
    return 'AREA_SHARE_GSF';
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

function resolveAreaShareFeatureDisplayPricing(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  pricingBasis: SpecialFeaturePricingBasis | null;
  sourcePricingStatus: FeaturePricingStatus | null;
  hasFeatureSquareFootage: boolean;
  squareFootageSummary?: number;
}): FeatureDisplayPricing | undefined {
  const {
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    pricingBasis,
    sourcePricingStatus,
    hasFeatureSquareFootage,
    squareFootageSummary,
  } = params;
  if (pricingBasis !== 'AREA_SHARE_GSF') {
    return undefined;
  }

  const configuredAreaShareOfGsf = resolveNumericField(
    backendAppliedFeaturePricing?.configured_area_share_of_gsf,
    backendFeaturePricing?.configured_area_share_of_gsf,
  );
  const costPerFeatureAreaSF = resolveAreaShareRate({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
  });
  const appliedQuantity = resolveAreaShareQuantity({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    configuredAreaShareOfGsf,
    squareFootageSummary,
  });
  const totalCost = resolveAreaShareTotalCost({
    backendAppliedFeaturePricing,
    costPerFeatureAreaSF,
    appliedQuantity,
  });
  const explanationLines =
    typeof configuredAreaShareOfGsf === 'number'
      ? [`Assumed feature area = ${formatPercent(configuredAreaShareOfGsf)} of project GSF`]
      : undefined;
  const statusLabel = sourcePricingStatus === 'incremental' ? 'Incremental premium' : undefined;

  if (sourcePricingStatus === 'included_in_baseline') {
    return {
      amountLabel: 'Included in baseline',
      detailLabel: 'No additional premium for this subtype',
      explanationLines,
      totalCost: 0,
      isEstimate: false,
      isPlaceholder: false,
      pricingStatus: 'included_in_baseline',
      pricingBasis,
    };
  }

  if (
    typeof costPerFeatureAreaSF === 'number' &&
    typeof appliedQuantity === 'number' &&
    typeof totalCost === 'number'
  ) {
    return {
      amountLabel: `+${formatCurrency(totalCost)}`,
      detailLabel: `${formatCurrency(costPerFeatureAreaSF)} per feature-area SF × ${formatNumber(appliedQuantity)} SF assumed feature area`,
      explanationLines,
      totalCost,
      isEstimate: false,
      isPlaceholder: false,
      pricingStatus: sourcePricingStatus,
      pricingBasis,
      statusLabel,
    };
  }

  if (typeof costPerFeatureAreaSF === 'number') {
    return {
      amountLabel: `+${formatCurrency(costPerFeatureAreaSF)} per feature-area SF`,
      detailLabel:
        hasFeatureSquareFootage && typeof configuredAreaShareOfGsf === 'number'
          ? `Assumed feature area = ${formatPercent(configuredAreaShareOfGsf)} of project GSF`
          : 'Estimate until project SF is provided',
      explanationLines,
      isEstimate: true,
      isPlaceholder: false,
      pricingStatus: sourcePricingStatus,
      pricingBasis,
      statusLabel,
    };
  }

  return undefined;
}

function resolveAreaShareRate(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
}): number | undefined {
  const { backendAppliedFeaturePricing, backendFeaturePricing } = params;
  return resolveNumericField(
    backendAppliedFeaturePricing?.configured_cost_per_feature_area_sf,
    backendAppliedFeaturePricing?.configured_value,
    backendFeaturePricing?.configured_cost_per_feature_area_sf,
    backendFeaturePricing?.configured_value,
  );
}

function resolveAreaShareQuantity(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  configuredAreaShareOfGsf?: number;
  squareFootageSummary?: number;
}): number | undefined {
  const {
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    configuredAreaShareOfGsf,
    squareFootageSummary,
  } = params;
  const explicitQuantity = resolveNumericField(
    backendAppliedFeaturePricing?.applied_quantity,
    backendFeaturePricing?.applied_quantity,
  );
  if (typeof explicitQuantity === 'number') {
    return explicitQuantity;
  }
  if (
    typeof configuredAreaShareOfGsf === 'number' &&
    typeof squareFootageSummary === 'number' &&
    squareFootageSummary > 0
  ) {
    return configuredAreaShareOfGsf * squareFootageSummary;
  }
  return undefined;
}

function resolveAreaShareTotalCost(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  costPerFeatureAreaSF?: number;
  appliedQuantity?: number;
}): number | undefined {
  const { backendAppliedFeaturePricing, costPerFeatureAreaSF, appliedQuantity } = params;
  if (
    typeof backendAppliedFeaturePricing?.total_cost === 'number' &&
    Number.isFinite(backendAppliedFeaturePricing.total_cost)
  ) {
    return backendAppliedFeaturePricing.total_cost;
  }
  if (typeof costPerFeatureAreaSF === 'number' && typeof appliedQuantity === 'number') {
    return costPerFeatureAreaSF * appliedQuantity;
  }
  return undefined;
}

function resolveConfiguredCount(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  squareFootageSummary?: number;
}): number | undefined {
  const { backendAppliedFeaturePricing, backendFeaturePricing, squareFootageSummary } = params;
  if (!backendFeaturePricing) {
    const appliedQuantity =
      backendAppliedFeaturePricing?.billed_quantity ??
      backendAppliedFeaturePricing?.applied_quantity;
    return typeof appliedQuantity === 'number' && Number.isFinite(appliedQuantity)
      ? appliedQuantity
      : undefined;
  }

  const appliedQuantity =
    backendAppliedFeaturePricing?.billed_quantity ??
    backendAppliedFeaturePricing?.applied_quantity;
  if (typeof appliedQuantity === 'number' && Number.isFinite(appliedQuantity)) {
    return appliedQuantity;
  }

  if (
    typeof backendFeaturePricing.billed_quantity === 'number' &&
    Number.isFinite(backendFeaturePricing.billed_quantity)
  ) {
    return backendFeaturePricing.billed_quantity;
  }

  if (
    typeof backendFeaturePricing.requested_quantity === 'number' &&
    Number.isFinite(backendFeaturePricing.requested_quantity)
  ) {
    return backendFeaturePricing.requested_quantity;
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

function resolveAppliedCountTotalCost(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  costPerCount?: number;
  resolvedCount?: number;
}): number | undefined {
  const { backendAppliedFeaturePricing, costPerCount, resolvedCount } = params;
  if (
    typeof backendAppliedFeaturePricing?.total_cost === 'number' &&
    Number.isFinite(backendAppliedFeaturePricing.total_cost)
  ) {
    return backendAppliedFeaturePricing.total_cost;
  }
  if (typeof costPerCount === 'number' && typeof resolvedCount === 'number') {
    return costPerCount * resolvedCount;
  }
  return undefined;
}

function resolveCountPricingMode(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
}): SpecialFeatureCountPricingMode | undefined {
  const { backendAppliedFeaturePricing, backendFeaturePricing } = params;
  if (backendAppliedFeaturePricing?.count_pricing_mode) {
    return backendAppliedFeaturePricing.count_pricing_mode;
  }
  return backendFeaturePricing?.count_pricing_mode;
}

function resolveOverageFeatureDisplayPricing(params: {
  backendAppliedFeaturePricing?: SpecialFeatureBreakdownRow;
  backendFeaturePricing?: AvailableSpecialFeaturePricing;
  pricingBasis: SpecialFeaturePricingBasis | null;
  sourcePricingStatus: FeaturePricingStatus | null;
}): FeatureDisplayPricing | undefined {
  const {
    backendAppliedFeaturePricing,
    backendFeaturePricing,
    pricingBasis,
    sourcePricingStatus,
  } = params;
  if (pricingBasis !== 'COUNT_BASED') {
    return undefined;
  }

  const countPricingMode = resolveCountPricingMode({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
  });
  if (countPricingMode !== 'overage_above_default') {
    return undefined;
  }

  const requestedQuantity = resolveNumericField(
    backendAppliedFeaturePricing?.requested_quantity,
    backendFeaturePricing?.requested_quantity,
  );
  const includedBaselineQuantity = resolveNumericField(
    backendAppliedFeaturePricing?.included_baseline_quantity,
    backendFeaturePricing?.included_baseline_quantity,
  );
  const billedQuantity = resolveNumericField(
    backendAppliedFeaturePricing?.billed_quantity,
    backendFeaturePricing?.billed_quantity,
    backendAppliedFeaturePricing?.applied_quantity,
  );
  const requestedQuantitySource =
    backendAppliedFeaturePricing?.requested_quantity_source ??
    backendFeaturePricing?.requested_quantity_source;

  const hasExplicitRequestedQuantity =
    typeof requestedQuantitySource === 'string' &&
    requestedQuantitySource.startsWith('explicit_override:');
  if (
    !hasExplicitRequestedQuantity ||
    typeof requestedQuantity !== 'number' ||
    typeof includedBaselineQuantity !== 'number' ||
    typeof billedQuantity !== 'number'
  ) {
    return undefined;
  }

  const unitLabel =
    backendAppliedFeaturePricing?.unit_label ?? backendFeaturePricing?.unit_label ?? 'item';
  const costPerCount = getConfiguredCountRate({
    backendAppliedFeaturePricing,
    backendFeaturePricing,
  });
  const totalCost = resolveAppliedCountTotalCost({
    backendAppliedFeaturePricing,
    costPerCount,
    resolvedCount: billedQuantity,
  });
  const hasBilledOverage = billedQuantity > 0;

  return {
    amountLabel: resolveOverageAmountLabel({
      totalCost,
      hasBilledOverage,
      sourcePricingStatus,
    }),
    detailLabel: resolveOverageDetailLabel({
      costPerCount,
      billedQuantity,
      unitLabel,
      hasBilledOverage,
      sourcePricingStatus,
    }),
    explanationLines: [
      `Baseline includes ${formatQuantityWithUnit(includedBaselineQuantity, unitLabel)}`,
      `You specified ${formatQuantityWithUnit(requestedQuantity, unitLabel)}`,
      hasBilledOverage
        ? `Pricing includes ${formatAdditionalQuantityWithUnit(billedQuantity, unitLabel)}`
        : `No additional ${pluralizeUnitLabel(unitLabel, 2)} priced`,
    ],
    totalCost,
    isEstimate: false,
    isPlaceholder: false,
    pricingStatus: hasBilledOverage ? 'incremental' : sourcePricingStatus,
    pricingBasis,
    statusLabel: hasBilledOverage
      ? 'Incremental premium'
      : sourcePricingStatus === 'incremental'
        ? 'No additional premium'
        : undefined,
  };
}

function resolveOverageAmountLabel(params: {
  totalCost?: number;
  hasBilledOverage: boolean;
  sourcePricingStatus: FeaturePricingStatus | null;
}): string {
  const { totalCost, hasBilledOverage, sourcePricingStatus } = params;
  if (hasBilledOverage && typeof totalCost === 'number') {
    return `+${formatCurrency(totalCost)}`;
  }
  if (sourcePricingStatus === 'included_in_baseline') {
    return 'Included in baseline';
  }
  return '$0';
}

function resolveOverageDetailLabel(params: {
  costPerCount?: number;
  billedQuantity: number;
  unitLabel: string;
  hasBilledOverage: boolean;
  sourcePricingStatus: FeaturePricingStatus | null;
}): string {
  const { costPerCount, billedQuantity, unitLabel, hasBilledOverage, sourcePricingStatus } = params;
  if (hasBilledOverage && typeof costPerCount === 'number') {
    return `${formatCurrency(costPerCount)} per ${unitLabel} × ${formatQuantityWithUnit(billedQuantity, unitLabel)}`;
  }
  if (sourcePricingStatus === 'included_in_baseline') {
    return 'No additional premium for this subtype';
  }
  return 'No additional units priced';
}

function resolveNumericField(...values: Array<number | undefined>): number | undefined {
  for (const value of values) {
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
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

function formatAdditionalQuantityWithUnit(quantity: number, unitLabel: string): string {
  return `${formatNumber(quantity)} additional ${pluralizeUnitLabel(unitLabel, quantity)}`;
}

function formatPercent(value: number): string {
  const pct = value * 100;
  return `${pct.toFixed(Number.isInteger(pct) ? 0 : 1)}%`;
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
