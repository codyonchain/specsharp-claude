"""Validate DealShield tile profile registry hygiene."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ALLOWED_TRANSFORM_OPS = {"mul", "add"}
REQUIRED_TILE_IDS = ("cost_plus_10", "revenue_minus_10")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _ensure_backend_on_path() -> None:
    backend_path = _repo_root() / "backend"
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _format_path(path: Iterable[str]) -> str:
    output = ""
    for part in path:
        if part.startswith("["):
            output += part
        else:
            if output:
                output += "."
            output += part
    return output or "<root>"


def _scan_numeric_paths(
    value: Any,
    path: Tuple[str, ...],
    allowed_path: Tuple[str, ...],
    found: List[Tuple[str, ...]],
) -> None:
    if _is_number(value):
        if path != allowed_path:
            found.append(path)
        return
    if isinstance(value, dict):
        for key in sorted(value.keys(), key=str):
            _scan_numeric_paths(value[key], path + (str(key),), allowed_path, found)
        return
    if isinstance(value, list):
        for idx, item in enumerate(value):
            _scan_numeric_paths(item, path + (f"[{idx}]",), allowed_path, found)


def _find_disallowed_numeric_paths(tile: Dict[str, Any]) -> List[str]:
    found: List[Tuple[str, ...]] = []
    _scan_numeric_paths(tile, tuple(), ("transform", "value"), found)
    return [_format_path(path) for path in found]


def _aggregate_profiles(sources: List[Any]) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    combined: Dict[str, Any] = {}
    errors: Dict[str, List[str]] = {}
    origins: Dict[str, int] = {}

    for idx, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.setdefault(f"source[{idx}]", []).append("source is not a dict")
            continue
        for profile_id in sorted(source.keys(), key=str):
            if profile_id in combined:
                origin = origins.get(profile_id)
                if origin is None:
                    errors.setdefault(profile_id, []).append(
                        f"duplicate profile_id across sources: source[{idx}]"
                    )
                else:
                    errors.setdefault(profile_id, []).append(
                        f"duplicate profile_id across sources: source[{idx}] (already in source[{origin}])"
                    )
                continue
            combined[profile_id] = source[profile_id]
            origins[profile_id] = idx

    return combined, errors


def _validate_tile(tile: Dict[str, Any], index: int) -> Tuple[List[str], Optional[str], Optional[bool]]:
    errors: List[str] = []
    tile_id = tile.get("tile_id")
    if not isinstance(tile_id, str) or not tile_id.strip():
        errors.append(f"tiles[{index}].tile_id must be a non-empty string")
        tile_id = None

    label = tile.get("label")
    if not isinstance(label, str) or not label.strip():
        errors.append(f"tiles[{index}].label must be a non-empty string")

    metric_ref = tile.get("metric_ref")
    if not isinstance(metric_ref, str) or not metric_ref.strip():
        errors.append(f"tiles[{index}].metric_ref must be a non-empty string")

    required = tile.get("required")
    if not isinstance(required, bool):
        errors.append(f"tiles[{index}].required must be a bool")
        required = None

    transform = tile.get("transform")
    if not isinstance(transform, dict):
        errors.append(f"tiles[{index}].transform must be a dict with op/value")
    else:
        op = transform.get("op")
        if op not in ALLOWED_TRANSFORM_OPS:
            errors.append(
                f"tiles[{index}].transform.op must be one of {sorted(ALLOWED_TRANSFORM_OPS)}"
            )
        value = transform.get("value")
        if not _is_number(value):
            errors.append(f"tiles[{index}].transform.value must be int or float")

    for path in _find_disallowed_numeric_paths(tile):
        errors.append(
            f"tiles[{index}] contains numeric value at '{path}' (only transform.value allowed)"
        )

    return errors, tile_id, required


def _validate_profile(profile_id: str, profile: Any) -> Tuple[List[str], int]:
    errors: List[str] = []
    tile_ids: List[str] = []
    tile_required: Dict[str, Optional[bool]] = {}

    if not isinstance(profile, dict):
        errors.append("profile must be a dict")
        return errors, 0

    version = profile.get("version")
    if not isinstance(version, str) or not version.strip():
        errors.append("version must be a non-empty string")
    elif version != "v1":
        errors.append("version must be 'v1'")

    tiles = profile.get("tiles")
    if not isinstance(tiles, list):
        errors.append("tiles must be a list")
        tiles = []

    derived_rows = profile.get("derived_rows")
    if not isinstance(derived_rows, list):
        errors.append("derived_rows must be a list (can be empty)")
        derived_rows = []

    tile_count = len(tiles)
    for idx, tile in enumerate(tiles):
        if not isinstance(tile, dict):
            errors.append(f"tiles[{idx}] must be a dict")
            continue

        tile_errors, tile_id, required = _validate_tile(tile, idx)
        errors.extend(tile_errors)

        if tile_id is None:
            continue

        if tile_id in tile_ids:
            errors.append(f"tiles[{idx}].tile_id '{tile_id}' is duplicated")
        else:
            tile_ids.append(tile_id)
            tile_required[tile_id] = required

    for required_id in REQUIRED_TILE_IDS:
        if required_id not in tile_required:
            errors.append(f"required tile_id '{required_id}' is missing")
        elif tile_required[required_id] is not True:
            errors.append(f"required tile_id '{required_id}' must have required=True")

    tile_id_set = set(tile_ids)
    for idx, row in enumerate(derived_rows):
        if not isinstance(row, dict):
            errors.append(f"derived_rows[{idx}] must be a dict")
            continue

        row_id = row.get("row_id")
        if not isinstance(row_id, str) or not row_id.strip():
            errors.append(f"derived_rows[{idx}].row_id must be a non-empty string")
            row_id = None

        label = row.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"derived_rows[{idx}].label must be a non-empty string")

        apply_tiles = row.get("apply_tiles")
        if not isinstance(apply_tiles, list):
            errors.append(f"derived_rows[{idx}].apply_tiles must be a list")
            apply_tiles = []

        apply_tile_ids: List[str] = []
        for tile_idx, tile_id in enumerate(apply_tiles):
            if not isinstance(tile_id, str) or not tile_id.strip():
                errors.append(
                    f"derived_rows[{idx}].apply_tiles[{tile_idx}] must be a non-empty string"
                )
                continue
            apply_tile_ids.append(tile_id)
            if tile_id not in tile_id_set:
                errors.append(
                    f"derived_rows[{idx}].apply_tiles references unknown tile_id '{tile_id}'"
                )

        if row_id in {"conservative", "ugly"}:
            missing_required = [
                tile_id for tile_id in REQUIRED_TILE_IDS if tile_id not in apply_tile_ids
            ]
            if missing_required:
                errors.append(
                    f"derived_rows[{idx}] '{row_id}' must include {missing_required} in apply_tiles"
                )

    return errors, tile_count


def _report_fail(profile_errors: Dict[str, List[str]]) -> None:
    print("FAIL: DealShield tile profile validation failed")
    for profile_id in sorted(profile_errors.keys(), key=str):
        print(f"profile_id: {profile_id}")
        for reason in profile_errors[profile_id]:
            print(f"reason: {reason}")


def _report_pass(source_count: int, profile_count: int, tile_count: int) -> None:
    print("PASS: DealShield tile profiles OK")
    print(f"sources: {source_count}")
    print(f"profiles: {profile_count}")
    print(f"tiles: {tile_count}")


def main() -> int:
    _ensure_backend_on_path()
    try:
        from app.v2.config.type_profiles import dealshield_tiles
    except Exception as exc:
        print("FAIL: unable to import dealshield tile profiles")
        print(f"reason: {exc}")
        return 1

    sources = getattr(dealshield_tiles, "DEALSHIELD_TILE_PROFILE_SOURCES", None)
    if not isinstance(sources, list):
        print("FAIL: DEALSHIELD_TILE_PROFILE_SOURCES must be a list of dicts")
        return 1

    combined_profiles, aggregate_errors = _aggregate_profiles(sources)
    profile_errors: Dict[str, List[str]] = dict(aggregate_errors)

    total_tiles = 0
    for profile_id in sorted(combined_profiles.keys(), key=str):
        errors, tile_count = _validate_profile(profile_id, combined_profiles[profile_id])
        total_tiles += tile_count
        if errors:
            profile_errors.setdefault(profile_id, []).extend(errors)

    if profile_errors:
        _report_fail(profile_errors)
        return 1

    _report_pass(len(sources), len(combined_profiles), total_tiles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
