# Aliases (Frontend/UI Terms -> Canonical v2 Keys)

## Purpose
Canonical taxonomy keys are defined by backend v2 config (MASTER_CONFIG) and exported into:
- shared/building_types.json (canonical)
- backend/shared/building_types.json (generated copy)

This file defines UI-facing aliases and legacy naming that must map deterministically to canonical keys.

## Canonical rule
- JSON taxonomies contain canonical keys ONLY.
- Aliases are policy and live here (and optionally in frontend mapping code).

## Alias map (current)
- residential -> multifamily
- commercial -> office

## Deprecation policy
- UI may display legacy labels for familiarity, but must send canonical keys to backend.
- Backend accepts canonical keys only (unless explicitly designed to accept aliases).

## Notes
- mixed_use and specialty are canonical v2 building types and must exist in UI + API taxonomy.
