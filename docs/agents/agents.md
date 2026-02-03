# SpecSharp Agents.md (Non-Negotiable Rules)

## Mission
SpecSharp is deterministic underwriting + construction logic. No AI guessing in calculations.

## Operating Rules
1) Determinism first: no randomness, no hidden defaults.
2) Explicit overrides always win (0% office, 0 docks, 0 mezz, etc.).
3) Traceability required: any override/clamp/assumption must add a calculation_trace entry.
4) Surgical changes only. Minimal diff. No speculative refactors.
5) Scope boundaries are hard: only change allowed files listed in Build.md.
6) Type defines contract; subtype defines behavior. Multi-model types require subtype-declared model_class (see decision_models.md).

## Output Requirements (every agent response)
- Summary (≤5 bullets)
- Risks / blast radius (what other subtypes could be affected)
- Commands run (if any)
- git status
- git diff --stat
- git diff

## Never do
- Don’t hit production domains unless Build.md explicitly enables it.
- Don’t expand scope beyond listed files.
- Don’t “update goldens” unless Build.md explicitly authorizes rebaseline.
