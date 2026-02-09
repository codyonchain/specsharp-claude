# Underwriting Model Map (Deterministic, Canonical)

## Purpose
Provide one deterministic underwriting map from `building_type -> subtype -> model form` so subtype behavior stays explicit and non-blended. Constants can be calibrated later; model form must be fixed.

## Non-Negotiables
- No blended models inside a subtype. Each subtype has one primary model form.
- Allowed primary forms: `NOI cap rate`, `RevPAR ADR`, `throughput model`, `unit economics`, `sum-of-parts`, `feasibility`.
- If the intended form is not fully implemented yet, mark it as `Not modeled` explicitly.
- Deterministic drivers must come from subtype config + global multipliers (`cost_factor`, `market_factor`, finish/quality), not ad hoc logic.

## Civic
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `community_center` | Public `feasibility` (educational/civic): cost-first; revenue underwriting disabled (`annual_revenue = 0`). | Total project cost, cost/SF, soft-cost burden, funding requirement, schedule risk. | - `base_cost_per_sf`, `trades`, `soft_costs`<br>- `special_features` and contingency<br>- global regional + finish multipliers |
| `courthouse` | Public `feasibility` (educational/civic): cost-first; revenue underwriting disabled (`annual_revenue = 0`). | Total project cost, cost/SF, soft-cost burden, funding requirement, schedule risk. | - `base_cost_per_sf`, `trades`, `soft_costs`<br>- `special_features` and contingency<br>- global regional + finish multipliers |
| `government_building` | Public `feasibility` (educational/civic): cost-first; revenue underwriting disabled (`annual_revenue = 0`). | Total project cost, cost/SF, soft-cost burden, funding requirement, schedule risk. | - `base_cost_per_sf`, `trades`, `soft_costs`<br>- `special_features` and contingency<br>- global regional + finish multipliers |
| `library` | Public `feasibility` (educational/civic): cost-first; revenue underwriting disabled (`annual_revenue = 0`). | Total project cost, cost/SF, soft-cost burden, funding requirement, schedule risk. | - `base_cost_per_sf`, `trades`, `soft_costs`<br>- `special_features` and contingency<br>- global regional + finish multipliers |
| `public_safety` | Public `feasibility` (educational/civic): cost-first; revenue underwriting disabled (`annual_revenue = 0`). | Total project cost, cost/SF, soft-cost burden, funding requirement, schedule risk. | - `base_cost_per_sf`, `trades`, `soft_costs`<br>- `special_features` and contingency<br>- global regional + finish multipliers |

## Educational
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `community_college` | Educational `feasibility` proxy with per-student throughput: `students = sf * students_per_sf`; proxy revenue = `students * revenue_per_student`. | Students served (proxy), annual proxy revenue, NOI proxy, DSCR/yield gates, cost per student proxy. | - `students_per_sf`, `base_revenue_per_student_annual`<br>- `operating_margin_base/premium`<br>- type profile gates (`target_yield`, `target_dscr`) |
| `elementary_school` | Educational `feasibility` proxy with per-student throughput: `students = sf * students_per_sf`; proxy revenue = `students * revenue_per_student`. | Students served (proxy), annual proxy revenue, NOI proxy, DSCR/yield gates, cost per student proxy. | - `students_per_sf`, `base_revenue_per_student_annual`<br>- `operating_margin_base/premium`<br>- type profile gates (`target_yield`, `target_dscr`) |
| `high_school` | Educational `feasibility` proxy with per-student throughput: `students = sf * students_per_sf`; proxy revenue = `students * revenue_per_student`. | Students served (proxy), annual proxy revenue, NOI proxy, DSCR/yield gates, cost per student proxy. | - `students_per_sf`, `base_revenue_per_student_annual`<br>- `operating_margin_base/premium`<br>- type profile gates (`target_yield`, `target_dscr`) |
| `middle_school` | Educational `feasibility` proxy with per-student throughput: `students = sf * students_per_sf`; proxy revenue = `students * revenue_per_student`. | Students served (proxy), annual proxy revenue, NOI proxy, DSCR/yield gates, cost per student proxy. | - `students_per_sf`, `base_revenue_per_student_annual`<br>- `operating_margin_base/premium`<br>- type profile gates (`target_yield`, `target_dscr`) |
| `university` | Educational `feasibility` proxy with per-student throughput: `students = sf * students_per_sf`; proxy revenue = `students * revenue_per_student`. | Students served (proxy), annual proxy revenue, NOI proxy, DSCR/yield gates, cost per student proxy. | - `students_per_sf`, `base_revenue_per_student_annual`<br>- `operating_margin_base/premium`<br>- type profile gates (`target_yield`, `target_dscr`) |

## Healthcare
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `dental_office` | `Throughput model` with `unit economics` overlays; primary revenue currently per-SF lease/operations proxy. | Annual revenue, NOI, DSCR, yield-on-cost, per-operatory unit metrics. | - `base_revenue_per_sf_annual`<br>- `financial_metrics.units_per_sf` and `revenue_per_unit_annual` (overlay)<br>- subtype expense ratios and financing terms |
| `hospital` | Bed-based `throughput model`: `beds = sf * beds_per_sf`; revenue = `beds * revenue_per_bed_annual`. | Annual revenue, NOI, DSCR, yield-on-cost, bed-count and per-bed economics. | - `beds_per_sf`, `base_revenue_per_bed_annual`<br>- `operating_margin_base/premium` and cost ratios<br>- type profile gates (`target_yield`, `target_dscr`) |
| `imaging_center` | `Throughput model` with `unit economics` overlays; primary revenue currently per-SF proxy (`Not modeled`: per-scan throughput as primary). | Annual revenue, NOI, DSCR, yield-on-cost, scan-room unit metrics. | - `base_revenue_per_sf_annual`<br>- `financial_metrics.units_per_sf` and per-unit economics (overlay)<br>- subtype expense ratios and financing terms |
| `medical_center` | Healthcare operating model using per-SF revenue proxy (NOI-focused). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. | - `base_revenue_per_sf_annual`<br>- occupancy and margin settings<br>- subtype cost ratios + financing terms |
| `medical_office_building` | MOB lease-style `NOI cap rate` model: per-SF revenue with explicit MOB NOI context. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, per-unit MOB metrics. | - `base_revenue_per_sf_annual`<br>- `operating_margin_base` and occupancy<br>- `financial_metrics` unit overlays + type profile gates |
| `nursing_home` | Bed-based `throughput model`: `beds = sf * beds_per_sf`; revenue = `beds * revenue_per_bed_annual`. | Annual revenue, NOI, DSCR, yield-on-cost, bed-count and per-bed economics. | - `beds_per_sf`, `base_revenue_per_bed_annual`<br>- `operating_margin_base/premium` and expense ratios<br>- subtype financing terms |
| `outpatient_clinic` | Visit-based `throughput model`: revenue = `visits_per_day * days_per_year * revenue_per_visit`. | Annual revenue, NOI, DSCR, yield-on-cost, visit-volume unit economics. | - `base_revenue_per_visit`, `visits_per_day`, `days_per_year`<br>- outpatient `financial_metrics` per-unit overlays<br>- subtype expense ratios + financing terms |
| `rehabilitation` | Bed-based `throughput model`: `beds = sf * beds_per_sf`; revenue = `beds * revenue_per_bed_annual`. | Annual revenue, NOI, DSCR, yield-on-cost, bed-count and per-bed economics. | - `beds_per_sf`, `base_revenue_per_bed_annual`<br>- `operating_margin_base/premium` and expense ratios<br>- subtype financing terms |
| `surgical_center` | `Throughput model` with OR `unit economics` overlays; primary revenue currently per-SF proxy (`Not modeled`: per-procedure throughput as primary). | Annual revenue, NOI, DSCR, yield-on-cost, per-OR unit metrics. | - `base_revenue_per_sf_annual`<br>- `financial_metrics.units_per_sf` and per-unit economics (overlay)<br>- subtype expense ratios + financing terms |
| `urgent_care` | Visit-based `throughput model`: revenue = `visits_per_day * days_per_year * revenue_per_visit`. | Annual revenue, NOI, DSCR, yield-on-cost, visit-volume unit economics. | - `base_revenue_per_visit`, `visits_per_day`, `days_per_year`<br>- outpatient `financial_metrics` per-unit overlays<br>- subtype expense ratios + financing terms |

## Hospitality
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `full_service_hotel` | `RevPAR ADR` model: `room_revenue = rooms * ADR * occupancy * 365`; then expense stack to NOI. | Rooms/keys, ADR, occupancy, RevPAR ADR, annual room revenue, NOI, DSCR, yield-on-cost, cost/key. | - `rooms_per_sf` or explicit `rooms/keys`<br>- ADR and occupancy defaults/overrides<br>- margin/expense ratios, cap-rate and DSCR gates |
| `limited_service_hotel` | `RevPAR ADR` model: `room_revenue = rooms * ADR * occupancy * 365`; deterministic expense profile applied. | Rooms/keys, ADR, occupancy, RevPAR ADR, annual room revenue, NOI, DSCR, yield-on-cost, cost/key. | - `rooms_per_sf` or explicit `rooms/keys`<br>- `base_adr_by_market`, `base_occupancy_by_market`<br>- `expense_percentages`, cap-rate defaults, DSCR/yield gates |

## Industrial
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `cold_storage` | `NOI cap rate` model with NNN-style per-SF rent and subtype expense profile. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and enforced `operating_margin_base`<br>- utility/labor/maintenance ratios + financing terms |
| `distribution_center` | `NOI cap rate` model with NNN-style per-SF rent. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and enforced `operating_margin_base`<br>- subtype cost ratios + financing terms |
| `flex_space` | `NOI cap rate` model with deterministic office-share uplift (`Not blended` beyond explicit `office_share` input). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, flex revenue/SF trace. | - `base_revenue_per_sf_annual`<br>- optional `office_share` uplift path<br>- occupancy, enforced margin, subtype expense ratios |
| `manufacturing` | `NOI cap rate` model with NNN-style per-SF rent. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and enforced `operating_margin_base`<br>- subtype cost ratios + financing terms |
| `warehouse` | `NOI cap rate` model with NNN-style per-SF rent. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and enforced `operating_margin_base`<br>- subtype cost ratios + financing terms |

## Mixed Use
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `hotel_retail` | Intended model: `sum-of-parts` by component. Current runtime: per-SF NOI proxy (`Not modeled`: explicit component decomposition). | Current: annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. Target: component NOI + aggregate value. | - current `base_revenue_per_sf_annual`, occupancy, margins<br>- current subtype financing/cost profile<br>- target component shares/drivers are `Not modeled` |
| `office_residential` | Intended model: `sum-of-parts` by component. Current runtime: per-SF NOI proxy (`Not modeled`: explicit component decomposition). | Current: annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. Target: component NOI + aggregate value. | - current `base_revenue_per_sf_annual`, occupancy, margins<br>- current subtype financing/cost profile<br>- target component shares/drivers are `Not modeled` |
| `retail_residential` | Intended model: `sum-of-parts` by component. Current runtime: per-SF NOI proxy (`Not modeled`: explicit component decomposition). | Current: annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. Target: component NOI + aggregate value. | - current `base_revenue_per_sf_annual`, occupancy, margins<br>- current subtype financing/cost profile<br>- target component shares/drivers are `Not modeled` |
| `transit_oriented` | Intended model: `sum-of-parts` by component. Current runtime: per-SF NOI proxy (`Not modeled`: explicit component decomposition). | Current: annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. Target: component NOI + aggregate value. | - current `base_revenue_per_sf_annual`, occupancy, margins<br>- current subtype financing/cost profile<br>- target component shares/drivers are `Not modeled` |
| `urban_mixed` | Intended model: `sum-of-parts` by component. Current runtime: per-SF NOI proxy (`Not modeled`: explicit component decomposition). | Current: annual revenue, NOI, DSCR, yield-on-cost, cap-rate value. Target: component NOI + aggregate value. | - current `base_revenue_per_sf_annual`, occupancy, margins<br>- current subtype financing/cost profile<br>- target component shares/drivers are `Not modeled` |

## Multifamily
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `affordable_housing` | Unit-rent `NOI cap rate` model: `units = sf * units_per_sf`; revenue = `units * monthly_rent * 12`. | Units, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, revenue per unit. | - `units_per_sf`, `base_revenue_per_unit_monthly`<br>- occupancy and operating margin settings<br>- subtype financing terms and type profile gates |
| `luxury_apartments` | Unit-rent `NOI cap rate` model: `units = sf * units_per_sf`; revenue = `units * monthly_rent * 12`. | Units, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, revenue per unit. | - `units_per_sf`, `base_revenue_per_unit_monthly`<br>- occupancy and operating margin settings<br>- subtype financing terms and type profile gates |
| `market_rate_apartments` | Unit-rent `NOI cap rate` model: `units = sf * units_per_sf`; revenue = `units * monthly_rent * 12`. | Units, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, revenue per unit. | - `units_per_sf`, `base_revenue_per_unit_monthly`<br>- occupancy and operating margin settings<br>- subtype financing terms and type profile gates |

## Office
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `class_a` | Full office `NOI cap rate` model: PGI -> vacancy/credit loss -> EGI -> NOI with TI/LC amortization. | PGI, EGI, NOI, rent/SF, NOI margin, DSCR, yield-on-cost, cap-rate value, payback. | - `financial_metrics` profile (`base_rent_per_sf`, vacancy, opex, TI, LC)<br>- optional `operating_expense_per_sf` and `cam_charges_per_sf` overrides<br>- type profile cap-rate/yield/DSCR gates |
| `class_b` | Office `NOI cap rate` model using deterministic per-SF revenue/margin path (`Not modeled`: Class A TI/LC underwriting profile). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |

## Parking
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `automated_parking` | Per-space `NOI cap rate` model: `spaces = sf * spaces_per_sf`; revenue = `spaces * revenue_per_space_monthly * 12`. | Spaces, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, cost per space. | - `spaces_per_sf`, `base_revenue_per_space_monthly`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `parking_garage` | Per-space `NOI cap rate` model: `spaces = sf * spaces_per_sf`; revenue = `spaces * revenue_per_space_monthly * 12`. | Spaces, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, cost per space. | - `spaces_per_sf`, `base_revenue_per_space_monthly`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `surface_parking` | Per-space `NOI cap rate` model: `spaces = sf * spaces_per_sf`; revenue = `spaces * revenue_per_space_monthly * 12`. | Spaces, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, cost per space. | - `spaces_per_sf`, `base_revenue_per_space_monthly`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `underground_parking` | Per-space `NOI cap rate` model: `spaces = sf * spaces_per_sf`; revenue = `spaces * revenue_per_space_monthly * 12`. | Spaces, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, cost per space. | - `spaces_per_sf`, `base_revenue_per_space_monthly`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |

## Recreation
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `aquatic_center` | Recreation operating model using per-SF revenue proxy (NOI-focused). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and margin settings<br>- subtype expense ratios + financing terms |
| `fitness_center` | Recreation operating model using per-SF revenue proxy (NOI-focused). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and margin settings<br>- subtype expense ratios + financing terms |
| `recreation_center` | Recreation operating model using per-SF revenue proxy (NOI-focused). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and margin settings<br>- subtype expense ratios + financing terms |
| `sports_complex` | Recreation operating model using per-SF revenue proxy (NOI-focused). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and margin settings<br>- subtype expense ratios + financing terms |
| `stadium` | Seat-based `throughput model`: `seats = sf * seats_per_sf`; revenue = `seats * revenue_per_seat_annual`. | Seats, annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, revenue per seat. | - `seats_per_sf`, `base_revenue_per_seat_annual`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |

## Restaurant
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `bar_tavern` | Restaurant `NOI cap rate` operating model using per-SF sales/revenue. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype food/labor/utility expense ratios |
| `cafe` | Restaurant `NOI cap rate` operating model using per-SF sales/revenue. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype food/labor/utility expense ratios |
| `fine_dining` | Restaurant `NOI cap rate` operating model using per-SF sales/revenue. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype food/labor/utility expense ratios |
| `full_service` | Restaurant `NOI cap rate` model with deterministic finish-level multipliers for revenue/occupancy/margin. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, finish-adjusted sensitivity. | - `base_revenue_per_sf_annual`<br>- `finish_level_multipliers` for revenue/occupancy/margin<br>- subtype expense ratios + financing terms |
| `quick_service` | Restaurant `NOI cap rate` operating model using per-SF sales/revenue. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype food/labor/utility expense ratios |

## Retail
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `big_box` | Retail `NOI cap rate` model using per-SF revenue and deterministic margin profile. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype financing terms + type profile gates |
| `shopping_center` | Retail `NOI cap rate` model using per-SF revenue and deterministic margin profile. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype financing terms + type profile gates |

## Specialty
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `broadcast_facility` | Specialty operating `NOI cap rate` model with per-SF revenue proxy. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `car_dealership` | Specialty operating `NOI cap rate` model with per-SF revenue proxy. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `data_center` | Specialty `NOI cap rate` model with per-SF revenue proxy (`Not modeled`: explicit MW/IT-load throughput). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- utility/connectivity/security ratios + financing terms |
| `laboratory` | Specialty operating `NOI cap rate` model with per-SF revenue proxy. | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype expense ratios + financing terms |
| `self_storage` | Specialty `NOI cap rate` model with per-SF proxy (`Not modeled`: explicit unit-mix and in-place occupancy ladder). | Annual revenue, NOI, DSCR, yield-on-cost, cap-rate value, operating efficiency. | - `base_revenue_per_sf_annual`<br>- occupancy and operating margins<br>- subtype financing terms + expense ratios |

