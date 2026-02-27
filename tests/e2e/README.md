# UX Smoke E2E (Playwright)

These tests are scoped to high-signal UX flows:

- login/logout + session persistence
- create project + key form interactions
- packet export/download
- run-limit reached UI
- footer/legal + basic navigation sanity

## Environment

Set these before running authenticated tests:

```bash
export E2E_USER_TOKEN='...supabase access token...'
export TEST_BASE_URL='http://localhost:3000'
export E2E_API_BASE_URL='http://127.0.0.1:8001'
```

Optional second user token:

```bash
export E2E_SECONDARY_USER_TOKEN='...'
```

## Run

```bash
npx playwright test --config=tests/playwright.config.ts tests/e2e/smoke
```

Notes:

- Authenticated tests auto-skip when `E2E_USER_TOKEN` is missing.
- Run-limit test does not consume real credits; it stubs the backend 403 response and validates UI behavior.
