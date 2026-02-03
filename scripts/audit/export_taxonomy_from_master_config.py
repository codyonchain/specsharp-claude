import sys
from pathlib import Path

from taxonomy_utils import build_taxonomy_from_master_config, repo_root, write_json


def main() -> int:
    root = repo_root()
    target = root / "shared" / "building_types.json"
    taxonomy, type_count, subtype_count = build_taxonomy_from_master_config()
    write_json(target, taxonomy)
    print(f"Wrote {target}")
    print(f"Types: {type_count}")
    print(f"Subtypes: {subtype_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
