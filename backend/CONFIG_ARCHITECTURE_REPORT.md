# Config Architecture Verification Report (Archived)

## Status Update (2026-02-03)
- Legacy config file `app/services/building_types_config.py` has been removed.
- The active config system is `app/v2/config/master_config.py`.
- Shared taxonomy JSON is `shared/building_types.json` (with a backend copy at `backend/shared/building_types.json`).

## Guidance
- Do not reintroduce the legacy config.
- Update taxonomy and subtype definitions in `master_config.py` and keep JSON in sync.
