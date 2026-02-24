# AUDIT_REPORT_TEMPLATE.md

## Purpose
Standardized audit report template for pre-build analysis.  
Use this to produce evidence-based findings and a work-order-ready handoff.

## Usage
1) Run audit-only workflow from `/Users/codymarchant/Documents/Projects/specsharp-claude/AUDIT_PROCESS.md`.  
2) Fill all required sections below.  
3) Do not edit code during this report.  
4) If any `P0` fails, mark implementation blocked.

---

## 1) Audit Header
- Audit ID:
- Date/Time:
- Auditor:
- Repo Root:
- Branch:
- Commit SHA:
- Worktree State (`clean|dirty`):
- Audit Scope:
- Change Size (`small|medium|large`):
- Risk Tolerance (`strict|moderate|fast`):

## 2) Preflight Evidence
- `pwd` output:
- `git rev-parse --show-toplevel` output:
- `git branch --show-current` output:
- `git rev-parse HEAD` output:
- `git status --short` summary:
- Identity Gate Result (`PASS|FAIL`):
- Notes:

## 3) Request Normalization
- Requested change (plain language):
- Business intent:
- Acceptance criteria (requested):
- Explicit out-of-scope:
- Assumptions:
- Ambiguities:

## 4) RepoMap Grounding
Map request to `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md`.
- Relevant routes/pages:
- Relevant components:
- Relevant services/helpers/hooks:
- Relevant backend/config areas:
- Classification per item (`Active|Legacy|Uncertain`):
- Evidence (`/absolute/path:line`):

## 5) Impact Map
### In-Scope Files (likely impacted)
- `/absolute/path` — reason — evidence

### Out-of-Scope Files
- `/absolute/path` — reason

### Dependency / Blast Radius Notes
- Shared consumers:
- Contract consumers:
- Regression hotspots:

## 6) Invariant Evaluation
Reference `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md`.

| Invariant ID | Severity | Status (PASS/FAIL/UNKNOWN) | Evidence (`path:line`) | Notes |
|---|---|---|---|---|

### Invariant Summary
- Any `P0` failed? (`yes|no`)
- Any in-scope `UNKNOWN`? (`yes|no`)
- Blocked? (`yes|no`)
- Blocking reasons:

## 7) Test Gate Plan
Reference `/Users/codymarchant/Documents/Projects/specsharp-claude/TEST_MATRIX.md`.

| Category ID | Gate ID | Severity | Command / Manual Check | Expected Result | Rationale |
|---|---|---|---|---|---|

### Critical Path Smoke Checks
- New project flow:
- Project details flow:
- Executive view flow:
- Construction view flow:
- DealShield flow:

## 8) Findings (Ordered by Severity)
For each finding:
- Severity (`P0|P1|P2|P3`):
- Title:
- Risk:
- Impact:
- Evidence (`/absolute/path:line`):
- Recommendation:

## 9) Work Order Draft (Handoff-Ready)
- Objective:
- Allowed files to edit:
- Must-not-edit files:
- Ordered execution steps:
- Required test gates:
- Acceptance criteria:
- Rollback plan:
- Stop conditions:

## 10) Confidence Summary
- Coverage %:
- Evidence Density %:
- Confidence Score (/10):
- Open Uncertainties:
- Blockers:
- Final Decision (`APPROVE_FOR_IMPLEMENTATION|BLOCK`):

## 11) Sign-off
- Auditor:
- Reviewer:
- Date:
- Notes:

---

## Quick Completion Checklist
- [ ] Preflight identity gate passed
- [ ] RepoMap consulted first
- [ ] In-scope/out-of-scope explicit
- [ ] Invariants evaluated with evidence
- [ ] Test gates mapped from TEST_MATRIX
- [ ] Findings ranked by severity
- [ ] Work order draft included
- [ ] Confidence + decision recorded
