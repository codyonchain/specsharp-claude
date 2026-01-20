#!/usr/bin/env python3
"""Run a single representative calculation and emit a summarized trace."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

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

SAMPLE_CASE = {
    "name": "Dallas Medical Office",
    "building_type": BuildingType.HEALTHCARE,
    "subtype": "medical_office",
    "square_footage": 80000,
    "location": "Dallas, TX",
    "project_class": ProjectClass.GROUND_UP,
    "ownership_type": OwnershipType.FOR_PROFIT,
    "finish_level": "Premium",
}

DEBUG_FLAG = os.getenv("SPECSHARP_DEBUG_TRACE", "0").lower() in {"1", "true", "yes", "on"}


def _build_debug_trace(result: Dict[str, Any]) -> Dict[str, Any]:
    modifiers = result.get("modifiers") or {}
    project_info = result.get("project_info") or {}
    revenue = result.get("revenue_analysis") or {}
    return_metrics = result.get("return_metrics") or {}
    ownership = result.get("ownership_analysis") or {}
    return {
        "engine": "unified_engine.calculate_project",
        "building_type": project_info.get("building_type"),
        "subtype": project_info.get("subtype"),
        "finish_level": project_info.get("finish_level"),
        "multipliers": {
            "cost_factor": modifiers.get("cost_factor"),
            "revenue_factor": modifiers.get("revenue_factor"),
            "cost_region_factor": modifiers.get("regional_cost_factor"),
            "revenue_region_factor": modifiers.get("market_factor"),
            "finish_cost_factor": modifiers.get("finish_cost_factor"),
            "finish_revenue_factor": modifiers.get("finish_revenue_factor"),
        },
        "revenue_model": {
            "annual_revenue": revenue.get("annual_revenue"),
            "revenue_per_sf": revenue.get("revenue_per_sf"),
            "operating_margin": revenue.get("operating_margin"),
            "occupancy_rate": revenue.get("occupancy_rate"),
        },
        "valuation": {
            "yield_on_cost": result.get("yield_on_cost"),
            "market_cap_rate": return_metrics.get("market_cap_rate") or (result.get("profile") or {}).get("market_cap_rate"),
            "property_value": return_metrics.get("property_value"),
        },
        "debt_metrics": ownership.get("debt_metrics"),
        "trace_steps": result.get("calculation_trace"),
    }


def main() -> None:
    result = unified_engine.calculate_project(
        building_type=SAMPLE_CASE["building_type"],
        subtype=SAMPLE_CASE["subtype"],
        square_footage=SAMPLE_CASE["square_footage"],
        location=SAMPLE_CASE["location"],
        project_class=SAMPLE_CASE["project_class"],
        floors=4,
        ownership_type=SAMPLE_CASE["ownership_type"],
        finish_level=SAMPLE_CASE["finish_level"],
        finish_level_source="explicit",
        special_features=[],
    )

    summary: Dict[str, Any] = {
        "case": SAMPLE_CASE["name"],
        "hero_title": f"{result['project_info']['display_name']} – {result['project_info']['location']}",
        "project_info": result["project_info"],
        "totals": result.get("totals"),
        "construction_costs": result.get("construction_costs"),
        "trade_breakdown": result.get("trade_breakdown"),
        "soft_costs": result.get("soft_costs"),
        "revenue_analysis": result.get("revenue_analysis"),
        "return_metrics": result.get("return_metrics"),
        "debt_metrics": (result.get("ownership_analysis") or {}).get("debt_metrics"),
        "timestamp": result.get("timestamp"),
    }

    if DEBUG_FLAG:
        summary["debug_trace"] = _build_debug_trace(result)

    output_path = OUTPUT_DIR / "trace_one.json"
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[audit] trace written to {output_path}")


if __name__ == "__main__":
    main()
