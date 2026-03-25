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
  if (buildingType === "multifamily") {
    const modeledUnits =
      subtype === "luxury_apartments"
        ? 72
        : subtype === "affordable_housing"
          ? 64
          : 68;
    const annualRevenue =
      project.analysis.calculations.revenue_analysis?.annual_revenue ?? 1850000;
    const totalProjectCost =
      project.analysis.calculations.totals?.total_project_cost ?? 3700000;
    project.analysis.calculations.operational_metrics = {
      ...(project.analysis.calculations.operational_metrics || {}),
      per_unit: {
        ...(project.analysis.calculations.operational_metrics?.per_unit || {}),
        units: modeledUnits,
        units_source: "test_fixture",
        annual_revenue_per_unit: annualRevenue / modeledUnits,
        cost_per_unit: totalProjectCost / modeledUnits,
      },
    };
    project.analysis.calculations.ownership_analysis.operational_metrics =
      project.analysis.calculations.operational_metrics;
    project.analysis.calculations.project_info.unit_label = "Units";
    project.analysis.calculations.project_info.unit_type = "units";
  }
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

const buildImagingCenterProject = (options?: {
  mriSuites?: number;
  ctSuites?: number;
}) => {
  const project = buildCrossTypeProject(
    "healthcare",
    "imaging_center",
    "healthcare_imaging_center_v1"
  );
  const mriSuites = options?.mriSuites ?? 0;
  const ctSuites = options?.ctSuites ?? 0;
  const hasExplicitModalityCounts = mriSuites + ctSuites > 0;
  const unitLabel = hasExplicitModalityCounts
    ? "specified modality suites"
    : "unspecified modality program";
  const unitCountSource = hasExplicitModalityCounts
    ? "explicit_modality_counts"
    : "unspecified_modality_program";
  const totalSpecifiedModalitySuites = hasExplicitModalityCounts ? mriSuites + ctSuites : null;
  const imagingModalityProgram = {
    state: unitCountSource,
    has_explicit_modality_counts: hasExplicitModalityCounts,
    mri_suites: hasExplicitModalityCounts && mriSuites > 0 ? mriSuites : null,
    ct_suites: hasExplicitModalityCounts && ctSuites > 0 ? ctSuites : null,
    total_specified_modality_suites: totalSpecifiedModalitySuites,
    unit_label: unitLabel,
    unit_count_source: unitCountSource,
  };

  project.analysis.calculations.facility_metrics = {
    type: "healthcare",
    unit_label: unitLabel,
    unit_count_source: unitCountSource,
    imaging_modality_program: imagingModalityProgram,
    ...(hasExplicitModalityCounts
      ? {
          units: totalSpecifiedModalitySuites,
          entries: [
            ...(mriSuites > 0
              ? [{ id: "mri_suites", label: "MRI Suites", value: mriSuites, unit: "suites" }]
              : []),
            ...(ctSuites > 0
              ? [{ id: "ct_suites", label: "CT Suites", value: ctSuites, unit: "suites" }]
              : []),
            {
              id: "total_specified_modality_suites",
              label: "Total Specified Modality Suites",
              value: totalSpecifiedModalitySuites,
              unit: "suites",
            },
          ],
        }
      : {}),
  };
  project.analysis.calculations.operational_metrics = {
    staffing: hasExplicitModalityCounts
      ? [
          ...(mriSuites > 0 ? [{ label: "MRI Suites", value: String(mriSuites) }] : []),
          ...(ctSuites > 0 ? [{ label: "CT Suites", value: String(ctSuites) }] : []),
          {
            label: "Total Specified Modality Suites",
            value: String(totalSpecifiedModalitySuites),
          },
        ]
      : [
          { label: "Modality Program", value: "Unspecified" },
          { label: "Visible Unit Contract", value: "MRI/CT counts required" },
        ],
    revenue: {
      "Revenue per SF": "$433",
      "Labor Cost Ratio": "32%",
      "Operating Margin": "22.0%",
    },
    kpis: hasExplicitModalityCounts
      ? [
          { label: "Specified Modality Suites", value: String(totalSpecifiedModalitySuites), color: "green" },
          { label: "Modality Utilization", value: "Explicit MRI/CT counts", color: "green" },
          { label: "Modality Program Efficiency", value: "Visible units aligned", color: "green" },
        ]
      : [
          { label: "Modality Utilization", value: "Unspecified", color: "yellow" },
          { label: "Modality Program Efficiency", value: "Awaiting MRI/CT counts", color: "yellow" },
        ],
    per_unit: {
      unit_label: unitLabel,
      unit_type: unitLabel,
      units_source: unitCountSource,
      imaging_modality_program: imagingModalityProgram,
      ...(hasExplicitModalityCounts ? { units: totalSpecifiedModalitySuites } : {}),
    },
  };
  project.analysis.calculations.ownership_analysis.operational_metrics =
    project.analysis.calculations.operational_metrics;
  project.analysis.calculations.project_info = {
    ...project.analysis.calculations.project_info,
    unit_label: unitLabel,
    unit_type: unitLabel,
    unit_count_source: unitCountSource,
    imaging_modality_program: imagingModalityProgram,
    ...(hasExplicitModalityCounts ? { unit_count: totalSpecifiedModalitySuites } : {}),
  };
  if (!hasExplicitModalityCounts) {
    delete project.analysis.calculations.project_info.unit_count;
  }
  project.analysis.calculations.unit_label = unitLabel;
  project.analysis.calculations.unit_type = unitLabel;
  if (hasExplicitModalityCounts) {
    project.analysis.calculations.resolved_unit_count = totalSpecifiedModalitySuites;
  } else {
    delete project.analysis.calculations.resolved_unit_count;
  }
  return project;
};

const buildUrgentCareProject = (options?: {
  examRooms?: number;
  procedureRooms?: number;
  xRayRooms?: number;
  inferredExamRooms?: number;
}) => {
  const project = buildCrossTypeProject(
    "healthcare",
    "urgent_care",
    "healthcare_urgent_care_v1"
  );
  const examRooms = options?.examRooms;
  const procedureRooms = options?.procedureRooms ?? 0;
  const xRayRooms = options?.xRayRooms ?? 0;
  const inferredExamRooms = options?.inferredExamRooms ?? 14;
  const hasExplicitExamRooms =
    typeof examRooms === "number" && Number.isFinite(examRooms) && examRooms > 0;
  const resolvedExamRooms = hasExplicitExamRooms ? examRooms : inferredExamRooms;
  const unitLabel = hasExplicitExamRooms ? "exam rooms" : "inferred exam rooms";
  const unitCountSource = hasExplicitExamRooms
    ? "explicit_override:exam_room_count"
    : "inferred_exam_room_count";
  const annualRevenue =
    project.analysis.calculations.revenue_analysis?.annual_revenue ?? 8550000;
  const totalProjectCost =
    project.analysis.calculations.totals?.total_project_cost ?? 6500000;
  const entries = [
    ...(procedureRooms > 0
      ? [{ id: "procedure_rooms", label: "Procedure Rooms", value: procedureRooms, unit: "rooms" }]
      : []),
    ...(xRayRooms > 0
      ? [{ id: "x_ray_rooms", label: "X-Ray Rooms", value: xRayRooms, unit: "rooms" }]
      : []),
  ];

  if (hasExplicitExamRooms) {
    project.analysis.parsed_input.exam_room_count = examRooms;
  } else {
    delete project.analysis.parsed_input.exam_room_count;
  }
  if (procedureRooms > 0) {
    project.analysis.parsed_input.procedure_room_count = procedureRooms;
  }
  if (xRayRooms > 0) {
    project.analysis.parsed_input.x_ray_room_count = xRayRooms;
  }

  project.analysis.calculations.facility_metrics = {
    type: "healthcare",
    units: resolvedExamRooms,
    unit_label: unitLabel,
    unit_count_source: unitCountSource,
    cost_per_unit: totalProjectCost / resolvedExamRooms,
    revenue_per_unit: annualRevenue / resolvedExamRooms,
    ...(entries.length > 0 ? { entries } : {}),
  };
  project.analysis.calculations.operational_metrics = {
    staffing: [
      { label: hasExplicitExamRooms ? "Exam Rooms" : "Inferred Exam Rooms", value: String(resolvedExamRooms) },
      ...(procedureRooms > 0 ? [{ label: "Procedure Rooms", value: String(procedureRooms) }] : []),
      ...(xRayRooms > 0 ? [{ label: "X-Ray Rooms", value: String(xRayRooms) }] : []),
    ],
    revenue: {
      [`Revenue per ${hasExplicitExamRooms ? "Exam Rooms" : "Inferred Exam Rooms"}`]: `$${Math.round(
        annualRevenue / resolvedExamRooms
      ).toLocaleString()}`,
      "Operating Margin": "22.0%",
    },
    kpis: [
      { label: "Visits / Day", value: "156.0", color: "green" },
      {
        label: hasExplicitExamRooms ? "Exam Room Utilization" : "Inferred Exam Room Utilization",
        value: "80%",
        color: "green",
      },
    ],
    per_unit: {
      units: resolvedExamRooms,
      unit_label: unitLabel,
      unit_type: unitLabel,
      units_source: unitCountSource,
      annual_revenue_per_unit: annualRevenue / resolvedExamRooms,
      cost_per_unit: totalProjectCost / resolvedExamRooms,
      ...(entries.length > 0
        ? {
            urgent_care_room_program: {
              state: hasExplicitExamRooms
                ? "explicit_exam_room_count"
                : "inferred_exam_room_count",
              entries,
            },
          }
        : {}),
    },
  };
  project.analysis.calculations.ownership_analysis.operational_metrics =
    project.analysis.calculations.operational_metrics;
  project.analysis.calculations.project_info = {
    ...project.analysis.calculations.project_info,
    unit_label: unitLabel,
    unit_type: unitLabel,
    unit_count_source: unitCountSource,
    unit_count: resolvedExamRooms,
  };
  project.analysis.calculations.unit_label = unitLabel;
  project.analysis.calculations.unit_type = unitLabel;
  project.analysis.calculations.resolved_unit_count = resolvedExamRooms;
  return project;
};

const buildFetchedProjectViewProject = (project: any) => {
  const parsedInput = {
    ...(project.analysis?.parsed_input || {}),
  };
  if (
    typeof parsedInput.building_subtype !== "string" &&
    typeof parsedInput.subtype === "string"
  ) {
    parsedInput.building_subtype = parsedInput.subtype;
  }

  const calculationData = {
    ...(project.analysis?.calculations || {}),
    parsed_input: parsedInput,
    request_data: {
      ...(project.analysis?.calculations?.request_data || {}),
      building_type: parsedInput.building_type,
      subtype: parsedInput.subtype,
      building_subtype: parsedInput.building_subtype,
      location: parsedInput.location,
      square_footage: parsedInput.square_footage,
      floors: parsedInput.floors,
    },
  };

  return {
    ...project,
    building_type:
      parsedInput.building_type || project.analysis?.calculations?.project_info?.building_type,
    subtype: parsedInput.subtype || project.analysis?.calculations?.project_info?.subtype,
    calculation_data: calculationData,
    roi_analysis: calculationData.roi_analysis,
    revenue_analysis: calculationData.revenue_analysis,
    analysis: {
      calculations: calculationData,
    },
  };
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

const buildOperatingModelMetric = (
  id: string,
  label: string,
  value: number | string,
  kind: "currency" | "percentage" | "number" | "text",
  extras: Record<string, unknown> = {}
) => ({
  id,
  label,
  value,
  kind,
  ...extras,
});

const buildOperatingModel = (
  variant: string,
  sections: Array<{
    id: string;
    title: string;
    layout: "tiles" | "list" | "signals";
    metrics: Array<ReturnType<typeof buildOperatingModelMetric>>;
  }>,
  notes: string[] = []
) => ({
  variant,
  title: "Operating Model",
  sections,
  notes,
});

const withOperatingModel = (project: any, operatingModel: any) => {
  project.analysis.calculations.operating_model = operatingModel;
  project.analysis.calculations.ownership_analysis = {
    ...(project.analysis.calculations.ownership_analysis || {}),
    operating_model: operatingModel,
  };
  return project;
};

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

  it("renders a backend-owned office operating model without efficiency-score fallback semantics", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("office", "class_a", "office_class_a_v1"),
      buildOperatingModel(
        "office_underwriting",
        [
          {
            id: "office_rent_recoveries",
            title: "Rent & Recoveries",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("rent_sf", "Rent / SF", 38.25, "currency", {
                decimals: 2,
                suffix: "/yr",
              }),
              buildOperatingModelMetric("recoverable_cam", "Recoverable CAM", "$6.10/SF", "text"),
            ],
          },
          {
            id: "office_operating_burden",
            title: "Operating Burden",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("office_opex", "Operating Expenses", 312000, "currency"),
              buildOperatingModelMetric("office_margin", "NOI Margin", 0.62, "percentage"),
              buildOperatingModelMetric("office_expense_ratio", "Expense Ratio", 0.38, "percentage"),
            ],
          },
          {
            id: "office_allocations",
            title: "Cost Allocations",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("office_mgmt", "Management Allocation", 54000, "currency"),
              buildOperatingModelMetric("office_maintenance", "Maintenance Allocation", 87000, "currency"),
            ],
          },
        ],
        ["Landlord-side office underwriting and recoverable operating costs."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "office_class_a_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Operating Model")).toBeInTheDocument();
    expect(screen.getByText("Rent & Recoveries")).toBeInTheDocument();
    expect(screen.getByText("Operating Burden")).toBeInTheDocument();
    expect(screen.getByText("Cost Allocations")).toBeInTheDocument();
    expect(screen.queryByText("Efficiency Score")).not.toBeInTheDocument();
    expect(screen.queryByText("Target KPIs")).not.toBeInTheDocument();
  });

  it("renders warehouse projects with backend-owned property ops instead of staffing fallback tiles", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("industrial", "warehouse", "industrial_warehouse_v1"),
      buildOperatingModel(
        "industrial_property_ops",
        [
          {
            id: "warehouse_lease_productivity",
            title: "Lease Productivity",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("warehouse_rent", "Effective Rent / SF", 11.5, "currency", {
                decimals: 2,
                suffix: "/yr",
                emphasis: "primary",
              }),
              buildOperatingModelMetric("warehouse_occ", "Occupancy Assumption", 0.95, "percentage"),
              buildOperatingModelMetric("warehouse_margin", "NOI Margin", 0.88, "percentage"),
            ],
          },
          {
            id: "warehouse_cost_mix",
            title: "Operating Cost Mix",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("warehouse_tax", "Property Tax", 42110, "currency"),
              buildOperatingModelMetric("warehouse_utilities", "Utilities", 26318, "currency"),
              buildOperatingModelMetric("warehouse_total_expenses", "Total Expenses", 189046, "currency"),
            ],
          },
        ],
        ["Landlord-side property operations only; tenant business operations excluded."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "industrial_warehouse_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Operating Model")).toBeInTheDocument();
    expect(screen.getByText("Lease Productivity")).toBeInTheDocument();
    expect(screen.getByText("Operating Cost Mix")).toBeInTheDocument();
    expect(screen.getByText("Effective Rent / SF")).toBeInTheDocument();
    expect(screen.queryByText("Operational Efficiency")).not.toBeInTheDocument();
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
    expect(screen.queryByText("Efficiency Score")).not.toBeInTheDocument();
    expect(screen.queryByText("Target KPIs")).not.toBeInTheDocument();
  });

  it("renders backend-owned healthcare operating model content for medical office projects", () => {
    const project = withOperatingModel(
      buildCrossTypeProject(
        "healthcare",
        "medical_office_building",
        "healthcare_medical_office_building_v1"
      ),
      buildOperatingModel(
        "healthcare_operating_model",
        [
          {
            id: "mob_staffing",
            title: "Staffing",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("mob_providers", "Providers (MD/DO/NP/PA FTE)", 6, "number"),
              buildOperatingModelMetric("mob_suites", "Tenant Suites", 14, "number"),
            ],
          },
          {
            id: "mob_revenue_productivity",
            title: "Revenue Productivity",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("mob_provider_revenue", "Revenue per Provider", 520000, "currency"),
              buildOperatingModelMetric("mob_suite_revenue", "Revenue per Tenant Suites", 223000, "currency"),
            ],
          },
          {
            id: "mob_operating_signals",
            title: "Operating Signals",
            layout: "signals",
            metrics: [
              buildOperatingModelMetric("mob_utilization", "Suite Utilization", 0.87, "percentage", { state: "green" }),
              buildOperatingModelMetric("mob_throughput", "Tenant Throughput Yield", "Stable", "text", { state: "green" }),
            ],
          },
        ],
        ["Backend-owned healthcare staffing, throughput, and utilization model."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_medical_office_building_v1",
            "GO",
            "base_value_gap_positive"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Staffing")).toBeInTheDocument();
    expect(screen.getByText("Revenue Productivity")).toBeInTheDocument();
    expect(screen.getByText("Operating Signals")).toBeInTheDocument();
    expect(screen.getByText("Tenant Suites")).toBeInTheDocument();
    expect(screen.getByText("Tenant Throughput Yield")).toBeInTheDocument();
    expect(screen.queryByText("Soft Costs % of Total")).not.toBeInTheDocument();
    expect(screen.queryByText("Revenue Efficiency")).not.toBeInTheDocument();
    expect(screen.queryByText("Target KPIs")).not.toBeInTheDocument();
  });

  it("renders Imaging Center MRI-only cases with modality counts only and no fake per-suite economics", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildFetchedProjectViewProject(buildImagingCenterProject({ mriSuites: 2 }))}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_imaging_center_v1",
            "Needs Work",
            "tight_flex_band"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getAllByText("MRI Suites").length).toBeGreaterThan(0);
    expect(screen.queryByText("CT Suites")).not.toBeInTheDocument();
    expect(screen.getAllByText("Total Specified Modality Suites").length).toBeGreaterThan(0);
    expect(screen.queryByText("Cost per specified modality suites")).not.toBeInTheDocument();
    expect(screen.queryByText("Revenue per specified modality suites")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Scan Rooms")).not.toBeInTheDocument();
    expect(screen.queryByText(/scan rooms/i)).not.toBeInTheDocument();
  });

  it("renders Imaging Center modality counts without surfacing Total Scan Rooms when explicit MRI and CT counts are present", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildFetchedProjectViewProject(buildImagingCenterProject({ mriSuites: 2, ctSuites: 1 }))}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_imaging_center_v1",
            "Needs Work",
            "tight_flex_band"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("MRI Suites")).toBeInTheDocument();
    expect(screen.getByText("CT Suites")).toBeInTheDocument();
    expect(screen.getAllByText("Total Specified Modality Suites").length).toBeGreaterThan(0);
    expect(screen.getByText("MRI 2 • CT 1")).toBeInTheDocument();
    expect(screen.queryByText("Cost per specified modality suites")).not.toBeInTheDocument();
    expect(screen.queryByText("Revenue per specified modality suites")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Scan Rooms")).not.toBeInTheDocument();
    expect(screen.queryByText(/scan rooms/i)).not.toBeInTheDocument();
  });

  it("renders Imaging Center no-count cases as an unspecified modality program instead of a fake room total", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildFetchedProjectViewProject(buildImagingCenterProject())}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_imaging_center_v1",
            "Needs Work",
            "tight_flex_band"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getAllByText("Modality Program").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Unspecified").length).toBeGreaterThan(0);
    expect(
      screen.getByText(
        "Imaging Center visible unit counts appear only when MRI or CT suite counts are provided."
      )
    ).toBeInTheDocument();
    expect(screen.queryByText("Total Specified Modality Suites")).not.toBeInTheDocument();
    expect(screen.queryByText("Cost per unspecified modality program")).not.toBeInTheDocument();
    expect(screen.queryByText("Revenue per unspecified modality program")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Scan Rooms")).not.toBeInTheDocument();
    expect(screen.queryByText(/scan rooms/i)).not.toBeInTheDocument();
  });

  it("renders Urgent Care no-count cases with Inferred Exam Rooms from backend truth", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildFetchedProjectViewProject(buildUrgentCareProject())}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_urgent_care_v1",
            "GO",
            "base_value_gap_positive"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Inferred Exam Rooms")).toBeInTheDocument();
    expect(screen.queryByText(/^Exam Rooms$/)).not.toBeInTheDocument();
    expect(screen.queryByText("Procedure Rooms")).not.toBeInTheDocument();
    expect(screen.queryByText("X-Ray Rooms")).not.toBeInTheDocument();
  });

  it("renders Urgent Care procedure and x-ray room counts as separate visible program rows", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildFetchedProjectViewProject(
            buildUrgentCareProject({ examRooms: 10, procedureRooms: 2, xRayRooms: 2 })
          )}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "healthcare_urgent_care_v1",
            "GO",
            "base_value_gap_positive"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Exam Rooms")).toBeInTheDocument();
    expect(screen.getByText("Procedure Rooms")).toBeInTheDocument();
    expect(screen.getByText("X-Ray Rooms")).toBeInTheDocument();
    expect(screen.getAllByText("2").length).toBeGreaterThan(1);
    expect(screen.queryByText("Inferred Exam Rooms")).not.toBeInTheDocument();
  });

  it("renders hotel-native operating model metrics for hospitality projects", () => {
    const project = withOperatingModel(
      buildHospitalityProject("hospitality_limited_service_hotel_v1"),
      buildOperatingModel(
        "hospitality_keys",
        [
          {
            id: "hotel_keys",
            title: "Key Metrics",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("hotel_rooms", "Rooms", 160, "number"),
              buildOperatingModelMetric("hotel_adr", "ADR", 212, "currency"),
              buildOperatingModelMetric("hotel_occupancy", "Occupancy", 0.74, "percentage"),
              buildOperatingModelMetric("hotel_revpar", "RevPAR", 156.88, "currency", { decimals: 2 }),
            ],
          },
          {
            id: "hotel_performance",
            title: "Operating Performance",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("hotel_revenue", "Annual Room Revenue", 9020000, "currency"),
              buildOperatingModelMetric("hotel_margin", "NOI Margin", 0.33, "percentage"),
            ],
          },
        ],
        ["Hotel key productivity and stabilized operating conversion."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildHospitalityDealShieldViewModel(
            "hospitality_limited_service_hotel_v1"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Key Metrics")).toBeInTheDocument();
    expect(screen.getByText("Operating Performance")).toBeInTheDocument();
    expect(screen.getAllByText("Rooms").length).toBeGreaterThan(0);
    expect(screen.getAllByText("ADR").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Occupancy").length).toBeGreaterThan(0);
    expect(screen.getAllByText("RevPAR").length).toBeGreaterThan(0);
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
  });

  it("renders multifamily operating model without heuristic staffing or target tiles", () => {
    const project = withOperatingModel(
      buildCrossTypeProject(
        "multifamily",
        "market_rate_apartments",
        "multifamily_market_rate_apartments_v1"
      ),
      buildOperatingModel(
        "multifamily_unit_economics",
        [
          {
            id: "mf_unit_economics",
            title: "Unit Economics",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("mf_units", "Units", 82, "number"),
              buildOperatingModelMetric("mf_revenue_unit", "Revenue / Unit", 22800, "currency", {
                suffix: "/yr",
              }),
              buildOperatingModelMetric("mf_average_rent", "Average Rent", 1900, "currency", {
                suffix: "/mo",
              }),
              buildOperatingModelMetric("mf_occ", "Occupancy Assumption", 0.94, "percentage"),
            ],
          },
          {
            id: "mf_burden",
            title: "Operating Burden",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("mf_expenses", "Total Expenses", 448000, "currency"),
              buildOperatingModelMetric("mf_margin", "NOI Margin", 0.61, "percentage"),
              buildOperatingModelMetric("mf_expense_ratio", "Expense Ratio", 0.39, "percentage"),
            ],
          },
        ],
        ["Unit economics and landlord-side operating burden only."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "multifamily_market_rate_apartments_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Unit Economics")).toBeInTheDocument();
    expect(screen.getByText("Operating Burden")).toBeInTheDocument();
    expect(screen.getByText("Average Rent")).toBeInTheDocument();
    expect(screen.queryByText("Units per Manager")).not.toBeInTheDocument();
    expect(screen.queryByText("Maintenance Staff")).not.toBeInTheDocument();
    expect(screen.queryByText("Target KPIs")).not.toBeInTheDocument();
  });

  it("renders data center projects with subtype-native infrastructure cost mix", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("specialty", "data_center", "specialty_data_center_v1"),
      buildOperatingModel(
        "data_center_infrastructure",
        [
          {
            id: "dc_productivity",
            title: "Asset Productivity",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("dc_revenue", "Revenue / SF", 150, "currency", {
                decimals: 2,
                suffix: "/yr",
              }),
              buildOperatingModelMetric("dc_margin", "NOI Margin", 0.45, "percentage"),
            ],
          },
          {
            id: "dc_cost_mix",
            title: "Infrastructure Cost Mix",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("dc_utilities", "Utilities", 712500, "currency"),
              buildOperatingModelMetric("dc_connectivity", "Connectivity", 142500, "currency"),
              buildOperatingModelMetric("dc_expense_ratio", "Expense Ratio", 0.55, "percentage"),
            ],
          },
        ],
        ["Infrastructure-side operating cost mix; tenant compute load is not modeled."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "specialty_data_center_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Asset Productivity")).toBeInTheDocument();
    expect(screen.getByText("Infrastructure Cost Mix")).toBeInTheDocument();
    expect(screen.getByText("Connectivity")).toBeInTheDocument();
    expect(screen.queryByText("Efficiency Score")).not.toBeInTheDocument();
  });

  it("renders mixed-use projects with backend-owned revenue mix semantics", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("mixed_use", "office_residential", "mixed_use_office_residential_v1"),
      buildOperatingModel(
        "mixed_use_revenue_mix",
        [
          {
            id: "mixed_use_revenue_mix",
            title: "Revenue Mix",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("mixed_use_source", "Mix Source", "User Input", "text"),
              buildOperatingModelMetric(
                "mixed_use_composition",
                "Mix Composition",
                "Office 70% / Residential 30%",
                "text"
              ),
              buildOperatingModelMetric("mixed_use_factor", "Revenue Factor Applied", 1.08, "number", {
                decimals: 2,
                suffix: "×",
              }),
            ],
          },
          {
            id: "mixed_use_blended_productivity",
            title: "Blended Productivity & Burden",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("mixed_use_revenue_sf", "Blended Revenue / SF", 42.5, "currency", {
                decimals: 2,
                suffix: "/yr",
                emphasis: "primary",
              }),
              buildOperatingModelMetric("mixed_use_margin", "NOI Margin", 0.61, "percentage"),
              buildOperatingModelMetric("mixed_use_expense_ratio", "Expense Ratio", 0.39, "percentage"),
            ],
          },
        ],
        ["Blended revenue reflects the applied mixed-use share weighting."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "mixed_use_office_residential_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Revenue Mix")).toBeInTheDocument();
    expect(screen.getByText("Blended Productivity & Burden")).toBeInTheDocument();
    expect(screen.getByText("Mix Composition")).toBeInTheDocument();
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
  });

  it("renders retail projects with lease-productivity operating model content", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("retail", "shopping_center", "retail_shopping_center_v1"),
      buildOperatingModel(
        "retail_lease_productivity",
        [
          {
            id: "retail_lease_productivity",
            title: "Lease Productivity",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("retail_rent", "Effective Rent / SF", 32.2, "currency", {
                decimals: 2,
                suffix: "/yr",
                emphasis: "primary",
              }),
              buildOperatingModelMetric("retail_occupancy", "Occupancy Assumption", 0.92, "percentage"),
            ],
          },
          {
            id: "retail_operating_burden",
            title: "Operating Burden",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("retail_expenses", "Total Expenses", 284000, "currency"),
              buildOperatingModelMetric("retail_margin", "NOI Margin", 0.65, "percentage"),
              buildOperatingModelMetric("retail_expense_ratio", "Expense Ratio", 0.35, "percentage"),
            ],
          },
        ],
        ["Landlord-side retail lease productivity and operating burden only; tenant staffing is excluded."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "retail_shopping_center_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Lease Productivity")).toBeInTheDocument();
    expect(screen.getByText("Operating Burden")).toBeInTheDocument();
    expect(screen.getByText("Effective Rent / SF")).toBeInTheDocument();
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
    expect(screen.queryByText("Efficiency Score")).not.toBeInTheDocument();
  });

  it("renders restaurant projects with restaurant-native burden semantics", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("restaurant", "full_service", "restaurant_full_service_v1"),
      buildOperatingModel(
        "restaurant_core_economics",
        [
          {
            id: "restaurant_core_economics",
            title: "Core Economics",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("restaurant_sales_sf", "Sales / SF", 350, "currency", {
                decimals: 0,
                suffix: "/yr",
                emphasis: "primary",
              }),
              buildOperatingModelMetric("restaurant_occupancy", "Occupancy Assumption", 0.8, "percentage"),
              buildOperatingModelMetric("restaurant_margin", "NOI Margin", 0.1, "percentage"),
            ],
          },
          {
            id: "restaurant_operating_burden",
            title: "Operating Burden",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("restaurant_prime_cost", "Prime Cost", 0.65, "percentage"),
              buildOperatingModelMetric("restaurant_labor_burden", "Labor Burden", 0.33, "percentage"),
              buildOperatingModelMetric("restaurant_food_burden", "Food Burden", 0.32, "percentage"),
              buildOperatingModelMetric("restaurant_beverage_burden", "Beverage Burden", 0.15, "percentage"),
              buildOperatingModelMetric("restaurant_expense_ratio", "Expense Ratio", 0.9, "percentage"),
            ],
          },
        ],
        ["Restaurant core economics reflect modeled sales and prime-cost burden assumptions."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "restaurant_full_service_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Core Economics")).toBeInTheDocument();
    expect(screen.getByText("Operating Burden")).toBeInTheDocument();
    expect(screen.getByText("Prime Cost")).toBeInTheDocument();
    expect(screen.queryByText("Efficiency Score")).not.toBeInTheDocument();
    expect(screen.queryByText("Target KPIs")).not.toBeInTheDocument();
  });

  it("renders parking projects with space-economics operating model content", () => {
    const project = withOperatingModel(
      buildCrossTypeProject("parking", "parking_garage", "parking_parking_garage_v1"),
      buildOperatingModel(
        "parking_space_economics",
        [
          {
            id: "parking_space_economics",
            title: "Space Economics",
            layout: "tiles",
            metrics: [
              buildOperatingModelMetric("parking_spaces", "Spaces", 66, "number", {
                emphasis: "primary",
              }),
              buildOperatingModelMetric("parking_revenue_space", "Revenue / Space / Month", 150, "currency", {
                decimals: 0,
                suffix: "/mo",
              }),
              buildOperatingModelMetric("parking_occupancy", "Occupancy Assumption", 0.85, "percentage"),
            ],
          },
          {
            id: "parking_operating_burden",
            title: "Operating Burden",
            layout: "list",
            metrics: [
              buildOperatingModelMetric("parking_margin", "NOI Margin", 0.75, "percentage"),
              buildOperatingModelMetric("parking_expense_ratio", "Expense Ratio", 0.25, "percentage"),
            ],
          },
        ],
        ["Space economics reflect modeled stall productivity and stabilized parking burden."]
      )
    );

    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={project}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "parking_parking_garage_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.getByText("Space Economics")).toBeInTheDocument();
    expect(screen.getByText("Revenue / Space / Month")).toBeInTheDocument();
    expect(screen.getByText("Operating Burden")).toBeInTheDocument();
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
  });

  it("omits the operating model section entirely for still-unsupported families without a backend contract", () => {
    render(
      <MemoryRouter>
        <ExecutiveViewComplete
          project={buildCrossTypeProject("civic", "library", "civic_library_v1")}
          dealShieldData={buildCrossTypeDealShieldViewModel(
            "civic_library_v1",
            "Needs Work",
            "low_flex_before_break_buffer"
          ) as any}
        />
      </MemoryRouter>
    );

    expect(screen.queryByText("Operating Model")).not.toBeInTheDocument();
    expect(screen.queryByText("Operational Efficiency")).not.toBeInTheDocument();
    expect(screen.queryByText("Staffing Metrics")).not.toBeInTheDocument();
  });
});
