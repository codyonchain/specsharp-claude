# Subtype: Cold Storage (Industrial)

## Overrides
- MEP intensity: Very High (refrigeration)
- envelope intensity: High
- revenue intensity: Higher but risk-flagged

## Deterministic drivers
- freezer_ratio vs cooler_ratio (explicit input wins; else deterministic default)
- refrigeration_tier (explicit input wins; else deterministic default)
- backup_power (boolean flag)

## Trace requirements (additional)
- cold_storage_intensity_applied (or captured in modifiers_applied with subtype=cold_storage)

## Acceptance tests
- If freezer_ratio explicitly set, it must override defaults.
- High-intensity adders must be traceable.
