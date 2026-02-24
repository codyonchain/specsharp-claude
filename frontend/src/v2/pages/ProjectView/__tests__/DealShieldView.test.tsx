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

const SPECIALTY_POLICY_CONTRACT_CASES = [
  {
    subtype: "data_center",
    profileId: "specialty_data_center_v1",
    scopeProfileId: "specialty_data_center_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Utility + Backup Power Train +15%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 18.0,
    observedValue: 16.4,
    flexBeforeBreakPct: 1.6,
    expectedFlexLabel: "1.60% (Structurally Tight)",
    baseDscr: 1.42,
    stressedDscr: 1.18,
  },
  {
    subtype: "laboratory",
    profileId: "specialty_laboratory_v1",
    scopeProfileId: "specialty_laboratory_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "MEP Validation and Containment Fit-Out +12%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 0.0,
    observedValue: -125000,
    flexBeforeBreakPct: 1.9,
    expectedFlexLabel: "1.90% (Structurally Tight)",
    baseDscr: 1.35,
    stressedDscr: 1.06,
  },
  {
    subtype: "self_storage",
    profileId: "specialty_self_storage_v1",
    scopeProfileId: "specialty_self_storage_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Lease-Up Velocity and Security Stack +10%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 8.0,
    observedValue: 10.8,
    flexBeforeBreakPct: 5.4,
    expectedFlexLabel: "5.40% (Flexible)",
    baseDscr: 1.58,
    stressedDscr: 1.33,
  },
  {
    subtype: "car_dealership",
    profileId: "specialty_car_dealership_v1",
    scopeProfileId: "specialty_car_dealership_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Showroom Envelope + Service Bay Equipment +11%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 22.0,
    observedValue: 20.5,
    flexBeforeBreakPct: 1.8,
    expectedFlexLabel: "1.80% (Structurally Tight)",
    baseDscr: 1.41,
    stressedDscr: 1.14,
  },
  {
    subtype: "broadcast_facility",
    profileId: "specialty_broadcast_facility_v1",
    scopeProfileId: "specialty_broadcast_facility_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "Acoustics Isolation + Studio Systems +9%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 50000.0,
    observedValue: 42000,
    flexBeforeBreakPct: 3.1,
    expectedFlexLabel: "3.10% (Moderate)",
    baseDscr: 1.31,
    stressedDscr: 1.09,
  },
] as const;

const DECISION_REASON_TEXT: Record<string, string> = {
  low_flex_before_break_buffer: "Status reflects low flex-before-break buffer.",
  tight_flex_band: "Status reflects a tight flex-before-break band.",
  base_value_gap_positive: "Base value gap is positive under current assumptions.",
};

const HEALTHCARE_POLICY_CONTRACT_CASES = [
  {
    subtype: "surgical_center",
    profileId: "healthcare_surgical_center_v1",
    scopeProfileId: "healthcare_surgical_center_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "OR Sterile Core + Infection Control +11%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 9.0,
    observedValue: 7.8,
    flexBeforeBreakPct: 1.7,
    expectedFlexLabel: "1.70% (Structurally Tight)",
    baseDscr: 1.34,
    stressedDscr: 1.12,
  },
  {
    subtype: "imaging_center",
    profileId: "healthcare_imaging_center_v1",
    scopeProfileId: "healthcare_imaging_center_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "Shielding + Magnet Quench Infrastructure +10%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 0.0,
    observedValue: -185000,
    flexBeforeBreakPct: 1.9,
    expectedFlexLabel: "1.90% (Structurally Tight)",
    baseDscr: 1.29,
    stressedDscr: 1.03,
  },
  {
    subtype: "urgent_care",
    profileId: "healthcare_urgent_care_v1",
    scopeProfileId: "healthcare_urgent_care_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Rapid Turn Rooms + Front-End Throughput +8%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 5.5,
    observedValue: 8.6,
    flexBeforeBreakPct: 5.4,
    expectedFlexLabel: "5.40% (Flexible)",
    baseDscr: 1.52,
    stressedDscr: 1.31,
  },
  {
    subtype: "outpatient_clinic",
    profileId: "healthcare_outpatient_clinic_v1",
    scopeProfileId: "healthcare_outpatient_clinic_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Clinic Pods + MEP Coordination +9%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 7.0,
    observedValue: 6.2,
    flexBeforeBreakPct: 1.8,
    expectedFlexLabel: "1.80% (Structurally Tight)",
    baseDscr: 1.36,
    stressedDscr: 1.13,
  },
  {
    subtype: "medical_office_building",
    profileId: "healthcare_medical_office_building_v1",
    scopeProfileId: "healthcare_medical_office_building_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Tenant Improvement Velocity +8%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 25000.0,
    observedValue: 91000,
    flexBeforeBreakPct: 4.6,
    expectedFlexLabel: "4.60% (Moderate)",
    baseDscr: 1.47,
    stressedDscr: 1.24,
  },
  {
    subtype: "dental_office",
    profileId: "healthcare_dental_office_v1",
    scopeProfileId: "healthcare_dental_office_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "Plumbing Med-Gas Coordination +9%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 0.0,
    observedValue: -42000,
    flexBeforeBreakPct: 1.6,
    expectedFlexLabel: "1.60% (Structurally Tight)",
    baseDscr: 1.33,
    stressedDscr: 1.07,
  },
  {
    subtype: "hospital",
    profileId: "healthcare_hospital_v1",
    scopeProfileId: "healthcare_hospital_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Critical Care MEP + Vertical Transport +12%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 12.0,
    observedValue: 10.5,
    flexBeforeBreakPct: 1.5,
    expectedFlexLabel: "1.50% (Structurally Tight)",
    baseDscr: 1.31,
    stressedDscr: 1.08,
  },
  {
    subtype: "medical_center",
    profileId: "healthcare_medical_center_v1",
    scopeProfileId: "healthcare_medical_center_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Diagnostic + Procedure Core +10%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 8.5,
    observedValue: 7.1,
    flexBeforeBreakPct: 1.9,
    expectedFlexLabel: "1.90% (Structurally Tight)",
    baseDscr: 1.35,
    stressedDscr: 1.11,
  },
  {
    subtype: "nursing_home",
    profileId: "healthcare_nursing_home_v1",
    scopeProfileId: "healthcare_nursing_home_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Resident Care Pods + Nurse Call Stack +7%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 0.0,
    observedValue: 125000,
    flexBeforeBreakPct: 5.1,
    expectedFlexLabel: "5.10% (Flexible)",
    baseDscr: 1.49,
    stressedDscr: 1.27,
  },
  {
    subtype: "rehabilitation",
    profileId: "healthcare_rehabilitation_v1",
    scopeProfileId: "healthcare_rehabilitation_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "Therapy Gym + Hydro Systems +9%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 50000.0,
    observedValue: 28000,
    flexBeforeBreakPct: 3.2,
    expectedFlexLabel: "3.20% (Moderate)",
    baseDscr: 1.32,
    stressedDscr: 1.1,
  },
] as const;

const OFFICE_POLICY_CONTRACT_CASES = [
  {
    subtype: "class_a",
    profileId: "office_class_a_v1",
    scopeProfileId: "office_class_a_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "IC + Lease Velocity + Tenant-Improvement Discipline +11%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 7.0,
    observedValue: 6.1,
    flexBeforeBreakPct: 1.8,
    expectedFlexLabel: "1.80% (Structurally Tight)",
    baseDscr: 1.38,
    stressedDscr: 1.14,
  },
  {
    subtype: "class_b",
    profileId: "office_class_b_v1",
    scopeProfileId: "office_class_b_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "IC + Renewal Risk + Operating Cost Capture +8%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 0.0,
    observedValue: -42000,
    flexBeforeBreakPct: 5.2,
    expectedFlexLabel: "5.20% (Flexible)",
    baseDscr: 1.44,
    stressedDscr: 1.2,
  },
] as const;

const POLICY_CONTRACT_CASES = [
  {
    buildingType: "restaurant",
    profileId: "restaurant_bar_tavern_v1",
    scopeProfileId: "restaurant_bar_tavern_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Entertainment + Life-Safety +10%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 35.0,
    observedValue: 34.2,
    flexBeforeBreakPct: 1.8,
    expectedFlexLabel: "1.80% (Structurally Tight)",
  },
  {
    buildingType: "hospitality",
    profileId: "hospitality_full_service_hotel_v1",
    scopeProfileId: "hospitality_full_service_hotel_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Ballroom and F&B Fit-Out +12%",
    breakScenarioLabel: "Ugly",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 50.0,
    observedValue: 49.3,
    flexBeforeBreakPct: 3.2,
    expectedFlexLabel: "3.20% (Moderate)",
  },
  {
    buildingType: "multifamily",
    profileId: "multifamily_luxury_apartments_v1",
    scopeProfileId: "multifamily_luxury_apartments_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Amenity Finishes +15%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 250000.0,
    observedValue: 200000,
    flexBeforeBreakPct: 4.2,
    expectedFlexLabel: "4.20% (Moderate)",
  },
  {
    buildingType: "industrial",
    profileId: "industrial_distribution_center_v1",
    scopeProfileId: "industrial_distribution_center_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "tight_flex_band",
    primaryControlLabel: "Electrical +10%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: -25.0,
    observedValue: -45.9,
    flexBeforeBreakPct: 1.9,
    expectedFlexLabel: "1.90% (Structurally Tight)",
  },
] as const;

const MULTIFAMILY_POLICY_CONTRACT_CASES: Array<(typeof POLICY_CONTRACT_CASES)[number]> = [
  {
    buildingType: "multifamily",
    profileId: "multifamily_market_rate_apartments_v1",
    scopeProfileId: "multifamily_market_rate_apartments_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Structural Base Carry Proxy +5%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 6.0,
    observedValue: 5.4,
    flexBeforeBreakPct: 1.9,
    expectedFlexLabel: "1.90% (Structurally Tight)",
  },
  {
    buildingType: "multifamily",
    profileId: "multifamily_luxury_apartments_v1",
    scopeProfileId: "multifamily_luxury_apartments_structural_v1",
    decisionStatus: "GO",
    decisionReasonCode: "base_value_gap_positive",
    primaryControlLabel: "Amenity Finishes +15%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap",
    breakMetricRef: "decision_summary.value_gap",
    breakOperator: "<=",
    threshold: 250000.0,
    observedValue: 200000,
    flexBeforeBreakPct: 4.2,
    expectedFlexLabel: "4.20% (Moderate)",
  },
  {
    buildingType: "multifamily",
    profileId: "multifamily_affordable_housing_v1",
    scopeProfileId: "multifamily_affordable_housing_structural_v1",
    decisionStatus: "Needs Work",
    decisionReasonCode: "low_flex_before_break_buffer",
    primaryControlLabel: "Compliance Electrical +8%",
    breakScenarioLabel: "Conservative",
    breakMetric: "value_gap_pct",
    breakMetricRef: "decision_summary.value_gap_pct",
    breakOperator: "<=",
    threshold: 8.0,
    observedValue: 7.2,
    flexBeforeBreakPct: 2.1,
    expectedFlexLabel: "2.10% (Moderate)",
  },
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

const buildPolicyBackedDealShieldPayload = (
  input: (typeof POLICY_CONTRACT_CASES)[number]
) => ({
  profile_id: input.profileId,
  view_model: {
    profile_id: input.profileId,
    tile_profile_id: input.profileId,
    content_profile_id: input.profileId,
    scope_items_profile_id: input.scopeProfileId,
    decision_status: input.decisionStatus,
    decision_reason_code: input.decisionReasonCode,
    decision_status_provenance: {
      status_source: "dealshield_policy_v1",
      policy_id: "dealshield_canonical_policy_v1",
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
      {
        id: "break_metric",
        label: "Break Metric",
        metric_ref: input.breakMetricRef,
      },
    ],
    rows: [
      {
        scenario_id: "base",
        label: "Base",
        cells: [
          { col_id: "total_cost", value: 12000000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 3200000, metric_ref: "revenue_analysis.annual_revenue" },
          { col_id: "break_metric", value: 62.0, metric_ref: input.breakMetricRef },
        ],
      },
      {
        scenario_id: "conservative",
        label: "Conservative",
        cells: [
          { col_id: "total_cost", value: 13200000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 2880000, metric_ref: "revenue_analysis.annual_revenue" },
          { col_id: "break_metric", value: input.observedValue, metric_ref: input.breakMetricRef },
        ],
      },
      {
        scenario_id: "ugly",
        label: "Ugly",
        cells: [
          { col_id: "total_cost", value: 13800000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 2760000, metric_ref: "revenue_analysis.annual_revenue" },
          {
            col_id: "break_metric",
            value: input.breakMetric === "value_gap_pct" ? input.observedValue - 1.5 : input.observedValue - 50000,
            metric_ref: input.breakMetricRef,
          },
        ],
      },
    ],
    content: {
      profile_id: input.profileId,
      fastest_change: {
        drivers: [
          { tile_id: "cost_plus_10", label: "Confirm hard costs +/-10%" },
          { tile_id: "revenue_minus_10", label: "Validate demand revenue +/-10%" },
        ],
      },
      most_likely_wrong: [
        {
          id: "mlw_1",
          text: `${input.buildingType} downside concentration is under-modeled.`,
          why: "Single-driver sensitivity dominates downside exposure.",
          driver_tile_id: "cost_plus_10",
        },
      ],
      question_bank: [
        {
          id: "qb_1",
          driver_tile_id: "cost_plus_10",
          questions: ["Which key assumptions still rely on placeholders?"],
        },
      ],
      red_flags_actions: [
        {
          id: "rf_1",
          flag: "Procurement sequencing remains partially open.",
          action: "Lock top three risk trades before GMP validation.",
        },
      ],
    },
    primary_control_variable: {
      tile_id: "policy_primary_tile",
      label: input.primaryControlLabel,
      impact_pct: 7.5,
      delta_cost: 120000,
      severity: "High",
    },
    first_break_condition: {
      scenario_id: input.breakScenarioLabel.toLowerCase(),
      scenario_label: input.breakScenarioLabel,
      break_metric: input.breakMetric,
      operator: input.breakOperator,
      threshold: input.threshold,
      observed_value: input.observedValue,
      observed_value_pct: input.breakMetric === "value_gap_pct" ? input.observedValue : -1.4,
    },
    flex_before_break_pct: input.flexBeforeBreakPct,
    exposure_concentration_pct: 58.4,
    ranked_likely_wrong: [
      {
        id: "mlw_1",
        text: `${input.buildingType} downside concentration is under-modeled.`,
        why: "Single-driver sensitivity dominates downside exposure.",
        driver_tile_id: "cost_plus_10",
        impact_pct: 7.5,
        severity: "High",
      },
    ],
    decision_insurance_provenance: {
      enabled: true,
      profile_id: input.profileId,
      decision_insurance_policy: {
        status: "available",
        source: "decision_insurance_policy",
        policy_id: "decision_insurance_subtype_policy_v1",
        profile_id: input.profileId,
      },
      primary_control_variable: {
        status: "available",
        source: "decision_insurance_policy.primary_control_variable",
      },
      first_break_condition: {
        status: "available",
        source: "decision_insurance_policy.collapse_trigger",
        policy_metric: input.breakMetric,
        policy_threshold: input.threshold,
        policy_operator: input.breakOperator,
      },
      flex_before_break_pct: {
        status: "available",
        calibration_source: "decision_insurance_policy.flex_calibration",
        band:
          input.flexBeforeBreakPct <= 2.0
            ? "tight"
            : input.flexBeforeBreakPct <= 5.0
              ? "moderate"
              : "comfortable",
      },
      exposure_concentration_pct: { status: "available" },
      ranked_likely_wrong: { status: "available" },
    },
    provenance: {
      profile_id: input.profileId,
      content_profile_id: input.profileId,
      scope_items_profile_id: input.scopeProfileId,
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
        ugly: {
          scenario_label: "Ugly",
          applied_tile_ids: ["cost_plus_10", "revenue_minus_10"],
          cost_scalar: 1.15,
          revenue_scalar: 0.88,
        },
      },
      metric_refs_used: [
        "totals.total_project_cost",
        "revenue_analysis.annual_revenue",
        input.breakMetricRef,
      ],
      decision_insurance: {
        enabled: true,
        profile_id: input.profileId,
        decision_insurance_policy: {
          status: "available",
          source: "decision_insurance_policy",
          policy_id: "decision_insurance_subtype_policy_v1",
          profile_id: input.profileId,
        },
        primary_control_variable: { status: "available" },
        first_break_condition: { status: "available" },
        flex_before_break_pct: { status: "available" },
        exposure_concentration_pct: { status: "available" },
        ranked_likely_wrong: { status: "available" },
      },
      dealshield_controls: {
        stress_band_pct: 10,
        use_cost_anchor: false,
        use_revenue_anchor: false,
      },
    },
  },
});

const buildFlexExposurePolicyPayload = (
  flexBeforeBreakPct: number,
  exposureConcentrationPct: number
) => {
  const payload = buildPolicyBackedDealShieldPayload(POLICY_CONTRACT_CASES[0]) as any;
  payload.view_model.flex_before_break_pct = flexBeforeBreakPct;
  payload.view_model.exposure_concentration_pct = exposureConcentrationPct;
  payload.view_model.decision_insurance_provenance.flex_before_break_pct.band =
    flexBeforeBreakPct < 2
      ? "tight"
      : flexBeforeBreakPct < 5
        ? "moderate"
        : "comfortable";
  return payload;
};

type SubtypePolicyContractCase = {
  subtype: string;
  profileId: string;
  scopeProfileId: string;
  decisionStatus: string;
  decisionReasonCode: string;
  primaryControlLabel: string;
  breakScenarioLabel: string;
  breakMetric: string;
  breakMetricRef: string;
  breakOperator: string;
  threshold: number;
  observedValue: number;
  flexBeforeBreakPct: number;
  expectedFlexLabel: string;
  baseDscr: number;
  stressedDscr: number;
};

const buildSubtypePolicyPayload = (
  input: SubtypePolicyContractCase
) => ({
  profile_id: input.profileId,
  view_model: {
    profile_id: input.profileId,
    tile_profile_id: input.profileId,
    content_profile_id: input.profileId,
    scope_items_profile_id: input.scopeProfileId,
    decision_status: input.decisionStatus,
    decision_reason_code: input.decisionReasonCode,
    decision_status_provenance: {
      status_source: "dealshield_policy_v1",
      policy_id: "decision_insurance_subtype_policy_v1",
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
      {
        id: "dscr",
        label: "DSCR",
        metric_ref: "ownership_analysis.debt_metrics.calculated_dscr",
      },
      {
        id: "break_metric",
        label: "Break Metric",
        metric_ref: input.breakMetricRef,
      },
    ],
    rows: [
      {
        scenario_id: "base",
        label: "Base",
        cells: [
          { col_id: "total_cost", value: 24000000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 6200000, metric_ref: "revenue_analysis.annual_revenue" },
          { col_id: "dscr", value: input.baseDscr, metric_ref: "ownership_analysis.debt_metrics.calculated_dscr" },
          {
            col_id: "break_metric",
            value: input.breakMetric === "value_gap_pct" ? input.observedValue + 8.0 : input.observedValue + 200000,
            metric_ref: input.breakMetricRef,
          },
        ],
      },
      {
        scenario_id: "conservative",
        label: "Conservative",
        cells: [
          { col_id: "total_cost", value: 26400000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 5600000, metric_ref: "revenue_analysis.annual_revenue" },
          { col_id: "dscr", value: input.stressedDscr, metric_ref: "ownership_analysis.debt_metrics.calculated_dscr" },
          { col_id: "break_metric", value: input.observedValue, metric_ref: input.breakMetricRef },
        ],
      },
      {
        scenario_id: "ugly",
        label: "Ugly",
        cells: [
          { col_id: "total_cost", value: 27600000, metric_ref: "totals.total_project_cost" },
          { col_id: "annual_revenue", value: 5340000, metric_ref: "revenue_analysis.annual_revenue" },
          {
            col_id: "dscr",
            value: Math.max(0.85, Number((input.stressedDscr - 0.12).toFixed(2))),
            metric_ref: "ownership_analysis.debt_metrics.calculated_dscr",
          },
          {
            col_id: "break_metric",
            value: input.breakMetric === "value_gap_pct" ? input.observedValue - 3.0 : input.observedValue - 110000,
            metric_ref: input.breakMetricRef,
          },
        ],
      },
    ],
    content: {
      profile_id: input.profileId,
      fastest_change: {
        drivers: [
          { tile_id: "cost_plus_10", label: "Confirm hard costs +/-10%" },
          { tile_id: "revenue_minus_10", label: "Validate demand revenue +/-10%" },
        ],
      },
      most_likely_wrong: [
        {
          id: "mlw_1",
          text: `${input.subtype} downside concentration is under-modeled.`,
          why: "Single-driver sensitivity dominates downside exposure.",
          driver_tile_id: "cost_plus_10",
        },
      ],
      question_bank: [
        {
          id: "qb_1",
          driver_tile_id: "cost_plus_10",
          questions: ["Which risk assumptions remain placeholder-based?"],
        },
      ],
      red_flags_actions: [
        {
          id: "rf_1",
          flag: "Commissioning scope is partially unresolved.",
          action: "Lock mission-critical scopes before procurement freeze.",
        },
      ],
    },
    primary_control_variable: {
      tile_id: "policy_primary_tile",
      label: input.primaryControlLabel,
      impact_pct: 8.2,
      delta_cost: 145000,
      severity: "High",
    },
    first_break_condition: {
      scenario_id: input.breakScenarioLabel.toLowerCase().replace(/\s+/g, "_"),
      scenario_label: input.breakScenarioLabel,
      break_metric: input.breakMetric,
      operator: input.breakOperator,
      threshold: input.threshold,
      observed_value: input.observedValue,
      observed_value_pct: input.breakMetric === "value_gap_pct" ? input.observedValue : -1.1,
    },
    flex_before_break_pct: input.flexBeforeBreakPct,
    exposure_concentration_pct: 61.2,
    ranked_likely_wrong: [
      {
        id: "mlw_1",
        text: `${input.subtype} downside concentration is under-modeled.`,
        why: "Single-driver sensitivity dominates downside exposure.",
        driver_tile_id: "cost_plus_10",
        impact_pct: 8.2,
        severity: "High",
      },
    ],
    decision_insurance_provenance: {
      enabled: true,
      profile_id: input.profileId,
      decision_insurance_policy: {
        status: "available",
        source: "decision_insurance_policy",
        policy_id: "decision_insurance_subtype_policy_v1",
        profile_id: input.profileId,
      },
      primary_control_variable: {
        status: "available",
        source: "decision_insurance_policy.primary_control_variable",
      },
      first_break_condition: {
        status: "available",
        source: "decision_insurance_policy.collapse_trigger",
        policy_metric: input.breakMetric,
        policy_threshold: input.threshold,
        policy_operator: input.breakOperator,
      },
      flex_before_break_pct: {
        status: "available",
        calibration_source: "decision_insurance_policy.flex_calibration",
        band:
          input.flexBeforeBreakPct <= 2.0
            ? "tight"
            : input.flexBeforeBreakPct <= 5.0
              ? "moderate"
              : "comfortable",
      },
      exposure_concentration_pct: { status: "available" },
      ranked_likely_wrong: { status: "available" },
    },
    provenance: {
      profile_id: input.profileId,
      content_profile_id: input.profileId,
      scope_items_profile_id: input.scopeProfileId,
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
        input.breakMetricRef,
      ],
      decision_insurance: {
        enabled: true,
        profile_id: input.profileId,
        decision_insurance_policy: {
          status: "available",
          source: "decision_insurance_policy",
          policy_id: "decision_insurance_subtype_policy_v1",
          profile_id: input.profileId,
        },
        primary_control_variable: { status: "available" },
        first_break_condition: { status: "available" },
        flex_before_break_pct: { status: "available" },
        exposure_concentration_pct: { status: "available" },
        ranked_likely_wrong: { status: "available" },
      },
      dealshield_controls: {
        stress_band_pct: 10,
        use_cost_anchor: false,
        use_revenue_anchor: false,
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

  it("renders explicit multifamily policy-backed first-break semantics with metric-aware observed/threshold formatting", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_multifamily_policy_contract_0"
        data={buildPolicyBackedDealShieldPayload(MULTIFAMILY_POLICY_CONTRACT_CASES[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of MULTIFAMILY_POLICY_CONTRACT_CASES) {
      rerender(
        <DealShieldView
          projectId={`proj_${testCase.profileId}`}
          data={buildPolicyBackedDealShieldPayload(testCase) as any}
          loading={false}
          error={null}
        />
      );

      expect(screen.getByText("Decision Insurance")).toBeInTheDocument();
      expect(screen.getAllByText(testCase.profileId).length).toBeGreaterThan(0);
      expect(screen.getByText(testCase.primaryControlLabel)).toBeInTheDocument();

      if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value-gap percentage crosses threshold.`
          )
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("%");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("%")
            );
          })
        ).toBeInTheDocument();
      } else {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value gap crosses threshold.`
          )
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("$")
            );
          })
        ).toBeInTheDocument();
      }

      expect(screen.getByText(testCase.expectedFlexLabel)).toBeInTheDocument();
    }
  });

  it("renders policy-backed primary-control and collapse/flex contract fields for restaurant, hospitality, multifamily, and industrial", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_policy_contract_0"
        data={buildPolicyBackedDealShieldPayload(POLICY_CONTRACT_CASES[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of POLICY_CONTRACT_CASES) {
      rerender(
        <DealShieldView
          projectId={`proj_${testCase.profileId}`}
          data={buildPolicyBackedDealShieldPayload(testCase) as any}
          loading={false}
          error={null}
        />
      );

      expect(screen.getByText("Decision Insurance")).toBeInTheDocument();
      expect(screen.getAllByText(testCase.profileId).length).toBeGreaterThan(0);
      expect(screen.getByText(testCase.primaryControlLabel)).toBeInTheDocument();

      if (testCase.breakMetric === "value_gap") {
        if (testCase.threshold === 0) {
          expect(
            screen.getByText(`Break occurs in ${testCase.breakScenarioLabel}: value gap turns negative.`)
          ).toBeInTheDocument();
        } else {
          expect(
            screen.getByText(
              `Break occurs in ${testCase.breakScenarioLabel}: value gap crosses threshold.`
            )
          ).toBeInTheDocument();
        }
      } else if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value-gap percentage crosses threshold.`
          )
        ).toBeInTheDocument();
      } else {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: ${testCase.breakMetric} crosses threshold.`
          )
        ).toBeInTheDocument();
      }

      if (testCase.breakMetric === "value_gap") {
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Threshold:") && text.includes(testCase.breakOperator) && text.includes("$");
          })
        ).toBeInTheDocument();
      } else if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Threshold:") && text.includes(testCase.breakOperator) && text.includes("%");
          })
        ).toBeInTheDocument();
      } else {
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Threshold:") && text.includes(testCase.breakOperator);
          })
        ).toBeInTheDocument();
      }
      expect(screen.getByText(testCase.expectedFlexLabel)).toBeInTheDocument();
    }
  });

  it("renders industrial first-break percentage wording with percent-formatted observed and threshold values", () => {
    const industrialCase = POLICY_CONTRACT_CASES.find(
      (testCase) => testCase.profileId === "industrial_distribution_center_v1"
    );
    expect(industrialCase).toBeDefined();

    render(
      <DealShieldView
        projectId="proj_industrial_policy_contract"
        data={buildPolicyBackedDealShieldPayload(industrialCase!) as any}
        loading={false}
        error={null}
      />
    );

    expect(
      screen.getByText(
        "Break occurs in Conservative: value-gap percentage crosses threshold."
      )
    ).toBeInTheDocument();
    expect(
      screen.getByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return text.includes("Observed:") && text.includes("-45.9%");
      })
    ).toBeInTheDocument();
    expect(
      screen.getByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return text.includes("Threshold:") && text.includes("<=") && text.includes("-25.0%");
      })
    ).toBeInTheDocument();
  });

  it("renders explicit office parity for class_a and class_b with canonical decision policy, first-break semantics, DSCR disclosure, and scenario controls", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_office_policy_contract_0"
        data={buildSubtypePolicyPayload(OFFICE_POLICY_CONTRACT_CASES[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of OFFICE_POLICY_CONTRACT_CASES) {
      rerender(
        <DealShieldView
          projectId={`proj_${testCase.profileId}`}
          data={buildSubtypePolicyPayload(testCase) as any}
          loading={false}
          error={null}
        />
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      expect(screen.getByText(DECISION_REASON_TEXT[testCase.decisionReasonCode])).toBeInTheDocument();
      expect(screen.getAllByText(testCase.profileId).length).toBeGreaterThan(0);
      expect(screen.getByText(testCase.primaryControlLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.expectedFlexLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.baseDscr.toFixed(2))).toBeInTheDocument();
      expect(
        screen.getByText("DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.")
      ).toBeInTheDocument();

      const decisionPolicyMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes("Decision Policy:") &&
          text.includes(`Status: ${testCase.decisionStatus}`) &&
          text.includes(`Reason: ${testCase.decisionReasonCode}`) &&
          text.includes("Source: dealshield_policy_v1")
        );
      });
      expect(decisionPolicyMatches.length).toBeGreaterThan(0);

      const controlsLineMatches = screen.getAllByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return (
          text.includes(
            `Tile: ${testCase.profileId} | Content: ${testCase.profileId} | Scope: ${testCase.scopeProfileId}`
          ) &&
          text.includes("Stress band: ±10%") &&
          text.includes("Anchor: Off")
        );
      });
      expect(controlsLineMatches.length).toBeGreaterThan(0);
      expect(screen.getAllByText("±10%").length).toBeGreaterThan(0);

      if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value-gap percentage crosses threshold.`
          )
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("%") && !text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("%") &&
              !text.includes("$")
            );
          })
        ).toBeInTheDocument();
      } else {
        const expectedSummary =
          testCase.threshold === 0
            ? `Break occurs in ${testCase.breakScenarioLabel}: value gap turns negative.`
            : `Break occurs in ${testCase.breakScenarioLabel}: value gap crosses threshold.`;
        expect(screen.getByText(expectedSummary)).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("$")
            );
          })
        ).toBeInTheDocument();
      }
    }
  });

  it("renders explicit specialty parity with canonical status/reason, truthful first-break units, and DSCR visibility (including data center)", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_specialty_policy_contract_0"
        data={buildSubtypePolicyPayload(SPECIALTY_POLICY_CONTRACT_CASES[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of SPECIALTY_POLICY_CONTRACT_CASES) {
      rerender(
        <DealShieldView
          projectId={`proj_${testCase.profileId}`}
          data={buildSubtypePolicyPayload(testCase) as any}
          loading={false}
          error={null}
        />
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      expect(screen.getByText(DECISION_REASON_TEXT[testCase.decisionReasonCode])).toBeInTheDocument();
      expect(screen.getAllByText(testCase.profileId).length).toBeGreaterThan(0);
      expect(screen.getByText(testCase.primaryControlLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.expectedFlexLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.baseDscr.toFixed(2))).toBeInTheDocument();
      expect(
        screen.getByText("DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.")
      ).toBeInTheDocument();

      if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value-gap percentage crosses threshold.`
          )
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("%") && !text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("%") &&
              !text.includes("$")
            );
          })
        ).toBeInTheDocument();
      } else {
        const expectedSummary =
          testCase.threshold === 0
            ? `Break occurs in ${testCase.breakScenarioLabel}: value gap turns negative.`
            : `Break occurs in ${testCase.breakScenarioLabel}: value gap crosses threshold.`;
        expect(screen.getByText(expectedSummary)).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("$")
            );
          })
        ).toBeInTheDocument();
      }
    }
  });

  it("renders explicit healthcare parity with canonical status/reason, metric-aware first-break units, and DSCR visibility for all ten subtypes", () => {
    const { rerender } = render(
      <DealShieldView
        projectId="proj_healthcare_policy_contract_0"
        data={buildSubtypePolicyPayload(HEALTHCARE_POLICY_CONTRACT_CASES[0]) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of HEALTHCARE_POLICY_CONTRACT_CASES) {
      rerender(
        <DealShieldView
          projectId={`proj_${testCase.profileId}`}
          data={buildSubtypePolicyPayload(testCase) as any}
          loading={false}
          error={null}
        />
      );

      expect(
        screen.getByText(`Investment Decision: ${testCase.decisionStatus}`)
      ).toBeInTheDocument();
      expect(screen.getByText(DECISION_REASON_TEXT[testCase.decisionReasonCode])).toBeInTheDocument();
      expect(screen.getAllByText(testCase.profileId).length).toBeGreaterThan(0);
      expect(screen.getByText(testCase.primaryControlLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.expectedFlexLabel)).toBeInTheDocument();
      expect(screen.getByText(testCase.baseDscr.toFixed(2))).toBeInTheDocument();
      expect(
        screen.getByText("DSCR and Yield reflect the underwriting/debt terms in this run — see Provenance.")
      ).toBeInTheDocument();

      if (testCase.breakMetric === "value_gap_pct") {
        expect(
          screen.getByText(
            `Break occurs in ${testCase.breakScenarioLabel}: value-gap percentage crosses threshold.`
          )
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("%") && !text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("%") &&
              !text.includes("$")
            );
          })
        ).toBeInTheDocument();
      } else {
        const expectedSummary =
          testCase.threshold === 0
            ? `Break occurs in ${testCase.breakScenarioLabel}: value gap turns negative.`
            : `Break occurs in ${testCase.breakScenarioLabel}: value gap crosses threshold.`;
        expect(screen.getByText(expectedSummary)).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return text.includes("Observed:") && text.includes("$");
          })
        ).toBeInTheDocument();
        expect(
          screen.getByText((_, element) => {
            if (element?.tagName.toLowerCase() !== "p") return false;
            const text = element.textContent ?? "";
            return (
              text.includes("Threshold:") &&
              text.includes(testCase.breakOperator) &&
              text.includes("$")
            );
          })
        ).toBeInTheDocument();
      }
    }
  });

  it("renders flex and exposure as backend percent units without multiplying by 100", () => {
    render(
      <DealShieldView
        projectId="proj_percent_unit_fix"
        data={buildFlexExposurePolicyPayload(1.3588, 1.3588) as any}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("1.36% (Structurally Tight)")).toBeInTheDocument();
    expect(
      screen.getByText((_, element) => {
        if (element?.tagName.toLowerCase() !== "p") return false;
        const text = element.textContent ?? "";
        return text.includes("Primary control variable contributes 1.36%");
      })
    ).toBeInTheDocument();
    expect(screen.queryByText("136.00% (Structurally Tight)")).not.toBeInTheDocument();
  });

  it("classifies flex band thresholds using percent units (<2 tight, <5 moderate, >=5 flexible)", () => {
    const cases = [
      { value: 1.99, expectedLabel: "1.99% (Structurally Tight)" },
      { value: 2.0, expectedLabel: "2.00% (Moderate)" },
      { value: 4.99, expectedLabel: "4.99% (Moderate)" },
      { value: 5.0, expectedLabel: "5.00% (Flexible)" },
    ];
    const { rerender } = render(
      <DealShieldView
        projectId="proj_flex_thresholds_0"
        data={buildFlexExposurePolicyPayload(cases[0].value, 58.4) as any}
        loading={false}
        error={null}
      />
    );

    for (const testCase of cases) {
      rerender(
        <DealShieldView
          projectId={`proj_flex_thresholds_${testCase.value}`}
          data={buildFlexExposurePolicyPayload(testCase.value, 58.4) as any}
          loading={false}
          error={null}
        />
      );
      expect(screen.getByText(testCase.expectedLabel)).toBeInTheDocument();
    }
  });
});
