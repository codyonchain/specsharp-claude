# Subtype: Distribution Center (Industrial)

## Overrides
- revenue intensity: modest premium vs Warehouse (market_factor applied)
- MEP intensity: Medium
- sitework intensity: Higher (truck courts, logistics)

## Deterministic drivers
- dock_doors (primary)
- trailer_parking (explicit input wins; else deterministic proxy)
- office_ratio (explicit overrides win)

## Acceptance tests
- Dock doors explicit override must win over defaults.
- Any dock-derived assumptions must be traceable.
