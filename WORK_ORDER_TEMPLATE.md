# WORK_ORDER_TEMPLATE.md

## Purpose
Standardized implementation plan generated from audit outputs so engineers and Codex can execute safely, predictably, and traceably.

## Usage
1) Complete audit first per `/Users/codymarchant/Documents/Projects/specsharp-claude/AUDIT_PROCESS.md`.
2) Fill this template using audit evidence.
3) Execute only within approved scope.
4) Validate against `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md` and `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`.

Do not begin implementation until all required fields are complete. If any required field is unknown, set `UNKNOWN` with blocker note and halt execution.

---

## 1) Work Order Header
- Work Order ID:
- Date:
- Author:
- Repo Root: `/Users/codymarchant/Documents/Projects/specsharp-claude`
- Branch:
- Commit SHA (start):
- Source Audit Reference:
- Change Size: `small | medium | large`
- Risk Level: `low | medium | high`

Sizing expectations:
- `small`: single-area change, minimal blast radius, concise step list.
- `medium`: multi-file same subsystem, explicit dependency checks.
- `large`: cross-subsystem change, phased execution and rollback checkpoints.

## 2) Objective
- Business goal:
- Technical goal:
- Non-goals:

## 3) Scope Control
### In-Scope Files (Allowed to Edit)
(List absolute file paths only)

### Out-of-Scope Files (Must Not Edit)
(List absolute file paths only)

### Scope Guardrails
- No edits outside In-Scope Files.
- If additional file is needed, stop and re-audit.
- No opportunistic refactors unless explicitly listed.
- Allowed-files-only rule is mandatory for all execution steps and checks.

## 4) Evidence Basis
For each key decision, cite:
- Claim:
- Evidence: `/absolute/path:line`
- Confidence: `high | medium | low`
- Notes:

Evidence requirements:
- Use only absolute-path citations with 1-based line number.
- No decision may rely on unstated assumptions.

## 5) Impact Map
- Routes/pages impacted:
- Components impacted:
- Services/helpers/hooks impacted:
- Backend/API/config impacted:
- Legacy surfaces touched? `yes/no` (if yes, explain)

## 6) Invariant Compliance Plan
Reference `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md`.

Create a table:
- Invariant ID
- Severity
- Status at Start (`PASS|FAIL|UNKNOWN`)
- How this work order preserves it
- Required proof artifact

| Invariant ID | Severity | Status at Start (`PASS|FAIL|UNKNOWN`) | How this work order preserves it | Required proof artifact |
|---|---|---|---|---|
| | | | | |

Blockers:
- List any invariant that must be resolved before implementation starts.
- If any `P0` is `FAIL` or any in-scope invariant is `UNKNOWN`, halt execution.

## 7) Execution Plan (Ordered Steps)
For each step include:
- Step #:
- File(s):
- Exact change intent:
- Why:
- Risk:
- Pre-check:
- Post-check:
- Stop condition (what triggers halt/re-audit):

Step template (repeat as needed):
- Step #:
- File(s): (absolute paths; must be in In-Scope Files)
- Exact change intent:
- Why:
- Risk:
- Pre-check:
- Post-check:
- Stop condition (what triggers halt/re-audit):

Require strict ordering and minimal blast radius.

## 8) Test Gate Plan
Reference `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`.

For each required gate include:
- Gate ID:
- Severity (`P0|P1|P2`)
- Command or Manual Check:
- Expected Result:
- Failure Action:

Include:
- Required automated checks
- Required critical smoke checks
- Numeric lineage verification checks (if numbers affected)

Gate enforcement rules:
- Commands/manual checks must map directly to matrix gates.
- Every gate must have explicit pass/fail evidence.
- Any failed required gate blocks completion.

## 9) Acceptance Criteria
Define measurable outcomes:
- Functional criteria:
- Data/numeric correctness criteria:
- UX criteria:
- Contract compatibility criteria:
- Performance criteria (if applicable):

Each criterion must be testable and binary pass/fail.
No criterion may be subjective; rewrite ambiguous language before execution.

## 10) Rollback Plan
- Rollback trigger conditions:
- Rollback method:
- Data/API compatibility considerations:
- Verification after rollback:

Rollback plan is mandatory. Do not execute implementation without explicit trigger conditions and post-rollback verification steps.

## 11) Implementation Constraints
- No extra files beyond in-scope.
- No silent behavior changes outside objective.
- No contract breaks unless explicitly declared.
- If unexpected repo state appears, stop and escalate.

## 12) Reporting Format During Execution
Require status updates in this format:
- Current step:
- Files touched:
- Checks run:
- Results:
- Blockers:

## 13) Completion Record
To be filled after implementation:
- Commit SHA (end):
- Files actually changed:
- Gate results summary:
- Smoke check summary:
- Invariant re-check summary:
- Residual risks:
- Follow-up tasks:

## 14) Sign-off
- Implementer:
- Reviewer:
- Approved for merge: `yes/no`
- Notes:

---

## Quick Fill Checklist
- [ ] Header complete
- [ ] Allowed files explicit
- [ ] Evidence citations attached
- [ ] Invariants mapped
- [ ] Test gates mapped
- [ ] Acceptance criteria measurable
- [ ] Rollback defined
- [ ] Stop conditions defined
