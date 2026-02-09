# Git Workflow Guardrails

Workflow conventions for Cody and parallel agents.

## Preferred Branch + Worktree Strategy

- Do promotion work on a hardening branch, never on `main`.
- If your primary tree is dirty, use an isolated worktree for Codex work:

```bash
git worktree add ../specsharp-hardening codex/<ticket-or-scope>
cd ../specsharp-hardening
git branch --show-current
git status --short
```

- Keep sprint commits narrow and path-scoped.

## Path-Scoped Staging (Required)

Use explicit staging paths, never `git add .` for hardening sprints.

```bash
git add scripts/audit/preflight.sh docs/library/build_manifest.md
git add docs/library/CodyReadHere.md scripts/audit/promotion_queue.py
git add scripts/audit/fixtures_audit.py docs/library/git_workflow.md
git diff --cached --stat
```

## Shared File Lock Policy

- One agent edits one shared file at a time.
- Shared files include:
  - `backend/app/v2/config/type_profiles/dealshield_tiles/<building_type>.py`
  - `backend/app/v2/config/type_profiles/dealshield_content/<building_type>.py`
  - `backend/app/v2/config/type_profiles/scope_items/<building_type>.py`
  - `scripts/audit/parity/fixtures/basic_fixtures.json`
  - `docs/status/subtype_coverage_matrix.{md,csv,json}`
  - `docs/library/*.md` files touched by multiple contributors
- Acquire lock in team chat/PR note before editing; release after commit hash is posted.

## Commit Message Conventions

- `chore:` repo tooling, runbooks, non-runtime hardening
- `docs:` documentation-only changes
- `audit:` audit script or gate logic updates
- `feat:` behavior changes for user-facing/app logic
- `fix:` bug fixes

Examples:
- `chore: add preflight runner + workflow hardening artifacts`
- `audit: tighten subtype promotion queue ranking output`
- `docs: update build manifest truth map`

## Optional Hook (Documented, Not Enforced)

Optional pre-commit approach: require a staged diffstat acknowledgement file before commit.

Concept:
1. Developer runs `git diff --cached --stat`.
2. Developer records acknowledgement (`.git/DIFFSTAT_OK` timestamp).
3. Pre-commit hook fails if staged changes exist and acknowledgement is missing/stale.

This keeps the guardrail explicit without forcing repo-wide hook enforcement.
