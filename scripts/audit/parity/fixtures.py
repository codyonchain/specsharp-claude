#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "basic_fixtures.json"


def load_fixtures(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    fixture_path = path or FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError("Fixture file must contain a JSON list")

    return sorted(data, key=lambda item: item.get("id", ""))
