# Subtype Build.md (Agent Work Order)

## Agent
- Agent ID:
- Date:
- Branch (required): codex/<date>/<type>-<subtype>-<agent-id>

## Target
- Building Type (canonical v2 key):
- Subtype (canonical v2 key):

## Mission (one sentence)
Make this subtype output client-trustworthy and **distinct** by fully specifying decision model, KPIs, construction trade detail, milestones, trust/assumptions, and provenance requirements--without hidden defaults.

---

# Required Context (must read first)
## Global contracts
- docs/library/taxonomy_contract.md
- docs/library/aliases.md
- docs/agents/agents.md
- docs/agents/lane_rules.md
- docs/agents/traceability.md
- docs/agents/decision_models.md
- docs/library/constructionview_contract.md
- docs/library/executiveview_contract.md
- docs/library/subtype_spec_checklist.md

## Type + subtype docs
- docs/building_types/<type>/BuildingType.md
- docs/building_types/<type>/subtypes/<subtype>.md

---

# Scope Boundaries (allowed files)
## Allowed (Subtype Owner lane)
- backend/app/v2/config/subtypes/<type>/<subtype>.py
- docs/building_types/<type>/subtypes/<subtype>.md
- docs/builds/<date>/<agent-id>-<type>-<subtype>.Build.md
- tests scoped to this subtype only (if authorized): tests/** (list exact paths)

## Forbidden (requires CCR / core integrator)
- backend/app/v2/engines/unified_engine.py
- backend/app/v2/api/scope.py
- backend/app/services/nlp_service.py
- backend/app/core/building_taxonomy.py
- backend/app/v2/config/master_config.py (aggregation only; no subtype edits)
- shared/building_types.json or backend/shared/building_types.json (generated artifacts)

---

# Non-Negotiable Invariants
1) Deterministic math only. No randomness.
2) Explicit overrides always win (0% office / 0 docks / 0 mezz / etc.).
3) Traceability required: any override/clamp/inference must emit a trace breadcrumb.
4) Taxonomy strictness (Option M):
   - Building type STRICT: unknown type must error (no silent coercion).
   - Subtype LENIENT: unknown subtype must deterministically fall back and emit warning trace.
5) Regional is global: cost_factor and market_factor rules must not be localized in subtype.

---

# Subtype Spec Blocks (MUST COMPLETE)
You must fully fill Blocks A--D below. No "use defaults" unless explicitly declared.

## Block A -- Decision & KPI Spec (ExecutiveView)
### A1) Model Declaration
- model_class: NOI / Operating / Throughput / Public-feasibility / Mixed
- valuation_mode: cap_rate / payback / hybrid / none
- decision_profile_id: <string>

### A2) KPI Set (ordered list, 3--7)
List each KPI:
- id:
- label:
- unit:
- definition:
- provenance (what config field or derived formula produces it):

### A3) Recommendation Gates
Define GO / NEEDS WORK / NO-GO gates:
- gate metric id:
- threshold(s):
- rationale:
- trace requirement:

### A4) Recommendation Copy Profile
Provide:
- GO headline template:
- NEEDS WORK headline template:
- NO-GO headline template:
- top-3 rationale bullets template:
- playbook "what to improve" hooks:

---

## Block B -- Construction Spec (ConstructionView)
### B1) Trade Summary Spec
- trade_distribution_profile_id OR explicit trade percentages:
- required emphasized trades:
- required reduced/zero trades:
- explanation of subtype divergence:

### B2) Signature Line Items (must appear)
List signature items:
- item name:
- unit + quantity derivation:
- inclusion condition (explicit/default/inferred):
- provenance requirement:

### B3) Special Features Spec
- allowed feature_ids:
- default features (if any):
- inferred features (if any) + trace + confidence impact:
- pricing/adders + provenance:

### B4) Equipment & Fees Spec
- required equipment buckets:
- required fee categories:
- subtype-specific adders:

### B5) Schedule & Milestones Spec
- schedule_profile_id OR explicit milestone list:
- critical milestones:
- commissioning milestones (if relevant):
Milestone format:
- id / label / offset_months / critical_path

---

## Block C -- Assumptions & Trust Spec
### C1) Subtype Assumptions Table
Include:
- driver name + unit
- default value (if any) + why acceptable
- range/band
- missing input behavior (confidence impact + trace)

### C2) Confidence Band Drivers
- what raises confidence:
- what lowers confidence:
- required warnings (city-only, fallback, inferred drivers):

### C3) Risk Exposure Notes
Provide risk notes per category:
- cost risk (severity + mitigation)
- schedule risk (severity + mitigation)
- market/revenue risk (severity + mitigation)
- operational complexity (severity + mitigation)
- regulatory/compliance (if relevant)

---

## Block D -- Provenance Spec
### D1) Required Trace Steps
List required trace step IDs for:
- overrides
- inference
- clamps
- profile selectors

### D2) Provenance Report Requirements
Must explicitly explain:
- cost_factor and market_factor used and their sources
- all overrides/inferences/clamps (with trace ids)
- special features included and why
- any fallback subtype usage and why (unknown_subtype_fallback)

---

# Deltas vs Type Defaults (Mandatory)
List what differs from the type template. If "none," state why.
- Decision/KPIs deltas:
- Trade distribution deltas:
- Schedule/milestone deltas:
- Features/equipment deltas:
- Risk/trust deltas:

---

# Acceptance Tests (required)
## Required gates (must run unless explicitly waived)
- python3 scripts/audit/verify_taxonomy_sync.py
- python3 scripts/audit/fingerprint_master_config.py

## Subtype-specific checks (choose or add)
- invariant tests for trace steps relevant to this subtype
- golden case(s) for this subtype (optional until parity harness phase)

**If tests are not run, state why.**

---

# Output Requirements (mandatory)
At the end of your work, output:
- Summary (<=5 bullets)
- Risks / blast radius (what else could be impacted)
- Commands run
- git status
- git diff --stat
- git diff

---

# Agent Checklist (must complete)
- Scope boundary respected (only allowed files changed)
- Determinism preserved (no hidden defaults)
- Overrides honored (explicit inputs win)
- Traceability added/kept (required steps present)
- Taxonomy contract respected (type strict, subtype fallback warning)
- Subtype distinctness achieved (KPIs/trades/milestones are subtype-specific)
- Provenance requirements satisfied
- Acceptance tests listed (run or explicitly waived)
- Diff proof printed
