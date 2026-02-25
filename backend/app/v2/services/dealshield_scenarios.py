"""DealShield scenario snapshot builder for Wave-1 profiles."""
from __future__ import annotations

import copy
import math
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from app.v2.config.master_config import OwnershipType
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile


WAVE1_PROFILES: Set[str] = {
    "industrial_warehouse_v1",
    "industrial_distribution_center_v1",
    "industrial_manufacturing_v1",
    "industrial_flex_space_v1",
    "industrial_cold_storage_v1",
    "healthcare_surgical_center_v1",
    "healthcare_imaging_center_v1",
    "healthcare_medical_office_building_v1",
    "healthcare_outpatient_clinic_v1",
    "healthcare_dental_office_v1",
    "healthcare_hospital_v1",
    "healthcare_medical_center_v1",
    "healthcare_nursing_home_v1",
    "healthcare_rehabilitation_v1",
    "healthcare_urgent_care_v1",
    "restaurant_quick_service_v1",
    "restaurant_full_service_v1",
    "restaurant_fine_dining_v1",
    "restaurant_cafe_v1",
    "restaurant_bar_tavern_v1",
    "hospitality_limited_service_hotel_v1",
    "hospitality_full_service_hotel_v1",
    "office_class_a_v1",
    "office_class_b_v1",
    "retail_shopping_center_v1",
    "retail_big_box_v1",
    "multifamily_market_rate_apartments_v1",
    "multifamily_luxury_apartments_v1",
    "multifamily_affordable_housing_v1",
    "specialty_data_center_v1",
    "specialty_laboratory_v1",
    "specialty_self_storage_v1",
    "specialty_car_dealership_v1",
    "specialty_broadcast_facility_v1",
    "educational_elementary_school_v1",
    "educational_middle_school_v1",
    "educational_high_school_v1",
    "educational_university_v1",
    "educational_community_college_v1",
    "civic_library_v1",
    "civic_courthouse_v1",
    "civic_government_building_v1",
    "civic_community_center_v1",
    "civic_public_safety_v1",
    "recreation_fitness_center_v1",
    "recreation_sports_complex_v1",
    "recreation_aquatic_center_v1",
    "recreation_recreation_center_v1",
    "recreation_stadium_v1",
    "mixed_use_office_residential_v1",
    "mixed_use_retail_residential_v1",
    "mixed_use_hotel_retail_v1",
    "mixed_use_transit_oriented_v1",
    "mixed_use_urban_mixed_v1",
}

_ALLOWED_STRESS_BAND_PCTS: Set[int] = {10, 7, 5, 3}
_COLD_STORAGE_UGLY_COMMISSIONING_DELAY_MONTHS = 3
_MONTHS_PER_YEAR = 12.0


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


def _get_dealshield_controls(base_payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_controls = base_payload.get("dealshield_controls")
    controls = raw_controls if isinstance(raw_controls, dict) else {}

    raw_band = controls.get("stress_band_pct")
    band_pct = 10
    if _is_number(raw_band):
        candidate_band = int(float(raw_band))
        if candidate_band in _ALLOWED_STRESS_BAND_PCTS:
            band_pct = candidate_band

    anchor_total_project_cost = controls.get("anchor_total_project_cost")
    normalized_cost_anchor = float(anchor_total_project_cost) if _is_number(anchor_total_project_cost) else None
    use_cost_anchor = bool(controls.get("use_cost_anchor")) and normalized_cost_anchor is not None

    anchor_annual_revenue = controls.get("anchor_annual_revenue")
    normalized_revenue_anchor = float(anchor_annual_revenue) if _is_number(anchor_annual_revenue) else None
    use_revenue_anchor = bool(controls.get("use_revenue_anchor")) and normalized_revenue_anchor is not None

    return {
        "stress_band_pct": band_pct,
        "anchor_total_project_cost": normalized_cost_anchor,
        "use_cost_anchor": use_cost_anchor,
        "anchor_annual_revenue": normalized_revenue_anchor,
        "use_revenue_anchor": use_revenue_anchor,
    }


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


def _scale_stress_band_transforms(
    tile_id: str,
    transforms: List[Dict[str, Any]],
    stress_up_scalar: float,
    stress_down_scalar: float,
) -> List[Dict[str, Any]]:
    if not isinstance(tile_id, str):
        return [dict(transform) for transform in transforms]
    if not (tile_id.endswith("_plus_10") or tile_id.endswith("_minus_10")):
        return [dict(transform) for transform in transforms]

    scaled: List[Dict[str, Any]] = []
    for transform in transforms:
        next_transform = dict(transform)
        if next_transform.get("op") == "mul" and _is_number(next_transform.get("value")):
            operand = float(next_transform["value"])
            if tile_id.endswith("_plus_10") and math.isclose(operand, 1.10, rel_tol=0.0, abs_tol=1e-9):
                next_transform["value"] = float(stress_up_scalar)
            elif tile_id.endswith("_minus_10") and math.isclose(operand, 0.90, rel_tol=0.0, abs_tol=1e-9):
                next_transform["value"] = float(stress_down_scalar)
        scaled.append(next_transform)

    return scaled


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
    if metric_ref == "totals.cost_per_sf":
        totals = payload.get("totals")
        project_info = payload.get("project_info")
        if not isinstance(totals, dict) or not isinstance(project_info, dict):
            raise DealShieldScenarioError("Missing totals/project_info for cost_per_sf scenario override")
        square_footage = project_info.get("square_footage")
        if not _is_number(square_footage) or float(square_footage) <= 0:
            raise DealShieldScenarioError("Missing/invalid project_info.square_footage for cost_per_sf scenario override")

        old_cost_per_sf = totals.get("cost_per_sf")
        if not _is_number(old_cost_per_sf):
            total_project_cost = totals.get("total_project_cost")
            if not _is_number(total_project_cost):
                raise DealShieldScenarioError("Missing totals.cost_per_sf and totals.total_project_cost for scenario override")
            old_cost_per_sf = float(total_project_cost) / float(square_footage)

        new_cost_per_sf = _apply_transforms(float(old_cost_per_sf), transforms)
        target_total_cost = float(new_cost_per_sf) * float(square_footage)
        current_total_cost = totals.get("total_project_cost")
        if not _is_number(current_total_cost):
            current_total_cost = float(old_cost_per_sf) * float(square_footage)

        _apply_cost_delta(payload, float(target_total_cost) - float(current_total_cost))
        return

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


def _scalar_from_transforms(transforms: List[Dict[str, Any]]) -> Optional[float]:
    if len(transforms) != 1:
        return None
    transform = transforms[0]
    if transform.get("op") != "mul":
        return None
    value = transform.get("value")
    if not _is_number(value):
        return None
    return float(value)


def _driver_entry(tile_id: str, metric_ref: str, transforms: List[Dict[str, Any]]) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "tile_id": tile_id,
        "metric_ref": metric_ref,
    }
    if len(transforms) == 1:
        entry["op"] = transforms[0].get("op")
        entry["value"] = transforms[0].get("value")
    else:
        entry["transforms"] = transforms
    return entry


def _cold_storage_ugly_ramp_factor(commissioning_delay_months: int) -> float:
    if commissioning_delay_months <= 0:
        return 1.0
    if commissioning_delay_months >= int(_MONTHS_PER_YEAR):
        return 0.0
    return (_MONTHS_PER_YEAR - float(commissioning_delay_months)) / _MONTHS_PER_YEAR


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
        'mixed_use_split': payload.get('mixed_use_split'),
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
        if _is_number(value):
            continue
        # Some public-sector profiles do not emit annual_revenue directly; revenue stress is
        # still modeled through modifiers.revenue_factor and downstream financial recompute.
        if metric_ref == "revenue_analysis.annual_revenue":
            revenue_factor = _resolve_metric_ref(payload, "modifiers.revenue_factor")
            if _is_number(revenue_factor):
                continue
        raise DealShieldScenarioError(
            f"Scenario '{scenario_id}' missing numeric metric_ref '{metric_ref}'"
        )


def _build_ownership_bundle_without_trace_side_effects(
    engine: Any,
    building_config: Any,
    ownership_type: OwnershipType,
    total_project_cost: float,
    calculation_context: Dict[str, Any],
) -> Dict[str, Any]:
    trace = getattr(engine, "calculation_trace", None)
    if not isinstance(trace, list):
        return engine._build_ownership_bundle(
            building_config=building_config,
            ownership_type=ownership_type,
            total_project_cost=total_project_cost,
            calculation_context=calculation_context,
        )

    trace_snapshot = list(trace)
    try:
        return engine._build_ownership_bundle(
            building_config=building_config,
            ownership_type=ownership_type,
            total_project_cost=total_project_cost,
            calculation_context=calculation_context,
        )
    finally:
        trace[:] = trace_snapshot


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
    controls = _get_dealshield_controls(base_payload)
    band_fraction = float(controls["stress_band_pct"]) / 100.0
    stress_cost_scalar = 1.0 + band_fraction
    stress_revenue_scalar = 1.0 - band_fraction
    cost_anchor_used = bool(controls.get("use_cost_anchor"))
    cost_anchor_value = controls.get("anchor_total_project_cost")
    revenue_anchor_used = bool(controls.get("use_revenue_anchor"))
    revenue_anchor_value = controls.get("anchor_annual_revenue")

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
    scenario_inputs: Dict[str, Any] = {}
    _assert_tile_metrics(base_snapshot, tile_metric_refs, "base")

    if cost_anchor_used:
        totals = base_snapshot.get("totals") or {}
        base_total = totals.get("total_project_cost")
        if not _is_number(base_total):
            raise DealShieldScenarioError("Missing totals.total_project_cost for base cost anchor")
        _apply_cost_delta(base_snapshot, float(cost_anchor_value) - float(base_total))

        ownership_type = _select_ownership_type(building_config)
        calculation_context = _build_calculation_context(base_snapshot, "base")
        total_cost_value = (base_snapshot.get("totals") or {}).get("total_project_cost")
        if not _is_number(total_cost_value):
            raise DealShieldScenarioError("Base total_project_cost missing or invalid after cost anchor")
        bundle = _build_ownership_bundle_without_trace_side_effects(
            engine=engine,
            building_config=building_config,
            ownership_type=ownership_type,
            total_project_cost=total_cost_value,
            calculation_context=calculation_context,
        )
        _apply_financial_bundle(base_snapshot, bundle)

    scenario_inputs["base"] = {
        "applied_tile_ids": [],
        "cost_scalar": None,
        "revenue_scalar": None,
        "driver": None,
        "stress_band_pct": controls["stress_band_pct"],
        "cost_anchor_used": cost_anchor_used,
        "cost_anchor_value": float(cost_anchor_value) if cost_anchor_used else None,
        "revenue_anchor_used": revenue_anchor_used,
        "revenue_anchor_value": float(revenue_anchor_value) if revenue_anchor_used else None,
        "mixed_use_split": base_payload.get("mixed_use_split"),
        "mixed_use_split_source": (
            base_payload.get("mixed_use_split", {}).get("source")
            if isinstance(base_payload.get("mixed_use_split"), dict)
            else None
        ),
        "explain": {
            "short": "Base scenario (no profile levers applied; financials recomputed).",
            "levers": [],
        },
    }

    for scenario in scenario_defs:
        scenario_id = scenario["scenario_id"]
        scenario_payload = copy.deepcopy(base_payload)
        scenario_payload.pop("dealshield_scenarios", None)

        cost_transforms: List[Dict[str, Any]] = []
        revenue_transforms: List[Dict[str, Any]] = []
        driver_overrides: List[Tuple[str, List[Dict[str, Any]]]] = []
        applied_tile_ids = list(scenario.get("apply_tiles") or []) + list(scenario.get("plus_tiles") or [])
        cost_tiles: List[Dict[str, Any]] = []
        revenue_tiles: List[Dict[str, Any]] = []
        driver_entries: List[Dict[str, Any]] = []
        levers: List[str] = []
        commissioning_delay_months: Optional[int] = None
        ramp_factor: Optional[float] = None

        for tile_id in applied_tile_ids:
            tile = tile_by_id.get(tile_id)
            if not tile:
                raise DealShieldScenarioError(f"Scenario '{scenario_id}' references missing tile '{tile_id}'")
            metric_ref = tile.get("metric_ref")
            transforms = _normalize_transforms(tile.get("transform"))
            transforms = _scale_stress_band_transforms(
                tile_id=tile_id,
                transforms=transforms,
                stress_up_scalar=stress_cost_scalar,
                stress_down_scalar=stress_revenue_scalar,
            )
            if metric_ref == "totals.total_project_cost":
                cost_transforms.extend(transforms)
                cost_tiles.append({
                    "tile_id": tile_id,
                    "transforms": transforms,
                })
                levers.append(f"Total project cost scaled (tile {tile_id}).")
            elif metric_ref in {"revenue_analysis.annual_revenue", "modifiers.revenue_factor"}:
                revenue_transforms.extend(transforms)
                revenue_tiles.append({
                    "tile_id": tile_id,
                    "transforms": transforms,
                })
                levers.append(f"Revenue stress scaled via {metric_ref} (tile {tile_id}).")
            else:
                driver_overrides.append((metric_ref, transforms))
                driver_entries.append(_driver_entry(tile_id, metric_ref, transforms))
                levers.append(f"Driver override applied (tile {tile_id}).")

        display_name = scenario_id.replace("_", " ").title()
        cost_scalar = _scalar_from_transforms(cost_tiles[0]["transforms"]) if len(cost_tiles) == 1 else None
        revenue_scalar = _scalar_from_transforms(revenue_tiles[0]["transforms"]) if len(revenue_tiles) == 1 else None

        scenario_input: Dict[str, Any] = {
            "applied_tile_ids": applied_tile_ids,
            "cost_scalar": cost_scalar,
            "revenue_scalar": revenue_scalar,
            "driver": None,
            "stress_band_pct": controls["stress_band_pct"],
            "cost_anchor_used": cost_anchor_used,
            "cost_anchor_value": float(cost_anchor_value) if cost_anchor_used else None,
            "revenue_anchor_used": revenue_anchor_used,
            "revenue_anchor_value": float(revenue_anchor_value) if revenue_anchor_used else None,
            "mixed_use_split": scenario_payload.get("mixed_use_split"),
            "mixed_use_split_source": (
                scenario_payload.get("mixed_use_split", {}).get("source")
                if isinstance(scenario_payload.get("mixed_use_split"), dict)
                else None
            ),
            "explain": {
                "short": f"{display_name} scenario (profile-defined levers applied; financials recomputed).",
                "levers": levers,
            },
        }
        if profile_id == "industrial_cold_storage_v1" and scenario_id == "ugly":
            commissioning_delay_months = _COLD_STORAGE_UGLY_COMMISSIONING_DELAY_MONTHS
            ramp_factor = _cold_storage_ugly_ramp_factor(commissioning_delay_months)
            scenario_input["commissioning_delay_months"] = commissioning_delay_months
            scenario_input["ramp_factor"] = ramp_factor
            levers.append(
                "Cold-storage ugly commissioning delay applied "
                f"({commissioning_delay_months} months; year-1 ramp factor {ramp_factor:.2f})."
            )

        if cost_tiles and cost_scalar is None:
            if len(cost_tiles) == 1:
                scenario_input["cost_transforms"] = cost_tiles[0]["transforms"]
            else:
                scenario_input["cost_transforms"] = cost_tiles

        if revenue_tiles and revenue_scalar is None:
            if len(revenue_tiles) == 1:
                scenario_input["revenue_transforms"] = revenue_tiles[0]["transforms"]
            else:
                scenario_input["revenue_transforms"] = revenue_tiles

        if len(driver_entries) == 1:
            scenario_input["driver"] = driver_entries[0]
        elif len(driver_entries) > 1:
            scenario_input["driver"] = driver_entries

        scenario_inputs[scenario_id] = scenario_input

        totals = scenario_payload.get("totals") or {}
        base_total_raw = totals.get("total_project_cost")
        if not _is_number(base_total_raw):
            raise DealShieldScenarioError("Missing totals.total_project_cost for scenario override")
        base_total_cost = float(base_total_raw)
        if cost_anchor_used:
            base_total_cost = float(cost_anchor_value)
            _apply_cost_delta(scenario_payload, base_total_cost - float(base_total_raw))

        if cost_transforms:
            new_total = _apply_transforms(base_total_cost, cost_transforms)
            if not _is_number(new_total):
                raise DealShieldScenarioError("Scenario total_project_cost is not numeric")
            _apply_cost_delta(scenario_payload, float(new_total) - base_total_cost)

        for metric_ref, transforms in driver_overrides:
            _apply_driver_override(scenario_payload, metric_ref, transforms)

        if revenue_transforms:
            modifiers = dict(scenario_payload.get("modifiers") or {})
            base_factor = modifiers.get("revenue_factor", 1.0)
            if not _is_number(base_factor):
                base_factor = 1.0
            revenue_block = scenario_payload.get("revenue_analysis") or {}
            base_revenue = revenue_block.get("annual_revenue")
            if _is_number(base_revenue):
                new_revenue = _apply_transforms(float(base_revenue), revenue_transforms)
                if not _is_number(new_revenue):
                    raise DealShieldScenarioError("Scenario annual_revenue is not numeric")
                factor = (new_revenue / float(base_revenue)) if base_revenue else 1.0
                modifiers["revenue_factor"] = float(base_factor) * factor
            else:
                # Educational/public profiles may not emit annual_revenue; apply stress to revenue factor directly.
                modifiers["revenue_factor"] = _apply_transforms(float(base_factor), revenue_transforms)
            scenario_payload["modifiers"] = modifiers

        if ramp_factor is not None:
            modifiers = dict(scenario_payload.get("modifiers") or {})
            base_factor = modifiers.get("revenue_factor", 1.0)
            if not _is_number(base_factor):
                base_factor = 1.0
            modifiers["revenue_factor"] = float(base_factor) * float(ramp_factor)
            scenario_payload["modifiers"] = modifiers

        ownership_type = _select_ownership_type(building_config)
        calculation_context = _build_calculation_context(scenario_payload, scenario_id)
        total_cost_value = (scenario_payload.get("totals") or {}).get("total_project_cost")
        if not _is_number(total_cost_value):
            raise DealShieldScenarioError("Scenario total_project_cost missing or invalid")
        bundle = _build_ownership_bundle_without_trace_side_effects(
            engine=engine,
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
        "scenario_inputs": scenario_inputs,
        "driver_specs": scenario_defs,
    }

    return {
        "profile_id": profile_id,
        "scenarios": scenarios,
        "provenance": provenance,
    }
