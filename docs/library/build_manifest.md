# Build Manifest

This file is the single source of truth for where subtype-promotion truth lives, what each output must guarantee, and which gates are mandatory before merge.

## Three Views and Their Guarantees

### 1) DealShield Front Door
- Audience: skeptical decision room.
- Guarantee: one-page, downside-first, deterministic summary with explicit assumptions and audit trail.
- Contract: `docs/library/dealshield_contract.md`.

### 2) Executive Appendix
- Audience: lender/investor decision makers.
- Guarantee: deterministic investment framing, model-class-aligned KPIs, and explicit decision rule traceability.
- Contract: `docs/library/executiveview_contract.md`.

### 3) Construction Appendix
- Audience: owner/GC/operators.
- Guarantee: deterministic trade/schedule/provenance detail with subtype-specific scope and milestone clarity.
- Contract: `docs/library/constructionview_contract.md`.

## Where Truth Lives

### Canonical config + subtype truth
- Subtypes: `backend/app/v2/config/subtypes/<building_type>/<subtype>.py`
- Base type profiles: `backend/app/v2/config/type_profiles/<building_type>.py`
- Scope items registries: `backend/app/v2/config/type_profiles/scope_items/<building_type>.py`
- DealShield tile registries: `backend/app/v2/config/type_profiles/dealshield_tiles/<building_type>.py`
- DealShield content registries: `backend/app/v2/config/type_profiles/dealshield_content/<building_type>.py`
- Master taxonomy/config wiring: `backend/app/v2/config/master_config.py`

### Docs + subtype intent
- Subtype docs: `docs/building_types/<building_type>/subtypes/<subtype>.md`
- Library contracts/runbooks: `docs/library/*.md`

### Audits + matrix outputs
- Matrix generator: `scripts/audit/status/generate_coverage_matrix.py`
- Matrix artifacts: `docs/status/subtype_coverage_matrix.{md,csv,json}`
- Fingerprints: `scripts/audit/fingerprint_all.py`
- Parity harness + fixtures: `scripts/audit/parity/run_parity.py`, `scripts/audit/parity/fixtures/`
- Queue + fixture audits: `scripts/audit/promotion_queue.py`, `scripts/audit/fixtures_audit.py`
- Preflight runner: `scripts/audit/preflight.sh`

## Baseline vs Promoted

### Baseline (Wave B)
- Coverage exists but can still be partial.
- Typical gaps: missing subtype docs, missing DealShield profile wiring, missing fixture coverage.
- Coverage matrix status is often red/yellow.

### Promoted (Wave 1 quality)
- Treated as ship-ready and defensible.
- Minimum bar:
  - `wave1 == true` or matrix status is green with deterministic profile/doc wiring.
  - parity fixture coverage exists for the promoted subtype.
  - contracts and docs remain aligned.

## Required Gates and Timing

Run `scripts/audit/preflight.sh` before every merge or handoff.

`preflight.sh` required gates (fail if missing/failing), in order:
1. `scripts/audit/fingerprint_all.py`
2. `scripts/audit/parity/run_parity.py`
3. `frontend: npm run typecheck`
4. `frontend: npm run build`

Optional gates are allowed to skip when missing:
- `scripts/audit/subtype_coverage_audit.py`
- `scripts/audit/subtype_promotion_audit.py`
- single DealShield runner under `scripts/audit/dealshield/` if one exists

## Parallel Workflow Rules

- One agent per shared file at a time (shared registries, matrix outputs, runbooks).
- Use path-scoped staging only: `git add <explicit paths>`.
- Before every commit, always show staged diffstat:
  - `git diff --cached --stat`
