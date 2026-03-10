from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.v2.config.master_config import BuildingType, get_building_config


LEASE_RENT_MARKET_RATE_FAMILY_ID = "lease_rent_market_rate"
HOSPITALITY_FAMILY_ID = "hospitality"
OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID = "operating_business_fit_out_heavy"
MIXED_USE_BLENDED_FAMILY_ID = "mixed_use_blended"
HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID = "high_capex_parking_special_case"
SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID = "subsidized_public_institutional"

_SUBSIDIZED_ADS_HIDE_SUBTYPES = {
    "affordable_housing",
    "hospital",
    "medical_center",
    "elementary_school",
    "middle_school",
    "high_school",
}

_FAMILY_LABELS = {
    LEASE_RENT_MARKET_RATE_FAMILY_ID: "Lease / Rent Market-Rate",
    HOSPITALITY_FAMILY_ID: "Hospitality",
    OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID: "Operating-Business / Fit-Out-Heavy",
    MIXED_USE_BLENDED_FAMILY_ID: "Mixed-Use Blended",
    HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID: "High-Capex / Parking Special-Case",
    SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID: "Subsidized / Public / Institutional",
}

_ITEM_META = {
    "debt_amount": {"label": "Debt Amount", "format": "currency"},
    "equity_amount": {"label": "Equity Amount", "format": "currency"},
    "grants_amount": {"label": "Grants", "format": "currency"},
    "philanthropy_amount": {"label": "Philanthropy", "format": "currency"},
    "debt_ratio": {"label": "Debt Ratio", "format": "percentage", "decimals": 1},
    "annual_debt_service": {"label": "Annual Debt Service", "format": "currency"},
    "calculated_dscr": {"label": "Calculated DSCR", "format": "multiple", "decimals": 2},
    "target_dscr": {"label": "Target DSCR", "format": "multiple", "decimals": 2},
    "yield_on_cost": {"label": "Yield on Cost", "format": "percentage", "decimals": 1},
    "market_cap_rate": {"label": "Market Cap Rate", "format": "percentage", "decimals": 1},
    "cap_rate_spread_bps": {"label": "Cap Spread", "format": "basis_points", "decimals": 0},
}


def _normalize_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace(" ", "_")


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _to_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if number != number:
            return None
        return number
    return None


def _resolve_context(payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    parsed = _as_dict(parsed_input)
    project_info = _as_dict(payload.get("project_info"))
    request_data = _as_dict(payload.get("request_data"))

    return {
        "building_type": _normalize_key(
            parsed.get("building_type")
            or request_data.get("building_type")
            or project_info.get("building_type")
        ),
        "subtype": _normalize_key(
            parsed.get("subtype")
            or parsed.get("building_subtype")
            or request_data.get("subtype")
            or project_info.get("subtype")
        ),
        "ownership_type": _normalize_key(
            parsed.get("ownership_type")
            or request_data.get("ownership_type")
        ),
    }


def _coerce_building_type(value: str) -> Optional[BuildingType]:
    if not value:
        return None
    try:
        return BuildingType(value)
    except ValueError:
        return None


def _resolve_family_from_config(
    payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    context = _resolve_context(payload, parsed_input)
    building_type = _coerce_building_type(context["building_type"])
    subtype = context["subtype"]
    if building_type is None or not subtype:
        return None

    config = get_building_config(building_type, subtype)
    family_id = getattr(config, "financing_presentation_family", None) if config else None
    return family_id if isinstance(family_id, str) and family_id else None


def _resolve_family_fallback(
    payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]] = None
) -> str:
    context = _resolve_context(payload, parsed_input)
    building_type = context["building_type"]

    if building_type in {"civic", "educational", "recreation"}:
        return SUBSIDIZED_PUBLIC_INSTITUTIONAL_FAMILY_ID
    if building_type == "hospitality":
        return HOSPITALITY_FAMILY_ID
    if building_type == "mixed_use":
        return MIXED_USE_BLENDED_FAMILY_ID
    if building_type == "parking":
        return HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID
    if building_type in {"restaurant", "healthcare"}:
        return OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID
    return LEASE_RENT_MARKET_RATE_FAMILY_ID


def resolve_financing_family(payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]] = None) -> str:
    family_id = _resolve_family_from_config(payload, parsed_input)
    if family_id:
        return family_id
    return _resolve_family_fallback(payload, parsed_input)


def _build_values(payload: Dict[str, Any]) -> Dict[str, Optional[float]]:
    ownership_analysis = _as_dict(payload.get("ownership_analysis"))
    financing_sources = _as_dict(ownership_analysis.get("financing_sources"))
    debt_metrics = _as_dict(ownership_analysis.get("debt_metrics"))
    totals = _as_dict(payload.get("totals"))

    debt_amount = _to_number(financing_sources.get("debt_amount"))
    total_project_cost = _to_number(totals.get("total_project_cost"))
    debt_ratio = None
    if debt_amount is not None and total_project_cost is not None and total_project_cost > 0:
        debt_ratio = debt_amount / total_project_cost

    return {
        "debt_amount": debt_amount,
        "equity_amount": _to_number(financing_sources.get("equity_amount")),
        "grants_amount": _to_number(financing_sources.get("grants_amount")),
        "philanthropy_amount": _to_number(financing_sources.get("philanthropy_amount")),
        "debt_ratio": debt_ratio,
        "annual_debt_service": _to_number(debt_metrics.get("annual_debt_service")),
        "calculated_dscr": _to_number(debt_metrics.get("calculated_dscr")),
        "target_dscr": _to_number(debt_metrics.get("target_dscr")),
        "yield_on_cost": _to_number(ownership_analysis.get("yield_on_cost")),
        "market_cap_rate": _to_number(ownership_analysis.get("market_cap_rate")),
        "cap_rate_spread_bps": _to_number(ownership_analysis.get("cap_rate_spread_bps")),
    }


def _show_subsidized_annual_debt_service(payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]]) -> bool:
    context = _resolve_context(payload, parsed_input)
    if context["building_type"] == "civic":
        return False
    return context["subtype"] not in _SUBSIDIZED_ADS_HIDE_SUBTYPES


def _append_item(
    items: List[Dict[str, Any]],
    field_id: str,
    values: Dict[str, Optional[float]],
    *,
    positive_only: bool = False,
    allow_zero: bool = False,
) -> None:
    value = values.get(field_id)
    if value is None:
        return
    if positive_only and value <= 0:
        return
    if not allow_zero and value == 0:
        return
    meta = _ITEM_META[field_id]
    item = {
        "id": field_id,
        "label": meta["label"],
        "value": value,
        "format": meta["format"],
    }
    if "decimals" in meta:
        item["decimals"] = meta["decimals"]
    items.append(item)


def build_financing_summary(
    payload: Dict[str, Any], parsed_input: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    family_id = resolve_financing_family(payload, parsed_input)
    values = _build_values(payload)
    items: List[Dict[str, Any]] = []

    if family_id == LEASE_RENT_MARKET_RATE_FAMILY_ID:
        for field_id in (
            "debt_amount",
            "equity_amount",
        ):
            _append_item(items, field_id, values, allow_zero=True)
        for field_id in ("grants_amount", "philanthropy_amount"):
            _append_item(items, field_id, values, positive_only=True)
        for field_id in (
            "debt_ratio",
            "annual_debt_service",
            "calculated_dscr",
            "target_dscr",
            "yield_on_cost",
            "market_cap_rate",
            "cap_rate_spread_bps",
        ):
            _append_item(
                items,
                field_id,
                values,
                positive_only=field_id not in {"cap_rate_spread_bps"},
                allow_zero=field_id in {"debt_ratio", "cap_rate_spread_bps"},
            )
    elif family_id == HOSPITALITY_FAMILY_ID:
        for field_id in ("debt_amount", "equity_amount"):
            _append_item(items, field_id, values, allow_zero=True)
        for field_id in (
            "annual_debt_service",
            "calculated_dscr",
            "target_dscr",
            "yield_on_cost",
            "market_cap_rate",
            "cap_rate_spread_bps",
        ):
            _append_item(
                items,
                field_id,
                values,
                positive_only=field_id not in {"cap_rate_spread_bps"},
                allow_zero=field_id == "cap_rate_spread_bps",
            )
    elif family_id == OPERATING_BUSINESS_FIT_OUT_HEAVY_FAMILY_ID:
        for field_id in ("debt_amount", "equity_amount"):
            _append_item(items, field_id, values, allow_zero=True)
        for field_id in (
            "annual_debt_service",
            "calculated_dscr",
            "target_dscr",
            "yield_on_cost",
        ):
            _append_item(items, field_id, values, positive_only=True)
    elif family_id == MIXED_USE_BLENDED_FAMILY_ID:
        for field_id in ("debt_amount", "equity_amount"):
            _append_item(items, field_id, values, allow_zero=True)
        _append_item(items, "grants_amount", values, positive_only=True)
        for field_id in (
            "annual_debt_service",
            "calculated_dscr",
            "target_dscr",
            "yield_on_cost",
        ):
            _append_item(items, field_id, values, positive_only=True)
    elif family_id == HIGH_CAPEX_PARKING_SPECIAL_CASE_FAMILY_ID:
        for field_id in ("debt_amount", "equity_amount"):
            _append_item(items, field_id, values, allow_zero=True)
        for field_id in (
            "annual_debt_service",
            "calculated_dscr",
            "target_dscr",
            "yield_on_cost",
        ):
            _append_item(items, field_id, values, positive_only=True)
    else:
        for field_id in ("debt_amount", "equity_amount"):
            _append_item(items, field_id, values, allow_zero=True)
        for field_id in ("grants_amount", "philanthropy_amount"):
            _append_item(items, field_id, values, positive_only=True)
        _append_item(items, "debt_ratio", values, allow_zero=True)
        if _show_subsidized_annual_debt_service(payload, parsed_input):
            _append_item(items, "annual_debt_service", values, positive_only=True)

    return {
        "family_id": family_id,
        "family_label": _FAMILY_LABELS[family_id],
        "items": items,
    }
