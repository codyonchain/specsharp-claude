import React from 'react';
import { render, screen } from '@testing-library/react';
import { FinancialRequirementsCard } from '../FinancialRequirementsCard';
import { FinancialRequirements } from '../../../types';

// Mock requirements data
const mockRequirements: FinancialRequirements = {
  primary_metrics: {
    title: 'Primary Metrics',
    metrics: [
      {
        label: 'Total Beds',
        value: '150',
        tooltip: 'Based on 0.15 beds per SF'
      },
      {
        label: 'Investment per Bed',
        value: '$2,500,000',
        tooltip: 'Total investment / 150 beds'
      }
    ]
  },
  performance_targets: {
    title: 'Performance Requirements',
    metrics: [
      {
        label: 'Required Daily Rate',
        value: '$1,200',
        status: 'green'
      }
    ]
  },
  market_analysis: {
    title: 'Market Feasibility',
    metrics: [
      {
        label: 'Market Average Daily Rate',
        value: '$1,400',
        status: 'green'
      }
    ]
  }
};

describe('FinancialRequirementsCard', () => {
  it('renders without crashing', () => {
    render(<FinancialRequirementsCard requirements={mockRequirements} />);
    expect(screen.getByText('Hospital Financial Requirements')).toBeInTheDocument();
  });

  it('displays all sections when data is provided', () => {
    render(<FinancialRequirementsCard requirements={mockRequirements} />);
    
    expect(screen.getByText('Primary Metrics')).toBeInTheDocument();
    expect(screen.getByText('Performance Requirements')).toBeInTheDocument();
    expect(screen.getByText('Market Feasibility')).toBeInTheDocument();
  });

  it('displays metric values correctly', () => {
    render(<FinancialRequirementsCard requirements={mockRequirements} />);
    
    expect(screen.getByText('150')).toBeInTheDocument();
    expect(screen.getByText('$2,500,000')).toBeInTheDocument();
    expect(screen.getByText('$1,200')).toBeInTheDocument();
    expect(screen.getByText('$1,400')).toBeInTheDocument();
  });

  it('does not render when isVisible is false', () => {
    render(<FinancialRequirementsCard requirements={mockRequirements} isVisible={false} />);
    
    expect(screen.queryByText('Hospital Financial Requirements')).not.toBeInTheDocument();
  });

  it('does not render when requirements is null', () => {
    render(<FinancialRequirementsCard requirements={null as any} />);
    
    expect(screen.queryByText('Hospital Financial Requirements')).not.toBeInTheDocument();
  });

  it('shows empty state when no metrics are provided', () => {
    const emptyRequirements: FinancialRequirements = {
      primary_metrics: { title: '', metrics: [] },
      performance_targets: { title: '', metrics: [] },
      market_analysis: { title: '', metrics: [] }
    };
    
    render(<FinancialRequirementsCard requirements={emptyRequirements} />);
    
    expect(screen.getByText('Financial requirements data is not available for this project type.')).toBeInTheDocument();
  });
});