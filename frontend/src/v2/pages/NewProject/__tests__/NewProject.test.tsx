import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { NewProject } from '../NewProject';
import { authService } from '../../../../services/api';
import { createProject } from '../../../api/client';
import { useProjectAnalysis } from '../../../hooks/useProjectAnalysis';

vi.mock('../../../hooks/useProjectAnalysis', () => ({
  useProjectAnalysis: vi.fn(),
}));

vi.mock('../../../api/client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../../api/client')>();
  return {
    ...actual,
    api: {
      ...actual.api,
      analyzeProject: vi.fn(),
    },
    createProject: vi.fn(),
  };
});

vi.mock('../../../../services/api', () => ({
  authService: {
    getCurrentUser: vi.fn(),
  },
}));

const mockUseProjectAnalysis = vi.mocked(useProjectAnalysis);
const mockCreateProject = vi.mocked(createProject);
const mockGetCurrentUser = vi.mocked(authService.getCurrentUser);

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
          id: 'outdoor_seating',
          label: 'Outdoor Seating',
          pricing_status: 'included_in_baseline',
          configured_cost_per_sf: 25,
        },
        {
          id: 'bar',
          label: 'Bar',
          pricing_status: 'incremental',
          configured_cost_per_sf: 35,
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

const areaShareAnalysisResult = {
  parsed_input: {
    building_type: 'hospitality',
    subtype: 'full_service_hotel',
    square_footage: 85000,
    location: 'Nashville, TN',
    project_class: 'ground_up',
    floors: 8,
    confidence: 1,
  },
  calculations: {
    project_info: {
      building_type: 'hospitality',
      subtype: 'full_service_hotel',
      display_name: 'Full Service Hotel',
      project_class: 'ground_up',
      square_footage: 85000,
      location: 'Nashville, TN',
      floors: 8,
      typical_floors: 8,
      available_special_feature_pricing: [
        {
          id: 'ballroom',
          label: 'Ballroom',
          pricing_status: 'included_in_baseline',
          pricing_basis: 'AREA_SHARE_GSF',
          configured_value: 50,
          configured_area_share_of_gsf: 0.08,
          applied_quantity: 6800,
        },
        {
          id: 'spa',
          label: 'Spa',
          pricing_status: 'incremental',
          pricing_basis: 'AREA_SHARE_GSF',
          configured_value: 60,
          configured_area_share_of_gsf: 0.04,
          applied_quantity: 3400,
          applied_value: 60,
          total_cost: 204000,
        },
      ],
    },
    construction_costs: {
      base_cost_per_sf: 420,
      class_multiplier: 1,
      regional_multiplier: 1.03,
      final_cost_per_sf: 432.6,
      construction_total: 36771000,
      equipment_total: 0,
      special_features_total: 0,
      special_features_breakdown: [],
    },
    trade_breakdown: {},
    soft_costs: {},
    totals: {
      hard_costs: 36771000,
      soft_costs: 5515650,
      total_project_cost: 42286650,
      cost_per_sf: 497.5,
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
    mockCreateProject.mockResolvedValue({
      id: 'project_123',
    } as any);
    mockGetCurrentUser.mockResolvedValue({
      run_limits: {
        is_unlimited: false,
        remaining_runs: 3,
      },
    } as any);

    Object.defineProperty(window, 'scrollTo', {
      configurable: true,
      value: vi.fn(),
    });
    Object.defineProperty(Element.prototype, 'scrollIntoView', {
      configurable: true,
      value: vi.fn(),
    });
  });

  it('shows a proactive run-limit blocker on /new only when trusted current state proves the org is exhausted', async () => {
    mockGetCurrentUser.mockResolvedValueOnce({
      run_limits: {
        is_unlimited: false,
        remaining_runs: 0,
      },
    } as any);

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/Start with:/i), {
      target: { value: '6,500 SF full service restaurant in Nashville, TN' },
    });
    fireEvent.change(screen.getByPlaceholderText(/City, ST \(e\.g\., Dallas, TX\)/i), {
      target: { value: 'Nashville, TN' },
    });

    expect(
      await screen.findByText("You've used all included runs")
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        'This org has used all included runs for Decision Packet generation. You can still analyze drafts and review existing work.'
      )
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Generate Decision Packet/i })
    ).toBeDisabled();
    expect(
      screen.getByRole('button', { name: /Generate Draft Packet/i })
    ).toBeEnabled();
  });

  it('does not show a false proactive blocker when runs remain', async () => {
    mockGetCurrentUser.mockResolvedValueOnce({
      run_limits: {
        is_unlimited: false,
        remaining_runs: 2,
      },
    } as any);

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockGetCurrentUser).toHaveBeenCalled();
    });

    expect(
      screen.queryByText("You've used all included runs")
    ).not.toBeInTheDocument();
    fireEvent.click(
      screen.getByRole('checkbox', {
        name: /I confirm these inputs reflect the basis of this decision\./i,
      })
    );
    expect(
      screen.getByRole('button', { name: /Generate Decision Packet/i })
    ).toBeEnabled();
  });

  it('does not proactively block when run-limit state is unknown', async () => {
    mockGetCurrentUser.mockResolvedValueOnce({} as any);

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(mockGetCurrentUser).toHaveBeenCalled();
    });

    expect(
      screen.queryByText("You've used all included runs")
    ).not.toBeInTheDocument();
    fireEvent.click(
      screen.getByRole('checkbox', {
        name: /I confirm these inputs reflect the basis of this decision\./i,
      })
    );
    expect(
      screen.getByRole('button', { name: /Generate Decision Packet/i })
    ).toBeEnabled();
  });

  it('shows the shared exhaustion fallback only for exact backend run_limit_reached responses', async () => {
    mockCreateProject.mockRejectedValueOnce({
      message: 'Run limit reached. Call Cody to add more runs.',
      code: 'run_limit_reached',
      status: 403,
    } as any);

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    fireEvent.click(
      screen.getByRole('checkbox', {
        name: /I confirm these inputs reflect the basis of this decision\./i,
      })
    );
    fireEvent.click(screen.getByRole('button', { name: /Generate Decision Packet/i }));

    expect(
      await screen.findByRole('dialog', { name: /You've used all included runs/i })
    ).toBeInTheDocument();
    expect(screen.queryByText('Run limit reached. Call Cody to add more runs.')).not.toBeInTheDocument();
    expect(
      screen.getByRole('link', { name: /Email Cody to add more runs/i })
    ).toHaveAttribute('href', expect.stringContaining('mailto:cody@specsharp.ai'));
  });

  it('bounds unrelated internal save failures and does not show the exhaustion blocker', async () => {
    mockCreateProject.mockRejectedValueOnce({
      message: 'sqlalchemy.exc.StatementError: confidential deal packet failed to persist',
      code: 'forbidden',
      status: 403,
    } as any);

    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    fireEvent.click(
      screen.getByRole('checkbox', {
        name: /I confirm these inputs reflect the basis of this decision\./i,
      })
    );
    fireEvent.click(screen.getByRole('button', { name: /Generate Decision Packet/i }));

    expect(
      await screen.findByText("We couldn't generate this decision packet. Please try again.")
    ).toBeInTheDocument();
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(
      screen.queryByText("You've used all included runs")
    ).not.toBeInTheDocument();
  });

  it('renders backend-driven included and incremental feature pricing states in the actual component', () => {
    render(
      <MemoryRouter>
        <NewProject />
      </MemoryRouter>
    );

    const outdoorSeatingCheckbox = screen.getByRole('checkbox', { name: /outdoor seating/i });
    const barCheckbox = screen.getByRole('checkbox', { name: /bar/i });

    fireEvent.click(outdoorSeatingCheckbox);
    fireEvent.click(barCheckbox);

    const outdoorSeatingRow = outdoorSeatingCheckbox.closest('label');
    expect(outdoorSeatingRow).not.toBeNull();
    expect(within(outdoorSeatingRow as HTMLElement).getByText('Included in baseline')).toBeInTheDocument();
    expect(
      within(outdoorSeatingRow as HTMLElement).getByText('No additional premium for this subtype')
    ).toBeInTheDocument();
    expect(within(outdoorSeatingRow as HTMLElement).queryByText(/\+\$/)).not.toBeInTheDocument();
    expect(within(outdoorSeatingRow as HTMLElement).queryByText(/\/SF/)).not.toBeInTheDocument();

    const barRow = barCheckbox.closest('label');
    expect(barRow).not.toBeNull();
    expect(within(barRow as HTMLElement).getByText('Incremental premium')).toBeInTheDocument();
    expect(within(barRow as HTMLElement).getByText('+$227,500')).toBeInTheDocument();
    expect(within(barRow as HTMLElement).getByText('$35.00/SF × 6,500 SF')).toBeInTheDocument();

    const selectedImpactSummary = screen.getByText('Selected Feature Impact').parentElement;
    expect(selectedImpactSummary).not.toBeNull();
    expect(within(selectedImpactSummary as HTMLElement).getByText('+$227,500')).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).getByText('1 selected feature is included in baseline.')
    ).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).queryByText('No incremental premium')
    ).not.toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).getByText('$35 / SF combined impact')
    ).toBeInTheDocument();
  });

  it('renders area-share backend pricing truth for selected included and incremental features', () => {
    mockUseProjectAnalysis.mockReturnValue({
      analyzing: false,
      calculating: false,
      result: areaShareAnalysisResult,
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

    const ballroomCheckbox = screen.getByRole('checkbox', { name: /ballroom/i });
    const spaCheckbox = screen.getByRole('checkbox', { name: /spa/i });

    fireEvent.click(ballroomCheckbox);
    fireEvent.click(spaCheckbox);

    const ballroomRow = ballroomCheckbox.closest('label');
    expect(ballroomRow).not.toBeNull();
    expect(within(ballroomRow as HTMLElement).getByText('Included in baseline')).toBeInTheDocument();
    expect(
      within(ballroomRow as HTMLElement).getByText('No additional premium for this subtype')
    ).toBeInTheDocument();
    expect(
      within(ballroomRow as HTMLElement).getByText('Assumed feature area = 8% of project GSF')
    ).toBeInTheDocument();
    expect(within(ballroomRow as HTMLElement).queryByText(/\/SF × 85,000 SF/)).not.toBeInTheDocument();

    const spaRow = spaCheckbox.closest('label');
    expect(spaRow).not.toBeNull();
    expect(within(spaRow as HTMLElement).getByText('Incremental premium')).toBeInTheDocument();
    expect(within(spaRow as HTMLElement).getByText('+$204,000')).toBeInTheDocument();
    expect(
      within(spaRow as HTMLElement).getByText(
        '$60.00 per feature-area SF × 3,400 SF assumed feature area'
      )
    ).toBeInTheDocument();
    expect(
      within(spaRow as HTMLElement).getByText('Assumed feature area = 4% of project GSF')
    ).toBeInTheDocument();
    expect(within(spaRow as HTMLElement).queryByText(/\/SF × 85,000 SF/)).not.toBeInTheDocument();

    const selectedImpactSummary = screen.getByText('Selected Feature Impact').parentElement;
    expect(selectedImpactSummary).not.toBeNull();
    expect(within(selectedImpactSummary as HTMLElement).getByText('+$204,000')).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).getByText('1 selected feature is included in baseline.')
    ).toBeInTheDocument();
    expect(
      within(selectedImpactSummary as HTMLElement).queryByText(/combined impact/i)
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
