# AUDIT_PROCESS.md

## Purpose
Defines the mandatory pre-build audit workflow for SpecSharp so changes are scoped, evidenced, and test-gated before implementation.

## Scope
Applies to all change requests in:
`/Users/codymarchant/Documents/Projects/specsharp-claude`

## Required Inputs
- `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md`
- `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md`
- `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`

## Non-Negotiable Rules
- Audit mode only: no file edits, no commits.
- Evidence required for non-trivial claims (`absolute-path:line`).
- Uncertainty must be labeled `Uncertain`; no guessing.
- Any failed `P0` invariant or gate blocks implementation.
- Audit must finish with a work-order-ready output.

## Phase 0: Preflight Identity Gate
Required commands and captured outputs:
- `pwd`
- `git rev-parse --show-toplevel`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git status --short`

Pass criteria:
- repo root exact match
- branch/commit/worktree recorded

## Phase 1: Request Normalization
Require audit to capture:
- requested change (plain language)
- business intent
- acceptance criteria
- explicit out-of-scope
- risk tolerance (strict/moderate/fast)

Pass criteria:
- scope and success conditions are unambiguous.

## Phase 2: RepoMap Grounding
Require:
- search `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md` first
- map request to route/page/component/config/engine areas
- mark each mapped area as Active/Legacy/Uncertain
- include evidence citations

Pass criteria:
- all in-scope areas mapped with evidence.

## Phase 3: Impact & Dependency Mapping
Require:
- list exact likely-impacted files
- list adjacent dependencies (shared components, helpers, API consumers)
- identify blast radius and regression risk areas

Pass criteria:
- in-scope and out-of-scope file lists are explicit.

## Phase 4: Invariant Evaluation
Require:
- evaluate all relevant invariants from `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md`
- record `PASS | FAIL | UNKNOWN` per invariant ID
- provide evidence and notes per invariant

Pass criteria:
- no `FAIL` on `P0`
- no unresolved `UNKNOWN` in in-scope areas

## Phase 5: Test Gate Selection
Require:
- map impacted change categories to `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`
- produce required gates (`P0/P1/P2`) for those categories
- include command list and manual smoke checks
- command list must be copied verbatim from `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`; no added or inferred commands

Pass criteria:
- all required gates identified and justified.
- matrix-derived command list present with no speculative commands.

## Phase 6: Findings & Risk Scoring
Require:
- findings ordered by severity (`P0/P1/P2/P3`)
- each finding includes: title, risk, impact, evidence, recommendation
- overall risk score and confidence score

Pass criteria:
- actionable findings with traceable evidence.

## Phase 7: Work Order Draft Generation
Require output ready for implementation thread:
- objective
- in-scope files only
- out-of-scope files
- step-by-step execution order
- required test gates
- acceptance criteria
- rollback plan
- explicit stop conditions

Pass criteria:
- implementer can execute without guessing.

## Audit Output Schema (Required)
Define exact sections required in every audit response:

1) Audit Header
- repo_root
- branch
- commit_sha
- worktree_state
- audit_scope
- timestamp

2) Impact Map
- in_scope_files
- out_of_scope_files
- dependency_notes
- evidence

3) Invariant Table
- invariant_id
- severity
- status
- evidence
- notes

4) Test Gate Plan
- category_id
- required_gates
- commands/manual checks
- rationale

5) Findings
- severity
- title
- risk
- evidence
- recommendation

6) Work Order Draft
- objective
- files_to_edit
- execution_steps
- acceptance_criteria
- rollback_plan
- stop_conditions

7) Confidence Summary
- coverage_percent
- evidence_density_percent
- confidence_score_10
- open_uncertainties
- blockers

## Decision Rules
- Block implementation if:
- repo identity gate fails
- any `P0` invariant fails
- required `P0` test gate missing
- unresolved in-scope uncertainty remains
- Approve implementation only if:
- scope is explicit
- evidence is sufficient
- required gates are defined
- work order is complete

## Audit Timebox Guidance
Define default timeboxes:
- small change audit: 15–30 min
- medium change audit: 30–60 min
- large/cross-cutting audit: 60–120 min
Require escalation note if timebox exceeded.

## Quality Checklist
Include checklist:
- root verified
- scope clear
- repomap consulted first
- invariants evaluated
- tests mapped
- findings ranked
- work order complete
- confidence reported

## Hand-off Protocol
Define what gets handed to implementation thread:
- full audit output
- approved work order
- allowed files list
- required gates list
- explicit constraints (`no extra files` rule)
