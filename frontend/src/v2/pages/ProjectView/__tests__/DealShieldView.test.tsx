import React from "react";
import { render, screen } from "@testing-library/react";
import { DealShieldView } from "../DealShieldView";

const RESTAURANT_PROFILE_IDS = [
  "restaurant_quick_service_v1",
  "restaurant_full_service_v1",
  "restaurant_fine_dining_v1",
  "restaurant_cafe_v1",
  "restaurant_bar_tavern_v1",
];

const buildRestaurantDealShieldPayload = (profileId: string) => ({
  profile_id: profileId,
  view_model: {
    profile_id: profileId,
    tile_profile_id: profileId,
    content_profile_id: profileId,
    scope_items_profile_id: "restaurant_full_service_structural_v1",
    decision_status: "GO",
    decision_reason_code: "explicit_status_signal",
    decision_status_provenance: {
      status_source: "payload_or_decision_summary",
    },
    columns: [
      {
        id: "total_cost",
        label: "Total Project Cost",
        metric_ref: "totals.total_project_cost",
      },
      {
        id: "annual_revenue",
        label: "Annual Revenue",
        metric_ref: "revenue_analysis.annual_revenue",
      },
    ],
    rows: [
      {
        scenario_id: "base",
        label: "Base",
        cells: [
          {
            col_id: "total_cost",
            value: 3000000,
            metric_ref: "totals.total_project_cost",
          },
          {
            col_id: "annual_revenue",
            value: 1500000,
            metric_ref: "revenue_analysis.annual_revenue",
          },
        ],
      },
      {
        scenario_id: "conservative",
        label: "Conservative",
        cells: [
          {
            col_id: "total_cost",
            value: 3300000,
            metric_ref: "totals.total_project_cost",
          },
          {
            col_id: "annual_revenue",
            value: 1350000,
            metric_ref: "revenue_analysis.annual_revenue",
          },
        ],
      },
    ],
    content: {
      profile_id: profileId,
      fastest_change: {
        drivers: [
          { tile_id: "cost_plus_10", label: "Confirm hard costs +/-10%" },
          { tile_id: "revenue_minus_10", label: "Validate revenue +/-10%" },
        ],
      },
      most_likely_wrong: [
        {
          id: "mlw_1",
          text: "Opening-month throughput assumptions are aggressive.",
          why: "Early utilization variance can move NOI rapidly.",
          driver_tile_id: "revenue_minus_10",
        },
      ],
      question_bank: [
        {
          id: "qb_1",
          driver_tile_id: "cost_plus_10",
          questions: ["Which scopes are still allowance-based?"],
        },
      ],
      red_flags_actions: [
        {
          id: "rf_1",
          flag: "Prototype standards are not fully locked.",
          action: "Obtain final issue-for-construction package before buyout.",
        },
      ],
    },
    primary_control_variable: {
      tile_id: "cost_plus_10",
      label: "Confirm hard costs +/-10%",
      impact_pct: 6.4,
      delta_cost: 192000,
      severity: "Med",
    },
    first_break_condition: {
      scenario_id: "conservative",
      scenario_label: "Conservative",
      break_metric: "value_gap",
      operator: "<=",
      threshold: 0.0,
      observed_value: -25000,
      observed_value_pct: -0.8,
    },
    flex_before_break_pct: 2.1,
    exposure_concentration_pct: 43.2,
    ranked_likely_wrong: [
      {
        id: "mlw_1",
        text: "Opening-month throughput assumptions are aggressive.",
        why: "Early utilization variance can move NOI rapidly.",
        driver_tile_id: "revenue_minus_10",
        impact_pct: 4.2,
        severity: "Med",
      },
    ],
    decision_insurance_provenance: {
      enabled: true,
      profile_id: profileId,
      primary_control_variable: { status: "available" },
      first_break_condition: { status: "available" },
      flex_before_break_pct: { status: "available" },
      exposure_concentration_pct: { status: "available" },
      ranked_likely_wrong: { status: "available" },
    },
    provenance: {
      profile_id: profileId,
      content_profile_id: profileId,
      scope_items_profile_id: "restaurant_full_service_structural_v1",
      scenario_inputs: {
        base: {
          scenario_label: "Base",
          applied_tile_ids: [],
          cost_scalar: 1.0,
          revenue_scalar: 1.0,
        },
        conservative: {
          scenario_label: "Conservative",
          applied_tile_ids: ["cost_plus_10", "revenue_minus_10"],
          cost_scalar: 1.1,
          revenue_scalar: 0.9,
        },
      },
      metric_refs_used: ["totals.total_project_cost", "revenue_analysis.annual_revenue"],
      decision_insurance: {
        enabled: true,
        profile_id: profileId,
        primary_control_variable: { status: "available" },
        first_break_condition: { status: "available" },
        flex_before_break_pct: { status: "available" },
        exposure_concentration_pct: { status: "available" },
        ranked_likely_wrong: { status: "available" },
      },
      dealshield_controls: {
        stress_band_pct: 10,
        use_cost_anchor: true,
        anchor_total_project_cost: 3000000,
      },
    },
  },
});

describe("DealShieldView", () => {
  it("renders restaurant decision status, DI provenance, and backend-shaped scenario rows", () => {
    const profileId = "restaurant_full_service_v1";
    render(
      <DealShieldView
        projectId="proj_restaurant_full_service"
        data={buildRestaurantDealShieldPayload(profileId) as any}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("DealShield")).toBeInTheDocument();
    expect(screen.getByText("Decision Status")).toBeInTheDocument();
    expect(screen.getByText("Investment Decision: GO")).toBeInTheDocument();
    expect(screen.getByText("Decision Insurance")).toBeInTheDocument();
    expect(screen.getByText("Primary Control Variable")).toBeInTheDocument();
    expect(screen.getByText("Decision Metrics")).toBeInTheDocument();
    expect(screen.getAllByText("Conservative").length).toBeGreaterThan(0);
    expect(screen.getByText("$3,000,000")).toBeInTheDocument();
    expect(screen.getByText("$1,500,000")).toBeInTheDocument();
    expect(
      screen.getByText((_, element) => {
        const text = element?.textContent ?? "";
        return text.includes(
          `Tile: ${profileId} | Content: ${profileId} | Scope: restaurant_full_service_structural_v1`
        );
      })
    ).toBeInTheDocument();
    expect(screen.queryByText("Decision Insurance unavailable for this profile/run.")).not.toBeInTheDocument();
  });

  it("supports all five restaurant DealShield profile IDs without quick-service-only assumptions", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_restaurant_all"
        data={buildRestaurantDealShieldPayload(RESTAURANT_PROFILE_IDS[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const profileId of RESTAURANT_PROFILE_IDS) {
      rerender(
        <DealShieldView
          projectId={`proj_${profileId}`}
          data={buildRestaurantDealShieldPayload(profileId) as any}
          loading={false}
          error={null}
        />
      );
      expect(screen.getAllByText(profileId).length).toBeGreaterThan(0);
      expect(screen.getByText("Decision Insurance")).toBeInTheDocument();
      expect(screen.getAllByText("Conservative").length).toBeGreaterThan(0);
    }
  });
});
