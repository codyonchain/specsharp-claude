# INVARIANTS.md

## Purpose
This file defines non-negotiable rules that must hold before, during, and after any code change.
If any `P0` invariant fails, the change is blocked.

## How To Use
1. Run preflight checks first.
2. Map intended change to `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md`.
3. Evaluate all invariants below.
4. Record `PASS | FAIL | UNKNOWN` with evidence (`file:line`, command output).
5. Only proceed to implementation if all `P0` pass and no unresolved `UNKNOWN` remains for impacted areas.

## Severity Model
- `P0`: Release blocker.
- `P1`: Must be resolved before merge.
- `P2`: Important quality guardrail; may proceed only with explicit approval and risk note.

---

## Invariants

### Repo / Process

**INV-P0-001: Repo Identity Lock**
- Rule: `pwd` and `git rev-parse --show-toplevel` must both equal `/Users/codymarchant/Documents/Projects/specsharp-claude`.
- Why: Prevents auditing or editing the wrong project.
- Verify: command output.

**INV-P0-002: Scope Lock Before Edits**
- Rule: No file edits until impacted files are identified and justified with evidence from `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md`.
- Why: Prevents random-file edits.
- Verify: audit report contains explicit in-scope file list with reasons.

**INV-P1-003: Worktree Transparency**
- Rule: Current branch, commit SHA, and `git status --short` must be recorded before audit and before implementation.
- Why: Prevents hidden drift and misattribution.
- Verify: audit header includes all three.

### Architecture / Ownership

**INV-P0-004: Every Claim Must Have Evidence**
- Rule: Non-trivial architectural claims must include `file:line` evidence.
- Why: Eliminates guesswork.
- Verify: audit and work order include citations.

**INV-P0-005: Active vs Legacy Must Be Explicit**
- Rule: Components/routes/configs in scope must be labeled `Active | Legacy | Uncertain`.
- Why: Avoids editing dead paths or wrong implementations.
- Verify: labels present for each mapped item.

**INV-P1-006: No Unresolved Uncertainty in Edited Areas**
- Rule: Any `Uncertain` item touching intended change scope must be resolved before coding.
- Why: Prevents wrong-target changes.
- Verify: no unresolved `Uncertain` in in-scope paths.

### Routing / UI

**INV-P0-007: Route-to-Page Ownership**
- Rule: Every changed page must map to concrete route definitions and owning page/component files.
- Why: Prevents “changed component but wrong route”.
- Verify: route -> page -> component chain with evidence.

**INV-P1-008: Shared Component Impact Check**
- Rule: If editing shared UI components, list all known consuming routes/pages.
- Why: Prevents silent regressions.
- Verify: dependency usage evidence in audit.

### Numeric / Domain Logic

**INV-P0-009: Numeric Lineage Completeness**
- Rule: For each changed user-visible number, lineage must be traceable end-to-end:
  UI -> component -> helper/hook/service -> API/config -> formula/default.
- Why: Prevents incorrect business outputs.
- Verify: complete lineage map with evidence.

**INV-P0-010: No Undocumented Hardcoded Business Constants**
- Rule: Business-critical numeric constants in UI/frontend/backend must be sourced from approved config or explicitly documented in RepoMap and PR notes.
- Why: Prevents hidden divergence.
- Verify: grep/find checks and citation review.

**INV-P1-011: Unit and Timeframe Consistency**
- Rule: Values must preserve units/timeframe semantics (per SF, per unit, monthly vs annual) across transforms and displays.
- Why: Prevents silently wrong math.
- Verify: mapping notes + test assertions.

**INV-P1-012: Deterministic Rounding Rules**
- Rule: Rounding/formatting occurs in one defined layer and is consistent across views.
- Why: Prevents inconsistent totals across pages.
- Verify: evidence of rounding location and test coverage.

### API / Contract

**INV-P0-013: API Contract Compatibility**
- Rule: Response shape consumed by frontend for in-scope pages must remain compatible, or all consumers must be updated in same work order.
- Why: Prevents runtime breaks.
- Verify: contract diff + consumer list.

**INV-P1-014: Backward Compatibility Declaration**
- Rule: Any intentional contract break must be declared in work order with migration steps.
- Why: Prevents accidental breakage.
- Verify: explicit “breaking change” section.

### Validation / Testing

**INV-P0-015: Required Checks Must Pass**
- Rule: All required checks from `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md` for impacted subsystems must pass.
- Why: Prevents unvalidated merges.
- Verify: command list + pass/fail results.

**INV-P1-016: Critical Path Smoke Validation**
- Rule: Changed user paths (e.g., new project, project details, executive/construction/deal views) must have explicit smoke verification steps.
- Why: Prevents obvious runtime regressions.
- Verify: smoke checklist results.

**INV-P2-017: Performance Regression Guard**
- Rule: Changes on critical render/data paths must include quick regression check (load time/query count/render churn) when applicable.
- Why: Prevents gradual UX degradation.
- Verify: measured before/after note.

---

## Audit Decision Rule
- Block if any `P0` = `FAIL`.
- Block if any in-scope item = `UNKNOWN`.
- Block if evidence is missing for key claims.
- Proceed only when all `P0` pass and required test gates pass.

## Required Audit Output Fields
- Repo root, branch, commit SHA, worktree state.
- In-scope files and out-of-scope files.
- Invariant results table (`ID`, `Status`, `Evidence`, `Notes`).
- Risk summary and confidence score.
- Work order draft tied to verified invariants.
