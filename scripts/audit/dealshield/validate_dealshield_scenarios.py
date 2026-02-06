#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List

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

    if failures:
        print("FAIL: DealShield scenario validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: DealShield scenarios validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
