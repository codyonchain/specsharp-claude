from dataclasses import dataclass, field
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from app.v2.config.master_config import (
    BuildingConfig,
    SpecialFeaturePricingBasis,
    SpecialFeatureCountPricingMode,
)

INCLUDED_IN_BASELINE = "included_in_baseline"
INCREMENTAL = "incremental"
VALID_SPECIAL_FEATURE_PRICING_STATUSES = {
    INCLUDED_IN_BASELINE,
    INCREMENTAL,
}
LEGACY_FLOAT_NORMALIZATION_SOURCE = "legacy_float_normalized"
STRUCTURED_RULE_SOURCE = "structured_rule"
SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCLUDED_IN_BASELINE = "included_in_baseline"
SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_ONLY = "incremental_premium_only"
SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_WITH_TRADE_ALLOCATION = (
    "incremental_premium_with_trade_allocation"
)
SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE = (
    "Counted once in hard costs; distributed across the Trade Summary above."
)
VALID_TRADE_ALLOCATION_KEYS = (
    "structural",
    "mechanical",
    "electrical",
    "plumbing",
    "finishes",
)


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
class NormalizedSpecialFeatureDefaultCountRule:
    rule_type: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NormalizedSpecialFeaturePricingRule:
    feature_id: str
    basis: SpecialFeaturePricingBasis
    configured_value: float
    assumption_source: str
    count: Optional[float] = None
    count_pricing_mode: SpecialFeatureCountPricingMode = SpecialFeatureCountPricingMode.ALL_UNITS
    count_override_keys: Tuple[str, ...] = ()
    unit_label: Optional[str] = None
    default_count_bands: Tuple[NormalizedSpecialFeatureCountBand, ...] = ()
    default_count_rule: Optional[NormalizedSpecialFeatureDefaultCountRule] = None
    area_share_of_gsf: Optional[float] = None
    size_band: Optional[str] = None
    trade_allocation_weights: Tuple[Tuple[str, float], ...] = ()


@dataclass(frozen=True)
class ResolvedSpecialFeatureCountQuantity:
    quantity: float
    source: str
    resolved_size_band: Optional[str] = None


@dataclass(frozen=True)
class ResolvedCountBasedPricingQuantities:
    requested_quantity: float
    requested_quantity_source: str
    billed_quantity: float
    billed_quantity_source: str
    included_baseline_quantity: Optional[float] = None
    included_baseline_quantity_source: Optional[str] = None
    resolved_size_band: Optional[str] = None
    has_explicit_requested_quantity: bool = False


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
    configured_area_share_of_gsf: Optional[float] = None
    count_pricing_mode: Optional[SpecialFeatureCountPricingMode] = None
    unit_label: Optional[str] = None
    resolved_size_band: Optional[str] = None
    requested_quantity: Optional[float] = None
    requested_quantity_source: Optional[str] = None
    included_baseline_quantity: Optional[float] = None
    included_baseline_quantity_source: Optional[str] = None
    billed_quantity: Optional[float] = None
    billed_quantity_source: Optional[str] = None
    trade_composition_mode: str = SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_ONLY
    trade_allocation_weights: Dict[str, float] = field(default_factory=dict)
    trade_allocation_amounts: Dict[str, float] = field(default_factory=dict)
    trade_allocation_note: Optional[str] = None


@dataclass(frozen=True)
class ComposedTradeBreakdown:
    trade_breakdown: Dict[str, float]
    allocated_special_features_total: float
    allocated_feature_ids: List[str]


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


def _coerce_special_feature_count_pricing_mode(
    feature_id: str,
    raw_mode: Any,
) -> SpecialFeatureCountPricingMode:
    if raw_mode is None:
        return SpecialFeatureCountPricingMode.ALL_UNITS
    if isinstance(raw_mode, SpecialFeatureCountPricingMode):
        return raw_mode
    if isinstance(raw_mode, str):
        try:
            return SpecialFeatureCountPricingMode(raw_mode)
        except ValueError as exc:
            raise ValueError(
                f"Invalid special feature count pricing mode '{raw_mode}' for feature '{feature_id}'"
            ) from exc
    raise ValueError(
        f"Invalid special feature count pricing mode type '{type(raw_mode).__name__}' "
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


def _normalize_default_count_rule(
    feature_id: str,
    raw_rule: Any,
) -> Optional[NormalizedSpecialFeatureDefaultCountRule]:
    if raw_rule is None:
        return None
    if not isinstance(raw_rule, Mapping):
        raise ValueError(
            f"Special feature pricing field 'default_count_rule' for feature '{feature_id}' "
            "must be a dictionary"
        )

    raw_rule_type = _coerce_optional_string(
        feature_id=feature_id,
        field_name="default_count_rule.type",
        raw_value=raw_rule.get("type"),
    )
    if raw_rule_type is None:
        raise ValueError(
            f"Special feature pricing field 'default_count_rule.type' for feature '{feature_id}' "
            "must be a non-empty string"
        )

    rule_type = raw_rule_type.strip().lower()
    if rule_type not in {"dock_count", "count_per_sf_ceil"}:
        raise ValueError(
            f"Unsupported special feature default count rule '{raw_rule_type}' for feature '{feature_id}'"
        )

    raw_params = raw_rule.get("params") or {}
    if not isinstance(raw_params, Mapping):
        raise ValueError(
            f"Special feature pricing field 'default_count_rule.params' for feature '{feature_id}' "
            "must be a dictionary"
        )

    return NormalizedSpecialFeatureDefaultCountRule(
        rule_type=rule_type,
        params={str(key): value for key, value in raw_params.items()},
    )


def _normalize_trade_allocation_weights(
    feature_id: str,
    raw_allocation: Any,
) -> Tuple[Tuple[str, float], ...]:
    if raw_allocation is None:
        return ()
    if not isinstance(raw_allocation, Mapping):
        raise ValueError(
            f"Special feature pricing field 'trade_allocation' for feature '{feature_id}' "
            "must be a dictionary"
        )

    normalized: Dict[str, float] = {}
    for raw_trade_key, raw_share in raw_allocation.items():
        trade_key = str(raw_trade_key or "").strip().lower()
        if trade_key not in VALID_TRADE_ALLOCATION_KEYS:
            raise ValueError(
                f"Invalid trade allocation key '{raw_trade_key}' for feature '{feature_id}'"
            )
        share = _coerce_optional_float(
            feature_id=feature_id,
            field_name=f"trade_allocation.{trade_key}",
            raw_value=raw_share,
            required=True,
        )
        if share is None or share < 0:
            raise ValueError(
                f"Special feature trade allocation '{trade_key}' for feature '{feature_id}' "
                "must be non-negative"
            )
        if share > 0:
            normalized[trade_key] = float(share)

    if not normalized:
        return ()

    total_share = sum(normalized.values())
    if abs(total_share - 1.0) > 0.01:
        raise ValueError(
            f"Special feature trade allocation for feature '{feature_id}' must sum to 1.0, "
            f"got {total_share:.4f}"
        )

    return tuple(
        (trade_key, normalized[trade_key])
        for trade_key in VALID_TRADE_ALLOCATION_KEYS
        if trade_key in normalized
    )


def _normalize_count_quantity(raw_value: Any) -> Optional[float]:
    if not isinstance(raw_value, (int, float)):
        return None
    normalized_value = float(raw_value)
    if normalized_value <= 0:
        return None
    return float(max(1, int(round(normalized_value))))


def _resolve_explicit_count_override(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    pricing_override_sources: Optional[Iterable[Mapping[str, Any]]],
) -> Optional[ResolvedSpecialFeatureCountQuantity]:
    for source in pricing_override_sources or []:
        if not isinstance(source, Mapping):
            continue
        for key in rule.count_override_keys:
            if key not in source:
                continue
            override_count = _normalize_count_quantity(source.get(key))
            if override_count is not None:
                return ResolvedSpecialFeatureCountQuantity(
                    quantity=override_count,
                    source=f"explicit_override:{key}",
                )
    return None


def _resolve_default_count_quantity(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    square_footage: float,
) -> Optional[ResolvedSpecialFeatureCountQuantity]:
    sf_value = float(square_footage or 0.0)
    for band in rule.default_count_bands:
        max_square_footage = band.max_square_footage
        if max_square_footage is None or sf_value <= float(max_square_footage):
            band_count = _normalize_count_quantity(band.count)
            if band_count is not None:
                return ResolvedSpecialFeatureCountQuantity(
                    quantity=band_count,
                    source="size_band_default",
                    resolved_size_band=band.label,
                )

    default_count_rule = rule.default_count_rule
    if default_count_rule is not None:
        if default_count_rule.rule_type == "dock_count":
            default_min = _coerce_optional_float(
                feature_id=rule.feature_id,
                field_name="default_count_rule.params.default_min",
                raw_value=default_count_rule.params.get("default_min"),
            )
            default_sf_per_dock = _coerce_optional_float(
                feature_id=rule.feature_id,
                field_name="default_count_rule.params.default_sf_per_dock",
                raw_value=default_count_rule.params.get("default_sf_per_dock"),
            )
            default_min_count = max(
                0,
                int(round(default_min if default_min is not None else 1.0)),
            )
            sf_per_dock = float(default_sf_per_dock if default_sf_per_dock is not None else 10000.0)
            if sf_per_dock <= 0:
                raise ValueError(
                    f"Special feature default count rule 'dock_count' for feature '{rule.feature_id}' "
                    "must define a positive 'default_sf_per_dock'"
                )
            resolved_quantity = _normalize_count_quantity(
                max(default_min_count, int(round(sf_value / sf_per_dock)))
            )
            if resolved_quantity is not None:
                return ResolvedSpecialFeatureCountQuantity(
                    quantity=resolved_quantity,
                    source="default_count_rule:dock_count",
                )
        if default_count_rule.rule_type == "count_per_sf_ceil":
            if sf_value <= 0:
                return None
            default_min = _coerce_optional_float(
                feature_id=rule.feature_id,
                field_name="default_count_rule.params.default_min",
                raw_value=default_count_rule.params.get("default_min"),
            )
            sf_per_count = _coerce_optional_float(
                feature_id=rule.feature_id,
                field_name="default_count_rule.params.sf_per_count",
                raw_value=default_count_rule.params.get("sf_per_count"),
                required=True,
            )
            default_min_count = max(
                0,
                int(round(default_min if default_min is not None else 1.0)),
            )
            sf_per_count_value = float(sf_per_count if sf_per_count is not None else 5000.0)
            if sf_per_count_value <= 0:
                raise ValueError(
                    f"Special feature default count rule 'count_per_sf_ceil' for feature '{rule.feature_id}' "
                    "must define a positive 'sf_per_count'"
                )
            resolved_quantity = _normalize_count_quantity(
                max(default_min_count, int(math.ceil(sf_value / sf_per_count_value)))
            )
            if resolved_quantity is not None:
                return ResolvedSpecialFeatureCountQuantity(
                    quantity=resolved_quantity,
                    source="default_count_rule:count_per_sf_ceil",
                )

    configured_count = _normalize_count_quantity(rule.count)
    if configured_count is not None:
        return ResolvedSpecialFeatureCountQuantity(
            quantity=configured_count,
            source="configured_default_count",
            resolved_size_band=rule.size_band,
        )
    return None


def _resolve_count_based_pricing_quantities(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    square_footage: float,
    pricing_override_sources: Optional[Iterable[Mapping[str, Any]]],
) -> ResolvedCountBasedPricingQuantities:
    explicit_quantity = _resolve_explicit_count_override(
        rule=rule,
        pricing_override_sources=pricing_override_sources,
    )
    default_quantity = _resolve_default_count_quantity(
        rule=rule,
        square_footage=square_footage,
    )
    requested_quantity = explicit_quantity or default_quantity
    if requested_quantity is None:
        raise ValueError(
            f"Count-based special feature '{rule.feature_id}' is missing a usable count override or default"
        )

    if rule.count_pricing_mode == SpecialFeatureCountPricingMode.ALL_UNITS:
        return ResolvedCountBasedPricingQuantities(
            requested_quantity=requested_quantity.quantity,
            requested_quantity_source=requested_quantity.source,
            billed_quantity=requested_quantity.quantity,
            billed_quantity_source=requested_quantity.source,
            resolved_size_band=requested_quantity.resolved_size_band,
            has_explicit_requested_quantity=explicit_quantity is not None,
        )

    if explicit_quantity is not None:
        if default_quantity is None:
            if (
                rule.default_count_rule is not None
                and rule.default_count_rule.rule_type == "count_per_sf_ceil"
            ):
                return ResolvedCountBasedPricingQuantities(
                    requested_quantity=explicit_quantity.quantity,
                    requested_quantity_source=explicit_quantity.source,
                    billed_quantity=explicit_quantity.quantity,
                    billed_quantity_source=explicit_quantity.source,
                    has_explicit_requested_quantity=True,
                )
            raise ValueError(
                f"Count-based overage feature '{rule.feature_id}' is missing a usable baseline default"
            )
        billed_quantity = max(0.0, explicit_quantity.quantity - default_quantity.quantity)
        return ResolvedCountBasedPricingQuantities(
            requested_quantity=explicit_quantity.quantity,
            requested_quantity_source=explicit_quantity.source,
            billed_quantity=billed_quantity,
            billed_quantity_source="overage_above_default",
            included_baseline_quantity=default_quantity.quantity,
            included_baseline_quantity_source=default_quantity.source,
            resolved_size_band=default_quantity.resolved_size_band,
            has_explicit_requested_quantity=True,
        )

    return ResolvedCountBasedPricingQuantities(
        requested_quantity=requested_quantity.quantity,
        requested_quantity_source=requested_quantity.source,
        billed_quantity=requested_quantity.quantity,
        billed_quantity_source=requested_quantity.source,
        included_baseline_quantity=(
            default_quantity.quantity if default_quantity is not None else None
        ),
        included_baseline_quantity_source=(
            default_quantity.source if default_quantity is not None else None
        ),
        resolved_size_band=requested_quantity.resolved_size_band,
        has_explicit_requested_quantity=False,
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
    count_pricing_mode = _coerce_special_feature_count_pricing_mode(
        feature_id,
        raw_rule.get("count_pricing_mode"),
    )
    raw_size_band = raw_rule.get("size_band")
    if raw_size_band is not None and not isinstance(raw_size_band, str):
        raise ValueError(
            f"Special feature pricing field 'size_band' for feature '{feature_id}' must be a string"
        )

    normalized_count = _coerce_optional_float(
        feature_id=feature_id,
        field_name="count",
        raw_value=raw_rule.get("count"),
    )
    normalized_default_count_bands = _normalize_default_count_bands(
        feature_id=feature_id,
        raw_bands=raw_rule.get("default_count_bands"),
    )
    normalized_default_count_rule = _normalize_default_count_rule(
        feature_id=feature_id,
        raw_rule=raw_rule.get("default_count_rule"),
    )
    normalized_area_share_of_gsf = _coerce_optional_float(
        feature_id=feature_id,
        field_name="area_share_of_gsf",
        raw_value=raw_rule.get("area_share_of_gsf"),
    )
    if (
        basis == SpecialFeaturePricingBasis.COUNT_BASED
        and count_pricing_mode == SpecialFeatureCountPricingMode.OVERAGE_ABOVE_DEFAULT
        and normalized_count is None
        and not normalized_default_count_bands
        and normalized_default_count_rule is None
    ):
        raise ValueError(
            f"Count-based overage feature '{feature_id}' must define a baseline default count"
        )
    if basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF:
        if normalized_area_share_of_gsf is None:
            raise ValueError(
                f"Area-share special feature '{feature_id}' must define 'area_share_of_gsf'"
            )
        if normalized_area_share_of_gsf <= 0 or normalized_area_share_of_gsf > 1:
            raise ValueError(
                f"Area-share special feature '{feature_id}' must define 'area_share_of_gsf' within (0, 1]"
            )

    return NormalizedSpecialFeaturePricingRule(
        feature_id=feature_id,
        basis=basis,
        configured_value=float(configured_value),
        count=normalized_count,
        count_pricing_mode=count_pricing_mode,
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
        default_count_bands=normalized_default_count_bands,
        default_count_rule=normalized_default_count_rule,
        area_share_of_gsf=normalized_area_share_of_gsf,
        size_band=raw_size_band,
        trade_allocation_weights=_normalize_trade_allocation_weights(
            feature_id=feature_id,
            raw_allocation=raw_rule.get("trade_allocation"),
        ),
        assumption_source=STRUCTURED_RULE_SOURCE,
    )


def resolve_default_count_quantity_for_rule(
    rule: NormalizedSpecialFeaturePricingRule,
    *,
    square_footage: float,
) -> Optional[ResolvedSpecialFeatureCountQuantity]:
    return _resolve_default_count_quantity(
        rule=rule,
        square_footage=square_footage,
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
        preview["count_pricing_mode"] = rule.count_pricing_mode.value
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
        if rule.default_count_rule is not None:
            preview["configured_default_count_rule"] = {
                "type": rule.default_count_rule.rule_type,
                "params": dict(rule.default_count_rule.params),
            }
    if rule.basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF:
        preview["configured_cost_per_feature_area_sf"] = rule.configured_value
    if rule.count is not None:
        preview["configured_count"] = rule.count
    if rule.area_share_of_gsf is not None:
        preview["configured_area_share_of_gsf"] = rule.area_share_of_gsf
    if rule.size_band is not None:
        preview["size_band"] = rule.size_band
    return preview


def serialize_resolved_special_feature_pricing_rule_preview(
    rule: NormalizedSpecialFeaturePricingRule,
    *,
    square_footage: float,
    pricing_override_sources: Optional[Iterable[Mapping[str, Any]]] = None,
    pricing_status: Optional[str] = None,
) -> Dict[str, Any]:
    preview = serialize_special_feature_pricing_rule_preview(
        rule,
        pricing_status=pricing_status,
    )
    if rule.basis != SpecialFeaturePricingBasis.COUNT_BASED:
        return preview

    resolved_quantities = _resolve_count_based_pricing_quantities(
        rule=rule,
        square_footage=square_footage,
        pricing_override_sources=pricing_override_sources,
    )
    preview["requested_quantity"] = resolved_quantities.requested_quantity
    preview["requested_quantity_source"] = resolved_quantities.requested_quantity_source
    preview["billed_quantity"] = resolved_quantities.billed_quantity
    preview["billed_quantity_source"] = resolved_quantities.billed_quantity_source
    if resolved_quantities.included_baseline_quantity is not None:
        preview["included_baseline_quantity"] = resolved_quantities.included_baseline_quantity
    if resolved_quantities.included_baseline_quantity_source is not None:
        preview["included_baseline_quantity_source"] = (
            resolved_quantities.included_baseline_quantity_source
        )
    if resolved_quantities.resolved_size_band is not None:
        preview["resolved_size_band"] = resolved_quantities.resolved_size_band
    return preview


def _resolve_trade_composition_mode(
    *,
    pricing_status: str,
    trade_allocation_weights: Mapping[str, float],
    total_cost: float,
) -> str:
    if pricing_status == INCLUDED_IN_BASELINE:
        return SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCLUDED_IN_BASELINE
    if trade_allocation_weights and float(total_cost or 0.0) > 0:
        return SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_WITH_TRADE_ALLOCATION
    return SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_ONLY


def _build_trade_allocation_payload(
    *,
    rule: NormalizedSpecialFeaturePricingRule,
    pricing_status: str,
    total_cost: float,
) -> Tuple[str, Dict[str, float], Dict[str, float], Optional[str]]:
    trade_allocation_weights = {
        trade_key: float(weight)
        for trade_key, weight in rule.trade_allocation_weights
    }
    trade_composition_mode = _resolve_trade_composition_mode(
        pricing_status=pricing_status,
        trade_allocation_weights=trade_allocation_weights,
        total_cost=total_cost,
    )

    if trade_composition_mode != SPECIAL_FEATURE_TRADE_COMPOSITION_MODE_INCREMENTAL_PREMIUM_WITH_TRADE_ALLOCATION:
        return trade_composition_mode, trade_allocation_weights, {}, None

    trade_allocation_amounts = {
        trade_key: float(total_cost) * float(weight)
        for trade_key, weight in trade_allocation_weights.items()
        if float(weight) > 0
    }
    return (
        trade_composition_mode,
        trade_allocation_weights,
        trade_allocation_amounts,
        SPECIAL_FEATURE_TRADE_ALLOCATION_NOTE,
    )


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
        total_cost = applied_cost_per_sf * applied_quantity
        (
            trade_composition_mode,
            trade_allocation_weights,
            trade_allocation_amounts,
            trade_allocation_note,
        ) = _build_trade_allocation_payload(
            rule=rule,
            pricing_status=pricing_status,
            total_cost=total_cost,
        )
        return AppliedSpecialFeaturePricing(
            feature_id=rule.feature_id,
            pricing_status=pricing_status,
            pricing_basis=rule.basis,
            configured_value=rule.configured_value,
            applied_value=applied_cost_per_sf,
            applied_quantity=applied_quantity,
            quantity_source="whole_project_sf",
            total_cost=total_cost,
            configured_cost_per_sf=configured_cost_per_sf,
            cost_per_sf=applied_cost_per_sf,
            assumption_source=rule.assumption_source,
            trade_composition_mode=trade_composition_mode,
            trade_allocation_weights=trade_allocation_weights,
            trade_allocation_amounts=trade_allocation_amounts,
            trade_allocation_note=trade_allocation_note,
        )

    if rule.basis == SpecialFeaturePricingBasis.COUNT_BASED:
        resolved_quantities = _resolve_count_based_pricing_quantities(
            rule=rule,
            square_footage=square_footage,
            pricing_override_sources=pricing_override_sources,
        )
        configured_cost_per_count = rule.configured_value
        should_apply_overage_charge = (
            rule.count_pricing_mode == SpecialFeatureCountPricingMode.OVERAGE_ABOVE_DEFAULT
            and resolved_quantities.has_explicit_requested_quantity
        )
        if should_apply_overage_charge:
            applied_cost_per_count = (
                configured_cost_per_count if resolved_quantities.billed_quantity > 0 else 0.0
            )
        else:
            applied_cost_per_count = (
                0.0
                if pricing_status == INCLUDED_IN_BASELINE
                else (
                    configured_cost_per_count
                    if resolved_quantities.billed_quantity > 0
                    else 0.0
                )
            )
        total_cost = applied_cost_per_count * resolved_quantities.billed_quantity
        (
            trade_composition_mode,
            trade_allocation_weights,
            trade_allocation_amounts,
            trade_allocation_note,
        ) = _build_trade_allocation_payload(
            rule=rule,
            pricing_status=pricing_status,
            total_cost=total_cost,
        )
        return AppliedSpecialFeaturePricing(
            feature_id=rule.feature_id,
            pricing_status=pricing_status,
            pricing_basis=rule.basis,
            configured_value=rule.configured_value,
            applied_value=applied_cost_per_count,
            applied_quantity=resolved_quantities.billed_quantity,
            quantity_source=resolved_quantities.billed_quantity_source,
            total_cost=total_cost,
            configured_cost_per_count=configured_cost_per_count,
            cost_per_count=applied_cost_per_count,
            count_pricing_mode=rule.count_pricing_mode,
            unit_label=rule.unit_label,
            resolved_size_band=resolved_quantities.resolved_size_band,
            requested_quantity=resolved_quantities.requested_quantity,
            requested_quantity_source=resolved_quantities.requested_quantity_source,
            included_baseline_quantity=resolved_quantities.included_baseline_quantity,
            included_baseline_quantity_source=(
                resolved_quantities.included_baseline_quantity_source
            ),
            billed_quantity=resolved_quantities.billed_quantity,
            billed_quantity_source=resolved_quantities.billed_quantity_source,
            assumption_source=rule.assumption_source,
            trade_composition_mode=trade_composition_mode,
            trade_allocation_weights=trade_allocation_weights,
            trade_allocation_amounts=trade_allocation_amounts,
            trade_allocation_note=trade_allocation_note,
        )

    if rule.basis == SpecialFeaturePricingBasis.AREA_SHARE_GSF:
        if rule.area_share_of_gsf is None:
            raise ValueError(
                f"Area-share special feature '{rule.feature_id}' is missing 'area_share_of_gsf'"
            )
        configured_cost_per_feature_area_sf = rule.configured_value
        applied_cost_per_feature_area_sf = (
            0.0
            if pricing_status == INCLUDED_IN_BASELINE
            else configured_cost_per_feature_area_sf
        )
        applied_quantity = float(square_footage or 0.0) * float(rule.area_share_of_gsf)
        total_cost = applied_cost_per_feature_area_sf * applied_quantity
        (
            trade_composition_mode,
            trade_allocation_weights,
            trade_allocation_amounts,
            trade_allocation_note,
        ) = _build_trade_allocation_payload(
            rule=rule,
            pricing_status=pricing_status,
            total_cost=total_cost,
        )
        return AppliedSpecialFeaturePricing(
            feature_id=rule.feature_id,
            pricing_status=pricing_status,
            pricing_basis=rule.basis,
            configured_value=rule.configured_value,
            applied_value=applied_cost_per_feature_area_sf,
            applied_quantity=applied_quantity,
            quantity_source="area_share_of_gsf",
            total_cost=total_cost,
            configured_area_share_of_gsf=rule.area_share_of_gsf,
            assumption_source=rule.assumption_source,
            trade_composition_mode=trade_composition_mode,
            trade_allocation_weights=trade_allocation_weights,
            trade_allocation_amounts=trade_allocation_amounts,
            trade_allocation_note=trade_allocation_note,
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
        "trade_composition_mode": applied_pricing.trade_composition_mode,
    }
    if applied_pricing.configured_cost_per_sf is not None:
        row["configured_cost_per_sf"] = applied_pricing.configured_cost_per_sf
    if applied_pricing.cost_per_sf is not None:
        row["cost_per_sf"] = applied_pricing.cost_per_sf
    if applied_pricing.configured_cost_per_count is not None:
        row["configured_cost_per_count"] = applied_pricing.configured_cost_per_count
    if applied_pricing.cost_per_count is not None:
        row["cost_per_count"] = applied_pricing.cost_per_count
    if applied_pricing.configured_area_share_of_gsf is not None:
        row["configured_area_share_of_gsf"] = applied_pricing.configured_area_share_of_gsf
    if applied_pricing.count_pricing_mode is not None:
        row["count_pricing_mode"] = applied_pricing.count_pricing_mode.value
    if applied_pricing.unit_label is not None:
        row["unit_label"] = applied_pricing.unit_label
    if applied_pricing.resolved_size_band is not None:
        row["resolved_size_band"] = applied_pricing.resolved_size_band
    if applied_pricing.requested_quantity is not None:
        row["requested_quantity"] = applied_pricing.requested_quantity
    if applied_pricing.requested_quantity_source is not None:
        row["requested_quantity_source"] = applied_pricing.requested_quantity_source
    if applied_pricing.included_baseline_quantity is not None:
        row["included_baseline_quantity"] = applied_pricing.included_baseline_quantity
    if applied_pricing.included_baseline_quantity_source is not None:
        row["included_baseline_quantity_source"] = (
            applied_pricing.included_baseline_quantity_source
        )
    if applied_pricing.billed_quantity is not None:
        row["billed_quantity"] = applied_pricing.billed_quantity
    if applied_pricing.billed_quantity_source is not None:
        row["billed_quantity_source"] = applied_pricing.billed_quantity_source
    if applied_pricing.trade_allocation_weights:
        row["trade_allocation_weights"] = dict(applied_pricing.trade_allocation_weights)
    if applied_pricing.trade_allocation_amounts:
        row["trade_allocation_amounts"] = dict(applied_pricing.trade_allocation_amounts)
        row["trade_allocation_applied"] = True
    if applied_pricing.trade_allocation_note is not None:
        row["trade_allocation_note"] = applied_pricing.trade_allocation_note
    return row


def compose_trade_breakdown_with_special_feature_allocations(
    base_trades: Mapping[str, Any],
    applied_special_feature_pricing: Optional[Iterable[AppliedSpecialFeaturePricing]],
) -> ComposedTradeBreakdown:
    composed_trades: Dict[str, float] = {
        str(trade_key): float(amount or 0.0)
        for trade_key, amount in (base_trades or {}).items()
    }
    allocated_special_features_total = 0.0
    allocated_feature_ids: List[str] = []

    for applied_pricing in applied_special_feature_pricing or []:
        trade_allocation_amounts = applied_pricing.trade_allocation_amounts or {}
        if not trade_allocation_amounts:
            continue
        allocated_feature_ids.append(applied_pricing.feature_id)
        for trade_key, amount in trade_allocation_amounts.items():
            normalized_trade_key = str(trade_key).strip().lower()
            amount_value = float(amount or 0.0)
            if normalized_trade_key not in VALID_TRADE_ALLOCATION_KEYS or amount_value <= 0:
                continue
            composed_trades[normalized_trade_key] = (
                float(composed_trades.get(normalized_trade_key, 0.0) or 0.0)
                + amount_value
            )
            allocated_special_features_total += amount_value

    return ComposedTradeBreakdown(
        trade_breakdown=composed_trades,
        allocated_special_features_total=allocated_special_features_total,
        allocated_feature_ids=allocated_feature_ids,
    )


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
