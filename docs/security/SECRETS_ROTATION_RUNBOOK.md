# Secrets Rotation Runbook

Use this when a secret file is committed or leaked.

## 1) Contain

1. Remove secret files from git tracking:
   `git rm --cached backend/.env.production backend/.env.backup`
2. Ensure secret files are ignored in `.gitignore`.
3. Commit containment immediately.

## 2) Rotate

Rotate every credential that may have been exposed, including:

- Supabase `SERVICE_ROLE_KEY` and any legacy API keys
- Supabase database password (`DATABASE_URL`)
- Google OAuth client secret
- App secrets (`SECRET_KEY`, `SESSION_SECRET_KEY`, JWT secrets)
- Stripe secrets/webhook secret
- Redis passwords/tokens (if configured)

## 3) Purge Git History (coordinated maintenance window)

History rewrite is destructive and must be coordinated with all collaborators.

Example (run once from a clean clone):

```bash
git filter-repo --path backend/.env.production --path backend/.env.backup --invert-paths
git push --force-with-lease --all
git push --force-with-lease --tags
```

After rewrite, all contributors must reclone or hard-reset to the rewritten history.

## 4) Verify

1. Secret scan locally:
   `gitleaks git --config .gitleaks.toml --redact`
2. Confirm no tracked env secrets:
   `git ls-files | rg '(^|/)\\.env(\\.|$)'`
3. Confirm CI secret scan passes (`Secret Scan` workflow).
