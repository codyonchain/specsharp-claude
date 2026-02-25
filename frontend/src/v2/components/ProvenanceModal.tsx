import React from 'react';
import { X, FileText, TrendingUp, MapPin, Calculator, Layers, DollarSign, CheckCircle } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';

interface ProvenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: any;
  displayData?: any;
}

export const ProvenanceModal: React.FC<ProvenanceModalProps> = ({
  isOpen,
  onClose,
  analysis,
  displayData,
}) => {
  if (!isOpen) return null;

  const analysisRecord = analysis || {};
  const calc = analysisRecord.calculations || {};
  const parsedInput = analysisRecord.parsed_input || {};
  const calculationTrace = Array.isArray(calc?.calculation_trace)
    ? calc.calculation_trace
    : Array.isArray(analysisRecord?.calculation_trace)
      ? analysisRecord.calculation_trace
      : [];
  const projectInfo = calc.project_info || {};
  const ownershipAnalysis = calc.ownership_analysis || {};
  const returnMetrics = calc.return_metrics || {};
  const roiAnalysis = calc.roi_analysis || {};
  const roiMetrics = calc.roi_metrics || {};
  const totals = calc.totals || {};
  const revenueRequirements =
    calc.revenue_requirements || ownershipAnalysis.revenue_requirements || {};
  const investmentAnalysis = ownershipAnalysis.investment_analysis || {};
  const buildingTypeFromParsed = (parsedInput?.building_type || '').toLowerCase();
  const buildingTypeFromCalc = (projectInfo?.building_type || '').toLowerCase();
  const buildingTypeFromDisplay = (displayData?.buildingType || '').toLowerCase();
  const normalizedBuildingType =
    buildingTypeFromParsed || buildingTypeFromCalc || buildingTypeFromDisplay || '';
  const normalizedSubtype =
    parsedInput?.subtype ||
    parsedInput?.building_subtype ||
    projectInfo?.subtype ||
    displayData?.subtype ||
    undefined;
  const resolvedSquareFootage =
    typeof parsedInput?.square_footage === 'number' && parsedInput.square_footage > 0
      ? parsedInput.square_footage
      : typeof projectInfo?.square_footage === 'number' && projectInfo.square_footage > 0
        ? projectInfo.square_footage
        : undefined;
  const resolvedLocation =
    parsedInput?.location || projectInfo?.location || undefined;
  const resolvedProjectClass =
    parsedInput?.project_classification ||
    parsedInput?.project_class ||
    projectInfo?.project_class ||
    undefined;
  const detectionSource =
    parsedInput?.detection_source || 'N/A';
  const conflictResolution =
    parsedInput?.detection_conflict_resolution || 'N/A';

  const formatLabel = (value?: string) => {
    if (!value || typeof value !== 'string') {
      return 'N/A';
    }
    return value
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  const formatProjectClass = (value?: string) => {
    if (!value || typeof value !== 'string') {
      return 'Ground-Up';
    }
    return value
      .replace(/_/g, '-')
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  };

  const generatedAtTimestamp = (() => {
    if (!Array.isArray(calculationTrace) || calculationTrace.length === 0) {
      return undefined;
    }
    const timestamps = calculationTrace
      .map((trace) => trace?.timestamp)
      .filter((value): value is string => typeof value === 'string' && !Number.isNaN(Date.parse(value)));
    if (timestamps.length === 0) {
      return undefined;
    }
    return timestamps
      .map((value) => Date.parse(value))
      .reduce((max, current) => (current > max ? current : max), 0);
  })();

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Get icon for each trace step
  const getStepIcon = (step: string) => {
    if (step.toLowerCase().includes('base')) return <DollarSign className="h-4 w-4" />;
    if (step.toLowerCase().includes('regional')) return <MapPin className="h-4 w-4" />;
    if (step.toLowerCase().includes('complexity') || step.toLowerCase().includes('class')) return <Layers className="h-4 w-4" />;
    if (step.toLowerCase().includes('trade')) return <Calculator className="h-4 w-4" />;
    if (step.toLowerCase().includes('soft')) return <FileText className="h-4 w-4" />;
    if (step.toLowerCase().includes('total')) return <CheckCircle className="h-4 w-4" />;
    return <TrendingUp className="h-4 w-4" />;
  };

  // Format data values
  const formatDataValue = (key: string, value: any): string => {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    const keyLower = key.toLowerCase();
    const isFactorKey =
      keyLower.includes('factor') ||
      keyLower.includes('multiplier');
    const isPercentKey =
      keyLower.includes('pct') ||
      keyLower.includes('percent') ||
      keyLower.includes('percentage') ||
      keyLower.includes('margin') ||
      keyLower.includes('yield') ||
      keyLower.includes('roi');
    const isCurrencyKey =
      keyLower.includes('cost') ||
      keyLower.includes('total') ||
      keyLower.includes('amount') ||
      keyLower.includes('revenue') ||
      keyLower.includes('noi') ||
      keyLower.includes('npv') ||
      keyLower.includes('debt') ||
      keyLower.includes('value');

    if (isPercentKey) {
      if (typeof value !== 'number' || !Number.isFinite(value)) return String(value);
      const normalized = value > 0 && value < 1 ? value * 100 : value;
      return `${normalized.toFixed(2)}%`;
    }
    if (isFactorKey) {
      if (typeof value !== 'number' || !Number.isFinite(value)) return String(value);
      return `${value.toFixed(2)}x`;
    }
    if (isCurrencyKey && !keyLower.includes('cost_factor')) {
      if (typeof value !== 'number' || !Number.isFinite(value)) return String(value);
      return formatCurrency(value);
    }
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return String(value);
  };

  const feasibilityTrace = Array.isArray(calculationTrace)
    ? [...calculationTrace].reverse().find(trace => trace?.step === 'feasibility_evaluated')
    : undefined;
  const isDevMode = import.meta.env.MODE !== 'production';

  const normalizeRate = (value?: number | null) => {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      return undefined;
    }
    if (value === 0) {
      return 0;
    }
    const normalized = value > 1 ? value / 100 : value;
    return normalized;
  };

  const getNormalizedRate = (...values: Array<number | null | undefined>) => {
    for (const value of values) {
      const normalized = normalizeRate(value);
      if (typeof normalized === 'number') {
        return normalized;
      }
    }
    return undefined;
  };

  const totalProjectCost =
    typeof totals?.total_project_cost === 'number' && totals.total_project_cost > 0
      ? totals.total_project_cost
      : undefined;
  const estimatedNoiRaw =
    typeof returnMetrics?.estimated_annual_noi === 'number'
      ? returnMetrics.estimated_annual_noi
      : typeof ownershipAnalysis?.return_metrics?.estimated_annual_noi === 'number'
        ? ownershipAnalysis.return_metrics.estimated_annual_noi
        : typeof roiAnalysis?.financial_metrics?.net_income === 'number'
          ? roiAnalysis.financial_metrics.net_income
          : typeof calc?.revenue_analysis?.net_income === 'number'
            ? calc.revenue_analysis.net_income
            : undefined;
  const derivedYieldOnCost =
    typeof estimatedNoiRaw === 'number' &&
    typeof totalProjectCost === 'number'
      ? estimatedNoiRaw / totalProjectCost
      : undefined;

  const formatPercent = (value: any) => {
    if (typeof value !== 'number' || Number.isNaN(value)) {
      return 'N/A';
    }
    const v = value > 0 && value < 1 ? value * 100 : value;
    return `${v.toFixed(2)}%`;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b px-6 py-4 z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">Provenance Receipt</h2>
                  <p className="text-sm text-gray-600">Detailed calculation audit trail</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                <X className="h-5 w-5 text-gray-500" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
            {/* Project Summary */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Project Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Building Type</p>
                  <p className="font-medium">
                    {projectInfo?.display_name
                      ? projectInfo.display_name
                      : formatLabel(normalizedBuildingType)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Subtype</p>
                  <p className="font-medium">{formatLabel(normalizedSubtype)}</p>
                </div>
                <div>
                  <p className="text-gray-600">Square Footage</p>
                  <p className="font-medium">
                    {resolvedSquareFootage
                      ? `${resolvedSquareFootage.toLocaleString()} SF`
                      : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Location</p>
                  <p className="font-medium">
                    {resolvedLocation || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Project Class</p>
                  <p className="font-medium">
                    {formatProjectClass(resolvedProjectClass)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Detection Source</p>
                  <p className="font-medium text-xs break-all">
                    {detectionSource}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Conflict Outcome</p>
                  <p className="font-medium text-xs break-all">
                    {conflictResolution}
                  </p>
                </div>
              </div>
            </div>

            {/* Data Sources */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Run Provenance</h3>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• Building type: {formatLabel(normalizedBuildingType)}</li>
                <li>• Subtype: {formatLabel(normalizedSubtype)}</li>
                <li>
                  • Scope profile: {calc?.scope_items_profile_id || calc?.scope_profile || 'N/A'}
                </li>
                <li>
                  • DealShield tile profile: {calc?.dealshield_tile_profile_id || 'N/A'}
                </li>
                <li>
                  • Schedule source: {calc?.construction_schedule?.schedule_source || 'N/A'}
                </li>
                <li>
                  • Schedule profile: {calc?.construction_schedule?.profile_id || 'N/A'}
                </li>
              </ul>
            </div>

            {(() => {
              const feasibilityData = feasibilityTrace?.data || feasibilityTrace?.payload || {};
              const isIndustrial = normalizedBuildingType === 'industrial';

              let roiPercent: number | undefined;
              let targetRoiPercent: number | undefined;
              let npvRaw: number | undefined;
              let feasibilityState: 'GO' | 'Needs Work' | 'NO-GO' | undefined;

              if (isIndustrial) {
                const yoc = typeof displayData?.yieldOnCost === 'number' && Number.isFinite(displayData.yieldOnCost)
                  ? displayData.yieldOnCost
                  : undefined;
                const targetYield =
                  typeof displayData?.targetYield === 'number' && Number.isFinite(displayData.targetYield)
                    ? displayData.targetYield
                    : undefined;

                const debtMetrics = ownershipAnalysis?.debt_metrics || {};
                const dscrValue =
                  typeof debtMetrics.calculated_dscr === 'number'
                    ? debtMetrics.calculated_dscr
                    : typeof debtMetrics.dscr === 'number'
                      ? debtMetrics.dscr
                      : undefined;
                const dscrTarget =
                  typeof debtMetrics.target_dscr === 'number'
                    ? debtMetrics.target_dscr
                    : 1.25;

                const dscrOk =
                  typeof dscrValue === 'number' &&
                  typeof dscrTarget === 'number' &&
                  Number.isFinite(dscrValue) &&
                  Number.isFinite(dscrTarget)
                    ? dscrValue >= dscrTarget
                    : false;

                if (typeof yoc === 'number') {
                  roiPercent = normalizeRate(yoc);
                }
                if (typeof targetYield === 'number') {
                  targetRoiPercent = normalizeRate(targetYield);
                }

                npvRaw =
                  typeof feasibilityData.npv === 'number'
                    ? feasibilityData.npv
                    : typeof roiAnalysis?.npv === 'number'
                      ? roiAnalysis.npv
                      : undefined;

                if (
                  typeof yoc === 'number' &&
                  typeof targetYield === 'number' &&
                  typeof dscrValue === 'number' &&
                  typeof dscrTarget === 'number'
                ) {
                  if (dscrValue >= dscrTarget && yoc >= targetYield) {
                    feasibilityState = 'GO';
                  } else if (dscrValue >= dscrTarget && yoc >= targetYield - 0.002) {
                    feasibilityState = 'Needs Work';
                  } else if (dscrValue >= dscrTarget) {
                    feasibilityState = 'NO-GO';
                  } else {
                    feasibilityState = 'NO-GO';
                  }
                }
              } else {
                const roiNumber = getNormalizedRate(
                  feasibilityData.roi,
                  derivedYieldOnCost,
                  roiMetrics?.yield_on_cost,
                  roiAnalysis?.yield_on_cost,
                  investmentAnalysis?.actual_roi,
                  ownershipAnalysis?.return_metrics?.roi,
                  returnMetrics?.roi,
                  returnMetrics?.cash_on_cash_return
                );

                const targetRoiNumber = getNormalizedRate(
                  feasibilityData.target_roi,
                  revenueRequirements?.target_yield,
                  investmentAnalysis?.target_yield,
                  ownershipAnalysis?.return_metrics?.target_roi,
                  returnMetrics?.target_roi,
                  roiAnalysis?.target_roi
                );

                npvRaw =
                  typeof feasibilityData.npv === 'number'
                    ? feasibilityData.npv
                    : typeof roiAnalysis?.npv === 'number'
                      ? roiAnalysis.npv
                      : undefined;

                if (typeof roiNumber === 'number') roiPercent = roiNumber;
                if (typeof targetRoiNumber === 'number') targetRoiPercent = targetRoiNumber;

                if (typeof feasibilityData.feasible === 'boolean') {
                  feasibilityState = feasibilityData.feasible ? 'GO' : 'NO-GO';
                } else if (
                  typeof roiPercent === 'number' &&
                  typeof targetRoiPercent === 'number'
                ) {
                  const roiPct = roiPercent > 0 && roiPercent < 1 ? roiPercent * 100 : roiPercent;
                  const targetPct =
                    targetRoiPercent > 0 && targetRoiPercent < 1
                      ? targetRoiPercent * 100
                      : targetRoiPercent;
                  feasibilityState = roiPct >= targetPct ? 'GO' : 'NO-GO';
                }
              }

              const roiDisplay = typeof roiPercent === 'number' ? formatPercent(roiPercent) : 'N/A';
              const targetRoiDisplay =
                typeof targetRoiPercent === 'number' ? formatPercent(targetRoiPercent) : 'N/A';
              const npvDisplay =
                typeof npvRaw === 'number' ? formatCurrency(npvRaw) : 'N/A';
              const feasibleDisplay = feasibilityState ?? 'N/A';
              const feasibilityClass =
                feasibilityState === 'GO'
                  ? 'text-green-700'
                  : feasibilityState === 'Needs Work'
                    ? 'text-amber-700'
                    : 'text-red-700';

              return (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-6">
                  <h3 className="font-semibold text-purple-900 mb-2">
                    Feasibility Evaluation{isDevMode ? ' (dev)' : ''}
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-purple-700 uppercase tracking-wide text-xs mb-1">ROI</p>
                      <p className="font-semibold text-gray-900">{roiDisplay}</p>
                    </div>
                    <div>
                      <p className="text-purple-700 uppercase tracking-wide text-xs mb-1">Target ROI</p>
                      <p className="font-semibold text-gray-900">{targetRoiDisplay}</p>
                    </div>
                    <div>
                      <p className="text-purple-700 uppercase tracking-wide text-xs mb-1">NPV</p>
                      <p className="font-semibold text-gray-900">{npvDisplay}</p>
                    </div>
                    <div>
                      <p className="text-purple-700 uppercase tracking-wide text-xs mb-1">Feasible</p>
                      <p className={`font-semibold ${feasibilityClass}`}>
                        {feasibleDisplay}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* Calculation Trace */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Calculation Steps</h3>
              
              {calculationTrace && calculationTrace.length > 0 ? (
                <div className="space-y-3">
                  {calculationTrace.map((trace, index) => (
                    <div key={index} className="border rounded-lg p-4 hover:shadow-sm transition">
                      <div className="flex items-start gap-3">
                        <div className="p-2 bg-gray-100 rounded-lg mt-1">
                          {getStepIcon(trace.step)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-900">{trace.step}</h4>
                            <span className="text-xs text-gray-500">
                              Step {index + 1} of {calculationTrace.length}
                            </span>
                          </div>
                          
                          {(trace.data || trace.payload) &&
                            Object.keys((trace.data || trace.payload) as Record<string, unknown>).length > 0 && (
                            <div className="bg-gray-50 rounded p-3 space-y-2">
                              {Object.entries((trace.data || trace.payload) as Record<string, unknown>).map(([key, value]) => (
                                <div key={key} className="flex justify-between text-sm">
                                  <span className="text-gray-600">
                                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:
                                  </span>
                                  <span className="font-medium text-gray-900">
                                    {formatDataValue(key, value)}
                                  </span>
                                </div>
                              ))}
                            </div>
                          )}
                          
                          {trace.timestamp && (
                            <p className="text-xs text-gray-500 mt-2">
                              {formatTimestamp(trace.timestamp)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <Calculator className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                  <p>No calculation trace available</p>
                  <p className="text-sm mt-1">Calculation details will appear here</p>
                </div>
              )}
            </div>

            {/* Confidence Statement */}
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="text-sm text-green-800">
                  <p className="font-semibold mb-1">Calculation Confidence</p>
                  {typeof parsedInput?.confidence_projects === 'number' ? (
                    <p>
                      This run references {parsedInput.confidence_projects} comparable projects in the configured confidence model.
                    </p>
                  ) : (
                    <p>
                      Confidence cohort size is not explicitly provided for this run; use the trace steps and profile IDs above for auditability.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Generated on {new Date(generatedAtTimestamp || Date.now()).toLocaleDateString('en-US', {
                  month: 'long', 
                  day: 'numeric', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              <button
                onClick={onClose}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
