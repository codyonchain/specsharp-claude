import React, { useState } from 'react';
import { formatCurrency, formatPercent } from '../../utils/formatters';
import { formatters } from '../../utils/displayFormatters';

interface Props {
  trades: Record<string, number>;
  calculations?: any; // Backend calculations object
}

export const TradeBreakdown: React.FC<Props> = ({ trades, calculations }) => {
  // Add state to track which trade is expanded
  const [expandedTrade, setExpandedTrade] = useState<string | null>(null);
  
  // Add state to track hover for visual feedback
  const [hoveredTrade, setHoveredTrade] = useState<string | null>(null);
  
  // Use backend total instead of reducing
  const total = calculations?.construction_costs?.trades_total || 
               calculations?.totals?.hard_costs || 
               Object.values(trades).reduce((sum, val) => sum + val, 0);
  
  const tradeData = Object.entries(trades)
    .map(([name, amount]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1).replace('_', ' '),
      amount,
      percentage: calculations?.trade_breakdown?.percentages?.[name.toLowerCase()] || (amount / total)
    }))
    .sort((a, b) => b.amount - a.amount);
  
  // Get cost DNA data for multiplier display
  const costDna = calculations?.cost_dna;
  const regionalMultiplier = costDna?.regional_adjustment || 
                            calculations?.construction_costs?.regional_multiplier || 
                            1.0;
  const marketName = costDna?.market_name || 'Nashville';
  const baseCost = costDna?.base_cost || calculations?.construction_costs?.base_cost_per_sf || 0;
  const finalCost = costDna?.final_cost || calculations?.construction_costs?.final_cost_per_sf || 0;
  
  // Handler for trade clicks
  const handleTradeClick = (tradeName: string) => {
    setExpandedTrade(expandedTrade === tradeName ? null : tradeName);
  };
  
  // Helper function for trade colors
  const getTradeColor = (tradeName: string): string => {
    const colors: Record<string, string> = {
      'Structural': 'bg-blue-500',
      'Mechanical': 'bg-green-500',
      'Electrical': 'bg-yellow-500',
      'Plumbing': 'bg-purple-500',
      'Finishes': 'bg-pink-500'
    };
    return colors[tradeName] || 'bg-gray-500';
  };
  
  // Temporary component data until backend provides it
  const getTradeComponents = (tradeName: string) => {
    const trade = tradeData.find(t => t.name === tradeName);
    const totalCost = trade?.amount || 0;
    
    const components: Record<string, Array<{name: string, percentage: number}>> = {
      'Structural': [
        { name: 'Foundation', percentage: 27 },
        { name: 'Framing', percentage: 48 },
        { name: 'Roofing', percentage: 25 }
      ],
      'Mechanical': [
        { name: 'HVAC Systems', percentage: 60 },
        { name: 'Plumbing', percentage: 40 }
      ],
      'Electrical': [
        { name: 'Power Distribution', percentage: 40 },
        { name: 'Lighting', percentage: 30 },
        { name: 'Low Voltage', percentage: 30 }
      ],
      'Plumbing': [
        { name: 'Fixtures', percentage: 35 },
        { name: 'Piping', percentage: 45 },
        { name: 'Equipment', percentage: 20 }
      ],
      'Finishes': [
        { name: 'Flooring', percentage: 25 },
        { name: 'Wall Finishes', percentage: 30 },
        { name: 'Ceilings', percentage: 20 },
        { name: 'Specialties', percentage: 25 }
      ]
    };
    
    const tradeComponents = components[tradeName] || [];
    return tradeComponents.map(comp => ({
      ...comp,
      cost: Math.round(totalCost * (comp.percentage / 100))
    }));
  };

  return (
    <div className="space-y-6">
      {/* Cost Build-Up Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold mb-4">Cost Build-Up</h2>
        
        {/* Regional Multiplier Display */}
        <div className="mb-4 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-600 font-medium">{marketName} Market Adjustment</span>
            <span className="font-semibold text-lg">
              {regionalMultiplier.toFixed(2)}x
              {regionalMultiplier !== 1 && (
                <span className="text-sm text-gray-500 ml-1">
                  ({regionalMultiplier > 1 ? '+' : ''}{((regionalMultiplier - 1) * 100).toFixed(0)}%)
                </span>
              )}
            </span>
          </div>
          
          {/* Visual Cost Flow */}
          {costDna && (
            <div className="mt-4 p-3 bg-white rounded border border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <div className="text-center">
                  <div className="font-semibold text-gray-700">${baseCost.toFixed(0)}</div>
                  <div className="text-xs text-gray-500">Base Cost/SF</div>
                </div>
                <div className="text-gray-400">→</div>
                <div className="text-center">
                  <div className="font-semibold text-blue-600">
                    ${costDna.applied_adjustments?.after_regional?.toFixed(0) || (baseCost * regionalMultiplier).toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-500">After Regional</div>
                </div>
                <div className="text-gray-400">→</div>
                <div className="text-center">
                  <div className="font-semibold text-green-600">${finalCost.toFixed(0)}</div>
                  <div className="text-xs text-gray-500">Final Cost/SF</div>
                </div>
              </div>
            </div>
          )}
          
          {/* Market Context */}
          {costDna?.market_context && (
            <div className="mt-3 text-sm text-gray-600">
              <span className="font-medium">{marketName}</span> is{' '}
              <span className="font-medium text-blue-600">
                {costDna.market_context.comparison}
              </span>
              {costDna.market_context.percentage_difference !== 0 && (
                <span> by {Math.abs(costDna.market_context.percentage_difference)}%</span>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Trade Breakdown Section */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-bold mb-4">Trade Breakdown</h2>
      
      <div className="space-y-3">
        {tradeData.map((trade) => (
          <div key={trade.name} className="mb-2">
            {/* Make the trade row clickable */}
            <div 
              onClick={() => handleTradeClick(trade.name)}
              onMouseEnter={() => setHoveredTrade(trade.name)}
              onMouseLeave={() => setHoveredTrade(null)}
              className={`
                cursor-pointer transition-all duration-200 rounded-lg p-3
                ${hoveredTrade === trade.name ? 'bg-gray-50 shadow-sm' : ''}
                ${expandedTrade === trade.name ? 'bg-blue-50 shadow-md' : ''}
              `}
            >
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${getTradeColor(trade.name)}`} />
                  <span className="text-sm font-medium text-gray-700">{trade.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600">{formatters.percentage(trade.percentage)}</span>
                  <span className="text-sm font-semibold">{formatters.currency(trade.amount)}</span>
                  {/* Add expand/collapse indicator */}
                  <svg 
                    className={`w-4 h-4 transition-transform ${expandedTrade === trade.name ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${trade.percentage * 100}%` }}
                />
              </div>
            </div>
            
            {/* Expanded detail section */}
            {expandedTrade === trade.name && (
              <div className="mt-2 ml-6 p-4 bg-white border border-gray-200 rounded-lg shadow-inner">
                <h4 className="font-semibold text-gray-700 mb-3">Component Breakdown</h4>
                {getTradeComponents(trade.name).map((component) => (
                  <div key={component.name} className="flex justify-between py-2 border-b border-gray-100 last:border-0">
                    <span className="text-sm text-gray-600">{component.name}</span>
                    <div className="flex gap-4">
                      <span className="text-sm text-gray-500">{component.percentage}%</span>
                      <span className="text-sm font-medium">{formatters.currency(component.cost)}</span>
                    </div>
                  </div>
                ))}
                
                {/* View Details button like V1 */}
                <button 
                  className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: Implement detail modal
                    console.log(`View details for ${trade.name}`);
                  }}
                >
                  View Details 
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      </div>
    </div>
  );
};