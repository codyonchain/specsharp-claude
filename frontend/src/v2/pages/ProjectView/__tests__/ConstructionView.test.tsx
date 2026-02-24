import React from "react";
import { render, screen } from "@testing-library/react";
import { ConstructionView } from "../ConstructionView";

const buildRestaurantProject = (scheduleSource: "subtype" | "building_type") =>
  ({
    id: "proj_restaurant_construction",
    project_id: "proj_restaurant_construction",
    name: "Restaurant Construction",
    description: "Restaurant schedule parity fixture",
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
        floors: 1,
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
        totals: {
          hard_costs: 3200000,
          soft_costs: 500000,
          total_project_cost: 3700000,
          cost_per_sf: 462.5,
        },
        trade_breakdown: {
          structural: 700000,
          mechanical: 950000,
          electrical: 520000,
          plumbing: 410000,
          finishes: 620000,
        },
        ownership_analysis: {
          debt_metrics: {
            calculated_dscr: 1.46,
          },
          return_metrics: {
            estimated_annual_noi: 430000,
          },
          yield_on_cost: 0.116,
        },
        return_metrics: {
          payback_period: 7.8,
        },
        construction_schedule: {
          building_type: "restaurant",
          subtype: scheduleSource === "subtype" ? "full_service" : null,
          schedule_source: scheduleSource,
          total_months: scheduleSource === "subtype" ? 15 : 14,
          phases: [
            { id: "site_foundation", label: "Site Foundation", start_month: 0, duration_months: 3, end_month: 3 },
            { id: "structural", label: "Structure", start_month: 2, duration_months: 5, end_month: 7 },
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
              base: { scenario_label: "Base", applied_tile_ids: [] },
            },
          },
        },
        calculation_trace: [],
        scope_items: [],
      },
    },
  }) as any;

describe("ConstructionView", () => {
  it("renders subtype schedule messaging for restaurant subtype schedules", () => {
    render(<ConstructionView project={buildRestaurantProject("subtype")} />);

    expect(screen.getByText("Construction Schedule")).toBeInTheDocument();
    expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
    expect(
      screen.getByText("Timeline is tailored for this subtype profile.")
    ).toBeInTheDocument();
  });

  it("renders building-type baseline messaging on restaurant subtype fallback", () => {
    render(<ConstructionView project={buildRestaurantProject("building_type")} />);

    expect(screen.getByText("Construction Schedule")).toBeInTheDocument();
    expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
    expect(
      screen.getByText("Timeline uses building-type baseline (subtype override unavailable).")
    ).toBeInTheDocument();
  });
});
