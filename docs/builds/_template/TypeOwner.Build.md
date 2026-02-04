# Type Owner Build.md (Agent Work Order)

## Agent
- Type Owner Agent ID:
- Date:
- Branch (required): codex/<date>/type-owner-<type>-<agent-id>

## Target
- Building Type (canonical v2 key):
- Type Owner Module:
  - backend/app/v2/config/profiles/<type>.py (future)
  - or current type-level constants in master_config.py (transitional only)

## Mission (one sentence)
Maintain and improve the type-level underwriting contract and profiles so all subtypes remain consistent, defensible, and client-trustworthy--without flattening subtype distinctness.

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

## Type docs
- docs/building_types/<type>/BuildingType.md
- docs/agents/DEV_VERIFY.md
- docs/agents/PRE_DEPLOY.md

---

# Scope Boundaries (allowed files)
## Allowed (Type Owner lane)
- docs/building_types/<type>/BuildingType.md
- docs/building_types/<type>/subtypes/*.md (only if editing type-level guidance text; avoid subtype values)
- docs/builds/<date>/<agent-id>-type-owner-<type>.Build.md
- backend/app/v2/config/profiles/<type>.py (once profiles are sharded)
- type-level tables owned by this type (when migrated)

## Forbidden (requires CCR / core integrator)
- backend/app/v2/engines/unified_engine.py
- shared parsing/detection logic
- subtype config modules (backend/app/v2/config/subtypes/**) unless explicitly approved
- shared/building_types.json or backend/shared/building_types.json (generated)
- backend/app/v2/config/master_config.py beyond aggregation/ordering (unless explicitly authorized)

---

## Timeline Coverage Responsibilities (Type Owner Lane)

### Why this exists
PROJECT_TIMELINES is a type-level schedule model used to power Key Milestones / Construction Schedule in outputs.
After sharding PROJECT_TIMELINES into type-owner modules, we must fill coverage intentionally (this is a behavior change and must be done in a dedicated commit).

## Margin Coverage Responsibilities (Type Owner Lane)

### Why this exists
MARGINS is a type-level default operating margin used as a fallback when subtype-specific margins are not provided.
After sharding MARGINS into type-owner modules, missing types must be filled intentionally (this is a behavior change and must be done in a dedicated commit).

### Required coverage
- Provide a margin value for this building type (even if it’s a placeholder baseline).
- Document whether subtype configs override this default (operating_margin_base/premium) and under what conditions.

### Operator checks
- python3 scripts/audit/fingerprint_margins.py
- python3 scripts/audit/fingerprint_all.py


### Required coverage (post-shard follow-on)
- ground_up (required baseline)
- renovation (if supported by engine; otherwise add as TODO with explicit fallback note)
- addition (if supported)
- tenant_improvement (if supported)

### Acceptance criteria
- No silent fallback: timeline selection must be explicit and traceable.
- Milestone list shape matches contract requirements (id/label/offset_months) and preserves ordering.
- For missing project classes, document deterministic fallback behavior (and add TODO with owner + target milestone/date).

### Operator checks (run before merge)
- python3 scripts/audit/fingerprint_project_timelines.py
- python3 scripts/audit/fingerprint_all.py

### Coverage audit (run to see gaps)
- Grep where PROJECT_TIMELINES is defined/consumed and list missing types/classes.
- Record missing coverage as a tracked TODO in the type owner Build.md for the next pass.

---

# Non-Negotiable Invariants
1) Do not collapse subtype distinctness:
   - Type-level defaults may exist, but subtype must own its deltas and its KPI/trade/milestone spec.
2) Taxonomy contract enforced (Option M):
   - Type STRICT, subtype fallback warning + deterministic default subtype.
3) Regional logic is global:
   - cost_factor/market_factor logic must remain global, not per subtype.
4) Traceability:
   - type-level profiles that affect outputs must emit trace breadcrumbs (where applicable).

---

# Type Contract Specification (MUST COMPLETE)

## A) Model Contract (Type-level)
- model_class default for this type: NOI / Operating / Throughput / Public-feasibility / Mixed
- Is this a multi-model bucket type?
  - YES/NO
  - If YES: which subtypes must declare model_class explicitly?

## B) Required Modules (ExecutiveView)
For this type, list required modules and which are optional:
- Trust & assumptions: required
- Investment decision: required
- Revenue projections: required (model-class dependent)
- Facility metrics template: required (type template)
- Financing structure: required (if applicable)
- Quick sensitivity: required
- Key milestones: required
- Operational efficiency: required (model-class dependent)
- Prescriptive playbook: required (type template + subtype deltas)

## C) Required Modules (ConstructionView)
- Trade Summary: required
- Trade Distribution detail: required
- Schedule + milestones: required
- Special features: required (type-approved feature categories)
- Equipment & fees: required (type buckets)
- Confidence band: required (global algorithm; type declares driver categories)
- Risk exposure + notes: required
- Provenance report: required

## D) KPI Template (Type-level)
Define a *template* KPI set for subtypes to override:
- baseline KPIs for the type
- allowed KPI variants
- rules preventing wrong-model KPIs (e.g., no cap-rate valuation for operating business types)

## E) Risk Template (Type-level)
Define type-level risk categories and typical drivers:
- cost/schedule/market/ops/compliance
- what must always be called out

---

# Type Profile / Knobs (MUST COMPLETE)
These are type-level settings owned by this agent (not subtype-specific values).

## A) Type-level profile fields (examples)
- target ROI bands (if applicable)
- DSCR targets (if applicable)
- typical cap-rate bands (NOI types)
- financing assumptions bands
- default confidence driver weighting categories

## B) What subtypes must override
List which subtypes must explicitly override defaults and why.

---

# Guardrails Against "Flattening"
You must include:
- A list of "allowed defaults" (safe, structural)
- A list of "never default globally" items (must be subtype-owned)
Examples of never-default:
- restaurant KPI set
- healthcare throughput drivers
- cold storage refrigeration assumptions
- subtype-specific trade splits
- subtype-specific milestones

---

# Acceptance Tests (required)
- python3 scripts/audit/verify_taxonomy_sync.py
- python3 scripts/audit/fingerprint_master_config.py
(Optional depending on what changed)
- python3 scripts/audit/fingerprint_building_profiles.py
- python3 scripts/audit/fingerprint_all.py

If tests are not run, state why.

---

# Output Requirements (mandatory)
At end of work:
- Summary (<=5 bullets)
- Cross-subtype blast radius (which subtypes are affected and why)
- Commands run
- git status
- git diff --stat
- git diff

---

# Type Owner Checklist (must complete)
- Stayed inside type-owner scope
- Did not edit subtype-owned numeric parameters unless explicitly authorized
- Preserved subtype distinctness (no flattening)
- Model contract is correct and documented
- View contracts are satisfied (ExecutiveView + ConstructionView)
- Taxonomy contract respected (strict type, lenient subtype fallback policy)
- Tests listed (run or explicitly waived)
- Diff proof printed
