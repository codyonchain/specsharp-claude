from fingerprint_utils import format_sample, load_master_config


def main() -> int:
    mc = load_master_config()
    config = mc.OFFICE_UNDERWRITING_CONFIG

    if not isinstance(config, dict) or not config:
        print("ERROR: OFFICE_UNDERWRITING_CONFIG missing or empty")
        return 1

    keys = sorted(config.keys())
    print("OFFICE_UNDERWRITING_CONFIG fingerprint")
    print(f"Profiles: {len(keys)} ({format_sample(keys)})")

    for profile_key in keys:
        profile = config.get(profile_key)
        if not isinstance(profile, dict):
            print(f"ERROR: office profile {profile_key} is not a dict")
            return 1
        profile_keys = sorted(profile.keys())
        print(f"- {profile_key}: keys={len(profile_keys)} {format_sample(profile_keys)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
