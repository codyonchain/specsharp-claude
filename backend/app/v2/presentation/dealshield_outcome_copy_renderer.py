from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Tuple

from app.v2.config.outcome_copy_packs import get_outcome_copy_pack
from app.v2.presentation.client_text_sanitizer import sanitize_client_text


class OutcomeState(str, Enum):
    GO_STRONG = "GO_STRONG"
    GO_THIN = "GO_THIN"
    NOGO_DEBT_PASSES = "NOGO_DEBT_PASSES"
    NOGO_DEBT_FAILS = "NOGO_DEBT_FAILS"


def _to_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
        return parsed if parsed == parsed else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = float(text.replace("$", "").replace(",", ""))
        except ValueError:
            return None
        return parsed if parsed == parsed else None
    return None


def _normalize_percentish(value: Any) -> Optional[float]:
    parsed = _to_number(value)
    if parsed is None:
        return None
    if abs(parsed) <= 1.5:
        return parsed * 100.0
    return parsed


def _normalize_status(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower().replace("_", " ")
    if not normalized:
        return None
    if "no-go" in normalized or "no go" in normalized:
        return "NO-GO"
    if "needs work" in normalized or "near break" in normalized:
        return "Needs Work"
    if "pending" in normalized or "review" in normalized:
        return "PENDING"
    if normalized == "go" or normalized.startswith("go "):
        return "GO"
    return None


def _normalize_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _extract_building_subtype(payload: Dict[str, Any]) -> Tuple[str, str]:
    info = payload.get("project_info") if isinstance(payload.get("project_info"), dict) else {}
    building_type = (
        payload.get("building_type")
        or payload.get("buildingType")
        or info.get("building_type")
        or info.get("buildingType")
        or payload.get("building")
        or ""
    )
    subtype = (
        payload.get("subtype")
        or payload.get("building_subtype")
        or payload.get("buildingSubtype")
        or info.get("subtype")
        or info.get("building_subtype")
        or info.get("buildingSubtype")
        or ""
    )
    return _normalize_key(building_type), _normalize_key(subtype)


def _extract_value_gap(payload: Dict[str, Any], view_model: Dict[str, Any]) -> Optional[float]:
    summary = view_model.get("decision_summary") if isinstance(view_model.get("decision_summary"), dict) else {}
    return (
        _to_number(view_model.get("value_gap"))
        or _to_number(summary.get("value_gap"))
        or _to_number(payload.get("value_gap"))
        or _to_number((payload.get("decision_summary") or {}).get("value_gap") if isinstance(payload.get("decision_summary"), dict) else None)
    )


def _extract_dscr_inputs(payload: Dict[str, Any], view_model: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    ownership = payload.get("ownership_analysis") if isinstance(payload.get("ownership_analysis"), dict) else {}
    debt = ownership.get("debt_metrics") if isinstance(ownership.get("debt_metrics"), dict) else {}

    dscr_value = _to_number(view_model.get("dscr"))
    target_dscr = _to_number(view_model.get("target_dscr"))

    if dscr_value is None:
        dscr_value = _to_number(debt.get("calculated_dscr"))
    if target_dscr is None:
        target_dscr = (
            _to_number(debt.get("target_dscr"))
            or _to_number(debt.get("dscr_target"))
            or _to_number(debt.get("required_dscr"))
            or _to_number(debt.get("minimum_dscr"))
        )

    return dscr_value, target_dscr


def _extract_flex_and_first_break(view_model: Dict[str, Any]) -> Tuple[Optional[float], str]:
    first_break = view_model.get("first_break_condition") if isinstance(view_model.get("first_break_condition"), dict) else {}
    scenario_label = first_break.get("scenario_label") or first_break.get("scenario_id") or ""
    return _normalize_percentish(view_model.get("flex_before_break_pct")), _normalize_key(scenario_label)


def _is_policy_pass(decision_status: Optional[str], value_gap: Optional[float]) -> bool:
    if value_gap is not None:
        return value_gap > 0
    if decision_status in {"GO", "Needs Work"}:
        return True
    if decision_status == "NO-GO":
        return False
    return False


def _is_debt_pass(dscr_value: Optional[float], target_dscr: Optional[float]) -> bool:
    if dscr_value is None or target_dscr is None:
        return False
    return dscr_value >= target_dscr


def select_outcome_state(inputs: Dict[str, Any]) -> OutcomeState:
    policy_pass = bool(inputs.get("policy_pass"))
    debt_pass = bool(inputs.get("debt_pass"))
    thin_cushion = bool(inputs.get("thin_cushion"))

    if policy_pass:
        return OutcomeState.GO_THIN if thin_cushion else OutcomeState.GO_STRONG
    return OutcomeState.NOGO_DEBT_PASSES if debt_pass else OutcomeState.NOGO_DEBT_FAILS


def _state_key(state: OutcomeState) -> str:
    return state.value if isinstance(state, OutcomeState) else str(state).strip().upper()


def get_pack_drivers(pack: Dict[str, Any], view: str, state: OutcomeState) -> list[str]:
    fallback = pack.get("drivers_primary")
    fallback_list = [str(item).strip() for item in fallback if str(item).strip()] if isinstance(fallback, list) else []

    drivers = pack.get("drivers")
    if isinstance(drivers, dict):
        view_drivers = drivers.get(_normalize_key(view))
        if isinstance(view_drivers, dict):
            state_drivers = view_drivers.get(_state_key(state))
            if isinstance(state_drivers, list):
                resolved = [str(item).strip() for item in state_drivers if str(item).strip()]
                if resolved:
                    return resolved

    if fallback_list:
        return fallback_list
    return ["cost basis discipline", "NOI durability"]


def get_pack_template_override(pack: Dict[str, Any], view: str, state: OutcomeState) -> Optional[Dict[str, str]]:
    templates = pack.get("templates")
    if not isinstance(templates, dict):
        return None
    view_templates = templates.get(_normalize_key(view))
    if not isinstance(view_templates, dict):
        return None
    template = view_templates.get(_state_key(state))
    if not isinstance(template, dict):
        return None
    return template


def _join_drivers(drivers: list[str]) -> str:
    formatted = [item for item in drivers if item]
    if not formatted:
        return "cost basis and NOI durability"
    if len(formatted) == 1:
        return formatted[0]
    return f"{formatted[0]} and {formatted[1]}"


def render_dealshield_copy(state: OutcomeState, pack: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, str]:
    drivers = _join_drivers(get_pack_drivers(pack=pack, view="dealshield", state=state))
    first_break_label = context.get("first_break_label") or "modeled stress"

    if state == OutcomeState.GO_STRONG:
        summary = "Base case clears the policy threshold with durable cushion."
        detail = f"Primary monitoring drivers: {drivers}. First break remains outside near-base stress."
    elif state == OutcomeState.GO_THIN:
        summary = "Base case clears the policy threshold, but cushion is thin."
        detail = f"Primary monitoring drivers: {drivers}. First break appears in {first_break_label}; validate assumptions before commit."
    elif state == OutcomeState.NOGO_DEBT_PASSES:
        summary = "Base case breaks the policy threshold (value gap non-positive), even with debt coverage clearing target."
        detail = f"Primary repair drivers: {drivers}. Use first-break and flex outputs to isolate the forcing assumption."
    else:
        summary = "Base case breaks the policy threshold and debt coverage is below target."
        detail = f"Primary repair drivers: {drivers}. Rework basis/NOI and debt terms before rerun."

    override = get_pack_template_override(pack=pack, view="dealshield", state=state)
    if isinstance(override, dict):
        override_summary = override.get("summary")
        override_detail = override.get("detail")
        if isinstance(override_summary, str) and override_summary.strip():
            summary = override_summary.strip()
        if isinstance(override_detail, str) and override_detail.strip():
            detail = override_detail.strip()

    return sanitize_client_text({
        "decision_status_summary": summary,
        "decision_status_detail": detail,
        "policy_basis_line": "Policy basis: DealShield canonical policy.",
    })


def render_execview_copy(state: OutcomeState, pack: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, str]:
    drivers = _join_drivers(get_pack_drivers(pack=pack, view="executive", state=state))
    dscr_value = context.get("dscr_value")
    dscr_target = context.get("target_dscr")

    dscr_text = "—" if dscr_value is None else f"{float(dscr_value):.2f}x"
    target_text = "—" if dscr_target is None else f"{float(dscr_target):.2f}x"

    if state == OutcomeState.GO_STRONG:
        how_to_interpret = (
            f"GO: policy threshold clears with healthy cushion. Keep diligence focused on {drivers}."
        )
        target_yield_lens_label = "Target Yield: Met (Cushion)"
    elif state == OutcomeState.GO_THIN:
        how_to_interpret = (
            f"GO (thin cushion): policy threshold clears, but first-break proximity is tight. Focus diligence on {drivers}."
        )
        target_yield_lens_label = "Target Yield: Thin Cushion"
    elif state == OutcomeState.NOGO_DEBT_PASSES:
        how_to_interpret = (
            f"NO-GO: policy breaks on value support while Debt Lens DSCR clears ({dscr_text} vs {target_text}). "
            f"Focus remediation on {drivers}."
        )
        target_yield_lens_label = "Target Yield: Not Met"
    else:
        how_to_interpret = (
            f"NO-GO: policy breaks and Debt Lens DSCR is below target ({dscr_text} vs {target_text}). "
            f"Rework {drivers} and debt sizing before rerun."
        )
        target_yield_lens_label = "Target Yield: Not Met"

    override = get_pack_template_override(pack=pack, view="executive", state=state)
    if isinstance(override, dict):
        override_how_to_interpret = override.get("how_to_interpret")
        override_target_yield_lens_label = override.get("target_yield_lens_label")
        if isinstance(override_how_to_interpret, str) and override_how_to_interpret.strip():
            how_to_interpret = override_how_to_interpret.strip()
        if isinstance(override_target_yield_lens_label, str) and override_target_yield_lens_label.strip():
            target_yield_lens_label = override_target_yield_lens_label.strip()

    return sanitize_client_text({
        "how_to_interpret": how_to_interpret,
        "policy_basis_line": "Policy basis: DealShield canonical policy.",
        "target_yield_lens_label": target_yield_lens_label,
    })


def build_outcome_copy_bundle(payload: Dict[str, Any], view_model: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    safe_payload = payload if isinstance(payload, dict) else {}
    safe_view_model = view_model if isinstance(view_model, dict) else {}
    payload_summary = safe_payload.get("decision_summary") if isinstance(safe_payload.get("decision_summary"), dict) else {}

    building_type, subtype = _extract_building_subtype(safe_payload)
    pack = get_outcome_copy_pack(building_type, subtype)

    decision_status = _normalize_status(
        safe_view_model.get("decision_status")
        or safe_payload.get("decision_status")
        or payload_summary.get("decision_status")
    )
    value_gap = _extract_value_gap(safe_payload, safe_view_model)
    dscr_value, target_dscr = _extract_dscr_inputs(safe_payload, safe_view_model)
    flex_pct, first_break_label = _extract_flex_and_first_break(safe_view_model)

    thin_cushion = bool(
        (flex_pct is not None and flex_pct < 10.0)
        or first_break_label == "conservative"
        or decision_status == "Needs Work"
    )
    policy_pass = _is_policy_pass(decision_status=decision_status, value_gap=value_gap)
    debt_pass = _is_debt_pass(dscr_value=dscr_value, target_dscr=target_dscr)

    state = select_outcome_state(
        {
            "policy_pass": policy_pass,
            "debt_pass": debt_pass,
            "thin_cushion": thin_cushion,
        }
    )

    context = {
        "building_type": building_type,
        "subtype": subtype,
        "decision_status": decision_status,
        "value_gap": value_gap,
        "dscr_value": dscr_value,
        "target_dscr": target_dscr,
        "flex_before_break_pct": flex_pct,
        "first_break_label": first_break_label,
    }

    return {
        "outcome_state": state.value,
        "dealshield": render_dealshield_copy(state=state, pack=pack, context=context),
        "executive": render_execview_copy(state=state, pack=pack, context=context),
    }
