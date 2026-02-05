# Subtype: Urgent Care (Healthcare)

## Block A - Decision & KPIs (Decision Insurance)
DealShield is the decision insurance front door. ExecutiveView and ConstructionView are the proof appendices. Every statement below maps to deterministic drivers (config fields, profiles, or explicit inputs).

### Primary decision moment (VP Dev / Fund Partner)
Make a go/no-go call on an urgent care clinic based on deterministic all-in cost, schedule, and visit-volume economics. If cost or yield gates fail, decide whether to rescope clinical program (exam rooms, imaging/lab, observation bays), reprice, or walk before DD.

### What success looks like
- Greenlight: Cost, schedule, and yield gates pass with a clear driver story.
- Rescope: Exam room count, imaging/lab scope, or observation bays are corrected and re-run.
- Reprice: Base cost or regional factors are adjusted, then decision gates re-evaluated.
- Walk: Deterministic downside (cost +10% and revenue -10%) fails DSCR/yield gates with no credible driver fix.

### KPI outputs (and deterministic sources)
- All-in cost ($ and $/SF): ConstructionView totals from `construction_costs`, `soft_costs`, and `total_project_cost`.
- Schedule and milestones: Timeline profile from `backend/app/v2/config/type_profiles/project_timelines/healthcare.py` (ground_up) or deterministic fallback if project class lacks a profile.
- Revenue proxy (modeled): ExecutiveView `revenue_analysis` using `base_revenue_per_sf_annual`, `base_revenue_per_visit`, `visits_per_day`, `days_per_year`, occupancy defaults, and `operating_margin_base`.
- Unit economics: `financial_metrics` per exam room using `units_per_sf` and `revenue_per_unit_annual`.
- Downside deltas: DealShield tiles sourced from deterministic `sensitivity_analysis` (cost +/-10%, revenue +/-10%).

### Deterministic drivers for this subtype
- Exam room count derived from `financial_metrics.units_per_sf` unless explicit room count inputs are provided.
- Visit volume and revenue per visit from subtype defaults (`visits_per_day`, `days_per_year`, `base_revenue_per_visit`).
- Special feature adders only when explicitly provided: `trauma_room`, `x_ray`, `laboratory`, `pharmacy`, `hc_urgent_on_site_lab`, `hc_urgent_imaging_suite`, `hc_urgent_observation_bays`.

### DealShield tiles (deterministic)
- Tile 1: Cost +10% (required, from `sensitivity_analysis.cost_up_10`).
- Tile 2: Revenue -10% (required, from `sensitivity_analysis.revenue_down_10`).
- Tile 3 (subtype driver): Imaging/Lab/Observation intensity when explicit input exists for `hc_urgent_imaging_suite`, `hc_urgent_on_site_lab`, `x_ray`, `laboratory`, or `hc_urgent_observation_bays`. If no explicit input is present, hide this tile (do not infer).

### Conservative / Ugly rows
- Conservative: Apply Cost +10% and Revenue -10% together (derived from the two required tiles; no new numbers).
- Ugly: Conservative plus the driver tile when present (derived; no new numbers). If no driver tile is present, Ugly equals Conservative.

### Confidence band (driver-tied, no fabricated %)
- Exam room count uncertainty widens confidence when program is inferred from SF rather than explicitly provided.
- Visit volume uncertainty widens confidence when `visits_per_day` or `days_per_year` are not overridden.
- Imaging or on-site lab scope uncertainty widens confidence unless explicit special feature inputs exist.
- Observation bay requirement uncertainty widens confidence unless `hc_urgent_observation_bays` is confirmed.
- Clinical finish level uncertainty widens confidence because finish multipliers are global defaults unless overridden.
- Infection control requirements (negative pressure, enhanced filtration) widen confidence unless explicit MEP upgrades are provided.
- Operating hours assumption (365 days/year default) widens confidence when the clinic is not truly 7-day.

If the platform emits an explicit confidence score/label, show it; otherwise keep the band qualitative and driver-tied as above.

### Risk exposure + notes (failure modes tied to drivers)
- Imaging suite required but not input: electrical and mechanical scope understates load and cooling.
- On-site lab needs higher ventilation and plumbing: lab exhaust and wet utilities are not modeled without explicit input.
- Observation bays or trauma room included late: increases clinical finishes and MEP intensity beyond baseline.
- Infection control upgrades (negative pressure/isolation) missing: mechanical scope and schedule risk rise.
- Emergency power or generator requirements omitted: electrical scope and equipment costs understate.
- 24/7 operations assumed incorrectly: revenue, labor, and utility ratios misstate NOI.
- Heavy equipment loads (imaging) exceed slab assumptions: structural scope and schedule risk rise.

### Provenance report (deterministic pointers)
- Subtype config: `backend/app/v2/config/subtypes/healthcare/urgent_care.py`.
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/healthcare.py` -> `healthcare_urgent_care_structural_v1`.
- Type profile (yield/DSCR gates): `backend/app/v2/config/type_profiles/healthcare.py`.
- Margin profile: `backend/app/v2/config/type_profiles/margins/healthcare.py`.
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/healthcare.py`.
- Finish level factors: `backend/app/v2/config/master_config.py` (`FINISH_LEVELS`, `get_finish_cost_factor`).

## Block B - ConstructionView: Trade Summary & Scope Items (Critical Trust Layer)
ConstructionView for urgent care shows these trades: Structural, Mechanical, Electrical, Plumbing, Finishes. Site/Civil is not modeled as a separate trade for this subtype.

### Structural
- Included scope: Slab on grade, foundations/footings, structural framing, exterior wall envelope, and roof structure via `healthcare_urgent_care_structural_v1`.
- Common exclude: Major sitework, grading, and utilities (not a modeled trade).
- Common exclude: Specialized slab reinforcement for heavy imaging equipment unless explicitly added.
- Special features/equipment mapping: Imaging/lab equipment adders live in subtype `special_features`, not in the structural profile.
- Primary deterministic drivers: `healthcare_urgent_care_structural_v1` scope items and total SF.
- How to validate fast: Confirm single-story shell assumptions and any heavy equipment loads.

### Mechanical
- Included scope: Baseline outpatient HVAC and ventilation intensity implied by trade breakdown and total SF.
- Common exclude: Negative pressure isolation rooms or dedicated lab exhaust unless explicitly specified.
- Common exclude: Specialty imaging HVAC (heat rejection or chilled water) without explicit inputs.
- Infection control considerations: Enhanced filtration, pressure relationships, and air change rates are not modeled unless explicitly provided.
- Special features/equipment mapping: Imaging suite or on-site lab adders must be explicit; otherwise mechanical scope remains baseline.
- Primary deterministic drivers: Mechanical trade share, total SF, and any explicit special feature inputs.
- How to validate fast: Confirm required air change rates, filtration level, and any lab or imaging HVAC loads.

### Electrical
- Included scope: Baseline clinic power distribution and lighting implied by trade breakdown and total SF.
- Common exclude: Emergency power/generator systems unless explicitly specified.
- Common exclude: Imaging equipment power and dedicated panels unless explicit inputs exist.
- Infection control considerations: Any required redundant power or monitoring systems must be explicit inputs.
- Special features/equipment mapping: `x_ray` or `hc_urgent_imaging_suite` adders only apply with explicit input.
- Primary deterministic drivers: Electrical trade share, total SF, and special feature inputs.
- How to validate fast: Confirm imaging loads, emergency power requirements, and low-voltage scope.

### Plumbing
- Included scope: Baseline clinic plumbing implied by trade breakdown and total SF.
- Common exclude: Lab waste, process plumbing, or specialty sinks unless explicitly specified.
- Common exclude: Medical gas systems unless explicitly provided.
- Infection control considerations: Handwash sink density and isolation plumbing need explicit program inputs.
- Special features/equipment mapping: Lab or trauma room adders must be explicit; otherwise plumbing scope remains baseline.
- Primary deterministic drivers: Plumbing trade share, total SF, and special feature inputs.
- How to validate fast: Confirm lab plumbing, med gas, and any procedure room requirements.

### Finishes
- Included scope: Standard clinical finishes implied by trade breakdown and finish level multipliers.
- Common exclude: Premium clinical finishes (seamless resin floors, high-end wall protection) unless finish level is overridden.
- Common exclude: Specialized shielding or lead-lined rooms (imaging) unless explicitly specified.
- Infection control considerations: Cleanable surfaces and upgraded wall protection are not modeled without explicit finish level or scope inputs.
- Special features/equipment mapping: Imaging/lab room finish upgrades require explicit inputs.
- Primary deterministic drivers: Finishes trade share, total SF, and finish level multiplier.
- How to validate fast: Confirm finish level target and any imaging or lab room finish requirements.

### Trade distribution % rule
- Percentages must come from deterministic trade totals in `calculations.trade_breakdown`; never fabricate.

### Construction schedule + key milestones
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/healthcare.py` (ground_up) unless project class lacks a profile, in which case the deterministic default timeline is used.
- Milestones (as configured): Design & Licensing (offset_months 0), Shell & MEP Rough-In (offset_months 4), Interior Buildout & Finishes (offset_months 8), Equipment & Low Voltage (offset_months 12), Soft Opening & Ramp-Up (offset_months 16).

## Block C - ExecutiveView: Decision Appendix Checklist
- Investment Decision: Deterministic from ownership analysis and decision gates (yield/DSCR).
- Revenue projections (visit-based): Deterministic from `base_revenue_per_sf_annual`, `base_revenue_per_visit`, `visits_per_day`, `days_per_year`, occupancy, and margin defaults.
- Facility metrics: Deterministic from facility metrics profile `healthcare_outpatient`.
- Prescriptive playbook: Input required; only show actions tied to confirmed drivers (exam rooms, imaging/lab, schedule overrides).
- Feasibility vs target yield: Deterministic using `target_yield` from the healthcare type profile and computed yield on cost.
- Major soft cost categories: Deterministic from subtype `soft_costs` config.
- Key financial indicators (DSCR/yield/NOI/etc): Deterministic from `ownership_analysis` and `revenue_analysis` outputs.
- Market position: Input required (comps or operator pipeline); do not infer.
- Quick sensitivity: Deterministic from `sensitivity_analysis` (cost +/-10%, revenue +/-10%).
- Key milestones: Deterministic from the healthcare timeline profile and aligned to ConstructionView milestones.
- Financing structure: Deterministic from subtype financing terms (debt/equity, rate, DSCR target, ROI target).
- Operational efficiency: Deterministic from operating ratios in subtype config (labor, supply, management fee, insurance, utilities, maintenance, marketing).
- Executive decision points: Deterministic; if yield or DSCR gates fail, the recommendation shifts to rescope/reprice/walk.
- Footer: Deterministic; must state determinism, provenance, and what inputs would change the answer.

## Block D - Assumptions & Question Bank (Subtype-local, ranked and mapped)

### Ranked assumptions (5-7)
1. Exam room count follows `financial_metrics.units_per_sf` unless explicitly provided; impacts revenue and staffing assumptions.
2. Visit volume follows `visits_per_day` and `days_per_year` defaults; impacts revenue and labor ratios.
3. Imaging, on-site lab, trauma room, and observation bays are zero unless explicit special feature inputs are provided.
4. Clinical finishes align to baseline finish level multipliers; premium clinical finishes are not included unless overridden.
5. Mechanical systems are baseline outpatient (no negative pressure/isolation) unless explicit MEP upgrades are provided.
6. Structural profile assumes a single-story clinic and baseline slab loads; heavy imaging loads are not included unless specified.

### Most likely wrong (top 3)
- Imaging/lab scope is required but not explicitly input, understating MEP and finishes.
- Operating hours and visit volume differ materially from defaults, shifting revenue and staffing economics.
- Infection control requirements exceed baseline (negative pressure or enhanced filtration), increasing mechanical scope.

### Question bank (8-12)
1. How many exam rooms are required, and is there a fixed program count? Driver: exam room count or SF per room. Changes: revenue and staffing metrics. Shows: ExecutiveView revenue analysis.
2. What are operating hours and days per year? Driver: `visits_per_day`, `days_per_year`. Changes: revenue and labor ratios. Shows: ExecutiveView revenue/NOI.
3. Is there on-site imaging (x-ray) or a dedicated imaging suite? Driver: `x_ray`, `hc_urgent_imaging_suite`. Changes: electrical/mechanical scope. Shows: DealShield driver tile and ConstructionView MEP notes.
4. Is an on-site lab required (phlebotomy, CLIA lab)? Driver: `laboratory`, `hc_urgent_on_site_lab`. Changes: plumbing and mechanical scope. Shows: DealShield driver tile and MEP notes.
5. Are observation bays or a trauma room required? Driver: `hc_urgent_observation_bays`, `trauma_room`. Changes: finishes and MEP intensity. Shows: ConstructionView Finishes/MEP.
6. Any infection control requirements (negative pressure, isolation rooms, enhanced filtration)? Driver: MEP upgrades. Changes: mechanical scope and schedule. Shows: ConstructionView Mechanical.
7. Are medical gas or procedure capabilities required? Driver: explicit MEP upgrades. Changes: plumbing/mechanical scope. Shows: ConstructionView Plumbing/Mechanical.
8. Is emergency power or generator backup required? Driver: electrical upgrades. Changes: electrical scope and equipment. Shows: ConstructionView Electrical.
9. Target finish level for clinical areas? Driver: finish level multiplier. Changes: finishes cost. Shows: ConstructionView totals.
10. Is there a hard opening date or accelerated schedule? Driver: timeline override. Changes: schedule risk and contingency posture. Shows: ConstructionView schedule.

### Red-flag -> action table
| Trigger | Why it matters | What to ask | What to change |
| --- | --- | --- | --- |
| Imaging suite required | Electrical and HVAC loads rise | Confirm imaging modality and room count | Add `hc_urgent_imaging_suite` or `x_ray` inputs and rerun |
| On-site lab required | Ventilation and plumbing scope increase | Confirm lab type and scope | Add `hc_urgent_on_site_lab` or `laboratory` inputs |
| Observation bays added | Raises clinical finishes and MEP intensity | Confirm bay count and acuity | Add `hc_urgent_observation_bays` input |
| Negative pressure/isolation required | Mechanical scope and schedule change | Confirm air change rates and pressure zones | Add explicit MEP upgrades or adjust trade assumptions |
| 7-day operations not accurate | Revenue and labor economics shift | Confirm operating days/hours | Override `visits_per_day` / `days_per_year` |

### Negotiation levers (3-5)
- Limit imaging scope to essential modalities only: Driver `hc_urgent_imaging_suite` / `x_ray`. Reduces electrical and mechanical adders.
- Defer on-site lab buildout: Driver `hc_urgent_on_site_lab` / `laboratory`. Shrinks plumbing and mechanical scope.
- Right-size observation bays: Driver `hc_urgent_observation_bays`. Reduces finishes and MEP intensity.
- Keep clinical finishes at baseline: Driver finish level multiplier. Controls finishes cost without changing program.
- Align operating hours to realistic demand: Driver `visits_per_day` / `days_per_year`. Stabilizes revenue assumptions and staffing ratios.
