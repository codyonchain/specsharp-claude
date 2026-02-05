# Wave 0.5 Hardcode Audit Notes

## Scope
Active v2 path audit focused on:
- `backend/app/v2/engines/unified_engine.py`
- `backend/app/v2/api/scope.py`
- `frontend/src/v2/pages/ProjectView/ConstructionView.tsx`

## Migrated (Wave 0.5)
- Warehouse structural scope itemization moved from engine hardcode to config profile:
  - `industrial_warehouse_structural_v1` in `backend/app/v2/config/type_profiles/scope_items/industrial.py`
- Engine now resolves scope items generically from `scope_items_profile` (+ optional deterministic overrides), with no warehouse-only label/share constants in engine.
- Frontend fabricated per-trade `materials/labor/equipment` split heuristics removed.
  - ConstructionView now renders split cards only when backend supplies `trade_cost_splits`.
- Frontend fabricated equipment sub-split heuristics removed.
  - Equipment breakdown now renders only when backend supplies `construction_costs.equipment_breakdown`.

## Kept Intentionally (Current Active Path)
- API fallback in `backend/app/v2/api/scope.py` remains as one LUMP SUM system per trade when `scope_items` are absent.
  - This is deterministic and intentionally coarse.

## Deferred
- Existing hardcoded flex/cold-storage scope-item narratives in engine are still active legacy paths (`industrial_flex`, `industrial_cold_storage`).
  - Deferred to next scope-item profile wave to keep this migration behavior-preserving for warehouse/distribution shell profile rollout.
