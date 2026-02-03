from fingerprint_utils import format_sample, load_master_config, sorted_type_keys, type_key


def main() -> int:
    mc = load_master_config()
    margins = mc.MARGINS

    if not isinstance(margins, dict) or not margins:
        print("ERROR: MARGINS missing or empty")
        return 1

    type_keys = sorted_type_keys(margins.keys())
    print("MARGINS fingerprint")
    print(f"Types: {len(type_keys)} ({format_sample(type_keys)})")

    for building_type in sorted(margins.keys(), key=type_key):
        value = margins.get(building_type)
        try:
            margin = float(value)
        except (TypeError, ValueError):
            print(f"ERROR: margin for {type_key(building_type)} is not numeric")
            return 1
        if not (0 <= margin <= 1):
            print(f"ERROR: margin for {type_key(building_type)} out of range: {margin}")
            return 1
        print(f"- {type_key(building_type)}: {margin:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
