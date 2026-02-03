from fingerprint_utils import load_master_config, sorted_type_keys, type_key


def main() -> int:
    mc = load_master_config()
    timelines = mc.PROJECT_TIMELINES

    if not isinstance(timelines, dict) or not timelines:
        print("ERROR: PROJECT_TIMELINES missing or empty")
        return 1

    type_keys = sorted_type_keys(timelines.keys())
    print("PROJECT_TIMELINES fingerprint")
    print(f"Types: {len(type_keys)}")

    for building_type in sorted(timelines.keys(), key=type_key):
        type_name = type_key(building_type)
        timeline = timelines.get(building_type)
        if not isinstance(timeline, dict):
            print(f"ERROR: timeline for {type_name} is not a dict")
            return 1

        class_keys = sorted(timeline.keys())
        print(f"{type_name}: classes={len(class_keys)}")

        for class_key in class_keys:
            cfg = timeline.get(class_key, {})
            if not isinstance(cfg, dict):
                print(f"ERROR: timeline config for {type_name}/{class_key} is not a dict")
                return 1

            milestones = cfg.get("milestones", []) or []
            if isinstance(milestones, dict):
                # Legacy shape: {id: offset_months}. Normalize to list of dicts.
                milestones = [
                    {"id": key, "label": str(key), "offset_months": value}
                    for key, value in milestones.items()
                ]
            if not isinstance(milestones, list):
                print(f"ERROR: milestones for {type_name}/{class_key} is not a list")
                return 1

            milestone_ids = []
            for milestone in milestones:
                if not isinstance(milestone, dict):
                    print(f"ERROR: milestone entry for {type_name}/{class_key} is not a dict")
                    return 1
                milestone_id = milestone.get("id")
                label = milestone.get("label")
                offset_months = milestone.get("offset_months")
                if not milestone_id:
                    print(f"ERROR: milestone entry for {type_name}/{class_key} missing id")
                    return 1
                if label is None:
                    print(f"ERROR: milestone entry for {type_name}/{class_key} missing label")
                    return 1
                if offset_months is None:
                    print(f"ERROR: milestone entry for {type_name}/{class_key} missing offset_months")
                    return 1
                milestone_ids.append(str(milestone_id))

            milestone_ids = sorted(milestone_ids)
            first_ids = milestone_ids[:2]
            last_ids = milestone_ids[-2:] if len(milestone_ids) > 2 else milestone_ids
            total_months = cfg.get("total_months")

            print(
                f"{class_key}: total_months={total_months} "
                f"milestones={len(milestone_ids)} first={first_ids} last={last_ids}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
