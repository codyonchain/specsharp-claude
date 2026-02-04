# ConstructionView Contract (Global)

**Contract ID:** ConstructionView Contract  
**Version:** v1.1  
**Last updated:** February 4, 2026  
**Owner lane:** Type Owner + Core Integrator  
**Change log:**
- v1.1: Added explicit required sections list, validation checklist, deterministic fallback provenance rule, and explicit milestone object shape; tightened normative language; added concise examples.
- v1.0: Initial global contract.

## Purpose
ConstructionView MUST provide a client-trustworthy, deterministic, and explainable output for a single project. This contract MUST enforce a consistent structure while allowing subtype-specific divergence (trade %, line items, milestones, features, risk notes).

## Ownership Model
- Global contract (this document) MUST define structure, required fields, and validation rules.
- Type Owner MUST provide type-level defaults/templates (trade distribution template, schedule template, equipment categories).
- Subtype Owner MUST provide subtype-specific trade summary content, trade distributions, feature lists, equipment/fees, milestone deltas, and notes.

## Determinism Rules (Non-Negotiable)
1. No hidden assumptions: defaults MUST be explicit and explainable.
2. Explicit overrides MUST always win (0% office / 0 docks / 0 mezz / etc.).
3. Any override, clamp, or inference MUST produce a `calculation_trace` breadcrumb.
4. Regional multipliers MUST be global (cost_factor/market_factor) and MUST NOT be localized per subtype outside the canonical system.

---

## Required Sections (Explicit List)
The ConstructionView output MUST include these sections, in order:
1. Project Summary Header
2. Trade Summary
3. Trade Distribution Detail
4. Construction Schedule + Key Milestones
5. Special Features
6. Equipment & Fees
7. Confidence Band
8. Risk Exposure & Notes
9. Provenance Report

---

# Required Sections (ConstructionView)

## 1) Project Summary Header
**Required fields (MUST include):**
- Building Type (canonical v2 key)
- Subtype (canonical v2 key)
- Location (City, ST)
- Project Class (ground_up / tenant_improvement / renovation etc.)
- Square Footage (GSF)
- Version / Timestamp
- Confidence Band (see section 7)

**Validation (MUST pass):**
- Building type MUST be canonical; unknown type is an error.
- Unknown subtype MUST deterministically fall back with a warning trace (`unknown_subtype_fallback`).

---

## 2) Trade Summary (Core Output)
This MUST look like something a GC/Owner would recognize.

### 2.1 Trade List (Required)
Trade Summary MUST include at minimum these trade categories (even if zeroed):
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

**Subtype divergence requirement (MUST):**
- Percent splits and line items MUST differ by subtype when reality differs.
- Examples: Cold Storage MUST show higher Mechanical/Electrical and Equipment; Fine Dining MUST show higher Finishes and Kitchen/MEP complexity than QSR.

### 2.2 Trade Summary Columns (Required)
For each trade row, output MUST include:
- Trade Name
- Trade % of Hard Cost (or of Total Construction Cost; MUST be consistent)
- Cost ($)
- Cost/SF ($/SF) (SHOULD include)
- Notes (short, subtype-specific)

**Validation (MUST pass):**
- Trade % MUST sum to ~100% within tolerance (define tolerance, e.g., +/-0.5%).
- If a trade is not applicable, it MUST be 0% and MUST state why in Notes.

---

## 3) Trade Distribution Detail (Subtrade / Line Items)
This MUST explain what is included.

**Required fields per line item (MUST include):**
- Item Name (human-readable)
- Quantity (with unit)
- Unit Cost (MAY omit if you do not model)
- Total Cost
- Provenance tag (rule/data source)

**Subtype divergence requirement (MUST):**
- Subtype MUST explicitly list key line items relevant to that subtype:
  - Industrial: dock packages, slab specs, office buildout if applicable
  - Restaurant: kitchen package, grease trap, hood suppression, seating area finishes
  - Healthcare: imaging equipment, exam rooms, med gases, sterilization
  - Hospitality: rooms/keys packages, FF&E buckets, back-of-house

---

## 4) Construction Schedule + Key Milestones
### 4.1 Schedule Summary (Required)
Output MUST include:
- Total duration (months)
- Phase list (ordered)
- Key milestone table

**Fallback rule (MUST):**
If a type/subtype/project_class lacks a specific timeline template, output MUST show the deterministic fallback used and MUST emit a trace/provenance entry documenting the fallback.

### 4.2 Key Milestones (Required Structure)
Each milestone object MUST have this shape:
- `{id, label, offset_months}`

Additional fields MAY be present, but these three MUST exist.

**Subtype divergence requirement (MUST):**
- Hospital vs Urgent Care schedules MUST differ.
- Fine Dining vs QSR schedules MUST differ if fit-out complexity differs.
- Industrial cold storage schedule MUST reflect specialty MEP commissioning.

**Validation (MUST pass):**
- Milestone IDs MUST be deterministic.
- Milestones MUST be ordered by `offset_months`.

---

## 5) Special Features (Explicit Adders)
### 5.1 Feature List
For each feature, output MUST include:
- `feature_id` (canonical string id)
- `display_name`
- cost impact (absolute or $/SF)
- quantity basis (if applicable)
- provenance (explicit input vs inferred vs default)

**Rules (MUST):**
- Features MUST NEVER be silently assumed.
- If inferred, output MUST add a trace step (`feature_inferred`) and SHOULD lower confidence.

---

## 6) Equipment & Fees (Required Categories)
This section MUST include:
- Equipment (hard equipment)
- FF&E (if applicable)
- Permits/fees (if modeled)
- Testing/commissioning (if applicable)
- IT/controls (if applicable)
- Specialty systems (type/subtype dependent)

**Subtype divergence requirement (MUST):**
- Data center equipment and commissioning MUST differ from self-storage.
- Cold storage refrigeration equipment MUST appear distinctly.

---

## 7) Confidence Band (Global Algorithm, Subtype-Specific Drivers)
### 7.1 Confidence Output (Required)
Output MUST include:
- Confidence label: High / Medium / Low
- Confidence score (0-100) (SHOULD include)
- Drivers list (what increased/decreased confidence)

### 7.2 Confidence Driver Rules
Global drivers (MUST be considered):
- completeness of inputs (SF, location, subtype specificity)
- presence of explicit overrides (good)
- reliance on inference (bad unless traceable)
- presence of regional ambiguity (city-only) (bad -> warning)
- presence of unknown subtype fallback (bad -> warning)

Subtype drivers (MUST be declared by subtype):
- key operational drivers provided (docks, keys, exam rooms, seats, kW load)
- special feature clarity (explicit vs inferred)
- schedule complexity (higher complexity -> lower confidence without inputs)

**Validation (MUST pass):**
- Any confidence degradation MUST be traceable in provenance/trace.

---

## 8) Risk Exposure & Notes (Client-Readable, Subtype-Specific)
### 8.1 Risk Exposure (Required Categories)
At minimum, output MUST include:
- Cost risk
- Schedule risk
- Market/Revenue risk (if relevant to ConstructionView)
- Design/Scope risk
- Regulatory/Compliance risk (if relevant)
- Operational complexity risk (if relevant)

Each risk MUST include:
- `severity` (low/medium/high)
- explanation (1-2 sentences)
- mitigation suggestion (short)

### 8.2 Notes
- Notes MUST be subtype-aware and not generic.
- Notes MUST explain major drivers of cost/complexity.

---

## 9) Provenance Report (Trust Anchor)
This is the key trust mechanism: "Where did these numbers come from?"

### 9.1 Required provenance fields
Output MUST include:
- canonical config reference (building type + subtype key)
- `cost_factor` and `market_factor` values and source
- list of overrides applied (explicit)
- list of inferences applied (with trace step IDs)
- special features list and why included
- any clamps applied (restaurant clamp etc.) with trace

### 9.2 Provenance formatting rule
Provenance MUST clearly distinguish:
- explicit user inputs
- deterministic defaults
- deterministic inferences
- policy clamps/guards

**Validation (MUST pass):**
- If clamp/override/inference happened, it MUST appear in both trace and provenance.

---

## Examples (Short)
**Milestone list (one item):**
```json
[{"id":"groundbreaking","label":"Groundbreaking","offset_months":0}]
```

**Trade row (one item):**
```json
{"trade":"Mechanical (HVAC)","pct":0.18,"cost":540000,"notes":"Cold storage refrigeration load"}
```

**Special feature (one entry):**
```json
{"feature_id":"walk_in_freezer","display_name":"Walk-In Freezer","cost_per_sf":45,"provenance":"explicit_input"}
```

---

## Validation Checklist (MUST Pass)
- All required sections are present and ordered as listed.
- Building Type and Subtype are canonical or deterministically fall back with trace.
- Trade Summary includes minimum trade categories and % totals within tolerance.
- Trade Distribution includes subtype-specific key line items and provenance tags.
- Schedule has total duration, phases, and milestones; milestone objects match `{id,label,offset_months}` and are ordered.
- Fallback timeline usage is shown in output and recorded in trace/provenance when applicable.
- Special features are explicit or traced when inferred; no silent additions.
- Equipment & Fees include required categories and subtype distinctions.
- Confidence drivers are listed and any degradation is traceable.
- Risk section includes required categories with severity, explanation, mitigation.
- Provenance distinguishes explicit inputs, defaults, inferences, and clamps.

---

# Acceptance Criteria (for any subtype Build.md)
A subtype is not "done" until ALL of the following are true:
1. Trade Summary rows are populated and reflect subtype reality.
2. Trade Distribution includes subtype-specific key line items.
3. Schedule + milestones reflect subtype reality and obey the milestone shape rule.
4. Special features and equipment/fees are subtype-appropriate.
5. Confidence band drivers are correctly applied and traceable.
6. Risk exposure notes are subtype-specific.
7. Provenance report makes it obvious why the output is trustworthy.
