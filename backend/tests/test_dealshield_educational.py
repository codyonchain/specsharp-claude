import math

from app.v2.config.master_config import (
    BuildingType,
    get_building_config,
)
from app.v2.config.type_profiles.dealshield_content import educational as educational_content
from app.v2.config.type_profiles.scope_items import educational as educational_scope_profiles
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile


EDUCATIONAL_PROFILE_IDS = {
    "elementary_school": {
        "tile_profile": "educational_elementary_school_v1",
        "scope_profile": "educational_elementary_school_structural_v1",
    },
    "middle_school": {
        "tile_profile": "educational_middle_school_v1",
        "scope_profile": "educational_middle_school_structural_v1",
    },
    "high_school": {
        "tile_profile": "educational_high_school_v1",
        "scope_profile": "educational_high_school_structural_v1",
    },
    "university": {
        "tile_profile": "educational_university_v1",
        "scope_profile": "educational_university_structural_v1",
    },
    "community_college": {
        "tile_profile": "educational_community_college_v1",
        "scope_profile": "educational_community_college_structural_v1",
    },
}

EDUCATIONAL_SCOPE_DEPTH_FLOORS = {
    "elementary_school": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "middle_school": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
    "high_school": {
        "structural": 4,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 4,
        "finishes": 4,
    },
    "university": {
        "structural": 4,
        "mechanical": 5,
        "electrical": 5,
        "plumbing": 4,
        "finishes": 4,
    },
    "community_college": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 3,
    },
}


def _profile_tile_ids(profile):
    return {
        tile.get("tile_id")
        for tile in profile.get("tiles", [])
        if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
    }


def test_educational_subtype_wiring_is_explicit():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        cfg = get_building_config(BuildingType.EDUCATIONAL, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile_profile"]
        assert cfg.scope_items_profile == expected["scope_profile"]

        tile_profile = get_dealshield_profile(expected["tile_profile"])
        assert tile_profile.get("profile_id") == expected["tile_profile"]
        assert _profile_tile_ids(tile_profile)

        assert educational_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype] == expected["scope_profile"]
        assert expected["scope_profile"] in educational_scope_profiles.SCOPE_ITEM_PROFILES


def test_educational_profiles_are_not_clones_across_tiles_content_and_scope():
    primary_tile_ids = []
    subtype_row_ids = []
    first_mlw_texts = []
    scope_signatures = []

    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        tile_profile = get_dealshield_profile(expected["tile_profile"])
        tile_ids = _profile_tile_ids(tile_profile)
        primary_tiles = sorted(tile_ids - {"cost_plus_10", "revenue_minus_10"})
        assert len(primary_tiles) == 1
        primary_tile_ids.append(primary_tiles[0])

        row_ids = {
            row.get("row_id")
            for row in tile_profile.get("derived_rows", [])
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        }
        subtype_rows = sorted(row_ids - {"conservative", "ugly"})
        assert len(subtype_rows) == 1
        subtype_row_ids.append(subtype_rows[0])

        content = educational_content.DEALSHIELD_CONTENT_PROFILES[expected["tile_profile"]]
        first_mlw_texts.append(content["most_likely_wrong"][0]["text"])

        scope_profile = educational_scope_profiles.SCOPE_ITEM_PROFILES[expected["scope_profile"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.append(signature)

    assert len(primary_tile_ids) == len(set(primary_tile_ids))
    assert len(subtype_row_ids) == len(set(subtype_row_ids))
    assert len(first_mlw_texts) == len(set(first_mlw_texts))
    assert len(scope_signatures) == len(set(scope_signatures))


def test_educational_content_references_existing_tile_ids():
    for subtype, expected in EDUCATIONAL_PROFILE_IDS.items():
        profile_id = expected["tile_profile"]
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = _profile_tile_ids(tile_profile)
        assert tile_ids

        content = educational_content.DEALSHIELD_CONTENT_PROFILES[profile_id]
        drivers = content.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        for entry in mlw:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids
            assert isinstance(entry.get("text"), str) and entry.get("text").strip()
            assert isinstance(entry.get("why"), str) and entry.get("why").strip()

        question_bank = content.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for entry in question_bank:
            assert isinstance(entry, dict)
            assert entry.get("driver_tile_id") in tile_ids
            questions = entry.get("questions")
            assert isinstance(questions, list) and questions
            assert all(isinstance(question, str) and question.strip() for question in questions)


def test_educational_scope_profiles_keep_depth_floors_and_allocation_sum_to_one():
    for subtype, floors in EDUCATIONAL_SCOPE_DEPTH_FLOORS.items():
        profile_id = educational_scope_profiles.SCOPE_ITEM_DEFAULTS[subtype]
        profile = educational_scope_profiles.SCOPE_ITEM_PROFILES[profile_id]
        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5

        by_trade = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(by_trade.keys()) == {"structural", "mechanical", "electrical", "plumbing", "finishes"}

        for trade_key, minimum_items in floors.items():
            items = by_trade[trade_key].get("items")
            assert isinstance(items, list)
            assert len(items) >= minimum_items
            total_share = sum(
                float(item.get("allocation", {}).get("share", 0.0))
                for item in items
            )
            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{profile_id}::{trade_key} share total expected 1.0, got {total_share}"
            )
