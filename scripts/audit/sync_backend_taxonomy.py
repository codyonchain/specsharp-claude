import shutil
from pathlib import Path

from taxonomy_utils import repo_root


def main() -> int:
    root = repo_root()
    source = root / "shared" / "building_types.json"
    target = root / "backend" / "shared" / "building_types.json"
    if not source.exists():
        raise FileNotFoundError(f"Missing canonical taxonomy at {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print(f"Synced {source} -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
