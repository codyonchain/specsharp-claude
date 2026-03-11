import pytest

from app.services.nlp_service import NLPService


@pytest.fixture(scope="module")
def nlp_parser() -> NLPService:
    return NLPService()


@pytest.mark.parametrize(
    "description,expected_subtype",
    [
        (
            "New 185,000 SF luxury apartment complex with concierge lobby and resident gym in Nashville, TN",
            "luxury_apartments",
        ),
        (
            "New 220,000 SF luxury apartment complex with fitness center and pool in Nashville, TN",
            "luxury_apartments",
        ),
        (
            "New 200,000 SF apartment building with rooftop amenity and pool in Nashville, TN",
            "market_rate_apartments",
        ),
    ],
)
def test_strong_multifamily_intent_is_not_rerouted_by_amenity_language(
    nlp_parser: NLPService,
    description: str,
    expected_subtype: str,
):
    parsed = nlp_parser.extract_project_details(description)

    assert parsed["building_type"] == "multifamily"
    assert parsed["subtype"] == expected_subtype
    assert parsed["building_subtype"] == expected_subtype


def test_clear_fitness_center_prompt_still_routes_to_recreation(nlp_parser: NLPService):
    parsed = nlp_parser.extract_project_details(
        "New 60,000 SF standalone fitness center with locker rooms and group fitness studios in Nashville, TN"
    )

    assert parsed["building_type"] == "recreation"
    assert parsed["subtype"] == "fitness_center"
    assert parsed["building_subtype"] == "fitness_center"
