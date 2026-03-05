#!/usr/bin/env python3
from __future__ import annotations

import math
from typing import Any, Dict, Optional

from app.v2.config.master_config import BuildingType, OwnershipType, ProjectClass
from app.v2.engines.unified_engine import unified_engine


def _run_multifamily_case(unit_count: Optional[int] = None) -> Dict[str, Any]:
    request_overrides: Dict[str, Any] = {}
    if unit_count is not None:
        request_overrides["unit_count"] = int(unit_count)

    result = unified_engine.calculate_project(
        building_type=BuildingType.MULTIFAMILY,
        subtype="market_rate_apartments",
        square_footage=250000,
        location="Dallas, TX",
        project_class=ProjectClass.GROUND_UP,
        ownership_type=OwnershipType.FOR_PROFIT,
        parsed_input_overrides=request_overrides or None,
    )

    ownership_analysis = result.get("ownership_analysis") or {}
    operational_metrics = ownership_analysis.get("operational_metrics") or {}
    per_unit = operational_metrics.get("per_unit") or {}
    revenue_analysis = ownership_analysis.get("revenue_analysis") or {}
    project_info = result.get("project_info") or {}

    units = per_unit.get("units")
    if isinstance(units, float):
        units = int(round(units))

    return {
        "result": result,
        "project_info": project_info,
        "per_unit": per_unit,
        "units": units,
        "units_source": per_unit.get("units_source"),
        "annual_revenue": revenue_analysis.get("annual_revenue"),
        "annual_revenue_per_unit": per_unit.get("annual_revenue_per_unit"),
    }


def main() -> None:
    # A) Explicit unit_count overrides derived
    explicit_case = _run_multifamily_case(unit_count=220)
    assert explicit_case["units"] == 220, f"expected explicit units 220, got {explicit_case['units']}"
    assert (
        explicit_case["units_source"] == "user_input"
    ), f"expected units_source user_input, got {explicit_case['units_source']}"

    project_info_explicit = explicit_case["project_info"]
    if "unit_count" in project_info_explicit:
        assert project_info_explicit.get("unit_count") == 220, (
            "project_info.unit_count exists but does not match explicit value"
        )
    if "unit_count_source" in project_info_explicit:
        assert project_info_explicit.get("unit_count_source") == "user_input", (
            "project_info.unit_count_source exists but is not user_input"
        )

    # B) Derived units still work
    derived_case = _run_multifamily_case(unit_count=None)
    assert (
        derived_case["units_source"] == "derived"
    ), f"expected units_source derived, got {derived_case['units_source']}"
    assert isinstance(derived_case["units"], int), (
        f"expected derived units to be int, got {type(derived_case['units']).__name__}"
    )

    # C) Revenue math uses resolved units
    resolved_units = explicit_case["units"]
    annual_revenue = explicit_case["annual_revenue"]
    annual_revenue_per_unit = explicit_case["annual_revenue_per_unit"]
    assert isinstance(annual_revenue, (int, float)), "annual_revenue missing from ownership analysis"
    assert isinstance(annual_revenue_per_unit, (int, float)), "annual_revenue_per_unit missing from per_unit metrics"
    reconstructed_revenue = float(annual_revenue_per_unit) * float(resolved_units)
    assert math.isclose(
        reconstructed_revenue,
        float(annual_revenue),
        rel_tol=0.0,
        abs_tol=2.0,
    ), (
        "revenue consistency failed: "
        f"annual_revenue_per_unit * units={reconstructed_revenue}, annual_revenue={annual_revenue}"
    )

    print("PASS: unit/key count gate")


if __name__ == "__main__":
    main()
