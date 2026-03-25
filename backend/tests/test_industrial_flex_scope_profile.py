import pytest

from app.services.nlp_service import NLPService
from app.v2.config.master_config import BuildingType, ProjectClass
from app.v2.engines.unified_engine import unified_engine


ANCHOR_DESCRIPTION = (
    "125,000 SF single-story Class A industrial flex space with 30% office/showroom "
    "buildout, rear loading, and surface parking in Nashville, TN"
)
DEFAULT_DESCRIPTION = (
    "125,000 SF single-story Class A industrial flex space with rear loading in Nashville, TN"
)


def _construction_view_system(payload, trade_label, system_name):
    scope_items = payload.get("construction_view_scope_items") or payload.get("scope_items")
    assert isinstance(scope_items, list) and scope_items

    for trade in scope_items:
        if trade.get("trade") != trade_label:
            continue
        for system in trade.get("systems") or []:
            if isinstance(system, dict) and system.get("name") == system_name:
                return system

    raise AssertionError(f"Missing scope system '{system_name}' in trade '{trade_label}'")


def _calculate_flex_payload(*, parsed_input_overrides=None):
    return unified_engine.calculate_project(
        building_type=BuildingType.INDUSTRIAL,
        subtype="flex_space",
        square_footage=125_000,
        location="Nashville, TN",
        project_class=ProjectClass.GROUND_UP,
        floors=1,
        parsed_input_overrides=parsed_input_overrides,
    )


def _calculate_flex_payload_from_description(description):
    parsed = NLPService().extract_project_details(description)
    return parsed, _calculate_flex_payload(parsed_input_overrides=parsed)


def test_flex_anchor_office_share_increases_pricing_and_scope_quantities():
    default_parsed, default_payload = _calculate_flex_payload_from_description(DEFAULT_DESCRIPTION)
    parsed, payload = _calculate_flex_payload_from_description(ANCHOR_DESCRIPTION)

    assert parsed["subtype"] == "flex_space"
    assert parsed["office_share"] == pytest.approx(0.3)
    assert "office_percent" not in parsed
    assert default_parsed["subtype"] == "flex_space"
    assert "office_share" not in default_parsed

    default_construction_costs = default_payload["construction_costs"]
    explicit_construction_costs = payload["construction_costs"]
    finishes_row = _construction_view_system(
        payload,
        "Finishes",
        "Office and showroom partitions (gypsum assemblies)",
    )
    default_finishes_row = _construction_view_system(
        default_payload,
        "Finishes",
        "Office and showroom partitions (gypsum assemblies)",
    )
    mechanical_row = _construction_view_system(
        payload,
        "Mechanical",
        "Office/showroom VAV and split-system conditioning",
    )
    default_mechanical_row = _construction_view_system(
        default_payload,
        "Mechanical",
        "Office/showroom VAV and split-system conditioning",
    )

    assert explicit_construction_costs["final_cost_per_sf"] > default_construction_costs["final_cost_per_sf"]
    assert explicit_construction_costs["construction_total"] > default_construction_costs["construction_total"]
    assert payload["trade_breakdown"]["finishes"] > default_payload["trade_breakdown"]["finishes"]
    assert payload["trade_breakdown"]["mechanical"] > default_payload["trade_breakdown"]["mechanical"]
    assert finishes_row["quantity"] == pytest.approx(37_500.0)
    assert mechanical_row["quantity"] == pytest.approx(37_500.0)
    assert default_finishes_row["quantity"] == pytest.approx(25_000.0)
    assert default_mechanical_row["quantity"] == pytest.approx(25_000.0)
    assert finishes_row["total_cost"] > default_finishes_row["total_cost"]
    assert mechanical_row["total_cost"] > default_mechanical_row["total_cost"]


def test_flex_office_share_alias_affects_pricing_without_frontend_normalization():
    default_payload = _calculate_flex_payload(parsed_input_overrides={})
    payload = _calculate_flex_payload(
        parsed_input_overrides={
            "description": ANCHOR_DESCRIPTION,
            "office_share": 0.3,
        },
    )

    finishes_row = _construction_view_system(
        payload,
        "Finishes",
        "Office and showroom partitions (gypsum assemblies)",
    )

    assert payload["construction_costs"]["final_cost_per_sf"] > default_payload["construction_costs"]["final_cost_per_sf"]
    assert payload["construction_costs"]["construction_total"] > default_payload["construction_costs"]["construction_total"]
    assert finishes_row["quantity"] == pytest.approx(37_500.0)


def test_flex_default_scope_quantities_and_pricing_remain_unchanged_without_explicit_office_share():
    parsed, payload = _calculate_flex_payload_from_description(DEFAULT_DESCRIPTION)

    assert parsed["subtype"] == "flex_space"
    assert "office_share" not in parsed

    finishes_row = _construction_view_system(
        payload,
        "Finishes",
        "Office and showroom partitions (gypsum assemblies)",
    )
    mechanical_row = _construction_view_system(
        payload,
        "Mechanical",
        "Office/showroom VAV and split-system conditioning",
    )

    assert payload["construction_costs"]["final_cost_per_sf"] == pytest.approx(118.45)
    assert payload["construction_costs"]["construction_total"] == pytest.approx(14_806_250.0)
    assert finishes_row["quantity"] == pytest.approx(25_000.0)
    assert mechanical_row["quantity"] == pytest.approx(25_000.0)
