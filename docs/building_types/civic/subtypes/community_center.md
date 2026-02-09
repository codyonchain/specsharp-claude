# Subtype: Community Center (Civic)

## A) Decision / KPIs (Feasibility)
Decision intent: determine GO / RESCOPE / REPRICE / WALK from deterministic feasibility outputs.

Primary outputs:
- Cost feasibility: total project cost and cost/SF from subtype trade mix + soft costs.
- Schedule risk: timeline confidence driven by MEP coordination, permitting, and long-lead scope.
- Compliance risk: life-safety, accessibility, food service, and assembly occupancy/code exposure.
- Program fit: whether planned spaces (gym, community rooms, kitchen, fitness) match target use.

## B) Construction (Top Scope Drivers)
- MEP intensity: gym ventilation loads, kitchen exhaust/makeup air, and electrical service for multipurpose use.
- Security: access control, after-hours zoning, and camera/life-safety integration.
- Envelope: durable/high-traffic envelope and moisture control for high occupant turnover.
- Sitework: drop-off/parking flow, ADA routes, outdoor pavilion interfaces, and utility tie-ins.

Special features status:
- Modeled (config adders): `gymnasium`, `kitchen`, `multipurpose_room`, `fitness_center`, `outdoor_pavilion`.
- Not modeled explicitly: natatorium/pool systems, theater/acoustics package, structured parking, major off-site utility relocation.

## C) Assumptions / Trust
Not modeled (must be treated as external scope or overrides):
- Land acquisition, financing fees beyond configured soft-cost rates, and owner FF&E programs.
- Deep geotech/foundation anomalies, environmental remediation, and major off-site civil upgrades.
- Public operating subsidies/revenue policy and staffing model beyond baseline feasibility math.

Must confirm before investment committee:
- Final program mix (SF by gym, kitchen, multipurpose, fitness, admin, support).
- AHJ requirements for occupancy classification, egress, fire protection, and food service permits.
- Utility capacity and lead times for kitchen/mechanical/electrical loads.
- Security standard (public-only vs mixed secure zones).

## D) Provenance
Profiles wired for this subtype:
- DealShield tile profile: `civic_baseline_v1`.
- DealShield content profile: `civic_baseline_v1`.
- Scope items profile: `civic_baseline_structural_v1`.

What would change fastest:
- Program mix shifts (gym/kitchen/fitness share of total SF).
- Site and utility constraints discovered in DD.
- Security/compliance scope changes from AHJ or owner policy.
