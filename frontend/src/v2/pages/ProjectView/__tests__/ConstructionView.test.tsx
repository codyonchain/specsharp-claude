import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
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

const SPECIALTY_SCHEDULE_CASES = [
  {
    subtype: "data_center",
    sitePhaseLabel: "Utility Interconnect + Foundations",
    structuralPhaseLabel: "Critical Power + Cooling Plant",
  },
  {
    subtype: "laboratory",
    sitePhaseLabel: "Lab Utility Rough-In + Foundations",
    structuralPhaseLabel: "Containment Build + Commissioning",
  },
  {
    subtype: "self_storage",
    sitePhaseLabel: "Prototype Pads + Foundations",
    structuralPhaseLabel: "Envelope + Access-Control Buildout",
  },
  {
    subtype: "car_dealership",
    sitePhaseLabel: "Showroom + Service Slab",
    structuralPhaseLabel: "Service Equipment + Delivery Court",
  },
  {
    subtype: "broadcast_facility",
    sitePhaseLabel: "Acoustic Isolation + Foundations",
    structuralPhaseLabel: "Studio Systems + Transmission Backbone",
  },
] as const;

const DATA_CENTER_SCOPE_ITEMS = [
  {
    trade: "structural",
    systems: [
      { name: "Raised Floor + Cable Trench", quantity: 120000, unit: "SF", unit_cost: 42.5, total_cost: 5100000 },
      { name: "Heavy Roof + Support Steel", quantity: 120000, unit: "SF", unit_cost: 35.0, total_cost: 4200000 },
      { name: "Seismic Bracing for Rack Rows", quantity: 120000, unit: "SF", unit_cost: 22.0, total_cost: 2640000 },
    ],
  },
  {
    trade: "mechanical",
    systems: [
      { name: "Central Plant Chillers", quantity: 120000, unit: "SF", unit_cost: 58.0, total_cost: 6960000 },
      { name: "Aisle Containment + Controls", quantity: 120000, unit: "SF", unit_cost: 41.0, total_cost: 4920000 },
      { name: "CRAH Units + Hot Aisle Return", quantity: 120000, unit: "SF", unit_cost: 37.0, total_cost: 4440000 },
      { name: "Condenser Water Pumping + Treatment", quantity: 120000, unit: "SF", unit_cost: 28.0, total_cost: 3360000 },
      { name: "Economizer Relief + Airside Controls", quantity: 120000, unit: "SF", unit_cost: 23.0, total_cost: 2760000 },
    ],
  },
  {
    trade: "electrical",
    systems: [
      { name: "UPS, Switchgear + Distribution", quantity: 120000, unit: "SF", unit_cost: 62.0, total_cost: 7440000 },
      { name: "Generator Paralleling + Fuel Controls", quantity: 120000, unit: "SF", unit_cost: 49.0, total_cost: 5880000 },
      { name: "Busway + Rack Power Taps", quantity: 120000, unit: "SF", unit_cost: 40.0, total_cost: 4800000 },
      { name: "Battery Monitoring + DC Controls", quantity: 120000, unit: "SF", unit_cost: 33.0, total_cost: 3960000 },
      { name: "Branch Circuit Monitoring + BMS Points", quantity: 120000, unit: "SF", unit_cost: 29.0, total_cost: 3480000 },
    ],
  },
  {
    trade: "plumbing",
    systems: [
      { name: "Process Water + Leak Detection", quantity: 120000, unit: "SF", unit_cost: 19.0, total_cost: 2280000 },
      { name: "Sanitary / Domestic + Trenching", quantity: 120000, unit: "SF", unit_cost: 14.0, total_cost: 1680000 },
      { name: "Humidification Makeup + Blowdown", quantity: 120000, unit: "SF", unit_cost: 11.0, total_cost: 1320000 },
    ],
  },
  {
    trade: "finishes",
    systems: [
      { name: "White Space Envelope", quantity: 120000, unit: "SF", unit_cost: 17.0, total_cost: 2040000 },
      { name: "NOC + Support Areas", quantity: 120000, unit: "SF", unit_cost: 14.0, total_cost: 1680000 },
      { name: "Antistatic Access Floor Finish Package", quantity: 120000, unit: "SF", unit_cost: 13.0, total_cost: 1560000 },
    ],
  },
] as const;

const MULTIFAMILY_SCHEDULE_CASES = [
  { subtype: "market_rate_apartments" },
  { subtype: "luxury_apartments" },
  { subtype: "affordable_housing" },
] as const;

const OFFICE_SCHEDULE_CASES = [
  {
    subtype: "class_a",
    sitePhaseLabel: "Class A Podium + Utility Enablement",
    structuralPhaseLabel: "Class A Core/Shell + Premium Tenant Stack",
  },
  {
    subtype: "class_b",
    sitePhaseLabel: "Class B Sitework + Utility Tie-Ins",
    structuralPhaseLabel: "Class B Core/Shell + Tenant Readiness",
  },
] as const;

const RETAIL_SCHEDULE_CASES = [
  {
    subtype: "shopping_center",
    sitePhaseLabel: "Retail Pad Prep + Utility Looping",
    structuralPhaseLabel: "Inline Shell + Canopy Program",
  },
  {
    subtype: "big_box",
    sitePhaseLabel: "Big Box Grading + Heavy Slab Prep",
    structuralPhaseLabel: "Long-Span Steel + Dock Apron Build",
  },
] as const;

const HEALTHCARE_SCHEDULE_CASES = [
  {
    subtype: "surgical_center",
    sitePhaseLabel: "OR Sterile-Core Prep + Foundations",
    structuralPhaseLabel: "Procedure Suite Build + Commissioning",
  },
  {
    subtype: "imaging_center",
    sitePhaseLabel: "Shielding + Magnet Slab Prep",
    structuralPhaseLabel: "MRI/CT Suite Build + Integration",
  },
  {
    subtype: "urgent_care",
    sitePhaseLabel: "Fast-Track Utility Tie-Ins",
    structuralPhaseLabel: "Exam Pod Build + Throughput Systems",
  },
  {
    subtype: "outpatient_clinic",
    sitePhaseLabel: "Clinic Utility Grid + Foundations",
    structuralPhaseLabel: "Exam Pod Build + Nurse Core",
  },
  {
    subtype: "medical_office_building",
    sitePhaseLabel: "Tenant Utility Backbone + Podium",
    structuralPhaseLabel: "Shell + Vertical Core Build",
  },
  {
    subtype: "dental_office",
    sitePhaseLabel: "Chair Utility Trenching + Foundations",
    structuralPhaseLabel: "Operatory Build + Sterilization Core",
  },
  {
    subtype: "hospital",
    sitePhaseLabel: "Campus Utility Spine + Foundations",
    structuralPhaseLabel: "Critical Care Tower + MEP Plant",
  },
  {
    subtype: "medical_center",
    sitePhaseLabel: "Diagnostic Utility Grid + Foundations",
    structuralPhaseLabel: "Procedure Core + Ambulatory Fit-Out",
  },
  {
    subtype: "nursing_home",
    sitePhaseLabel: "Resident Wing Foundations + Utilities",
    structuralPhaseLabel: "Resident Pods + Life-Safety Build",
  },
  {
    subtype: "rehabilitation",
    sitePhaseLabel: "Therapy Utility Prep + Foundations",
    structuralPhaseLabel: "Rehab Gym + Hydro Suite Build",
  },
] as const;

const EDUCATIONAL_SCHEDULE_CASES = [
  {
    subtype: "elementary_school",
    sitePhaseLabel: "Elementary Site Utilities + Foundations",
    structuralPhaseLabel: "Classroom Wings + Life-Safety Envelope",
  },
  {
    subtype: "middle_school",
    sitePhaseLabel: "Middle School Utility Grid + Foundations",
    structuralPhaseLabel: "STEM Lab Wings + Commons Buildout",
  },
  {
    subtype: "high_school",
    sitePhaseLabel: "High School Campus Prep + Stadium Utilities",
    structuralPhaseLabel: "Academic Core + Athletics Support Build",
  },
  {
    subtype: "university",
    sitePhaseLabel: "University Research Utility Spine + Foundations",
    structuralPhaseLabel: "Lab/Academic Core + Commissioning Blocks",
  },
  {
    subtype: "community_college",
    sitePhaseLabel: "Community College Trades Utility Prep + Foundations",
    structuralPhaseLabel: "Workforce Labs + Flexible Classroom Build",
  },
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

const buildSpecialtyScheduleProject = (
  subtype: (typeof SPECIALTY_SCHEDULE_CASES)[number]["subtype"],
  scheduleSource: "subtype" | "building_type"
) => {
  const fixture = SPECIALTY_SCHEDULE_CASES.find((item) => item.subtype === subtype)!;
  const project = buildCrossTypeScheduleProject("specialty", subtype, scheduleSource);
  project.analysis.calculations.construction_schedule.total_months =
    scheduleSource === "subtype"
      ? subtype === "data_center"
        ? 28
        : subtype === "laboratory"
          ? 24
          : subtype === "self_storage"
            ? 12
            : subtype === "car_dealership"
              ? 16
              : 18
      : subtype === "data_center"
        ? 26
        : subtype === "laboratory"
          ? 22
          : subtype === "self_storage"
            ? 11
            : subtype === "car_dealership"
              ? 15
              : 17;
  project.analysis.calculations.construction_schedule.phases =
    scheduleSource === "subtype"
      ? [
          {
            id: "site_foundation",
            label: fixture.sitePhaseLabel,
            start_month: 0,
            duration_months: 6,
            end_month: 6,
          },
          {
            id: "structural",
            label: fixture.structuralPhaseLabel,
            start_month: 4,
            duration_months: 12,
            end_month: 16,
          },
        ]
      : [
          {
            id: "site_foundation",
            label: "Specialty Baseline Site Program",
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: "Specialty Baseline Structural Program",
            start_month: 3,
            duration_months: 10,
            end_month: 13,
          },
        ];
  project.analysis.calculations.scope_items =
    subtype === "data_center"
      ? DATA_CENTER_SCOPE_ITEMS.map((trade) => ({
          trade: trade.trade,
          systems: trade.systems.map((system) => ({ ...system })),
        }))
      : [];
  return project;
};

const buildHealthcareScheduleProject = (
  subtype: (typeof HEALTHCARE_SCHEDULE_CASES)[number]["subtype"],
  scheduleSource: "subtype" | "building_type"
) => {
  const fixture = HEALTHCARE_SCHEDULE_CASES.find((item) => item.subtype === subtype)!;
  const project = buildCrossTypeScheduleProject("healthcare", subtype, scheduleSource);
  project.analysis.calculations.construction_schedule.total_months =
    scheduleSource === "subtype"
      ? subtype === "hospital"
        ? 34
        : subtype === "medical_center"
          ? 30
          : subtype === "nursing_home"
            ? 22
            : subtype === "medical_office_building"
              ? 24
              : 18
      : 20;
  project.analysis.calculations.construction_schedule.phases =
    scheduleSource === "subtype"
      ? [
          {
            id: "site_foundation",
            label: fixture.sitePhaseLabel,
            start_month: 0,
            duration_months: 6,
            end_month: 6,
          },
          {
            id: "structural",
            label: fixture.structuralPhaseLabel,
            start_month: 4,
            duration_months: 12,
            end_month: 16,
          },
        ]
      : [
          {
            id: "site_foundation",
            label: "Healthcare Baseline Site Program",
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: "Healthcare Baseline Structural Program",
            start_month: 3,
            duration_months: 10,
            end_month: 13,
          },
        ];
  return project;
};

const buildEducationalScheduleProject = (
  subtype: (typeof EDUCATIONAL_SCHEDULE_CASES)[number]["subtype"],
  scheduleSource: "subtype" | "building_type",
  options?: { unknownFallbackSubtype?: boolean }
) => {
  const fixture = EDUCATIONAL_SCHEDULE_CASES.find((item) => item.subtype === subtype)!;
  const fallbackSubtype =
    scheduleSource === "building_type" && options?.unknownFallbackSubtype
      ? "unknown_educational_variant"
      : subtype;
  const project = buildCrossTypeScheduleProject("educational", fallbackSubtype, scheduleSource);
  project.analysis.calculations.construction_schedule.total_months =
    scheduleSource === "subtype"
      ? subtype === "elementary_school"
        ? 18
        : subtype === "middle_school"
          ? 22
          : subtype === "high_school"
            ? 26
            : subtype === "university"
              ? 30
              : 21
      : 30;
  project.analysis.calculations.construction_schedule.phases =
    scheduleSource === "subtype"
      ? [
          {
            id: "site_foundation",
            label: fixture.sitePhaseLabel,
            start_month: 0,
            duration_months: 6,
            end_month: 6,
          },
          {
            id: "structural",
            label: fixture.structuralPhaseLabel,
            start_month: 4,
            duration_months: 12,
            end_month: 16,
          },
        ]
      : [
          {
            id: "site_foundation",
            label: "Educational Baseline Site Program",
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: "Educational Baseline Structural Program",
            start_month: 3,
            duration_months: 10,
            end_month: 13,
          },
        ];
  return project;
};

const buildOfficeScheduleProject = (
  subtype: (typeof OFFICE_SCHEDULE_CASES)[number]["subtype"],
  scheduleSource: "subtype" | "building_type"
) => {
  const fixture = OFFICE_SCHEDULE_CASES.find((item) => item.subtype === subtype)!;
  const project = buildCrossTypeScheduleProject("office", subtype, scheduleSource);
  project.analysis.calculations.construction_schedule.total_months =
    scheduleSource === "subtype"
      ? subtype === "class_a"
        ? 26
        : 18
      : 20;
  project.analysis.calculations.construction_schedule.phases =
    scheduleSource === "subtype"
      ? [
          {
            id: "site_foundation",
            label: fixture.sitePhaseLabel,
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: fixture.structuralPhaseLabel,
            start_month: 3,
            duration_months: 11,
            end_month: 14,
          },
        ]
      : [
          {
            id: "site_foundation",
            label: "Office Baseline Site Program",
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: "Office Baseline Structural Program",
            start_month: 3,
            duration_months: 10,
            end_month: 13,
          },
        ];
  return project;
};

const buildRetailScheduleProject = (
  subtype: (typeof RETAIL_SCHEDULE_CASES)[number]["subtype"],
  scheduleSource: "subtype" | "building_type"
) => {
  const fixture = RETAIL_SCHEDULE_CASES.find((item) => item.subtype === subtype)!;
  const project = buildCrossTypeScheduleProject("retail", subtype, scheduleSource);
  project.analysis.calculations.construction_schedule.total_months =
    scheduleSource === "subtype"
      ? subtype === "shopping_center"
        ? 20
        : 18
      : 24;
  project.analysis.calculations.construction_schedule.phases =
    scheduleSource === "subtype"
      ? [
          {
            id: "site_foundation",
            label: fixture.sitePhaseLabel,
            start_month: 0,
            duration_months: 4,
            end_month: 4,
          },
          {
            id: "structural",
            label: fixture.structuralPhaseLabel,
            start_month: 2,
            duration_months: 8,
            end_month: 10,
          },
        ]
      : [
          {
            id: "site_foundation",
            label: "Retail Baseline Site Program",
            start_month: 0,
            duration_months: 5,
            end_month: 5,
          },
          {
            id: "structural",
            label: "Retail Baseline Structural Program",
            start_month: 3,
            duration_months: 10,
            end_month: 13,
          },
        ];
  return project;
};

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

  it("renders industrial distribution-center schedule provenance for subtype and baseline fallback", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildCrossTypeScheduleProject(
          "industrial",
          "distribution_center",
          "subtype"
        )}
      />
    );

    expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
    expect(
      screen.getByText("Timeline is tailored for this subtype profile.")
    ).toBeInTheDocument();
    expect(screen.getAllByText("Subtype Structural Program").length).toBeGreaterThan(0);

    rerender(
      <ConstructionView
        project={buildCrossTypeScheduleProject(
          "industrial",
          "distribution_center",
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
    expect(screen.getAllByText("Baseline Structural Program").length).toBeGreaterThan(0);
  });

  it("renders explicit multifamily schedule provenance parity for subtype and fallback sources", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildCrossTypeScheduleProject(
          "multifamily",
          MULTIFAMILY_SCHEDULE_CASES[0].subtype,
          "subtype"
        )}
      />
    );

    for (const testCase of MULTIFAMILY_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildCrossTypeScheduleProject(
            "multifamily",
            testCase.subtype,
            "subtype"
          )}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText("Subtype Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Subtype Structural Program").length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildCrossTypeScheduleProject(
            "multifamily",
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
      expect(screen.getAllByText("Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders truthful specialty schedule-source provenance for all five subtypes, including data center", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildSpecialtyScheduleProject(SPECIALTY_SCHEDULE_CASES[0].subtype, "subtype")}
      />
    );

    for (const testCase of SPECIALTY_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildSpecialtyScheduleProject(testCase.subtype, "subtype")}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText(testCase.sitePhaseLabel).length).toBeGreaterThan(0);
      expect(screen.getAllByText(testCase.structuralPhaseLabel).length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildSpecialtyScheduleProject(testCase.subtype, "building_type")}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
      expect(screen.getAllByText("Specialty Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Specialty Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders explicit healthcare schedule-source provenance parity for all ten subtypes, including medical_office_building", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildHealthcareScheduleProject(HEALTHCARE_SCHEDULE_CASES[0].subtype, "subtype")}
      />
    );

    for (const testCase of HEALTHCARE_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildHealthcareScheduleProject(testCase.subtype, "subtype")}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText(testCase.sitePhaseLabel).length).toBeGreaterThan(0);
      expect(screen.getAllByText(testCase.structuralPhaseLabel).length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildHealthcareScheduleProject(testCase.subtype, "building_type")}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
      expect(screen.getAllByText("Healthcare Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Healthcare Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders educational schedule-source parity for all five subtypes with explicit unknown-subtype fallback messaging", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildEducationalScheduleProject(EDUCATIONAL_SCHEDULE_CASES[0].subtype, "subtype")}
      />
    );

    for (const testCase of EDUCATIONAL_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildEducationalScheduleProject(testCase.subtype, "subtype")}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText(testCase.sitePhaseLabel).length).toBeGreaterThan(0);
      expect(screen.getAllByText(testCase.structuralPhaseLabel).length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildEducationalScheduleProject(testCase.subtype, "building_type", {
            unknownFallbackSubtype: true,
          })}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
      expect(screen.getAllByText("Educational Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Educational Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders office schedule-source parity for class_a and class_b with subtype-specific phases and truthful fallback messaging", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildOfficeScheduleProject(OFFICE_SCHEDULE_CASES[0].subtype, "subtype")}
      />
    );

    for (const testCase of OFFICE_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildOfficeScheduleProject(testCase.subtype, "subtype")}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByTitle(`Subtype schedule • type: office • subtype: ${testCase.subtype}`)
      ).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText(testCase.sitePhaseLabel).length).toBeGreaterThan(0);
      expect(screen.getAllByText(testCase.structuralPhaseLabel).length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildOfficeScheduleProject(testCase.subtype, "building_type")}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByTitle("Building-type baseline • type: office")
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
      expect(screen.getAllByText("Office Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Office Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders retail schedule-source parity for shopping_center and big_box with subtype-specific phases and truthful fallback messaging", () => {
    const { rerender } = render(
      <ConstructionView
        project={buildRetailScheduleProject(RETAIL_SCHEDULE_CASES[0].subtype, "subtype")}
      />
    );

    for (const testCase of RETAIL_SCHEDULE_CASES) {
      rerender(
        <ConstructionView
          project={buildRetailScheduleProject(testCase.subtype, "subtype")}
        />
      );
      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(
        screen.getByTitle(`Subtype schedule • type: retail • subtype: ${testCase.subtype}`)
      ).toBeInTheDocument();
      expect(
        screen.getByText("Timeline is tailored for this subtype profile.")
      ).toBeInTheDocument();
      expect(screen.getAllByText(testCase.sitePhaseLabel).length).toBeGreaterThan(0);
      expect(screen.getAllByText(testCase.structuralPhaseLabel).length).toBeGreaterThan(0);

      rerender(
        <ConstructionView
          project={buildRetailScheduleProject(testCase.subtype, "building_type")}
        />
      );
      expect(screen.getByText("Building-type baseline")).toBeInTheDocument();
      expect(
        screen.getByTitle("Building-type baseline • type: retail")
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          "Timeline uses building-type baseline (subtype override unavailable)."
        )
      ).toBeInTheDocument();
      expect(screen.getAllByText("Retail Baseline Site Program").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Retail Baseline Structural Program").length).toBeGreaterThan(0);
    }
  });

  it("renders office trade scope depth and per-feature breakdown visibility for class_a and class_b without fallback copy", () => {
    const cases = [
      {
        subtype: "class_a" as const,
        structuralName: "Post-Tensioned Floor Plates + Premium Core",
        mechanicalName: "VAV + DOAS Integration and Tenant Condenser Loops",
        electricalName: "Smart Switchgear + Tenant Metering Backbone",
        plumbingName: "High-Rise Booster + Low-Flow Fixture Branches",
        finishesName: "Executive Finish Package + Acoustic Ceilings",
        breakdown: [
          { id: "executive_floor", label: "Executive Floor", cost_per_sf: 4.5, total_cost: 360000 },
          { id: "data_center", label: "Data Center", cost_per_sf: 3.5, total_cost: 280000 },
        ],
      },
      {
        subtype: "class_b" as const,
        structuralName: "Composite Slab + Repositioned Core Openings",
        mechanicalName: "Packaged RTU Upgrades + Outside-Air Reset",
        electricalName: "Tenant Submetering + LED Retrofit Distribution",
        plumbingName: "Restroom Stack Renewal + Domestic Hot-Water Loop",
        finishesName: "Lobby Refresh + Demountable Collaboration Rooms",
        breakdown: [
          { id: "conference_room", label: "Conference Room Suite", cost_per_sf: 2.0, total_cost: 120000 },
          { id: "security_desk", label: "Security Desk", cost_per_sf: 1.5, total_cost: 90000 },
        ],
      },
    ];

    const { rerender } = render(
      <ConstructionView project={buildOfficeScheduleProject(cases[0].subtype, "subtype")} />
    );

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    for (const testCase of cases) {
      const project = buildOfficeScheduleProject(testCase.subtype, "subtype");
      project.analysis.calculations.trade_breakdown = {
        structural: 4600000,
        mechanical: 5200000,
        electrical: 4800000,
        plumbing: 2600000,
        finishes: 4100000,
      };
      project.analysis.calculations.scope_items = [
        {
          trade: "structural",
          systems: [
            { name: testCase.structuralName, quantity: 160000, unit: "SF", unit_cost: 34, total_cost: 5440000 },
            { name: "Lateral Frame + Drift Controls", quantity: 160000, unit: "SF", unit_cost: 26, total_cost: 4160000 },
            { name: "Facade Support + Edge Slab Detailing", quantity: 160000, unit: "SF", unit_cost: 22, total_cost: 3520000 },
            { name: "Loading Dock Slab Reinforcement", quantity: 160000, unit: "SF", unit_cost: 12, total_cost: 1920000 },
            { name: "Stair and Core Fireproofing Program", quantity: 160000, unit: "SF", unit_cost: 10, total_cost: 1600000 },
          ],
        },
        {
          trade: "mechanical",
          systems: [
            { name: testCase.mechanicalName, quantity: 160000, unit: "SF", unit_cost: 31, total_cost: 4960000 },
            { name: "Tenant Branch Ductwork + Zoning Controls", quantity: 160000, unit: "SF", unit_cost: 24, total_cost: 3840000 },
            { name: "Central Plant Integration + BMS Points", quantity: 160000, unit: "SF", unit_cost: 20, total_cost: 3200000 },
            { name: "Core Exhaust + Relief Air Distribution", quantity: 160000, unit: "SF", unit_cost: 16, total_cost: 2560000 },
            { name: "Commissioning and TAB Package", quantity: 160000, unit: "SF", unit_cost: 11, total_cost: 1760000 },
          ],
        },
        {
          trade: "electrical",
          systems: [
            { name: testCase.electricalName, quantity: 160000, unit: "SF", unit_cost: 30, total_cost: 4800000 },
            { name: "Vertical Riser + Panelboard Distribution", quantity: 160000, unit: "SF", unit_cost: 24, total_cost: 3840000 },
            { name: "Lighting Control + Daylight Harvesting", quantity: 160000, unit: "SF", unit_cost: 18, total_cost: 2880000 },
            { name: "Low-Voltage Backbone + Access Control", quantity: 160000, unit: "SF", unit_cost: 14, total_cost: 2240000 },
            { name: "Emergency Power Transfer + ATS", quantity: 160000, unit: "SF", unit_cost: 12, total_cost: 1920000 },
          ],
        },
        {
          trade: "plumbing",
          systems: [
            { name: testCase.plumbingName, quantity: 160000, unit: "SF", unit_cost: 19, total_cost: 3040000 },
            { name: "Domestic Cold-Water Distribution", quantity: 160000, unit: "SF", unit_cost: 15, total_cost: 2400000 },
            { name: "Sanitary + Vent Stack Coordination", quantity: 160000, unit: "SF", unit_cost: 12, total_cost: 1920000 },
            { name: "Storm Leader + Roof Drain Routing", quantity: 160000, unit: "SF", unit_cost: 11, total_cost: 1760000 },
            { name: "Tenant Pantry and Breakroom Rough-In", quantity: 160000, unit: "SF", unit_cost: 9, total_cost: 1440000 },
          ],
        },
        {
          trade: "finishes",
          systems: [
            { name: testCase.finishesName, quantity: 160000, unit: "SF", unit_cost: 22, total_cost: 3520000 },
            { name: "Raised Access Flooring + Carpet Tile", quantity: 160000, unit: "SF", unit_cost: 18, total_cost: 2880000 },
            { name: "Glass Fronts + Demising Partitions", quantity: 160000, unit: "SF", unit_cost: 15, total_cost: 2400000 },
            { name: "Lobby Stone + Feature Millwork", quantity: 160000, unit: "SF", unit_cost: 13, total_cost: 2080000 },
            { name: "Tenant Paint + Acoustical Ceilings", quantity: 160000, unit: "SF", unit_cost: 11, total_cost: 1760000 },
          ],
        },
      ];
      project.analysis.calculations.construction_costs.special_features_total = testCase.breakdown.reduce(
        (sum, item) => sum + item.total_cost,
        0
      );
      project.analysis.calculations.construction_costs.special_features_breakdown = testCase.breakdown;

      rerender(<ConstructionView project={project} />);

      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(screen.getByText("Special Features")).toBeInTheDocument();
      for (const row of testCase.breakdown) {
        expect(screen.getByText(row.label)).toBeInTheDocument();
      }
      expect(
        screen.queryByText("Selected feature IDs were not provided in project data; showing aggregate only.")
      ).not.toBeInTheDocument();
      expect(
        screen.queryByText("Per-feature breakdown is unavailable for this project version; showing aggregate total only.")
      ).not.toBeInTheDocument();

      openTradeCard("Structural");
      expect(screen.getByText("5 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.structuralName)).toBeInTheDocument();

      openTradeCard("Mechanical");
      expect(screen.getByText("5 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.mechanicalName)).toBeInTheDocument();

      openTradeCard("Electrical");
      expect(screen.getByText("5 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.electricalName)).toBeInTheDocument();

      openTradeCard("Plumbing");
      expect(screen.getByText("5 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.plumbingName)).toBeInTheDocument();

      openTradeCard("Finishes");
      expect(screen.getByText("5 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.finishesName)).toBeInTheDocument();
    }
  });

  it("renders retail trade scope depth and per-feature breakdown visibility for shopping_center and big_box", () => {
    const cases = [
      {
        subtype: "shopping_center" as const,
        structuralName: "Inline Shell Bay Frames + Canopy Steel",
        mechanicalName: "Multi-Tenant RTU Program + Controls",
        electricalName: "Tenant Metering + Site Lighting Backbone",
        plumbingName: "Sanitary Main + Grease Interceptor Network",
        finishesName: "Storefront Systems + Wayfinding Package",
        expectedSystems: {
          structural: "4 systems",
          mechanical: "4 systems",
          electrical: "4 systems",
          plumbing: "3 systems",
          finishes: "4 systems",
        },
        breakdown: [
          { id: "covered_walkway", label: "Covered Walkway", cost_per_sf: 2.0, total_cost: 160000 },
          { id: "drive_thru", label: "Drive-Thru", cost_per_sf: 4.0, total_cost: 320000 },
        ],
      },
      {
        subtype: "big_box" as const,
        structuralName: "Long-Span Steel + Dock Apron Reinforcement",
        mechanicalName: "High-Bay HVAC + Refrigeration Support",
        electricalName: "High-Amp Service + Case Power Distribution",
        plumbingName: "Domestic Main + Process Waste Routing",
        finishesName: "Front-End Buildout + Branded Entry Finishes",
        expectedSystems: {
          structural: "5 systems",
          mechanical: "4 systems",
          electrical: "4 systems",
          plumbing: "3 systems",
          finishes: "4 systems",
        },
        breakdown: [
          { id: "mezzanine", label: "Mezzanine", cost_per_sf: 2.5, total_cost: 200000 },
          { id: "refrigerated_storage", label: "Refrigerated Storage", cost_per_sf: 3.5, total_cost: 280000 },
        ],
      },
    ];

    const { rerender } = render(
      <ConstructionView project={buildRetailScheduleProject(cases[0].subtype, "subtype")} />
    );

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    for (const testCase of cases) {
      const project = buildRetailScheduleProject(testCase.subtype, "subtype");
      project.analysis.calculations.trade_breakdown = {
        structural: 4200000,
        mechanical: 4800000,
        electrical: 4500000,
        plumbing: 2400000,
        finishes: 3600000,
      };
      project.analysis.calculations.scope_items = [
        {
          trade: "structural",
          systems:
            testCase.subtype === "shopping_center"
              ? [
                  { name: testCase.structuralName, quantity: 150000, unit: "SF", unit_cost: 26, total_cost: 3900000 },
                  { name: "Canopy Colonnade Framing", quantity: 150000, unit: "SF", unit_cost: 20, total_cost: 3000000 },
                  { name: "Pad Foundation + Plaza Slab", quantity: 150000, unit: "SF", unit_cost: 18, total_cost: 2700000 },
                  { name: "Loading Apron Reinforcement", quantity: 150000, unit: "SF", unit_cost: 12, total_cost: 1800000 },
                ]
              : [
                  { name: testCase.structuralName, quantity: 180000, unit: "SF", unit_cost: 29, total_cost: 5220000 },
                  { name: "Thickened Slab Loading Zones", quantity: 180000, unit: "SF", unit_cost: 24, total_cost: 4320000 },
                  { name: "Mezzanine and Stair Core Package", quantity: 180000, unit: "SF", unit_cost: 20, total_cost: 3600000 },
                  { name: "Dock Wall + Yard Structure", quantity: 180000, unit: "SF", unit_cost: 16, total_cost: 2880000 },
                  { name: "Garden Center Canopy Steel", quantity: 180000, unit: "SF", unit_cost: 12, total_cost: 2160000 },
                ],
        },
        {
          trade: "mechanical",
          systems: [
            { name: testCase.mechanicalName, quantity: 170000, unit: "SF", unit_cost: 27, total_cost: 4590000 },
            { name: "Tenant Duct Distribution + Balancing", quantity: 170000, unit: "SF", unit_cost: 22, total_cost: 3740000 },
            { name: "Controls Integration + TAB", quantity: 170000, unit: "SF", unit_cost: 17, total_cost: 2890000 },
            { name: "Exhaust and Makeup-Air Package", quantity: 170000, unit: "SF", unit_cost: 14, total_cost: 2380000 },
          ],
        },
        {
          trade: "electrical",
          systems: [
            { name: testCase.electricalName, quantity: 170000, unit: "SF", unit_cost: 26, total_cost: 4420000 },
            { name: "Switchgear + Feeder Distribution", quantity: 170000, unit: "SF", unit_cost: 21, total_cost: 3570000 },
            { name: "Life-Safety Fire Alarm Controls", quantity: 170000, unit: "SF", unit_cost: 16, total_cost: 2720000 },
            { name: "Exterior Lighting + Access Controls", quantity: 170000, unit: "SF", unit_cost: 13, total_cost: 2210000 },
          ],
        },
        {
          trade: "plumbing",
          systems: [
            { name: testCase.plumbingName, quantity: 170000, unit: "SF", unit_cost: 18, total_cost: 3060000 },
            { name: "Domestic Water Loop + Branches", quantity: 170000, unit: "SF", unit_cost: 14, total_cost: 2380000 },
            { name: "Restroom Core Fixture Package", quantity: 170000, unit: "SF", unit_cost: 12, total_cost: 2040000 },
          ],
        },
        {
          trade: "finishes",
          systems: [
            { name: testCase.finishesName, quantity: 170000, unit: "SF", unit_cost: 20, total_cost: 3400000 },
            { name: "Inline White-Box Turnover", quantity: 170000, unit: "SF", unit_cost: 16, total_cost: 2720000 },
            { name: "Common-Area Ceiling + Paving Finishes", quantity: 170000, unit: "SF", unit_cost: 14, total_cost: 2380000 },
            { name: "Entry Signage + Branding Finishes", quantity: 170000, unit: "SF", unit_cost: 12, total_cost: 2040000 },
          ],
        },
      ];
      project.analysis.calculations.construction_costs.special_features_total = testCase.breakdown.reduce(
        (sum, item) => sum + item.total_cost,
        0
      );
      project.analysis.calculations.construction_costs.special_features_breakdown = testCase.breakdown;

      rerender(<ConstructionView project={project} />);

      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
      expect(screen.getByText("Special Features")).toBeInTheDocument();
      for (const row of testCase.breakdown) {
        expect(screen.getByText(row.label)).toBeInTheDocument();
      }
      expect(
        screen.queryByText("Selected feature IDs were not provided in project data; showing aggregate only.")
      ).not.toBeInTheDocument();
      expect(
        screen.queryByText("Per-feature breakdown is unavailable for this project version; showing aggregate total only.")
      ).not.toBeInTheDocument();

      openTradeCard("Structural");
      expect(screen.getByText(testCase.expectedSystems.structural)).toBeInTheDocument();
      expect(screen.getByText(testCase.structuralName)).toBeInTheDocument();

      openTradeCard("Mechanical");
      expect(screen.getByText(testCase.expectedSystems.mechanical)).toBeInTheDocument();
      expect(screen.getByText(testCase.mechanicalName)).toBeInTheDocument();

      openTradeCard("Electrical");
      expect(screen.getByText(testCase.expectedSystems.electrical)).toBeInTheDocument();
      expect(screen.getByText(testCase.electricalName)).toBeInTheDocument();

      openTradeCard("Plumbing");
      expect(screen.getByText(testCase.expectedSystems.plumbing)).toBeInTheDocument();
      expect(screen.getByText(testCase.plumbingName)).toBeInTheDocument();

      openTradeCard("Finishes");
      expect(screen.getByText(testCase.expectedSystems.finishes)).toBeInTheDocument();
      expect(screen.getByText(testCase.finishesName)).toBeInTheDocument();
    }
  });

  it("renders healthcare dominant-trade scope depth and truthful special-feature breakdown", () => {
    const project = buildHealthcareScheduleProject("hospital", "subtype");
    project.analysis.calculations.trade_breakdown = {
      structural: 4200000,
      mechanical: 6400000,
      electrical: 5900000,
      plumbing: 3100000,
      finishes: 2800000,
    };
    project.analysis.calculations.scope_items = [
      {
        trade: "mechanical",
        systems: [
          { name: "Air-Handling Units + Filtration", quantity: 180000, unit: "SF", unit_cost: 34, total_cost: 6120000 },
          { name: "Chilled Water Distribution", quantity: 180000, unit: "SF", unit_cost: 26, total_cost: 4680000 },
          { name: "Medical Exhaust + Isolation Controls", quantity: 180000, unit: "SF", unit_cost: 23, total_cost: 4140000 },
          { name: "Critical Care Humidity Control", quantity: 180000, unit: "SF", unit_cost: 21, total_cost: 3780000 },
          { name: "Smoke Control + Stair Pressurization", quantity: 180000, unit: "SF", unit_cost: 18, total_cost: 3240000 },
        ],
      },
      {
        trade: "electrical",
        systems: [
          { name: "Redundant Switchgear + UPS", quantity: 180000, unit: "SF", unit_cost: 29, total_cost: 5220000 },
          { name: "Nurse Call + Low Voltage Backbone", quantity: 180000, unit: "SF", unit_cost: 18, total_cost: 3240000 },
          { name: "Essential Power Branch Circuits", quantity: 180000, unit: "SF", unit_cost: 16, total_cost: 2880000 },
          { name: "Generator Paralleling + ATS Matrix", quantity: 180000, unit: "SF", unit_cost: 15, total_cost: 2700000 },
          { name: "Imaging + OR Power Conditioning", quantity: 180000, unit: "SF", unit_cost: 13, total_cost: 2340000 },
        ],
      },
    ];
    project.analysis.calculations.construction_costs.special_features_total = 900000;
    project.analysis.calculations.construction_costs.special_features_breakdown = [
      {
        id: "negative_pressure_isolation",
        label: "Negative Pressure Isolation Rooms",
        cost_per_sf: 2.5,
        total_cost: 450000,
      },
      {
        id: "nurse_call_system_upgrade",
        label: "Advanced Nurse Call System",
        cost_per_sf: 2.5,
        total_cost: 450000,
      },
    ];

    render(<ConstructionView project={project} />);

    expect(screen.getByText("Subtype schedule")).toBeInTheDocument();
    expect(screen.getByText("Special Features")).toBeInTheDocument();
    expect(screen.getByText("Negative Pressure Isolation Rooms")).toBeInTheDocument();
    expect(screen.getByText("Advanced Nurse Call System")).toBeInTheDocument();
    expect(
      screen.queryByText("Per-feature breakdown is unavailable for this project version; showing aggregate total only.")
    ).not.toBeInTheDocument();

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    openTradeCard("Mechanical");
    expect(screen.getByText("5 systems")).toBeInTheDocument();
    expect(screen.getByText("Air-Handling Units + Filtration")).toBeInTheDocument();
    expect(screen.getByText("Medical Exhaust + Isolation Controls")).toBeInTheDocument();
    expect(screen.getByText("Smoke Control + Stair Pressurization")).toBeInTheDocument();

    openTradeCard("Electrical");
    expect(screen.getByText("5 systems")).toBeInTheDocument();
    expect(screen.getByText("Redundant Switchgear + UPS")).toBeInTheDocument();
    expect(screen.getByText("Nurse Call + Low Voltage Backbone")).toBeInTheDocument();
    expect(screen.getByText("Imaging + OR Power Conditioning")).toBeInTheDocument();
  });

  it("keeps per-feature special-feature breakdown visible for imaging, urgent care, and medical-office subtype fixtures", () => {
    const cases = [
      {
        subtype: "imaging_center" as const,
        breakdown: [
          { id: "mri_suite", label: "MRI Suite Upgrade", cost_per_sf: 3.5, total_cost: 175000 },
          { id: "ct_suite", label: "CT Suite Buildout", cost_per_sf: 2.5, total_cost: 125000 },
        ],
      },
      {
        subtype: "urgent_care" as const,
        breakdown: [
          { id: "laboratory", label: "On-Site Lab Expansion", cost_per_sf: 2.0, total_cost: 100000 },
          { id: "imaging_suite", label: "Fast-Track Imaging Pod", cost_per_sf: 1.8, total_cost: 90000 },
        ],
      },
      {
        subtype: "medical_office_building" as const,
        breakdown: [
          { id: "ambulatory_buildout", label: "Ambulatory Buildout Program", cost_per_sf: 2.6, total_cost: 130000 },
          { id: "infusion_suite", label: "Infusion Suite Shell Prep", cost_per_sf: 1.4, total_cost: 70000 },
        ],
      },
    ];

    const { rerender } = render(
      <ConstructionView
        project={buildHealthcareScheduleProject(cases[0].subtype, "subtype")}
      />
    );

    for (const fixture of cases) {
      const project = buildHealthcareScheduleProject(fixture.subtype, "subtype");
      project.analysis.calculations.construction_costs.special_features_total = fixture.breakdown.reduce(
        (sum, item) => sum + item.total_cost,
        0
      );
      project.analysis.calculations.construction_costs.special_features_breakdown = fixture.breakdown;

      rerender(<ConstructionView project={project} />);

      expect(screen.getByText("Special Features")).toBeInTheDocument();
      for (const row of fixture.breakdown) {
        expect(screen.getByText(row.label)).toBeInTheDocument();
      }
      expect(
        screen.queryByText("Per-feature breakdown is unavailable for this project version; showing aggregate total only.")
      ).not.toBeInTheDocument();
    }
  });

  it("renders deeper mechanical/electrical/plumbing system depth for surgical and imaging subtype paths", () => {
    const cases = [
      {
        subtype: "surgical_center",
        mechanicalName: "OR AHUs + Pressure Cascade Controls",
        electricalName: "Isolated Power Panels + UPS",
        plumbingName: "Medical Gas Backbone + Zone Valves",
      },
      {
        subtype: "imaging_center",
        mechanicalName: "MRI Quench + Relief Air Path",
        electricalName: "Power Quality Filtering + Harmonic Mitigation",
        plumbingName: "Shielded-Room Drainage + Process Cooling Isolation",
      },
    ] as const;

    const { rerender } = render(
      <ConstructionView
        project={buildHealthcareScheduleProject(cases[0].subtype, "subtype")}
      />
    );

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    for (const testCase of cases) {
      const project = buildHealthcareScheduleProject(testCase.subtype, "subtype");
      project.analysis.calculations.trade_breakdown = {
        structural: 3600000,
        mechanical: 5200000,
        electrical: 4900000,
        plumbing: 2800000,
        finishes: 2600000,
      };
      project.analysis.calculations.scope_items = [
        {
          trade: "mechanical",
          systems: [
            { name: testCase.mechanicalName, quantity: 120000, unit: "SF", unit_cost: 31, total_cost: 3720000 },
            { name: "Dedicated Airside Distribution", quantity: 120000, unit: "SF", unit_cost: 24, total_cost: 2880000 },
            { name: "Temperature/Humidity Controls", quantity: 120000, unit: "SF", unit_cost: 21, total_cost: 2520000 },
            { name: "Procedure Exhaust + Heat Recovery", quantity: 120000, unit: "SF", unit_cost: 18, total_cost: 2160000 },
          ],
        },
        {
          trade: "electrical",
          systems: [
            { name: testCase.electricalName, quantity: 120000, unit: "SF", unit_cost: 29, total_cost: 3480000 },
            { name: "Dedicated Modality/Procedure Distribution", quantity: 120000, unit: "SF", unit_cost: 24, total_cost: 2880000 },
            { name: "Clinical Lighting + Controls", quantity: 120000, unit: "SF", unit_cost: 20, total_cost: 2400000 },
            { name: "Low Voltage + Monitoring Backbone", quantity: 120000, unit: "SF", unit_cost: 17, total_cost: 2040000 },
          ],
        },
        {
          trade: "plumbing",
          systems: [
            { name: testCase.plumbingName, quantity: 120000, unit: "SF", unit_cost: 22, total_cost: 2640000 },
            { name: "Domestic + Sanitary Distribution", quantity: 120000, unit: "SF", unit_cost: 17, total_cost: 2040000 },
            { name: "Fixture Group Rough-In", quantity: 120000, unit: "SF", unit_cost: 13, total_cost: 1560000 },
            { name: "Special Waste + Pretreatment", quantity: 120000, unit: "SF", unit_cost: 11, total_cost: 1320000 },
          ],
        },
      ];

      rerender(<ConstructionView project={project} />);

      openTradeCard("Mechanical");
      expect(screen.getByText("4 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.mechanicalName)).toBeInTheDocument();

      openTradeCard("Electrical");
      expect(screen.getByText("4 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.electricalName)).toBeInTheDocument();

      openTradeCard("Plumbing");
      expect(screen.getByText("4 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.plumbingName)).toBeInTheDocument();
    }
  });

  it("renders educational trade scope depth as subtype-specific and non-generic for all five subtypes", () => {
    const cases = [
      {
        subtype: "elementary_school" as const,
        structuralName: "Elementary Classroom Wing Framing",
        mechanicalName: "Elementary Classroom HVAC Zoning",
        electricalName: "Elementary Life-Safety + Classroom Power",
        plumbingName: "Elementary Restroom + Drinking Station Network",
        finishesName: "Elementary Corridor Acoustics + Durable Finishes",
      },
      {
        subtype: "middle_school" as const,
        structuralName: "Middle School STEM Wing Structural Grid",
        mechanicalName: "Middle School Lab Ventilation Controls",
        electricalName: "Middle School Lab Power + AV Distribution",
        plumbingName: "Middle School Science-Lab Plumbing Branches",
        finishesName: "Middle School Commons + Wayfinding Finishes",
      },
      {
        subtype: "high_school" as const,
        structuralName: "High School Fieldhouse + Arts Core Framing",
        mechanicalName: "High School Gym + Auditorium Air Systems",
        electricalName: "High School Event Lighting + Sound Power",
        plumbingName: "High School Locker + Culinary Lab Plumbing",
        finishesName: "High School Academic + Athletic Finish Package",
      },
      {
        subtype: "university" as const,
        structuralName: "University Research Podium + Core Framing",
        mechanicalName: "University Research Lab Exhaust + Controls",
        electricalName: "University Research Redundant Power Backbone",
        plumbingName: "University Wet-Lab + Process Waste Systems",
        finishesName: "University Lecture Hall + Lab Support Finishes",
      },
      {
        subtype: "community_college" as const,
        structuralName: "Community College Workforce Lab Bay Framing",
        mechanicalName: "Community College Trade-Shop Ventilation",
        electricalName: "Community College Shop Power + Safety Interlocks",
        plumbingName: "Community College Skills Lab Plumbing Backbone",
        finishesName: "Community College Flexible Classroom Finishes",
      },
    ];

    const { rerender } = render(
      <ConstructionView project={buildEducationalScheduleProject(cases[0].subtype, "subtype")} />
    );

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    for (const testCase of cases) {
      const project = buildEducationalScheduleProject(testCase.subtype, "subtype");
      project.analysis.calculations.trade_breakdown = {
        structural: 3900000,
        mechanical: 4100000,
        electrical: 3600000,
        plumbing: 2700000,
        finishes: 3300000,
      };
      project.analysis.calculations.scope_items = [
        {
          trade: "structural",
          systems: [
            { name: testCase.structuralName, quantity: 120000, unit: "SF", unit_cost: 24, total_cost: 2880000 },
            { name: "Structural Shear + Lateral Reinforcement", quantity: 120000, unit: "SF", unit_cost: 18, total_cost: 2160000 },
            { name: "Envelope Support + Stair Core Framing", quantity: 120000, unit: "SF", unit_cost: 16, total_cost: 1920000 },
          ],
        },
        {
          trade: "mechanical",
          systems: [
            { name: testCase.mechanicalName, quantity: 120000, unit: "SF", unit_cost: 25, total_cost: 3000000 },
            { name: "Dedicated Outside Air + Balancing", quantity: 120000, unit: "SF", unit_cost: 20, total_cost: 2400000 },
            { name: "Commissioning + Controls Integration", quantity: 120000, unit: "SF", unit_cost: 15, total_cost: 1800000 },
          ],
        },
        {
          trade: "electrical",
          systems: [
            { name: testCase.electricalName, quantity: 120000, unit: "SF", unit_cost: 23, total_cost: 2760000 },
            { name: "Switchgear + Distribution Panels", quantity: 120000, unit: "SF", unit_cost: 19, total_cost: 2280000 },
            { name: "Fire Alarm + Data Backbone", quantity: 120000, unit: "SF", unit_cost: 14, total_cost: 1680000 },
          ],
        },
        {
          trade: "plumbing",
          systems: [
            { name: testCase.plumbingName, quantity: 120000, unit: "SF", unit_cost: 18, total_cost: 2160000 },
            { name: "Domestic Water + Sanitary Routing", quantity: 120000, unit: "SF", unit_cost: 14, total_cost: 1680000 },
            { name: "Fixture Group Rough-In + Final Trim", quantity: 120000, unit: "SF", unit_cost: 10, total_cost: 1200000 },
          ],
        },
        {
          trade: "finishes",
          systems: [
            { name: testCase.finishesName, quantity: 120000, unit: "SF", unit_cost: 20, total_cost: 2400000 },
            { name: "Interior Doors + Hardware Program", quantity: 120000, unit: "SF", unit_cost: 15, total_cost: 1800000 },
            { name: "Flooring + Ceiling + Wall Finish Scope", quantity: 120000, unit: "SF", unit_cost: 12, total_cost: 1440000 },
          ],
        },
      ];

      rerender(<ConstructionView project={project} />);

      expect(screen.getByText("Subtype schedule")).toBeInTheDocument();

      openTradeCard("Structural");
      expect(screen.getByText("3 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.structuralName)).toBeInTheDocument();

      openTradeCard("Mechanical");
      expect(screen.getByText("3 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.mechanicalName)).toBeInTheDocument();

      openTradeCard("Electrical");
      expect(screen.getByText("3 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.electricalName)).toBeInTheDocument();

      openTradeCard("Plumbing");
      expect(screen.getByText("3 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.plumbingName)).toBeInTheDocument();

      openTradeCard("Finishes");
      expect(screen.getByText("3 systems")).toBeInTheDocument();
      expect(screen.getByText(testCase.finishesName)).toBeInTheDocument();
    }
  });

  it("renders expanded data-center scope detail for dominant mechanical and electrical trades", () => {
    render(
      <ConstructionView
        project={buildSpecialtyScheduleProject("data_center", "subtype")}
      />
    );

    const openTradeCard = (tradeName: string) => {
      const tradeHeading = screen.getByText(tradeName, { selector: "h4" });
      const tradeCard = tradeHeading.closest('[role="button"]');
      expect(tradeCard).not.toBeNull();
      fireEvent.click(tradeCard as HTMLElement);
    };

    openTradeCard("Mechanical");
    expect(screen.getByText("5 systems")).toBeInTheDocument();
    expect(screen.getByText("CRAH Units + Hot Aisle Return")).toBeInTheDocument();
    expect(screen.getByText("Economizer Relief + Airside Controls")).toBeInTheDocument();
    expect(screen.getAllByRole("row").length).toBeGreaterThanOrEqual(6);

    openTradeCard("Electrical");
    expect(screen.getByText("5 systems")).toBeInTheDocument();
    expect(screen.getByText("Busway + Rack Power Taps")).toBeInTheDocument();
    expect(screen.getByText("Branch Circuit Monitoring + BMS Points")).toBeInTheDocument();
    expect(screen.getAllByRole("row").length).toBeGreaterThanOrEqual(6);
  });
});
