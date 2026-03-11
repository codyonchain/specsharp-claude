from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

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
class NormalizedSpecialFeatureCountBand:
    count: float
    label: Optional[str] = None
    max_square_footage: Optional[float] = None


@dataclass(frozen=True)
class NormalizedSpecialFeaturePricingRule:
    feature_id: str
    basis: SpecialFeaturePricingBasis
    configured_value: float
    assumption_source: str
    count: Optional[float] = None
    count_override_keys: Tuple[str, ...] = ()
    unit_label: Optional[str] = None
    default_count_bands: Tuple[NormalizedSpecialFeatureCountBand, ...] = ()
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
    quantity_source: str
    total_cost: float
    assumption_source: str
    configured_cost_per_sf: Optional[float] = None
    cost_per_sf: Optional[float] = None
    configured_cost_per_count: Optional[float] = None
    cost_per_count: Optional[float] = None
    unit_label: Optional[str] = None
    resolved_size_band: Optional[str] = None


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


def _coerce_optional_string(
    *,
    feature_id: str,
    field_name: str,
    raw_value: Any,
) -> Optional[str]:
    if raw_value is None:
        return None
    if isinstance(raw_value, str):
        value = raw_value.strip()
        return value or None
    raise ValueError(
        f"Special feature pricing field '{field_name}' for feature '{feature_id}' "
        f"must be a string, got '{type(raw_value).__name__}'"
    )


def _coerce_string_list(
    *,
    feature_id: str,
    field_name: str,
    raw_value: Any,
) -> Tuple[str, ...]:
    if raw_value is None:
        return ()
    if not isinstance(raw_value, Sequence) or isinstance(raw_value, (str, bytes)):
        raise ValueError(
            f"Special feature pricing field '{field_name}' for feature '{feature_id}' "
            f"must be a list of strings"
        )

    values: List[str] = []
    for item in raw_value:
        if not isinstance(item, str):
            raise ValueError(
                f"Special feature pricing field '{field_name}' for feature '{feature_id}' "
                f"must contain only strings"
            )
        normalized_item = item.strip()
        if normalized_item:
            values.append(normalized_item)
    return tuple(values)


def _normalize_default_count_bands(
    feature_id: str,
    raw_bands: Any,
) -> Tuple[NormalizedSpecialFeatureCountBand, ...]:
    if raw_bands is None:
        return ()
    if not isinstance(raw_bands, list):
        raise ValueError(
            f"Special feature pricing field 'default_count_bands' for feature '{feature_id}' "
            f"must be a list"
        )

    normalized_bands: List[NormalizedSpecialFeatureCountBand] = []
    for raw_band in raw_bands:
        if not isinstance(raw_band, Mapping):
            raise ValueError(
                f"Special feature pricing field 'default_count_bands' for feature '{feature_id}' "
                f"must contain dictionaries"
            )
        normalized_bands.append(
            NormalizedSpecialFeatureCountBand(
                count=float(
                    _coerce_optional_float(
                        feature_id=feature_id,
                        field_name="default_count_bands.count",
                        raw_value=raw_band.get("count"),
                        required=True,
                    )
                ),
                label=_coerce_optional_string(
                    feature_id=feature_id,
                    field_name="default_count_bands.label",
                    raw_value=raw_band.get("label"),
                ),
                max_square_footage=_coerce_optional_float(
                    feature_id=feature_id,
                    field_name="default_count_bands.max_square_footage",
                    raw_value=raw_band.get("max_square_footage"),
                ),
            )
        )
    return tuple(normalized_bands)


def _normalize_count_quantity(raw_value: Any) -> Optional[float]:
    if not isinstance(raw_value, (int, float)):
        return None
    normalized_value = float(raw_value)
    if normalized_value <= 0:
        return None
    return float(max(1, int(round(normalized_value))))


def _resolve_count_based_quantity(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    square_footage: float,
    pricing_override_sources: Optional[Iterable[Mapping[str, Any]]],
) -> Tuple[float, str, Optional[str]]:
    for source in pricing_override_sources or []:
        if not isinstance(source, Mapping):
            continue
        for key in rule.count_override_keys:
            if key not in source:
                continue
            override_count = _normalize_count_quantity(source.get(key))
            if override_count is not None:
                return override_count, f"explicit_override:{key}", None

    sf_value = float(square_footage or 0.0)
    for band in rule.default_count_bands:
        max_square_footage = band.max_square_footage
        if max_square_footage is None or sf_value <= float(max_square_footage):
            band_count = _normalize_count_quantity(band.count)
            if band_count is not None:
                return band_count, "size_band_default", band.label

    configured_count = _normalize_count_quantity(rule.count)
    if configured_count is not None:
        return configured_count, "configured_default_count", rule.size_band

    raise ValueError(
        f"Count-based special feature '{rule.feature_id}' is missing a usable count override or default"
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
        count_override_keys=_coerce_string_list(
            feature_id=feature_id,
            field_name="count_override_keys",
            raw_value=raw_rule.get("count_override_keys"),
        ),
        unit_label=_coerce_optional_string(
            feature_id=feature_id,
            field_name="unit_label",
            raw_value=raw_rule.get("unit_label"),
        ),
        default_count_bands=_normalize_default_count_bands(
            feature_id=feature_id,
            raw_bands=raw_rule.get("default_count_bands"),
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
    if rule.basis == SpecialFeaturePricingBasis.COUNT_BASED:
        preview["configured_cost_per_count"] = rule.configured_value
        if rule.unit_label is not None:
            preview["unit_label"] = rule.unit_label
        if rule.count_override_keys:
            preview["count_override_keys"] = list(rule.count_override_keys)
        if rule.default_count_bands:
            preview["configured_count_bands"] = [
                {
                    "label": band.label,
                    "max_square_footage": band.max_square_footage,
                    "count": band.count,
                }
                for band in rule.default_count_bands
            ]
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
    pricing_override_sources: Optional[Iterable[Mapping[str, Any]]] = None,
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
            quantity_source="whole_project_sf",
            total_cost=applied_cost_per_sf * applied_quantity,
            configured_cost_per_sf=configured_cost_per_sf,
            cost_per_sf=applied_cost_per_sf,
            assumption_source=rule.assumption_source,
        )

    if rule.basis == SpecialFeaturePricingBasis.COUNT_BASED:
        resolved_count, quantity_source, resolved_size_band = _resolve_count_based_quantity(
            rule=rule,
            square_footage=square_footage,
            pricing_override_sources=pricing_override_sources,
        )
        configured_cost_per_count = rule.configured_value
        applied_cost_per_count = (
            0.0 if pricing_status == INCLUDED_IN_BASELINE else configured_cost_per_count
        )
        return AppliedSpecialFeaturePricing(
            feature_id=rule.feature_id,
            pricing_status=pricing_status,
            pricing_basis=rule.basis,
            configured_value=rule.configured_value,
            applied_value=applied_cost_per_count,
            applied_quantity=resolved_count,
            quantity_source=quantity_source,
            total_cost=applied_cost_per_count * resolved_count,
            configured_cost_per_count=configured_cost_per_count,
            cost_per_count=applied_cost_per_count,
            unit_label=rule.unit_label,
            resolved_size_band=resolved_size_band,
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
        "quantity_source": applied_pricing.quantity_source,
        "total_cost": applied_pricing.total_cost,
        "assumption_source": applied_pricing.assumption_source,
    }
    if applied_pricing.configured_cost_per_sf is not None:
        row["configured_cost_per_sf"] = applied_pricing.configured_cost_per_sf
    if applied_pricing.cost_per_sf is not None:
        row["cost_per_sf"] = applied_pricing.cost_per_sf
    if applied_pricing.configured_cost_per_count is not None:
        row["configured_cost_per_count"] = applied_pricing.configured_cost_per_count
    if applied_pricing.cost_per_count is not None:
        row["cost_per_count"] = applied_pricing.cost_per_count
    if applied_pricing.unit_label is not None:
        row["unit_label"] = applied_pricing.unit_label
    if applied_pricing.resolved_size_band is not None:
        row["resolved_size_band"] = applied_pricing.resolved_size_band
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
