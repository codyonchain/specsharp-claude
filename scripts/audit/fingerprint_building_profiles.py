from fingerprint_utils import format_sample, load_master_config, sorted_type_keys, type_key


def main() -> int:
    mc = load_master_config()
    profiles = mc.BUILDING_PROFILES

    if not isinstance(profiles, dict) or not profiles:
        print("ERROR: BUILDING_PROFILES missing or empty")
        return 1

    type_keys = sorted_type_keys(profiles.keys())
    print("BUILDING_PROFILES fingerprint")
    print(f"Types: {len(type_keys)} ({format_sample(type_keys)})")

    for building_type in sorted(profiles.keys(), key=type_key):
        profile = profiles.get(building_type)
        if not isinstance(profile, dict):
            print(f"ERROR: profile for {type_key(building_type)} is not a dict")
            return 1
        keys = sorted(profile.keys())
        print(f"- {type_key(building_type)}: keys={len(keys)} {format_sample(keys)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
