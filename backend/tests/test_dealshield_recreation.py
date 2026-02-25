import math

from app.v2.config.master_config import BuildingType, get_building_config
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles import recreation as recreation_tiles
from app.v2.config.type_profiles.dealshield_content import recreation as recreation_content
from app.v2.config.type_profiles.scope_items import recreation as recreation_scope


RECREATION_PROFILE_MAP = {
    "fitness_center": {
        "tile": "recreation_fitness_center_v1",
        "scope": "recreation_fitness_center_structural_v1",
    },
    "sports_complex": {
        "tile": "recreation_sports_complex_v1",
        "scope": "recreation_sports_complex_structural_v1",
    },
    "aquatic_center": {
        "tile": "recreation_aquatic_center_v1",
        "scope": "recreation_aquatic_center_structural_v1",
    },
    "recreation_center": {
        "tile": "recreation_recreation_center_v1",
        "scope": "recreation_recreation_center_structural_v1",
    },
    "stadium": {
        "tile": "recreation_stadium_v1",
        "scope": "recreation_stadium_structural_v1",
    },
}


RECREATION_SCOPE_MIN_ITEMS_BY_SUBTYPE = {
    "fitness_center": {"structural": 4, "mechanical": 5, "electrical": 4, "plumbing": 3, "finishes": 4},
    "sports_complex": {"structural": 5, "mechanical": 4, "electrical": 4, "plumbing": 3, "finishes": 4},
    "aquatic_center": {"structural": 4, "mechanical": 6, "electrical": 5, "plumbing": 5, "finishes": 4},
    "recreation_center": {"structural": 4, "mechanical": 5, "electrical": 4, "plumbing": 3, "finishes": 4},
    "stadium": {"structural": 6, "mechanical": 5, "electrical": 5, "plumbing": 4, "finishes": 5},
}


def test_recreation_subtypes_wire_scope_and_tile_profiles_explicitly():
    for subtype, expected in RECREATION_PROFILE_MAP.items():
        cfg = get_building_config(BuildingType.RECREATION, subtype)
        assert cfg is not None
        assert cfg.dealshield_tile_profile == expected["tile"]
        assert cfg.scope_items_profile == expected["scope"]


def test_recreation_defaults_map_to_matching_profile_ids():
    assert recreation_tiles.DEALSHIELD_TILE_DEFAULTS == {
        subtype: values["tile"] for subtype, values in RECREATION_PROFILE_MAP.items()
    }
    scope_defaults = recreation_scope.SCOPE_ITEM_DEFAULTS.get("default_profile_by_subtype")
    assert isinstance(scope_defaults, dict)
    assert scope_defaults == {
        subtype: values["scope"] for subtype, values in RECREATION_PROFILE_MAP.items()
    }


def test_recreation_tile_profiles_are_subtype_authored_not_clones():
    primary_tile_ids = []
    derived_row_signatures = []

    for subtype, expected in RECREATION_PROFILE_MAP.items():
        profile = get_dealshield_profile(expected["tile"])
        assert profile.get("profile_id") == expected["tile"]

        tiles = profile.get("tiles")
        assert isinstance(tiles, list) and len(tiles) >= 4
        tile_ids = [tile.get("tile_id") for tile in tiles if isinstance(tile, dict)]
        assert all(isinstance(tile_id, str) and tile_id for tile_id in tile_ids)
        assert len(tile_ids) == len(set(tile_ids))

        rows = profile.get("derived_rows")
        assert isinstance(rows, list) and rows
        row_ids = tuple(
            row.get("row_id")
            for row in rows
            if isinstance(row, dict) and isinstance(row.get("row_id"), str)
        )
        assert "conservative" in row_ids
        assert "ugly" in row_ids
        assert any(row_id not in {"conservative", "ugly"} for row_id in row_ids)

        primary_tile_ids.append(tile_ids[0])
        derived_row_signatures.append((subtype, row_ids))

    assert len(primary_tile_ids) == len(set(primary_tile_ids))
    assert len({rows for _, rows in derived_row_signatures}) == len(derived_row_signatures)


def test_recreation_content_to_tile_integrity():
    for profile_id, content_profile in recreation_content.DEALSHIELD_CONTENT_PROFILES.items():
        tile_profile = get_dealshield_profile(profile_id)
        tile_ids = {
            tile.get("tile_id")
            for tile in tile_profile.get("tiles", [])
            if isinstance(tile, dict) and isinstance(tile.get("tile_id"), str)
        }
        assert tile_ids

        drivers = content_profile.get("fastest_change", {}).get("drivers")
        assert isinstance(drivers, list) and len(drivers) == 3
        for driver in drivers:
            assert isinstance(driver, dict)
            assert driver.get("tile_id") in tile_ids

        mlw = content_profile.get("most_likely_wrong")
        assert isinstance(mlw, list) and len(mlw) >= 3
        for entry in mlw:
            assert isinstance(entry, dict)
            assert isinstance(entry.get("text"), str) and entry.get("text").strip()
            assert isinstance(entry.get("why"), str) and entry.get("why").strip()
            assert entry.get("driver_tile_id") in tile_ids

        question_bank = content_profile.get("question_bank")
        assert isinstance(question_bank, list) and len(question_bank) == 3
        for group in question_bank:
            assert isinstance(group, dict)
            assert group.get("driver_tile_id") in tile_ids
            questions = group.get("questions")
            assert isinstance(questions, list) and questions


def test_recreation_scope_profile_trade_item_depth_and_allocation_sum():
    required_trades = {"structural", "mechanical", "electrical", "plumbing", "finishes"}

    for subtype, expected in RECREATION_PROFILE_MAP.items():
        profile = recreation_scope.SCOPE_ITEM_PROFILES[expected["scope"]]
        assert profile.get("profile_id") == expected["scope"]

        trade_profiles = profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and len(trade_profiles) == 5
        trade_map = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }
        assert set(trade_map.keys()) == required_trades

        for trade_key, min_items in RECREATION_SCOPE_MIN_ITEMS_BY_SUBTYPE[subtype].items():
            trade = trade_map[trade_key]
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= min_items

            total_share = 0.0
            for item in items:
                assert isinstance(item, dict)
                allocation = item.get("allocation")
                assert isinstance(allocation, dict)
                assert allocation.get("type") == "share_of_trade"
                share = allocation.get("share")
                assert isinstance(share, (int, float))
                total_share += float(share)

            assert math.isclose(total_share, 1.0, rel_tol=1e-9, abs_tol=1e-9), (
                f"{expected['scope']}::{trade_key} share total must equal 1.0, got {total_share}"
            )


def test_recreation_no_clone_signatures_across_tile_content_and_scope():
    first_mlw_texts = []
    scope_signatures = []

    for subtype, expected in RECREATION_PROFILE_MAP.items():
        tile_profile = get_dealshield_profile(expected["tile"])
        tiles = tile_profile.get("tiles")
        assert isinstance(tiles, list) and tiles

        content_profile = recreation_content.DEALSHIELD_CONTENT_PROFILES[expected["tile"]]
        mlw = content_profile.get("most_likely_wrong")
        assert isinstance(mlw, list) and mlw
        first_mlw_text = mlw[0].get("text")
        assert isinstance(first_mlw_text, str) and first_mlw_text.strip()
        first_mlw_texts.append(first_mlw_text.strip())

        scope_profile = recreation_scope.SCOPE_ITEM_PROFILES[expected["scope"]]
        signature = tuple(
            (
                trade.get("trade_key"),
                tuple(item.get("key") for item in trade.get("items", []) if isinstance(item, dict)),
            )
            for trade in scope_profile.get("trade_profiles", [])
            if isinstance(trade, dict)
        )
        scope_signatures.append(signature)

    assert len(first_mlw_texts) == len(set(first_mlw_texts))
    assert len(scope_signatures) == len(set(scope_signatures))
