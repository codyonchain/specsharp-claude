import React from 'react';
import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { NewProject } from '../NewProject';
import { useProjectAnalysis } from '../../../hooks/useProjectAnalysis';

vi.mock('../../../hooks/useProjectAnalysis', () => ({
  useProjectAnalysis: vi.fn(),
}));

vi.mock('../../../api/client', () => ({
  api: {
    analyzeProject: vi.fn(),
  },
  createProject: vi.fn(),
}));

const mockUseProjectAnalysis = vi.mocked(useProjectAnalysis);

const analysisResult = {
  parsed_input: {
    building_type: 'restaurant',
    subtype: 'full_service',
    square_footage: 6500,
    location: 'Nashville, TN',
    project_class: 'ground_up',
    floors: 1,
    confidence: 1,
  },
  calculations: {
    project_info: {
      building_type: 'restaurant',
      subtype: 'full_service',
      display_name: 'Full Service Restaurant',
      project_class: 'ground_up',
      square_footage: 6500,
      location: 'Nashville, TN',
      floors: 1,
      typical_floors: 1,
      available_special_feature_pricing: [
        {
          id: 'private_dining',
          label: 'Private Dining',
          pricing_status: 'included_in_baseline',
          configured_cost_per_sf: 30,
        },
        {
          id: 'wine_cellar',
          label: 'Wine Cellar',
          pricing_status: 'incremental',
          configured_cost_per_sf: 45,
        },
      ],
    },
    construction_costs: {
      base_cost_per_sf: 385,
      class_multiplier: 1,
      regional_multiplier: 1.03,
      final_cost_per_sf: 396.55,
      construction_total: 3000000,
      equipment_total: 200000,
      special_features_total: 0,
      special_features_breakdown: [],
    },
    trade_breakdown: {},
    soft_costs: {},
    totals: {
      hard_costs: 3200000,
      soft_costs: 480000,
      total_project_cost: 3680000,
      cost_per_sf: 566.15,
    },
    calculation_trace: [],
    timestamp: '2026-03-10T12:00:00Z',
  },
  confidence: 1,
} as any;

describe('NewProject special feature pricing parity', () => {
  beforeEach(() => {
    mockUseProjectAnalysis.mockReturnValue({
      analyzing: false,
      calculating: false,
      result: analysisResult,
      error: null,
      analyzeDescription: vi.fn(),
      calculateDirect: vi.fn(),
      reset: vi.fn(),
    });

    Object.defineProperty(window, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
    Object.defineProperty(Element.prototype, 'scrollIntoView', {
      configurable: true,
      value: vi.fn(),
    });
  });

  it('renders backend-driven included and incremental feature pricing states in the actual component', () => {
    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    const privateDiningCheckbox = screen.getByRole('checkbox', { name: /private dining/i });
    const wineCellarCheckbox = screen.getByRole('checkbox', { name: /wine cellar/i });

    fireEvent.click(privateDiningCheckbox);
    fireEvent.click(wineCellarCheckbox);

    const privateDiningRow = privateDiningCheckbox.closest('label');
    expect(privateDiningRow).not.toBeNull();
    expect(within(privateDiningRow as HTMLElement).getByText('Included in baseline')).toBeInTheDocument();
    expect(
      within(privateDiningRow as HTMLElement).getByText('No additional premium for this subtype')
    ).toBeInTheDocument();
    expect(within(privateDiningRow as HTMLElement).queryByText(/\+\$/)).not.toBeInTheDocument();
    expect(within(privateDiningRow as HTMLElement).queryByText(/\/SF/)).not.toBeInTheDocument();

    const wineCellarRow = wineCellarCheckbox.closest('label');
    expect(wineCellarRow).not.toBeNull();
    expect(within(wineCellarRow as HTMLElement).getByText('Incremental premium')).toBeInTheDocument();
    expect(within(wineCellarRow as HTMLElement).getByText('+$292,500')).toBeInTheDocument();
    expect(within(wineCellarRow as HTMLElement).getByText('$45.00/SF × 6,500 SF')).toBeInTheDocument();

    const selectedImpactSummary = screen.getByText('Selected Feature Impact').parentElement;
    expect(selectedImpactSummary).not.toBeNull();
    expect(within(selectedImpactSummary as HTMLElement).getByText('+$292,500')).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).getByText('1 selected feature is included in baseline.')
    ).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).queryByText('No incremental premium')
    ).not.toBeInTheDocument();
  });
});
