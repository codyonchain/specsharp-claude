#!/usr/bin/env python3
"""Run a deterministic regression sweep across representative building types."""

from __future__ import annotations

import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.v2.engines.unified_engine import unified_engine  # type: ignore  # noqa: E402
from app.v2.config.master_config import (  # type: ignore  # noqa: E402
    BuildingType,
    ProjectClass,
    OwnershipType,
)

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DEBUG_FLAG = os.getenv("SPECSHARP_DEBUG_TRACE", "0").lower() in {"1", "true", "yes", "on"}

GOLDEN_CASES = [
    {
        "name": "Hospital 120k SF",
        "building_type": BuildingType.HEALTHCARE,
        "subtype": "hospital",
        "square_footage": 120_000,
        "location": "Nashville, TN",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.NON_PROFIT,
        "finish_level": "Premium",
        "floors": 6,
    },
    {
        "name": "Restaurant Full-Service 6k SF",
        "building_type": BuildingType.RESTAURANT,
        "subtype": "full_service",
        "square_footage": 6_000,
        "location": "Chicago, IL",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.FOR_PROFIT,
        "finish_level": "Standard",
        "floors": 1,
    },
    {
        "name": "Industrial Distribution 250k SF",
        "building_type": BuildingType.INDUSTRIAL,
        "subtype": "distribution_center",
        "square_footage": 250_000,
        "location": "Dallas, TX",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.FOR_PROFIT,
        "finish_level": "Standard",
        "floors": 1,
    },
    {
        "name": "Office Class A 180k SF",
        "building_type": BuildingType.OFFICE,
        "subtype": "class_a",
        "square_footage": 180_000,
        "location": "Seattle, WA",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.FOR_PROFIT,
        "finish_level": "Premium",
        "floors": 12,
    },
    {
        "name": "Multifamily Luxury 220k SF",
        "building_type": BuildingType.MULTIFAMILY,
        "subtype": "luxury_apartments",
        "square_footage": 220_000,
        "location": "Charlotte, NC",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.FOR_PROFIT,
        "finish_level": "Luxury",
        "floors": 8,
    },
    {
        "name": "Hospitality Limited Service 150k SF",
        "building_type": BuildingType.HOSPITALITY,
        "subtype": "limited_service_hotel",
        "square_footage": 150_000,
        "location": "Orlando, FL",
        "project_class": ProjectClass.GROUND_UP,
        "ownership_type": OwnershipType.FOR_PROFIT,
        "finish_level": "Premium",
        "floors": 9,
    },
]


def _round_floats(value: Any, precision: int = 6) -> Any:
    if isinstance(value, dict):
        return {k: _round_floats(v, precision) for k, v in value.items()}
    if isinstance(value, list):
        return [_round_floats(item, precision) for item in value]
    if isinstance(value, float):
        return round(value, precision)
    return value


def _sanitize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = deepcopy(result)
    sanitized.pop("timestamp", None)
    trace = sanitized.get("calculation_trace")
    if isinstance(trace, list):
        cleaned = []
        for entry in trace:
            if isinstance(entry, dict):
                entry = dict(entry)
                entry.pop("timestamp", None)
                cleaned.append(_round_floats(entry))
        sanitized["calculation_trace"] = cleaned
    return _round_floats(sanitized)


def _top_scope_systems(result: Dict[str, Any], limit: int = 3) -> List[Dict[str, Any]]:
    systems: List[Dict[str, Any]] = []
    for item in result.get("scope_items") or []:
        if not isinstance(item, dict):
            continue
        trade = item.get("trade")
        for system in item.get("systems") or []:
            if not isinstance(system, dict):
                continue
            systems.append({
                "trade": trade,
                "name": system.get("name"),
                "total_cost": system.get("total_cost"),
                "unit_cost": system.get("unit_cost"),
            })
    systems.sort(key=lambda s: s.get("total_cost") or 0, reverse=True)
    return systems[:limit]


def _summarize_case(case: Dict[str, Any], result: Dict[str, Any], deterministic: bool) -> Dict[str, Any]:
    project_info = result.get("project_info") or {}
    totals = result.get("totals") or {}
    ownership = result.get("ownership_analysis") or {}
    trade_breakdown = result.get("trade_breakdown") or {}
    return {
        "case": case["name"],
        "deterministic": deterministic,
        "hero": {
            "title": f"{project_info.get('display_name')} – {project_info.get('location')}",
            "square_footage": project_info.get("square_footage"),
            "cost_per_sf": totals.get("cost_per_sf"),
            "total_project_cost": totals.get("total_project_cost"),
        },
        "area_splits": {
            "trade_breakdown": trade_breakdown,
            "soft_costs": result.get("soft_costs"),
        },
        "top_scope_systems": _top_scope_systems(result),
        "return_metrics": result.get("return_metrics"),
        "debt_metrics": ownership.get("debt_metrics"),
        "revenue_analysis": result.get("revenue_analysis"),
    }


def _calculate_case(case: Dict[str, Any]) -> Dict[str, Any]:
    return unified_engine.calculate_project(
        building_type=case["building_type"],
        subtype=case["subtype"],
        square_footage=case["square_footage"],
        location=case["location"],
        project_class=case["project_class"],
        floors=case.get("floors", 1),
        ownership_type=case["ownership_type"],
        finish_level=case["finish_level"],
        finish_level_source="explicit",
        special_features=[],
    )


def run() -> None:
    report: List[Dict[str, Any]] = []
    for case in GOLDEN_CASES:
        print(f"[audit] running case: {case['name']}")
        runs = [_calculate_case(case) for _ in range(3)]
        deterministic = True
        if not DEBUG_FLAG:
            baseline = _sanitize_result(runs[0])
            for idx, candidate in enumerate(runs[1:], start=2):
                sanitized_candidate = _sanitize_result(candidate)
                if sanitized_candidate != baseline:
                    if os.getenv("AUDIT_DEBUG"):
                        print(f"[audit] determinism mismatch for {case['name']} run #{idx}")
                        print("baseline snippet:", list(baseline.items())[:3])
                        print("candidate snippet:", list(sanitized_candidate.items())[:3])
                    deterministic = False
                    raise AssertionError(
                        f"Non-deterministic output detected for {case['name']} run #{idx}"
                    )
        report.append(_summarize_case(case, runs[0], deterministic))

    payload = {
        "debug_trace_enabled": DEBUG_FLAG,
        "cases": report,
    }

    json_path = OUTPUT_DIR / "regression_report.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Golden Regression Report",
        f"- Debug trace enabled: {DEBUG_FLAG}",
        "",
    ]
    for case in report:
        hero = case["hero"]
        md_lines.append(f"## {case['case']}")
        md_lines.append(f"*Deterministic:* {case['deterministic']}")
        md_lines.append(
            f"- Hero: {hero.get('title')} — {hero.get('square_footage')} SF @ ${hero.get('cost_per_sf')}/SF"
        )
        md_lines.append(f"- Total project cost: ${hero.get('total_project_cost')}")
        md_lines.append(
            f"- Key return metrics: {json.dumps(case.get('return_metrics'), indent=2)}"
        )
        md_lines.append("")

    md_path = OUTPUT_DIR / "regression_report.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[audit] regression JSON written to {json_path}")
    print(f"[audit] regression markdown written to {md_path}")


if __name__ == "__main__":
    run()
