import React from 'react';
import { formatCurrency, formatPercent } from '../../utils/formatters';

interface Props {
  trades: Record<string, number>;
}

export const TradeBreakdown: React.FC<Props> = ({ trades }) => {
  const total = Object.values(trades).reduce((sum, val) => sum + val, 0);
  
  const tradeData = Object.entries(trades)
    .map(([name, amount]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1).replace('_', ' '),
      amount,
      percentage: amount / total
    }))
    .sort((a, b) => b.amount - a.amount);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold mb-4">Trade Breakdown</h2>
      
      <div className="space-y-3">
        {tradeData.map((trade) => (
          <div key={trade.name}>
            <div className="flex justify-between items-center mb-1">
              <span className="text-sm font-medium text-gray-700">{trade.name}</span>
              <span className="text-sm text-gray-600">{formatCurrency(trade.amount)}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${trade.percentage * 100}%` }}
              />
            </div>
            <div className="flex justify-end mt-1">
              <span className="text-xs text-gray-500">{formatPercent(trade.percentage)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};