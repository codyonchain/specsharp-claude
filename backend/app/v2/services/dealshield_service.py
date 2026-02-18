from __future__ import annotations

import copy
import json
import math
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from app.v2.config.type_profiles.dealshield_content import get_dealshield_content_profile

_MISSING = object()

_WAVE1_PROFILE_IDS: Set[str] = {
    "industrial_warehouse_v1",
    "industrial_cold_storage_v1",
    "healthcare_medical_office_building_v1",
    "healthcare_urgent_care_v1",
    "restaurant_quick_service_v1",
    "hospitality_limited_service_hotel_v1",
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
    profile_id = profile.get("profile_id")
    if isinstance(profile_id, str) and profile_id.strip():
        provenance["profile_id"] = profile_id.strip()
    if content_profile_id:
        provenance["content_profile_id"] = content_profile_id
    scope_items_profile_id = _resolve_scope_items_profile_id(payload)
    if scope_items_profile_id:
        provenance["scope_items_profile_id"] = scope_items_profile_id
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
    view_model["provenance"] = provenance

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
    return view_model
