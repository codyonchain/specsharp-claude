"""
Test cases for Cost DNA calculation engine
"""
import pytest
from app.services.cost_dna_service import CostCalculationEngine


class TestCostDNA:
    """Test Cost DNA generation and detection"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = CostCalculationEngine()
    
    def test_hospital_cost_dna_generation(self):
        """Test hospital project with multiple detected factors"""
        result = self.engine.calculate_with_dna(
            square_footage=50000,
            occupancy_type="healthcare",
            location="San Francisco, CA",
            project_classification="addition",
            description="Hospital surgical wing addition with 8 operating rooms and imaging center in California",
            finish_level="premium"
        )
        
        # Check structure
        assert 'cost_dna' in result
        assert 'confidence_score' in result
        assert 'comparable_projects' in result
        
        # Check detected factors
        dna = result['cost_dna']
        assert len(dna['detected_factors']) > 0
        
        # Should detect OSHPD, surgical, imaging
        factor_names = [f['factor'] for f in dna['detected_factors']]
        assert 'OSHPD Compliance' in factor_names
        assert 'Surgical Suite Requirements' in factor_names
        assert 'Imaging Equipment Infrastructure' in factor_names
        
        # Check multipliers
        assert len(dna['applied_multipliers']) >= 2  # Location and classification
        
        # High cost location
        location_mult = next(m for m in dna['applied_multipliers'] if 'Regional' in m['factor'])
        assert float(location_mult['value'].replace('x', '')) > 1.3  # SF is expensive
        
        # Addition complexity
        class_mult = next(m for m in dna['applied_multipliers'] if 'Addition' in m['factor'])
        assert float(class_mult['value'].replace('x', '')) >= 1.20  # Healthcare addition
        
        # Confidence should be reasonable
        assert 60 <= result['confidence_score'] <= 100
    
    def test_restaurant_cost_dna(self):
        """Test restaurant with commercial kitchen and special features"""
        result = self.engine.calculate_with_dna(
            square_footage=4000,
            occupancy_type="restaurant",
            location="Nashville, TN",
            project_classification="ground_up",
            description="Fine dining restaurant with commercial kitchen, wine cellar, and outdoor patio",
            finish_level="premium"
        )
        
        dna = result['cost_dna']
        
        # Should detect kitchen, wine cellar, patio
        factor_names = [f['factor'] for f in dna['detected_factors']]
        assert 'Commercial Kitchen' in factor_names
        assert 'Wine Storage' in factor_names
        assert 'Outdoor Dining Area' in factor_names
        # Premium finishes would be detected if explicitly mentioned in description
        # The finish_level parameter affects base cost but isn't shown as detected factor
        
        # Nashville location
        location_mult = next(m for m in dna['applied_multipliers'] if 'Regional' in m['factor'])
        assert 1.0 <= float(location_mult['value'].replace('x', '')) <= 1.05
        
        # Should have comparables
        assert len(result['comparable_projects']) > 0
    
    def test_warehouse_with_special_conditions(self):
        """Test warehouse with clear height and automation"""
        result = self.engine.calculate_with_dna(
            square_footage=150000,
            occupancy_type="warehouse",
            location="Memphis, TN",
            project_classification="ground_up",
            description="Distribution warehouse with 35-foot clear height, automated conveyor systems, and 20 loading docks",
            finish_level="standard"
        )
        
        dna = result['cost_dna']
        
        # Should detect height and automation
        factor_names = [f['factor'] for f in dna['detected_factors']]
        assert any('Clear Height' in f for f in factor_names)
        assert 'Automation Systems' in factor_names
        
        # Memphis is below average
        location_mult = next(m for m in dna['applied_multipliers'] if 'Regional' in m['factor'])
        assert float(location_mult['value'].replace('x', '')) < 1.0
    
    def test_winter_conditions_detection(self):
        """Test winter conditions for New England renovation"""
        result = self.engine.calculate_with_dna(
            square_footage=10000,
            occupancy_type="office",
            location="Manchester, NH",
            project_classification="renovation",
            description="Office renovation in downtown Manchester",
            finish_level="standard"
        )
        
        dna = result['cost_dna']
        
        # Should detect winter conditions
        condition_names = [c['factor'] for c in dna['special_conditions']]
        assert 'Winter Protection' in condition_names or 'Winter Conditions' in condition_names
    
    def test_seismic_detection_california(self):
        """Test seismic requirements for California"""
        result = self.engine.calculate_with_dna(
            square_footage=25000,
            occupancy_type="office",
            location="Los Angeles, CA",
            project_classification="ground_up",
            description="New office building",
            finish_level="standard"
        )
        
        dna = result['cost_dna']
        
        # Should detect seismic requirements
        condition_names = [c['factor'] for c in dna['special_conditions']]
        assert any('Seismic' in c for c in condition_names)
    
    def test_leed_certification_detection(self):
        """Test LEED certification detection"""
        result = self.engine.calculate_with_dna(
            square_footage=50000,
            occupancy_type="office",
            location="Boston, MA",
            project_classification="ground_up",
            description="New LEED Gold certified office building with sustainable features",
            finish_level="premium"
        )
        
        dna = result['cost_dna']
        
        # Should detect LEED
        factor_names = [f['factor'] for f in dna['detected_factors']]
        assert any('LEED' in f and 'Gold' in f for f in factor_names)
    
    def test_confidence_scoring(self):
        """Test confidence score calculation"""
        # Simple project should have high confidence
        simple_result = self.engine.calculate_with_dna(
            square_footage=10000,
            occupancy_type="office",
            location="Nashville, TN",
            project_classification="ground_up",
            description="Standard office building",
            finish_level="standard"
        )
        
        # Complex project should have lower confidence
        complex_result = self.engine.calculate_with_dna(
            square_footage=500000,  # Very large
            occupancy_type="healthcare",
            location="Rural Town, XX",  # Unknown location
            project_classification="renovation",
            description="Complex hospital renovation with multiple special requirements including OSHPD, clean rooms, MRI, surgery",
            finish_level="premium"
        )
        
        assert simple_result['confidence_score'] > complex_result['confidence_score']
        assert simple_result['confidence_score'] >= 85  # Simple should be high
        assert complex_result['confidence_score'] <= 75  # Complex should be lower
    
    def test_comparable_projects(self):
        """Test comparable project generation"""
        result = self.engine.calculate_with_dna(
            square_footage=20000,
            occupancy_type="retail",
            location="Dallas, TX",
            project_classification="ground_up",
            description="New retail store",
            finish_level="standard"
        )
        
        comparables = result['comparable_projects']
        assert len(comparables) >= 3
        
        # Check structure
        for comp in comparables:
            assert 'project_name' in comp
            assert 'location' in comp
            assert 'square_footage' in comp
            assert 'cost_per_sf' in comp
            assert 'similarity_score' in comp
        
        # Similarity scores should decrease
        scores = [c['similarity_score'] for c in comparables]
        assert scores == sorted(scores, reverse=True)
    
    def test_market_conditions(self):
        """Test market conditions detection"""
        result = self.engine.calculate_with_dna(
            square_footage=50000,
            occupancy_type="office",
            location="Austin, TX",
            project_classification="ground_up",
            description="New office building",
            finish_level="standard"
        )
        
        dna = result['cost_dna']
        
        # Should have market adjustments
        assert len(dna['market_adjustments']) > 0
        market = dna['market_adjustments'][0]
        assert 'volatile_materials' in market
        assert 'adjustment_percent' in market
    
    def test_mixed_use_calculation(self):
        """Test mixed-use project with multiple building types"""
        result = self.engine.calculate_with_dna(
            square_footage=100000,
            occupancy_type="mixed",
            location="Nashville, TN",
            project_classification="ground_up",
            description="Mixed-use development",
            finish_level="standard",
            building_mix={"retail": 0.3, "office": 0.4, "residential": 0.3}
        )
        
        dna = result['cost_dna']
        
        # Should show mixed-use weighting
        base_components = dna['base_components']
        assert any('Mixed-Use' in c['factor'] for c in base_components)
    
    def test_fast_track_detection(self):
        """Test accelerated schedule detection"""
        result = self.engine.calculate_with_dna(
            square_footage=15000,
            occupancy_type="healthcare",
            location="Boston, MA",
            project_classification="ground_up",
            description="Urgent care center needed on fast track schedule",
            finish_level="standard"
        )
        
        dna = result['cost_dna']
        
        # Should detect accelerated schedule
        factor_names = [f['factor'] for f in dna['detected_factors']]
        assert 'Accelerated Schedule' in factor_names
    
    def test_urban_constraints(self):
        """Test urban site constraints detection"""
        result = self.engine.calculate_with_dna(
            square_footage=30000,
            occupancy_type="office",
            location="Downtown Manhattan, New York",
            project_classification="ground_up",
            description="New office tower in downtown",
            finish_level="premium"
        )
        
        dna = result['cost_dna']
        
        # Should detect urban constraints
        condition_names = [c['factor'] for c in dna['special_conditions']]
        assert 'Urban Site Constraints' in condition_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])