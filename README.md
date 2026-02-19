# SpecSharp Contributor README

## Overview
SpecSharp currently runs with an active V2 surface: a React + Vite frontend and a FastAPI backend. The active contributor flow centers on V2 routes such as `/new` and `/project/:id`, with project details split across DealShield, Executive View, and Trade Breakdown.

## Tech Stack
- Frontend: React + Vite (`frontend/package.json` scripts/dependencies; Vite React plugin).
- Frontend runtime config: dev server on port `3000` with strict port; `/api` proxy targets backend `8001`.
- Backend: FastAPI app served via `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`.
- Shared taxonomy data: `shared/building_types.json`, generated from backend `master_config.py`.
- Validation/tooling surfaces present in matrix: npm frontend checks, Playwright E2E, backend `pytest`, backend smoke scripts.

## Project Structure
- `frontend/`: Active UI entrypoint (`src/main.tsx`) and V2 app (`src/v2/**`).
- `backend/`: FastAPI app, V2 API/controllers/services/engines.
- `shared/`: Shared generated taxonomy (`building_types.json`).
- Root scripts: `start-frontend.sh`, `start-backend.sh`, `start-all.sh` (legacy/misaligned path target).
- Governance docs: `RepoMap.md`, `INVARIANTS.md`, `TEST_MATRIX.md`, `AUDIT_PROCESS.md`.

## Local Development (frontend/backend commands)
Frontend:
```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend
npm run dev
```

Frontend explicit localhost command (documented local success path):
```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude/frontend
npm run dev -- --host 127.0.0.1 --port 3000 --strictPort
```

Backend:
```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Repo-level test-mode launchers (from matrix inventory):
```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude
npm run backend:test
npm run frontend:test
```

## Routing and Key UI Surfaces
Active V2 routes:
- `/` (home), `/login`, `/dashboard`, `/new`, `/project/:id`, `/diagnostics`, `/signup`.
- `/new` -> `NewProject` page (analyze + save workflow).
- `/project/:id` -> `ProjectView` with tabs: `DealShield`, `Executive View`, `Trade Breakdown`.
- `ProjectView` initializes with `executive` and can auto-switch to `dealshield` after successful DealShield fetch (unless user already selected a view).

Legacy route surface still in tree:
- V1 router in `frontend/src/App.tsx` includes `/scope/new` and `/project/:projectId`, but `src/main.tsx` imports `./v2/App` as root.

## Data/Number Lineage Summary
- New Project `Total Project Cost`: UI card <- `summaryTotals.total_project_cost` <- `result.calculations` <- frontend `/analyze` call <- backend `unified_engine.calculate_project` where `total_project_cost = total_hard_costs + total_soft_costs`.
- Executive `TOTAL INVESTMENT REQUIRED`: UI <- `totals.total_project_cost` from project fetch response (`calculation_data` mapping path).
- Construction totals: UI prefers `calculations.totals.hard_costs`; documented fallback literal exists (`246900000`).
- DealShield `Value Gap`: backend computes `stabilized_value = noi / cap_rate`, then `value_gap = stabilized_value - total_cost`, exposed through decision summary fields.
- Executive NOI/DSCR math includes frontend target NOI formulas and backend DSCR calculation path (`estimated_annual_noi / annual_debt_service`).

## Config Ownership
- Canonical building taxonomy authority is backend `backend/app/v2/config/master_config.py`.
- `shared/building_types.json` is generated from that backend config.
- Active frontend taxonomy consumer chain uses `frontend/src/core/buildingTaxonomy.ts` and V2 `NewProject` mapping.
- Parallel legacy taxonomy exists in `frontend/src/config/buildingTypes.ts` and is tied to V1 `ScopeGenerator` surface.

## Active vs Legacy Surface
Active:
- `frontend/src/main.tsx` -> `frontend/src/v2/App.tsx` route tree.
- V2 pages/components for New Project and Project View tabs.
- DealShield API/service path in V2 frontend client and backend V2 scope/service files.
- Shared UI components used across V2 surfaces (`LoadingSpinner`, `ErrorMessage`, `ProjectHeader`).

Legacy or Orphan (documented):
- V1 router and V1 route flows (`/scope/new`, V1 `/project/:projectId`).
- `frontend/src/config/buildingTypes.ts` legacy config path.
- `start-all.sh` points to `/Users/codymarchant/specsharp/*` instead of this repo root.
- `BUILDING_SUBTYPES` (`frontend/src/v2/types/index.ts`), `API_CONFIG` (`frontend/src/config/api.ts`), and `BuildingTypeSelector.tsx` were reported as currently unused by corroboration scans.

## Testing and Validation Gates
- Invariant policy is severity-based (`P0`, `P1`, `P2`); any failed `P0` blocks progress.
- Mandatory governance includes repo identity lock, evidence-backed claims, explicit Active/Legacy labeling, route ownership mapping, numeric lineage completeness, and API contract compatibility.
- `TEST_MATRIX.md` defines category-based required gates (`CAT-001` through `CAT-012`) and exact commands.
- Core automated gates listed in matrix include:
  - Frontend: `npm run lint`, `npm run typecheck`, `npm run build`, `npm run test:v2`
  - Repo integration: `npm run test:e2e`, `npm run backend:test`, `npm run frontend:test`
  - Backend: `pytest`, `backend/scripts/v2_audit/validate_v2_ready.sh`, `backend/test-owner-view.sh`
- Manual deterministic smoke checks include `M-SMOKE-NEW`, `M-SMOKE-PROJECT`, `M-SMOKE-EXEC`, `M-SMOKE-CONSTR`, `M-SMOKE-DEAL`, plus `M-NUM-LINEAGE`.

## Known Limitations / Environment Notes
- Prior runtime proof captured a frontend dev-server failure: `Error: listen EPERM: operation not permitted ::1:3000` when running `npm run dev`, with follow-up `curl` checks returning `000` for both `127.0.0.1:3000` and `localhost:3000`.
- RepoMap also records operator runtime proof that `npm run dev -- --host 127.0.0.1 --port 3000 --strictPort` started Vite and reported local URL `http://127.0.0.1:3000/`.
- `start-all.sh` is documented as legacy/misaligned for this repository path.

## Engineering Governance Workflow
1. Audit first (no edits): run preflight identity gate, normalize request, map scope to RepoMap, evaluate invariants, map test gates, and produce findings/risk.
2. Work order generation: create an implementation-ready order with objective, in-scope/out-of-scope files, execution steps, acceptance criteria, rollback plan, and stop conditions.
3. Implementation: proceed only when `P0` invariants pass and no in-scope uncertainty remains.
4. Post-change audit/validation: run required matrix gates and critical smoke checks for impacted categories, confirm numeric lineage/contract integrity, and block on any failed required `P0` gate or invariant.

## Verified As Of
- Repo root: `/Users/codymarchant/Documents/Projects/specsharp-claude`
- Branch: `codex/w_matrix_coverage_report`
- Commit SHA: `da57e278984e0183c64fcd657fdc1cdee4ff5f68`
- Source of facts for this README: `RepoMap.md`, `INVARIANTS.md`, `TEST_MATRIX.md`, `AUDIT_PROCESS.md`
