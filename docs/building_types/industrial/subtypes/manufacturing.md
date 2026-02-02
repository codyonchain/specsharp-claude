# Subtype: Manufacturing (Industrial)

## Overrides
- MEP intensity: High
- power intensity: Higher (deterministic tier)
- risk tolerance: Higher variability (flag missing drivers)

## Deterministic drivers
- power_intensity_tier (explicit input wins; else deterministic default)
- crane_bay (boolean if specified)

## Acceptance tests
- If manufacturing triggers power adder, emit modifiers_applied trace with the reason.
