from app.v2.config.master_config import BuildingType, get_building_config
from app.v2.config.type_profiles.dealshield_tiles import get_dealshield_profile
from app.v2.config.type_profiles.dealshield_tiles.specialty import DEALSHIELD_TILE_DEFAULTS
from app.v2.config.type_profiles.dealshield_content import specialty as specialty_content
from app.v2.config.type_profiles.scope_items import specialty as specialty_scope_items
from app.v2.engines.unified_engine import unified_engine
from app.v2.config.master_config import ProjectClass
from app.v2.services.dealshield_service import build_dealshield_view_model
from tests.dealshield_contract_assertions import assert_decision_insurance_truth_parity


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

SPECIALTY_SCOPE_MIN_ITEMS_BY_SUBTYPE = {
    "data_center": {
        "structural": 3,
        "mechanical": 4,
        "electrical": 4,
        "plumbing": 3,
        "finishes": 3,
    },
    "laboratory": {
        "structural": 2,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 3,
        "finishes": 2,
    },
    "self_storage": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 2,
        "finishes": 2,
    },
    "car_dealership": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 2,
        "finishes": 2,
    },
    "broadcast_facility": {
        "structural": 3,
        "mechanical": 3,
        "electrical": 3,
        "plumbing": 2,
        "finishes": 2,
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


def test_specialty_scope_profile_trade_item_depth_by_subtype():
    for subtype, expected in SPECIALTY_PROFILE_MAP.items():
        scope_profile = specialty_scope_items.SCOPE_ITEM_PROFILES[expected["scope"]]
        trade_profiles = scope_profile.get("trade_profiles")
        assert isinstance(trade_profiles, list) and trade_profiles
        trade_map = {
            trade.get("trade_key"): trade
            for trade in trade_profiles
            if isinstance(trade, dict) and isinstance(trade.get("trade_key"), str)
        }

        for trade_key, min_items in SPECIALTY_SCOPE_MIN_ITEMS_BY_SUBTYPE[subtype].items():
            trade = trade_map.get(trade_key)
            assert isinstance(trade, dict), f"missing {trade_key} in {expected['scope']}"
            items = trade.get("items")
            assert isinstance(items, list)
            assert len(items) >= min_items, (
                f"{expected['scope']}::{trade_key} expected >= {min_items} scope items, "
                f"found {len(items)}"
            )


def test_specialty_scope_trade_allocation_shares_sum_to_one():
    for expected in SPECIALTY_PROFILE_MAP.values():
        scope_profile = specialty_scope_items.SCOPE_ITEM_PROFILES[expected["scope"]]
        for trade_profile in scope_profile.get("trade_profiles", []):
            items = trade_profile.get("items")
            assert isinstance(items, list) and items
            total_share = 0.0
            for item in items:
                allocation = item.get("allocation")
                assert isinstance(allocation, dict)
                assert allocation.get("type") == "share_of_trade"
                share = allocation.get("share")
                assert isinstance(share, (int, float))
                total_share += float(share)
            assert abs(total_share - 1.0) <= 1e-9, (
                f"{scope_profile['profile_id']}::{trade_profile.get('trade_key')} "
                f"share total must equal 1.0, got {total_share}"
            )


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


def test_specialty_wave1_scenarios_emit_for_all_profiles():
    for subtype, expected in SPECIALTY_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.SPECIALTY,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        assert payload.get("dealshield_tile_profile") == expected["tile"]
        scenario_block = payload.get("dealshield_scenarios")
        assert isinstance(scenario_block, dict)
        assert scenario_block.get("profile_id") == expected["tile"]
        scenario_ids = scenario_block.get("scenario_ids")
        if not isinstance(scenario_ids, list):
            provenance = scenario_block.get("provenance")
            scenario_ids = provenance.get("scenario_ids") if isinstance(provenance, dict) else None
        assert isinstance(scenario_ids, list)
        assert "base" in scenario_ids
        assert "conservative" in scenario_ids
        assert "ugly" in scenario_ids
        assert expected["stress"] in scenario_ids


def test_specialty_decision_insurance_policy_contract_outputs():
    for subtype, expected in SPECIALTY_PROFILE_MAP.items():
        payload = unified_engine.calculate_project(
            building_type=BuildingType.SPECIALTY,
            subtype=subtype,
            square_footage=80_000,
            location="Nashville, TN",
            project_class=ProjectClass.GROUND_UP,
        )
        profile = get_dealshield_profile(expected["tile"])
        view_model = build_dealshield_view_model(
            project_id=f"specialty-policy-{subtype}",
            payload=payload,
            profile=profile,
        )
        assert_decision_insurance_truth_parity(view_model)

        provenance = view_model.get("decision_insurance_provenance")
        assert isinstance(provenance, dict)
        policy_block = provenance.get("decision_insurance_policy")
        assert isinstance(policy_block, dict)
        assert policy_block.get("status") == "available"
        assert policy_block.get("profile_id") == expected["tile"]

        primary_control = view_model.get("primary_control_variable")
        assert isinstance(primary_control, dict)
        assert isinstance(primary_control.get("tile_id"), str) and primary_control.get("tile_id")

        first_break = provenance.get("first_break_condition")
        assert isinstance(first_break, dict)
        assert first_break.get("source") in {
            "decision_insurance_policy.collapse_trigger",
            "decision_table.rows.stabilized_value.value_gap",
        }

        flex = provenance.get("flex_before_break_pct")
        assert isinstance(flex, dict)
        assert flex.get("status") == "available"
        assert flex.get("calibration_source") == "decision_insurance_policy.flex_calibration"
