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

_DECISION_TABLE_COLUMNS: List[Dict[str, str]] = [
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


def _resolve_profile_scenario_rows(profile: Dict[str, Any]) -> List[Dict[str, str]]:
    derived_rows = profile.get("derived_rows")
    if not isinstance(derived_rows, list):
        return [{"scenario_id": "base", "label": "Base"}]

    rows: List[Dict[str, str]] = [{"scenario_id": "base", "label": "Base"}]
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
        rows.append({"scenario_id": normalized_id, "label": label})
    return rows


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


def _apply_display_guards(
    payload: Dict[str, Any],
    decision_table: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    columns = decision_table.get("columns")
    if not isinstance(columns, list):
        columns = []
        decision_table["columns"] = columns

    rows = decision_table.get("rows")
    if not isinstance(rows, list):
        rows = []
        decision_table["rows"] = rows

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
        cap_rate_value = None

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

    if not has_financing_assumptions:
        financing_assumptions = {}

    return financing_assumptions, disclosures


def _build_decision_table(payload: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    columns: List[Dict[str, Any]] = []
    for col in _DECISION_TABLE_COLUMNS:
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

    rows: List[Dict[str, Any]] = []
    for row in scenario_rows:
        scenario_id = row["scenario_id"]
        label = row["label"]
        scenario_snapshot = _resolve_dealshield_scenario_snapshot(payload, scenario_id)

        if is_wave1_profile and scenario_snapshot is None:
            raise DealShieldResolutionError(
                f"Wave-1 profile '{profile_id}' missing dealshield_scenarios snapshot for scenario '{scenario_id}'"
            )

        cells: List[Dict[str, Any]] = []
        for col in columns:
            metric_ref = col["metric_ref"]
            col_id = col["id"]

            if is_wave1_profile:
                raw_snapshot_value = _resolve_metric_ref(scenario_snapshot or {}, metric_ref)
                if raw_snapshot_value is _MISSING or not _is_number(raw_snapshot_value):
                    raise DealShieldResolutionError(
                        f"Wave-1 profile '{profile_id}' missing/non-numeric snapshot metric_ref "
                        f"'{metric_ref}' for scenario '{scenario_id}'"
                    )

            value, source_path, provenance_kind = _resolve_decision_value(payload, scenario_id, metric_ref)
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

        rows.append({"scenario_id": scenario_id, "label": label, "cells": cells})

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
    return copy.deepcopy(controls)


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

    decision_table = _build_decision_table(payload, profile)
    financing_assumptions, dealshield_disclosures = _apply_display_guards(payload, decision_table)
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
    provenance["scenario_inputs"] = scenario_inputs
    provenance["dealshield_controls"] = _extract_dealshield_controls(payload)
    if financing_assumptions:
        view_model["financing_assumptions"] = copy.deepcopy(financing_assumptions)
        provenance["financing_assumptions"] = copy.deepcopy(financing_assumptions)
    if dealshield_disclosures:
        view_model["dealshield_disclosures"] = list(dealshield_disclosures)
        provenance["dealshield_disclosures"] = list(dealshield_disclosures)
    view_model["provenance"] = provenance

    content_profile_id = _resolve_dealshield_content_profile_id(payload, profile)
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
