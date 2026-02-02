# DEV_VERIFY (Daily Gate)

## Purpose
Fast local deterministic gate for agent work (minutes). No prod checks. No massive suites.

## Default Components
Frontend:
- npm run lint
- npm run typecheck
- npm run build

Backend:
- targeted pytest suite for invariants + traceability (no goldens by default)

E2E:
- local smoke only (tests/e2e/critical-paths/smoke.spec.ts)

## Rules
- DEV_VERIFY must be fast and runnable repeatedly.
- Any failing invariant blocks merge.
- Production-domain checks are forbidden in DEV_VERIFY.
