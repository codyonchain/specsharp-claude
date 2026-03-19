import pytest

from app.services.nlp_service import NLPService


@pytest.fixture(scope="module")
def nlp_parser() -> NLPService:
    return NLPService()


@pytest.mark.parametrize(
    "description",
    [
        "18,000 SF urgent care center with imaging suites in Manchester, NH",
        "12,000 SF walk-in clinic with imaging suite in Nashville, TN",
    ],
)
def test_explicit_urgent_care_identity_beats_supporting_imaging_language(
    nlp_parser: NLPService,
    description: str,
):
    parsed = nlp_parser.extract_project_details(description)

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "urgent_care"
    assert parsed["building_subtype"] == "urgent_care"


@pytest.mark.parametrize(
    "description",
    [
        "12,000 SF imaging center with 2 MRI suites in Nashville, TN",
        "14,000 SF diagnostic imaging suite with CT in Nashville, TN",
    ],
)
def test_true_imaging_center_prompts_still_route_to_imaging_center(
    nlp_parser: NLPService,
    description: str,
):
    parsed = nlp_parser.extract_project_details(description)

    assert parsed["building_type"] == "healthcare"
    assert parsed["subtype"] == "imaging_center"
    assert parsed["building_subtype"] == "imaging_center"
