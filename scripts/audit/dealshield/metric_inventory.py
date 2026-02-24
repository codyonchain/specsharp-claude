#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parents[3]
PARITY_DIR = ROOT / "scripts" / "audit" / "parity"

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(PARITY_DIR))

from app.v2.engines.unified_engine import UnifiedEngine  # noqa: E402
from app.v2.config.master_config import (  # noqa: E402
    BuildingType,
    ProjectClass,
    OwnershipType,
)
from fixtures import load_fixtures  # noqa: E402


SKIP_KEYS = {"timestamp", "calculation_trace"}

COST_CANDIDATES = [
    "totals.total_project_cost",
    "totals.hard_costs",
    "construction_costs.construction_total",
]

REVENUE_CANDIDATES = [
    "revenue_analysis.annual_revenue",
    "totals.annual_revenue",
    "revenue_requirements.annual_revenue",
]

NOI_CANDIDATES = [
    "return_metrics.estimated_annual_noi",
    "revenue_analysis.net_income",
    "ownership_analysis.return_metrics.estimated_annual_noi",
]


def _resolve_project_class(value: Optional[str]) -> ProjectClass:
    if not value:
        return ProjectClass.GROUND_UP
    try:
        return ProjectClass(value)
    except Exception:
        return ProjectClass.GROUND_UP


def _resolve_ownership_type(value: Optional[str]) -> OwnershipType:
    if not value:
        return OwnershipType.FOR_PROFIT
    try:
        return OwnershipType(value)
    except Exception:
        return OwnershipType.FOR_PROFIT


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return False
        return True
    return False


def _format_example(value: Any) -> str:
    return repr(value)


def _collect_numeric_paths(
    obj: Any,
    path: str,
    fixture_id: str,
    fixture_paths: Set[str],
    registry: Dict[str, Dict[str, Any]],
) -> None:
    if _is_number(obj):
        fixture_paths.add(path)
        info = registry.setdefault(
            path,
            {
                "types": set(),
                "example": None,
                "example_fixture": None,
                "fixtures": set(),
            },
        )
        info["fixtures"].add(fixture_id)
        info["types"].add("int" if isinstance(obj, int) and not isinstance(obj, bool) else "float")
        if info["example"] is None:
            info["example"] = obj
            info["example_fixture"] = fixture_id
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in SKIP_KEYS:
                continue
            next_path = f"{path}.{key}" if path else key
            _collect_numeric_paths(value, next_path, fixture_id, fixture_paths, registry)
        return

    if isinstance(obj, list):
        next_path = f"{path}[]" if path else "[]"
        for item in obj:
            _collect_numeric_paths(item, next_path, fixture_id, fixture_paths, registry)
        return


def _run_fixture(engine: UnifiedEngine, fixture: Dict[str, Any]) -> Dict[str, Any]:
    building_type = BuildingType(fixture["building_type"])
    subtype = fixture["subtype"]
    square_footage = fixture["square_footage"]
    project_class = _resolve_project_class(fixture.get("project_class"))
    finish_level = fixture.get("finish_level")

    extra_inputs = fixture.get("extra_inputs") or {}
    location = extra_inputs.get("location", "Nashville, TN")
    floors = extra_inputs.get("floors", 1)
    ownership_type = _resolve_ownership_type(extra_inputs.get("ownership_type"))
    special_features = extra_inputs.get("special_features")
    parsed_input_overrides = extra_inputs.get("parsed_input_overrides")

    return engine.calculate_project(
        building_type=building_type,
        subtype=subtype,
        square_footage=square_footage,
        location=location,
        project_class=project_class,
        floors=floors,
        ownership_type=ownership_type,
        finish_level=finish_level,
        special_features=special_features,
        parsed_input_overrides=parsed_input_overrides,
    )


def _pick_best_candidate(
    candidates: List[str],
    registry: Dict[str, Dict[str, Any]],
) -> Tuple[Optional[str], int]:
    best_path = None
    best_count = -1
    for path in candidates:
        info = registry.get(path)
        if not info:
            continue
        count = len(info["fixtures"])
        if count > best_count:
            best_path = path
            best_count = count
    return best_path, best_count


def run() -> int:
    fixtures = load_fixtures()
    fixtures = sorted(fixtures, key=lambda item: item.get("id", ""))

    engine = UnifiedEngine()

    registry: Dict[str, Dict[str, Any]] = {}
    fixture_paths: Dict[str, Set[str]] = {}
    fixture_meta: Dict[str, Dict[str, str]] = {}

    for fixture in fixtures:
        fixture_id = fixture.get("id", "<missing-id>")
        fixture_meta[fixture_id] = {
            "building_type": fixture.get("building_type", ""),
            "subtype": fixture.get("subtype", ""),
        }
        result = _run_fixture(engine, fixture)
        paths: Set[str] = set()
        _collect_numeric_paths(result, "", fixture_id, paths, registry)
        fixture_paths[fixture_id] = paths

    fixture_ids = sorted(fixture_paths.keys())
    print(f"Metric inventory (fixtures: {len(fixture_ids)})")
    for path in sorted(registry.keys()):
        info = registry[path]
        types = "|".join(sorted(info["types"]))
        example = _format_example(info["example"])
        count = len(info["fixtures"])
        print(f"{path} | {types} | {example} | {count}/{len(fixture_ids)}")

    cost_best, cost_count = _pick_best_candidate(COST_CANDIDATES, registry)
    revenue_best, revenue_count = _pick_best_candidate(REVENUE_CANDIDATES, registry)
    noi_best, noi_count = _pick_best_candidate(NOI_CANDIDATES, registry)

    print("")
    print("Recommended refs")
    if cost_best:
        print(f"cost_base: {cost_best} (present {cost_count}/{len(fixture_ids)})")
    else:
        print("cost_base: <none found>")
    if revenue_best:
        print(f"revenue_base: {revenue_best} (present {revenue_count}/{len(fixture_ids)})")
    elif noi_best:
        print(f"revenue_base: <none found>; fallback_noi: {noi_best} (present {noi_count}/{len(fixture_ids)})")
    else:
        print("revenue_base: <none found>; fallback_noi: <none found>")

    print("")
    print("Fixture coverage (recommended candidates)")
    for fixture_id in fixture_ids:
        paths = fixture_paths[fixture_id]
        cost_pick = next((p for p in COST_CANDIDATES if p in paths), None)
        revenue_pick = next((p for p in REVENUE_CANDIDATES if p in paths), None)
        noi_pick = next((p for p in NOI_CANDIDATES if p in paths), None)
        coverage_note = "revenue" if revenue_pick else ("noi" if noi_pick else "missing")
        chosen_revenue = revenue_pick or noi_pick or "<none>"
        meta = fixture_meta.get(fixture_id, {})
        subtype = meta.get("subtype", "")
        building_type = meta.get("building_type", "")
        print(
            f"{fixture_id} [{building_type}/{subtype}] "
            f"cost={cost_pick or '<none>'} "
            f"revenue={chosen_revenue} ({coverage_note})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(run())
