import React from "react";
import { render, screen } from "@testing-library/react";
import { ConstructionView } from "../ConstructionView";

const HOSPITALITY_PROFILE_IDS = [
  "hospitality_limited_service_hotel_v1",
  "hospitality_full_service_hotel_v1",
];

const CROSS_TYPE_SCHEDULE_CASES = [
  { buildingType: "restaurant", subtype: "bar_tavern" },
  { buildingType: "hospitality", subtype: "full_service_hotel" },
  { buildingType: "multifamily", subtype: "luxury_apartments" },
  { buildingType: "industrial", subtype: "distribution_center" },
] as const;

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

const buildHospitalityProject = (
  profileId: string,
  scheduleSource: "subtype" | "building_type" = "subtype"
) =>
  ({
    id: "proj_hospitality_construction",
    project_id: "proj_hospitality_construction",
    name: "Hospitality Construction",
    description: "Hospitality schedule contract fixture",
    created_at: "2026-02-24T00:00:00Z",
    updated_at: "2026-02-24T00:00:00Z",
    user_id: "test-user",
    is_shared: false,
    analysis: {
      parsed_input: {
        building_type: "hospitality",
        subtype:
          scheduleSource === "subtype"
            ? profileId === "hospitality_full_service_hotel_v1"
              ? "full_service_hotel"
              : "limited_service_hotel"
            : "unknown_hotel_variant",
        square_footage: 85000,
        location: "Nashville, TN",
        project_classification: "ground_up",
        floors: 8,
      },
      calculations: {
        project_info: {
          building_type: "hospitality",
          subtype:
            scheduleSource === "subtype"
              ? profileId === "hospitality_full_service_hotel_v1"
                ? "full_service_hotel"
                : "limited_service_hotel"
              : "unknown_hotel_variant",
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
        soft_costs: {
          total: 4200000,
          breakdown: {},
        },
        totals: {
          hard_costs: 31700000,
          soft_costs: 4200000,
          total_project_cost: 35900000,
          cost_per_sf: 422.35,
        },
        trade_breakdown: {
          structural: 7600000,
          mechanical: 8200000,
          electrical: 4700000,
          plumbing: 4100000,
          finishes: 7100000,
        },
        ownership_analysis: {
          debt_metrics: {
            calculated_dscr: 1.42,
          },
          return_metrics: {
            estimated_annual_noi: 2980000,
          },
          yield_on_cost: 0.083,
        },
        return_metrics: {
          payback_period: 10.6,
        },
        construction_schedule: {
          building_type: "hospitality",
          subtype:
            scheduleSource === "subtype"
              ? profileId === "hospitality_full_service_hotel_v1"
                ? "full_service_hotel"
                : "limited_service_hotel"
              : null,
          schedule_source: scheduleSource,
          total_months:
            scheduleSource === "subtype"
              ? profileId === "hospitality_full_service_hotel_v1"
                ? 32
                : 24
              : 30,
          phases:
            scheduleSource === "subtype"
              ? profileId === "hospitality_full_service_hotel_v1"
                ? [
                    { id: "site_foundation", label: "Site, Podium & Foundations", start_month: 0, duration_months: 6, end_month: 6 },
                    { id: "structural", label: "Structure, Core & Towers", start_month: 4, duration_months: 14, end_month: 18 },
                  ]
                : [
                    { id: "site_foundation", label: "Site Utilities & Foundations", start_month: 0, duration_months: 4, end_month: 4 },
                    { id: "structural", label: "Podium & Guestroom Structure", start_month: 2, duration_months: 10, end_month: 12 },
                  ]
              : [
                  { id: "site_foundation", label: "Site & Podium Work", start_month: 0, duration_months: 6, end_month: 6 },
                  { id: "structural", label: "Structure & Garage", start_month: 4, duration_months: 14, end_month: 18 },
                ],
        },
        dealshield_scenarios: {
          profile_id: profileId,
          scenarios: {
            base: {
              totals: { total_project_cost: 35900000, cost_per_sf: 422.35 },
              revenue_analysis: { annual_revenue: 9020000 },
              ownership_analysis: {
                yield_on_cost: 0.083,
                debt_metrics: { calculated_dscr: 1.42 },
              },
              return_metrics: { payback_period: 10.6 },
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

const buildCrossTypeScheduleProject = (
  buildingType: string,
  subtype: string,
  scheduleSource: "subtype" | "building_type"
) =>
  ({
    id: `proj_${buildingType}_${subtype}_${scheduleSource}`,
    project_id: `proj_${buildingType}_${subtype}_${scheduleSource}`,
    name: `${buildingType} ${subtype}`,
    description: "Cross-type schedule provenance fixture",
    created_at: "2026-02-24T00:00:00Z",
    updated_at: "2026-02-24T00:00:00Z",
    user_id: "test-user",
    is_shared: false,
    analysis: {
      parsed_input: {
        building_type: buildingType,
        subtype,
        square_footage: 50000,
        location: "Nashville, TN",
        project_classification: "ground_up",
        floors: 5,
      },
      calculations: {
        project_info: {
          building_type: buildingType,
          subtype,
          display_name: `${buildingType} ${subtype}`,
          project_class: "ground_up",
          square_footage: 50000,
          location: "Nashville, TN",
          floors: 5,
          typical_floors: 5,
        },
        construction_costs: {
          base_cost_per_sf: 300,
          class_multiplier: 1,
          regional_multiplier: 1.03,
          final_cost_per_sf: 309,
          construction_total: 15000000,
          equipment_total: 800000,
          special_features_total: 0,
          cost_build_up: [],
        },
        soft_costs: {
          total: 2000000,
          breakdown: {},
        },
        totals: {
          hard_costs: 15800000,
          soft_costs: 2000000,
          total_project_cost: 17800000,
          cost_per_sf: 356,
        },
        trade_breakdown: {
          structural: 3800000,
          mechanical: 3600000,
          electrical: 3100000,
          plumbing: 2200000,
          finishes: 3100000,
        },
        ownership_analysis: {
          debt_metrics: {
            calculated_dscr: 1.35,
          },
          return_metrics: {
            estimated_annual_noi: 1450000,
          },
          yield_on_cost: 0.081,
        },
        return_metrics: {
          payback_period: 9.4,
        },
        construction_schedule: {
          building_type: buildingType,
          subtype: scheduleSource === "subtype" ? subtype : null,
          schedule_source: scheduleSource,
          total_months: scheduleSource === "subtype" ? 20 : 22,
          phases:
            scheduleSource === "subtype"
              ? [
                  {
                    id: "site_foundation",
                    label: "Subtype Site Program",
                    start_month: 0,
                    duration_months: 4,
                    end_month: 4,
                  },
                  {
                    id: "structural",
                    label: "Subtype Structural Program",
                    start_month: 3,
                    duration_months: 9,
                    end_month: 12,
                  },
                ]
              : [
                  {
                    id: "site_foundation",
                    label: "Baseline Site Program",
                    start_month: 0,
                    duration_months: 5,
                    end_month: 5,
                  },
                  {
                    id: "structural",
                    label: "Baseline Structural Program",
                    start_month: 4,
                    duration_months: 10,
                    end_month: 14,
                  },
                ],
        },
        dealshield_scenarios: {
          profile_id: `${buildingType}_${subtype}_v1`,
          scenarios: {
            base: {
              totals: { total_project_cost: 17800000, cost_per_sf: 356 },
              revenue_analysis: { annual_revenue: 5200000 },
              ownership_analysis: {
                yield_on_cost: 0.081,
                debt_metrics: { calculated_dscr: 1.35 },
              },
              return_metrics: { payback_period: 9.4 },
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

  it("renders hospitality subtype schedule contract for both hotel profiles", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildHospitalityProject(HOSPITALITY_PROFILE_IDS[0], "subtype")}
      />
    );

    for (const profileId of HOSPITALITY_PROFILE_IDS) {
      rerender(
        <ConstructionView
          project={buildHospitalityProject(profileId, "subtype")}
        />
      );
      expect(screen.getByText("Construction Schedule")).toBeInTheDocument();
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
    }
  });

  it("renders hospitality fallback payload contract with building-type baseline schedule source", () => {
    render(
      <ConstructionView
        project={buildHospitalityProject(
          "hospitality_full_service_hotel_v1",
          "building_type"
        )}
      />
    );

    expect(screen.getByText("Construction Schedule")).toBeInTheDocument();
    expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
    expect(
      screen.getByText("Timeline uses building-type baseline (subtype override unavailable).")
    ).toBeInTheDocument();
    expect(screen.getAllByText("Site & Podium Work").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Structure & Garage").length).toBeGreaterThan(0);
  });

  it("keeps schedule provenance messaging parity across restaurant, hospitality, multifamily, and industrial", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildCrossTypeScheduleProject(
          CROSS_TYPE_SCHEDULE_CASES[0].buildingType,
          CROSS_TYPE_SCHEDULE_CASES[0].subtype,
          "subtype"
        )}
      />
    );

    for (const testCase of CROSS_TYPE_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildCrossTypeScheduleProject(
            testCase.buildingType,
            testCase.subtype,
            "subtype"
          )}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();

      rerender(
        <ConstructionView
          project={buildCrossTypeScheduleProject(
            testCase.buildingType,
            testCase.subtype,
            "building_type"
          )}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
    }
  });
});
