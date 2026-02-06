import React from 'react';
import { render, screen } from '@testing-library/react';
import { DealShieldView } from '../DealShieldView';

const mockDealShield = {
  profile_id: 'profile_123',
  view_model: {
    columns: [{ label: 'Base' }, { label: 'Stretch' }],
    rows: [
      {
        label: 'Scenario A',
        values: [
          { value: 100 },
          { value: 200, coverage: 'partial' }
        ]
      }
    ],
    content: {
      fastest_change: {
        drivers: [{ label: 'Labor' }, { label: 'Steel' }]
      },
      most_likely_wrong: ['Permit timing'],
      question_bank: [{ label: 'What is the schedule risk?' }],
      red_flags: ['Flag A'],
      actions: ['Action A']
    },
    provenance: {
      scenario_inputs: [
        {
          scenario_label: 'Scenario A',
          applied_tile_ids: ['tile_1'],
          cost_scalar: 1.1,
          revenue_scalar: 0.9,
          driver: { metric_ref: 'metric_1' }
        }
      ],
      metric_refs_used: ['metric_1']
    }
  }
};

describe('DealShieldView', () => {
  it('renders scenario labels and columns', () => {
    render(
      <DealShieldView
        projectId="proj_1"
        data={mockDealShield as any}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText('DealShield')).toBeInTheDocument();
    expect(screen.getByText('Scenario Table')).toBeInTheDocument();
    expect(screen.getByText('Base')).toBeInTheDocument();
    expect(screen.getByText('Stretch')).toBeInTheDocument();
    expect(screen.getByText('Scenario A')).toBeInTheDocument();
    expect(screen.getByText('base-locked')).toBeInTheDocument();
  });
});
