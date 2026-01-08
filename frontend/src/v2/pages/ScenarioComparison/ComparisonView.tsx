import React, { useMemo } from 'react';
import {
  Trophy,
  DollarSign,
  TrendingUp,
  Clock,
  Star,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Project, Scenario, ComparisonResult } from './types';

interface ComparisonViewProps {
  scenarios: Scenario[];
  comparisonResult: ComparisonResult | null;
  project: Project;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

const ComparisonView: React.FC<ComparisonViewProps> = ({
  scenarios,
  comparisonResult,
  project,
}) => {
  // Calculate winners for each metric
  const winners = useMemo(() => {
    if (!comparisonResult || !comparisonResult.scenarios) return {};

    const validScenarios = comparisonResult.scenarios.filter(s => !s.error);
    
    return {
      lowestCost: validScenarios.reduce((min, s) => 
        s.totals.total_project_cost < min.totals.total_project_cost ? s : min
      )?.scenario_name,
      bestROI: validScenarios.reduce((max, s) => 
        (s.ownership_analysis?.estimated_roi || 0) > (max.ownership_analysis?.estimated_roi || 0) ? s : max
      )?.scenario_name,
      fastestPayback: validScenarios.reduce((min, s) => 
        (s.ownership_analysis?.payback_years || Infinity) < (min.ownership_analysis?.payback_years || Infinity) ? s : min
      )?.scenario_name,
      lowestCostPerSF: validScenarios.reduce((min, s) => 
        s.totals.cost_per_sf < min.totals.cost_per_sf ? s : min
      )?.scenario_name,
    };
  }, [comparisonResult]);

  // Prepare data for charts
  const barChartData = useMemo(() => {
    if (!comparisonResult) return [];
    return comparisonResult.scenarios.map((s, i) => ({
      name: s.scenario_name,
      totalCost: s.totals?.total_project_cost || 0,
      costPerSF: s.totals?.cost_per_sf || 0,
      color: COLORS[i % COLORS.length],
    }));
  }, [comparisonResult]);

  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`;
    return `$${value.toFixed(0)}`;
  };

  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`;

  const getRecommendation = () => {
    if (!comparisonResult) return null;

    const scores = comparisonResult.scenarios.map(s => {
      let score = 0;
      
      // Cost efficiency (30%)
      if (s.scenario_name === winners.lowestCost) score += 30;
      else if (s.scenario_name === winners.lowestCostPerSF) score += 15;
      
      // ROI (40%)
      if (s.scenario_name === winners.bestROI) score += 40;
      
      // Payback (30%)
      if (s.scenario_name === winners.fastestPayback) score += 30;
      
      return { name: s.scenario_name, score };
    });

    const recommended = scores.reduce((max, s) => s.score > max.score ? s : max);
    const recommendedScenario = comparisonResult.scenarios.find(s => s.scenario_name === recommended.name);

    return {
      name: recommended.name,
      score: recommended.score,
      scenario: recommendedScenario,
    };
  };

  const recommendation = getRecommendation();

  if (!comparisonResult) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Run comparison to see results</p>
      </div>
    );
  }

  return (
    <div>
      {/* Winner Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {scenarios.map((scenario) => (
          <div
            key={scenario.id}
            className={`p-4 rounded-lg border-2 ${
              scenario.name === recommendation?.name
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200'
            } relative`}
          >
            <h3 className="text-lg font-semibold mb-2">{scenario.name}</h3>
            
            <div className="flex flex-wrap gap-1 mb-2">
              {scenario.name === winners.lowestCost && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                  <DollarSign className="h-3 w-3" />
                  Lowest Cost
                </span>
              )}
              {scenario.name === winners.bestROI && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                  <TrendingUp className="h-3 w-3" />
                  Best ROI
                </span>
              )}
              {scenario.name === winners.fastestPayback && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                  <Clock className="h-3 w-3" />
                  Fastest Payback
                </span>
              )}
              {scenario.name === recommendation?.name && (
                <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                  <Star className="h-3 w-3" />
                  Recommended
                </span>
              )}
            </div>

            <p className="text-2xl font-bold">
              {formatCurrency(scenario.totalCost)}
            </p>
            <p className="text-sm text-gray-600">
              ${scenario.costPerSF}/SF
            </p>
          </div>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="bg-white rounded-lg border border-gray-200 mb-6 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                {comparisonResult.scenarios.map((s, i) => (
                  <th key={i} className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {s.scenario_name}
                  </th>
                ))}
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Best
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {/* Total Investment */}
              <tr>
                <td className="px-4 py-3 text-sm text-gray-900">Total Investment</td>
                {comparisonResult.scenarios.map((s, i) => (
                  <td 
                    key={i} 
                    className={`px-4 py-3 text-sm text-right ${
                      s.scenario_name === winners.lowestCost
                        ? 'font-semibold text-green-600'
                        : 'text-gray-900'
                    }`}
                  >
                    {formatCurrency(s.totals?.total_project_cost || 0)}
                  </td>
                ))}
                <td className="px-4 py-3 text-center">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                    {winners.lowestCost}
                  </span>
                </td>
              </tr>

              {/* Cost per SF */}
              <tr>
                <td className="px-4 py-3 text-sm text-gray-900">Cost per SF</td>
                {comparisonResult.scenarios.map((s, i) => (
                  <td 
                    key={i} 
                    className={`px-4 py-3 text-sm text-right ${
                      s.scenario_name === winners.lowestCostPerSF
                        ? 'font-semibold text-green-600'
                        : 'text-gray-900'
                    }`}
                  >
                    ${s.totals?.cost_per_sf || 0}/SF
                  </td>
                ))}
                <td className="px-4 py-3 text-center">
                  <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                    {winners.lowestCostPerSF}
                  </span>
                </td>
              </tr>

              {/* ROI */}
              <tr>
                <td className="px-4 py-3 text-sm text-gray-900">ROI</td>
                {comparisonResult.scenarios.map((s, i) => (
                  <td 
                    key={i} 
                    className={`px-4 py-3 text-sm text-right ${
                      s.scenario_name === winners.bestROI
                        ? 'font-semibold text-blue-600'
                        : 'text-gray-900'
                    }`}
                  >
                    {formatPercent(s.ownership_analysis?.estimated_roi || 0)}
                  </td>
                ))}
                <td className="px-4 py-3 text-center">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                    {winners.bestROI}
                  </span>
                </td>
              </tr>

              {/* Payback Period */}
              <tr>
                <td className="px-4 py-3 text-sm text-gray-900">Payback Period</td>
                {comparisonResult.scenarios.map((s, i) => (
                  <td 
                    key={i} 
                    className={`px-4 py-3 text-sm text-right ${
                      s.scenario_name === winners.fastestPayback
                        ? 'font-semibold text-orange-600'
                        : 'text-gray-900'
                    }`}
                  >
                    {s.ownership_analysis?.payback_years?.toFixed(1) || 'N/A'} years
                  </td>
                ))}
                <td className="px-4 py-3 text-center">
                  <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                    {winners.fastestPayback}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Cost Comparison Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Cost Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barChartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(v) => `$${(v / 1000000).toFixed(1)}M`} />
            <Tooltip formatter={(v: number) => formatCurrency(v)} />
            <Bar dataKey="totalCost" name="Total Cost">
              {barChartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Executive Recommendation */}
      {recommendation && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Trophy className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <h3 className="font-semibold text-green-900 mb-2">Recommendation</h3>
              <p className="text-green-800">
                The <strong>{recommendation.name}</strong> scenario offers the best balance of cost 
                ({formatCurrency(recommendation.scenario?.totals?.total_project_cost || 0)}) and returns 
                ({formatPercent(recommendation.scenario?.ownership_analysis?.estimated_roi || 0)} ROI), 
                with a payback period of {recommendation.scenario?.ownership_analysis?.payback_years?.toFixed(1) || 'N/A'} years.
                This option achieves the project objectives while optimizing financial performance.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComparisonView;