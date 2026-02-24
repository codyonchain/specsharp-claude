from app.v2.config.master_config import BuildingType, get_building_config
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles.specialty import DEALSHIELD_TILE_DEFAULTS
from app.v2.config.type_profiles.dealshield_content import specialty as specialty_content
from app.v2.config.type_profiles.scope_items import specialty as specialty_scope_items


SPECIALTY_PROFILE_MAP = {
    "data_center": {
        "tile": "specialty_data_center_v1",
        "scope": "specialty_data_center_structural_v1",
        "stress": "commissioning_failure_window",
    },
    "laboratory": {
        "tile": "specialty_laboratory_v1",
        "scope": "specialty_laboratory_structural_v1",
        "stress": "validation_retest_cycle",
    },
    "self_storage": {
        "tile": "specialty_self_storage_v1",
        "scope": "specialty_self_storage_structural_v1",
        "stress": "leaseup_drag",
    },
    "car_dealership": {
        "tile": "specialty_car_dealership_v1",
        "scope": "specialty_car_dealership_structural_v1",
        "stress": "service_absorption_slip",
    },
    "broadcast_facility": {
        "tile": "specialty_broadcast_facility_v1",
        "scope": "specialty_broadcast_facility_structural_v1",
        "stress": "control_room_recommissioning",
    },
}


def test_specialty_subtypes_wire_scope_and_tile_profiles():
    for subtype, expected in SPECIALTY_PROFILE_MAP.items():
        config = get_building_config(BuildingType.SPECIALTY, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_specialty_scope_and_tile_defaults_are_stable():
    scope_defaults = specialty_scope_items.SCOPE_ITEM_DEFAULTS.get("specialty_profile_by_subtype")
    assert isinstance(scope_defaults, dict)
    assert DEALSHIELD_TILE_DEFAULTS == {
        subtype: values["tile"] for subtype, values in SPECIALTY_PROFILE_MAP.items()
    }
    assert scope_defaults == {
        subtype: values["scope"] for subtype, values in SPECIALTY_PROFILE_MAP.items()
    }


def test_specialty_tile_profiles_resolve_with_required_shape():
    for subtype, expected in SPECIALTY_PROFILE_MAP.items():
        profile_id = expected["tile"]
        profile = get_dealshield_profile(profile_id)
        assert profile.get("profile_id") == profile_id
        assert profile.get("version") == "v1"
        assert isinstance(profile.get("tiles"), list) and profile["tiles"]
        assert isinstance(profile.get("derived_rows"), list) and profile["derived_rows"]

        tile_ids = [tile.get("tile_id") for tile in profile["tiles"] if isinstance(tile, dict)]
        assert all(isinstance(tile_id, str) and tile_id for tile_id in tile_ids)
        assert len(tile_ids) == len(set(tile_ids)), f"duplicate tile_id found in {profile_id}"

        scenario_ids = [row.get("row_id") for row in profile["derived_rows"] if isinstance(row, dict)]
        assert "conservative" in scenario_ids, f"missing conservative row for {profile_id}"
        assert "ugly" in scenario_ids, f"missing ugly row for {profile_id}"
        assert any(
            scenario_id not in {"conservative", "ugly"} for scenario_id in scenario_ids
        ), f"missing subtype-authored stress row for {profile_id}"


def test_specialty_content_to_tile_integrity():
    for profile_id, content in specialty_content.DEALSHIELD_CONTENT_PROFILES.items():
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        fastest_change = content.get("fastest_change")
        assert isinstance(fastest_change, dict)
        drivers = fastest_change.get("drivers")
        assert isinstance(drivers, list) and drivers
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        most_likely_wrong = content.get("most_likely_wrong")
        assert isinstance(most_likely_wrong, list) and most_likely_wrong
        for item in most_likely_wrong:
            assert isinstance(item, dict)
            assert isinstance(item.get("text"), str) and item["text"].strip()
            assert isinstance(item.get("why"), str) and item["why"].strip()
            assert item.get("driver_tile_id") in tile_ids

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and question_bank
        for group in question_bank:
            assert isinstance(group, dict)
            assert group.get("driver_tile_id") in tile_ids
            questions = group.get("questions")
            assert isinstance(questions, list) and questions


def test_specialty_no_clone_invariants():
    profiles = [
        get_dealshield_profile(values["tile"])
        for values in SPECIALTY_PROFILE_MAP.values()
    ]
    primary_tile_ids = []
    first_mlw_texts = []

    for profile in profiles:
        tiles = profile.get("tiles")
        assert isinstance(tiles, list) and tiles
        primary_tile_ids.append(tiles[0].get("tile_id"))

        content = specialty_content.DEALSHIELD_CONTENT_PROFILES[profile["profile_id"]]
        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and mlw
        first_mlw_texts.append(mlw[0].get("text"))

    assert len(primary_tile_ids) == len(set(primary_tile_ids))
    assert len(first_mlw_texts) == len(set(first_mlw_texts))
