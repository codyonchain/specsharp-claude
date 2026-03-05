from __future__ import annotations

from copy import deepcopy

import pytest

from app.v2.config import outcome_copy_packs
from app.v2.presentation.client_text_sanitizer import sanitize_client_text
from app.v2.presentation.dealshield_outcome_copy_renderer import build_outcome_copy_bundle


BANNED_TOKENS = [
    "(tile:",
    "metric_refs_used",
    "policy source:",
    "dealshield_policy_v1",
    "dealshield_canonical_policy_v1",
    "marginal",
    "not feasible",
]


@pytest.mark.parametrize(
    "name,value_gap,dscr,target_dscr,flex_pct,first_break,expected_state",
    [
        ("GO_STRONG", 1_000_000.0, 1.35, 1.20, 12.5, "ugly", "GO_STRONG"),
        ("GO_THIN", 250_000.0, 1.28, 1.20, 4.5, "conservative", "GO_THIN"),
        ("NOGO_DEBT_PASSES", -100_000.0, 1.30, 1.20, 0.0, "base", "NOGO_DEBT_PASSES"),
        ("NOGO_DEBT_FAILS", -250_000.0, 1.05, 1.20, 0.0, "base", "NOGO_DEBT_FAILS"),
    ],
)
def test_outcome_copy_renderer_selects_all_four_states_and_blocks_banned_tokens(
    name: str,
    value_gap: float,
    dscr: float,
    target_dscr: float,
    flex_pct: float,
    first_break: str,
    expected_state: str,
):
    payload = {
        "building_type": "multifamily",
        "subtype": "market_rate_apartments",
        "ownership_analysis": {
            "debt_metrics": {
                "calculated_dscr": dscr,
                "target_dscr": target_dscr,
            }
        },
    }
    view_model = {
        "decision_status": "GO" if value_gap > 0 else "NO-GO",
        "decision_reason_code": "base_value_gap_positive" if value_gap > 0 else "base_case_break_condition",
        "decision_summary": {"value_gap": value_gap},
        "value_gap": value_gap,
        "flex_before_break_pct": flex_pct,
        "first_break_condition": {
            "scenario_label": first_break,
            "scenario_id": first_break,
        },
    }

    bundle = build_outcome_copy_bundle(payload=payload, view_model=view_model)

    assert bundle["outcome_state"] == expected_state, name

    dealshield_copy = bundle["dealshield"]
    executive_copy = bundle["executive"]

    assert isinstance(dealshield_copy.get("decision_status_summary"), str)
    assert dealshield_copy["decision_status_summary"].strip()
    assert isinstance(executive_copy.get("how_to_interpret"), str)
    assert executive_copy["how_to_interpret"].strip()
    assert isinstance(executive_copy.get("target_yield_lens_label"), str)
    assert executive_copy["target_yield_lens_label"].strip()

    combined = "\n".join(
        [
            dealshield_copy.get("decision_status_summary", ""),
            dealshield_copy.get("decision_status_detail", ""),
            dealshield_copy.get("policy_basis_line", ""),
            executive_copy.get("how_to_interpret", ""),
            executive_copy.get("policy_basis_line", ""),
            executive_copy.get("target_yield_lens_label", ""),
        ]
    ).lower()

    for token in BANNED_TOKENS:
        assert token not in combined


def test_outcome_copy_renderer_uses_subtype_pack_phrase_for_cafe():
    payload = {
        "building_type": "restaurant",
        "subtype": "cafe",
        "ownership_analysis": {
            "debt_metrics": {
                "calculated_dscr": 1.24,
                "target_dscr": 1.20,
            }
        },
    }
    view_model = {
        "decision_status": "NO-GO",
        "decision_reason_code": "base_case_break_condition",
        "decision_summary": {"value_gap": -50000.0},
        "value_gap": -50000.0,
        "flex_before_break_pct": 0.0,
        "first_break_condition": {"scenario_label": "base", "scenario_id": "base"},
    }

    bundle = build_outcome_copy_bundle(payload=payload, view_model=view_model)
    detail = bundle["dealshield"]["decision_status_detail"].lower()

    assert "ticket/throughput consistency" in detail


def test_outcome_copy_renderer_uses_multifamily_market_rate_template_override_for_go_thin():
    payload = {
        "building_type": "multifamily",
        "subtype": "market_rate_apartments",
        "ownership_analysis": {
            "debt_metrics": {
                "calculated_dscr": 1.30,
                "target_dscr": 1.20,
            }
        },
    }
    view_model = {
        "decision_status": "GO",
        "decision_reason_code": "base_value_gap_positive",
        "decision_summary": {"value_gap": 150000.0},
        "value_gap": 150000.0,
        "flex_before_break_pct": 4.2,
        "first_break_condition": {"scenario_label": "conservative", "scenario_id": "conservative"},
    }

    bundle = build_outcome_copy_bundle(payload=payload, view_model=view_model)

    assert bundle["outcome_state"] == "GO_THIN"
    assert bundle["dealshield"]["decision_status_summary"] == "Base case clears the policy threshold, but cushion is thin."
    assert bundle["dealshield"]["decision_status_detail"] == (
        "Validate cost basis and carry discipline under lease-up timing, and rent/concession elasticity versus expense growth before commitment."
    )
    assert bundle["executive"]["how_to_interpret"] == (
        "GO (thin cushion): policy clears, but break proximity is tight. Pressure-test lease-up carry and concession elasticity versus expense growth."
    )
    assert bundle["executive"]["target_yield_lens_label"] == "Target Yield: Thin Cushion"


def test_outcome_copy_renderer_falls_back_to_global_templates_when_no_subtype_override():
    payload = {
        "building_type": "industrial",
        "subtype": "warehouse",
        "ownership_analysis": {
            "debt_metrics": {
                "calculated_dscr": 1.04,
                "target_dscr": 1.20,
            }
        },
    }
    view_model = {
        "decision_status": "NO-GO",
        "decision_reason_code": "base_case_break_condition",
        "decision_summary": {"value_gap": -100000.0},
        "value_gap": -100000.0,
        "flex_before_break_pct": 0.0,
        "first_break_condition": {"scenario_label": "base", "scenario_id": "base"},
    }

    bundle = build_outcome_copy_bundle(payload=payload, view_model=view_model)

    assert bundle["outcome_state"] == "NOGO_DEBT_FAILS"
    assert bundle["dealshield"]["decision_status_summary"] == (
        "Base case breaks the policy threshold and debt coverage is below target."
    )
    assert bundle["dealshield"]["decision_status_detail"] == (
        "Primary repair drivers: sitework/civil and shell basis and lease-up absorption shape. Rework basis/NOI and debt terms before rerun."
    )
    assert bundle["executive"]["target_yield_lens_label"] == "Target Yield: Not Met"


def test_outcome_copy_renderer_honors_runtime_temporary_pack_override(monkeypatch: pytest.MonkeyPatch):
    key = ("multifamily", "market_rate_apartments")
    original_pack = deepcopy(outcome_copy_packs.SUBTYPE_PACKS.get(key, {}))
    override_pack = deepcopy(original_pack)
    override_pack.setdefault("templates", {}).setdefault("dealshield", {})["GO_THIN"] = {
        "summary": "Runtime override summary.",
        "detail": "Runtime override detail.",
    }
    override_pack.setdefault("templates", {}).setdefault("executive", {})["GO_THIN"] = {
        "how_to_interpret": "Runtime override executive narrative.",
        "target_yield_lens_label": "Target Yield: Thin Cushion",
    }
    monkeypatch.setitem(outcome_copy_packs.SUBTYPE_PACKS, key, override_pack)

    payload = {
        "building_type": "multifamily",
        "subtype": "market_rate_apartments",
        "ownership_analysis": {
            "debt_metrics": {
                "calculated_dscr": 1.31,
                "target_dscr": 1.20,
            }
        },
    }
    view_model = {
        "decision_status": "GO",
        "decision_reason_code": "base_value_gap_positive",
        "decision_summary": {"value_gap": 120000.0},
        "value_gap": 120000.0,
        "flex_before_break_pct": 3.0,
        "first_break_condition": {"scenario_label": "conservative", "scenario_id": "conservative"},
    }

    bundle = build_outcome_copy_bundle(payload=payload, view_model=view_model)

    assert bundle["outcome_state"] == "GO_THIN"
    assert bundle["dealshield"]["decision_status_summary"] == "Runtime override summary."
    assert bundle["dealshield"]["decision_status_detail"] == "Runtime override detail."
    assert bundle["executive"]["how_to_interpret"] == "Runtime override executive narrative."
    assert bundle["executive"]["target_yield_lens_label"] == "Target Yield: Thin Cushion"


def test_client_text_sanitizer_removes_debug_tokens_without_corrupting_content():
    raw = {
        "line": "Policy source: dealshield_policy_v1 (dealshield_canonical_policy_v1)",
        "question": "Lease-up assumptions (tile: revenue_minus_10)",
        "metric_refs_used": ["totals.total_project_cost"],
        "status": "Marginal",
        "secondary": "Not Feasible",
        "safe": "Policy basis: DealShield canonical policy",
    }

    sanitized = sanitize_client_text(raw)

    assert "metric_refs_used" not in sanitized
    assert sanitized["safe"] == "Policy basis: DealShield canonical policy"
    assert "policy source" not in sanitized.get("line", "").lower()
    assert "(tile:" not in sanitized.get("question", "").lower()
    assert sanitized.get("status", "").lower() == "thin cushion"
    assert sanitized.get("secondary", "").lower() == "target yield: not met"
