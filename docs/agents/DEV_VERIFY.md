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

## Taxonomy Drift Prevention (Required)

DEV_VERIFY must include:
1) Generate canonical taxonomy from MASTER_CONFIG:
   - scripts/audit/export_taxonomy_from_master_config.py
2) Sync backend runtime copy:
   - scripts/audit/sync_backend_taxonomy.py
3) Verify no drift between shared and backend copies:
   - scripts/audit/verify_taxonomy_sync.py

DEV_VERIFY fails if:
- shared/building_types.json != backend/shared/building_types.json (canonicalized equality)
- canonical taxonomy does not match MASTER_CONFIG-derived types/subtypes

## Rules
- DEV_VERIFY must be fast and runnable repeatedly.
- Any failing invariant blocks merge.
- Production-domain checks are forbidden in DEV_VERIFY.
