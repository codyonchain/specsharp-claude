from importlib import import_module


def main() -> int:
    modules = [
        ("MASTER_CONFIG", "fingerprint_master_config"),
        ("BUILDING_PROFILES", "fingerprint_building_profiles"),
        ("PROJECT_TIMELINES", "fingerprint_project_timelines"),
        ("MARGINS", "fingerprint_margins"),
        ("OFFICE_UNDERWRITING_CONFIG", "fingerprint_office_underwriting_config"),
    ]

    failures = []
    for label, module_name in modules:
        module = import_module(module_name)
        print(f"\n== {label} ==")
        code = module.main()
        if code != 0:
            failures.append(label)

    if failures:
        print("\nERROR: fingerprint failures")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nAll fingerprints passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
