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

SECTION_HEADERS = [
    "What would change this decision fastest?",
    "Most likely wrong",
    "Question bank",
    "Red flags & actions",
]


def _is_placeholder_text(value: Any) -> bool:
    if not isinstance(value, str):
        return True
    text = value.strip()
    if not text:
        return True
    if text in {"-", "—"}:
        return True
    if "tbd" in text.lower():
        return True
    return False


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
    validated_profiles = set()

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
        content = view_model.get("content")
        if not isinstance(content, dict):
            failures.append(f"{name}: missing view_model.content")
            continue

        if content.get("version") != "v1":
            failures.append(f"{name}: content.version must be v1")

        fastest_change = content.get("fastest_change")
        if not isinstance(fastest_change, dict):
            failures.append(f"{name}: fastest_change missing/invalid")
        else:
            drivers = fastest_change.get("drivers")
            if not isinstance(drivers, list) or len(drivers) != 3:
                failures.append(f"{name}: fastest_change.drivers must have length 3")

        most_likely_wrong = content.get("most_likely_wrong")
        if not isinstance(most_likely_wrong, list) or len(most_likely_wrong) < 2:
            failures.append(f"{name}: most_likely_wrong must have at least 2 entries")
        else:
            for idx, item in enumerate(most_likely_wrong):
                if not isinstance(item, dict):
                    failures.append(f"{name}: most_likely_wrong[{idx}] must be an object")
                    continue
                text = item.get("text")
                if _is_placeholder_text(text):
                    failures.append(f"{name}: most_likely_wrong[{idx}].text has placeholder content")

        question_bank = content.get("question_bank")
        if not isinstance(question_bank, list) or len(question_bank) < 2:
            failures.append(f"{name}: question_bank must have at least 2 groups")
        else:
            for idx, group in enumerate(question_bank):
                if not isinstance(group, dict):
                    failures.append(f"{name}: question_bank[{idx}] must be an object")
                    continue
                questions = group.get("questions")
                if not isinstance(questions, list) or len(questions) < 2:
                    failures.append(f"{name}: question_bank[{idx}].questions must have at least 2 questions")
                    continue
                for q_idx, question in enumerate(questions):
                    if _is_placeholder_text(question):
                        failures.append(f"{name}: question_bank[{idx}].questions[{q_idx}] has placeholder content")

        red_flags_actions = content.get("red_flags_actions")
        if not isinstance(red_flags_actions, list) or not (2 <= len(red_flags_actions) <= 4):
            failures.append(f"{name}: red_flags_actions must have 2-4 entries")
        else:
            for idx, item in enumerate(red_flags_actions):
                if not isinstance(item, dict):
                    failures.append(f"{name}: red_flags_actions[{idx}] must be an object")
                    continue
                flag = item.get("flag")
                action = item.get("action")
                if _is_placeholder_text(flag):
                    failures.append(f"{name}: red_flags_actions[{idx}].flag has placeholder content")
                if _is_placeholder_text(action):
                    failures.append(f"{name}: red_flags_actions[{idx}].action has placeholder content")

        html = render_dealshield_html(view_model)
        for header in SECTION_HEADERS:
            if html_module.escape(header) not in html:
                failures.append(f"{name}: missing section header '{header}' in html")

        validated_profiles.add(profile_id)

    missing_profiles = [pid for pid in WAVE1_PROFILES if pid not in validated_profiles]
    if missing_profiles:
        failures.append(f"missing Wave-1 profile coverage: {sorted(missing_profiles)}")

    if failures:
        print("FAIL: DealShield content contract validation failed")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("PASS: DealShield content contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
