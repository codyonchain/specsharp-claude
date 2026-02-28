from __future__ import annotations

from typing import Any


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
