# DealShield UI Display-Only Cutover Log

## Purpose
Track backend truth fields that are now contract-tested, plus UI logic/copy branches that should be removed or switched to backend-driven flags in follow-on stages.

## Stage 1 (Current): Backend Contract Hardening
- Added/validated backend decision-insurance outputs:
  - `first_break_condition_holds`
  - `break_risk_level`
  - `break_risk_reason`
  - `break_risk` (`{level, reason}`)
- Added/validated provenance blocks:
  - `decision_insurance_provenance.first_break_condition_holds`
  - `decision_insurance_provenance.break_risk`
- Added invariant tests to lock these fields for hardened profiles and industrial subtype coverage.

## Stage 2 Candidates: UI Cutover to Backend Truth
- DealShieldView:
  - Replace any local break-condition math with `first_break_condition_holds`.
  - Replace local severity-vs-break risk reconciliation with backend `break_risk_*`.
  - Keep UI as renderer-only for status/copy gating decisions tied to break condition.
- ExecutiveViewComplete:
  - Remove local condition checks that infer break/no-break from raw numeric fields.
  - Gate status copy from canonical backend outputs (`decision_status`, `decision_reason_code`, `first_break_condition_holds` when needed).

## Stage 3 Candidates: Cleanup/Consolidation
- Remove redundant frontend helper utilities that duplicate backend threshold evaluation.
- Add explicit UI contract tests that fail when local threshold math is reintroduced.
- Keep subtype-authored copy maps, but trigger them from backend truth fields only.

## Guardrails
- No cross-building-type behavior changes without explicit subtype matrix and tests.
- No backend severity math policy rewrite unless separately approved.
- UI should not compute or reinterpret decision policy outputs.
