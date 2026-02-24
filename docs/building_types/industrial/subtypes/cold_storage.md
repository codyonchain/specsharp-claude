# Subtype: Cold Storage (Industrial)

## Underwriting overrides vs base type
- MEP intensity: Very high (refrigeration systems dominate total cost)
- Envelope intensity: High (insulated panels, vapor barriers, cold dock packages)
- Revenue risk: Higher volatility with power and temperature compliance exposure
- Operating expense load: Higher utility and monitoring ratios than standard industrial

## Deterministic drivers (explicit inputs override defaults)
- Freezer vs cooler area split (requires explicit input to be modeled; otherwise not shown)
- Refrigeration system tier (ammonia vs Freon vs CO2, if provided)
- Redundancy level (N+1 compressors / backup power) if provided
- Dock door count and office SF overrides (if provided) apply to scope items

---

## Block A - Decision & KPIs (DealShield front door)

### Decision moment
Cold storage is a GO only when NOI metrics clear target DSCR and yield thresholds after cold-chain risk stress (power and refrigeration reliability). If the project fails under a cost +10% or revenue -10% stress, the decision shifts to RESCOPE or REPRICE. If critical cold-chain risks cannot be mitigated or insured, WALK.

### Decision copy (explicit)
- GO: "Cold-chain scope is fully covered and NOI clears targets under base and stress cases. Proceed to underwriting and bid validation."
- RESCOPE: "Cold-chain scope is overbuilt or misaligned. Reduce freezer area, simplify temp zones, or re-balance dock package before underwriting."
- REPRICE: "Revenue does not cover the refrigeration and power premium. Reprice rent or incentives to clear DSCR and yield targets."
- WALK: "Power capacity, refrigeration redundancy, or insurer requirements cannot be satisfied at acceptable cost. Do not proceed."

### KPI outputs mapping to views
| KPI | ExecutiveView | DealShield | ConstructionView | Provenance |
| --- | --- | --- | --- | --- |
| noi | Primary NOI metric | Decision gate | N/A | Derived from revenue model using config ratios in `backend/app/v2/config/subtypes/industrial/cold_storage.py` |
| dscr | Primary lender gate | Decision gate | N/A | Financing terms in `backend/app/v2/config/subtypes/industrial/cold_storage.py` |
| yield_on_cost | Primary feasibility gate | Decision gate | N/A | Derived from NOI and total cost |
| stabilized_value | Cap-rate value | Support | N/A | NOI / cap_rate (global model) |
| breakeven_rent_psf | Support diagnostic | Support | N/A | Derived from NOI targets and rentable SF |
| construction_total | N/A | Cost tile input | Primary cost output | Trade breakdown and scope items |

### DealShield tiles (minimum)
- Cost +10%: Deterministic stress = `construction_total * 1.10` (no other changes).
- Revenue -10%: Deterministic stress = `base_revenue_per_sf_annual * 0.90` (occupancy and margin use base values unless explicitly overridden).
- Driver tile (freezer vs cooler split / temp class): Requires explicit user input; not shown until modeled.

### Conservative / ugly derived rules (no invented numbers)
- Conservative: Use base revenue inputs (base rent, base occupancy, base operating margin) with unmodified construction cost.
- Ugly: Combine Cost +10% and Revenue -10% simultaneously; no additional multipliers beyond these two stress tiles.

### Confidence band drivers (cold-chain specific)
- Freezer percentage of total area
- Refrigeration system type (ammonia vs Freon vs CO2)
- Insulated envelope package (panel R-value and roof insulation)
- Utility upgrade scope (service size, transformer, switchgear)
- Redundancy level (backup power and compressor redundancy)
- Dock equipment and cold-door package
- Blast freezer rooms or ultra-low temperature zones
- Operating schedule (24/7 vs limited hours)

### Risk exposure + notes (tie to drivers)
- Freezer percentage: Higher freezer mix increases refrigeration load and energy risk; verify electrical capacity and redundancy.
- Refrigeration system type: Ammonia or CO2 systems can trigger higher safety and compliance requirements; confirm jurisdictional constraints.
- Insulated envelope package: Under-specified insulation or vapor barrier drives condensation, ice, and performance failures; validate envelope spec.
- Utility upgrade scope: Utility lead times and service upgrades can delay schedules; confirm utility commitment and cost share.
- Redundancy level: Insufficient backup power elevates spoilage risk and insurance premiums; validate required uptime.
- Dock equipment package: Cold-dock doors and seals drive capex and energy; validate door counts and dock throughput.
- Blast freezer rooms: Specialized rooms add mechanical and control complexity; confirm if included or excluded.
- Operating schedule: 24/7 operations increase wear and maintenance; confirm staffing and maintenance budgets.

### Provenance pointers
- Subtype config: `backend/app/v2/config/subtypes/industrial/cold_storage.py`
- Scope items profile: `backend/app/v2/config/type_profiles/scope_items/industrial.py` (profile id `industrial_cold_storage_structural_v1`)
- Timeline profile: `backend/app/v2/config/type_profiles/project_timelines/industrial.py`
- Global contracts: `docs/library/dealshield_contract.md`, `docs/library/executiveview_contract.md`, `docs/library/constructionview_contract.md`

---

## Block B - ConstructionView Trade Summary (CRITICAL)

### Trade distribution rule (deterministic only)
Use the trade percentages in `backend/app/v2/config/subtypes/industrial/cold_storage.py` with no inference:
- Structural 0.25
- Mechanical 0.35
- Electrical 0.18
- Plumbing 0.10
- Finishes 0.12

### Cold-storage callouts (must be explicit)
- Refrigeration and mechanical intensity drives a larger mechanical share and commissioning risk.
- Electrical power and utility upgrades are a top risk driver for schedule and contingency.
- Insulated envelope and slab vapor barrier are mandatory scope items.
- Cold docks and door packages are required to maintain temperature integrity.
- Fire protection and insurer constraints require early validation of ESFR / in-rack systems.

### Structural
- Included scope: insulated slab on grade with vapor barrier, heavier foundations and frost protection, structural shell, cold dock pits/aprons.
- Excludes: site acquisition, off-site utility extensions, specialized rack systems.
- Adders: under-slab heating protection, enhanced dock aprons if blast freezer or ultra-low temp zones are present.
- Drivers: freezer percentage, envelope package, dock door count.
- Validate questions: Do we have freezer area percentage and required slab frost protection? Are dock doors and cold canopies confirmed?

### Mechanical
- Included scope: industrial refrigeration system, evaporators/condensers, refrigerant piping, controls, temperature monitoring.
- Excludes: tenant-owned process equipment, specialized automation beyond base controls.
- Adders: blast freezer systems, multi-zone temperature control, redundancy (N+1 compressors).
- Drivers: refrigeration system type, temp zone count, redundancy requirement.
- Validate questions: What refrigerant type is required? Are blast freezers or multi-temp zones included?

### Electrical
- Included scope: high-capacity power distribution, motor control centers, controls and monitoring, lighting.
- Excludes: utility company fees beyond on-site work, data center-grade UPS unless specified.
- Adders: backup power generator tie-in, high-capacity switchgear, utility service upgrades.
- Drivers: utility service size, redundancy requirement, freezer percentage.
- Validate questions: Is utility service upgrade required? Is backup power required by insurer or operator?

### Plumbing
- Included scope: ESFR / in-rack sprinkler systems, domestic water, floor drains, restrooms.
- Excludes: process wastewater treatment or specialized sanitation systems.
- Adders: freeze protection for exposed piping, enhanced fire suppression for high rack storage.
- Drivers: storage height, insurer requirements, temperature zone count.
- Validate questions: Are in-rack sprinklers mandated? Is freeze protection required at docks or mezzanines?

### Finishes
- Included scope: insulated panel walls/ceilings, food-grade finishes, cold-rated doors and seals, limited office/control room buildout.
- Excludes: tenant-specific finishes beyond food-grade baseline.
- Adders: higher R-value panels, hygienic wall/ceiling systems, specialized door packages.
- Drivers: insulation package, freezer percentage, dock package.
- Validate questions: Are panel R-values and vapor barrier specs defined? Are cold-door packages specified?

### Schedule + milestones (from default timeline)
- Uses industrial `ground_up` timeline from `backend/app/v2/config/type_profiles/project_timelines/industrial.py`.
- Total duration: 18 months.
- Milestones: groundbreaking (0), structure_complete (8), substantial_completion (14), grand_opening (18).

---

## Block C - ExecutiveView checklist (same as warehouse)
Status legend: Deterministic (config or derived) | Requires input | N/A

- Trust & Assumptions: Deterministic (explicit drivers + defaults) with Required input for any declared overrides.
- Regional Context: Requires input (location for cost_factor and market_factor).
- Investment Decision: Deterministic (decision gates from DSCR and yield_on_cost).
- Revenue Projections: Requires input (rent and occupancy overrides); deterministic defaults exist in config.
- Facility Metrics: Requires input for freezer/cooler split and temp zones; otherwise deterministic base metrics.
- Soft Costs: Deterministic (config soft_costs).
- Feasibility vs Target Yield: Deterministic (compare to target thresholds).
- Sensitivities: Deterministic (Cost +10% and Revenue -10% only).
- Risks: Deterministic list; requires input to refine freezer %, redundancy, and insulation spec.
- Milestones: Deterministic (industrial ground_up timeline).
- Financing: Deterministic (config terms) with Requires input if ownership type differs.
- Op Efficiency: Deterministic (utility and monitoring ratios from config).
- Disclaimers + Provenance: Deterministic (standard contract language + trace anchors).

Quick sensitivity alignment: ExecutiveView sensitivities MUST mirror DealShield tiles (Cost +10%, Revenue -10%).

---

## Block D - Assumptions & Question Bank

### Ranked assumptions (driver-tied)
1. Freezer percentage of total SF is within the expected cold-chain band.
2. Refrigeration system type is compatible with local code and insurer requirements.
3. Utility service can support refrigeration load without major off-site upgrades.
4. Insulated envelope and slab vapor barrier package meets temperature target.
5. Redundancy level (backup power, compressor redundancy) is aligned with operator uptime needs.
6. Dock count and cold-door package are sufficient for throughput.
7. Blast freezer rooms are excluded unless explicitly stated.

### Most likely wrong (top 3)
1. Freezer percentage assumption (drives mechanical and electrical load).
2. Utility upgrade scope (drives cost and schedule).
3. Redundancy requirement (drives mechanical and electrical adders).

### Question bank (driver-tied)
1. What percentage of total area is freezer vs cooler vs ambient?
2. Which refrigeration system type is required (ammonia, Freon, CO2)?
3. Are blast freezer rooms included? If yes, how many and what size?
4. Is N+1 compressor redundancy required? Is backup power required?
5. What is the required service size (kVA) and has the utility confirmed capacity?
6. Are panel R-values and slab vapor barrier specs defined?
7. How many dock doors are required and are they cold-dock capable?
8. Is in-rack sprinkler or ESFR required by insurer?
9. What operating schedule is planned (24/7 vs limited hours)?
10. Are food-grade finishes or sanitary washdown areas required?

### Red-flag -> Action table
| Red flag | Action |
| --- | --- |
| Utility upgrade required with long lead time | Escalate schedule risk, confirm utility letter, add contingency for service upgrades. |
| Redundancy required but not budgeted | Reprice mechanical and electrical scope, add backup power allowance. |
| Freezer % higher than assumed | Rescope refrigeration and insulation package, update energy and cost sensitivity. |
| Insurer mandates in-rack sprinklers | Add fire protection scope and validate rack layout requirements. |
| Blast freezer rooms requested late | Treat as scope change, add mechanical/electrical adders, update schedule. |

### Negotiation levers (cost or risk impact)
- Reduce freezer percentage or consolidate temperature zones to lower refrigeration load.
- Align redundancy requirement to a clear uptime target (avoid over-spec).
- Phase utility upgrades or secure utility incentives to offset capex.
- Optimize dock door count and cold-door package to match throughput.
- Lock in envelope R-value spec early to avoid late-stage change orders.

---

## Trace requirements (additional)
- cold_storage_intensity_applied (or captured in modifiers_applied with subtype=cold_storage)
- scope_items_profile_selected (profile id `industrial_cold_storage_structural_v1`)
- recommendation_derived (decision gates + stress tiles)

## Acceptance tests (invariants)
- If freezer percentage is explicitly set (future input), it overrides defaults and is traceable.
- Trade percentages and scope items must originate from config (no engine hardcode).
- DealShield sensitivities match ExecutiveView sensitivities (Cost +10%, Revenue -10%).
