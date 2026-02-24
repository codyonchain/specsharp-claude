"""
Tests for active NLP project naming contract.

Current behavior:
- extract_project_details() returns parsed fields only.
- generate_project_name() derives a deterministic "<Subtype|Type> in <Location>" label.
"""

import pytest

from app.services.nlp_service import NLPService


class TestProjectNameGeneration:
    """Validate deterministic name generation from active parser output."""

    def setup_method(self):
        self.nlp_service = NLPService()

    def _parse_and_name(self, description: str):
        parsed = self.nlp_service.extract_project_details(description)
        name = self.nlp_service.generate_project_name(description, parsed)
        return parsed, name

    def test_hospital_addition_name(self):
        description = "Expand hospital with new 50000 sf surgical wing including 8 operating rooms in Manchester, NH"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == "hospital"
        assert parsed["location"] == "Manchester"
        assert name == "Hospital in Manchester"

    def test_restaurant_ground_up_name(self):
        description = "New 4000 sf fast-casual restaurant with commercial kitchen in Nashville"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "restaurant"
        assert parsed["subtype"] == "full_service"
        assert parsed["project_classification"] == "ground_up"
        assert name == "Full Service in Nashville"

    def test_retail_to_clinic_conversion(self):
        description = "Convert 8000 sf retail space to urgent care clinic with 12 exam rooms"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == "urgent_care"
        assert parsed["project_classification"] == "renovation"
        assert name == "Urgent Care in Nashville"

    def test_restaurant_renovation_downtown(self):
        description = "Full gut renovation of 5000 sf restaurant in downtown Manchester"
        parsed, name = self._parse_and_name(description)

        assert parsed["subtype"] == "full_service"
        assert parsed["project_classification"] == "renovation"
        assert parsed["location"] == "Downtown"
        assert name == "Full Service in Downtown"

    def test_medical_office_with_imaging(self):
        description = "Build new 75000 sf Class A medical office building with imaging center"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == "medical_office_building"
        assert parsed["square_footage"] == 75000
        assert name == "Medical Office Building in Nashville"

    def test_warehouse_with_docks(self):
        description = "New 150000 sf distribution warehouse with 30-foot clear height and 20 loading docks in Memphis, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "industrial"
        assert parsed["subtype"] == "warehouse"
        assert parsed["location"] == "Memphis"
        assert name == "Warehouse in Memphis"

    def test_school_addition(self):
        description = "Building extension adding 15000 sf of classroom space to existing high school"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "educational"
        assert parsed["subtype"] == "high_school"
        assert parsed["project_classification"] == "addition"
        assert name == "High School in Nashville"

    def test_surgical_center_with_features(self):
        description = "Construct 10000 sf addition to medical clinic for outpatient surgery center with 4 procedure rooms"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == "surgical_center"
        assert parsed["project_classification"] == "addition"
        assert name == "Surgical Center in Nashville"

    def test_restaurant_with_patio(self):
        description = "New 6000 sf restaurant with outdoor patio and full bar in Franklin, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "restaurant"
        assert parsed["subtype"] == "bar_tavern"
        assert parsed["location"] == "Franklin"
        assert name == "Bar Tavern in Franklin"

    def test_name_length_truncation(self):
        description = (
            "Build new 100000 sf hospital with emergency department, surgical wing, imaging center, "
            "laboratory, pharmacy, outpatient clinic, and administrative offices in Manchester, New Hampshire"
        )
        parsed, name = self._parse_and_name(description)

        assert parsed["subtype"] == "hospital"
        assert name == "Hospital in Manchester"
        assert len(name) <= 65

    def test_detail_suggestions_restaurant(self):
        description = "New restaurant in Nashville"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "restaurant"
        assert parsed["subtype"] == "full_service"
        assert parsed["square_footage"] is None
        assert "detail_suggestions" not in parsed
        assert name == "Full Service in Nashville"

    def test_detail_suggestions_healthcare(self):
        description = "New medical clinic in Manchester"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == "medical_office_building"
        assert parsed["square_footage"] is None
        assert "detail_suggestions" not in parsed
        assert name == "Medical Office Building in Manchester"

    def test_detail_suggestions_warehouse(self):
        description = "New warehouse facility"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "industrial"
        assert parsed["subtype"] == "warehouse"
        assert parsed["square_footage"] is None
        assert "detail_suggestions" not in parsed
        assert name == "Warehouse in Nashville"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 3200 sf quick service restaurant with drive thru in Nashville, TN",
                "quick_service",
                "Quick Service in Nashville",
            ),
            (
                "New 4800 sf full service restaurant with table service in Nashville, TN",
                "full_service",
                "Full Service in Nashville",
            ),
            (
                "New 5200 sf fine dining restaurant with tasting menu in Nashville, TN",
                "fine_dining",
                "Fine Dining in Nashville",
            ),
            (
                "New 2600 sf cafe coffee shop with bakery counter in Nashville, TN",
                "cafe",
                "Cafe in Nashville",
            ),
            (
                "New 4500 sf tavern pub with cocktail lounge in Nashville, TN",
                "bar_tavern",
                "Bar Tavern in Nashville",
            ),
        ],
    )
    def test_restaurant_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "restaurant"
        assert parsed["subtype"] == expected_subtype
        assert name == expected_name

    @pytest.mark.parametrize(
        "description",
        [
            "Build a 128,000 SF limited service hotel with 210 keys, breakfast area, fitness center, business center, and pool in Nashville, TN.",
            "Build a 128,000 SF limited service hotel with 210 keys in Nashville, TN.",
        ],
    )
    def test_limited_service_hotel_intent_wins_over_amenity_overlap(self, description):
        parsed, _ = self._parse_and_name(description)

        assert parsed["building_type"] == "hospitality"
        assert parsed["subtype"] == "limited_service_hotel"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 120000 sf tier iv data center with redundant power trains in Nashville, TN",
                "data_center",
                "Data Center in Nashville",
            ),
            (
                "New 45000 sf biotech laboratory with clean room suites in Nashville, TN",
                "laboratory",
                "Laboratory in Nashville",
            ),
            (
                "New 80000 sf self storage facility with climate control in Nashville, TN",
                "self_storage",
                "Self Storage in Nashville",
            ),
            (
                "New 35000 sf auto dealership with service bays and showroom in Nashville, TN",
                "car_dealership",
                "Car Dealership in Nashville",
            ),
            (
                "New 42000 sf broadcast studio and soundstage production facility in Nashville, TN",
                "broadcast_facility",
                "Broadcast Facility in Nashville",
            ),
        ],
    )
    def test_specialty_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "specialty"
        assert parsed["subtype"] == expected_subtype
        assert name == expected_name

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 28000 sf ambulatory surgery center with 6 OR suites in Nashville, TN",
                "surgical_center",
                "Surgical Center in Nashville",
            ),
            (
                "New 32000 sf diagnostic imaging center with MRI and CT suites in Nashville, TN",
                "imaging_center",
                "Imaging Center in Nashville",
            ),
            (
                "New 14000 sf urgent care center with walk-in triage in Nashville, TN",
                "urgent_care",
                "Urgent Care in Nashville",
            ),
            (
                "New 36000 sf outpatient clinic for primary care in Nashville, TN",
                "outpatient_clinic",
                "Outpatient Clinic in Nashville",
            ),
            (
                "New 85000 sf medical office building with physician suites in Nashville, TN",
                "medical_office_building",
                "Medical Office Building in Nashville",
            ),
            (
                "New 9000 sf dental office with sterilization bay in Nashville, TN",
                "dental_office",
                "Dental Office in Nashville",
            ),
            (
                "New 240000 sf acute care hospital with emergency department in Nashville, TN",
                "hospital",
                "Hospital in Nashville",
            ),
            (
                "New 180000 sf regional medical center campus in Nashville, TN",
                "medical_center",
                "Medical Center in Nashville",
            ),
            (
                "New 70000 sf skilled nursing facility with long-term care beds in Nashville, TN",
                "nursing_home",
                "Nursing Home in Nashville",
            ),
            (
                "New 42000 sf rehabilitation center with therapy gym in Nashville, TN",
                "rehabilitation",
                "Rehabilitation in Nashville",
            ),
        ],
    )
    def test_healthcare_subtype_discoverability_all_ten_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "healthcare"
        assert parsed["subtype"] == expected_subtype
        assert name == expected_name

    def test_recreation_prompt_with_pool_and_fitness_remains_recreation(self):
        description = (
            "Build a 110,000 SF aquatic center and sports complex with indoor pool, "
            "fitness studios, and basketball courts in Nashville, TN."
        )
        parsed, _ = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
