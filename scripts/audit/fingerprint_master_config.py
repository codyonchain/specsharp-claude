from fingerprint_utils import format_sample, load_master_config, sorted_type_keys, type_key


def main() -> int:
    mc = load_master_config()
    master_config = mc.MASTER_CONFIG

    type_keys = sorted_type_keys(master_config.keys())
    if len(type_keys) != 13:
        print("ERROR: MASTER_CONFIG type count mismatch")
        print(f"  Expected: 13, Found: {len(type_keys)}")
        return 1

    subtype_total = 0
    subtype_index = {}
    for building_type in sorted(master_config.keys(), key=type_key):
        subtypes = master_config.get(building_type, {}) or {}
        subtype_keys = sorted(subtypes.keys())
        subtype_index[type_key(building_type)] = subtype_keys
        subtype_total += len(subtype_keys)

    if subtype_total != 58:
        print("ERROR: MASTER_CONFIG subtype count mismatch")
        print(f"  Expected: 58, Found: {subtype_total}")
        return 1

    print("MASTER_CONFIG fingerprint")
    print(f"Types: {len(type_keys)} ({format_sample(type_keys)})")
    print(f"Subtypes: {subtype_total}")

    for type_name in sorted(subtype_index.keys()):
        subtype_keys = subtype_index[type_name]
        print(f"- {type_name}: subtypes={len(subtype_keys)} {format_sample(subtype_keys)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
