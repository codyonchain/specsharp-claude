# Core Integrator Build.md (Agent Work Order)

## Agent
- Core Integrator Agent ID:
- Date:
- Branch (required): codex/<date>/core-<topic>-<agent-id>

## Mission (one sentence)
Implement the smallest possible cross-subtype engine change safely, preserving determinism and trust, with parity harness validation and traceability guarantees.

---

# Required Context (must read first)
## Global contracts
- docs/library/taxonomy_contract.md
- docs/library/aliases.md
- docs/agents/agents.md
- docs/agents/lane_rules.md
- docs/agents/traceability.md
- docs/agents/decision_models.md
- docs/agents/core_change_request.md
- docs/agents/engine_intake_agent.md
- docs/library/constructionview_contract.md
- docs/library/executiveview_contract.md
- docs/library/subtype_spec_checklist.md

## Drift + alarms
- python3 scripts/audit/verify_taxonomy_sync.py
- python3 scripts/audit/fingerprint_all.py

---

# Scope Boundaries (allowed files)
## Allowed (Core Integrator lane)
- backend/app/v2/engines/unified_engine.py
- backend/app/v2/api/scope.py (only if required for trace or contract)
- backend/app/services/nlp_service.py (only if canonical taxonomy/detection requires it)
- backend/app/core/building_taxonomy.py (strictness/normalization behavior)
- backend/app/v2/config/master_config.py (aggregation only; not subtype values)
- backend/app/v2/config/config_types.py (schema changes only)
- scripts/audit/** (parity harness, drift checks)
- tests/** (regression + parity tests)

## Forbidden unless explicitly approved
- Editing subtype numeric parameters across many files in one PR (must be coordinated)
- Changing canonical taxonomy keys without updating generator + verify scripts

---

# Non-Negotiable Invariants
1) Determinism preserved: no randomness, no hidden defaults.
2) Taxonomy strictness enforced (Option M):
   - type STRICT (unknown type errors)
   - subtype LENIENT fallback with warning trace
3) Traceability:
   - every override/clamp/inference must emit calculation_trace breadcrumb
   - trace step IDs must come from the trace registry (no ad-hoc IDs)
4) Behavior-preserving refactors must prove parity via parity harness
5) No silent behavior drift: fingerprints must still pass

---

# CCR Intake (if applicable)
If this work is driven by a Core Change Request (CCR), include:
- CCR ID/path:
- Requester:
- Problem statement:
- Evidence (failing tests/repro):
- Approved scope:
- Approved behavior change (YES/NO):

---

# Task Specification (MUST COMPLETE)

## A) What is changing (explicit)
- Files to change:
- What behavior changes:
- What behavior must remain identical:

## B) Why engine change is necessary (vs config/type)
- Explain why subtype config or type profile cannot solve it.

## C) Minimal patch strategy
- Smallest diff that achieves goal.
- No refactors unrelated to the goal.

---

# Core Integrator Patterns (Common Tasks)

## Pattern 1 -- Replace hardcoded subtype lists with config-driven selectors
Goal: move constants/selectors into config, keep formulas in engine.
Example conversions:
- industrial_shell_subtypes -> cfg.scope_profile == "industrial_shell"
- restaurant clamps -> cfg.cost_clamp (min/max/exclusions)
- healthcare outpatient lists -> cfg.facility_metrics_profile == "healthcare_outpatient"
- manufacturing exclusions -> cfg.exclude_from_facility_opex

## Pattern 2 -- Trace registry alignment
- Ensure docs and code use the same trace step IDs.
- Add tests for required trace emission.

## Pattern 3 -- Parity harness + fixtures
- Define canonical fixture inputs for affected areas.
- Compare key outputs before/after changes.
- Block merge if parity fails (unless behavior change is approved).

---

# Parity Harness Requirements (Mandatory for behavior-preserving work)

## Fixture Set (must define)
For each impacted subtype or selector change, include a minimal JSON fixture:
- industrial: warehouse, flex_space, cold_storage
- restaurant: full_service, quick_service
- healthcare outpatient: imaging_center, urgent_care, surgical_center, medical_office_building
- manufacturing: manufacturing
(Adjust based on CCR scope)

## Parity Checks (must define)
Compare at least:
- totals (total_project_cost, cost_per_sf)
- recommendation outcome (GO/NO-GO/NEEDS WORK)
- key KPIs (model-class appropriate)
- trace presence for relevant steps
- confidence band label/drivers (if available)

## Output Comparison Policy
- Behavior-preserving: must match exactly (or within defined tolerance).
- Behavior change approved: must document expected diffs and update goldens/tests.

---

# Acceptance Tests (Required)
Run and report:

## Drift/structure gates
- python3 scripts/audit/verify_taxonomy_sync.py
- python3 scripts/audit/fingerprint_all.py

## Parity harness (if applicable)
- python3 scripts/audit/compare_engine_outputs.py (or whatever parity script is named)

## Targeted tests
- pytest selection relevant to CCR/feature (list exact files/tests)

If tests are not run, state why (should be rare for core integrator).

---

# Output Requirements (Mandatory)
At end of work, output:
- Summary (<=5 bullets)
- Risk / blast radius
- Commands run
- git status
- git diff --stat
- git diff

---

# Core Integrator Checklist (Must Complete)
- Stayed inside approved scope
- Determinism preserved
- Taxonomy policy respected (Option M)
- Traceability preserved/expanded with registry IDs
- Fingerprints pass
- Parity harness passes (or behavior change approved + documented)
- Regression tests added/updated as needed
- Diff proof printed
