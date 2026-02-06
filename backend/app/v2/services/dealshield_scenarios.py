"""DealShield scenario snapshot builder for Wave-1 profiles."""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from app.v2.config.master_config import OwnershipType
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile


WAVE1_PROFILES: Set[str] = {
    "industrial_warehouse_v1",
    "industrial_cold_storage_v1",
    "healthcare_medical_office_building_v1",
    "healthcare_urgent_care_v1",
    "restaurant_quick_service_v1",
    "hospitality_limited_service_hotel_v1",
}


class DealShieldScenarioError(ValueError):
    pass


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


def _normalize_transforms(transform: Any) -> List[Dict[str, Any]]:
    if transform is None:
        return []
    if isinstance(transform, dict):
        return [transform]
    if isinstance(transform, list):
        if not all(isinstance(item, dict) for item in transform):
            raise DealShieldScenarioError("Transform list must contain dict entries")
        return list(transform)
    raise DealShieldScenarioError(f"Unsupported transform type: {type(transform).__name__}")


def _apply_transform(value: float, transform: Dict[str, Any]) -> float:
    op = transform.get("op")
    operand = transform.get("value")
    if not _is_number(operand):
        raise DealShieldScenarioError("Transform value must be numeric")

    operand_value = float(operand)
    if op == "mul":
        return value * operand_value
    if op == "add":
        return value + operand_value
    if op == "sub":
        return value - operand_value
    if op == "div":
        if operand_value == 0:
            raise DealShieldScenarioError("Transform division by zero")
        return value / operand_value
    raise DealShieldScenarioError(f"Unsupported transform op: {op}")


def _apply_transforms(value: float, transforms: Iterable[Dict[str, Any]]) -> float:
    output = float(value)
    for transform in transforms:
        output = _apply_transform(output, transform)
    return output


def _scale_dict_numbers(target: Dict[str, Any], factor: float) -> None:
    for key, value in target.items():
        if _is_number(value):
            target[key] = float(value) * factor


def _apply_cost_scale(payload: Dict[str, Any], factor: float) -> None:
    if not _is_number(factor) or factor == 1:
        return

    totals = payload.get("totals")
    if isinstance(totals, dict):
        for key in ("hard_costs", "soft_costs", "total_project_cost"):
            if _is_number(totals.get(key)):
                totals[key] = float(totals[key]) * factor

    construction = payload.get("construction_costs")
    if isinstance(construction, dict):
        for key in ("construction_total", "equipment_total", "special_features_total"):
            if _is_number(construction.get(key)):
                construction[key] = float(construction[key]) * factor

    trade_breakdown = payload.get("trade_breakdown")
    if isinstance(trade_breakdown, dict):
        _scale_dict_numbers(trade_breakdown, factor)

    soft_costs = payload.get("soft_costs")
    if isinstance(soft_costs, dict):
        _scale_dict_numbers(soft_costs, factor)

    totals = payload.get("totals")
    if isinstance(totals, dict):
        total_cost = totals.get("total_project_cost")
        square_footage = (payload.get("project_info") or {}).get("square_footage")
        if _is_number(total_cost) and _is_number(square_footage) and square_footage:
            totals["cost_per_sf"] = float(total_cost) / float(square_footage)


def _apply_cost_delta(payload: Dict[str, Any], delta: float) -> None:
    if not _is_number(delta) or delta == 0:
        return

    totals = payload.get("totals")
    if isinstance(totals, dict):
        if _is_number(totals.get("hard_costs")):
            totals["hard_costs"] = float(totals["hard_costs"]) + float(delta)
        if _is_number(totals.get("total_project_cost")):
            totals["total_project_cost"] = float(totals["total_project_cost"]) + float(delta)
        elif _is_number(totals.get("hard_costs")) and _is_number(totals.get("soft_costs")):
            totals["total_project_cost"] = float(totals["hard_costs"]) + float(totals["soft_costs"])

        total_cost = totals.get("total_project_cost")
        square_footage = (payload.get("project_info") or {}).get("square_footage")
        if _is_number(total_cost) and _is_number(square_footage) and square_footage:
            totals["cost_per_sf"] = float(total_cost) / float(square_footage)


def _apply_driver_override(
    payload: Dict[str, Any],
    metric_ref: str,
    transforms: List[Dict[str, Any]],
) -> None:
    if metric_ref.startswith("trade_breakdown."):
        trade_key = metric_ref.split(".", 1)[1]
        trade_breakdown = payload.get("trade_breakdown")
        if not isinstance(trade_breakdown, dict) or not _is_number(trade_breakdown.get(trade_key)):
            raise DealShieldScenarioError(f"Missing trade_breakdown.{trade_key} for scenario override")
        old_value = float(trade_breakdown[trade_key])
        new_value = _apply_transforms(old_value, transforms)
        trade_breakdown[trade_key] = new_value
        delta = new_value - old_value
        construction = payload.get("construction_costs")
        if isinstance(construction, dict) and _is_number(construction.get("construction_total")):
            construction["construction_total"] = float(construction["construction_total"]) + delta
        _apply_cost_delta(payload, delta)
        return

    if metric_ref == "construction_costs.equipment_total":
        construction = payload.get("construction_costs")
        if not isinstance(construction, dict) or not _is_number(construction.get("equipment_total")):
            raise DealShieldScenarioError("Missing construction_costs.equipment_total for scenario override")
        old_value = float(construction["equipment_total"])
        new_value = _apply_transforms(old_value, transforms)
        construction["equipment_total"] = new_value
        delta = new_value - old_value
        _apply_cost_delta(payload, delta)
        return

    raise DealShieldScenarioError(f"Unsupported driver metric_ref: {metric_ref}")


def _select_ownership_type(building_config: Any) -> OwnershipType:
    ownership_types = list(building_config.ownership_types.keys())
    if not ownership_types:
        raise DealShieldScenarioError("Building config missing ownership_types")
    if len(ownership_types) == 1:
        return ownership_types[0]
    for candidate in ownership_types:
        if candidate == OwnershipType.FOR_PROFIT:
            return candidate
    return sorted(ownership_types, key=lambda item: item.value)[0]


def _build_calculation_context(
    payload: Dict[str, Any],
    scenario_id: str,
) -> Dict[str, Any]:
    project_info = payload.get("project_info") or {}
    totals = payload.get("totals") or {}
    construction = payload.get("construction_costs") or {}

    context = dict(payload)
    context.update({
        'building_type': project_info.get('building_type'),
        'subtype': project_info.get('subtype'),
        'square_footage': project_info.get('square_footage'),
        'total_cost': totals.get('total_project_cost'),
        'subtotal': construction.get('construction_total'),
        'modifiers': payload.get('modifiers') or {},
        'quality_factor': construction.get('quality_factor'),
        'finish_level': project_info.get('finish_level'),
        'regional_context': payload.get('regional'),
        'location': project_info.get('location'),
        'scenario': scenario_id,
    })
    return context


def _apply_financial_bundle(
    payload: Dict[str, Any],
    bundle: Dict[str, Any],
) -> None:
    ownership_analysis = bundle.get('ownership_analysis')
    if not ownership_analysis:
        return

    payload['ownership_analysis'] = ownership_analysis
    payload['revenue_analysis'] = ownership_analysis.get('revenue_analysis', {})
    payload['revenue_requirements'] = ownership_analysis.get('revenue_requirements', {})
    payload['roi_analysis'] = ownership_analysis.get('roi_analysis', {})
    payload['operational_efficiency'] = ownership_analysis.get('operational_efficiency', {})
    payload['return_metrics'] = ownership_analysis.get('return_metrics', {})
    payload['roi_metrics'] = ownership_analysis.get('roi_metrics', {})
    payload['department_allocation'] = ownership_analysis.get('department_allocation', [])
    payload['operational_metrics'] = ownership_analysis.get('operational_metrics', {})
    payload['sensitivity_analysis'] = ownership_analysis.get('sensitivity_analysis')

    revenue_data = bundle.get('revenue_data') or {}
    if 'hospitality_financials' in revenue_data:
        payload['hospitality_financials'] = revenue_data.get('hospitality_financials')
    if bundle.get('flex_revenue_per_sf') is not None:
        payload['flex_revenue_per_sf'] = bundle.get('flex_revenue_per_sf')


def _assert_tile_metrics(payload: Dict[str, Any], metric_refs: List[str], scenario_id: str) -> None:
    for metric_ref in metric_refs:
        value = _resolve_metric_ref(payload, metric_ref)
        if not _is_number(value):
            raise DealShieldScenarioError(
                f"Scenario '{scenario_id}' missing numeric metric_ref '{metric_ref}'"
            )


def build_dealshield_scenarios(
    base_payload: Dict[str, Any],
    building_config: Any,
    engine: Any,
) -> Dict[str, Any]:
    profile_id = (
        base_payload.get("dealshield_tile_profile")
        or getattr(building_config, "dealshield_tile_profile", None)
    )
    if not isinstance(profile_id, str) or not profile_id.strip():
        return {}

    profile_id = profile_id.strip()
    if profile_id not in WAVE1_PROFILES:
        return {}

    profile = get_dealshield_profile(profile_id)
    if profile.get("version") != "v1":
        raise DealShieldScenarioError(f"Unsupported DealShield profile version for {profile_id}")

    tiles = profile.get("tiles") or []
    derived_rows = profile.get("derived_rows") or []

    tile_metric_refs = [tile.get("metric_ref") for tile in tiles if isinstance(tile, dict)]
    tile_by_id = {tile.get("tile_id"): tile for tile in tiles if isinstance(tile, dict)}

    scenario_defs: List[Dict[str, Any]] = []
    for row in derived_rows:
        if not isinstance(row, dict):
            raise DealShieldScenarioError("Derived row must be a dict")
        scenario_id = row.get("row_id") or row.get("id") or row.get("scenario_id")
        if not isinstance(scenario_id, str) or not scenario_id.strip():
            raise DealShieldScenarioError("Derived scenario_id missing or invalid")
        apply_tiles = row.get("apply_tiles") if isinstance(row.get("apply_tiles"), list) else []
        plus_tiles = row.get("plus_tiles") if isinstance(row.get("plus_tiles"), list) else []
        scenario_defs.append({
            "scenario_id": scenario_id.strip(),
            "apply_tiles": apply_tiles,
            "plus_tiles": plus_tiles,
        })

    base_snapshot = copy.deepcopy(base_payload)
    base_snapshot.pop("dealshield_scenarios", None)

    scenarios: Dict[str, Dict[str, Any]] = {"base": base_snapshot}
    _assert_tile_metrics(base_snapshot, tile_metric_refs, "base")

    for scenario in scenario_defs:
        scenario_id = scenario["scenario_id"]
        scenario_payload = copy.deepcopy(base_payload)
        scenario_payload.pop("dealshield_scenarios", None)

        cost_transforms: List[Dict[str, Any]] = []
        revenue_transforms: List[Dict[str, Any]] = []
        driver_overrides: List[Tuple[str, List[Dict[str, Any]]]] = []

        tile_ids = list(scenario.get("apply_tiles") or []) + list(scenario.get("plus_tiles") or [])
        for tile_id in tile_ids:
            tile = tile_by_id.get(tile_id)
            if not tile:
                raise DealShieldScenarioError(f"Scenario '{scenario_id}' references missing tile '{tile_id}'")
            metric_ref = tile.get("metric_ref")
            transforms = _normalize_transforms(tile.get("transform"))
            if metric_ref == "totals.total_project_cost":
                cost_transforms.extend(transforms)
            elif metric_ref == "revenue_analysis.annual_revenue":
                revenue_transforms.extend(transforms)
            else:
                driver_overrides.append((metric_ref, transforms))

        if cost_transforms:
            totals = scenario_payload.get("totals") or {}
            base_total = totals.get("total_project_cost")
            if not _is_number(base_total):
                raise DealShieldScenarioError("Missing totals.total_project_cost for scenario cost override")
            new_total = _apply_transforms(float(base_total), cost_transforms)
            if not _is_number(new_total):
                raise DealShieldScenarioError("Scenario total_project_cost is not numeric")
            factor = (new_total / float(base_total)) if base_total else 1.0
            _apply_cost_scale(scenario_payload, factor)

        for metric_ref, transforms in driver_overrides:
            _apply_driver_override(scenario_payload, metric_ref, transforms)

        if revenue_transforms:
            revenue_block = scenario_payload.get("revenue_analysis") or {}
            base_revenue = revenue_block.get("annual_revenue")
            if not _is_number(base_revenue):
                raise DealShieldScenarioError("Missing revenue_analysis.annual_revenue for scenario override")
            new_revenue = _apply_transforms(float(base_revenue), revenue_transforms)
            if not _is_number(new_revenue):
                raise DealShieldScenarioError("Scenario annual_revenue is not numeric")
            factor = (new_revenue / float(base_revenue)) if base_revenue else 1.0
            modifiers = dict(scenario_payload.get("modifiers") or {})
            base_factor = modifiers.get("revenue_factor", 1.0)
            if not _is_number(base_factor):
                base_factor = 1.0
            modifiers["revenue_factor"] = float(base_factor) * factor
            scenario_payload["modifiers"] = modifiers

        ownership_type = _select_ownership_type(building_config)
        calculation_context = _build_calculation_context(scenario_payload, scenario_id)
        total_cost_value = (scenario_payload.get("totals") or {}).get("total_project_cost")
        if not _is_number(total_cost_value):
            raise DealShieldScenarioError("Scenario total_project_cost missing or invalid")
        bundle = engine._build_ownership_bundle(
            building_config=building_config,
            ownership_type=ownership_type,
            total_project_cost=total_cost_value,
            calculation_context=calculation_context,
        )
        _apply_financial_bundle(scenario_payload, bundle)

        _assert_tile_metrics(scenario_payload, tile_metric_refs, scenario_id)

        scenarios[scenario_id] = scenario_payload

    provenance = {
        "profile_id": profile_id,
        "scenario_ids": ["base"] + [row["scenario_id"] for row in scenario_defs],
        "tile_metric_refs": tile_metric_refs,
        "driver_specs": scenario_defs,
    }

    return {
        "profile_id": profile_id,
        "scenarios": scenarios,
        "provenance": provenance,
    }
