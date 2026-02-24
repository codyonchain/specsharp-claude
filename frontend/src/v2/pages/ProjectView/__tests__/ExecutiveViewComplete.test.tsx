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
  profileId: string
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
  return project;
};

const buildCrossTypeDealShieldViewModel = (
  profileId: string,
  decisionStatus: string,
  decisionReasonCode: string
) => ({
  decision_status: decisionStatus,
  decision_reason_code: decisionReasonCode,
  decision_status_provenance: {
    status_source: "dealshield_policy_v1",
    policy_id: "decision_insurance_subtype_policy_v1",
  },
  decision_insurance_provenance: {
    enabled: true,
    profile_id: profileId,
  },
  tile_profile_id: profileId,
  content_profile_id: profileId,
  scope_items_profile_id: `${profileId.replace(/_v1$/, "")}_structural_v1`,
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
});
