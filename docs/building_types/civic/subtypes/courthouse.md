# Subtype: Courthouse (Civic)

## A) Decision / KPIs (Feasibility)
Decision intent: determine GO / RESCOPE / REPRICE / WALK from deterministic feasibility outputs.

Primary outputs:
- Cost feasibility: total project cost and cost/SF from subtype trade mix + soft costs + explicit security adders.
- Schedule risk: timeline confidence driven by permitting, security coordination, and long-lead life-safety/electrical gear.
- Compliance risk: life-safety, secure circulation, detention interfaces, and jurisdictional courthouse security standards.
- Program fit: whether courtroom program and security operations (screening, holding, transport) match intended use.

## B) Construction (Top Scope Drivers)
- Security zones: separation of public, staff/judicial, and in-custody circulation paths drives core planning and rework risk.
- Holding/detention flow: holding cell count and transfer workflow drive plumbing, ventilation, hardware, and supervision layouts.
- Magnetometer screening: lane count and peak throughput assumptions drive lobby geometry, low-voltage, and queuing performance.
- Sallyport operations: secure vehicle transfer and controlled ingress drive structural/interface scope and sequencing.
- Ballistic considerations: rated glazing/doors and protected-zone hardening can materially shift envelope and finish packages.
- Redundancy: backup power and continuity requirements for life-safety/security systems can shift electrical architecture and cost.

Special features status:
- Modeled (config adders): `courtroom`, `jury_room`, `holding_cells`, `judges_chambers`, `security_screening`, `magnetometer_screening_lanes`, `sallyport`, `ballistic_glazing_package`, `redundant_life_safety_power`.
- Not modeled explicitly: full detention pod buildout, off-site utility relocations, perimeter anti-ram civil works, and broad owner technology/FF&E programs.

## C) Assumptions / Trust
Not modeled (must be treated as external scope or overrides):
- Land acquisition, financing fees beyond configured soft-cost rates, and owner FF&E programs.
- Deep geotech/foundation anomalies, environmental remediation, and major off-site civil upgrades.
- Staffing/operations policy assumptions (screening staffing, detainee movement policy, court scheduling policy) beyond baseline feasibility math.

Must confirm before investment committee:
- Security-zone matrix and approved circulation strategy (public/staff/in-custody).
- Holding capacity, detainee transfer workflow, and detention-related AHJ/security requirements.
- Magnetometer lane count and throughput target for peak arrival windows.
- Sallyport requirement, vehicle classes, and controlled perimeter assumptions.
- Ballistic rating requirements by area and continuity requirements for critical systems during outages.

## D) Provenance
Profiles wired for this subtype:
- DealShield tile profile: `civic_baseline_v1`.
- DealShield content profile: `civic_baseline_v1`.
- Scope items profile: `civic_baseline_structural_v1`.

What would change fastest:
- Security-zone, holding, and magnetometer throughput changes from agency/security review.
- Sallyport and ballistic requirements introduced or upgraded after concept design.
- Redundancy requirements for life-safety/security systems driven by owner policy or AHJ interpretation.
