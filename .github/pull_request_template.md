# Summary
<!-- What changed and why? One or two sentences. -->

# Engine Health
- **Engine Contract Hash (from CI output):** `ENGINE_CONTRACT_HASH=...`
- **Stable Tests (CI):** trace ✅ · invariants ✅ · golden ✅
  <!-- If any are failing, explain why here, or link to CI logs. -->

# Risk & Trace
- Does this change alter public engine interfaces (function signatures) or trace step names?
  - [ ] No
  - [ ] Yes — updated tests and docs/ENGINE_CONTRACT.md accordingly
- Does it change regional multipliers, NOI derivation, special-features math, or clamps?
  - [ ] No
  - [ ] Yes — golden/invariants updated

# Checklist
- [ ] Ran local health check  
      `PYTHONPATH=. python backend/scripts/engine_contract_check.py`
- [ ] Stable suites pass locally or on CI  
      `PYTHONPATH=. pytest -q tests/test_trace_flags.py tests/test_invariants.py tests/test_revenue_golden.py`
- [ ] (If contract changed) appended new hash to `docs/ENGINE_CONTRACT.md`
- [ ] Trace entries follow standardized schema (`step`, `data{...}`)

# Notes for Reviewers
<!-- Optional: link to CI run, highlight any intentional hash change, or paste a short diff summary. -->
