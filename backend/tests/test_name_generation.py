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

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 65000 sf class A office tower with tenant amenity floor in Nashville, TN",
                "class_a",
                "Class A in Nashville",
            ),
            (
                "Renovate 42000 sf class B office building with lobby refresh in Nashville, TN",
                "class_b",
                "Class B in Nashville",
            ),
        ],
    )
    def test_office_subtype_discoverability_for_class_a_and_class_b(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "office"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_office_unknown_subtype_is_explicit_and_not_silent_class_b_fallback(self):
        description = "New 40000 sf office building with conference suites in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "office"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Office in Nashville"

    @pytest.mark.parametrize(
        "description,expected_subtype",
        [
            (
                "New 320,000 SF Class A office tower in Nashville, TN with premium amenity floors, fitness center, cafeteria, conference center, concierge lobby, executive floor, on-site data center, structured parking, green roof, and outdoor terrace.",
                "class_a",
            ),
            (
                "New 145,000 SF Class B office renovation in Memphis, TN with conference rooms, storage space, security desk, and surface parking.",
                "class_b",
            ),
        ],
    )
    def test_office_strong_intent_guards_against_generic_amenity_reroutes(
        self,
        description,
        expected_subtype,
    ):
        parsed, _ = self._parse_and_name(description)

        assert parsed["building_type"] == "office"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype

    def test_office_building_without_class_signal_keeps_unknown_subtype(self):
        description = "New 145,000 SF office building in Memphis, TN."
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "office"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Office in Memphis"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 95,000 sf neighborhood shopping center with inline suites in Nashville, TN",
                "shopping_center",
                "Shopping Center in Nashville",
            ),
            (
                "New 180,000 sf big box retail store with loading docks and garden center in Nashville, TN",
                "big_box",
                "Big Box in Nashville",
            ),
        ],
    )
    def test_retail_subtype_discoverability_for_shopping_center_and_big_box(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "retail"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_retail_unknown_subtype_is_explicit_and_not_silent_shopping_center_fallback(self):
        description = "New 45,000 sf retail shell building in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "retail"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Retail in Nashville"

    def test_school_addition(self):
        description = "Building extension adding 15000 sf of classroom space to existing high school"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "educational"
        assert parsed["subtype"] == "high_school"
        assert parsed["project_classification"] == "addition"
        assert name == "High School in Nashville"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 42000 sf elementary school with classroom wing and cafeteria in Nashville, TN",
                "elementary_school",
                "Elementary School in Nashville",
            ),
            (
                "New 68000 sf middle school with media lab and gymnasium in Nashville, TN",
                "middle_school",
                "Middle School in Nashville",
            ),
            (
                "New 115000 sf high school with field house and performing arts hall in Nashville, TN",
                "high_school",
                "High School in Nashville",
            ),
            (
                "New 185000 sf university science and lecture complex in Nashville, TN",
                "university",
                "University in Nashville",
            ),
            (
                "Renovate 62000 sf community college workforce training center in Nashville, TN",
                "community_college",
                "Community College in Nashville",
            ),
        ],
    )
    def test_educational_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "educational"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_educational_unknown_subtype_is_explicit_and_not_silent_elementary_fallback(self):
        description = "New 38000 sf education support building in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "educational"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Educational in Nashville"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 48000 sf public library with makerspace labs and reading halls in Nashville, TN",
                "library",
                "Library in Nashville",
            ),
            (
                "New 120000 sf county courthouse with secure holding and courtroom suites in Nashville, TN",
                "courthouse",
                "Courthouse in Nashville",
            ),
            (
                "New 65000 sf municipal government building with council chambers in Nashville, TN",
                "government_building",
                "Government Building in Nashville",
            ),
            (
                "New 55000 sf community center with gymnasium and multi-purpose rooms in Nashville, TN",
                "community_center",
                "Community Center in Nashville",
            ),
            (
                "New 42000 sf public safety facility with fire station bays and dispatch center in Nashville, TN",
                "public_safety",
                "Public Safety in Nashville",
            ),
        ],
    )
    def test_civic_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "civic"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_civic_unknown_subtype_is_explicit_and_not_silent_government_fallback(self):
        description = "New 30000 sf civic administration annex in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "civic"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Civic in Nashville"

    def test_civic_library_intent_wins_over_educational_and_hospitality_overlap(self):
        description = (
            "New 60000 sf public library learning commons with campus-style study suites, "
            "guest support desks, and after-hours community programming in Nashville, TN"
        )
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "civic"
        assert parsed["subtype"] == "library"
        assert name == "Library in Nashville"

    def test_courthouse_intent_is_not_rerouted_to_generic_office(self):
        description = "Renovate 85000 sf courthouse office annex and courtroom support areas in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "civic"
        assert parsed["subtype"] == "courthouse"
        assert name == "Courthouse in Nashville"

    def test_public_safety_station_dispatch_intent_is_not_rerouted_to_broadcast(self):
        description = (
            "New 38000 sf police station and emergency dispatch center with apparatus bay in Nashville, TN"
        )
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "civic"
        assert parsed["subtype"] == "public_safety"
        assert name == "Public Safety in Nashville"

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

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 42000 sf fitness center with cardio deck and strength rooms in Nashville, TN",
                "fitness_center",
                "Fitness Center in Nashville",
            ),
            (
                "Build a 95000 sf sports complex with multiple courts and indoor track in Nashville, TN",
                "sports_complex",
                "Sports Complex in Nashville",
            ),
            (
                "New 80000 sf aquatic center with competition pool and natatorium in Nashville, TN",
                "aquatic_center",
                "Aquatic Center in Nashville",
            ),
            (
                "Renovate a 60000 sf recreation center with gymnasium and activity rooms in Nashville, TN",
                "recreation_center",
                "Recreation Center in Nashville",
            ),
            (
                "Build a 320000 sf stadium with seating bowl and event concourse in Nashville, TN",
                "stadium",
                "Stadium in Nashville",
            ),
        ],
    )
    def test_recreation_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_recreation_unknown_subtype_is_explicit_and_not_silent_recreation_center_fallback(self):
        description = "New 50000 sf recreation facility in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
        assert parsed["subtype"] is None
        assert parsed["building_subtype"] is None
        assert name == "Recreation in Nashville"

    def test_sports_complex_intent_is_not_rerouted_to_civic_community_center(self):
        description = "Build a 90000 sf sports complex with tournament courts and field house in Nashville, TN"
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
        assert parsed["subtype"] == "sports_complex"
        assert name == "Sports Complex in Nashville"

    def test_aquatic_center_intent_is_not_rerouted_to_hospitality_pool_language(self):
        description = (
            "Build a municipal aquatic center with competition pool, lap lanes, and natatorium in Nashville, TN"
        )
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
        assert parsed["subtype"] == "aquatic_center"
        assert name == "Aquatic Center in Nashville"

    def test_stadium_intent_is_not_rerouted_to_parking_or_retail_event_language(self):
        description = (
            "New stadium with event concourse, ticketing, and adjacent parking lots in Nashville, TN"
        )
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "recreation"
        assert parsed["subtype"] == "stadium"
        assert name == "Stadium in Nashville"

    @pytest.mark.parametrize(
        "description,expected_subtype,expected_name",
        [
            (
                "New 180000 sf mixed-use office and residential tower in Nashville, TN",
                "office_residential",
                "Office Residential in Nashville",
            ),
            (
                "New 145000 sf mixed-use retail and residential podium project in Nashville, TN",
                "retail_residential",
                "Retail Residential in Nashville",
            ),
            (
                "New 210000 sf mixed-use hotel and retail destination in Nashville, TN",
                "hotel_retail",
                "Hotel Retail in Nashville",
            ),
            (
                "New 240000 sf transit-oriented mixed-use development over a station in Nashville, TN",
                "transit_oriented",
                "Transit Oriented in Nashville",
            ),
            (
                "New 200000 sf urban mixed-use district redevelopment in Nashville, TN",
                "urban_mixed",
                "Urban Mixed in Nashville",
            ),
        ],
    )
    def test_mixed_use_subtype_discoverability_all_five_profiles(
        self,
        description,
        expected_subtype,
        expected_name,
    ):
        parsed, name = self._parse_and_name(description)

        assert parsed["building_type"] == "mixed_use"
        assert parsed["subtype"] == expected_subtype
        assert parsed["building_subtype"] == expected_subtype
        assert name == expected_name

    def test_hotel_residential_alias_maps_to_hotel_retail_with_provenance(self):
        parsed, name = self._parse_and_name(
            "New 220000 sf mixed-use hotel residential tower with street retail in Nashville, TN"
        )

        assert parsed["building_type"] == "mixed_use"
        assert parsed["subtype"] == "hotel_retail"
        alias = parsed.get("subtype_alias_mapping")
        assert isinstance(alias, dict)
        assert alias.get("from") == "hotel_residential"
        assert alias.get("to") == "hotel_retail"
        assert name == "Hotel Retail in Nashville"

    @pytest.mark.parametrize(
        "description,expected_pattern",
        [
            (
                "Mixed-use office and residential project with a 60/40 program split in Nashville, TN",
                "ratio_pair",
            ),
            (
                "Mixed-use tower with 70% office / 30% residential allocation in Nashville, TN",
                "component_percent",
            ),
            (
                "Mixed-use district that is mostly residential with neighborhood retail in Nashville, TN",
                "mostly_component",
            ),
            (
                "Mixed-use podium with retail-heavy program and apartments above in Nashville, TN",
                "heavy_component",
            ),
            (
                "Mixed-use redevelopment with balanced program between uses in Nashville, TN",
                "balanced_pair",
            ),
        ],
    )
    def test_mixed_use_split_hint_patterns_are_detectable(self, description, expected_pattern):
        parsed, _ = self._parse_and_name(description)

        assert parsed["building_type"] == "mixed_use"
        split_hint = parsed.get("mixed_use_split_hint")
        assert isinstance(split_hint, dict)
        assert split_hint.get("pattern") == expected_pattern
