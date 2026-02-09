#!/usr/bin/env python3
"""Generate subtype coverage matrix outputs for DealShield/Executive/Construction readiness."""

from __future__ import annotations

import ast
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[3]
SUBTYPES_DIR = ROOT / "backend" / "app" / "v2" / "config" / "subtypes"
TILES_DIR = ROOT / "backend" / "app" / "v2" / "config" / "type_profiles" / "dealshield_tiles"
CONTENT_DIR = ROOT / "backend" / "app" / "v2" / "config" / "type_profiles" / "dealshield_content"
DOCS_BUILDING_TYPES_DIR = ROOT / "docs" / "building_types"
STATUS_DIR = ROOT / "docs" / "status"

CSV_PATH = STATUS_DIR / "subtype_coverage_matrix.csv"
MD_PATH = STATUS_DIR / "subtype_coverage_matrix.md"
JSON_PATH = STATUS_DIR / "subtype_coverage_matrix.json"

COLUMNS = [
    "building_type",
    "subtype",
    "wave1",
    "dealshield_tile_profile",
    "dealshield_has_tile_profile",
    "dealshield_has_content_profile",
    "scope_items_profile",
    "scope_items_overrides",
    "facility_metrics_profile",
    "has_special_features",
    "subtype_doc_exists",
    "status",
]

WAVE1_SUBTYPES: Set[Tuple[str, str]] = {
    ("industrial", "warehouse"),
    ("industrial", "cold_storage"),
    ("healthcare", "medical_office_building"),
    ("healthcare", "urgent_care"),
    ("restaurant", "quick_service"),
    ("hospitality", "limited_service_hotel"),
}


def _parse_module(path: Path) -> ast.Module:
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path))


def _extract_literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _truthy_nonempty(node: Optional[ast.AST]) -> bool:
    if node is None:
        return False

    value = _extract_literal(node)
    if value is not None:
        if isinstance(value, (str, list, tuple, dict, set)):
            return len(value) > 0
        return bool(value)

    if isinstance(node, ast.Constant):
        return bool(node.value)
    if isinstance(node, ast.Dict):
        return len(node.keys) > 0
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return len(node.elts) > 0

    # Unknown dynamic expression: treat as configured.
    return True


def _string_value(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    value = _extract_literal(node)
    return value if isinstance(value, str) else ""


def _config_call_from_module(module: ast.Module) -> Optional[ast.Call]:
    for node in module.body:
        value: Optional[ast.AST] = None
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == "CONFIG" for target in node.targets):
                value = node.value
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "CONFIG":
                value = node.value

        if isinstance(value, ast.Tuple) and len(value.elts) >= 3:
            candidate = value.elts[2]
            if isinstance(candidate, ast.Call):
                return candidate
    return None


def _extract_subtype_signals(path: Path) -> Dict[str, Any]:
    module = _parse_module(path)
    config_call = _config_call_from_module(module)

    if not isinstance(config_call, ast.Call):
        return {
            "dealshield_tile_profile": "",
            "scope_items_profile": "",
            "scope_items_overrides": False,
            "facility_metrics_profile": "",
            "has_special_features": False,
        }

    kw_map = {kw.arg: kw.value for kw in config_call.keywords if kw.arg}

    return {
        "dealshield_tile_profile": _string_value(kw_map.get("dealshield_tile_profile")),
        "scope_items_profile": _string_value(kw_map.get("scope_items_profile")),
        "scope_items_overrides": _truthy_nonempty(kw_map.get("scope_items_overrides")),
        "facility_metrics_profile": _string_value(kw_map.get("facility_metrics_profile")),
        "has_special_features": _truthy_nonempty(kw_map.get("special_features")),
        # Additional scanned (currently not surfaced in table columns):
        "has_exclude_from_facility_opex": _truthy_nonempty(kw_map.get("exclude_from_facility_opex")),
        "project_timeline_profile": _string_value(kw_map.get("project_timeline_profile")),
    }


def _dict_keys_from_expr(node: ast.AST) -> Set[str]:
    if isinstance(node, ast.Dict):
        keys: Set[str] = set()
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.add(key.value)
        return keys
    return set()


def _collect_registry_profile_ids(directory: Path, variable_name: str) -> Set[str]:
    profile_ids: Set[str] = set()
    for path in sorted(directory.glob("*.py")):
        if path.name == "__init__.py":
            continue
        module = _parse_module(path)
        for node in module.body:
            value: Optional[ast.AST] = None
            if isinstance(node, ast.Assign):
                if any(isinstance(target, ast.Name) and target.id == variable_name for target in node.targets):
                    value = node.value
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == variable_name:
                    value = node.value
            if value is not None:
                profile_ids.update(_dict_keys_from_expr(value))
    return profile_ids


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _status_for_row(row: Dict[str, Any]) -> str:
    if row["wave1"] or (
        row["dealshield_has_tile_profile"]
        and row["dealshield_has_content_profile"]
        and bool(row["scope_items_profile"])
        and row["subtype_doc_exists"]
    ):
        return "✅"

    if (
        (row["dealshield_has_tile_profile"] and row["dealshield_has_content_profile"])
        or bool(row["scope_items_profile"])
        or row["subtype_doc_exists"]
    ):
        return "🟡"

    return "🔴"


def _iter_subtype_files() -> Iterable[Path]:
    for path in sorted(SUBTYPES_DIR.glob("*/*.py")):
        if path.name == "__init__.py":
            continue
        yield path


def _build_rows(tile_ids: Set[str], content_ids: Set[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for path in _iter_subtype_files():
        building_type = path.parent.name
        subtype = path.stem

        signals = _extract_subtype_signals(path)
        profile_id = signals["dealshield_tile_profile"]
        has_tile = bool(profile_id) and profile_id in tile_ids
        has_content = bool(profile_id) and profile_id in content_ids

        doc_path = DOCS_BUILDING_TYPES_DIR / building_type / "subtypes" / f"{subtype}.md"

        row: Dict[str, Any] = {
            "building_type": building_type,
            "subtype": subtype,
            "wave1": (building_type, subtype) in WAVE1_SUBTYPES,
            "dealshield_tile_profile": profile_id,
            "dealshield_has_tile_profile": has_tile,
            "dealshield_has_content_profile": has_content,
            "scope_items_profile": signals["scope_items_profile"],
            "scope_items_overrides": signals["scope_items_overrides"],
            "facility_metrics_profile": signals["facility_metrics_profile"],
            "has_special_features": signals["has_special_features"],
            "subtype_doc_exists": doc_path.exists(),
        }
        row["status"] = _status_for_row(row)
        rows.append(row)

    rows.sort(key=lambda item: (item["building_type"], item["subtype"]))
    return rows


def _write_csv(rows: List[Dict[str, Any]]) -> None:
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            serialized = dict(row)
            for key in (
                "wave1",
                "dealshield_has_tile_profile",
                "dealshield_has_content_profile",
                "scope_items_overrides",
                "has_special_features",
                "subtype_doc_exists",
            ):
                serialized[key] = _bool_text(bool(serialized[key]))
            writer.writerow(serialized)


def _write_markdown(rows: List[Dict[str, Any]]) -> None:
    header = "| " + " | ".join(COLUMNS) + " |"
    divider = "| " + " | ".join(["---"] * len(COLUMNS)) + " |"
    lines = [
        "# Subtype Coverage Matrix",
        "",
        header,
        divider,
    ]

    for row in rows:
        display_values: List[str] = []
        for col in COLUMNS:
            value = row[col]
            if isinstance(value, bool):
                display_values.append(_bool_text(value))
            else:
                display_values.append(str(value))
        lines.append("| " + " | ".join(display_values) + " |")

    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_rollups(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_type: Dict[str, Dict[str, int]] = {}
    totals: Dict[str, int] = {"✅": 0, "🟡": 0, "🔴": 0, "total": 0}

    grouped: Dict[str, Dict[str, int]] = defaultdict(lambda: {"✅": 0, "🟡": 0, "🔴": 0, "total": 0})

    for row in rows:
        status = row["status"]
        building_type = row["building_type"]
        grouped[building_type][status] += 1
        grouped[building_type]["total"] += 1
        totals[status] += 1
        totals["total"] += 1

    for building_type in sorted(grouped.keys()):
        by_type[building_type] = grouped[building_type]

    return {"by_type": by_type, "totals": totals}


def _write_json(rows: List[Dict[str, Any]], rollups: Dict[str, Any]) -> None:
    payload = {
        "columns": COLUMNS,
        "rows": rows,
        "rollups": rollups,
    }
    with JSON_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def main() -> None:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)

    tile_profile_ids = _collect_registry_profile_ids(TILES_DIR, "DEALSHIELD_TILE_PROFILES")
    content_profile_ids = _collect_registry_profile_ids(CONTENT_DIR, "DEALSHIELD_CONTENT_PROFILES")

    rows = _build_rows(tile_profile_ids, content_profile_ids)
    rollups = _build_rollups(rows)

    _write_csv(rows)
    _write_markdown(rows)
    _write_json(rows, rollups)

    print(f"Wrote: {CSV_PATH}")
    print(f"Wrote: {MD_PATH}")
    print(f"Wrote: {JSON_PATH}")


if __name__ == "__main__":
    main()
