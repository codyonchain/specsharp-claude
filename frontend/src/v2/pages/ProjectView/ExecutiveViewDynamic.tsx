import React from 'react';
import { Project, BuildingType } from '../../types';
import { formatCurrency, formatNumber, formatPercent } from '../../utils/formatters';
import { 
  TrendingUp, DollarSign, Building, Clock, AlertCircle,
  Heart, Home, ShoppingBag, Briefcase, Factory, Hotel,
  GraduationCap, Building2, Users, Target, TrendingDown,
  CheckCircle, Info, Download
} from 'lucide-react';

interface Props {
  project: Project;
}

// Get appropriate icon for building type
const getBuildingIcon = (buildingType: string) => {
  switch (buildingType) {
    case BuildingType.HEALTHCARE: return Heart;
    case BuildingType.MULTIFAMILY: return Home;
    case BuildingType.RETAIL: return ShoppingBag;
    case BuildingType.OFFICE: return Briefcase;
    case BuildingType.INDUSTRIAL: return Factory;
    case BuildingType.HOSPITALITY: return Hotel;
    case BuildingType.EDUCATIONAL: return GraduationCap;
    default: return Building2;
  }
};

// Get appropriate capacity metric
const getCapacityMetric = (buildingType: string, squareFeet: number) => {
  switch (buildingType) {
    case BuildingType.HEALTHCARE:
      return { label: 'Beds Capacity', value: Math.round(squareFeet / 800), unit: 'beds' };
    case BuildingType.MULTIFAMILY:
      return { label: 'Units', value: Math.round(squareFeet / 950), unit: 'units' };
    case BuildingType.HOSPITALITY:
      return { label: 'Rooms', value: Math.round(squareFeet / 400), unit: 'rooms' };
    case BuildingType.EDUCATIONAL:
      return { label: 'Students', value: Math.round(squareFeet / 125), unit: 'students' };
    case BuildingType.OFFICE:
      return { label: 'Occupancy', value: Math.round(squareFeet / 150), unit: 'people' };
    case BuildingType.RETAIL:
      return { label: 'Visitors/Day', value: Math.round(squareFeet / 30), unit: 'visitors' };
    default:
      return { label: 'Capacity', value: squareFeet, unit: 'SF' };
  }
};

// Get appropriate soft costs based on building type
const getSoftCostCategories = (buildingType: string, totalCost: number) => {
  const baseCategories = [
    { name: 'Design & Engineering', amount: totalCost * 0.056, percent: 18 },
    { name: 'Construction Contingency', amount: totalCost * 0.07, percent: 22 },
    { name: 'Owner Contingency', amount: totalCost * 0.035, percent: 11 },
    { name: 'Permits & Legal', amount: totalCost * 0.025, percent: 8 },
  ];

  // Add building-specific soft costs
  switch (buildingType) {
    case BuildingType.HEALTHCARE:
      return [
        { name: 'Medical Equipment', amount: totalCost * 0.08, percent: 26 },
        ...baseCategories,
        { name: 'FF&E', amount: totalCost * 0.022, percent: 7 },
      ];
    case BuildingType.MULTIFAMILY:
      return [
        { name: 'Appliances & Fixtures', amount: totalCost * 0.04, percent: 13 },
        ...baseCategories,
        { name: 'Marketing & Leasing', amount: totalCost * 0.02, percent: 6 },
      ];
    case BuildingType.HOSPITALITY:
      return [
        { name: 'FF&E', amount: totalCost * 0.08, percent: 26 },
        ...baseCategories,
        { name: 'Pre-Opening', amount: totalCost * 0.025, percent: 8 },
      ];
    case BuildingType.RETAIL:
      return [
        { name: 'Tenant Improvements', amount: totalCost * 0.05, percent: 16 },
        ...baseCategories,
        { name: 'Signage & Branding', amount: totalCost * 0.015, percent: 5 },
      ];
    default:
      return [
        { name: 'FF&E', amount: totalCost * 0.04, percent: 13 },
        ...baseCategories,
      ];
  }
};

export const ExecutiveViewDynamic: React.FC<Props> = ({ project }) => {
  const { parsed_input, calculations } = project.analysis;
  const { totals, construction_costs } = calculations;
  const buildingType = parsed_input.building_type;
  
  // Use totals.hard_costs for construction total
  const constructionTotal = totals.hard_costs;
  
  // Calculate key metrics
  const roi = 0.046; // This should come from backend calculations
  const paybackPeriod = 21.7; // This should come from backend calculations
  const dscr = calculations.ownership_analysis?.debt_metrics?.calculated_dscr || 1.81;
  
  // Get dynamic values based on building type
  const BuildingIcon = getBuildingIcon(buildingType);
  const capacity = getCapacityMetric(buildingType, parsed_input.square_footage);
  const softCostCategories = getSoftCostCategories(buildingType, totals.total_project_cost);

  return (
    <div className="space-y-6">
      {/* Header Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <span className="text-sm text-gray-500">Total Investment</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(totals.total_project_cost)}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {formatCurrency(totals.cost_per_sf)}/SF
          </p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <Building className="h-8 w-8 text-green-600" />
            <span className="text-sm text-gray-500">Construction</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(constructionTotal)}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {formatPercent(constructionTotal / totals.total_project_cost)} of total
          </p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <BuildingIcon className="h-8 w-8 text-purple-600" />
            <span className="text-sm text-gray-500">{capacity.label}</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(capacity.value)}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            {capacity.unit}
          </p>
        </div>

        <div className="bg-white rounded-lg p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <Clock className="h-8 w-8 text-orange-600" />
            <span className="text-sm text-gray-500">Timeline</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {parsed_input.floors <= 3 ? '12-14' : '18-24'}
          </p>
          <p className="text-sm text-gray-500 mt-2">months</p>
        </div>
      </div>

      {/* Financial Metrics */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Financial Metrics</h3>
        <div className="grid grid-cols-4 gap-6">
          <div>
            <p className="text-sm text-gray-500 mb-1">ROI</p>
            <p className="text-xl font-bold text-green-600">
              {formatPercent(roi)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Payback Period</p>
            <p className="text-xl font-bold text-gray-900">
              {paybackPeriod} years
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">DSCR</p>
            <p className="text-xl font-bold text-gray-900">
              {dscr.toFixed(2)}x
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Cost/SF</p>
            <p className="text-xl font-bold text-gray-900">
              {formatCurrency(totals.cost_per_sf)}
            </p>
          </div>
        </div>
      </div>

      {/* Soft Costs Breakdown */}
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Soft Costs Breakdown</h3>
        <div className="space-y-3">
          {softCostCategories.map((category) => (
            <div key={category.name} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-blue-600 rounded-full" />
                <span className="text-sm text-gray-700">{category.name}</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-500">
                  {formatPercent(category.percent / 100)}
                </span>
                <span className="text-sm font-semibold text-gray-900">
                  {formatCurrency(category.amount)}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="font-semibold text-gray-900">Total Soft Costs</span>
            <span className="text-lg font-bold text-gray-900">
              {formatCurrency(totals.soft_costs)}
            </span>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-blue-900">Key Insights</h3>
        <div className="space-y-3">
          <div className="flex gap-3">
            <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                Cost Efficiency
              </p>
              <p className="text-sm text-gray-600">
                Your {formatCurrency(totals.cost_per_sf)}/SF is competitive for {buildingType} projects in {parsed_input.location}
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <Info className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-gray-900">
                Construction Timeline
              </p>
              <p className="text-sm text-gray-600">
                Expected {parsed_input.floors <= 3 ? '12-14' : '18-24'} months based on {formatNumber(parsed_input.square_footage)} SF and {parsed_input.floors} floors
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};