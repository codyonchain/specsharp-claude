# Differentiation Matrix (SpecSharp)
## Purpose
Document building-type coverage so backend/ frontend configs stay in sync and we can spot gaps before adding subtype-specific logic.
## Subtype Coverage
### Backend (master_config.py)
- Total building types: 13
- Total subtypes: 58
- Per type:
  - healthcare (10) → [hospital, surgical_center, medical_center, imaging_center, outpatient_clinic, urgent_care, medical_office, dental_office, rehabilitation, nursing_home]
  - multifamily (3) → [luxury_apartments, market_rate_apartments, affordable_housing]
  - office (2) → [class_a, class_b]
  - retail (2) → [shopping_center, big_box]
  - industrial (5) → [warehouse, distribution_center, manufacturing, flex_space, cold_storage]
  - hospitality (2) → [full_service_hotel, limited_service_hotel]
  - educational (5) → [elementary_school, middle_school, high_school, university, community_college]
  - mixed_use (5) → [retail_residential, office_residential, hotel_retail, urban_mixed, transit_oriented]
  - restaurant (5) → [quick_service, full_service, fine_dining, bar_tavern, cafe]
  - specialty (5) → [data_center, laboratory, self_storage, car_dealership, broadcast_facility]
  - civic (5) → [government_building, public_safety, library, community_center, courthouse]
  - recreation (5) → [fitness_center, sports_complex, aquatic_center, recreation_center, stadium]
  - parking (4) → [surface_parking, parking_garage, underground_parking, automated_parking]

### Frontend (buildingTypes.ts)
- Total building types: 11
- Total subtypes: 55
- Per type:
  - restaurant (4) → [qsr, fast_casual, casual_dining, fine_dining]
  - healthcare (5) → [hospital, medical_office, urgent_care, surgery_center, dental_office]
  - residential (5) → [luxury_apartments, market_rate_apartments, affordable_housing, student_housing, condominiums]
  - office (5) → [luxury_apartments, market_rate_apartments, affordable_housing, student_housing, condominiums]
  - industrial (5) → [warehouse, manufacturing, flex_space, cold_storage, data_center]
  - retail (6) → [big_box, strip_center, mall_retail, boutique_retail, grocery, convenience_store]
  - education (6) → [elementary_school, middle_school, high_school, university, vocational_school, daycare]
  - hospitality (5) → [luxury_hotel, full_service_hotel, limited_service_hotel, economy_hotel, boutique_hotel]
  - senior_living (4) → [independent_living, assisted_living, memory_care, skilled_nursing]
  - mixed_use (4) → [retail_residential, office_residential, hotel_retail, full_mixed]
  - specialty (6) → [laboratory, clean_room, sports_facility, theater, parking_garage, religious]

### Mismatches
- In backend not in frontend: ['civic', 'educational', 'multifamily', 'parking', 'recreation']
- In frontend not in backend: ['education', 'residential', 'senior_living']
## Differentiation Knobs (What SHOULD vary by type/subtype)
**A) Cost**
- `base_cost_per_sf`, `cost_range`, `equipment_cost_per_sf`, `typical_floors`
- `trades` (structural/mechanical/etc. percentages)
- `soft_costs`, `soft_costs_pct_of_hard`, `contingency_pct_of_hard`
- `special_features`, `ti_allowance_per_sf`, `development_cost_per_sf_by_finish`

**B) Revenue**
- `base_revenue_per_sf_annual`, `base_revenue_per_unit_monthly`, `base_revenue_per_bed_annual`, `base_revenue_per_room_annual`
- `base_sales_per_sf_annual`, `base_adr_by_market`, `base_occupancy_by_market`
- `units_per_sf`, `beds_per_sf`, `rooms_per_sf`, `students_per_sf`, `visits_per_day`, `procedures_per_day`, `scans_per_day`
- `operating_margin_base/premium`, `operating_expense_per_sf`, `cam_charges_per_sf`, `expense_percentages`

**C) Underwriting / Valuation**
- `ownership_types` (debt ratios, rates, DSCR targets)
- `yield_on_cost_hurdle`, `dscr_target`, `market_cap_rate`, `cap_rate_defaults`, `discount_rate`
- `financial_metrics` (e.g., office rent profiles, hospitality ADR curves)

**D) Regional & Quality**
- `regional_multipliers`, `base_adr_by_market`, `base_occupancy_by_market`
- Finish-level knobs: `development_cost_per_sf_by_finish`, quality/finish overrides (via `resolve_quality_factor`)
- Location overrides (`REGIONAL_OVERRIDES`, `market_factor`), `basis_risk_tolerance_pct`

**E) Output Flags / Operational Metrics**
- `PROJECT_TIMELINES` / `construction_schedule`
- `operational_metrics`, `labor_cost_ratio`, `management_fee_ratio`, `utility_cost_ratio`, etc.
- `department_allocation`, staffing percentages (`staffing_pct_property_mgmt`, `staffing_pct_maintenance`)

## Family-Level Differentiation Summary (Backend)
| building_type | subtype_count | revenue_driver(s) | valuation_method(s) | opex_model | region multipliers | quality/finish | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| healthcare | 7 | per_sf/per_bed/per_room/per_visit | cap_rate/yield_on_cost/discount_rate | Y | cost+rev | Y | hospitals, clinics, labs blend per-bed + per-room economics; includes medical equipment+staff expense ratios |
| multifamily | 5 | per_sf/per_unit | cap_rate/yield_on_cost | Y | cost+rev | Y | apartment stack supports rent-per-unit + occupancy + underwriting targets |
| office | 5 | per_sf/per_unit (floors) | cap_rate/yield_on_cost/discount_rate | Y | cost+rev | Y | Class A/B variants rely on office financial_metrics (rent/NOI per SF) + TI/LC amortization |
| retail | 6 | per_sf/per_unit (shops) | cap_rate/yield_on_cost | Y | cost+rev | Y | Big box vs boutique use sales_per_sf baselines + CAM/opex percentages |
| restaurant | 5 | per_sf/per_unit (seats) | cap_rate/yield_on_cost | Y | cost+rev | Y | QSR vs fine dining use sales_per_sf + per-seat revenue; includes kitchen equipment knobs |
| industrial | 5 | per_sf/per_unit (flex office) | cap_rate/yield_on_cost | Partial | cost+rev | Y | Warehouses/production rely on per_sf revenue or flex-office overlays; some opex overrides for flex |
| hospitality | 5 | ADR/occupancy/per_room | cap_rate/yield_on_cost/discount_rate | Y | cost+rev | Y | Hotels drive ADR × occupancy × room count plus hospitality expense ratios |
| educational | 6 | per_unit (students) | cap_rate/yield_on_cost | Y | cost+rev | Y | Schools rely on per-student revenue + explicit staffing/opex buckets |
| mixed_use | 4 | combo (per_sf + per_unit) | cap_rate/yield_on_cost | Y | cost+rev | Y | Blend of office/retail/residential drivers per scenario |
| specialty | 6 | varied (per_sf/per_visit/per_room) | cap_rate/yield_on_cost | Y | cost+rev | Y | Labs, sports, theaters each with bespoke revenue ratios |
| civic | 5 | none/per_sf (public) | yield_on_cost/break-even | Partial | cost | Y | Government/civic projects focus on cost + minimal revenue, rely on grants |
| recreation | 5 | per_sf/per_visit | cap_rate/yield_on_cost | Partial | cost+rev | Y | Stadiums, gyms, arenas mix ticket/visit revenue with lifestyle expense ratios |
| parking | 3 | per_unit (spaces) | cap_rate/yield_on_cost | Partial | cost+rev | Y | Parking relies on spaces_per_sf + revenue per space; limited opex detail |
