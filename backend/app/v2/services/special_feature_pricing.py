from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

from app.v2.config.master_config import (
    BuildingConfig,
    SpecialFeaturePricingBasis,
)

INCLUDED_IN_BASELINE = "included_in_baseline"
INCREMENTAL = "incremental"
VALID_SPECIAL_FEATURE_PRICING_STATUSES = {
    INCLUDED_IN_BASELINE,
    INCREMENTAL,
}
LEGACY_FLOAT_NORMALIZATION_SOURCE = "legacy_float_normalized"
STRUCTURED_RULE_SOURCE = "structured_rule"


@dataclass(frozen=True)
class ResolvedSpecialFeaturePricing:
    selected_feature_ids: List[str]
    incremental_feature_ids: List[str]
    included_in_baseline_feature_ids: List[str]
    pricing_status_by_feature_id: Dict[str, str]


@dataclass(frozen=True)
class NormalizedSpecialFeaturePricingRule:
    feature_id: str
    basis: SpecialFeaturePricingBasis
    configured_value: float
    assumption_source: str
    count: Optional[float] = None
    area_share_of_gsf: Optional[float] = None
    size_band: Optional[str] = None


@dataclass(frozen=True)
class AppliedSpecialFeaturePricing:
    feature_id: str
    pricing_status: str
    pricing_basis: SpecialFeaturePricingBasis
    configured_value: float
    applied_value: float
    applied_quantity: float
    total_cost: float
    assumption_source: str
    configured_cost_per_sf: Optional[float] = None
    cost_per_sf: Optional[float] = None


def _coerce_special_feature_pricing_basis(
    feature_id: str,
    raw_basis: Any,
) -> SpecialFeaturePricingBasis:
    if raw_basis is None:
        return SpecialFeaturePricingBasis.WHOLE_PROJECT_SF
    if isinstance(raw_basis, SpecialFeaturePricingBasis):
        return raw_basis
    if isinstance(raw_basis, str):
        try:
            return SpecialFeaturePricingBasis(raw_basis)
        except ValueError as exc:
            raise ValueError(
                f"Invalid special feature pricing basis '{raw_basis}' for feature '{feature_id}'"
            ) from exc
    raise ValueError(
        f"Invalid special feature pricing basis type '{type(raw_basis).__name__}' "
        f"for feature '{feature_id}'"
    )


def _coerce_optional_float(
    *,
    feature_id: str,
    field_name: str,
    raw_value: Any,
    required: bool = False,
) -> Optional[float]:
    if raw_value is None:
        if required:
            raise ValueError(
                f"Missing required special feature pricing field '{field_name}' for feature '{feature_id}'"
            )
        return None
    if isinstance(raw_value, (int, float)):
        return float(raw_value)
    raise ValueError(
        f"Special feature pricing field '{field_name}' for feature '{feature_id}' "
        f"must be numeric, got '{type(raw_value).__name__}'"
    )


def normalize_special_feature_pricing_rule(
    feature_id: str,
    raw_rule: Any,
) -> NormalizedSpecialFeaturePricingRule:
    if isinstance(raw_rule, (int, float)):
        return NormalizedSpecialFeaturePricingRule(
            feature_id=feature_id,
            basis=SpecialFeaturePricingBasis.WHOLE_PROJECT_SF,
            configured_value=float(raw_rule),
            assumption_source=LEGACY_FLOAT_NORMALIZATION_SOURCE,
        )

    if not isinstance(raw_rule, Mapping):
        raise ValueError(
            f"Unsupported special feature pricing config type '{type(raw_rule).__name__}' "
            f"for feature '{feature_id}'"
        )

    basis = _coerce_special_feature_pricing_basis(feature_id, raw_rule.get("basis"))
    configured_value = _coerce_optional_float(
        feature_id=feature_id,
        field_name="value",
        raw_value=raw_rule.get("value"),
        required=True,
    )
    raw_size_band = raw_rule.get("size_band")
    if raw_size_band is not None and not isinstance(raw_size_band, str):
        raise ValueError(
            f"Special feature pricing field 'size_band' for feature '{feature_id}' must be a string"
        )

    return NormalizedSpecialFeaturePricingRule(
        feature_id=feature_id,
        basis=basis,
        configured_value=float(configured_value),
        count=_coerce_optional_float(
            feature_id=feature_id,
            field_name="count",
            raw_value=raw_rule.get("count"),
        ),
        area_share_of_gsf=_coerce_optional_float(
            feature_id=feature_id,
            field_name="area_share_of_gsf",
            raw_value=raw_rule.get("area_share_of_gsf"),
        ),
        size_band=raw_size_band,
        assumption_source=STRUCTURED_RULE_SOURCE,
    )


def resolve_normalized_special_feature_pricing_rules(
    building_config: BuildingConfig,
    selected_feature_ids: Optional[Iterable[str]],
) -> List[NormalizedSpecialFeaturePricingRule]:
    available_feature_costs = building_config.special_features or {}
    normalized_rules: List[NormalizedSpecialFeaturePricingRule] = []
    seen_feature_ids = set()

    for feature_id in selected_feature_ids or []:
        if not isinstance(feature_id, str):
            continue
        if feature_id in seen_feature_ids:
            continue
        if feature_id not in available_feature_costs:
            continue

        normalized_rules.append(
            normalize_special_feature_pricing_rule(
                feature_id=feature_id,
                raw_rule=available_feature_costs[feature_id],
            )
        )
        seen_feature_ids.add(feature_id)

    return normalized_rules


def serialize_special_feature_pricing_rule_preview(
    rule: NormalizedSpecialFeaturePricingRule,
    *,
    pricing_status: Optional[str] = None,
) -> Dict[str, Any]:
    preview: Dict[str, Any] = {
        "id": rule.feature_id,
        "pricing_basis": rule.basis.value,
        "configured_value": rule.configured_value,
        "assumption_source": rule.assumption_source,
    }
    if pricing_status is not None:
        preview["pricing_status"] = pricing_status
    if rule.basis == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF:
        preview["configured_cost_per_sf"] = rule.configured_value
    if rule.count is not None:
        preview["configured_count"] = rule.count
    if rule.area_share_of_gsf is not None:
        preview["configured_area_share_of_gsf"] = rule.area_share_of_gsf
    if rule.size_band is not None:
        preview["size_band"] = rule.size_band
    return preview


def apply_special_feature_pricing_rule(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    square_footage: float,
    pricing_status: str,
) -> AppliedSpecialFeaturePricing:
    if pricing_status not in VALID_SPECIAL_FEATURE_PRICING_STATUSES:
        raise ValueError(
            f"Invalid special feature pricing status '{pricing_status}' for feature '{rule.feature_id}'"
        )

    if rule.basis == SpecialFeaturePricingBasis.WHOLE_PROJECT_SF:
        configured_cost_per_sf = rule.configured_value
        applied_cost_per_sf = (
            0.0 if pricing_status == INCLUDED_IN_BASELINE else configured_cost_per_sf
        )
        applied_quantity = float(square_footage)
        return AppliedSpecialFeaturePricing(
            feature_id=rule.feature_id,
            pricing_status=pricing_status,
            pricing_basis=rule.basis,
            configured_value=rule.configured_value,
            applied_value=applied_cost_per_sf,
            applied_quantity=applied_quantity,
            total_cost=applied_cost_per_sf * applied_quantity,
            configured_cost_per_sf=configured_cost_per_sf,
            cost_per_sf=applied_cost_per_sf,
            assumption_source=rule.assumption_source,
        )

    raise NotImplementedError(
        f"Special feature pricing basis '{rule.basis.value}' is not active yet for feature '{rule.feature_id}'"
    )


def serialize_applied_special_feature_pricing(
    applied_pricing: AppliedSpecialFeaturePricing,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "id": applied_pricing.feature_id,
        "pricing_status": applied_pricing.pricing_status,
        "pricing_basis": applied_pricing.pricing_basis.value,
        "configured_value": applied_pricing.configured_value,
        "applied_value": applied_pricing.applied_value,
        "applied_quantity": applied_pricing.applied_quantity,
        "total_cost": applied_pricing.total_cost,
        "assumption_source": applied_pricing.assumption_source,
    }
    if applied_pricing.configured_cost_per_sf is not None:
        row["configured_cost_per_sf"] = applied_pricing.configured_cost_per_sf
    if applied_pricing.cost_per_sf is not None:
        row["cost_per_sf"] = applied_pricing.cost_per_sf
    return row


def resolve_special_feature_pricing(
    building_config: BuildingConfig,
    selected_feature_ids: Optional[Iterable[str]],
) -> ResolvedSpecialFeaturePricing:
    available_feature_costs = building_config.special_features or {}
    pricing_statuses = building_config.special_feature_pricing_statuses or {}

    resolved_selected_feature_ids: List[str] = []
    incremental_feature_ids: List[str] = []
    included_in_baseline_feature_ids: List[str] = []
    pricing_status_by_feature_id: Dict[str, str] = {}
    seen_feature_ids = set()

    for feature_id in selected_feature_ids or []:
        if not isinstance(feature_id, str):
            continue
        if feature_id in seen_feature_ids:
            continue
        if feature_id not in available_feature_costs:
            continue

        status = pricing_statuses.get(feature_id, INCREMENTAL)
        if status not in VALID_SPECIAL_FEATURE_PRICING_STATUSES:
            raise ValueError(
                f"Invalid special feature pricing status '{status}' for feature '{feature_id}'"
            )

        seen_feature_ids.add(feature_id)
        resolved_selected_feature_ids.append(feature_id)
        pricing_status_by_feature_id[feature_id] = status
        if status == INCLUDED_IN_BASELINE:
            included_in_baseline_feature_ids.append(feature_id)
        else:
            incremental_feature_ids.append(feature_id)

    return ResolvedSpecialFeaturePricing(
        selected_feature_ids=resolved_selected_feature_ids,
        incremental_feature_ids=incremental_feature_ids,
        included_in_baseline_feature_ids=included_in_baseline_feature_ids,
        pricing_status_by_feature_id=pricing_status_by_feature_id,
    )
