import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { trustNarrative } from "@/content/trustNarrative";
import { ExecutiveViewComplete } from "../ExecutiveViewComplete";

const HOSPITALITY_PROFILE_IDS = [
  "hospitality_limited_service_hotel_v1",
  "hospitality_full_service_hotel_v1",
];

const RESTAURANT_POLICY_CASES = [
  {
    subtype: "quick_service",
    profileId: "restaurant_quick_service_v1",
  },
  {
    subtype: "full_service",
    profileId: "restaurant_full_service_v1",
  },
  {
    subtype: "fine_dining",
    profileId: "restaurant_fine_dining_v1",
  },
  {
    subtype: "cafe",
    profileId: "restaurant_cafe_v1",
  },
  {
    subtype: "bar_tavern",
    profileId: "restaurant_bar_tavern_v1",
  },
] as const;

const CROSS_TYPE_POLICY_CASES = [
  {
    buildingType: "restaurant",
    subtype: "bar_tavern",
    profileId: "restaurant_bar_tavern_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    buildingType: "hospitality",
    subtype: "full_service_hotel",
    profileId: "hospitality_full_service_hotel_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    buildingType: "multifamily",
    subtype: "luxury_apartments",
    profileId: "multifamily_luxury_apartments_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    buildingType: "industrial",
    subtype: "distribution_center",
    profileId: "industrial_distribution_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
] as const;

const INDUSTRIAL_POLICY_CASES = [
  {
    subtype: "warehouse",
    profileId: "industrial_warehouse_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "distribution_center",
    profileId: "industrial_distribution_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "manufacturing",
    profileId: "industrial_manufacturing_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "cold_storage",
    profileId: "industrial_cold_storage_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "flex_space",
    profileId: "industrial_flex_space_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
] as const;

const SPECIALTY_POLICY_CASES = [
  {
    subtype: "data_center",
    profileId: "specialty_data_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "laboratory",
    profileId: "specialty_laboratory_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "self_storage",
    profileId: "specialty_self_storage_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "car_dealership",
    profileId: "specialty_car_dealership_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "broadcast_facility",
    profileId: "specialty_broadcast_facility_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
] as const;

const MULTIFAMILY_POLICY_CASES = [
  {
    subtype: "market_rate_apartments",
    profileId: "multifamily_market_rate_apartments_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "luxury_apartments",
    profileId: "multifamily_luxury_apartments_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "affordable_housing",
    profileId: "multifamily_affordable_housing_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
] as const;

const OFFICE_POLICY_CASES = [
  {
    subtype: "class_a",
    profileId: "office_class_a_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "class_b",
    profileId: "office_class_b_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
] as const;

const RETAIL_POLICY_CASES = [
  {
    subtype: "shopping_center",
    profileId: "retail_shopping_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "big_box",
    profileId: "retail_big_box_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
] as const;

const HEALTHCARE_POLICY_CASES = [
  {
    subtype: "surgical_center",
    profileId: "healthcare_surgical_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "imaging_center",
    profileId: "healthcare_imaging_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "urgent_care",
    profileId: "healthcare_urgent_care_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "outpatient_clinic",
    profileId: "healthcare_outpatient_clinic_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "medical_office_building",
    profileId: "healthcare_medical_office_building_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "dental_office",
    profileId: "healthcare_dental_office_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "hospital",
    profileId: "healthcare_hospital_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "medical_center",
    profileId: "healthcare_medical_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "nursing_home",
    profileId: "healthcare_nursing_home_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "rehabilitation",
    profileId: "healthcare_rehabilitation_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
] as const;

const EDUCATIONAL_POLICY_CASES = [
  {
    subtype: "elementary_school",
    profileId: "educational_elementary_school_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "middle_school",
    profileId: "educational_middle_school_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "high_school",
    profileId: "educational_high_school_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "university",
    profileId: "educational_university_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "community_college",
    profileId: "educational_community_college_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
] as const;

const CIVIC_POLICY_CASES = [
  {
    subtype: "library",
    profileId: "civic_library_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "courthouse",
    profileId: "civic_courthouse_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "government_building",
    profileId: "civic_government_building_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "community_center",
    profileId: "civic_community_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "public_safety",
    profileId: "civic_public_safety_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
] as const;

const RECREATION_POLICY_CASES = [
  {
    subtype: "fitness_center",
    profileId: "recreation_fitness_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "sports_complex",
    profileId: "recreation_sports_complex_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "aquatic_center",
    profileId: "recreation_aquatic_center_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "recreation_center",
    profileId: "recreation_recreation_center_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
  {
    subtype: "stadium",
    profileId: "recreation_stadium_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
] as const;

const PARKING_POLICY_CASES = [
  {
    subtype: "surface_parking",
    profileId: "parking_surface_parking_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
  },
  {
    subtype: "parking_garage",
    profileId: "parking_parking_garage_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "underground_parking",
    profileId: "parking_underground_parking_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
  },
  {
    subtype: "automated_parking",
    profileId: "parking_automated_parking_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
  },
] as const;

const MIXED_USE_POLICY_CASES = [
  {
    subtype: "office_residential",
    profileId: "mixed_use_office_residential_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    mixedUseSplitSource: "user_input",
    mixedUseSplitValue: { office: 70, residential: 30 },
    mixedUseSplitMetricRef: "mixed_use_split.office",
  },
  {
    subtype: "retail_residential",
    profileId: "mixed_use_retail_residential_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    mixedUseSplitSource: "nlp_detected",
    mixedUseSplitValue: { retail: 40, residential: 60 },
    mixedUseSplitMetricRef: "mixed_use_split.retail",
  },
  {
    subtype: "hotel_retail",
    profileId: "mixed_use_hotel_retail_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    mixedUseSplitSource: "user_input",
    mixedUseSplitValue: { hotel: 65, retail: 35 },
    mixedUseSplitMetricRef: "mixed_use_split.hotel",
  },
  {
    subtype: "transit_oriented",
    profileId: "mixed_use_transit_oriented_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    mixedUseSplitSource: "default",
    mixedUseSplitValue: { transit: 25, residential: 45, retail: 30 },
    mixedUseSplitMetricRef: "mixed_use_split.transit",
  },
  {
    subtype: "urban_mixed",
    profileId: "mixed_use_urban_mixed_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    mixedUseSplitSource: "nlp_detected",
    mixedUseSplitValue: { office: 20, residential: 50, retail: 20, hotel: 10 },
    mixedUseSplitMetricRef: "mixed_use_split.residential",
  },
] as const;

const buildRestaurantProject = () =>
  ({
    id: "proj_restaurant_exec",
    project_id: "proj_restaurant_exec",
    name: "Restaurant Full Service",
    description: "Restaurant parity test fixture",
    created_at: "2026-02-24T00:00:00Z",
    updated_at: "2026-02-24T00:00:00Z",
    user_id: "test-user",
    is_shared: false,
    analysis: {
      parsed_input: {
        building_type: "restaurant",
        subtype: "full_service",
        square_footage: 8000,
        location: "Nashville, TN",
        project_classification: "ground_up",
        display_name: "Full Service Restaurant",
      },
      calculations: {
        project_info: {
          building_type: "restaurant",
          subtype: "full_service",
          display_name: "Full Service Restaurant",
          project_class: "ground_up",
          square_footage: 8000,
          location: "Nashville, TN",
          floors: 1,
          typical_floors: 1,
        },
        construction_costs: {
          base_cost_per_sf: 385,
          class_multiplier: 1,
          regional_multiplier: 1.03,
          final_cost_per_sf: 396.55,
          construction_total: 3000000,
          equipment_total: 200000,
          special_features_total: 0,
          cost_build_up: [],
        },
        soft_costs: {
          total: 500000,
          breakdown: {},
        },
        trade_breakdown: {
          structural: 700000,
          mechanical: 950000,
          electrical: 520000,
          plumbing: 410000,
          finishes: 620000,
        },
        totals: {
          hard_costs: 3200000,
          soft_costs: 500000,
          total_project_cost: 3700000,
          cost_per_sf: 462.5,
        },
        revenue_analysis: {
          annual_revenue: 1850000,
          net_income: 430000,
        },
        return_metrics: {
          estimated_annual_noi: 430000,
          cash_on_cash_return: 14.2,
          npv: 100000,
          payback_period: 7.8,
          market_cap_rate: 0.065,
          property_value: 6615384.62,
        },
        ownership_analysis: {
          debt_metrics: {
            annual_debt_service: 295000,
            target_dscr: 1.3,
            calculated_dscr: 1.46,
          },
          return_metrics: {
            estimated_annual_noi: 430000,
            cash_on_cash_return: 14.2,
            npv: 100000,
            payback_period: 7.8,
            market_cap_rate: 0.065,
            property_value: 6615384.62,
          },
          yield_on_cost: 0.116,
        },
        construction_schedule: {
          building_type: "restaurant",
          subtype: "full_service",
          schedule_source: "subtype",
          total_months: 15,
          phases: [
            { id: "site_foundation", label: "Site Foundation", start_month: 0, duration_months: 3, end_month: 3 },
          ],
        },
        dealshield_scenarios: {
          profile_id: "restaurant_full_service_v1",
          scenarios: {
            base: {
              totals: { total_project_cost: 3700000, cost_per_sf: 462.5 },
              revenue_analysis: { annual_revenue: 1850000 },
              ownership_analysis: {
                yield_on_cost: 0.116,
                debt_metrics: { calculated_dscr: 1.46 },
                return_metrics: { estimated_annual_noi: 430000 },
              },
              return_metrics: { payback_period: 7.8 },
            },
          },
          provenance: {
            scenario_ids: ["base"],
            scenario_inputs: {
              base: {
                scenario_label: "Base",
                applied_tile_ids: [],
              },
            },
          },
        },
        calculation_trace: [],
      },
    },
  }) as any;

const buildHospitalityProject = (profileId: string) =>
  ({
    id: `proj_hospitality_exec_${profileId}`,
    project_id: `proj_hospitality_exec_${profileId}`,
    name: "Hospitality Full Service",
    description: "Hospitality parity test fixture",
    created_at: "2026-02-24T00:00:00Z",
    updated_at: "2026-02-24T00:00:00Z",
    user_id: "test-user",
    is_shared: false,
    analysis: {
      parsed_input: {
        building_type: "hospitality",
        subtype:
          profileId === "hospitality_full_service_hotel_v1"
            ? "full_service_hotel"
            : "limited_service_hotel",
        square_footage: 85000,
        location: "Nashville, TN",
        project_classification: "ground_up",
        display_name:
          profileId === "hospitality_full_service_hotel_v1"
            ? "Full Service Hotel"
            : "Select Service Hotel",
      },
      calculations: {
        project_info: {
          building_type: "hospitality",
          subtype:
            profileId === "hospitality_full_service_hotel_v1"
              ? "full_service_hotel"
              : "limited_service_hotel",
          display_name:
            profileId === "hospitality_full_service_hotel_v1"
              ? "Full Service Hotel"
              : "Select Service Hotel",
          project_class: "ground_up",
          square_footage: 85000,
          location: "Nashville, TN",
          floors: 8,
          typical_floors: 8,
        },
        construction_costs: {
          base_cost_per_sf: 325,
          class_multiplier: 1,
          regional_multiplier: 1.03,
          final_cost_per_sf: 334.75,
          construction_total: 28500000,
          equipment_total: 3200000,
          special_features_total: 0,
          cost_build_up: [],
        },
        totals: {
          hard_costs: 31700000,
          soft_costs: 4200000,
          total_project_cost: 35900000,
          cost_per_sf: 422.35,
        },
        hospitality_financials: {
          adr: 212,
          occupancy: 0.74,
          revpar: 156.88,
          noi_margin: 0.33,
          annual_noi: 2980000,
        },
        revenue_analysis: {
          annual_revenue: 9020000,
          net_income: 2980000,
        },
        return_metrics: {
          estimated_annual_noi: 2980000,
          market_cap_rate: 0.075,
          property_value: 39733333.33,
        },
        ownership_analysis: {
          debt_metrics: {
            annual_debt_service: 2100000,
            target_dscr: 1.35,
            calculated_dscr: 1.42,
          },
          return_metrics: {
            estimated_annual_noi: 2980000,
            market_cap_rate: 0.075,
            property_value: 39733333.33,
          },
          yield_on_cost: 0.083,
        },
        dealshield_scenarios: {
          profile_id: profileId,
          scenarios: {
            base: {
              totals: { total_project_cost: 35900000 },
              revenue_analysis: { annual_revenue: 9020000 },
              ownership_analysis: {
                debt_metrics: { calculated_dscr: 1.42 },
                yield_on_cost: 0.083,
              },
            },
          },
          provenance: {
            scenario_ids: ["base"],
            scenario_inputs: {
              base: {
                scenario_label: "Base",
                applied_tile_ids: [],
              },
            },
          },
        },
        calculation_trace: [],
      },
    },
  }) as any;

const buildHospitalityProjectWithExplicitFloors = (
  profileId: string,
  floors: number
) => {
  const project = buildHospitalityProject(profileId);
  project.analysis.parsed_input.floors = floors;
  project.analysis.calculations.project_info.floors = floors;
  project.analysis.calculations.project_info.typical_floors = 8;
  return project;
};

const restaurantDealShieldViewModel = {
  decision_status: "GO",
  decision_reason_code: "explicit_status_signal",
  decision_status_provenance: {
    status_source: "payload_or_decision_summary",
    policy_id: "restaurant_policy_v1",
  },
  decision_insurance_provenance: {
    enabled: true,
    profile_id: "restaurant_full_service_v1",
  },
  tile_profile_id: "restaurant_full_service_v1",
  content_profile_id: "restaurant_full_service_v1",
  scope_items_profile_id: "restaurant_full_service_structural_v1",
  executive_rendered_copy: {
    how_to_interpret:
      "GO because policy threshold clears under current assumptions.",
    policy_basis_line: "Policy basis: DealShield canonical policy.",
    target_yield_lens_label: "Target Yield: Not Met",
  },
};

const buildHospitalityDealShieldViewModel = (profileId: string) => ({
  decision_status: "Needs Work",
  decision_reason_code: "low_flex_before_break_buffer",
  decision_status_provenance: {
    status_source: "dealshield_policy_v1",
    policy_id: "dealshield_canonical_policy_v1",
  },
  decision_insurance_provenance: {
    enabled: true,
    profile_id: profileId,
  },
  tile_profile_id: profileId,
  content_profile_id: profileId,
  scope_items_profile_id:
    profileId === "hospitality_full_service_hotel_v1"
      ? "hospitality_full_service_hotel_structural_v1"
      : "hospitality_limited_service_hotel_structural_v1",
  executive_rendered_copy: {
    how_to_interpret:
      "Needs Work because policy cushion is tight under current assumptions.",
    policy_basis_line: "Policy basis: DealShield canonical policy.",
    target_yield_lens_label: "Target Yield: Not Met",
  },
});

const buildCrossTypeProject = (
  buildingType: string,
  subtype: string,
  profileId: string,
  mixedUseSplit?: Record<string, number>
) => {
  const project = buildRestaurantProject();
  project.id = `proj_exec_${profileId}`;
  project.project_id = `proj_exec_${profileId}`;
  project.name = `${buildingType} ${subtype}`;
  project.analysis.parsed_input.building_type = buildingType;
  project.analysis.parsed_input.subtype = subtype;
  project.analysis.calculations.project_info.building_type = buildingType;
  project.analysis.calculations.project_info.subtype = subtype;
  project.analysis.calculations.dealshield_scenarios.profile_id = profileId;
  if (mixedUseSplit) {
    project.analysis.parsed_input.mixed_use_split = {
      source: "user_input",
      normalization_applied: true,
      value: mixedUseSplit,
    };
    const scenarioInputs = project.analysis.calculations.dealshield_scenarios.provenance.scenario_inputs;
    if (scenarioInputs?.base) {
      scenarioInputs.base.mixed_use_split_source = "user_input";
      scenarioInputs.base.mixed_use_split = {
        source: "user_input",
        normalization_applied: true,
        value: mixedUseSplit,
      };
    }
  }
  return project;
};

const buildCrossTypeDealShieldViewModel = (
  profileId: string,
  decisionStatus: string,
  decisionReasonCode: string,
  options?: {
    mixedUseSplitSource?: "user_input" | "nlp_detected" | "default";
    mixedUseSplitValue?: Record<string, number>;
    mixedUseSplitMetricRef?: string;
  }
) => ({
  decision_status: decisionStatus,
  decision_reason_code: decisionReasonCode,
  decision_status_provenance: {
    status_source: "dealshield_policy_v1",
    policy_id: "decision_insurance_subtype_policy_v1",
    ...(options?.mixedUseSplitSource
      ? { mixed_use_split_source: options.mixedUseSplitSource }
      : {}),
  },
  decision_insurance_provenance: {
    enabled: true,
    profile_id: profileId,
  },
  tile_profile_id: profileId,
  content_profile_id: profileId,
  scope_items_profile_id: `${profileId.replace(/_v1$/, "")}_structural_v1`,
  executive_rendered_copy: {
    how_to_interpret:
      `${decisionStatus} is supplied by backend policy outputs.`,
    policy_basis_line: "Policy basis: DealShield canonical policy.",
    target_yield_lens_label: "Target Yield: Not Met",
  },
  ...(options?.mixedUseSplitValue
    ? {
        provenance: {
          scenario_inputs: {
            base: {
              scenario_label: "Base",
              mixed_use_split_source: options.mixedUseSplitSource ?? "user_input",
              mixed_use_split: {
                source: options.mixedUseSplitSource ?? "user_input",
                normalization_applied: true,
                value: options.mixedUseSplitValue,
              },
              driver: {
                metric_ref: options.mixedUseSplitMetricRef ?? "mixed_use_split.office",
              },
            },
          },
        },
      }
    : {}),
});

const withExecutiveRenderedCopy = (
  viewModel: any,
  copy: {
    how_to_interpret: string;
    policy_basis_line?: string;
    target_yield_lens_label?: string;
  }
) => ({
  ...viewModel,
  executive_rendered_copy: {
    how_to_interpret: copy.how_to_interpret,
    policy_basis_line: copy.policy_basis_line ?? "Policy basis: DealShield canonical policy.",
    target_yield_lens_label: copy.target_yield_lens_label ?? "Target Yield: Not Met",
  },
});

describe("ExecutiveViewComplete", () => {
  it("keeps one Trust & Assumptions trigger and renders the shared executive trust guide in the drawer", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildRestaurantProject()}
          dealShieldData={restaurantDealShieldViewModel as any}
        />
      </MemoryRouter>
    );

    const trustButtons = screen.getAllByRole("button", {
      name: /Trust & Assumptions/i,
    });
    expect(trustButtons).toHaveLength(1);
    expect(screen.queryByText("Why this estimate")).not.toBeInTheDocument();
    expect(screen.queryByText("How we model construction")).not.toBeInTheDocument();
    expect(screen.queryByText("What’s assumed here")).not.toBeInTheDocument();
    expect(
      screen.queryByText("How to interpret this recommendation")
    ).not.toBeInTheDocument();

    const trustPanel = screen.getByRole("dialog", { name: "Trust panel" });
    expect(trustPanel.className).toContain("translate-x-full");

    fireEvent.click(trustButtons[0]);

    expect(trustPanel.className).toContain("translate-x-0");
    expect(screen.queryByText("Interpretation lenses")).not.toBeInTheDocument();
    expect(screen.getByText(trustNarrative.title)).toBeInTheDocument();
    expect(screen.getByText(trustNarrative.sections[0].title)).toBeInTheDocument();
    expect(screen.getByText(trustNarrative.sections[3].title)).toBeInTheDocument();

    fireEvent.click(
      screen.getByRole("button", { name: "Close trust panel" })
    );

    expect(trustPanel.className).toContain("translate-x-full");
  });

  it("prefers resolved explicit floors over subtype typical floors in the executive header", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProjectWithExplicitFloors(
            "hospitality_limited_service_hotel_v1",
            12
          )}
          dealShieldData={
            buildHospitalityDealShieldViewModel(
              "hospitality_limited_service_hotel_v1"
            ) as any
          }
        />
      </MemoryRouter>
    );

    expect(screen.getByText("12 Floors")).toBeInTheDocument();
    expect(screen.queryByText("8 Floors")).not.toBeInTheDocument();
  });

  it("does not synthesize executive narrative copy when backend executive_rendered_copy is missing", () => {
    const payload = { ...restaurantDealShieldViewModel } as any;
    delete payload.executive_rendered_copy;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildRestaurantProject()}
          dealShieldData={payload}
        />
      </MemoryRouter>
    );

    expect(
      screen.queryByText("Recommendation is supplied by backend policy outputs.")
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText("Policy basis: DealShield canonical policy.")
    ).not.toBeInTheDocument();
  });

  it("renders canonical restaurant decision status and provenance source", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildRestaurantProject()}
          dealShieldData={restaurantDealShieldViewModel as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Investment Decision: GO")).toBeInTheDocument();
    const policyLineMatches = screen.getAllByText((_, element) => {
      if (element?.tagName.toLowerCase() !== "p") return false;
      const text = element.textContent ?? "";
      return (
        text.includes("Policy basis: DealShield canonical policy")
      );
    });
    expect(policyLineMatches.length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
  });

  it("renders financing summary from the backend financing contract instead of rebuilding capital stack assumptions in the UI", () => {
    const project = buildRestaurantProject();
    project.analysis.calculations.financing_summary = {
      family_id: "operating_business_fit_out_heavy",
      family_label: "Operating-Business / Fit-Out-Heavy",
      subtitle: "Modeled debt coverage against operator-driven NOI.",
      note: "Interpret as directional; coverage depends on operating assumptions.",
      items: [
        { id: "debt_amount", label: "Debt Amount", value: 2400000, format: "currency" },
        { id: "equity_amount", label: "Equity Amount", value: 1300000, format: "currency" },
        { id: "annual_debt_service", label: "Annual Debt Service", value: 295000, format: "currency" },
        { id: "calculated_dscr", label: "Calculated DSCR", value: 1.46, format: "multiple", decimals: 2 },
        { id: "target_dscr", label: "Target DSCR", value: 1.3, format: "multiple", decimals: 2 },
      ],
    };

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={restaurantDealShieldViewModel as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Financing Summary")).toBeInTheDocument();
    expect(screen.getByText("Modeled debt coverage against operator-driven NOI.")).toBeInTheDocument();
    expect(screen.getByText("Interpret as directional; coverage depends on operating assumptions.")).toBeInTheDocument();
    expect(screen.getByText("Debt Amount")).toBeInTheDocument();
    expect(screen.getByText("Equity Amount")).toBeInTheDocument();
    expect(screen.getByText("Annual Debt Service")).toBeInTheDocument();
    expect(screen.getByText("Calculated DSCR")).toBeInTheDocument();
    expect(screen.getByText("Target DSCR")).toBeInTheDocument();
    expect(screen.queryByText("Debt Rate")).not.toBeInTheDocument();
    expect(screen.queryByText("Debt Ratio")).not.toBeInTheDocument();

    expect(screen.queryByText("Financing Structure")).not.toBeInTheDocument();
    expect(screen.queryByText(/Senior Debt/)).not.toBeInTheDocument();
    expect(screen.queryByText("Mezzanine")).not.toBeInTheDocument();
    expect(screen.queryByText("Weighted Rate")).not.toBeInTheDocument();
    expect(screen.queryByText("Interest During Construction")).not.toBeInTheDocument();
  });

  it("renders subsidized financing summary fields without DSCR or yield lenses when the backend family suppresses them", () => {
    const project = buildCrossTypeProject(
      "multifamily",
      "affordable_housing",
      "multifamily_affordable_housing_v1"
    );
    project.analysis.calculations.financing_summary = {
      family_id: "subsidized_public_institutional",
      family_label: "Subsidized / Public / Institutional",
      subtitle: "Modeled source mix only; financing depth remains intentionally limited.",
      note: "Coverage-style metrics stay intentionally constrained for this family.",
      items: [
        { id: "debt_amount", label: "Debt Amount", value: 1250000, format: "currency" },
        { id: "equity_amount", label: "Equity Amount", value: 900000, format: "currency" },
        { id: "grants_amount", label: "Grants", value: 600000, format: "currency" },
        { id: "philanthropy_amount", label: "Philanthropy", value: 350000, format: "currency" },
        { id: "debt_ratio", label: "Debt Ratio", value: 0.4, format: "percentage", decimals: 1 },
      ],
    };

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "multifamily_affordable_housing_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Debt Amount")).toBeInTheDocument();
    expect(screen.getByText("Equity Amount")).toBeInTheDocument();
    expect(screen.getByText("Modeled source mix only; financing depth remains intentionally limited.")).toBeInTheDocument();
    expect(screen.getByText("Coverage-style metrics stay intentionally constrained for this family.")).toBeInTheDocument();
    expect(screen.getByText("Grants")).toBeInTheDocument();
    expect(screen.getByText("Philanthropy")).toBeInTheDocument();
    expect(screen.getByText("Debt Ratio")).toBeInTheDocument();
    expect(screen.queryByText("Annual Debt Service")).not.toBeInTheDocument();
    expect(screen.queryByText("Calculated DSCR")).not.toBeInTheDocument();
    expect(screen.queryByText("Target DSCR")).not.toBeInTheDocument();
    expect(screen.queryByText("Yield on Cost")).not.toBeInTheDocument();
  });

  it("renders canonical hospitality decision contract fields for both hotel profiles", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject(HOSPITALITY_PROFILE_IDS[0])}
          dealShieldData={buildHospitalityDealShieldViewModel(
            HOSPITALITY_PROFILE_IDS[0]
          ) as any}
        />
      </MemoryRouter>
    );

    for (const profileId of HOSPITALITY_PROFILE_IDS) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildHospitalityProject(profileId)}
            dealShieldData={buildHospitalityDealShieldViewModel(profileId) as any}
          />
        </MemoryRouter>
      );

      expect(screen.getByText("Investment Decision: Needs Work")).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("does not derive decision status from feasibility when DealShield status is missing", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildRestaurantProject()}
          dealShieldData={{ profile_id: "restaurant_full_service_v1" } as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Investment Decision: Under Review")).toBeInTheDocument();
    expect(screen.queryByText("Investment Decision: GO")).not.toBeInTheDocument();
    expect(screen.queryByText("Investment Decision: NO-GO")).not.toBeInTheDocument();
  });

  it("uses limited-service hotel NO-GO narrative that explains value-gap mismatch when debt and yield clear", () => {
    const limitedServiceDealShield = {
      ...buildHospitalityDealShieldViewModel("hospitality_limited_service_hotel_v1"),
      decision_status: "NO-GO",
      decision_reason_code: "base_case_break_condition",
      executive_rendered_copy: {
        how_to_interpret:
          "At ADR $195 / Occ 72% / RevPAR $140, NOI is ~$3.7M; debt coverage is healthy. NO-GO because the base-case value gap is non-positive even though DSCR and yield clear. Use DealShield to isolate the first-break driver and validate it.",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: -320000,
      },
      first_break_condition_holds: true,
      decision_summary: {
        value_gap: -320000,
        value_gap_pct: -0.9,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_limited_service_hotel_v1")}
          dealShieldData={limitedServiceDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("At ADR") && text.includes("/ Occ") && text.includes("/ RevPAR")
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("NO-GO because") && text.includes("Use DealShield to isolate")
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) => text.includes("Hotel clears underwriting at"))
    ).not.toBeInTheDocument();
  });

  it("uses hotel-native footer metrics for both limited-service and full-service hotels", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_limited_service_hotel_v1")}
          dealShieldData={buildHospitalityDealShieldViewModel(
            "hospitality_limited_service_hotel_v1"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("KEYS")).toBeInTheDocument();
    expect(screen.getByText("COST / KEY")).toBeInTheDocument();
    expect(screen.getByText("REVPAR")).toBeInTheDocument();
    expect(screen.getByText("DEBT LENS: DSCR")).toBeInTheDocument();
    expect(screen.queryByText("INVESTMENT PER UNIT")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Units")).not.toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_full_service_hotel_v1")}
          dealShieldData={buildHospitalityDealShieldViewModel(
            "hospitality_full_service_hotel_v1"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("KEYS")).toBeInTheDocument();
    expect(screen.getByText("COST / KEY")).toBeInTheDocument();
    expect(screen.getByText("REVPAR")).toBeInTheDocument();
    expect(screen.getByText("DEBT LENS: DSCR")).toBeInTheDocument();
    expect(screen.queryByText("INVESTMENT PER UNIT")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Units")).not.toBeInTheDocument();
  });

  it("adds full-service hotel NO-GO mismatch explanation when policy breaks despite strong debt/yield lenses", () => {
    const fullServiceDealShield = {
      ...buildHospitalityDealShieldViewModel("hospitality_full_service_hotel_v1"),
      decision_status: "NO-GO",
      decision_reason_code: "base_case_break_condition",
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO because the policy's value-gap threshold breaks in Base even though DSCR and yield appear strong; use DealShield to see the first-break driver and validate it.",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: -450000,
      },
      first_break_condition_holds: true,
      decision_summary: {
        value_gap: -450000,
        value_gap_pct: -1.1,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_full_service_hotel_v1")}
          dealShieldData={fullServiceDealShield}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Debt Lens: DSCR")).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("NO-GO because the policy's value-gap threshold breaks in Base")
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("use DealShield to see the first-break driver and validate it")
      )
    ).toBeInTheDocument();
  });

  it("uses hotel fallback NO-GO narrative when base-break truth is not verified", () => {
    const limitedServiceDealShield = {
      ...buildHospitalityDealShieldViewModel("hospitality_limited_service_hotel_v1"),
      decision_status: "NO-GO",
      decision_reason_code: "base_case_break_condition",
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO under current ADR, occupancy, and benchmark value assumptions.",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: 25000,
      },
      first_break_condition_holds: false,
      decision_summary: {
        value_gap: -210000,
        value_gap_pct: -0.6,
      },
    } as any;

    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_limited_service_hotel_v1")}
          dealShieldData={limitedServiceDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("NO-GO under current ADR, occupancy, and benchmark value assumptions")
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes("NO-GO because the base-case value gap is non-positive even though DSCR and yield clear")
      )
    ).not.toBeInTheDocument();

    const fullServiceDealShield = {
      ...buildHospitalityDealShieldViewModel("hospitality_full_service_hotel_v1"),
      decision_status: "NO-GO",
      decision_reason_code: "base_case_break_condition",
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO under current ADR mix, F&B/ballroom program scope, and benchmark value assumptions.",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: 18000,
      },
      first_break_condition_holds: false,
      decision_summary: {
        value_gap: -390000,
        value_gap_pct: -0.8,
      },
    } as any;

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildHospitalityProject("hospitality_full_service_hotel_v1")}
          dealShieldData={fullServiceDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("NO-GO under current ADR mix, F&B/ballroom program scope, and benchmark value assumptions")
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes("NO-GO because the policy's value-gap threshold breaks in Base")
      )
    ).not.toBeInTheDocument();
  });

  it("keeps restaurant NO-GO detail DSCR wording truthful across all five restaurant subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "restaurant",
            RESTAURANT_POLICY_CASES[0].subtype,
            RESTAURANT_POLICY_CASES[0].profileId
          )}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              RESTAURANT_POLICY_CASES[0].profileId,
              "NO-GO",
              "base_case_break_condition"
            ),
            {
              how_to_interpret:
                "NO-GO because value support is below policy threshold while DSCR 1.46× meets the 1.30× requirement.",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of RESTAURANT_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject("restaurant", testCase.subtype, testCase.profileId)}
            dealShieldData={withExecutiveRenderedCopy(
              buildCrossTypeDealShieldViewModel(
                testCase.profileId,
                "NO-GO",
                "base_case_break_condition"
              ),
              {
                how_to_interpret:
                  "NO-GO because value support is below policy threshold while DSCR 1.46× meets the 1.30× requirement.",
              }
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText((text) =>
          text.includes("DSCR 1.46× meets the 1.30× requirement.")
        )
      ).toBeInTheDocument();
      expect(
        screen.queryByText((text) =>
          text.includes("and/or DSCR 1.46× are below the 1.30× requirement.")
        )
      ).not.toBeInTheDocument();
      expect(screen.getByText("Market return benchmark")).toBeInTheDocument();
      expect(screen.queryByText("Market cap rate")).not.toBeInTheDocument();
    }
  });

  it("handles missing restaurant DSCR values without contradictory NO-GO copy", () => {
    const restaurantProject = buildCrossTypeProject(
      "restaurant",
      "full_service",
      "restaurant_full_service_v1"
    );
    restaurantProject.analysis.calculations.ownership_analysis.debt_metrics.calculated_dscr = Number.NaN;
    restaurantProject.analysis.calculations.dealshield_scenarios.scenarios.base.ownership_analysis.debt_metrics.calculated_dscr =
      Number.NaN;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={restaurantProject}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "restaurant_full_service_v1",
              "NO-GO",
              "base_case_break_condition"
            ),
            {
              how_to_interpret:
                "NO-GO because value support is below policy threshold; DSCR data is still loading against the 1.30× requirement.",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("DSCR data is still loading against the 1.30× requirement.")
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes("and/or DSCR")
      )
    ).not.toBeInTheDocument();
  });

  it("adds full-service-specific GO/NO-GO narrative guidance without spilling into other restaurant subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "full_service", "restaurant_full_service_v1")}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "restaurant_full_service_v1",
              "NO-GO",
              "base_case_break_condition"
            ),
            {
              how_to_interpret:
                "Full Service viability is driven by sales per SF and prime cost (labor + food) under the current layout/turn assumptions. Primary fix paths: raise sales per SF (turns/check), reduce prime cost %, or renegotiate occupancy cost.",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes(
          "Full Service viability is driven by sales per SF and prime cost (labor + food) under the current layout/turn assumptions."
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes(
          "Primary fix paths: raise sales per SF (turns/check), reduce prime cost %, or renegotiate occupancy cost."
        )
      )
    ).toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "full_service", "restaurant_full_service_v1")}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "restaurant_full_service_v1",
              "GO",
              "base_value_gap_positive"
            ),
            {
              how_to_interpret:
                "GO with policy cushion. Still validate occupancy cost % at projected sales and table turns by daypart.",
              target_yield_lens_label: "Target Yield: Met (Cushion)",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("Still validate occupancy cost % at projected sales and table turns by daypart.")
      )
    ).toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "quick_service", "restaurant_quick_service_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_quick_service_v1",
            "NO-GO",
            "base_case_break_condition"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.queryByText((text) =>
        text.includes(
          "Full Service viability is driven by sales per SF and prime cost (labor + food) under the current layout/turn assumptions."
        )
      )
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes(
          "Primary fix paths: raise sales per SF (turns/check), reduce prime cost %, or renegotiate occupancy cost."
        )
      )
    ).not.toBeInTheDocument();
  });

  it("adds quick-service-specific DSCR label and throughput-first decision-points guidance", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "quick_service", "restaurant_quick_service_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_quick_service_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Debt Lens: DSCR")).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes(
          "QSR reality check: validate peak-hour throughput (cars/hour or tickets/hour) and service time assumptions; that's the first-break driver."
        )
      )
    ).toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "fine_dining", "restaurant_fine_dining_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_fine_dining_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("DSCR VS TARGET")).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes(
          "QSR reality check: validate peak-hour throughput (cars/hour or tickets/hour) and service time assumptions; that's the first-break driver."
        )
      )
    ).not.toBeInTheDocument();
  });

  it("uses Buildout Payback helper copy for full-service, quick-service, and fine-dining", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "full_service", "restaurant_full_service_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_full_service_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Buildout payback at current NOI.")).toBeInTheDocument();
    expect(screen.queryByText("Simple payback at current NOI")).not.toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "quick_service", "restaurant_quick_service_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_quick_service_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Buildout payback at current NOI.")).toBeInTheDocument();
    expect(screen.queryByText("Simple payback at current NOI")).not.toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("restaurant", "fine_dining", "restaurant_fine_dining_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_fine_dining_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Buildout payback at current NOI.")).toBeInTheDocument();
    expect(screen.queryByText("Simple payback at current NOI")).not.toBeInTheDocument();
  });

  it("shows fine-dining revenue clarifier only when sales per SF clears but NOI still misses target", () => {
    const fineDiningProject = buildCrossTypeProject(
      "restaurant",
      "fine_dining",
      "restaurant_fine_dining_v1"
    );
    fineDiningProject.analysis.calculations.revenue_analysis = {
      annual_revenue: 5040000,
      net_income: 250000,
    };
    fineDiningProject.analysis.calculations.revenue_requirements = {
      required_value: 296000,
      market_value: 250000,
      required_revenue_per_sf: 462.5,
      actual_revenue_per_sf: 630,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Margin and occupancy assumptions need tightening.",
      },
    };

    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={fineDiningProject}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_fine_dining_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes(
          "Sales/SF clears easily; the hurdle is margin/prime cost and occupancy cost, not top-line demand."
        )
      )
    ).toBeInTheDocument();

    const fullServiceProject = buildCrossTypeProject(
      "restaurant",
      "full_service",
      "restaurant_full_service_v1"
    );
    fullServiceProject.analysis.calculations.revenue_analysis = {
      annual_revenue: 5040000,
      net_income: 250000,
    };
    fullServiceProject.analysis.calculations.revenue_requirements = {
      required_value: 296000,
      market_value: 250000,
      required_revenue_per_sf: 462.5,
      actual_revenue_per_sf: 630,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Margin and occupancy assumptions need tightening.",
      },
    };

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={fullServiceProject}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_full_service_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.queryByText((text) =>
        text.includes(
          "Sales/SF clears easily; the hurdle is margin/prime cost and occupancy cost, not top-line demand."
        )
      )
    ).not.toBeInTheDocument();
  });

  it("replaces restaurant footer unit-template fields with restaurant-native metrics and keeps non-restaurant unchanged", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "restaurant",
            RESTAURANT_POLICY_CASES[0].subtype,
            RESTAURANT_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            RESTAURANT_POLICY_CASES[0].profileId,
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of RESTAURANT_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject("restaurant", testCase.subtype, testCase.profileId)}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              "Needs Work",
              "low_flex_before_break_buffer"
            ) as any}
          />
        </MemoryRouter>
      );

      expect(screen.getByText("COST PER SF")).toBeInTheDocument();
      expect(screen.getByText("SALES PER SF")).toBeInTheDocument();
      expect(screen.getByText("PRIME COST %")).toBeInTheDocument();
      expect(screen.getByText("BUILDOUT PAYBACK")).toBeInTheDocument();
      expect(screen.queryByText("INVESTMENT PER UNIT")).not.toBeInTheDocument();
      expect(screen.queryByText("Total Units")).not.toBeInTheDocument();
    }

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("office", "class_a", "office_class_a_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "office_class_a_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("INVESTMENT PER UNIT")).toBeInTheDocument();
  });

  it("keeps canonical decision status/reason/provenance contract parity across restaurant, hospitality, multifamily, and industrial", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            CROSS_TYPE_POLICY_CASES[0].buildingType,
            CROSS_TYPE_POLICY_CASES[0].subtype,
            CROSS_TYPE_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            CROSS_TYPE_POLICY_CASES[0].profileId,
            CROSS_TYPE_POLICY_CASES[0].decisionStatus,
            CROSS_TYPE_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of CROSS_TYPE_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              testCase.buildingType,
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
    }
  });

  it("renders industrial canonical decision status/reason/provenance contract", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "industrial",
            "distribution_center",
            "industrial_distribution_center_v1"
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "industrial_distribution_center_v1",
            "Needs Work",
            "tight_flex_band"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Investment Decision: Needs Work")).toBeInTheDocument();
    const policyLineMatches = screen.getAllByText((_, element) => {
      if (element?.tagName.toLowerCase() !== "p") return false;
      const text = element.textContent ?? "";
      return text.includes("Policy basis: DealShield canonical policy");
    });
    expect(policyLineMatches.length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
  });

  it("uses distribution-center NO-GO policy basis copy, target-yield badge wording, and milestone disclaimer updates", () => {
    const distributionProject = buildCrossTypeProject(
      "industrial",
      "distribution_center",
      "industrial_distribution_center_v1"
    );
    distributionProject.analysis.calculations.revenue_requirements = {
      required_value: 1_250_000,
      market_value: 1_050_000,
      required_revenue_per_sf: 52.5,
      actual_revenue_per_sf: 46.2,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Tighten yield drivers before IC.",
      },
    };

    const distributionDealShield = {
      ...buildCrossTypeDealShieldViewModel(
        "industrial_distribution_center_v1",
        "NO-GO",
        "base_case_break_condition"
      ),
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO because value support is below policy threshold under current distribution-center assumptions.",
        policy_basis_line:
          "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive).",
        target_yield_lens_label: "Below Target Yield",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: -220000,
      },
      first_break_condition_holds: true,
      decision_summary: {
        value_gap: -220000,
        value_gap_pct: -1.1,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={distributionProject}
          dealShieldData={distributionDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getAllByText(
        "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive)."
      ).length
    ).toBeGreaterThan(0);
    expect(
      screen.queryByText((text) => text.includes("Policy source: dealshield_policy_v1"))
    ).not.toBeInTheDocument();
    expect(screen.getAllByText("Below Target Yield").length).toBeGreaterThan(0);
    expect(screen.queryByText("Not Feasible")).not.toBeInTheDocument();
    expect(screen.getByText("Planning timeline (schedule risk not modeled in base case).")).toBeInTheDocument();
    expect(
      screen.queryByText(
        "Milestones are baseline planning assumptions. Yield, DSCR, and NOI metrics do not currently include schedule-delay or acceleration effects."
      )
    ).not.toBeInTheDocument();
  });

  it("uses distribution-center NO-GO policy fallback copy when base-break evidence is unverified", () => {
    const distributionDealShield = {
      ...buildCrossTypeDealShieldViewModel(
        "industrial_distribution_center_v1",
        "NO-GO",
        "base_case_break_condition"
      ),
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO under current distribution-center assumptions with value support below threshold.",
        policy_basis_line:
          "Policy basis: DealShield canonical policy — NO-GO under current value-gap threshold stress.",
        target_yield_lens_label: "Below Target Yield",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: 45000,
      },
      first_break_condition_holds: false,
      decision_summary: {
        value_gap: 45000,
        value_gap_pct: 0.2,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "industrial",
            "distribution_center",
            "industrial_distribution_center_v1"
          )}
          dealShieldData={distributionDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getAllByText(
        "Policy basis: DealShield canonical policy — NO-GO under current value-gap threshold stress."
      ).length
    ).toBeGreaterThan(0);
    expect(
      screen.queryByText("Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive).")
    ).not.toBeInTheDocument();
  });

  it("renders industrial-native executive metric framing for all five industrial subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "industrial",
            INDUSTRIAL_POLICY_CASES[0].subtype,
            INDUSTRIAL_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            INDUSTRIAL_POLICY_CASES[0].profileId,
            INDUSTRIAL_POLICY_CASES[0].decisionStatus,
            INDUSTRIAL_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of INDUSTRIAL_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject("industrial", testCase.subtype, testCase.profileId)}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(screen.getByText("Debt Lens: DSCR")).toBeInTheDocument();
      expect(screen.getByText("Yield Spread vs Market")).toBeInTheDocument();
      expect(screen.getByText("INVESTMENT PER SF")).toBeInTheDocument();
      expect(
        screen.getByText("See what it takes to clear target yield through NOI lift, scope compression, or both.")
      ).toBeInTheDocument();
      expect(screen.queryAllByText("Simple Payback (yrs)")).toHaveLength(0);
      expect(screen.queryByText("INVESTMENT PER UNIT")).not.toBeInTheDocument();

      if (testCase.subtype === "cold_storage") {
        expect(
          screen.getByText((text) =>
            text.includes(
              "For cold storage, this signals whether refrigeration/utility load + commissioning ramp assumptions can clear both equity and lender hurdles."
            )
          )
        ).toBeInTheDocument();
      }

      if (testCase.subtype === "warehouse") {
        expect(
          screen.getByText((text) =>
            text.includes(
              "validate slab thickness, dock package, ESFR, truck court and utility routing"
            )
          )
        ).toBeInTheDocument();
      } else if (testCase.subtype === "cold_storage") {
        expect(
          screen.getByText((text) =>
            text.includes(
              "prioritize insulated slab + vapor barrier, panel/envelope performance, refrigeration utility loads, and commissioning gates to keep the budget aligned"
            )
          )
        ).toBeInTheDocument();
      } else if (testCase.decisionStatus === "Needs Work") {
        expect(
          screen.getByText((text) =>
            text.includes(
              "prioritize slab thickness, dock count, ESFR coverage, and truck court design"
            )
          )
        ).toBeInTheDocument();
      }
    }
  });

  it("uses warehouse-only Cushion badge wording when revenue feasibility card is present", () => {
    const warehouseProject = buildCrossTypeProject(
      "industrial",
      "warehouse",
      "industrial_warehouse_v1"
    );
    warehouseProject.analysis.calculations.revenue_requirements = {
      required_value: 300000,
      market_value: 310000,
      required_revenue_per_sf: 37.5,
      actual_revenue_per_sf: 38.75,
      feasibility: {
        status: "Feasible",
        recommendation: "Maintain underwriting discipline.",
      },
    };

    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={warehouseProject}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "industrial_warehouse_v1",
              "Needs Work",
              "low_flex_before_break_buffer"
            ),
            {
              how_to_interpret:
                "Needs Work due to thin policy cushion under current warehouse assumptions.",
              target_yield_lens_label: "Cushion",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getAllByText(/^Cushion$/).length).toBeGreaterThan(0);
    expect(screen.queryByText(/^Marginal$/)).not.toBeInTheDocument();

    const distributionProject = buildCrossTypeProject(
      "industrial",
      "distribution_center",
      "industrial_distribution_center_v1"
    );
    distributionProject.analysis.calculations.revenue_requirements = {
      required_value: 300000,
      market_value: 310000,
      required_revenue_per_sf: 37.5,
      actual_revenue_per_sf: 38.75,
      feasibility: {
        status: "Feasible",
        recommendation: "Maintain underwriting discipline.",
      },
    };

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={distributionProject}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "industrial_distribution_center_v1",
              "Needs Work",
              "tight_flex_band"
            ),
            {
              how_to_interpret:
                "Needs Work due to tight flex band in distribution-center downside tests.",
              target_yield_lens_label: "Marginal",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getAllByText(/^Marginal$/).length).toBeGreaterThan(0);
    expect(screen.queryAllByText(/^Cushion$/).length).toBe(0);
  });

  it("adds manufacturing-specific downside note in NO-GO decision explanation", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("industrial", "manufacturing", "industrial_manufacturing_v1")}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "industrial_manufacturing_v1",
              "NO-GO",
              "base_value_gap_non_positive"
            ),
            {
              how_to_interpret:
                "NO-GO under current manufacturing assumptions. For manufacturing, also validate commissioning/qualification timeline and process utility loads—those usually drive the downside.",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText(
        "For manufacturing, also validate commissioning/qualification timeline and process utility loads—those usually drive the downside.",
        { exact: false }
      )
    ).toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("industrial", "distribution_center", "industrial_distribution_center_v1")}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "industrial_distribution_center_v1",
              "NO-GO",
              "base_value_gap_non_positive"
            ),
            {
              how_to_interpret:
                "NO-GO under current distribution-center assumptions with value support below threshold.",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.queryByText(
        "For manufacturing, also validate commissioning/qualification timeline and process utility loads—those usually drive the downside.",
        { exact: false }
      )
    ).not.toBeInTheDocument();
  });

  it("uses manufacturing policy-basis copy and lens-safe target-yield wording without debug identifiers", () => {
    const manufacturingProject = buildCrossTypeProject(
      "industrial",
      "manufacturing",
      "industrial_manufacturing_v1"
    );
    manufacturingProject.analysis.calculations.revenue_requirements = {
      required_value: 1_520_000,
      market_value: 1_280_000,
      required_revenue_per_sf: 74.2,
      actual_revenue_per_sf: 65.0,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Rework process MEP scope and commissioning assumptions.",
      },
    };

    const manufacturingDealShield = {
      ...buildCrossTypeDealShieldViewModel(
        "industrial_manufacturing_v1",
        "NO-GO",
        "base_case_break_condition"
      ),
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO under current manufacturing assumptions with value support below threshold.",
        policy_basis_line:
          "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive).",
        target_yield_lens_label: "Target Yield: Not Met",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: -140000,
      },
      first_break_condition_holds: true,
      decision_summary: {
        value_gap: -140000,
        value_gap_pct: -0.8,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={manufacturingProject}
          dealShieldData={manufacturingDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getAllByText(
        "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive)."
      ).length
    ).toBeGreaterThan(0);
    expect(
      screen.queryByText((text) => text.includes("Policy source: dealshield_policy_v1"))
    ).not.toBeInTheDocument();
    expect(screen.getAllByText("Target Yield: Not Met").length).toBeGreaterThan(0);
    expect(screen.queryByText("Not Feasible")).not.toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes(
          "utility/service capacity, process MEP integration, commissioning/qualification timeline, and throughput ramp assumptions"
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes("dock configuration") || text.includes("truck flow")
      )
    ).not.toBeInTheDocument();
    expect(screen.getByText("Planning timeline (schedule risk not modeled in base case).")).toBeInTheDocument();
  });

  it("applies manufacturing trust-copy via manufacturing profile ids even when parsed subtype is not manufacturing", () => {
    const project = buildCrossTypeProject(
      "industrial",
      "warehouse",
      "industrial_manufacturing_v1"
    );
    project.analysis.calculations.revenue_requirements = {
      required_value: 1_520_000,
      market_value: 1_280_000,
      required_revenue_per_sf: 74.2,
      actual_revenue_per_sf: 65.0,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Rework process MEP scope and commissioning assumptions.",
      },
    };

    const dealShield = {
      ...buildCrossTypeDealShieldViewModel(
        "industrial_manufacturing_v1",
        "NO-GO",
        "base_case_break_condition"
      ),
      executive_rendered_copy: {
        how_to_interpret:
          "NO-GO under current manufacturing assumptions with value support below threshold.",
        policy_basis_line:
          "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive).",
        target_yield_lens_label: "Target Yield: Not Met",
      },
      first_break_condition: {
        scenario_id: "base",
        scenario_label: "Base",
        break_metric: "value_gap",
        operator: "<=",
        threshold: 0,
        observed_value: -140000,
      },
      first_break_condition_holds: true,
      decision_summary: {
        value_gap: -140000,
        value_gap_pct: -0.8,
      },
    } as any;

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={dealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getAllByText(
        "Policy basis: DealShield canonical policy — Base case breaks (value gap non-positive)."
      ).length
    ).toBeGreaterThan(0);
    expect(
      screen.queryByText((text) => text.includes("Policy source: dealshield_policy_v1"))
    ).not.toBeInTheDocument();
    expect(screen.getAllByText("Target Yield: Not Met").length).toBeGreaterThan(0);
    expect(
      screen.getByText((text) =>
        text.includes(
          "For manufacturing, this signals whether utility/service capacity, process MEP integration, commissioning/qualification timeline, and throughput ramp assumptions can clear both equity and lender hurdles."
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes("For industrial, this signals whether the rent roll, dock configuration, and truck flow can clear both equity and lender hurdles.")
      )
    ).not.toBeInTheDocument();
    expect(screen.getByText("Planning timeline (schedule risk not modeled in base case).")).toBeInTheDocument();
  });

  it("uses cold-storage-native NO-GO action levers instead of generic scope-cut wording", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("industrial", "cold_storage", "industrial_cold_storage_v1")}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "industrial_cold_storage_v1",
              "NO-GO",
              "base_value_gap_non_positive"
            ),
            {
              how_to_interpret:
                "Confirm refrigeration plant scope + utility rates\nUnderwrite commissioning-to-stabilization ramp (don't assume day-1 utilization)\nReduce basis via envelope/plant VE, not generic scope cuts",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText("Confirm refrigeration plant scope + utility rates", { exact: false })
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Underwrite commissioning-to-stabilization ramp (don't assume day-1 utilization)",
        { exact: false }
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Reduce basis via envelope/plant VE, not generic scope cuts",
        { exact: false }
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Improve rents, cut scope, or rework the capital stack before advancing.", {
        exact: false,
      })
    ).not.toBeInTheDocument();
  });

  it("uses market-rate multifamily NO-GO narrative with explicit equity/debt lens precedence and subtype-native fix paths", () => {
    const marketRateDealShield = buildCrossTypeDealShieldViewModel(
      "multifamily_market_rate_apartments_v1",
      "NO-GO",
      "base_case_break_condition"
    ) as any;
    marketRateDealShield.executive_rendered_copy = {
      how_to_interpret:
        "NO-GO because value gap is non-positive (equity lens), even with DSCR 1.46× meeting 1.30× (debt lens). Primary fix paths: concessions + lease-up pace (market reality), expense load / payroll / utilities (ops reality), basis discipline (hard + soft) / fee stack, and debt sizing / rate / IO period (debt lens).",
      policy_basis_line: "Policy basis: DealShield canonical policy.",
      target_yield_lens_label: "Target Yield: Not Met",
    };
    marketRateDealShield.decision_summary = {
      value_gap: -250000,
      value_gap_pct: -3.4,
    };

    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "multifamily",
            "market_rate_apartments",
            "multifamily_market_rate_apartments_v1"
          )}
          dealShieldData={marketRateDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes(
          "NO-GO because value gap is non-positive (equity lens), even with DSCR 1.46× meeting 1.30× (debt lens)."
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes(
          "Primary fix paths: concessions + lease-up pace (market reality), expense load / payroll / utilities (ops reality), basis discipline (hard + soft) / fee stack, and debt sizing / rate / IO period (debt lens)."
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.queryByText("Improve rents, cut scope, or rework the capital stack before advancing.", {
        exact: false,
      })
    ).not.toBeInTheDocument();

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "multifamily",
            "luxury_apartments",
            "multifamily_luxury_apartments_v1"
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "multifamily_luxury_apartments_v1",
            "NO-GO",
            "base_case_break_condition"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(
      screen.queryByText((text) =>
        text.includes(
          "NO-GO because value gap is non-positive (equity lens), even with DSCR 1.46× meeting 1.30× (debt lens)."
        )
      )
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText((text) =>
        text.includes(
          "Primary fix paths: concessions + lease-up pace (market reality), expense load / payroll / utilities (ops reality), basis discipline (hard + soft) / fee stack, and debt sizing / rate / IO period (debt lens)."
        )
      )
    ).not.toBeInTheDocument();
  });

  it("uses market-rate value-gap-first NO-GO copy when DSCR is below target and shows program-assumption footer language", () => {
    const marketRateProject = buildCrossTypeProject(
      "multifamily",
      "market_rate_apartments",
      "multifamily_market_rate_apartments_v1"
    );
    marketRateProject.analysis.calculations.ownership_analysis.debt_metrics.calculated_dscr = 1.19;
    marketRateProject.analysis.calculations.ownership_analysis.debt_metrics.target_dscr = 1.2;
    marketRateProject.analysis.calculations.dealshield_scenarios.scenarios.base.ownership_analysis.debt_metrics.calculated_dscr =
      1.19;
    marketRateProject.analysis.calculations.dealshield_scenarios.scenarios.base.ownership_analysis.debt_metrics.target_dscr =
      1.2;

    const marketRateDealShield = buildCrossTypeDealShieldViewModel(
      "multifamily_market_rate_apartments_v1",
      "NO-GO",
      "base_case_break_condition"
    ) as any;
    marketRateDealShield.executive_rendered_copy = {
      how_to_interpret:
        "NO-GO because value gap is non-positive (policy break), and Debt Lens DSCR 1.19× is below 1.20×. Bottom line: policy breaks on value gap; Debt Lens DSCR is below target (1.19× vs 1.20×); focus diligence on cost basis + carry drivers before IC.",
      policy_basis_line: "Policy basis: DealShield canonical policy.",
      target_yield_lens_label: "Target Yield: Not Met",
    };
    marketRateDealShield.decision_summary = {
      value_gap: -3_600_000,
      value_gap_pct: -7.8,
    };

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={marketRateProject}
          dealShieldData={marketRateDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes(
          "NO-GO because value gap is non-positive (policy break), and Debt Lens DSCR 1.19× is below 1.20×."
        )
      )
    ).toBeInTheDocument();
    expect(
      screen.getAllByText((text) =>
        text.includes(
          "Bottom line: policy breaks on value gap; Debt Lens DSCR is below target (1.19× vs 1.20×); focus diligence on cost basis + carry drivers before IC."
        )
      ).length
    ).toBeGreaterThan(0);
    expect(screen.getByText("Program assumption")).toBeInTheDocument();
    expect(screen.queryByText("Derived from square footage and density")).not.toBeInTheDocument();
  });

  it("uses affordable-housing lens-separated NO-GO copy and NOI-driven feasibility messaging", () => {
    const affordableProject = buildCrossTypeProject(
      "multifamily",
      "affordable_housing",
      "multifamily_affordable_housing_v1"
    );
    affordableProject.analysis.calculations.ownership_analysis.debt_metrics.calculated_dscr = 2.61;
    affordableProject.analysis.calculations.ownership_analysis.debt_metrics.target_dscr = 1.15;
    affordableProject.analysis.calculations.dealshield_scenarios.scenarios.base.ownership_analysis.debt_metrics.calculated_dscr =
      2.61;
    affordableProject.analysis.calculations.dealshield_scenarios.scenarios.base.ownership_analysis.debt_metrics.target_dscr =
      1.15;
    affordableProject.analysis.calculations.revenue_requirements = {
      required_value: 2_950_000,
      market_value: 2_620_000,
      required_revenue_per_sf: 13,
      actual_revenue_per_sf: 21,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Cost controls and scope alignment are required to close NOI gap.",
      },
    };

    const affordableDealShield = buildCrossTypeDealShieldViewModel(
      "multifamily_affordable_housing_v1",
      "NO-GO",
      "base_case_break_condition"
    ) as any;
    affordableDealShield.executive_rendered_copy = {
      how_to_interpret:
        "NO-GO because the policy breaks on stabilized value gap (negative). Debt Lens: DSCR 2.61× clears target 1.15×, so this is not a lender-coverage failure. Equity/Market Lens: yield on cost (5.2%) is below the market benchmark (7.5%), indicating weak value support at this basis. Bottom line: DSCR clears, but the policy fails on negative value gap—diligence should focus on compliance-driven scope drift, allowances/contingency realism, and cost controls under capped rents.",
      policy_basis_line: "Policy basis: DealShield canonical policy.",
      target_yield_lens_label: "Below Target NOI (Cost/Expense Driven)",
    };
    affordableDealShield.decision_summary = {
      value_gap: -3_600_000,
      value_gap_pct: -7.8,
    };

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={affordableProject}
          dealShieldData={affordableDealShield}
        />
      </MemoryRouter>
    );

    expect(
      screen.getByText((text) =>
        text.includes("NO-GO because the policy breaks on stabilized value gap (negative).")
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("Debt Lens: DSCR 2.61× clears target 1.15×, so this is not a lender-coverage failure.")
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("Equity/Market Lens: yield on cost") &&
        text.includes("is below the market benchmark") &&
        text.includes("indicating weak value support at this basis.")
      )
    ).toBeInTheDocument();
    expect(
      screen.getAllByText((text) =>
        text.includes(
          "Bottom line: DSCR clears, but the policy fails on negative value gap—diligence should focus on compliance-driven scope drift, allowances/contingency realism, and cost controls under capped rents."
        )
      ).length
    ).toBeGreaterThan(0);
    expect(screen.getAllByText("Below Target NOI (Cost/Expense Driven)").length).toBeGreaterThan(0);
    expect(
      screen.getByText(
        "Revenue per SF is sufficient; the shortfall is driven by NOI/expense/cost basis, not rent levels."
      )
    ).toBeInTheDocument();
    expect(screen.getByText("Program assumption")).toBeInTheDocument();
    expect(screen.queryByText("Derived from square footage and density")).not.toBeInTheDocument();
  });

  it("renders explicit multifamily canonical decision status/reason/provenance parity", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "multifamily",
            MULTIFAMILY_POLICY_CASES[0].subtype,
            MULTIFAMILY_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            MULTIFAMILY_POLICY_CASES[0].profileId,
            MULTIFAMILY_POLICY_CASES[0].decisionStatus,
            MULTIFAMILY_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of MULTIFAMILY_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "multifamily",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("renders multifamily-native debt/equity/reality lens copy and metric labels", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "multifamily",
            "luxury_apartments",
            "multifamily_luxury_apartments_v1"
          )}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "multifamily_luxury_apartments_v1",
              "GO",
              "base_value_gap_positive"
            ),
            {
              how_to_interpret:
                "Project clears multifamily underwriting across equity and debt lenses. Equity Lens: value support remains positive. Debt Lens: coverage clears target. Reality Check: maintain lease-up and expense discipline.",
              target_yield_lens_label: "Target Yield: Thin Cushion",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Debt Lens: DSCR (Target 1.30×)")).toBeInTheDocument();
    expect(screen.getByText("Stabilized Value Gap")).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("Project clears multifamily underwriting across equity and debt lenses.")
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((text) =>
        text.includes("Equity Lens:") &&
        text.includes("Debt Lens:") &&
        text.includes("Reality Check:")
      )
    ).toBeInTheDocument();
  });

  it("applies luxury multifamily target-yield and footer copy overrides without changing GO verdict logic", () => {
    const luxuryProject = buildCrossTypeProject(
      "multifamily",
      "luxury_apartments",
      "multifamily_luxury_apartments_v1"
    );
    luxuryProject.analysis.calculations.revenue_analysis = {
      annual_revenue: 5_040_000,
      net_income: 250_000,
    };
    luxuryProject.analysis.calculations.revenue_requirements = {
      required_value: 296_000,
      market_value: 250_000,
      required_revenue_per_sf: 462.5,
      actual_revenue_per_sf: 630,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Margin and occupancy assumptions need tightening.",
      },
    };

    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={luxuryProject}
          dealShieldData={withExecutiveRenderedCopy(
            buildCrossTypeDealShieldViewModel(
              "multifamily_luxury_apartments_v1",
              "GO",
              "base_value_gap_positive"
            ),
            {
              how_to_interpret:
                "Project clears multifamily underwriting across equity and debt lenses.",
              target_yield_lens_label: "Below Target Yield (Thin Cushion)",
            }
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Investment Decision: GO")).toBeInTheDocument();
    expect(screen.getAllByText("Below Target Yield (Thin Cushion)").length).toBeGreaterThan(0);
    expect(screen.queryByText("Not Feasible")).not.toBeInTheDocument();
    expect(
      screen.getByText(
        "This section tests the target yield hurdle; the overall verdict is driven by DealShield policy/value gap."
      )
    ).toBeInTheDocument();
    expect(screen.getByText("Planning timeline (schedule risk not modeled in base case).")).toBeInTheDocument();
    expect(screen.getByText("COST PER UNIT")).toBeInTheDocument();
    expect(screen.getByText("Cost per modeled unit")).toBeInTheDocument();
    expect(screen.getByText("Program assumption")).toBeInTheDocument();
    expect(screen.queryByText("Derived from square footage and density")).not.toBeInTheDocument();
    expect(screen.queryByText("Total project cost divided by units")).not.toBeInTheDocument();

    const marketRateProject = buildCrossTypeProject(
      "multifamily",
      "market_rate_apartments",
      "multifamily_market_rate_apartments_v1"
    );
    marketRateProject.analysis.calculations.revenue_analysis = {
      annual_revenue: 5_040_000,
      net_income: 250_000,
    };
    marketRateProject.analysis.calculations.revenue_requirements = {
      required_value: 296_000,
      market_value: 250_000,
      required_revenue_per_sf: 462.5,
      actual_revenue_per_sf: 630,
      feasibility: {
        status: "Not Feasible",
        recommendation: "Margin and occupancy assumptions need tightening.",
      },
    };

    rerender(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={marketRateProject}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "multifamily_market_rate_apartments_v1",
            "GO",
            "base_value_gap_positive"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getAllByText("Target Yield: Not Met").length).toBeGreaterThan(0);
    expect(screen.queryAllByText("Below Target Yield (Thin Cushion)").length).toBe(0);
    expect(
      screen.queryByText(
        "This section tests the target yield hurdle; the overall verdict is driven by DealShield policy/value gap."
      )
    ).not.toBeInTheDocument();
  });

  it("keeps canonical decision status/reason/provenance parity for office class_a and class_b", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "office",
            OFFICE_POLICY_CASES[0].subtype,
            OFFICE_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            OFFICE_POLICY_CASES[0].profileId,
            OFFICE_POLICY_CASES[0].decisionStatus,
            OFFICE_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of OFFICE_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject("office", testCase.subtype, testCase.profileId)}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for retail shopping_center and big_box", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "retail",
            RETAIL_POLICY_CASES[0].subtype,
            RETAIL_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            RETAIL_POLICY_CASES[0].profileId,
            RETAIL_POLICY_CASES[0].decisionStatus,
            RETAIL_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of RETAIL_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject("retail", testCase.subtype, testCase.profileId)}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for specialty subtypes, including data center", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "specialty",
            SPECIALTY_POLICY_CASES[0].subtype,
            SPECIALTY_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            SPECIALTY_POLICY_CASES[0].profileId,
            SPECIALTY_POLICY_CASES[0].decisionStatus,
            SPECIALTY_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of SPECIALTY_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "specialty",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for all healthcare subtypes, including medical_office_building", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "healthcare",
            HEALTHCARE_POLICY_CASES[0].subtype,
            HEALTHCARE_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            HEALTHCARE_POLICY_CASES[0].profileId,
            HEALTHCARE_POLICY_CASES[0].decisionStatus,
            HEALTHCARE_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of HEALTHCARE_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "healthcare",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for all five educational subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "educational",
            EDUCATIONAL_POLICY_CASES[0].subtype,
            EDUCATIONAL_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            EDUCATIONAL_POLICY_CASES[0].profileId,
            EDUCATIONAL_POLICY_CASES[0].decisionStatus,
            EDUCATIONAL_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of EDUCATIONAL_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "educational",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for all five civic subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "civic",
            CIVIC_POLICY_CASES[0].subtype,
            CIVIC_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            CIVIC_POLICY_CASES[0].profileId,
            CIVIC_POLICY_CASES[0].decisionStatus,
            CIVIC_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of CIVIC_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "civic",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for all five recreation subtypes", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "recreation",
            RECREATION_POLICY_CASES[0].subtype,
            RECREATION_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            RECREATION_POLICY_CASES[0].profileId,
            RECREATION_POLICY_CASES[0].decisionStatus,
            RECREATION_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of RECREATION_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "recreation",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps canonical decision status/reason/provenance parity for all four parking subtypes with policy-source consistency", () => {
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "parking",
            PARKING_POLICY_CASES[0].subtype,
            PARKING_POLICY_CASES[0].profileId
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            PARKING_POLICY_CASES[0].profileId,
            PARKING_POLICY_CASES[0].decisionStatus,
            PARKING_POLICY_CASES[0].decisionReasonCode
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of PARKING_POLICY_CASES) {
      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete
            project={buildCrossTypeProject(
              "parking",
              testCase.subtype,
              testCase.profileId
            )}
            dealShieldData={buildCrossTypeDealShieldViewModel(
              testCase.profileId,
              testCase.decisionStatus,
              testCase.decisionReasonCode
            ) as any}
          />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });

  it("keeps mixed_use canonical status/reason/provenance parity for all five subtypes and carries split provenance through fixtures", () => {
    const first = MIXED_USE_POLICY_CASES[0];
    const { rerender } = render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject(
            "mixed_use",
            first.subtype,
            first.profileId,
            first.mixedUseSplitValue
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            first.profileId,
            first.decisionStatus,
            first.decisionReasonCode,
            {
              mixedUseSplitSource: first.mixedUseSplitSource,
              mixedUseSplitValue: first.mixedUseSplitValue,
              mixedUseSplitMetricRef: first.mixedUseSplitMetricRef,
            }
          ) as any}
        />
      </MemoryRouter>
    );

    for (const testCase of MIXED_USE_POLICY_CASES) {
      const project = buildCrossTypeProject(
        "mixed_use",
        testCase.subtype,
        testCase.profileId,
        testCase.mixedUseSplitValue
      );
      const viewModel = buildCrossTypeDealShieldViewModel(
        testCase.profileId,
        testCase.decisionStatus,
        testCase.decisionReasonCode,
        {
          mixedUseSplitSource: testCase.mixedUseSplitSource,
          mixedUseSplitValue: testCase.mixedUseSplitValue,
          mixedUseSplitMetricRef: testCase.mixedUseSplitMetricRef,
        }
      );

      expect(project.analysis.parsed_input.mixed_use_split.value).toEqual(testCase.mixedUseSplitValue);
      expect(
        project.analysis.calculations.dealshield_scenarios.provenance.scenario_inputs.base
          .mixed_use_split_source
      ).toBe("user_input");
      expect((viewModel as any).decision_status_provenance.mixed_use_split_source).toBe(
        testCase.mixedUseSplitSource
      );
      expect((viewModel as any).provenance.scenario_inputs.base.mixed_use_split.value).toEqual(
        testCase.mixedUseSplitValue
      );

      rerender(
        <MemoryRouter>
          <ExecutiveViewComplete project={project} dealShieldData={viewModel as any} />
        </MemoryRouter>
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      const policyLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Policy basis: DealShield canonical policy")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });
});
