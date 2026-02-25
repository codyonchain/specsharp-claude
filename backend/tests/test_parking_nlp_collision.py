import pytest

from app.services.nlp_service import NLPService
from app.v2.engines.unified_engine import unified_engine


@pytest.fixture(scope="module")
def nlp_parser() -> NLPService:
    return NLPService()


@pytest.mark.parametrize(
    "description,expected_type",
    [
        ("luxury apartments with parking garage", "multifamily"),
        ("hotel with underground parking", "hospitality"),
        ("office tower with structured parking", "office"),
    ],
)
def test_parking_mentions_do_not_override_non_parking_primary_intent(
    nlp_parser: NLPService,
    description: str,
    expected_type: str,
):
    parsed = nlp_parser.extract_project_details(description)
    assert parsed["building_type"] == expected_type
    assert parsed["building_type"] != "parking"


@pytest.mark.parametrize(
    "description,expected_subtype",
    [
        ("new standalone parking garage", "parking_garage"),
        ("automated parking structure", "automated_parking"),
        ("surface parking lot expansion", "surface_parking"),
    ],
)
def test_parking_primary_intents_route_to_parking_with_expected_subtype(
    nlp_parser: NLPService,
    description: str,
    expected_subtype: str,
):
    parsed = nlp_parser.extract_project_details(description)
    assert parsed["building_type"] == "parking"
    assert parsed["subtype"] == expected_subtype
    assert parsed["detection_source"] == "nlp_service.parking_primary_intent"
    assert str(parsed["detection_conflict_resolution"]).startswith("parking_primary_")


def test_unknown_parking_subtype_is_explicit_when_intent_is_primary(nlp_parser: NLPService):
    parsed = nlp_parser.extract_project_details("new standalone parking facility in Nashville, TN")
    assert parsed["building_type"] == "parking"
    assert parsed["subtype"] is None
    assert parsed["building_subtype"] is None
    assert parsed["detection_source"] == "nlp_service.parking_primary_intent"
    assert parsed["detection_conflict_resolution"] == "parking_primary_standalone"


def test_parking_collision_provenance_surfaces_in_parser_and_engine():
    description = "luxury apartments with parking garage"
    parsed = NLPService().extract_project_details(description)
    assert parsed["building_type"] == "multifamily"
    assert parsed["detection_source"] == "nlp_service.parking_conflict_router"
    assert parsed["detection_conflict_resolution"] == "parking_demoted_multifamily_primary"

    estimate = unified_engine.estimate_from_description(
        description=description,
        square_footage=100_000,
        location="Nashville, TN",
    )
    detection_info = estimate.get("detection_info")
    assert isinstance(detection_info, dict)
    assert detection_info.get("detected_type") == "multifamily"
    assert str(detection_info.get("detection_source", "")).startswith("nlp_service.parking_conflict_router")
    assert detection_info.get("detection_conflict_outcome") == "parking_demoted_multifamily_primary"
