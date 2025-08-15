import { useState } from 'react';
import { ChevronDown, ChevronUp, Package } from 'lucide-react';
import { formatCurrency } from '../utils/formatters';
import './TradeSummary.css';

interface KeyMetric {
  label: string;
  value: string | number;
  unit: string;
}

interface TradeSummaryData {
  trade: string;
  total_cost: number;
  key_metrics: KeyMetric[];
  systems: any[];
  category_data: any;
}

interface TradeSummaryProps {
  tradeSummaries: TradeSummaryData[];
  onGeneratePackage: (trade: string) => void;
  isReadOnly?: boolean;
}

function TradeSummary({ tradeSummaries, onGeneratePackage, isReadOnly = false }: TradeSummaryProps) {
  const [expandedTrades, setExpandedTrades] = useState<Set<string>>(new Set());

  const toggleExpanded = (trade: string) => {
    const newExpanded = new Set(expandedTrades);
    if (newExpanded.has(trade)) {
      newExpanded.delete(trade);
    } else {
      newExpanded.add(trade);
    }
    setExpandedTrades(newExpanded);
  };

  const getTradeIcon = (trade: string) => {
    const icons: Record<string, string> = {
      'Electrical': '⚡',
      'HVAC': '🌡️',
      'Plumbing': '🚰',
      'Structural': '🏗️'
    };
    return icons[trade] || '📦';
  };


  return (
    <div className="trade-summary">
      <h2>Trade Summary</h2>
      
      <div className="trade-cards">
        {tradeSummaries.map((summary) => {
          const isExpanded = expandedTrades.has(summary.trade);
          const tradeKey = summary.trade.toLowerCase().replace(/\s+/g, '-');
          
          return (
            <div key={summary.trade} className="trade-card">
              <div className="trade-header">
                <div className="trade-title">
                  <span className="trade-icon">{getTradeIcon(summary.trade)}</span>
                  <h3>{summary.trade}</h3>
                </div>
                <div className="trade-total">
                  {formatCurrency(summary.total_cost)}
                </div>
              </div>
              
              <div className="trade-metrics">
                {summary.key_metrics.map((metric, index) => (
                  <div key={index} className="metric">
                    <span className="metric-label">{metric.label}:</span>
                    <span className="metric-value">
                      {metric.value} {metric.unit}
                    </span>
                  </div>
                ))}
              </div>
              
              <div className="trade-actions">
                <button 
                  className="view-details-btn"
                  onClick={() => toggleExpanded(summary.trade)}
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp size={16} />
                      Hide Details
                    </>
                  ) : (
                    <>
                      <ChevronDown size={16} />
                      View Details
                    </>
                  )}
                </button>
                
                {!isReadOnly && (
                  <button 
                    className="generate-package-btn"
                    onClick={() => onGeneratePackage(tradeKey)}
                  >
                    <Package size={16} />
                    Trade Package
                  </button>
                )}
              </div>
              
              {isExpanded && (
                <div className="trade-details">
                  <table className="systems-table">
                    <thead>
                      <tr>
                        <th>Item Description</th>
                        <th>Qty</th>
                        <th>Unit</th>
                        <th>Unit Cost</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.systems.map((system, index) => (
                        <tr key={index}>
                          <td className="system-name">{system.name}</td>
                          <td className="text-right">{system.quantity.toLocaleString()}</td>
                          <td className="text-center">{system.unit}</td>
                          <td className="text-right">${system.unit_cost.toFixed(2)}</td>
                          <td className="text-right">{formatCurrency(system.total_cost)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colSpan={4} className="text-right font-bold">Subtotal:</td>
                        <td className="text-right font-bold">
                          {formatCurrency(summary.category_data.subtotal)}
                        </td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TradeSummary;