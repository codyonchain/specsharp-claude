# Subtype: Library (Civic)

## Underwriting overrides vs base type
- Financing and compatibility requirements intentionally mirror `community_center` (`backend/app/v2/config/subtypes/civic/community_center.py`): Government and Non-Profit ownership paths are enabled, with no incompatible project classes.
- Library trade emphasis is shifted toward stack load capacity, acoustics, daylighting controls, community-room flexibility, and maker-space MEP intensity.
- Revenue and operating assumptions remain civic/non-revenue (`base_revenue_per_sf_annual=0`, occupancy and margins fixed at civic defaults).

## Deterministic drivers (explicit inputs override defaults)
- Trade mix from `backend/app/v2/config/subtypes/civic/library.py`:
  - Structural 0.28
  - Mechanical 0.25
  - Electrical 0.16
  - Plumbing 0.13
  - Finishes 0.18
- Special features from subtype config:
  - `stacks_load_reinforcement`
  - `acoustic_treatment`
  - `daylighting_controls`
  - `community_rooms`
  - `maker_space_mep`
- Location/regional multipliers when city is provided.

---

## Block A - Decision & KPI framing (DealShield front door)

### Decision moment
Library projects are evaluated on deterministic cost, schedule, and financing fit (not operating yield). The project should move forward only when stack loading, acoustic performance, daylighting intent, community room program, and maker-space MEP scope are all explicit and funded.

### Go / Reprice / Rescope / Walk
- Go: Core civic program and the five trust-critical drivers are defined and funded.
- Reprice: Scope is valid but base cost or feature adders need budget updates.
- Rescope: Program elements are unclear (for example maker-space utility density or community-room count) and require scope tightening.
- Walk: Funding structure cannot cover required structural/MEP performance.

### Confidence band drivers (library-specific)
- Stack loading assumptions for dense collections and archive zones.
- Acoustic separation expectations between quiet reading zones and active spaces.
- Daylighting strategy (glazing, glare control, daylight-linked controls).
- Community room count and flexibility requirements.
- Maker-space ventilation, power density, and specialty plumbing needs.

### Provenance pointers
- Subtype config: `backend/app/v2/config/subtypes/civic/library.py`.
- Reference requirements pattern: `backend/app/v2/config/subtypes/civic/community_center.py`.
- Global finish and cost factor mechanics: `backend/app/v2/config/master_config.py`.

---

## Block B - ConstructionView Trade Summary (Critical)

### Structural
- Included scope: baseline structure plus stack-load reinforcement allowances.
- Watch items: floor live-load assumptions in stack-heavy zones and archive areas.
- Validation questions: Which areas require high-density shelving loads? Are any slab/framing upgrades expected?

### Mechanical
- Included scope: baseline HVAC with higher emphasis for mixed quiet/activity programming.
- Watch items: zoning for community rooms and ventilation/thermal control in maker areas.
- Validation questions: Are maker spaces conditioned as standard classrooms or as higher-load workshops?

### Electrical
- Included scope: baseline power and lighting with added control complexity.
- Watch items: daylighting controls, AV for community rooms, and higher receptacle density in maker zones.
- Validation questions: What is the expected maker-space plug/process load? Is dimming/daylight control required throughout reading areas?

### Plumbing
- Included scope: baseline domestic and sanitary systems.
- Watch items: any sink/process plumbing tied to maker-space curriculum.
- Validation questions: Do maker areas need dedicated utility sinks, floor drains, or specialty waste handling?

### Finishes
- Included scope: standard civic interior finishes.
- Watch items: acoustic treatments are expected as explicit feature adders, not assumed in baseline finishes.
- Validation questions: Which rooms require speech privacy or high STC/NRC performance?

### Trade distribution rule
- ConstructionView trade percentages must come directly from deterministic trade outputs; do not infer alternate splits.

---

## Block C - ExecutiveView checklist (deterministic vs input)
- Financing structure: Deterministic from subtype ownership terms; matches community-center requirement pattern.
- Total project cost and soft costs: Deterministic from subtype cost stack and selected features.
- Sensitivity checks: Deterministic scenario stress should still be shown for cost-side variance.
- Program adequacy narrative: Requires input for stack loads, acoustic targets, daylight intent, community-room count, and maker-space MEP requirements.
- Key milestones and delivery risk: Requires input if schedule acceleration or phasing is requested.

---

## Block D - Assumptions & Question Bank

### Ranked assumptions
1. Stack-heavy zones are identified early and structurally accommodated.
2. Acoustic targets are defined between quiet reading and active collaboration areas.
3. Daylighting strategy is coordinated with glare control and lighting controls.
4. Community room program (count, size, flexibility) is known at concept stage.
5. Maker-space MEP needs are explicit and not treated as generic classroom loads.

### Most likely wrong (top 3)
1. Stack load assumptions are too low for final shelving density.
2. Maker-space mechanical/electrical/plumbing scope is understated.
3. Acoustic separation requirements are discovered late and force redesign.

### Question bank (driver-tied)
1. Which areas require dense stacks or archival storage? Driver: `stacks_load_reinforcement`.
2. What acoustic criteria apply to reading rooms and adjacent active spaces? Driver: `acoustic_treatment`.
3. Is daylighting control required in reading areas and community rooms? Driver: `daylighting_controls`.
4. How many community rooms are required, and what AV/flex use is expected? Driver: `community_rooms`.
5. What maker-space utilities are required (ventilation, power, sinks/process plumbing)? Driver: `maker_space_mep`.
