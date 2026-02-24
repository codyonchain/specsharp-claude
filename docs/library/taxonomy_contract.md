# Taxonomy Contract (Canonical Building Types & Subtypes)

## Purpose
Guarantee that **UI, API, and docs** all use the exact same canonical building type + subtype keyspace, without drift.

This contract exists to support:
- deterministic underwriting (v2 engine)
- parallel subtype agents (58 subtype owners)
- zero “silent mismatch” between frontend taxonomy and backend normalization

---

## Canonical Source of Truth
**Canonical taxonomy is derived from:**
- `backend/app/v2/config/master_config.py` (`MASTER_CONFIG`)

This is authoritative because it drives v2 runtime behavior and contains:
- **13 building types**
- **58 subtypes**

---

## Canonical Files (must stay in sync)

### Canonical taxonomy file (frontend + shared)
- `shared/building_types.json`

### Generated backend copy (backend runtime dependency)
- `backend/shared/building_types.json`

**Important:** these files contain **canonical keys only**.  
Aliases are policy and live in:
- `docs/library/aliases.md`
- and optionally in frontend mapping code

---

## Why there are two files
Backend code (via `building_taxonomy.py`) reads `backend/shared/building_types.json` relative to backend runtime layout.
Frontend imports `shared/building_types.json`.

To avoid deployment/path risk, we keep a backend-local copy — but it is **generated** from the canonical shared file.

---

## Non-Negotiable Rules
1) **Do not manually edit** `backend/shared/building_types.json`  
   - It is a generated artifact and will be overwritten.

2) `shared/building_types.json` is canonical, but it should also be generated from `MASTER_CONFIG` rather than hand-edited.

3) **Canonical keys only** in both JSON files.  
   - No “residential/commercial” keys in JSON.
   - Aliases live in `docs/library/aliases.md`.

4) Any change to v2 taxonomy (new type/subtype, rename, remove) must update:
   - `MASTER_CONFIG`
   - regenerated JSON files
   - alias policy (if needed)
   - and any UI/API validation logic that relies on taxonomy

---

## Generation & Sync Workflow (Step 0)
We maintain three small deterministic scripts:

### A) Export canonical taxonomy from MASTER_CONFIG
- `scripts/audit/export_taxonomy_from_master_config.py`

Writes:
- `shared/building_types.json`

### B) Sync backend copy from canonical shared file
- `scripts/audit/sync_backend_taxonomy.py` (or `.sh`)

Copies:
- `shared/building_types.json` → `backend/shared/building_types.json`

### C) Verify sync (drift alarm)
- `scripts/audit/verify_taxonomy_sync.py`

Checks:
- Canonicalized JSON equality (order-insensitive) between the two files
- Fails if mismatch

---

## DEV_VERIFY integration
`verify_taxonomy_sync` becomes part of DEV_VERIFY so drift is impossible.

DEV_VERIFY should fail if:
- the two JSON files differ
- canonical JSON does not match MASTER_CONFIG-derived keys

---

## API / UI Contracts
## Taxonomy Strictness Policy (Option M)

### Building Type: STRICT
- If building_type is missing or not in the canonical taxonomy keys:
  - The system must NOT silently coerce to another type (e.g., office).
  - Behavior: return a validation error (HTTP 400 at API layer) or fail fast in engine-level validation.
  - Trace: if a calculation_trace exists, include a critical trace entry:
    - step: unknown_building_type
    - data: { received_type: <raw>, allowed_types: <list> }

### Subtype: LENIENT (with warning + deterministic fallback)
- If building_type is valid but subtype is missing or invalid:
  - Behavior: deterministically fall back to a default subtype for that building type.
    - Default subtype selection rule must be deterministic and documented (e.g., a per-type default_subtype).
  - Trace: must include a warning trace entry:
    - step: unknown_subtype_fallback
    - data: {
        building_type: <canonical>,
        received_subtype: <raw or null>,
        fallback_subtype: <chosen>,
        reason: "invalid_or_missing_subtype"
      }

### No silent coercion rule
- Under no circumstance should an unknown building type be normalized into a different known type without explicit policy and trace.
- Subtype fallback is allowed only within a confirmed canonical building type.

### Backend normalization
- Backend must normalize and validate against canonical keys from `backend/shared/building_types.json`.
- Backend must not silently coerce unknown types into another type (e.g., specialty → office) without a trace warning + explicit rule.

### Frontend taxonomy
- Frontend must display and emit canonical v2 keys.
- If frontend accepts legacy labels, it must map them deterministically to canonical keys before sending to backend.

---

## Auditing & Change Control
Any PR that changes taxonomy must include:
- regenerated `shared/building_types.json`
- regenerated `backend/shared/building_types.json`
- output of `verify_taxonomy_sync` (or CI proof)

---

## Definitions
- **Canonical keys:** v2 engine keys as defined in `MASTER_CONFIG`.
- **Aliases:** UI/legacy labels that map deterministically to canonical keys (see `docs/library/aliases.md`).
- **Drift:** any mismatch between `MASTER_CONFIG` and the JSON files, or between shared and backend copies.

---
