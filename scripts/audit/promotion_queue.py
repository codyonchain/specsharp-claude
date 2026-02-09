#!/usr/bin/env python3
"""Generate deterministic promotion queue stubs from subtype coverage matrix output."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[2]
MATRIX_CANDIDATES = (
    ROOT / "subtype_coverage_matrix.json",
    ROOT / "docs" / "status" / "subtype_coverage_matrix.json",
)
STATUS_PRIORITY = {"red": 0, "yellow": 1, "green": 2}
STATUS_CANONICAL = {
    "🔴": "red",
    "red": "red",
    "🟡": "yellow",
    "yellow": "yellow",
    "✅": "green",
    "green": "green",
}


@dataclass(frozen=True)
class QueueItem:
    building_type: str
    subtype: str
    status: str
    status_display: str
    wave1: bool
    rationale: str
    files_to_touch: Tuple[str, ...]


def _fail(message: str, code: int = 1) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return code


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    if isinstance(value, (int, float)):
        return value != 0
    return False


def _canonical_status(value: Any) -> str:
    key = str(value).strip().lower()
    return STATUS_CANONICAL.get(str(value).strip(), STATUS_CANONICAL.get(key, "unknown"))


def _pick_matrix_path() -> Path | None:
    for candidate in MATRIX_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def _load_rows(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        rows = payload.get("rows")
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    raise ValueError(f"Unsupported matrix JSON shape in {path}")


def _build_rationale(row: Dict[str, Any]) -> str:
    notes: List[str] = []
    status = _canonical_status(row.get("status", ""))
    if status == "red":
        notes.append("red coverage (highest priority)")
    elif status == "yellow":
        notes.append("yellow coverage (next priority)")
    elif status == "green":
        notes.append("green coverage (lowest priority)")
    else:
        notes.append("unknown coverage status")

    if _as_bool(row.get("wave1")):
        notes.append("wave1 baseline subtype")

    profile_id = str(row.get("dealshield_tile_profile", "")).strip()
    has_tile = _as_bool(row.get("dealshield_has_tile_profile"))
    has_content = _as_bool(row.get("dealshield_has_content_profile"))
    has_scope_profile = bool(str(row.get("scope_items_profile", "")).strip())
    has_doc = _as_bool(row.get("subtype_doc_exists"))

    if not profile_id:
        notes.append("dealshield_tile_profile missing")
    else:
        if not has_tile:
            notes.append("tile profile not found in registry")
        if not has_content:
            notes.append("content profile not found in registry")

    if not has_scope_profile:
        notes.append("scope_items_profile missing")
    if not has_doc:
        notes.append("subtype doc missing")

    return "; ".join(notes)


def _files_to_touch(row: Dict[str, Any]) -> Tuple[str, ...]:
    building_type = str(row.get("building_type", "")).strip()
    subtype = str(row.get("subtype", "")).strip()
    if not building_type or not subtype:
        return tuple()

    files = [
        f"backend/app/v2/config/subtypes/{building_type}/{subtype}.py",
        f"backend/app/v2/config/type_profiles/dealshield_tiles/{building_type}.py",
        f"backend/app/v2/config/type_profiles/dealshield_content/{building_type}.py",
        f"backend/app/v2/config/type_profiles/scope_items/{building_type}.py",
        f"docs/building_types/{building_type}/subtypes/{subtype}.md",
        "scripts/audit/parity/fixtures/basic_fixtures.json",
    ]
    return tuple(files)


def _build_queue(rows: Iterable[Dict[str, Any]], building_type_filter: str | None) -> List[QueueItem]:
    items: List[QueueItem] = []

    for row in rows:
        building_type = str(row.get("building_type", "")).strip()
        subtype = str(row.get("subtype", "")).strip()
        if not building_type or not subtype:
            continue
        if building_type_filter and building_type != building_type_filter:
            continue

        status = _canonical_status(row.get("status", ""))
        status_display = str(row.get("status", "")).strip() or "unknown"
        items.append(
            QueueItem(
                building_type=building_type,
                subtype=subtype,
                status=status,
                status_display=status_display,
                wave1=_as_bool(row.get("wave1")),
                rationale=_build_rationale(row),
                files_to_touch=_files_to_touch(row),
            )
        )

    return sorted(
        items,
        key=lambda item: (
            STATUS_PRIORITY.get(item.status, 99),
            item.building_type,
            item.subtype,
        ),
    )


def _split_stub_files(item: QueueItem) -> Tuple[List[str], List[Tuple[str, str | None]]]:
    shared_paths = {
        f"backend/app/v2/config/type_profiles/dealshield_tiles/{item.building_type}.py",
        f"backend/app/v2/config/type_profiles/dealshield_content/{item.building_type}.py",
        f"backend/app/v2/config/type_profiles/scope_items/{item.building_type}.py",
        "scripts/audit/parity/fixtures/basic_fixtures.json",
    }
    shared_notes = {
        "scripts/audit/parity/fixtures/basic_fixtures.json": "only if adding fixture.",
    }

    subtype_specific: List[str] = []
    shared: List[Tuple[str, str | None]] = []
    for file_path in item.files_to_touch:
        if file_path in shared_paths:
            shared.append((file_path, shared_notes.get(file_path)))
        else:
            subtype_specific.append(file_path)
    return subtype_specific, shared


def _render_markdown(matrix_path: Path, queue: Sequence[QueueItem], limit: int, building_type_filter: str | None) -> str:
    top = list(queue[:limit])
    lines: List[str] = []
    lines.append("# Promotion Queue")
    lines.append("")
    lines.append(f"- Matrix source: `{matrix_path.relative_to(ROOT)}`")
    lines.append(f"- Total candidates: {len(queue)}")
    lines.append(f"- Building type filter: `{building_type_filter or 'all'}`")
    lines.append(f"- Showing top: {len(top)}")
    lines.append("")
    lines.append("## Ranked Candidates")
    lines.append("")

    for index, item in enumerate(top, start=1):
        lines.append(
            f"{index}. `{item.building_type}/{item.subtype}` "
            f"({item.status_display} -> {item.status.upper()}) - {item.rationale}"
        )

    lines.append("")
    lines.append("## Work Order Stubs")
    lines.append("")
    for item in top:
        subtype_specific_files, shared_files = _split_stub_files(item)
        lines.append(f"### `{item.building_type}/{item.subtype}`")
        lines.append(f"- Priority: `{item.status.upper()}`")
        lines.append(f"- Rationale: {item.rationale}")
        lines.append("- Files to touch:")
        lines.append("  - Subtype-specific files (safe to parallelize):")
        if subtype_specific_files:
            for file_path in subtype_specific_files:
                lines.append(f"    - `{file_path}`")
        else:
            lines.append("    - _(none)_")
        lines.append("  - Shared type-level files (one-agent ownership):")
        if shared_files:
            for file_path, note in shared_files:
                if note:
                    lines.append(f"    - `{file_path}` ({note})")
                else:
                    lines.append(f"    - `{file_path}`")
        else:
            lines.append("    - _(none)_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_json(matrix_path: Path, queue: Sequence[QueueItem], limit: int, building_type_filter: str | None) -> str:
    top = list(queue[:limit])
    payload = {
        "matrix_path": str(matrix_path.relative_to(ROOT)),
        "total_candidates": len(queue),
        "filter": {"building_type": building_type_filter or "all"},
        "limit": limit,
        "ranked": [
            {
                "rank": index,
                "building_type": item.building_type,
                "subtype": item.subtype,
                "status": item.status,
                "status_display": item.status_display,
                "wave1": item.wave1,
                "rationale": item.rationale,
            }
            for index, item in enumerate(top, start=1)
        ],
        "work_orders": [
            {
                "building_type": item.building_type,
                "subtype": item.subtype,
                "status": item.status,
                "files_to_touch": list(item.files_to_touch),
            }
            for item in top
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--type", dest="building_type", help="filter to one building type")
    parser.add_argument("--limit", type=int, default=10, help="top N candidates to output (default: 10)")
    parser.add_argument("--format", choices=("md", "json"), default="md", help="output format")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.limit < 1:
        return _fail("--limit must be >= 1", code=2)

    matrix_path = _pick_matrix_path()
    if matrix_path is None:
        print("ERROR: matrix JSON not found. Expected one of:", file=sys.stderr)
        for candidate in MATRIX_CANDIDATES:
            print(f"- {candidate.relative_to(ROOT)}", file=sys.stderr)
        print(
            "Generate it first with: python3 scripts/audit/status/generate_coverage_matrix.py",
            file=sys.stderr,
        )
        return 2

    try:
        rows = _load_rows(matrix_path)
    except Exception as exc:
        return _fail(str(exc), code=2)

    queue = _build_queue(rows, args.building_type)
    if args.format == "json":
        sys.stdout.write(_render_json(matrix_path, queue, args.limit, args.building_type))
    else:
        sys.stdout.write(_render_markdown(matrix_path, queue, args.limit, args.building_type))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
