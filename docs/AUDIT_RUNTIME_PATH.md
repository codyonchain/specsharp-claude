# 1. Overview
Project reports in SpecSharp flow from the React V2 `ProjectView` container through a single `useProject` data hook that calls the V2 API client (`frontend/src/v2/api/client.ts`). The client fetches a stored project (`GET /api/v2/scope/projects/{id}`) whose payload includes the `calculation_data` blob produced when the project was originally analyzed by `UnifiedEngine.calculate_project()` on the backend. The frontend passes this blob through `BackendDataMapper` to normalize numbers for `ExecutiveViewComplete` and `ConstructionView`, while export actions (PDF) reuse the same stored payload via `/pdf/project/{project_id}/pdf`. Ad-hoc “what-if” tools (`/api/v2/calculate`, `/api/v2/compare`) call the same engine without persisting, returning the same schema (minus DB metadata), so the mapper and UI can consume the result immediately.

# 2. Golden Runtime Path: Stored Project
- `frontend/src/v2/pages/ProjectView/ProjectView.tsx` (`ProjectView` component): Loads `useProject(id)` and decides whether to render `ExecutiveViewComplete` or `ConstructionView`. **Input**: router param `id`. **Output**: passes `project: Project` (with `analysis.calculations`) to child components.
- `frontend/src/v2/hooks/useProject.ts` (`useProject` hook): Calls `api.getProject(id)` (line 34) and stores the JSON response. **Input**: project ID string. **Output**: `project` object with `{analysis: {calculations: …}}`.
- `frontend/src/v2/api/client.ts` (`getProject` method, lines ~685-768): Issues `GET /api/v2/scope/projects/{id}` via `request('/scope/projects/{id}', 'v2')`, then wraps `calculation_data` into `analysis.calculations`. **Input**: `id`. **Output**: mapped project where `analysis.calculations` references backend `calculation_data`.
- `backend/app/v2/api/scope.py` (`@router.get("/scope/projects/{project_id}")`, lines ~753-779): Loads `Project` row, calls `format_project_response`, returns `ProjectResponse.success`. **Input**: DB row. **Output**: JSON payload containing `calculation_data`, `project_info`, `totals`, etc.
- `backend/app/v2/engines/unified_engine.py` (`UnifiedEngine.calculate_project`, lines ~187-750): Generates `project_info`, `construction_costs`, `totals`, `ownership_analysis`, `calculation_trace`, etc., when the project was first analyzed (via `/analyze`/`/calculate`). **Input**: request params (building_type, subtype, square_footage, etc.). **Output**: the `calculation_data` blob stored in DB.
- Stored payload → `frontend/src/v2/utils/backendDataMapper.ts` (`BackendDataMapper.mapToDisplay`, lines 194-1175): Converts backend keys (`totals.total_project_cost`, `ownership_analysis.return_metrics`) into UI-friendly `displayData` (ROI, DSCR, facility metrics). **Input**: `analysis.calculations`. **Output**: normalized `DisplayData`.
- `frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx` and `ConstructionView.tsx`: Consume both `project.analysis.calculations` and `displayData` to render hero cards, breakdowns, etc. **Input**: Project + mapped data. **Output**: UI.

# 3. Golden Runtime Path: Ad-hoc Calculate / Compare
- Frontend:
  - `frontend/src/v2/pages/ScenarioComparison/ScenarioBuilder.tsx` and `ScenarioComparison.tsx` call `api.client.post('/api/v2/calculate', …)` and `api.client.post('/api/v2/compare', …)` with scenario definitions.
- Backend:
  - `backend/app/v2/api/scope.py` `@router.post("/calculate")` (lines ~478-520) and `@router.post("/compare")` (lines ~537-571) parse payloads, normalize enums, then call `unified_engine.calculate_project` (or `calculate_comparison`).
- Engine:
  - `UnifiedEngine.calculate_project()` returns the same structure (`project_info`, `totals`, `ownership_analysis`, `return_metrics`). For `/compare`, the engine iterates scenarios and aggregates results.
- Response:
  - The frontend receives the raw engine result (not stored), which downstream UI modules or comparison tables consume directly (same schema used by `BackendDataMapper`, so existing components can render without DB persistence).

# 4. PDF Export Path
- `frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx` (`handleExportPdf`, lines ~1870-1895): Invokes `pdfService.exportProject(projectId)`.
- `frontend/src/services/api.ts` (`pdfService.exportProject`, lines ~276-287): Performs `GET /pdf/project/{projectId}/pdf` via shared Axios client, streams blob for download.
- `backend/app/v2/api/scope.py` (`@router.get("/pdf/project/{project_id}/pdf")`, lines ~1064-1126): Retrieves stored project, ensures `request_data` defaults, then calls `pdf_export_service.generate_professional_pdf(project_payload, client_name)`.
- `backend/app/services/pdf_export_service.py`: `ProfessionalPDFExportService` (instantiated as `pdf_export_service`) formats the PDF using HTML templates + wkhtmltopdf/weasyprint (implementation resides entirely in this module). The generated binary is streamed back with Content-Disposition headers.

# 5. Payload Ownership and Schema Boundaries
- **Truth generation**: `UnifiedEngine.calculate_project()` produces authoritative keys—`project_info`, `construction_costs`, `trade_breakdown`, `soft_costs`, `totals`, `ownership_analysis`, `revenue_analysis`, `return_metrics`, `calculation_trace`.
- **Persistence layer**: `format_project_response()` stores that blob as `Project.calculation_data` and exposes it unchanged to API clients (plus snake/camel casing for metadata).
- **Frontend translation**: `BackendDataMapper.mapToDisplay()` is the only place where backend schema is reshaped for UI (adds `displayData` fields, fallback calculations, heuristic ROI/NOI derivations).
- **Schema boundaries**:
  - `/api/v2` responses guarantee `calculation_data` for saved projects.
  - Ad-hoc `/calculate`/`/compare` responses mirror the same structure but skip DB-specific wrappers.
  - PDF export reuses the stored payload; no additional transformations beyond `request_data` backfill.

# 6. Divergence / Drift Risks (IMPORTANT)
- **Stored vs. Ad-hoc data**: Saved projects rely on the engine version used at creation; `/api/v2/scope/projects/{id}` simply replays stored `calculation_data`. If `UnifiedEngine` logic changes, existing `calculation_data` grows stale while `/calculate` returns the new schema/values (see `backend/app/v2/api/scope.py:712-779` vs. `/calculate`).
- **Frontend fallbacks**: `BackendDataMapper` derives values when backend fields are missing (e.g., annual revenue fallback `estimated_annual_noi / 0.6` at `frontend/src/v2/utils/backendDataMapper.ts:1094-1106`, payback derived from `total_cost / NOI` lines 1068-1079). If backend changes remove a field, mapper-generated numbers may diverge from backend-intended logic without detection.
- **Multiple engines**: Legacy `owner_view_engine.py`, `cost_dna_service.py`, and scenario services still exist. Some endpoints (`/scope/projects/{id}/owner-view` in `backend/app/v2/api/scope.py:1039-1055`) call other engines; if those outputs feed UI or exports, they may differ from unified engine assumptions.
- **PDF path**: `pdf_export_service` formats data independently; if it expects keys that diverge from `calculation_data`, PDF content could drift from UI (e.g., additional `request_data` merging in `backend/app/v2/api/scope.py:1090-1105`).
- **Client adapters**: `frontend/src/v2/api/client.ts` adapts V1 projects (localStorage) to V2 schema. Bugs in this adapter can introduce inconsistent shapes (e.g., `adaptV1ToV2Structure`), leading to mismatched fields between stored DB projects and local fallback data.
