## Non-negotiable Invariants
- NLP is config-driven: patterns auto-generated from master_config (types/subtypes), priority: specific→general, phrase→word; numbers parse with/without commas.
- Regional multipliers are centralized, not per building type. City+State required for non-default; city-only ⇒ 1.0 + warning.
- Cost and revenue use distinct regional factors when configured; never auto-reuse cost factor for revenue.
- FinishLevel/quality is honored end-to-end (frontend → API → engine); no silent overrides.
- Special-features math respects unit types (per-unit vs per-SF).
- Restaurant clamp (250–700 $/SF) is explicit/flagged or removed; never silent.
- NOI = Revenue − OPEX (derived), not a fixed %.
- Cap-rate valuation applies only to types that use it (MF, office, retail, industrial, storage, DC). Others use DCF/sales multiples as configured.
- Cost buildup UI uses dynamic {location} label (no hardcoded “Nashville, TN Market”).
- Timelines are calculated (no hardcoded dates).

## Golden Cases (TN / NH focus)
A) 5,000 sf full_service_restaurant — Nashville, TN  
B) 50,000 sf class A office — Nashville, TN  
C) 75,000 sf warehouse + 10% office — Nashville, TN  
D) 65,000 sf middle_school (800 students) — Bedford, NH  
E) 120,000 sf warehouse (24 docks) — La Vergne, TN

Assert totals (cost, revenue, NOI, ROI, payback), and which regional multipliers were used (cost vs revenue).

## Fix/Issue Themes
- NLP: auto-generate patterns from master_config; priority rules; numeric regex handles 1,000 / 1000.
- Regional: new centralized multiplier system; remove per-type multipliers.
- Valuation: cap-rate logic only for MF/office/retail/industrial/storage/data-centers; others use RevPAR/sales multiples/DCF.
- Margins: set explicit margin per type; base & premium aligned until real quality model is in place.
- FinishLevel: frontend must send finishLevel; backend must apply quality_factor deterministically.
- Restaurants: corrected expense ratios and expense-driven NOI; clamp behavior explicit/flagged.
- UI labels: dynamic location label; dynamic milestone timelines.
