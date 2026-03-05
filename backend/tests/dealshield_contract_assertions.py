from __future__ import annotations

from typing import Any

_BANNED_COPY_TOKENS = (
    "(tile:",
    "metric_refs_used",
    "policy source:",
    "dealshield_policy_v1",
    "dealshield_canonical_policy_v1",
    "marginal",
    "not feasible",
)


def assert_decision_insurance_truth_parity(view_model: dict[str, Any]) -> None:
    assert isinstance(view_model, dict)
    assert "first_break_condition_holds" in view_model
    assert "break_risk_level" in view_model
    assert "break_risk_reason" in view_model

    di_provenance = view_model.get("decision_insurance_provenance")
    assert isinstance(di_provenance, dict)

    first_break_holds = view_model.get("first_break_condition_holds")
    assert first_break_holds is None or isinstance(first_break_holds, bool)
    first_break_holds_provenance = di_provenance.get("first_break_condition_holds")
    assert isinstance(first_break_holds_provenance, dict)
    assert first_break_holds_provenance.get("source") == "decision_insurance.first_break_condition"
    if first_break_holds is None:
        assert first_break_holds_provenance.get("status") == "unavailable"
    else:
        assert first_break_holds_provenance.get("status") == "available"
        assert first_break_holds_provenance.get("value") is first_break_holds

    break_risk_level = view_model.get("break_risk_level")
    break_risk_reason = view_model.get("break_risk_reason")
    assert break_risk_level is None or isinstance(break_risk_level, str)
    assert break_risk_reason is None or isinstance(break_risk_reason, str)

    break_risk_provenance = di_provenance.get("break_risk")
    assert isinstance(break_risk_provenance, dict)
    assert break_risk_provenance.get("source") == "decision_insurance.break_risk"
    if break_risk_level is None:
        assert break_risk_reason is None
        assert break_risk_provenance.get("status") == "unavailable"
        assert view_model.get("break_risk") is None
    else:
        assert break_risk_level.strip()
        assert isinstance(break_risk_reason, str) and break_risk_reason.strip()
        assert break_risk_provenance.get("status") == "available"
        assert break_risk_provenance.get("level") == break_risk_level
        assert break_risk_provenance.get("reason") == break_risk_reason
        assert view_model.get("break_risk") == {
            "level": break_risk_level,
            "reason": break_risk_reason,
        }

    rendered_copy = view_model.get("rendered_copy")
    assert isinstance(rendered_copy, dict)
    assert isinstance(rendered_copy.get("decision_status_summary"), str)
    assert rendered_copy["decision_status_summary"].strip()
    assert isinstance(rendered_copy.get("policy_basis_line"), str)
    assert rendered_copy["policy_basis_line"].strip()

    executive_copy = view_model.get("executive_rendered_copy")
    assert isinstance(executive_copy, dict)
    assert isinstance(executive_copy.get("how_to_interpret"), str)
    assert executive_copy["how_to_interpret"].strip()
    assert isinstance(executive_copy.get("target_yield_lens_label"), str)
    assert executive_copy["target_yield_lens_label"].strip()

    outcome_state = view_model.get("outcome_state")
    assert isinstance(outcome_state, str)
    assert outcome_state in {"GO_STRONG", "GO_THIN", "NOGO_DEBT_PASSES", "NOGO_DEBT_FAILS"}

    combined_copy = "\n".join(
        [
            str(rendered_copy.get("decision_status_summary", "")),
            str(rendered_copy.get("decision_status_detail", "")),
            str(rendered_copy.get("policy_basis_line", "")),
            str(executive_copy.get("how_to_interpret", "")),
            str(executive_copy.get("policy_basis_line", "")),
            str(executive_copy.get("target_yield_lens_label", "")),
        ]
    ).lower()
    for token in _BANNED_COPY_TOKENS:
        assert token not in combined_copy
