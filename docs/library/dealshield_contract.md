# DealShield Contract
Decision Insurance One-Pager (Front Door)

**Contract ID:** DealShield Contract  
**Version:** v1.0  
**Owner lane:** Type Owner + Core Integrator  
**Status:** Launch-critical  
**Last updated:** 2026-02-04

## Purpose
DealShield is the portable, room-ready artifact that converts SpecSharp from:
> “I’ll use it privately” → “I can cite it.”

DealShield is not “analysis output.” It is **Decision Insurance**:
- conservative by default
- explicit about assumptions
- honest about where it’s likely wrong
- defensible in a skeptical room
- reproducible/auditable (human readable, deterministic)

DealShield is the **front door**. ExecutiveView + ConstructionView are appendix/proof.

---

## Non-Goals
- DealShield does **not** replace ExecutiveView or ConstructionView.
- DealShield must **not invent numbers**. It only summarizes and composes values already present in deterministic outputs (Exec/Construction) + deterministic scenario tiles (when available).
- DealShield is not a sales deck or hype memo.

---

## Determinism Rules
**MUST:** Same inputs → same outputs, including DealShield.  
**MUST:** DealShield fields map to deterministic sources:
- ExecutiveView / ownership analysis outputs
- ConstructionView / trade breakdown outputs
- Deterministic scenario tiles (e.g., cost ±10%, revenue ±10%) when used

**MUST NOT:** “trained on data” claims unless substantiated.  
**MUST:** Every flagged risk/assumption/driver must map to a known driver:
- a known trade bucket, or
- a known config key/feature assumption, or
- a named scope/quantity driver, or
- an explicit scenario tile reference.

---

## Output Format
DealShield is **one page by default**.
- May spill to 2 pages only if absolutely necessary.
- Must be readable in **60–90 seconds**.

Tone:
- conservative, precise, operator voice
- no hype language
- no “accurate” claims
- must include humility clauses:
  - “Most sensitive to…”
  - “High-variance items…”
  - “If wrong, most likely here…”

---

## Section Order (Template)

### 0) Header (Required)
**MUST include:**
- Project name
- Location
- Canonical building type + subtype
- Square footage
- Project class (ground_up/addition/renovation/TI if supported)
- Run timestamp
- Version string (engine/config version)
- Posture: Conservative / Base / Aggressive (**default Conservative**)
- Confidence: Low / Medium / High (never optimistic by default)

**MUST:** Header values must match ExecView + ConstructionView.

---

### 1) Verdict Strip (Downside-First) — Required
Compact box containing:
- **DealShield Verdict:** Green / Yellow / Red
- **Primary reason (1 line)**: must name a driver (not a vibe)
- **Top 2 risks** (bullets, ≤2 lines each)
- **If you only remember one thing:** one sentence

Rules:
- **No hype.**
- If confidence ≠ High, **must include at least one explicit uncertainty statement**.
- Verdict must be deterministic (see “Verdict Logic”).

---

### 2) Downside Summary Table — Required
A 3-row table:

**Rows:** Base / Conservative / Ugly  
**Columns (max 5):**
- Total Cost ($)
- Cost/SF
- Contingency posture (short)
- Schedule risk note (short)
- Optional: 1–2 underwriting impacts (DSCR / yield / NOI sensitivity) if available

Rules:
- **Base** = deterministic baseline.
- **Conservative/Ugly** MUST be derived from deterministic drivers:
  - scenario tiles when present (preferred)
  - or deterministic driver adjustments explicitly documented in Audit Trail
- Ugly is “what breaks first,” not fear-mongering.
- Table must cite what drove Conservative/Ugly (e.g., “Cost +10% tile”, “Revenue −10% tile”).

---

### 3) Key Assumptions (Ranked by Sensitivity) — Required
List **5–7 max**, ranked by impact.

Each item MUST include:
- Assumption statement
- Why it matters (1 line)
- What would change it (1 line)
- Sensitivity tag: High / Medium / Low
- Provenance pointer (trade/config/tile)

Rules:
- Must be real assumptions implied by the run (not boilerplate).
- Assumptions must be consistent with subtype specs.

---

### 4) Most Likely Wrong Here (Honesty Block) — Required
Top 3 bullets:
- #1 likely wrong area + why + what to verify
- #2 likely wrong area + why + what to verify
- #3 likely wrong area + why + what to verify

Rules:
- Must map to actual volatility drivers (sitework, structure, MEP, finishes, phasing, FF&E, revenue/occupancy/rent).
- No vague language.

---

### 5) Questions to Ask Tomorrow (Action Block) — Required
8–12 total questions, grouped:
- A) GC / Estimator (5–7)
- B) Owner / Design / Program (3–5)

Rules:
- Not generic: must be generated from Assumptions + “Most Likely Wrong” + deltas vs baseline.

---

### 6) If Questioned, Say This (Political Cover Scripts) — Required
3 scripts, 2–3 sentences each:
1) Boss script (what it is/isn’t)
2) GC pushback script (clarifications needed)
3) IC script (downside framing + conservatism + auditability)

Rules:
- Must explicitly state SpecSharp is a **risk lens**, not a diligence replacement.
- Must highlight transparency + determinism.

---

### 7) Audit Trail (Human-Readable Provenance) — Required
A) Inputs used (mini table)
- Type/subtype
- SF, location, project class
- Posture + confidence
- Major toggles (finish level, special features, clamp posture, etc.)
- Run ID / input hash

B) Cost lineage (tight chain)
- base cost source
- multipliers applied
- adders (equipment/FF&E)
- totals (construction, soft, total investment)

C) Top 5 cost drivers (ranked)
For each:
- driver name (Sitework/Structure/MEP/Envelope/Interiors etc.)
- directionality vs baseline (↑/↓)
- why (1 line, deterministic)
- what would change it (1 line)

D) Reproducibility line
- “Reproduce this run with input hash: XXXXX”
- “Same inputs → same outputs”

Rules:
- No “model vibes” explanations.
- Every driver must map to deterministic sources.

---

### 8) Appendix Pointers — Required (tiny footer)
- “For details: ExecutiveView page X, ConstructionView page Y”
(or links/anchors in-app)

---

## Verdict Logic (v1)
DealShield verdict must be deterministic and conservative by default.

**MUST:** Use thresholds already present in type profiles / underwriting outputs when available.  
**SHOULD:** Prefer “downside-first” classification.

Example v1 rule (illustrative; actual thresholds owned by type owners):
- **Red:** fails any hard hurdle (DSCR below minimum OR yield below hurdle by material gap) OR confidence Low + multiple high-variance drivers
- **Yellow:** near hurdles / Needs Work recommendation
- **Green:** clears hurdles with margin + confidence Medium/High

Verdict must cite the primary driver and one “what breaks first” line.

---

## Acceptance Gates (Hard)
### Gate A — Headline integrity (FAIL)
DealShield header fields must match ExecView + ConstructionView:
- SF, subtype, location, posture
No mismatches.

### Gate B — Derived numbers integrity (FAIL)
Downside table must reconcile:
- Base row equals baseline deterministic output
- Conservative/Ugly derived from documented deterministic sources
No freehand numbers.

### Gate C — Traceability (FAIL)
Each item in:
- Key assumptions
- Most likely wrong
- Top drivers
...must map to a deterministic driver source (trade/config/tile).

### Gate D — One-page readability (FAIL/WARN)
FAIL if unreadable / too dense.  
WARN if spills to 2 pages (allowed only if necessary).

---

## Subtype Responsibilities (Implication)
Because DealShield is the front door, each subtype MUST eventually own:
- sensitivity tiles that reflect its actual economics (cost/revenue knobs)
- ranked assumptions that are subtype-specific (not generic)
- question bank that maps to its volatility drivers

Subtype work is not “copy polish.” It is trust engineering.

---

## Implementation Notes (Launch-Safe)
DealShield should be built as:
- Third in-app view (primary)
- One-click PDF export from same data model (secondary)
Both must render from the same DealShieldModel to avoid drift.
