import React, { useEffect, useMemo, useState } from 'react';
import { Download, ShieldCheck } from 'lucide-react';
import { api } from '../../api/client';
import {
  DealShieldControls,
  DealShieldViewModel,
  DecisionInsuranceFirstBreakCondition,
  DecisionInsurancePrimaryControlVariable,
  DecisionInsuranceProvenance,
  DecisionInsuranceRankedLikelyWrongItem,
} from '../../types';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { ErrorMessage } from '../../components/common/ErrorMessage';
import { pdfService } from '@/services/api';

interface Props {
  projectId: string;
  data?: DealShieldViewModel | null;
  loading?: boolean;
  error?: Error | null;
}

const MISSING_VALUE = '—';
const NOT_MODELED_VALUE = 'Not modeled';
const DEALSHIELD_STRESS_OPTIONS: Array<DealShieldControls['stress_band_pct']> = [10, 7, 5, 3];
const DEFAULT_DEALSHIELD_CONTROLS: DealShieldControls = {
  stress_band_pct: 10,
  anchor_total_project_cost: null,
  use_cost_anchor: false,
  anchor_annual_revenue: null,
  use_revenue_anchor: false,
};

type DecisionMetricType = 'currency' | 'percent' | 'ratio' | 'number';

const toFiniteNumber = (value: unknown): number | null => {
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const normalized = trimmed.replace(/[$,%\s,]/g, '');
    if (!normalized) return null;
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
};

const inferDecisionMetricType = (metricRef: unknown): DecisionMetricType => {
  if (typeof metricRef !== 'string') return 'number';
  const ref = metricRef.toLowerCase();
  if (ref.includes('dscr') || ref.includes('cap_rate')) return 'ratio';
  if (ref.includes('yield_on_cost') || ref.includes('pct') || ref.includes('percent')) return 'percent';
  const currencyHints = [
    'total_project_cost',
    'annual_revenue',
    'noi',
    'cost',
    'revenue',
    'income',
    'budget',
    'amount',
  ];
  if (currencyHints.some((hint) => ref.includes(hint))) return 'currency';
  return 'number';
};

const formatValue = (value: unknown) => {
  if (value === null || value === undefined || value === '') return MISSING_VALUE;
  if (typeof value === 'number' && Number.isFinite(value)) {
    return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value);
  }
  if (typeof value === 'number') return MISSING_VALUE;
  if (typeof value === 'string') {
    if (/not modeled/i.test(value)) return NOT_MODELED_VALUE;
    return value.trim() ? value : MISSING_VALUE;
  }
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (typeof value === 'object') return JSON.stringify(value);
  return String(value);
};

const isCurrencyMetric = (metricRef: unknown) => {
  if (typeof metricRef !== 'string') return false;
  const ref = metricRef.toLowerCase();
  if (ref.includes('dscr') || ref.includes('yield_on_cost')) return false;
  const hints = ['cost', 'revenue', 'price', 'value', 'amount', 'budget', 'income', 'noi', 'capex', 'opex'];
  return hints.some(hint => ref.includes(hint));
};

const formatDecisionMetricValue = (value: unknown, metricRef: unknown) => {
  if (value === null || value === undefined || value === '') return MISSING_VALUE;
  if (typeof value === 'string') {
    const text = value.trim();
    if (!text) return MISSING_VALUE;
    if (/not modeled/i.test(text)) return NOT_MODELED_VALUE;
    if (toFiniteNumber(text) === null) return text;
  }

  const numeric = toFiniteNumber(value);
  if (numeric === null) return MISSING_VALUE;

  const ref = typeof metricRef === 'string' ? metricRef.toLowerCase() : '';
  if (ref.includes('yield_on_cost')) {
    if (numeric <= 1.5) {
      return `${new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      }).format(numeric * 100)}%`;
    }
    if (numeric <= 150) {
      return `${new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
      }).format(numeric)}%`;
    }
    return `${new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(numeric)}%`;
  }

  if (ref.includes('dscr')) {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numeric);
  }

  const metricType = inferDecisionMetricType(metricRef);
  if (metricType === 'currency' || isCurrencyMetric(metricRef)) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: Math.abs(numeric) >= 1000 ? 0 : 2,
      maximumFractionDigits: Math.abs(numeric) >= 1000 ? 0 : 2,
    }).format(numeric);
  }

  if (metricType === 'percent') {
    const percentValue = Math.abs(numeric) <= 1.5 ? numeric * 100 : numeric;
    return `${new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 1,
      maximumFractionDigits: 1,
    }).format(percentValue)}%`;
  }

  if (metricType === 'ratio') {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numeric);
  }

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(numeric);
};

const formatSignedCurrency = (value: number) => {
  const sign = value < 0 ? '-' : '+';
  const absoluteValue = Math.abs(value);
  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: absoluteValue >= 1000 ? 0 : 2,
    maximumFractionDigits: absoluteValue >= 1000 ? 0 : 2,
  }).format(absoluteValue);
  return `${sign}${formatted}`;
};

const formatSignedPercent = (value: number) => {
  const sign = value < 0 ? '-' : '+';
  return `${sign}${new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(Math.abs(value))}%`;
};

const formatAssumptionPercent = (value: unknown) => {
  const numeric = toFiniteNumber(value);
  if (numeric === null) return MISSING_VALUE;
  const percentValue = Math.abs(numeric) <= 1.5 ? numeric * 100 : numeric;
  return `${new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2,
  }).format(percentValue)}%`;
};

const normalizePercentValue = (value: number) => (Math.abs(value) <= 1.5 ? value * 100 : value);

const formatAssumptionPercentFixed2 = (value: unknown) => {
  const numeric = toFiniteNumber(value);
  if (numeric === null) return MISSING_VALUE;
  return `${new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(normalizePercentValue(numeric))}%`;
};

const classifyFlexBeforeBreak = (value: number): 'Structurally Tight' | 'Moderate' | 'Flexible' => {
  if (value < 2.0) return 'Structurally Tight';
  if (value < 5.0) return 'Moderate';
  return 'Flexible';
};

const formatAssumptionYears = (value: unknown) => {
  const numeric = toFiniteNumber(value);
  if (numeric === null) return MISSING_VALUE;
  return `${new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 1,
  }).format(numeric)} yrs`;
};

const formatAssumptionMonths = (value: unknown) => {
  const numeric = toFiniteNumber(value);
  if (numeric === null) return MISSING_VALUE;
  return `${new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(numeric)} mo`;
};

const normalizeUnavailableReason = (reason: unknown): string | null => {
  if (typeof reason !== 'string') return null;
  const trimmed = reason.trim();
  if (!trimmed) return null;
  const spaced = trimmed.replace(/_/g, ' ');
  const sentence = spaced.charAt(0).toUpperCase() + spaced.slice(1);
  return sentence.endsWith('.') ? sentence : `${sentence}.`;
};

const unavailableReasonFromProvenance = (entry: unknown): string | null => {
  if (!entry || typeof entry !== 'object') return null;
  const block = entry as Record<string, unknown>;
  if (block.status === 'unavailable') {
    return normalizeUnavailableReason(block.reason) ?? 'Unavailable.';
  }
  return null;
};

const normalizeDisclosures = (value: unknown): string[] => {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => (item == null ? '' : String(item).trim()))
    .filter(Boolean);
};

const labelFrom = (value: any, fallback: string = '-') => {
  if (!value) return fallback;
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return String(value);
  if (typeof value === 'object') {
    return (
      value.label ??
      value.name ??
      value.title ??
      value.display ??
      value.text ??
      value.question ??
      value.flag ??
      value.action ??
      value.value ??
      fallback
    );
  }
  return fallback;
};

const listValue = (value: unknown) => {
  if (Array.isArray(value)) return value.map(item => formatValue(item)).join(', ');
  return formatValue(value);
};

const normalizeStressBand = (value: unknown): DealShieldControls['stress_band_pct'] => {
  const numeric = toFiniteNumber(value);
  if (numeric === null) return 10;
  const band = Math.trunc(numeric) as DealShieldControls['stress_band_pct'];
  return DEALSHIELD_STRESS_OPTIONS.includes(band) ? band : 10;
};

const normalizeDealShieldControls = (value: unknown, scenarioInputsRaw: unknown): DealShieldControls => {
  const controls = value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
  const scenarioInputs =
    scenarioInputsRaw && typeof scenarioInputsRaw === 'object'
      ? (scenarioInputsRaw as Record<string, unknown>)
      : {};
  const baseScenario =
    (scenarioInputs.base && typeof scenarioInputs.base === 'object'
      ? (scenarioInputs.base as Record<string, unknown>)
      : null) ||
    (scenarioInputs.conservative && typeof scenarioInputs.conservative === 'object'
      ? (scenarioInputs.conservative as Record<string, unknown>)
      : null);

  const stress_band_pct = normalizeStressBand(
    controls.stress_band_pct ?? baseScenario?.stress_band_pct ?? DEFAULT_DEALSHIELD_CONTROLS.stress_band_pct
  );

  const anchor_total_project_cost = toFiniteNumber(
    controls.anchor_total_project_cost ?? baseScenario?.cost_anchor_value
  );
  const use_cost_anchor =
    controls.use_cost_anchor === true ||
    (baseScenario?.cost_anchor_used === true && anchor_total_project_cost !== null);

  const anchor_annual_revenue = toFiniteNumber(
    controls.anchor_annual_revenue ?? baseScenario?.revenue_anchor_value
  );
  const use_revenue_anchor =
    controls.use_revenue_anchor === true ||
    (baseScenario?.revenue_anchor_used === true && anchor_annual_revenue !== null);

  return {
    stress_band_pct,
    anchor_total_project_cost,
    use_cost_anchor,
    anchor_annual_revenue,
    use_revenue_anchor,
  };
};

const getScenarioBadge = (scenarioLabel: string) => {
  const key = scenarioLabel.toLowerCase();
  if (key.includes('base')) {
    return { label: 'Base', className: 'bg-emerald-50 text-emerald-700 ring-emerald-200' };
  }
  if (key.includes('conservative') || key.includes('cons')) {
    return { label: 'Conservative', className: 'bg-amber-50 text-amber-700 ring-amber-200' };
  }
  if (key.includes('ugly')) {
    return { label: 'Ugly', className: 'bg-rose-50 text-rose-700 ring-rose-200' };
  }
  return null;
};

export const DealShieldView: React.FC<Props> = ({
  projectId,
  data,
  loading,
  error,
}) => {
  const isControlled = data !== undefined || loading !== undefined || error !== undefined;
  const [localState, setLocalState] = useState<{
    data: DealShieldViewModel | null;
    loading: boolean;
    error: Error | null;
  }>({
    data: null,
    loading: !isControlled,
    error: null,
  });
  const [overrideData, setOverrideData] = useState<DealShieldViewModel | null>(null);
  const [exporting, setExporting] = useState(false);
  const [controlsSaving, setControlsSaving] = useState(false);
  const [controlsError, setControlsError] = useState<string | null>(null);
  const [controls, setControls] = useState<DealShieldControls>(DEFAULT_DEALSHIELD_CONTROLS);

  useEffect(() => {
    if (isControlled || !projectId) return;
    let isActive = true;
    setLocalState({ data: null, loading: true, error: null });
    api.fetchDealShield(projectId)
      .then((response) => {
        if (!isActive) return;
        setLocalState({ data: response, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!isActive) return;
        setLocalState({ data: null, loading: false, error: err });
      });
    return () => {
      isActive = false;
    };
  }, [isControlled, projectId]);

  useEffect(() => {
    setOverrideData(null);
  }, [projectId]);

  const dealShieldData = isControlled ? overrideData ?? data ?? null : localState.data;
  const dealShieldLoading = isControlled ? !!loading : localState.loading;
  const dealShieldError = isControlled ? error ?? null : localState.error;

  const viewModel = useMemo(() => {
    if (!dealShieldData) return null;
    return (
      (dealShieldData as any).view_model ??
      (dealShieldData as any).viewModel ??
      dealShieldData
    );
  }, [dealShieldData]);

  const content = (viewModel as any)?.content ?? (dealShieldData as any)?.content ?? {};
  const decisionTable = (viewModel as any)?.decision_table ?? (viewModel as any)?.decisionTable ?? null;
  const fallbackColumns = Array.isArray((viewModel as any)?.columns) ? (viewModel as any).columns : [];
  const fallbackRows = Array.isArray((viewModel as any)?.rows) ? (viewModel as any).rows : [];
  const columns = Array.isArray(decisionTable?.columns) ? decisionTable.columns : fallbackColumns;
  const rows = Array.isArray(decisionTable?.rows) ? decisionTable.rows : fallbackRows;

  const fastestChangeDrivers = Array.isArray(content?.fastest_change?.drivers)
    ? content.fastest_change.drivers
    : Array.isArray(content?.fastestChange?.drivers)
      ? content.fastestChange.drivers
      : [];
  const driverLabelByTileId = useMemo(() => {
    const map = new Map<string, string>();
    fastestChangeDrivers.forEach((driver: any) => {
      const tileId = driver?.tile_id ?? driver?.tileId ?? driver?.id;
      if (!tileId) return;
      const label = labelFrom(driver, String(tileId));
      map.set(String(tileId), String(label));
    });
    return map;
  }, [fastestChangeDrivers]);
  const fastestChangeText = fastestChangeDrivers
    .map((driver: any) => labelFrom(driver, ''))
    .filter(Boolean)
    .join('; ');

  const mostLikelyWrongRaw =
    content?.most_likely_wrong ??
    content?.mostLikelyWrong ??
    content?.most_likely_wrong_items ??
    [];
  const mostLikelyWrong = Array.isArray(mostLikelyWrongRaw)
    ? mostLikelyWrongRaw
    : Array.isArray(mostLikelyWrongRaw?.items)
      ? mostLikelyWrongRaw.items
      : [];

  const questionBankRaw = content?.question_bank ?? content?.questionBank ?? [];
  const questionBank = Array.isArray(questionBankRaw)
    ? questionBankRaw
    : Array.isArray(questionBankRaw?.items)
      ? questionBankRaw.items
      : [];
  const hasDriverTileId = questionBank.some(
    (item: any) => item?.driver_tile_id || item?.driverTileId
  );
  const questionGroups = questionBank.reduce((acc: Record<string, any[]>, item: any) => {
    const key = hasDriverTileId
      ? (item?.driver_tile_id || item?.driverTileId || '-')
      : 'all';
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});

  const redFlagsActionsRaw = content?.red_flags_actions ?? content?.redFlagsActions ?? [];
  const redFlagsActions = Array.isArray(redFlagsActionsRaw) ? redFlagsActionsRaw : [];
  const redFlagsRaw = content?.red_flags ?? content?.redFlags ?? [];
  const actionsRaw = content?.actions ?? content?.action_items ?? content?.actionItems ?? [];
  const redFlags = Array.isArray(redFlagsRaw) && redFlagsRaw.length > 0
    ? redFlagsRaw
    : redFlagsActions.map((item: any) => item?.flag).filter(Boolean);
  const actions = Array.isArray(actionsRaw) && actionsRaw.length > 0
    ? actionsRaw
    : redFlagsActions.map((item: any) => item?.action).filter(Boolean);

  const provenance = (viewModel as any)?.provenance ?? (dealShieldData as any)?.provenance ?? {};
  const decisionInsuranceProvenanceRaw =
    (viewModel as any)?.decision_insurance_provenance ??
    (viewModel as any)?.decisionInsuranceProvenance ??
    provenance?.decision_insurance ??
    provenance?.decisionInsurance;
  const decisionInsuranceProvenance =
    decisionInsuranceProvenanceRaw && typeof decisionInsuranceProvenanceRaw === 'object'
      ? (decisionInsuranceProvenanceRaw as DecisionInsuranceProvenance)
      : null;

  const primaryControlVariableRaw =
    (viewModel as any)?.primary_control_variable ??
    (viewModel as any)?.primaryControlVariable;
  const primaryControlVariable =
    primaryControlVariableRaw && typeof primaryControlVariableRaw === 'object'
      ? (primaryControlVariableRaw as DecisionInsurancePrimaryControlVariable)
      : null;

  const firstBreakConditionRaw =
    (viewModel as any)?.first_break_condition ??
    (viewModel as any)?.firstBreakCondition;
  const firstBreakCondition =
    firstBreakConditionRaw && typeof firstBreakConditionRaw === 'object'
      ? (firstBreakConditionRaw as DecisionInsuranceFirstBreakCondition)
      : null;

  const flexBeforeBreakPct = toFiniteNumber(
    (viewModel as any)?.flex_before_break_pct ?? (viewModel as any)?.flexBeforeBreakPct
  );
  const exposureConcentrationPct = toFiniteNumber(
    (viewModel as any)?.exposure_concentration_pct ?? (viewModel as any)?.exposureConcentrationPct
  );
  const firstBreakScenarioLabel = formatValue(
    firstBreakCondition?.scenario_label ?? firstBreakCondition?.scenario_id
  );
  const flexBeforeBreakDisplay = flexBeforeBreakPct !== null
    ? `${formatAssumptionPercentFixed2(flexBeforeBreakPct)} (${classifyFlexBeforeBreak(normalizePercentValue(flexBeforeBreakPct))})`
    : null;
  const exposureConcentrationSentence = exposureConcentrationPct !== null
    ? `Primary control variable contributes ${formatAssumptionPercentFixed2(exposureConcentrationPct)} of modeled downside sensitivity.`
    : null;

  const rankedLikelyWrongRaw =
    (viewModel as any)?.ranked_likely_wrong ??
    (viewModel as any)?.rankedLikelyWrong ??
    [];
  const rankedLikelyWrong = Array.isArray(rankedLikelyWrongRaw)
    ? (rankedLikelyWrongRaw as DecisionInsuranceRankedLikelyWrongItem[])
    : [];

  const primaryControlUnavailableReason = unavailableReasonFromProvenance(
    decisionInsuranceProvenance?.primary_control_variable
  );
  const firstBreakUnavailableReason = unavailableReasonFromProvenance(
    decisionInsuranceProvenance?.first_break_condition
  );
  const flexBeforeBreakUnavailableReason = unavailableReasonFromProvenance(
    decisionInsuranceProvenance?.flex_before_break_pct
  );
  const exposureConcentrationUnavailableReason = unavailableReasonFromProvenance(
    decisionInsuranceProvenance?.exposure_concentration_pct
  );
  const rankedLikelyWrongUnavailableReason = unavailableReasonFromProvenance(
    decisionInsuranceProvenance?.ranked_likely_wrong
  );

  const decisionInsuranceUnavailableNotes = useMemo(
    () => [
      primaryControlUnavailableReason,
      firstBreakUnavailableReason,
      flexBeforeBreakUnavailableReason,
      exposureConcentrationUnavailableReason,
      rankedLikelyWrongUnavailableReason,
    ].filter((value, index, array): value is string => !!value && array.indexOf(value) === index),
    [
      exposureConcentrationUnavailableReason,
      firstBreakUnavailableReason,
      flexBeforeBreakUnavailableReason,
      primaryControlUnavailableReason,
      rankedLikelyWrongUnavailableReason,
    ]
  );
  const hasDecisionInsuranceData =
    !!primaryControlVariable ||
    !!firstBreakCondition ||
    flexBeforeBreakPct !== null ||
    exposureConcentrationPct !== null ||
    rankedLikelyWrong.length > 0 ||
    decisionInsuranceUnavailableNotes.length > 0;

  const financingAssumptionsRaw =
    (viewModel as any)?.financing_assumptions ??
    provenance?.financing_assumptions ??
    (dealShieldData as any)?.financing_assumptions;
  const financingAssumptions =
    financingAssumptionsRaw && typeof financingAssumptionsRaw === 'object'
      ? (financingAssumptionsRaw as Record<string, unknown>)
      : null;
  const financingAssumptionItems = useMemo(() => {
    if (!financingAssumptions) return [];
    const debtPct = financingAssumptions.debt_pct ?? financingAssumptions.ltv;
    const ioValue =
      financingAssumptions.interest_only_months ??
      financingAssumptions.io_months ??
      financingAssumptions.interest_only;
    return [
      {
        label: 'Debt %',
        value: formatAssumptionPercent(debtPct),
      },
      {
        label: 'Rate',
        value: formatAssumptionPercent(financingAssumptions.interest_rate_pct),
      },
      {
        label: 'Amortization',
        value: formatAssumptionYears(financingAssumptions.amort_years),
      },
      {
        label: 'Loan term',
        value: formatAssumptionYears(financingAssumptions.loan_term_years),
      },
      {
        label: 'Interest-only',
        value:
          typeof ioValue === 'boolean'
            ? (ioValue ? 'Yes' : 'No')
            : formatAssumptionMonths(ioValue),
      },
    ].filter((item) => item.value !== MISSING_VALUE);
  }, [financingAssumptions]);
  const dealShieldDisclosures = useMemo(
    () =>
      normalizeDisclosures((viewModel as any)?.dealshield_disclosures).concat(
        normalizeDisclosures(provenance?.dealshield_disclosures)
      ).filter((value, index, array) => array.indexOf(value) === index),
    [provenance?.dealshield_disclosures, viewModel]
  );
  const decisionSummary = useMemo(() => {
    const summaryRaw =
      ((viewModel as any)?.decision_summary && typeof (viewModel as any).decision_summary === 'object'
        ? (viewModel as any).decision_summary
        : (viewModel as any)?.decisionSummary && typeof (viewModel as any).decisionSummary === 'object'
          ? (viewModel as any).decisionSummary
          : {}) as Record<string, unknown>;

    const fallbackCapRate =
      (viewModel as any)?.cap_rate_used_pct ?? (viewModel as any)?.capRateUsedPct;
    const fallbackValueGap =
      (viewModel as any)?.value_gap ?? (viewModel as any)?.valueGap;
    const fallbackValueGapPct =
      (viewModel as any)?.value_gap_pct ?? (viewModel as any)?.valueGapPct;

    const capRateUsedPct = toFiniteNumber(
      summaryRaw.cap_rate_used_pct ?? summaryRaw.capRateUsedPct ?? fallbackCapRate
    );
    const stabilizedValueFromSummary = toFiniteNumber(
      summaryRaw.stabilized_value ?? summaryRaw.stabilizedValue
    );
    let valueGap = toFiniteNumber(
      summaryRaw.value_gap ?? summaryRaw.valueGap ?? fallbackValueGap
    );
    let valueGapPct = toFiniteNumber(
      summaryRaw.value_gap_pct ?? summaryRaw.valueGapPct ?? fallbackValueGapPct
    );
    const notModeledRaw = summaryRaw.not_modeled_reason ?? summaryRaw.notModeledReason;
    let notModeledReason =
      typeof notModeledRaw === 'string' && notModeledRaw.trim()
        ? notModeledRaw.trim()
        : null;

    const baseRow = rows.find((row: any) => {
      if (!row || typeof row !== 'object') return false;
      const scenarioId = typeof row?.scenario_id === 'string' ? row.scenario_id.toLowerCase() : '';
      const label = typeof row?.label === 'string' ? row.label.toLowerCase() : '';
      return scenarioId === 'base' || label === 'base';
    }) ?? rows[0];

    let baseStabilizedValue = stabilizedValueFromSummary;
    let baseTotalCost: number | null = null;
    if (baseRow && typeof baseRow === 'object') {
      const baseCells = Array.isArray(baseRow?.cells)
        ? baseRow.cells
        : Array.isArray(baseRow?.values)
          ? baseRow.values
          : [];
      const cellMap = new Map<string, any>();
      baseCells.forEach((cell: any, index: number) => {
        if (!cell || typeof cell !== 'object') {
          cellMap.set(String(index), cell);
          return;
        }
        const cellId =
          cell?.col_id ??
          cell?.colId ??
          cell?.tile_id ??
          cell?.tileId ??
          cell?.id ??
          String(index);
        cellMap.set(String(cellId), cell);
      });
      const stabilizedCell = cellMap.get('stabilized_value');
      const totalCostCell = cellMap.get('total_cost');
      baseStabilizedValue = toFiniteNumber(stabilizedCell?.value ?? stabilizedCell ?? stabilizedValueFromSummary);
      baseTotalCost = toFiniteNumber(totalCostCell?.value ?? totalCostCell);
    }

    if (valueGap === null && baseStabilizedValue !== null && baseTotalCost !== null) {
      valueGap = baseStabilizedValue - baseTotalCost;
    }
    if (valueGapPct === null && valueGap !== null && baseTotalCost !== null && baseTotalCost !== 0) {
      valueGapPct = (valueGap / baseTotalCost) * 100;
    }
    if (!notModeledReason && baseStabilizedValue === null && capRateUsedPct === null) {
      const capRateDisclosure = dealShieldDisclosures.find((item) => /cap rate missing/i.test(item));
      if (capRateDisclosure) {
        notModeledReason = capRateDisclosure;
      }
    }

    return {
      stabilizedValue: baseStabilizedValue,
      capRateUsedPct,
      valueGap,
      valueGapPct,
      notModeledReason,
    };
  }, [dealShieldDisclosures, rows, viewModel]);
  const scenarioInputsRaw = provenance?.scenario_inputs ?? (viewModel as any)?.scenario_inputs;
  const provenanceControlsRaw = provenance?.dealshield_controls ?? (dealShieldData as any)?.dealshield_controls;
  const scenarioInputs = useMemo(() => {
    if (Array.isArray(scenarioInputsRaw)) return scenarioInputsRaw;
    if (scenarioInputsRaw && typeof scenarioInputsRaw === 'object') {
      return Object.entries(scenarioInputsRaw).map(([scenarioId, input]) => {
        const payload = input && typeof input === 'object' ? input : {};
        return {
          scenario: scenarioId,
          ...(payload as Record<string, unknown>),
        };
      });
    }
    return [];
  }, [scenarioInputsRaw]);
  const controlsFromPayload = useMemo(
    () => normalizeDealShieldControls(provenanceControlsRaw, scenarioInputsRaw),
    [provenanceControlsRaw, scenarioInputsRaw]
  );

  useEffect(() => {
    setControls(controlsFromPayload);
  }, [controlsFromPayload]);
  const metricRefsUsed = Array.isArray(provenance?.metric_refs_used)
    ? provenance.metric_refs_used
    : Array.isArray((viewModel as any)?.metric_refs_used)
      ? (viewModel as any).metric_refs_used
      : [];
  const metricRefPills = metricRefsUsed
    .map((ref: any) => (ref == null ? '' : String(ref).trim()))
    .filter(Boolean);

  const profileId =
    (dealShieldData as any)?.profile_id ??
    (dealShieldData as any)?.profileId ??
    (viewModel as any)?.profile_id ??
    (viewModel as any)?.profileId;
  const tileProfileId = provenance?.profile_id ?? profileId;
  const contentProfileId = provenance?.content_profile_id ?? content?.profile_id;
  const scopeProfileId = provenance?.scope_items_profile_id;
  const provenanceControls = provenanceControlsRaw && typeof provenanceControlsRaw === 'object'
    ? (provenanceControlsRaw as Record<string, unknown>)
    : {};
  const stressBandText = toFiniteNumber(provenanceControls?.stress_band_pct) !== null
    ? `±${Math.trunc(Number(provenanceControls.stress_band_pct))}%`
    : MISSING_VALUE;
  const anchorEnabled = typeof provenanceControls?.use_anchor === 'boolean'
    ? provenanceControls.use_anchor
    : (typeof provenanceControls?.use_cost_anchor === 'boolean' ? provenanceControls.use_cost_anchor : null);
  const anchorAmount = provenanceControls?.anchor_total_cost ?? provenanceControls?.anchor_total_project_cost;
  const anchorText = anchorEnabled === true
    ? `On${toFiniteNumber(anchorAmount) !== null ? ` (${formatDecisionMetricValue(anchorAmount, 'totals.total_project_cost')})` : ''}`
    : (anchorEnabled === false ? 'Off' : MISSING_VALUE);
  const hasUnderwritingColumns = columns.some((column: any) => ['annual_revenue', 'noi', 'dscr', 'yoc'].includes(String(column?.id ?? column?.tile_id ?? '')));
  const context =
    (dealShieldData as any)?.context ??
    (viewModel as any)?.context ??
    (dealShieldData as any)?.profile_context ??
    {};
  const contextLocation =
    context?.location_display ??
    context?.location ??
    [context?.city, context?.state].filter(Boolean).join(', ');
  const contextSf =
    context?.square_footage ??
    context?.squareFootage ??
    context?.sf ??
    context?.gross_sf ??
    context?.grossSf;

  const persistControls = async (nextControls: DealShieldControls) => {
    if (!projectId) return;
    setControls(nextControls);
    setControlsError(null);
    try {
      setControlsSaving(true);
      await api.updateDealShieldControls(projectId, nextControls);
      const refreshed = await api.fetchDealShield(projectId);
      if (isControlled) {
        setOverrideData(refreshed);
      } else {
        setLocalState({ data: refreshed, loading: false, error: null });
      }
    } catch (err) {
      console.error('Failed to update DealShield controls:', err);
      setControlsError('Could not update controls. Please retry.');
    } finally {
      setControlsSaving(false);
    }
  };

  const handleStressBandChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const stressBand = normalizeStressBand(Number(event.target.value));
    void persistControls({
      ...controls,
      stress_band_pct: stressBand,
    });
  };

  const handleUseCostAnchorChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const useAnchor = event.target.checked;
    void persistControls({
      ...controls,
      use_cost_anchor: useAnchor,
    });
  };

  const handleAnchorTotalCostChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const raw = event.target.value;
    const numeric = raw.trim() ? toFiniteNumber(raw) : null;
    void persistControls({
      ...controls,
      anchor_total_project_cost: numeric,
    });
  };

  const handleExportPdf = async () => {
    if (!projectId || exporting) return;
    try {
      setExporting(true);
      const response = await pdfService.exportDealShield(projectId);
      const blob = new Blob(
        [response.data],
        { type: response.headers?.['content-type'] || 'application/pdf' }
      );

      const filename = `dealshield_${projectId}.pdf`;
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('DealShield PDF export failed:', err);
      alert('Failed to export DealShield PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-blue-600" />
              <h2 className="text-2xl font-semibold text-slate-900">DealShield</h2>
            </div>
            {profileId && (
              <p className="text-sm text-slate-500">
                profile_id: <span className="font-medium text-slate-700">{profileId}</span>
              </p>
            )}
            <div className="flex flex-wrap gap-2 text-xs text-slate-600">
              {contextLocation && (
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  {contextLocation}
                </span>
              )}
              {contextSf !== undefined && contextSf !== null && contextSf !== '' && (
                <span className="rounded-full bg-slate-100 px-2.5 py-1">
                  {formatValue(contextSf)} SF
                </span>
              )}
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-3">
              <div className="grid gap-3 sm:grid-cols-3">
                <label className="flex flex-col gap-1 text-sm text-slate-700">
                  <span className="font-medium">Stress band</span>
                  <select
                    value={controls.stress_band_pct}
                    onChange={handleStressBandChange}
                    disabled={controlsSaving}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {DEALSHIELD_STRESS_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        ±{option}%
                      </option>
                    ))}
                  </select>
                  <span className="text-xs text-slate-500">Stress band (not estimate accuracy).</span>
                </label>
                <label className="flex items-center gap-2 self-end text-sm text-slate-700">
                  <input
                    type="checkbox"
                    checked={controls.use_cost_anchor}
                    onChange={handleUseCostAnchorChange}
                    disabled={controlsSaving}
                    className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="font-medium">Use bid/GMP anchor</span>
                </label>
                <label className="flex flex-col gap-1 text-sm text-slate-700">
                  <span className="font-medium">Anchor total cost</span>
                  <input
                    type="number"
                    value={controls.anchor_total_project_cost ?? ''}
                    onChange={handleAnchorTotalCostChange}
                    placeholder="15000000"
                    disabled={controlsSaving}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                  />
                </label>
              </div>
              {controlsSaving && (
                <p className="mt-2 text-xs text-slate-500">Updating DealShield scenarios...</p>
              )}
              {controlsError && (
                <p className="mt-2 text-xs text-rose-600">{controlsError}</p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={handleExportPdf}
            disabled={!dealShieldData || exporting}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {exporting ? 'Exporting...' : 'Export DealShield PDF'}
          </button>
        </div>
      </div>

      {dealShieldLoading && (
        <LoadingSpinner size="large" message="Loading DealShield..." />
      )}

      {dealShieldError && (
        <ErrorMessage error="DealShield not available" />
      )}

      {!dealShieldLoading && !dealShieldError && !dealShieldData && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 text-sm text-slate-600">
          DealShield not available.
        </div>
      )}

      {!dealShieldLoading && !dealShieldError && dealShieldData && (
        <>
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-xl font-semibold tracking-tight text-slate-900">Decision Insurance</h3>
            {hasDecisionInsuranceData ? (
              <div className="space-y-4">
                <div className="grid gap-3 md:grid-cols-2">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Primary Control Variable</p>
                    {primaryControlVariable ? (
                      <div className="mt-2 space-y-1 text-sm text-slate-700">
                        <p>
                          <span className="font-medium text-slate-600">Label:</span>{' '}
                          <span>{labelFrom(primaryControlVariable, '-')}</span>
                        </p>
                        <p>
                          <span className="font-medium text-slate-600">Impact:</span>{' '}
                          <span>{formatAssumptionPercent(primaryControlVariable.impact_pct)}</span>
                        </p>
                        <p>
                          <span className="font-medium text-slate-600">Severity:</span>{' '}
                          <span>{formatValue(primaryControlVariable.severity)}</span>
                        </p>
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-slate-700">{primaryControlUnavailableReason ?? 'Unavailable.'}</p>
                    )}
                  </div>

                  <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">First Break Condition</p>
                    {firstBreakCondition ? (
                      <div className="mt-2 space-y-1 text-sm text-slate-700">
                        <p>Break occurs in {firstBreakScenarioLabel}: value gap turns negative.</p>
                        <p>
                          <span className="font-medium text-slate-600">Scenario:</span>{' '}
                          <span>{formatValue(firstBreakCondition.scenario_label ?? firstBreakCondition.scenario_id)}</span>
                        </p>
                        <p>
                          <span className="font-medium text-slate-600">Observed:</span>{' '}
                          <span>{formatDecisionMetricValue(firstBreakCondition.observed_value, 'derived.value_gap')}</span>
                        </p>
                        <p>
                          <span className="font-medium text-slate-600">Threshold:</span>{' '}
                          <span>
                            {formatValue(firstBreakCondition.operator)}{' '}
                            {formatDecisionMetricValue(firstBreakCondition.threshold, 'derived.value_gap')}
                          </span>
                        </p>
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-slate-700">{firstBreakUnavailableReason ?? 'No modeled break condition.'}</p>
                    )}
                  </div>

                  <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Flex Before Break %</p>
                    {flexBeforeBreakPct !== null ? (
                      <p className="mt-2 text-sm text-slate-700">{flexBeforeBreakDisplay}</p>
                    ) : (
                      <p className="mt-2 text-sm text-slate-700">{flexBeforeBreakUnavailableReason ?? 'Unavailable.'}</p>
                    )}
                  </div>

                  <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Exposure Concentration %</p>
                    {exposureConcentrationPct !== null ? (
                      <div className="mt-2 space-y-1 text-sm text-slate-700">
                        <p>{formatAssumptionPercent(exposureConcentrationPct)}</p>
                        <p>{exposureConcentrationSentence}</p>
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-slate-700">{exposureConcentrationUnavailableReason ?? 'Unavailable.'}</p>
                    )}
                  </div>
                </div>

                <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Ranked Most Likely Wrong</p>
                  {rankedLikelyWrong.length > 0 ? (
                    <ul className="mt-2 space-y-2 text-sm text-slate-700">
                      {rankedLikelyWrong.map((entry, index) => (
                        <li key={`${entry.id ?? 'ranked-likely-wrong'}-${index}`} className="rounded border border-slate-200 bg-white px-2.5 py-2">
                          <p className="font-medium text-slate-800">{formatValue(entry.text ?? entry.id)}</p>
                          <p className="mt-1 text-xs text-slate-600">
                            Impact: {formatAssumptionPercent(entry.impact_pct)} | Severity: {formatValue(entry.severity)}
                          </p>
                          <p className="mt-1 text-xs text-slate-600">Why: {formatValue(entry.why)}</p>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-2 text-sm text-slate-700">{rankedLikelyWrongUnavailableReason ?? 'Unavailable.'}</p>
                  )}
                </div>

                {decisionInsuranceUnavailableNotes.length > 0 && (
                  <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2.5">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-amber-700">Unavailable Reason(s)</p>
                    <ul className="mt-2 list-disc pl-5 text-xs text-amber-800 space-y-0.5">
                      {decisionInsuranceUnavailableNotes.map((note, index) => (
                        <li key={`decision-insurance-unavailable-${index}`}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-slate-700">Decision Insurance unavailable for this profile/run.</p>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-xl font-semibold tracking-tight text-slate-900">Decision Metrics</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full overflow-hidden rounded-xl border border-slate-200 text-sm">
                <thead className="bg-slate-50/90 text-slate-600">
                  <tr>
                    <th className="px-2.5 py-2 text-left font-semibold">Scenario</th>
                    {columns.map((column: any, index: number) => (
                      <th key={index} className="px-2.5 py-2 text-left font-semibold">
                        {labelFrom(column?.label ?? column, '-')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row: any, rowIndex: number) => {
                    const scenarioLabel = labelFrom(row, '-');
                    const scenarioDelta = typeof row?.delta === 'string' && row.delta.trim() ? row.delta.trim() : null;
                    const scenarioBadge = getScenarioBadge(scenarioLabel);
                    const rowValues = Array.isArray(row?.values)
                      ? row.values
                      : Array.isArray(row?.cells)
                        ? row.cells
                        : Array.isArray(row?.data)
                          ? row.data
                          : [];
                    const byColId = new Map<string, any>();
                    rowValues.forEach((cell: any, cellIndex: number) => {
                      if (!cell || typeof cell !== 'object') {
                        byColId.set(String(cellIndex), cell);
                        return;
                      }
                      const cellColId =
                        cell?.col_id ??
                        cell?.colId ??
                        cell?.tile_id ??
                        cell?.tileId ??
                        cell?.id;
                      if (cellColId !== undefined && cellColId !== null) {
                        byColId.set(String(cellColId), cell);
                      }
                    });
                    return (
                      <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'}>
                        <td className="px-2.5 py-2 font-medium text-slate-800">
                          <div>
                            <div className="flex items-center gap-2">
                              {scenarioBadge && (
                                <span className={`inline-flex rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ${scenarioBadge.className}`}>
                                  {scenarioBadge.label}
                                </span>
                              )}
                              <span>{scenarioLabel}</span>
                            </div>
                            {scenarioDelta && <p className="text-[11px] font-normal text-slate-500">{scenarioDelta}</p>}
                          </div>
                        </td>
                        {columns.map((column: any, colIndex: number) => {
                          const columnId =
                            column?.id ??
                            column?.col_id ??
                            column?.colId ??
                            column?.tile_id ??
                            column?.tileId ??
                            String(colIndex);
                          const cell = byColId.get(String(columnId)) ?? rowValues[colIndex];
                          const rawValue =
                            cell?.value ??
                            cell?.formatted ??
                            cell?.display ??
                            cell?.label ??
                            cell;
                          const metricRef =
                            cell?.metric_ref ??
                            cell?.metricRef ??
                            column?.metric_ref ??
                            column?.metricRef;
                          return (
                            <td key={colIndex} className="px-2.5 py-2 text-slate-700">
                              {formatDecisionMetricValue(rawValue, metricRef)}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="mt-3 text-xs text-slate-500">
              {hasUnderwritingColumns
                ? 'DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.'
                : 'Feasibility risk labels are deterministic scenario tags, not modeled probabilities.'}
            </p>
            {(decisionSummary.stabilizedValue !== null || decisionSummary.notModeledReason) && (
              <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Decision Summary</p>
                {decisionSummary.stabilizedValue !== null && decisionSummary.capRateUsedPct !== null ? (
                  <div className="mt-2 grid gap-x-4 gap-y-1 text-xs text-slate-700 sm:grid-cols-2">
                    <p>
                      <span className="font-medium text-slate-600">Stabilized Value:</span>{' '}
                      <span>{formatDecisionMetricValue(decisionSummary.stabilizedValue, 'derived.stabilized_value')}</span>
                    </p>
                    <p>
                      <span className="font-medium text-slate-600">Cap Rate Used:</span>{' '}
                      <span>{formatAssumptionPercent(decisionSummary.capRateUsedPct)}</span>
                    </p>
                    {decisionSummary.valueGap !== null && (
                      <p className="sm:col-span-2">
                        <span className="font-medium text-slate-600">Value Gap:</span>{' '}
                        <span>{formatSignedCurrency(decisionSummary.valueGap)}</span>
                        {decisionSummary.valueGapPct !== null && (
                          <span> ({formatSignedPercent(decisionSummary.valueGapPct)} of cost)</span>
                        )}
                      </p>
                    )}
                  </div>
                ) : (
                  <p className="mt-2 text-xs text-slate-700">
                    {decisionSummary.notModeledReason ?? 'Not modeled: cap rate missing'}
                  </p>
                )}
              </div>
            )}
            {(financingAssumptionItems.length > 0 || dealShieldDisclosures.length > 0) && (
              <div className="mt-3 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Assumptions</p>
                {financingAssumptionItems.length > 0 ? (
                  <div className="mt-2 grid gap-x-4 gap-y-1 text-xs text-slate-700 sm:grid-cols-2">
                    {financingAssumptionItems.map((item) => (
                      <p key={item.label}>
                        <span className="font-medium text-slate-600">{item.label}:</span>{' '}
                        <span>{item.value}</span>
                      </p>
                    ))}
                  </div>
                ) : (
                  <ul className="mt-2 space-y-1 text-xs text-slate-700">
                    {dealShieldDisclosures.map((item, index) => (
                      <li key={`assumptions-disclosure-${index}`}>{item}</li>
                    ))}
                  </ul>
                )}
                {financingAssumptionItems.length > 0 && dealShieldDisclosures.length > 0 && (
                  <ul className="mt-2 space-y-1 text-xs text-slate-600">
                    {dealShieldDisclosures.map((item, index) => (
                      <li key={`assumptions-extra-disclosure-${index}`}>{item}</li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm space-y-5">
            <div>
              <h3 className="mb-2 text-xl font-semibold tracking-tight text-slate-900">Fastest-Change</h3>
              <p className="text-sm text-slate-700">
                {fastestChangeText || '-'}
              </p>
            </div>
            <div>
              <h3 className="mb-2 text-xl font-semibold tracking-tight text-slate-900">Most Likely Wrong</h3>
              {mostLikelyWrong.length > 0 ? (
                <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                  {mostLikelyWrong.map((item: any, index: number) => (
                    <li key={index}>{labelFrom(item)}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-500">-</p>
              )}
            </div>
            <div>
              <h3 className="mb-2 text-xl font-semibold tracking-tight text-slate-900">Question Bank</h3>
              {questionBank.length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(questionGroups).map(([groupKey, items]) => (
                    <div key={groupKey} className="space-y-2">
                      {hasDriverTileId && (
                        <p className="text-sm font-semibold text-slate-700">
                          {driverLabelByTileId.get(groupKey) ?? groupKey}
                          {groupKey !== '-' && (
                            <span className="ml-2 align-middle text-[10px] font-medium text-slate-400 font-mono">
                              (tile: {groupKey})
                            </span>
                          )}
                        </p>
                      )}
                      <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                        {(items as any[]).flatMap((item, index) => {
                          const questions = Array.isArray(item?.questions)
                            ? item.questions
                            : [labelFrom(item)];
                          return questions.map((question: any, qIndex: number) => (
                            <li key={`${index}-${qIndex}`}>{labelFrom(question)}</li>
                          ));
                        })}
                      </ul>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">-</p>
              )}
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <h3 className="mb-2 text-xl font-semibold tracking-tight text-slate-900">Red Flags</h3>
                {redFlags.length > 0 ? (
                  <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                    {redFlags.map((item: any, index: number) => (
                      <li key={index}>{labelFrom(item)}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">-</p>
                )}
              </div>
              <div>
                <h3 className="mb-2 text-xl font-semibold tracking-tight text-slate-900">Actions</h3>
                {actions.length > 0 ? (
                  <ul className="list-disc pl-5 text-sm text-slate-700 space-y-1">
                    {actions.map((item: any, index: number) => (
                      <li key={index}>{labelFrom(item)}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">-</p>
                )}
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold tracking-tight text-slate-900">Provenance</h3>
              <span className="text-xs uppercase tracking-wide text-slate-400">Inputs</span>
            </div>
            <p className="mb-3 text-xs text-slate-600">
              <span className="font-semibold text-slate-700">Profiles &amp; Controls:</span>{' '}
              Tile: {formatValue(tileProfileId)} | Content: {formatValue(contentProfileId)} | Scope: {formatValue(scopeProfileId)} | Stress band: {stressBandText} | Anchor: {anchorText}
            </p>
            {scenarioInputs.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full overflow-hidden rounded-xl border border-slate-200 text-sm">
                  <thead className="bg-slate-50/90 text-slate-600">
                    <tr>
                      <th className="px-2.5 py-2 text-left font-semibold">Scenario</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Applied Tile IDs</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Stress Band</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Cost Scalar</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Revenue Scalar</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Cost Anchor</th>
                      <th className="px-2.5 py-2 text-left font-semibold">Driver metric (Ugly only)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scenarioInputs.map((input: any, index: number) => {
                      const metricRef =
                        input?.driver?.metric_ref ??
                        input?.driver?.metricRef ??
                        input?.metric_ref ??
                        input?.metricRef;
                      return (
                        <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-slate-50/40'}>
                          <td className="px-2.5 py-2 text-slate-700">
                            {labelFrom(input?.scenario ?? input?.scenario_label ?? input?.label ?? input?.name)}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {listValue(input?.applied_tile_ids ?? input?.appliedTileIds ?? input?.tiles)}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {input?.stress_band_pct !== undefined && input?.stress_band_pct !== null
                              ? `±${formatValue(input?.stress_band_pct)}%`
                              : MISSING_VALUE}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {formatValue(input?.cost_scalar ?? input?.costScalar)}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {formatValue(input?.revenue_scalar ?? input?.revenueScalar)}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {input?.cost_anchor_used
                              ? formatDecisionMetricValue(input?.cost_anchor_value, 'totals.total_project_cost')
                              : 'No'}
                          </td>
                          <td className="px-2.5 py-2 text-slate-700">
                            {formatValue(metricRef)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-slate-500">-</p>
            )}

            {metricRefPills.length > 0 && (
              <div className="mt-4">
                <div className="text-sm font-medium text-slate-700">metric_refs_used:</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {metricRefPills.map((ref: string, index: number) => (
                    <span
                      key={`${ref}-${index}`}
                      className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[11px] text-slate-600 font-mono"
                    >
                      {ref}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};
