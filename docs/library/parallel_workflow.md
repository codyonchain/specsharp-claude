# Parallel Workflow Playbook

Canonical workflow for parallel agent execution during hardening sprints.

## Golden Rule Checklist (Run Before Any Task)

```bash
git branch --show-current
git status --short
bash scripts/audit/preflight.sh
```

If any step fails, stop and resolve before editing or staging.

## 1) Clean-Tree Rule

- Never commit unless the working tree is clean.
- Only exception: running gates while intentionally dirty, using `PREFLIGHT_ALLOW_DIRTY=1`.
- Dirty-tree gate runs are for validation only, not for commit.

```bash
git status --short
# If output is non-empty, do not commit.
```

```bash
PREFLIGHT_ALLOW_DIRTY=1 bash scripts/audit/preflight.sh
```

## 2) Worktree-First Pattern (Preferred for Codex/Executors)

When the primary tree is dirty, do not mix unrelated edits. Use an isolated worktree.

```bash
# Example from repo root
git worktree add .worktrees/<branch_name> -b <branch_name> <base_branch>
cd .worktrees/<branch_name>
git branch --show-current
git status --short
```

Expected result: new branch, isolated filesystem, clean status before task work.

## 3) Shared-File Ownership Rule (Type-Owner Lock)

Shared files require a single explicit owner for the task window.

- One owner edits shared files.
- Non-owners may edit subtype-specific files/docs only.
- If a work order includes shared files, it must explicitly mark them as shared.

Examples of shared files/categories:
- Type profiles:
  - `backend/app/v2/config/type_profiles/dealshield_tiles/<building_type>.py`
  - `backend/app/v2/config/type_profiles/dealshield_content/<building_type>.py`
  - `backend/app/v2/config/type_profiles/scope_items/<building_type>.py`
- Master config / shared scope items:
  - `scripts/audit/parity/fixtures/basic_fixtures.json`
  - `docs/status/subtype_coverage_matrix.md`
  - `docs/status/subtype_coverage_matrix.csv`
  - `docs/status/subtype_coverage_matrix.json`
- Shared docs touched by multiple agents:
  - `docs/library/*.md`

## 4) Path-Scoped Staging + Cached Diffstat Rule

Always stage only the intended paths, then verify exactly what is queued.

```bash
git add <scoped-path-1> <scoped-path-2>
git diff --cached --stat
git commit -m "<message>"
```

Rules:
- Never use `git add .` in hardening workflow.
- If cached diffstat shows unrelated files, unstage and restage by path.
- Do not commit with a dirty working tree.

## 5) Executor Thread Workflow (Codex)

Executor runs commands; architect issues one work order at a time.

### Executor Runs

```bash
git branch --show-current
git status --short
python3 scripts/audit/promotion_queue.py
python3 scripts/audit/fixtures_audit.py
bash scripts/audit/preflight.sh
git add <scoped paths>
git diff --cached --stat
```

### Executor Reports Back

- Branch and cleanliness state (`git status --short`).
- Exact staged diffstat (`git diff --cached --stat`).
- Gate/audit outcomes:
  - `python3 scripts/audit/promotion_queue.py`
  - `python3 scripts/audit/fixtures_audit.py`
  - `bash scripts/audit/preflight.sh`
- Any blockers with command + short error summary.

This keeps execution deterministic, path-scoped, and collision-resistant across parallel agents.
