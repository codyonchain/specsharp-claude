import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _ensure_backend_on_path() -> Path:
    root = _repo_root()
    backend_path = root / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    return root


def ensure_backend_on_path() -> Path:
    return _ensure_backend_on_path()


def _title_from_key(key: str) -> str:
    return " ".join(part.capitalize() for part in key.split("_"))


def _type_aliases() -> Dict[str, List[str]]:
    return {
        "multifamily": ["residential", "multi_family", "multi_family_residential", "apartments", "apartment"],
        "healthcare": ["medical", "health"],
        "educational": ["education", "school", "academic"],
        "office": ["commercial", "business"],
        "industrial": ["warehouse", "manufacturing", "logistics"],
        "retail": ["shopping", "store", "shop"],
        "hospitality": ["hotel", "lodging", "accommodation"],
        "restaurant": ["dining", "food service", "eatery"],
        "civic": ["government", "municipal", "public"],
        "recreation": ["sports", "fitness", "entertainment"],
        "parking": ["garage", "parking structure"],
        "mixed_use": [],
        "specialty": [],
    }


def build_taxonomy_from_master_config() -> Tuple[Dict[str, Any], int, int]:
    root = _ensure_backend_on_path()
    from app.v2.config import master_config as mc

    building_types: Dict[str, Any] = {}
    subtype_count = 0
    alias_map = _type_aliases()

    for building_type in sorted(mc.MASTER_CONFIG.keys(), key=lambda t: t.value):
        type_key = building_type.value
        subtypes = mc.MASTER_CONFIG.get(building_type, {})
        subtype_entries: Dict[str, Any] = {}

        for subtype_key in sorted(subtypes.keys()):
            cfg = subtypes[subtype_key]
            display_name = getattr(cfg, "display_name", None) or _title_from_key(subtype_key)
            base_cost = getattr(cfg, "base_cost_per_sf", None)
            nlp_cfg = getattr(cfg, "nlp", None)
            keywords = []
            if nlp_cfg is not None:
                nlp_keywords = getattr(nlp_cfg, "keywords", None)
                if isinstance(nlp_keywords, list):
                    keywords = [str(k) for k in nlp_keywords if k]
            subtype_entries[subtype_key] = {
                "display_name": display_name,
                "keywords": sorted(keywords),
                "base_cost_per_sf": base_cost,
            }

        subtype_count += len(subtype_entries)
        building_types[type_key] = {
            "display_name": _title_from_key(type_key),
            "aliases": sorted(alias_map.get(type_key, [])),
            "subtypes": subtype_entries,
        }

    type_count = len(building_types)
    taxonomy = {
        "generated_from": "backend/app/v2/config/master_config.py",
        "generated_at": datetime.now().replace(microsecond=0).isoformat(),
        "type_count": type_count,
        "subtype_count": subtype_count,
        "canonical_keys_only": True,
        "schema_version": 1,
        "version": "1.0.0",
        "description": "Single source of truth for all building types in SpecSharp",
        "building_types": building_types,
    }
    return taxonomy, type_count, subtype_count


def _sort_obj(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sort_obj(value[k]) for k in sorted(value.keys())}
    if isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            return sorted(value)
        return [_sort_obj(item) for item in value]
    return value


def canonicalize_json(data: Dict[str, Any]) -> Dict[str, Any]:
    return _sort_obj(data)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    canonical = canonicalize_json(data)
    path.write_text(json.dumps(canonical, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def repo_root() -> Path:
    return _repo_root()
