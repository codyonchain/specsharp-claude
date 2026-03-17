# Browser E2E (Playwright)

The canonical blocking launch suite lives under `tests/e2e/launch` and covers:

- login/logout + session persistence
- dashboard route protection
- `/new` draft packet -> confirmed save -> project view
- dashboard reopen flow
- DealShield control persistence + packet export/download
- run-limit reached UI gating

The additive smoke suite lives under `tests/e2e/smoke` and is not the primary CI launch signal.

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
npm run test:e2e
```

Optional additive smoke run:

```bash
npm run test:e2e:smoke
```

Notes:

- The blocking launch suite requires `E2E_USER_TOKEN`; CI should fail preflight if it is missing.
- The run-limit launch test does not consume real credits; it stubs the backend 403 response and validates UI behavior.
