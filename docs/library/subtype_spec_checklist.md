# Subtype Spec Checklist (Required for "Done")

## Purpose
Guarantee that **every subtype** produces a client-trustworthy output on its own.
This checklist prevents subtypes from becoming "too close" due to generic type defaults.

**Rule:** Global/type docs define structure and templates.
**Subtype must fully specify content and deltas** where reality differs.

A subtype is **not eligible for agent completion** until all blocks below are fully filled.

---

# Block A -- Decision & KPI Spec (ExecutiveView)

## A1) Model Declaration
- model_class: NOI / Operating / Throughput / Public-feasibility / Mixed
- valuation_mode: cap_rate / payback / hybrid / none
- decision_profile_id: <string> (used to select copy + thresholds)

## A2) Required KPIs (Ordered list)
Provide 3-7 KPI slots, in order. Each KPI must include:
- id (snake_case)
- label
- unit
- definition (1 sentence)
- provenance source (config field or derived formula)

**Examples**
- QSR: payback_years, cash_on_cash, margin_pct, transactions_per_day, avg_ticket
- Fine Dining: margin_pct, seat_turns, avg_check, labor_intensity_flag, ramp_risk
- Warehouse: noi, dscr, yield_on_cost, stabilized_value, breakeven_rent_psf
- Imaging Center: scans_per_day, reimbursement_per_scan, staffing_ratio, dscr

## A3) Recommendation Gates
Define the gates that drive:
- GO / NEEDS WORK / NO-GO

Each gate includes:
- metric id
- threshold(s)
- rationale (1 sentence)
- trace requirement (must be explainable)

Example:
- DSCR >= 1.25 (NOI assets)
- Payback <= 6.0 years (operating assets)
- Margin durability >= target (operating assets)
- Unit throughput meets minimum (throughput assets)

## A4) Recommendation Copy Profile
Subtype must provide:
- headline template (GO/NO-GO/NEEDS WORK)
- top 3 bullet rationale templates
- "what to improve" playbook bullet template hooks

---

# Block B -- Construction Spec (ConstructionView)

## B1) Trade Summary Spec
Subtype must define:
- trade_distribution_profile_id (or explicit trade percentages)
- any trades that MUST be emphasized for this subtype
- any trades that MUST be reduced/zeroed

Required: explain why this subtype differs from its type defaults.

Examples:
- Cold Storage: Mechanical/Electrical up, Equipment present, Envelope intensity up
- Fine Dining: Finishes up, Mechanical/Plumbing up, Kitchen package
- QSR: Finishes moderate, Equipment present, fast fit-out
- Data Center: Electrical/Mechanical extreme, commissioning, redundancy systems

## B2) Trade Line Item Spec (must include subtype signature items)
List the "signature" line items that must appear in Trade Distribution Detail:
- item name
- unit and quantity derivation
- inclusion condition (explicit vs default vs inferred)
- provenance requirement

Examples:
- Industrial: dock package, slab spec, office buildout line items
- Restaurant: hood suppression, grease trap, kitchen equipment
- Healthcare: med gases, imaging equipment, sterilization, exam rooms
- Hotel: rooms/keys package, FF&E, back-of-house

## B3) Special Features Spec
Subtype must define:
- allowed feature_ids
- default features (if any) and when allowed
- inferred features (if any) + trace requirement + confidence impact
- feature pricing logic (adders) + provenance

## B4) Equipment & Fees Spec
Subtype must declare required buckets and any subtype-specific adders:
- equipment
- FF&E (if applicable)
- testing/commissioning
- IT/controls
- specialty systems

## B5) Construction Schedule & Milestones Spec
Subtype must define:
- schedule_profile_id OR explicit milestone list
- milestone deltas from type template
- critical path milestones
- commissioning milestones if relevant

Milestones must include:
- id, label, offset_months, critical_path

---

# Block C -- Assumptions & Trust Spec

## C1) Assumptions List (Subtype-specific)
Subtype must list:
- core drivers (with units)
- default values (if any) + why acceptable
- acceptable ranges (min/max or bands)
- what happens when missing (confidence impact, warnings)

Examples:
- Hotels: keys, ADR, occupancy, RevPAR
- Restaurants: seats/turns OR transactions/day, avg ticket, labor ratio
- Industrial: dock doors, office ratio, clear height
- Healthcare: exam rooms, scans/day, reimbursement rate

## C2) Confidence Band Drivers
Subtype must declare:
- which missing inputs lower confidence
- which inferred values lower confidence
- which inputs raise confidence (explicit drivers)

Must map to a deterministic scoring approach.

## C3) Risk Exposure Notes
Subtype must provide structured risk notes across:
- cost risk
- schedule risk
- market/revenue risk (if relevant)
- operational complexity risk
- regulatory/compliance risk (if relevant)

Each includes severity + mitigation suggestion.

---

# Block D -- Provenance Spec (Auditability)

## D1) Required Trace Steps
Subtype must list required trace breadcrumbs for:
- overrides (explicit inputs)
- inference (if any)
- clamps (if any)
- profile selectors

Trace step IDs must match the global trace registry.

## D2) Provenance Report Requirements
Subtype must define what provenance must explicitly state:
- which config fields were used (base_cost_per_sf, margins, etc.)
- cost_factor and market_factor used and their sources
- any fallback subtype usage (unknown_subtype_fallback)
- any city-only warning (city_only_location_warning)
- special features included and why

---

# Completion Gate
A subtype is "DONE" only when:
1) All four blocks A-D are filled.
2) ConstructionView output satisfies `constructionview_contract.md`.
3) ExecutiveView output satisfies `executiveview_contract.md`.
4) Determinism + traceability rules are satisfied.
5) Acceptance tests exist (at least invariants + trace checks; goldens as needed).
6) No generic type defaults are relied on without explicit subtype opt-in.

---

# Notes
- Multi-model types (Specialty/Healthcare/Mixed Use): subtype must declare model_class and KPI set explicitly.
- Global/Type templates are allowed only as defaults; subtype must list deltas explicitly to avoid "blurry" outputs.
