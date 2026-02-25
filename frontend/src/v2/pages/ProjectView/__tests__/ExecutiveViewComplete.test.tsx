import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ExecutiveViewComplete } from "../ExecutiveViewComplete";

const HOSPITALITY_PROFILE_IDS = [
  "hospitality_limited_service_hotel_v1",
  "hospitality_full_service_hotel_v1",
];

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

describe("ExecutiveViewComplete", () => {
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
        text.includes("Policy source: payload_or_decision_summary") &&
        text.includes("restaurant_policy_v1") &&
        text.includes("reason: explicit_status_signal")
      );
    });
    expect(policyLineMatches.length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("dealshield_canonical_policy_v1") &&
          text.includes("reason: low_flex_before_break_buffer")
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
      return (
        text.includes("Policy source: dealshield_policy_v1") &&
        text.includes("decision_insurance_subtype_policy_v1") &&
        text.includes("reason: tight_flex_band")
      );
    });
    expect(policyLineMatches.length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
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
          text.includes("Policy source: dealshield_policy_v1") &&
          text.includes("decision_insurance_subtype_policy_v1") &&
          text.includes(`reason: ${testCase.decisionReasonCode}`)
        );
      });
      expect(policyLineMatches.length).toBeGreaterThan(0);
      expect(screen.getByRole("button", { name: "Scenario" })).toBeInTheDocument();
    }
  });
});
