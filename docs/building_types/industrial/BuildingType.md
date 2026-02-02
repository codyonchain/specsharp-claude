# Building Type: Industrial

## Underwriting model
- Category: NOI (stabilized income asset)
- Primary valuation method: cap_rate
- Recommendation logic (default):
  - GO if DSCR >= target AND yield_on_cost >= target AND critical risk flags are not present
  - NEEDS WORK if close to thresholds or key drivers are missing
  - NO-GO if DSCR materially below target or yield_on_cost below minimum

## Primary metrics (must output)
- NOI
- DSCR
- Yield on Cost
- Stabilized Value (cap-rate derived)
- Breakeven Rent/SF (if applicable)

## Revenue model (deterministic)
Inputs:
- rent_per_sf_year (market baseline)
- rentable_sf (or rentable_ratio × GSF)
- occupancy_stabilized
Formula (conceptual):
- EGI = rent_per_sf_year × rentable_sf × occupancy
- NOI = EGI - opex (or EGI × NOI_margin if opex modeled as margin)

## Cost intensity model (deterministic)
Inputs:
- deterministic scope + quantities
- global cost_rate
- cost_factor (City, State)
Formula:
- total_cost = scope_cost × cost_factor

## Financing & lender logic
- DSCR target: deterministic per subtype
- LTC: deterministic per subtype
- Debt sizing: NOI / DSCR-driven

## Trace requirements
Must include trace steps when triggered:
- valuation_model_selected (cap_rate)
- regional_override_applied (if cost_factor/market_factor override)
- city_only_location_warning (if missing state)
- modifiers_applied (finish/MEP/intensity adjustments)
- recommendation_derived
