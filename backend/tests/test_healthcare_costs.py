"""
Test cases for healthcare facility cost calculations
Ensures accurate pricing for hospitals, medical centers, and healthcare facilities
"""
import pytest
from app.services.healthcare_cost_service import healthcare_cost_service, HealthcareFacilityType
from app.services.nlp_service import NLPService
from app.services.building_type_service import BuildingTypeService

class TestHealthcareCosts:
    """Test healthcare cost calculations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.healthcare_service = healthcare_cost_service
        self.nlp_service = NLPService()
        self.building_type_service = BuildingTypeService()
    
    def test_hospital_detection(self):
        """Test that hospitals are properly detected from description"""
        test_cases = [
            {
                'description': 'New 50000 sf hospital addition in Manchester NH',
                'expected_type': HealthcareFacilityType.HOSPITAL,
                'expected_base_min': 500,
                'expected_base_max': 600
            },
            {
                'description': 'Build a 100000 square foot medical center with emergency department',
                'expected_type': HealthcareFacilityType.HOSPITAL,
                'expected_base_min': 500,
                'expected_base_max': 600
            },
            {
                'description': 'Regional trauma center with ICU and operating rooms',
                'expected_type': HealthcareFacilityType.HOSPITAL,
                'expected_base_min': 550,
                'expected_base_max': 700
            }
        ]
        
        for case in test_cases:
            result = self.healthcare_service.determine_facility_type(
                case['description']
            )
            assert result == case['expected_type'], \
                f"Failed to detect hospital in: {case['description']}"
            
            cost_data = self.healthcare_service.get_healthcare_cost(
                case['description']
            )
            base_cost = cost_data['adjusted_cost_per_sf']
            assert case['expected_base_min'] <= base_cost <= case['expected_base_max'], \
                f"Hospital base cost {base_cost} not in expected range {case['expected_base_min']}-{case['expected_base_max']}"
    
    def test_outpatient_clinic_detection(self):
        """Test outpatient and clinic detection"""
        test_cases = [
            {
                'description': 'Build 20000 sf outpatient clinic in Nashville',
                'expected_type': HealthcareFacilityType.OUTPATIENT_CLINIC,
                'expected_base_min': 375,  # Base outpatient clinic
                'expected_base_max': 425   # May have emergency features
            },
            {
                'description': 'New urgent care center 8000 square feet',
                'expected_type': HealthcareFacilityType.URGENT_CARE,
                'expected_base_min': 350,  # Base urgent care
                'expected_base_max': 400   # With emergency feature: 350 + 50
            },
            {
                'description': 'Walk-in clinic for immediate care services',
                'expected_type': HealthcareFacilityType.OUTPATIENT_CLINIC,  # 'walk-in clinic' matches outpatient first
                'expected_base_min': 375,  # Base outpatient
                'expected_base_max': 425   # May have emergency features
            }
        ]
        
        for case in test_cases:
            result = self.healthcare_service.determine_facility_type(
                case['description']
            )
            assert result == case['expected_type'], \
                f"Failed to detect {case['expected_type']} in: {case['description']}, got {result} instead"
            
            cost_data = self.healthcare_service.get_healthcare_cost(
                case['description']
            )
            base_cost = cost_data['adjusted_cost_per_sf']
            assert case['expected_base_min'] <= base_cost <= case['expected_base_max'], \
                f"Clinic base cost {base_cost} not in expected range"
    
    def test_surgical_center_detection(self):
        """Test surgical and specialty center detection"""
        test_cases = [
            {
                'description': '15000 sf surgical center with 4 operating rooms',
                'expected_type': HealthcareFacilityType.SURGICAL_CENTER,
                'expected_base_min': 475,  # Base surgical center
                'expected_base_max': 600   # With emergency + surgery: 475 + 50 + 75 = 600
            },
            {
                'description': 'Ambulatory surgery center with procedure rooms',
                'expected_type': HealthcareFacilityType.SURGICAL_CENTER,
                'expected_base_min': 475,  # Base surgical center 
                'expected_base_max': 600   # With emergency + surgery features
            },
            {
                'description': 'Outpatient surgery facility 12000 square feet',
                'expected_type': HealthcareFacilityType.SURGICAL_CENTER,
                'expected_base_min': 475,  # Base surgical center
                'expected_base_max': 600   # With emergency + surgery features
            }
        ]
        
        for case in test_cases:
            result = self.healthcare_service.determine_facility_type(
                case['description']
            )
            assert result == case['expected_type'], \
                f"Failed to detect surgical center in: {case['description']}"
            
            cost_data = self.healthcare_service.get_healthcare_cost(
                case['description']
            )
            base_cost = cost_data['adjusted_cost_per_sf']
            assert case['expected_base_min'] <= base_cost <= case['expected_base_max'], \
                f"Surgical center base cost {base_cost} not in expected range"
    
    def test_medical_office_detection(self):
        """Test medical office building detection"""
        test_cases = [
            {
                'description': 'Medical office building 10000 sf for primary care',
                'expected_type': HealthcareFacilityType.MEDICAL_OFFICE,
                'expected_base_min': 325,  # Base medical office
                'expected_base_max': 350   # No extra features expected
            },
            {
                'description': 'Doctor office space for family medicine practice',
                'expected_type': HealthcareFacilityType.MEDICAL_OFFICE,
                'expected_base_min': 325,  # Base medical office
                'expected_base_max': 365   # May have imaging feature
            },
            {
                'description': 'Dental office 5000 square feet',
                'expected_type': HealthcareFacilityType.DENTAL_OFFICE,
                'expected_base_min': 300,  # Base dental office
                'expected_base_max': 325   # No extra features expected
            }
        ]
        
        for case in test_cases:
            result = self.healthcare_service.determine_facility_type(
                case['description']
            )
            assert result == case['expected_type'], \
                f"Failed to detect medical office in: {case['description']}"
            
            cost_data = self.healthcare_service.get_healthcare_cost(
                case['description']
            )
            base_cost = cost_data['adjusted_cost_per_sf']
            assert case['expected_base_min'] <= base_cost <= case['expected_base_max'], \
                f"Medical office base cost {base_cost} not in expected range"
    
    def test_feature_detection(self):
        """Test detection of healthcare-specific features"""
        descriptions = {
            'emergency': 'Hospital with 24/7 emergency department',
            'surgery': 'Medical center with operating rooms and surgical suites',
            'imaging': 'Healthcare facility with MRI and CT scan capabilities',
            'lab': 'Hospital with full laboratory and pathology services',
            'specialty': 'Pediatric cancer center with specialized treatment',
        }
        
        for feature, description in descriptions.items():
            cost_data = self.healthcare_service.get_healthcare_cost(description)
            features = cost_data['features']
            
            if feature == 'emergency':
                assert features['has_emergency'] == True
            elif feature == 'surgery':
                assert features['has_surgery'] == True
            elif feature == 'imaging':
                assert features['has_imaging'] == True
            elif feature == 'lab':
                assert features['has_lab'] == True
            elif feature == 'specialty':
                assert features['is_specialty'] == True
    
    def test_bed_count_extraction(self):
        """Test extraction of bed count from description"""
        test_cases = [
            ('200 bed hospital', 200),
            ('50-bed facility', 50),
            ('Hospital with 150 patient rooms', 150),
            ('100 room medical center', 100),
            ('Small 25 bed hospital', 25)
        ]
        
        for description, expected_beds in test_cases:
            beds = self.healthcare_service.extract_bed_count(description.lower())
            assert beds == expected_beds, \
                f"Failed to extract {expected_beds} beds from: {description}"
    
    def test_total_cost_calculation(self):
        """Test total cost calculations for various healthcare facilities"""
        test_cases = [
            {
                'description': 'New 50000 sf hospital in Manchester NH',
                'square_footage': 50000,
                'expected_total_min': 27_500_000,  # ~$550/SF
                'expected_total_max': 30_000_000   # $600/SF (with features)
            },
            {
                'description': 'Build 20000 sf outpatient clinic in Nashville',
                'square_footage': 20000,
                'expected_total_min': 7_500_000,   # $375/SF
                'expected_total_max': 8_500_000    # ~$425/SF (with features)
            },
            {
                'description': '15000 sf surgical center with imaging',
                'square_footage': 15000,
                'expected_total_min': 9_000_000,   # ~$600/SF (475 base + features)
                'expected_total_max': 9_600_000    # $640/SF (with emergency, surgery, imaging)
            },
            {
                'description': 'Medical office building 10000 sf',
                'square_footage': 10000,
                'expected_total_min': 3_250_000,   # $325/SF
                'expected_total_max': 3_500_000    # ~$350/SF
            }
        ]
        
        for case in test_cases:
            cost_data = self.healthcare_service.get_healthcare_cost(
                case['description'],
                square_footage=case['square_footage']
            )
            
            cost_per_sf = cost_data['adjusted_cost_per_sf']
            total_cost = cost_per_sf * case['square_footage']
            
            assert case['expected_total_min'] <= total_cost <= case['expected_total_max'], \
                f"Total cost ${total_cost:,.0f} not in expected range " \
                f"${case['expected_total_min']:,.0f}-${case['expected_total_max']:,.0f} " \
                f"for: {case['description']}"
    
    def test_healthcare_addition_multiplier(self):
        """Test that healthcare additions have appropriate multipliers"""
        test_cases = [
            (HealthcareFacilityType.HOSPITAL, 1.25),
            (HealthcareFacilityType.SURGICAL_CENTER, 1.20),
            (HealthcareFacilityType.MEDICAL_OFFICE, 1.15),
            (HealthcareFacilityType.OUTPATIENT_CLINIC, 1.15)
        ]
        
        for facility_type, expected_multiplier in test_cases:
            multiplier = self.healthcare_service.get_healthcare_addition_multiplier(facility_type)
            assert multiplier == expected_multiplier, \
                f"Wrong multiplier for {facility_type}: {multiplier} vs {expected_multiplier}"
    
    def test_nlp_integration(self):
        """Test that NLP service properly detects healthcare facilities"""
        descriptions = [
            'Build a new 50000 sf hospital in Manchester',
            'Construct medical office building 15000 square feet',
            'New surgical center with 4 operating rooms',
            'Outpatient clinic for urgent care services'
        ]
        
        for description in descriptions:
            extracted = self.nlp_service.extract_project_details(description)
            
            assert extracted.get('is_healthcare') == True, \
                f"NLP failed to detect healthcare in: {description}"
            assert extracted.get('building_type') == 'healthcare', \
                f"Wrong building type for: {description}"
            assert extracted.get('occupancy_type') == 'healthcare', \
                f"Wrong occupancy type for: {description}"
            assert 'healthcare_details' in extracted, \
                f"Missing healthcare details for: {description}"
    
    def test_trade_breakdown(self):
        """Test that healthcare facilities have appropriate trade breakdowns"""
        hospital_cost = self.healthcare_service.get_healthcare_cost(
            'New hospital with emergency department'
        )
        
        trade_breakdown = hospital_cost['trade_breakdown']
        
        # Hospitals should have high mechanical costs (35%)
        assert trade_breakdown['mechanical'] >= 0.35, \
            "Hospital mechanical should be at least 35%"
        
        # Hospitals should have significant electrical (20%)
        assert trade_breakdown['electrical'] >= 0.20, \
            "Hospital electrical should be at least 20%"
        
        # Hospitals should have lower finishes percentage (8%)
        assert trade_breakdown['finishes'] <= 0.10, \
            "Hospital finishes should be 10% or less"
        
        # Sum should be 100%
        total = sum(trade_breakdown.values())
        assert 0.99 <= total <= 1.01, \
            f"Trade breakdown should sum to ~100%, got {total*100:.1f}%"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])