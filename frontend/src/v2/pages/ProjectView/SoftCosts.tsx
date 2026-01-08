import React from 'react';
import { formatCurrency } from '../../utils/formatters';

interface Props {
  costs: Record<string, number>;
}

export const SoftCosts: React.FC<Props> = ({ costs }) => {
  const costEntries = Object.entries(costs)
    .map(([key, value]) => ({
      name: key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      amount: value
    }))
    .sort((a, b) => b.amount - a.amount);

  const total = Object.values(costs).reduce((sum, val) => sum + val, 0);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold mb-4">Soft Costs</h2>
      
      <div className="space-y-2">
        {costEntries.map((cost) => (
          <div key={cost.name} className="flex justify-between items-center">
            <span className="text-gray-600">{cost.name}</span>
            <span className="font-medium">{formatCurrency(cost.amount)}</span>
          </div>
        ))}
        
        <div className="border-t pt-2 mt-2">
          <div className="flex justify-between items-center">
            <span className="font-semibold">Total Soft Costs</span>
            <span className="font-bold text-lg">{formatCurrency(total)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};