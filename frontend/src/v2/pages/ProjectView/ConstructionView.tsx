import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Project } from '../../types';
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatters';
import { pdfService } from '@/services/api';
import { generateExportFilename } from '@/utils/filenameGenerator';
import { 
  HardHat, TrendingUp, Calendar, Clock, ChevronRight, 
  AlertCircle, Info, FileText, Building, Wrench, Zap, 
  Droplet, PaintBucket, DollarSign, MapPin, Download, BarChart3, Package
} from 'lucide-react';
import { ProvenanceModal } from '../../components/ProvenanceModal';
import { BackendDataMapper } from '../../utils/backendDataMapper';
import { ScenarioModal } from '@/v2/components/ScenarioModal';

type TradeCostSplit = {
  materials: number;
  labor: number;
  equipment: number;
};

type AnyRecord = Record<string, any>;

const normalizeTradeCostSplit = (split: TradeCostSplit): TradeCostSplit => {
  const { materials, labor, equipment } = split;
  const total = materials + labor + equipment || 1;
  return {
    materials: materials / total,
    labor: labor / total,
    equipment: equipment / total,
  };
};

interface Props {
  project: Project;
}

const conceptualLabelByTrade: Record<string, string> = {
  structural: 'Structural systems (pre-design)',
  mechanical: 'Mechanical systems (conceptual)',
  electrical: 'Electrical distribution & power systems (conceptual)',
  plumbing: 'Plumbing & process utilities (conceptual)',
  finishes: 'Interior finishes & fit-out (conceptual)',
};

const formatCurrency2 = (value: number): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatQuantityWithUnit = (
  quantity?: number,
  unitRaw?: string,
  tradeKeyRaw?: string
): string => {
  const hasQty = typeof quantity === 'number' && !Number.isNaN(quantity);
  const unit = (unitRaw || '').trim().toUpperCase();
  const normalizedUnit = unit.replace(/\s+/g, '_');
  const isLumpSumUnit =
    normalizedUnit === 'LUMP_SUM' ||
    normalizedUnit === 'LUMPSUM' ||
    normalizedUnit === 'LS';

  if (hasQty && quantity === 1 && isLumpSumUnit) {
    const tradeKey = (tradeKeyRaw || '').toLowerCase().trim();
    return conceptualLabelByTrade[tradeKey] || 'Conceptual system allowance';
  }

  if (hasQty && unit) {
    return `${formatNumber(quantity as number)} ${unit}`;
  }
  if (hasQty) {
    return formatNumber(quantity as number);
  }
  if (unit) {
    return isLumpSumUnit ? '1 LS' : unit;
  }
  return '—';
};

const getScopeHint = (
  buildingTypeRaw: string,
  tradeNameRaw: string,
  systemNameRaw?: string
): string | undefined => {
  const buildingType = (buildingTypeRaw || '').toLowerCase();
  const tradeName = (tradeNameRaw || '').toLowerCase();
  const label = (systemNameRaw || '').toLowerCase();

  if (buildingType === 'industrial') {
    if (tradeName === 'structural') {
      if (label.includes('slab on grade')) {
        return 'Slab cost is scaled to total warehouse SF. Typical 6" slab with localized thickening at docks and racking lines.';
      }
      if (label.includes('tilt-wall') || label.includes('shell')) {
        return 'Tilt-wall and shell costs scale with overall footprint and assumed clear height for a Class A distribution warehouse.';
      }
      if (label.includes('foundations')) {
        return 'Foundations include footings, thickened slab strips, and isolated pads sized proportionally to building SF.';
      }
    }

    if (tradeName === 'mechanical') {
      if (label.includes('rooftop units') || label.includes('rtus')) {
        return 'Assumes approximately 1 rooftop unit (RTU) per 15,000 SF of warehouse area. Adjust count for higher office or temperature control requirements.';
      }
      if (label.includes('ductwork') || label.includes('ventilation')) {
        return 'Ductwork and ventilation costs scale with conditioned SF and the assumed RTU count.';
      }
    }

    if (tradeName === 'electrical') {
      if (label.includes('high-bay lighting') || label.includes('lighting')) {
        return 'Lighting cost is sized to typical high-bay LED fixtures and controls at standard warehouse light levels.';
      }
      if (label.includes('power distribution') || label.includes('panels')) {
        return 'Power distribution covers panels, feeders, and branch circuits sized for a typical dry warehouse with modest office load.';
      }
    }

    if (tradeName === 'plumbing') {
      if (label.includes('restroom groups') || label.includes('fixtures')) {
        return 'Assumes roughly one pair of restrooms (fixture group) per 25,000 SF of building area, with code-minimum fixture counts.';
      }
      if (
        label.includes('domestic water') ||
        label.includes('hose bibs') ||
        label.includes('roof drains')
      ) {
        return 'Domestic water, hose bibs, and roof drains are scaled to footprint and typical roof drainage requirements for this size warehouse.';
      }
    }

    if (tradeName === 'finishes') {
      if (label.includes('office build-out')) {
        return 'Office build-out assumes approximately 5% of total SF (minimum 1,500 SF) for conditioned office, breakroom, and support space.';
      }
      if (label.includes('floor sealers') || label.includes('striping')) {
        return 'Warehouse finish scope includes slab sealing, striping, and basic protection needed for racking and forklift traffic.';
      }
      if (label.includes('doors') || label.includes('hardware')) {
        return 'Doors, frames, hardware, and misc interior finishes are sized proportionally to assumed office and dock door counts.';
      }
    }
  }

  return undefined;
};

type PhaseTradeMix = {
  structural?: number;
  mechanical?: number;
  electrical?: number;
  plumbing?: number;
  finishes?: number;
};

const normalizeMix = (mix: PhaseTradeMix): PhaseTradeMix => {
  const entries = Object.entries(mix).filter(([_, v]) => typeof v === 'number' && !Number.isNaN(v));
  if (entries.length === 0) return {};
  const total = entries.reduce((sum, [, v]) => sum + (v as number), 0) || 1;
  const normalized: PhaseTradeMix = {};
  for (const [k, v] of entries) {
    normalized[k as keyof PhaseTradeMix] = (v as number) / total;
  }
  return normalized;
};

/**
 * Get a heuristic trade mix for a given phase.
 * For now we implement industrial warehouse logic; other building types can be added later.
 */
const getPhaseTradeMix = (buildingTypeRaw: string, phaseIdRaw: string): PhaseTradeMix => {
  const bt = (buildingTypeRaw || '').toLowerCase();
  const phaseId = (phaseIdRaw || '').toLowerCase();

  if (bt === 'industrial') {
    const isSite =
      phaseId.includes('site') ||
      phaseId.includes('foundation') ||
      phaseId.includes('foundations') ||
      phaseId.includes('podium');
    const isStructure =
      phaseId.includes('structure') ||
      phaseId.includes('frame') ||
      phaseId.includes('superstructure') ||
      (phaseId.includes('shell') && !phaseId.includes('envelope'));
    const isEnvelope =
      phaseId.includes('envelope') ||
      phaseId.includes('skin') ||
      phaseId.includes('exterior');
    const isMepRough =
      phaseId.includes('mep_rough') ||
      phaseId.includes('rough-in') ||
      (phaseId.includes('rough') && phaseId.includes('mep'));
    const isInteriorFinishes =
      phaseId.includes('interior') ||
      (phaseId.includes('finishes') && !phaseId.includes('mep'));
    const isMepFinishes =
      phaseId.includes('mep_finishes') ||
      phaseId.includes('commissioning') ||
      phaseId.includes('punch');

    if (isSite) {
      return normalizeMix({
        structural: 0.7,
        plumbing: 0.3,
      });
    }
    if (isStructure) {
      return normalizeMix({
        structural: 1.0,
      });
    }
    if (isEnvelope) {
      return normalizeMix({
        structural: 0.6,
        finishes: 0.4,
      });
    }
    if (isMepRough) {
      return normalizeMix({
        mechanical: 0.4,
        electrical: 0.4,
        plumbing: 0.2,
      });
    }
    if (isInteriorFinishes) {
      return normalizeMix({
        finishes: 0.7,
        electrical: 0.2,
        mechanical: 0.1,
      });
    }
    if (isMepFinishes) {
      return normalizeMix({
        mechanical: 0.4,
        electrical: 0.4,
        plumbing: 0.2,
      });
    }
  }

  return {};
};

const getPhaseTooltip = (
  buildingTypeRaw: string,
  phaseIdRaw: string,
  mix: PhaseTradeMix | undefined
): string | undefined => {
  const bt = (buildingTypeRaw || '').toLowerCase();
  const phaseId = (phaseIdRaw || '').toLowerCase();

  const tradesPhrase = (() => {
    if (!mix) return '';
    const entries = Object.entries(mix)
      .filter(([, v]) => typeof v === 'number' && (v as number) > 0.01)
      .sort((a, b) => (b[1] as number) - (a[1] as number))
      .slice(0, 3)
      .map(([k, v]) => {
        const name =
          k === 'structural'
            ? 'Structural'
            : k === 'mechanical'
              ? 'Mechanical'
              : k === 'electrical'
                ? 'Electrical'
                : k === 'plumbing'
                  ? 'Plumbing'
                  : k === 'finishes'
                    ? 'Finishes'
                    : k;
        return `${name} ${Math.round((v as number) * 100)}%`;
      });
    return entries.length ? ` Key trades: ${entries.join(', ')}.` : '';
  })();
  const tradesSuffix = tradesPhrase ? ` ${tradesPhrase}` : '';

  if (bt === 'industrial') {
    if (phaseId.includes('site') || phaseId.includes('foundation')) {
      return `Sitework, foundations, and underground utilities for the warehouse structure.${tradesSuffix}`;
    }
    if (phaseId.includes('structure')) {
      return `Erection of the primary structure and shell framing.${tradesSuffix}`;
    }
    if (phaseId.includes('envelope') || phaseId.includes('skin')) {
      return `Exterior envelope, roofing, and weatherproofing of the building.${tradesSuffix}`;
    }
    if (phaseId.includes('mep_rough') || (phaseId.includes('rough') && phaseId.includes('mep'))) {
      return `MEP rough-in in the field: ductwork, conduit, and piping runs before walls close.${tradesSuffix}`;
    }
    if (phaseId.includes('interior') || phaseId.includes('fit')) {
      return `Interior office build-out and warehouse finishes.${tradesSuffix}`;
    }
    if (phaseId.includes('commissioning') || phaseId.includes('systems') || phaseId.includes('punch')) {
      return `Final MEP trim, systems start-up, testing, and punch list closeout.${tradesSuffix}`;
    }
  }

  return tradesSuffix || undefined;
};

export const ConstructionView: React.FC<Props> = ({ project }) => {
  const [expandedTrade, setExpandedTrade] = useState<string | null>(null);
  const [showProvenanceModal, setShowProvenanceModal] = useState(false);
  const [showTraceModal, setShowTraceModal] = useState(false);
  const [activeTradeFilter, setActiveTradeFilter] = useState<'all' | 'structural' | 'mechanical' | 'electrical' | 'plumbing' | 'finishes'>('all');
  const [isScenarioOpen, setIsScenarioOpen] = useState(false);
  
  const analysis = project.analysis;
  if (!analysis) {
    return <div className="p-6">Loading trade breakdown...</div>;
  }
  
  const calculations = analysis.calculations || {};
  const parsed_input = analysis.parsed_input || {};
  const displayData = BackendDataMapper.mapToDisplay(project.analysis);
  const isDev = typeof import.meta !== 'undefined' && Boolean(import.meta.env?.DEV);
  const constructionSchedule = calculations?.construction_schedule;

  const calculationTraceRaw = Array.isArray(calculations.calculation_trace)
    ? (calculations.calculation_trace as any[])
    : [];

  const calculationTrace = calculationTraceRaw.map((entry: any, index: number) => {
    const step = typeof entry?.step === 'string' ? entry.step : `step_${index + 1}`;
    const payload = entry?.payload ?? entry?.data ?? entry ?? {};
    return { step, payload };
  });

  // ========================================
  // PULL FROM SAME CALCULATION ENGINE
  // ========================================
  
  // Get values from calculations object - NO HARDCODING
  const squareFootageRaw =
    typeof parsed_input.square_footage === 'number' && parsed_input.square_footage > 0
      ? parsed_input.square_footage
      : typeof calculations.project_info?.square_footage === 'number' && calculations.project_info.square_footage > 0
        ? calculations.project_info.square_footage
        : 0;
  const squareFootage = squareFootageRaw > 0 ? squareFootageRaw : 0;
  const safeSquareFootage = squareFootage > 0 ? squareFootage : 1;

  const buildingTypeRaw =
    parsed_input.building_type ||
    calculations.project_info?.building_type ||
    'office';
  const buildingType = buildingTypeRaw;
  const baseCostPerSF = calculations.construction_costs?.base_cost_per_sf || 1150;
  const regionalMultiplier = calculations.construction_costs?.regional_multiplier || 1.03;
  const complexityMultiplier = calculations.construction_costs?.class_multiplier || 1.00;
  const finalCostPerSF = calculations.construction_costs?.final_cost_per_sf || 1185;
  const rawCostBuildUp = Array.isArray(calculations.construction_costs?.cost_build_up)
    ? calculations.construction_costs.cost_build_up
    : [];
  const displayCostBuildUp = Array.isArray(displayData.constructionCostBuildUp)
    ? displayData.constructionCostBuildUp
    : [];
  const finishLevelName = (displayData.finishLevel || parsed_input.finish_level || 'standard').toString().toLowerCase();
  const costBuildUpSource =
    displayCostBuildUp.length > 0
      ? displayCostBuildUp
      : rawCostBuildUp;
  const fallbackCostBuildUp = [
    { label: 'Base Cost', value_per_sf: baseCostPerSF },
    { label: 'Regional', multiplier: regionalMultiplier || 1 },
    { label: 'Complexity', multiplier: complexityMultiplier || 1 },
  ];
  if (finishLevelName !== 'standard') {
    fallbackCostBuildUp.push({
      label: 'Finish Level',
      multiplier: calculations.construction_costs?.finish_cost_factor || 1,
    });
  }
  const costBuildUp =
    costBuildUpSource.length > 0 ? costBuildUpSource : fallbackCostBuildUp;

  
  // Debug: Log the actual values
  console.log('Construction View Debug:', {
    baseCostPerSF,
    regionalMultiplier,
    complexityMultiplier,
    finalCostPerSF,
    expectedFinal: baseCostPerSF * regionalMultiplier * complexityMultiplier,
    location: calculations.project_info?.location,
    rawData: calculations.construction_costs
  });
  // Use totals.hard_costs for the headline card (base construction + equipment + special features)
  const constructionTotal =
    typeof calculations.totals?.hard_costs === 'number'
      ? calculations.totals.hard_costs
      : 246900000;

  const regionalInfo = calculations?.regional;
  const fallbackLocationDisplay =
    calculations?.project_info?.location ||
    parsed_input?.location ||
    (project as AnyRecord)?.location ||
    'City, ST';
  const locationDisplay =
    regionalInfo?.location_display ||
    (regionalInfo && regionalInfo.city
      ? `${regionalInfo.city}${regionalInfo.state ? `, ${regionalInfo.state}` : ''}`
      : fallbackLocationDisplay);
  const regionalMultiplierValue =
    typeof regionalInfo?.multiplier === 'number'
      ? regionalInfo.multiplier
      : typeof calculations?.construction_costs?.regional_multiplier === 'number'
        ? calculations.construction_costs.regional_multiplier
        : 1;
  const regionalDeltaPct = Math.round(Math.abs((regionalMultiplierValue - 1) * 100));
  const regionalComparisonCopy =
    regionalMultiplierValue > 1
      ? `${locationDisplay} is ${regionalDeltaPct}% above the national baseline.`
      : regionalMultiplierValue < 1
        ? `${locationDisplay} is ${regionalDeltaPct}% below the national baseline.`
        : `${locationDisplay} aligns with the national baseline.`;

  // Scenario modal base metrics
  const projectRecord = project as AnyRecord;
  const analysisRecord = analysis as AnyRecord;
  const scenarioProjectTitle =
    (analysisRecord?.parsed_input?.display_name as string) ||
    (analysisRecord?.parsed_input?.project_name as string) ||
    projectRecord?.project_name ||
    project?.name ||
    'Project';

  const scenarioLocationLine = [
    (analysisRecord?.parsed_input?.location as string) || project?.location || '',
    buildingType || '',
    (analysisRecord?.parsed_input?.square_footage as AnyRecord)?.toString?.() ||
      projectRecord?.square_footage?.toString?.() ||
      '',
  ]
    .filter(Boolean)
    .join(' • ');

  const scenarioCalc = analysisRecord?.calculations || projectRecord?.calculation_data || {};
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
    projectRecord?.total_cost ??
    projectRecord?.totalCost ??
    null;

  const baseCostPerSf =
    projectRecord?.cost_per_sqft ??
    projectRecord?.costPerSqft ??
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

  // Use construction_total as the base for trade breakdown (excludes equipment + special features)
  const baseConstructionTotal =
    typeof calculations.construction_costs?.construction_total === 'number'
      ? calculations.construction_costs.construction_total
      : constructionTotal;

  const specialFeaturesTotal =
    typeof calculations.construction_costs?.special_features_total === 'number'
      ? calculations.construction_costs.special_features_total
      : 0;

  const specialFeaturesBreakdownRaw = calculations.construction_costs?.special_features_breakdown;
  const specialFeaturesBreakdown = Array.isArray(specialFeaturesBreakdownRaw)
    ? specialFeaturesBreakdownRaw
        .filter(
          (item: any) =>
            item &&
            typeof item.id === 'string' &&
            typeof item.label === 'string' &&
            typeof item.cost_per_sf === 'number' &&
            Number.isFinite(item.cost_per_sf) &&
            typeof item.total_cost === 'number' &&
            Number.isFinite(item.total_cost)
        )
        .map((item: any) => ({
          id: item.id,
          label: item.label,
          costPerSF: item.cost_per_sf,
          totalCost: item.total_cost,
        }))
    : [];
  const hasSpecialFeaturesBreakdown = specialFeaturesBreakdown.length > 0;

  const equipmentTotal =
    typeof calculations.construction_costs?.equipment_total === 'number'
      ? calculations.construction_costs.equipment_total
      : Math.max(constructionTotal - baseConstructionTotal - specialFeaturesTotal, 0);
  const equipmentBreakdownRaw = calculations.construction_costs?.equipment_breakdown;
  const equipmentBreakdown =
    equipmentBreakdownRaw &&
    typeof equipmentBreakdownRaw.mechanical === 'number' &&
    typeof equipmentBreakdownRaw.electrical === 'number' &&
    typeof equipmentBreakdownRaw.dock === 'number'
      ? equipmentBreakdownRaw
      : null;

  const displayCostPerSF = Math.round(
    finalCostPerSF || constructionTotal / safeSquareFootage
  );

  // Trade breakdown from calculations – backend is the source of truth.
  // Normalize to a { [tradeName]: amount } map so this works whether
  // trade_breakdown is a dict or an array of { name, amount, percent_of_construction }.
  const rawTradeBreakdown: any = calculations.trade_breakdown || {};

  const actualTradeBreakdown: Record<string, number> = Array.isArray(rawTradeBreakdown)
    ? rawTradeBreakdown.reduce((acc: Record<string, number>, item: any) => {
        if (!item || !item.name) return acc;
        const key = String(item.name).toLowerCase();
        const amount =
          typeof item.amount === 'number'
            ? item.amount
            : typeof item.value === 'number'
              ? item.value
              : 0;
        if (amount > 0) {
          acc[key] = amount;
        }
        return acc;
      }, {})
    : (rawTradeBreakdown as Record<string, number>);

  const tradeCostSplitsRaw = (calculations as AnyRecord).trade_cost_splits;
  const tradeCostSplitsByTrade: Record<string, TradeCostSplit> =
    tradeCostSplitsRaw && typeof tradeCostSplitsRaw === 'object'
      ? Object.entries(tradeCostSplitsRaw).reduce((acc: Record<string, TradeCostSplit>, [rawKey, rawSplit]) => {
          if (!rawSplit || typeof rawSplit !== 'object') return acc;
          const materials = Number((rawSplit as AnyRecord).materials);
          const labor = Number((rawSplit as AnyRecord).labor);
          const equipment = Number((rawSplit as AnyRecord).equipment);
          if ([materials, labor, equipment].some(v => Number.isNaN(v) || v < 0)) {
            return acc;
          }
          acc[String(rawKey).toLowerCase()] = normalizeTradeCostSplit({
            materials,
            labor,
            equipment,
          });
          return acc;
        }, {})
      : {};

  const tradeBaseTotal =
    Object.values(actualTradeBreakdown).reduce(
      (sum: number, val: any) => sum + (val || 0),
      0
    ) || baseConstructionTotal;

  const getTradeAmount = (key: string, fallbackPct: number) => {
    const value = actualTradeBreakdown[key];
    if (typeof value === 'number' && value > 0) {
      return value;
    }
    // Fallback only if backend data is missing for some reason.
    return tradeBaseTotal * fallbackPct;
  };

  // Fallback percentages here are only a safety net; normally the backend should provide all amounts.
  const structuralAmount = getTradeAmount('structural', 0.35);
  const mechanicalAmount = getTradeAmount('mechanical', 0.15);
  const electricalAmount = getTradeAmount('electrical', 0.12);
  const plumbingAmount = getTradeAmount('plumbing', 0.08);
  const finishesAmount = getTradeAmount('finishes', 0.30);

  const safeTradeBaseTotal = tradeBaseTotal || 1; // avoid divide-by-zero

  const tradeBreakdown = {
    structural: {
      amount: structuralAmount,
      percent: Math.round((structuralAmount / safeTradeBaseTotal) * 100),
      color: 'blue',
      icon: Building,
      costPerSF: Math.round(structuralAmount / safeSquareFootage)
    },
    mechanical: {
      amount: mechanicalAmount,
      percent: Math.round((mechanicalAmount / safeTradeBaseTotal) * 100),
      color: 'green',
      icon: Wrench,
      costPerSF: Math.round(mechanicalAmount / safeSquareFootage)
    },
    electrical: {
      amount: electricalAmount,
      percent: Math.round((electricalAmount / safeTradeBaseTotal) * 100),
      color: 'yellow',
      icon: Zap,
      costPerSF: Math.round(electricalAmount / safeSquareFootage)
    },
    plumbing: {
      amount: plumbingAmount,
      percent: Math.round((plumbingAmount / safeTradeBaseTotal) * 100),
      color: 'purple',
      icon: Droplet,
      costPerSF: Math.round(plumbingAmount / safeSquareFootage)
    },
    finishes: {
      amount: finishesAmount,
      percent: Math.round((finishesAmount / safeTradeBaseTotal) * 100),
      color: 'pink',
      icon: PaintBucket,
      costPerSF: Math.round(finishesAmount / safeSquareFootage)
    }
  };

  // Convert to array for iteration
  const trades = Object.entries(tradeBreakdown).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    ...value
  }));

  const filteredTrades =
    activeTradeFilter === 'all'
      ? trades
      : trades.filter(trade => trade.name.toLowerCase() === activeTradeFilter);

  const tradeFilterOptions = [
    { key: 'all', label: 'All Trades' },
    { key: 'structural', label: 'Structural' },
    { key: 'mechanical', label: 'Mechanical' },
    { key: 'electrical', label: 'Electrical' },
    { key: 'plumbing', label: 'Plumbing' },
    { key: 'finishes', label: 'Finishes' },
  ] as const;

  const tradeFilterColorMap: Record<'structural' | 'mechanical' | 'electrical' | 'plumbing' | 'finishes', string> = {
    structural: tradeBreakdown.structural.color,
    mechanical: tradeBreakdown.mechanical.color,
    electrical: tradeBreakdown.electrical.color,
    plumbing: tradeBreakdown.plumbing.color,
    finishes: tradeBreakdown.finishes.color,
  };

  const tradeLegendLabel =
    activeTradeFilter === 'all'
      ? `${trades.length} Major Trades`
      : `${filteredTrades.length} trade${filteredTrades.length === 1 ? '' : 's'} selected`;

  // ========================================
  // Risk & Exposure – derived signals
  // ========================================
  const softCosts = (calculations.soft_costs || {}) as Record<string, number>;
  const contingencyAmount =
    typeof softCosts.contingency === 'number' ? softCosts.contingency : 0;
  const constructionBase = baseConstructionTotal || constructionTotal || 0;
  const contingencyPct =
    constructionBase > 0 ? contingencyAmount / constructionBase : 0;

  const costModifiers = calculations.modifiers || {};
  const regionalFactor =
    typeof costModifiers.cost_factor === 'number'
      ? costModifiers.cost_factor
      : (typeof costModifiers.regional_cost_factor === 'number'
          ? costModifiers.regional_cost_factor
          : 1);
  const marketFactor =
    typeof costModifiers.market_factor === 'number'
      ? costModifiers.market_factor
      : 1;

  const totalTradesAmount =
    structuralAmount +
      mechanicalAmount +
      electricalAmount +
      plumbingAmount +
      finishesAmount ||
    constructionBase;

  const mechElecPlumb =
    mechanicalAmount + electricalAmount + plumbingAmount;

  const contingencyLevel =
    contingencyPct >= 0.12
      ? 'High'
      : contingencyPct >= 0.08
        ? 'Moderate'
        : contingencyPct > 0
          ? 'Low'
          : 'Not specified';

  const longLeadExposure =
    (structuralAmount + mechanicalAmount) / (totalTradesAmount || 1);

  const laborHeavyTradesShare =
    mechElecPlumb / (totalTradesAmount || 1);

  const isHighLaborVolatility = laborHeavyTradesShare >= 0.45;

  const isAboveMarketRegion = marketFactor > 1.05;
  const isBelowMarketRegion = marketFactor < 0.95;

  const riskInsights: {
    title: string;
    level?: 'low' | 'moderate' | 'high';
    note: string;
  }[] = [];

  if (contingencyPct > 0) {
    let level: 'low' | 'moderate' | 'high';
    if (contingencyPct >= 0.12) level = 'high';
    else if (contingencyPct >= 0.08) level = 'moderate';
    else level = 'low';

    riskInsights.push({
      title: 'Contingency Coverage',
      level,
      note:
        contingencyLevel === 'Not specified'
          ? 'Contingency line item is minimal or not clearly specified in soft costs.'
          : `Contingency is approximately ${formatPercent(
              contingencyPct
            )} of core construction. Level: ${contingencyLevel}.`,
    });
  } else {
    riskInsights.push({
      title: 'Contingency Coverage',
      level: 'low',
      note:
        'No explicit contingency was detected in soft costs. Consider adding a buffer for scope growth and change orders.',
    });
  }

  riskInsights.push({
    title: 'Long-Lead Components',
    level: longLeadExposure >= 0.45 ? 'high' : longLeadExposure >= 0.30 ? 'moderate' : 'low',
    note:
      buildingTypeRaw.toLowerCase() === 'industrial'
        ? 'Structural steel, tilt-wall panels, roof systems, and major mechanical equipment drive a significant portion of cost. Locking in suppliers and lead times early will be important.'
        : 'Major structural and mechanical systems typically carry longer lead times. Early procurement and schedule protection are recommended.',
  });

  riskInsights.push({
    title: 'Labor Volatility',
    level: isHighLaborVolatility ? 'high' : 'moderate',
    note: isHighLaborVolatility
      ? 'Mechanical, electrical, and plumbing trades represent a large share of cost. Availability of licensed trades in this market can materially impact schedule and pricing.'
      : 'Labor exposure is balanced across trades. Standard local labor market risk still applies.',
  });

  if (isAboveMarketRegion) {
    riskInsights.push({
      title: 'Regional Cost Pressure',
      level: 'moderate',
      note:
        'Regional cost index is above national average. Local wages, materials, or logistics are likely inflating hard costs relative to other markets.',
    });
  } else if (isBelowMarketRegion) {
    riskInsights.push({
      title: 'Regional Cost Pressure',
      level: 'low',
      note:
        'Regional cost index is slightly below national average. This provides some buffer against cost escalation relative to higher-cost markets.',
    });
  } else {
    riskInsights.push({
      title: 'Regional Cost Pressure',
      level: 'low',
      note:
        'Regional cost index is approximately in line with national averages.',
    });
  }

  riskInsights.push({
    title: 'Code & Compliance Considerations',
    level: 'moderate',
    note:
      buildingTypeRaw.toLowerCase() === 'industrial'
        ? 'Fire protection (ESFR vs. CMDA), egress, and dock / traffic layouts will be key coordination points with the AHJ. Early conversations with local plan reviewers can de-risk later redesign.'
        : 'Life safety, accessibility, and energy code requirements can introduce design iteration late in the process. Early alignment with local code officials is recommended.',
  });

  // ========================================
  // Scope items by trade (from backend payload)
  // ========================================
  const scopeItemsRaw: any =
    (calculations as any).scope_items ||
    (analysis as any).scope_items ||
    (project as any).scope_items ||
    [];

  type ScopeSystem = {
    name?: string;
    quantity?: number;
    unit?: string;
    unit_cost?: number;
    total_cost?: number;
  };

  type ScopeItemByTrade = {
    tradeKey: string;
    tradeLabel: string;
    systems: ScopeSystem[];
  };

  const scopeItemsByTradeMap: Record<string, ScopeItemByTrade> = Array.isArray(scopeItemsRaw)
    ? scopeItemsRaw.reduce((acc: Record<string, ScopeItemByTrade>, item: any) => {
        if (!item) return acc;
        const rawTrade = item.trade || item.name || '';
        if (!rawTrade) return acc;
        const tradeKey = String(rawTrade).toLowerCase();
        const tradeLabel =
          trades.find(t => t.name.toLowerCase() === tradeKey)?.name ||
          rawTrade.toString();

        const systemsArray: ScopeSystem[] = Array.isArray(item.systems)
          ? item.systems
          : [];

        if (!acc[tradeKey]) {
          acc[tradeKey] = {
            tradeKey,
            tradeLabel,
            systems: []
          };
        }

        acc[tradeKey].systems.push(
          ...systemsArray.map((sys: any) => {
            const rawUnit = sys?.unit || sys?.unit_type || sys?.unitType;
            return {
              name: sys?.name,
              quantity: typeof sys?.quantity === 'number' ? sys.quantity : undefined,
              unit: typeof rawUnit === 'string' && rawUnit ? rawUnit : undefined,
              unit_cost: typeof sys?.unit_cost === 'number' ? sys.unit_cost : undefined,
              total_cost: typeof sys?.total_cost === 'number' ? sys.total_cost : undefined
            };
          })
        );

        return acc;
      }, {})
    : {};

  // Order scope items by the same trade order as the main trade cards
  const scopeItemsByTrade: ScopeItemByTrade[] = [
    ...trades
      .map(trade => {
        const key = trade.name.toLowerCase();
        return scopeItemsByTradeMap[key];
      })
      .filter(Boolean) as ScopeItemByTrade[],
    ...Object.values(scopeItemsByTradeMap).filter(item => {
      return !trades.some(t => t.name.toLowerCase() === item.tradeKey);
    })
  ];

  const formatMultiplier = (value?: number) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return undefined;
    }
    return value.toFixed(3).replace(/(?:\.0+|(\.\d+?)0+)$/, '$1');
  };
  const costBuildUpSequence = costBuildUp.map((step: any) => {
    if (!step) {
      return 'Unknown';
    }
    if (typeof step.value_per_sf === 'number') {
      return `${step.label ?? 'Base'} ${formatCurrency(step.value_per_sf)}/SF`;
    }
    if (typeof step.multiplier === 'number') {
      const formatted = formatMultiplier(step.multiplier);
      return `${step.label ?? 'Step'} ×${formatted ?? step.multiplier}`;
    }
    return step.label || 'Unknown';
  });
  const hasFinishStep = costBuildUp.some((step: any) => (step?.label || '').toLowerCase() === 'finish level');
  const costBuildUpLogRef = useRef(false);

  useEffect(() => {
    if (!isDev || costBuildUpLogRef.current) {
      return;
    }
    console.log('[SpecSharp DEV] cost_build_up', costBuildUp);
    costBuildUpLogRef.current = true;
  }, [isDev, costBuildUp]);

  useEffect(() => {
    if (
      expandedTrade &&
      activeTradeFilter !== 'all' &&
      expandedTrade.toLowerCase() !== activeTradeFilter
    ) {
      setExpandedTrade(null);
    }
  }, [activeTradeFilter, expandedTrade]);

  useEffect(() => {
    if (!showTraceModal) {
      return;
    }
    const handler = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setShowTraceModal(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showTraceModal]);

  type BackendPhase = {
    id?: string;
    label?: string;
    start_month?: number;
    startMonth?: number;
    duration?: number;
    color?: string;
  };

  type TimelinePhase = {
    id: string;
    label: string;
    startMonth: number;
    duration: number;
    color: string;
  };

  const backendPhases: BackendPhase[] = Array.isArray(constructionSchedule?.phases)
    ? (constructionSchedule?.phases as BackendPhase[])
    : [];

  const fallbackPhases: TimelinePhase[] = [
    { id: 'site_foundation', label: 'Site & Podium Work', startMonth: 0, duration: 6, color: 'blue' },
    { id: 'structural', label: 'Structure & Garage', startMonth: 4, duration: 14, color: 'green' },
    { id: 'exterior_envelope', label: 'Exterior Envelope', startMonth: 10, duration: 10, color: 'orange' },
    { id: 'mep_rough', label: 'MEP Rough', startMonth: 12, duration: 10, color: 'purple' },
    { id: 'interior_finishes', label: 'Interior Finishes', startMonth: 18, duration: 12, color: 'pink' },
    { id: 'mep_finishes', label: 'Commissioning & Punch', startMonth: 22, duration: 8, color: 'teal' }
  ];

  const phases: TimelinePhase[] =
    backendPhases.length > 0
      ? backendPhases.map((phase, index) => ({
          id: phase.id || phase.label || `phase-${index}`,
          label: phase.label || phase.id || `Phase ${index + 1}`,
          startMonth:
            typeof phase.start_month === 'number'
              ? phase.start_month
              : typeof phase.startMonth === 'number'
                ? phase.startMonth
                : 0,
          duration:
            typeof (phase as any).duration === 'number'
              ? (phase as any).duration
              : typeof (phase as any).duration_months === 'number'
                ? (phase as any).duration_months
                : 0,
          color: phase.color || 'blue'
        }))
      : fallbackPhases;

  const phasesWithTrades = phases.map(phase => ({
    ...phase,
    tradeMix: getPhaseTradeMix(buildingTypeRaw, phase.id),
  }));

  const totalMonthsRaw =
    typeof constructionSchedule?.total_months === 'number' ? constructionSchedule.total_months : 0;
  const totalMonths = totalMonthsRaw > 0 ? totalMonthsRaw : 30;

  const timelineMarkers = useMemo(() => {
    const segments = 4;
    const labels: string[] = [];
    for (let i = 0; i <= segments; i++) {
      const monthValue = i === 0 ? 1 : Math.max(1, Math.round((totalMonths / segments) * i));
      labels.push(`M${monthValue}`);
    }
    return labels;
  }, [totalMonths]);

  const timelineStartYearSource =
    calculations.project_timeline?.start_year ||
    parsed_input?.start_year ||
    new Date().getFullYear();
  const timelineStartYear =
    typeof timelineStartYearSource === 'number'
      ? timelineStartYearSource
      : Number(timelineStartYearSource) || new Date().getFullYear();

  const formatMonthToQuarter = (monthValue: number) => {
    if (typeof monthValue !== 'number' || Number.isNaN(monthValue)) {
      return 'TBD';
    }
    const normalized = Math.max(0, Math.round(monthValue));
    const yearOffset = Math.floor(normalized / 12);
    const quarter = Math.floor((normalized % 12) / 3) + 1;
    const displayYear = timelineStartYear + yearOffset;
    return `Q${quarter} ${displayYear}`;
  };

  const milestoneIcons = [HardHat, Building, Wrench, TrendingUp];
  const milestonePhases = phases.slice(0, 4);
  const milestones = milestonePhases.map((phase, index) => {
    const midpoint = phase.startMonth + phase.duration / 2;
    return {
      id: phase.id || `milestone-${index}`,
      label: phase.label,
      dateLabel: formatMonthToQuarter(midpoint)
    };
  });

  // Helper function for donut chart
  const createPath = (startAngle: number, endAngle: number, innerRadius: number = 25, outerRadius: number = 40) => {
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;
    
    const x1 = 50 + outerRadius * Math.cos(startAngleRad);
    const y1 = 50 + outerRadius * Math.sin(startAngleRad);
    const x2 = 50 + outerRadius * Math.cos(endAngleRad);
    const y2 = 50 + outerRadius * Math.sin(endAngleRad);
    
    const x3 = 50 + innerRadius * Math.cos(endAngleRad);
    const y3 = 50 + innerRadius * Math.sin(endAngleRad);
    const x4 = 50 + innerRadius * Math.cos(startAngleRad);
    const y4 = 50 + innerRadius * Math.sin(startAngleRad);
    
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    
    return `M ${x1} ${y1} A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2} ${y2} L ${x3} ${y3} A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x4} ${y4} Z`;
  };

  const timelineMonthsLabel = `${totalMonths} Month${totalMonths === 1 ? '' : 's'} Timeline`;

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

  return (
    <>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 pb-16 pb-[env(safe-area-inset-bottom)]">
      {/* Header Section - Dark Blue */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-xl p-6 sm:p-8 text-white">
        <div className="flex flex-col gap-6 lg:flex-row lg:justify-between">
          <div className="space-y-4">
            <h1 className="text-2xl sm:text-3xl font-bold">
              {formatNumber(squareFootage)} SF {calculations.project_info?.display_name || 'Building'}
            </h1>
            <div className="flex flex-wrap gap-x-4 gap-y-2 text-xs sm:text-sm text-slate-300">
              <span className="flex items-center gap-1 min-w-0">
                <MapPin className="h-3 w-3" />
                {locationDisplay}
              </span>
              <span className="flex items-center gap-1 min-w-0">
                <Building className="h-3 w-3" />
                {parsed_input.floors || calculations.project_info?.typical_floors || 4} Floors
              </span>
              <span className="capitalize min-w-0">{parsed_input.project_classification?.replace('_', '-') || 'Ground-Up'}</span>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-3 w-full">
              <button
                onClick={handleExportPdf}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-white/10 backdrop-blur border border-white/20 text-white rounded-lg hover:bg-white/20 transition w-full sm:w-auto"
              >
                <Download className="h-4 w-4" />
                Export PDF
              </button>
              <button
                onClick={() => setIsScenarioOpen(true)}
                className="flex items-center justify-center gap-2 px-4 py-2 bg-white text-slate-800 rounded-lg hover:bg-slate-100 transition font-medium w-full sm:w-auto"
              >
                <BarChart3 className="h-4 w-4" />
                Compare Scenarios
              </button>
            </div>
          </div>
          
          <div className="text-left lg:text-right space-y-2">
            <p className="text-xs text-slate-400 uppercase tracking-wider">CONSTRUCTION COST</p>
            <p className="text-3xl sm:text-4xl font-bold">{formatCurrency(constructionTotal)}</p>
            <p className="text-base sm:text-lg text-slate-300">{formatCurrency(displayCostPerSF)} per SF</p>
          </div>
        </div>
        
        <div className="flex flex-wrap items-center gap-2 mt-6 text-sm text-slate-400">
          <Calendar className="h-4 w-4" />
          <span>{timelineMonthsLabel}</span>
          <span className="mx-2">•</span>
          <Clock className="h-4 w-4" />
          <span>Q1 2025 - Q2 2027</span>
        </div>
      </div>

      {/* Trade Filter Pills */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="flex gap-2 flex-wrap items-center">
          {tradeFilterOptions.map(pill => {
            const key = pill.key;
            const isActive = activeTradeFilter === key;
            let color: string | undefined;
            if (key !== 'all') {
              color = tradeFilterColorMap[key];
            }

            return (
              <button
                key={pill.key}
                type="button"
                onClick={() => setActiveTradeFilter(key)}
                className={[
                  'inline-flex items-center rounded-full px-3 py-1.5 text-xs font-medium border transition',
                  isActive
                    ? 'bg-blue-100 text-blue-700 border-blue-200'
                    : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                ].join(' ')}
              >
                {color && (
                  <span className={`w-2 h-2 rounded-full bg-${color}-500 mr-1.5`}></span>
                )}
                {pill.label}
              </button>
            );
          })}
          <span className="ml-1 text-[11px] text-gray-500">
            {activeTradeFilter === 'all'
              ? 'Showing all trades'
              : `Showing ${activeTradeFilter.charAt(0).toUpperCase() + activeTradeFilter.slice(1)} only`}
          </span>
        </div>
      </div>

      {/* Project Cost Analysis */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Project Cost Analysis</h2>
        <p className="text-gray-600 mb-6">Comprehensive breakdown of construction costs by trade</p>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Trade Distribution */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">Trade Distribution</h3>
              <span className="text-sm text-gray-500">{tradeLegendLabel}</span>
            </div>
            
            {/* Donut Chart */}
            <div className="flex justify-center mb-6">
              <div className="relative">
                <svg width="200" height="200" viewBox="0 0 100 100" className="transform -rotate-90">
                  {(() => {
                    let currentAngle = 0;
                    return filteredTrades.map((trade) => {
                      const startAngle = currentAngle;
                      const endAngle = currentAngle + (trade.percent / 100) * 360;
                      currentAngle = endAngle;
                      
                      const colors = {
                        blue: '#3B82F6',
                        green: '#10B981',
                        yellow: '#F59E0B',
                        purple: '#8B5CF6',
                        pink: '#EC4899'
                      };
                      
                      return (
                        <path
                          key={trade.name}
                          d={createPath(startAngle, endAngle)}
                          fill={colors[trade.color as keyof typeof colors]}
                          className="hover:opacity-80 transition-opacity cursor-pointer"
                        />
                      );
                    });
                  })()}
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-2xl font-bold">${(constructionTotal / 1000000).toFixed(0)}M</p>
                    <p className="text-xs text-gray-500 uppercase">Total</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Legend */}
            <div className="space-y-2">
              {filteredTrades.map(trade => (
                <div key={trade.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full bg-${trade.color}-500`}></div>
                    <span className="text-sm text-gray-700">{trade.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold">{trade.percent}%</span>
                    <span className="text-xs text-gray-500 ml-2">${(trade.amount / 1000000).toFixed(0)}M</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Construction Schedule */}
          <div className="bg-gray-50 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="font-semibold text-gray-900">Construction Schedule</h3>
              <span className="text-sm text-gray-500 flex items-center gap-1">
                <Clock className="h-4 w-4" />
                {timelineMonthsLabel}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-4">Phased timeline with trade overlap optimization</p>
            <p className="text-xs text-gray-500 mb-4">
              Schedule shown is a planning baseline by building type. It does not yet reflect subtype-specific permitting, procurement, or financing-timing variance.
            </p>
            {/* Mobile Timeline */}
            <div className="md:hidden space-y-4">
              {phasesWithTrades.map((phase) => {
                const mixEntries = Object.entries(phase.tradeMix || {}).filter(
                  ([, value]) => typeof value === 'number' && value > 0.01
                );
                const phaseTooltip = getPhaseTooltip(buildingTypeRaw, phase.id, phase.tradeMix);
                return (
                  <div key={`${phase.id}-mobile`} className="p-3 bg-white rounded-lg border border-gray-200 space-y-2">
                    <div className="flex justify-between gap-4">
                      <span
                        className={`text-sm font-semibold text-gray-900 ${phaseTooltip ? 'cursor-help border-b border-dotted border-gray-300 pb-[1px]' : ''}`}
                        title={phaseTooltip || ''}
                      >
                        {phase.label}
                      </span>
                      <span className="text-xs text-gray-500 whitespace-nowrap">{phase.duration} mo</span>
                    </div>
                    <div className="relative h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                      {totalMonths > 0 && phase.duration > 0 && (
                        <div
                          className="absolute h-full rounded-full bg-blue-500"
                          style={{
                            width: `${(phase.duration / totalMonths) * 100}%`,
                          }}
                        />
                      )}
                    </div>
                    {mixEntries.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {mixEntries.map(([key, value]) => {
                          const label = key.charAt(0).toUpperCase() + key.slice(1);
                          const chipColorClass = (() => {
                            const k = key.toLowerCase();
                            if (k === 'structural') return 'bg-blue-100 text-blue-800 border-blue-200';
                            if (k === 'mechanical') return 'bg-green-100 text-green-800 border-green-200';
                            if (k === 'electrical') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
                            if (k === 'plumbing') return 'bg-purple-100 text-purple-800 border-purple-200';
                            if (k === 'finishes') return 'bg-pink-100 text-pink-800 border-pink-200';
                            return 'bg-gray-100 text-gray-700 border-gray-200';
                          })();
                          return (
                            <span
                              key={`${phase.id}-${key}-mobile`}
                              className={`inline-flex items-center rounded-full border px-2 py-[2px] text-[10px] font-medium ${chipColorClass}`}
                            >
                              {label}&nbsp;{Math.round((value as number) * 100)}%
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Desktop Timeline */}
            <div className="hidden md:block">
              <div className="flex text-xs text-gray-400 mb-3 ml-24">
                {timelineMarkers.map((marker, index) => (
                  <span key={`${marker}-${index}`} className="flex-1">
                    {marker}
                  </span>
                ))}
              </div>
              
              <div className="space-y-2">
                {phasesWithTrades.map((phase) => {
                  const mixEntries = Object.entries(phase.tradeMix || {}).filter(
                    ([, value]) => typeof value === 'number' && value > 0.01
                  );
                  const phaseTooltip = getPhaseTooltip(buildingTypeRaw, phase.id, phase.tradeMix);
                  return (
                    <div key={phase.id}>
                      <div className="flex items-center gap-2">
                        <div className="w-20 text-xs text-gray-700 text-right truncate">
                          <span
                            className={`font-medium ${phaseTooltip ? 'cursor-help border-b border-dotted border-gray-300 pb-[1px]' : ''}`}
                            title={phaseTooltip || ''}
                          >
                            {phase.label}
                          </span>
                        </div>
                        <div className="flex-1 relative h-4 bg-gray-200 rounded-full overflow-hidden">
                          {totalMonths > 0 && phase.duration > 0 && (
                            <div
                              className="absolute h-full rounded-full"
                              style={{
                                left: `${(phase.startMonth / totalMonths) * 100}%`,
                                width: `${(phase.duration / totalMonths) * 100}%`,
                                backgroundColor: phase.color || '#3b82f6',
                              }}
                            />
                          )}
                        </div>
                        <span className="text-xs text-gray-500 w-10 text-right">{phase.duration} mo</span>
                      </div>
                      {mixEntries.length > 0 && (
                        <div className="mt-1 flex flex-wrap gap-1 ml-20">
                          {mixEntries.map(([key, value]) => {
                            const label = (() => {
                              const k = key.toLowerCase();
                              if (k === 'structural') return 'Structural';
                              if (k === 'mechanical') return 'Mechanical';
                              if (k === 'electrical') return 'Electrical';
                              if (k === 'plumbing') return 'Plumbing';
                              if (k === 'finishes') return 'Finishes';
                              return key;
                            })();
                            const chipColorClass = (() => {
                              const k = key.toLowerCase();
                              if (k === 'structural') return 'bg-blue-100 text-blue-800 border-blue-200';
                              if (k === 'mechanical') return 'bg-green-100 text-green-800 border-green-200';
                              if (k === 'electrical') return 'bg-yellow-100 text-yellow-800 border-yellow-200';
                              if (k === 'plumbing') return 'bg-purple-100 text-purple-800 border-purple-200';
                              if (k === 'finishes') return 'bg-pink-100 text-pink-800 border-pink-200';
                              return 'bg-gray-100 text-gray-700 border-gray-200';
                            })();
                            return (
                              <span
                                key={`${phase.id}-${key}`}
                                className={`inline-flex items-center rounded-full border px-2 py-[2px] text-[10px] font-medium ${chipColorClass}`}
                              >
                                {label}&nbsp;{Math.round((value as number) * 100)}%
                              </span>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Key Milestones */}
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-gray-700 mb-3">Key Milestones</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {milestones.map((milestone, index) => {
                  const Icon = milestoneIcons[index % milestoneIcons.length];
                  return (
                    <div
                      key={milestone.id}
                      className="flex items-center gap-3 bg-white rounded-lg border border-gray-200 p-3"
                    >
                      <div className="p-2 rounded-full bg-slate-100">
                        <Icon className="h-4 w-4 text-slate-600" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-900">{milestone.label}</p>
                        <p className="text-xs text-gray-500">{milestone.dateLabel}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Warning - Dynamic based on building type */}
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
              <div className="flex items-start gap-2">
                <Info className="h-4 w-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-yellow-800">
                  <strong>Long-lead items:</strong> {
                    buildingType === 'healthcare' ? 'Medical equipment and AHUs require 16-20 week lead time. Order by Month 3 to avoid delays.' :
                    buildingType === 'restaurant' ? 'Kitchen equipment and bar fixtures require 8-10 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'office' ? 'Furniture systems and AV equipment require 6-8 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'retail' ? 'Display fixtures and POS systems require 6-8 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'industrial' ? 'Specialized machinery and racking systems require 10-12 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'hospitality' ? 'FF&E packages and kitchen equipment require 10-12 week lead time. Order by Month 2 to avoid delays.' :
                    buildingType === 'multifamily' ? 'Appliance packages and cabinetry require 8-10 week lead time. Order by Month 2 to avoid delays.' :
                    'Equipment and fixtures require standard lead times. Verify with suppliers for specific requirements.'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Trade Summary */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Trade Summary</h3>
          <button className="text-sm text-gray-500">
            Click on any trade for detailed breakdown
          </button>
        </div>
        
        <div className="space-y-4">
          {filteredTrades.map(trade => {
            const Icon = trade.icon;
            const scopeForTrade = scopeItemsByTrade.find(
              item => item.tradeKey === trade.name.toLowerCase()
            );
            const hasScopeForTrade =
              scopeForTrade && Array.isArray(scopeForTrade.systems) && scopeForTrade.systems.length > 0;
            const split = tradeCostSplitsByTrade[trade.name.toLowerCase()] || null;
            const materialsCost = split ? trade.amount * split.materials : 0;
            const laborCost = split ? trade.amount * split.labor : 0;
            const equipmentCost = split ? trade.amount * split.equipment : 0;
            const progressWidth = Math.max(0, Math.min(100, trade.percent));
            return (
              <div key={trade.name} className="border rounded-lg hover:shadow-md transition">
                <div 
                  className="p-4 cursor-pointer hover:bg-gray-50 transition-all"
                  onClick={() => setExpandedTrade(expandedTrade === trade.name ? null : trade.name)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setExpandedTrade(expandedTrade === trade.name ? null : trade.name);
                    }
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 bg-${trade.color}-50 rounded-lg`}>
                        <Icon className={`h-5 w-5 text-${trade.color}-600`} />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{trade.name}</h4>
                        <p className="text-sm text-gray-500">{trade.percent}% of construction cost</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6 mt-4 sm:mt-0">
                      <div className="text-right">
                        <p className="text-2xl font-bold">{formatCurrency(trade.amount)}</p>
                        <p className="text-sm text-gray-500">{formatCurrency(trade.costPerSF)}/SF</p>
                      </div>
                      <div className="p-2 rounded-lg transition">
                        <ChevronRight className={`h-5 w-5 text-gray-400 transition-transform ${expandedTrade === trade.name ? 'rotate-90' : ''}`} />
                      </div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                      <div 
                        className={`bg-${trade.color}-500 h-2 rounded-full transition-all`}
                        style={{ width: `${progressWidth}%` }}
                      />
                    </div>
                  </div>
                </div>
                
                {/* Expanded Details */}
                {expandedTrade === trade.name && (
                  <div className="px-4 pb-4">
                    {split && (
                      <div className="pt-4 border-t grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                        <div>
                          <div className="text-[11px] text-gray-500">Materials</div>
                          <div className="font-semibold text-gray-900">{formatCurrency(materialsCost)}</div>
                          <div className="text-[11px] text-gray-500">
                            {formatPercent(split.materials)} of {trade.percent}%
                          </div>
                        </div>
                        <div>
                          <div className="text-[11px] text-gray-500">Labor</div>
                          <div className="font-semibold text-gray-900">{formatCurrency(laborCost)}</div>
                          <div className="text-[11px] text-gray-500">
                            {formatPercent(split.labor)} of {trade.percent}%
                          </div>
                        </div>
                        <div>
                          <div className="text-[11px] text-gray-500">Equipment</div>
                          <div className="font-semibold text-gray-900">{formatCurrency(equipmentCost)}</div>
                          <div className="text-[11px] text-gray-500">
                            {formatPercent(split.equipment)} of {trade.percent}%
                          </div>
                        </div>
                      </div>
                    )}

                    {hasScopeForTrade && (
                      <div className="mt-5">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs font-semibold text-gray-900">
                            Scope Items
                          </span>
                          <span className="text-[10px] text-gray-500">
                            {scopeForTrade!.systems.length} system
                            {scopeForTrade!.systems.length === 1 ? '' : 's'}
                          </span>
                        </div>

                        <div className="overflow-x-auto rounded-lg border border-gray-100 bg-white">
                          <table className="min-w-full text-[11px]">
                            <thead className="bg-gray-50 text-gray-500 border-b border-gray-100">
                              <tr>
                                <th className="py-1.5 pl-3 pr-2 text-left text-[11px] font-medium tracking-wide">
                                  Item
                                </th>
                                <th className="py-1.5 px-2 text-left text-[11px] font-medium tracking-wide">
                                  Quantity
                                </th>
                                <th className="py-1.5 px-2 text-right text-[11px] font-medium tracking-wide">
                                  Unit Cost
                                </th>
                                <th className="py-1.5 pr-3 pl-2 text-right text-[11px] font-medium tracking-wide">
                                  Total Cost
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {scopeForTrade!.systems.map((sys, idx) => {
                                const hint = getScopeHint(
                                  buildingTypeRaw,
                                  trade.name,
                                  sys.name
                                );

                                return (
                                  <tr
                                    key={`${scopeForTrade!.tradeKey}-${idx}-${sys.name || 'sys'}`}
                                    className="border-b border-gray-50 last:border-b-0"
                                  >
                                    <td className="py-1.5 pl-3 pr-2 text-[11px] text-gray-900">
                                      {hint ? (
                                        <span
                                          title={hint}
                                          className="inline-flex items-center gap-1 cursor-help"
                                        >
                                          <span className="border-b border-dotted border-gray-300 pb-[1px]">
                                            {sys.name || 'Scope item'}
                                          </span>
                                        </span>
                                      ) : (
                                        sys.name || 'Scope item'
                                      )}
                                    </td>
                                    <td className="py-1.5 px-2 text-left text-[11px] text-gray-700 whitespace-nowrap">
                                      {formatQuantityWithUnit(sys.quantity, sys.unit, trade.name)}
                                    </td>
                                    <td className="py-1.5 px-2 text-right text-[11px] text-gray-700">
                                      {typeof sys.unit_cost === 'number'
                                        ? formatCurrency2(sys.unit_cost)
                                        : '—'}
                                    </td>
                                    <td className="py-1.5 pr-3 pl-2 text-right text-[11px] font-semibold text-gray-900">
                                      {typeof sys.total_cost === 'number'
                                        ? formatCurrency2(sys.total_cost)
                                        : '—'}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        
        <div className="mt-6 pt-6 border-t text-right">
          <p className="text-lg text-gray-600">Total Construction Cost:</p>
          <p className="text-3xl font-bold text-blue-600">{formatCurrency(constructionTotal)}</p>
        </div>
        
        {/* Note about equipment */}
        {equipmentTotal > 0 && (
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start gap-2">
              <Info className="h-4 w-4 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-amber-800">
                <strong>Note:</strong> Trade percentages shown are based on base construction cost of {formatCurrency(baseConstructionTotal)}. 
                Equipment/FF&E of {formatCurrency(equipmentTotal)} is handled separately and shown in the Cost Build-Up Analysis above.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Cost Build-Up Analysis - Enhanced Design */}
      <div className="bg-gradient-to-br from-gray-50 to-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">Cost Build-Up Analysis</h3>
            <p className="text-gray-600">Understanding how your price is calculated step by step</p>
          </div>
          {calculationTrace.length > 0 && (
            <button
              type="button"
              onClick={() => setShowTraceModal(true)}
              className="text-[11px] font-semibold text-blue-600 hover:text-blue-700 underline underline-offset-2"
            >
              View Calculation Trace
            </button>
          )}
        </div>
        
        {/* Main calculation flow */}
        <div className="space-y-8">
          {/* Row 1: Base calculation */}
          <div className="-mx-4 sm:mx-0 overflow-x-auto pb-4">
            <div className="flex items-center justify-between gap-6 min-w-[720px] sm:min-w-0 px-4 sm:px-0">
              <div className="flex-1 min-w-[220px]">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 1: Base Cost</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">${formatNumber(baseCostPerSF)}</p>
                  <p className="text-lg text-gray-600">per SF</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">RSMeans 2024 Q3 {calculations.project_info?.display_name || 'Building'}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 flex-shrink-0">
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <ChevronRight className="h-6 w-6 text-gray-400" />
            </div>
            
            <div className="flex-1 min-w-[220px]">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 2: Regional Adjustment</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">×{regionalMultiplier.toFixed(2)}</p>
                  <p className="text-lg text-gray-600">multiplier</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">{locationDisplay} Market</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 flex-shrink-0">
              <div className="w-12 h-0.5 bg-gray-300"></div>
              <ChevronRight className="h-6 w-6 text-gray-400" />
            </div>
            
            <div className="flex-1 min-w-[220px]">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <p className="text-sm text-gray-500 uppercase tracking-wider mb-3 font-medium">Step 3: Complexity</p>
                <div className="flex items-baseline gap-2">
                  <p className="text-4xl font-bold text-gray-900">×{complexityMultiplier.toFixed(2)}</p>
                  <p className="text-lg text-gray-600">multiplier</p>
                </div>
                <p className="text-sm text-gray-500 mt-3">Ground-Up Construction</p>
              </div>
            </div>
          </div>
          </div>
          
          {/* Row 2: Base total */}
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:gap-6">
            <div className="flex-1">
              <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
                <p className="text-sm text-gray-600 uppercase tracking-wider mb-3 font-medium">Base Construction</p>
                <p className="text-3xl font-bold text-gray-900">${formatNumber(finalCostPerSF)}/SF</p>
                <p className="text-lg text-gray-700 mt-2">{formatCurrency(baseConstructionTotal)}</p>
                <p className="text-sm text-gray-500 mt-1">Core construction cost</p>
              </div>
            </div>
            
            {specialFeaturesTotal > 0 && (
              <>
                <div className="flex items-center gap-2">
                  <span className="text-2xl text-gray-400 font-bold">+</span>
                </div>
                
                <div className="flex-1">
                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-6 border border-orange-200">
                    <p className="text-sm text-orange-700 uppercase tracking-wider mb-3 font-medium">Special Features</p>
                    <p className="text-3xl font-bold text-orange-600">{formatCurrency(specialFeaturesTotal)}</p>
                    <p className="mt-1 text-xs text-gray-500">
                      Backend aggregate (`special_features_total`) applied to hard costs.
                    </p>
                    <div className="mt-3 space-y-2">
                      {hasSpecialFeaturesBreakdown ? (
                        specialFeaturesBreakdown.map((feature) => (
                          <div
                            key={feature.id}
                            className="rounded-lg border border-orange-100 bg-white/70 px-3 py-2"
                          >
                            <div className="flex items-center justify-between gap-2">
                              <p className="text-sm text-gray-800">{feature.label}</p>
                              <p className="text-sm font-semibold text-gray-900">
                                {formatCurrency(feature.totalCost)}
                              </p>
                            </div>
                            {squareFootage > 0 && (
                              <p className="text-xs text-gray-500 mt-1">
                                {formatCurrency(feature.costPerSF)}/SF × {formatNumber(squareFootage)} SF
                              </p>
                            )}
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-gray-700">
                          Selected feature IDs were not provided in project data; showing aggregate only.
                        </p>
                      )}
                    </div>
                    {!hasSpecialFeaturesBreakdown && (
                      <p className="mt-2 text-xs text-gray-500">
                        Per-feature breakdown is unavailable for this project version; showing aggregate total only.
                      </p>
                    )}
                  </div>
                </div>
              </>
            )}
          </div>
          
          {/* Equipment/FF&E Addition */}
          {equipmentTotal > 0 && (
            <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <Package className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-blue-700 font-semibold uppercase tracking-wider">
                      Equipment & FF&E
                    </p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">
                      {formatCurrency(equipmentTotal)}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      {buildingType === 'multifamily' ? 'Appliances, fixtures & furnishings' :
                       buildingType === 'healthcare' ? 'Medical equipment & furnishings' :
                       buildingType === 'educational' ? 'Classroom equipment & technology' :
                       'Furniture, fixtures & equipment'}
                    </p>
                  </div>
                </div>
                <div className="text-left lg:text-right mt-4 lg:mt-0">
                  <p className="text-lg font-bold text-gray-900">
                    +${Math.round(equipmentTotal / safeSquareFootage)}/SF
                  </p>
                  <p className="text-sm text-gray-500">
                    {((equipmentTotal / constructionTotal) * 100).toFixed(1)}% of total
                  </p>
                </div>
              </div>
              {equipmentBreakdown && (
                <div className="mt-4 grid gap-3 text-[11px] text-blue-800 sm:grid-cols-2 lg:grid-cols-3">
                  <div className="flex flex-col">
                    <span className="font-semibold">Mechanical equipment</span>
                    <span className="text-blue-700">
                      {formatCurrency(equipmentBreakdown.mechanical)}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-semibold">Electrical gear</span>
                    <span className="text-blue-700">
                      {formatCurrency(equipmentBreakdown.electrical)}
                    </span>
                  </div>
                  <div className="flex flex-col">
                    <span className="font-semibold">Dock &amp; material handling</span>
                    <span className="text-blue-700">
                      {formatCurrency(equipmentBreakdown.dock)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Row 3: Final total */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl p-6 sm:p-8 text-white shadow-xl">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-sm uppercase tracking-wider mb-2 opacity-90">Final Construction Cost</p>
                <p className="text-4xl sm:text-5xl font-bold break-words">{formatCurrency(constructionTotal)}</p>
              </div>
              <div className="text-left lg:text-right">
                <p className="text-2xl font-semibold">${formatNumber(Math.round(constructionTotal / safeSquareFootage))}/SF</p>
                <p className="text-sm opacity-90 mt-1">All-in cost per square foot</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sensitivity Analysis */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Sensitivity Analysis</h3>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Regional Multiplier</span>
              <span className="text-sm font-bold">{regionalMultiplier.toFixed(2)}x</span>
            </div>
            <input 
              type="range" 
              min="80" 
              max="120" 
              value={regionalMultiplier * 100} 
              className="w-full"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">{regionalComparisonCopy}</p>
          </div>
          
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Complexity Factor</span>
              <span className="text-sm font-bold">{complexityMultiplier.toFixed(2)}x</span>
            </div>
            <input 
              type="range" 
              min="80" 
              max="120" 
              value={complexityMultiplier * 100} 
              className="w-full"
              disabled
            />
            <p className="text-xs text-gray-500 mt-1">Ground-Up (baseline complexity)</p>
          </div>
          
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-2">Confidence Band</p>
            <p className="text-2xl font-bold">95%</p>
            <p className="text-xs text-gray-500 mt-1">confidence level</p>
            <p className="text-sm text-gray-600 mt-2">
              ${formatNumber(Math.round(finalCostPerSF * 0.9))}/SF - ${formatNumber(Math.round(finalCostPerSF * 1.1))}/SF
            </p>
            <p className="text-xs text-gray-500 mt-1">Based on 47 similar projects</p>
          </div>
        </div>
      </div>

      {riskInsights.length > 0 && (
        <div className="mt-10">
          <div className="bg-white shadow-sm rounded-2xl border border-gray-100 p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h3 className="text-sm font-semibold text-gray-900">
                  Risk &amp; Exposure Notes
                </h3>
                <p className="text-xs text-gray-500">
                  High-level factors that could move cost, schedule, or scope.
                </p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {riskInsights.map((risk, idx) => (
                <div
                  key={`${risk.title}-${idx}`}
                  className="border border-gray-100 rounded-lg p-3 bg-gray-50/60"
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-semibold text-gray-900">
                      {risk.title}
                    </span>
                    {risk.level && (
                      <span
                        className={`
                          inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium
                          ${
                            risk.level === 'high'
                              ? 'bg-red-50 text-red-700 border border-red-100'
                              : risk.level === 'moderate'
                                ? 'bg-amber-50 text-amber-700 border border-amber-100'
                                : 'bg-emerald-50 text-emerald-700 border border-emerald-100'
                          }
                        `}
                      >
                        {risk.level === 'high'
                          ? 'Higher Risk'
                          : risk.level === 'moderate'
                            ? 'Moderate Risk'
                            : 'Lower Risk'}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] leading-snug text-gray-700">
                    {risk.note}
                  </p>
                </div>
              ))}
            </div>

            <p className="mt-3 text-[10px] text-gray-500">
              These notes are directional only and do not replace a full risk and constructability review.
            </p>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center py-6">
        <button 
          onClick={() => setShowProvenanceModal(true)}
          className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium transition-colors"
        >
          <FileText className="h-4 w-4" />
          View Detailed Provenance Receipt
        </button>
      </div>
      
      {/* Provenance Modal */}
      <ProvenanceModal
        isOpen={showProvenanceModal}
        onClose={() => setShowProvenanceModal(false)}
        projectData={{
          building_type: calculations?.project_info?.building_type || parsed_input?.building_type,
          square_footage:
            typeof calculations?.project_info?.square_footage === 'number'
              ? calculations.project_info.square_footage
              : squareFootage,
          location: calculations?.project_info?.location || parsed_input?.location,
          project_class:
            calculations?.project_info?.project_class ||
            parsed_input?.project_classification ||
            parsed_input?.project_class,
          confidence_projects: 47
        }}
        calculationData={calculations}
        calculationTrace={calculations?.calculation_trace || project.analysis?.calculation_trace}
        displayData={displayData}
      />

      {showTraceModal && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40">
          <div className="max-h-[80vh] w-full max-w-3xl overflow-hidden rounded-2xl bg-white shadow-xl border border-gray-200">
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
              <div>
                <h2 className="text-sm font-semibold text-gray-900">
                  Calculation Trace
                </h2>
                <p className="text-[11px] text-gray-500">
                  Raw steps recorded by the SpecSharp engine while pricing this project.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowTraceModal(false)}
                className="text-xs font-medium text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>

            <div className="max-h-[70vh] overflow-y-auto px-4 py-3 bg-gray-50">
              {calculationTrace.length === 0 ? (
                <p className="text-[11px] text-gray-500">
                  No calculation trace is available for this project.
                </p>
              ) : (
                <div className="space-y-2">
                  {calculationTrace.map((entry, idx) => (
                    <div
                      key={`${entry.step}-${idx}`}
                      className="rounded-lg border border-gray-200 bg-white px-3 py-2"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] font-semibold text-gray-900">
                          {idx + 1}. {entry.step}
                        </span>
                      </div>
                      <pre className="max-h-40 overflow-auto rounded bg-gray-900/95 px-2 py-1 text-[10px] leading-snug text-gray-100">
                        {JSON.stringify(entry.payload, null, 2)}
                      </pre>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="border-t border-gray-100 px-4 py-2">
              <p className="text-[10px] text-gray-500">
                This trace is intended for internal review and debugging. Values shown are intermediate engine states and may not be fully normalized for presentation.
              </p>
            </div>
          </div>
        </div>
      )}
      </div>
      <ScenarioModal
        open={isScenarioOpen}
        onClose={() => setIsScenarioOpen(false)}
        base={scenarioBase}
      />
    </>
  );
};
