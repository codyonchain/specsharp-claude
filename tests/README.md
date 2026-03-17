# SpecSharp Tests

## Active suites

1. Backend acceptance contracts:
   `backend/tests/test_v2_acceptance.py`
2. Browser launch E2E (Playwright, blocking):
   `tests/e2e/launch/*.spec.ts`
3. Browser smoke (Playwright, additive/manual only):
   `tests/e2e/smoke/*.spec.ts`

## Browser launch scope

- Login/logout + session persistence
- Dashboard route guard + reload
- `/new` draft packet -> confirmed save -> project view
- DealShield control persistence + launch-critical PDF export
- Run-limit reached UI messaging

See: `tests/e2e/README.md` for env vars and commands.
