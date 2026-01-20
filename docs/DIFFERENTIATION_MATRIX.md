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

## Engine Consumption Proof (UnifiedEngine)

- Master config binding → unified_engine.py: sets self.config = MASTER_CONFIG (~183) and later pulls subtype_config = MASTER_CONFIG[building_enum].get(subtype) (~1712–1727).
- Subtype normalization/routing → normalizes subtype from dict/enums at entry (~287–298, ~460–462).
- Config lookup + validation → building_config = get_building_config(building_type, subtype) (~300–306) and validate_project_class(building_type, subtype, project_class) (~306).
- Finish level inference + quality factor → resolve_quality_factor(normalized_finish_level, building_type, subtype) (~249–273).
- Regional context + cost/revenue separation → resolve_location_context(location) (~386); cost uses cost_factor/regional_multiplier_effective (~379–387); revenue uses revenue_factor/market_factor (~1746–1794, ~2281–2293).
- Construction cost pipeline → base_cost_per_sf from building_config.base_cost_per_sf (~315) → complexity/project class multipliers (~341–345) → regional + finish multipliers (~376–387) → construction_cost (~397).
- Equipment cost (subtype-configured) → equipment_cost_per_sf * finish_cost_factor * sf (~399–401).
- Special feature adders → building_config.special_features[feature] influences cost (~414).
- Revenue driver selection by type → _calculate_revenue_by_type branches and uses subtype_config fields (healthcare per bed/visit/procedure/scan/SF ~2295–2339; multifamily per unit ~2339–2343; hospitality ADR×occ×rooms ~2352–2360, ~2569–2679; office financial profile ~2365–2390, ~2523–2566; educational per student ~2392–2397; parking per space ~2399–2403; restaurant per seat or per SF ~2407–2411; industrial/default per SF + flex blending ~2419–2462).
- Finish-level revenue adjustments (selective) → full-service restaurant finish maps (~2464–2488).
- Margin/expenses model → margin_pct from modifiers or get_margin_pct (~1747–1826) with subtype overrides like operating_expense_per_sf/cam/staffing (office ~1753–1759) and hospitality expense pct (~1808–1865).
- NOI selection for financing consistency → prefers noi_from_revenue else fallback method (~1577–1601).
- Valuation/returns backend-owned → get_exit_cap_and_discount_rate (~2741–2769), terminal value net_income/exit_cap_rate (~1961–1967), NPV/IRR via calculate_npv/calculate_irr (~1974–1992, ~2810–2873), payback total_cost/net_income (~2003–2004).

## Family-Level Differentiation (Evidence-Based)

| building_type | subtype_count | revenue_knobs_present | margin/expense_knobs_present | valuation_knobs_present | cost_knobs_present | region/quality_knobs_present | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| healthcare | 10 | per_sf, per_bed, per_visit | margin_base/premium, labor_ratio, equipment_lease | ownership, dscr, yield_on_cost | base_cost, equipment_cost, soft_costs, special_features, contingency/TI | regional, basis_risk | Healthcare stores per-bed/visit revenue plus layered labor + leasing expense ratios. |
| multifamily | 3 | per_sf, per_unit | margin_base/premium, property_tax, reserves | cap_rate, ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Multifamily relies on per-unit rents with property_tax/reserve expense toggles. |
| office | 2 | per_sf | margin_base/premium, opex_per_sf, cam, staffing_pct | cap_rate, ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Office keeps per-sf rents with explicit CAM/opex and staffing percentages. |
| retail | 2 | per_sf, sales_per_sf | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Retail captures per-sf + sales_per_sf revenue with simple margin bands. |
| restaurant | 5 | per_sf | margin_base/premium, food/beverage, franchise_ratio | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Restaurant entries mix per-sf revenue with food/beverage/franchise expense ratios. |
| industrial | 5 | per_sf | margin_base/premium, labor_ratio, property_tax, monitoring | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Industrial keeps per-sf revenue plus labor/property_tax/monitoring expense overrides. |
| hospitality | 2 | ADR, per_room, per_sf | margin_base/premium, expense_percentages, franchise_ratio | ownership, dscr, yield_on_cost, cap_rate_defaults | base_cost, equipment_cost, soft_costs, special_features | regional, ADR, occupancy, finish_costs | Hospitality carries ADR/occupancy tables with expense_pct mixes and underwriting hurdles. |
| educational | 5 | per_sf, per_student | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Educational subtypes expose per-student density revenue with basic margin knobs. |
| mixed_use | 5 | per_sf | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Mixed_use configs only flag per-sf revenue with standard ownership + cost knobs. |
| specialty | 5 | per_sf | margin_base/premium, labor_ratio, connectivity | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Specialty stack retains per-sf revenue plus niche expense knobs (labor/connectivity). |
| civic | 5 | per_sf | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Civic entries store per-sf cost focus with only basic margin toggles. |
| recreation | 5 | per_sf, per_seat | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Recreation mixes per-sf and per-seat density controls with simple margin bands. |
| parking | 4 | per_sf, per_space | margin_base/premium | ownership | base_cost, equipment_cost, soft_costs, special_features | regional | Parking explicitly sets per-space revenue and standard ownership/cost knobs. |
