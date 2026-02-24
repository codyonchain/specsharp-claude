# Subtype: Quick Service Restaurant (Restaurant)

## Underwriting overrides vs base type
- High MEP intensity driven by kitchen ventilation, hood/fire suppression, and grease management.
- Revenue is modeled (base revenue, occupancy, margin); decision insurance requires explicit downside stress.
- Site and drive-thru flow can dominate schedule and permit risk even when not fully modeled as a trade.

## Deterministic drivers (explicit inputs override defaults)
- Drive-thru selections (special features `drive_thru` / `double_drive_thru`) when explicitly provided.
- Outdoor seating or play area only if explicitly selected as special features.
- Location (regional multipliers) when provided.

---

## Block A - Decision & KPIs (DealShield front door)

### Decision moment
QSR is a GO only if NOI and DSCR clear targets under base and downside stress (Cost +10%, Revenue -10%). If the stress case fails, the decision shifts to RESCOPE (reduce scope or site intensity), REPRICE (adjust revenue or incentives), or WALK (if hood/grease/fire requirements or site constraints cannot be funded).

### Decision copy (explicit)
- GO: "QSR program clears NOI/DSCR under base and stress cases with hood/grease/fire scope validated. Proceed to underwriting and bids."
- RESCOPE: "Program or site intensity is too high; reduce drive-thru scope, simplify kitchen package, or adjust footprint before underwriting."
- REPRICE: "Revenue does not clear downside stress; adjust rent or incentives and re-run."
- WALK: "Hood/grease/fire compliance or site constraints cannot be resolved at acceptable cost or schedule."

### KPI outputs mapping to views
| KPI | ExecutiveView | DealShield | ConstructionView | Provenance |
| --- | --- | --- | --- | --- |
| noi | Primary NOI metric | Decision gate | N/A | Derived from revenue model using `backend/app/v2/config/subtypes/restaurant/quick_service.py` ratios |
| dscr | Primary lender gate | Decision gate | N/A | Financing terms in `backend/app/v2/config/subtypes/restaurant/quick_service.py` |
| yield_on_cost | Primary feasibility gate | Decision gate | N/A | Derived from NOI and total cost |
| stabilized_value | Cap-rate value | Support | N/A | NOI / cap_rate (global model) |
| breakeven_rent_psf | Support diagnostic | Support | N/A | Derived from NOI targets and rentable SF |
| construction_total | N/A | Cost tile input | Primary cost output | Trade breakdown and scope items |

### DealShield tiles (minimum)
- Cost +10%: Deterministic stress = `construction_total * 1.10`.
- Revenue -10%: Deterministic stress = `base_revenue_per_sf_annual * 0.90` with base occupancy and margin unless explicitly overridden.
- Driver tile (optional): Drive-thru intensity (single vs double) only when `drive_thru` / `double_drive_thru` is explicitly selected; otherwise hide this tile.

### Conservative / ugly derived rules (no invented numbers)
- Conservative: Apply Cost +10% and Revenue -10% together.
- Ugly: Conservative plus the drive-thru tile when present. If no driver tile, Ugly equals Conservative.

### Confidence band drivers (QSR-specific)
- Hood and fire suppression complexity (equipment and code requirements).
- Grease interceptor size and routing (plumbing and site tie-in).
- Kitchen equipment interface allowances (power, gas, make-up air) if explicitly specified.
- Drive-thru and paving/site intensity (stacking length, lane count, curb cuts).
- Finish level assumptions (uses config defaults unless finish-level overrides are provided).

### Risk exposure + notes (tie to drivers)
- Hood/fire suppression not sized: mechanical and plumbing scope under-estimated; compliance risk.
- Grease interceptor omitted or undersized: plumbing and sitework cost spikes; schedule risk.
- Equipment loads missing: electrical service and HVAC adders hidden; cost risk.
- Drive-thru sitework underestimated: paving, striping, and circulation costs unmodeled.
- Finish level mismatch: revenue expectations and cost factor drift.

### Provenance pointers
- Subtype config: `backend/app/v2/config/subtypes/restaurant/quick_service.py`.
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/restaurant.py` (profile id `restaurant_quick_service_structural_v1`).
- Type profile (yield/DSCR gates): `backend/app/v2/config/type_profiles/restaurant.py`.
- Finish level factors: `backend/app/v2/config/master_config.py` (`finish_level_multipliers`, `FINISH_LEVELS`, `get_finish_cost_factor`).
- Global contracts: `docs/library/dealshield_contract.md`, `docs/library/executiveview_contract.md`, `docs/library/constructionview_contract.md`.

---

## Block B - ConstructionView Trade Summary (CRITICAL)

### Trade distribution rule (deterministic only)
Use the trade percentages in `backend/app/v2/config/subtypes/restaurant/quick_service.py` with no inference:
- Structural 0.22
- Mechanical 0.28
- Electrical 0.15
- Plumbing 0.15
- Finishes 0.20

### QSR trust-critical callouts (explicit)
- Hood exhaust and fire suppression are trust-critical and must be validated early.
- Grease interceptor sizing and routing drive plumbing and site tie-ins.
- Kitchen equipment interface allowances are user-input driven unless explicitly modeled.
- Drive-thru and site paving are not a standalone trade; treat as sitework adders when present.

### Structural
- Included scope: slab/foundations, structural frame/shell, roof structure, and envelope structural allowances via `restaurant_quick_service_structural_v1`.
- Excludes: major sitework, paving, and off-site utilities (not modeled as a trade).
- Drivers: total SF and any structural scope overrides.
- Validate questions: Is the slab or roof designed for heavy rooftop equipment or canopy loads?

### Mechanical
- Included scope: baseline HVAC and ventilation tied to trade share; mechanical intensity assumes kitchen exhaust demand.
- Hood/fire suppression note: Hood exhaust and make-up air requirements must be explicitly validated; treat as a must-confirm scope item even if not separately itemized.
- Excludes: specialized kitchen equipment packages unless explicitly provided.
- Drivers: kitchen intensity and ventilation requirements (explicit input if available).
- Validate questions: What hood size and airflows are required? Are make-up air units included?

### Electrical
- Included scope: baseline power distribution and lighting within trade share.
- Equipment interface note: High-load kitchen equipment (fryers, ovens, warmers) requires explicit input to size service and panels.
- Excludes: utility upgrades or transformer scopes unless explicitly provided.
- Drivers: equipment load and service size (explicit input).
- Validate questions: What is the required service size and panel count for the kitchen line?

### Plumbing
- Included scope: domestic plumbing and baseline fire protection within trade share.
- Grease interceptor + fire suppression: Grease interceptor sizing, routing, and hood suppression are trust-critical; treat as required confirmation.
- Excludes: specialized wastewater treatment or off-site utility upgrades.
- Drivers: kitchen intensity, grease load, and fire suppression requirements (explicit input).
- Validate questions: Is a grease interceptor required on-site? What size and location are mandated by AHJ?

### Finishes
- Included scope: dining area, back-of-house finishes, and standard interiors within trade share.
- Finish level note: Uses finish-level multipliers or defaults from config; no subtype-specific finish overrides are assumed.
- Excludes: premium brand build-outs unless explicitly specified.
- Drivers: finish level and brand standard inputs.
- Validate questions: What finish level is required for front-of-house vs back-of-house?

### Trade distribution % rule
- Percentages must come from deterministic trade totals in `calculations.trade_breakdown`; never fabricate.

---

## Block C - ExecutiveView checklist (complete and honest)
Status legend: Deterministic (config or derived) | Requires input | N/A

- Trust & Assumptions: Deterministic, with Required input for any declared overrides.
- Regional Context: Requires input (location for cost_factor and market_factor).
- Investment Decision: Deterministic (decision gates from DSCR and yield_on_cost).
- Revenue Projections: Deterministic defaults exist; requires input for brand-specific overrides.
- Facility Metrics: N/A (no `facility_metrics_profile` configured).
- Soft Costs: Deterministic (config `soft_costs`).
- Feasibility vs Target Yield: Deterministic (compare to target thresholds in type profile).
- Sensitivities: Deterministic (Cost +10% and Revenue -10% only).
- Risks: Deterministic list with Required input to refine hood/grease/fire and site scope.
- Milestones: Requires input (no restaurant-specific timeline profile referenced).
- Financing: Deterministic (config terms) with Requires input if ownership type differs.
- Op Efficiency: Deterministic (cost ratios from subtype config).
- Disclaimers + Provenance: Deterministic (standard contract language + trace anchors).

Quick sensitivity alignment: ExecutiveView sensitivities MUST mirror DealShield tiles (Cost +10%, Revenue -10%).

---

## Block D - Assumptions & Question Bank

### Ranked assumptions (driver-tied)
1. Hood exhaust and fire suppression scope matches a standard QSR line; affects Mechanical and Plumbing.
2. Grease interceptor sizing is within typical QSR ranges; affects Plumbing and site tie-ins.
3. Kitchen equipment loads are within baseline electrical assumptions; affects Electrical service sizing.
4. Drive-thru scope is single-lane unless explicitly stated; affects site/paving adders.
5. Finish level aligns with config defaults; affects cost and revenue factors.
6. Sitework is light-to-moderate and does not require major off-site utilities.

### Most likely wrong (top 3)
1. Hood/fire suppression scope underestimated (code requirements vary by AHJ).
2. Grease interceptor sizing and routing under-scoped.
3. Drive-thru and paving/sitework underestimated.

### Question bank (driver-tied)
1. Is a drive-thru required? If yes, single or double lane? Driver: `drive_thru` / `double_drive_thru`.
2. What hood length, type, and suppression system are required by code? Driver: hood/fire scope.
3. Is a grease interceptor required on-site? What size and location? Driver: plumbing and site tie-ins.
4. What is the kitchen equipment package and connected load (electric/gas)? Driver: electrical and mechanical adders.
5. Are make-up air units included with the hood system? Driver: mechanical scope.
6. Any brand-standard finish upgrades for the dining area? Driver: finish level multiplier.
7. What site/paving scope is required for the drive-thru and parking layout? Driver: site intensity.
8. Are there utility upgrades or off-site extensions needed? Driver: utilities and schedule risk.

### Red-flag -> Action table
| Red flag | Action |
| --- | --- |
| Hood/fire suppression requirements unclear | Require AHJ or fire marshal confirmation; add mechanical and plumbing allowances. |
| Grease interceptor not defined | Obtain plumbing requirements and add site tie-in scope. |
| Drive-thru added late | Treat as scope change; add sitework and permitting time. |
| Kitchen equipment loads higher than assumed | Upsize electrical service and HVAC; update cost and schedule. |
| Finish level exceeds defaults | Apply finish-level override and re-run revenue/cost impacts. |

### Negotiation levers (cost or risk impact)
- Reduce drive-thru scope or stacking length to lower sitework and paving cost.
- Right-size hood and suppression to code minimums rather than over-spec.
- Align kitchen equipment package to a baseline line-up before bids.
- Separate front-of-house finish upgrades from core shell to avoid baseline escalation.
- Phase sitework improvements to defer non-essential paving.
