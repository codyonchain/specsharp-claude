# Build.md (Agent Work Order)

## Agent
- Agent ID:
- Date:
- Branch:

## Mission
One-sentence objective.

## Required Context (must read)
- docs/library/taxonomy_contract.md
- docs/library/aliases.md
- docs/agents/agents.md
- docs/agents/DEV_VERIFY.md

## Scope Boundaries (allowed files)
- <exact file list>

## Do Not Change
- <explicit file list>

## Hard Invariants
- Determinism preserved: no randomness or hidden defaults.
- Overrides honored: explicit inputs override defaults (0% office / 0 docks / 0 mezz, etc.).
- Traceability required: any override/clamp/inference must add a calculation_trace entry.

## Taxonomy Acceptance Rules (Non-Negotiable)

- BuildingType is STRICT:
  - Unknown building types must error (no silent normalization).
  - If trace is available, emit `unknown_building_type` (critical).

- Subtype is LENIENT:
  - Unknown/missing subtype must deterministically fall back to the documented default subtype for that type.
  - Must emit `unknown_subtype_fallback` (warning) with received + fallback values.

- Canonical keys only:
  - All code/config must use canonical v2 keys (per MASTER_CONFIG).
  - Aliases like residential/commercial must be resolved before hitting v2 engine logic.

## Acceptance Tests (DEV_VERIFY scope)
- <list of tests or commands>
- If not run, state why.

## Output Requirements
- Summary (<=5 bullets)
- Risks / blast radius
- Commands run
- git status
- git diff --stat
- git diff

## Agent Checklist (must complete in output)
- Scope boundary respected: List the exact files changed and confirm they are within the allowed scope.
- Determinism preserved: Confirm no new randomness/AI inference; all defaults remain explicit + auditable.
- Overrides honored: Confirm explicit inputs override defaults (0% office / 0 docks / 0 mezz, etc.).
- Traceability added/kept: If you apply any override/clamp/assumption, ensure calculation_trace includes a breadcrumb.
- Cross-subtype blast radius: Name the other subtypes that could be affected and why (or "none" with reasoning).
- Acceptance tests: List which DEV_VERIFY checks you ran (or why not allowed) and expected pass/fail.
- Diff proof: Print git diff --stat and git diff at the end.
- Taxonomy contract respected: Type strictness enforced; subtype fallback deterministic + trace emitted.
