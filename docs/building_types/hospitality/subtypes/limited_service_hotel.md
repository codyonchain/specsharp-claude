# Subtype: Limited Service Hotel (Hospitality)

## Block A - Decision & KPIs (Decision Insurance)
DealShield is the decision insurance front door. ExecutiveView and ConstructionView are the proof appendices. Every statement below maps to deterministic drivers (config fields, profiles, or explicit inputs).

### Primary decision moment (VP Dev / Fund Partner)
Make a go/no-go call on a limited service hotel based on deterministic all-in cost, schedule, and hospitality underwriting outputs (ADR, occupancy, NOI, and yield/DSCR gates). If cost or yield gates fail, decide whether to rescope key count/amenities, reprice, or walk before DD.

### What success looks like
- Greenlight: Cost, schedule, and yield/DSCR gates pass with a clear driver story.
- Rescope: Key count, amenity package, or finish level assumptions are corrected and re-run.
- Reprice: Base cost or regional factors are adjusted, then decision gates re-evaluated.
- Walk: Deterministic downside (cost +10% and revenue -10%) fails DSCR/yield gates with no credible driver fix.

### KPI outputs (and deterministic sources)
- All-in cost ($ and $/SF): ConstructionView totals from `construction_costs`, `soft_costs`, and `totals.total_project_cost`.
- Schedule and milestones: Timeline profile from `backend/app/v2/config/type_profiles/project_timelines/hospitality.py` (ground_up) or deterministic fallback if project class lacks a profile.
- Revenue proxy (modeled): ExecutiveView `revenue_analysis` outputs driven by ADR/occupancy/keys logic in `_build_hospitality_financials` using `base_adr_by_market`, `base_occupancy_by_market`, `rooms_per_sf`, and expense percentages.
- NOI, yield on cost, and DSCR: `revenue_analysis` and `ownership_analysis` outputs using subtype financing terms and hospitality revenue model.
- Downside deltas: DealShield tiles sourced from deterministic `sensitivity_analysis` (cost +/-10%, revenue +/-10%).

### DealShield tiles (deterministic)
- Tile 1: Cost +10% (required, from `sensitivity_analysis.cost_up_10`).
- Tile 2: Revenue -10% (required, from `sensitivity_analysis.revenue_down_10`, driven by ADR/occupancy/keys model).
- Tile 3 (subtype driver): Key count (rooms/keys) from `rooms_per_sf` * total SF or explicit `rooms`/`keys` input. Show only when total SF or key inputs are present; otherwise hide.

### Conservative / Ugly rows
- Conservative: Apply Cost +10% and Revenue -10% together (derived from the two required tiles; no new numbers).
- Ugly: Conservative plus the Key count tile when present (derived; no new numbers). If no driver tile is present, Ugly equals Conservative.

### Confidence band (driver-tied, no fabricated %)
- Key count uncertainty widens confidence when `rooms`/`keys` are inferred from SF (no explicit input).
- ADR/occupancy uncertainty widens confidence when overrides are not provided and defaults from `base_adr_by_market` / `base_occupancy_by_market` are used.
- Expense load uncertainty widens confidence when hotel-specific expense inputs are not provided (uses `expense_percentages`).
- Amenity package uncertainty widens confidence when special features (breakfast area, fitness, business center, pool) are assumed but not explicitly selected.
- Finish level uncertainty widens confidence because finish multipliers adjust total cost; explicit finish level tightens.
- Schedule acceleration widens confidence when a custom timeline overrides the hospitality ground_up profile.

If the platform emits an explicit confidence score/label, show it; otherwise keep the band qualitative and driver-tied as above.

### Risk exposure + notes (failure modes tied to drivers)
- Keys/room count wrong: mis-sizes guestroom stack, MEP risers, and FF&E budget; breaks revenue and NOI outputs.
- ADR/occupancy overrides missing: defaults may misstate revenue in non-primary markets.
- Amenity scope understated: breakfast/fitness/pool adders not captured unless explicitly selected.
- FF&E boundary unclear: equipment cost per SF is the only modeled FF&E bucket; missing scope can hide large costs.
- Parking/land/sitework not modeled: total project cost and schedule risk rise without explicit adders.
- Financing terms mismatch: DSCR gate uses subtype financing terms; if the capital stack differs, underwriting must be updated.

### Provenance report (deterministic pointers)
- Subtype config: `backend/app/v2/config/subtypes/hospitality/limited_service_hotel.py`.
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/hospitality.py` -> `hospitality_limited_service_hotel_structural_v1`.
- Type profile (yield/DSCR gates): `backend/app/v2/config/type_profiles/hospitality.py`.
- Margin profile: `backend/app/v2/config/type_profiles/margins/hospitality.py`.
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/hospitality.py`.
- Finish level factors: `backend/app/v2/config/master_config.py` (`FINISH_LEVELS`, `get_finish_cost_factor`).

## Block B - ConstructionView: Trade Summary & Scope Items (Critical Trust Layer)
ConstructionView for limited service hotel shows these trades: Structural, Mechanical, Electrical, Plumbing, Finishes. Structural is itemized via scope items; other trades are modeled as trade-level totals from the subtype `trades` shares. Amenities (breakfast area, fitness, business center, pool) are only costed when explicitly selected via special features.

### Structural
- Included scope: Foundations, slab, and footings via `foundations_slab_footings`.
- Included scope: Structural frame via `structural_frame` (typical mid-rise guestroom stack and corridor/core framing).
- Included scope: Roof structure and deck via `roof_structure_deck`.
- Included scope: Stairs and elevator core structural allowance via `stairs_elevator_core_allowance`.
- Included scope: Misc. structural and lateral system allowances via `misc_structural_allowance`.
- Common exclude: Major sitework, grading, retention, and utilities (not a modeled trade).
- Common exclude: Structured parking or podium parking (not modeled unless added explicitly).
- Primary deterministic drivers: `hospitality_limited_service_hotel_structural_v1` scope items profile and total SF.
- How to validate fast: Confirm floor count/stacking, core layout, and whether any podium/parking structure is required.

### Mechanical
- Included scope (trade total only): Guestroom HVAC, corridor pressurization, ventilation, and central plant/RTU allowances sized to total SF.
- Common exclude: Full-service F&B kitchens, conference center mechanical, or spa/pool dehumidification systems beyond limited-service scope.
- Special features/equipment mapping: Pool HVAC or dehumidification is not explicitly modeled unless added externally.
- Primary deterministic drivers: Trade share from subtype config and total SF; no scope-item profile for mechanical.
- How to validate fast: Confirm HVAC system type (PTAC/VRF/central) and any pool or laundry loads.

### Electrical
- Included scope (trade total only): Guestroom power, lighting, life safety, and core electrical allowances.
- Common exclude: High-capacity EV charging or large-scale commercial laundry power beyond baseline.
- Special features/equipment mapping: Special feature adders do not explicitly allocate to electrical; add explicit scope if required.
- Primary deterministic drivers: Trade share from subtype config and total SF; no scope-item profile for electrical.
- How to validate fast: Confirm service size and any specialty power loads.

### Plumbing
- Included scope (trade total only): Guestroom plumbing stacks, domestic hot water, and public restroom allowances.
- Common exclude: Large commercial laundry plants or extensive pool plumbing beyond baseline.
- Special features/equipment mapping: Pool plumbing is not explicitly modeled unless added externally.
- Primary deterministic drivers: Trade share from subtype config and total SF; no scope-item profile for plumbing.
- How to validate fast: Confirm laundry equipment strategy and any pool/spa scope.

### Finishes
- Included scope (trade total only): Guestroom finishes, corridor finishes, and front-of-house finishes consistent with finish level.
- Common exclude: FF&E (beds, casegoods, seating) is not part of Finishes; it is captured only through `equipment_cost_per_sf` in the subtype config.
- Common exclude: Brand-standard upgrade packages unless reflected in finish level or explicit adders.
- Special features/equipment mapping: Breakfast/fitness/business/pool are modeled as special feature adders, not finishes trade items.
- Primary deterministic drivers: Finish level multiplier from `master_config.py`, trade share from subtype config, and total SF.
- How to validate fast: Confirm brand finish standard and whether any lobby/amenity upgrades are planned.

### Trade distribution % rule
- Percentages must come from deterministic trade totals in `trade_breakdown`; never fabricate.

### Construction schedule + key milestones
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/hospitality.py` (ground_up) unless project class lacks a profile, in which case the deterministic default timeline is used.
- Milestones (as configured): Groundbreaking (offset_months 0), Structure Complete (offset_months 14), Substantial Completion (offset_months 24), Grand Opening (offset_months 30).

## Block C - ExecutiveView: Decision Appendix Checklist
- [Deterministic] Investment Decision: from `ownership_analysis` (DSCR, ROI) and yield outputs.
- [Deterministic] Revenue projections (ADR/occupancy/NOI): from `_build_hospitality_financials` using `base_adr_by_market`, `base_occupancy_by_market`, `rooms_per_sf`, and `expense_percentages` unless overrides are provided.
- [N/A] Facility metrics: no `facility_metrics_profile` configured.
- [Deterministic] Feasibility vs target yield: using `target_yield` from hospitality type profile and computed yield on cost.
- [Deterministic] Major soft cost categories: from subtype `soft_costs` config.
- [Deterministic] Key financial indicators (DSCR/yield/NOI/etc): from `ownership_analysis` and `revenue_analysis` outputs.
- [Input] Market position: comps/brand placement; do not infer.
- [Deterministic] Quick sensitivity: from `sensitivity_analysis` (cost +/-10%, revenue +/-10%).
- [Deterministic] Key milestones: from the hospitality timeline profile and aligned to ConstructionView milestones.
- [Deterministic] Financing structure: from subtype `ownership_types` terms (debt/equity mix, rate, target DSCR, target ROI).
- [Deterministic] Operational efficiency: from `expense_percentages` and operating ratios in subtype config.
- [Deterministic] Executive decision points: if yield or DSCR gates fail, recommendation shifts to rescope/reprice/walk.
- [Deterministic] Footer: must state determinism, provenance, and what inputs would change the answer.

## Block D - Assumptions & Question Bank (Subtype-local, ranked and mapped)

### Ranked assumptions (5-7)
1. Key count equals `rooms_per_sf` * GSF unless `rooms`/`keys` override is provided. Impacts revenue and NOI; validate with brand program.
2. ADR and occupancy follow `base_adr_by_market` / `base_occupancy_by_market` unless overrides are provided. Impacts revenue, NOI, and yield; validate with comp set.
3. Expense load uses `expense_percentages` defaults. Impacts NOI and DSCR; validate with operator pro forma.
4. Finish level is standard unless explicitly set. Impacts construction cost and brand standard; validate with brand PIP.
5. Amenities limited to breakfast area, fitness, business center, and pool only when explicitly selected. Impacts total cost; validate with brand prototype.
6. No structured parking or heavy sitework assumed. Impacts cost and schedule; validate with site plan.

### Most likely wrong (top 3)
- Key count and stacking are inferred from SF; program may shift keys or floor count.
- ADR/occupancy defaults may diverge from actual market or brand positioning.
- Amenity package (pool, expanded breakfast, laundry) may be larger than implied by defaults.

### Question bank (8-12)
1. What is the confirmed key count and typical room size? Driver: `rooms`/`keys` or `rooms_per_sf`. Changes: revenue, NOI, and sensitivity outputs. Shows: DealShield driver tile and ExecutiveView revenue.
2. What ADR and stabilized occupancy should we use? Driver: ADR/occupancy overrides. Changes: revenue/NOI and yield gap. Shows: ExecutiveView revenue and sensitivity.
3. Which amenities are in scope (breakfast, fitness, business center, pool)? Driver: special features selection. Changes: construction adders and schedule risk. Shows: ConstructionView totals and risk notes.
4. Is there a brand-required finish level or PIP scope? Driver: finish level multiplier. Changes: total cost and margins. Shows: ConstructionView totals and ExecutiveView cost.
5. Is structured parking or podium parking required? Driver: non-modeled scope. Changes: total cost and schedule outside modeled trades. Shows: DealShield risk.
6. What HVAC system type is planned (PTAC, VRF, central plant)? Driver: mechanical intensity. Changes: mechanical trade assumptions and schedule risk. Shows: ConstructionView Mechanical.
7. Is there an on-site laundry plant or outsourced service? Driver: plumbing/electrical intensity. Changes: MEP scope and operating expenses. Shows: ConstructionView MEP and operating ratios.
8. Any meeting rooms or expanded public areas beyond limited service prototype? Driver: finishes/MEP intensity. Changes: cost and schedule. Shows: ConstructionView Finishes and risk notes.
9. What is the target capital stack (debt/equity mix and rate)? Driver: financing terms. Changes: DSCR and ROI outputs. Shows: ExecutiveView financing.

### Red-flag -> action table
| Trigger | Why it matters | What to ask | What to change |
| --- | --- | --- | --- |
| Key count deviates from inferred GSF | Revenue and NOI scale directly with keys | Confirm brand key count and room mix | Override `rooms`/`keys` and rerun |
| ADR/occupancy below defaults | Yield and DSCR may fail | Provide comp set or underwriting assumptions | Override ADR/occupancy inputs |
| Amenity package expanded (pool, large breakfast) | Cost adders not modeled by default | Confirm amenity list and sizes | Add special features or explicit cost adders |
| Structured parking required | Major cost/schedule not modeled | Confirm parking type and stall count | Add external parking scope or adjust total cost |
| Brand PIP upgrades | Finish costs rise materially | Confirm PIP scope and finish level | Set finish level or add explicit scope |
| HVAC system upgrade (VRF/central) | Mechanical cost and schedule increase | Confirm system selection | Add mechanical scope adjustment |

### Negotiation levers (3-5)
- Reduce amenity package scope: Special features adders. Moves the needle by trimming discrete cost adders.
- Rebalance room mix or key count: `rooms`/`keys` override. Moves the needle by aligning revenue and cost to realistic key count.
- Keep finish level at standard: Finish level multiplier. Moves the needle by avoiding premium interior costs.
- Avoid structured parking: External scope. Moves the needle by removing major unmodeled cost.
- Align HVAC system to baseline: Mechanical intensity. Moves the needle by avoiding high-cost system upgrades.
