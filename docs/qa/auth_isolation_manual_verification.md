# Auth Isolation Manual Verification

## 1) Apply DB-level RLS in Supabase
1. Open Supabase SQL Editor for the target project.
2. Run [`backend/sql/supabase_auth_rls_hardening.sql`](/Users/codymarchant/Documents/Projects/specsharp-claude/.worktrees/merge_specialty_into_main/backend/sql/supabase_auth_rls_hardening.sql).
3. Confirm success with no SQL errors.

## 2) Get two real user tokens
Use two different accounts in separate browser profiles:
- User A token: `localStorage.getItem('specsharp_access_token')`
- User B token: `localStorage.getItem('specsharp_access_token')`

## 3) Run automated manual-verification script
```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude/.worktrees/merge_specialty_into_main
TOKEN_USER_A='paste-user-a-token' TOKEN_USER_B='paste-user-b-token' API_BASE_URL='http://127.0.0.1:8001/api/v2' ./scripts/security/verify_auth_isolation.sh
```

Expected result:
- Script prints `== RESULT: AUTH ISOLATION CHECK PASSED ==`
- Cross-user reads fail (project, owner-view URL, DealShield PDF URL)
- Each user sees only their own project in list endpoint

## 4) Production endpoint run
```bash
TOKEN_USER_A='paste-user-a-token' TOKEN_USER_B='paste-user-b-token' API_BASE_URL='https://api.specsharp.ai/api/v2' ./scripts/security/verify_auth_isolation.sh
```

## Notes
- The script creates one project per user and attempts cleanup at the end.
- If cleanup fails, remove projects from dashboard or call delete endpoint with owner token.

## Manual onboarding (no public signup)
1. In Supabase, go to `Authentication -> Users -> Add user`.
2. Add the customer email (set `email_confirm=true`).
3. Keep backend setting `ALLOW_AUTO_ORG_PROVISIONING=false` in production.
4. On first login, backend claims the pre-provisioned membership by email and binds it to the real Supabase `user_id`.

## Quick run top-up (2-5 minute ops)
Use the backend helper script:

```bash
cd /Users/codymarchant/Documents/Projects/specsharp-claude/.worktrees/merge_specialty_into_main/backend
PYTHONPATH=$PWD ./venv/bin/python scripts/grant_runs.py --email customer@example.com --add-runs 10
```

Notes:
- If the user does not exist in `organization_members` yet, the script resolves them by Supabase email and provisions a workspace.
- Unlimited override users are controlled by `UNLIMITED_ACCESS_EMAILS` in `backend/.env` (comma-separated).
