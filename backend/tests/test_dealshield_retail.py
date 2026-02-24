import math

from app.v2.config.master_config import BuildingType, get_building_config
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import retail as retail_tile_profiles
from app.v2.config.type_profiles.dealshield_content import retail as retail_content_profiles
from app.v2.config.type_profiles.scope_items import retail as retail_scope_profiles


RETAIL_PROFILE_MAP = {
    "shopping_center": {
        "tile": "retail_shopping_center_v1",
        "scope": "retail_shopping_center_structural_v1",
    },
    "big_box": {
        "tile": "retail_big_box_v1",
        "scope": "retail_big_box_structural_v1",
    },
}

RETAIL_SCOPE_DEPTH_FLOOR = {
    "shopping_center": {
        "structural": 4,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 3,
        "finishes": 4,
    },
    "big_box": {
        "structural": 5,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 3,
        "finishes": 4,
    },
}


def _scope_trade_map(profile_id: str) -> dict[str, dict]:
    profile = retail_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
    return {
        trade.get("trade_key"): trade
        for trade in profile.get("trade_profiles", [])
        if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
    }


def test_retail_subtypes_wire_explicit_tile_and_scope_profiles():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        config = get_building_config(BuildingType.RETAIL, subtype)
        assert config is not None
        assert config.dealshield_tile_profile == expected["tile"]
        assert config.scope_items_profile == expected["scope"]


def test_retail_registries_and_defaults_are_non_empty_and_deterministic():
    assert retail_tile_profiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: expected["tile"] for subtype, expected in RETAIL_PROFILE_MAP.items()
    }
    assert retail_scope_profiles.SCOPE_ITEM_DEFAULTS == {
        subtype: expected["scope"] for subtype, expected in RETAIL_PROFILE_MAP.items()
    }

    assert retail_tile_profiles.DEALSHIELD_TILE_PROFILES
    assert retail_content_profiles.DEALSHIELD_CONTENT_PROFILES
    assert retail_scope_profiles.SCOPE_ITEM_PROFILES


def test_retail_scope_profiles_meet_depth_floor_and_normalized_shares():
    for subtype, expected in RETAIL_PROFILE_MAP.items():
        trade_map = _scope_trade_map(expected["scope"])
        assert set(trade_map.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum in RETAIL_SCOPE_DEPTH_FLOOR[subtype].items():
            items = trade_map[trade_key].get("items")
            assert isinstance(items, list) and len(items) >= minimum
            total_share = sum(float(item.get("allocation", {}).get("share", 0.0)) for item in items)
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total expected 1.0, got {total_share}"
            )


def test_retail_content_to_tile_integrity():
    for profile_id in RETAIL_PROFILE_MAP.values():
        resolved_profile_id = profile_id["tile"]
        tile_profile = get_dealshield_profile(resolved_profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[resolved_profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and drivers
        for driver in drivers:
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        for item in mlw:
            assert item.get("driver_tile_id") in tile_ids
            assert isinstance(item.get("text"), str) and item["text"].strip()
            assert isinstance(item.get("why"), str) and item["why"].strip()

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for entry in question_bank:
            assert entry.get("driver_tile_id") in tile_ids
            questions = entry.get("questions")
            assert isinstance(questions, list) and len(questions) >= 2


def test_retail_profiles_are_authored_not_clones():
    shopping_tile = get_dealshield_profile(RETAIL_PROFILE_MAP["shopping_center"]["tile"])
    big_box_tile = get_dealshield_profile(RETAIL_PROFILE_MAP["big_box"]["tile"])

    assert shopping_tile["tiles"][2]["tile_id"] != big_box_tile["tiles"][2]["tile_id"]

    shopping_rows = {row["row_id"] for row in shopping_tile["derived_rows"]}
    big_box_rows = {row["row_id"] for row in big_box_tile["derived_rows"]}
    assert shopping_rows != big_box_rows

    shopping_content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[RETAIL_PROFILE_MAP["shopping_center"]["tile"]]
    big_box_content = retail_content_profiles.DEALSHIELD_CONTENT_PROFILES[RETAIL_PROFILE_MAP["big_box"]["tile"]]
    assert shopping_content["most_likely_wrong"][0]["text"] != big_box_content["most_likely_wrong"][0]["text"]
    assert shopping_content["fastest_change"]["drivers"][2]["label"] != big_box_content["fastest_change"]["drivers"][2]["label"]

    shopping_scope = _scope_trade_map(RETAIL_PROFILE_MAP["shopping_center"]["scope"])
    big_box_scope = _scope_trade_map(RETAIL_PROFILE_MAP["big_box"]["scope"])
    shopping_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(shopping_scope.items())
    )
    big_box_signature = tuple(
        (trade_key, tuple(item["key"] for item in trade.get("items", [])))
        for trade_key, trade in sorted(big_box_scope.items())
    )
    assert shopping_signature != big_box_signature
