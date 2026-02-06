from __future__ import annotations

import json
import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

_MISSING = object()

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


def _extract_dealshield_scenario_inputs(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ds_block = payload.get("dealshield_scenarios")
    if not isinstance(ds_block, dict):
        return None
    provenance = ds_block.get("provenance")
    if not isinstance(provenance, dict):
        return None
    scenario_inputs = provenance.get("scenario_inputs")
    if not isinstance(scenario_inputs, dict):
        return None
    return scenario_inputs


def build_dealshield_view_model(project_id: str, payload: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    view_model = build_dealshield_scenario_table(project_id, payload, profile)
    context = _extract_dealshield_context(payload)
    if context:
        view_model["context"] = context
    scenario_inputs = _extract_dealshield_scenario_inputs(payload)
    if scenario_inputs:
        provenance = view_model.get("provenance")
        if not isinstance(provenance, dict):
            provenance = {}
        provenance["scenario_inputs"] = scenario_inputs
        view_model["provenance"] = provenance
    return view_model
