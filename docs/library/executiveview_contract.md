# ExecutiveView Contract (Global)

## Purpose
Define the required structure, copy standards, and decision framework for ExecutiveView so a single output reads like a lender/investor-ready memo.
ExecutiveView must be **model-class appropriate** and **subtype-distinct**.

## Ownership Model
- Global contract (this doc): required modules, field definitions, copy standards.
- Type-owner: which modules apply for the type (NOI vs Operating vs Throughput vs Mixed vs Feasibility) + type-level templates.
- Subtype-owner: subtype-specific drivers, KPI set, thresholds, recommendation copy profile, risk notes, and provenance specifics.

## Determinism + Trust Rules
1) No silent type coercion (unknown type is an error).
2) Unknown subtype falls back deterministically with warning trace.
3) Regional factors are global (cost_factor, market_factor) and must be explained consistently.
4) Every override/clamp/inference must be traceable and visible in assumptions/provenance.
5) ExecutiveView must never present a metric that doesn't match the model class.

---

# Required Modules (ExecutiveView)

## 1) Trust & Assumptions (Always required)
### 1.1 Trust Statement (Required)
A short paragraph explaining:
- deterministic engine (no guessing)
- what inputs were provided vs inferred
- how to interpret confidence band

### 1.2 Assumptions Table (Required)
Must include:
- Location + cost_factor + market_factor
- Project class
- Core facility drivers (subtype-defined list)
- Any default assumptions used
- Any inferred assumptions used (with trace IDs)

**Subtype divergence requirement:**
Assumptions must list the subtype-specific drivers:
- QSR: transactions/day, avg ticket, margin
- Fine Dining: seats, turns, avg check, labor intensity assumptions
- Cold Storage: freezer ratio, refrigeration tier, equipment assumptions
- Imaging Center: machines, scans/day, reimbursement assumptions
- Hotel: keys, ADR, occupancy, RevPAR

---

## 2) Regional Context (Always required; global)
This module explains regional impact without subtype-specific distortion.

Required fields:
- cost_factor explanation (construction reality)
- market_factor explanation (pricing power/demand)
- any overrides or city-only inference warning

**Validation:**
- Must align with taxonomy/trace policy (city-only warning must be surfaced).

---

## 3) Investment Decision (Always required)
### 3.1 Recommendation (Required)
- GO / NO-GO / NEEDS WORK
- One-sentence headline justification

### 3.2 Decision Criteria (Required)
ExecutiveView must show the gates used to decide, based on model class:
- NOI assets: DSCR, yield on cost, stabilized value logic
- Operating assets: payback, cash-on-cash, margin durability
- Throughput assets: unit economics + DSCR + risk flags
- Mixed use: sum-of-parts + blended gates
- Feasibility: budget fit + schedule risk + program fit

**Subtype divergence requirement:**
Each subtype defines:
- which KPIs are displayed as "Key Financial Indicators"
- threshold values
- recommendation copy profile (tone and specifics)

---

## 4) Revenue Projections (Model-class dependent)
### NOI / Cap-rate assets
Required outputs:
- Effective Gross Income (EGI)
- NOI
- Cap-rate derived value
- DSCR
- Yield on cost

### Operating business assets (Restaurant/Hospitality/etc.)
Required outputs:
- Annual revenue
- Operating margin and net income
- Payback period
- Cash-on-cash (if equity modeled)
- Break-even metric (occupancy or sales)

### Throughput-driven healthcare/specialty
Required outputs:
- Units x throughput x reimbursement logic summary
- Unit economics (per room / per procedure)
- Operating margin and cash flow
- DSCR if debt applies

### Feasibility (Public/institutional)
Required outputs:
- Total cost
- Cost per unit served (student/seat/bed/etc.)
- Schedule and risk summary
- Funding fit (if provided)

**Validation:**
- Must not display cap-rate valuation for operating assets unless subtype explicitly declares hybrid.

---

## 5) Facility Metrics (Subtype-owned, template-driven)
This module is *always present* but its metrics are subtype-defined.

Rules:
- Each subtype must define a `facility_metrics_set` (ordered list).
- Each metric must include: label, value, unit, and provenance.

Examples:
- Industrial: clear height, dock doors, office ratio
- Restaurant: seats, turns, avg check, kitchen ratio
- Healthcare: exam rooms, beds, scans/day, providers
- Hotel: keys, ADR, occupancy, RevPAR

---

## 6) Feasibility vs Target Yield (Always required, but model-class aware)
- NOI assets: compare yield on cost to target yield
- Operating assets: compare payback/cash-on-cash to target ranges
- Throughput assets: compare unit economics to targets + risk tier
- Feasibility assets: compare cost/program/schedule to acceptable thresholds

Subtype must define the specific "target" metrics and ranges.

---

## 7) Major Soft Cost Categories (Always required)
Must show at minimum:
- Design/architecture/engineering
- Permits/fees
- Financing costs
- Contingency
- CM/GC general conditions (if modeled)
- Testing/commissioning (if relevant)
- FF&E (if relevant)

Subtype may override emphasis and add categories.

---

## 8) Key Financial Indicators (Subtype-owned KPI set)
This is a critical divergence point: **do not reuse the same KPI list across subtypes** unless appropriate.

Subtype must provide:
- Ordered KPI list (3-7 KPIs)
- Each KPI: definition, value, units, and why it matters

Validation:
- KPI list must match model class (no DSCR for public feasibility assets unless explicitly modeled).

---

## 9) Market Position (Required)
Must include:
- brief market note tied to market_factor (global)
- subtype-specific sensitivity to market conditions (e.g., restaurants more volatile than warehouses)

---

## 10) Quick Sensitivity (Required)
Subtype must declare sensitivity variables (2-4):
- NOI assets: rent, occupancy, cap rate, cost/SF
- Hotels: ADR, occupancy, margin
- Restaurants: transactions, avg ticket, labor cost, rent
- Healthcare: throughput, reimbursement, staffing cost

Sensitivity must be deterministic: controlled deltas without re-running base engine (if that's the system rule).

---

## 11) Key Milestones (Required)
ExecutiveView repeats schedule in executive-friendly form:
- Total duration
- 5-8 key milestones (subset from ConstructionView)
- Critical risk milestones highlighted

---

## 12) Financing Structure (Required)
Must include:
- LTC, debt/equity
- interest rate assumption (if applicable)
- DSCR target (if applicable)
- summary of debt sizing logic

Subtype may override financing assumptions if that asset class differs.

---

## 13) Operational Efficiency (Model-class dependent, required)
Should include:
- major expense drivers
- operating margin explanation
- subtype-specific operational risk notes

---

## 14) Prescriptive Playbook (Required)
Type owner provides the template; subtype provides deltas.

Structure:
- 3-6 bullets: "what to improve to turn NEEDS WORK into GO"
- Must reference the actual gating metrics.

Examples:
- NOI asset: raise rents, reduce cost/SF, improve occupancy assumptions, cap-rate risk
- Restaurant: improve margin, lower labor ratio, increase throughput, reduce build-out cost
- Healthcare: increase throughput, adjust staffing ratio, reduce capex intensity

---

## 15) Executive Decision Points (Required)
A short list of "what you must confirm before committing capital," subtype-specific:
- missing key inputs
- biggest risks
- recommended next diligence steps

---

## 16) Footer / Disclaimers (Required)
Global, consistent across all outputs:
- deterministic estimate disclaimer
- not a substitute for bid set / lender underwriting
- encourage validating key drivers

---

# Acceptance Criteria (for any subtype Build.md)
A subtype is not "done" until:
1) ExecutiveView modules match the correct model class
2) KPIs are subtype-distinct and defensible
3) Recommendation copy is subtype-appropriate and grounded in metrics
4) Assumptions list is subtype-specific and provenance-backed
5) Quick sensitivity variables match subtype drivers
6) Key milestones are reasonable for subtype
7) Traceability/provenance fully supports trust narrative
