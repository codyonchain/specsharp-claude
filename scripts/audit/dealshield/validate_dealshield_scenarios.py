#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
PARITY_DIR = ROOT / "scripts" / "audit" / "parity"

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(PARITY_DIR))

from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile  # noqa: E402
from app.v2.services.dealshield_service import build_dealshield_scenario_table  # noqa: E402
from app.v2.services.dealshield_scenarios import WAVE1_PROFILES  # noqa: E402
from run_parity import get_fixture_outputs  # noqa: E402


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
            return None
        current = current[part]
    return current


def _expected_scenario_ids(profile: Dict[str, Any]) -> List[str]:
    derived_rows = profile.get("derived_rows") or []
    scenario_ids: List[str] = ["base"]
    for row in derived_rows:
        if not isinstance(row, dict):
            continue
        scenario_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if isinstance(scenario_id, str) and scenario_id.strip():
            scenario_ids.append(scenario_id.strip())
    return scenario_ids


def _normalize_transforms(transform: Any) -> List[Dict[str, Any]]:
    if transform is None:
        return []
    if isinstance(transform, dict):
        return [transform]
    if isinstance(transform, list) and all(isinstance(item, dict) for item in transform):
        return list(transform)
    raise ValueError("Transform must be dict or list of dicts")


def _apply_transform(value: float, transform: Dict[str, Any]) -> float:
    op = transform.get("op")
    operand = transform.get("value")
    if not _is_number(operand):
        raise ValueError("Transform value must be numeric")
    operand_value = float(operand)
    if op == "mul":
        return value * operand_value
    if op == "add":
        return value + operand_value
    if op == "sub":
        return value - operand_value
    if op == "div":
        if operand_value == 0:
            raise ValueError("Transform division by zero")
        return value / operand_value
    raise ValueError(f"Unsupported transform op: {op}")


def _apply_transforms(value: float, transforms: List[Dict[str, Any]]) -> float:
    output = float(value)
    for transform in transforms:
        output = _apply_transform(output, transform)
    return output


def _scenario_rows(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    derived_rows = profile.get("derived_rows") or []
    rows: List[Dict[str, Any]] = []
    for row in derived_rows:
        if not isinstance(row, dict):
            continue
        scenario_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            continue
        rows.append({
            "scenario_id": scenario_id.strip(),
            "apply_tiles": row.get("apply_tiles") if isinstance(row.get("apply_tiles"), list) else [],
            "plus_tiles": row.get("plus_tiles") if isinstance(row.get("plus_tiles"), list) else [],
        })
    return rows


def _is_close(left: float, right: float, tol: float = 0.01) -> bool:
    return math.isclose(left, right, rel_tol=1e-6, abs_tol=tol)


def run() -> int:
    fixtures = get_fixture_outputs()
    failures: List[str] = []

    for fixture in fixtures:
        name = fixture.get("name") or "<unknown>"
        payload = fixture.get("payload")
        if not isinstance(payload, dict):
            continue

        profile_id = payload.get("dealshield_tile_profile")
        if profile_id not in WAVE1_PROFILES:
            continue

        profile = get_dealshield_profile(profile_id)
        expected_scenarios = _expected_scenario_ids(profile)
        tiles = profile.get("tiles") or []
        tile_metric_refs = [tile.get("metric_ref") for tile in tiles if isinstance(tile, dict)]
        tile_by_id = {
            tile.get("tile_id"): tile
            for tile in tiles
            if isinstance(tile, dict) and tile.get("tile_id")
        }

        ds_block = payload.get("dealshield_scenarios")
        if not isinstance(ds_block, dict):
            failures.append(f"{name}: missing dealshield_scenarios block")
            continue

        scenarios = ds_block.get("scenarios")
        if not isinstance(scenarios, dict):
            failures.append(f"{name}: dealshield_scenarios.scenarios missing")
            continue

        for scenario_id in expected_scenarios:
            scenario_payload = scenarios.get(scenario_id)
            if not isinstance(scenario_payload, dict):
                failures.append(f"{name}: scenario '{scenario_id}' missing")
                continue
            for metric_ref in tile_metric_refs:
                value = _resolve_metric_ref(scenario_payload, metric_ref)
                if not _is_number(value):
                    failures.append(
                        f"{name}: scenario '{scenario_id}' missing numeric '{metric_ref}'"
                    )

        table = build_dealshield_scenario_table(name, payload, profile)
        for row in table.get("rows", []):
            for cell in row.get("cells", []):
                if cell.get("coverage") != "complete":
                    failures.append(
                        f"{name}: coverage not complete for scenario '{row.get('scenario_id')}'"
                    )

        base_payload = scenarios.get("base") if isinstance(scenarios, dict) else None
        if not isinstance(base_payload, dict):
            failures.append(f"{name}: base scenario missing or invalid")
            continue

        base_total = _resolve_metric_ref(base_payload, "totals.total_project_cost")
        base_revenue = _resolve_metric_ref(base_payload, "revenue_analysis.annual_revenue")
        if not _is_number(base_total) or not _is_number(base_revenue):
            failures.append(f"{name}: base totals/revenue missing numeric values")
            continue

        for row in _scenario_rows(profile):
            scenario_id = row["scenario_id"]
            scenario_payload = scenarios.get(scenario_id)
            if not isinstance(scenario_payload, dict):
                continue

            cost_transforms: List[Dict[str, Any]] = []
            revenue_transforms: List[Dict[str, Any]] = []
            driver_tiles: List[Tuple[str, List[Dict[str, Any]]]] = []

            tile_ids = list(row["apply_tiles"]) + list(row["plus_tiles"])
            for tile_id in tile_ids:
                tile = tile_by_id.get(tile_id)
                if not tile:
                    continue
                metric_ref = tile.get("metric_ref")
                transforms = _normalize_transforms(tile.get("transform"))
                if metric_ref == "totals.total_project_cost":
                    cost_transforms.extend(transforms)
                elif metric_ref == "revenue_analysis.annual_revenue":
                    revenue_transforms.extend(transforms)
                elif tile_id in row["plus_tiles"]:
                    driver_tiles.append((metric_ref, transforms))

            expected_total = _apply_transforms(float(base_total), cost_transforms) if cost_transforms else float(base_total)
            expected_revenue = _apply_transforms(float(base_revenue), revenue_transforms) if revenue_transforms else float(base_revenue)

            scenario_total = _resolve_metric_ref(scenario_payload, "totals.total_project_cost")
            scenario_revenue = _resolve_metric_ref(scenario_payload, "revenue_analysis.annual_revenue")

            if _is_number(scenario_revenue):
                if not _is_close(float(scenario_revenue), expected_revenue):
                    failures.append(
                        f"{name}: scenario '{scenario_id}' annual_revenue not expected"
                    )

            for metric_ref, transforms in driver_tiles:
                base_driver = _resolve_metric_ref(base_payload, metric_ref)
                scenario_driver = _resolve_metric_ref(scenario_payload, metric_ref)
                if not _is_number(base_driver) or not _is_number(scenario_driver):
                    failures.append(
                        f"{name}: scenario '{scenario_id}' driver '{metric_ref}' missing"
                    )
                    continue
                expected_driver = _apply_transforms(float(base_driver), transforms)
                expected_total += (expected_driver - float(base_driver))
                if not _is_close(float(scenario_driver), expected_driver):
                    failures.append(
                        f"{name}: scenario '{scenario_id}' driver '{metric_ref}' not expected"
                    )

                if scenario_id == "ugly":
                    conservative_payload = scenarios.get("conservative")
                    conservative_driver = None
                    if isinstance(conservative_payload, dict):
                        conservative_driver = _resolve_metric_ref(conservative_payload, metric_ref)
                    if _is_number(conservative_driver):
                        if not _is_close(float(conservative_driver), float(base_driver)):
                            failures.append(
                                f"{name}: conservative changed driver '{metric_ref}' unexpectedly"
                            )
                        if float(scenario_driver) < float(conservative_driver):
                            failures.append(
                                f"{name}: ugly driver '{metric_ref}' not >= conservative"
                            )

            if _is_number(scenario_total):
                if not _is_close(float(scenario_total), expected_total):
                    failures.append(
                        f"{name}: scenario '{scenario_id}' total_project_cost not expected"
                    )

            if scenario_id == "ugly":
                conservative_payload = scenarios.get("conservative")
                conservative_total = None
                if isinstance(conservative_payload, dict):
                    conservative_total = _resolve_metric_ref(conservative_payload, "totals.total_project_cost")
                if _is_number(conservative_total) and _is_number(scenario_total):
                    if float(scenario_total) < float(conservative_total):
                        failures.append(
                            f"{name}: ugly total_project_cost not >= conservative"
                        )

    if failures:
        print("FAIL: DealShield scenario validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: DealShield scenarios validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
