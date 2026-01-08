import React from 'react';
import { OwnershipAnalysis as OwnershipAnalysisType } from '../../types';
import { formatCurrency, formatPercent } from '../../utils/formatters';

interface Props {
  analysis: OwnershipAnalysisType;
}

export const OwnershipAnalysis: React.FC<Props> = ({ analysis }) => {
  const { financing_sources, debt_metrics, return_metrics } = analysis;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-bold mb-4">Ownership Analysis</h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Financing Sources</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Debt</span>
              <span>{formatCurrency(financing_sources.debt_amount)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Equity</span>
              <span>{formatCurrency(financing_sources.equity_amount)}</span>
            </div>
            {financing_sources.philanthropy_amount > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Philanthropy</span>
                <span>{formatCurrency(financing_sources.philanthropy_amount)}</span>
              </div>
            )}
            {financing_sources.grants_amount > 0 && (
              <div className="flex justify-between">
                <span className="text-gray-600">Grants</span>
                <span>{formatCurrency(financing_sources.grants_amount)}</span>
              </div>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Debt Metrics</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Interest Rate</span>
              <span>{formatPercent(debt_metrics.debt_rate)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Monthly Payment</span>
              <span>{formatCurrency(debt_metrics.monthly_debt_service)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">DSCR</span>
              <span className={debt_metrics.dscr_meets_target ? 'text-green-600' : 'text-red-600'}>
                {debt_metrics.calculated_dscr.toFixed(2)}x
              </span>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Return Metrics</h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Est. Annual NOI</span>
              <span>{formatCurrency(return_metrics.estimated_annual_noi)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cash on Cash</span>
              <span>{formatPercent(return_metrics.cash_on_cash_return)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};