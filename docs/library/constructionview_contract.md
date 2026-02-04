# ConstructionView Contract (Global)

## Purpose
Define the required structure, fields, and quality bar for ConstructionView so any single project output is client-trustworthy.
This contract enforces **consistent layout** while allowing **subtype-specific divergence** (trade %, line items, milestones, features, risk notes).

## Ownership Model
- Global contract (this doc): structure + required fields + validation rules.
- Type-owner: type-level defaults/templates (trade distribution template, schedule template, equipment categories).
- Subtype-owner: subtype-specific trade summary content, trade distributions, feature lists, equipment/fees, milestones deltas, and notes.

## Determinism Rules (Non-Negotiable)
1) No hidden assumptions: defaults must be explicit and explainable.
2) Explicit overrides always win (0% office / 0 docks / 0 mezz / etc.).
3) Any override/clamp/inference must produce a `calculation_trace` breadcrumb.
4) Regional multipliers are global (cost_factor/market_factor); never localized per subtype outside the canonical system.

---

# Required Sections (ConstructionView)

## 1) Project Summary Header
**Required fields:**
- Building Type (canonical v2 key)
- Subtype (canonical v2 key)
- Location (City, ST)
- Project Class (ground_up / tenant_improvement / renovation etc.)
- Square Footage (GSF)
- Version / Timestamp
- Confidence Band (see section 7)

**Validation:**
- Building type must be canonical; unknown type is an error.
- Unknown subtype must deterministically fall back with warning trace (unknown_subtype_fallback).

---

## 2) Trade Summary (Core Output)
This must look like something a GC/Owner would recognize.

### 2.1 Trade List (Required)
Trade Summary must include at minimum these trade categories (even if zeroed):
- Sitework
- Foundations
- Structural
- Envelope
- Interiors / Finishes
- Mechanical (HVAC)
- Electrical
- Plumbing
- Fire Protection (if applicable)
- Low Voltage / Controls (if applicable)
- Conveying (if applicable)
- Specialties / Equipment (if applicable)
- General Conditions / GC OH&P (if modeled)
- Contingency (if modeled)

**Subtype divergence requirement:**
- The *percent split and line items* must differ by subtype when reality differs.
  - Example: Cold Storage must have materially higher Mechanical/Electrical and Equipment.
  - Example: Fine Dining must have higher Finishes and Kitchen/MEP complexity than QSR.

### 2.2 Trade Summary Columns (Required)
For each trade row:
- Trade Name
- Trade % of Hard Cost (or of Total Construction Cost -- must be consistent)
- Cost ($)
- Cost/SF ($/SF) (optional but recommended)
- Notes (short, subtype-specific)

**Validation:**
- Trade % must sum to ~100% within tolerance (define tolerance, e.g., +/-0.5%).
- If a trade is not applicable, it must be 0% and show why in Notes.

---

## 3) Trade Distribution Detail (Subtrade / Line Items)
A second-level breakdown that explains what is included.

**Required fields per line item:**
- Item Name (human-readable)
- Quantity (with unit)
- Unit Cost (optional if you model)
- Total Cost
- Provenance tag (what rule/data produced it)

**Subtype divergence requirement:**
- Subtype must explicitly list key line items relevant to that subtype:
  - Industrial: dock packages, slab specs, office buildout if applicable
  - Restaurant: kitchen package, grease trap, hood suppression, seating area finishes
  - Healthcare: imaging equipment, exam rooms, med gases, sterilization
  - Hospitality: rooms/keys packages, FF&E buckets, back-of-house

---

## 4) Construction Schedule + Key Milestones
### 4.1 Schedule Summary
Required fields:
- Total duration (months)
- Phase list (ordered)
- Key milestone table

**Note:** If a type/subtype/project_class lacks a specific timeline template, output must clearly indicate the deterministic fallback used (and emit a trace/provenance entry).

### 4.2 Key Milestones (Required Structure)
Each milestone must include:
- id (snake_case)
- label
- offset_months (integer)
- critical_path (boolean)
- notes (optional)

**Subtype divergence requirement:**
- Hospital vs Urgent Care schedules must differ.
- Fine Dining vs QSR schedules must differ if fit-out complexity differs.
- Industrial cold storage schedule must reflect specialty MEP commissioning.

**Validation:**
- Milestone IDs must be deterministic.
- Milestones must be ordered by offset_months.

---

## 5) Special Features (Explicit adders)
### 5.1 Feature List
For each feature:
- feature_id (canonical string id)
- display_name
- cost impact (absolute or $/SF)
- quantity basis (if applicable)
- provenance (why included -- explicit input vs inferred vs default)

**Rules:**
- Features must never be silently assumed.
- If inferred, must add trace step (feature_inferred) and lower confidence.

---

## 6) Equipment & Fees (Required Categories)
This section must include:
- Equipment (hard equipment)
- FF&E (if applicable)
- Permits/fees (if modeled)
- Testing/commissioning (if applicable)
- IT/controls (if applicable)
- Specialty systems (type/subtype dependent)

**Subtype divergence requirement:**
- Data center equipment and commissioning is not comparable to self-storage.
- Cold storage refrigeration equipment must appear distinctly.

---

## 7) Confidence Band (Global algorithm, subtype-specific drivers)
### 7.1 Confidence Output (Required)
- Confidence label: High / Medium / Low
- Confidence score (0-100) (optional but recommended)
- Drivers list (what increased/decreased confidence)

### 7.2 Confidence Driver Rules
Global drivers (always considered):
- completeness of inputs (SF, location, subtype specificity)
- presence of explicit overrides (good)
- reliance on inference (bad unless traceable)
- presence of regional ambiguity (city-only) (bad -> warning)
- presence of unknown subtype fallback (bad -> warning)

Subtype drivers (must be declared by subtype):
- key operational drivers provided (docks, keys, exam rooms, seats, kW load)
- special feature clarity (explicit vs inferred)
- schedule complexity (higher complexity -> lower confidence without inputs)

**Validation:**
- Any confidence degradation must be traceable in provenance/trace.

---

## 8) Risk Exposure & Notes (Client-readable, subtype-specific)
### 8.1 Risk Exposure (Required categories)
At minimum:
- Cost risk
- Schedule risk
- Market/Revenue risk (if relevant to ConstructionView)
- Design/Scope risk
- Regulatory/Compliance risk (if relevant)
- Operational complexity risk (if relevant)

Each risk must include:
- severity: low/medium/high
- explanation (1-2 sentences)
- mitigation suggestion (short)

### 8.2 Notes
- Must be subtype-aware and not generic.
- Must explain major drivers of cost/complexity.

---

## 9) Provenance Report (Trust anchor)
This is the key trust mechanism: "Where did these numbers come from?"

### 9.1 Required provenance fields
- canonical config reference (building type + subtype key)
- cost_factor and market_factor values and source
- list of overrides applied (explicit)
- list of inferences applied (with trace step IDs)
- special features list and why included
- any clamps applied (restaurant clamp etc.) with trace

### 9.2 Provenance formatting rule
Provenance must clearly distinguish:
- explicit user inputs
- deterministic defaults
- deterministic inferences
- policy clamps/guards

**Validation:**
- If clamp/override/inference happened, it must appear in both trace and provenance.

---

# Acceptance Criteria (for any subtype Build.md)
A subtype is not "done" until:
1) Trade Summary rows are populated and reflect subtype reality
2) Trade Distribution includes subtype-specific key line items
3) Schedule + milestones reflect subtype reality
4) Special features and equipment/fees are subtype-appropriate
5) Confidence band drivers are correctly applied
6) Risk exposure notes are subtype-specific
7) Provenance report makes it obvious why the output is trustworthy
