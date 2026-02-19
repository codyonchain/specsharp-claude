"""
Tests for active NLP project naming contract.

Current behavior:
- extract_project_details() returns parsed fields only.
- generate_project_name() derives a deterministic "<Subtype|Type> in <Location>" label.
"""

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
        assert parsed["subtype"] == "medical_office"
        assert parsed["square_footage"] == 75000
        assert name == "Medical Office in Nashville"

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
        assert parsed["subtype"] == "medical_office"
        assert parsed["square_footage"] is None
        assert "detail_suggestions" not in parsed
        assert name == "Medical Office in Manchester"

    def test_detail_suggestions_warehouse(self):
        description = "New warehouse facility"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "industrial"
        assert parsed["subtype"] == "warehouse"
        assert parsed["square_footage"] is None
        assert "detail_suggestions" not in parsed
        assert name == "Warehouse in Nashville"
