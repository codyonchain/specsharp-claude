# Retail A+ Manual QA (Fast Close)

Run context:
- branch: `codex/retail_hardening`
- commit: `a3e913b`
- backend port: `8001`
- frontend port: `3000`

Canonical prompts:
- shopping_center: `New 95,000 sf neighborhood shopping center with inline suites in Nashville, TN`
- big_box: `New 180,000 sf big box retail store with loading docks and garden center in Nashville, TN`

| Check | shopping_center | big_box |
|---|---|---|
| DealShield canonical status/reason/provenance | PASS (`NO-GO` / `base_case_break_condition` / `dealshield_policy_v1`) | PASS (`NO-GO` / `base_case_break_condition` / `dealshield_policy_v1`) |
| Special features aggregate + per-feature breakdown present | PASS (`special_features_total=5700000`, labels: `Covered Walkway`, `Drive Thru`) | PASS (`special_features_total=9000000`, labels: `Garden Center`, `Curbside Pickup`) |
| schedule source value captured (subtype/building_type) | PASS (`subtype`) | PASS (`subtype`) |

Artifact links:
- shopping_center: [retail_shopping_center_20260224_212819.pdf](assets/retail_shopping_center_20260224_212819.pdf), [retail_shopping_center_20260224_212819.png](assets/retail_shopping_center_20260224_212819.png)
- big_box: [retail_big_box_20260224_212819.pdf](assets/retail_big_box_20260224_212819.pdf), [retail_big_box_20260224_212819.png](assets/retail_big_box_20260224_212819.png)

Limitation: Evidence is PDF-derived and not full UI-tab capture.
