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

const countBasedAnalysisResult = {
  parsed_input: {
    building_type: 'healthcare',
    subtype: 'surgical_center',
    square_footage: 18000,
    location: 'Nashville, TN',
    project_class: 'ground_up',
    floors: 1,
    confidence: 1,
  },
  calculations: {
    project_info: {
      building_type: 'healthcare',
      subtype: 'surgical_center',
      display_name: 'Surgical Center',
      project_class: 'ground_up',
      square_footage: 18000,
      location: 'Nashville, TN',
      floors: 1,
      typical_floors: 1,
      available_special_feature_pricing: [
        {
          id: 'operating_room',
          label: 'Operating Room',
          pricing_status: 'included_in_baseline',
          pricing_basis: 'COUNT_BASED',
          configured_value: 450000,
          configured_cost_per_count: 450000,
          configured_count_bands: [
            { label: 'small_asc', max_square_footage: 12000, count: 2 },
            { label: 'mid_asc', max_square_footage: 20000, count: 4 },
            { label: 'large_asc', count: 6 },
          ],
          unit_label: 'room',
        },
        {
          id: 'hc_asc_hybrid_or_cath_lab',
          label: 'Hybrid OR / Cath Lab',
          pricing_status: 'incremental',
          pricing_basis: 'COUNT_BASED',
          configured_value: 950000,
          configured_cost_per_count: 950000,
          configured_count: 1,
          unit_label: 'lab',
        },
      ],
    },
    construction_costs: {
      base_cost_per_sf: 610,
      class_multiplier: 1,
      regional_multiplier: 1.03,
      final_cost_per_sf: 628.3,
      construction_total: 11309400,
      equipment_total: 450000,
      special_features_total: 0,
      special_features_breakdown: [],
    },
    trade_breakdown: {},
    soft_costs: {},
    totals: {
      hard_costs: 11759400,
      soft_costs: 1763910,
      total_project_cost: 13523310,
      cost_per_sf: 751.3,
    },
    calculation_trace: [],
    timestamp: '2026-03-10T12:00:00Z',
  },
  confidence: 1,
} as any;

const overageCountBasedAnalysisResult = {
  parsed_input: {
    building_type: 'healthcare',
    subtype: 'surgical_center',
    square_footage: 18000,
    location: 'Nashville, TN',
    project_class: 'ground_up',
    floors: 1,
    confidence: 1,
  },
  calculations: {
    project_info: {
      building_type: 'healthcare',
      subtype: 'surgical_center',
      display_name: 'Surgical Center',
      project_class: 'ground_up',
      square_footage: 18000,
      location: 'Nashville, TN',
      floors: 1,
      typical_floors: 1,
      available_special_feature_pricing: [
        {
          id: 'operating_room',
          label: 'Operating Room',
          pricing_status: 'included_in_baseline',
          pricing_basis: 'COUNT_BASED',
          count_pricing_mode: 'overage_above_default',
          configured_value: 450000,
          configured_cost_per_count: 450000,
          requested_quantity: 6,
          requested_quantity_source: 'explicit_override:operating_room_count',
          included_baseline_quantity: 4,
          billed_quantity: 2,
          unit_label: 'room',
        },
      ],
    },
    construction_costs: {
      base_cost_per_sf: 610,
      class_multiplier: 1,
      regional_multiplier: 1.03,
      final_cost_per_sf: 628.3,
      construction_total: 11309400,
      equipment_total: 450000,
      special_features_total: 900000,
      special_features_breakdown: [],
    },
    trade_breakdown: {},
    soft_costs: {},
    totals: {
      hard_costs: 12659400,
      soft_costs: 1898910,
      total_project_cost: 14558310,
      cost_per_sf: 808.8,
    },
    calculation_trace: [],
    timestamp: '2026-03-10T12:00:00Z',
  },
  confidence: 1,
} as any;

const overageNoChargeAnalysisResult = {
  parsed_input: {
    building_type: 'healthcare',
    subtype: 'imaging_center',
    square_footage: 12000,
    location: 'Nashville, TN',
    project_class: 'ground_up',
    floors: 1,
    confidence: 1,
  },
  calculations: {
    project_info: {
      building_type: 'healthcare',
      subtype: 'imaging_center',
      display_name: 'Imaging Center',
      project_class: 'ground_up',
      square_footage: 12000,
      location: 'Nashville, TN',
      floors: 1,
      typical_floors: 1,
      available_special_feature_pricing: [
        {
          id: 'mri_suite',
          label: 'MRI Suite',
          pricing_status: 'included_in_baseline',
          pricing_basis: 'COUNT_BASED',
          count_pricing_mode: 'overage_above_default',
          configured_value: 850000,
          configured_cost_per_count: 850000,
          requested_quantity: 1,
          requested_quantity_source: 'explicit_override:mri_suite_count',
          included_baseline_quantity: 1,
          billed_quantity: 0,
          unit_label: 'suite',
        },
      ],
    },
    construction_costs: {
      base_cost_per_sf: 520,
      class_multiplier: 1,
      regional_multiplier: 1.03,
      final_cost_per_sf: 535.6,
      construction_total: 6427200,
      equipment_total: 450000,
      special_features_total: 0,
      special_features_breakdown: [],
    },
    trade_breakdown: {},
    soft_costs: {},
    totals: {
      hard_costs: 6877200,
      soft_costs: 1031580,
      total_project_cost: 7908780,
      cost_per_sf: 659.1,
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

  it('renders count-based backend pricing truth for selected included and incremental features', () => {
    mockUseProjectAnalysis.mockReturnValue({
      analyzing: false,
      calculating: false,
      result: countBasedAnalysisResult,
      error: null,
      analyzeDescription: vi.fn(),
      calculateDirect: vi.fn(),
      reset: vi.fn(),
    });

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    const operatingRoomCheckbox = screen.getByRole('checkbox', { name: /operating room/i });
    const hybridLabCheckbox = screen.getByRole('checkbox', { name: /hybrid or \/ cath lab/i });

    fireEvent.click(operatingRoomCheckbox);
    fireEvent.click(hybridLabCheckbox);

    const operatingRoomRow = operatingRoomCheckbox.closest('label');
    expect(operatingRoomRow).not.toBeNull();
    expect(within(operatingRoomRow as HTMLElement).getByText('Included in baseline')).toBeInTheDocument();
    expect(
      within(operatingRoomRow as HTMLElement).getByText('No additional premium for this subtype')
    ).toBeInTheDocument();
    expect(within(operatingRoomRow as HTMLElement).queryByText(/\/SF/)).not.toBeInTheDocument();

    const hybridLabRow = hybridLabCheckbox.closest('label');
    expect(hybridLabRow).not.toBeNull();
    expect(within(hybridLabRow as HTMLElement).getByText('Incremental premium')).toBeInTheDocument();
    expect(within(hybridLabRow as HTMLElement).getByText('+$950,000')).toBeInTheDocument();
    expect(
      within(hybridLabRow as HTMLElement).getByText('$950,000 per lab × 1 lab')
    ).toBeInTheDocument();
    expect(within(hybridLabRow as HTMLElement).queryByText(/\/SF/)).not.toBeInTheDocument();

    const selectedImpactSummary = screen.getByText('Selected Feature Impact').parentElement;
    expect(selectedImpactSummary).not.toBeNull();
    expect(within(selectedImpactSummary as HTMLElement).getByText('+$950,000')).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).getByText('1 selected feature is included in baseline.')
    ).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).queryByText(/combined impact/i)
    ).not.toBeInTheDocument();
  });

  it('explains billed overage clearly for overage-mode count-based features', () => {
    mockUseProjectAnalysis.mockReturnValue({
      analyzing: false,
      calculating: false,
      result: overageCountBasedAnalysisResult,
      error: null,
      analyzeDescription: vi.fn(),
      calculateDirect: vi.fn(),
      reset: vi.fn(),
    });

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    const operatingRoomCheckbox = screen.getByRole('checkbox', { name: /operating room/i });
    fireEvent.click(operatingRoomCheckbox);

    const operatingRoomRow = operatingRoomCheckbox.closest('label');
    expect(operatingRoomRow).not.toBeNull();
    expect(within(operatingRoomRow as HTMLElement).getByText('Incremental premium')).toBeInTheDocument();
    expect(within(operatingRoomRow as HTMLElement).getByText('+$900,000')).toBeInTheDocument();
    expect(
      within(operatingRoomRow as HTMLElement).getByText('$450,000 per room × 2 rooms')
    ).toBeInTheDocument();
    expect(
      within(operatingRoomRow as HTMLElement).getByText('Baseline includes 4 rooms')
    ).toBeInTheDocument();
    expect(
      within(operatingRoomRow as HTMLElement).getByText('You specified 6 rooms')
    ).toBeInTheDocument();
    expect(
      within(operatingRoomRow as HTMLElement).getByText('Pricing includes 2 additional rooms')
    ).toBeInTheDocument();
  });

  it('explains no-overage cases without hiding the selected included feature', () => {
    mockUseProjectAnalysis.mockReturnValue({
      analyzing: false,
      calculating: false,
      result: overageNoChargeAnalysisResult,
      error: null,
      analyzeDescription: vi.fn(),
      calculateDirect: vi.fn(),
      reset: vi.fn(),
    });

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    const mriSuiteRow = screen.getByText('MRI Suite').closest('label');
    expect(mriSuiteRow).not.toBeNull();
    const mriSuiteCheckbox = within(mriSuiteRow as HTMLElement).getByRole('checkbox');
    fireEvent.click(mriSuiteCheckbox);

    expect(within(mriSuiteRow as HTMLElement).getByText('Included in baseline')).toBeInTheDocument();
    expect(
      within(mriSuiteRow as HTMLElement).getByText('No additional premium for this subtype')
    ).toBeInTheDocument();
    expect(
      within(mriSuiteRow as HTMLElement).getByText('Baseline includes 1 suite')
    ).toBeInTheDocument();
    expect(
      within(mriSuiteRow as HTMLElement).getByText('You specified 1 suite')
    ).toBeInTheDocument();
    expect(
      within(mriSuiteRow as HTMLElement).getByText('No additional suites priced')
    ).toBeInTheDocument();
    expect(within(mriSuiteRow as HTMLElement).queryByText(/\+\$/)).not.toBeInTheDocument();
  });
});
