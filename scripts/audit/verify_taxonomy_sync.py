import json
from pathlib import Path

from taxonomy_utils import (
    build_taxonomy_from_master_config,
    canonicalize_json,
    load_json,
    repo_root,
)


def _normalize(data):
    return canonicalize_json(data)


def _extract_keys(data):
    building_types = data.get("building_types", {})
    type_keys = set(building_types.keys())
    subtype_keys = {
        t: set((building_types.get(t, {}).get("subtypes", {}) or {}).keys())
        for t in type_keys
    }
    return type_keys, subtype_keys


def main() -> int:
    root = repo_root()
    shared_path = root / "shared" / "building_types.json"
    backend_path = root / "backend" / "shared" / "building_types.json"

    if not shared_path.exists():
        print(f"Missing {shared_path}")
        return 1
    if not backend_path.exists():
        print(f"Missing {backend_path}")
        return 1

    shared_data = load_json(shared_path)
    backend_data = load_json(backend_path)

    if _normalize(shared_data) != _normalize(backend_data):
        print("ERROR: shared and backend taxonomy JSON differ")
        return 1

    expected_data, expected_type_count, expected_subtype_count = build_taxonomy_from_master_config()

    shared_types, shared_subtypes = _extract_keys(shared_data)
    expected_types, expected_subtypes = _extract_keys(expected_data)

    if shared_types != expected_types:
        missing = expected_types - shared_types
        extra = shared_types - expected_types
        print("ERROR: building type keys mismatch")
        if missing:
            print(f"  Missing: {sorted(missing)}")
        if extra:
            print(f"  Extra: {sorted(extra)}")
        return 1

    for type_key, expected_set in expected_subtypes.items():
        actual_set = shared_subtypes.get(type_key, set())
        if actual_set != expected_set:
            missing = expected_set - actual_set
            extra = actual_set - expected_set
            print(f"ERROR: subtype keys mismatch for {type_key}")
            if missing:
                print(f"  Missing: {sorted(missing)}")
            if extra:
                print(f"  Extra: {sorted(extra)}")
            return 1

    type_count = shared_data.get("type_count")
    subtype_count = shared_data.get("subtype_count")
    if type_count != expected_type_count or subtype_count != expected_subtype_count:
        print("ERROR: type/subtype count mismatch")
        print(f"  Expected types: {expected_type_count}, got: {type_count}")
        print(f"  Expected subtypes: {expected_subtype_count}, got: {subtype_count}")
        return 1

    print("Taxonomy sync verified")
    print(f"Types: {type_count}")
    print(f"Subtypes: {subtype_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
