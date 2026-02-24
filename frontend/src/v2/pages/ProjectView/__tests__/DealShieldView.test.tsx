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

const HOSPITALITY_PROFILE_IDS = [
  "hospitality_limited_service_hotel_v1",
  "hospitality_full_service_hotel_v1",
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

const buildHospitalityDealShieldPayload = (profileId: string) => ({
  profile_id: profileId,
  view_model: {
    profile_id: profileId,
    tile_profile_id: profileId,
    content_profile_id: profileId,
    scope_items_profile_id:
      profileId === "hospitality_full_service_hotel_v1"
        ? "hospitality_full_service_hotel_structural_v1"
        : "hospitality_limited_service_hotel_structural_v1",
    decision_status: "Needs Work",
    decision_reason_code: "low_flex_before_break_buffer",
    decision_status_provenance: {
      status_source: "dealshield_policy_v1",
      policy_id: "dealshield_canonical_policy_v1",
    },
    decision_table: {
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
        {
          id: "dscr",
          label: "DSCR",
          metric_ref: "ownership_analysis.debt_metrics.calculated_dscr",
        },
      ],
      rows: [
        {
          scenario_id: "base",
          label: "Base",
          cells: [
            { col_id: "total_cost", value: 28000000, metric_ref: "totals.total_project_cost" },
            { col_id: "annual_revenue", value: 6400000, metric_ref: "revenue_analysis.annual_revenue" },
            { col_id: "dscr", value: 1.42, metric_ref: "ownership_analysis.debt_metrics.calculated_dscr" },
          ],
        },
        {
          scenario_id: "conservative",
          label: "Conservative",
          cells: [
            { col_id: "total_cost", value: 30800000, metric_ref: "totals.total_project_cost" },
            { col_id: "annual_revenue", value: 5760000, metric_ref: "revenue_analysis.annual_revenue" },
            { col_id: "dscr", value: 1.21, metric_ref: "ownership_analysis.debt_metrics.calculated_dscr" },
          ],
        },
        {
          scenario_id: "ugly",
          label: "Ugly",
          cells: [
            { col_id: "total_cost", value: 32200000, metric_ref: "totals.total_project_cost" },
            { col_id: "annual_revenue", value: 5600000, metric_ref: "revenue_analysis.annual_revenue" },
            { col_id: "dscr", value: 1.11, metric_ref: "ownership_analysis.debt_metrics.calculated_dscr" },
          ],
        },
      ],
    },
    content: {
      profile_id: profileId,
      fastest_change: {
        drivers: [
          { tile_id: "cost_plus_10", label: "Confirm hard costs +/-10%" },
          { tile_id: "revenue_minus_10", label: "Validate demand revenue +/-10%" },
        ],
      },
      most_likely_wrong: [
        {
          id: "mlw_1",
          text: "Group demand is softer than baseline underwriting assumptions.",
          driver_tile_id: "revenue_minus_10",
        },
      ],
      question_bank: [
        {
          id: "qb_1",
          driver_tile_id: "cost_plus_10",
          questions: ["Which long-lead packages are still allowance-backed?"],
        },
      ],
      red_flags_actions: [
        {
          id: "rf_1",
          flag: "Operator fit-out scope remains partially open.",
          action: "Lock scope bulletin before release for procurement.",
        },
      ],
    },
    primary_control_variable: {
      tile_id: "revenue_minus_10",
      label: "Validate demand revenue +/-10%",
      impact_pct: 7.1,
      delta_cost: -400000,
      severity: "High",
    },
    first_break_condition: {
      scenario_id: "ugly",
      scenario_label: "Ugly",
      break_metric: "value_gap",
      operator: "<=",
      threshold: 0.0,
      observed_value: -320000,
      observed_value_pct: -1.1,
    },
    flex_before_break_pct: 1.8,
    exposure_concentration_pct: 61.5,
    ranked_likely_wrong: [
      {
        id: "mlw_1",
        text: "Group demand is softer than baseline underwriting assumptions.",
        driver_tile_id: "revenue_minus_10",
        impact_pct: 7.1,
        severity: "High",
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
      scope_items_profile_id:
        profileId === "hospitality_full_service_hotel_v1"
          ? "hospitality_full_service_hotel_structural_v1"
          : "hospitality_limited_service_hotel_structural_v1",
      scenario_inputs: {
        base: {
          scenario_label: "Base",
          applied_tile_ids: [],
          stress_band_pct: 10,
          cost_scalar: 1.0,
          revenue_scalar: 1.0,
        },
        conservative: {
          scenario_label: "Conservative",
          applied_tile_ids: ["cost_plus_10", "revenue_minus_10"],
          stress_band_pct: 10,
          cost_scalar: 1.1,
          revenue_scalar: 0.9,
        },
        ugly: {
          scenario_label: "Ugly",
          applied_tile_ids: ["cost_plus_10", "revenue_minus_10"],
          stress_band_pct: 10,
          cost_scalar: 1.15,
          revenue_scalar: 0.88,
        },
      },
      metric_refs_used: [
        "totals.total_project_cost",
        "revenue_analysis.annual_revenue",
        "ownership_analysis.debt_metrics.calculated_dscr",
      ],
      dealshield_controls: {
        stress_band_pct: 10,
        use_cost_anchor: false,
        use_revenue_anchor: false,
      },
      decision_insurance: {
        enabled: true,
        profile_id: profileId,
        primary_control_variable: { status: "available" },
        first_break_condition: { status: "available" },
        flex_before_break_pct: { status: "available" },
        exposure_concentration_pct: { status: "available" },
        ranked_likely_wrong: { status: "available" },
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
    const provenanceMatches = screen.getAllByText((_, element) => {
      if (element?.tagName.toLowerCase() !== "p") return false;
      const text = element.textContent ?? "";
      return text.includes(
        `Tile: ${profileId} | Content: ${profileId} | Scope: restaurant_full_service_structural_v1`
      );
    });
    expect(provenanceMatches.length).toBeGreaterThan(0);
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

  it("renders decision status provenance source when reason code is absent", () => {
    const profileId = "restaurant_cafe_v1";
    const payload = buildRestaurantDealShieldPayload(profileId) as any;
    delete payload.view_model.decision_reason_code;
    payload.view_model.decision_status_provenance = {
      status_source: "restaurant_policy_v1",
    };

    render(
      <DealShieldView
        projectId="proj_restaurant_status_source"
        data={payload}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Decision Status")).toBeInTheDocument();
    expect(screen.getByText("Investment Decision: GO")).toBeInTheDocument();
    expect(screen.getByText("Status source: restaurant_policy_v1.")).toBeInTheDocument();
  });

  it("renders hospitality canonical decision and decision-insurance contract fields for both hotel profiles", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_hospitality_profiles"
        data={buildHospitalityDealShieldPayload(HOSPITALITY_PROFILE_IDS[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const profileId of HOSPITALITY_PROFILE_IDS) {
      rerender(
        <DealShieldView
          projectId={`proj_${profileId}`}
          data={buildHospitalityDealShieldPayload(profileId) as any}
          loading={false}
          error={null}
        />
      );

      expect(screen.getByText("Decision Status")).toBeInTheDocument();
      expect(screen.getByText("Investment Decision: Needs Work")).toBeInTheDocument();
      expect(screen.getByText("Decision Insurance")).toBeInTheDocument();
      expect(screen.getByText("Primary Control Variable")).toBeInTheDocument();
      expect(screen.getByText("First Break Condition")).toBeInTheDocument();
      expect(screen.getByText("Flex Before Break %")).toBeInTheDocument();
      expect(screen.getByText("Exposure Concentration %")).toBeInTheDocument();
      expect(screen.getByText("Decision Metrics")).toBeInTheDocument();
      expect(screen.getAllByText("Conservative").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Ugly").length).toBeGreaterThan(0);
      expect(screen.getByText("$28,000,000")).toBeInTheDocument();
      expect(screen.getByText("$6,400,000")).toBeInTheDocument();
      expect(screen.getAllByText("1.42").length).toBeGreaterThan(0);
      expect(screen.getAllByText(profileId).length).toBeGreaterThan(0);
      expect(
        screen.queryByText("Decision Insurance unavailable for this profile/run.")
      ).not.toBeInTheDocument();
    }
  });

  it("renders backend-shaped hospitality scenario inputs in provenance", () => {
    render(
      <DealShieldView
        projectId="proj_hospitality_scenarios"
        data={buildHospitalityDealShieldPayload("hospitality_full_service_hotel_v1") as any}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Provenance")).toBeInTheDocument();
    expect(screen.getByText("Driver metric (Ugly only)")).toBeInTheDocument();
    expect(screen.getAllByText("Conservative").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Ugly").length).toBeGreaterThan(0);
    expect(screen.getAllByText("cost_plus_10, revenue_minus_10").length).toBeGreaterThan(0);
    expect(screen.getAllByText("±10%").length).toBeGreaterThan(0);
  });
});
