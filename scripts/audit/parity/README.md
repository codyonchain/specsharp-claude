# Parity Harness MVP

This harness runs deterministic fixtures and asserts selector-driven behavior for Phase 4 changes.

## Usage

From repo root:

```bash
python3 scripts/audit/parity/run_parity.py
```

## Fixtures

Fixtures live in `scripts/audit/parity/fixtures/basic_fixtures.json` and are sorted by `id` before execution.

Each fixture includes:
- `id`
- `building_type`
- `subtype`
- `square_footage`
- `project_class`
- `finish_level` (optional)
- `extra_inputs` (optional)
- `expected` signature (required)

### Adding a fixture

1. Add a new JSON object to `basic_fixtures.json`.
2. Run the harness once to compute actual signatures and update the `expected` block.
3. Keep expected values minimal but meaningful to avoid noisy diffs.

## Output

The harness prints `PASS <id>` for matches and `FAIL <id>` with expected vs actual signatures when mismatched.

A non-zero exit code indicates one or more failures.
