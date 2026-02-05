# DealShield Metric Refs (Fixture-Backed)

Ground-truth metric refs harvested from `UnifiedEngine.calculate_project` outputs using the parity fixtures in `scripts/audit/parity/fixtures/basic_fixtures.json` (11 fixtures). Dotpaths use `[]` to denote arrays. `timestamp` and `calculation_trace` are excluded.

Regenerate inventory:
```
python3 scripts/audit/dealshield/metric_inventory.py
```

## Canonical Refs (Recommended)

### DealShield Base Metrics
- Cost base metric: `totals.total_project_cost` (present in all 11 fixtures)
- Revenue base metric: `revenue_analysis.annual_revenue` (present in all 11 fixtures)
- NOI fallback: `return_metrics.estimated_annual_noi` (present in all 11 fixtures)

### DealShield Sensitivity Tiles (Direct Scenario Outputs)
- Cost +10% tile: `sensitivity_analysis.cost_up_10.yield_on_cost` (present in all 11 fixtures)
- Revenue -10% tile: `sensitivity_analysis.revenue_down_10.yield_on_cost` (present in all 11 fixtures)
- Baseline yield on cost: `sensitivity_analysis.base.yield_on_cost` (present in all 11 fixtures)

## ExecutiveView / Underwriting Refs

| Metric ref | Notes | Fixtures/subtypes |
| --- | --- | --- |
| `revenue_analysis.annual_revenue` | Canonical revenue | All fixtures |
| `revenue_analysis.net_income` | Revenue-derived NOI | All fixtures |
| `return_metrics.estimated_annual_noi` | Canonical NOI | All fixtures |
| `ownership_analysis.debt_metrics.calculated_dscr` | DSCR | All fixtures |
| `profile.target_yield` | Target yield | All fixtures |
| `profile.target_dscr` | Target DSCR | All fixtures |
| `profile.market_cap_rate` | Market cap rate | All fixtures |
| `return_metrics.cap_rate` | Cap rate | All fixtures |
| `return_metrics.irr` | IRR | All fixtures |
| `return_metrics.cash_on_cash_return` | Cash-on-cash | All fixtures |
| `return_metrics.payback_period` | Payback period (yrs) | All fixtures |
| `return_metrics.property_value` | Implied value | All fixtures |
| `sensitivity_analysis.base.yield_on_cost` | Baseline YOC | All fixtures |
| `sensitivity_analysis.cost_up_10.yield_on_cost` | Cost +10% YOC | All fixtures |
| `sensitivity_analysis.revenue_down_10.yield_on_cost` | Revenue -10% YOC | All fixtures |

## ConstructionView Refs

| Metric ref | Notes | Fixtures/subtypes |
| --- | --- | --- |
| `totals.total_project_cost` | Total all-in cost | All fixtures |
| `totals.cost_per_sf` | All-in cost per SF | All fixtures |
| `totals.hard_costs` | Hard costs | All fixtures |
| `totals.soft_costs` | Soft costs | All fixtures |
| `construction_costs.construction_total` | Construction subtotal | All fixtures |
| `construction_costs.final_cost_per_sf` | Final cost per SF | All fixtures |
| `construction_costs.equipment_total` | Equipment total | All fixtures |

Soft cost buckets (all fixtures, except `soft_costs.medical_equipment` only in healthcare):
- `soft_costs.construction_management`
- `soft_costs.contingency`
- `soft_costs.design_fees`
- `soft_costs.financing`
- `soft_costs.legal`
- `soft_costs.medical_equipment`
- `soft_costs.permits`
- `soft_costs.startup`
- `soft_costs.testing`

## Trade Totals Refs (Per Trade)

All present in all fixtures:
- `trade_breakdown.structural`
- `trade_breakdown.mechanical`
- `trade_breakdown.electrical`
- `trade_breakdown.plumbing`
- `trade_breakdown.finishes`

## Scope Items Refs (Multi-Trade)

| Metric ref | Notes | Fixtures/subtypes |
| --- | --- | --- |
| `scope_items[].systems[].unit_cost` | Unit cost per scope system | `healthcare_medical_office_building`, `industrial_cold_storage`, `industrial_flex_space`, `industrial_warehouse_shell`, `restaurant_quick_service_clamp` |
| `scope_items[].systems[].quantity` | Quantity driver | Same fixtures as above |
| `scope_items[].systems[].total_cost` | Total cost per system | Same fixtures as above |

## Facility Metrics (If Present)

| Metric ref | Notes | Fixtures/subtypes |
| --- | --- | --- |
| `facility_metrics.metrics[].value` | Restaurant per-SF metrics | All restaurant fixtures |
| `facility_metrics.units` | Outpatient units | `healthcare_medical_office_building`, `healthcare_outpatient_clinic` |
| `facility_metrics.cost_per_unit` | Outpatient cost/unit | Same outpatient fixtures |
| `facility_metrics.revenue_per_unit` | Outpatient revenue/unit | Same outpatient fixtures |

## Coverage Matrix (Wave 1 Subtypes)

Recommended refs for DealShield tiles by subtype family. All metrics below are verified in the listed fixture(s) unless noted.

| Subtype family | Fixture id(s) | Cost base ref | Revenue base ref | Cost +10 tile ref | Revenue -10 tile ref | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Industrial warehouse | `industrial_warehouse_shell` | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | Scope items present |
| Industrial cold storage | `industrial_cold_storage` | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | Scope items present |
| MOB (medical office building) | `healthcare_medical_office_building` | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | Facility metrics + scope items present |
| Urgent care | `healthcare_outpatient_clinic` | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | Closest parity fixture to urgent care |
| QSR | `restaurant_quick_service_clamp` | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | Restaurant facility metrics present |
| Limited service hotel | None in parity fixtures | `totals.total_project_cost` | `revenue_analysis.annual_revenue` | `sensitivity_analysis.cost_up_10.yield_on_cost` | `sensitivity_analysis.revenue_down_10.yield_on_cost` | No fixture coverage; refs unverified for hotel subtype |

## Notes
- Top-level `revenue_analysis.*`, `return_metrics.*`, and `sensitivity_analysis.*` are canonical. The same values also appear under `ownership_analysis.*`, but use the top-level refs for DealShield.
- If revenue metrics are missing in a future subtype, use `return_metrics.estimated_annual_noi` as the fallback for revenue-based tiles.
