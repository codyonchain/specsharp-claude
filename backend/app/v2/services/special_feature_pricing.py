from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from app.v2.config.master_config import BuildingConfig

INCLUDED_IN_BASELINE = "included_in_baseline"
INCREMENTAL = "incremental"
VALID_SPECIAL_FEATURE_PRICING_STATUSES = {
    INCLUDED_IN_BASELINE,
    INCREMENTAL,
}


@dataclass(frozen=True)
class ResolvedSpecialFeaturePricing:
    selected_feature_ids: List[str]
    incremental_feature_ids: List[str]
    included_in_baseline_feature_ids: List[str]
    pricing_status_by_feature_id: Dict[str, str]


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
