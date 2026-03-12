from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.utils.formatting import format_currency, format_percentage


_SEVERITY_RANK = {
    "high": 3,
    "moderate": 2,
    "low": 1,
}

_DRIVER_PRIORITY = {
    "contingency_adequacy": 1,
    "critical_systems_scope_burden": 2,
    "trade_procurement_concentration": 3,
    "regional_cost_pressure": 4,
}

_ALWAYS_ON_CRITICAL_SCOPE_FAMILIES = {
    ("specialty", "data_center"),
    ("industrial", "cold_storage"),
    ("hospitality", "full_service_hotel"),
}

_SELECTIVE_CRITICAL_SCOPE_FAMILIES = {
    ("restaurant", "full_service"),
    ("restaurant", "fine_dining"),
    ("industrial", "flex_space"),
}


def _to_number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or value is None:
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


def _format_ratio_pct(value: float) -> str:
    return format_percentage(value * 100.0, 1)


def _titleize_trade(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "Trade"
    return value.strip().replace("_", " ").replace("-", " ").title()


def _normalize_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(ch for ch in value.strip().lower() if ch.isalnum())


def _join_labels(labels: Sequence[str], *, limit: int = 2) -> str:
    unique_labels: List[str] = []
    seen = set()
    for label in labels:
        if not isinstance(label, str):
            continue
        cleaned = label.strip()
        if not cleaned:
            continue
        marker = cleaned.lower()
        if marker in seen:
            continue
        seen.add(marker)
        unique_labels.append(cleaned)

    if not unique_labels:
        return ""

    clipped = unique_labels[: max(1, limit)]
    if len(clipped) == 1:
        return clipped[0]
    if len(clipped) == 2:
        return f"{clipped[0]} and {clipped[1]}"
    return f"{', '.join(clipped[:-1])}, and {clipped[-1]}"


def _combine_sources(*source_values: str) -> str:
    ordered: List[str] = []
    seen = set()
    for source_value in source_values:
        if not source_value:
            continue
        for raw_item in str(source_value).split(","):
            item = raw_item.strip()
            if not item or item in seen:
                continue
            seen.add(item)
            ordered.append(item)
    return ",".join(ordered)


def _resolve_trade_key(value: Any) -> Optional[str]:
    normalized = _normalize_key(value)
    if not normalized:
        return None
    if "structural" in normalized:
        return "structural"
    if "mechanical" in normalized:
        return "mechanical"
    if "electrical" in normalized:
        return "electrical"
    if "plumbing" in normalized:
        return "plumbing"
    if "finish" in normalized:
        return "finishes"
    return None


def _extract_scope_signals(payload: Dict[str, Any], construction_total: float) -> Dict[str, Any]:
    scope_items = payload.get("scope_items")
    systems_by_trade: Dict[str, List[Dict[str, Any]]] = {}
    flattened_systems: List[Dict[str, Any]] = []

    if not isinstance(scope_items, list):
        return {
            "systems_by_trade": systems_by_trade,
            "flattened_systems": flattened_systems,
            "top_scope_systems": [],
            "top_two_scope_share": 0.0,
        }

    for trade_entry in scope_items:
        if not isinstance(trade_entry, dict):
            continue
        trade_key = _resolve_trade_key(trade_entry.get("trade"))
        systems = trade_entry.get("systems")
        if not trade_key or not isinstance(systems, list):
            continue

        trade_bucket: List[Dict[str, Any]] = []
        for system in systems:
            if not isinstance(system, dict):
                continue
            name = str(system.get("name") or "").strip()
            total_cost = _to_number(system.get("total_cost"))
            if not name or total_cost is None or total_cost <= 0:
                continue

            system_payload = {
                "trade_key": trade_key,
                "name": name,
                "total_cost": total_cost,
                "share_of_construction": (
                    total_cost / construction_total if construction_total > 0 else 0.0
                ),
            }
            trade_bucket.append(system_payload)
            flattened_systems.append(system_payload)

        if trade_bucket:
            trade_bucket.sort(key=lambda item: item["total_cost"], reverse=True)
            systems_by_trade[trade_key] = trade_bucket

    flattened_systems.sort(key=lambda item: item["total_cost"], reverse=True)
    top_scope_systems = flattened_systems[:3]
    top_two_scope_share = sum(
        float(item.get("share_of_construction", 0.0) or 0.0)
        for item in flattened_systems[:2]
    )

    return {
        "systems_by_trade": systems_by_trade,
        "flattened_systems": flattened_systems,
        "top_scope_systems": top_scope_systems,
        "top_two_scope_share": top_two_scope_share,
    }


def _extract_special_feature_signals(payload: Dict[str, Any], construction_total: float) -> Dict[str, Any]:
    construction_costs = payload.get("construction_costs")
    if not isinstance(construction_costs, dict):
        return {
            "features": [],
            "special_features_total": 0.0,
            "special_feature_share": 0.0,
        }

    breakdown = construction_costs.get("special_features_breakdown")
    features: List[Dict[str, Any]] = []

    if isinstance(breakdown, list):
        for row in breakdown:
            if not isinstance(row, dict):
                continue
            label = str(row.get("label") or row.get("id") or "").strip()
            total_cost = _to_number(row.get("total_cost"))
            if not label or total_cost is None or total_cost <= 0:
                continue
            features.append(
                {
                    "label": label,
                    "total_cost": total_cost,
                    "pricing_status": str(row.get("pricing_status") or "").strip(),
                    "share_of_construction": (
                        total_cost / construction_total if construction_total > 0 else 0.0
                    ),
                }
            )

    features.sort(key=lambda item: item["total_cost"], reverse=True)
    special_features_total = _to_number(construction_costs.get("special_features_total"))
    if special_features_total is None:
        special_features_total = sum(item["total_cost"] for item in features)

    return {
        "features": features,
        "special_features_total": max(0.0, float(special_features_total or 0.0)),
        "special_feature_share": (
            max(0.0, float(special_features_total or 0.0)) / construction_total
            if construction_total > 0
            else 0.0
        ),
    }


def _build_driver_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    project_info = payload.get("project_info")
    construction_costs = payload.get("construction_costs")
    soft_costs = payload.get("soft_costs")
    regional = payload.get("regional")
    trade_breakdown = payload.get("trade_breakdown")

    has_project_info = isinstance(project_info, dict)
    has_construction_costs = isinstance(construction_costs, dict)
    has_soft_costs = isinstance(soft_costs, dict)
    has_regional = isinstance(regional, dict)
    has_trade_breakdown = isinstance(trade_breakdown, dict)

    if not has_project_info:
        project_info = {}
    if not has_construction_costs:
        construction_costs = {}
    if not has_soft_costs:
        soft_costs = {}
    if not has_regional:
        regional = {}
    if not has_trade_breakdown:
        trade_breakdown = {}

    construction_total = _to_number(construction_costs.get("construction_total")) or 0.0
    equipment_total = _to_number(construction_costs.get("equipment_total")) or 0.0
    contingency_amount = _to_number(soft_costs.get("contingency"))

    regional_multiplier = _to_number(construction_costs.get("regional_multiplier"))
    regional_source = "construction_costs.regional_multiplier" if regional_multiplier is not None else ""
    if regional_multiplier is None:
        regional_multiplier = _to_number(regional.get("multiplier"))
        if regional_multiplier is not None:
            regional_source = "regional.multiplier"

    location_display = regional.get("location_display")
    if not isinstance(location_display, str) or not location_display.strip():
        if isinstance(project_info.get("location"), str):
            location_display = project_info["location"]
        else:
            location_display = "This market"

    top_trades: List[Dict[str, Any]] = []
    for trade_key, amount_raw in trade_breakdown.items():
        amount = _to_number(amount_raw)
        if amount is None or amount <= 0:
            continue
        top_trades.append(
            {
                "key": str(trade_key),
                "label": _titleize_trade(trade_key),
                "amount": amount,
                "share_of_construction": (
                    amount / construction_total if construction_total > 0 else 0.0
                ),
            }
        )
    top_trades.sort(key=lambda item: item["amount"], reverse=True)

    scope_signals = _extract_scope_signals(payload, construction_total)
    special_feature_signals = _extract_special_feature_signals(payload, construction_total)

    return {
        "has_construction_costs": has_construction_costs,
        "has_soft_costs": has_soft_costs,
        "building_type": str(project_info.get("building_type") or "").strip().lower(),
        "subtype": str(project_info.get("subtype") or "").strip().lower(),
        "location_display": location_display,
        "construction_total": construction_total,
        "contingency_amount": contingency_amount,
        "equipment_total": equipment_total,
        "equipment_share": (
            equipment_total / construction_total if construction_total > 0 else 0.0
        ),
        "regional_multiplier": regional_multiplier,
        "regional_source": regional_source,
        "top_trades": top_trades,
        **scope_signals,
        **special_feature_signals,
    }


def _get_trade_scope_labels(context: Dict[str, Any], trade_keys: Sequence[str], *, limit: int = 2) -> str:
    systems_by_trade = context.get("systems_by_trade")
    if not isinstance(systems_by_trade, dict):
        return ""

    labels: List[str] = []
    for trade_key in trade_keys:
        systems = systems_by_trade.get(str(trade_key))
        if not isinstance(systems, list) or not systems:
            continue
        top_system = systems[0]
        if isinstance(top_system, dict) and isinstance(top_system.get("name"), str):
            labels.append(top_system["name"])

    return _join_labels(labels, limit=limit)


def _build_contingency_context_details(context: Dict[str, Any]) -> Dict[str, Any]:
    detail_cards: List[Dict[str, Any]] = []
    building_type = str(context.get("building_type") or "")
    family_key = (building_type, str(context.get("subtype") or ""))

    top_scope_systems = context.get("top_scope_systems")
    if not isinstance(top_scope_systems, list):
        top_scope_systems = []

    special_features = context.get("features")
    if not isinstance(special_features, list):
        special_features = []

    special_feature_share = float(context.get("special_feature_share", 0.0) or 0.0)
    if special_feature_share >= 0.03 and special_features:
        feature_labels = _join_labels([item.get("label", "") for item in special_features], limit=2)
        detail_cards.append(
            {
                "why": (
                    f"Selected specialty scope already adds {format_currency(context['special_features_total'])} "
                    f"across {feature_labels}."
                ),
                "evidence": (
                    f"Selected specialty scope: {format_currency(context['special_features_total'])} "
                    f"across {feature_labels}."
                ),
                "verify": f"Check whether that buffer already needs to cover {feature_labels}.",
                "source": "construction_costs.special_features_breakdown",
            }
        )

    equipment_share = float(context.get("equipment_share", 0.0) or 0.0)
    if equipment_share >= 0.12:
        detail_cards.append(
            {
                "why": (
                    f"Equipment allowances add {format_currency(context['equipment_total'])} "
                    "beyond core construction."
                ),
                "evidence": f"Equipment allowance: {format_currency(context['equipment_total'])}.",
                "verify": (
                    "Check whether equipment and specialty-system assumptions are already consuming part "
                    "of the remaining buffer."
                ),
                "source": "construction_costs.equipment_total",
            }
        )

    top_two_scope_share = float(context.get("top_two_scope_share", 0.0) or 0.0)
    if top_two_scope_share >= 0.18 and (
        building_type == "healthcare"
        or family_key in _ALWAYS_ON_CRITICAL_SCOPE_FAMILIES
        or special_feature_share >= 0.03
    ):
        lead_systems = _join_labels([item.get("name", "") for item in top_scope_systems], limit=2)
        if lead_systems:
            detail_cards.append(
                {
                    "why": f"The current scope model is led by {lead_systems}.",
                    "evidence": (
                        f"Lead systems: {lead_systems} "
                        f"({_format_ratio_pct(top_two_scope_share)} of core construction)."
                    ),
                    "verify": (
                        f"Confirm whether performance or owner-standard decisions inside {lead_systems} "
                        "are still open."
                    ),
                    "source": "scope_items",
                }
            )

    return {
        "details": detail_cards[:2],
    }


def _build_contingency_driver(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not bool(context.get("has_construction_costs")) or not bool(context.get("has_soft_costs")):
        return None

    contingency_amount = _to_number(context.get("contingency_amount"))
    construction_total = _to_number(context.get("construction_total"))
    if contingency_amount is None or construction_total is None or construction_total <= 0:
        return None

    contingency_pct = contingency_amount / construction_total
    contingency_pct_display = _format_ratio_pct(contingency_pct)
    detail_cards = _build_contingency_context_details(context).get("details", [])

    if contingency_pct < 0.06:
        severity = "high"
        why = (
            f"Contingency is {contingency_pct_display} of core construction, "
            "which leaves limited room for scope growth, buyout drift, or late package resets."
        )
    elif contingency_pct < 0.08:
        severity = "moderate"
        why = (
            f"Contingency is {contingency_pct_display} of core construction. "
            "That is workable, but buffer can tighten quickly if open scope or package pricing moves."
        )
    else:
        severity = "low"
        why = (
            f"Contingency is {contingency_pct_display} of core construction, "
            "which provides a more durable buffer against typical scope movement."
        )

    evidence_parts = [
        f"Contingency: {contingency_pct_display} of {format_currency(construction_total)} core construction."
    ]
    verify_next = (
        "Confirm what is still truly uncommitted, what is already absorbing scope decisions, "
        "and who controls release of the remaining contingency."
    )
    source = "soft_costs.contingency,construction_costs.construction_total"

    for detail in detail_cards:
        if not isinstance(detail, dict):
            continue
        detail_why = str(detail.get("why") or "").strip()
        if detail_why:
            why = f"{why} {detail_why}"
        evidence = str(detail.get("evidence") or "").strip()
        if evidence:
            evidence_parts.append(evidence)
        verify_detail = str(detail.get("verify") or "").strip()
        if verify_detail:
            verify_next = f"{verify_next} {verify_detail}"
        source = _combine_sources(source, str(detail.get("source") or ""))

    return {
        "id": "contingency_adequacy",
        "title": "Contingency Adequacy",
        "severity": severity,
        "why_this_is_showing": why.strip(),
        "affects": ["basis", "cost_confidence"],
        "verify_next": verify_next.strip(),
        "evidence_summary": " ".join(evidence_parts).strip(),
        "source": source,
        "status": "supported",
    }


def _build_trade_procurement_driver(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    top_trades = context.get("top_trades")
    if not isinstance(top_trades, list) or not top_trades:
        return None

    primary = top_trades[0]
    secondary = top_trades[1] if len(top_trades) > 1 else None
    primary_share = float(primary.get("share_of_construction", 0.0) or 0.0)
    combined_share = primary_share + float(
        secondary.get("share_of_construction", 0.0) if isinstance(secondary, dict) else 0.0
    )
    combined_share_display = _format_ratio_pct(combined_share)
    secondary_label = f" and {secondary['label']}" if isinstance(secondary, dict) else ""

    if primary_share >= 0.35 or combined_share >= 0.65:
        severity = "high"
        why = (
            f"{primary['label']}"
            f"{secondary_label} account for {combined_share_display} "
            "of core construction, so a small set of packages drives buyout concentration and basis sensitivity."
        )
    elif combined_share >= 0.55:
        severity = "moderate"
        why = (
            f"{primary['label']}"
            f"{secondary_label} account for {combined_share_display} "
            "of core construction, so cost confidence depends on a limited number of packages."
        )
    else:
        severity = "low"
        why = (
            f"The two largest packages account for {combined_share_display} of core construction, "
            "so package concentration is more distributed across trades."
        )

    lead_systems = ""
    if combined_share >= 0.55:
        trade_keys = [str(primary.get("key") or "")]
        if isinstance(secondary, dict):
            trade_keys.append(str(secondary.get("key") or ""))
        lead_systems = _get_trade_scope_labels(context, trade_keys)
        if lead_systems:
            why = (
                f"{why} The modeled scope inside those packages is led by {lead_systems}."
            )

    evidence_parts = [
        f"{primary['label']} {_format_ratio_pct(primary_share)}",
    ]
    if isinstance(secondary, dict):
        evidence_parts.append(
            f"{secondary['label']} {_format_ratio_pct(float(secondary.get('share_of_construction', 0.0) or 0.0))}"
        )

    verify_target = f"{primary['label']}{secondary_label}"
    verify_next = (
        f"Pressure-test the current basis against {verify_target} and confirm where scope definition "
        "or pricing could still move."
    )
    evidence_summary = (
        f"Top packages: {', '.join(evidence_parts)} ({combined_share_display} combined)."
    )
    source = "trade_breakdown"

    if lead_systems:
        verify_next = (
            f"Pressure-test the current basis against {verify_target}, especially {lead_systems}, "
            "and confirm where scope definition or owner standards could still move."
        )
        evidence_summary = f"{evidence_summary} Lead systems: {lead_systems}."
        source = _combine_sources(source, "scope_items")

    return {
        "id": "trade_procurement_concentration",
        "title": "Trade / Package Concentration",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["cost_confidence", "procurement", "schedule"],
        "verify_next": verify_next,
        "evidence_summary": evidence_summary,
        "source": source,
        "status": "supported",
    }


def _build_regional_cost_pressure_driver(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not bool(context.get("has_construction_costs")):
        return None

    multiplier = _to_number(context.get("regional_multiplier"))
    source = str(context.get("regional_source") or "")
    if multiplier is None or multiplier <= 1.05:
        return None

    location_display = str(context.get("location_display") or "This market")
    construction_total = _to_number(context.get("construction_total"))
    delta_pct_display = format_percentage((multiplier - 1.0) * 100.0, 1)
    uplift_amount = None
    if construction_total is not None and construction_total > 0 and multiplier > 0:
        uplift_amount = construction_total - (construction_total / multiplier)

    if uplift_amount is not None and uplift_amount > 0:
        why_suffix = (
            f" which embeds roughly {format_currency(uplift_amount)} of regional pricing pressure "
            "in the current core construction basis."
        )
    elif multiplier >= 1.15:
        why_suffix = (
            " which can compress pricing tolerance and reduce room for scope movement."
        )
    else:
        why_suffix = " adding upward pressure to local pricing and procurement assumptions."

    if multiplier >= 1.15:
        severity = "high"
    else:
        severity = "moderate"

    why = (
        f"{location_display} is {delta_pct_display} above the national construction-cost baseline,"
        f"{why_suffix}"
    )

    evidence_summary = f"Regional construction multiplier: {multiplier:.2f}x vs 1.00 baseline."
    if uplift_amount is not None and uplift_amount > 0 and construction_total is not None:
        evidence_summary = (
            f"{evidence_summary} Location-driven uplift: {format_currency(uplift_amount)} "
            f"on {format_currency(construction_total)} core construction."
        )
        source = _combine_sources(source, "construction_costs.construction_total")

    return {
        "id": "regional_cost_pressure",
        "title": "Regional Cost Pressure",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["basis", "cost_confidence", "procurement"],
        "verify_next": (
            "Confirm current subcontractor pricing, freight/logistics assumptions, "
            "and any escalation coverage against the regional premium already embedded in the basis."
        ),
        "evidence_summary": evidence_summary,
        "source": source or "regional.multiplier",
        "status": "supported",
    }


def _should_emit_critical_systems_driver(context: Dict[str, Any]) -> bool:
    building_type = str(context.get("building_type") or "")
    subtype = str(context.get("subtype") or "")
    family_key = (building_type, subtype)
    top_scope_systems = context.get("top_scope_systems")
    if not isinstance(top_scope_systems, list) or len(top_scope_systems) < 2:
        return False

    equipment_share = float(context.get("equipment_share", 0.0) or 0.0)
    special_feature_share = float(context.get("special_feature_share", 0.0) or 0.0)
    top_two_scope_share = float(context.get("top_two_scope_share", 0.0) or 0.0)

    if building_type == "healthcare":
        return (
            equipment_share >= 0.10
            or top_two_scope_share >= 0.14
            or special_feature_share >= 0.02
        )

    if family_key in _ALWAYS_ON_CRITICAL_SCOPE_FAMILIES:
        if family_key == ("specialty", "data_center"):
            return (
                equipment_share >= 0.18
                or top_two_scope_share >= 0.18
                or special_feature_share >= 0.02
            )
        if family_key == ("industrial", "cold_storage"):
            return (
                equipment_share >= 0.15
                or top_two_scope_share >= 0.18
                or special_feature_share >= 0.02
            )
        return (
            equipment_share >= 0.10
            or top_two_scope_share >= 0.12
            or special_feature_share >= 0.02
        )

    if family_key in _SELECTIVE_CRITICAL_SCOPE_FAMILIES:
        if family_key == ("industrial", "flex_space"):
            return special_feature_share >= 0.03 and top_two_scope_share >= 0.16
        return special_feature_share >= 0.02 and top_two_scope_share >= 0.16

    return False


def _build_critical_systems_driver(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not _should_emit_critical_systems_driver(context):
        return None

    top_scope_systems = context["top_scope_systems"]
    lead_systems_text = _join_labels([item.get("name", "") for item in top_scope_systems], limit=2)
    lead_scope_share = float(context.get("top_two_scope_share", 0.0) or 0.0)
    equipment_share = float(context.get("equipment_share", 0.0) or 0.0)
    special_feature_share = float(context.get("special_feature_share", 0.0) or 0.0)

    if equipment_share >= 0.20 or lead_scope_share >= 0.20 or special_feature_share >= 0.05:
        severity = "high"
    else:
        severity = "moderate"

    why = (
        f"A meaningful share of the current basis sits in critical systems and specialty scope, "
        f"led by {lead_systems_text}."
    )
    evidence_parts = [
        f"Lead systems: {lead_systems_text} ({_format_ratio_pct(lead_scope_share)} of core construction)."
    ]
    verify_next = (
        f"Confirm the owner-standard, performance, and interface assumptions inside {lead_systems_text}, "
        "and confirm those systems are fully reflected in the current basis."
    )
    source = "scope_items"

    special_features = context.get("features")
    if not isinstance(special_features, list):
        special_features = []

    if special_feature_share >= 0.02 and special_features:
        feature_labels = _join_labels([item.get("label", "") for item in special_features], limit=2)
        why = (
            f"{why} Selected specialty scope adds {format_currency(context['special_features_total'])} "
            f"across {feature_labels}."
        )
        evidence_parts.append(
            f"Selected specialty scope: {feature_labels} ({format_currency(context['special_features_total'])})."
        )
        verify_next = (
            f"Confirm the owner-standard, performance, and interface assumptions inside {lead_systems_text}, "
            "and confirm the selected specialty scope is fully reflected in the current basis."
        )
        source = _combine_sources(source, "construction_costs.special_features_breakdown")

    if equipment_share >= 0.10:
        why = (
            f"{why} Equipment allowances add {format_currency(context['equipment_total'])} "
            "beyond core construction."
        )
        evidence_parts.append(
            f"Equipment allowance: {format_currency(context['equipment_total'])}."
        )
        source = _combine_sources(source, "construction_costs.equipment_total")

    return {
        "id": "critical_systems_scope_burden",
        "title": "Critical Systems / Specialty Scope Burden",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["basis", "cost_confidence", "schedule"],
        "verify_next": verify_next,
        "evidence_summary": " ".join(evidence_parts),
        "source": source,
        "status": "supported",
    }


def build_construction_risk_drivers(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    context = _build_driver_context(payload)
    drivers = [
        driver
        for driver in (
            _build_contingency_driver(context),
            _build_critical_systems_driver(context),
            _build_trade_procurement_driver(context),
            _build_regional_cost_pressure_driver(context),
        )
        if isinstance(driver, dict)
    ]

    drivers.sort(
        key=lambda driver: (
            -_SEVERITY_RANK.get(str(driver.get("severity")), 0),
            _DRIVER_PRIORITY.get(str(driver.get("id")), 99),
            str(driver.get("id")),
        )
    )
    return drivers
