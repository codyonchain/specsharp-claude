# Dual Config System Audit Report (Archived)

## Status Update (2026-02-03)
- Legacy config file `app/services/building_types_config.py` has been removed.
- Comparison script `backend/compare_configs.py` has been removed.
- `app/v2/config/master_config.py` is the only supported configuration source.
- Taxonomy JSON lives in `shared/building_types.json` and `backend/shared/building_types.json`.

## Guidance
- Do not reintroduce the legacy config.
- Any type/subtype changes must be made in `master_config.py` and mirrored in the shared taxonomy JSON.
