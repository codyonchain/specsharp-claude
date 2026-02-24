# SpecSharp Decision Models (Canonical)

## NOI / cap-rate assets
Revenue → NOI → value via cap rate.
Primary metrics: NOI, DSCR, yield on cost, exit value.

## Operating business assets
Revenue → operating margin → cash flow.
Primary metrics: payback, cash-on-cash, margin durability.
No forced cap-rate terminal value.

## Throughput-driven healthcare/specialty
Units × throughput × reimbursement OR lease model (MOB).
Primary metrics: DSCR + unit economics + risk flags.

## Public/institutional feasibility
No revenue underwriting by default.
Primary outputs: cost, schedule risk, program metrics, budget fit.

## Mixed-use sum-of-parts
Underwrite each component with its native model and combine deterministically.

## Contract vs Behavior (Critical Rule)

**Building type defines the contract. Subtype defines the behavior.**

- Building type defines:
  - model contract (what must be output)
  - required metrics and decision framing
  - default template selection (if applicable)

- Subtype defines:
  - the actual drivers and parameters (rent/ADR/margins/throughput/etc.)
  - behavior selectors (profiles/clamps/multipliers)
  - acceptance tests and invariants

### Multi-model building types
Some “types” are buckets that contain multiple real-world business models (e.g., Specialty, Healthcare, Mixed Use).
For these, the subtype must explicitly declare its `model_class` and the engine must select templates accordingly.

Model classes:
- NOI / cap-rate
- Operating / payback
- Throughput healthcare/specialty
- Public feasibility
- Mixed sum-of-parts
