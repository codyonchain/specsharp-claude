# SpecSharp Tests

## Active suites

1. Backend acceptance contracts:
   `backend/tests/test_v2_acceptance.py`
2. Browser UX smoke (Playwright):
   `tests/e2e/smoke/*.spec.ts`

## Playwright UX scope

- Login/logout + session persistence
- New project key interactions
- Packet export/download
- Run-limit reached UI messaging
- Footer/legal links + basic nav sanity

See: `tests/e2e/README.md` for env vars and commands.
