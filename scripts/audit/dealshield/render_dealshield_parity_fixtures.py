#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
PARITY_DIR = ROOT / "scripts" / "audit" / "parity"

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(PARITY_DIR))

from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile  # noqa: E402
from app.v2.services.dealshield_service import build_dealshield_scenario_table  # noqa: E402
from app.v2.engines.unified_engine import UnifiedEngine  # noqa: E402
from app.v2.config.master_config import (  # noqa: E402
    BuildingType,
    ProjectClass,
    OwnershipType,
)
from fixtures import load_fixtures  # noqa: E402


EXPECTED_PROFILES: List[str] = [
    "industrial_warehouse_v1",
    "industrial_cold_storage_v1",
    "healthcare_medical_office_building_v1",
    "healthcare_urgent_care_v1",
    "restaurant_quick_service_v1",
    "hospitality_limited_service_hotel_v1",
]


def _stable_hash(payload: Dict[str, Any]) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


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


def _compute_payload(engine: UnifiedEngine, fixture: Dict[str, Any]) -> Dict[str, Any]:
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

    return engine.calculate_project(
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


def _get_fixture_outputs() -> List[Dict[str, Any]]:
    fixtures = load_fixtures()
    fixtures = sorted(fixtures, key=lambda item: item.get("id", ""))
    engine = UnifiedEngine()
    outputs: List[Dict[str, Any]] = []
    for fixture in fixtures:
        fixture_id = fixture.get("id", "<missing-id>")
        payload = _compute_payload(engine, fixture)
        outputs.append({"name": fixture_id, "payload": payload})
    return outputs


def run() -> int:
    fixtures = _get_fixture_outputs()
    rendered_profiles = set()

    for fixture in fixtures:
        name = fixture.get("name") or "<unknown>"
        payload = fixture.get("payload")
        if not isinstance(payload, dict):
            continue

        profile_id = payload.get("dealshield_tile_profile")
        if profile_id not in EXPECTED_PROFILES:
            continue

        profile = get_dealshield_profile(profile_id)
        table = build_dealshield_scenario_table(name, payload, profile)
        digest = _stable_hash(table)

        print(f"HASH {name} profile_id={profile_id} {digest}")
        rendered_profiles.add(profile_id)

    expected_count = int(os.environ.get("EXPECT_DEALSHIELD_RENDER_COUNT", "6") or "6")
    missing_profiles = [pid for pid in EXPECTED_PROFILES if pid not in rendered_profiles]

    if len(rendered_profiles) < expected_count or missing_profiles:
        print(
            "FAIL: DealShield render count mismatch; "
            f"expected={expected_count} rendered={len(rendered_profiles)}"
        )
        print(f"missing_profile_ids={missing_profiles}")
        return 1

    print("PASS: DealShield parity fixtures rendered")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
