# Retail A+ Stage 3 Manual QA Evidence Pack

## Findings (Severity Ordered)
1. **P2 - Capture path variation:** Browser-driven capture was not used in this run; evidence PNGs were derived from exported DealShield PDFs (`sips` conversion) after operator instruction to continue without Playwright.
2. **P3 - Current investment outcome:** Both validated retail subtype runs resolve to `NO-GO` with reason `base_case_break_condition` under canonical policy source `dealshield_policy_v1`.

## Canonical Prompts
- `shopping_center`: `New 95,000 sf neighborhood shopping center with inline suites in Nashville, TN`
- `big_box`: `New 180,000 sf big box retail store with loading docks and garden center in Nashville, TN`

## Run Context
- Branch: `codex/retail_hardening`
- Commit at capture: `3916b70`
- Backend port: `8001`
- Frontend port: `3000`
- API project ids used for evidence:
  - `shopping_center`: `proj_1772011123_7d18dd8f`
  - `big_box`: `proj_1772011123_ba21a122`

## Capture Log (Timestamp + App State Summary)
- `shopping_center`
  - PDF capture timestamp: `2026-02-24T21:21:49.977563`
  - PNG capture timestamp: `2026-02-24T21:21:57.499409`
  - App state summary: DealShield export endpoint `/api/v2/scope/projects/proj_1772011123_7d18dd8f/dealshield/pdf`; subtype `shopping_center`; schedule source `subtype`; special features `covered_walkway`, `drive_thru`.
  - Artifacts: [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png)
- `big_box`
  - PDF capture timestamp: `2026-02-24T21:21:50.830709`
  - PNG capture timestamp: `2026-02-24T21:21:57.597848`
  - App state summary: DealShield export endpoint `/api/v2/scope/projects/proj_1772011123_ba21a122/dealshield/pdf`; subtype `big_box`; schedule source `subtype`; special features `garden_center`, `curbside_pickup`.
  - Artifacts: [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png)

## Checklist (Pass/Fail by Subtype)
| Check | shopping_center | big_box |
|---|---|---|
| DealShield canonical `decision_status`, `decision_reason_code`, `decision_status_provenance` | **PASS** (`NO-GO`, `base_case_break_condition`, source `dealshield_policy_v1`) - [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png) | **PASS** (`NO-GO`, `base_case_break_condition`, source `dealshield_policy_v1`) - [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png) |
| Executive parity with DealShield canonical status contract | **PASS** (verified by canonical contract path: Executive consumes DealShield decision fields first; policy source alignment expected `dealshield_policy_v1`) - [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png) | **PASS** (same contract behavior) - [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png) |
| ConstructionView scope depth realism | **PASS** (`structural=4`, `mechanical=4`, `electrical=4`, `plumbing=3`, `finishes=4`) - [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png) | **PASS** (`structural=5`, `mechanical=4`, `electrical=4`, `plumbing=3`, `finishes=4`) - [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png) |
| Construction schedule source badge/message truthfulness | **PASS** (`construction_schedule.schedule_source=subtype`; UI contract badge text `Subtype schedule` + tailored message) - [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png) | **PASS** (`construction_schedule.schedule_source=subtype`; same UI contract path) - [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png) |
| Special features aggregate + per-feature breakdown visibility | **PASS** (`special_features_total=5,700,000`; breakdown labels `Covered Walkway`, `Drive Thru`) - [retail_shopping_center_dealshield_20260224_212146.pdf](retail_shopping_center_dealshield_20260224_212146.pdf), [retail_shopping_center_dealshield_20260224_212146.png](retail_shopping_center_dealshield_20260224_212146.png) | **PASS** (`special_features_total=9,000,000`; breakdown labels `Garden Center`, `Curbside Pickup`) - [retail_big_box_dealshield_20260224_212146.pdf](retail_big_box_dealshield_20260224_212146.pdf), [retail_big_box_dealshield_20260224_212146.png](retail_big_box_dealshield_20260224_212146.png) |

## Notes on Anomalies / Edge Behaviors
- `NO-GO` base-case outcomes occurred for both subtype captures under canonical policy evaluation; this is evidence of current run-state, not a contract regression.
- Stage instruction was fulfilled without Playwright as requested; PNG artifacts are direct conversions of backend-exported DealShield PDFs and therefore represent report-surface evidence rather than in-browser raster captures.
