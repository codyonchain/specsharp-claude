# Underwriting Model Map (Deterministic, Canonical)

## Purpose
Define the target-state deterministic underwriting model by `building_type -> subtype`. This map specifies required model form, outputs, and deterministic drivers so subtype underwriting remains explicit and non-blended.

## Non-Negotiables
- One subtype, one primary model form.
- No blended models unless the subtype is explicitly `sum-of-parts`.
- Drivers must be explicit, deterministic inputs/ratios.
- When a required driver is not defined, declare it as `GAP: missing driver input <x>`.

## Civic
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `community_center` | `feasibility` (program/cost/compliance/schedule) | Total cost, cost/SF, schedule risk, compliance risk, program fit, funding fit (if provided). | - Program demand (users served, room counts)<br>- `base_cost_per_sf`, trade mix, soft costs<br>- complexity flags from special features |
| `courthouse` | `feasibility` (program/cost/compliance/schedule) | Total cost, cost/SF, schedule risk, compliance risk, program fit, funding fit (if provided). | - Program demand (courtrooms, security zones)<br>- `base_cost_per_sf`, trade mix, soft costs<br>- complexity flags from special features |
| `government_building` | `feasibility` (program/cost/compliance/schedule) | Total cost, cost/SF, schedule risk, compliance risk, program fit, funding fit (if provided). | - Program demand (department seats, public counters)<br>- `base_cost_per_sf`, trade mix, soft costs<br>- complexity flags from special features |
| `library` | `feasibility` (program/cost/compliance/schedule) | Total cost, cost/SF, schedule risk, compliance risk, program fit, funding fit (if provided). | - Program demand (seats, stacks, learning spaces)<br>- `base_cost_per_sf`, trade mix, soft costs<br>- complexity flags from special features |
| `public_safety` | `feasibility` (program/cost/compliance/schedule) | Total cost, cost/SF, schedule risk, compliance risk, program fit, funding fit (if provided). | - Program demand (apparatus bays, dispatch, holding)<br>- `base_cost_per_sf`, trade mix, soft costs<br>- complexity flags from special features |

## Educational
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `community_college` | `feasibility` (program + budget fit) | Total cost, cost/SF, schedule risk, cost per student, cost per classroom/seat, funding fit (if provided). | - Students and classrooms derived from SF: `students_per_sf`, `classrooms_per_sf`<br>- complexity flags (labs/gyms/shop spaces) from special features<br>- `base_cost_per_sf`, trade mix, soft costs |
| `elementary_school` | `feasibility` (program + budget fit) | Total cost, cost/SF, schedule risk, cost per student, cost per classroom/seat, funding fit (if provided). | - Students and classrooms derived from SF: `students_per_sf`, `classrooms_per_sf`<br>- complexity flags (labs/gyms/shop spaces) from special features<br>- `base_cost_per_sf`, trade mix, soft costs |
| `high_school` | `feasibility` (program + budget fit) | Total cost, cost/SF, schedule risk, cost per student, cost per classroom/seat, funding fit (if provided). | - Students and classrooms derived from SF: `students_per_sf`, `classrooms_per_sf`<br>- complexity flags (labs/gyms/shop spaces) from special features<br>- `base_cost_per_sf`, trade mix, soft costs |
| `middle_school` | `feasibility` (program + budget fit) | Total cost, cost/SF, schedule risk, cost per student, cost per classroom/seat, funding fit (if provided). | - Students and classrooms derived from SF: `students_per_sf`, `classrooms_per_sf`<br>- complexity flags (labs/gyms/shop spaces) from special features<br>- `base_cost_per_sf`, trade mix, soft costs |
| `university` | `feasibility` (program + budget fit) | Total cost, cost/SF, schedule risk, cost per student, cost per classroom/seat, funding fit (if provided). | - Students and classrooms derived from SF: `students_per_sf`, `classrooms_per_sf`<br>- complexity flags (labs/gyms/shop spaces) from special features<br>- `base_cost_per_sf`, trade mix, soft costs |

## Healthcare
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `dental_office` | `throughput model` + `unit economics` | Visits/procedures, annual revenue, margin, DSCR (if debt), yield/payback by strategy. | - Operatories, provider capacity, visits per chair/day<br>- Avg reimbursement per visit/procedure and payer mix<br>- `GAP: missing driver input no-show/cancellation rate` |
| `hospital` | `throughput model` + `unit economics` | Admissions/bed-days, annual revenue, margin, DSCR (if debt), cost per bed-day. | - Beds, occupancy, length of stay<br>- Net revenue per bed-day by acuity/service mix<br>- `GAP: missing driver input case-mix index` |
| `imaging_center` | `throughput model` + `unit economics` | Scans/year, annual revenue, margin, DSCR (if debt), cost per scan room. | - Scan rooms, scans/day, operating days/year<br>- Reimbursement per scan by modality mix<br>- `GAP: missing driver input modality utilization mix` |
| `medical_center` | `sum-of-parts` (service-line level) | Service-line volumes, annual revenue, margin, DSCR (if debt), consolidated feasibility. | - Component service lines (clinic, diagnostics, procedure suites)<br>- Volume and reimbursement per service line<br>- `GAP: missing driver input deterministic component share schema` |
| `medical_office_building` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable SF, rent/SF, vacancy, expense ratio<br>- TI/LC assumptions and lease-up pace<br>- Cap rate and debt terms |
| `nursing_home` | `throughput model` + `unit economics` | Resident-days, annual revenue, margin, DSCR (if debt), cost per resident-day. | - Beds, occupancy, length of stay<br>- Reimbursement per resident-day by payer mix<br>- `GAP: missing driver input care-level mix` |
| `outpatient_clinic` | `throughput model` + `unit economics` | Visits/year, annual revenue, margin, DSCR (if debt), cost per visit. | - Exam rooms, visits/day, operating days/year<br>- Reimbursement per visit by payer mix<br>- `GAP: missing driver input provider productivity factor` |
| `rehabilitation` | `throughput model` + `unit economics` | Therapy sessions/bed-days, annual revenue, margin, DSCR (if debt), cost per treatment day. | - Beds or treatment slots, utilization, length of stay<br>- Reimbursement per treatment day/session<br>- `GAP: missing driver input therapy intensity mix` |
| `surgical_center` | `throughput model` + `unit economics` | Cases/year, annual revenue, margin, DSCR (if debt), cost per OR and per case. | - OR count, cases/OR/day, operating days/year<br>- Reimbursement per case by procedure mix<br>- `GAP: missing driver input block-time utilization` |
| `urgent_care` | `throughput model` + `unit economics` | Visits/year, annual revenue, margin, DSCR (if debt), cost per visit. | - Exam rooms, visits/day, operating days/year<br>- Avg reimbursement per visit and ancillary attach rates<br>- `GAP: missing driver input seasonal demand curve` |

## Hospitality
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `full_service_hotel` | `RevPAR ADR` | ADR, occupancy, RevPAR, room revenue, total NOI, cap-rate value, DSCR (if debt), cost/key. | - Keys, ADR, occupancy, operating days<br>- Ancillary revenue by department and expense ratios<br>- Stabilized cap rate and debt terms |
| `limited_service_hotel` | `RevPAR ADR` | ADR, occupancy, RevPAR, room revenue, total NOI, cap-rate value, DSCR (if debt), cost/key. | - Keys, ADR, occupancy, operating days<br>- Ancillary revenue and department expense ratios<br>- Stabilized cap rate and debt terms |

## Industrial
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `cold_storage` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable SF, rent/SF, vacancy<br>- Refrigeration energy/load cost factors<br>- Lease terms and cap rate |
| `distribution_center` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable SF, rent/SF, vacancy<br>- Clear-height/dock-driven rent adjustments<br>- Lease terms and cap rate |
| `flex_space` | `sum-of-parts` (industrial + office components) | Component EGI/NOI, blended asset NOI, cap-rate value, DSCR (if debt). | - Explicit SF split by component (warehouse vs office)<br>- Component rents, vacancies, expense ratios<br>- `GAP: missing driver input deterministic component split input` |
| `manufacturing` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable SF, rent/SF, vacancy<br>- Utility/power intensity expense factors<br>- Lease terms and cap rate |
| `warehouse` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable SF, rent/SF, vacancy<br>- Rent adjustments from dock/clear-height characteristics<br>- Lease terms and cap rate |

## Mixed Use
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `hotel_retail` | `sum-of-parts` | Component NOI/value by use, aggregate value, blended yield, DSCR (if debt). | - Component SF and share by use type<br>- Component model per use (hotel RevPAR ADR, retail NOI)<br>- `GAP: missing driver input deterministic use-allocation schema` |
| `office_residential` | `sum-of-parts` | Component NOI/value by use, aggregate value, blended yield, DSCR (if debt). | - Component SF and share by use type<br>- Component model per use (office NOI, multifamily NOI)<br>- `GAP: missing driver input deterministic use-allocation schema` |
| `retail_residential` | `sum-of-parts` | Component NOI/value by use, aggregate value, blended yield, DSCR (if debt). | - Component SF and share by use type<br>- Component model per use (retail NOI, multifamily NOI)<br>- `GAP: missing driver input deterministic use-allocation schema` |
| `transit_oriented` | `sum-of-parts` | Component NOI/value by use, aggregate value, blended yield, DSCR (if debt). | - Component SF and share by use type<br>- Component model per use by transit-oriented program<br>- `GAP: missing driver input deterministic use-allocation schema` |
| `urban_mixed` | `sum-of-parts` | Component NOI/value by use, aggregate value, blended yield, DSCR (if debt). | - Component SF and share by use type<br>- Component model per use by program mix<br>- `GAP: missing driver input deterministic use-allocation schema` |

## Multifamily
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `affordable_housing` | `NOI cap rate` | Units, EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Unit mix, rents by unit type, vacancy<br>- Concessions, operating expense ratio, reserves<br>- Cap rate and debt terms |
| `luxury_apartments` | `NOI cap rate` | Units, EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Unit mix, rents by unit type, vacancy<br>- Amenity premium and operating expense ratio<br>- Cap rate and debt terms |
| `market_rate_apartments` | `NOI cap rate` | Units, EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Unit mix, rents by unit type, vacancy<br>- Operating expense ratio and concessions<br>- Cap rate and debt terms |

## Office
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `class_a` | `NOI cap rate` | PGI, EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rent/SF, vacancy/credit loss, opex ratio<br>- TI/LC amortization and lease-up assumptions<br>- Exit cap rate and debt terms |
| `class_b` | `NOI cap rate` | PGI, EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rent/SF, vacancy/credit loss, opex ratio<br>- TI/LC assumptions by repositioning strategy<br>- Exit cap rate and debt terms |

## Parking
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `automated_parking` | `unit economics` | Breakeven utilization, annual cash flow, payback, cash-on-cash, DSCR (if debt). | - Space count, utilization, price per stay/monthly pass mix<br>- Turnover by daypart and operating hours<br>- Opex and maintenance burden by automation level |
| `parking_garage` | `unit economics` | Breakeven utilization, annual cash flow, payback, cash-on-cash, DSCR (if debt). | - Space count, utilization, price per stay/monthly pass mix<br>- Turnover by daypart and operating hours<br>- Opex and maintenance burden |
| `surface_parking` | `unit economics` | Breakeven utilization, annual cash flow, payback, cash-on-cash, DSCR (if debt). | - Space count, utilization, price per stay/monthly pass mix<br>- Turnover by daypart and operating hours<br>- Opex burden and land carry assumptions |
| `underground_parking` | `unit economics` | Breakeven utilization, annual cash flow, payback, cash-on-cash, DSCR (if debt). | - Space count, utilization, price per stay/monthly pass mix<br>- Turnover by daypart and operating hours<br>- Opex and ventilation/life-safety burden |

## Recreation
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `aquatic_center` | `unit economics` | Breakeven attendance, payback, margin, cash-on-cash, DSCR (if debt). | - Daily attendance, admission/membership mix<br>- Program revenue and occupancy by time block<br>- `GAP: missing driver input lane-hour utilization` |
| `fitness_center` | `unit economics` | Breakeven membership, payback, margin, cash-on-cash, DSCR (if debt). | - Membership count, churn, monthly dues<br>- Class/PT attach rates and utilization<br>- `GAP: missing driver input retention cohort curve` |
| `recreation_center` | `unit economics` | Breakeven attendance, payback, margin, cash-on-cash, DSCR (if debt). | - Daily attendance and membership mix<br>- Program utilization by room/court/hour<br>- `GAP: missing driver input program mix schema` |
| `sports_complex` | `unit economics` | Breakeven bookings, payback, margin, cash-on-cash, DSCR (if debt). | - Field/court count, booking hours, rate per slot<br>- Tournament/event cadence and ancillary spend<br>- `GAP: missing driver input deterministic weather-seasonality factor` |
| `stadium` | `unit economics` | Breakeven attendance, payback, margin, cash-on-cash, DSCR (if debt). | - Events/year, attendance/event, avg spend per attendee<br>- Premium seating/sponsorship/parking contributions<br>- `GAP: missing driver input deterministic event calendar profile` |

## Restaurant
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `bar_tavern` | `unit economics` | Breakeven sales, payback, operating margin, cash-on-cash, DSCR (if debt). | - Seats/stools, turns/day, avg check<br>- Daypart demand curve and beverage mix<br>- COGS/labor by food vs beverage mix |
| `cafe` | `unit economics` | Breakeven sales, payback, operating margin, cash-on-cash, DSCR (if debt). | - Transactions/day, avg ticket, operating days/year<br>- Daypart demand curve and takeout mix<br>- Beverage/food mix and labor model |
| `fine_dining` | `unit economics` | Breakeven sales, payback, operating margin, cash-on-cash, DSCR (if debt). | - Seats, turns/day, avg check, operating days/year<br>- Reservation yield and menu mix<br>- Beverage program mix and labor intensity |
| `full_service` | `unit economics` | Breakeven sales, payback, operating margin, cash-on-cash, DSCR (if debt). | - Seats, turns/day, avg check, operating days/year<br>- Daypart demand curve and table-mix assumptions<br>- Beverage mix and labor model |
| `quick_service` | `unit economics` | Breakeven sales, payback, operating margin, cash-on-cash, DSCR (if debt). | - Transactions/day, avg ticket, operating days/year<br>- Daypart demand curve and channel mix (counter/drive-thru/delivery)<br>- Beverage mix and labor model |

## Retail
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `big_box` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Leasable SF, rent/SF, vacancy, recoveries<br>- Lease term and tenant-credit assumptions<br>- Cap rate and debt terms |
| `shopping_center` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Tenant mix, rent/SF by bay, vacancy, recoveries<br>- Small-shop/shop-anchor leasing assumptions<br>- Cap rate and debt terms |

## Specialty
| Subtype | Core model form | Key outputs | Deterministic drivers |
| --- | --- | --- | --- |
| `broadcast_facility` | `unit economics` | Breakeven studio utilization, payback, margin, cash-on-cash, DSCR (if debt). | - Studio/control-room hours sold, rate per hour<br>- Utilization by production type and daypart<br>- `GAP: missing driver input deterministic booking profile` |
| `car_dealership` | `unit economics` | Breakeven gross profit, payback, margin, cash-on-cash, DSCR (if debt). | - Vehicle sales volume by category, gross per unit<br>- Service-bay throughput and parts/labor mix<br>- `GAP: missing driver input deterministic inventory turn factor` |
| `data_center` | `throughput model` + `unit economics` | kW/MW sold, annual revenue, NOI, payback, DSCR (if debt), yield. | - Critical load sold (kW or MW), price per kW-month<br>- PUE/energy cost and uptime SLA tier<br>- `GAP: missing driver input deterministic power-ramp curve` |
| `laboratory` | `NOI cap rate` | EGI, NOI, cap-rate value, yield-on-cost, DSCR (if debt). | - Rentable lab SF, rent/SF, vacancy<br>- Expense load for lab infrastructure and compliance<br>- Cap rate and debt terms |
| `self_storage` | `unit economics` | Breakeven occupancy, payback, margin, cash-on-cash, DSCR (if debt). | - Unit count by size tier, rent per unit tier, occupancy<br>- Move-in/move-out/churn assumptions<br>- `GAP: missing driver input deterministic unit-size mix schema` |
