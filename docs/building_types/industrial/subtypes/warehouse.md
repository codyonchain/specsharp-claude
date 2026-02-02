# Subtype: Warehouse (Industrial)

## Underwriting overrides vs base type
- revenue intensity: baseline industrial rent
- finish level defaults: Standard
- MEP intensity: Low–Medium
- risk tolerance: Standard

## Deterministic drivers
- dock_doors (explicit overrides win)
- office_ratio (explicit overrides win)
- clear_height (explicit input wins; otherwise deterministic default)

## Acceptance tests (invariants)
- City-only location must emit city_only_location_warning trace.
- office_ratio explicitly 0 must result in 0 office scope and blended rent logic.
- Any derived dock assumptions must be traceable.
