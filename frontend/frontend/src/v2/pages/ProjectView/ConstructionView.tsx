import React from 'react';
import { Project } from '../../types';
import { CostSummary } from './CostSummary';
import { TradeBreakdown } from './TradeBreakdown';
import { SoftCosts } from './SoftCosts';

interface Props {
  project: Project;
}

export const ConstructionView: React.FC<Props> = ({ project }) => {
  const { calculations } = project.analysis;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CostSummary 
          costs={calculations.construction_costs}
          totals={calculations.totals}
        />
        <TradeBreakdown trades={calculations.trade_breakdown} />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SoftCosts costs={calculations.soft_costs} />
      </div>
    </div>
  );
};
