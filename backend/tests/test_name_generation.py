"""
Test cases for smart project name generation
"""
import pytest
from app.services.nlp_service import NLPService

class TestProjectNameGeneration:
    """Test smart project name generation from natural language"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.nlp_service = NLPService()
    
    def test_hospital_addition_name(self):
        """Test hospital addition naming"""
        description = 'Expand hospital with new 50000 sf surgical wing including 8 operating rooms in Manchester, NH'
        parsed = self.nlp_service.extract_project_details(description)
        
        expected_name_contains = ['Hospital', 'Manchester', '50K SF']
        name = parsed.get('suggested_project_name', '')
        
        for term in expected_name_contains:
            assert term in name, f"Expected '{term}' in project name '{name}'"
    
    def test_restaurant_ground_up_name(self):
        """Test new restaurant naming"""
        description = 'New 4000 sf fast-casual restaurant with commercial kitchen in Nashville'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'New' in name, f"Expected 'New' in project name '{name}'"
        assert 'Restaurant' in name, f"Expected 'Restaurant' in project name '{name}'"
        assert 'Nashville' in name, f"Expected 'Nashville' in project name '{name}'"
    
    def test_retail_to_clinic_conversion(self):
        """Test conversion project naming"""
        description = 'Convert 8000 sf retail space to urgent care clinic with 12 exam rooms'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'Urgent Care' in name or 'Clinic' in name, f"Expected medical facility in name '{name}'"
        assert 'Conversion' in name, f"Expected 'Conversion' in project name '{name}'"
    
    def test_restaurant_renovation_downtown(self):
        """Test renovation with downtown location"""
        description = 'Full gut renovation of 5000 sf restaurant in downtown Manchester'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'Restaurant' in name, f"Expected 'Restaurant' in project name '{name}'"
        assert 'Renovation' in name, f"Expected 'Renovation' in project name '{name}'"
        assert 'Downtown' in name or 'Manchester' in name, f"Expected location in name '{name}'"
    
    def test_medical_office_with_imaging(self):
        """Test medical facility with special features"""
        description = 'Build new 75000 sf Class A medical office building with imaging center'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        # Either Medical or Imaging Center is acceptable
        assert 'Medical' in name or 'Imaging' in name, f"Expected 'Medical' or 'Imaging' in project name '{name}'"
        assert '75K SF' in name, f"Expected size '75K SF' in project name '{name}'"
        # The name should reflect it's a new construction
        assert 'New' in name, f"Expected 'New' in project name '{name}'"
    
    def test_warehouse_with_docks(self):
        """Test warehouse with loading docks"""
        description = 'New 150000 sf distribution warehouse with 30-foot clear height and 20 loading docks in Memphis, TN'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'Distribution' in name or 'Warehouse' in name, f"Expected warehouse type in name '{name}'"
        assert 'Memphis' in name, f"Expected 'Memphis' in project name '{name}'"
        assert '150K SF' in name, f"Expected size in project name '{name}'"
    
    def test_school_addition(self):
        """Test school addition project"""
        description = 'Building extension adding 15000 sf of classroom space to existing high school'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'School' in name or 'Classroom' in name, f"Expected school-related term in name '{name}'"
        assert 'Addition' in name or 'Extension' in name, f"Expected addition/extension in name '{name}'"
        assert '15K SF' in name, f"Expected size in project name '{name}'"
    
    def test_surgical_center_with_features(self):
        """Test surgical center with multiple features"""
        description = 'Construct 10000 sf addition to medical clinic for outpatient surgery center with 4 procedure rooms'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        # Should include surgery center and possibly room count
        assert 'Surgical' in name or 'Surgery' in name, f"Expected surgery-related term in name '{name}'"
        assert '10K SF' in name, f"Expected size in project name '{name}'"
    
    def test_restaurant_with_patio(self):
        """Test restaurant with outdoor features"""
        description = 'New 6000 sf restaurant with outdoor patio and full bar in Franklin, TN'
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert 'Restaurant' in name, f"Expected 'Restaurant' in project name '{name}'"
        assert 'Franklin' in name, f"Expected 'Franklin' in project name '{name}'"
        # May include patio as a feature
        assert 'Patio' in name or 'Restaurant' in name, f"Expected feature or type in name '{name}'"
    
    def test_name_length_truncation(self):
        """Test that very long descriptions generate reasonable length names"""
        description = ('Build new 100000 sf hospital with emergency department, surgical wing, '
                      'imaging center, laboratory, pharmacy, outpatient clinic, and administrative '
                      'offices in Manchester, New Hampshire')
        parsed = self.nlp_service.extract_project_details(description)
        
        name = parsed.get('suggested_project_name', '')
        assert len(name) <= 65, f"Project name too long ({len(name)} chars): '{name}'"
        assert 'Hospital' in name, f"Expected 'Hospital' in project name '{name}'"
        assert '100K SF' in name, f"Expected size in project name '{name}'"
    
    def test_detail_suggestions_restaurant(self):
        """Test that restaurant projects get appropriate detail suggestions"""
        description = 'New restaurant in Nashville'
        parsed = self.nlp_service.extract_project_details(description)
        
        suggestions = parsed.get('detail_suggestions', [])
        assert len(suggestions) > 0, "Expected detail suggestions for restaurant"
        assert any('kitchen' in s.lower() for s in suggestions), "Expected kitchen-related suggestion"
        assert any('seating' in s.lower() for s in suggestions), "Expected seating-related suggestion"
    
    def test_detail_suggestions_healthcare(self):
        """Test that healthcare projects get appropriate detail suggestions"""
        description = 'New medical clinic in Manchester'
        parsed = self.nlp_service.extract_project_details(description)
        
        suggestions = parsed.get('detail_suggestions', [])
        assert len(suggestions) > 0, "Expected detail suggestions for healthcare"
        assert any('exam' in s.lower() or 'operating' in s.lower() for s in suggestions), \
            "Expected room-related suggestion"
        assert any('equipment' in s.lower() for s in suggestions), "Expected equipment-related suggestion"
    
    def test_detail_suggestions_warehouse(self):
        """Test that warehouse projects get appropriate detail suggestions"""
        description = 'New warehouse facility'
        parsed = self.nlp_service.extract_project_details(description)
        
        suggestions = parsed.get('detail_suggestions', [])
        assert len(suggestions) > 0, "Expected detail suggestions for warehouse"
        assert any('height' in s.lower() for s in suggestions), "Expected clear height suggestion"
        assert any('dock' in s.lower() for s in suggestions), "Expected loading dock suggestion"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])