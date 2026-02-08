#!/usr/bin/env python3
from __future__ import annotations

import html as html_module
import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[3]
PARITY_DIR = ROOT / "scripts" / "audit" / "parity"

sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(PARITY_DIR))

from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile  # noqa: E402
from app.v2.services.dealshield_service import build_dealshield_view_model  # noqa: E402
from app.v2.services.dealshield_scenarios import WAVE1_PROFILES  # noqa: E402
from app.v2.engines.unified_engine import UnifiedEngine  # noqa: E402
from app.v2.config.master_config import (  # noqa: E402
    BuildingType,
    ProjectClass,
    OwnershipType,
)
from fixtures import load_fixtures  # noqa: E402

DEALSHIELD_EXPORT_PATH = ROOT / "backend" / "app" / "services" / "dealshield_export.py"
spec = importlib.util.spec_from_file_location("app.services.dealshield_export", DEALSHIELD_EXPORT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Unable to load dealshield_export module")
dealshield_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dealshield_module)
render_dealshield_html = dealshield_module.render_dealshield_html

DECISION_COLUMN_LABELS = [
    "Total Project Cost",
    "Annual Revenue",
    "NOI",
    "DSCR",
    "Yield on Cost",
]


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
    failures: List[str] = []

    for fixture in fixtures:
        name = fixture.get("name") or "<unknown>"
        payload = fixture.get("payload")
        if not isinstance(payload, dict):
            continue

        profile_id = payload.get("dealshield_tile_profile")
        if profile_id not in WAVE1_PROFILES:
            continue

        profile = get_dealshield_profile(profile_id)
        view_model = build_dealshield_view_model(name, payload, profile)
        html = render_dealshield_html(view_model)

        if str(profile_id) not in html:
            failures.append(f"{name}: missing profile_id in html")

        for label in DECISION_COLUMN_LABELS:
            if html_module.escape(label) not in html:
                failures.append(f"{name}: missing decision column label '{label}' in html")

        decision_table = view_model.get("decision_table")
        decision_rows = decision_table.get("rows") if isinstance(decision_table, dict) else []
        if not isinstance(decision_rows, list):
            decision_rows = []

        base_label: Optional[str] = None
        derived_labels: List[str] = []
        for row in decision_rows:
            if not isinstance(row, dict):
                continue
            label = row.get("label") or row.get("scenario_id")
            if not isinstance(label, str) or not label.strip():
                continue
            normalized_label = label.strip()
            scenario_id = row.get("scenario_id")
            if scenario_id == "base":
                base_label = normalized_label
            else:
                derived_labels.append(normalized_label)

        if not base_label:
            failures.append(f"{name}: decision_table missing base label")
            continue
        if len(derived_labels) < 2:
            failures.append(f"{name}: decision_table must have at least 2 derived scenario labels")
            continue

        expected_labels = [base_label, derived_labels[0], derived_labels[1]]
        for label in expected_labels:
            if html_module.escape(label) not in html:
                failures.append(f"{name}: missing scenario label '{label}' in html")

    if failures:
        print("FAIL: DealShield export contract validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: DealShield export contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
