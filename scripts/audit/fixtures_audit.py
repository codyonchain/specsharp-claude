#!/usr/bin/env python3
"""Audit parity fixtures so promoted subtypes always have fixture coverage."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[2]
MATRIX_CANDIDATES = (
    ROOT / "subtype_coverage_matrix.json",
    ROOT / "docs" / "status" / "subtype_coverage_matrix.json",
)
STATUS_CANONICAL = {
    "✅": "green",
    "green": "green",
    "🟡": "yellow",
    "yellow": "yellow",
    "🔴": "red",
    "red": "red",
}


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _canonical_status(value: Any) -> str:
    raw = str(value).strip()
    return STATUS_CANONICAL.get(raw, STATUS_CANONICAL.get(raw.lower(), "unknown"))


def _pick_matrix_path() -> Path | None:
    for path in MATRIX_CANDIDATES:
        if path.is_file():
            return path
    return None


def _load_rows(matrix_path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(matrix_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    raise ValueError(f"Unsupported matrix format in {matrix_path}")


def _promoted_pairs(rows: Iterable[Dict[str, Any]]) -> Set[Tuple[str, str]]:
    promoted: Set[Tuple[str, str]] = set()
    for row in rows:
        building_type = str(row.get("building_type", "")).strip()
        subtype = str(row.get("subtype", "")).strip()
        if not building_type or not subtype:
            continue
        wave1 = _as_bool(row.get("wave1"))
        status = _canonical_status(row.get("status", ""))
        if wave1 or status == "green":
            promoted.add((building_type, subtype))
    return promoted


def _fixture_dir() -> Path:
    parity_dir = ROOT / "scripts" / "audit" / "parity"
    if not parity_dir.is_dir():
        raise RuntimeError("TODO: parity directory missing at scripts/audit/parity")

    fixture_dirs = sorted({path.resolve() for path in parity_dir.rglob("fixtures") if path.is_dir()})
    if not fixture_dirs:
        raise RuntimeError("TODO: no parity fixtures directory found under scripts/audit/parity")
    if len(fixture_dirs) > 1:
        options = "\n".join(f"- {path}" for path in fixture_dirs)
        raise RuntimeError(f"TODO: fixture location ambiguous; found multiple directories:\n{options}")
    return fixture_dirs[0]


def _collect_pairs(node: Any, sink: Set[Tuple[str, str]]) -> None:
    if isinstance(node, dict):
        building_type = node.get("building_type")
        subtype = node.get("subtype")
        if isinstance(building_type, str) and isinstance(subtype, str):
            sink.add((building_type.strip(), subtype.strip()))
        for value in node.values():
            _collect_pairs(value, sink)
    elif isinstance(node, list):
        for item in node:
            _collect_pairs(item, sink)


def _fixture_pairs(fixtures_dir: Path) -> Set[Tuple[str, str]]:
    json_files = sorted(fixtures_dir.rglob("*.json"))
    if not json_files:
        raise RuntimeError(f"TODO: no JSON fixtures found in {fixtures_dir}")

    pairs: Set[Tuple[str, str]] = set()
    for fixture_file in json_files:
        try:
            payload = json.loads(fixture_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"TODO: could not parse fixture JSON {fixture_file}: {exc}") from exc
        _collect_pairs(payload, pairs)

    normalized = {(building_type, subtype) for building_type, subtype in pairs if building_type and subtype}
    if not normalized:
        raise RuntimeError(
            f"TODO: fixture matching convention is ambiguous in {fixtures_dir}; "
            "no (building_type, subtype) tokens were found in JSON payloads."
        )
    return normalized


def main() -> int:
    matrix_path = _pick_matrix_path()
    if matrix_path is None:
        print("ERROR: subtype coverage matrix JSON not found.", file=sys.stderr)
        print("Expected one of:", file=sys.stderr)
        for candidate in MATRIX_CANDIDATES:
            print(f"- {candidate.relative_to(ROOT)}", file=sys.stderr)
        print(
            "Generate it first with: python3 scripts/audit/status/generate_coverage_matrix.py",
            file=sys.stderr,
        )
        return 2

    try:
        rows = _load_rows(matrix_path)
        promoted = _promoted_pairs(rows)
        fixtures_dir = _fixture_dir()
        fixture_pairs = _fixture_pairs(fixtures_dir)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    missing = sorted(pair for pair in promoted if pair not in fixture_pairs)

    print(f"Matrix source: {matrix_path.relative_to(ROOT)}")
    print(f"Fixtures directory: {fixtures_dir.relative_to(ROOT)}")
    print(f"Promoted subtypes: {len(promoted)}")
    print(f"Fixture-covered promoted subtypes: {len(promoted) - len(missing)}")

    if missing:
        print("Promoted subtypes missing fixtures:")
        for building_type, subtype in missing:
            print(f"- {building_type}/{subtype}")
        return 1

    print("All promoted subtypes have fixture coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
