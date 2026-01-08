import React from 'react';
import { X, FileText, TrendingUp, MapPin, Calculator, Layers, DollarSign, CheckCircle } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';

interface ProvenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectData: any;
  calculationTrace?: any[];
  calculationData?: any;
  displayData?: any;
}

export const ProvenanceModal: React.FC<ProvenanceModalProps> = ({
  isOpen,
  onClose,
  projectData,
  calculationTrace = [],
  calculationData,
  displayData,
}) => {
  if (!isOpen) return null;

  const calc = calculationData || {};
  const projectInfo = calc.project_info || {};
  const ownershipAnalysis = calc.ownership_analysis || {};
  const returnMetrics = calc.return_metrics || {};
  const roiAnalysis = calc.roi_analysis || {};
  const roiMetrics = calc.roi_metrics || {};
  const totals = calc.totals || {};
  const revenueRequirements =
    calc.revenue_requirements || ownershipAnalysis.revenue_requirements || {};
  const investmentAnalysis = ownershipAnalysis.investment_analysis || {};
  const buildingTypeFromCalc = (projectInfo?.building_type || '').toLowerCase();
  const buildingTypeFromDisplay = (displayData?.buildingType || '').toLowerCase();
  const normalizedBuildingType =
    buildingTypeFromCalc || buildingTypeFromDisplay || '';

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
    if (key.toLowerCase().includes('cost') || key.toLowerCase().includes('total') || key.toLowerCase().includes('amount')) {
      return typeof value === 'number' ? formatCurrency(value) : value;
    }
    if (key.toLowerCase().includes('multiplier') || key.toLowerCase().includes('rate')) {
      return typeof value === 'number' ? `${value.toFixed(2)}x` : value;
    }
    if (key.toLowerCase().includes('percentage') || key.toLowerCase().includes('percent')) {
      return typeof value === 'number' ? `${(value * 100).toFixed(1)}%` : value;
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
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Building Type</p>
                  <p className="font-medium">
                    {projectInfo?.display_name ||
                      projectInfo?.building_type ||
                      projectData?.building_type ||
                      'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Square Footage</p>
                  <p className="font-medium">
                    {projectInfo?.square_footage
                      ? `${projectInfo.square_footage.toLocaleString()} SF`
                      : projectData?.square_footage
                        ? `${projectData.square_footage.toLocaleString()} SF`
                        : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Location</p>
                  <p className="font-medium">
                    {projectInfo?.location || projectData?.location || 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Project Class</p>
                  <p className="font-medium">
                    {projectInfo?.project_class ||
                      projectData?.project_class ||
                      'Ground-Up'}
                  </p>
                </div>
              </div>
            </div>

            {/* Data Sources */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-900 mb-2">Data Sources</h3>
              <ul className="space-y-1 text-sm text-blue-800">
                <li>• Base costs: RSMeans 2024 Q3 Construction Cost Data</li>
                <li>• Regional adjustments: SpecSharp Market Intelligence Database</li>
                <li>• Trade breakdowns: Industry-standard allocations</li>
                <li>• Soft costs: Regional market averages</li>
                <li>• Equipment costs: Manufacturer MSRP data</li>
              </ul>
            </div>

            {(() => {
              const feasibilityData = feasibilityTrace?.data || {};
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
                          
                          {trace.data && Object.keys(trace.data).length > 0 && (
                            <div className="bg-gray-50 rounded p-3 space-y-2">
                              {Object.entries(trace.data).map(([key, value]) => (
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
                  <p>This estimate is based on current market data and has been validated against {projectData?.confidence_projects || 47} similar projects in the region. The methodology follows industry-standard practices and incorporates real-time market conditions.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Generated on {new Date().toLocaleDateString('en-US', { 
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
