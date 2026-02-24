from __future__ import annotations

import copy
import json
import math
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile
from app.v2.config.type_profiles.decision_insurance_policy import (
    DECISION_INSURANCE_POLICY_ID,
    get_decision_insurance_policy,
)

_MISSING = object()

_WAVE1_PROFILE_IDS: Set[str] = {
    "industrial_warehouse_v1",
    "industrial_distribution_center_v1",
    "industrial_manufacturing_v1",
    "industrial_flex_space_v1",
    "industrial_cold_storage_v1",
    "healthcare_medical_office_building_v1",
    "healthcare_urgent_care_v1",
    "restaurant_quick_service_v1",
    "restaurant_full_service_v1",
    "restaurant_fine_dining_v1",
    "restaurant_cafe_v1",
    "restaurant_bar_tavern_v1",
    "hospitality_limited_service_hotel_v1",
    "hospitality_full_service_hotel_v1",
}

_DEFAULT_DECISION_TABLE_COLUMNS: List[Dict[str, str]] = [
    {
        "id": "total_cost",
        "label": "Total Project Cost",
        "metric_ref": "totals.total_project_cost",
    },
    {
        "id": "annual_revenue",
        "label": "Annual Revenue",
        "metric_ref": "revenue_analysis.annual_revenue",
    },
    {
        "id": "noi",
        "label": "NOI",
        "metric_ref": "return_metrics.estimated_annual_noi",
    },
    {
        "id": "dscr",
        "label": "DSCR",
        "metric_ref": "ownership_analysis.debt_metrics.calculated_dscr",
    },
    {
        "id": "yoc",
        "label": "Yield on Cost",
        "metric_ref": "ownership_analysis.yield_on_cost",
    },
]

_ROW_RISK_LABEL_PREFIX = "row.risk_labels."

class DealShieldResolutionError(ValueError):
    pass

def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return False
        return True
    return False

def _resolve_metric_ref(payload: Dict[str, Any], metric_ref: str) -> Any:
    current: Any = payload
    for part in metric_ref.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current

def _normalize_transforms(transform: Any) -> List[Dict[str, Any]]:
    if transform is None:
        return []
    if isinstance(transform, dict):
        return [transform]
    if isinstance(transform, list):
        if not all(isinstance(item, dict) for item in transform):
            raise DealShieldResolutionError("Transform list must contain dict entries")
        return list(transform)
    raise DealShieldResolutionError(f"Unsupported transform type: {type(transform).__name__}")

def _apply_transform(value: float, transform: Dict[str, Any]) -> float:
    op = transform.get("op")
    operand = transform.get("value")
    if not _is_number(operand):
        raise DealShieldResolutionError("Transform value must be numeric")
    operand_value = float(operand)
    if op == "mul":
        return value * operand_value
    if op == "add":
        return value + operand_value
    if op == "sub":
        return value - operand_value
    if op == "div":
        if operand_value == 0:
            raise DealShieldResolutionError("Transform division by zero")
        return value / operand_value
    raise DealShieldResolutionError(f"Unsupported transform op: {op}")

def _apply_transforms(value: float, transforms: Iterable[Dict[str, Any]]) -> float:
    out = float(value)
    for t in transforms:
        out = _apply_transform(out, t)
    return out

def _iter_sensitivity_blocks(payload: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
    blocks: List[Tuple[str, Dict[str, Any]]] = []
    s = payload.get("sensitivity_analysis")
    if isinstance(s, dict):
        blocks.append(("sensitivity_analysis", s))
    oa = payload.get("ownership_analysis")
    if isinstance(oa, dict):
        os = oa.get("sensitivity_analysis")
        if isinstance(os, dict):
            blocks.append(("ownership_analysis.sensitivity_analysis", os))
    return blocks

def _resolve_sensitivity_value(payload: Dict[str, Any], scenario_id: str, metric_ref: str) -> Tuple[Optional[float], Optional[str]]:
    for base_path, block in _iter_sensitivity_blocks(payload):
        sp = block.get(scenario_id)
        if isinstance(sp, dict):
            v = _resolve_metric_ref(sp, metric_ref)
            if v is not _MISSING and _is_number(v):
                return float(v), f"{base_path}.{scenario_id}"
        scenarios = block.get("scenarios")
        if isinstance(scenarios, dict):
            sp = scenarios.get(scenario_id)
            if isinstance(sp, dict):
                v = _resolve_metric_ref(sp, metric_ref)
                if v is not _MISSING and _is_number(v):
                    return float(v), f"{base_path}.scenarios.{scenario_id}"
    return None, None

def _resolve_dealshield_scenarios_value(payload: Dict[str, Any], scenario_id: str, metric_ref: str) -> Tuple[Optional[float], Optional[str]]:
    ds = payload.get("dealshield_scenarios")
    if not isinstance(ds, dict):
        return None, None
    scenarios = ds.get("scenarios")
    if not isinstance(scenarios, dict):
        return None, None
    sp = scenarios.get(scenario_id)
    if not isinstance(sp, dict):
        return None, None
    v = _resolve_metric_ref(sp, metric_ref)
    if v is _MISSING or not _is_number(v):
        return None, None
    return float(v), f"dealshield_scenarios.scenarios.{scenario_id}"

def _collect_sensitivity_presence(payload: Dict[str, Any]) -> List[str]:
    paths: List[str] = []
    s = payload.get("sensitivity_analysis")
    if isinstance(s, dict):
        paths.append("sensitivity_analysis")
        if isinstance(s.get("scenarios"), dict):
            paths.append("sensitivity_analysis.scenarios")
    oa = payload.get("ownership_analysis")
    if isinstance(oa, dict):
        os = oa.get("sensitivity_analysis")
        if isinstance(os, dict):
            paths.append("ownership_analysis.sensitivity_analysis")
            if isinstance(os.get("scenarios"), dict):
                paths.append("ownership_analysis.sensitivity_analysis.scenarios")
    return paths


def _normalize_risk_label(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized == "low":
        return "Low"
    if normalized in {"med", "medium"}:
        return "Med"
    if normalized == "high":
        return "High"
    return None


def _resolve_decision_columns(profile: Dict[str, Any]) -> List[Dict[str, str]]:
    configured = profile.get("decision_table_columns")
    if not isinstance(configured, list):
        return _DEFAULT_DECISION_TABLE_COLUMNS

    columns: List[Dict[str, str]] = []
    for col in configured:
        if not isinstance(col, dict):
            continue
        col_id = col.get("id")
        label = col.get("label")
        metric_ref = col.get("metric_ref")
        if not (
            isinstance(col_id, str)
            and col_id.strip()
            and isinstance(label, str)
            and label.strip()
            and isinstance(metric_ref, str)
            and metric_ref.strip()
        ):
            continue
        columns.append(
            {
                "id": col_id.strip(),
                "label": label.strip(),
                "metric_ref": metric_ref.strip(),
            }
        )
    return columns or _DEFAULT_DECISION_TABLE_COLUMNS


def _resolve_profile_scenario_rows(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    derived_rows = profile.get("derived_rows")
    base_row_cfg = profile.get("base_row") if isinstance(profile.get("base_row"), dict) else {}
    base_row: Dict[str, Any] = {
        "scenario_id": "base",
        "label": (
            base_row_cfg.get("label")
            if isinstance(base_row_cfg.get("label"), str) and base_row_cfg.get("label").strip()
            else "Base"
        ),
    }
    if isinstance(base_row_cfg.get("delta"), str) and base_row_cfg.get("delta").strip():
        base_row["delta"] = base_row_cfg.get("delta").strip()
    if isinstance(base_row_cfg.get("risk_labels"), dict):
        base_row["risk_labels"] = copy.deepcopy(base_row_cfg.get("risk_labels"))
    if not isinstance(derived_rows, list):
        return [base_row]

    rows: List[Dict[str, Any]] = [base_row]
    seen = {"base"}
    for row in derived_rows:
        if not isinstance(row, dict):
            continue
        scenario_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            continue
        normalized_id = scenario_id.strip()
        if normalized_id in seen:
            continue
        seen.add(normalized_id)
        label = row.get("label") if isinstance(row.get("label"), str) and row.get("label").strip() else normalized_id
        resolved_row: Dict[str, Any] = {"scenario_id": normalized_id, "label": label}
        if isinstance(row.get("delta"), str) and row.get("delta").strip():
            resolved_row["delta"] = row.get("delta").strip()
        if isinstance(row.get("risk_labels"), dict):
            resolved_row["risk_labels"] = copy.deepcopy(row.get("risk_labels"))
        rows.append(resolved_row)
    return rows


def _resolve_row_metric_value(
    row: Dict[str, Any],
    metric_ref: str,
) -> Tuple[Optional[str], Optional[str], str]:
    if not metric_ref.startswith(_ROW_RISK_LABEL_PREFIX):
        return None, None, "missing"
    key = metric_ref[len(_ROW_RISK_LABEL_PREFIX):].strip()
    if not key:
        return None, None, "missing"
    risk_labels = row.get("risk_labels")
    if not isinstance(risk_labels, dict):
        return None, None, "missing"
    value = _normalize_risk_label(risk_labels.get(key))
    return value, (f"row.risk_labels.{key}" if value is not None else None), ("profile_row" if value is not None else "missing")


def _resolve_profile_row_for_scenario(profile: Dict[str, Any], scenario_id: str) -> Dict[str, Any]:
    if scenario_id == "base":
        base_row = profile.get("base_row")
        return base_row if isinstance(base_row, dict) else {}
    derived_rows = profile.get("derived_rows")
    if not isinstance(derived_rows, list):
        return {}
    for row in derived_rows:
        if not isinstance(row, dict):
            continue
        row_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if row_id == scenario_id:
            return row
    return {}


def _resolve_profile_transformed_value(
    payload: Dict[str, Any],
    profile: Dict[str, Any],
    scenario_id: str,
    metric_ref: str,
) -> Optional[float]:
    if scenario_id == "base":
        return None
    raw_base = _resolve_metric_ref(payload, metric_ref)
    if raw_base is _MISSING or not _is_number(raw_base):
        return None
    row = _resolve_profile_row_for_scenario(profile, scenario_id)
    if not isinstance(row, dict):
        return None
    tiles = profile.get("tiles")
    if not isinstance(tiles, list):
        return None
    tile_map = {
        tile.get("tile_id"): tile
        for tile in tiles
        if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
    }
    tile_ids: List[str] = []
    for key in ("apply_tiles", "plus_tiles"):
        values = row.get(key)
        if isinstance(values, list):
            tile_ids.extend(tile_id for tile_id in values if isinstance(tile_id, str))
    transforms: List[Dict[str, Any]] = []
    for tile_id in tile_ids:
        tile = tile_map.get(tile_id)
        if not isinstance(tile, dict) or tile.get("metric_ref") != metric_ref:
            continue
        transforms.extend(_normalize_transforms(tile.get("transform")))
    if not transforms:
        return None
    return _apply_transforms(float(raw_base), transforms)


def _resolve_project_square_footage(payload: Dict[str, Any]) -> Optional[float]:
    project_info = payload.get("project_info")
    if isinstance(project_info, dict) and _is_number(project_info.get("square_footage")):
        sf = float(project_info.get("square_footage"))
        if sf > 0:
            return sf
    if _is_number(payload.get("square_footage")):
        sf = float(payload.get("square_footage"))
        if sf > 0:
            return sf
    return None


def _resolve_dealshield_scenario_snapshot(payload: Dict[str, Any], scenario_id: str) -> Optional[Dict[str, Any]]:
    ds = payload.get("dealshield_scenarios")
    if not isinstance(ds, dict):
        return None
    scenarios = ds.get("scenarios")
    if not isinstance(scenarios, dict):
        return None
    scenario_payload = scenarios.get(scenario_id)
    if not isinstance(scenario_payload, dict):
        return None
    return scenario_payload


def _resolve_decision_value(
    payload: Dict[str, Any],
    scenario_id: str,
    metric_ref: str,
) -> Tuple[Optional[float], Optional[str], str]:
    if scenario_id == "base":
        v, src = _resolve_dealshield_scenarios_value(payload, "base", metric_ref)
        if v is not None:
            return v, src, "dealshield_scenarios"
        raw = _resolve_metric_ref(payload, metric_ref)
        if raw is not _MISSING and _is_number(raw):
            return float(raw), metric_ref, "payload_base"
        return None, None, "missing"

    v, src = _resolve_dealshield_scenarios_value(payload, scenario_id, metric_ref)
    if v is not None:
        return v, src, "dealshield_scenarios"
    return None, None, "missing"


def _resolve_cap_rate_used(payload: Dict[str, Any]) -> Optional[float]:
    return_metrics = payload.get("return_metrics")
    profile = payload.get("profile")

    cap_rate_value: Optional[float] = None
    if isinstance(return_metrics, dict) and _is_number(return_metrics.get("market_cap_rate")):
        cap_rate_value = float(return_metrics.get("market_cap_rate"))
    elif isinstance(profile, dict) and _is_number(profile.get("market_cap_rate")):
        cap_rate_value = float(profile.get("market_cap_rate"))
    elif isinstance(return_metrics, dict) and _is_number(return_metrics.get("cap_rate")):
        cap_rate_value = float(return_metrics.get("cap_rate"))

    if cap_rate_value is not None and cap_rate_value <= 0:
        return None
    return cap_rate_value


def _extract_decision_cell_value(row: Dict[str, Any], col_id: str) -> Optional[float]:
    cells = row.get("cells")
    if not isinstance(cells, list):
        return None
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        cell_id = cell.get("col_id") or cell.get("tile_id") or cell.get("id")
        if cell_id != col_id:
            continue
        raw_value = cell.get("value")
        if _is_number(raw_value):
            return float(raw_value)
        return None
    return None


def _apply_display_guards(
    payload: Dict[str, Any],
    decision_table: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str], Dict[str, Any]]:
    columns = decision_table.get("columns")
    if not isinstance(columns, list):
        columns = []
        decision_table["columns"] = columns

    rows = decision_table.get("rows")
    if not isinstance(rows, list):
        rows = []
        decision_table["rows"] = rows
    column_ids = {
        col.get("id")
        for col in columns
        if isinstance(col, dict) and isinstance(col.get("id"), str)
    }
    if not column_ids.intersection({"annual_revenue", "noi", "dscr", "yoc"}):
        return {}, [], {}

    disclosures: List[str] = []
    schedule_disclosure = (
        "DealShield scenarios stress cost/revenue assumptions only; schedule slippage or acceleration impacts "
        "(carry, debt timing, lease-up timing) are not modeled here."
    )
    if schedule_disclosure not in disclosures:
        disclosures.append(schedule_disclosure)
    financing_raw = payload.get("financing_assumptions")
    if not isinstance(financing_raw, dict):
        ownership_analysis = payload.get("ownership_analysis")
        debt_metrics = ownership_analysis.get("debt_metrics") if isinstance(ownership_analysis, dict) else None
        financing_raw = debt_metrics if isinstance(debt_metrics, dict) else {}

    financing_assumptions = {
        key: financing_raw.get(key)
        for key in (
            "debt_pct",
            "ltv",
            "interest_rate_pct",
            "amort_years",
            "loan_term_years",
            "interest_only_months",
        )
        if key in financing_raw
    }
    debt_pct = financing_assumptions.get("debt_pct")
    if not _is_number(debt_pct):
        debt_pct = financing_assumptions.get("ltv")
    has_financing_assumptions = (
        _is_number(debt_pct)
        and _is_number(financing_assumptions.get("interest_rate_pct"))
        and (
            _is_number(financing_assumptions.get("amort_years"))
            or _is_number(financing_assumptions.get("loan_term_years"))
        )
    )

    cap_rate_value = _resolve_cap_rate_used(payload)

    has_stabilized_value_column = any(
        isinstance(col, dict) and col.get("id") == "stabilized_value" for col in columns
    )
    if not has_stabilized_value_column:
        columns.append(
            {
                "id": "stabilized_value",
                "tile_id": "stabilized_value",
                "label": "Stabilized Value",
                "metric_ref": "derived.stabilized_value",
            }
        )

    for row in rows:
        if not isinstance(row, dict):
            continue
        row_cells = row.get("cells")
        if not isinstance(row_cells, list):
            row_cells = []
            row["cells"] = row_cells

        row_cell_map: Dict[str, Dict[str, Any]] = {}
        for cell in row_cells:
            if not isinstance(cell, dict):
                continue
            cell_id = cell.get("col_id") or cell.get("tile_id") or cell.get("id")
            if isinstance(cell_id, str) and cell_id:
                row_cell_map[cell_id] = cell

        dscr_cell = row_cell_map.get("dscr")
        if isinstance(dscr_cell, dict) and _is_number(dscr_cell.get("value")) and not has_financing_assumptions:
            dscr_cell["value"] = None
            dscr_cell["provenance_kind"] = "missing"
            dscr_cell["scenario_source_path"] = None
            if "Not modeled: financing assumptions missing" not in disclosures:
                disclosures.append("Not modeled: financing assumptions missing")

        noi_value: Optional[float] = None
        noi_cell = row_cell_map.get("noi")
        if isinstance(noi_cell, dict) and _is_number(noi_cell.get("value")):
            noi_value = float(noi_cell.get("value"))
        total_cost_value: Optional[float] = None
        total_cost_cell = row_cell_map.get("total_cost")
        if isinstance(total_cost_cell, dict) and _is_number(total_cost_cell.get("value")):
            total_cost_value = float(total_cost_cell.get("value"))

        stabilized_value: Optional[float] = None
        if noi_value is not None:
            if cap_rate_value is not None:
                stabilized_value = noi_value / cap_rate_value
            else:
                if "Not modeled: cap rate missing" not in disclosures:
                    disclosures.append("Not modeled: cap rate missing")

        stabilized_cell = row_cell_map.get("stabilized_value")
        if not isinstance(stabilized_cell, dict):
            stabilized_cell = {
                "col_id": "stabilized_value",
                "tile_id": "stabilized_value",
            }
            row_cells.append(stabilized_cell)

        stabilized_cell["value"] = stabilized_value
        stabilized_cell["provenance_kind"] = "derived" if stabilized_value is not None else "missing"
        stabilized_cell["cap_rate_used_pct"] = (cap_rate_value * 100.0) if stabilized_value is not None and cap_rate_value is not None else None
        if stabilized_value is not None and total_cost_value is not None:
            value_gap = stabilized_value - total_cost_value
            stabilized_cell["value_gap"] = value_gap
            stabilized_cell["value_gap_pct"] = (
                (value_gap / total_cost_value) * 100.0
                if total_cost_value != 0
                else None
            )
        else:
            stabilized_cell["value_gap"] = None
            stabilized_cell["value_gap_pct"] = None

    decision_summary: Dict[str, Any] = {
        "scenario_id": "base",
        "scenario_label": "Base",
        "stabilized_value": None,
        "cap_rate_used_pct": (cap_rate_value * 100.0) if cap_rate_value is not None else None,
        "value_gap": None,
        "value_gap_pct": None,
    }
    base_row = next(
        (
            row
            for row in rows
            if isinstance(row, dict)
            and (
                row.get("scenario_id") == "base"
                or str(row.get("label", "")).strip().lower() == "base"
            )
        ),
        rows[0] if rows else None,
    )
    if isinstance(base_row, dict):
        scenario_id = base_row.get("scenario_id")
        if isinstance(scenario_id, str) and scenario_id:
            decision_summary["scenario_id"] = scenario_id
        scenario_label = base_row.get("label")
        if isinstance(scenario_label, str) and scenario_label.strip():
            decision_summary["scenario_label"] = scenario_label.strip()
        base_stabilized_value = _extract_decision_cell_value(base_row, "stabilized_value")
        base_total_cost = _extract_decision_cell_value(base_row, "total_cost")
        decision_summary["stabilized_value"] = base_stabilized_value
        if base_stabilized_value is not None and base_total_cost is not None:
            value_gap = base_stabilized_value - base_total_cost
            decision_summary["value_gap"] = value_gap
            if base_total_cost != 0:
                decision_summary["value_gap_pct"] = (value_gap / base_total_cost) * 100.0
    if decision_summary.get("stabilized_value") is None and cap_rate_value is None:
        decision_summary["not_modeled_reason"] = "Not modeled: cap rate missing"

    if not has_financing_assumptions:
        financing_assumptions = {}

    return financing_assumptions, disclosures, decision_summary


def _build_decision_table(payload: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    columns: List[Dict[str, Any]] = []
    for col in _resolve_decision_columns(profile):
        col_id = col["id"]
        columns.append(
            {
                "id": col_id,
                "tile_id": col_id,
                "label": col["label"],
                "metric_ref": col["metric_ref"],
            }
        )

    scenario_rows = _resolve_profile_scenario_rows(profile)
    profile_id = profile.get("profile_id")
    is_wave1_profile = isinstance(profile_id, str) and profile_id in _WAVE1_PROFILE_IDS
    square_footage = _resolve_project_square_footage(payload)

    rows: List[Dict[str, Any]] = []
    for row in scenario_rows:
        scenario_id = row.get("scenario_id")
        label = row.get("label")
        if not isinstance(scenario_id, str) or not scenario_id:
            continue
        if not isinstance(label, str) or not label:
            label = scenario_id
        scenario_snapshot = _resolve_dealshield_scenario_snapshot(payload, scenario_id)

        if is_wave1_profile and scenario_snapshot is None:
            raise DealShieldResolutionError(
                f"Wave-1 profile '{profile_id}' missing dealshield_scenarios snapshot for scenario '{scenario_id}'"
            )

        cells: List[Dict[str, Any]] = []
        total_cost_value_for_row: Optional[float] = None
        for col in columns:
            metric_ref = col["metric_ref"]
            col_id = col["id"]
            row_value, row_source_path, row_provenance_kind = _resolve_row_metric_value(row, metric_ref)
            if row_value is not None:
                cells.append(
                    {
                        "col_id": col_id,
                        "tile_id": col_id,
                        "value": row_value,
                        "metric_ref": metric_ref,
                        "provenance_kind": row_provenance_kind,
                        "scenario_source_path": row_source_path,
                    }
                )
                continue

            if is_wave1_profile:
                raw_snapshot_value = _resolve_metric_ref(scenario_snapshot or {}, metric_ref)
                if raw_snapshot_value is _MISSING or not _is_number(raw_snapshot_value):
                    raise DealShieldResolutionError(
                        f"Wave-1 profile '{profile_id}' missing/non-numeric snapshot metric_ref "
                        f"'{metric_ref}' for scenario '{scenario_id}'"
                    )

            value, source_path, provenance_kind = _resolve_decision_value(payload, scenario_id, metric_ref)
            if value is None:
                transformed_value = _resolve_profile_transformed_value(
                    payload=payload,
                    profile=profile,
                    scenario_id=scenario_id,
                    metric_ref=metric_ref,
                )
                if transformed_value is not None:
                    value = transformed_value
                    source_path = f"profile.derived_rows.{scenario_id}"
                    provenance_kind = "profile_transform"
            if metric_ref == "totals.total_project_cost" and value is not None:
                total_cost_value_for_row = float(value)
            if (
                metric_ref == "totals.cost_per_sf"
                and value is None
                and total_cost_value_for_row is not None
                and square_footage is not None
                and square_footage > 0
            ):
                value = total_cost_value_for_row / square_footage
                source_path = "derived.total_cost_over_square_footage"
                provenance_kind = "derived"
            cells.append(
                {
                    "col_id": col_id,
                    "tile_id": col_id,
                    "value": value,
                    "metric_ref": metric_ref,
                    "provenance_kind": provenance_kind,
                    "scenario_source_path": source_path,
                }
            )

        resolved_row: Dict[str, Any] = {"scenario_id": scenario_id, "label": label, "cells": cells}
        delta = row.get("delta")
        if isinstance(delta, str) and delta.strip():
            resolved_row["delta"] = delta.strip()
        rows.append(resolved_row)

    return {"columns": columns, "rows": rows}

def build_dealshield_scenario_table(project_id: str, payload: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise DealShieldResolutionError("Payload must be a dict")
    if not isinstance(profile, dict):
        raise DealShieldResolutionError("Profile must be a dict")
    if profile.get("version") != "v1":
        raise DealShieldResolutionError(f"Unsupported profile version: {profile.get('version')}")

    tiles = profile.get("tiles")
    if not isinstance(tiles, list):
        raise DealShieldResolutionError("Profile tiles must be a list")
    derived_rows = profile.get("derived_rows")
    if not isinstance(derived_rows, list):
        raise DealShieldResolutionError("Profile derived_rows must be a list")

    columns: List[Dict[str, Any]] = []
    base_values: Dict[str, float] = {}
    base_transforms: Dict[str, List[Dict[str, Any]]] = {}

    for tile in tiles:
        if not isinstance(tile, dict):
            raise DealShieldResolutionError("Tile entries must be dicts")
        tile_id = tile.get("tile_id")
        metric_ref = tile.get("metric_ref")
        label = tile.get("label")
        required = bool(tile.get("required", False))
        if not isinstance(tile_id, str) or not tile_id:
            raise DealShieldResolutionError("Tile tile_id missing or invalid")
        if not isinstance(metric_ref, str) or not metric_ref:
            raise DealShieldResolutionError(f"Tile '{tile_id}' metric_ref missing or invalid")

        raw = _resolve_metric_ref(payload, metric_ref)
        if raw is _MISSING or not _is_number(raw):
            raise DealShieldResolutionError(f"Missing/non-numeric base metric_ref '{metric_ref}' for tile '{tile_id}'")

        transforms = _normalize_transforms(tile.get("transform"))
        value = _apply_transforms(float(raw), transforms) if transforms else float(raw)
        if not _is_number(value):
            raise DealShieldResolutionError(f"Non-numeric base value for tile '{tile_id}' after transform")

        base_values[tile_id] = float(value)
        base_transforms[tile_id] = transforms
        columns.append({"tile_id": tile_id, "label": label, "metric_ref": metric_ref, "required": required})

    rows: List[Dict[str, Any]] = []

    base_cells: List[Dict[str, Any]] = []
    for tile in tiles:
        tile_id = tile["tile_id"]
        metric_ref = tile["metric_ref"]
        base_cells.append({
            "tile_id": tile_id,
            "value": base_values[tile_id],
            "coverage": "complete",
            "provenance": {
                "kind": "observed",
                "metric_ref": metric_ref,
                "scenario_id": "base",
                "base_transform_applied": base_transforms.get(tile_id, []),
            },
        })
    rows.append({"scenario_id": "base", "label": "Base", "cells": base_cells})

    for row in derived_rows:
        if not isinstance(row, dict):
            raise DealShieldResolutionError("Derived rows must be dicts")
        scenario_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise DealShieldResolutionError("Derived scenario_id missing or invalid")
        scenario_id = scenario_id.strip()
        label = row.get("label") or scenario_id

        cells: List[Dict[str, Any]] = []
        for tile in tiles:
            tile_id = tile["tile_id"]
            metric_ref = tile["metric_ref"]

            v, src = _resolve_dealshield_scenarios_value(payload, scenario_id, metric_ref)
            if v is not None:
                cells.append({
                    "tile_id": tile_id,
                    "value": v,
                    "coverage": "complete",
                    "provenance": {
                        "kind": "dealshield_scenarios",
                        "metric_ref": metric_ref,
                        "scenario_id": scenario_id,
                        "scenario_source_path": src,
                    },
                })
                continue

            v, src = _resolve_sensitivity_value(payload, scenario_id, metric_ref)
            if v is not None:
                cells.append({
                    "tile_id": tile_id,
                    "value": v,
                    "coverage": "complete",
                    "provenance": {
                        "kind": "sensitivity",
                        "metric_ref": metric_ref,
                        "scenario_id": scenario_id,
                        "scenario_source_path": src,
                    },
                })
                continue

            cells.append({
                "tile_id": tile_id,
                "value": base_values[tile_id],
                "coverage": "base_only",
                "provenance": {
                    "kind": "observed_base_only",
                    "metric_ref": metric_ref,
                    "scenario_id": scenario_id,
                    "base_transform_applied": base_transforms.get(tile_id, []),
                },
                "explain": {
                    "why_not": "Scenario metric not yet emitted deterministically",
                    "planned_fix": "Engine will emit dealshield_scenarios with full metric snapshots per scenario",
                    "note": "This cell is base-locked until scenario snapshots exist",
                },
            })

        rows.append({"scenario_id": scenario_id, "label": label, "cells": cells})

    ds_present = isinstance(payload.get("dealshield_scenarios"), dict) and isinstance(payload.get("dealshield_scenarios", {}).get("scenarios"), dict)
    metric_refs_used = [t.get("metric_ref") for t in tiles if isinstance(t, dict)]

    return {
        "project_id": project_id,
        "profile_id": profile.get("profile_id"),
        "profile_version": profile.get("version"),
        "columns": columns,
        "rows": rows,
        "provenance": {
            "metric_refs_used": metric_refs_used,
            "sensitivity_blocks_present": _collect_sensitivity_presence(payload),
            "dealshield_scenarios_present": bool(ds_present),
        },
    }


def _extract_dealshield_context(payload: Dict[str, Any]) -> Dict[str, Any]:
    info = payload.get("project_info")
    if not isinstance(info, dict):
        return {}
    context: Dict[str, Any] = {}
    if info.get("location"):
        context["location"] = info.get("location")
    if info.get("square_footage") is not None:
        context["square_footage"] = info.get("square_footage")
    return context


def _extract_dealshield_scenario_inputs(payload: Dict[str, Any]) -> Dict[str, Any]:
    ds_block = payload.get("dealshield_scenarios")
    if not isinstance(ds_block, dict):
        return {}
    provenance = ds_block.get("provenance")
    if not isinstance(provenance, dict):
        return {}
    scenario_inputs = provenance.get("scenario_inputs")
    if not isinstance(scenario_inputs, dict):
        return {}
    return scenario_inputs


def _extract_dealshield_controls(payload: Dict[str, Any]) -> Dict[str, Any]:
    controls = payload.get("dealshield_controls")
    if not isinstance(controls, dict):
        return {}
    resolved = copy.deepcopy(controls)
    if _is_number(controls.get("stress_band_pct")):
        resolved["stress_band_pct"] = float(controls.get("stress_band_pct"))
    use_anchor = controls.get("use_anchor")
    if not isinstance(use_anchor, bool):
        use_anchor = controls.get("use_cost_anchor")
    if isinstance(use_anchor, bool):
        resolved["use_anchor"] = use_anchor
    anchor_total_cost = controls.get("anchor_total_cost")
    if not _is_number(anchor_total_cost):
        anchor_total_cost = controls.get("anchor_total_project_cost")
    if _is_number(anchor_total_cost):
        resolved["anchor_total_cost"] = float(anchor_total_cost)
    return resolved


def _resolve_scope_items_profile_id(payload: Dict[str, Any]) -> Optional[str]:
    for source in (payload, payload.get("project_info"), payload.get("profile")):
        if not isinstance(source, dict):
            continue
        for key in ("scope_items_profile_id", "scope_items_profile", "scope_profile_id"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _resolve_dealshield_content_profile_id(payload: Dict[str, Any], profile: Dict[str, Any]) -> Optional[str]:
    payload_profile_id = payload.get("dealshield_content_profile")
    if isinstance(payload_profile_id, str) and payload_profile_id.strip():
        return payload_profile_id.strip()
    profile_id = profile.get("profile_id")
    if isinstance(profile_id, str) and profile_id.strip():
        return profile_id.strip()
    return None


def _resolve_dealshield_content_drivers(content: Dict[str, Any], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    tiles = profile.get("tiles")
    if not isinstance(tiles, list):
        return []

    tile_map: Dict[str, Dict[str, Any]] = {}
    for tile in tiles:
        if not isinstance(tile, dict):
            continue
        tile_id = tile.get("tile_id")
        if isinstance(tile_id, str) and tile_id:
            tile_map[tile_id] = tile

    fastest_change = content.get("fastest_change")
    if not isinstance(fastest_change, dict):
        return []
    drivers = fastest_change.get("drivers")
    if not isinstance(drivers, list):
        return []

    resolved: List[Dict[str, Any]] = []
    for driver in drivers:
        if not isinstance(driver, dict):
            continue
        tile_id = driver.get("tile_id")
        if not isinstance(tile_id, str) or not tile_id:
            continue
        tile = tile_map.get(tile_id)
        if not isinstance(tile, dict):
            continue
        resolved.append(
            {
                "tile_id": tile_id,
                "metric_ref": tile.get("metric_ref"),
                "transform": tile.get("transform"),
            }
        )
    return resolved


def _is_multifamily_profile(profile_id: Any) -> bool:
    return isinstance(profile_id, str) and profile_id.startswith("multifamily_")


def _is_industrial_profile(profile_id: Any) -> bool:
    return isinstance(profile_id, str) and profile_id.startswith("industrial_")


def _is_restaurant_profile(profile_id: Any) -> bool:
    return isinstance(profile_id, str) and profile_id.startswith("restaurant_")


def _is_hospitality_profile(profile_id: Any) -> bool:
    return isinstance(profile_id, str) and profile_id.startswith("hospitality_")


def _supports_decision_insurance_profile(profile_id: Any) -> bool:
    return (
        _is_multifamily_profile(profile_id)
        or _is_industrial_profile(profile_id)
        or _is_restaurant_profile(profile_id)
        or _is_hospitality_profile(profile_id)
    )


def _resolve_cell_map(row: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    cell_map: Dict[str, Dict[str, Any]] = {}
    cells = row.get("cells")
    if not isinstance(cells, list):
        return cell_map
    for cell in cells:
        if not isinstance(cell, dict):
            continue
        col_id = cell.get("col_id") or cell.get("tile_id") or cell.get("id")
        if isinstance(col_id, str) and col_id:
            cell_map[col_id] = cell
    return cell_map


def _resolve_severity_thresholds(content: Optional[Dict[str, Any]]) -> Tuple[float, float]:
    high_default = 10.0
    med_default = 4.0
    if not isinstance(content, dict):
        return high_default, med_default
    block = content.get("decision_insurance")
    if not isinstance(block, dict):
        return high_default, med_default
    thresholds = block.get("severity_thresholds_pct")
    if not isinstance(thresholds, dict):
        return high_default, med_default
    high = float(thresholds.get("high")) if _is_number(thresholds.get("high")) else high_default
    med = float(thresholds.get("med")) if _is_number(thresholds.get("med")) else med_default
    if high < med:
        high, med = med, high
    if med < 0:
        med = med_default
    return high, med


def _classify_impact_severity(impact_pct: Optional[float], high_threshold: float, med_threshold: float) -> str:
    if impact_pct is None:
        return "Unknown"
    if impact_pct >= high_threshold:
        return "High"
    if impact_pct >= med_threshold:
        return "Med"
    return "Low"


def _resolve_metric_for_driver(
    payload: Dict[str, Any],
    metric_ref: str,
) -> Tuple[Optional[float], Optional[str]]:
    base_snapshot = _resolve_dealshield_scenario_snapshot(payload, "base")
    if isinstance(base_snapshot, dict):
        raw = _resolve_metric_ref(base_snapshot, metric_ref)
        if raw is not _MISSING and _is_number(raw):
            return float(raw), f"dealshield_scenarios.scenarios.base.{metric_ref}"
    raw_payload = _resolve_metric_ref(payload, metric_ref)
    if raw_payload is not _MISSING and _is_number(raw_payload):
        return float(raw_payload), metric_ref
    return None, None


def _resolve_base_total_cost(payload: Dict[str, Any], rows: List[Dict[str, Any]]) -> Tuple[Optional[float], Optional[str]]:
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        scenario_id = row.get("scenario_id")
        label = str(row.get("label", "")).strip().lower()
        if scenario_id != "base" and label != "base":
            continue
        value = _extract_decision_cell_value(row, "total_cost")
        if value is not None:
            return value, f"rows[{index}].cells.total_cost"
    raw = _resolve_metric_ref(payload, "totals.total_project_cost")
    if raw is not _MISSING and _is_number(raw):
        return float(raw), "totals.total_project_cost"
    return None, None


def _build_row_snapshots(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    snapshots: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        cell_map = _resolve_cell_map(row)
        total_cost = None
        stabilized_value = None
        value_gap = None
        value_gap_pct = None
        total_cell = cell_map.get("total_cost")
        if isinstance(total_cell, dict) and _is_number(total_cell.get("value")):
            total_cost = float(total_cell.get("value"))
        stabilized_cell = cell_map.get("stabilized_value")
        if isinstance(stabilized_cell, dict):
            if _is_number(stabilized_cell.get("value")):
                stabilized_value = float(stabilized_cell.get("value"))
            if _is_number(stabilized_cell.get("value_gap")):
                value_gap = float(stabilized_cell.get("value_gap"))
            if _is_number(stabilized_cell.get("value_gap_pct")):
                value_gap_pct = float(stabilized_cell.get("value_gap_pct"))
        if value_gap is None and stabilized_value is not None and total_cost is not None:
            value_gap = stabilized_value - total_cost
        if value_gap_pct is None and value_gap is not None and total_cost not in (None, 0):
            value_gap_pct = (value_gap / total_cost) * 100.0
        snapshots.append(
            {
                "index": index,
                "scenario_id": row.get("scenario_id"),
                "scenario_label": row.get("label"),
                "total_cost": total_cost,
                "stabilized_value": stabilized_value,
                "value_gap": value_gap,
                "value_gap_pct": value_gap_pct,
            }
        )
    return snapshots


def _resolve_row_snapshot_metric_value(row: Dict[str, Any], metric: str) -> Optional[float]:
    if not isinstance(row, dict):
        return None
    metric_key = (metric or "").strip()
    if not metric_key:
        return None
    raw_value = row.get(metric_key)
    if not _is_number(raw_value):
        return None
    return float(raw_value)


def _resolve_policy_primary_control_variable(
    policy: Optional[Dict[str, Any]],
    driver_impacts: List[Dict[str, Any]],
    high_threshold: float,
    med_threshold: float,
) -> Optional[Dict[str, Any]]:
    if not isinstance(policy, dict):
        return None
    primary_cfg = policy.get("primary_control_variable")
    if not isinstance(primary_cfg, dict):
        return None

    tile_id = primary_cfg.get("tile_id")
    if not isinstance(tile_id, str) or not tile_id.strip():
        return None
    resolved_tile_id = tile_id.strip()
    expected_metric_ref = primary_cfg.get("metric_ref")
    expected_metric_ref = expected_metric_ref.strip() if isinstance(expected_metric_ref, str) and expected_metric_ref.strip() else None

    matching_entry: Optional[Dict[str, Any]] = None
    for entry in driver_impacts:
        if not isinstance(entry, dict):
            continue
        if entry.get("tile_id") != resolved_tile_id:
            continue
        entry_metric_ref = entry.get("metric_ref")
        if expected_metric_ref and entry_metric_ref != expected_metric_ref:
            continue
        matching_entry = entry
        break

    if not isinstance(matching_entry, dict):
        return None

    impact_pct = float(matching_entry.get("impact_pct")) if _is_number(matching_entry.get("impact_pct")) else None
    delta_cost = float(matching_entry.get("delta_cost")) if _is_number(matching_entry.get("delta_cost")) else None
    label = primary_cfg.get("label") if isinstance(primary_cfg.get("label"), str) and primary_cfg.get("label").strip() else matching_entry.get("label")
    metric_ref = expected_metric_ref or matching_entry.get("metric_ref")
    if not isinstance(metric_ref, str) or not metric_ref.strip():
        return None

    return {
        "tile_id": resolved_tile_id,
        "label": label,
        "metric_ref": metric_ref.strip(),
        "impact_pct": impact_pct,
        "delta_cost": delta_cost,
        "severity": _classify_impact_severity(impact_pct, high_threshold, med_threshold),
    }


def _resolve_policy_collapse_row(
    row_snapshots: List[Dict[str, Any]],
    collapse_cfg: Optional[Dict[str, Any]],
) -> Tuple[Optional[Dict[str, Any]], Optional[float], Optional[str], Optional[float]]:
    if not isinstance(collapse_cfg, dict) or not row_snapshots:
        return None, None, None, None

    metric = collapse_cfg.get("metric")
    metric_name = metric.strip() if isinstance(metric, str) and metric.strip() else "value_gap"
    operator = collapse_cfg.get("operator")
    op = operator.strip() if isinstance(operator, str) and operator.strip() else "<="

    threshold_raw = collapse_cfg.get("threshold")
    threshold = float(threshold_raw) if _is_number(threshold_raw) else 0.0

    rows_by_id: Dict[str, Dict[str, Any]] = {}
    ordered_rows: List[Dict[str, Any]] = []

    for row in row_snapshots:
        if not isinstance(row, dict):
            continue
        scenario_id = row.get("scenario_id")
        if isinstance(scenario_id, str) and scenario_id and scenario_id not in rows_by_id:
            rows_by_id[scenario_id] = row

    scenario_priority = collapse_cfg.get("scenario_priority")
    if isinstance(scenario_priority, list):
        for scenario_id in scenario_priority:
            if isinstance(scenario_id, str) and scenario_id in rows_by_id:
                ordered_rows.append(rows_by_id[scenario_id])

    for row in row_snapshots:
        if not isinstance(row, dict):
            continue
        if row not in ordered_rows:
            ordered_rows.append(row)

    for row in ordered_rows:
        metric_value = _resolve_row_snapshot_metric_value(row, metric_name)
        if metric_value is None:
            continue
        if op == "<=" and metric_value <= threshold:
            return row, metric_value, metric_name, threshold
        if op == "<" and metric_value < threshold:
            return row, metric_value, metric_name, threshold
        if op == ">=" and metric_value >= threshold:
            return row, metric_value, metric_name, threshold
        if op == ">" and metric_value > threshold:
            return row, metric_value, metric_name, threshold

    return None, None, metric_name, threshold


def _resolve_flex_band(flex_value_pct: Optional[float], calibration: Optional[Dict[str, Any]]) -> Optional[str]:
    if flex_value_pct is None or not isinstance(calibration, dict):
        return None
    tight_raw = calibration.get("tight_max_pct")
    moderate_raw = calibration.get("moderate_max_pct")
    tight_max = float(tight_raw) if _is_number(tight_raw) else 2.0
    moderate_max = float(moderate_raw) if _is_number(moderate_raw) else 6.0
    if moderate_max < tight_max:
        moderate_max = tight_max
    if flex_value_pct <= tight_max:
        return "tight"
    if flex_value_pct <= moderate_max:
        return "moderate"
    return "comfortable"


def _build_multifamily_decision_insurance(
    payload: Dict[str, Any],
    profile: Dict[str, Any],
    rows: List[Dict[str, Any]],
    content: Optional[Dict[str, Any]],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    profile_id = profile.get("profile_id")
    if not _supports_decision_insurance_profile(profile_id):
        return {}, {}

    outputs: Dict[str, Any] = {
        "primary_control_variable": None,
        "first_break_condition": None,
        "flex_before_break_pct": None,
        "exposure_concentration_pct": None,
        "ranked_likely_wrong": [],
    }
    provenance: Dict[str, Any] = {
        "enabled": True,
        "profile_id": profile_id,
    }

    high_threshold, med_threshold = _resolve_severity_thresholds(content)
    provenance["severity_thresholds_pct"] = {
        "high": high_threshold,
        "med": med_threshold,
    }
    decision_policy = get_decision_insurance_policy(profile_id)
    if isinstance(decision_policy, dict):
        provenance["decision_insurance_policy"] = {
            "status": "available",
            "policy_id": DECISION_INSURANCE_POLICY_ID,
            "profile_id": profile_id,
            "source": "app.v2.config.type_profiles.decision_insurance_policy",
            "primary_control_variable": copy.deepcopy(decision_policy.get("primary_control_variable")),
            "collapse_trigger": copy.deepcopy(decision_policy.get("collapse_trigger")),
            "flex_calibration": copy.deepcopy(decision_policy.get("flex_calibration")),
        }
    else:
        provenance["decision_insurance_policy"] = {
            "status": "unavailable",
            "policy_id": DECISION_INSURANCE_POLICY_ID,
            "profile_id": profile_id,
            "reason": "profile_policy_missing",
            "source": "app.v2.config.type_profiles.decision_insurance_policy",
        }

    fastest_change = content.get("fastest_change") if isinstance(content, dict) else None
    fastest_drivers = fastest_change.get("drivers") if isinstance(fastest_change, dict) else None
    driver_order: Dict[str, int] = {}
    driver_labels: Dict[str, str] = {}
    if isinstance(fastest_drivers, list):
        for idx, driver in enumerate(fastest_drivers):
            if not isinstance(driver, dict):
                continue
            tile_id = driver.get("tile_id")
            if not isinstance(tile_id, str) or not tile_id:
                continue
            if tile_id not in driver_order:
                driver_order[tile_id] = idx
            label = driver.get("label")
            if isinstance(label, str) and label.strip():
                driver_labels[tile_id] = label.strip()

    base_total_cost, base_total_cost_source = _resolve_base_total_cost(payload, rows)
    square_footage = _resolve_project_square_footage(payload)
    square_footage_source = (
        "project_info.square_footage"
        if isinstance(payload.get("project_info"), dict) and _is_number((payload.get("project_info") or {}).get("square_footage"))
        else ("square_footage" if _is_number(payload.get("square_footage")) else None)
    )

    resolved_drivers = content.get("resolved_drivers") if isinstance(content, dict) else None
    driver_impacts: List[Dict[str, Any]] = []
    if isinstance(resolved_drivers, list):
        for driver in resolved_drivers:
            if not isinstance(driver, dict):
                continue
            tile_id = driver.get("tile_id")
            metric_ref = driver.get("metric_ref")
            if not isinstance(tile_id, str) or not tile_id or not isinstance(metric_ref, str) or not metric_ref:
                continue
            label = driver_labels.get(tile_id, tile_id)
            transforms = []
            transform_source = f"content.resolved_drivers[{len(driver_impacts)}].transform"
            try:
                transforms = _normalize_transforms(driver.get("transform"))
            except DealShieldResolutionError as exc:
                driver_impacts.append(
                    {
                        "tile_id": tile_id,
                        "label": label,
                        "metric_ref": metric_ref,
                        "impact_pct": None,
                        "delta_cost": None,
                        "severity": "Unknown",
                        "unavailable_reason": f"invalid_transform:{exc}",
                        "order_index": driver_order.get(tile_id, 999),
                    }
                )
                continue

            base_metric_value, base_metric_source = _resolve_metric_for_driver(payload, metric_ref)
            if base_metric_value is None:
                driver_impacts.append(
                    {
                        "tile_id": tile_id,
                        "label": label,
                        "metric_ref": metric_ref,
                        "impact_pct": None,
                        "delta_cost": None,
                        "severity": "Unknown",
                        "unavailable_reason": "base_metric_missing",
                        "order_index": driver_order.get(tile_id, 999),
                        "base_metric_source": base_metric_source,
                    }
                )
                continue

            transformed_metric_value = _apply_transforms(base_metric_value, transforms) if transforms else base_metric_value
            delta_metric = transformed_metric_value - base_metric_value
            delta_cost: Optional[float] = None
            delta_cost_source = None
            unavailable_reason = None
            if metric_ref == "totals.total_project_cost":
                delta_cost = delta_metric
                delta_cost_source = "driver_delta.total_project_cost"
            elif metric_ref == "totals.cost_per_sf":
                if square_footage is None or square_footage <= 0:
                    unavailable_reason = "square_footage_missing"
                else:
                    delta_cost = delta_metric * square_footage
                    delta_cost_source = "driver_delta.cost_per_sf_times_square_footage"
            elif metric_ref.startswith("trade_breakdown.") or metric_ref == "construction_costs.equipment_total":
                delta_cost = delta_metric
                delta_cost_source = "driver_delta.absolute_cost_component"
            else:
                unavailable_reason = "unsupported_metric_ref"

            impact_pct: Optional[float] = None
            if delta_cost is not None and base_total_cost is not None and base_total_cost > 0:
                impact_pct = abs(delta_cost / base_total_cost) * 100.0
            elif delta_cost is not None and (base_total_cost is None or base_total_cost <= 0):
                unavailable_reason = "base_total_cost_missing_or_non_positive"

            driver_impacts.append(
                {
                    "tile_id": tile_id,
                    "label": label,
                    "metric_ref": metric_ref,
                    "impact_pct": impact_pct,
                    "delta_cost": delta_cost,
                    "severity": _classify_impact_severity(impact_pct, high_threshold, med_threshold),
                    "unavailable_reason": unavailable_reason,
                    "order_index": driver_order.get(tile_id, 999),
                    "base_metric_source": base_metric_source,
                    "transform_source": transform_source,
                    "delta_cost_source": delta_cost_source,
                }
            )

    sortable_impacts = [
        entry
        for entry in driver_impacts
        if _is_number(entry.get("impact_pct")) and _is_number(entry.get("delta_cost"))
    ]
    sortable_impacts.sort(key=lambda entry: (-float(entry["impact_pct"]), int(entry.get("order_index", 999))))

    policy_primary_control = _resolve_policy_primary_control_variable(
        policy=decision_policy,
        driver_impacts=driver_impacts,
        high_threshold=high_threshold,
        med_threshold=med_threshold,
    )
    if isinstance(policy_primary_control, dict):
        outputs["primary_control_variable"] = policy_primary_control
        provenance["primary_control_variable"] = {
            "status": "available",
            "selected_tile_id": policy_primary_control.get("tile_id"),
            "selection_basis": "policy_primary_control_variable",
            "policy_id": DECISION_INSURANCE_POLICY_ID,
            "policy_source": "decision_insurance_policy.primary_control_variable",
            "base_total_cost_source": base_total_cost_source,
            "square_footage_source": square_footage_source,
            "driver_impacts": copy.deepcopy(driver_impacts),
        }
    elif sortable_impacts:
        top = sortable_impacts[0]
        outputs["primary_control_variable"] = {
            "tile_id": top.get("tile_id"),
            "label": top.get("label"),
            "metric_ref": top.get("metric_ref"),
            "impact_pct": top.get("impact_pct"),
            "delta_cost": top.get("delta_cost"),
            "severity": top.get("severity"),
        }
        provenance["primary_control_variable"] = {
            "status": "available",
            "selected_tile_id": top.get("tile_id"),
            "selection_basis": "max_abs_cost_impact_pct",
            "policy_id": DECISION_INSURANCE_POLICY_ID,
            "policy_source": "fallback_sensitivity_impact",
            "base_total_cost_source": base_total_cost_source,
            "square_footage_source": square_footage_source,
            "driver_impacts": copy.deepcopy(driver_impacts),
        }
    else:
        provenance["primary_control_variable"] = {
            "status": "unavailable",
            "reason": "no_driver_impact_available",
            "policy_id": DECISION_INSURANCE_POLICY_ID,
            "policy_source": "fallback_sensitivity_impact",
            "base_total_cost_source": base_total_cost_source,
            "square_footage_source": square_footage_source,
            "driver_impacts": copy.deepcopy(driver_impacts),
        }

    if sortable_impacts:
        denominator = sum(abs(float(entry.get("delta_cost", 0.0))) for entry in sortable_impacts)
        if denominator > 0:
            numerator = max(abs(float(entry.get("delta_cost", 0.0))) for entry in sortable_impacts)
            outputs["exposure_concentration_pct"] = (numerator / denominator) * 100.0
            provenance["exposure_concentration_pct"] = {
                "status": "available",
                "numerator_abs_delta_cost": numerator,
                "denominator_abs_delta_cost": denominator,
                "source": "resolved_driver_impacts",
            }
        else:
            provenance["exposure_concentration_pct"] = {
                "status": "unavailable",
                "reason": "zero_driver_delta_denominator",
                "source": "resolved_driver_impacts",
            }
    else:
        provenance["exposure_concentration_pct"] = {
            "status": "unavailable",
            "reason": "no_driver_impact_available",
            "source": "resolved_driver_impacts",
        }

    row_snapshots = _build_row_snapshots(rows)
    provenance["row_snapshots"] = copy.deepcopy(row_snapshots)
    base_row_snapshot = next(
        (
            row
            for row in row_snapshots
            if row.get("scenario_id") == "base"
            or str(row.get("scenario_label", "")).strip().lower() == "base"
        ),
        row_snapshots[0] if row_snapshots else None,
    )
    collapse_cfg = decision_policy.get("collapse_trigger") if isinstance(decision_policy, dict) else None
    policy_break_row, policy_break_value, policy_break_metric, policy_break_threshold = _resolve_policy_collapse_row(
        row_snapshots=row_snapshots,
        collapse_cfg=collapse_cfg if isinstance(collapse_cfg, dict) else None,
    )

    fallback_break_row = next(
        (
            row
            for row in row_snapshots
            if row is not base_row_snapshot and _is_number(row.get("value_gap")) and float(row.get("value_gap")) <= 0
        ),
        None,
    )

    first_break_row = policy_break_row if policy_break_row is not None else fallback_break_row
    if first_break_row is not None:
        if policy_break_row is not None:
            collapse_operator = collapse_cfg.get("operator") if isinstance(collapse_cfg, dict) else "<="
            if not isinstance(collapse_operator, str) or not collapse_operator.strip():
                collapse_operator = "<="
            resolved_policy_metric = policy_break_metric or "value_gap"
            resolved_policy_threshold = policy_break_threshold if policy_break_threshold is not None else 0.0
            outputs["first_break_condition"] = {
                "scenario_id": first_break_row.get("scenario_id"),
                "scenario_label": first_break_row.get("scenario_label"),
                "break_metric": resolved_policy_metric,
                "operator": collapse_operator,
                "threshold": resolved_policy_threshold,
                "observed_value": policy_break_value,
                "observed_value_pct": first_break_row.get("value_gap_pct"),
            }
            provenance["first_break_condition"] = {
                "status": "available",
                "row_index": first_break_row.get("index"),
                "source": "decision_insurance_policy.collapse_trigger",
                "policy_id": DECISION_INSURANCE_POLICY_ID,
                "policy_metric": resolved_policy_metric,
                "policy_threshold": resolved_policy_threshold,
                "policy_operator": collapse_operator,
                "policy_observed_value": policy_break_value,
            }
        else:
            outputs["first_break_condition"] = {
                "scenario_id": first_break_row.get("scenario_id"),
                "scenario_label": first_break_row.get("scenario_label"),
                "break_metric": "value_gap",
                "operator": "<=",
                "threshold": 0.0,
                "observed_value": first_break_row.get("value_gap"),
                "observed_value_pct": first_break_row.get("value_gap_pct"),
            }
            provenance["first_break_condition"] = {
                "status": "available",
                "row_index": first_break_row.get("index"),
                "source": "decision_table.rows.stabilized_value.value_gap",
            }
    else:
        provenance["first_break_condition"] = {
            "status": "unavailable",
            "reason": (
                "policy_threshold_not_reached"
                if isinstance(collapse_cfg, dict)
                else "no_modeled_break_condition"
            ),
            "source": (
                "decision_insurance_policy.collapse_trigger"
                if isinstance(collapse_cfg, dict)
                else "decision_table.rows.stabilized_value.value_gap"
            ),
            "policy_id": DECISION_INSURANCE_POLICY_ID if isinstance(collapse_cfg, dict) else None,
        }

    if base_row_snapshot is None:
        provenance["flex_before_break_pct"] = {
            "status": "unavailable",
            "reason": "base_row_missing",
            "policy_id": DECISION_INSURANCE_POLICY_ID if isinstance(collapse_cfg, dict) else None,
        }
    elif isinstance(collapse_cfg, dict):
        base_total = base_row_snapshot.get("total_cost")
        collapse_metric = policy_break_metric or "value_gap"
        collapse_threshold = policy_break_threshold if policy_break_threshold is not None else 0.0
        base_metric_value = _resolve_row_snapshot_metric_value(base_row_snapshot, collapse_metric)

        if not _is_number(base_total) or float(base_total) <= 0:
            provenance["flex_before_break_pct"] = {
                "status": "unavailable",
                "reason": "base_row_gap_or_total_cost_missing",
                "base_row_index": base_row_snapshot.get("index"),
                "policy_id": DECISION_INSURANCE_POLICY_ID,
            }
        elif base_metric_value is None:
            provenance["flex_before_break_pct"] = {
                "status": "unavailable",
                "reason": "base_row_metric_missing_for_policy_collapse",
                "metric": collapse_metric,
                "base_row_index": base_row_snapshot.get("index"),
                "policy_id": DECISION_INSURANCE_POLICY_ID,
            }
        elif base_metric_value <= collapse_threshold:
            outputs["flex_before_break_pct"] = 0.0
            provenance["flex_before_break_pct"] = {
                "status": "available",
                "reason": "base_already_broken_policy",
                "metric": collapse_metric,
                "threshold": collapse_threshold,
                "base_row_index": base_row_snapshot.get("index"),
                "policy_id": DECISION_INSURANCE_POLICY_ID,
            }
        elif first_break_row is None:
            provenance["flex_before_break_pct"] = {
                "status": "unavailable",
                "reason": "policy_threshold_not_reached",
                "metric": collapse_metric,
                "threshold": collapse_threshold,
                "base_row_index": base_row_snapshot.get("index"),
                "policy_id": DECISION_INSURANCE_POLICY_ID,
            }
        else:
            break_total = first_break_row.get("total_cost")
            break_metric_value = _resolve_row_snapshot_metric_value(first_break_row, collapse_metric)
            if not _is_number(break_total) or break_metric_value is None:
                provenance["flex_before_break_pct"] = {
                    "status": "unavailable",
                    "reason": "break_row_metric_or_total_cost_missing",
                    "metric": collapse_metric,
                    "break_row_index": first_break_row.get("index"),
                    "policy_id": DECISION_INSURANCE_POLICY_ID,
                }
            else:
                denominator = base_metric_value - break_metric_value
                if denominator <= 0:
                    provenance["flex_before_break_pct"] = {
                        "status": "unavailable",
                        "reason": "non_positive_interpolation_denominator",
                        "base_metric": base_metric_value,
                        "break_metric": break_metric_value,
                        "metric": collapse_metric,
                        "policy_id": DECISION_INSURANCE_POLICY_ID,
                    }
                else:
                    stress_break_row_pct = ((float(break_total) - float(base_total)) / float(base_total)) * 100.0
                    interpolation_numerator = base_metric_value - collapse_threshold
                    outputs["flex_before_break_pct"] = max(
                        0.0,
                        stress_break_row_pct * (interpolation_numerator / denominator),
                    )
                    provenance["flex_before_break_pct"] = {
                        "status": "available",
                        "method": "linear_interpolation_to_policy_threshold",
                        "metric": collapse_metric,
                        "threshold": collapse_threshold,
                        "stress_break_row_pct": stress_break_row_pct,
                        "base_metric": base_metric_value,
                        "break_metric": break_metric_value,
                        "base_row_index": base_row_snapshot.get("index"),
                        "break_row_index": first_break_row.get("index"),
                        "policy_id": DECISION_INSURANCE_POLICY_ID,
                    }
    else:
        base_gap = base_row_snapshot.get("value_gap")
        base_total = base_row_snapshot.get("total_cost")
        if not _is_number(base_gap) or not _is_number(base_total) or float(base_total) <= 0:
            provenance["flex_before_break_pct"] = {
                "status": "unavailable",
                "reason": "base_row_gap_or_total_cost_missing",
                "base_row_index": base_row_snapshot.get("index"),
            }
        elif float(base_gap) <= 0:
            outputs["flex_before_break_pct"] = 0.0
            provenance["flex_before_break_pct"] = {
                "status": "available",
                "reason": "base_already_broken",
                "base_row_index": base_row_snapshot.get("index"),
            }
        elif first_break_row is None:
            provenance["flex_before_break_pct"] = {
                "status": "unavailable",
                "reason": "no_modeled_break_condition",
                "base_row_index": base_row_snapshot.get("index"),
            }
        else:
            break_total = first_break_row.get("total_cost")
            break_gap = first_break_row.get("value_gap")
            if not _is_number(break_total) or not _is_number(break_gap):
                provenance["flex_before_break_pct"] = {
                    "status": "unavailable",
                    "reason": "break_row_gap_or_total_cost_missing",
                    "break_row_index": first_break_row.get("index"),
                }
            else:
                base_gap_value = float(base_gap)
                break_gap_value = float(break_gap)
                denominator = base_gap_value - break_gap_value
                if denominator <= 0:
                    provenance["flex_before_break_pct"] = {
                        "status": "unavailable",
                        "reason": "non_positive_interpolation_denominator",
                        "base_gap": base_gap_value,
                        "break_gap": break_gap_value,
                    }
                else:
                    stress_break_row_pct = ((float(break_total) - float(base_total)) / float(base_total)) * 100.0
                    outputs["flex_before_break_pct"] = max(
                        0.0,
                        stress_break_row_pct * (base_gap_value / denominator),
                    )
                    provenance["flex_before_break_pct"] = {
                        "status": "available",
                        "method": "linear_interpolation_to_value_gap_zero",
                        "stress_break_row_pct": stress_break_row_pct,
                        "base_gap": base_gap_value,
                        "break_gap": break_gap_value,
                        "base_row_index": base_row_snapshot.get("index"),
                        "break_row_index": first_break_row.get("index"),
                    }

    flex_calibration = decision_policy.get("flex_calibration") if isinstance(decision_policy, dict) else None
    if isinstance(flex_calibration, dict):
        flex_value = float(outputs.get("flex_before_break_pct")) if _is_number(outputs.get("flex_before_break_pct")) else None
        if flex_value is None:
            fallback_flex = flex_calibration.get("fallback_pct")
            if _is_number(fallback_flex):
                flex_value = float(fallback_flex)
                outputs["flex_before_break_pct"] = flex_value
                provenance["flex_before_break_pct"] = {
                    "status": "available",
                    "reason": "policy_calibrated_fallback",
                    "policy_id": DECISION_INSURANCE_POLICY_ID,
                    "fallback_pct": flex_value,
                }
        band = _resolve_flex_band(flex_value, flex_calibration)
        if isinstance(band, str):
            outputs["flex_before_break_band"] = band
            if isinstance(provenance.get("flex_before_break_pct"), dict):
                provenance["flex_before_break_pct"]["band"] = band
                provenance["flex_before_break_pct"]["calibration_source"] = "decision_insurance_policy.flex_calibration"

    impact_by_tile: Dict[str, Optional[float]] = {}
    for entry in driver_impacts:
        tile_id = entry.get("tile_id")
        impact_pct = entry.get("impact_pct")
        if isinstance(tile_id, str) and tile_id:
            impact_by_tile[tile_id] = float(impact_pct) if _is_number(impact_pct) else None

    mlw_source = content.get("most_likely_wrong") if isinstance(content, dict) else None
    ranked_items: List[Dict[str, Any]] = []
    if isinstance(mlw_source, list):
        for idx, entry in enumerate(mlw_source):
            if not isinstance(entry, dict):
                continue
            fallback_tile = None
            if idx < len(driver_order):
                fallback_tile = next(
                    (tile for tile, order_idx in driver_order.items() if order_idx == idx),
                    None,
                )
            driver_tile_id = entry.get("driver_tile_id")
            if not isinstance(driver_tile_id, str) or not driver_tile_id:
                driver_tile_id = fallback_tile
            impact_pct = impact_by_tile.get(driver_tile_id) if isinstance(driver_tile_id, str) else None
            ranked_items.append(
                {
                    "id": entry.get("id"),
                    "text": entry.get("text"),
                    "why": entry.get("why"),
                    "driver_tile_id": driver_tile_id,
                    "impact_pct": impact_pct,
                    "severity": _classify_impact_severity(impact_pct, high_threshold, med_threshold),
                    "_original_index": idx,
                }
            )

    ranked_items.sort(
        key=lambda item: (
            item.get("impact_pct") is None,
            -(float(item.get("impact_pct")) if _is_number(item.get("impact_pct")) else 0.0),
            int(item.get("_original_index", 0)),
        )
    )
    outputs["ranked_likely_wrong"] = [
        {
            "id": item.get("id"),
            "text": item.get("text"),
            "why": item.get("why"),
            "driver_tile_id": item.get("driver_tile_id"),
            "impact_pct": item.get("impact_pct"),
            "severity": item.get("severity"),
        }
        for item in ranked_items
    ]
    provenance["ranked_likely_wrong"] = {
        "status": "available" if ranked_items else "unavailable",
        "reason": None if ranked_items else "content_most_likely_wrong_missing_or_empty",
        "source": "content.most_likely_wrong",
        "driver_impact_source": "decision_insurance.primary_control_variable.driver_impacts",
    }

    return outputs, provenance


def _normalize_decision_status(value: Any) -> Optional[str]:
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


def _normalize_percentish_value(value: Any) -> Optional[float]:
    if not _is_number(value):
        return None
    parsed = float(value)
    if abs(parsed) <= 1.5:
        return parsed * 100.0
    return parsed


def _resolve_canonical_decision_status(
    payload: Dict[str, Any],
    decision_summary: Dict[str, Any],
    decision_insurance_outputs: Dict[str, Any],
    decision_insurance_provenance: Dict[str, Any],
) -> Tuple[str, str, Dict[str, Any]]:
    policy_id = "dealshield_canonical_policy_v1"
    explicit_sources = [
        payload.get("decision_status"),
        payload.get("decisionStatus"),
        decision_summary.get("decision_status"),
        decision_summary.get("decisionStatus"),
        decision_summary.get("recommendation"),
        decision_summary.get("status"),
    ]
    explicit_status = None
    explicit_raw_value = None
    for source in explicit_sources:
        normalized = _normalize_decision_status(source)
        if normalized:
            explicit_status = normalized
            explicit_raw_value = source
            break
    if explicit_status:
        return (
            explicit_status,
            "explicit_status_signal",
            {
                "policy_id": policy_id,
                "status": explicit_status,
                "reason_code": "explicit_status_signal",
                "status_source": "payload_or_decision_summary",
                "explicit_raw_value": explicit_raw_value,
            },
        )

    not_modeled_reason = decision_summary.get("not_modeled_reason") or decision_summary.get("notModeledReason")
    first_break = decision_insurance_outputs.get("first_break_condition")
    first_break_scenario = None
    if isinstance(first_break, dict):
        first_break_scenario = first_break.get("scenario_id") or first_break.get("scenarioId")
    first_break_is_base = isinstance(first_break_scenario, str) and first_break_scenario.strip().lower() == "base"
    flex_provenance = (
        decision_insurance_provenance.get("flex_before_break_pct")
        if isinstance(decision_insurance_provenance.get("flex_before_break_pct"), dict)
        else {}
    )
    flex_reason = flex_provenance.get("reason")
    base_already_broken = isinstance(flex_reason, str) and flex_reason.strip().lower() == "base_already_broken"

    value_gap = decision_summary.get("value_gap")
    flex_before_break_pct = _normalize_percentish_value(decision_insurance_outputs.get("flex_before_break_pct"))
    flex_band_value = (
        decision_insurance_outputs.get("flex_before_break_band")
        if isinstance(decision_insurance_outputs.get("flex_before_break_band"), str)
        else flex_provenance.get("band")
    )
    has_tight_flex_band = (
        isinstance(flex_band_value, str) and "tight" in flex_band_value.strip().lower()
    )

    provenance = {
        "policy_id": policy_id,
        "status_source": "dealshield_policy_v1",
        "value_gap": float(value_gap) if _is_number(value_gap) else None,
        "not_modeled_reason": not_modeled_reason if isinstance(not_modeled_reason, str) else None,
        "first_break_scenario_id": first_break_scenario,
        "base_break_detected": bool(first_break_is_base or base_already_broken),
        "flex_before_break_pct_normalized": flex_before_break_pct,
        "flex_band": flex_band_value if isinstance(flex_band_value, str) else None,
    }

    if isinstance(not_modeled_reason, str) and not_modeled_reason.strip():
        return "PENDING", "not_modeled_inputs_missing", {**provenance}

    if first_break_is_base or base_already_broken:
        return "NO-GO", "base_case_break_condition", {**provenance}

    if _is_number(value_gap):
        if float(value_gap) <= 0:
            return "NO-GO", "base_value_gap_non_positive", {**provenance}
        if flex_before_break_pct is not None and flex_before_break_pct <= 2.0:
            return "Needs Work", "low_flex_before_break_buffer", {**provenance}
        return "GO", "base_value_gap_positive", {**provenance}

    if has_tight_flex_band:
        return "Needs Work", "tight_flex_band", {**provenance}

    if flex_before_break_pct is not None:
        if flex_before_break_pct <= 2.0:
            return "Needs Work", "low_flex_before_break_buffer", {**provenance}
        return "GO", "flex_before_break_buffer_positive", {**provenance}

    return "PENDING", "insufficient_modeled_inputs", {**provenance}


def build_dealshield_view_model(project_id: str, payload: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    view_model = build_dealshield_scenario_table(project_id, payload, profile)
    legacy_columns = copy.deepcopy(view_model.get("columns", []))
    legacy_rows = copy.deepcopy(view_model.get("rows", []))
    content_profile_id = _resolve_dealshield_content_profile_id(payload, profile)

    decision_table = _build_decision_table(payload, profile)
    financing_assumptions, dealshield_disclosures, decision_summary = _apply_display_guards(payload, decision_table)
    view_model["decision_table"] = decision_table
    view_model["legacy_scenario_table"] = {
        "columns": legacy_columns if isinstance(legacy_columns, list) else [],
        "rows": legacy_rows if isinstance(legacy_rows, list) else [],
    }
    view_model["columns"] = decision_table.get("columns", [])
    view_model["rows"] = decision_table.get("rows", [])

    context = _extract_dealshield_context(payload)
    if context:
        view_model["context"] = context
    scenario_inputs = _extract_dealshield_scenario_inputs(payload)
    provenance = view_model.get("provenance")
    if not isinstance(provenance, dict):
        provenance = {}
    resolved_tile_profile_id: Optional[str] = None
    profile_id = profile.get("profile_id")
    if isinstance(profile_id, str) and profile_id.strip():
        resolved_tile_profile_id = profile_id.strip()
    provenance["profile_id"] = resolved_tile_profile_id
    view_model["tile_profile_id"] = resolved_tile_profile_id

    resolved_content_profile_id = content_profile_id if isinstance(content_profile_id, str) and content_profile_id.strip() else None
    provenance["content_profile_id"] = resolved_content_profile_id
    view_model["content_profile_id"] = resolved_content_profile_id

    scope_items_profile_id = _resolve_scope_items_profile_id(payload)
    resolved_scope_items_profile_id = scope_items_profile_id if isinstance(scope_items_profile_id, str) and scope_items_profile_id.strip() else None
    provenance["scope_items_profile_id"] = resolved_scope_items_profile_id
    view_model["scope_items_profile_id"] = resolved_scope_items_profile_id
    provenance["scenario_inputs"] = scenario_inputs
    controls = _extract_dealshield_controls(payload)
    if controls:
        provenance["dealshield_controls"] = controls
    if financing_assumptions:
        view_model["financing_assumptions"] = copy.deepcopy(financing_assumptions)
        provenance["financing_assumptions"] = copy.deepcopy(financing_assumptions)
    if dealshield_disclosures:
        view_model["dealshield_disclosures"] = list(dealshield_disclosures)
        provenance["dealshield_disclosures"] = list(dealshield_disclosures)
    if isinstance(decision_summary, dict):
        summary_copy = copy.deepcopy(decision_summary)
        view_model["decision_summary"] = summary_copy
        view_model["cap_rate_used_pct"] = summary_copy.get("cap_rate_used_pct")
        view_model["value_gap"] = summary_copy.get("value_gap")
        view_model["value_gap_pct"] = summary_copy.get("value_gap_pct")
        provenance["decision_summary"] = summary_copy
    content_profile: Optional[Dict[str, Any]] = None
    if content_profile_id:
        try:
            content_profile = copy.deepcopy(get_dealshield_content_profile(content_profile_id))
        except KeyError:
            content_profile = None
        if isinstance(content_profile, dict):
            content_profile["resolved_drivers"] = _resolve_dealshield_content_drivers(
                content_profile, profile
            )
            view_model["content"] = content_profile

    decision_insurance_outputs, decision_insurance_provenance = _build_multifamily_decision_insurance(
        payload=payload,
        profile=profile,
        rows=view_model["rows"] if isinstance(view_model.get("rows"), list) else [],
        content=view_model.get("content") if isinstance(view_model.get("content"), dict) else None,
    )
    if decision_insurance_provenance:
        view_model["decision_insurance_provenance"] = copy.deepcopy(decision_insurance_provenance)
        provenance["decision_insurance"] = copy.deepcopy(decision_insurance_provenance)
        for output_key, output_value in decision_insurance_outputs.items():
            view_model[output_key] = output_value

    resolved_status, resolved_reason_code, status_provenance = _resolve_canonical_decision_status(
        payload=payload,
        decision_summary=decision_summary if isinstance(decision_summary, dict) else {},
        decision_insurance_outputs=decision_insurance_outputs if isinstance(decision_insurance_outputs, dict) else {},
        decision_insurance_provenance=decision_insurance_provenance if isinstance(decision_insurance_provenance, dict) else {},
    )
    view_model["decision_status"] = resolved_status
    view_model["decision_reason_code"] = resolved_reason_code
    view_model["decision_status_provenance"] = copy.deepcopy(status_provenance)
    if isinstance(decision_summary, dict):
        decision_summary["decision_status"] = resolved_status
        decision_summary["decision_reason_code"] = resolved_reason_code
        decision_summary["decision_status_provenance"] = copy.deepcopy(status_provenance)
    if isinstance(view_model.get("decision_summary"), dict):
        view_model["decision_summary"]["decision_status"] = resolved_status
        view_model["decision_summary"]["decision_reason_code"] = resolved_reason_code
        view_model["decision_summary"]["decision_status_provenance"] = copy.deepcopy(status_provenance)
    if isinstance(provenance.get("decision_summary"), dict):
        provenance["decision_summary"]["decision_status"] = resolved_status
        provenance["decision_summary"]["decision_reason_code"] = resolved_reason_code
        provenance["decision_summary"]["decision_status_provenance"] = copy.deepcopy(status_provenance)
    provenance["decision_status"] = resolved_status
    provenance["decision_reason_code"] = resolved_reason_code
    provenance["decision_status_provenance"] = copy.deepcopy(status_provenance)

    view_model["provenance"] = provenance
    return view_model
