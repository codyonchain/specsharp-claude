# PRE_DEPLOY (Release Gate)

## Purpose
Slow, broad validation before shipping (weekly / monthly / release). Not run on every patch.

## Includes
Frontend:
- lint
- typecheck
- build

Backend:
- full pytest suite (including goldens if explicitly authorized)

E2E:
- full e2e battery (critical-paths + edge-cases)
- optionally: accessibility, visual regression, performance
- optionally: production smoke tests (explicitly enabled only)

## Rules
- PRE_DEPLOY may be slow.
- PRE_DEPLOY must never run by default during daily development.
- Any production-domain test must be gated behind an env flag (e.g. E2E_PROD=1).
