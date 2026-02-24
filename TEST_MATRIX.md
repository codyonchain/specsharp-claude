# TEST_MATRIX.md

## Purpose
Defines required verification gates by change type so audits and work orders are deterministic.

## Scope
Applies to all changes in `/Users/codymarchant/Documents/Projects/specsharp-claude`.

## Usage
1. Identify change category from the matrix below.
2. Run every required gate for that category.
3. Record `PASS | FAIL | BLOCKED` with command output summary.
4. If any `P0` gate fails, block implementation/merge.

## Command Inventory (Verified)

| Command | Layer (`frontend` \| `backend` \| `repo`) | Purpose | Exists? (`yes`/`no`) | Evidence (`absolute-path:line`) |
| --- | --- | --- | --- | --- |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run lint` | frontend | Frontend lint gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/package.json:11` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run typecheck` | frontend | Frontend type check gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/package.json:10` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run build` | frontend | Frontend production build gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/package.json:8` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run test:v2` | frontend | Frontend V2 automated test gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/package.json:13` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run test:e2e` | repo | Playwright end-to-end integration gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/package.json:3` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run backend:test` | repo | Start backend in test mode (`uvicorn`, port 8001) for smoke/E2E | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/package.json:6` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run frontend:test` | repo | Start frontend in test mode for smoke/E2E | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/package.json:7` |
| `cd /Users/codymarchant/Documents/Projects/specsharp-claude/backend && pytest` | backend | Backend automated test gate | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/backend/README.md:38` |
| `bash /Users/codymarchant/Documents/Projects/specsharp-claude/backend/scripts/v2_audit/validate_v2_ready.sh` | backend | Backend V2 API/integration smoke suite | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/backend/scripts/v2_audit/validate_v2_ready.sh:46` |
| `bash /Users/codymarchant/Documents/Projects/specsharp-claude/backend/test-owner-view.sh` | backend | Backend owner-view endpoint smoke check | yes | `/Users/codymarchant/Documents/Projects/specsharp-claude/backend/test-owner-view.sh:37` |

## Gate Severity
- `P0`: Must pass, otherwise block.
- `P1`: Must pass before merge.
- `P2`: Recommended; may proceed only with explicit risk note.

## Change Categories

| Category ID | Change Type | Typical Files | Required Gates | Notes |
| --- | --- | --- | --- | --- |
| CAT-001 | Copy/content-only UI change | `frontend/src/**/*.tsx`, `frontend/src/**/*.css` | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD`, `M-SMOKE-NEW` or `M-SMOKE-PROJECT` | No API or formula impact expected. |
| CAT-002 | Route/page wiring change | `frontend/src/v2/App.tsx`, route/page components | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD`, `G-FE-UNIT`, `G-E2E`, `M-SMOKE-NEW`, `M-SMOKE-PROJECT` | Validate route guards and navigation. |
| CAT-003 | Shared component/UI behavior change | shared UI components used by multiple pages | `G-FE-LINT`, `G-FE-TSC`, `G-FE-UNIT`, `G-FE-BUILD`, `G-E2E`, `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL` | Cross-route regression risk is high. |
| CAT-004 | Frontend data-fetch/transform change | `frontend/src/v2/hooks/**`, `frontend/src/v2/api/**`, selectors/helpers | `G-FE-TSC`, `G-FE-UNIT`, `G-BE-PYTEST`, `G-E2E`, `G-BE-V2-SMOKE`, `M-SMOKE-NEW`, `M-SMOKE-PROJECT`, `M-NUM-LINEAGE` | Include payload shape and transform checks. |
| CAT-005 | Numeric/formula/business logic change | calculation helpers, view-model math, numeric format logic | `G-BE-PYTEST`, `G-BE-V2-SMOKE`, `G-E2E`, `G-FE-BUILD`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` | Mandatory lineage validation. |
| CAT-006 | Config change (`building_types`, `building_subtypes`, similar) | `backend/app/v2/config/**`, `shared/building_types.json`, frontend taxonomy consumers | `G-BE-PYTEST`, `G-FE-TSC`, `G-FE-BUILD`, `G-BE-V2-SMOKE`, `G-E2E`, `M-SMOKE-NEW`, `M-SMOKE-EXEC`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` | Confirm taxonomy propagates end-to-end. |
| CAT-007 | Backend API/controller change | `backend/app/api/**`, `backend/app/v2/api/**` | `G-BE-PYTEST`, `G-BE-V2-SMOKE`, `G-E2E`, `G-BE-OWNER-SMOKE`, `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-DEAL` | Contract compatibility required. |
| CAT-008 | Backend engine/calculation change | `backend/app/v2/engines/**`, backend services with numeric outputs | `G-BE-PYTEST`, `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE`, `G-E2E`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` | Highest numeric regression risk. |
| CAT-009 | DB model/migration change | `backend/app/db/**`, `backend/alembic/**`, `backend/migrations/**` | `G-BE-PYTEST`, `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE`, `M-SMOKE-PROJECT`, `M-SMOKE-EXEC` | Validate reads/writes and API hydration. |
| CAT-010 | Auth/security/session change | auth middleware, token/session handling, route protection | `G-E2E`, `G-BE-PYTEST`, `G-FE-BUILD`, `M-SMOKE-NEW`, `M-SMOKE-PROJECT` | Must validate protected route behavior. |
| CAT-011 | Build/tooling/config pipeline change | `package.json`, frontend tool configs, CI scripts | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD`, `G-FE-UNIT`, `G-E2E`, `M-SMOKE-NEW`, `M-SMOKE-PROJECT` | Ensure local and CI parity. |
| CAT-012 | Cross-cutting multi-layer change | frontend + backend + config/db in one change | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD`, `G-BE-PYTEST`, `G-E2E`, `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE`, `G-FE-UNIT`, all `M-SMOKE-*`, `M-NUM-LINEAGE` | Run full matrix for impacted surfaces. |

## Required Gates by Category

### Gate IDs (Automated)
- `G-FE-LINT`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run lint`
- `G-FE-TSC`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run typecheck`
- `G-FE-BUILD`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run build`
- `G-FE-UNIT`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend && npm run test:v2`
- `G-E2E`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run test:e2e`
- `G-BE-PYTEST`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude/backend && pytest`
- `G-BE-V2-SMOKE`: `bash /Users/codymarchant/Documents/Projects/specsharp-claude/backend/scripts/v2_audit/validate_v2_ready.sh`
- `G-BE-OWNER-SMOKE`: `bash /Users/codymarchant/Documents/Projects/specsharp-claude/backend/test-owner-view.sh`
- `G-STACK-BE`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run backend:test`
- `G-STACK-FE`: `cd /Users/codymarchant/Documents/Projects/specsharp-claude && npm run frontend:test`

### Gate IDs (Manual deterministic)
- `M-SMOKE-NEW`: Run Critical Path Smoke Check "New project flow".
- `M-SMOKE-PROJECT`: Run Critical Path Smoke Check "Project details flow".
- `M-SMOKE-EXEC`: Run Critical Path Smoke Check "Executive view flow".
- `M-SMOKE-CONSTR`: Run Critical Path Smoke Check "Construction view flow".
- `M-SMOKE-DEAL`: Run Critical Path Smoke Check "DealShield flow".
- `M-NUM-LINEAGE`: Run all five Numeric Lineage Verification Rules.

### Category-to-Severity Mapping

| Category ID | `P0` gates (blocking) | `P1` gates | `P2` gates |
| --- | --- | --- | --- |
| CAT-001 | `G-FE-LINT`, `G-FE-TSC` | `G-FE-BUILD` | `M-SMOKE-NEW` or `M-SMOKE-PROJECT` |
| CAT-002 | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD` | `G-FE-UNIT`, `G-E2E` | `M-SMOKE-NEW`, `M-SMOKE-PROJECT` |
| CAT-003 | `G-FE-LINT`, `G-FE-TSC`, `G-FE-UNIT` | `G-FE-BUILD`, `G-E2E` | `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL` |
| CAT-004 | `G-FE-TSC`, `G-FE-UNIT`, `G-BE-PYTEST` | `G-E2E`, `G-BE-V2-SMOKE` | `M-SMOKE-NEW`, `M-SMOKE-PROJECT`, `M-NUM-LINEAGE` |
| CAT-005 | `G-BE-PYTEST`, `G-BE-V2-SMOKE` | `G-E2E`, `G-FE-BUILD` | `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` |
| CAT-006 | `G-BE-PYTEST`, `G-FE-TSC`, `G-FE-BUILD` | `G-BE-V2-SMOKE`, `G-E2E` | `M-SMOKE-NEW`, `M-SMOKE-EXEC`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` |
| CAT-007 | `G-BE-PYTEST`, `G-BE-V2-SMOKE` | `G-E2E`, `G-BE-OWNER-SMOKE` | `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-DEAL` |
| CAT-008 | `G-BE-PYTEST`, `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE` | `G-E2E` | `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` |
| CAT-009 | `G-BE-PYTEST` | `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE` | `M-SMOKE-PROJECT`, `M-SMOKE-EXEC` |
| CAT-010 | `G-E2E`, `G-BE-PYTEST` | `G-FE-BUILD` | `M-SMOKE-NEW`, `M-SMOKE-PROJECT` |
| CAT-011 | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD` | `G-FE-UNIT`, `G-E2E` | `M-SMOKE-NEW`, `M-SMOKE-PROJECT` |
| CAT-012 | `G-FE-LINT`, `G-FE-TSC`, `G-FE-BUILD`, `G-BE-PYTEST`, `G-E2E` | `G-BE-V2-SMOKE`, `G-BE-OWNER-SMOKE`, `G-FE-UNIT` | `M-SMOKE-NEW`, `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, `M-NUM-LINEAGE` |

## Critical Path Smoke Checks

### New project flow (`M-SMOKE-NEW`)
- Route/page: `/new` -> `NewProject` (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/App.tsx:64`).
- Expected visible outputs: "2. Analyze", "3. Save", "Total Project Cost", "Save Project & View Details" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:952`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:959`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:1422`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:1451`).
- Key numbers to verify: non-empty `Total Project Cost` value after analysis (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:903`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/NewProject/NewProject.tsx:1422`).
- Failure signals: Analyze button stays disabled with valid input, save action fails, or total cost remains blank/zero unexpectedly.

### Project details flow (`M-SMOKE-PROJECT`)
- Route/page: `/project/:id` -> `ProjectView` (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/App.tsx:72`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectView.tsx:13`).
- Expected visible outputs: tabs "DealShield", "Executive View", "Trade Breakdown" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:38`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:49`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:60`).
- Key numbers to verify: at least one top-level currency metric is shown after project load (DealShield or Executive/Construction tab).
- Failure signals: "Project not found" appears (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectView.tsx:58`), tab switches fail, or numeric panels do not populate.

### Executive view flow (`M-SMOKE-EXEC`)
- Route/page: `/project/:id` + "Executive View" tab (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:49`).
- Expected visible outputs: "TOTAL INVESTMENT REQUIRED", "STABILIZED YIELD (NOI / COST)", "DSCR VS TARGET" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx:1948`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx:2009`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx:2023`).
- Key numbers to verify: total investment amount, stabilized yield %, and DSCR multiplier are all present.
- Failure signals: missing executive cards, NaN/undefined numeric values, or DSCR panel absent.

### Construction view flow (`M-SMOKE-CONSTR`)
- Route/page: `/project/:id` + "Trade Breakdown" tab (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:60`).
- Expected visible outputs: "Total Construction Cost", "Base Construction", "Final Construction Cost", "Construction Schedule" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ConstructionView.tsx:1634`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ConstructionView.tsx:1724`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ConstructionView.tsx:1812`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ConstructionView.tsx:1261`).
- Key numbers to verify: total construction amount and final construction amount are populated and non-negative.
- Failure signals: construction totals missing, schedule section missing, or totals regress to obvious placeholders.

### DealShield flow (`M-SMOKE-DEAL`)
- Route/page: `/project/:id` + "DealShield" tab (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/ProjectHeader.tsx:38`).
- Expected visible outputs: "DealShield", "Stabilized Value", "Value Gap", "Export DealShield PDF" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/DealShieldView.tsx:710`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/DealShieldView.tsx:905`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/DealShieldView.tsx:914`, `/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/DealShieldView.tsx:784`).
- Key numbers to verify: stabilized value and value gap numbers both render.
- Failure signals: "DealShield not available" (`/Users/codymarchant/Documents/Projects/specsharp-claude/frontend/src/v2/pages/ProjectView/DealShieldView.tsx:799`), no metrics, or control update errors.

## Numeric Lineage Verification Rules
Include mandatory checks whenever user-visible numbers may change:
1) Verify UI display source path.
2) Verify helper/hook/selector transform path.
3) Verify API/config source.
4) Verify formula/default/rounding behavior.
5) Confirm unit/timeframe consistency.
Reference `/Users/codymarchant/Documents/Projects/specsharp-claude/RepoMap.md` and `/Users/codymarchant/Documents/Projects/specsharp-claude/INVARIANTS.md`.

## Evidence Logging Format
Use this exact format in audits/work orders:
- Gate: <gate-id>
- Command: `<exact command>`
- Result: PASS|FAIL|BLOCKED
- Evidence: `<absolute-path:line>` and short output summary
- Notes: <risk/exception>

## Decision Rules
- Block if any `P0` gate fails.
- Block if required gate is missing command definition and no manual deterministic fallback is defined.
- Block if numeric lineage checks are required but incomplete.
- Proceed only when all required gates pass for all impacted categories.

## Fast-Start Checklist
1) Confirm repo identity.
2) Identify categories impacted.
3) Run all required `P0` gates.
4) Run required `P1` gates.
5) Run critical smoke checks.
6) Attach evidence log.
7) Produce work order or implementation approval.
