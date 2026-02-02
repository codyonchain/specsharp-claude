# Subtype: Flex Space (Industrial)

## Overrides
- blended rent model: office portion + industrial portion
- finish level: higher on office portion
- MEP intensity: Medium

## Deterministic drivers
- office_ratio (critical; explicit overrides win)
- finish_level (explicit input wins)

## Acceptance tests
- Office ratio must deterministically change both rent blend and cost blend.
- Office ratio explicitly 0 must behave as pure industrial.
