import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DealShieldViewModel, DecisionStatus, Project } from '../../types';
import { formatters, safeGet } from '../../utils/displayFormatters';
import { formatPerSf } from '@/v2/utils/formatters';
import { BackendDataMapper } from '../../utils/backendDataMapper';
// Removed FinancialRequirementsCard - was only implemented for hospital
import { pdfService } from '@/services/api';
import { generateExportFilename } from '@/utils/filenameGenerator';
import { ScenarioModal } from '@/v2/components/ScenarioModal';
import { TrustPanel } from '@/v2/components/trust/TrustPanel';
import { 
  TrendingUp, DollarSign, Building, Clock, AlertCircle,
  Heart, Headphones, Cpu, MapPin, Calendar, ChevronRight,
  BarChart3, Users, Building2, Home, Briefcase, Target,
  GraduationCap, CheckCircle, Info, ArrowUpRight, XCircle,
  Activity, Shield, Wrench, Zap, Droplet, PaintBucket,
  AlertTriangle, Lightbulb, Download
} from 'lucide-react';

const DEBUG_EXECUTIVE =
  typeof window !== 'undefined' &&
  (window as any).__SPECSHARP_DEBUG_FLAGS__?.includes('executive') === true;

interface Props {
  project: Project;
  dealShieldData?: DealShieldViewModel | null;
}

// Local title casing to avoid depending on missing formatters.titleCase
const toTitleCase = (value?: string): string => {
  if (!value) return '';
  return value
    .toString()
    .replace(/_/g, ' ')
    .toLowerCase()
    .replace(/\b\w/g, c => c.toUpperCase());
};

const toComparableKey = (value: unknown): string | null => {
  if (typeof value !== 'string') return null;
  const trimmed = value.trim().toLowerCase();
  return trimmed ? trimmed.replace(/\s+/g, '_') : null;
};

type AnyRecord = Record<string, any>;

const toRecord = (value: unknown): AnyRecord =>
  value && typeof value === 'object' && !Array.isArray(value)
    ? (value as AnyRecord)
    : {};

const coalesceRecord = (...candidates: unknown[]): AnyRecord => {
  for (const candidate of candidates) {
    if (candidate && typeof candidate === 'object' && !Array.isArray(candidate)) {
      return candidate as AnyRecord;
    }
  }
  return {};
};

const isZeroLikeMetricValue = (value: unknown): boolean => {
  if (value === null || value === undefined) {
    return true;
  }
  if (typeof value === 'number') {
    return !Number.isFinite(value) || value === 0;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed || trimmed === '—' || trimmed.toLowerCase() === 'n/a') {
      return true;
    }
    const numeric = Number(trimmed.replace(/[^0-9.-]/g, ''));
    return Number.isFinite(numeric) && numeric === 0;
  }
  return false;
};

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

const normalizeBackendDecision = (value: unknown): DecisionStatus | undefined => {
  if (typeof value !== 'string') return undefined;
  const normalized = value.trim().toLowerCase();
  if (!normalized) return undefined;
  if (normalized.includes('no-go') || normalized.includes('no_go') || normalized.includes('no go')) return 'NO-GO';
  if (normalized.includes('needs work') || normalized.includes('near break') || normalized.includes('work')) return 'Needs Work';
  if (normalized.includes('pending') || normalized.includes('review')) return 'PENDING';
  if (normalized === 'go' || normalized.startsWith('go ')) return 'GO';
  return undefined;
};

const decisionReasonCopy = (value: unknown): string | undefined => {
  if (typeof value !== 'string') return undefined;
  const key = value.trim().toLowerCase();
  if (!key) return undefined;
  const map: Record<string, string> = {
    explicit_status_signal: 'Decision status is set directly by backend policy output.',
    not_modeled_inputs_missing: 'Decision status is pending because required modeled inputs are missing.',
    base_case_break_condition: 'Decision status is NO-GO because the base scenario already breaks.',
    base_value_gap_non_positive: 'Decision status is NO-GO because base value gap is non-positive.',
    low_flex_before_break_buffer: 'Decision status reflects low flex-before-break buffer.',
    base_value_gap_positive: 'Decision status is GO because base value gap is positive.',
    tight_flex_band: 'Decision status reflects a tight flex-before-break band.',
    flex_before_break_buffer_positive: 'Decision status reflects positive flex-before-break buffer.',
    insufficient_modeled_inputs: 'Decision status is pending due to insufficient modeled inputs.',
  };
  if (map[key]) return map[key];
  const label = key.replace(/_/g, ' ');
  return `${label.charAt(0).toUpperCase()}${label.slice(1)}.`;
};

const buildSafeAnalysis = (project?: Project | null): AnyRecord => {
  const projectRecord = toRecord(project);
  const rawAnalysis = toRecord(projectRecord.analysis);
  const calculations = coalesceRecord(
    rawAnalysis.calculations,
    projectRecord.calculation_data,
    projectRecord.calculations,
    projectRecord
  );
  const parsedInput = coalesceRecord(
    rawAnalysis.parsed_input,
    rawAnalysis.request_payload?.parsed_input,
    projectRecord.parsed_input,
    projectRecord.form_state,
    projectRecord.form_inputs
  );

  return {
    ...rawAnalysis,
    parsed_input: parsedInput,
    calculations
  };
};

interface SectionCardProps {
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}

const SectionCard: React.FC<SectionCardProps> = ({ title, subtitle, className, children }) => (
  <div className={`rounded-2xl border border-slate-200 bg-white shadow-sm ${className ?? ''}`}>
    <div className="px-6 py-5 border-b border-slate-100 space-y-2">
      {typeof title === 'string' ? (
        <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
      ) : (
        title
      )}
      {subtitle ? <p className="text-sm text-slate-500">{subtitle}</p> : null}
    </div>
    <div className="p-6">{children}</div>
  </div>
);

export const ExecutiveViewComplete: React.FC<Props> = ({ project, dealShieldData }) => {
  const navigate = useNavigate();
  const [isScenarioOpen, setIsScenarioOpen] = useState(false);
  const [isTrustPanelOpen, setIsTrustPanelOpen] = useState(false);
  const [trustPanelSection, setTrustPanelSection] = useState<string | undefined>();
  const openTrustPanel = (sectionId?: string) => {
    setTrustPanelSection(sectionId);
    setIsTrustPanelOpen(true);
  };
  useEffect(() => {
    if (!isTrustPanelOpen) {
      setTrustPanelSection(undefined);
    }
  }, [isTrustPanelOpen]);
  
  // Early return if no project data - check multiple paths for data
  if (!project?.analysis && !project?.calculation_data) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>Loading project data...</p>
      </div>
    );
  }

  // Normalize analysis payload so downstream consumers always receive objects
  const analysis = buildSafeAnalysis(project);
  
  // Map backend data through our mapper
  const displayData = BackendDataMapper.mapToDisplay(analysis || {});
  const revenueAnalysis =
    displayData?.revenueAnalysis ??
    displayData?.revenue_analysis ??
    {};
  const calculations = analysis?.calculations || {};
  const calculationsRecord = toRecord(calculations);
  const calculationFacilityMetrics = toRecord(
    calculationsRecord.facilityMetrics ?? calculationsRecord.facility_metrics
  );
  let { buildingType, facilityMetrics } = displayData;
  const rawBuildingType =
    analysis?.parsed_input?.building_type ??
    analysis?.parsed_input?.buildingType ??
    buildingType ??
    displayData?.buildingType ??
    '';
  const parsedBuildingType = rawBuildingType.toString().toLowerCase();
  const normalizedBuildingType = parsedBuildingType.replace(/\s+/g, '_');
  const rawSubtype =
    analysis?.parsed_input?.subtype ??
    analysis?.parsed_input?.building_subtype ??
    analysis?.parsed_input?.buildingSubtype ??
    displayData?.buildingSubtype ??
    '';
  const parsedSubtype = rawSubtype
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '_');
  const dealShieldRecord = toRecord(dealShieldData);
  const hasDealShieldPayload = Object.keys(dealShieldRecord).length > 0;
  const dealShieldProvenanceRecord = coalesceRecord(
    dealShieldRecord.decision_insurance_provenance,
    dealShieldRecord.decisionInsuranceProvenance,
    toRecord(dealShieldRecord.provenance).decision_insurance,
    toRecord(dealShieldRecord.provenance).decisionInsurance
  );
  const flexBeforeBreakProvenanceRecord = coalesceRecord(
    dealShieldProvenanceRecord.flex_before_break_pct,
    dealShieldProvenanceRecord.flexBeforeBreakPct
  );
  const firstBreakConditionRecord = coalesceRecord(
    dealShieldRecord.first_break_condition,
    dealShieldRecord.firstBreakCondition
  );
  const hasFirstBreakCondition = Object.keys(firstBreakConditionRecord).length > 0;
  const firstBreakScenarioId = toComparableKey(
    firstBreakConditionRecord.scenario_id ?? firstBreakConditionRecord.scenarioId
  );
  const firstBreakScenarioLabel = toComparableKey(
    firstBreakConditionRecord.scenario_label ?? firstBreakConditionRecord.scenarioLabel
  );
  const hasBaseBreakCondition =
    hasFirstBreakCondition &&
    (firstBreakScenarioId === 'base' || firstBreakScenarioLabel === 'base');
  const flexBeforeBreakReason = toComparableKey(flexBeforeBreakProvenanceRecord.reason);
  const hasBaseAlreadyBroken = flexBeforeBreakReason === 'base_already_broken';
  const flexBeforeBreakBand = toComparableKey(
    dealShieldRecord.flex_before_break_band ??
    dealShieldRecord.flexBeforeBreakBand ??
    flexBeforeBreakProvenanceRecord.band
  );
  const hasTightFlexBand =
    typeof flexBeforeBreakBand === 'string' &&
    flexBeforeBreakBand.includes('tight');
  const flexBeforeBreakPctValue = toFiniteNumber(
    dealShieldRecord.flex_before_break_pct ?? dealShieldRecord.flexBeforeBreakPct
  );
  const normalizedFlexBeforeBreakPct =
    typeof flexBeforeBreakPctValue === 'number'
      ? (Math.abs(flexBeforeBreakPctValue) <= 1.5 ? flexBeforeBreakPctValue * 100 : flexBeforeBreakPctValue)
      : null;
  const decisionSummaryRecord = coalesceRecord(
    dealShieldRecord.decision_summary,
    dealShieldRecord.decisionSummary
  );
  const canonicalValueGap = toFiniteNumber(
    decisionSummaryRecord.value_gap ??
    decisionSummaryRecord.valueGap ??
    dealShieldRecord.value_gap ??
    dealShieldRecord.valueGap
  );
  const canonicalNotModeledReason = toComparableKey(
    decisionSummaryRecord.not_modeled_reason ?? decisionSummaryRecord.notModeledReason
  );
  const displaySubtypeLower = (displayData?.buildingSubtype || '')
    .toString()
    .toLowerCase()
    .replace(/\s+/g, '_');
  const isFlexIndustrial = parsedSubtype === 'flex_space';
  const subtypeLabelOverride = displaySubtypeLower === 'flex_space' ? 'Flex Industrial' : null;
  const displayUnitLabelRaw =
    typeof displayData?.unitLabel === 'string' ? displayData.unitLabel : undefined;
  const facilityUnitLabel =
    typeof facilityMetrics?.unitLabel === 'string'
      ? facilityMetrics.unitLabel
      : typeof (facilityMetrics as AnyRecord)?.unit_label === 'string'
        ? (facilityMetrics as AnyRecord).unit_label
        : undefined;
  const calculationUnitLabel =
    typeof calculationsRecord.unit_label === 'string'
      ? calculationsRecord.unit_label
      : typeof calculationsRecord.unitLabel === 'string'
        ? calculationsRecord.unitLabel
        : undefined;
  const unitLabelCandidates = [facilityUnitLabel, calculationUnitLabel, displayUnitLabelRaw]
    .filter((label): label is string => typeof label === 'string');
  const unitLabelIndicatesDental = unitLabelCandidates.some(label => {
    const lower = label.toLowerCase();
    return (
      lower.includes('operatory') ||
      lower.includes('operatories') ||
      lower.includes('operat') ||
      lower.includes('dent')
    );
  });

  const isDentalOffice =
    (
      analysis?.parsed_input?.building_type === 'healthcare' &&
      analysis?.parsed_input?.subtype === 'dental_office'
    ) ||
    displaySubtypeLower === 'dental_office' ||
    unitLabelIndicatesDental;

  if (DEBUG_EXECUTIVE) {
    console.log('[SpecSharp][OE Debug]', {
      parsedSubtype: analysis?.parsed_input?.subtype,
      displaySubtype: displaySubtypeLower,
      unitLabelCandidates,
      unitLabelIndicatesDental,
      isDentalOffice
    });
  }
  const isHealthcareOutpatient =
    parsedBuildingType === 'healthcare' &&
    ['outpatient_clinic', 'urgent_care'].includes(parsedSubtype);
  const isImagingCenter =
    parsedBuildingType === 'healthcare' && parsedSubtype === 'imaging_center';
  const isSurgicalCenter =
    parsedBuildingType === 'healthcare' && parsedSubtype === 'surgical_center';
  const isHealthcareMob =
    parsedBuildingType === 'healthcare' &&
    (
      parsedSubtype === 'medical_office' ||
      displaySubtypeLower === 'medical_office' ||
      displaySubtypeLower.includes('medical_office') ||
      (typeof facilityUnitLabel === 'string' &&
        facilityUnitLabel.toLowerCase().includes('tenant suite'))
    );
  // Scenario modal base metrics (v1 universal multipliers)
  const projectInfo = calculations?.project_info || {};
  const isDistributionCenterProject =
    typeof projectInfo?.subtype === 'string' &&
    projectInfo.subtype.toLowerCase() === 'distribution_center';
  const distributionCenterLabel = 'Class A Distribution Center';
  const sanitizeDistributionCopy = (value?: string | null): string | undefined => {
    if (!isDistributionCenterProject) {
      return typeof value === 'string' ? value : undefined;
    }
    if (typeof value !== 'string' || !value.trim()) {
      return distributionCenterLabel;
    }
    return value.replace(/warehouse/gi, 'Distribution Center');
  };
  const scenarioProjectTitleRaw =
    (analysis?.parsed_input?.display_name as string) ||
    (analysis?.parsed_input?.project_name as string) ||
    (project as AnyRecord)?.project_name ||
    project?.name ||
    'Project';
  const scenarioProjectTitle = (() => {
    const sanitized = sanitizeDistributionCopy(scenarioProjectTitleRaw) ?? scenarioProjectTitleRaw;
    if (!sanitized) {
      return sanitized;
    }
    if (subtypeLabelOverride) {
      return sanitized.replace(/flex[\s-]+space/gi, subtypeLabelOverride);
    }
    return sanitized;
  })();

  const scenarioLocationLine = [
    (analysis?.parsed_input?.location as string) || project?.location || '',
    rawBuildingType || '',
    (analysis?.parsed_input?.square_footage as AnyRecord)?.toString?.() ||
      (project as AnyRecord)?.square_footage?.toString?.() ||
      '',
  ]
    .filter(Boolean)
    .join(' • ');

  const scenarioCalc = (analysis as AnyRecord)?.calculations || (project as AnyRecord)?.calculation_data || {};
  const scenarioDealShieldBundle = coalesceRecord(
    scenarioCalc?.dealshield_scenarios,
    scenarioCalc?.dealShieldScenarios,
    (analysis as AnyRecord)?.dealshield_scenarios,
    (analysis as AnyRecord)?.dealShieldScenarios,
    (project as AnyRecord)?.calculation_data?.dealshield_scenarios,
    (project as AnyRecord)?.calculation_data?.dealShieldScenarios,
    dealShieldRecord?.dealshield_scenarios,
    dealShieldRecord?.dealShieldScenarios,
    toRecord(dealShieldRecord?.view_model).dealshield_scenarios,
    toRecord(dealShieldRecord?.view_model).dealShieldScenarios,
    toRecord(dealShieldRecord?.viewModel).dealshield_scenarios,
    toRecord(dealShieldRecord?.viewModel).dealShieldScenarios
  );
  const scenarioReturn =
    scenarioCalc?.ownership_analysis?.return_metrics ||
    scenarioCalc?.ownershipAnalysis?.returnMetrics ||
    {};
  const scenarioDebtMetrics =
    scenarioCalc?.ownership_analysis?.debt_metrics ||
    scenarioCalc?.ownershipAnalysis?.debtMetrics ||
    {};

  const baseTotalInvestment =
    (scenarioCalc?.totals?.total_investment_required ??
      scenarioCalc?.totals?.totalInvestmentRequired ??
      null) ??
    (project as AnyRecord)?.total_cost ??
    (project as AnyRecord)?.totalCost ??
    null;

  const baseCostPerSf =
    (project as AnyRecord)?.cost_per_sqft ??
    (project as AnyRecord)?.costPerSqft ??
    null;

  const baseNoi =
    scenarioReturn?.estimated_annual_noi ??
    scenarioReturn?.estimatedAnnualNoi ??
    null;

  const baseYieldPct =
    scenarioReturn?.cash_on_cash_return ??
    scenarioReturn?.cashOnCashReturn ??
    null;

  const baseDscr =
    scenarioDebtMetrics?.calculated_dscr ??
    scenarioDebtMetrics?.calculatedDscr ??
    null;

  const basePayback =
    scenarioReturn?.payback_period ??
    scenarioReturn?.paybackPeriod ??
    null;

  const scenarioBase = {
    projectTitle: scenarioProjectTitle,
    locationLine: scenarioLocationLine,
    totalInvestment:
      typeof baseTotalInvestment === 'number'
        ? baseTotalInvestment
        : Number(baseTotalInvestment) || null,
    costPerSf:
      typeof baseCostPerSf === 'number'
        ? baseCostPerSf
        : Number(baseCostPerSf) || null,
    stabilizedNoi:
      typeof baseNoi === 'number' ? baseNoi : Number(baseNoi) || null,
    stabilizedYieldPct:
      typeof baseYieldPct === 'number'
        ? baseYieldPct
        : Number(baseYieldPct) || null,
    dscr:
      typeof baseDscr === 'number' ? baseDscr : Number(baseDscr) || null,
    paybackYears:
      typeof basePayback === 'number'
        ? basePayback
        : Number(basePayback) || null,
  };
  const isHealthcareSurgicalCenter =
    isSurgicalCenter ||
    (typeof facilityUnitLabel === 'string' &&
      facilityUnitLabel.toLowerCase().includes('operating room'));
  const revenuePerUnitLabel = isHealthcareSurgicalCenter
    ? 'Revenue per Operating Room'
    : isHealthcareMob
      ? 'Revenue per Suite'
      : 'Revenue per Bed';
  const unitsPerNurseLabel = isHealthcareSurgicalCenter
    ? 'ORs per Nurse'
    : 'Beds per Nurse';
  let unitLabel = facilityUnitLabel
    ? toTitleCase(facilityUnitLabel)
    : displayUnitLabelRaw
      ? toTitleCase(displayUnitLabelRaw)
      : 'Units';
  let unitType = (facilityUnitLabel || displayData?.unitType || unitLabel || 'units').toString().toLowerCase();
  if (parsedBuildingType === 'healthcare') {
    if (isHealthcareOutpatient) {
      unitLabel = 'Exam Rooms';
      unitType = 'exam rooms';
    } else if (isSurgicalCenter) {
      unitLabel = 'Operating Rooms';
      unitType = 'operating rooms';
    } else if (isDentalOffice) {
      unitLabel = 'Operatories';
      unitType = 'operatories';
    }
  }
  const isOffice =
    buildingType === 'OFFICE' ||
    (typeof buildingType === 'string' && buildingType.toUpperCase().includes('OFFICE'));
  const isMultifamilyProject = parsedBuildingType.includes('multifamily');
  const staffing = toRecord(
    displayData?.operational_metrics?.staffing ??
    displayData?.operational_metrics ??
    displayData?.staffing
  );
  const facilityUnitsValue =
    calculationFacilityMetrics.units ??
    facilityMetrics?.units ??
    displayData?.facilityMetrics?.units ??
    null;
  const backendStaffing = toRecord(
    calculationsRecord.staffing ??
    calculationsRecord.staffing_metrics ??
    {}
  );
  const providersFromBackend =
    typeof backendStaffing.providers === 'number' && backendStaffing.providers > 0
      ? backendStaffing.providers
      : typeof backendStaffing.total_providers === 'number' && backendStaffing.total_providers > 0
        ? backendStaffing.total_providers
        : undefined;
  const fallbackProvidersValue =
    typeof staffing?.providers === 'number' && staffing.providers > 0
      ? staffing.providers
      : undefined;
  const dentalProviderCount = providersFromBackend ?? fallbackProvidersValue ?? 1;

  const parseNumericOrNull = (value: unknown): number | null => {
    if (typeof value === 'number' && !Number.isNaN(value)) return value;
    if (typeof value === 'string') {
      const cleaned = value.replace(/[^0-9.\-]/g, '');
      const parsed = parseFloat(cleaned);
      return Number.isFinite(parsed) ? parsed : null;
    }
    return null;
  };

  let dentalAnnualRevenueValue = parseNumericOrNull(
    (revenueAnalysis as AnyRecord | null | undefined)?.annual_revenue
  );

  if (dentalAnnualRevenueValue == null) {
    dentalAnnualRevenueValue =
      typeof displayData?.annualRevenue === 'number'
        ? displayData.annualRevenue
        : null;
  }

  let dentalNoiMarginRaw = parseNumericOrNull(
    (revenueAnalysis as AnyRecord | null | undefined)?.operating_margin
  );

  if (dentalNoiMarginRaw == null) {
    dentalNoiMarginRaw =
      typeof displayData?.operatingMargin === 'number'
        ? displayData.operatingMargin
        : null;
  }

  const dentalNoiMarginValue =
    dentalNoiMarginRaw != null
      ? dentalNoiMarginRaw > 1
        ? dentalNoiMarginRaw / 100
        : dentalNoiMarginRaw
      : null;
  const dentalOperatoriesValue =
    typeof facilityUnitsValue === 'number' ? facilityUnitsValue : null;
  const dentalRevenuePerProviderValue =
    dentalAnnualRevenueValue != null && dentalProviderCount > 0
      ? dentalAnnualRevenueValue / dentalProviderCount
      : null;
  const dentalRevenuePerOperatoryValue =
    dentalAnnualRevenueValue != null &&
    typeof dentalOperatoriesValue === 'number' &&
    dentalOperatoriesValue > 0
      ? dentalAnnualRevenueValue / dentalOperatoriesValue
      : null;
  const dentalUtilizationValue =
    dentalRevenuePerOperatoryValue != null
      ? Math.min(dentalRevenuePerOperatoryValue / 600000, 1)
      : null;
  const dentalOpsPerProviderValue =
    typeof dentalOperatoriesValue === 'number' &&
    dentalOperatoriesValue > 0 &&
    dentalProviderCount > 0
      ? (dentalOperatoriesValue / dentalProviderCount).toFixed(1)
      : null;

  if (DEBUG_EXECUTIVE && isDentalOffice) {
    console.log('[SpecSharp][OE Dental Metrics]', {
      revenueAnalysis,
      staffingRecord: backendStaffing,
      dentalAnnualRevenueValue,
      dentalNoiMarginValue,
      dentalProviderCount,
      dentalOperatoriesValue,
      dentalRevenuePerProviderValue,
      dentalRevenuePerOperatoryValue,
      dentalUtilizationValue,
      dentalOpsPerProviderValue
    });
  }
  const revenueRequired = {
    impliedAdrForTargetRevpar: displayData.impliedAdrForTargetRevpar,
    impliedOccupancyForTargetRevpar: displayData.impliedOccupancyForTargetRevpar,
    requiredNoiPerSf: displayData.requiredNoiPerSf,
    currentNoiPerSf: displayData.currentNoiPerSf,
  };
  const staffingMetricsArray = Array.isArray(displayData.staffingMetrics)
    ? displayData.staffingMetrics
    : [];
  let normalizedStaffingMetrics = staffingMetricsArray.map(metric => {
    if (
      isHealthcareSurgicalCenter &&
      typeof metric?.label === 'string' &&
      metric.label.toLowerCase().includes('beds per nurse')
    ) {
      return { ...metric, label: unitsPerNurseLabel };
    }
    return metric;
  });
  if (isDentalOffice) {
    const operatories = facilityUnitsValue;
    const noiMarginValue = typeof revenueAnalysis?.operating_margin === 'number'
      ? revenueAnalysis.operating_margin
      : null;
    normalizedStaffingMetrics = [
      {
        label: 'Operatories',
        value: operatories != null ? operatories : '-',
      },
      {
        label: 'NOI Margin',
        value: noiMarginValue != null
          ? formatters.percentage(noiMarginValue)
          : formatters.percentage(0),
      },
    ];
  }
  if (isHealthcareMob) {
    const tenantSuites =
      facilityMetrics?.units ??
      displayData?.facilityMetrics?.units ??
      null;
    const noiMarginValue =
      typeof displayData?.operatingMargin === 'number'
        ? displayData.operatingMargin
        : typeof displayData?.operationalEfficiency?.operating_margin === 'number'
          ? displayData.operationalEfficiency.operating_margin
          : typeof displayData?.operational_metrics?.operating_margin === 'number'
            ? displayData.operational_metrics.operating_margin
            : typeof revenueAnalysis?.operating_margin === 'number'
              ? revenueAnalysis.operating_margin
              : null;
    normalizedStaffingMetrics = [
      {
        label: 'Tenant Suites',
        value: tenantSuites != null ? tenantSuites : '-',
      },
      {
        label: 'NOI Margin',
        value: typeof noiMarginValue === 'number'
          ? formatters.percentage(noiMarginValue)
          : formatters.percentage(0),
      },
    ];
  }
  const revenueMetricsRecord = toRecord(displayData.revenueMetrics || {});
  let normalizedRevenueMetrics = Object.entries(revenueMetricsRecord).map(
    ([key, value]) => {
      const normalizedKey = typeof key === 'string' ? key : '';
      const normalizedKeyLower = normalizedKey.trim().toLowerCase();
      const spacedLabel = normalizedKey.includes('_')
        ? normalizedKey.replace(/_/g, ' ')
        : normalizedKey;
      const isPerBedMetric =
        normalizedKeyLower === 'revenue_per_bed' ||
        spacedLabel.toLowerCase() === 'revenue per bed';
      const label =
        isPerBedMetric && (isHealthcareSurgicalCenter || isHealthcareMob)
          ? revenuePerUnitLabel
          : spacedLabel.toLowerCase() === 'labor cost ratio' && isHealthcareMob
            ? 'Labor Cost Ratio (N/A)'
            : spacedLabel;
      return { key: normalizedKey || 'metric', label, value };
    }
  );
  if (isDentalOffice) {
    const providersRaw =
      typeof staffing?.providers === 'number'
        ? staffing.providers
        : null;
    const providers = providersRaw && providersRaw > 0 ? providersRaw : 1;
    const annualRevenueValue = typeof revenueAnalysis?.annual_revenue === 'number'
      ? revenueAnalysis.annual_revenue
      : null;
    const operatories = facilityUnitsValue;
    const revenuePerProvider = annualRevenueValue != null && providers > 0
      ? formatters.currencyExact(annualRevenueValue / providers)
      : formatters.currencyExact(0);
    const revenuePerOperatory = annualRevenueValue != null &&
      typeof operatories === 'number' &&
      operatories > 0
        ? formatters.currencyExact(annualRevenueValue / operatories)
        : formatters.currencyExact(0);
    const opMargin = typeof revenueAnalysis?.operating_margin === 'number'
      ? formatters.percentage(revenueAnalysis.operating_margin)
      : formatters.percentage(0);
    normalizedRevenueMetrics = [
      {
        key: 'rev_provider',
        label: 'Revenue per Provider',
        value: revenuePerProvider
      },
      {
        key: 'rev_operatory',
        label: 'Revenue per Operatory',
        value: revenuePerOperatory
      },
      {
        key: 'op_margin',
        label: 'Operating Margin',
        value: opMargin
      }
    ];
  }
  let operationalKpis = displayData.kpis || [];
  if (isHealthcareMob) {
    const totalsData = displayData?.totals || calculations?.totals || {};
    const softCostsValue =
      totalsData?.soft_costs ??
      totalsData?.soft_costs_total ??
      totalsData?.softCosts ??
      totalsData?.softCostsTotal ??
      0;
    const totalCostValue =
      totalsData?.total_project_cost ??
      totalsData?.total_cost ??
      totalsData?.totalProjectCost ??
      totalsData?.totalCost ??
      0;
    const yieldOnCostValue =
      displayData?.yieldOnCost ??
      displayData?.yield_on_cost ??
      calculations?.ownership_analysis?.yield_on_cost ??
      calculations?.ownership_analysis?.yieldOnCost ??
      undefined;
    const dscrValue =
      displayData?.dscr ??
      calculations?.ownership_analysis?.debt_metrics?.calculated_dscr ??
      calculations?.ownership_analysis?.debt_metrics?.calculatedDSCR ??
      undefined;
    const softCostPct =
      totalCostValue && softCostsValue
        ? softCostsValue / totalCostValue
        : undefined;
    operationalKpis = [
      {
        label: 'Yield on Cost',
        value: typeof yieldOnCostValue === 'number'
          ? formatters.percentage(yieldOnCostValue)
          : formatters.percentage(0),
        color: 'purple'
      },
      {
        label: 'DSCR',
        value: typeof dscrValue === 'number'
          ? `${dscrValue.toFixed(2)}×`
          : '—',
        color: 'indigo'
      },
      {
        label: 'Soft Costs % of Total',
        value: typeof softCostPct === 'number'
          ? formatters.percentage(softCostPct)
          : formatters.percentage(0),
        color: 'pink'
      }
    ];
  }
  if (isDentalOffice) {
    const providersRaw =
      typeof staffing?.providers === 'number'
        ? staffing.providers
        : null;
    const providers = providersRaw && providersRaw > 0 ? providersRaw : 1;
    const annualRevenueValue = typeof revenueAnalysis?.annual_revenue === 'number'
      ? revenueAnalysis.annual_revenue
      : null;
    const operatories = facilityUnitsValue;
    const productionPerProvider = annualRevenueValue != null && providers > 0
      ? formatters.currencyExact(annualRevenueValue / providers)
      : formatters.currencyExact(0);
    const utilizationPct = annualRevenueValue != null &&
      typeof operatories === 'number' &&
      operatories > 0
        ? formatters.percentage(Math.min(annualRevenueValue / (operatories * 600000), 1))
        : formatters.percentage(0);
    const opsPerProvider = typeof operatories === 'number' &&
      operatories > 0 &&
      providers > 0
        ? (operatories / providers).toFixed(1)
        : '0.0';
    operationalKpis = [
      {
        label: 'Production / Provider',
        value: productionPerProvider,
        color: 'purple'
      },
      {
        label: 'Chair Utilization',
        value: utilizationPct,
        color: 'indigo'
      },
      {
        label: 'Ops per Provider',
        value: opsPerProvider,
        color: 'pink'
      }
    ];
  }
  const projectTimeline = displayData.projectTimeline;
  const dscrFromDisplay = typeof displayData.dscr === 'number' ? displayData.dscr : undefined;
  const dscrFromOwnership = typeof (analysis as AnyRecord)?.calculations?.ownership_analysis?.debt_metrics?.calculated_dscr === 'number'
    ? (analysis as AnyRecord).calculations.ownership_analysis.debt_metrics.calculated_dscr
    : undefined;
  const targetDscrFromOwnership = typeof (analysis as AnyRecord)?.calculations?.ownership_analysis?.debt_metrics?.target_dscr === 'number'
    ? (analysis as AnyRecord).calculations.ownership_analysis.debt_metrics.target_dscr
    : undefined;
  const dscr = dscrFromDisplay ?? dscrFromOwnership;
  const targetDscr = targetDscrFromOwnership;
  const resolvedTargetDscr = typeof targetDscr === 'number' && Number.isFinite(targetDscr) ? targetDscr : 1.25;
  const dscrTargetDisplay = Number.isFinite(resolvedTargetDscr)
    ? `${resolvedTargetDscr.toFixed(2)}×`
    : '—';
  const yieldOnCost = typeof displayData.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
    ? displayData.yieldOnCost
    : undefined;
  const stabilizedYield = typeof yieldOnCost === 'number'
    ? yieldOnCost
    : (typeof displayData.roi === 'number' ? displayData.roi : 0);
  const marketCapRateDisplay = typeof displayData.marketCapRate === 'number' && Number.isFinite(displayData.marketCapRate)
    ? displayData.marketCapRate
    : undefined;
  const capRateSpreadBps = typeof displayData.capRateSpreadBps === 'number' && Number.isFinite(displayData.capRateSpreadBps)
    ? displayData.capRateSpreadBps
    : undefined;
  const effectiveYield = typeof yieldOnCost === 'number'
    ? yieldOnCost
    : (typeof displayData.roi === 'number' && Number.isFinite(displayData.roi) ? displayData.roi : undefined);
  const marketCapRateValue = marketCapRateDisplay;
  const computedYieldCapSpreadPct = typeof effectiveYield === 'number' && typeof marketCapRateValue === 'number'
    ? effectiveYield - marketCapRateValue
    : undefined;
  const yieldCapSpreadPct = typeof capRateSpreadBps === 'number'
    ? capRateSpreadBps / 10000
    : computedYieldCapSpreadPct;
  const yieldCapSpreadBps = typeof capRateSpreadBps === 'number'
    ? capRateSpreadBps
    : (typeof computedYieldCapSpreadPct === 'number' ? computedYieldCapSpreadPct * 10000 : undefined);
  const equityReturn = typeof displayData.roi === 'number' && Number.isFinite(displayData.roi)
    ? displayData.roi
    : undefined;
  const investmentDecisionFromDisplay = displayData.investmentDecision;
  const feasibilityFlag = typeof displayData.feasible === 'boolean' ? displayData.feasible : undefined;
  const backendDecision = normalizeBackendDecision(
    typeof investmentDecisionFromDisplay === 'string'
      ? investmentDecisionFromDisplay
      : investmentDecisionFromDisplay?.recommendation ?? investmentDecisionFromDisplay?.status
  );
  const fallbackDecisionStatus: DecisionStatus =
    backendDecision ??
    (feasibilityFlag === true
      ? 'GO'
      : feasibilityFlag === false
        ? 'NO-GO'
        : 'PENDING');
  const spreadBpsValue =
    typeof yieldOnCost === 'number' &&
    Number.isFinite(yieldOnCost) &&
    typeof marketCapRateDisplay === 'number' &&
    Number.isFinite(marketCapRateDisplay)
      ? (yieldOnCost - marketCapRateDisplay) * 10000
      : undefined;
  const dscrValue = typeof dscr === 'number' && Number.isFinite(dscr) ? dscr : undefined;
  const spreadPctValue = typeof spreadBpsValue === 'number' ? spreadBpsValue / 100 : undefined;
  const derivedDecisionStatus: DecisionStatus | undefined = (() => {
    if (
      typeof spreadBpsValue === 'number' &&
      typeof marketCapRateDisplay === 'number' &&
      typeof yieldOnCost === 'number' &&
      Number.isFinite(yieldOnCost) &&
      typeof dscrValue === 'number'
    ) {
      if (spreadBpsValue >= 200 && dscrValue >= resolvedTargetDscr) {
        return 'GO';
      }
      if (spreadBpsValue >= 0 && dscrValue >= resolvedTargetDscr) {
        return 'Needs Work';
      }
      return 'NO-GO';
    }
    return undefined;
  })();
  const explicitDealShieldDecision = normalizeBackendDecision(
    dealShieldRecord.decision_status ??
      dealShieldRecord.decisionStatus ??
      decisionSummaryRecord.decision_status ??
      decisionSummaryRecord.decisionStatus ??
      decisionSummaryRecord.recommendation ??
      decisionSummaryRecord.status
  );
  const decisionReasonCode =
    (typeof dealShieldRecord.decision_reason_code === 'string' ? dealShieldRecord.decision_reason_code : undefined) ??
    (typeof dealShieldRecord.decisionReasonCode === 'string' ? dealShieldRecord.decisionReasonCode : undefined) ??
    (typeof decisionSummaryRecord.decision_reason_code === 'string' ? decisionSummaryRecord.decision_reason_code : undefined) ??
    (typeof decisionSummaryRecord.decisionReasonCode === 'string' ? decisionSummaryRecord.decisionReasonCode : undefined);
  const decisionStatusProvenanceRecord = coalesceRecord(
    dealShieldRecord.decision_status_provenance,
    dealShieldRecord.decisionStatusProvenance,
    decisionSummaryRecord.decision_status_provenance,
    decisionSummaryRecord.decisionStatusProvenance
  );
  const decisionStatusSource =
    (typeof decisionStatusProvenanceRecord.status_source === 'string' ? decisionStatusProvenanceRecord.status_source : undefined) ??
    (typeof decisionStatusProvenanceRecord.statusSource === 'string' ? decisionStatusProvenanceRecord.statusSource : undefined);
  const decisionPolicyId =
    (typeof decisionStatusProvenanceRecord.policy_id === 'string' ? decisionStatusProvenanceRecord.policy_id : undefined) ??
    (typeof decisionStatusProvenanceRecord.policyId === 'string' ? decisionStatusProvenanceRecord.policyId : undefined);
  const canonicalDealShieldDecisionStatus: DecisionStatus | undefined = (() => {
    if (!hasDealShieldPayload || !explicitDealShieldDecision) return undefined;
    return explicitDealShieldDecision;
  })();
  const fallbackDealShieldDecisionStatus: DecisionStatus | undefined = (() => {
    if (!hasDealShieldPayload || canonicalDealShieldDecisionStatus) return undefined;
    if (canonicalNotModeledReason) return 'PENDING';
    if (hasBaseBreakCondition || hasBaseAlreadyBroken) return 'NO-GO';
    if (typeof canonicalValueGap === 'number') {
      if (canonicalValueGap <= 0) return 'NO-GO';
      if (
        typeof normalizedFlexBeforeBreakPct === 'number' &&
        normalizedFlexBeforeBreakPct <= 2
      ) {
        return 'Needs Work';
      }
      return 'GO';
    }
    if (hasTightFlexBand) return 'Needs Work';
    if (typeof normalizedFlexBeforeBreakPct === 'number') {
      return normalizedFlexBeforeBreakPct <= 2 ? 'Needs Work' : 'GO';
    }
    return undefined;
  })();
  let decisionStatus: DecisionStatus =
    canonicalDealShieldDecisionStatus ?? fallbackDealShieldDecisionStatus ?? derivedDecisionStatus ?? fallbackDecisionStatus;
  // Preserve historical industrial fallback when no DealShield-based status is available.
  (() => {
    if (canonicalDealShieldDecisionStatus || fallbackDealShieldDecisionStatus) return;
    const bt = (buildingType || '').toLowerCase();
    if (bt !== 'industrial') return;

    const yoc =
      typeof displayData.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
        ? displayData.yieldOnCost
        : undefined;
    const targetYieldFromDisplay =
      typeof displayData.targetYield === 'number' && Number.isFinite(displayData.targetYield)
        ? displayData.targetYield
        : undefined;
    const dscrOk =
      typeof dscrValue === 'number' &&
      typeof resolvedTargetDscr === 'number' &&
      Number.isFinite(dscrValue) &&
      Number.isFinite(resolvedTargetDscr)
        ? dscrValue >= resolvedTargetDscr
        : false;

    if (typeof yoc !== 'number' || typeof targetYieldFromDisplay !== 'number') {
      return;
    }

    if (dscrOk && yoc >= targetYieldFromDisplay) {
      decisionStatus = 'GO';
      return;
    }

    if (dscrOk && yoc >= targetYieldFromDisplay * 0.95) {
      decisionStatus = 'Needs Work';
      return;
    }

    decisionStatus = 'NO-GO';
  })();
  const isDealShieldCanonicalStatusActive = Boolean(canonicalDealShieldDecisionStatus);
  const decisionStatusLabel =
    decisionStatus === 'Needs Work'
      ? 'Needs Work'
      : decisionStatus === 'NO-GO'
        ? 'NO-GO'
        : decisionStatus === 'PENDING'
          ? 'Under Review'
          : 'GO';
  const feasibilityChipLabel =
    decisionStatus === 'Needs Work'
      ? 'Needs Work'
      : decisionStatus === 'NO-GO'
        ? 'NO-GO'
        : decisionStatus === 'GO'
          ? 'GO'
          : 'Needs Review';
  const decisionReasonText = decisionReasonCopy(decisionReasonCode)
    || (typeof decisionStatusProvenanceRecord.not_modeled_reason === 'string' ? decisionStatusProvenanceRecord.not_modeled_reason : undefined)
    || (typeof decisionStatusProvenanceRecord.notModeledReason === 'string' ? decisionStatusProvenanceRecord.notModeledReason : undefined)
    || displayData.decisionReason || (
    typeof investmentDecisionFromDisplay === 'object'
      ? investmentDecisionFromDisplay?.summary
    : undefined
  ) || 'Debt coverage and yield metrics are still loading.';
  const formatPct = (value?: number) =>
    typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(1)}%` : '—';
  const yieldPctValue = typeof yieldOnCost === 'number' && Number.isFinite(yieldOnCost)
    ? yieldOnCost * 100
    : undefined;
  const marketCapPctValue = typeof marketCapRateDisplay === 'number' && Number.isFinite(marketCapRateDisplay)
    ? marketCapRateDisplay * 100
    : undefined;
  const dscrText = typeof dscrValue === 'number' ? `${dscrValue.toFixed(2)}×` : undefined;
  const dscrTargetText = `${resolvedTargetDscr.toFixed(2)}×`;
  const dscrMeetsTarget = typeof dscrValue === 'number' && Number.isFinite(dscrValue)
    ? dscrValue >= resolvedTargetDscr
    : undefined;
  const stabilizedValueGapDisplay =
    typeof canonicalValueGap === 'number' && Number.isFinite(canonicalValueGap)
      ? `${canonicalValueGap >= 0 ? '+' : '-'}${formatters.currency(Math.abs(canonicalValueGap))}`
      : '—';
  const decisionCopy = (() => {
    const yieldText = formatPct(yieldPctValue);
    const marketText = formatPct(marketCapPctValue);
    const spreadText = typeof spreadPctValue === 'number'
      ? `${spreadPctValue >= 0 ? '+' : ''}${spreadPctValue.toFixed(1)}%`
      : undefined;
    if (decisionStatus === 'GO') {
      if (isMultifamilyProject) {
        return {
          body: 'Project clears multifamily underwriting across equity and debt lenses.',
          detail: `Equity Lens: ${yieldPctValue !== undefined ? `yield on cost ${yieldText}` : 'yield on cost'}${marketCapPctValue !== undefined ? ` vs market cap ${marketText}` : ''}${spreadText ? ` (${spreadText})` : ''}. Debt Lens: DSCR ${dscrText ?? '—'} meets target ${dscrTargetText}. Reality Check: stabilized value gap ${stabilizedValueGapDisplay}.`
        };
      }
      return {
        body: 'Project meets underwriting criteria with strong returns and healthy debt coverage.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'}${marketCapPctValue !== undefined ? ` vs market cap ${marketText}` : ''}${spreadText ? ` (${spreadText})` : ''}${
          dscrText
            ? ` and DSCR ${dscrText} ${dscrMeetsTarget === false ? `is below` : `meets`} the ${dscrTargetText} requirement.`
            : '.'
        }`
      };
    }
    if (decisionStatus === 'Needs Work') {
      return {
        body: 'Project is close to the yield hurdle but still needs improvement.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'} is roughly in line with the market cap${spreadText ? ` (${spreadText})` : ''}. Keep DSCR ${dscrText ?? '—'}× at or above ${dscrTargetText} while lifting NOI or trimming costs to add at least 200 bp of spread.`
      };
    }
    if (decisionStatus === 'NO-GO') {
      return {
        body: 'Project currently falls below underwriting thresholds.',
        detail: `${yieldPctValue !== undefined ? `Yield on cost ${yieldText}` : 'Yield on cost'}${marketCapPctValue !== undefined ? ` vs market cap ${marketText}` : ''}${spreadText ? ` (${spreadText})` : ''} and/or DSCR ${dscrText ?? '—'}× are below the ${dscrTargetText} requirement. Improve rents, cut scope, or rework the capital stack before advancing.`
      };
    }
    return {
      body: 'Investment analysis is still running.',
      detail: 'Once NOI, yield on cost, and DSCR metrics are available, this banner will classify the deal automatically.'
    };
  })();
  const decisionBodyClass = `mt-1 text-sm ${
    decisionStatus === 'GO' ? 'text-green-700' : decisionStatus === 'NO-GO' ? 'text-red-700' : 'text-amber-700'
  }`;
  const decisionDetailClass = `mt-1 text-xs ${
    decisionStatus === 'GO' ? 'text-green-600' : decisionStatus === 'NO-GO' ? 'text-red-600' : 'text-amber-600'
  }`;
  
  // Extract additional raw data we need - check multiple paths for data
  const parsed = analysis?.parsed_input || {};
  const ownership = calculations?.ownership_analysis || {};
  const rawConstructionSchedule = calculations?.construction_schedule;
  const totals = calculations?.totals || {};
  const construction_costs = calculations?.construction_costs || {};
  const soft_costs = calculations?.soft_costs || {};
  const investmentAnalysis = ownership?.investment_analysis || {};
  const debtMetrics = ownership?.debt_metrics || calculations?.debt_metrics || {};
  const annualDebtService = typeof debtMetrics?.annual_debt_service === 'number' && Number.isFinite(debtMetrics.annual_debt_service)
    ? debtMetrics.annual_debt_service
    : undefined;
  const hasDebt = typeof debtMetrics?.annual_debt_service === 'number' && debtMetrics.annual_debt_service > 0;
  const calculationTrace = Array.isArray(calculations?.calculation_trace)
    ? calculations.calculation_trace.filter((entry: any) => entry && typeof entry === 'object' && entry.step)
    : [];

  const getLatestTrace = (step: string) => {
    for (let i = calculationTrace.length - 1; i >= 0; i -= 1) {
      const entry = calculationTrace[i];
      if (entry?.step === step) {
        return entry;
      }
    }
    return undefined;
  };

  const finishSourceEntry = getLatestTrace('finish_level_source');
  const modifiersTrace = getLatestTrace('modifiers_applied');
  const inferredTrace = getLatestTrace('finish_level_inferred');

  const normalizeFinishLevel = (value?: string | null) => {
    if (!value || typeof value !== 'string') {
      return undefined;
    }
    const trimmed = value.trim();
    if (!trimmed) {
      return undefined;
    }
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
  };

  const finishLevelFromDisplay = normalizeFinishLevel(displayData.finishLevel);
  const finishLevelFromProject = normalizeFinishLevel(projectInfo?.finish_level);
  const finishLevelFromTrace = normalizeFinishLevel(inferredTrace?.data?.finish_level || modifiersTrace?.data?.finish_level);
  const finishLevel = finishLevelFromProject || finishLevelFromDisplay || finishLevelFromTrace;

  const displayFinishSource = displayData.finishLevelSource;
  const finishSourceRaw = finishSourceEntry?.data?.source;
  const finishSource =
    displayFinishSource === 'explicit' || displayFinishSource === 'description' || displayFinishSource === 'default'
      ? displayFinishSource
      : finishSourceRaw === 'explicit' || finishSourceRaw === 'description'
        ? finishSourceRaw
        : 'default';

  const regionalContext = toRecord(
    calculations?.regional ||
    analysis?.regional ||
    project?.analysis?.regional ||
    displayData?.regional
  );
  const costFactorFromDisplay = typeof displayData.costFactor === 'number' ? displayData.costFactor : undefined;
  const costFactorFromRegional = typeof regionalContext.cost_factor === 'number' ? regionalContext.cost_factor : undefined;
  const marketFactorFromRegional = typeof regionalContext.market_factor === 'number' ? regionalContext.market_factor : undefined;
  const modifierCostFactor = typeof modifiersTrace?.data?.cost_factor === 'number' ? modifiersTrace.data.cost_factor : undefined;
  const modifierMarketFactor = typeof modifiersTrace?.data?.market_factor === 'number' ? modifiersTrace.data.market_factor : undefined;
  const costFactor = costFactorFromRegional ?? modifierCostFactor ?? costFactorFromDisplay ?? 1.0;
  const marketFactor = marketFactorFromRegional ?? modifierMarketFactor ?? 1.0;

  const costPerSFValue = typeof displayData.costPerSF === 'number' && Number.isFinite(displayData.costPerSF)
    ? displayData.costPerSF
    : undefined;
  const marketCostPerSFField = (displayData as AnyRecord)?.marketCostPerSF;
  const inferredMarketCostPerSF = typeof costPerSFValue === 'number' && typeof costFactor === 'number' && costFactor > 0
    ? costPerSFValue / costFactor
    : undefined;
  const marketCostPerSF = typeof marketCostPerSFField === 'number' && Number.isFinite(marketCostPerSFField)
    ? marketCostPerSFField
    : inferredMarketCostPerSF;
  const costPerSFDeltaPct = typeof costPerSFValue === 'number' && typeof marketCostPerSF === 'number' && marketCostPerSF !== 0
    ? ((costPerSFValue - marketCostPerSF) / marketCostPerSF) * 100
    : undefined;
  const costPerSFGaugePosition = (() => {
    if (typeof costPerSFDeltaPct === 'number') {
      const clamped = Math.max(-20, Math.min(20, costPerSFDeltaPct));
      return ((clamped + 20) / 40) * 100;
    }
    return 50;
  })();
  const softCostRatio = typeof displayData.softCosts === 'number' &&
    typeof displayData.totalProjectCost === 'number' &&
    displayData.totalProjectCost > 0
      ? displayData.softCosts / displayData.totalProjectCost
      : undefined;

  const isDev = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV);

  const formatMultiplier = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return undefined;
    }
    return value.toFixed(3).replace(/(?:\.0+|(\.\d+?)0+)$/, '$1');
  };
  const formatChipMultiplier = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return undefined;
    }
    return value.toFixed(2);
  };

  const costFactorText = formatChipMultiplier(costFactor);
  const marketFactorText = formatChipMultiplier(marketFactor);

  const finishChipTooltip = finishSource === 'explicit'
    ? 'Source: Selected in form'
    : finishSource === 'description'
      ? 'Source: Inferred from description'
      : 'Source: Default (Standard)';

  const hasFinishPayload = Boolean(finishLevel || costFactor || marketFactor);
  const finishChipDetail = hasFinishPayload
    ? `Finish: ${finishLevel || 'Standard'} ${costFactorText && marketFactorText
      ? `(Cost ×${costFactorText} · Market ×${marketFactorText})`
      : '(applied)'}`.trim()
    : 'MISSING';

  const finishChipClasses = hasFinishPayload
    ? 'ml-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border bg-indigo-500/15 text-indigo-100 border-indigo-400/40'
    : 'ml-2 inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border bg-red-500/15 text-red-100 border-red-400/40';

  const finishDevLogRef = useRef(false);

  useEffect(() => {
    if (!isDev || finishDevLogRef.current) {
      return;
    }
    if (DEBUG_EXECUTIVE) {
      console.log('[SpecSharp DEV] Finish chip payload', {
        finishLevel: finishLevel || 'Standard',
        costFactor,
        marketFactor,
        modifiersTrace: modifiersTrace?.data || null,
        finishSource
      });
      finishDevLogRef.current = true;
    }
  }, [isDev, finishLevel, modifiersTrace, finishSource, costFactor, marketFactor]);
  
  // Basic project info
  const enrichedParsed: any = analysis?.parsed_input || {};
  const squareFootage =
    Number(enrichedParsed?.square_footage) ||
    Number(calculations?.construction_costs?.square_footage) ||
    Number(calculations?.totals?.square_footage) ||
    0;
  if (!buildingType) {
    buildingType = (enrichedParsed?.building_type || parsed?.building_type || 'general') as string;
  }
  const buildingSubtype = parsed?.building_subtype || parsed?.subtype || 'general';
  const location = parsed?.location || 'Nashville';
  let friendlyType =
    (enrichedParsed?.__display_type as string) ||
    toTitleCase(
      (projectInfo?.subtype as string) ||
      (projectInfo?.display_name as string) ||
      buildingSubtype ||
      buildingType ||
      'general'
    ) ||
    'General';
  if (isDistributionCenterProject) {
    friendlyType = distributionCenterLabel;
  }
  // For multifamily and other building types, use typical_floors if available (more accurate)
  const floors = projectInfo?.typical_floors || parsed?.floors || 1;
  const headerSquareFootage =
    Number(projectInfo?.square_footage) ||
    Number(totals?.square_footage) ||
    squareFootage;
  let headerFriendlyType =
    toTitleCase(
      (projectInfo?.subtype as string) ||
      (projectInfo?.display_name as string) ||
      friendlyType
    ) || friendlyType;
  if (isDistributionCenterProject) {
    headerFriendlyType = distributionCenterLabel;
  }
  const canonicalSubtype = String(
    (enrichedParsed?.subtype as string) ||
    (parsed?.subtype as string) ||
    (parsed?.building_subtype as string) ||
    (projectInfo?.subtype as string) ||
    buildingSubtype ||
    ''
  ).toLowerCase();
  const isFlexSpaceCanonical = canonicalSubtype === 'flex_space';
  if (isFlexSpaceCanonical) {
    friendlyType = 'Flex Industrial';
    headerFriendlyType = 'Flex Industrial';
  } else if (subtypeLabelOverride) {
    headerFriendlyType = headerFriendlyType.replace(/flex[\s-]+space/gi, subtypeLabelOverride);
  }
  const heroTitle =
    headerSquareFootage > 0
      ? `${formatters.squareFeet(headerSquareFootage)} ${headerFriendlyType}`
      : headerFriendlyType;
  const normalizedOfficeSquareFootage = Math.max(headerSquareFootage || squareFootage || 1, 1);
  const operatingExpensesTotal = typeof displayData.operatingExpenses === 'number' ? displayData.operatingExpenses : 0;
  const camChargesTotal = typeof displayData.camCharges === 'number' ? displayData.camCharges : 0;
  
  // Financial values with formatting
  const totalProjectCost = totals.total_project_cost || 0;
  const constructionTotal = totals.hard_costs || 0;
  const softCostsTotal = totals.soft_costs || 0;
  
  if (DEBUG_EXECUTIVE) {
    // TRACE CONSTRUCTION COST ISSUE
    console.log('=== CONSTRUCTION COST TRACE ===');
    console.log('1. Raw project data:', project);
    console.log('2. Analysis object:', project?.analysis);
    console.log('3. Calculations object:', calculations);
    console.log('4. Totals object:', totals);
    console.log('5. Hard costs value from totals:', totals?.hard_costs);
    console.log('6. DisplayData object:', displayData);
    console.log('7. DisplayData construction cost:', displayData?.constructionCost);
    console.log('8. ConstructionTotal variable:', constructionTotal);
    console.log('9. TotalProjectCost:', totalProjectCost);
    console.log('10. SoftCostsTotal:', softCostsTotal);
    console.log('=== END TRACE ===');
  }
  
  if (DEBUG_EXECUTIVE) {
    // DETAILED REVENUE DEBUG
    console.log('=== DETAILED REVENUE DEBUG ===');
    console.log('Full project prop:', project);
    console.log('project.calculation_data:', project?.calculation_data);
    console.log('project.roi_analysis:', project?.roi_analysis);
    console.log('project.revenue_analysis:', project?.revenue_analysis);
    console.log('analysis object:', analysis);
    console.log('analysis.calculations:', analysis?.calculations);
    console.log('calculations object (merged):', calculations);
    console.log('calculations keys:', Object.keys(calculations || {}));
    
    // Check all possible revenue paths
    console.log('Path checks:');
    console.log('  roi_analysis exists:', !!calculations?.roi_analysis);
    console.log('  financial_metrics exists:', !!calculations?.roi_analysis?.financial_metrics);
    console.log('  annual_revenue in financial_metrics:', calculations?.roi_analysis?.financial_metrics?.annual_revenue);
    console.log('  revenue_analysis exists:', !!calculations?.revenue_analysis);
    console.log('  annual_revenue in revenue_analysis:', calculations?.revenue_analysis?.annual_revenue);
    console.log('  direct annual_revenue:', calculations?.annual_revenue);
    console.log('=== END REVENUE DEBUG ===');
  }
  
  // Get values from backend calculations using correct data paths
  const annualRevenue = 
    calculations?.roi_analysis?.financial_metrics?.annual_revenue ||
    calculations?.revenue_analysis?.annual_revenue ||
    calculations?.ownership_analysis?.revenue_analysis?.annual_revenue ||
    calculations?.financial_metrics?.annual_revenue ||
    calculations?.annual_revenue ||
    displayData?.annualRevenue ||
    0; // No hardcoded value, just 0 if missing
    
  if (DEBUG_EXECUTIVE) {
    console.log('=== FINAL REVENUE VALUES ===');
    console.log('annualRevenue calculated as:', annualRevenue);
    console.log('operatingMargin will be calculated from paths...');
  }
  const noi = 
    calculations?.roi_analysis?.financial_metrics?.net_income ||
    calculations?.revenue_analysis?.net_income ||
    calculations?.ownership_analysis?.revenue_analysis?.net_income ||
    calculations?.return_metrics?.estimated_annual_noi ||
    calculations?.ownership_analysis?.return_metrics?.estimated_annual_noi ||
    displayData?.noi ||
    calculations?.net_income || 
    0;
  
  // Operating margin from backend calculations
  const operatingMargin = 
    calculations?.roi_analysis?.financial_metrics?.operating_margin ||
    calculations?.revenue_analysis?.operating_margin ||
    calculations?.ownership_analysis?.revenue_analysis?.operating_margin ||
    displayData?.operatingMargin ||
    calculations?.operating_margin ||
    0.08; // Default 8% for unknown types
    
  if (DEBUG_EXECUTIVE) {
    console.log('operatingMargin calculated as:', operatingMargin);
    console.log('noi calculated as:', noi);
    console.log('=== END FINAL VALUES ===');
  }
  
  // Revenue Requirements data
  const revenueReq = calculations?.revenue_requirements || 
                     calculations?.ownership_analysis?.revenue_requirements || 
                     null;
  const normalizeRate = (value?: number | null) => {
    if (typeof value !== 'number' || !Number.isFinite(value) || value <= 0) {
      return undefined;
    }
    return value > 1 ? value / 100 : value;
  };
  const targetYieldRate =
    normalizeRate(revenueReq?.target_yield) ||
    normalizeRate(investmentAnalysis?.target_yield) ||
    normalizeRate(calculations?.ownership_analysis?.return_metrics?.target_roi) ||
    normalizeRate((ownership as AnyRecord)?.return_metrics?.target_yield) ||
    normalizeRate((displayData as AnyRecord)?.targetYield) ||
    normalizeRate((displayData as AnyRecord)?.targetYieldPct) ||
    normalizeRate((displayData as AnyRecord)?.yieldTarget) ||
    0.08;
  const irrValue =
    typeof displayData.irr === 'number' && Number.isFinite(displayData.irr)
      ? displayData.irr
      : undefined;
  const normalizedInvestmentDecision = isDealShieldCanonicalStatusActive
    ? decisionStatus
    : backendDecision ?? decisionStatus;
  const irrBelowHurdle =
    normalizedInvestmentDecision === 'NO-GO' &&
    (
      (typeof dscrValue === 'number' && dscrValue < resolvedTargetDscr) ||
      (
        typeof yieldOnCost === 'number' &&
        typeof targetYieldRate === 'number' &&
        Number.isFinite(targetYieldRate) &&
        targetYieldRate > 0 &&
        yieldOnCost < targetYieldRate
      )
    );
  const irrDisplayLabel = irrBelowHurdle ? 'IRR (Below Hurdle)' : 'IRR';
  const irrDisplayValue = irrBelowHurdle
    ? '—'
    : typeof irrValue === 'number'
      ? formatters.percentage(irrValue)
      : '—';
  const irrHelperText = irrBelowHurdle ? 'Not meaningful prior to stabilization' : undefined;
  const requiredNoi = typeof totalProjectCost === 'number' && Number.isFinite(totalProjectCost)
    ? totalProjectCost * targetYieldRate
    : (typeof revenueReq?.required_value === 'number' ? revenueReq.required_value : undefined);
  const currentNoi = typeof noi === 'number' && Number.isFinite(noi)
    ? noi
    : (typeof revenueReq?.actual_net_income === 'number' ? revenueReq.actual_net_income : undefined);
  const noiGap = typeof currentNoi === 'number' && typeof requiredNoi === 'number'
    ? currentNoi - requiredNoi
    : undefined;
  const noiGapPct = typeof noiGap === 'number' && typeof requiredNoi === 'number' && requiredNoi !== 0
    ? (noiGap / requiredNoi) * 100
    : undefined;
  const currentRevenuePerSf =
    typeof annualRevenue === 'number' &&
    Number.isFinite(annualRevenue) &&
    typeof squareFootage === 'number' &&
    squareFootage > 0
      ? annualRevenue / squareFootage
      : (typeof revenueReq?.actual_revenue_per_sf === 'number' ? revenueReq.actual_revenue_per_sf : undefined);
  const requiredRevenuePerSf = (() => {
    if (
      typeof requiredNoi === 'number' &&
      typeof operatingMargin === 'number' &&
      operatingMargin > 0 &&
      typeof squareFootage === 'number' &&
      squareFootage > 0
    ) {
      return (requiredNoi / operatingMargin) / squareFootage;
    }
    if (
      typeof revenueReq?.required_revenue === 'number' &&
      typeof squareFootage === 'number' &&
      squareFootage > 0
    ) {
      return revenueReq.required_revenue / squareFootage;
    }
    if (typeof revenueReq?.required_revenue_per_sf === 'number') {
      return revenueReq.required_revenue_per_sf;
    }
    return undefined;
  })();
  const revenuePerSfGap = typeof currentRevenuePerSf === 'number' && typeof requiredRevenuePerSf === 'number'
    ? currentRevenuePerSf - requiredRevenuePerSf
    : undefined;
  const revenuePerSfGapPct = typeof revenuePerSfGap === 'number' && typeof requiredRevenuePerSf === 'number' && requiredRevenuePerSf !== 0
    ? (revenuePerSfGap / requiredRevenuePerSf) * 100
    : undefined;
  const normalizedFacilityType = (buildingType || '').toUpperCase();
  const showHotelFacilityMetrics =
    normalizedFacilityType === 'HOSPITALITY' || normalizedFacilityType === 'HOTEL';
  const showIndustrialFacilityMetrics =
    normalizedFacilityType === 'INDUSTRIAL' || normalizedFacilityType === 'WAREHOUSE';
  const showRestaurantFacilityMetrics = normalizedFacilityType === 'RESTAURANT';
  const isOfficeProject = isOffice;
  const isHospitalityProject = showHotelFacilityMetrics;
  const isRestaurantProject =
    normalizedFacilityType === 'RESTAURANT' ||
    (buildingType || '').toString().toUpperCase().includes('RESTAURANT');
  const hospitalityRooms =
    typeof facilityMetrics?.rooms === 'number' ? facilityMetrics.rooms : undefined;
  const hospitalityAdr =
    typeof facilityMetrics?.adr === 'number' ? facilityMetrics.adr : undefined;
  const hospitalityOccupancy =
    typeof facilityMetrics?.occupancy === 'number' ? facilityMetrics.occupancy : undefined;
  const hospitalityRevpar =
    typeof facilityMetrics?.revpar === 'number' ? facilityMetrics.revpar : undefined;
  const hospitalityCostPerKey =
    typeof facilityMetrics?.costPerKey === 'number' ? facilityMetrics.costPerKey : undefined;
  const hospitalityAdrText = hospitalityAdr !== undefined ? `$${hospitalityAdr.toFixed(0)}` : 'ADR pending';
  const hospitalityOccupancyText =
    hospitalityOccupancy !== undefined ? `${(hospitalityOccupancy * 100).toFixed(0)}% occupancy` : 'stabilized occupancy';
  const hospitalityRevparText =
    hospitalityRevpar !== undefined ? `$${hospitalityRevpar.toFixed(0)} RevPAR` : 'RevPAR loading';
  const hospitalityMarginText =
    typeof operatingMargin === 'number'
      ? `${(operatingMargin * 100).toFixed(1)}% NOI margin`
      : 'NOI margin pending';
  const restaurantSalesPerSf =
    typeof facilityMetrics?.restaurantSalesPerSf === 'number'
      ? facilityMetrics.restaurantSalesPerSf
      : typeof facilityMetrics?.revenuePerSf === 'number'
        ? facilityMetrics.revenuePerSf
        : undefined;
  const restaurantNoiPerSf =
    typeof facilityMetrics?.restaurantNoiPerSf === 'number'
      ? facilityMetrics.restaurantNoiPerSf
      : typeof facilityMetrics?.noiPerSf === 'number'
        ? facilityMetrics.noiPerSf
        : undefined;
  const restaurantCostPerSf =
    typeof facilityMetrics?.restaurantCostPerSf === 'number'
      ? facilityMetrics.restaurantCostPerSf
      : typeof facilityMetrics?.costPerSf === 'number'
        ? facilityMetrics.costPerSf
        : undefined;
  const hasRestaurantSalesPerSf = typeof restaurantSalesPerSf === 'number' && Number.isFinite(restaurantSalesPerSf);
  const hasRestaurantNoiPerSf = typeof restaurantNoiPerSf === 'number' && Number.isFinite(restaurantNoiPerSf);
  const hasRestaurantCostPerSf = typeof restaurantCostPerSf === 'number' && Number.isFinite(restaurantCostPerSf);
  const salesPerSfText = hasRestaurantSalesPerSf ? formatPerSf(restaurantSalesPerSf) : '—';
  const noiPerSfText = hasRestaurantNoiPerSf ? formatPerSf(restaurantNoiPerSf) : '—';
  const costPerSfText = hasRestaurantCostPerSf ? formatPerSf(restaurantCostPerSf) : '—';
  const officeNoiGapValue =
    typeof requiredNoi === 'number' && typeof currentNoi === 'number'
      ? requiredNoi - currentNoi
      : undefined;
  const officeNoiGapPct =
    typeof officeNoiGapValue === 'number' && typeof requiredNoi === 'number' && requiredNoi !== 0
      ? (officeNoiGapValue / requiredNoi) * 100
      : undefined;
  const officeRentGapValue =
    typeof requiredRevenuePerSf === 'number' && typeof currentRevenuePerSf === 'number'
      ? requiredRevenuePerSf - currentRevenuePerSf
      : undefined;
  const officeRentGapPct =
    typeof officeRentGapValue === 'number' &&
    typeof requiredRevenuePerSf === 'number' &&
    requiredRevenuePerSf !== 0
      ? (officeRentGapValue / requiredRevenuePerSf) * 100
      : undefined;
  const hospitalityRequiredNoiPerKeyValue =
    displayData.requiredNoiPerKey ??
    (isHospitalityProject &&
    typeof requiredNoi === 'number' &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? requiredNoi / hospitalityRooms
      : undefined);
  const hospitalityCurrentNoiPerKeyValue =
    displayData.currentNoiPerKey ??
    (isHospitalityProject &&
    typeof currentNoi === 'number' &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? currentNoi / hospitalityRooms
      : undefined);
  const hospitalityRequiredRevparValue =
    displayData.requiredRevpar ??
    (isHospitalityProject &&
    typeof requiredNoi === 'number' &&
    typeof operatingMargin === 'number' &&
    operatingMargin > 0 &&
    typeof hospitalityRooms === 'number' &&
    hospitalityRooms > 0
      ? (requiredNoi / operatingMargin) / (hospitalityRooms * 365)
      : undefined);
  const fallbackCurrentRevpar =
    hospitalityRevpar !== undefined
      ? hospitalityRevpar
      : isHospitalityProject &&
        typeof hospitalityRooms === 'number' &&
        hospitalityRooms > 0 &&
        typeof annualRevenue === 'number'
        ? annualRevenue / (hospitalityRooms * 365)
        : undefined;
  const hospitalityCurrentRevparValue = displayData.currentRevpar ?? fallbackCurrentRevpar;
  const hospitalityRevparGap =
    typeof hospitalityRequiredRevparValue === 'number' && typeof hospitalityCurrentRevparValue === 'number'
      ? hospitalityRequiredRevparValue - hospitalityCurrentRevparValue
      : undefined;
  const hospitalityRevparGapPct =
    typeof hospitalityRevparGap === 'number' &&
    typeof hospitalityRequiredRevparValue === 'number' &&
    hospitalityRequiredRevparValue !== 0
      ? (hospitalityRevparGap / hospitalityRequiredRevparValue) * 100
      : undefined;
  const feasibilityGapCopy = (() => {
    if (typeof noiGap !== 'number') {
      return 'Feasibility update pending NOI inputs.';
    }
    const gapCurrency = formatters.currency(Math.abs(noiGap));
    const pctText = `${Math.abs(noiGapPct ?? 0).toFixed(1)}%`;
    if (noiGap >= 0) {
      return isRestaurantProject
        ? `Store-level NOI is ${gapCurrency} (${pctText}) above requirement. Keep sales per SF and prime costs on track to preserve that cushion.`
        : `Current NOI is ${gapCurrency} (${pctText}) ahead of requirement.`;
    }
    return isRestaurantProject
      ? `Need ${gapCurrency} (${pctText}) more NOI — meaning higher sales per SF. Pressure-test day-part volume, check size, and prime cost discipline to close the gap.`
      : `Need ${gapCurrency} (${pctText}) more NOI to meet the yield target.`;
  })();

  const isIndustrialProject = (buildingType || '').toLowerCase() === 'industrial';
  const decisionYieldDisplay =
    typeof yieldOnCost === 'number' && Number.isFinite(yieldOnCost)
      ? `${(yieldOnCost * 100).toFixed(1)}%`
      : undefined;
  // Enhanced, context-aware Executive Decision Points
  const decisionBullets: string[] = (() => {
    const bullets: string[] = [];
    if (isHospitalityProject) {
      const basisSnippets: string[] = [];
      if (typeof costPerSFValue === 'number') {
        basisSnippets.push(formatters.costPerSF(costPerSFValue));
      }
      if (typeof facilityMetrics?.costPerKey === 'number') {
        basisSnippets.push(`${formatters.currencyExact(facilityMetrics.costPerKey)} per key`);
      }
      const basisCopy = basisSnippets.length
        ? basisSnippets.join(' | ')
        : 'basis inputs still populating';
      bullets.push(
        `Basis & keys: ${basisCopy}. Benchmark this against recent select-service trades so site, flag, and amenity mix justify the spend.`
      );

      const hotelAdr = typeof facilityMetrics?.adr === 'number' ? `$${facilityMetrics.adr.toFixed(0)}` : 'ADR inputs';
      const hotelOcc =
        typeof facilityMetrics?.occupancy === 'number'
          ? `${(facilityMetrics.occupancy * 100).toFixed(0)}% occupancy`
          : 'stabilized occupancy';
      const hotelRevpar =
        typeof facilityMetrics?.revpar === 'number' ? `$${facilityMetrics.revpar.toFixed(0)} RevPAR` : 'RevPAR inputs';
      const marginText =
        typeof operatingMargin === 'number'
          ? `${(operatingMargin * 100).toFixed(1)}% NOI margin`
          : 'NOI margin pending';

      const capRate = marketCapRateValue;
      const spreadBps = yieldCapSpreadBps;
      const dscrValue = typeof dscr === 'number' ? dscr : undefined;
      const dscrTarget = resolvedTargetDscr;
      const returnParts: string[] = [`ADR ${hotelAdr}`, hotelOcc, hotelRevpar, marginText];
      if (typeof effectiveYield === 'number' && typeof capRate === 'number' && typeof spreadBps === 'number') {
        returnParts.push(
          `yield ${(effectiveYield * 100).toFixed(1)}% vs ${(capRate * 100).toFixed(1)}% cap (${Math.abs(spreadBps).toFixed(0)} bp ${spreadBps >= 0 ? 'above' : 'below'})`
        );
      }
      if (typeof dscrValue === 'number') {
        const delta = dscrValue - dscrTarget;
        returnParts.push(`DSCR ${dscrValue.toFixed(2)}× ${delta >= 0 ? '≥' : '<'} ${dscrTarget.toFixed(2)}×`);
      }
      bullets.push(
        `Returns: ${returnParts.join(' · ')}. Stress ADR/occupancy against the comp set so RevPAR, DSCR, and IRR stay inside the acceptable hotel range.`
      );

      if (typeof softCostRatio === 'number') {
        const softPct = (softCostRatio * 100).toFixed(1);
        bullets.push(
          `Soft costs & reserves: ${softPct}% of total. Confirm franchise fees, management fees, FF&E/PIP reserves, and pre-opening spend align with brand standards so RevPAR doesn't erode.`
        );
      } else {
        bullets.push(
          'Soft costs & reserves: finalize FF&E, franchise, and management agreements to protect RevPAR and lender covenants.'
        );
      }

      return bullets;
    }

    // Non-hospitality branch preserves existing logic
    // 1) Cost positioning - cost/SF vs market benchmarks
    if (
      typeof costPerSFValue === 'number' &&
      typeof marketCostPerSF === 'number' &&
      typeof costPerSFDeltaPct === 'number'
    ) {
      const deltaPct = Math.abs(costPerSFDeltaPct).toFixed(1);
      const direction = costPerSFDeltaPct >= 0 ? 'above' : 'below';
      const implication =
        costPerSFDeltaPct >= 0 ? 'stretching the basis' : 'leaving cushion vs peers';
      bullets.push(
        `Basis risk: ${formatters.costPerSF(costPerSFValue)} sits ${deltaPct}% ${direction} market ${formatters.costPerSF(marketCostPerSF)} — ${implication}.`
      );
    } else if (typeof costPerSFValue === 'number') {
      bullets.push(
        `Basis check: ${formatters.costPerSF(costPerSFValue)} with no peer benchmarks loaded yet.`
      );
    } else {
      bullets.push('Basis check pending: total project cost still reconciling; confirm scope and inputs.');
    }

    // 2) Return positioning - yield vs cap + DSCR vs target
    const capRate = marketCapRateValue;
    const spreadBps = yieldCapSpreadBps;
    const dscrValue = typeof dscr === 'number' ? dscr : undefined;
    const dscrTarget = resolvedTargetDscr;

    if (typeof effectiveYield === 'number' || typeof dscrValue === 'number') {
      const parts: string[] = [];
      if (typeof effectiveYield === 'number' && typeof capRate === 'number' && typeof spreadBps === 'number') {
        const yieldPct = (effectiveYield * 100).toFixed(1);
        const capPct = (capRate * 100).toFixed(1);
        const spreadText = `${Math.abs(spreadBps).toFixed(0)} bp ${spreadBps >= 0 ? 'above' : 'below'}`;
        parts.push(`yield ${yieldPct}% vs ${capPct}% cap (${spreadText})`);
      } else if (typeof effectiveYield === 'number') {
        parts.push(`yield ${(effectiveYield * 100).toFixed(1)}% (cap TBD)`);
      } else if (typeof capRate === 'number') {
        parts.push(`market cap ${(capRate * 100).toFixed(1)}% (yield TBD)`);
      }

      if (typeof dscrValue === 'number') {
        const delta = dscrValue - dscrTarget;
        const meetsTarget = delta >= 0;
        parts.push(
          `DSCR ${dscrValue.toFixed(2)}× ${meetsTarget ? '≥' : '<'} ${dscrTarget.toFixed(2)}× target (${delta >= 0 ? '+' : ''}${delta.toFixed(2)}×)`
        );
      }

      let returnsText = `Returns: ${parts.join('; ')}.`;
      if (isIndustrialProject && isFlexIndustrial) {
        returnsText +=
          ' For flex industrial, this reflects the balance between office and warehouse lease mix, tenant flexibility, and achievable blended rents.';
      } else if (isIndustrialProject) {
        returnsText +=
          ' For industrial, this signals whether the rent roll, dock configuration, and truck flow can clear both equity and lender hurdles.';
      } else {
        returnsText += ' Together these determine whether the project clears both equity and lender hurdles.';
      }
      bullets.push(returnsText);
    } else {
      bullets.push('Returns: yield and DSCR metrics are still populating from the latest underwriting run.');
    }

    // 3) Soft-cost positioning - compare to 18-25% band
    if (typeof softCostRatio === 'number') {
      const softPct = (softCostRatio * 100).toFixed(1);
      let posture = 'within the 18-25% guardrail; balanced owner costs.';
      if (softCostRatio > 0.25) {
        posture = 'high vs the 18-25% band — trim VE or contingency.';
      } else if (softCostRatio < 0.18) {
        posture = 'below the band — confirm allowances and contingency.';
      }
      if (isIndustrialProject) {
        bullets.push(
          `Scope & sitework: ${softPct}% of total — prioritize slab thickness, dock count, ESFR coverage, and truck court design with your GC to keep the budget aligned.`
        );
      } else {
        bullets.push(`Soft costs: ${softPct}% of total — ${posture}`);
      }
    } else {
      bullets.push(
        isIndustrialProject
          ? 'Scope & sitework: awaiting detailed estimates to validate slab, dock, ESFR, and sitework allowances.'
          : 'Soft costs: awaiting latest estimates to benchmark against the 18-25% guidance band.'
      );
    }

    // 4) Optional “what needs to change” bullet when gaps are material
    const yieldShortfallBps =
      typeof spreadBps === 'number' && spreadBps < 0 ? Math.abs(spreadBps) : undefined;
    const dscrShortfall =
      typeof dscrValue === 'number' && dscrValue < dscrTarget ? dscrTarget - dscrValue : undefined;
    const revenueLiftNeeded =
      typeof requiredRevenuePerSf === 'number' &&
      typeof currentRevenuePerSf === 'number' &&
      requiredRevenuePerSf > currentRevenuePerSf
        ? requiredRevenuePerSf - currentRevenuePerSf
        : undefined;
    const noiLiftNeeded =
      typeof requiredNoi === 'number' &&
      typeof currentNoi === 'number' &&
      requiredNoi > currentNoi
        ? requiredNoi - currentNoi
        : undefined;
    const needsRemedy =
      (yieldShortfallBps ?? 0) >= 40 ||
      (dscrShortfall ?? 0) >= 0.05;

    if (needsRemedy) {
      const gapDetails: string[] = [];
      if (yieldShortfallBps) gapDetails.push(`${yieldShortfallBps.toFixed(0)} bp yield shortfall`);
      if (dscrShortfall) gapDetails.push(`${dscrShortfall.toFixed(2)}× DSCR gap`);

      const actionHints: string[] = [];
      if (typeof revenueLiftNeeded === 'number' && revenueLiftNeeded > 0) {
        actionHints.push(`~$${revenueLiftNeeded.toFixed(2)}/SF/yr revenue lift`);
      }
      if (typeof noiLiftNeeded === 'number' && noiLiftNeeded > 0) {
        actionHints.push(`${formatters.currency(noiLiftNeeded)} NOI improvement`);
      }

      const remedyText =
        actionHints.length > 0
          ? actionHints.join(' or ')
          : 'rent growth, scope reductions, or cheaper capital';
      bullets.push(`Adjustments: ${gapDetails.join(' and ')} flagged; plan for ${remedyText} to hit targets.`);
    }

    return bullets;
  })();
  const officeBasisSummary = (() => {
    if (typeof costPerSFValue === 'number') {
      if (typeof marketCostPerSF === 'number' && typeof costPerSFDeltaPct === 'number') {
        const deltaText = `${Math.abs(costPerSFDeltaPct).toFixed(1)}% ${costPerSFDeltaPct >= 0 ? 'above' : 'below'}`;
        return `${formatters.costPerSF(costPerSFValue)} vs ${formatters.costPerSF(marketCostPerSF)} (${deltaText} market)`;
      }
      return `${formatters.costPerSF(costPerSFValue)} (market comps pending)`;
    }
    return 'basis inputs still populating';
  })();
  const officeRentSummary =
    typeof facilityMetrics?.revenuePerSf === 'number'
      ? `$${facilityMetrics.revenuePerSf.toFixed(2)}/SF rent`
      : 'rent inputs loading';
  const officeReturnSummary = (() => {
    const parts: string[] = [];
    if (
      typeof effectiveYield === 'number' &&
      typeof marketCapRateDisplay === 'number' &&
      typeof yieldCapSpreadBps === 'number'
    ) {
      const spreadText = `${Math.abs(yieldCapSpreadBps).toFixed(0)} bp ${yieldCapSpreadBps >= 0 ? 'above' : 'below'}`;
      parts.push(
        `yield ${(effectiveYield * 100).toFixed(1)}% vs ${(marketCapRateDisplay * 100).toFixed(1)}% cap (${spreadText})`
      );
    } else if (typeof effectiveYield === 'number') {
      parts.push(`yield ${(effectiveYield * 100).toFixed(1)}%`);
    }
    if (typeof dscr === 'number') {
      const delta = dscr - resolvedTargetDscr;
      parts.push(`DSCR ${dscr.toFixed(2)}× ${delta >= 0 ? '≥' : '<'} ${resolvedTargetDscr.toFixed(2)}×`);
    }
    return parts.length ? parts.join(' · ') : 'yield and DSCR metrics still populating';
  })();

  // Financial Requirements removed - was only implemented for hospital
  
  // Get department icons based on building type
  const getDepartmentIcon = (deptName: string) => {
    if (deptName.includes('Residential')) return Home;
    if (deptName.includes('Clinical')) return Heart;
    if (deptName.includes('Academic')) return GraduationCap;
    if (deptName.includes('Office')) return Briefcase;
    if (deptName.includes('Common')) return Users;
    if (deptName.includes('Support')) return Headphones;
    if (deptName.includes('Infrastructure')) return Cpu;
    if (deptName.includes('Amenities')) return Shield;
    if (deptName.includes('Athletics')) return Activity;
    return Building2;
  };
  
  // Get department gradient based on index
  const getDepartmentGradient = (index: number) => {
    const gradients = [
      'from-blue-600 to-blue-700',
      'from-green-600 to-green-700',
      'from-purple-600 to-purple-700'
    ];
    return gradients[index % gradients.length];
  };
  
  // Soft costs breakdown from backend
  const softCostCategories = Object.entries(soft_costs?.breakdown || soft_costs || {})
    .filter(([key]) => key !== 'total' && key !== 'soft_cost_percentage')
    .map(([key, value]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      amount: value as number,
      percent: calculations?.soft_costs?.percentages?.[key] || 
               (softCostsTotal > 0 ? ((value as number) / softCostsTotal) * 100 : 0)
    }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5);

  const handleExportPdf = async () => {
    try {
      const projectId =
        project?.project_id ||
        project?.projectId ||
        project?.id;

      if (!projectId) {
        alert('Unable to determine project ID for PDF export.');
        return;
      }

      const response = await pdfService.exportProject(String(projectId));
      const blob = new Blob(
        [response.data],
        { type: response.headers?.['content-type'] || 'application/pdf' }
      );

      const filename = generateExportFilename(project, 'pdf', { includeDate: true });

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export failed:', err);
      alert('Failed to export PDF report. Please try again.');
    }
  };
  const sectionShell = 'rounded-2xl border border-slate-200 bg-white shadow-sm';
  const sectionPadding = 'p-4 sm:p-6';
  const sectionCardClasses = `${sectionShell} ${sectionPadding}`;

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 pb-16 pb-[env(safe-area-inset-bottom)]">
        {/* Executive Investment Dashboard Header */}
        <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-2xl p-6 sm:p-8 text-white shadow-2xl">
        <div className="flex flex-col gap-6 lg:flex-row lg:justify-between">
          <div className="space-y-4">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold break-words">
              {heroTitle}
            </h2>
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs sm:text-sm text-blue-200">
              <span className="flex items-center gap-1.5 min-w-0">
                <MapPin className="h-4 w-4" />
                {location}
              </span>
              <span className="flex items-center gap-1.5 min-w-0">
                <Building className="h-4 w-4" />
                {floors} {floors === 1 ? 'Floor' : 'Floors'}
              </span>
              <span className="flex items-center gap-1.5 min-w-0">
                <Calendar className="h-4 w-4" />
                Ground-Up
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 w-full">
              <button 
                onClick={handleExportPdf}
                className="w-full sm:w-auto px-4 py-2 bg-white/10 backdrop-blur border border-white/20 text-white rounded-lg hover:bg-white/20 transition flex items-center justify-center gap-2"
              >
                <Download className="h-4 w-4" />
                Export PDF
              </button>
                <button
                  onClick={() => setIsScenarioOpen(true)}
                  className="w-full sm:w-auto px-4 py-2 border border-white/30 text-white rounded-lg hover:bg-white/10 transition flex items-center justify-center gap-2"
                >
                  <Target className="h-4 w-4" />
                  Scenario
                </button>
                <button
                  type="button"
                  onClick={() => openTrustPanel('uncertainty')}
                  className="w-full sm:w-auto px-4 py-2 border border-white/0 text-white/80 rounded-lg hover:bg-white/10 transition flex items-center justify-center gap-2 text-sm"
                >
                  <span role="img" aria-hidden="true">🔒</span>
                  Trust &amp; Assumptions
                </button>
            </div>
          </div>
          
          <div className="text-left lg:text-right space-y-2 w-full lg:w-auto">
            <p className="text-xs text-blue-200 uppercase tracking-wider font-medium">TOTAL INVESTMENT REQUIRED</p>
            <p className="text-4xl sm:text-5xl font-bold break-words">{formatters.currency(totalProjectCost)}</p>
            <p className="text-base sm:text-lg text-blue-200">{formatters.costPerSF(totals.cost_per_sf)}</p>
            <button
              type="button"
              onClick={() => openTrustPanel('assumptions')}
              className="text-[11px] font-semibold text-blue-100/80 underline decoration-dotted underline-offset-2 hover:text-white transition"
            >
              Why this estimate
            </button>
            <div className="mt-3 flex flex-wrap gap-2 justify-start lg:justify-end">
              <span
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${decisionStatus === 'GO'
                  ? 'bg-green-500/15 text-green-100 border-green-400/40'
                  : decisionStatus === 'NO-GO'
                    ? 'bg-red-500/15 text-red-100 border-red-400/40'
                    : 'bg-amber-500/15 text-amber-100 border-amber-400/40'}`}
              >
                {decisionStatus === 'GO' ? <CheckCircle className="h-3 w-3" /> : decisionStatus === 'NO-GO' ? <AlertCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                {feasibilityChipLabel}
              </span>
              {isDev && (
                <span className={finishChipClasses} title={hasFinishPayload ? finishChipTooltip : undefined}>
                  {hasFinishPayload ? (
                    <>
                      <span className="font-semibold tracking-wide">DEV • Finish</span>
                      <span className="ml-1">{finishChipDetail}</span>
                    </>
                  ) : (
                    'DEV • Finish: MISSING'
                  )}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 pt-6 mt-6 border-t border-white/20">
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-1 font-medium">CONSTRUCTION</p>
            <p className="text-2xl sm:text-3xl font-bold">{formatters.currency(constructionTotal)}</p>
            <button
              type="button"
              onClick={() => openTrustPanel('conservative')}
              className="mt-1 text-[11px] text-blue-100/80 underline decoration-dotted underline-offset-2 hover:text-white transition"
            >
              How we model construction
            </button>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-1 font-medium">SOFT COSTS</p>
            <p className="text-2xl sm:text-3xl font-bold">{formatters.currency(softCostsTotal)}</p>
            <button
              type="button"
              onClick={() => openTrustPanel('assumptions')}
              className="mt-1 text-[11px] text-blue-100/80 underline decoration-dotted underline-offset-2 hover:text-white transition"
            >
              What’s assumed here
            </button>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-1 font-medium">STABILIZED YIELD (NOI / COST)</p>
            <p className="text-2xl sm:text-3xl font-bold">
              {formatters.percentage(stabilizedYield)}
            </p>
            {typeof yieldOnCost === 'number' && typeof marketCapRateDisplay === 'number' && (
              <p className="text-xs text-blue-200 mt-1">
                vs cap {(marketCapRateDisplay * 100).toFixed(1)}% ({((yieldOnCost - marketCapRateDisplay) * 100).toFixed(1)}% Δ)
              </p>
            )}
            <p className="text-[11px] text-blue-200/80 mt-1">
              Yield on total project cost at stabilization.
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">
              {isMultifamilyProject ? `Debt Lens: DSCR (Target ${dscrTargetDisplay})` : 'DSCR VS TARGET'}
            </p>
            <p className="text-2xl sm:text-3xl font-bold">
              {typeof dscr === 'number' ? `${dscr.toFixed(2)}×` : '—'}
            </p>
            <p className="text-xs text-blue-200 mt-1">
              target {dscrTargetDisplay}
            </p>
            <p className="text-[11px] text-blue-200/80 mt-1">
              Lender sizing based on NOI and annual debt service.
            </p>
          </div>
          <div>
            <p className="text-blue-200 text-xs uppercase tracking-wider mb-2 font-medium">
              {isMultifamilyProject ? 'Stabilized Value Gap' : 'Simple Payback (yrs)'}
            </p>
            <p className="text-2xl sm:text-3xl font-bold">
              {isMultifamilyProject ? stabilizedValueGapDisplay : formatters.years(displayData.paybackPeriod)}
            </p>
          </div>
        </div>
      </div>

      {/* Investment Decision Section with Enhanced Feedback */}
      {/* Patch 12F: legacy static NO-GO banner removed; the dynamic 3-state component below now owns all decision copy. */}
      <section className={`${sectionCardClasses} space-y-4`}>
        {/* Decision Header */}
        <div
          className={`${decisionStatus === 'GO'
            ? 'bg-green-50 border-green-500'
            : decisionStatus === 'NO-GO'
              ? 'bg-red-50 border-red-500'
              : 'bg-amber-50 border-amber-500'} border-l-4 rounded-lg p-6`}
        >
          <div className="flex items-start gap-3">
            {decisionStatus === 'GO' ? (
              <CheckCircle className="h-6 w-6 text-green-600 flex-shrink-0" />
            ) : decisionStatus === 'NO-GO' ? (
              <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
            ) : (
              <Clock className="h-6 w-6 text-amber-600 flex-shrink-0" />
            )}
            <div className="flex-1">
              <h3
                className={`font-bold text-lg ${decisionStatus === 'GO'
                  ? 'text-green-900'
                  : decisionStatus === 'NO-GO'
                    ? 'text-red-900'
                    : 'text-amber-900'}`}
              >
                Investment Decision: {decisionStatusLabel}
              </h3>
              {isDealShieldCanonicalStatusActive && (
                <p className="mt-1 text-xs text-slate-600">
                  Policy source: {decisionStatusSource ?? 'dealshield_policy_v1'}
                  {decisionPolicyId ? ` (${decisionPolicyId})` : ''}
                  {decisionReasonCode ? ` · reason: ${decisionReasonCode}` : ''}
                </p>
              )}
              <button
                type="button"
                onClick={() => openTrustPanel('lens')}
                className="mt-1 text-xs font-semibold text-slate-600 underline decoration-dotted underline-offset-2 hover:text-slate-900 transition"
              >
                How to interpret this recommendation
              </button>
              {isHospitalityProject ? (
                <>
                  <p className={decisionBodyClass}>
                    Hotel clears underwriting at {hospitalityAdrText}, {hospitalityOccupancyText}, and {hospitalityRevparText}, generating {hospitalityMarginText} to support the flagged room count and debt sizing.
                  </p>
                  <p className="mt-1 text-xs text-slate-600">
                    Hospitality memo: validate ADR and RevPAR against comp sets, keep DSCR comfortably above lender hotel hurdles, and confirm franchise, management, and FF&E reserves stay in sync with brand requirements.
                  </p>
                  {decisionReasonText && (
                    <p className="mt-2 text-xs text-slate-600">
                      Analyst context: {decisionReasonText}
                    </p>
                  )}
                </>
              ) : (
                <>
                  {isOffice ? (
                    <>
                      <p className="text-sm text-slate-700">
                        Office deal currently underperforms Class A underwriting targets. With current rent levels, occupancy, and TI/LC load, stabilized NOI is not sufficient to clear both equity and lender hurdles.
                      </p>
                      <p className="mt-1 text-sm text-slate-700">
                        Yield on cost and DSCR here should be read in the context of lease-up risk, tenant credit, and renewal probabilities. Use this view to test whether the rent and occupancy story is strong enough for this basis.
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Analyzer note: Focus first on achievable rent per SF, realistic stabilized occupancy, and the average TI/LC burden for this submarket. Debt sizing and return metrics will follow from the rent roll quality. If the gap is large, re-scope the project, lower hard costs, or revisit the target tenant mix.
                      </p>
                      {decisionReasonText && (
                        <p className="mt-2 text-xs text-slate-600">
                          Additional analyzer note: {decisionReasonText}
                        </p>
                      )}
                    </>
                  ) : (
                    <>
                      <p className={decisionBodyClass}>
                        {decisionCopy.body}
                      </p>
                      {decisionCopy.detail && (
                        <p className={decisionDetailClass}>
                          {decisionCopy.detail}
                        </p>
                      )}
                      {decisionReasonText && (
                        <p className="mt-2 text-xs text-slate-600">
                          Analyzer note: {decisionReasonText}
                        </p>
                      )}
                    </>
                  )}
                </>
              )}
              {hasDebt &&
                typeof dscr === 'number' &&
                Number.isFinite(dscr) &&
                dscr < resolvedTargetDscr && (
                  <p className="text-xs md:text-sm opacity-80 mt-0.5 text-red-700">
                    DSCR {dscr.toFixed(2)}× vs target {resolvedTargetDscr.toFixed(2)}×: coverage is below lender sizing.
                  </p>
                )}
              {typeof yieldOnCost === 'number' && yieldOnCost > 0 && (
                <p className="text-xs md:text-sm opacity-90 mt-0.5">
                  Yield on cost of {(yieldOnCost * 100).toFixed(1)}%
                  {typeof marketCapRateDisplay === 'number' && (
                    <> vs market cap {(marketCapRateDisplay * 100).toFixed(1)}%</>
                  )}
                  {typeof capRateSpreadBps === 'number' && (
                    <> ({capRateSpreadBps >= 0 ? '+' : ''}{(capRateSpreadBps / 100).toFixed(1)} bp)</>
                  )}
                </p>
              )}
            </div>
          </div>
        </div>
        
        {/* Metrics Table */}
        {displayData.metricsTable && displayData.metricsTable.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
              <h4 className="font-semibold text-gray-900">Investment Criteria Assessment</h4>
            </div>
            <div className="hidden md:block">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Metric</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Required</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {displayData.metricsTable.map((metric, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{metric.metric}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{metric.current}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">{metric.required}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {metric.status === 'pass' ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" /> Pass
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <XCircle className="h-3 w-3 mr-1" /> Fail
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="md:hidden p-4 space-y-4">
              {displayData.metricsTable.map((metric, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-gray-900">{metric.metric}</span>
                    {metric.status === 'pass' ? (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <CheckCircle className="h-3 w-3 mr-1" /> Pass
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <XCircle className="h-3 w-3 mr-1" /> Fail
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-700">
                    <p className="flex justify-between"><span>Current:</span><span className="font-medium">{metric.current}</span></p>
                    <p className="flex justify-between"><span>Required:</span><span className="font-medium text-gray-600">{metric.required}</span></p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Actionable Improvements for NO-GO */}
        {decisionStatus === 'NO-GO' && displayData.failedCriteria && displayData.failedCriteria.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                How to Make This Project Feasible
              </h4>
              <p className="text-sm text-gray-600 mt-1">Specific actions to meet investment criteria</p>
            </div>
            <div className="p-6 space-y-4">
              {displayData.failedCriteria.map((failure, idx) => (
                <div key={idx} className="flex gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                      {idx + 1}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-baseline justify-between mb-2">
                      <span className="font-semibold text-gray-900">{failure.metric}</span>
                      <span className="text-sm text-red-600">Gap: {failure.gap}</span>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{failure.fix}</p>
                    <div className="flex gap-4 text-xs text-gray-500">
                      <span>Current: {failure.current}</span>
                      <span>→</span>
                      <span>Required: {failure.required}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
            
            {/* Legacy improvements display - now handled above */}
            {false && decisionStatus === 'NO-GO' && displayData.improvementsNeeded && displayData.improvementsNeeded.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-red-200">
                <h4 className="font-semibold text-red-900 mb-3 flex items-center gap-2">
                  <AlertCircle className="h-4 w-4" />
                  Required Improvements:
                </h4>
                <div className="space-y-3">
                  {displayData.improvementsNeeded.map((improvement, idx) => (
                    <div key={idx} className="border-l-2 border-red-300 pl-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-gray-900">{improvement.metric}</span>
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-red-600">Current: {formatters.formatMetricValue(improvement.current, improvement.metric)}</span>
                          <span className="text-gray-400">→</span>
                          <span className="text-green-600">Required: {formatters.formatMetricValue(improvement.required, improvement.metric)}</span>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600">{improvement.suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Display suggestions if NO-GO */}
            {decisionStatus === 'NO-GO' && displayData.suggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white rounded-lg border border-amber-200">
                <h4 className="font-semibold text-amber-900 mb-2 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" />
                  Additional Optimization Strategies:
                </h4>
                <ul className="space-y-2">
                  {displayData.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-amber-600 mt-0.5">•</span>
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </li>
                  ))}
                </ul>
                
                {displayData.requiredRent > 0 && (
                  <div className="mt-3 pt-3 border-t border-amber-200">
                    <p className="text-sm text-gray-600">
                      Required rent for 8% return: <strong>{formatters.monthlyRent(displayData.requiredRent)}</strong>
                    </p>
                  </div>
                )}
              </div>
            )}
            
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-6 mt-3">
              <span className="flex items-center gap-2">
                <span className={`w-2 h-2 ${displayData.roi >= 0.08 ? 'bg-green-500' : 'bg-red-500'} rounded-full`}></span>
                <span className="text-sm">ROI: <strong>{formatters.percentage(displayData.roi)}</strong></span>
              </span>
            <span className="flex items-center gap-2">
              <span className={`w-2 h-2 ${displayData.dscr >= 1.25 ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
              <span className="text-sm">DSCR: <strong>{formatters.multiplier(displayData.dscr)}</strong></span>
            </span>
            <span className="flex items-center gap-2">
              <span className={`w-2 h-2 ${irrDisplayValue !== '—' ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
              <span className="text-sm">
                {irrDisplayLabel}: <strong>{irrDisplayValue}</strong>
                {irrHelperText ? <span className="ml-2 text-xs text-gray-500">{irrHelperText}</span> : null}
              </span>
            </span>
            <span className="flex items-center gap-2">
              <span className={`w-2 h-2 ${displayData.paybackPeriod <= 20 ? 'bg-green-500' : 'bg-amber-500'} rounded-full`}></span>
              <span className="text-sm">Payback: <strong>{formatters.years(displayData.paybackPeriod)}</strong></span>
            </span>
          </div>
      </section>

      {/* Three Key Metrics Cards */}
      <section className={sectionCardClasses}>
        <div className="grid grid-cols-1 gap-6">
        {/* Revenue Projections */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-green-500 to-green-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-green-50 rounded-lg">
                <DollarSign className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Revenue Projections</h3>
            </div>
            <p className="text-3xl font-bold text-gray-900">
              {formatters.currency(annualRevenue)}
            </p>
            <p className="text-sm text-gray-500 mb-4">Annual Revenue</p>
            {isFlexIndustrial ? (
              <p className="text-xs text-gray-500 mb-4 -mt-2">
                Includes blended rents across warehouse and office/showroom space.
              </p>
            ) : null}
            <div className="space-y-2 pt-4 border-t">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Operating Margin</span>
                <span className="font-bold">{formatters.percentage(operatingMargin)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Net Income</span>
                <span className="font-bold">{formatters.currency(noi)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Facility Metrics */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-blue-500 to-blue-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Building className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Facility Metrics</h3>
            </div>
            {showHotelFacilityMetrics ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs text-slate-700">
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Rooms
                  </div>
                  <div className="text-2xl font-semibold">
                    {typeof facilityMetrics?.rooms === 'number'
                      ? facilityMetrics.rooms.toLocaleString()
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Keys in the hotel</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    ADR
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.adr === 'number'
                      ? `$${facilityMetrics.adr.toFixed(0)}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Average daily rate</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Occupancy
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.occupancy === 'number'
                      ? `${(facilityMetrics.occupancy * 100).toFixed(0)}%`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Stabilized occupancy</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    RevPAR
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.revpar === 'number'
                      ? `$${facilityMetrics.revpar.toFixed(0)}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Revenue per available room</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1 md:col-span-2">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Cost per Key
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.costPerKey === 'number'
                      ? `$${facilityMetrics.costPerKey.toLocaleString(undefined, { maximumFractionDigits: 0 })}`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total project cost per room</div>
                </div>
              </div>
            ) : showIndustrialFacilityMetrics ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs text-slate-700">
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Building Size
                  </div>
                  <div className="text-2xl font-semibold">
                    {typeof facilityMetrics?.buildingSize === 'number'
                      ? `${facilityMetrics.buildingSize.toLocaleString()} SF`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total gross building area</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Cost per SF
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.costPerSf === 'number'
                      ? formatters.currencyExact(facilityMetrics.costPerSf)
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total project cost divided by SF</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Revenue & NOI per SF
                  </div>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">Revenue</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.revenuePerSf === 'number'
                          ? `$${facilityMetrics.revenuePerSf.toFixed(1)} /SF`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">NOI</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.noiPerSf === 'number'
                          ? `$${facilityMetrics.noiPerSf.toFixed(1)} /SF`
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : showRestaurantFacilityMetrics ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs text-slate-700">
                {/* --- SALES PER SF --- */}
                <div className="rounded-2xl border border-slate-100 bg-white/90 p-5 shadow-md shadow-slate-100/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                      Sales
                    </div>
                    <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-500/90 border border-slate-200 bg-slate-50 rounded-full px-2 py-[2px] shadow-sm">
                      /SF
                    </div>
                  </div>
                  <div className="text-3xl font-semibold leading-none font-mono tabular-nums">
                    {salesPerSfText}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Annual revenue divided by footprint
                  </div>
                </div>

                {/* --- NOI PER SF --- */}
                <div className="rounded-2xl border border-slate-100 bg-white/90 p-5 shadow-md shadow-slate-100/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                      NOI
                    </div>
                    <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-500/90 border border-slate-200 bg-slate-50 rounded-full px-2 py-[2px] shadow-sm">
                      /SF
                    </div>
                  </div>
                  <div className="text-3xl font-semibold leading-none font-mono tabular-nums">
                    {noiPerSfText}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Net income generated per square foot
                  </div>
                </div>

                {/* --- ALL-IN COST PER SF --- */}
                <div className="rounded-2xl border border-slate-100 bg-white/90 p-5 shadow-md shadow-slate-100/80 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                      All-in cost
                    </div>
                    <div className="text-[10px] font-semibold uppercase tracking-wide text-slate-500/90 border border-slate-200 bg-slate-50 rounded-full px-2 py-[2px] shadow-sm">
                      /SF
                    </div>
                  </div>
                  <div className="text-3xl font-semibold leading-none font-mono tabular-nums">
                    {costPerSfText}
                  </div>
                  <div className="text-[11px] text-slate-500">
                    Total project cost divided by SF
                  </div>
                </div>
              </div>
            ) : isOfficeProject ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-xs text-slate-700">
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Building Size
                  </div>
                  <div className="text-2xl font-semibold">
                    {typeof facilityMetrics?.buildingSize === 'number'
                      ? `${facilityMetrics.buildingSize.toLocaleString()} SF`
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total rentable area</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Cost per SF
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof facilityMetrics?.costPerSf === 'number'
                      ? formatters.currencyExact(facilityMetrics.costPerSf)
                      : '—'}
                  </div>
                  <div className="text-[11px] text-slate-500">Total project cost divided by SF</div>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-md shadow-slate-100 space-y-1">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                    Rent & NOI per SF
                  </div>
                  <div className="mt-2 space-y-1">
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">Rent</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.revenuePerSf === 'number'
                          ? `$${facilityMetrics.revenuePerSf.toFixed(2)}`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <span className="text-[11px] text-slate-500">NOI</span>
                      <span className="text-sm font-semibold">
                        {typeof facilityMetrics?.noiPerSf === 'number'
                          ? `$${facilityMetrics.noiPerSf.toFixed(2)}`
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : isOffice ? (
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="rounded-xl bg-slate-50 p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Required NOI (target yield)
                    </div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">
                      {formatters.currency(requiredNoi ?? revenueReq.required_value)}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Current NOI:{' '}
                      <span className="font-semibold">
                        {formatters.currency(currentNoi ?? revenueReq.market_value)}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Gap:{' '}
                      {typeof officeNoiGapValue === 'number' ? (
                        <>
                          {formatters.currency(officeNoiGapValue)}{' '}
                          {typeof officeNoiGapPct === 'number' ? (
                            <>({officeNoiGapPct.toFixed(1)}%)</>
                          ) : null}
                        </>
                      ) : (
                        '—'
                      )}
                    </div>
                    <div className="mt-3 text-xs text-slate-500 space-y-1">
                      <div>
                        Required NOI per SF:{' '}
                        <span className="font-semibold">
                          {typeof revenueRequired.requiredNoiPerSf === 'number'
                            ? `$${revenueRequired.requiredNoiPerSf.toFixed(2)}`
                            : '—'}
                        </span>
                      </div>
                      <div>
                        Current NOI per SF:{' '}
                        <span className="font-semibold">
                          {typeof revenueRequired.currentNoiPerSf === 'number'
                            ? `$${revenueRequired.currentNoiPerSf.toFixed(2)}`
                            : '—'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-4">
                    <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Rent per SF vs Target
                    </div>
                    <div className="text-2xl font-bold text-slate-900 mt-1">
                      {typeof requiredRevenuePerSf === 'number'
                        ? `$${requiredRevenuePerSf.toFixed(0)}`
                        : '—'}
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Current rent per SF:{' '}
                      <span className="font-semibold">
                        {typeof currentRevenuePerSf === 'number'
                          ? `$${currentRevenuePerSf.toFixed(0)}`
                          : '—'}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 mt-1">
                      Rent gap:{' '}
                      {typeof officeRentGapValue === 'number' ? (
                        <>
                          {`$${officeRentGapValue.toFixed(0)}`}{' '}
                          {typeof officeRentGapPct === 'number' ? (
                            <>({officeRentGapPct.toFixed(1)}%)</>
                          ) : null}
                        </>
                      ) : (
                        '—'
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-xs text-slate-500">
                  For office, focus on whether the required rent and NOI per SF are achievable given comp-set leases and realistic TI/LC packages. If required rent per SF is materially above market, the leasing and amenity plan must justify that premium to investors and lenders.
                </div>
              </div>
            ) : (
              <>
                <p className="text-3xl font-bold text-gray-900">{formatters.units(displayData.unitCount)}</p>
                <p className="text-sm text-gray-500 mb-4">{unitLabel}</p>
                <div className="space-y-2 pt-4 border-t">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Cost per {unitType}</span>
                    <span className="font-bold">{formatters.currencyExact(displayData.costPerUnit)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Revenue per {unitType}</span>
                    <span className="font-bold">{formatters.currency(displayData.revenuePerUnit)}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Investment Mix */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="h-1 bg-gradient-to-r from-purple-500 to-purple-600"></div>
          <div className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 bg-purple-50 rounded-lg">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Investment Mix</h3>
            </div>
            <div className="space-y-3 mt-6">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Construction</span>
                  <span className="font-bold">{formatters.percentage(constructionTotal / totalProjectCost)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(constructionTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">Soft Costs</span>
                  <span className="font-bold">{formatters.percentage(softCostsTotal / totalProjectCost)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${(softCostsTotal / totalProjectCost) * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Investment Mix */}
      </div>
      </section>

      {/* Department Cost Allocation */}
      {displayData.departments.length > 0 && (
        <section className={`${sectionCardClasses} space-y-6`}>
          <h3 className="text-xl font-bold text-gray-900 mb-6">Department Cost Allocation</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {displayData.departments.map((dept, idx) => {
              const Icon = getDepartmentIcon(dept.name);
              const gradient = getDepartmentGradient(idx);
              return (
                <div key={idx} className={`bg-gradient-to-br ${gradient} rounded-xl p-6 text-white shadow-xl`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="p-3 bg-white/20 rounded-lg backdrop-blur">
                      <Icon className="h-6 w-6" />
                    </div>
                    <div className="text-right">
                      <p className="text-4xl font-bold">{formatters.percentage(dept.percent)}</p>
                      <p className="text-sm text-white/80">of facility</p>
                    </div>
                  </div>
                  
                  <h4 className="text-lg font-bold mb-1">{dept.name}</h4>
                  <p className="text-3xl font-bold mb-4">{formatters.currency(dept.amount)}</p>
                  
                  <div className="space-y-2 pt-4 border-t border-white/20">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/80">Square Footage</span>
                      <span className="font-medium">{formatters.squareFeet(dept.square_footage)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-white/80">Cost per SF</span>
                      <span className="font-medium">{formatters.costPerSF(dept.cost_per_sf)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Target Yield Prescription */}
      <section className={`${sectionShell} shadow-lg shadow-slate-200/50`}>
        <div className="px-4 py-4 sm:px-6 sm:py-5 border-b border-slate-100">
          <div className="inline-flex items-center text-[11px] font-semibold uppercase mb-4 px-3 py-1 rounded-full bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 tracking-wide shadow-sm border border-indigo-200/50">
            Prescriptive Playbook
          </div>
          <h3 className="text-xl font-semibold text-slate-900">What It Would Take to Hit Target Yield</h3>
          <p className="text-sm text-slate-500 mt-1">See how much NOI or cost needs to move for this project to hit its underwriting hurdle.</p>
        </div>
        <div className="p-4 sm:p-6 md:p-8">
        {isOffice ? (
          <div className="space-y-3 text-sm text-slate-700">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              How to move this office deal toward the target yield
            </p>

            <div>
              <div className="font-semibold text-slate-800">
                1. Tighten the rent &amp; occupancy story
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Underwrite a rent per SF and stabilized occupancy that reflect the actual Class A comp set. If the model assumes above-market rent or unrealistic absorption, either dial those inputs back or invest in a tenant mix and amenity package that can sustain the premium.
              </div>
            </div>

            <div>
              <div className="font-semibold text-slate-800">
                2. Re-scope TI and leasing economics
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Tenant improvements and leasing commissions are often the biggest drag on office NOI. Consider spec suites, staggered TI packages, or shorter lease terms to reduce upfront burn while keeping rents achievable for tenants.
              </div>
            </div>

            <div>
              <div className="font-semibold text-slate-800">
                3. Value-engineer the building &amp; OpEx
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Revisit shell vs. build-out scope, amenity spend, and parking strategy. Pressure-test OpEx per SF against similar towers and explore service contracts or systems that keep long-term operating costs contained without undercutting tenant experience.
              </div>
            </div>
          </div>
        ) : isHospitalityProject ? (
          <div className="space-y-3 text-sm text-slate-700">
            <p className="text-xs uppercase tracking-wide text-slate-400">
              How to move this hotel toward the target yield
            </p>

            <div>
              <div className="font-semibold text-slate-800">
                1. Optimize ADR and RevPAR
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Use dynamic pricing and channel mix to close the RevPAR gap. Focus on rate integrity during peak periods and carefully
                discount only shoulder nights and weak segments. Benchmark ADR and RevPAR index against the comp set rather than chasing
                occupancy alone.
              </div>
            </div>

            <div>
              <div className="font-semibold text-slate-800">
                2. Build a defensible occupancy plan
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Layer in corporate, group, and transient demand to support the required stabilized occupancy. Secure key accounts and repeat
                business, and align sales activity with the events calendar so shoulder nights and weekends are protected.
              </div>
            </div>

            <div>
              <div className="font-semibold text-slate-800">
                3. Tighten operating and fee load
              </div>
              <div className="mt-1 text-xs text-slate-600">
                Review staffing ratios, outsource vs. in-house services, and franchise/management fee structure. Confirm FF&amp;E and PIP
                reserves are adequate so the property can maintain rate and RevPAR over the hold period without unexpected capital calls.
              </div>
            </div>
          </div>
        ) : isRestaurantProject ? (
          <div className="grid gap-6 md:gap-8 sm:grid-cols-2 lg:grid-cols-3 text-sm text-slate-700">
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Path 1 · Increase Sales per SF
              </p>
              <div className="text-slate-900 font-medium">
                Grow day-part mix and digital channels.
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Push more volume through the box by improving lunch and dinner balance, expanding takeout, delivery, and kiosk ordering,
                and using menu engineering plus upsells to lift the average check size.
              </p>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Path 2 · Tighten Food &amp; Labor Costs
              </p>
              <div className="text-slate-900 font-medium">
                Keep prime costs in the 60–65% range.
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Reduce waste, tighten portions, negotiate vendor pricing, and optimize staffing schedules so food plus labor stay near
                60–65% of sales and can absorb rent, utilities, and operating costs.
              </p>
            </div>

            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                Path 3 · Right-size TI, Kitchen &amp; Occupancy Cost
              </p>
              <div className="text-slate-900 font-medium">
                Protect NOI by trimming non-essential spend.
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">
                Value-engineer finishes and kitchen scope that do not change the guest experience. Standardize layouts, reuse prototypes, and
                stress-test base rent plus NNN charges against projected sales in both upside and downside cases.
              </p>
            </div>
          </div>
        ) : (
        (() => {
          const formatMoney = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? formatters.currency(value) : '—';
            const formatPercent = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : '—';
            const formatMultiplier = (value?: number) =>
              typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(2)}x` : '—';

            const totalCostValue =
              typeof totalProjectCost === 'number' && Number.isFinite(totalProjectCost) && totalProjectCost > 0
                ? totalProjectCost
                : undefined;
            const currentNoiValue = typeof currentNoi === 'number' && Number.isFinite(currentNoi) ? currentNoi : undefined;
            const requiredNoiValue = typeof requiredNoi === 'number' && Number.isFinite(requiredNoi) ? requiredNoi : undefined;
            const currentYieldValue = typeof stabilizedYield === 'number' && Number.isFinite(stabilizedYield) ? stabilizedYield : undefined;
            const targetYieldValue =
              typeof targetYieldRate === 'number' && Number.isFinite(targetYieldRate) && targetYieldRate > 0 ? targetYieldRate : undefined;
            const dscrValue = typeof dscr === 'number' && Number.isFinite(dscr) ? dscr : undefined;
            const targetDscrValue =
              typeof resolvedTargetDscr === 'number' && Number.isFinite(resolvedTargetDscr) ? resolvedTargetDscr : undefined;

            const noiShortfall =
              typeof requiredNoiValue === 'number' && typeof currentNoiValue === 'number'
                ? requiredNoiValue - currentNoiValue
                : undefined;
            const noiShortfallPct =
              typeof noiShortfall === 'number' && typeof currentNoiValue === 'number' && currentNoiValue !== 0
                ? noiShortfall / currentNoiValue
                : undefined;

            const maxCostForTarget =
              typeof currentNoiValue === 'number' &&
              typeof targetYieldValue === 'number' &&
              targetYieldValue > 0
                ? currentNoiValue / targetYieldValue
                : undefined;
            const costReductionNeeded =
              typeof totalCostValue === 'number' && typeof maxCostForTarget === 'number'
                ? totalCostValue - maxCostForTarget
                : undefined;

            const gapBps =
              typeof targetYieldValue === 'number' && typeof currentYieldValue === 'number'
                ? Math.round((targetYieldValue - currentYieldValue) * 10000)
                : undefined;

            let yieldSummary = 'Yield-on-cost data is still loading.';
            if (typeof currentYieldValue === 'number' && typeof targetYieldValue === 'number') {
              const direction =
                typeof gapBps === 'number'
                  ? gapBps > 0
                    ? `${Math.abs(gapBps)} bps below target`
                    : `${Math.abs(gapBps)} bps above target`
                  : null;
              yieldSummary = `Current yield is ${formatPercent(currentYieldValue)} vs ${formatPercent(targetYieldValue)}${
                direction ? ` (${direction})` : ''
              }.`;
            }

            let dscrSummary = 'Debt coverage metrics are still loading. Use lender sizing once available.';
            if (typeof dscrValue === 'number' && typeof targetDscrValue === 'number') {
              dscrSummary =
                dscrValue >= targetDscrValue
                  ? `Debt coverage is solid at ${formatMultiplier(dscrValue)} vs ${formatMultiplier(targetDscrValue)} — equity returns are the main limiter.`
                  : `Debt coverage is ${formatMultiplier(dscrValue)} vs ${formatMultiplier(
                      targetDscrValue
                    )}; expect lenders to require NOI lift, lower leverage, or added credit support.`;
            } else if (typeof dscrValue === 'number') {
              dscrSummary = `Debt coverage is ${formatMultiplier(dscrValue)}. Target DSCR not provided.`;
            }

          return (
              <div className="grid gap-6 md:gap-8 sm:grid-cols-2 lg:grid-cols-3 text-sm text-slate-700">
                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Path 1 · Increase NOI</p>
                    <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-2 shadow-md shadow-slate-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Current NOI</span>
                      <span className="font-semibold text-slate-900">{formatMoney(currentNoiValue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">NOI needed</span>
                      <span className="font-semibold text-slate-900">{formatMoney(requiredNoiValue)}</span>
                    </div>
                    <p className="text-[12px] text-slate-500 leading-relaxed border-t border-slate-100 pt-2">
                      {typeof noiShortfall === 'number' && noiShortfall > 0 ? (
                        <>
                          Increase annual NOI by <span className="font-semibold text-slate-900">{formatMoney(noiShortfall)}</span>
                          {typeof noiShortfallPct === 'number' && Number.isFinite(noiShortfallPct)
                            ? ` (${(noiShortfallPct * 100).toFixed(1)}% lift)`
                            : ''}{' '}
                          to reach {formatPercent(targetYieldValue)}.
                        </>
                      ) : requiredNoiValue && currentNoiValue ? (
                        'Current NOI already meets the target yield — keep this level of performance through stabilization.'
                      ) : (
                        'Once NOI and target yield metrics load, this path highlights the lift required.'
                      )}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Path 2 · Reduce Project Cost</p>
                    <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-2 shadow-md shadow-slate-100">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Current total cost</span>
                      <span className="font-semibold text-slate-900">{formatMoney(totalCostValue)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Max cost supported</span>
                      <span className="font-semibold text-slate-900">{formatMoney(maxCostForTarget)}</span>
                    </div>
                    <p className="text-[12px] text-slate-500 leading-relaxed border-t border-slate-100 pt-2">
                      {typeof costReductionNeeded === 'number' && costReductionNeeded > 0 ? (
                        <>
                          Value engineer roughly <span className="font-semibold text-slate-900">{formatMoney(costReductionNeeded)}</span> from the budget or
                          source grants/equity to close the gap.
                        </>
                      ) : totalCostValue && maxCostForTarget ? (
                        'Today’s cost basis already supports the target yield at current NOI.'
                      ) : (
                        'Cost stack guidance appears once current NOI and target yield inputs are ready.'
                      )}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <p className="text-xs font-semibold text-slate-500 uppercase tracking-[0.2em]">Summary & Perspective</p>
                  <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3 shadow-md shadow-slate-100">
                    <p className="text-sm text-slate-600 leading-relaxed">{yieldSummary}</p>
                    <p className="text-sm text-slate-600 leading-relaxed">{dscrSummary}</p>
                    <p className="text-sm text-slate-500 leading-relaxed">
                      Use this as the talking track for lease-up assumptions, cost value engineering, or capital-stack tweaks.
                    </p>
                  </div>
                </div>
              </div>
          );
        })()
        )}
        </div>
      </section>

      {/* Revenue Requirements Card */}
      {revenueReq && (
        <section className={`${sectionShell} overflow-hidden`}>
          <div className="bg-gradient-to-r from-emerald-500 to-teal-600 px-4 py-4 sm:px-6">
            <h3 className="text-lg font-bold text-white">Revenue Required to Hit Target Yield</h3>
            <p className="text-sm text-emerald-100">
              {isHospitalityProject
                ? 'Benchmark NOI per key and RevPAR against the brand’s underwriting targets.'
                : isRestaurantProject
                  ? 'Compare required NOI and sales per SF against current performance. Use this to see how far store-level sales would need to move to hit the underwriting hurdle.'
                  : 'Compare required NOI and revenue per SF against current performance.'}
            </p>
          </div>
          <div className="p-4 sm:p-6 space-y-5">
            {isHospitalityProject ? (
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Required NOI (target yield)</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatters.currency(requiredNoi ?? revenueReq.required_value)}
                  </p>
                  <p className="text-xs text-gray-600 mt-2">
                    Current NOI:{' '}
                    <span className="font-semibold text-gray-900">
                      {formatters.currency(currentNoi ?? revenueReq.market_value)}
                    </span>
                  </p>
                  {typeof noiGap === 'number' && (
                    <p className={`text-xs mt-1 ${noiGap >= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                      Gap: {formatters.currency(Math.abs(noiGap))} ({Math.abs(noiGapPct || 0).toFixed(1)}%)&nbsp;
                      {noiGap >= 0 ? 'surplus vs target' : 'shortfall vs target'}
                    </p>
                  )}
                  <div className="mt-3 text-xs text-gray-600 space-y-1">
                    <div>
                      Required NOI per key:{' '}
                      <span className="font-semibold text-gray-900">
                        {typeof hospitalityRequiredNoiPerKeyValue === 'number'
                          ? formatters.currency(hospitalityRequiredNoiPerKeyValue)
                          : '—'}
                      </span>
                    </div>
                    <div>
                      Current NOI per key:{' '}
                      <span className="font-semibold text-gray-900">
                        {typeof hospitalityCurrentNoiPerKeyValue === 'number'
                          ? formatters.currency(hospitalityCurrentNoiPerKeyValue)
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-900/80 mb-1">Required RevPAR</p>
                  <p className="text-2xl font-bold text-blue-700">
                    {typeof hospitalityRequiredRevparValue === 'number'
                      ? `$${hospitalityRequiredRevparValue.toFixed(0)}`
                      : '—'}
                  </p>
                  <p className="text-xs text-blue-900/80 mt-2">
                    Current RevPAR:{' '}
                    <span className="font-semibold">
                      {typeof hospitalityCurrentRevparValue === 'number'
                        ? `$${hospitalityCurrentRevparValue.toFixed(0)}`
                        : '—'}
                    </span>
                  </p>
                  {typeof hospitalityRevparGap === 'number' && (
                    <p className={`text-xs mt-1 ${hospitalityRevparGap <= 0 ? 'text-green-700' : 'text-amber-600'}`}>
                      Gap: ${Math.abs(hospitalityRevparGap).toFixed(0)} ({Math.abs(hospitalityRevparGapPct || 0).toFixed(1)}%)&nbsp;
                      {hospitalityRevparGap <= 0 ? 'above requirement' : 'needed to reach target'}
                    </p>
                  )}
                  <div className="mt-2 space-y-1 text-xs text-slate-500">
                    <div className="flex items-baseline justify-between">
                      <span>Implied ADR needed</span>
                      <span className="font-semibold">
                        {typeof revenueRequired.impliedAdrForTargetRevpar === 'number'
                          ? `$${revenueRequired.impliedAdrForTargetRevpar.toFixed(0)}`
                          : '—'}
                      </span>
                    </div>
                    <div className="flex items-baseline justify-between">
                      <span>Implied occupancy needed</span>
                      <span className="font-semibold">
                        {typeof revenueRequired.impliedOccupancyForTargetRevpar === 'number'
                          ? `${(revenueRequired.impliedOccupancyForTargetRevpar * 100).toFixed(0)}%`
                          : '—'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
            <div className="flex items-center justify-between mb-3">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Feasibility vs Target Yield
              </div>
              {(() => {
                const label =
                  decisionStatus === 'GO'
                    ? 'GO'
                    : decisionStatus === 'NO-GO'
                      ? 'Not Feasible'
                      : 'Marginal';
                const baseClasses =
                  'rounded-full px-3 py-1 text-[11px] font-semibold uppercase tracking-wide';
                const colorClasses =
                  decisionStatus === 'GO'
                    ? 'bg-emerald-100 text-emerald-900'
                    : decisionStatus === 'NO-GO'
                      ? 'bg-red-100 text-red-900'
                      : 'bg-amber-100 text-amber-900';
                return <div className={`${baseClasses} ${colorClasses}`}>{label}</div>;
              })()}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600 mb-1">Required NOI (target yield)</p>
                <p className="text-2xl font-bold text-gray-900">
                  {formatters.currency(requiredNoi ?? revenueReq.required_value)}
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  Current NOI:{' '}
                  <span className="font-semibold text-gray-900">
                    {formatters.currency(currentNoi ?? revenueReq.market_value)}
                  </span>
                </p>
                {typeof noiGap === 'number' && (
                  <p className={`text-xs mt-1 ${noiGap >= 0 ? 'text-green-600' : 'text-amber-600'}`}>
                    Gap: {formatters.currency(Math.abs(noiGap))} ({Math.abs(noiGapPct || 0).toFixed(1)}%)&nbsp;
                    {noiGap >= 0 ? 'surplus vs target' : 'shortfall vs target'}
                  </p>
                )}
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm text-blue-900/80 mb-1">
                  {isRestaurantProject ? 'Required Sales per SF' : 'Required Revenue per SF'}
                </p>
                <p className="text-2xl font-bold text-blue-700">
                  {typeof requiredRevenuePerSf === 'number' ? formatters.currency(requiredRevenuePerSf) : '—'}
                </p>
                <p className="text-xs text-blue-900/80 mt-2">
                  {isRestaurantProject ? 'Current sales per SF:' : 'Current revenue per SF:'}{' '}
                  <span className="font-semibold">
                    {typeof currentRevenuePerSf === 'number' ? formatters.currency(currentRevenuePerSf) : '—'}
                  </span>
                </p>
                {typeof revenuePerSfGap === 'number' && (
                  <p className={`text-xs mt-1 ${revenuePerSfGap >= 0 ? 'text-green-700' : 'text-amber-600'}`}>
                    Gap: {formatters.currency(Math.abs(revenuePerSfGap))} ({Math.abs(revenuePerSfGapPct || 0).toFixed(1)}%)&nbsp;
                    {revenuePerSfGap >= 0
                      ? isRestaurantProject
                        ? 'sales per SF already above requirement'
                        : 'above requirement'
                      : isRestaurantProject
                        ? 'additional sales needed to reach target'
                        : 'needed to reach target'}
                  </p>
                )}
              </div>
            </div>
              </>
            )}

            <div className={`p-4 rounded-lg ${
              (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-amber-50 border border-amber-200'
            }`}>
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wider text-gray-500">
                    Feasibility vs Target Yield
                  </p>
                  <p className="text-sm text-gray-800 leading-snug mt-1">
                    {feasibilityGapCopy}
                  </p>
                </div>
                <span className={`font-bold ${
                  (revenueReq.feasibility?.status || revenueReq.feasibility) === 'Feasible' ? 'text-green-600' : 'text-amber-600'
                }`}>
                  {revenueReq.feasibility?.status || revenueReq.feasibility}
                </span>
              </div>
              {revenueReq.feasibility?.recommendation && (
                <p className="text-sm mt-3 text-gray-600">
                  {revenueReq.feasibility.recommendation}
                </p>
              )}
            </div>
            
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between pt-4 border-t">
              <span className="text-sm text-gray-600">Simple Payback (yrs)</span>
              <span className="text-lg font-bold">{formatters.years(displayData.paybackPeriod)}</span>
            </div>
          </div>
        </section>
      )}

      {/* Financial Requirements removed - was only implemented for hospital */}

      {/* Major Soft Cost Categories */}
      {softCostCategories.length > 0 && (
        <section className={sectionCardClasses}>
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-900">Major Soft Cost Categories</h3>
            <div className="text-sm text-gray-500">
              {formatters.percentage(softCostsTotal / totalProjectCost)} of total investment
            </div>
          </div>
          <div className="space-y-4">
            {softCostCategories.map((category, index) => {
              const colors = ['blue', 'green', 'purple', 'orange', 'pink'];
              const color = colors[index % colors.length];
              
              return (
                <div key={index} className="flex items-center gap-4">
                  <div className={`w-3 h-12 bg-${color}-600 rounded`}></div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-semibold text-gray-800">{category.name}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-xs px-2 py-1 bg-gray-100 rounded-full text-gray-600">
                          {formatters.percentage(category.percent)}
                        </span>
                        <span className="text-lg font-bold text-gray-900">
                          {formatters.currency(category.amount)}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-2 bg-gradient-to-r from-${color}-500 to-${color}-600 rounded-full`}
                          style={{ width: `${Math.min(category.percent, 100)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <span className="text-lg font-semibold text-gray-900">Total Soft Costs</span>
              <div className="text-right">
                <span className="text-2xl font-bold text-gray-900">{formatters.currency(softCostsTotal)}</span>
                <span className="text-sm text-gray-500 block">{formatters.percentage(softCostsTotal / constructionTotal)} of construction</span>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Market Position */}
      <section className={`${sectionCardClasses} border-0 bg-transparent shadow-none p-0`}>
      <div className="grid grid-cols-1 gap-6">
        {/* Market Position */}
        <div className="bg-gradient-to-br from-white to-blue-50 rounded-xl shadow-lg border border-blue-100 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 sm:px-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Market Position
            </h3>
          </div>
          <div className="p-4 sm:p-6 space-y-4 text-sm">
            {(() => {
              const formatCost = (value?: number) =>
                typeof value === 'number' && Number.isFinite(value)
                  ? formatters.costPerSF(value)
                  : 'n/a';
              const basisCopy = typeof costPerSFDeltaPct === 'number'
                ? `${Math.abs(costPerSFDeltaPct).toFixed(1)}% ${costPerSFDeltaPct >= 0 ? 'above' : 'below'} benchmark`
                : 'Benchmark comparison pending additional market data.';
              return (
                <div className="bg-white rounded-lg p-4 shadow-sm space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-600">Your cost basis</span>
                    <span className="text-xl font-bold text-blue-600">
                      {formatCost(costPerSFValue ?? totals.cost_per_sf)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-500">
                      {isFlexIndustrial
                        ? 'Warehouse benchmark (excludes office/showroom component)'
                        : 'Market benchmark'}
                    </span>
                    <span className="font-medium text-gray-700">
                      {formatCost(marketCostPerSF)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">{basisCopy}</p>
                  {isFlexIndustrial ? (
                    <p className="text-xs text-gray-400">
                      Flex industrial projects with office components typically carry a higher cost basis than bulk warehouse assets.
                    </p>
                  ) : null}
                </div>
              );
            })()}

            <div className="relative">
              <div className="w-full bg-gradient-to-r from-green-100 via-yellow-100 to-red-100 rounded-full h-4 relative">
                <div
                  className="absolute top-1/2 transform -translate-y-1/2 w-6 h-6 bg-blue-600 rounded-full border-2 border-white shadow-lg z-10 transition-all"
                  style={{ left: `calc(${costPerSFGaugePosition}% - 12px)` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>-20%</span>
                <span>Market Avg</span>
                <span>+20%</span>
              </div>
              <div className="mt-4 p-3 bg-blue-50 rounded-lg text-center text-blue-800 text-sm font-semibold">
                {typeof costPerSFDeltaPct === 'number'
                  ? `${Math.abs(costPerSFDeltaPct).toFixed(1)}% ${costPerSFDeltaPct >= 0 ? 'above' : 'below'} market`
                  : 'Waiting on market cost inputs'}
              </div>
            </div>

            <div className="bg-slate-900/40 border border-slate-800/50 rounded-lg p-4 text-slate-100">
              {(() => {
                const formatPct = (value?: number) =>
                  typeof value === 'number' && Number.isFinite(value)
                    ? `${(value * 100).toFixed(1)}%`
                    : 'n/a';
                const spreadCopy = typeof yieldCapSpreadBps === 'number' && typeof yieldCapSpreadPct === 'number'
                  ? `Spread: ${yieldCapSpreadBps >= 0 ? '+' : '-'}${Math.abs(yieldCapSpreadBps).toFixed(0)} bp (${formatPct(Math.abs(yieldCapSpreadPct))}) ${yieldCapSpreadBps >= 0 ? 'above' : 'below'} market`
                  : 'Add a market cap benchmark to calculate spread.';
                return (
                  <>
                    <p className="text-xs uppercase tracking-wider text-slate-400 mb-2">Yield vs market cap</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Yield on cost</span>
                        <span className="font-semibold">{formatPct(effectiveYield)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-300">Market cap rate</span>
                        <span className="font-semibold">{formatPct(marketCapRateValue)}</span>
                      </div>
                      <p className="text-xs text-amber-200 mt-1">{spreadCopy}</p>
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        </div>

      </div>
      </section>

      {(() => {
        type SchedulePhase = {
          id?: string;
          label?: string;
          start_month?: number;
          startMonth?: number;
          duration?: number;
        };

        const schedulePhases: SchedulePhase[] = Array.isArray(rawConstructionSchedule?.phases)
          ? (rawConstructionSchedule?.phases as SchedulePhase[])
          : [];

        const milestoneStartYearSource =
          rawConstructionSchedule?.start_year ||
          calculations?.project_timeline?.start_year ||
          parsed?.start_year ||
          new Date().getFullYear();
        const milestoneStartYear =
          typeof milestoneStartYearSource === 'number'
            ? milestoneStartYearSource
            : Number(milestoneStartYearSource) || new Date().getFullYear();

        const formatScheduleMonthToQuarter = (monthValue: number) => {
          if (typeof monthValue !== 'number' || Number.isNaN(monthValue)) {
            return 'TBD';
          }
          const normalized = Math.max(0, monthValue);
          const yearOffset = Math.floor(normalized / 12);
          const quarter = Math.floor((normalized % 12) / 3) + 1;
          return `Q${quarter} ${milestoneStartYear + yearOffset}`;
        };

        const fallbackMilestones = [
          {
            id: 'groundbreaking',
            label: 'Groundbreaking',
            dateLabel: projectTimeline?.groundbreaking ?? 'TBD'
          },
          {
            id: 'structure',
            label: 'Structure Complete',
            dateLabel: projectTimeline?.structureComplete ?? 'TBD'
          },
          {
            id: 'substantial',
            label: 'Substantial Completion',
            dateLabel: projectTimeline?.substantialCompletion ?? 'TBD'
          },
          {
            id: 'grand_opening',
            label: buildingType === 'multifamily' ? 'First Tenant Move-in' : 'Grand Opening',
            dateLabel: projectTimeline?.grandOpening ?? 'TBD'
          },
          {
            id: 'soft_opening',
            label: 'Soft Opening & Ramp-Up',
            dateLabel:
              projectTimeline?._details?.find?.((detail: any) => detail?.id === 'soft_opening')?.date ??
              projectTimeline?.softOpening ??
              'TBD'
          }
        ];

        const scheduledMilestones =
          schedulePhases.length > 0
            ? schedulePhases.slice(0, 5).map((phase, idx) => {
                const startMonth =
                  typeof phase.start_month === 'number'
                    ? phase.start_month
                    : typeof phase.startMonth === 'number'
                      ? phase.startMonth
                      : 0;
                const duration = typeof phase.duration === 'number' ? phase.duration : 0;
                const midPoint = startMonth + duration / 2;
                return {
                  id: phase.id ?? `phase_${idx}`,
                  label: phase.label ?? `Phase ${idx + 1}`,
                  dateLabel: formatScheduleMonthToQuarter(midPoint)
                };
              })
            : [];

        let milestones = scheduledMilestones.length > 0 ? scheduledMilestones : fallbackMilestones;

        if (isDentalOffice) {
          const dentalMilestoneLabels = [
            'Design & Licensing',
            'Shell & Core / MEP Rough-In',
            'Dental Buildout & Finishes',
            'Equipment Installation & Sterilization',
            'Final Inspections & Commissioning'
          ];

          milestones = milestones.map((milestone, idx) => ({
            ...milestone,
            label: dentalMilestoneLabels[idx] ?? milestone.label
          }));
        }
        const milestoneIconMap = [
          { icon: CheckCircle, color: 'green' },
          { icon: Building, color: 'blue' },
          { icon: Users, color: 'purple' },
          { icon: Target, color: 'orange' },
          { icon: Activity, color: 'pink' }
        ];

        return (
          <div className="bg-gradient-to-br from-white via-blue-50 to-indigo-50 rounded-xl shadow-lg p-8 border border-blue-100">
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <Calendar className="h-6 w-6 text-blue-600" />
              Key Milestones
            </h3>
            <p className="text-sm text-gray-600 mb-6">
              Milestones are baseline planning assumptions. Yield, DSCR, and NOI metrics do not currently include schedule-delay or acceleration effects.
            </p>
            <div className="relative">
              <div className="absolute left-10 top-10 bottom-0 w-0.5 bg-gradient-to-b from-blue-400 via-purple-400 to-pink-400"></div>
              <div className="space-y-8">
                {milestones.map((milestone, idx) => {
                  const iconConfig = milestoneIconMap[idx] || milestoneIconMap[milestoneIconMap.length - 1];
                  const Icon = iconConfig.icon;
                  const color = iconConfig.color;
                  return (
                    <div key={idx} className="flex items-center gap-6 group">
                      <div className={`w-20 h-20 bg-gradient-to-br from-${color}-100 to-${color}-200 rounded-full flex items-center justify-center flex-shrink-0 shadow-lg group-hover:scale-110 transition-transform`}>
                        <Icon className={`h-10 w-10 text-${color}-600`} />
                      </div>
                      <div className="flex-1 bg-white rounded-lg p-4 shadow-md group-hover:shadow-lg transition-shadow">
                        <p className="font-bold text-gray-900 text-lg">{milestone.label}</p>
                        <p className="text-sm text-gray-600">{milestone.dateLabel}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );
      })()}

      {/* Financing Structure & Operational Efficiency */}
      <section className={`${sectionCardClasses} border-0 bg-transparent shadow-none p-0`}>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Financing Structure */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl shadow-lg border border-green-100 overflow-hidden">
          <div className="bg-gradient-to-r from-green-600 to-emerald-600 px-4 py-4 sm:px-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Financing Structure
            </h3>
          </div>
          <div className="p-4 sm:p-6">
            <div className="space-y-4">
              {[
                { name: 'Senior Debt', percent: 0.65, color: 'blue' },
                { name: 'Mezzanine', percent: 0.15, color: 'purple' },
                { name: 'Equity', percent: 0.20, color: 'green' }
              ].map((item, idx) => (
                <div key={idx} className="bg-white rounded-lg p-3 shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-semibold text-gray-700">{item.name} ({formatters.percentage(item.percent)})</span>
                    <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * item.percent)}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className={`h-3 bg-gradient-to-r from-${item.color}-500 to-${item.color}-600 rounded-full`}
                      style={{ width: `${item.percent * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-6 border-t border-green-200 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Weighted Rate</span>
                <span className="font-bold text-gray-900">6.8%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Annual Debt Service</span>
                <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * 0.65 * 0.068)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Interest During Construction</span>
                <span className="font-bold text-gray-900">{formatters.currency(totalProjectCost * 0.044)}</span>
              </div>
              <div className="bg-green-100 rounded-lg p-3 mt-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-green-700">DSCR Target</span>
                  <span className="font-bold text-green-800">{dscrTargetDisplay}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Operational Efficiency */}
        {isDentalOffice ? (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border border-purple-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-4 py-4 sm:px-6">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Operational Efficiency
              </h3>
            </div>
            <div className="p-4 sm:p-6 space-y-6">
              <div>
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Staffing Metrics</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {[
                    {
                      label: 'Operatories',
                      value: dentalOperatoriesValue != null ? dentalOperatoriesValue : '-',
                      color: 'purple'
                    },
                    {
                      label: 'NOI Margin',
                      value: dentalNoiMarginValue != null
                        ? formatters.percentage(dentalNoiMarginValue)
                        : formatters.percentage(0),
                      color: 'pink'
                    }
                  ].map((tile, idx) => (
                    <div key={idx} className="bg-white text-center p-4 rounded-lg shadow-sm">
                      <p className={`text-3xl font-bold ${tile.color === 'purple' ? 'text-purple-600' : 'text-pink-600'}`}>
                        {tile.value}
                      </p>
                      <p className="text-xs text-gray-600">{tile.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Revenue Efficiency</h4>
                <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                  {[
                    {
                      label: 'Revenue per Provider',
                      value: dentalRevenuePerProviderValue != null
                        ? formatters.currencyExact(dentalRevenuePerProviderValue)
                        : formatters.currencyExact(0)
                    },
                    {
                      label: 'Revenue per Operatory',
                      value: dentalRevenuePerOperatoryValue != null
                        ? formatters.currencyExact(dentalRevenuePerOperatoryValue)
                        : formatters.currencyExact(0)
                    },
                    {
                      label: 'Operating Margin',
                      value: dentalNoiMarginValue != null
                        ? formatters.percentage(dentalNoiMarginValue)
                        : formatters.percentage(0)
                    }
                  ].map((row, idx) => (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-gray-600">{row.label}</span>
                      <span className="font-bold text-gray-900">{row.value}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Target KPIs</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {[
                    {
                      label: 'Production / Provider',
                      value: dentalRevenuePerProviderValue != null
                        ? formatters.currencyExact(dentalRevenuePerProviderValue)
                        : formatters.currencyExact(0),
                      color: 'purple'
                    },
                    {
                      label: 'Chair Utilization',
                      value: dentalUtilizationValue != null
                        ? formatters.percentage(dentalUtilizationValue)
                        : formatters.percentage(0),
                      color: 'indigo'
                    },
                    {
                      label: 'Ops per Provider',
                      value: dentalOpsPerProviderValue ?? '0.0',
                      color: 'pink'
                    }
                  ].map((kpi, idx) => (
                    <div key={idx} className={`bg-gradient-to-br from-${kpi.color}-100 to-${kpi.color}-200 p-3 rounded-lg text-center`}>
                      <p className={`text-xl font-bold text-${kpi.color}-700`}>{kpi.value}</p>
                      <p className={`text-xs text-${kpi.color}-600`}>{kpi.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl shadow-lg border border-purple-100 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Operational Efficiency
              </h3>
            </div>
            <div className="p-6">
              {normalizedStaffingMetrics.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Staffing Metrics</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {normalizedStaffingMetrics.slice(0, 2).map((metric, idx) => {
                      const rawLabel =
                        typeof metric?.label === 'string' && metric.label.trim()
                          ? metric.label
                          : `Metric ${idx + 1}`;
                      const labelLower = rawLabel.toLowerCase();
                      const isLaborMetric = labelLower.includes('labor');
                      const isManagementMetric = labelLower.includes('management');
                      const displayLabel = isLaborMetric ? 'Facility Ops Labor' : rawLabel;
                      const rawValue = metric?.value;
                      const zeroLike = (isLaborMetric || isManagementMetric) && isZeroLikeMetricValue(rawValue);
                      const normalizedValue =
                        rawValue === null || rawValue === undefined
                          ? '—'
                          : typeof rawValue === 'number'
                            ? (Number.isFinite(rawValue) ? rawValue.toLocaleString() : '—')
                            : rawValue;
                      const displayValue = zeroLike ? 'Not modeled' : normalizedValue;
                      const helperText = isLaborMetric ? 'Production labor excluded (tenant business).' : undefined;
                      return (
                        <div key={idx} className="bg-white text-center p-4 rounded-lg shadow-sm">
                          <p className={`text-3xl font-bold ${idx === 0 ? 'text-purple-600' : 'text-pink-600'}`}>
                            {displayValue}
                          </p>
                          <p className="text-xs text-gray-600">{displayLabel}</p>
                          {helperText ? (
                            <p className="text-[10px] text-gray-500 mt-1">{helperText}</p>
                          ) : null}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {normalizedRevenueMetrics.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Revenue Efficiency</h4>
                  <div className="bg-white rounded-lg p-3 space-y-2 shadow-sm">
                    {normalizedRevenueMetrics.slice(0, 3).map(({ key, label, value }) => (
                      <div key={key} className="flex justify-between text-sm">
                        <span className="text-gray-600">{label}</span>
                        <span className="font-bold text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {buildingType === 'office' && (
                <div className="mb-4">
                  <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Office Opex & CAM</h4>
                  <div className="bg-white rounded-lg p-3 shadow-sm space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Operating Expenses</span>
                      <span className="font-bold text-gray-900">
                        {formatters.currency(operatingExpensesTotal)} ({formatters.currencyExact(operatingExpensesTotal / normalizedOfficeSquareFootage)}/SF)
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Recoverable CAM</span>
                      <span className="font-bold text-gray-900">
                        {camChargesTotal > 0
                          ? `${formatters.currency(camChargesTotal)} (${formatters.currencyExact(camChargesTotal / normalizedOfficeSquareFootage)}/SF)`
                          : 'Included in rent'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {operationalKpis.length > 0 && (
                <div>
                  <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Target KPIs</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {operationalKpis.slice(0, 3).map((kpi, idx) => (
                      <div key={idx} className={`bg-gradient-to-br from-${kpi.color}-100 to-${kpi.color}-200 p-3 rounded-lg text-center`}>
                        <p className={`text-xl font-bold text-${kpi.color}-700`}>{kpi.value}</p>
                        <p className={`text-xs text-${kpi.color}-600`}>{kpi.label}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
      </section>

      {/* Executive Decision Points */}
      <section className="bg-gradient-to-r from-amber-50 via-orange-50 to-amber-50 border-l-4 border-amber-500 rounded-xl shadow-lg p-4 sm:p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-3">
          <div className="p-2 bg-amber-100 rounded-lg">
            <Lightbulb className="h-6 w-6 text-amber-600" />
          </div>
          Executive Decision Points
        </h3>
        {decisionYieldDisplay && (
          <p className="text-sm text-amber-700 mb-4">
            Current yield on cost: <span className="font-semibold">{decisionYieldDisplay}</span>
          </p>
        )}
        <div className="space-y-3">
          {isOffice ? (
            <ol className="space-y-2 text-sm text-slate-700">
              <li>
                <span className="font-semibold">Basis &amp; rent/SF:</span>{' '}
                Current basis around {officeBasisSummary} with {officeRentSummary} implies a high bar for rent and tenant quality.
                Benchmark total project cost per SF and rentable SF against recent Class A trades in this submarket.
              </li>
              <li>
                <span className="font-semibold">Returns &amp; lease-up risk:</span>{' '}
                {officeReturnSummary}. Yield and DSCR are driven by rent/SF, stabilized occupancy, and the amortized impact of TI
                and leasing commissions — stress these assumptions against comp sets and renewal probabilities.
              </li>
              <li>
                <span className="font-semibold">TI/LC load &amp; OpEx:</span>{' '}
                Confirm TI allowances, leasing commissions, and operating expenses per SF align with broker guidance. Elevated TI/LC
                burn or underestimated OpEx compress NOI quickly even when headline rent appears strong, so validate the rent roll
                and tenant mix before moving forward.
              </li>
            </ol>
          ) : decisionBullets.length > 0 ? (
            decisionBullets.slice(0, 3).map((point, idx) => (
              <div key={idx} className="flex items-start gap-3 bg-white rounded-lg p-3 shadow-sm">
                <div className="w-6 h-6 bg-amber-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-amber-700 text-xs font-bold">{idx + 1}</span>
                </div>
                <span className="text-sm text-gray-700">{point}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-700">Cost, yield, and soft cost metrics are loading.</p>
          )}
        </div>
      </section>

      {/* Executive Financial Summary Footer */}
      <section className="rounded-2xl overflow-hidden shadow-2xl">
        <div className="bg-gradient-to-r from-slate-900 via-indigo-900 to-slate-900 p-5 sm:p-8">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 xl:grid-cols-4 2xl:grid-cols-5">
            <div className="text-center">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">TOTAL CAPITAL REQUIRED</p>
              <p className="text-3xl font-bold text-white">{formatters.currency(totalProjectCost)}</p>
              <p className="text-sm text-slate-500">Construction + Soft Costs</p>
            </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">EXPECTED ANNUAL RETURN</p>
            <p className="text-3xl font-bold text-white">{formatters.currency(noi)}</p>
            <p className="text-sm text-slate-500">After operating expenses</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">
              INVESTMENT PER UNIT
            </p>
            <p className="text-3xl font-bold text-white">
              {displayData.costPerUnit > 0 ? formatters.currencyExact(displayData.costPerUnit) : 'N/A'}
            </p>
            <p className="text-sm text-slate-500">Total project cost divided by units</p>
          </div>
            <div className="text-center">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">DEBT COVERAGE</p>
              <p className="text-3xl font-bold text-white">{formatters.multiplier(displayData.dscr)}</p>
              <p className="text-sm text-slate-500">DSCR (Target: {dscrTargetDisplay})</p>
            </div>
          {(() => {
            const showTotalUnitsFooter =
              (buildingType || '').toLowerCase() !== 'industrial' &&
              typeof displayData.units === 'number' &&
              displayData.units > 0;
            if (!showTotalUnitsFooter) return null;
            const footerUnitLabel = (() => {
              if (parsedBuildingType !== 'healthcare') {
                return 'Total Units';
              }
              if (isHealthcareOutpatient) {
                return 'Total Exam Rooms';
              }
              if (isImagingCenter) {
                return 'Total Scan Rooms';
              }
              if (isSurgicalCenter) {
                return 'Total Operating Rooms';
              }
              return 'Total Units';
            })();
            return (
            <div className="text-center">
              <p className="text-xs text-slate-400 uppercase tracking-wider mb-3">
                {footerUnitLabel}
              </p>
              <p className="text-3xl font-bold text-white">{displayData.units.toLocaleString()}</p>
              <p className="text-sm text-slate-500">Derived from square footage and density</p>
            </div>
            );
          })()}
          </div>
        </div>
      </section>

      </div>

      {/* Scenario Comparison Modal */}
      {isScenarioOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 px-4 py-8" onClick={() => setIsScenarioOpen(false)}>
          <div className="w-full max-w-6xl rounded-2xl border border-slate-800 bg-slate-950 shadow-2xl" onClick={event => event.stopPropagation()}>
            <div className="flex items-center justify-between gap-4 border-b border-slate-800 px-6 py-4">
              <div>
                <p className="text-sm font-semibold text-white">Scenario Comparison (legacy)</p>
                <p className="text-xs text-slate-400">Shows the current case alongside the target yield requirements.</p>
              </div>
              <button
                className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-3 py-1 text-xs font-semibold text-slate-200 hover:bg-slate-800"
                onClick={() => setIsScenarioOpen(false)}
              >
                <XCircle className="h-4 w-4" />
                Close
              </button>
            </div>
            <div className="px-6 py-6">
              {(() => {
                const formatPct = (value?: number) => (typeof value === 'number' && Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : '—');
                const formatCurrency0 = (value?: number) =>
                  typeof value === 'number' && Number.isFinite(value)
                    ? value.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
                    : '—';
                const formatRevenuePerSf = (value?: number) =>
                  typeof value === 'number' && Number.isFinite(value) ? `$${value.toFixed(0)}/SF` : '—';
                const formatDscrValue = (value?: number) => (typeof value === 'number' && Number.isFinite(value) ? `${value.toFixed(2)}×` : '—');

                const currentYieldValue = typeof stabilizedYield === 'number' && Number.isFinite(stabilizedYield) ? stabilizedYield : undefined;
                const targetYieldValue = typeof targetYieldRate === 'number' && Number.isFinite(targetYieldRate) ? targetYieldRate : undefined;

                const currentNoiValue = typeof noi === 'number' && Number.isFinite(noi) ? noi : undefined;
                const requiredNoiValue = typeof requiredNoi === 'number' && Number.isFinite(requiredNoi) ? requiredNoi : undefined;

                const currentRevenuePerSfValue =
                  typeof currentRevenuePerSf === 'number' && Number.isFinite(currentRevenuePerSf) ? currentRevenuePerSf : undefined;
                const requiredRevenuePerSfValue =
                  typeof requiredRevenuePerSf === 'number' && Number.isFinite(requiredRevenuePerSf) ? requiredRevenuePerSf : undefined;

                const currentDscrValue =
                  typeof dscr === 'number' && Number.isFinite(dscr)
                    ? dscr
                    : typeof annualDebtService === 'number' && annualDebtService > 0 && typeof currentNoiValue === 'number'
                      ? currentNoiValue / annualDebtService
                      : undefined;
                const targetDscrValue =
                  typeof requiredNoiValue === 'number' && typeof annualDebtService === 'number' && annualDebtService > 0
                    ? requiredNoiValue / annualDebtService
                    : undefined;

                const yieldGap = typeof targetYieldValue === 'number' && typeof currentYieldValue === 'number' ? targetYieldValue - currentYieldValue : undefined;
                const noiDelta =
                  typeof requiredNoiValue === 'number' && typeof currentNoiValue === 'number' ? requiredNoiValue - currentNoiValue : undefined;
                const noiDeltaPct =
                  typeof noiDelta === 'number' && typeof requiredNoiValue === 'number' && requiredNoiValue !== 0 ? noiDelta / requiredNoiValue : undefined;
                const revenueDeltaPerSf =
                  typeof requiredRevenuePerSfValue === 'number' && typeof currentRevenuePerSfValue === 'number'
                    ? requiredRevenuePerSfValue - currentRevenuePerSfValue
                    : undefined;
                const revenueDeltaPct =
                  typeof revenueDeltaPerSf === 'number' &&
                  typeof requiredRevenuePerSfValue === 'number' &&
                  requiredRevenuePerSfValue !== 0
                    ? revenueDeltaPerSf / requiredRevenuePerSfValue
                    : undefined;

                return (
                  <div className="space-y-4 text-xs md:text-sm text-slate-100">
                    <div className="rounded-lg border border-slate-800/60 bg-slate-900/70 px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                      <div>
                        <div className="text-xs font-semibold text-slate-200">Gaps to target</div>
                        <div className="text-xs text-slate-300 mt-1">
                          Yield gap:{' '}
                          <span className="font-semibold">
                            {typeof yieldGap === 'number' ? formatPct(yieldGap) : 'n/a'}
                          </span>
                          {targetYieldValue != null && currentYieldValue != null && (
                            <span className="text-slate-400">
                              {' '}
                              (current {formatPct(currentYieldValue)} vs target {formatPct(targetYieldValue)})
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-xs text-slate-300">
                        NOI gap:{' '}
                        <span className="font-semibold">
                          {formatCurrency0(noiDelta)}
                          {typeof noiDeltaPct === 'number' ? ` (${(noiDeltaPct * 100).toFixed(1)}%)` : ''}
                        </span>
                        <span className="mx-3 text-slate-700">|</span>
                        Revenue gap:{' '}
                        <span className="font-semibold">
                          {formatRevenuePerSf(revenueDeltaPerSf)}
                          {typeof revenueDeltaPct === 'number' ? ` (${(revenueDeltaPct * 100).toFixed(1)}%)` : ''}
                        </span>
                      </div>
                    </div>

                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Current scenario</p>
                        <div className="mt-3 space-y-2 text-sm text-slate-200">
                          <div className="flex justify-between">
                            <span>Yield on cost</span>
                            <span className="font-semibold">{formatPct(currentYieldValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>NOI</span>
                            <span className="font-semibold">{formatCurrency0(currentNoiValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Revenue per SF</span>
                            <span className="font-semibold">{formatRevenuePerSf(currentRevenuePerSfValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>DSCR</span>
                            <span className="font-semibold">{formatDscrValue(currentDscrValue)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-4">
                        <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Target yield scenario</p>
                        <div className="mt-3 space-y-2 text-sm text-slate-200">
                          <div className="flex justify-between">
                            <span>Yield on cost (target)</span>
                            <span className="font-semibold">{formatPct(targetYieldValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Required NOI</span>
                            <span className="font-semibold">{formatCurrency0(requiredNoiValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Required revenue per SF</span>
                            <span className="font-semibold">{formatRevenuePerSf(requiredRevenuePerSfValue)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>DSCR at target NOI</span>
                            <span className="font-semibold">{formatDscrValue(targetDscrValue)}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-slate-300">
                      {typeof yieldGap === 'number' && typeof targetYieldValue === 'number' && yieldGap > 0 ? (
                        <>
                          To reach a yield on cost of <span className="font-semibold">{formatPct(targetYieldValue)}</span>, the project needs roughly{' '}
                          <span className="font-semibold">{formatCurrency0(noiDelta)}</span> more NOI and{' '}
                          <span className="font-semibold">{formatRevenuePerSf(revenueDeltaPerSf)}</span> more revenue per SF (or equivalent cost savings).
                        </>
                      ) : (
                        <>Target yield isn’t configured for this asset yet—showing the current snapshot only.</>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
        <TrustPanel
          open={isTrustPanelOpen}
          onOpenChange={setIsTrustPanelOpen}
          initialSectionId={trustPanelSection}
        />
        <ScenarioModal
          open={isScenarioOpen}
          onClose={() => setIsScenarioOpen(false)}
          base={scenarioBase}
          dealShieldScenarioBundle={scenarioDealShieldBundle}
        />
      </>
    );
  };
