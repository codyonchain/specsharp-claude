# Subtype: Public Safety Facility (Civic)

## A) Decision / KPIs (Feasibility)
Decision intent: determine GO / RESCOPE / REPRICE / WALK from deterministic feasibility outputs.

Primary outputs:
- Cost feasibility: total project cost and cost/SF from subtype trade mix + soft costs.
- Schedule risk: timeline confidence driven by permitting, security coordination, and long-lead emergency systems.
- Compliance risk: life-safety, emergency-response operations, secure circulation, and detention-code exposure.
- Program fit: whether apparatus bay operations, dispatch, backup power, and detention functions match intended use.

## B) Construction (Top Scope Drivers)
- Apparatus bay performance: structural slab loads, bay clear heights/depths, turning geometry, and overhead door clearances.
- Exhaust capture and MEP: source-capture vehicle exhaust systems, makeup air, and bay pressure/ventilation strategy.
- Electrical resilience: emergency generator sizing, ATS topology, critical branch distribution, and runtime/fuel logistics.
- Dispatch and secure operations: hardened dispatch center, 24/7 controls/communications, and secure circulation between zones.
- Detention interfaces: sally port routing, holding/detention room requirements, ligature-resistant details, and controlled egress.

Special features status:
- Modeled (config adders): `apparatus_bay`, `dispatch_center`, `training_tower`, `emergency_generator`, `sally_port`.
- Not modeled explicitly: full detention pod buildout, ballistic/hardening packages beyond baseline, regional radio/network backbone upgrades, and major off-site utility relocation.

## C) Assumptions / Trust
Not modeled (must be treated as external scope or overrides):
- Land acquisition, financing fees beyond configured soft-cost rates, and owner FF&E programs.
- Deep geotech/foundation anomalies, environmental remediation, and major off-site civil upgrades.
- Operating policy/staffing model for emergency response and detention operations beyond baseline feasibility math.

Must confirm before investment committee:
- Apparatus fleet assumptions (vehicle count, dimensions, bay clearances, and maneuvering criteria).
- Exhaust capture basis (tailpipe/source capture approach, ventilation rates, and controls integration).
- Backup power scope (critical load list, redundancy target, runtime requirement, and fuel storage constraints).
- Dispatch program (console count, IT/AV/radio redundancy, and resilience standards).
- Detention and secure-custody requirements (sally port workflow, holding durations, and AHJ standards).

## D) Provenance
Profiles wired for this subtype:
- DealShield tile profile: `civic_baseline_v1`.
- DealShield content profile: `civic_baseline_v1`.
- Scope items profile: `civic_baseline_structural_v1`.

What would change fastest:
- Fleet and apparatus-bay planning changes (vehicle size/count and clearance assumptions).
- Emergency power and dispatch resilience requirements from owner/AHJ policy.
- Detention/security scope shifts from jurisdictional review and operations policy.
