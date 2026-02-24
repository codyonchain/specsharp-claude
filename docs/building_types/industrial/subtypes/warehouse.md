# Subtype: Warehouse (Industrial)

## Block A - Decision & KPIs (Decision Insurance)
DealShield is the decision insurance front door. ExecutiveView and ConstructionView are the proof appendices. Every statement below maps to deterministic drivers (config fields, profiles, or explicit inputs).

### Primary decision moment (VP Dev / Fund Partner)
Make a go/no-go call on a warehouse shell based on deterministic all-in cost, schedule, and NOI-based yield gates. If cost and yield gates fail, decide whether to rescope office/dock assumptions, reprice, or walk before DD.

### What success looks like
- Greenlight: Cost, schedule, and yield gates pass with a clear driver story.
- Rescope: Office buildout, dock intensity, or mezzanine assumptions are corrected and re-run.
- Reprice: Base cost or regional factors are adjusted, then decision gates re-evaluated.
- Walk: Deterministic downside (cost +10% and revenue -10%) fails DSCR/yield gates with no credible driver fix.

### KPI outputs (and deterministic sources)
- All-in cost ($ and $/SF): ConstructionView totals from `construction_costs`, `soft_costs`, and `total_project_cost`.
- Schedule and milestones: Timeline profile from `backend/app/v2/config/type_profiles/project_timelines/industrial.py` (ground_up) or deterministic fallback if project class lacks a profile.
- Revenue proxy (modeled): ExecutiveView `revenue_analysis` and NOI outputs using subtype config `base_revenue_per_sf_annual`, occupancy defaults, and `operating_margin_base`.
- Downside deltas: DealShield tiles sourced from deterministic `sensitivity_analysis` (cost +/-10%, revenue +/-10%).

### DealShield tiles (deterministic)
- Tile 1: Cost +10% (required, from `sensitivity_analysis.cost_up_10`).
- Tile 2: Revenue -10% (required, from `sensitivity_analysis.revenue_down_10`).
- Tile 3 (subtype driver): Office buildout intensity (office % or office SF) when explicit input is provided; uses `office_percent` / `office_sf` overrides in `industrial_warehouse_structural_v1`. If no explicit office input exists, do not show this tile.

### Conservative / Ugly rows
- Conservative: Apply Cost +10% and Revenue -10% together (derived from the two required tiles; no new numbers).
- Ugly: Conservative plus the Office buildout intensity tile when present (derived; no new numbers). If no driver tile is present, Ugly equals Conservative.

### Confidence band (driver-tied, no fabricated %)
- Office percent uncertainty widens confidence when `office_percent` / `office_sf` is not explicitly provided.
- Slab spec uncertainty widens confidence because the structural profile assumes a standard slab on grade; explicit slab spec tightens.
- Site intensity widens confidence because Site/Civil is not a separate trade in this subtype; explicit site scope tightens.
- Dock count uncertainty widens confidence when `dock_doors` / `dock_count` are inferred from SF.
- Fire protection standard (ESFR vs CMDA) widens confidence because the plumbing profile assumes ESFR unless overridden.
- Utility power upgrades widen confidence when high service loads are required beyond baseline electrical assumptions.
- Schedule acceleration widens confidence when a custom timeline overrides the industrial ground_up profile.

If the platform emits an explicit confidence score/label, show it; otherwise keep the band qualitative and driver-tied as above.

### Risk exposure + notes (failure modes tied to drivers)
- Dock count wrong: mis-sizes structural dock pits/aprons and equipment allocation; breaks Structural trade totals and schedule logic.
- Office buildout understated: compresses Finishes and Mechanical scope; breaks cost and revenue expectations.
- Slab load or thickness above baseline: structural cost and schedule under-estimated; requires explicit slab spec override.
- Fire protection standard mismatch: ESFR assumed; a CMDA or higher-hazard requirement shifts plumbing scope and schedule risk.
- Electrical service under-sized: main service and distribution assumptions fail; electrical scope and utility cost ratios break.
- Heavy sitework hidden in scope: Site/Civil not modeled as a trade; total cost and schedule risk rise without explicit adders.

### Provenance report (deterministic pointers)
- Subtype config: `backend/app/v2/config/subtypes/industrial/warehouse.py`.
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/industrial.py` -> `industrial_warehouse_structural_v1`.
- Type profile (yield/DSCR gates): `backend/app/v2/config/type_profiles/industrial.py`.
- Margin profile: `backend/app/v2/config/type_profiles/margins/industrial.py`.
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/industrial.py`.
- Finish level factors: `backend/app/v2/config/master_config.py` (`FINISH_LEVELS`, `get_finish_cost_factor`).

## Block B - ConstructionView: Trade Summary & Scope Items (Critical Trust Layer)
ConstructionView for warehouse shows these trades: Structural, Mechanical, Electrical, Plumbing, Finishes. Architectural/Envelope scope is embedded in Structural (tilt-wall shell). Fire protection is embedded in Plumbing (ESFR item). Site/Civil is not modeled as a separate trade for this subtype.

### Structural
- Included scope: Concrete slab on grade (6") via `concrete_slab_on_grade`.
- Included scope: Tilt-wall panels / structural shell via `tilt_wall_shell`.
- Included scope: Foundations, footings, and thickened slabs via `foundations_footings`.
- Included scope: Dock pits and loading aprons via `dock_pits_loading_aprons`.
- Included scope: Mezzanine structure when `mezzanine_sf` / percent is provided (otherwise omitted).
- Common exclude: Major sitework, grading, retention, and utilities (not a modeled trade).
- Common exclude: Specialized racking or automation foundations beyond baseline slab.
- Common exclude: Cold storage floor systems or freezer slabs (belongs to cold storage subtype).
- Special features/equipment mapping: Dock equipment is captured via `equipment_cost_per_sf` in subtype config, not in this trade.
- Primary deterministic drivers: `industrial_warehouse_structural_v1` scope items profile, `dock_doors` / `dock_count` overrides, `mezzanine_sf` / `mezzanine_percent`, and total SF.
- How to validate fast: Confirm dock door count and whether any mezzanine SF is required.

### Mechanical
- Included scope: Rooftop units and primary heating/cooling equipment via `rtu_primary_hvac`.
- Included scope: Make-up air and exhaust fans via `makeup_air_exhaust`.
- Included scope: Ductwork, distribution, and ventilation via `ductwork_distribution`.
- Common exclude: Process HVAC or refrigeration systems (belongs to cold storage or manufacturing).
- Common exclude: Dedicated office tenant HVAC beyond baseline RTUs.
- Special features/equipment mapping: No special mechanical features in this subtype config; additions must be explicit inputs.
- Primary deterministic drivers: `industrial_warehouse_structural_v1` mechanical rules (SF per RTU, SF per exhaust fan), total SF.
- How to validate fast: Confirm required HVAC zones and any process or high-bay cooling loads.

### Electrical
- Included scope: High-bay lighting and controls via `high_bay_lighting`.
- Included scope: Power distribution and panels via `power_distribution_panels`.
- Included scope: Main electrical service and switchgear via `main_service_switchgear`.
- Common exclude: High-capacity power upgrades for automation or heavy manufacturing loads.
- Common exclude: Specialty low-voltage, security, or controls beyond baseline.
- Special features/equipment mapping: No electrical special features in subtype config; power upgrades require explicit input.
- Primary deterministic drivers: `industrial_warehouse_structural_v1` electrical rules and total SF.
- How to validate fast: Confirm service size expectations and any automation or charging loads.

### Plumbing
- Included scope: Restroom groups via `restroom_groups`.
- Included scope: Domestic water, hose bibs, and roof drains via `domestic_water_roof_drains`.
- Included scope: Fire protection (ESFR sprinkler system) via `fire_protection_esfr`.
- Common exclude: Process plumbing or specialized waste systems.
- Common exclude: Fire pump upgrades or storage tanks beyond baseline ESFR assumptions.
- Special features/equipment mapping: Fire protection standard changes must be explicit inputs; otherwise ESFR is assumed.
- Primary deterministic drivers: `industrial_warehouse_structural_v1` plumbing rules (SF per restroom group), total SF.
- How to validate fast: Confirm hazard classification (ESFR vs CMDA) and restroom count requirements.

### Finishes
- Included scope: Office build-out (walls, ceilings, flooring) via `office_buildout`.
- Included scope: Warehouse floor sealers and striping via `warehouse_floor_sealers`.
- Included scope: Doors, hardware, and misc interior finishes via `doors_hardware_misc`.
- Common exclude: Premium office interiors beyond baseline finish level.
- Common exclude: Showroom-grade finishes (belongs to flex or specialty subtype).
- Special features/equipment mapping: Finish level multipliers from `master_config.py` affect total cost; no subtype-specific finish overrides for warehouse.
- Primary deterministic drivers: `office_percent` / `office_sf` overrides, finish level multiplier, total SF.
- How to validate fast: Confirm office percentage and finish level expectations.

### Trade distribution % rule
- Percentages must come from deterministic trade totals in `calculations.trade_breakdown`; never fabricate.

### Construction schedule + key milestones
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/industrial.py` (ground_up) unless project class lacks a profile, in which case the deterministic default timeline is used.
- Milestones (as configured): Groundbreaking (offset_months 0), Structure Complete (offset_months 8), Substantial Completion (offset_months 14), Grand Opening (offset_months 18).

## Block C - ExecutiveView: Decision Appendix Checklist
- Investment Decision: Provided deterministically from ownership analysis and decision gates (yield/DSCR).
- Revenue projections (rent/lease assumptions): Provided deterministically from `base_revenue_per_sf_annual`, occupancy, and margin defaults in subtype config.
- Facility metrics: Not applicable for industrial (no `facility_metrics_profile` configured).
- Prescriptive playbook: Requires explicit input; only show actions tied to confirmed drivers (office %, dock count, schedule overrides).
- Feasibility vs target yield: Provided deterministically using `target_yield` from the industrial type profile and computed yield on cost.
- Major soft cost categories: Provided deterministically from subtype `soft_costs` config.
- Key financial indicators (DSCR/yield/NOI/etc): Provided deterministically from `ownership_analysis` and `revenue_analysis` outputs.
- Market position: Requires explicit input (comps or broker intel); do not infer.
- Quick sensitivity: Provided deterministically from `sensitivity_analysis` (cost +/-10%, revenue +/-10%).
- Key milestones: Provided deterministically from the industrial timeline profile and aligned to ConstructionView milestones.
- Financing structure: Provided deterministically from subtype financing terms (debt/equity, rate, DSCR target, ROI target).
- Operational efficiency: Provided deterministically from operating ratio inputs in subtype config (utilities, taxes, insurance, maintenance, management, security, reserves, labor).
- Executive decision points: Provided deterministically; if yield or DSCR gates fail, the recommendation shifts to rescope/reprice/walk.
- Footer: Provided deterministically; must state determinism, provenance, and what inputs would change the answer.

## Block D - Assumptions & Question Bank (Subtype-local, ranked and mapped)

### Ranked assumptions (5-7)
1. Office share matches `office_percent` / `office_sf` (default or explicit). Impacts Finishes and Mechanical; shows in ConstructionView and DealShield driver tile; validate with program breakdown.
2. Dock count aligns with `dock_doors` / `dock_count` (default per SF if missing). Impacts Structural dock scope and equipment cost; shows in ConstructionView and DealShield; validate with loading plan.
3. Mezzanine scope is zero unless explicitly provided. Impacts Structural and schedule; shows in ConstructionView; validate with program.
4. Slab spec is standard slab on grade per profile. Impacts Structural and schedule; shows in ConstructionView; validate with structural criteria.
5. Fire protection assumes ESFR unless overridden. Impacts Plumbing scope and risk; shows in ConstructionView and ExecView risk; validate with AHJ and commodity classification.
6. Electrical service is baseline (no major upgrades). Impacts Electrical and operational efficiency; shows in ConstructionView and ExecView op efficiency; validate with tenant load letter.

### Most likely wrong (top 3)
- Dock count and door type are under-specified, shifting structural scope and equipment cost.
- Office buildout share is understated, compressing finishes and MEP assumptions.
- Site/Civil intensity is higher than implied, requiring explicit adders outside the modeled trades.

### Question bank (8-12)
1. How many dock doors and drive-in doors are required? Driver: `dock_count`. Changes: structural dock scope and equipment cost. Shows: ConstructionView Structural, DealShield driver tile.
2. What is office square footage or percent of GSF? Driver: `office_percent` / `office_sf`. Changes: Finishes and Mechanical scope. Shows: ConstructionView Finishes, ExecutiveView cost and sensitivity.
3. Is any mezzanine required (SF or percent)? Driver: `mezzanine_sf` / `mezzanine_percent`. Changes: Structural scope and schedule. Shows: ConstructionView Structural.
4. What is the required clear height and slab load? Driver: slab spec and structural assumptions. Changes: Structural cost/schedule. Shows: ConstructionView Structural and risk notes.
5. ESFR vs CMDA sprinkler standard? Driver: fire protection assumption. Changes: Plumbing scope and schedule risk. Shows: ConstructionView Plumbing and ExecView risk.
6. What is the electrical service size and automation load? Driver: electrical service. Changes: Electrical scope and operating ratios. Shows: ConstructionView Electrical and ExecView op efficiency.
7. Any cold storage, freezer, or process HVAC requirements? Driver: subtype fit. Changes: Mechanical scope and subtype selection. Shows: ConstructionView Mechanical; may require cold storage subtype.
8. What sitework is required (truck courts, paving, utilities, stormwater)? Driver: site intensity. Changes: total cost and schedule outside modeled trades. Shows: DealShield risk and provenance notes.
9. Target finish level for office areas? Driver: finish level multiplier. Changes: cost and revenue factor. Shows: ConstructionView totals and ExecutiveView revenue.
10. Is there a hard delivery date or accelerated schedule? Driver: timeline override. Changes: schedule and contingency posture. Shows: ConstructionView schedule and DealShield risk.

### Red-flag -> action table
| Trigger | Why it matters | What to ask | What to change |
| --- | --- | --- | --- |
| Dock count materially above default | Structural dock scope and equipment cost rise | Confirm door count and dock equipment needs | Update `dock_count` / equipment inputs and rerun |
| Office share above baseline | Finishes and MEP scope increase | Confirm office SF and finish level | Override `office_percent` / `office_sf` and finish level |
| ESFR not accepted by AHJ | Plumbing scope and schedule change | Confirm required sprinkler standard | Add fire protection override or rescope |
| High power/automation loads | Electrical scope and utility costs increase | Confirm service size and load profile | Add electrical service override or reclassify subtype |
| Heavy sitework scope | Cost/schedule unmodeled | Confirm sitework package | Add explicit sitework scope or adjust total cost externally |
| Schedule shorter than profile | Risk and contingency increase | Confirm critical path milestones | Apply timeline override and adjust contingency posture |

### Negotiation levers (3-5)
- Reduce office buildout share: Driver `office_percent` / Finishes. Moves the needle by shrinking high-cost interior scope.
- Optimize dock count and layout: Driver `dock_count` / Structural. Moves the needle by reducing dock pits and equipment allocation.
- Defer mezzanine buildout: Driver `mezzanine_sf` / Structural. Moves the needle by removing a discrete structural add.
- Keep slab spec at baseline: Driver slab spec / Structural. Moves the needle by avoiding high-load slab premiums.
- Maintain baseline fire protection: Driver ESFR vs upgrades / Plumbing. Moves the needle by avoiding higher-cost suppression systems.
