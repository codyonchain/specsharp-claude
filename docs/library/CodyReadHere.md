# Cody Read Here

Operational runbook for promotion work. Keep this file action-oriented and copy/paste-first.

## The Only 3 Things Cody Does

1. Promote subtypes.
2. Run preflight.
3. Ship scoped commits.

## Golden Path: Promote One Subtype

```bash
# 1) Refresh matrix + see next candidates
python3 scripts/audit/status/generate_coverage_matrix.py
python3 scripts/audit/promotion_queue.py --limit 10 --format md

# 2) Pick one subtype and implement profile/doc updates
#    (edit subtype config + dealshield registries + scope_items + subtype doc)

# 3) Ensure promoted subtype has parity fixture coverage
python3 scripts/audit/fixtures_audit.py

# 4) Run full merge-safe gates
bash scripts/audit/preflight.sh

# 5) Stage only intended files and show diffstat
git add <explicit file paths>
git diff --cached --stat
```

## Golden Path: Promote One Building Type With Multiple Agents

Role split:
- Agent A: subtype config updates (`backend/app/v2/config/subtypes/<type>/...`).
- Agent B: profile registries (`dealshield_tiles`, `dealshield_content`, `scope_items`).
- Agent C: docs + fixtures + queue checks (`docs/building_types/...`, `scripts/audit/parity/fixtures/...`).

Lock rule:
- Shared files are locked to one agent at a time.
- Shared files include:
  - `backend/app/v2/config/type_profiles/dealshield_tiles/<type>.py`
  - `backend/app/v2/config/type_profiles/dealshield_content/<type>.py`
  - `backend/app/v2/config/type_profiles/scope_items/<type>.py`
  - `scripts/audit/parity/fixtures/basic_fixtures.json`
  - `docs/status/subtype_coverage_matrix.*`

## Never Do These Manually Again

- Matrix generation: `python3 scripts/audit/status/generate_coverage_matrix.py`
- Promotion queue generation: `python3 scripts/audit/promotion_queue.py --limit 10 --format md`
- Promoted fixture enforcement: `python3 scripts/audit/fixtures_audit.py`
- Merge-safe gate pack: `bash scripts/audit/preflight.sh`

## Copy/Paste: Start of Session

```bash
git branch --show-current
git status --short
python3 scripts/audit/status/generate_coverage_matrix.py
python3 scripts/audit/promotion_queue.py --limit 10 --format md
```

## Copy/Paste: Run Preflight

```bash
bash scripts/audit/preflight.sh
```

## Copy/Paste: Stage + Diffstat

```bash
git add <file1> <file2> <file3>
git diff --cached --stat
```
