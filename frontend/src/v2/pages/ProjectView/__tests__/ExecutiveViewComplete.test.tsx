import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ExecutiveViewComplete } from "../ExecutiveViewComplete";

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
});
