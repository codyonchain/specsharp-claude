from __future__ import annotations

from datetime import datetime
import html as html_module
from typing import Any, Dict, List

from app.utils.formatting import format_currency
from app.v2.presentation.client_text_sanitizer import sanitize_client_text


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _sanitize_text(value: Any) -> str:
    if value is None:
        return ""
    sanitized = sanitize_client_text(str(value))
    if isinstance(sanitized, str):
        return sanitized.strip()
    return str(sanitized).strip()


def _escape(value: Any) -> str:
    return html_module.escape(_sanitize_text(value))


def _format_export_primary_control_label(label: Any, profile_id: Any) -> str:
    cleaned_label = _sanitize_text(label)
    cleaned_profile_id = _sanitize_text(profile_id)
    if (
        cleaned_profile_id.startswith("multifamily_market_rate_apartments")
        and cleaned_label.lower() == "structural base carry proxy +5%"
    ):
        return "Cost Basis Drift + Carry Risk"
    return cleaned_label


def _to_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        parsed = float(value)
        return parsed if parsed == parsed else None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = float(text.replace("$", "").replace(",", "").replace("%", ""))
        except ValueError:
            return None
        return parsed if parsed == parsed else None
    return None


def _normalize_percentish(value: Any) -> float | None:
    parsed = _to_number(value)
    if parsed is None:
        return None
    if abs(parsed) <= 1.5:
        return parsed * 100.0
    return parsed


def _format_money(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    return format_currency(parsed)


def _format_number(value: Any, digits: int = 0) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    if digits == 0 and float(parsed).is_integer():
        return f"{int(parsed):,d}"
    return f"{parsed:,.{digits}f}"


def _format_ratio(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    return f"{parsed:,.2f}x"


def _format_percent(value: Any, digits: int = 1) -> str:
    parsed = _normalize_percentish(value)
    if parsed is None:
        return "—"
    return f"{parsed:,.{digits}f}%"


def _format_percent_fixed_two(value: Any) -> str:
    return _format_percent(value, digits=2)


def _format_months(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    rounded = int(round(parsed))
    return f"{rounded} months"


def _format_basis_points(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    rounded = int(round(parsed))
    prefix = "+" if rounded > 0 else ""
    return f"{prefix}{rounded:,d} bps"


def _format_sqft(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    return f"{int(round(parsed)):,d} SF"


def _format_money_per_sf(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    return f"{format_currency(parsed)}/SF"


def _format_financing_summary_value(item: Dict[str, Any]) -> str:
    format_kind = _sanitize_text(item.get("format"))
    decimals_value = _to_number(item.get("decimals"))
    decimals = int(decimals_value) if decimals_value is not None else None
    value = item.get("value")

    if format_kind == "currency":
        return _format_money(value)
    if format_kind == "percentage":
        return _format_percent(value, digits=decimals if decimals is not None else 1)
    if format_kind == "multiple":
        parsed = _to_number(value)
        if parsed is None:
            return "—"
        digits = decimals if decimals is not None else 2
        return f"{parsed:,.{digits}f}×"
    if format_kind == "basis_points":
        return _format_basis_points(value)
    return _format_number(value, digits=decimals if decimals is not None else 0)


def _clean_packet_financing_disclosures(disclosures: Any, *, has_financing_summary: bool) -> List[str]:
    cleaned: List[str] = []
    for item in _as_list(disclosures):
        text = _sanitize_text(item)
        if not text:
            continue
        if has_financing_summary and text == "Not modeled: financing assumptions missing":
            continue
        if text not in cleaned:
            cleaned.append(text)
    return cleaned


def _format_compact_currency(value: float) -> str:
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= 1_000_000_000:
        return f"{sign}${magnitude / 1_000_000_000:,.1f}B"
    if magnitude >= 1_000_000:
        return f"{sign}${magnitude / 1_000_000:,.1f}M"
    if magnitude >= 1_000:
        return f"{sign}${magnitude / 1_000:,.1f}K"
    return f"{sign}${magnitude:,.0f}"


def _format_readable_insurance_value(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return _sanitize_text(value) or "—"
    if abs(parsed) >= 1_000:
        return _format_compact_currency(parsed)
    if abs(parsed) >= 100:
        return _format_number(parsed, 0)
    if abs(parsed) >= 10:
        return _format_number(parsed, 1)
    return _format_number(parsed, 2)


def _format_metric(label: str, value: str, detail: str = "") -> str:
    detail_html = (
        f"<div class=\"metric-detail\">{html_module.escape(detail)}</div>"
        if detail.strip()
        else ""
    )
    return (
        "<div class=\"metric-card\">"
        f"<div class=\"metric-label\">{html_module.escape(label)}</div>"
        f"<div class=\"metric-value\">{html_module.escape(value)}</div>"
        f"{detail_html}"
        "</div>"
    )


def _titleize_label(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    return value.strip().replace("_", " ").replace("-", " ").title()


def _humanize_question_bank_label(value: Any) -> str:
    raw = _sanitize_text(value)
    if not raw:
        return ""

    working = raw
    if ":" in working:
        _, _, tail = working.partition(":")
        if tail.strip():
            working = tail.strip()

    tokens = [token for token in working.replace("_", " ").replace("-", " ").split() if token]
    if not tokens:
        return ""

    while tokens and tokens[0].lower() in {"qb", "question", "questions"}:
        tokens.pop(0)
    while tokens and tokens[-1].isdigit():
        tokens.pop()

    if not tokens:
        return ""

    replacements = {
        "rev": "Revenue",
        "revenue": "Revenue",
        "cost": "Cost",
        "scope": "Scope",
        "ops": "Operations",
        "op": "Operations",
        "operator": "Operator",
        "noi": "NOI",
        "dscr": "DSCR",
        "adr": "ADR",
        "ffe": "FF&E",
        "fnb": "F&B",
        "mep": "MEP",
    }
    humanized_tokens = [replacements.get(token.lower(), token.title()) for token in tokens]
    humanized = " ".join(humanized_tokens).strip()

    if not humanized or any(char.isdigit() for char in humanized):
        return ""
    return humanized


def _resolve_question_bank_label(item: Dict[str, Any]) -> str:
    preferred_keys = (
        "title",
        "heading",
        "label",
        "group_label",
        "category",
        "driver_tile_label",
    )
    for key in preferred_keys:
        candidate = _sanitize_text(item.get(key))
        if not candidate:
            continue
        if any(marker in candidate.lower() for marker in ("qb_", "qb-", "driver_tile_id")):
            continue
        return candidate

    fallback = _humanize_question_bank_label(item.get("id"))
    if fallback:
        return fallback

    fallback = _humanize_question_bank_label(item.get("driver_tile_id"))
    if fallback:
        return fallback

    return "Diligence Questions"


def hydrate_project_payload_for_packet(project: Any, project_payload: Dict[str, Any]) -> Dict[str, Any]:
    calculation_data = project_payload.get("calculation_data") or {}
    if not isinstance(calculation_data, dict):
        calculation_data = {}

    request_data = (
        calculation_data.get("request_data")
        or calculation_data.get("parsed_input")
        or calculation_data.get("request_payload")
        or {}
    )
    if not isinstance(request_data, dict):
        request_data = {}
    request_data = dict(request_data)

    project_info = calculation_data.get("project_info") or {}
    if not isinstance(project_info, dict):
        project_info = {}

    request_data.setdefault("square_footage", project_payload.get("square_footage") or getattr(project, "square_footage", 0) or 0)
    request_data.setdefault("location", project_payload.get("location") or getattr(project, "location", None) or "Unknown")
    request_data.setdefault("building_type", project_info.get("building_type") or project_payload.get("building_type"))
    request_data.setdefault(
        "num_floors",
        request_data.get("floors")
        or project_info.get("floors")
        or project_payload.get("floors")
        or 1,
    )

    project_payload["request_data"] = request_data
    project_payload["project_name"] = (
        project_payload.get("project_name")
        or project_payload.get("name")
        or f"project_{getattr(project, 'project_id', None) or getattr(project, 'id', 'unknown')}"
    )
    return project_payload


def _packet_unavailable_notes(provenance: Dict[str, Any]) -> List[str]:
    notes: List[str] = []
    if not isinstance(provenance, dict):
        return notes

    for key in (
        "primary_control_variable",
        "first_break_condition",
        "flex_before_break_pct",
        "exposure_concentration_pct",
        "ranked_likely_wrong",
    ):
        value = provenance.get(key)
        if not isinstance(value, dict):
            continue
        reason = _sanitize_text(value.get("reason"))
        if reason and reason not in notes:
            notes.append(reason)
    return notes


def _normalize_schedule_phases(schedule: Dict[str, Any]) -> List[Dict[str, Any]]:
    phases_raw = schedule.get("phases")
    if not isinstance(phases_raw, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for index, phase in enumerate(phases_raw):
        if not isinstance(phase, dict):
            continue
        label = phase.get("label") or phase.get("id") or f"Phase {index + 1}"
        start_month = phase.get("start_month") if isinstance(phase.get("start_month"), (int, float)) else phase.get("startMonth")
        duration_months = phase.get("duration_months") if isinstance(phase.get("duration_months"), (int, float)) else phase.get("duration")
        normalized.append({
            "id": phase.get("id") or f"phase-{index + 1}",
            "label": label,
            "start_month": start_month if isinstance(start_month, (int, float)) else 0,
            "duration_months": duration_months if isinstance(duration_months, (int, float)) else 0,
        })
    return normalized


def _build_schedule_milestones(phases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    milestones: List[Dict[str, Any]] = []
    for phase in phases[:4]:
        start_month = _to_number(phase.get("start_month")) or 0
        duration_months = _to_number(phase.get("duration_months")) or 0
        midpoint = int(round(start_month + (duration_months / 2.0)))
        milestones.append({
            "label": phase.get("label") or phase.get("id") or "Milestone",
            "date_label": f"Month {midpoint}",
        })
    return milestones


def _normalize_special_feature_breakdown_rows(value: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for item in _as_list(value):
        if not isinstance(item, dict):
            continue
        feature_id = _sanitize_text(item.get("id"))
        label = _sanitize_text(item.get("label")) or _titleize_label(feature_id) or "Special Feature"
        pricing_status = _sanitize_text(item.get("pricing_status"))
        if pricing_status not in {"included_in_baseline", "incremental"}:
            pricing_status = ""
        row = {
            "id": feature_id,
            "label": label,
            "pricing_status": pricing_status,
            "pricing_basis": _sanitize_text(item.get("pricing_basis")),
            "count_pricing_mode": _sanitize_text(item.get("count_pricing_mode")),
            "configured_value": _to_number(item.get("configured_value")),
            "applied_quantity": _to_number(item.get("applied_quantity")),
            "configured_cost_per_sf": _to_number(item.get("configured_cost_per_sf")),
            "cost_per_sf": _to_number(item.get("cost_per_sf")),
            "configured_cost_per_count": _to_number(item.get("configured_cost_per_count")),
            "cost_per_count": _to_number(item.get("cost_per_count")),
            "configured_area_share_of_gsf": _to_number(item.get("configured_area_share_of_gsf")),
            "unit_label": _sanitize_text(item.get("unit_label")),
            "requested_quantity": _to_number(item.get("requested_quantity")),
            "requested_quantity_source": _sanitize_text(item.get("requested_quantity_source")),
            "included_baseline_quantity": _to_number(item.get("included_baseline_quantity")),
            "billed_quantity": _to_number(item.get("billed_quantity")),
            "total_cost": _to_number(item.get("total_cost")),
        }
        row["display_pricing_status"] = _resolve_special_feature_display_status(row)
        rows.append(row)
    return rows


def _format_quantity(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    if float(parsed).is_integer():
        return f"{int(parsed):,d}"
    return f"{parsed:,.1f}"


def _pluralize_unit_label(unit_label: Any, quantity: Any) -> str:
    normalized_unit_label = _sanitize_text(unit_label) or "item"
    parsed_quantity = _to_number(quantity)
    if parsed_quantity == 1:
        return normalized_unit_label
    lower_label = normalized_unit_label.lower()
    if len(lower_label) > 1 and lower_label.endswith("y") and lower_label[-2] not in {"a", "e", "i", "o", "u"}:
        return f"{normalized_unit_label[:-1]}ies"
    if lower_label.endswith(("s", "x", "z", "ch", "sh")):
        return f"{normalized_unit_label}es"
    return f"{normalized_unit_label}s"


def _format_area_share_percent(value: Any) -> str:
    parsed = _to_number(value)
    if parsed is None:
        return "—"
    pct = parsed * 100.0
    if float(pct).is_integer():
        return f"{int(pct)}%"
    return f"{pct:,.1f}%"


def _has_explicit_special_feature_requested_quantity(item: Dict[str, Any]) -> bool:
    requested_quantity_source = _sanitize_text(item.get("requested_quantity_source"))
    return requested_quantity_source.startswith("explicit_override:")


def _resolve_special_feature_display_status(item: Dict[str, Any]) -> str:
    pricing_status = _sanitize_text(item.get("pricing_status"))
    billed_quantity = _to_number(item.get("billed_quantity"))
    if (
        _sanitize_text(item.get("count_pricing_mode")) == "overage_above_default"
        and _has_explicit_special_feature_requested_quantity(item)
        and billed_quantity is not None
        and billed_quantity > 0
    ):
        return "incremental"
    if pricing_status in {"included_in_baseline", "incremental"}:
        return pricing_status
    total_cost = _to_number(item.get("total_cost"))
    if total_cost not in (None, 0.0):
        return "incremental"
    return ""


def _format_special_feature_basis_label(pricing_basis: str) -> str:
    if pricing_basis == "AREA_SHARE_GSF":
        return "Area-share of project GSF"
    if pricing_basis == "COUNT_BASED":
        return "Count-based"
    if pricing_basis == "WHOLE_PROJECT_SF":
        return "Whole-project SF"
    return _titleize_label(pricing_basis) or "Configured pricing basis"


def _resolve_special_feature_detail_lines(item: Dict[str, Any]) -> List[str]:
    pricing_basis = _sanitize_text(item.get("pricing_basis"))
    pricing_status = _sanitize_text(item.get("display_pricing_status") or item.get("pricing_status"))
    applied_quantity = _to_number(item.get("applied_quantity"))
    lines: List[str] = []

    if pricing_basis:
        lines.append(f"Basis: {_format_special_feature_basis_label(pricing_basis)}")

    if pricing_basis == "AREA_SHARE_GSF":
        configured_value = _to_number(item.get("configured_value"))
        if applied_quantity is not None:
            if pricing_status == "incremental" and configured_value is not None:
                lines.append(
                    f"{_format_money(configured_value)} per feature-area SF × "
                    f"{_format_quantity(applied_quantity)} SF assumed feature area"
                )
            else:
                lines.append(
                    f"Applied quantity: {_format_quantity(applied_quantity)} SF assumed feature area"
                )
        configured_area_share = _to_number(item.get("configured_area_share_of_gsf"))
        if configured_area_share is not None:
            lines.append(
                f"Assumed feature area = {_format_area_share_percent(configured_area_share)} of project GSF"
            )
        return lines

    if pricing_basis == "COUNT_BASED":
        configured_cost_per_count = _to_number(item.get("configured_cost_per_count"))
        unit_label = _sanitize_text(item.get("unit_label")) or "item"
        if applied_quantity is not None:
            if pricing_status == "incremental" and configured_cost_per_count is not None:
                lines.append(
                    f"{_format_money(configured_cost_per_count)} per {unit_label} × "
                    f"{_format_quantity(applied_quantity)} {_pluralize_unit_label(unit_label, applied_quantity)}"
                )
            else:
                lines.append(
                    f"Applied quantity: {_format_quantity(applied_quantity)} "
                    f"{_pluralize_unit_label(unit_label, applied_quantity)}"
                )

        if (
            _sanitize_text(item.get("count_pricing_mode")) == "overage_above_default"
            and _has_explicit_special_feature_requested_quantity(item)
        ):
            requested_quantity = _to_number(item.get("requested_quantity"))
            included_baseline_quantity = _to_number(item.get("included_baseline_quantity"))
            billed_quantity = _to_number(item.get("billed_quantity"))
            if requested_quantity is not None and included_baseline_quantity is not None and billed_quantity is not None:
                lines.extend(
                    [
                        f"Baseline includes {_format_quantity(included_baseline_quantity)} "
                        f"{_pluralize_unit_label(unit_label, included_baseline_quantity)}",
                        f"You specified {_format_quantity(requested_quantity)} "
                        f"{_pluralize_unit_label(unit_label, requested_quantity)}",
                        (
                            f"Pricing includes {_format_quantity(billed_quantity)} additional "
                            f"{_pluralize_unit_label(unit_label, billed_quantity)}"
                            if billed_quantity > 0
                            else f"No additional {_pluralize_unit_label(unit_label, 2)} priced"
                        ),
                    ]
                )
        return lines

    if pricing_basis == "WHOLE_PROJECT_SF":
        configured_cost_per_sf = _to_number(item.get("configured_cost_per_sf"))
        if applied_quantity is not None:
            if pricing_status == "incremental" and configured_cost_per_sf is not None:
                lines.append(
                    f"{_format_money(configured_cost_per_sf)}/SF × {_format_quantity(applied_quantity)} SF"
                )
            else:
                lines.append(f"Applied quantity: {_format_quantity(applied_quantity)} SF")
    return lines


def _resolve_special_feature_treatment(item: Dict[str, Any]) -> str:
    pricing_status = _sanitize_text(item.get("display_pricing_status") or item.get("pricing_status"))
    billed_quantity = _to_number(item.get("billed_quantity"))
    if pricing_status == "included_in_baseline":
        return "Included in baseline"
    if pricing_status == "incremental":
        if (
            _sanitize_text(item.get("count_pricing_mode")) == "overage_above_default"
            and _has_explicit_special_feature_requested_quantity(item)
            and billed_quantity == 0
        ):
            return "No additional premium"
        return "Incremental premium applied"
    if _to_number(item.get("total_cost")) not in (None, 0.0):
        return "Applied premium"
    return "Selected feature"


def compose_decision_packet_input(
    project: Any,
    project_payload: Dict[str, Any],
    payload: Dict[str, Any],
    dealshield_view_model: Dict[str, Any],
    client_name: str | None,
) -> Dict[str, Any]:
    calculation_data = project_payload.get("calculation_data") or {}
    if not isinstance(calculation_data, dict):
        calculation_data = {}

    request_data = project_payload.get("request_data") or {}
    if not isinstance(request_data, dict):
        request_data = {}

    project_info = calculation_data.get("project_info") or {}
    if not isinstance(project_info, dict):
        project_info = {}

    ownership = calculation_data.get("ownership_analysis") or {}
    if not isinstance(ownership, dict):
        ownership = {}

    return_metrics = ownership.get("return_metrics") or calculation_data.get("return_metrics") or {}
    if not isinstance(return_metrics, dict):
        return_metrics = {}

    debt_metrics = ownership.get("debt_metrics") or calculation_data.get("debt_metrics") or {}
    if not isinstance(debt_metrics, dict):
        debt_metrics = {}

    revenue_analysis = ownership.get("revenue_analysis") or calculation_data.get("revenue_analysis") or {}
    if not isinstance(revenue_analysis, dict):
        revenue_analysis = {}

    revenue_requirements = ownership.get("revenue_requirements") or calculation_data.get("revenue_requirements") or {}
    if not isinstance(revenue_requirements, dict):
        revenue_requirements = {}

    totals = calculation_data.get("totals") or {}
    if not isinstance(totals, dict):
        totals = {}

    construction_costs = calculation_data.get("construction_costs") or {}
    if not isinstance(construction_costs, dict):
        construction_costs = {}

    trade_breakdown = calculation_data.get("trade_breakdown") or project_payload.get("trade_breakdown") or {}
    if not isinstance(trade_breakdown, dict):
        trade_breakdown = {}

    construction_schedule = calculation_data.get("construction_schedule") or {}
    if not isinstance(construction_schedule, dict):
        construction_schedule = {}

    financing_summary = calculation_data.get("financing_summary") or {}
    if not isinstance(financing_summary, dict):
        financing_summary = {}
    financing_summary_items = [
        item
        for item in _as_list(financing_summary.get("items"))
        if isinstance(item, dict) and _sanitize_text(item.get("label")) and _to_number(item.get("value")) is not None
    ]
    financing_assumptions = calculation_data.get("financing_assumptions")
    if not isinstance(financing_assumptions, dict):
        financing_assumptions = dealshield_view_model.get("financing_assumptions")
    if not isinstance(financing_assumptions, dict):
        financing_assumptions = {}

    cover_square_footage = (
        _to_number(request_data.get("square_footage"))
        or _to_number(project_payload.get("square_footage"))
        or _to_number(getattr(project, "square_footage", None))
    )
    building_type = (
        project_info.get("building_type")
        or request_data.get("building_type")
        or project_payload.get("building_type")
        or getattr(project, "building_type", None)
    )
    subtype = (
        project_info.get("subtype")
        or project_payload.get("subtype")
        or payload.get("subtype")
    )

    annual_revenue = (
        _to_number(revenue_analysis.get("annual_revenue"))
        or _to_number(ownership.get("annual_revenue"))
        or _to_number(calculation_data.get("annual_revenue"))
        or _to_number(revenue_requirements.get("market_value"))
    )
    annual_noi = (
        _to_number(return_metrics.get("estimated_annual_noi"))
        or _to_number(revenue_analysis.get("net_income"))
        or _to_number(calculation_data.get("net_income"))
        or _to_number(revenue_requirements.get("actual_net_income"))
    )
    operating_margin = _normalize_percentish(revenue_analysis.get("operating_margin"))
    if operating_margin is None:
        operating_margin = _normalize_percentish(revenue_requirements.get("operating_margin"))
    if operating_margin is not None and abs(operating_margin) > 1.5:
        operating_margin = operating_margin / 100.0
    if operating_margin is None and annual_revenue and annual_revenue > 0 and annual_noi is not None:
        operating_margin = annual_noi / annual_revenue

    target_yield = _normalize_percentish(revenue_requirements.get("target_yield"))
    if target_yield is None:
        target_yield = _normalize_percentish(revenue_requirements.get("target_roi"))
    if target_yield is None:
        target_yield = _normalize_percentish(return_metrics.get("target_roi"))
    if target_yield is None:
        target_yield = _normalize_percentish(return_metrics.get("target_yield"))
    if target_yield is not None and abs(target_yield) > 1.5:
        target_yield = target_yield / 100.0

    total_project_cost = (
        _to_number(totals.get("total_project_cost"))
        or _to_number(project_payload.get("total_cost"))
        or _to_number(getattr(project, "total_cost", None))
    )
    cost_per_sqft = (
        _to_number(totals.get("cost_per_sqft"))
        or _to_number(totals.get("total_cost_per_sqft"))
        or _to_number(project_payload.get("cost_per_sqft"))
        or _to_number(getattr(project, "cost_per_sqft", None))
    )

    required_noi = _to_number(revenue_requirements.get("required_value"))
    if required_noi is None and total_project_cost is not None and target_yield is not None:
        required_noi = total_project_cost * target_yield

    current_noi = annual_noi or _to_number(revenue_requirements.get("actual_net_income"))
    noi_gap = current_noi - required_noi if current_noi is not None and required_noi is not None else None

    required_annual_revenue = _to_number(revenue_requirements.get("required_revenue"))
    if required_annual_revenue is None and required_noi is not None and operating_margin is not None and operating_margin > 0:
        required_annual_revenue = required_noi / operating_margin

    current_annual_revenue = annual_revenue or _to_number(revenue_requirements.get("market_value"))
    revenue_gap = (
        current_annual_revenue - required_annual_revenue
        if current_annual_revenue is not None and required_annual_revenue is not None
        else None
    )

    required_revenue_per_sf = _to_number(revenue_requirements.get("required_revenue_per_sf"))
    if required_revenue_per_sf is None and required_annual_revenue is not None and cover_square_footage and cover_square_footage > 0:
        required_revenue_per_sf = required_annual_revenue / cover_square_footage

    current_revenue_per_sf = _to_number(revenue_requirements.get("actual_revenue_per_sf"))
    if current_revenue_per_sf is None and current_annual_revenue is not None and cover_square_footage and cover_square_footage > 0:
        current_revenue_per_sf = current_annual_revenue / cover_square_footage

    rendered_copy = dealshield_view_model.get("rendered_copy") or {}
    if not isinstance(rendered_copy, dict):
        rendered_copy = {}
    decision_summary = dealshield_view_model.get("decision_summary") or {}
    if not isinstance(decision_summary, dict):
        decision_summary = {}
    content = dealshield_view_model.get("content") or {}
    if not isinstance(content, dict):
        content = {}
    provenance = dealshield_view_model.get("provenance") or {}
    if not isinstance(provenance, dict):
        provenance = {}
    packet_disclosures = _clean_packet_financing_disclosures(
        dealshield_view_model.get("dealshield_disclosures"),
        has_financing_summary=bool(financing_summary_items),
    )

    trade_items: List[Dict[str, Any]] = []
    total_trade_cost = sum(amount for amount in (_to_number(value) for value in trade_breakdown.values()) if amount is not None)
    for trade_name, amount_raw in trade_breakdown.items():
        amount = _to_number(amount_raw)
        if amount is None:
            continue
        trade_items.append({
            "label": _titleize_label(trade_name),
            "amount": amount,
            "percent": (amount / total_trade_cost) if total_trade_cost > 0 else None,
        })
    trade_items.sort(key=lambda item: item.get("amount") or 0, reverse=True)

    cost_build_up_items = construction_costs.get("cost_build_up")
    if not isinstance(cost_build_up_items, list):
        cost_build_up_items = []
    special_feature_breakdown = _normalize_special_feature_breakdown_rows(
        construction_costs.get("special_features_breakdown")
    )

    phases = _normalize_schedule_phases(construction_schedule)
    milestones = _build_schedule_milestones(phases)

    break_risk = dealshield_view_model.get("break_risk")
    if not isinstance(break_risk, dict):
        break_risk = {
            "level": dealshield_view_model.get("break_risk_level"),
            "reason": dealshield_view_model.get("break_risk_reason"),
        }

    decision_insurance_provenance = (
        dealshield_view_model.get("decision_insurance_provenance")
        or provenance.get("decision_insurance")
        or {}
    )
    if not isinstance(decision_insurance_provenance, dict):
        decision_insurance_provenance = {}

    exposure_pct = _to_number(dealshield_view_model.get("exposure_concentration_pct"))

    return {
        "cover_summary": {
            "project_name": project_payload.get("project_name") or getattr(project, "name", None),
            "client_name": client_name,
            "location": project_payload.get("location") or getattr(project, "location", None),
            "building_type": building_type,
            "building_type_label": _titleize_label(building_type),
            "subtype": subtype,
            "subtype_label": _titleize_label(subtype),
            "project_classification": project_payload.get("project_classification"),
            "square_footage": cover_square_footage,
            "generated_at": datetime.utcnow().strftime("%B %d, %Y"),
        },
        "decision_banner": {
            "decision_status": dealshield_view_model.get("decision_status"),
            "decision_reason_code": dealshield_view_model.get("decision_reason_code"),
            "summary": rendered_copy.get("decision_status_summary"),
            "detail": rendered_copy.get("decision_status_detail"),
            "policy_basis_line": rendered_copy.get("policy_basis_line"),
            "decision_summary": decision_summary,
        },
        "key_metrics": {
            "total_project_cost": total_project_cost,
            "yield_on_cost": _normalize_percentish(ownership.get("yield_on_cost")) or _normalize_percentish(calculation_data.get("yield_on_cost")),
            "dscr": _to_number(debt_metrics.get("calculated_dscr")),
            "annual_revenue": current_annual_revenue,
            "annual_noi": current_noi,
        },
        "decision_insurance": {
            "primary_control_variable": dealshield_view_model.get("primary_control_variable"),
            "first_break_condition": dealshield_view_model.get("first_break_condition"),
            "flex_before_break_pct": dealshield_view_model.get("flex_before_break_pct"),
            "flex_before_break_band": dealshield_view_model.get("flex_before_break_band"),
            "exposure_concentration_pct": dealshield_view_model.get("exposure_concentration_pct"),
            "exposure_sentence": (
                f"Primary control variable contributes {dealshield_view_model.get('exposure_concentration_pct')}% of modeled downside sensitivity."
                if exposure_pct is not None
                else None
            ),
            "break_risk": break_risk,
            "ranked_likely_wrong": dealshield_view_model.get("ranked_likely_wrong"),
            "unavailable_notes": _packet_unavailable_notes(decision_insurance_provenance),
            "provenance": decision_insurance_provenance,
        },
        "decision_metrics_table": (
            dealshield_view_model.get("decision_table")
            or {
                "columns": dealshield_view_model.get("columns", []),
                "rows": dealshield_view_model.get("rows", []),
            }
        ),
        "assumptions_not_modeled": {
            "financing_summary": financing_summary if financing_summary_items else {},
            "financing_assumptions": financing_assumptions,
            "disclosures": packet_disclosures,
            "decision_summary": decision_summary,
            "not_modeled_reason": decision_summary.get("not_modeled_reason"),
        },
        "economics_snapshot": {
            "total_project_cost": total_project_cost,
            "cost_per_sqft": cost_per_sqft,
            "annual_revenue": current_annual_revenue,
            "annual_noi": current_noi,
            "yield_on_cost": _normalize_percentish(ownership.get("yield_on_cost")) or _normalize_percentish(calculation_data.get("yield_on_cost")),
            "dscr": _to_number(debt_metrics.get("calculated_dscr")),
            "property_value": _to_number(return_metrics.get("property_value")),
            "target_yield": target_yield,
        },
        "revenue_required": {
            "target_yield": target_yield,
            "operating_margin": operating_margin,
            "required_noi": required_noi,
            "current_noi": current_noi,
            "noi_gap": noi_gap,
            "required_annual_revenue": required_annual_revenue,
            "current_annual_revenue": current_annual_revenue,
            "revenue_gap": revenue_gap,
            "required_revenue_per_sf": required_revenue_per_sf,
            "current_revenue_per_sf": current_revenue_per_sf,
        },
        "construction_summary": {
            "hard_costs": _to_number(totals.get("hard_costs")),
            "soft_costs": _to_number(totals.get("soft_costs")),
            "construction_total": _to_number(construction_costs.get("construction_total")) or _to_number(totals.get("hard_costs")),
            "total_project_cost": total_project_cost,
            "cost_per_sqft": cost_per_sqft,
            "special_features_total": _to_number(construction_costs.get("special_features_total")) or _to_number(totals.get("special_features_total")),
            "special_features_breakdown": special_feature_breakdown,
        },
        "trade_distribution": {
            "items": trade_items[:8],
        },
        "cost_build_up": {
            "items": cost_build_up_items,
        },
        "schedule_milestones": {
            "total_months": construction_schedule.get("total_months"),
            "phases": phases,
            "milestones": milestones,
        },
        "trust_sections": {
            "most_likely_wrong": content.get("most_likely_wrong"),
            "question_bank": content.get("question_bank"),
            "red_flags_actions": content.get("red_flags_actions"),
        },
        "provenance": {
            "profile_id": dealshield_view_model.get("tile_profile_id") or provenance.get("profile_id"),
            "content_profile_id": dealshield_view_model.get("content_profile_id") or provenance.get("content_profile_id"),
            "scope_items_profile_id": dealshield_view_model.get("scope_items_profile_id") or provenance.get("scope_items_profile_id"),
            "decision_status": dealshield_view_model.get("decision_status"),
            "decision_reason_code": dealshield_view_model.get("decision_reason_code"),
            "decision_status_provenance": dealshield_view_model.get("decision_status_provenance"),
            "scenario_inputs": provenance.get("scenario_inputs"),
            "dealshield_controls": provenance.get("dealshield_controls"),
            "context": dealshield_view_model.get("context"),
        },
    }


def _render_metric_grid(metrics: List[str]) -> str:
    if not metrics:
        return "<div class=\"empty-note\">No metrics available.</div>"
    return "<div class=\"metric-grid\">" + "".join(metrics) + "</div>"


def _render_cover_summary(summary: Dict[str, Any]) -> str:
    facts = [
        ("Project", _sanitize_text(summary.get("project_name")) or "SpecSharp Project"),
        ("Client", _sanitize_text(summary.get("client_name")) or "—"),
        ("Location", _sanitize_text(summary.get("location")) or "—"),
        ("Building Type", _sanitize_text(summary.get("building_type_label") or summary.get("building_type")) or "—"),
        ("Subtype", _sanitize_text(summary.get("subtype_label") or summary.get("subtype")) or "—"),
        ("Program", _sanitize_text(summary.get("project_classification")) or "—"),
        ("Building Size", _format_sqft(summary.get("square_footage"))),
        ("Generated", _sanitize_text(summary.get("generated_at")) or datetime.utcnow().strftime("%B %d, %Y")),
    ]
    rows = [
        (
            "<div class=\"cover-row\">"
            f"<span class=\"cover-label\">{html_module.escape(label)}</span>"
            f"<span class=\"cover-value\">{html_module.escape(value)}</span>"
            "</div>"
        )
        for label, value in facts
    ]
    return (
        "<section class=\"cover-summary\">"
        "<div class=\"eyebrow\">SpecSharp Decision Packet</div>"
        f"<h1>{html_module.escape(_sanitize_text(summary.get('project_name')) or 'SpecSharp Project')}</h1>"
        "<div class=\"cover-grid\">"
        + "".join(rows)
        + "</div>"
        "</section>"
    )


def _status_class(status: str) -> str:
    normalized = _sanitize_text(status).upper()
    if normalized == "GO":
        return "status-go"
    if normalized == "NO-GO":
        return "status-no-go"
    if normalized == "NEEDS WORK":
        return "status-needs-work"
    return "status-pending"


def _render_decision_banner(banner: Dict[str, Any]) -> str:
    status = _sanitize_text(banner.get("decision_status")) or "PENDING"
    reason = _sanitize_text(banner.get("decision_reason_code")) or "—"
    summary = _sanitize_text(banner.get("summary")) or "Decision summary unavailable."
    detail = _sanitize_text(banner.get("detail")) or ""
    basis = _sanitize_text(banner.get("policy_basis_line")) or ""

    detail_html = f"<p class=\"banner-detail\">{html_module.escape(detail)}</p>" if detail else ""
    basis_html = f"<p class=\"banner-basis\">{html_module.escape(basis)}</p>" if basis else ""

    return (
        f"<section class=\"decision-banner {_status_class(status)}\">"
        f"<div class=\"decision-status-chip\">{html_module.escape(status)}</div>"
        f"<div class=\"decision-reason\">Reason code: {html_module.escape(reason)}</div>"
        f"<h2>{html_module.escape(summary)}</h2>"
        f"{detail_html}"
        f"{basis_html}"
        "</section>"
    )


def _render_decision_insurance(insurance: Dict[str, Any], provenance: Dict[str, Any]) -> str:
    primary = _as_dict(insurance.get("primary_control_variable"))
    first_break = _as_dict(insurance.get("first_break_condition"))
    break_risk = _as_dict(insurance.get("break_risk"))
    ranked = _as_list(insurance.get("ranked_likely_wrong"))
    unavailable = [
        _sanitize_text(item)
        for item in _as_list(insurance.get("unavailable_notes"))
        if _sanitize_text(item)
    ]
    first_break_scenario = _sanitize_text(first_break.get("scenario_label") or first_break.get("scenario_id")) or "—"
    first_break_observed = _format_readable_insurance_value(first_break.get("observed_value"))
    first_break_operator = _sanitize_text(first_break.get("operator"))
    first_break_threshold_value = _format_readable_insurance_value(first_break.get("threshold_value")) if first_break.get("threshold_value") is not None else ""
    first_break_lines = [
        f"Scenario: {first_break_scenario}",
        f"Observed value: {first_break_observed}",
    ]
    if first_break_operator and first_break_threshold_value and first_break_threshold_value != "—":
        first_break_lines.append(f"Threshold: {first_break_operator} {first_break_threshold_value}")

    exposure_pct_display = _format_percent_fixed_two(insurance.get("exposure_concentration_pct"))
    if exposure_pct_display != "—":
        exposure_detail = f"Primary control variable contributes {exposure_pct_display} of modeled downside sensitivity."
    else:
        exposure_detail = "Primary control variable share of modeled downside sensitivity."

    primary_label = _format_export_primary_control_label(
        primary.get("label") or primary.get("id") or "Unavailable",
        provenance.get("profile_id"),
    )

    cards = [
        (
            "<div class=\"subcard\">"
            "<div class=\"subcard-title\">Primary Control Variable</div>"
            f"<div class=\"subcard-value\">{html_module.escape(primary_label)}</div>"
            "<div class=\"subcard-detail\">"
            f"Impact: {html_module.escape(_format_percent(primary.get('impact_pct')))}"
            f" | Severity: {html_module.escape(_sanitize_text(primary.get('severity')) or '—')}"
            f" | Break Risk: {html_module.escape(_sanitize_text(break_risk.get('level')) or '—')}"
            "</div>"
            "</div>"
        ),
        (
            "<div class=\"subcard\">"
            "<div class=\"subcard-title\">First Break Condition</div>"
            f"<div class=\"subcard-value\">{_escape(first_break.get('summary_text') or first_break.get('scenario_label') or first_break.get('scenario_id') or 'Unavailable')}</div>"
            + "<div class=\"subcard-detail\">"
            + "<br/>".join(html_module.escape(line) for line in first_break_lines)
            + "</div>"
            + "</div>"
        ),
        (
            "<div class=\"subcard\">"
            "<div class=\"subcard-title\">Flex Before Break</div>"
            f"<div class=\"subcard-value\">{html_module.escape(_format_percent_fixed_two(insurance.get('flex_before_break_pct')))}</div>"
            f"<div class=\"subcard-detail\">Band: {html_module.escape(_sanitize_text(insurance.get('flex_before_break_band')) or '—')}</div>"
            "</div>"
        ),
        (
            "<div class=\"subcard\">"
            "<div class=\"subcard-title\">Exposure Concentration</div>"
            f"<div class=\"subcard-value\">{html_module.escape(exposure_pct_display)}</div>"
            f"<div class=\"subcard-detail\">{html_module.escape(exposure_detail)}</div>"
            "</div>"
        ),
    ]

    ranked_html = ""
    if ranked:
        ranked_items = []
        for entry in ranked[:5]:
            item = _as_dict(entry)
            ranked_items.append(
                "<li>"
                f"<strong>{_escape(item.get('text') or item.get('id') or 'Risk')}</strong>"
                f"<div class=\"list-detail\">Impact: {html_module.escape(_format_percent(item.get('impact_pct')))}"
                f" | Severity: {html_module.escape(_sanitize_text(item.get('severity')) or '—')}</div>"
                f"<div class=\"list-detail\">Why: {_escape(item.get('why') or '—')}</div>"
                "</li>"
            )
        ranked_html = (
            "<div class=\"subsection\">"
            "<h3>Ranked Most Likely Wrong</h3>"
            "<ul class=\"bullet-list\">"
            + "".join(ranked_items)
            + "</ul></div>"
        )

    unavailable_html = ""
    if unavailable:
        unavailable_html = (
            "<div class=\"note-block\">"
            "<strong>Unavailable reason(s)</strong>"
            "<ul class=\"bullet-list compact\">"
            + "".join(f"<li>{html_module.escape(note)}</li>" for note in unavailable)
            + "</ul></div>"
        )

    return (
        "<section>"
        "<h2>Decision Insurance / Downside Summary</h2>"
        "<div class=\"subcard-grid\">"
        + "".join(cards)
        + "</div>"
        + ranked_html
        + unavailable_html
        + "</section>"
    )


def _render_decision_metrics_table(table_block: Dict[str, Any]) -> str:
    columns = [col for col in _as_list(table_block.get("columns")) if isinstance(col, dict)]
    rows = [row for row in _as_list(table_block.get("rows")) if isinstance(row, dict)]
    if not columns or not rows:
        return (
            "<section>"
            "<h2>Decision Metrics Table</h2>"
            "<div class=\"empty-note\">Decision metrics unavailable.</div>"
            "</section>"
        )

    header_cells = [
        f"<th>{_escape(col.get('label') or col.get('title') or col.get('id') or 'Metric')}</th>"
        for col in columns
    ]

    row_html: List[str] = []
    for row in rows:
        cells_by_id: Dict[str, Dict[str, Any]] = {}
        for cell in _as_list(row.get("cells")):
            if not isinstance(cell, dict):
                continue
            cell_id = cell.get("col_id") or cell.get("tile_id") or cell.get("id")
            if isinstance(cell_id, str) and cell_id:
                cells_by_id[cell_id] = cell

        rendered_cells = []
        for col in columns:
            col_id = col.get("id") or col.get("col_id") or col.get("tile_id")
            metric_ref = col.get("metric_ref") or col.get("metricRef")
            cell = cells_by_id.get(str(col_id)) if col_id is not None else None
            value = cell.get("display_value") if isinstance(cell, dict) and isinstance(cell.get("display_value"), str) else None
            if not value:
                raw_value = cell.get("value") if isinstance(cell, dict) else None
                if metric_ref and "dscr" in str(metric_ref).lower():
                    value = _format_ratio(raw_value)
                elif metric_ref and "yield" in str(metric_ref).lower():
                    value = _format_percent(raw_value)
                elif metric_ref and any(token in str(metric_ref).lower() for token in ("cost", "revenue", "value", "noi", "income")):
                    value = _format_money(raw_value)
                else:
                    value = _sanitize_text(raw_value) or "—"
            rendered_cells.append(f"<td>{html_module.escape(value)}</td>")

        row_label = _sanitize_text(row.get("label") or row.get("scenario_label") or row.get("scenario_id") or "Scenario")
        row_html.append(
            "<tr>"
            f"<th class=\"row-label\">{html_module.escape(row_label)}</th>"
            + "".join(rendered_cells)
            + "</tr>"
        )

    return (
        "<section class=\"decision-table-section\">"
        "<h2>Decision Metrics Table</h2>"
        "<table class=\"decision-table\">"
        "<thead><tr><th>Scenario</th>"
        + "".join(header_cells)
        + "</tr></thead>"
        "<tbody>"
        + "".join(row_html)
        + "</tbody></table>"
        "</section>"
    )


def _render_assumptions(section: Dict[str, Any]) -> str:
    financing_summary = _as_dict(section.get("financing_summary"))
    financing_summary_items = [
        item for item in _as_list(financing_summary.get("items")) if isinstance(item, dict)
    ]
    assumptions = _as_dict(section.get("financing_assumptions"))
    disclosures = [item for item in _as_list(section.get("disclosures")) if _sanitize_text(item)]
    summary = _as_dict(section.get("decision_summary"))
    not_modeled = _sanitize_text(section.get("not_modeled_reason") or summary.get("not_modeled_reason"))

    financing_summary_html = ""
    if financing_summary_items:
        financing_summary_rows = []
        for item in financing_summary_items:
            label = _sanitize_text(item.get("label"))
            value = _format_financing_summary_value(item)
            if not label or value == "—":
                continue
            financing_summary_rows.append(
                "<div class=\"info-item\">"
                f"<span class=\"info-label\">{html_module.escape(label)}</span>"
                f"<span class=\"info-value\">{html_module.escape(value)}</span>"
                "</div>"
            )
        if financing_summary_rows:
            financing_summary_html = (
                "<div class=\"subsection\">"
                "<h3>Current Modeled Financing Summary</h3>"
                "<div class=\"info-grid\">"
                + "".join(financing_summary_rows)
                + "</div></div>"
            )

    rows = [
        ("Debt %", _format_percent(assumptions.get("debt_pct") or assumptions.get("ltv"))),
        ("Rate", _format_percent(assumptions.get("interest_rate_pct"))),
        ("Amortization", _sanitize_text(assumptions.get("amort_years")) + (" yrs" if assumptions.get("amort_years") is not None else "")),
        ("Loan Term", _sanitize_text(assumptions.get("loan_term_years")) + (" yrs" if assumptions.get("loan_term_years") is not None else "")),
        ("Interest-only", _sanitize_text(assumptions.get("interest_only_months")) + (" mo" if assumptions.get("interest_only_months") is not None else "")),
        ("Annual Debt Service", _format_money(assumptions.get("annual_debt_service"))),
        ("Monthly Debt Service", _format_money(assumptions.get("monthly_debt_service"))),
        ("Target DSCR", _format_ratio(assumptions.get("target_dscr"))),
        ("Calculated DSCR", _format_ratio(assumptions.get("calculated_dscr"))),
    ]
    rows = [row for row in rows if row[1].strip() and row[1] != "—"]

    if rows:
        assumptions_html = (
            "<div class=\"subsection\">"
            "<h3>Structured Financing Assumptions</h3>"
            "<div class=\"info-grid\">"
            + "".join(
                "<div class=\"info-item\">"
                f"<span class=\"info-label\">{html_module.escape(label)}</span>"
                f"<span class=\"info-value\">{html_module.escape(value)}</span>"
                "</div>"
                for label, value in rows
            )
            + "</div></div>"
        )
    elif financing_summary_html:
        assumptions_html = (
            "<div class=\"note-block\">"
            "<strong>Structured financing boundary:</strong> Current modeled debt and source-mix outputs are shown above. "
            "Structured financing assumptions such as term, amortization, IO, and layered debt are not yet modeled."
            "</div>"
        )
    else:
        assumptions_html = "<div class=\"empty-note\">No financing assumptions provided.</div>"

    disclosures_html = ""
    if disclosures:
        disclosures_html = (
            "<div class=\"subsection\">"
            "<h3>What’s Not Modeled / Guardrails</h3>"
            "<ul class=\"bullet-list\">"
            + "".join(f"<li>{html_module.escape(_sanitize_text(item))}</li>" for item in disclosures)
            + "</ul></div>"
        )

    not_modeled_html = (
        "<div class=\"note-block\">"
        f"<strong>Not modeled:</strong> {html_module.escape(not_modeled)}"
        "</div>"
        if not_modeled
        else ""
    )

    return (
        "<section>"
        + (
            "<h2>Financing Summary / What’s Not Modeled</h2>"
            if financing_summary_html
            else "<h2>Assumptions / What’s Not Modeled</h2>"
        )
        + financing_summary_html
        + assumptions_html
        + disclosures_html
        + not_modeled_html
        + "</section>"
    )


def _render_economics_snapshot(snapshot: Dict[str, Any]) -> str:
    metrics = [
        _format_metric("Total Project Cost", _format_money(snapshot.get("total_project_cost"))),
        _format_metric("Cost per SF", _format_money_per_sf(snapshot.get("cost_per_sqft"))),
        _format_metric("Annual Revenue", _format_money(snapshot.get("annual_revenue"))),
        _format_metric("Annual NOI", _format_money(snapshot.get("annual_noi"))),
        _format_metric("Yield on Cost", _format_percent(snapshot.get("yield_on_cost"))),
        _format_metric("DSCR", _format_ratio(snapshot.get("dscr"))),
    ]
    if _to_number(snapshot.get("property_value")) is not None:
        metrics.append(_format_metric("Property Value", _format_money(snapshot.get("property_value"))))
    if _to_number(snapshot.get("target_yield")) is not None:
        metrics.append(_format_metric("Target Yield", _format_percent(snapshot.get("target_yield"))))

    return (
        "<section>"
        "<h2>Economics Snapshot</h2>"
        + _render_metric_grid(metrics)
        + "</section>"
    )


def _render_revenue_required(section: Dict[str, Any]) -> str:
    metrics = [
        _format_metric("Target Yield", _format_percent(section.get("target_yield"))),
        _format_metric("Required NOI", _format_money(section.get("required_noi"))),
        _format_metric("Current NOI", _format_money(section.get("current_noi"))),
        _format_metric("NOI Gap", _format_money(section.get("noi_gap"))),
        _format_metric("Required Annual Revenue", _format_money(section.get("required_annual_revenue"))),
        _format_metric("Current Annual Revenue", _format_money(section.get("current_annual_revenue"))),
        _format_metric("Revenue Gap", _format_money(section.get("revenue_gap"))),
    ]

    secondary = []
    if _to_number(section.get("required_revenue_per_sf")) is not None:
        secondary.append(_format_metric("Required Revenue / SF", _format_money_per_sf(section.get("required_revenue_per_sf"))))
    if _to_number(section.get("current_revenue_per_sf")) is not None:
        secondary.append(_format_metric("Current Revenue / SF", _format_money_per_sf(section.get("current_revenue_per_sf"))))
    if _to_number(section.get("operating_margin")) is not None:
        secondary.append(_format_metric("Operating Margin Used", _format_percent(section.get("operating_margin"))))

    return (
        "<section>"
        "<h2>Revenue Required to Hit Target Yield</h2>"
        + _render_metric_grid(metrics + secondary)
        + "</section>"
    )


def _render_construction_summary(section: Dict[str, Any]) -> str:
    metrics = [
        _format_metric("Hard Costs", _format_money(section.get("hard_costs"))),
        _format_metric("Soft Costs", _format_money(section.get("soft_costs"))),
        _format_metric("Base Construction", _format_money(section.get("construction_total"))),
        _format_metric("Total Project Cost", _format_money(section.get("total_project_cost"))),
        _format_metric("Cost per SF", _format_money_per_sf(section.get("cost_per_sqft"))),
    ]
    if _to_number(section.get("special_features_total")) is not None:
        metrics.append(_format_metric("Special Features", _format_money(section.get("special_features_total"))))
    special_features_rows = [
        item
        for item in _as_list(section.get("special_features_breakdown"))
        if isinstance(item, dict)
    ]
    special_features_html = ""
    if special_features_rows:
        rows: List[str] = []
        for item in special_features_rows:
            label = _sanitize_text(item.get("label")) or "Special Feature"
            amount = _format_money(item.get("total_cost"))
            treatment = _resolve_special_feature_treatment(item)
            detail_lines = _resolve_special_feature_detail_lines(item)
            detail_html = (
                "".join(
                    f"<div class=\"list-detail\">{html_module.escape(line)}</div>"
                    for line in detail_lines
                )
                if detail_lines
                else "—"
            )
            rows.append(
                "<tr>"
                f"<td>{html_module.escape(label)}</td>"
                f"<td>{html_module.escape(amount)}</td>"
                f"<td>{html_module.escape(treatment)}</td>"
                f"<td>{detail_html}</td>"
                "</tr>"
            )
        special_features_html = (
            "<div class=\"subsection\">"
            "<h3>Selected Special Features</h3>"
            "<table class=\"simple-table\">"
            "<thead><tr><th>Feature</th><th>Applied Amount</th><th>Treatment</th><th>Pricing Detail</th></tr></thead>"
            "<tbody>"
            + "".join(rows)
            + "</tbody></table>"
            "</div>"
        )

    return (
        "<section>"
        "<h2>Construction Cost Summary</h2>"
        + _render_metric_grid(metrics)
        + special_features_html
        + "</section>"
    )


def _render_trade_distribution(section: Dict[str, Any]) -> str:
    items = [item for item in _as_list(section.get("items")) if isinstance(item, dict)]
    if not items:
        return ""

    rows = []
    for item in items[:8]:
        label = _sanitize_text(item.get("label")) or "Trade"
        amount = _format_money(item.get("amount"))
        pct = _format_percent(item.get("percent"))
        rows.append(
            "<tr>"
            f"<td>{html_module.escape(label)}</td>"
            f"<td>{html_module.escape(amount)}</td>"
            f"<td>{html_module.escape(pct)}</td>"
            "</tr>"
        )

    return (
        "<section>"
        "<h2>Trade Distribution / Top Cost Drivers</h2>"
        "<table class=\"simple-table\">"
        "<thead><tr><th>Trade</th><th>Amount</th><th>Share</th></tr></thead>"
        "<tbody>"
        + "".join(rows)
        + "</tbody></table>"
        "</section>"
    )


def _render_cost_build_up(section: Dict[str, Any]) -> str:
    items = [item for item in _as_list(section.get("items")) if isinstance(item, dict)]
    if not items:
        return ""

    rows = []
    for item in items:
        label = _sanitize_text(item.get("label") or item.get("name"))
        value = "—"
        if _to_number(item.get("value_per_sf")) is not None:
            value = _format_money_per_sf(item.get("value_per_sf"))
        elif _to_number(item.get("value")) is not None:
            value = _format_money(item.get("value"))
        elif _to_number(item.get("multiplier")) is not None:
            value = f"{_format_number(item.get('multiplier'), 2)}x"
        if not label and value == "—":
            continue
        rows.append(
            "<tr>"
            f"<td>{html_module.escape(label or 'Line item')}</td>"
            f"<td>{html_module.escape(value)}</td>"
            "</tr>"
        )

    if not rows:
        return ""

    return (
        "<section>"
        "<h2>Cost Build-Up Analysis</h2>"
        "<table class=\"simple-table\">"
        "<thead><tr><th>Line Item</th><th>Modeled Value</th></tr></thead>"
        "<tbody>"
        + "".join(rows)
        + "</tbody></table>"
        "</section>"
    )


def _render_schedule(section: Dict[str, Any]) -> str:
    phases = [phase for phase in _as_list(section.get("phases")) if isinstance(phase, dict)]
    milestones = [item for item in _as_list(section.get("milestones")) if isinstance(item, dict)]
    total_months = _format_months(section.get("total_months"))

    phase_rows = []
    for phase in phases[:8]:
        phase_rows.append(
            "<tr>"
            f"<td>{_escape(phase.get('label') or phase.get('id') or 'Phase')}</td>"
            f"<td>{html_module.escape(_format_number(phase.get('start_month')))}</td>"
            f"<td>{html_module.escape(_format_number(phase.get('duration_months')))}</td>"
            "</tr>"
        )

    milestone_items = []
    for milestone in milestones[:4]:
        milestone_items.append(
            "<li>"
            f"<strong>{_escape(milestone.get('label') or 'Milestone')}</strong>"
            f"<span class=\"list-detail\">{_escape(milestone.get('date_label') or 'TBD')}</span>"
            "</li>"
        )

    overview_html = (
        f"<div class=\"note-block schedule-overview\"><strong>Modeled duration:</strong> {html_module.escape(total_months)}</div>"
        if total_months != "—"
        else ""
    )

    layout_parts: List[str] = []
    if phase_rows:
        layout_parts.append(
            "<div class=\"subsection\">"
            "<h3>Phases</h3>"
            "<table class=\"simple-table schedule-table\">"
            "<thead><tr><th>Phase</th><th>Start Month</th><th>Duration</th></tr></thead>"
            "<tbody>"
            + "".join(phase_rows)
            + "</tbody></table>"
            "</div>"
        )
    if milestone_items:
        layout_parts.append(
            "<div class=\"subsection\">"
            "<h3>Key Milestones</h3>"
            "<ul class=\"bullet-list milestone-list\">"
            + "".join(milestone_items)
            + "</ul>"
            "</div>"
        )

    if not overview_html and not layout_parts:
        return ""

    layout_html = (
        "<div class=\"schedule-layout\">"
        + "".join(layout_parts)
        + "</div>"
        if layout_parts
        else ""
    )

    return (
        "<section class=\"schedule-section\">"
        "<h2>Schedule + Key Milestones</h2>"
        + overview_html
        + layout_html
        + "</section>"
    )


def _render_most_likely_wrong(items: List[Any]) -> str:
    if not items:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Most Likely Wrong:</strong> Not configured for this packet."
            "</div>"
        )

    rendered = []
    for entry in items[:5]:
        item = _as_dict(entry)
        label = _sanitize_text(item.get("text") or item.get("id"))
        if not label:
            continue
        why = _sanitize_text(item.get("why"))
        rendered.append(
            "<li>"
            f"<strong>{html_module.escape(label)}</strong>"
            + (
                f"<div class=\"list-detail\">Why: {html_module.escape(why)}</div>"
                if why
                else ""
            )
            + "</li>"
        )
    if not rendered:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Most Likely Wrong:</strong> Not configured for this packet."
            "</div>"
        )
    return (
        "<section><h2>Most Likely Wrong</h2>"
        "<ul class=\"bullet-list\">"
        + "".join(rendered)
        + "</ul></section>"
    )


def _render_question_bank(items: List[Any]) -> str:
    if not items:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Question Bank:</strong> Not configured for this packet."
            "</div>"
        )

    rendered_groups = []
    for entry in items:
        item = _as_dict(entry)
        questions = [q for q in _as_list(item.get("questions")) if _sanitize_text(q)]
        if not questions:
            continue
        label = _resolve_question_bank_label(item)
        question_lines = "".join(f"<li>{_escape(question)}</li>" for question in questions)
        rendered_groups.append(
            "<div class=\"question-bank-group\">"
            f"<h3 class=\"question-bank-group-title\">{html_module.escape(label)}</h3>"
            "<ul class=\"bullet-list compact nested\">"
            + question_lines
            + "</ul></div>"
        )
    if not rendered_groups:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Question Bank:</strong> Not configured for this packet."
            "</div>"
        )
    return (
        "<section><h2>Question Bank</h2>"
        "<div class=\"content-subtle\">Focused diligence questions to pressure-test the modeled decision before capital is committed.</div>"
        "<div class=\"question-bank-groups\">"
        + "".join(rendered_groups)
        + "</div></section>"
    )


def _render_red_flags_actions(items: List[Any]) -> str:
    if not items:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Red Flags + Actions:</strong> Not configured for this packet."
            "</div>"
        )

    rendered = []
    for entry in items[:8]:
        item = _as_dict(entry)
        flag = _sanitize_text(item.get("flag"))
        action = _sanitize_text(item.get("action"))
        if not flag and not action:
            continue
        rendered.append(
            "<li>"
            + (
                f"<strong>{html_module.escape(flag)}</strong>"
                if flag
                else ""
            )
            + (
                f"<div class=\"list-detail\">Action: {html_module.escape(action)}</div>"
                if action
                else ""
            )
            + "</li>"
        )
    if not rendered:
        return (
            "<div class=\"content-subtle\">"
            "<strong>Red Flags + Actions:</strong> Not configured for this packet."
            "</div>"
        )
    return (
        "<section><h2>Red Flags + Actions</h2>"
        "<ul class=\"bullet-list\">"
        + "".join(rendered)
        + "</ul></section>"
    )


def _render_provenance(section: Dict[str, Any]) -> str:
    rows = [
        ("Tile Profile", _sanitize_text(section.get("profile_id")) or "—"),
        ("Content Profile", _sanitize_text(section.get("content_profile_id")) or "—"),
        ("Scope Items Profile", _sanitize_text(section.get("scope_items_profile_id")) or "—"),
        ("Decision Status", _sanitize_text(section.get("decision_status")) or "—"),
        ("Decision Reason", _sanitize_text(section.get("decision_reason_code")) or "—"),
    ]
    base_inputs = _as_dict(_as_dict(section.get("scenario_inputs")).get("base"))
    control_inputs = _as_dict(section.get("dealshield_controls"))

    base_input_rows = []
    for key in sorted(base_inputs.keys()):
        value = base_inputs.get(key)
        if isinstance(value, (dict, list)):
            continue
        text = _sanitize_text(value)
        if not text:
            continue
        base_input_rows.append(
            "<tr>"
            f"<td>{html_module.escape(key)}</td>"
            f"<td>{html_module.escape(text)}</td>"
            "</tr>"
        )

    control_rows = []
    for key in sorted(control_inputs.keys()):
        value = control_inputs.get(key)
        if isinstance(value, (dict, list)):
            continue
        text = _sanitize_text(value)
        if not text:
            continue
        control_rows.append(
            "<tr>"
            f"<td>{html_module.escape(key)}</td>"
            f"<td>{html_module.escape(text)}</td>"
            "</tr>"
        )

    info_grid = (
        "<div class=\"info-grid\">"
        + "".join(
            "<div class=\"info-item\">"
            f"<span class=\"info-label\">{html_module.escape(label)}</span>"
            f"<span class=\"info-value\">{html_module.escape(value)}</span>"
            "</div>"
            for label, value in rows
        )
        + "</div>"
    )

    base_html = (
        "<div class=\"subsection\"><h3>Scenario Inputs (Base)</h3>"
        "<table class=\"simple-table\"><tbody>"
        + "".join(base_input_rows)
        + "</tbody></table></div>"
        if base_input_rows
        else ""
    )
    controls_html = (
        "<div class=\"subsection\"><h3>DealShield Controls</h3>"
        "<table class=\"simple-table\"><tbody>"
        + "".join(control_rows)
        + "</tbody></table></div>"
        if control_rows
        else ""
    )

    return (
        "<section>"
        "<h2>Provenance / Receipt / References Used</h2>"
        + info_grid
        + base_html
        + controls_html
        + "</section>"
    )


def render_decision_packet_html(packet: Dict[str, Any]) -> str:
    cover_summary = _as_dict(packet.get("cover_summary"))
    decision_banner = _as_dict(packet.get("decision_banner"))
    key_metrics = _as_dict(packet.get("key_metrics"))
    decision_insurance = _as_dict(packet.get("decision_insurance"))
    decision_metrics_table = _as_dict(packet.get("decision_metrics_table"))
    assumptions_not_modeled = _as_dict(packet.get("assumptions_not_modeled"))
    economics_snapshot = _as_dict(packet.get("economics_snapshot"))
    revenue_required = _as_dict(packet.get("revenue_required"))
    construction_summary = _as_dict(packet.get("construction_summary"))
    trade_distribution = _as_dict(packet.get("trade_distribution"))
    cost_build_up = _as_dict(packet.get("cost_build_up"))
    schedule_milestones = _as_dict(packet.get("schedule_milestones"))
    trust_sections = _as_dict(packet.get("trust_sections"))
    provenance = _as_dict(packet.get("provenance"))

    metric_cards = [
        _format_metric("Total Cost", _format_money(key_metrics.get("total_project_cost"))),
        _format_metric("Yield on Cost", _format_percent(key_metrics.get("yield_on_cost"))),
        _format_metric("DSCR", _format_ratio(key_metrics.get("dscr"))),
        _format_metric("Annual Revenue", _format_money(key_metrics.get("annual_revenue"))),
        _format_metric("Annual NOI", _format_money(key_metrics.get("annual_noi"))),
    ]

    trust_html = (
        _render_most_likely_wrong(_as_list(trust_sections.get("most_likely_wrong")))
        + _render_question_bank(_as_list(trust_sections.get("question_bank")))
        + _render_red_flags_actions(_as_list(trust_sections.get("red_flags_actions")))
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{_escape(cover_summary.get("project_name") or "SpecSharp Decision Packet")}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Liberation Sans", "DejaVu Sans", Arial, Helvetica, sans-serif;
      color: #0f172a;
      background: #f8fafc;
      line-height: 1.45;
    }}
    .page {{
      max-width: 980px;
      margin: 0 auto;
      padding: 34px 28px 24px;
      background: #ffffff;
    }}
    .page-break {{
      page-break-before: always;
    }}
    h1 {{
      margin: 0 0 14px;
      font-size: 32px;
      line-height: 1.1;
      color: #0f172a;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 20px;
      line-height: 1.2;
      color: #0f172a;
    }}
    h3 {{
      margin: 0 0 10px;
      font-size: 14px;
      color: #1e293b;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }}
    section {{
      margin-bottom: 24px;
      padding: 18px 18px 16px;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      background: #ffffff;
    }}
    section > * + * {{
      margin-top: 12px;
    }}
    section > h2 + * {{
      margin-top: 0;
    }}
    .subsection {{
      margin-top: 16px;
    }}
    .subsection:first-of-type {{
      margin-top: 0;
    }}
    .subsection > * + * {{
      margin-top: 10px;
    }}
    .eyebrow {{
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: #475569;
      margin-bottom: 10px;
    }}
    .cover-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px 16px;
    }}
    .cover-row {{
      display: flex;
      flex-direction: column;
      padding: 10px 12px;
      border-radius: 10px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
    }}
    .cover-label, .metric-label, .info-label {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #64748b;
      line-height: 1.35;
    }}
    .cover-value, .metric-value, .info-value {{
      margin-top: 5px;
      font-size: 17px;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.25;
    }}
    .decision-banner {{
      border-width: 2px;
      padding: 18px;
    }}
    .status-go {{ border-color: #16a34a; background: #f0fdf4; }}
    .status-no-go {{ border-color: #dc2626; background: #fef2f2; }}
    .status-needs-work {{ border-color: #d97706; background: #fffbeb; }}
    .status-pending {{ border-color: #475569; background: #f8fafc; }}
    .decision-status-chip {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: #0f172a;
      color: #ffffff;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }}
    .decision-reason, .banner-detail, .banner-basis, .metric-detail, .subcard-detail, .list-detail, .content-subtle {{
      font-size: 11px;
      color: #475569;
      line-height: 1.55;
      margin-top: 0;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric-card, .info-item, .subcard {{
      display: flex;
      flex-direction: column;
      gap: 6px;
      padding: 13px 14px;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      background: #f8fafc;
    }}
    .subcard-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 14px;
    }}
    .subcard-title {{
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #64748b;
      margin-bottom: 0;
    }}
    .subcard-value {{
      font-size: 17px;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.25;
    }}
    .info-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .two-column {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      border-bottom: 1px solid #e2e8f0;
      padding: 10px 12px;
      text-align: left;
      vertical-align: top;
      font-size: 12px;
      line-height: 1.45;
    }}
    th {{
      font-size: 11px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #475569;
      background: #f8fafc;
    }}
    .decision-table, .simple-table {{
      margin-top: 6px;
    }}
    .decision-table th, .decision-table td {{
      padding: 12px 14px;
    }}
    .decision-table thead th {{
      font-size: 10px;
      letter-spacing: 0.06em;
    }}
    .decision-table tbody tr:nth-child(even) {{
      background: #fbfdff;
    }}
    .simple-table thead th {{
      font-size: 10px;
      letter-spacing: 0.05em;
    }}
    .row-label {{
      white-space: nowrap;
      color: #0f172a;
    }}
    .bullet-list {{
      margin: 0;
      padding-left: 20px;
    }}
    .bullet-list.compact {{
      margin-top: 6px;
    }}
    .bullet-list.nested {{
      margin-top: 6px;
    }}
    .bullet-list li {{
      margin-bottom: 8px;
      line-height: 1.5;
    }}
    .question-bank-groups {{
      display: grid;
      gap: 12px;
      margin-top: 12px;
    }}
    .question-bank-group {{
      padding: 14px 16px;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      background: #f8fafc;
    }}
    .question-bank-group-title {{
      margin: 0 0 8px;
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: none;
      color: #0f172a;
    }}
    .note-block {{
      margin: 0;
      padding: 12px 14px;
      border-radius: 10px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      font-size: 12px;
      color: #334155;
      line-height: 1.55;
    }}
    .empty-note {{
      font-size: 12px;
      color: #64748b;
    }}
    .schedule-section .schedule-overview {{
      max-width: 280px;
    }}
    .schedule-layout {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 22px;
      align-items: start;
    }}
    .schedule-layout .subsection {{
      margin-top: 0;
    }}
    .schedule-table th:first-child,
    .schedule-table td:first-child {{
      width: 52%;
    }}
    .milestone-list {{
      display: grid;
      gap: 8px;
      padding-left: 20px;
    }}
    .milestone-list li {{
      margin-bottom: 0;
    }}
  </style>
</head>
<body>
  <div class="page">
    {_render_cover_summary(cover_summary)}
    {_render_decision_banner(decision_banner)}
  </div>

  <div class="page page-break">
    <section>
      <h2>Key Metrics Strip</h2>
      {_render_metric_grid(metric_cards)}
    </section>
    {_render_decision_insurance(decision_insurance, provenance)}
    {_render_decision_metrics_table(decision_metrics_table)}
  </div>

  <div class="page page-break">
    {_render_assumptions(assumptions_not_modeled)}
    {_render_economics_snapshot(economics_snapshot)}
  </div>

  <div class="page page-break">
    {_render_revenue_required(revenue_required)}
    {_render_construction_summary(construction_summary)}
    {_render_trade_distribution(trade_distribution)}
  </div>

  <div class="page page-break">
    {_render_schedule(schedule_milestones)}
    {_render_cost_build_up(cost_build_up)}
    {trust_html}
  </div>

  <div class="page page-break">
    {_render_provenance(provenance)}
  </div>
</body>
</html>
"""
