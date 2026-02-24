# ExecutiveView Contract (Global)

**Contract ID:** ExecutiveView Contract  
**Version:** v1.1  
**Last updated:** February 4, 2026  
**Owner lane:** Type Owner + Core Integrator  
**Change log:**
- v1.1: Added explicit required sections and fields, validation checklist with FAIL/WARN, decision rule representation, and examples; tightened normative language.
- v1.0: Initial global contract.

## Purpose
ExecutiveView MUST provide a lender- and investor-ready summary that is deterministic, subtype-distinct, and aligned with model class. This contract MUST keep global structure stable while forcing subtype-owned decision framing and KPI selection.

## Ownership Model
- Global contract (this document) MUST define required modules, field definitions, and copy standards.
- Type Owner MUST define which modules apply for the type, the model class, and type-level templates.
- Subtype Owner MUST define subtype-specific drivers, KPI sets, thresholds, recommendation copy profile, risk notes, and provenance anchors.

## Determinism + Trust Rules (Non-Negotiable)
1. No silent type coercion: unknown type is an error.
2. Unknown subtype MUST deterministically fall back with a warning trace.
3. Regional factors are global (`cost_factor`, `market_factor`) and MUST be explained consistently.
4. Every override, clamp, or inference MUST be traceable and visible in assumptions and provenance.
5. ExecutiveView MUST NOT present metrics that conflict with the model class.

---

## Required Sections (Explicit List)
The ExecutiveView output MUST include these sections, in order:
1. Trust & Assumptions
2. Regional Context
3. Investment Decision
4. Revenue Projections
5. Facility Metrics
6. Soft Costs
7. Feasibility vs Target Yield
8. Sensitivities
9. Risks
10. Milestones
11. Financing
12. Op Efficiency
13. Disclaimers + Provenance

---

# Required Sections (ExecutiveView)

## 1) Trust & Assumptions (Required)
**Required fields (MUST include):**
- Trust statement describing deterministic engine behavior and confidence interpretation.
- Assumptions list with provenance anchors for each assumption.
- Inputs provided vs inferred, each with trace IDs.

**Subtype divergence requirement (MUST):**
Assumptions MUST include subtype-specific operational drivers (e.g., seats, keys, docks, exam rooms, throughput).

---

## 2) Regional Context (Required; Global-Only)
**Required fields (MUST include):**
- `cost_factor` explanation.
- `market_factor` explanation.
- Any regional ambiguity warning (city-only inference).

**Rules (MUST):**
- Regional Context MUST be global-only and MUST NOT include subtype-specific distortion.

---

## 3) Investment Decision (Required)
**Required fields (MUST include):**
- Decision label: GO / NO-GO / NEEDS WORK.
- One-sentence justification.
- Decision rule representation that lists gates and thresholds.
- Model-class label for the decision logic.

**Subtype divergence requirement (MUST):**
- Subtype MUST define the KPI gates and threshold values.
- Recommendation copy MUST follow subtype-defined tone and priorities.

---

## 4) Revenue Projections (Required; Model-Class Aware)
**Required fields (MUST include):**
- Model-class specific outputs, aligned to the subtype model class.
- Summary of the revenue logic used (e.g., NOI, operating, throughput, feasibility).

**Rules (MUST):**
- NOI assets MUST include EGI, NOI, DSCR, yield on cost, and cap-rate derived value.
- Operating assets MUST include annual revenue, operating margin, net income, and payback or cash-on-cash when equity is modeled.
- Throughput assets MUST include throughput logic, unit economics, operating margin, and DSCR when debt applies.
- Feasibility assets MUST include total cost, cost per unit served, and funding fit if provided.

---

## 5) Facility Metrics (Required; Profile Selection Rules)
**Required fields (MUST include):**
- `facility_metrics_profile` identifier.
- Ordered list of metrics with label, value, unit, and provenance.

**Rules (MUST):**
- Profile selection MUST be deterministic and traceable.
- Metrics list MUST be subtype-owned and MUST differ across subtypes when reality differs.

---

## 6) Soft Costs (Required Categories + Overrides)
**Required fields (MUST include):**
- Design/architecture/engineering
- Permits/fees
- Financing costs
- Contingency
- CM/GC general conditions if modeled
- Testing/commissioning if relevant
- FF&E if relevant
- Override list with provenance anchors

---

## 7) Feasibility vs Target Yield (Required; Model-Class Aware)
**Required fields (MUST include):**
- Target metrics and ranges, subtype-defined.
- Comparison statement of actuals vs targets.

**Rules (MUST):**
- NOI assets MUST compare yield on cost to target yield.
- Operating assets MUST compare payback or cash-on-cash to targets.
- Throughput assets MUST compare unit economics to targets and risk tier.
- Feasibility assets MUST compare cost, program fit, and schedule to thresholds.

---

## 8) Sensitivities (Required)
**Required fields (MUST include):**
- 2-4 sensitivity variables declared by subtype.
- Controlled delta values and resulting metric changes.
- Provenance for sensitivity method.

**Rules (MUST):**
- Sensitivities MUST be deterministic and MUST NOT silently re-run base engine unless the system policy allows it.

---

## 9) Risks (Required)
**Required fields (MUST include):**
- Risk list with severity (low/medium/high), short explanation, and mitigation.
- Subtype-specific risk drivers.

---

## 10) Milestones (Required; ConstructionView-Aligned)
**Required fields (MUST include):**
- Total duration.
- 5-8 key milestones drawn from ConstructionView.
- Alignment proof to ConstructionView milestone IDs.

**Rules (MUST):**
- Milestone IDs and ordering MUST match ConstructionView milestones for the same type/subtype/project_class.

---

## 11) Financing (Required)
**Required fields (MUST include):**
- LTC, debt/equity split.
- Interest rate assumption if applicable.
- DSCR target if applicable.
- Debt sizing logic summary with provenance anchors.

---

## 12) Op Efficiency (Required; Model-Class Dependent)
**Required fields (MUST include):**
- Major expense drivers.
- Operating margin explanation.
- Subtype-specific operational risks.

---

## 13) Disclaimers + Provenance (Required)
**Required fields (MUST include):**
- Deterministic estimate disclaimer.
- Not a substitute for bid set or lender underwriting.
- Provenance summary that distinguishes explicit inputs, defaults, inferences, and clamps.

---

## Examples (Short)
**Decision rule representation (one example):**
```json
{"decision":"GO","model_class":"noi","gates":[{"metric":"yield_on_cost","op":">=","threshold":0.085},{"metric":"dscr","op":">=","threshold":1.25}]}
```

**Threshold failure example (one example):**
```json
{"decision":"NEEDS WORK","failed_gates":[{"metric":"payback_years","op":"<=","threshold":8,"actual":11}]}
```

---

## Validation Checklist (FAIL)
- Missing any required section or required fields for a section.
- Decision rule representation missing or not model-class aligned.
- Revenue projections include metrics that conflict with the model class.
- Milestones do not align with ConstructionView milestone IDs.
- Facility metrics profile missing or not traceable.
- Missing provenance anchors for assumptions, overrides, or decision gates.

## Validation Checklist (WARN)
- Sensitivities lack provenance or show ambiguous delta logic.
- Regional Context includes subtype-specific distortion.
- Risks are generic and not subtype-specific.
- Op Efficiency lacks subtype-specific expense drivers.

---

# Acceptance Criteria (for any subtype Build.md)
A subtype is not "done" until ALL of the following are true:
1. ExecutiveView modules match the correct model class.
2. KPIs are subtype-distinct and defensible.
3. Recommendation copy is subtype-appropriate and grounded in metrics.
4. Assumptions list is subtype-specific and provenance-backed.
5. Sensitivity variables match subtype drivers.
6. Key milestones align with ConstructionView for the same subtype.
7. Traceability/provenance fully supports the trust narrative.
