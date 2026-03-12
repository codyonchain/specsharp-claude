from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.utils.formatting import format_currency, format_percentage


_SEVERITY_RANK = {
    "high": 3,
    "moderate": 2,
    "low": 1,
}

_DRIVER_PRIORITY = {
    "contingency_adequacy": 1,
    "trade_procurement_concentration": 2,
    "regional_cost_pressure": 3,
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


def _build_contingency_driver(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    construction_costs = payload.get("construction_costs")
    soft_costs = payload.get("soft_costs")
    if not isinstance(construction_costs, dict) or not isinstance(soft_costs, dict):
        return None

    contingency_amount = _to_number(soft_costs.get("contingency"))
    construction_total = _to_number(construction_costs.get("construction_total"))
    if contingency_amount is None or construction_total is None or construction_total <= 0:
        return None

    contingency_pct = contingency_amount / construction_total
    contingency_pct_display = _format_ratio_pct(contingency_pct)

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

    return {
        "id": "contingency_adequacy",
        "title": "Contingency Adequacy",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["basis", "cost_confidence"],
        "verify_next": (
            "Confirm what is still truly uncommitted, what is already absorbing scope decisions, "
            "and who controls release of the remaining contingency."
        ),
        "evidence_summary": (
            f"Contingency: {contingency_pct_display} of {format_currency(construction_total)} core construction."
        ),
        "source": "soft_costs.contingency",
        "status": "supported",
    }


def _build_trade_procurement_driver(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    trade_breakdown = payload.get("trade_breakdown")
    if not isinstance(trade_breakdown, dict):
        return None

    ranked_packages = []
    for trade_name, amount_raw in trade_breakdown.items():
        amount = _to_number(amount_raw)
        if amount is None or amount <= 0:
            continue
        ranked_packages.append(
            {
                "label": _titleize_trade(trade_name),
                "amount": amount,
            }
        )

    if not ranked_packages:
        return None

    ranked_packages.sort(key=lambda item: item["amount"], reverse=True)
    total_trade_cost = sum(item["amount"] for item in ranked_packages)
    if total_trade_cost <= 0:
        return None

    primary = ranked_packages[0]
    secondary = ranked_packages[1] if len(ranked_packages) > 1 else None
    primary_share = primary["amount"] / total_trade_cost
    combined_share = primary_share + ((secondary["amount"] / total_trade_cost) if secondary else 0.0)
    combined_share_display = _format_ratio_pct(combined_share)
    secondary_label = f" and {secondary['label']}" if secondary else ""

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

    evidence_parts = [
        f"{primary['label']} {_format_ratio_pct(primary_share)}",
    ]
    if secondary:
        evidence_parts.append(
            f"{secondary['label']} {_format_ratio_pct(secondary['amount'] / total_trade_cost)}"
        )

    verify_target = (
        f"{primary['label']}"
        f"{secondary_label}"
    )

    return {
        "id": "trade_procurement_concentration",
        "title": "Trade / Package Concentration",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["cost_confidence", "procurement", "schedule"],
        "verify_next": (
            f"Pressure-test the current basis against {verify_target} and confirm where scope definition "
            "or pricing could still move."
        ),
        "evidence_summary": (
            f"Top packages: {', '.join(evidence_parts)} ({combined_share_display} combined)."
        ),
        "source": "trade_breakdown",
        "status": "supported",
    }


def _build_regional_cost_pressure_driver(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    construction_costs = payload.get("construction_costs")
    regional = payload.get("regional")
    project_info = payload.get("project_info")
    if not isinstance(construction_costs, dict):
        return None

    multiplier = _to_number(construction_costs.get("regional_multiplier"))
    source = "construction_costs.regional_multiplier"
    if multiplier is None:
        source = ""
    if multiplier is None and isinstance(regional, dict):
        multiplier = _to_number(regional.get("multiplier"))
        if multiplier is not None:
            source = "regional.multiplier"
    if multiplier is None or multiplier <= 1.05:
        return None

    if isinstance(regional, dict):
        location_display = regional.get("location_display")
    else:
        location_display = None
    if not isinstance(location_display, str) or not location_display.strip():
        if isinstance(project_info, dict) and isinstance(project_info.get("location"), str):
            location_display = project_info["location"]
        else:
            location_display = "This market"

    delta_pct_display = format_percentage((multiplier - 1.0) * 100.0, 1)
    if multiplier >= 1.15:
        severity = "high"
        why = (
            f"{location_display} is {delta_pct_display} above the national construction-cost baseline, "
            "which can compress bid coverage and reduce tolerance for scope movement."
        )
    else:
        severity = "moderate"
        why = (
            f"{location_display} is {delta_pct_display} above the national construction-cost baseline, "
            "adding upward pressure to local pricing and procurement assumptions."
        )

    return {
        "id": "regional_cost_pressure",
        "title": "Regional Cost Pressure",
        "severity": severity,
        "why_this_is_showing": why,
        "affects": ["basis", "cost_confidence", "procurement"],
        "verify_next": (
            "Confirm current subcontractor pricing, freight/logistics assumptions, "
            "and any escalation coverage tied to this market."
        ),
        "evidence_summary": f"Regional construction multiplier: {multiplier:.2f}x vs 1.00 baseline.",
        "source": source or "regional.multiplier",
        "status": "supported",
    }


def build_construction_risk_drivers(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    drivers = [
        driver
        for driver in (
            _build_contingency_driver(payload),
            _build_trade_procurement_driver(payload),
            _build_regional_cost_pressure_driver(payload),
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
