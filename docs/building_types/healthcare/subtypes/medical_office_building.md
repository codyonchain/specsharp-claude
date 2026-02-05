# Subtype: Medical Office Building (Healthcare)

## Block A - Decision & KPIs (DealShield front door)
DealShield is the decision insurance front door. ExecutiveView and ConstructionView are the proof appendices. Every statement below maps to deterministic drivers (config fields, profiles, or explicit inputs).

### Investment decision (Go / Reprice / Rescope / Walk)
- Go: Cost, schedule, and yield gates pass with baseline outpatient assumptions and no unmodeled imaging/procedure scope.
- Reprice: Base cost, regional multipliers, or special feature adders are updated and gates are re-evaluated.
- Rescope: TI intensity, clinical program, or MEP upgrades are clarified and re-run against the same gates.
- Walk: Deterministic downside (cost +10% and revenue -10%) fails DSCR/yield gates with no credible driver fix.

### KPI mapping to views (deterministic sources)
- Total cost ($ and $/SF): ConstructionView totals from `construction_costs`, `soft_costs`, and `total_project_cost`.
- Schedule and milestones: Timeline profile from `backend/app/v2/config/type_profiles/project_timelines/healthcare.py` (ground_up) or deterministic fallback.
- Underwriting gates (yield/DSCR): ExecutiveView `ownership_analysis` using `backend/app/v2/config/type_profiles/healthcare.py` targets.
- Revenue proxy (modeled): ExecutiveView `revenue_analysis` using subtype `base_revenue_per_sf_annual`, occupancy defaults, and `operating_margin_base`.

### DealShield tiles (deterministic)
- Tile 1: Cost +10% (required, from `sensitivity_analysis.cost_up_10`).
- Tile 2: Revenue -10% (required, from `sensitivity_analysis.revenue_down_10`).
- Tile 3 (MOB driver): Imaging/procedure adders only when explicit `special_features` are selected (for example `ambulatory_imaging`, `mob_procedure_suite`, `mob_imaging_ready_shell`). If no explicit driver input exists, this tile is hidden until modeled.

### Conservative / Ugly rules
- Conservative: Apply Cost +10% and Revenue -10% together (derived from required tiles; no new numbers).
- Ugly: Conservative plus the MOB driver tile when it is present (derived; otherwise equals Conservative).

### Confidence band (driver-tied, no fabricated %)
- Clinical program clarity tightens confidence; ambiguous imaging/procedure scope widens it.
- TI intensity and finish level clarity tighten confidence; generic office assumptions widen it.
- Structural loading and span assumptions widen confidence when imaging shielding or heavy equipment is possible.
- MEP upgrade requirements (air changes, filtration, power redundancy) widen confidence when unspecified.
- Parking/covered drop-off scope widens confidence because it is not a separate trade and must be explicit.
- Schedule acceleration requests widen confidence when overriding the healthcare ground_up timeline.
- Regional multiplier inputs tighten confidence when city/state is explicit; defaults widen it.

### Risk exposure + notes (failure modes tied to drivers)
- Imaging/procedure scope understated: mechanical, electrical, and structural allowances break and costs move materially.
- TI intensity understated: finishes and MEP are compressed relative to outpatient expectations.
- Power and backup requirements understated: electrical scope and operating assumptions fail.
- Medical gas or specialty plumbing required: plumbing scope changes outside baseline MOB assumptions.
- Covered drop-off or canopy not scoped: structural and envelope allowances are short.
- Parking structure or major sitework assumed: not modeled as a trade and must be explicit.
- Schedule forced shorter than profile: contingency and sequencing risk increases.

### Provenance pointers (config paths + profile keys)
- Subtype config: `backend/app/v2/config/subtypes/healthcare/medical_office_building.py`.
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/healthcare.py` -> `healthcare_medical_office_building_structural_v1`.
- Type profile (yield/DSCR gates): `backend/app/v2/config/type_profiles/healthcare.py`.
- Margin profile: `backend/app/v2/config/type_profiles/margins/healthcare.py`.
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/healthcare.py`.
- Finish level factors: `backend/app/v2/config/master_config.py` (`FINISH_LEVELS`, `get_finish_cost_factor`).

## Block B - ConstructionView Trade Summary (Critical)
ConstructionView for a Medical Office Building shows these trades: Structural, Mechanical, Electrical, Plumbing, Finishes. Architectural/envelope structural allowances are embedded in Structural. Site/Civil is not modeled as a separate trade for this subtype.

### Structural
Included scope:
- Foundations, slab, and footings via `foundations_slab_footings`.
- Structural frame (steel/wood) via `structural_frame`.
- Roof structure and deck via `roof_structure_deck`.
- Exterior envelope structural allowances via `exterior_envelope_structural_allowance`.
- Misc. structural, stairs, and supports via `misc_stairs_supports`.
Excluded scope:
- Major sitework, grading, and utilities (not a modeled trade).
- Parking structures or below-grade parking.
- Imaging shielding foundations or heavy equipment pits beyond baseline.
Adders mapping:
- `special_features` adders (for example `mob_covered_dropoff`, `mob_imaging_ready_shell`) raise total cost when selected; trade attribution is handled downstream and is not explicitly modeled in the structural scope items.
Deterministic drivers:
- `healthcare_medical_office_building_structural_v1` scope items profile.
- Total SF and the subtype trade breakdown percentages.
Validation questions:
- Any heavy imaging/procedure rooms requiring structural reinforcement?
- Any covered drop-off or canopy scope that must be explicit?

### Mechanical
Included scope:
- Baseline outpatient HVAC equipment and distribution sized to total SF.
- Ventilation and exhaust for typical medical office use.
- Controls and zoning consistent with standard MOB layouts.
Excluded scope:
- Surgical-grade air change rates or specialty isolation requirements.
- Imaging equipment cooling loads or dedicated central plant.
- Laboratory exhaust or process HVAC.
Adders mapping:
- `special_features` like `mob_enhanced_mep`, `ambulatory_imaging`, or `mob_procedure_suite` add to total project cost when selected.
Deterministic drivers:
- Subtype trade breakdown percentages and total SF.
- Selected `special_features` inputs.
Validation questions:
- Any imaging/procedure suites requiring enhanced HVAC or redundancy?
- Any central plant or specialty ventilation requirements?

### Electrical
Included scope:
- Baseline electrical service, distribution, and panels for MOB office use.
- General lighting and receptacle power for tenant suites and common areas.
- Low-voltage allowances consistent with baseline MOB assumptions.
Excluded scope:
- Imaging equipment power, UPS, or generator capacity beyond baseline.
- Specialty nurse call, surgical, or lab power systems.
Adders mapping:
- `special_features` like `ambulatory_imaging` or `mob_procedure_suite` add to total project cost when selected.
Deterministic drivers:
- Subtype trade breakdown percentages and total SF.
- Selected `special_features` inputs.
Validation questions:
- Is imaging equipment or elevated power density required?
- Is emergency power or UPS expected beyond baseline?

### Plumbing
Included scope:
- Domestic water and sanitary systems for outpatient office use.
- Restroom groups sized to tenant and visitor counts.
- Standard storm drainage and roof drains.
Excluded scope:
- Medical gas systems, sterilization, or specialty waste.
- Procedure-grade plumbing beyond baseline outpatient assumptions.
Adders mapping:
- `special_features` like `mob_procedure_suite` add to total project cost when selected.
Deterministic drivers:
- Subtype trade breakdown percentages and total SF.
- Selected `special_features` inputs.
Validation questions:
- Any medical gas or specialty plumbing requirements?
- Do restroom counts or clinical suite counts differ from baseline?

### Finishes
Included scope:
- Tenant suite buildout (partitions, ceilings, flooring) at baseline finish level.
- Common area finishes for MOB lobbies and corridors.
- Casework and millwork allowances consistent with outpatient office use.
Excluded scope:
- Premium clinical finishes or lead-lined imaging rooms.
- High-end hospitality-grade lobbies beyond baseline finish level.
Adders mapping:
- `special_features` like `tenant_improvements`, `ambulatory_buildout`, or `mob_pharmacy_shell` add to total project cost when selected.
Deterministic drivers:
- Finish level multiplier from `master_config.py`.
- Selected `special_features` inputs.
Validation questions:
- What finish level is expected for tenant suites and lobby?
- Are any suites built to imaging/procedure standards?

### Trade Distribution %
- Percentages must come from deterministic `calculations.trade_breakdown`; never fabricate.

### Construction schedule + milestones
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/healthcare.py` (ground_up) unless project class lacks a profile, in which case the deterministic default timeline is used.
- Milestones (as configured): Design & Licensing (offset_months 0), Shell & MEP Rough-In (offset_months 4), Interior Buildout & Finishes (offset_months 8), Equipment & Low Voltage (offset_months 12), Soft Opening & Ramp-Up (offset_months 16).

## Block C - ExecutiveView checklist (deterministic vs input)
- Investment Decision: Deterministic from ownership analysis and decision gates (yield/DSCR).
- Revenue projections: Deterministic from `base_revenue_per_sf_annual`, occupancy defaults, and operating margins.
- Facility metrics: Deterministic when `facility_metrics_profile = healthcare_outpatient` is resolved.
- Prescriptive playbook (driver-tied next steps): Input required; only show actions tied to confirmed drivers.
- Feasibility vs target yield: Deterministic using `target_yield` in `backend/app/v2/config/type_profiles/healthcare.py`.
- Major soft costs: Deterministic from subtype `soft_costs` config.
- Key financial indicators: Deterministic from `ownership_analysis` and `revenue_analysis` outputs.
- Market position (user comps only): Input required.
- Quick sensitivity: Deterministic from `sensitivity_analysis` (cost +/-10%, revenue +/-10%).
- Key milestones: Deterministic from the healthcare timeline profile.
- Financing structure: Deterministic from subtype financing terms.
- Operational efficiency: Deterministic from `operating_margin_base` and `operating_margin_premium` defaults.
- Executive decision points: Deterministic; if yield or DSCR gates fail, recommendation shifts to rescope/reprice/walk.
- Footer: Deterministic summary with provenance, determinism tags, and explicit list of inputs that would change the answer.

## Block D - Assumptions & Question Bank

### Ranked assumptions (5-7)
1. Structural scope assumes standard outpatient loads without imaging shielding or heavy equipment pits. Impacts Structural; shows in ConstructionView.
2. TI intensity is baseline for MOB tenant suites and common areas. Impacts Finishes and MEP; shows in ConstructionView and DealShield driver tile when selected.
3. No procedure-grade HVAC or specialty ventilation beyond baseline outpatient standards. Impacts Mechanical; shows in ConstructionView and risk notes.
4. Electrical service is baseline office-grade with no imaging or backup power upgrades. Impacts Electrical; shows in ConstructionView.
5. Plumbing scope excludes medical gas and specialty waste systems. Impacts Plumbing; shows in ConstructionView and risk notes.
6. Covered drop-off or canopy scope is only included when explicitly selected. Impacts Structural and Finishes; shows via `special_features` adders.

### Most likely wrong (top 3)
- Imaging/procedure suite scope is understated, shifting MEP and structural requirements.
- Tenant improvement intensity is understated, compressing finishes and MEP scope.
- Power and backup requirements are higher than baseline assumptions.

### Question bank (8-12)
1. Are imaging or procedure suites included? Driver: `special_features` (`ambulatory_imaging`, `mob_procedure_suite`, `mob_imaging_ready_shell`). Changes: Mechanical, Electrical, Structural, Finishes. Shows: ConstructionView trades and DealShield driver tile.
2. What is the expected TI intensity for suites and common areas? Driver: finish level and `special_features` (`tenant_improvements`, `ambulatory_buildout`). Changes: Finishes and total cost. Shows: ConstructionView Finishes and sensitivity tiles.
3. Any covered drop-off or canopy scope? Driver: `special_features` (`mob_covered_dropoff`). Changes: Structural and envelope allowances. Shows: ConstructionView Structural.
4. Any pharmacy shell or specialty tenant suite shells? Driver: `special_features` (`mob_pharmacy_shell`). Changes: Finishes and MEP. Shows: ConstructionView Finishes and MEP trades.
5. Is emergency power or UPS required beyond baseline? Driver: explicit power requirements. Changes: Electrical scope and operating assumptions. Shows: ConstructionView Electrical and ExecutiveView risk notes.
6. Are medical gas, sterilization, or specialty waste systems required? Driver: clinical program input. Changes: Plumbing scope. Shows: ConstructionView Plumbing and risk notes.
7. Are structural loading or vibration criteria above baseline? Driver: imaging equipment loads. Changes: Structural scope and schedule. Shows: ConstructionView Structural.
8. Is the project schedule fixed or accelerated? Driver: timeline override. Changes: schedule and contingency posture. Shows: ConstructionView schedule and DealShield risk.
9. Are parking structures or major sitework in scope? Driver: explicit site scope. Changes: total cost outside modeled trades. Shows: DealShield risk and provenance notes.

### Red-flag -> action table
| Trigger | Why it matters | What to ask | What to change |
| --- | --- | --- | --- |
| Imaging/procedure suites added late | MEP and structural scope jump | Confirm suite count and equipment list | Select imaging/procedure `special_features` and re-run |
| TI intensity above baseline | Finishes and MEP costs rise | Confirm finish level and TI scope | Apply finish level and TI adders |
| Power redundancy required | Electrical scope and ops assumptions shift | Confirm generator/UPS requirements | Add explicit power scope and re-run |
| Medical gas required | Plumbing scope changes materially | Confirm gas types and counts | Add clinical plumbing scope or rescope subtype |
| Covered drop-off included | Structural and envelope allowances rise | Confirm canopy scope and size | Add `mob_covered_dropoff` and re-run |

### Negotiation levers (3-5)
- Limit imaging/procedure suite count: Driver `special_features`. Moves the needle by reducing MEP and structural adders.
- Right-size TI intensity: Driver finish level and `tenant_improvements`. Moves the needle by shrinking finishes and MEP scope.
- Defer covered drop-off scope: Driver `mob_covered_dropoff`. Moves the needle by reducing structural/envelope allowances.
- Standardize clinical suite specs: Driver `ambulatory_buildout`. Moves the needle by avoiding premium finish/MEP assumptions.
- Keep power baseline unless required: Driver explicit power upgrades. Moves the needle by avoiding electrical adders.
