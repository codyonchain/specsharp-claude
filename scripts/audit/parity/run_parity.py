#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
PARITY_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(PARITY_DIR))

from app.v2.engines.unified_engine import UnifiedEngine  # noqa: E402
from app.v2.config.master_config import (  # noqa: E402
    BuildingType,
    ProjectClass,
    OwnershipType,
    get_building_config,
)
from fixtures import load_fixtures  # noqa: E402


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


def _find_clamp_trace(trace: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for entry in trace or []:
        if entry.get("step") == "restaurant_cost_clamp":
            return entry.get("data") or {}
    return None


def _compute_signature(engine: UnifiedEngine, fixture: Dict[str, Any]) -> Dict[str, Any]:
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

    result = engine.calculate_project(
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

    signature: Dict[str, Any] = {
        "building_type": fixture["building_type"],
        "subtype": subtype,
    }

    building_config = get_building_config(building_type, subtype)

    if building_type == BuildingType.RESTAURANT:
        cost_clamp = getattr(building_config, "cost_clamp", None) or {}
        min_cost = cost_clamp.get("min_cost_per_sf", 250)
        max_cost = cost_clamp.get("max_cost_per_sf", 700)
        clamp_trace = _find_clamp_trace(result.get("calculation_trace", []))
        signature.update(
            {
                "min_cost_per_sf": min_cost,
                "max_cost_per_sf": max_cost,
                "cost_per_sf_before": clamp_trace.get("original_cost_per_sf") if clamp_trace else None,
                "cost_per_sf_after": result.get("totals", {}).get("cost_per_sf"),
                "clamp_applied_mode": clamp_trace.get("mode") if clamp_trace else None,
            }
        )

    if building_type == BuildingType.INDUSTRIAL:
        scope_profile = getattr(building_config, "scope_profile", None) if building_config else None
        signature.update(
            {
                "scope_profile": scope_profile,
                "scope_items_count": len(result.get("scope_items") or []),
                "finishes_trade_total": (result.get("trade_breakdown") or {}).get("finishes"),
                "is_flex": scope_profile == "industrial_flex",
                "is_cold_storage": scope_profile == "industrial_cold_storage",
            }
        )

    if building_type == BuildingType.HEALTHCARE:
        facility_profile = getattr(building_config, "facility_metrics_profile", None) if building_config else None
        facility_metrics = result.get("facility_metrics")
        signature.update(
            {
                "facility_metrics_profile": facility_profile,
                "outpatient_mode": facility_profile == "healthcare_outpatient",
                "metrics_shape_keyset": sorted(facility_metrics.keys()) if isinstance(facility_metrics, dict) else [],
            }
        )

    if subtype == "manufacturing":
        operational_efficiency = result.get("operational_efficiency") or {}
        excluded_attrs = [
            key for key in ("labor_cost", "raw_materials") if key in operational_efficiency
        ]
        sample_included = [
            key
            for key in ("utility_cost", "maintenance_cost", "property_tax")
            if key in operational_efficiency
        ]
        signature.update(
            {
                "excluded_attrs_present": excluded_attrs,
                "computed_attrs_present": sorted(sample_included),
            }
        )

    return signature


def run() -> int:
    fixtures = load_fixtures()
    fixtures = sorted(fixtures, key=lambda item: item.get("id", ""))

    engine = UnifiedEngine()
    failures = 0

    for fixture in fixtures:
        fixture_id = fixture.get("id", "<missing-id>")
        expected = fixture.get("expected", {})
        actual = _compute_signature(engine, fixture)

        if actual == expected:
            print(f"PASS {fixture_id}")
        else:
            failures += 1
            print(f"FAIL {fixture_id}")
            print("EXPECTED", json.dumps(expected, sort_keys=True))
            print("ACTUAL  ", json.dumps(actual, sort_keys=True))

    if failures:
        print(f"{failures} fixture(s) failed")
        return 1

    print(f"All {len(fixtures)} fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
