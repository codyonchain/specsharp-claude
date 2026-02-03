SpecSharp
=========

SpecSharp is a construction-backed underwriting engine for early-stage real estate feasibility. It compresses weeks of predevelopment work—cost estimation, revenue modeling, scenario analysis, and executive reporting—into minutes, using deterministic construction logic and market-aware assumptions.

SpecSharp is designed for developers, owners, and investment teams who need defensible answers before drawings exist.

What SpecSharp Does
-------------------

SpecSharp replaces the fragmented early feasibility stack (estimators, cost consultants, spreadsheets, test fits, and ad-hoc underwriting models) with a single, integrated workflow.

Core Views
----------

### ConstructionView

- Trade-level quantities and costs
- Deterministic scope generation
- Metro- and state-adjusted construction pricing
- Transparent rollups with no duplicate or hidden multipliers

### ExecutiveView

- Capex, financing, and return metrics (NOI, DSCR, IRR, equity)
- Facility and operational metrics tied to building type
- Prescriptive recommendations and risk context
- Designed for C-suite, IC, and lender review

### Scenarios & Exports

- Scenario comparison without re-running estimates
- Executive-ready PDF exports
- Consistent assumptions across all views

Regional & Location Logic
-------------------------

SpecSharp requires City, ST as input for all analyses.

Location is resolved once and applied consistently across the system:

- Major metros use explicit metro overrides
- All other locations fall back to state baselines
- Regional adjustments are applied exactly once in the core engine
- The resolved location, source, and multiplier are always visible for transparency

This avoids silent defaults and ensures numbers are defensible in executive and lender contexts.

Current Architecture (High Level)
---------------------------------

1. Natural-language project description
2. Deterministic scope + quantity generation
3. Regionalized construction cost calculation
4. Underwriting + scenario modeling
5. Executive reporting and export

SpecSharp deliberately separates construction logic from presentation, so all views consume the same underlying calculations.

Configuration Source of Truth
------------------------------

SpecSharp uses a single authoritative configuration source:

- `backend/app/v2/config/master_config.py`

Any taxonomy or subtype changes must be reflected here and kept in sync with:

- `shared/building_types.json`
- `backend/shared/building_types.json`

Running Locally
---------------

Exact commands may change as the project evolves.

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Environment variables are required for certain integrations; see `.env.example`.

Project Status
--------------

SpecSharp is under active development.

**Recently completed:**

- Unified regional cost system (metro + state)
- ConstructionView normalization
- ExecutiveView and PDF export overhaul
- Scenario workflow stabilization

**In progress:**

- Separation of construction cost vs market revenue factors
- Site and onboarding polish
- Expanded metro coverage

Philosophy
----------

SpecSharp prioritizes:

- Determinism over black-box AI
- Explainability over false precision
- Early-stage decision accuracy over final-design perfection

It is built to answer one question exceptionally well:

> “Should we pursue this deal?”
